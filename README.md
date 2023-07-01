# Audio Splitter using Whisperx
Created with the purpose for curating datasets for the sake of training AI models.  This is created with RVC (Retrieval-based Voice Conversion) in mind but generally works for any other AI voice model that needs short clips less than 10s.

## Youtube Video Tutorial
<insert tutorial later>

## Prerequisites
- Python 3.10 installation
- git installation
- vscode installation (highly recommended)

## Installation and basic usage
1. Clone the repository (repo)
```
git clone https://github.com/JarodMica/audiosplitter_whisper.git
```

2. Navigate into the repo with:
```
cd audiosplitter_whisper
``` 

4. Run setup-cuda.py if you have a compatible Nvidia graphics card or run setup-cpu.py if you do not. **NOTE:** This splitter will work on a CPU, albeit, very slowly.  The reason I keep this option is for people who may want to curate a dataset locally, but train on colab. (AMD not compatible, Mac is not coded for (should be able to use MPS though).  Both can use CPU option)

```
python setup-cuda.py
```

5. Activate the virtual envionrment (venv).
```
venv\Scripts\activate
```

6. If you ran into any permission issues, you'll need to change your windows Execution Policy to Remote Signed.  This does lower security on your system a small bit as it allows for scripts to be ran on your computer, however, only those signed by a Trusted Publisher or verified by you can be run (to my knowledge).  Do at your own risk.
    - Open a powershell window as admin.  Then, run the following command:

    ```
    Set-ExecutionPolicy RemoteSigned
    ```

    - If you want to change it back, you can with:
    ```
    Set-ExecutionPolicy Restricted
    ```

7. Now rerun step 5 and activate your venv.  After it's activated, you can then run the following command to start up the script:
```
python split_audio.py
```

For more details, please refer to the youtube video.