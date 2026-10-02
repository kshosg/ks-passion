"""The song library: a folder with a manifest, audio files and word-level transcripts.

library/
  manifest.json          songs + metadata (title, artist, licence, moods)
  audio/...              the full mix of each song
  vocals/...             optional isolated vocals (cleaner clips)
  transcripts/<id>.json  every sung word with start/end times, written by `songspeak ingest`
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from songspeak.licenses import License, LicensePolicy, parse_license

MANIFEST = "manifest.json"


@dataclass
class Song:
    id: str
    title: str
    artist: str
    audio: str  # path relative to the library root
    license: str  # CC URL, SPDX-style code or OWNED / ROYALTY-FREE / PD (see licenses.py)
    moods: list[str] = field(default_factory=list)
    vocals: str | None = None
    transcript: str | None = None
    source: str = "local"  # where it came from: ccmixter, freesound, local, demo
    source_url: str = ""  # the page we got it from, for attribution
    license_note: str = ""  # e.g. where a royalty-free licence was bought and what it allows

    @property
    def credit(self) -> str:
        return f"{self.title} - {self.artist}"

    @property
    def lic(self) -> License:
        lic = parse_license(self.license)
        assert lic is not None, "validated when the library loads"
        return lic


@dataclass
class Word:
    word: str  # normalised (see text.normalize_words)
    start: float  # seconds
    end: float
    prob: float = 1.0  # transcriber confidence, 0..1


class Library:
    def __init__(self, root: Path, songs: list[Song]):
        self.root = Path(root)
        self.songs: dict[str, Song] = {}
        for song in songs:
            self.add(song)

    def add(self, song: Song) -> None:
        if parse_license(song.license) is None:
            raise ValueError(
                f"Song {song.id!r} has licence {song.license!r}, which isn't recognised. "
                "Use a Creative Commons URL/code, OWNED, ROYALTY-FREE or PD."
            )
        if song.id in self.songs:
            raise ValueError(f"Duplicate song id {song.id!r}")
        self.songs[song.id] = song

    def remove(self, song_id: str) -> Song:
        """Take a song out of the library and delete its audio, vocals and transcript files."""
        song = self.songs.pop(song_id)
        for rel in {song.audio, song.vocals, song.transcript} - {None}:
            (self.root / rel).unlink(missing_ok=True)
        return song

    def usable(self, policy: LicensePolicy) -> list[Song]:
        """Songs whose licence allows remixing under this policy."""
        return [s for s in self.songs.values() if policy.allows(s.lic)]

    @classmethod
    def load(cls, root: Path | str) -> "Library":
        root = Path(root)
        data = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
        return cls(root, [Song(**entry) for entry in data["songs"]])

    def save(self) -> None:
        data = {"songs": [asdict(s) for s in self.songs.values()]}
        (self.root / MANIFEST).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    def audio_path(self, song: Song, prefer_vocals: bool = True) -> Path:
        if prefer_vocals and song.vocals and (self.root / song.vocals).exists():
            return self.root / song.vocals
        return self.root / song.audio

    def load_transcript(self, song: Song) -> list[Word]:
        if not song.transcript:
            return []
        data = json.loads((self.root / song.transcript).read_text(encoding="utf-8"))
        return [Word(**w) for w in data["words"]]

    def save_transcript(self, song: Song, words: list[Word]) -> None:
        song.transcript = song.transcript or f"transcripts/{song.id}.json"
        path = self.root / song.transcript
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"song_id": song.id, "words": [asdict(w) for w in words]}
        path.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
