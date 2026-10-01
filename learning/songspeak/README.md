# SongSpeak

Type a message, and SongSpeak builds it out of words sung in **Creative Commons and royalty-free songs**.
It gives you the audio, the credits, and the licence terms the finished clip must be shared under.

```
"Hello"       <-  Paper Lanterns - Demo Band A (0:01.00-0:01.32)
"everybody"   <-  Night Market - Demo Band B   (0:01.00-0:01.32)
"Welcome to"  <-  Harbour Lights - Demo Band C (0:01.00-0:01.78)
"Singapore"   <-  Merlion Skies - Demo Band D  (0:03.30-0:03.62)
```

Product thinking, legal reality check and roadmap: **[docs/PRODUCT_SPEC.md](docs/PRODUCT_SPEC.md)**.

> **On Windows?** Follow **[docs/WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md)**: it covers installing Python, Git and FFmpeg step by step. The commands below are for Mac/Linux.

## Quick start (no downloads needed)

Needs Python 3.10+ and `ffmpeg` (for MP3 files).

```bash
cd learning/songspeak
pip install -e .[dev,web]
pytest                                              # 28 tests
songspeak demo                                      # synthetic library -> out/demo/message.wav
songspeak serve --library out/demo/library          # web app on http://127.0.0.1:8000
```

The demo library is generated tones with invented words, so it runs anywhere.

## Build a real Creative Commons library

```bash
pip install -e .[ingest]                          # faster-whisper for word timestamps (~0.5 GB model download)
export FREESOUND_API_KEY=...                      # optional, free: https://freesound.org/apiv2/apply
scripts/build_cc_library.sh library 3             # 60 ccMixter a cappellas + Freesound sung words, ingest, stats
songspeak serve --library library
```

Or step by step:

```bash
songspeak fetch ccmixter  --library library --limit 20                      # a cappellas, no key needed
songspeak fetch ccmixter  --library library --tags acappella,female_vocals --offset 20
songspeak fetch freesound --library library --query "sung word" --limit 30   # CC0 / CC BY clips
songspeak add pack/hello.wav --library library --title "Hello (vocal one-shot)" --artist "Pack Name" \
    --license ROYALTY-FREE --license-note "Bought from <store> on <date>; licence allows app use" --a-cappella
songspeak ingest --library library                # transcribe everything new
songspeak stats  --library library --coverage docs/starter-words.txt
songspeak make "Hello, everybody. Welcome to Singapore!" --library library --out out/hello.mp3
```

### Licence rules (enforced in code)

Cutting a song into words and rearranging them makes an **adaptation**, so:

| Licence | Used? | What the output owes |
|---|---|---|
| CC0, Public domain, Owned | ✅ always | nothing (credits shown anyway) |
| CC BY | ✅ always | credit: title, artist, link, licence |
| CC BY-SA | ✅ always | credit, **and the output must be shared under CC BY-SA 4.0** |
| CC BY-NC / BY-NC-SA | ⚠️ only with `--allow-nc` (personal mode), **never** on the premium tier | credit; non-commercial use only |
| CC BY-ND / BY-NC-ND | ❌ never: ND forbids remixing | — |
| Royalty-free (bought) | ✅ if you add it with `--license-note` stating its terms allow this | whatever that licence says |
| Unknown | ❌ refused | — |

Every render writes a `.credits.json` file with the terms notice and a ready-to-paste attribution list. The web page has a "Copy credits" button.

Most ccMixter a cappellas are **CC BY-NC**, so a commercial-safe library is smaller. Run `stats` with and without `--allow-nc` to compare.

## Commands

| Command | Does |
|---|---|
| `make` | message → audio + credits (`--tier`, `--mood`, `--mix`, `--seed` to shuffle, `--allow-nc`) |
| `fetch ccmixter / freesound` | search, licence-check, download, add to the library |
| `add` | add a royalty-free / CC / owned file you already have |
| `ingest` | transcribe new songs (`--isolate-vocals` for full mixes; not needed for a cappellas) |
| `stats` | songs, licences, moods, vocabulary, and coverage of a word list |
| `search` | where a word or phrase is sung |
| `serve` | the web app |
| `demo` | synthetic library + example render |

## Code map

| File | Job |
|---|---|
| `songspeak/text.py` | Normalise the message, keep punctuation as pauses, enforce the character limit |
| `songspeak/licenses.py` | Parse CC/other licences, the usage policy, output terms |
| `songspeak/library.py` | Manifest, songs, transcripts |
| `songspeak/sources/` | `ccmixter.py`, `freesound.py` connectors; `collect.py` downloads and registers songs |
| `songspeak/ingest.py` | Demucs vocal isolation + faster-whisper word timestamps |
| `songspeak/index.py` | Every 1–8-word sung phrase → where it is sung (licence-filtered) |
| `songspeak/matcher.py` | Fewest-clips segmentation, then choose a song for each clip (confidence, mood, mix, shuffle) |
| `songspeak/render.py` | Cut, level, fade, pause, stream to WAV/MP3; credits and attribution |
| `songspeak/studio.py` | Request → audio + credits, shared by the CLI and web |
| `songspeak/web.py`, `static/index.html` | FastAPI app and the single-page UI |
| `songspeak/tiers.py` | Free (300 chars) vs premium (30,000 chars, moods, mix modes) |

Audio and libraries are git-ignored. Don't commit songs.
