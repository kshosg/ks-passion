"""Small audio toolkit: decode, cut, level, write. Mono float32 at 44.1 kHz throughout."""

from __future__ import annotations

import shutil
import subprocess
import wave
from pathlib import Path

import numpy as np

SR = 44_100


def load_mono(path: Path) -> np.ndarray:
    """Decode any audio file to mono float32 in [-1, 1] at SR."""
    path = Path(path)
    if path.suffix.lower() == ".wav":
        with wave.open(str(path), "rb") as wav:
            if wav.getsampwidth() == 2 and wav.getframerate() == SR:
                data = np.frombuffer(wav.readframes(wav.getnframes()), dtype="<i2").astype(np.float32) / 32768.0
                return data.reshape(-1, wav.getnchannels()).mean(axis=1)
    return _ffmpeg_decode(path)


def _ffmpeg_decode(path: Path) -> np.ndarray:
    if not shutil.which("ffmpeg"):
        raise RuntimeError(f"ffmpeg is needed to read {path.name}; install it or convert to 16-bit 44.1 kHz WAV.")
    cmd = ["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"]
    raw = subprocess.run(cmd, check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype="<f4").copy()


def cut(samples: np.ndarray, start: float, end: float, pad_before: float, pad_after: float) -> np.ndarray:
    a = max(0, int((start - pad_before) * SR))
    b = min(len(samples), int((end + pad_after) * SR))
    return samples[a:b].copy()


def fade(clip: np.ndarray, seconds: float) -> np.ndarray:
    """Short fade in/out so cuts don't click."""
    n = min(int(seconds * SR), len(clip) // 2)
    if n > 0:
        ramp = np.linspace(0.0, 1.0, n, dtype=np.float32)
        clip[:n] *= ramp
        clip[-n:] *= ramp[::-1]
    return clip


def level(clip: np.ndarray, target_dbfs: float) -> np.ndarray:
    """Bring a clip to a common loudness (RMS), never letting peaks clip."""
    rms = float(np.sqrt(np.mean(np.square(clip)))) if len(clip) else 0.0
    if rms < 1e-6:
        return clip
    gain = 10 ** (target_dbfs / 20) / rms
    peak = float(np.max(np.abs(clip)))
    gain = min(gain, 0.98 / peak)
    return clip * gain


def silence(seconds: float) -> np.ndarray:
    return np.zeros(int(seconds * SR), dtype=np.float32)


def tone(seconds: float, freq: float = 1000.0, dbfs: float = -24.0) -> np.ndarray:
    """A soft beep, used in place of a word no song in the library sings."""
    t = np.arange(int(seconds * SR), dtype=np.float32) / SR
    return fade(np.sin(2 * np.pi * freq * t).astype(np.float32) * 10 ** (dbfs / 20), 0.01)


class WavWriter:
    """Streams mono 16-bit WAV to disk, so a 30,000-character premium render needn't fit in memory."""

    def __init__(self, path: Path):
        self._wav = wave.open(str(path), "wb")
        self._wav.setnchannels(1)
        self._wav.setsampwidth(2)
        self._wav.setframerate(SR)
        self.frames = 0

    def write(self, samples: np.ndarray) -> None:
        pcm = (np.clip(samples, -1.0, 1.0) * 32767).astype("<i2")
        self._wav.writeframes(pcm.tobytes())
        self.frames += len(pcm)

    def close(self) -> None:
        self._wav.close()

    def __enter__(self) -> "WavWriter":
        return self

    def __exit__(self, *exc) -> None:
        self.close()


def wav_to_mp3(wav_path: Path, mp3_path: Path) -> None:
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg is needed for MP3 output.")
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(wav_path), "-codec:a", "libmp3lame", "-q:a", "2", str(mp3_path)]
    subprocess.run(cmd, check=True)
