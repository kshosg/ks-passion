"""One place that turns a request into audio + credits; used by both the CLI and the web app."""

from __future__ import annotations

import threading
from collections import Counter, OrderedDict
from dataclasses import dataclass
from pathlib import Path

from songspeak.index import PhraseIndex
from songspeak.library import Library
from songspeak.licenses import LicensePolicy
from songspeak.matcher import Segment, plan
from songspeak.render import RenderResult, RenderSettings, attribution, credits, render, terms
from songspeak.text import tokenize
from songspeak.tiers import MIX_VARIETY, Tier, TierError, check_request

DECODED_CACHE_SONGS = 64  # decoded songs kept in memory between requests (~10 MB each)


@dataclass
class Made:
    segments: list[Segment]
    result: RenderResult

    def to_dict(self) -> dict:
        t = terms(self.segments)
        return {
            "seconds": round(self.result.seconds, 2),
            "clips": self.result.clips,
            "songs": self.result.songs,
            "missing": self.result.missing,
            "segments": credits(self.segments),
            "attribution": attribution(self.segments),
            "terms": t.notice,
            "terms_conflict": t.conflict,
        }


class _LRU(OrderedDict):
    def __init__(self, size: int):
        super().__init__()
        self.size = size

    def __getitem__(self, key):
        self.move_to_end(key)
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.move_to_end(key)
        while len(self) > self.size:
            self.popitem(last=False)


class Studio:
    def __init__(self, library: Library, policy: LicensePolicy | None = None):
        self.library = library
        self.policy = policy or LicensePolicy()
        self.index = PhraseIndex.from_library(library, self.policy)
        self._decoded = _LRU(DECODED_CACHE_SONGS)
        self._lock = threading.Lock()

    def check(self, tier: Tier, mood: str | None, mix: str) -> None:
        check_request(tier, mood, mix)
        if tier.name != "free" and self.policy.allow_noncommercial:
            raise TierError("Paid renders can't use non-commercial (NC) songs; turn off --allow-nc.")

    def make(
        self,
        message: str,
        out_path: Path,
        tier: Tier,
        *,
        mood: str | None = None,
        mix: str = MIX_VARIETY,
        seed: int | None = None,
        settings: RenderSettings | None = None,
    ) -> Made:
        self.check(tier, mood, mix)
        tokens = tokenize(message, tier.max_chars)
        if not tokens:
            raise ValueError("The message has no words in it.")
        segments = plan(tokens, self.index, self.library, mood=mood, mix=mix, seed=seed)
        with self._lock:  # the decoded-audio cache isn't thread-safe
            result = render(segments, self.library, out_path, settings, self._decoded)
        return Made(segments, result)

    def stats(self) -> dict:
        usable = self.library.usable(self.policy)
        return {
            "songs": len(self.library.songs),
            "usable_songs": len(usable),
            "transcribed": sum(1 for s in usable if s.transcript),
            "vocabulary": self.index.vocabulary_size,
            "licenses": dict(Counter(s.lic.label for s in usable).most_common()),
            "sources": dict(Counter(s.source for s in usable).most_common()),
            "moods": sorted({m for s in usable for m in s.moods}),
        }
