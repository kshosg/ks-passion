import json
import wave

from songspeak.cli import main
from songspeak.demo import build_demo_library
from songspeak.index import PhraseIndex
from songspeak.library import Library
from songspeak.matcher import plan
from songspeak.render import render
from songspeak.text import tokenize


def test_demo_message_end_to_end(tmp_path):
    library = build_demo_library(tmp_path / "lib")
    library = Library.load(library.root)  # round-trips through the manifest
    segments = plan(tokenize("Hello, everybody. Welcome to Singapore!"), PhraseIndex.from_library(library), library)

    assert [s.text for s in segments] == ["Hello", "everybody", "Welcome to", "Singapore"]
    assert all(s.found for s in segments)
    assert segments[2].song.id == "harbour-lights"

    result = render(segments, library, tmp_path / "msg.wav")
    with wave.open(str(result.path)) as wav:
        seconds = wav.getnframes() / wav.getframerate()
    assert 2.0 < seconds < 5.0
    assert result.missing == []


def test_cli_make_with_missing_word(tmp_path, capsys):
    build_demo_library(tmp_path / "lib")
    out = tmp_path / "out.wav"
    code = main(["make", "Hello Kuala Lumpur", "--library", str(tmp_path / "lib"), "--out", str(out), "--missing", "tone"])
    assert code == 0
    assert out.exists()
    credits = json.loads(out.with_suffix(".credits.json").read_text())
    assert [c["found"] for c in credits] == [True, False, False]
    assert "not in the library yet: Kuala, Lumpur" in capsys.readouterr().out


def test_cli_enforces_free_tier(tmp_path, capsys):
    build_demo_library(tmp_path / "lib")
    assert main(["make", "x" * 301, "--library", str(tmp_path / "lib")]) == 1
    assert main(["make", "hello", "--library", str(tmp_path / "lib"), "--mood", "calm"]) == 1
    assert "premium" in capsys.readouterr().err
