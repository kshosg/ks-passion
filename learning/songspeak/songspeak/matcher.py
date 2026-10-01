"""Decide which sung phrase covers which part of the message.

Two steps:
1. Segmentation (dynamic programming): split the message into the fewest clips, so longer
   sung phrases win over word-by-word stitching. A clip never runs across punctuation,
   so commas and full stops keep their pauses. Words nobody sings cost far more than an
   extra clip, so they are only left unmatched when there is no other way.
2. Casting: for each phrase, choose which song to take it from: confident transcription,
   not a held note, the requested mood, and the requested mix (variety or few songs).
"""

from __future__ import annotations

import random
from collections import Counter
from dataclasses import dataclass

from songspeak.index import Occurrence, PhraseIndex
from songspeak.library import Library, Song
from songspeak.text import Token
from songspeak.tiers import MIX_FEWEST_SONGS, MIX_VARIETY

CLIP_COST = 1.0
MISSING_COST = 10.0
MOOD_BONUS = 0.5
REUSE_WEIGHT = 0.4
SPEECHLIKE_SECONDS_PER_WORD = 0.8  # longer than this per word is probably a held note
HELD_NOTE_PENALTY = 0.3


@dataclass
class Segment:
    tokens: list[Token]
    song: Song | None = None  # None: nobody in the library sings this word
    start: float = 0.0
    end: float = 0.0
    confidence: float = 0.0

    @property
    def text(self) -> str:
        return " ".join(t.display for t in self.tokens)

    @property
    def pause(self) -> str:
        return self.tokens[-1].pause

    @property
    def found(self) -> bool:
        return self.song is not None


def segment(tokens: list[Token], index: PhraseIndex) -> list[tuple[int, int, bool]]:
    """Fewest-clips split of ``tokens`` into (start, length, found) runs."""
    n = len(tokens)
    best = [0.0] * (n + 1)
    choice: list[tuple[int, bool]] = [(1, False)] * (n + 1)
    for i in range(n - 1, -1, -1):
        best[i], choice[i] = MISSING_COST + best[i + 1], (1, False)
        for length in range(1, min(index.max_phrase, n - i) + 1):
            if length > 1 and tokens[i + length - 2].pause:
                break  # don't sing straight through a comma or full stop
            if index.lookup(tuple(t.word for t in tokens[i : i + length])):
                cost = CLIP_COST + best[i + length]
                if cost <= best[i]:  # ties go to the longer phrase
                    best[i], choice[i] = cost, (length, True)

    runs, i = [], 0
    while i < n:
        length, found = choice[i]
        runs.append((i, length, found))
        i += length
    return runs


def plan(
    tokens: list[Token],
    index: PhraseIndex,
    library: Library,
    *,
    mood: str | None = None,
    mix: str = MIX_VARIETY,
    seed: int | None = None,
) -> list[Segment]:
    """Turn the message into an ordered list of clips to play."""
    rng = random.Random(seed) if seed is not None else None
    used: Counter[str] = Counter()
    segments: list[Segment] = []

    for i, length, found in segment(tokens, index):
        seg = Segment(tokens[i : i + length])
        if found:
            phrase = tuple(t.word for t in seg.tokens)
            occ = max(
                index.lookup(phrase),
                key=lambda o: (_score(o, index, library, used, mood, mix, rng), o.song_id, -o.first),
            )
            seg.song = library.songs[occ.song_id]
            seg.start, seg.end, seg.confidence = index.span(occ)
            used[occ.song_id] += 1
        segments.append(seg)
    return segments


def _score(
    occ: Occurrence,
    index: PhraseIndex,
    library: Library,
    used: Counter[str],
    mood: str | None,
    mix: str,
    rng: random.Random | None,
) -> float:
    start, end, confidence = index.span(occ)
    score = confidence
    seconds_per_word = (end - start) / occ.n
    score -= HELD_NOTE_PENALTY * max(0.0, seconds_per_word - SPEECHLIKE_SECONDS_PER_WORD)
    if mood and mood in library.songs[occ.song_id].moods:
        score += MOOD_BONUS
    reuse = used[occ.song_id]
    if mix == MIX_VARIETY:
        score -= REUSE_WEIGHT * reuse
    elif mix == MIX_FEWEST_SONGS and reuse:
        score += REUSE_WEIGHT
    if rng is not None:  # "shuffle": same message, different songs
        score += rng.uniform(0.0, 0.3)
    return score
