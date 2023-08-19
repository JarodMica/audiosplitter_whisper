<div align="center">

<h1>Audio Splitter</h1>

[![Licence](https://img.shields.io/badge/LICENSE-MIT-green.svg?style=for-the-badge)](https://raw.githubusercontent.com/filispeen/audiosplitter_whisper_headless/colab/LICENSE)
[![Open In Colab](https://img.shields.io/badge/Colab-F9AB00?style=for-the-badge&logo=googlecolab&color=525252)](https://colab.research.google.com/github/filispeen/audiosplitter_whisper_headless/blob/colab/Audio_Splitter.ipynb)
</div>

## Youtube Video Tutorial
https://youtu.be/9lsSSPnF67Q

## Prerequisites
- Python 3.10 installation
- git installation
- vscode installation (highly recommended)
- ffmpeg installation
- Cuda Capable Nvidia GPU (highly recommended)

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
