"""Licence-check, download and register songs in a library."""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from songspeak.library import Library, Song
from songspeak.licenses import LicensePolicy, parse_license
from songspeak.sources import Candidate, moods_from_tags
from songspeak.sources.http import download as http_download


@dataclass
class CollectReport:
    added: list[Song] = field(default_factory=list)
    skipped: list[tuple[str, str]] = field(default_factory=list)  # (title, reason)


def collect(
    library: Library,
    candidates: list[Candidate],
    policy: LicensePolicy,
    *,
    max_seconds: float | None = 600,
    download=http_download,
    log=print,
) -> CollectReport:
    """Add every candidate whose licence the policy allows. Saves the manifest after each song."""
    report = CollectReport()
    for cand in candidates:
        label = f"{cand.title} - {cand.artist}"
        if cand.song_id in library.songs:
            report.skipped.append((label, "already in library"))
            continue
        lic = parse_license(cand.license)
        if reason := policy.why_not(lic):
            report.skipped.append((label, reason))
            continue
        if max_seconds and cand.seconds and cand.seconds > max_seconds:
            report.skipped.append((label, f"longer than {max_seconds:.0f}s"))
            continue

        rel = f"audio/{cand.song_id}{_suffix(cand.download_url)}"
        try:
            download(cand.download_url, library.root / rel)
        except Exception as exc:  # one bad download shouldn't stop the batch
            report.skipped.append((label, f"download failed: {exc}"))
            continue

        song = Song(
            id=cand.song_id,
            title=cand.title,
            artist=cand.artist,
            audio=rel,
            license=lic.url or lic.code,
            moods=moods_from_tags(cand.tags),
            vocals=rel if cand.a_cappella else None,  # a cappella: the whole file is vocals
            source=cand.source,
            source_url=cand.page_url,
        )
        library.add(song)
        library.save()
        report.added.append(song)
        log(f"+ {label}  [{lic.label}]{'  a cappella' if cand.a_cappella else ''}")
    return report


def add_local(
    library: Library,
    path: Path,
    *,
    title: str,
    artist: str,
    license: str,
    license_note: str = "",
    source_url: str = "",
    moods: list[str] | None = None,
    a_cappella: bool = False,
) -> Song:
    """Copy a royalty-free / CC / owned file you already have into the library."""
    lic = parse_license(license)
    if lic is None:
        raise ValueError(f"Licence {license!r} not recognised. Use a CC URL/code, OWNED, ROYALTY-FREE or PD.")
    if lic.code == "ROYALTY-FREE" and not license_note:
        raise ValueError(
            "Royalty-free licences differ a lot. Add --license-note saying where you bought it and that its terms "
            "allow cutting it up and redistributing excerpts inside an app."
        )
    path = Path(path)
    song_id = "local-" + (re.sub(r"[^a-z0-9]+", "-", f"{artist} {title}".lower()).strip("-") or "track")
    rel = f"audio/{song_id}{path.suffix.lower()}"
    (library.root / "audio").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(path, library.root / rel)
    song = Song(
        id=song_id,
        title=title,
        artist=artist,
        audio=rel,
        license=lic.url or lic.code,
        moods=moods or [],
        vocals=rel if a_cappella else None,
        source="local",
        source_url=source_url,
        license_note=license_note,
    )
    library.add(song)
    library.save()
    return song


def _suffix(url: str) -> str:
    m = re.search(r"\.(mp3|ogg|flac|wav|m4a)(?:$|\?)", url.lower())
    return f".{m.group(1)}" if m else ".mp3"
