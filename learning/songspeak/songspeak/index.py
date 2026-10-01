"""Phrase index: every 1..N-word run sung in the library, mapped to where it is sung.

Good enough for a few thousand songs held in memory. At catalogue scale this becomes a
words table (song_id, position, word, start, end) in Postgres; see docs/PRODUCT_SPEC.md.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from songspeak.library import Library, Word
from songspeak.licenses import LicensePolicy

MAX_PHRASE = 8


@dataclass(frozen=True)
class Occurrence:
    song_id: str
    first: int  # index of the first word in that song's transcript
    n: int  # number of words


class PhraseIndex:
    def __init__(self, max_phrase: int = MAX_PHRASE):
        self.max_phrase = max_phrase
        self._words: dict[str, list[Word]] = {}
        self._grams: dict[tuple[str, ...], list[Occurrence]] = defaultdict(list)

    @classmethod
    def from_library(
        cls, library: Library, policy: LicensePolicy | None = None, max_phrase: int = MAX_PHRASE
    ) -> "PhraseIndex":
        """Index every song the licence policy allows (by default: commercial-safe licences only)."""
        index = cls(max_phrase)
        for song in library.usable(policy or LicensePolicy()):
            index.add_song(song.id, library.load_transcript(song))
        return index

    def add_song(self, song_id: str, words: list[Word]) -> None:
        words = [w for w in words if w.word]
        self._words[song_id] = words
        sequence = [w.word for w in words]
        for i in range(len(sequence)):
            for n in range(1, min(self.max_phrase, len(sequence) - i) + 1):
                self._grams[tuple(sequence[i : i + n])].append(Occurrence(song_id, i, n))

    def lookup(self, phrase: tuple[str, ...]) -> list[Occurrence]:
        return self._grams.get(phrase, [])

    def span(self, occ: Occurrence) -> tuple[float, float, float]:
        """(start seconds, end seconds, mean confidence) of an occurrence."""
        words = self._words[occ.song_id][occ.first : occ.first + occ.n]
        return words[0].start, words[-1].end, sum(w.prob for w in words) / len(words)

    @property
    def vocabulary_size(self) -> int:
        return sum(1 for gram in self._grams if len(gram) == 1)
