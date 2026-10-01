"""Find out which words are sung when: optional vocal isolation, then word-level transcription.

Heavy, optional dependencies (install with `pip install -e .[ingest,vocals]`):
- faster-whisper: speech recognition with per-word timestamps
- demucs: separates vocals from the backing track, which helps transcription a lot and
  gives cleaner clips
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from songspeak.library import Library, Song, Word
from songspeak.text import normalize_words


def isolate_vocals(library: Library, song: Song, model: str = "htdemucs") -> None:
    """Run Demucs on the song and record the vocals stem in the manifest."""
    if not shutil.which("demucs"):
        raise RuntimeError("demucs is not installed: pip install -e .[vocals]")
    src = library.root / song.audio
    out_dir = library.root / "vocals"
    subprocess.run(["demucs", "--two-stems=vocals", "-n", model, "-o", str(out_dir), str(src)], check=True)
    stem = out_dir / model / src.stem / "vocals.wav"
    target = out_dir / f"{song.id}.wav"
    stem.replace(target)
    song.vocals = str(target.relative_to(library.root))


def transcribe(path: Path, model_size: str = "small", language: str | None = "en") -> list[Word]:
    """Every sung word with start/end times."""
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError("faster-whisper is not installed: pip install -e .[ingest]") from exc

    model = WhisperModel(model_size, device="auto", compute_type="auto")
    segments, _ = model.transcribe(str(path), language=language, word_timestamps=True)
    words: list[Word] = []
    for seg in segments:
        for w in seg.words or []:
            words.extend(split_word(w.word, w.start, w.end, w.probability))
    return words


def split_word(raw: str, start: float, end: float, prob: float) -> list[Word]:
    """Normalise one transcribed item; "rock-n-roll" becomes three words sharing its time."""
    parts = normalize_words(raw)
    if not parts:
        return []
    step = (end - start) / len(parts)
    return [Word(p, start + k * step, start + (k + 1) * step, prob) for k, p in enumerate(parts)]


def ingest(
    library: Library,
    *,
    isolate: bool = False,
    model_size: str = "small",
    language: str | None = "en",
    force: bool = False,
    log=print,
) -> int:
    """Transcribe every song that has no transcript yet. Returns how many were processed."""
    done = 0
    for song in library.songs.values():
        if song.transcript and not force:
            continue
        log(f"Ingesting {song.credit} ...")
        if isolate and not song.vocals:
            isolate_vocals(library, song)
        words = transcribe(library.audio_path(song, prefer_vocals=True), model_size, language)
        library.save_transcript(song, words)
        library.save()  # save as we go, so a crash halfway keeps finished songs
        log(f"  {len(words)} words")
        done += 1
    return done
