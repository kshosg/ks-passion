"""Find out which words are sung when: optional vocal isolation, then word-level transcription.

Heavy, optional dependencies (install with `pip install -e .[ingest,vocals]`):
- faster-whisper: speech recognition with per-word timestamps
- demucs: separates vocals from the backing track, which helps transcription a lot and
  gives cleaner clips
"""

from __future__ import annotations

import os
import shutil
import subprocess
import warnings
from pathlib import Path

from songspeak import audio
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
    song.vocals = target.relative_to(library.root).as_posix()  # same manifest on Windows and Mac


def transcribe(path: Path, model_size: str = "small", language: str | None = "en") -> list[Word]:
    """Every sung word with start/end times."""
    # Harmless on Windows, but alarming to read: no symlink support, no Hugging Face login.
    os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
    warnings.filterwarnings("ignore", message=".*unauthenticated requests.*")
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError("faster-whisper is not installed: pip install -e .[ingest]") from exc

    model = _load_model(model_size)
    # Decode with ffmpeg ourselves and pass the samples, rather than letting faster-whisper open the
    # file with PyAV: PyAV 15+ dropped an argument faster-whisper 1.2 still passes (TypeError: metadata_errors).
    samples = audio.load_for_speech(path)
    segments, _ = model.transcribe(samples, language=language, word_timestamps=True)
    words: list[Word] = []
    for seg in segments:
        for w in seg.words or []:
            words.extend(split_word(w.word, w.start, w.end, w.probability))
    return words


_models: dict = {}


def _load_model(model_size: str):
    """Load the Whisper model once per run; the first run ever downloads it."""
    if model_size not in _models:
        from faster_whisper import WhisperModel

        print(f"Loading the '{model_size}' speech model (the first time, this downloads ~0.5 GB; please wait)...")
        _models[model_size] = WhisperModel(model_size, device="auto", compute_type="auto")
    return _models[model_size]


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
    """Transcribe every song that has no transcript yet. Returns how many were processed.

    A song that fails (bad file, decode error) is reported and skipped so the rest of the batch
    still runs; it has no transcript, so the next run tries it again.
    """
    try:
        import faster_whisper  # noqa: F401  (fail once, up front, rather than once per song)
    except ImportError as exc:
        raise RuntimeError("faster-whisper is not installed: pip install -e .[ingest]") from exc

    done, failed = 0, []
    for song in library.songs.values():
        if song.transcript and not force:
            continue
        log(f"Ingesting {song.credit} ...")
        try:
            if isolate and not song.vocals:
                isolate_vocals(library, song)
            words = transcribe(library.audio_path(song, prefer_vocals=True), model_size, language)
        except Exception as exc:  # noqa: BLE001  one bad song shouldn't stop an hour-long batch
            log(f"  failed, skipped: {type(exc).__name__}: {exc}")
            failed.append(song.credit)
            continue
        library.save_transcript(song, words)
        library.save()  # save as we go, so a crash halfway keeps finished songs
        log(f"  {len(words)} words")
        done += 1
    if failed:
        log(f"{len(failed)} song(s) failed and will be retried next run: {', '.join(failed)}")
    return done
