import pytest

from songspeak.index import PhraseIndex
from songspeak.library import Library, Song, Word
from songspeak.matcher import plan
from songspeak.text import normalize_words, tokenize
from songspeak.tiers import FREE, MIX_FEWEST_SONGS, PREMIUM, TierError, check_request


def _words(line, seconds_per_word=0.4, prob=0.9):
    return [Word(w, i * 0.5, i * 0.5 + seconds_per_word, prob) for i, w in enumerate(normalize_words(line))]


def _setup(songs):
    """songs: (id, moods, line[, seconds_per_word])"""
    library = Library("/nonexistent", [Song(s[0], s[0].title(), "Artist", f"{s[0]}.wav", "CC0-1.0", list(s[1])) for s in songs])
    index = PhraseIndex()
    for s in songs:
        index.add_song(s[0], _words(s[2], *s[3:]))
    return library, index


def _make(text, library, index, **kw):
    return plan(tokenize(text), index, library, **kw)


def test_prefers_longest_sung_phrase():
    library, index = _setup([("a", [], "hello there"), ("b", [], "welcome"), ("c", [], "welcome to singapore")])
    segs = _make("welcome to singapore", library, index)
    assert [(s.text, s.song.id) for s in segs] == [("welcome to singapore", "c")]


def test_phrases_do_not_run_through_punctuation():
    library, index = _setup([("a", [], "hello everybody"), ("b", [], "hello"), ("c", [], "everybody")])
    segs = _make("Hello, everybody", library, index)
    assert [s.text for s in segs] == ["Hello", "everybody"]


def test_unknown_words_are_reported_not_dropped():
    library, index = _setup([("a", [], "hello world")])
    segs = _make("hello zyzzyva world", library, index)
    assert [(s.text, s.found) for s in segs] == [("hello", True), ("zyzzyva", False), ("world", True)]


def test_variety_spreads_words_across_songs():
    library, index = _setup([("a", [], "one two three"), ("b", [], "one two three")])
    segs = _make("one, two, three", library, index)
    assert len({s.song.id for s in segs}) == 2


def test_fewest_songs_sticks_to_one_song():
    library, index = _setup([("a", [], "one two three"), ("b", [], "one two three")])
    segs = _make("one, two, three", library, index, mix=MIX_FEWEST_SONGS)
    assert len({s.song.id for s in segs}) == 1


def test_mood_preference():
    library, index = _setup([("calm", ["calm"], "hello"), ("loud", ["upbeat"], "hello")])
    assert _make("hello", library, index, mood="upbeat")[0].song.id == "loud"
    assert _make("hello", library, index, mood="calm")[0].song.id == "calm"


def test_avoids_long_held_notes():
    library, index = _setup([("held", [], "hello", 3.0, 0.99), ("short", [], "hello", 0.4, 0.9)])
    assert _make("hello", library, index)[0].song.id == "short"


def test_tier_rules():
    check_request(PREMIUM, "upbeat", MIX_FEWEST_SONGS)
    with pytest.raises(TierError):
        check_request(FREE, "upbeat", "variety")
    with pytest.raises(TierError):
        check_request(FREE, None, MIX_FEWEST_SONGS)
