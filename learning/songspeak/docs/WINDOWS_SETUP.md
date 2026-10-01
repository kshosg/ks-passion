# Running SongSpeak on Windows — step by step

For a first project on Windows PowerShell. Type each line, press Enter, and wait for it to finish before typing the next.
Lines starting with `#` are notes. Don't type them.

## One-time setup (about 15 minutes)

### 1. Install Python 3.12 (x64)

Download and run the **x64** installer: https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe
(on the first screen, leave "Add python.exe to PATH" **unticked** so it doesn't clash with any other Python you have).
Then close PowerShell, open a new window, and check:
```powershell
py -0p
py -V:3.12 -c "import platform; print(platform.machine())"
```
`py -0p` lists every Python installed. The x64 one shows as **`-V:3.12`** and the ARM one, if you have it, as `-V:3.12-arm64`.
The second line must print **AMD64**. If it prints ARM64 or "No suitable Python runtime found", the x64 installer didn't run.

Why x64, even on an ARM laptop (Snapdragon / Surface)? The speech-recognition engine used in "Build a real library"
(CTranslate2, behind faster-whisper) has no Windows-on-ARM build. Windows runs x64 Python automatically through
emulation, so it's a little slower but everything works. Python 3.12 is used because every package has a ready-made build for it.

### 2. Install Git (to download the code) and FFmpeg (to read/write MP3s)

```powershell
winget install --id Git.Git -e
winget install --id Gyan.FFmpeg -e
```
**Close PowerShell and open a new window**, which is needed so it finds the new programs. Then check:
```powershell
git --version
ffmpeg -version
```

### 3. Download the project

```powershell
cd $HOME\Documents
git clone https://github.com/kshosg/ks-passion.git
```
A browser window asks you to sign in to GitHub the first time, because the repository is private. Then:
```powershell
cd ks-passion
git checkout claude/trusting-cerf-2aufl8
cd learning\songspeak
```

### 4. Create a private Python environment for this project

This keeps SongSpeak's packages separate from everything else on your PC.

```powershell
py -V:3.12 -m venv .venv
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned     # one time only; answer Y
.\.venv\Scripts\Activate.ps1
```
Your prompt now starts with **(.venv)**. That means it worked.

### 5. Install SongSpeak

The quotes matter: without them PowerShell splits the text at the comma.

```powershell
python -m pip install -e ".[dev,web]"
python -m pytest
```
You should see **`28 passed`**.

## Try it: the demo (no internet needed)

```powershell
python -m songspeak demo
start out\demo\message.wav                  # plays it
python -m songspeak serve --library out\demo\library
```
Open **http://127.0.0.1:8000** in your browser and type a message. The demo library only knows a few words
(hello, everybody, welcome, to, Singapore…) and they're beeps, not real singing. That's expected.
Press **Ctrl + C** in PowerShell to stop the server.

## Build a real Creative Commons library

```powershell
python -m pip install -e ".[ingest]"                    # speech recognition, a big download
$env:FREESOUND_API_KEY = "paste-your-key-here"          # optional; free key at https://freesound.org/apiv2/apply
.\scripts\build_cc_library.ps1                          # downloads ~60 a cappellas, transcribes them (can take an hour+)
python -m songspeak serve --library library
```
Transcribing is slow on a normal PC (several minutes per song). To try a smaller batch first:
```powershell
.\scripts\build_cc_library.ps1 -Pages 1                 # 20 songs
```

## Every time after that

```powershell
cd $HOME\Documents\ks-passion\learning\songspeak
.\.venv\Scripts\Activate.ps1
git pull                                                # get the latest changes
python -m songspeak serve --library library
```

## If something goes wrong

| You see | Do this |
|---|---|
| `python` opens the Microsoft Store | Install Python from python.org with "Add to PATH" ticked, then reopen PowerShell |
| `winget` is not recognized | Install Git from https://git-scm.com/download/win and FFmpeg from https://www.gyan.dev/ffmpeg/builds/ by hand |
| `... is not recognized` right after installing something | Close PowerShell and open a new window |
| `running scripts is disabled on this system` | Run the `Set-ExecutionPolicy` line in step 4 |
| The prompt doesn't start with `(.venv)` | Run `.\.venv\Scripts\Activate.ps1` again from the `learning\songspeak` folder |
| `does not appear to be a Python project` | You're in the wrong folder: `cd $HOME\Documents\ks-passion\learning\songspeak` |
| `faster-whisper` / `ctranslate2` fails to install | The environment was made with ARM or 3.14 Python: delete the `.venv` folder and redo steps 4–5 with `py -V:3.12` |
| `py -V:3.12` says no suitable Python / prints ARM64 | Run the x64 installer from step 1, then open a new PowerShell window |
| `HTTP Error 403` / connection errors on fetch | Check your internet connection or VPN, then try again; ccMixter is sometimes slow |

Stuck? Copy the whole PowerShell output into the chat, like you did before. That's exactly what's needed.
