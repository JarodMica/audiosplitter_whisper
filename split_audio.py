import os
import subprocess
import yaml
import pysrt
import torch
import re
import unicodedata

from pydub import AudioSegment

yaml=input("Do you wanna write new config? Y/n: ").lower().replace("yes", "y")

if yaml=="y":
    inplan=input("Input language (example: en, ua, kz, ja): ")
    print('Write model name in ""')
    inpmodel=input('Input model "tiny", "base", "small", "medium", "large-v2": ')
    inpdiarize=input("Use diarization? True/False: ")
    if inpdiarize==True:
        HF_token=input("Input Hugging Face Token: ")
    else:
        HF_token="Nothing"
        
    conf = f"language : {inplan}\n"+\
f"model : {inpmodel}\n"+\
f"diarize : {inpdiarize}\n"+\
f"HF_token : {HF_token}\n"
        
    with open('conf.yaml', 'w') as f:
        f.write(conf)

with open("conf.yaml", "r") as file:
    settings = yaml.safe_load(file)

language = settings["language"]
whisper_model = settings["model"]
hf_token = settings["HF_token"]
diarize = settings["diarize"]

if torch.cuda.is_available():
    device = 'cuda'
    compute_type = "float16"
    print('CUDA is available. Running on GPU.')
else:
    device = 'cpu'
    compute_type = "int8"
    print('CUDA is not available. Running on CPU.')


def sanitize_filename(filename):
    # Remove diacritics and normalize Unicode characters
    normalized = unicodedata.normalize('NFKD', filename)
    sanitized = ''.join(c for c in normalized if not unicodedata.combining(c))
    
    # Regular Expression to match invalid characters
    invalid_chars_pattern = r'[<>:"/\\|?*]'
    
    # Replace invalid characters with an underscore
    sanitized_filename = re.sub(invalid_chars_pattern, '_', sanitized)
    
    return sanitized_filename

def diarize_audio_with_srt(audio_file, srt_file, output_dir, padding=0.0):
    '''
    Use whisperx generated SRT files in order to split the audio files with speaker
    numbering and diarization
    
    Args:
        - audio_file(str) - path to the audio file being processed
        - srt_file(str) - path to the srt file being used for the splicing
        - output_dir(str) - directory for the outputted files
        - padding(int) - how much additional sound to include before and after audio, can be useful for 
        - audio that is getting clipped.
    '''
    audio = AudioSegment.from_file(audio_file)
    subs = pysrt.open(srt_file)

    for i, sub in enumerate(subs):
        # Extract speaker from subtitle
        speaker = sub.text.split(']')[0][1:]
        sanitized_speaker = sanitize_filename(speaker)


        # Create speaker-specific output directory
        speaker_dir = os.path.join(output_dir, sanitized_speaker)
        if not os.path.exists(speaker_dir):
            os.makedirs(speaker_dir)

        # Calculate start and end times with padding (pydub uses milliseconds)
        start_time = max(0, sub.start.ordinal - padding * 1000)
        end_time = min(len(audio), sub.end.ordinal + padding * 1000)

        # Extract segment from audio
        segment = audio[start_time:end_time]

        # Generate output filename with suffix count
        existing_files = os.listdir(speaker_dir)
        file_count = len(existing_files)
        output_filename = f"segment_{file_count + 1}.wav"
        output_path = os.path.join(speaker_dir, output_filename)

        # Save segment
        segment.export(output_path, format="wav")

        print(f"Saved segment {i+1} to {output_path}")

def extract_audio_with_srt(audio_file, srt_file, output_dir, padding=0.0):
    '''
    Use whisperx generated SRT files in order to split the audio files
    
    Args:
        - audio_file(str) - path to the audio file being processed
        - srt_file(str) - path to the srt file being used for the splicing
        - output_dir(str) - drectory for the outputted files
        - padding(int) - how much additional sound to include before and after audio, can be useful for 
        - audio that is getting clipped.
    
    '''
    audio = AudioSegment.from_file(audio_file)
    subs = pysrt.open(srt_file)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Get existing file count in the output directory
    existing_files = os.listdir(output_dir)
    file_count = len(existing_files)

    for i, sub in enumerate(subs):
        # Calculate start and end times with padding (pydub uses milliseconds)
        start_time = max(0, sub.start.ordinal - padding * 1000)
        end_time = min(len(audio), sub.end.ordinal + padding * 1000)

        # Extract segment from audio
        segment = audio[start_time:end_time]

        # Generate output filename with suffix count
        output_filename = f"segment_{file_count + i + 1}.wav"
        output_path = os.path.join(output_dir, output_filename)

        # Save segment
        segment.export(output_path, format="wav")

        print(f"Saved segment {i+1} to {output_path}")

def run_whisperx(audio_files, output_dir):
    '''Generate SRT file using whisperx'''
    if diarize:
        subprocess.run(["whisperx", audio_files, 
                        "--device", device,
                        "--model", whisper_model, 
                        "--output_dir", output_dir, 
                        "--language", language,
                        "--diarize",
                        "--hf_token", hf_token,
                        "--output_format", "srt",
                        "--compute_type", compute_type])
    else:
        subprocess.run(["whisperx", audio_files, 
                    "--device", device,
                    "--model", whisper_model, 
                    "--output_dir", output_dir, 
                    "--language", language,
                    "--output_format", "srt",
                    "--compute_type", compute_type])

def create_directory(name):
    if not os.path.exists(name):
        os.makedirs(name)

def process_audio_files(input_folder):
    output_dir = os.path.join(input_folder, "output")
    wav_dir = os.path.join(input_folder, "wav_files")
    
    create_directory(output_dir)
    create_directory(wav_dir)

    for audio_file in os.listdir(input_folder):
        audio_file_path = os.path.join(input_folder, audio_file)
        if not os.path.isfile(audio_file_path):
            continue

        if not audio_file.endswith(".wav"):
            # Set output .wav file path
            wav_file_path = os.path.join(wav_dir, f"{os.path.splitext(audio_file)[0]}.wav")
            try:
                subprocess.run(['ffmpeg', '-i', audio_file_path, wav_file_path], check=True)
                audio_file_path = wav_file_path  # Update audio_file_path to point to the converted file
            except subprocess.CalledProcessError as e:
                print(f"Error: {e.output}. Couldn't convert {audio_file} to .wav format.")
                continue

        run_whisperx(audio_file_path, output_dir)
        srt_file = os.path.join(output_dir, f"{os.path.splitext(audio_file)[0]}.srt")

        # Set the output directory for speaker segments to be a subdirectory named after the .wav file
        speaker_segments_dir = os.path.join(output_dir, os.path.splitext(audio_file)[0])
        create_directory(speaker_segments_dir)

        if diarize:
            diarize_audio_with_srt(audio_file_path, srt_file, speaker_segments_dir)
        else: 
            extract_audio_with_srt(audio_file_path, srt_file, speaker_segments_dir)

def choose_input_folder(input_folder):
    process_audio_files(input_folder)

input_folder = input("Input path to your folder: ")
choose_input_folder(input_folder)
