"""Where songs come from: Creative Commons catalogues and royalty-free audio you bring yourself.

Every connector turns a catalogue's search results into ``Candidate`` objects; ``collect`` then
checks the licence, downloads the audio and adds it to the library.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Candidate:
    source: str  # "ccmixter", "freesound", ...
    source_id: str
    title: str
    artist: str
    license: str  # URL or name exactly as the catalogue gave it
    page_url: str  # human-readable page, used in attribution
    download_url: str
    tags: list[str] = field(default_factory=list)
    a_cappella: bool = False  # vocals only: no need to separate them from a backing track
    seconds: float | None = None

    @property
    def song_id(self) -> str:
        return f"{self.source}-{self.source_id}"


MOOD_TAGS = {
    "calm": {"calm", "chill", "chillout", "mellow", "ambient", "soft", "relaxing", "acoustic", "lullaby", "downtempo"},
    "upbeat": {"upbeat", "happy", "dance", "funky", "funk", "energetic", "party", "disco", "pop", "uplifting"},
    "romantic": {"love", "romantic", "romance", "sensual", "soul", "rnb", "r&b"},
    "melancholic": {"sad", "melancholy", "melancholic", "dark", "blues", "lonely", "heartbreak"},
    "dramatic": {"epic", "dramatic", "cinematic", "rock", "anthem", "powerful", "intense"},
    "funny": {"funny", "comedy", "silly", "humor", "humour", "novelty"},
    "hiphop": {"hip_hop", "hiphop", "hip-hop", "rap", "spoken_word"},
}


def moods_from_tags(tags: list[str]) -> list[str]:
    tags = {t.strip().lower() for t in tags}
    return sorted(mood for mood, words in MOOD_TAGS.items() if tags & words)
