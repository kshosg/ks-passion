"""Turn what the user typed (and what a transcriber heard) into matchable tokens."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

# A word is letters/digits with optional inner apostrophes ("don't", "rock'n'roll").
# Sentence and clause punctuation is kept only to decide how long to pause.
_TOKEN_RE = re.compile(r"[^\W_]+(?:'[^\W_]+)*|[.!?]+|[,;:–—]")
_APOSTROPHES = str.maketrans({"’": "'", "‘": "'", "`": "'", "ʼ": "'"})

SHORT_PAUSE = "short"
LONG_PAUSE = "long"


class TextTooLong(ValueError):
    """The message is over the character limit for the user's tier."""


@dataclass(frozen=True)
class Token:
    word: str  # normalised form used for matching, e.g. "singapore"
    display: str  # as typed, e.g. "Singapore"
    pause: str = ""  # pause after this word: "", SHORT_PAUSE or LONG_PAUSE


def _fold(text: str) -> str:
    """Lower-case, unify apostrophes and drop accents ("Café" -> "cafe")."""
    text = unicodedata.normalize("NFKD", text.translate(_APOSTROPHES))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return text.lower()


def normalize_words(text: str) -> list[str]:
    """Every matchable word in ``text``, normalised. Punctuation is dropped."""
    return [m.group(0) for m in _TOKEN_RE.finditer(_fold(text)) if m.group(0)[0].isalnum()]


def tokenize(text: str, max_chars: int | None = None) -> list[Token]:
    """Split the user's message into tokens, remembering where punctuation asks for a pause."""
    if max_chars is not None and len(text) > max_chars:
        raise TextTooLong(f"Message is {len(text)} characters; the limit is {max_chars}.")

    tokens: list[Token] = []
    for match in _TOKEN_RE.finditer(text.translate(_APOSTROPHES)):
        raw = match.group(0)
        if raw[0].isalnum():
            tokens.append(Token(word=_fold(raw), display=raw))
        elif tokens:
            pause = LONG_PAUSE if raw[0] in ".!?" else SHORT_PAUSE
            last = tokens[-1]
            if last.pause != LONG_PAUSE:
                tokens[-1] = Token(last.word, last.display, pause)
    return tokens
