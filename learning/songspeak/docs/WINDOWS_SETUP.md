# Running SongSpeak on Windows — step by step

For a first project on Windows PowerShell. Type each line, press Enter, and wait for it to finish before typing the next.
Lines starting with `#` are notes. Don't type them.

## One-time setup (about 15 minutes)

### 1. Check Python

```powershell
python --version
```
You need **3.10 or newer**. 3.12 is the safest choice. If the Microsoft Store opens or you get an error, install Python from
https://www.python.org/downloads/ and **tick "Add python.exe to PATH"** on the first installer screen. Then close and reopen PowerShell.

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
python -m venv .venv
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
| `faster-whisper` fails to install | Use Python 3.12: install it, delete the `.venv` folder, and redo steps 4–5 |
| `HTTP Error 403` / connection errors on fetch | Check your internet connection or VPN, then try again; ccMixter is sometimes slow |

Stuck? Copy the whole PowerShell output into the chat, like you did before. That's exactly what's needed.
