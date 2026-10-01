"""Stitch the planned clips into one audio file and write the credits."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from songspeak import audio
from songspeak.library import Library
from songspeak.licenses import OutputTerms, output_terms
from songspeak.matcher import Segment
from songspeak.text import LONG_PAUSE, SHORT_PAUSE

MISSING_SILENCE = "silence"
MISSING_TONE = "tone"


@dataclass
class RenderSettings:
    pad_before: float = 0.03  # sung consonants start a little before the timestamp
    pad_after: float = 0.07  # and vowels ring a little after it
    fade: float = 0.012
    gap: float = 0.10  # between clips with no punctuation between them
    short_pause: float = 0.30  # after , ; :
    long_pause: float = 0.60  # after . ! ?
    target_dbfs: float = -20.0
    prefer_vocals: bool = True  # use isolated vocals when the library has them
    missing: str = MISSING_SILENCE
    missing_seconds: float = 0.35


@dataclass
class RenderResult:
    path: Path
    seconds: float
    clips: int
    songs: int
    missing: list[str] = field(default_factory=list)


def render(
    segments: list[Segment],
    library: Library,
    out_path: Path,
    settings: RenderSettings | None = None,
    decoded: dict[str, np.ndarray] | None = None,
) -> RenderResult:
    """Write the audio. ``decoded`` can be a long-lived cache of decoded songs (the web server keeps one)."""
    settings = settings or RenderSettings()
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.suffix.lower() == ".wav":
        wav_path = out_path
    else:
        fd, tmp = tempfile.mkstemp(suffix=".wav")
        os.close(fd)  # Windows can't delete a file that still has an open handle
        wav_path = Path(tmp)

    decoded = {} if decoded is None else decoded
    with audio.WavWriter(wav_path) as out:
        for n, seg in enumerate(segments):
            out.write(_clip_for(seg, library, settings, decoded))
            if n < len(segments) - 1:
                out.write(audio.silence(_pause_after(seg, settings)))
        frames = out.frames

    if wav_path != out_path:
        audio.wav_to_mp3(wav_path, out_path)
        wav_path.unlink()

    return RenderResult(
        path=out_path,
        seconds=frames / audio.SR,
        clips=sum(1 for s in segments if s.found),
        songs=len({s.song.id for s in segments if s.song}),
        missing=[s.text for s in segments if not s.found],
    )


def _clip_for(seg: Segment, library: Library, settings: RenderSettings, decoded: dict[str, np.ndarray]) -> np.ndarray:
    if not seg.song:
        if settings.missing == MISSING_TONE:
            return audio.tone(settings.missing_seconds)
        return audio.silence(settings.missing_seconds)
    if seg.song.id not in decoded:
        decoded[seg.song.id] = audio.load_mono(library.audio_path(seg.song, settings.prefer_vocals))
    clip = audio.cut(decoded[seg.song.id], seg.start, seg.end, settings.pad_before, settings.pad_after)
    return audio.fade(audio.level(clip, settings.target_dbfs), settings.fade)


def _pause_after(seg: Segment, settings: RenderSettings) -> float:
    if seg.pause == LONG_PAUSE:
        return settings.long_pause
    if seg.pause == SHORT_PAUSE:
        return settings.short_pause
    return settings.gap


def credits(segments: list[Segment]) -> list[dict]:
    """Which song every clip came from, in playback order. Always shipped with the audio."""
    rows = []
    for seg in segments:
        row = {"text": seg.text, "found": seg.found}
        if seg.song:
            row.update(
                song=seg.song.title,
                artist=seg.song.artist,
                at=f"{_mmss(seg.start)}-{_mmss(seg.end)}",
                license=seg.song.lic.label,
                license_url=seg.song.lic.url,
                source_url=seg.song.source_url,
                confidence=round(seg.confidence, 2),
            )
        rows.append(row)
    return rows


def credits_text(segments: list[Segment]) -> str:
    lines = []
    for row in credits(segments):
        if row["found"]:
            lines.append(f'"{row["text"]}"  <-  {row["song"]} - {row["artist"]} ({row["at"]})')
        else:
            lines.append(f'"{row["text"]}"  <-  not found in library')
    return "\n".join(lines)


def terms(segments: list[Segment]) -> OutputTerms:
    return output_terms([s.song.lic for s in segments if s.song])


def attribution(segments: list[Segment]) -> list[str]:
    """One Creative Commons-style credit (title, author, source, licence) per song used, in order of first use."""
    lines, seen = [], set()
    for seg in segments:
        song = seg.song
        if not song or song.id in seen:
            continue
        seen.add(song.id)
        lic = song.lic
        if not lic.attribution and not song.source_url:
            continue
        line = f'"{song.title}" by {song.artist}'
        if song.source_url:
            line += f" ({song.source_url})"
        line += f", {lic.label}"
        if lic.url:
            line += f" ({lic.url})"
        lines.append(line + ". Excerpts cut and rearranged.")
    return lines


def write_credits(segments: list[Segment], path: Path) -> None:
    payload = {"terms": terms(segments).notice, "attribution": attribution(segments), "clips": credits(segments)}
    Path(path).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _mmss(seconds: float) -> str:
    return f"{int(seconds // 60)}:{seconds % 60:05.2f}"
