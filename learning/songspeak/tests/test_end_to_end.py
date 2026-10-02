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
    assert [c["found"] for c in credits["clips"]] == [True, False, False]
    assert "not in the library yet: Kuala, Lumpur" in capsys.readouterr().out


def test_cli_enforces_free_tier(tmp_path, capsys):
    build_demo_library(tmp_path / "lib")
    assert main(["make", "x" * 301, "--library", str(tmp_path / "lib")]) == 1
    assert main(["make", "hello", "--library", str(tmp_path / "lib"), "--mood", "calm"]) == 1
    assert "premium" in capsys.readouterr().err


def test_ingest_feeds_decoded_audio_to_the_model(tmp_path, monkeypatch):
    """faster-whisper gets 16 kHz samples, never a file path (its own PyAV decoding breaks with new PyAV)."""
    import sys
    import types

    import numpy as np

    from songspeak import ingest

    seen = {}

    class FakeModel:
        def transcribe(self, audio, language=None, word_timestamps=False):
            seen["audio"] = audio
            word = types.SimpleNamespace(word=" Hello,", start=1.0, end=1.4, probability=0.9)
            return [types.SimpleNamespace(words=[word])], None

    monkeypatch.setitem(sys.modules, "faster_whisper", types.SimpleNamespace(WhisperModel=None))
    monkeypatch.setitem(ingest._models, "small", FakeModel())
    library = build_demo_library(tmp_path / "lib")
    song = library.songs["late-train"]

    words = ingest.transcribe(library.audio_path(song))
    assert isinstance(seen["audio"], np.ndarray) and seen["audio"].dtype == np.float32
    seconds = len(seen["audio"]) / 16_000
    with wave.open(str(library.audio_path(song))) as wav:
        assert abs(seconds - wav.getnframes() / wav.getframerate()) < 0.05
    assert [(w.word, w.start) for w in words] == [("hello", 1.0)]


def test_ingest_skips_a_failing_song_and_carries_on(tmp_path, monkeypatch):
    import sys
    import types

    from songspeak import ingest

    library = build_demo_library(tmp_path / "lib")
    for song in library.songs.values():
        song.transcript = None
    calls = []

    def fake_transcribe(path, model_size, language):
        calls.append(path.name)
        if "night-market" in path.name:
            raise RuntimeError("could not decode")
        return []

    monkeypatch.setitem(sys.modules, "faster_whisper", types.SimpleNamespace())
    monkeypatch.setattr(ingest, "transcribe", fake_transcribe)
    log = []
    assert ingest.ingest(library, log=log.append) == 4
    assert len(calls) == 5
    assert any("failed, skipped: RuntimeError: could not decode" in line for line in log)
    assert Library.load(library.root).songs["night-market"].transcript is None


def test_ingest_drops_words_whisper_made_up(tmp_path, monkeypatch):
    import sys
    import types

    from songspeak import ingest

    def w(text, prob):
        return types.SimpleNamespace(word=text, start=1.0, end=1.3, probability=prob)

    class FakeModel:
        def transcribe(self, audio, language=None, word_timestamps=False):
            sung = types.SimpleNamespace(words=[w(" hello", 0.9), w(" mumble", 0.05)], no_speech_prob=0.1, avg_logprob=-0.3)
            noise = types.SimpleNamespace(words=[w(" thank", 0.6), w(" you", 0.6)], no_speech_prob=0.9, avg_logprob=-1.4)
            return [sung, noise], None

    monkeypatch.setitem(sys.modules, "faster_whisper", types.SimpleNamespace(WhisperModel=None))
    monkeypatch.setitem(ingest._models, "small", FakeModel())
    library = build_demo_library(tmp_path / "lib")
    words = ingest.transcribe(library.audio_path(library.songs["late-train"]))
    assert [x.word for x in words] == ["hello"]
