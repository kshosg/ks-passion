import pytest

from songspeak.text import LONG_PAUSE, SHORT_PAUSE, TextTooLong, normalize_words, tokenize


def test_tokenize_keeps_display_and_pauses():
    tokens = tokenize("Hello, everybody. Welcome to Singapore!")
    assert [t.word for t in tokens] == ["hello", "everybody", "welcome", "to", "singapore"]
    assert [t.display for t in tokens][-1] == "Singapore"
    assert [t.pause for t in tokens] == [SHORT_PAUSE, LONG_PAUSE, "", "", LONG_PAUSE]


def test_apostrophes_and_accents_are_unified():
    assert normalize_words("Don’t stop, CAFÉ rock-n-roll") == ["don't", "stop", "cafe", "rock", "n", "roll"]


def test_long_pause_wins_over_following_comma():
    tokens = tokenize("Wait!, okay")
    assert tokens[0].pause == LONG_PAUSE


def test_character_limit():
    tokenize("x" * 300, max_chars=300)
    with pytest.raises(TextTooLong):
        tokenize("x" * 301, max_chars=300)
