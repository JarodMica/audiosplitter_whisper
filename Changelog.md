# Changelog

## 8-4-2023
- Added "one_folder" parameter to the configuration file.  By setting this to true, it will collect audio from all folders and put them into one folder
    - This makes it easier to process a bunch of short audio files instead of putting each into their own individual folder
    - DOES NOT work with diarized audio.  It's beyond my knowledge atm to categorize and combine unique speakers to unique folders.  I'm sure it's possible if I dive into pyannote a bit more but not now.
- Changed naming convention to never repeat the same suffix, even across folders.  This makes it easier to combine datasets from diarization and has no affect on the one_folder logic as this occurs aft all files have been saved already.