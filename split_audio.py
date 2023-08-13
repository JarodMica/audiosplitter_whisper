import os
import subprocess
import yaml
import pysrt
import tkinter as tk
import torch
import re
import shutil
import unicodedata
from tkinter import filedialog
from pydub import AudioSegment

AUDIO_EXT = ".wav"
CONFIG_PATH = "conf.yaml"
FILE_COUNTER = 0


def load_settings(config_path):
    with open(config_path, "r") as file:
        return yaml.safe_load(file)


def get_device_info():
    if torch.cuda.is_available():
        print('CUDA is available. Running on GPU.')
        return 'cuda', "float16"
    else:
        print('CUDA is not available. Running on CPU.')
        return 'cpu', "int8"


def sanitize_filename(filename):
    # Remove diacritics and normalize Unicode characters
    normalized = unicodedata.normalize('NFKD', filename)
    sanitized = ''.join(c for c in normalized if not unicodedata.combining(c))

    # Regular Expression to match invalid characters
    invalid_chars_pattern = r'[<>:"/\\|?*]'

    # Replace invalid characters with an underscore
    return re.sub(invalid_chars_pattern, '_', sanitized)


def get_output_filename():
    global FILE_COUNTER
    FILE_COUNTER += 1
    return f"segment_{FILE_COUNTER}{AUDIO_EXT}"


def process_subtitle(audio, sub, output_dir, padding=0.0):
    '''
    Args:
        - padding(int) - how much additional sound to include before and after audio, can be useful for 
        audio that is getting clipped.
    '''
    start_time = max(0, sub.start.ordinal - padding * 1000)
    end_time = min(len(audio), sub.end.ordinal + padding * 1000)
    segment = audio[start_time:end_time]
    output_filename = get_output_filename()
    output_path = os.path.join(output_dir, output_filename)
    segment.export(output_path, format="wav")
    print(f"Saved segment to {output_path}")


def diarize_audio_with_srt(audio_file, srt_file, output_dir):
    '''
    Use whisperx generated SRT files in order to split the audio files with speaker
    numbering and diarization
    
    Args:
        - audio_file(str) - path to the audio file being processed
        - srt_file(str) - path to the srt file being used for the splicing
        - output_dir(str) - directory for the outputted files

    '''
    audio = AudioSegment.from_file(audio_file)
    subs = pysrt.open(srt_file)
    for sub in subs:
        speaker = sub.text.split(']')[0][1:]
        sanitized_speaker = sanitize_filename(speaker)
        speaker_dir = os.path.join(output_dir, sanitized_speaker)
        os.makedirs(speaker_dir, exist_ok=True)
        process_subtitle(audio, sub, speaker_dir)


def extract_audio_with_srt(audio_file, srt_file, output_dir):
    '''
    Use whisperx generated SRT files in order to split the audio files
    
    Args:
        - audio_file(str) - path to the audio file being processed
        - srt_file(str) - path to the srt file being used for the splicing
        - output_dir(str) - drectory for the outputted files
    '''
    audio = AudioSegment.from_file(audio_file)
    subs = pysrt.open(srt_file)
    os.makedirs(output_dir, exist_ok=True)
    for sub in subs:
        process_subtitle(audio, sub, output_dir)


def run_whisperx(audio_files, output_dir, settings, device, compute_type):
    base_cmd = ["whisperx", audio_files, 
                "--device", device,
                "--model", settings["model"], 
                "--output_dir", output_dir, 
                "--language", settings["language"],
                "--output_format", "srt",
                "--compute_type", compute_type]
    
    if settings["diarize"]:
        base_cmd.extend(["--diarize", "--hf_token", settings["HF_token"]])

    subprocess.run(base_cmd)


def process_audio_files(input_folder, settings):
    output_dir = os.path.join(input_folder, "output")
    wav_dir = os.path.join(input_folder, "wav_files")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(wav_dir, exist_ok=True)

    device, compute_type = get_device_info()

    for audio_file in os.listdir(input_folder):
        audio_file_path = os.path.join(input_folder, audio_file)
        if not os.path.isfile(audio_file_path):
            continue

        if not audio_file.endswith(AUDIO_EXT):
            wav_file_path = os.path.join(wav_dir, f"{os.path.splitext(audio_file)[0]}{AUDIO_EXT}")
            try:
                
                subprocess.run(['ffmpeg', '-i', audio_file_path, wav_file_path], check=True)
                audio_file_path = wav_file_path
            except subprocess.CalledProcessError as e:
                print(f"Error: {e.output}. Couldn't convert {audio_file} to {AUDIO_EXT} format.")
                continue

        run_whisperx(audio_file_path, output_dir, settings, device, compute_type)
        srt_file = os.path.join(output_dir, f"{os.path.splitext(audio_file)[0]}.srt")
        
        # Set the output directory for speaker segments to be a subdirectory named after the .wav file
        speaker_segments_dir = os.path.join(output_dir, os.path.splitext(audio_file)[0])
        os.makedirs(speaker_segments_dir, exist_ok=True)

        if settings["diarize"]:
            diarize_audio_with_srt(audio_file_path, srt_file, speaker_segments_dir)
        else: 
            extract_audio_with_srt(audio_file_path, srt_file, speaker_segments_dir)
    if settings["one_folder"] == True and settings["diarize"] == False:
        merge_segments(output_dir)

def merge_segments(output_dir):
    combined_dir = os.path.join(output_dir, "combined_folder")
    os.makedirs(combined_dir, exist_ok=True)

    for folder_name in os.listdir(output_dir):
        folder_path = os.path.join(output_dir, folder_name)
        if not os.path.isdir(folder_path) or folder_name == "combined_folder":
            continue

        for segment_name in os.listdir(folder_path):
            segment_path = os.path.join(folder_path, segment_name)
            new_segment_name = f"{folder_name}_{segment_name.split('_')[-1]}"
            new_segment_path = os.path.join(combined_dir, new_segment_name)
            shutil.move(segment_path, new_segment_path)

        os.rmdir(folder_path)  # Remove the original directory after all its segments have been moved

def select_input_folder():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askdirectory(title="Select input folder").replace("/","\\")


def main():
    input_folder = select_input_folder()
    settings = load_settings(CONFIG_PATH)
    process_audio_files(input_folder, settings)
    
if __name__ == "__main__":
    main()
