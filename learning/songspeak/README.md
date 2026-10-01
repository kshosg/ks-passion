# SongSpeak

Type a message, and SongSpeak builds it out of words sung in songs, then gives you the audio and a credits list.

```
"Hello"       <-  Paper Lanterns - Demo Band A (0:01.00-0:01.32)
"everybody"   <-  Night Market - Demo Band B   (0:01.00-0:01.32)
"Welcome to"  <-  Harbour Lights - Demo Band C (0:01.00-0:01.78)
"Singapore"   <-  Merlion Skies - Demo Band D  (0:03.30-0:03.62)
```

Product thinking, legal reality check and roadmap: **[docs/PRODUCT_SPEC.md](docs/PRODUCT_SPEC.md)**.

## Quick start

Needs Python 3.10+ and `ffmpeg` (only for MP3 files and non-WAV input).

```bash
cd learning/songspeak
pip install -e .[dev]
pytest                     # 15 tests
songspeak demo             # builds a synthetic library, writes out/demo/message.wav
```

The demo uses generated tones, not real songs, so it runs anywhere with no downloads or models.

## Using a real library

1. Create a library folder with `manifest.json` (every song **must** record its licence):

   ```json
   {
     "songs": [
       {
         "id": "harbour-lights",
         "title": "Harbour Lights",
         "artist": "Some Artist",
         "audio": "audio/harbour-lights.mp3",
         "license": "CC-BY-4.0 (ccMixter, link...)",
         "moods": ["calm"]
       }
     ]
   }
   ```

2. Transcribe it (installs Whisper and Demucs, which are large):

   ```bash
   pip install -e .[ingest,vocals]
   songspeak ingest --library my-library --isolate-vocals --model small
   ```

3. Make audio:

   ```bash
   songspeak make "Hello, everybody. Welcome to Singapore!" --library my-library --out out/hello.mp3
   songspeak make "..." --library my-library --seed 7               # shuffle: different songs
   songspeak make --file speech.txt --library my-library --tier premium --mood upbeat --mix fewest-songs
   songspeak search "welcome to" --library my-library               # where is this sung?
   ```

## Code map

| File | Job |
|---|---|
| `songspeak/text.py` | Normalise the message, keep punctuation as pauses, enforce the character limit |
| `songspeak/library.py` | Manifest, songs, transcripts |
| `songspeak/ingest.py` | Demucs vocal isolation + faster-whisper word timestamps |
| `songspeak/index.py` | Every 1–8-word sung phrase → where it is sung |
| `songspeak/matcher.py` | Fewest-clips segmentation, then choose a song for each clip (confidence, mood, mix, shuffle) |
| `songspeak/render.py` | Cut, level, fade, pause, stream to WAV/MP3, credits |
| `songspeak/tiers.py` | Free (300 chars) vs premium (30,000 chars, moods, mix modes) |
| `songspeak/demo.py` | Synthetic library for the demo and tests |

Audio is git-ignored. Don't commit songs: they're large and usually someone else's copyright.
