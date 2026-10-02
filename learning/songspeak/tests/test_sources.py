import pytest

from songspeak.index import PhraseIndex
from songspeak.library import Library, Word
from songspeak.licenses import LicensePolicy
from songspeak.sources import ccmixter, freesound, moods_from_tags
from songspeak.sources.collect import add_local, collect

# Shaped like ccMixter's /api/query?f=json output (titles and artists invented).
CCMIXTER_RESULTS = [
    {
        "upload_id": 1001, "upload_name": "Lantern Song (a cappella)", "user_name": "vox1", "user_real_name": "Vox One",
        "file_page_url": "http://ccmixter.org/files/vox1/1001",
        "license_url": "http://creativecommons.org/licenses/by/3.0/",
        "upload_tags": ",acappella,female_vocals,chill,",
        "upload_extra": {"usertags": "acappella,chill", "systags": "media,audio"},
        "files": [{"download_url": "http://ccmixter.org/content/vox1/vox1_-_Lantern_Song.mp3",
                   "file_name": "vox1_-_Lantern_Song.mp3",
                   "file_format_info": {"mime_type": "audio/mpeg", "ps": "2:31"}}],
    },
    {
        "upload_id": 1002, "upload_name": "Night Bus", "user_name": "vox2",
        "license_url": "http://creativecommons.org/licenses/by-nc/3.0/",
        "upload_tags": "acappella,male_vocals,upbeat",
        "files": [{"download_url": "http://ccmixter.org/content/vox2/night.mp3", "file_name": "night.mp3",
                   "file_format_info": {"mime_type": "audio/mpeg", "ps": "3:02"}}],
    },
    {
        "upload_id": 1003, "upload_name": "No Remix Please", "user_name": "vox3",
        "license_url": "http://creativecommons.org/licenses/by-nd/3.0/",
        "upload_tags": "acappella",
        "files": [{"download_url": "http://ccmixter.org/content/vox3/x.mp3", "file_name": "x.mp3", "file_format_info": {}}],
    },
    {"upload_id": 1004, "upload_name": "Zip only", "license_url": "http://creativecommons.org/licenses/by/3.0/",
     "files": [{"download_url": "http://ccmixter.org/content/x.zip", "file_name": "x.zip", "file_format_info": {"mime_type": "application/zip"}}]},
]

FREESOUND_RESULTS = {"results": [
    {"id": 555, "name": "sung word - welcome", "username": "singer_sg",
     "license": "http://creativecommons.org/publicdomain/zero/1.0/", "url": "https://freesound.org/people/singer_sg/sounds/555/",
     "tags": ["singing", "voice", "word"], "duration": 1.4,
     "previews": {"preview-hq-mp3": "https://cdn.freesound.org/previews/0/555-hq.mp3"}},
]}


def _fake_download(url, dest, referer=None):
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(b"ID3fake")


def test_ccmixter_parsing():
    params_seen = {}
    cands = ccmixter.search(fetch=lambda url, params: params_seen.update(params) or CCMIXTER_RESULTS)
    assert params_seen["tags"] == "acappella" and params_seen["f"] == "json"
    assert [c.song_id for c in cands] == ["ccmixter-1001", "ccmixter-1002", "ccmixter-1003"]  # zip-only dropped
    first = cands[0]
    assert first.artist == "Vox One" and first.a_cappella and first.seconds == 151
    assert first.download_url.endswith(".mp3")


def test_freesound_parsing_and_key(monkeypatch):
    monkeypatch.delenv("FREESOUND_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="API key"):
        freesound.search()
    cands = freesound.search(api_key="k", fetch=lambda url, params: FREESOUND_RESULTS)
    assert cands[0].song_id == "freesound-555" and cands[0].a_cappella
    assert cands[0].download_url.endswith("555-hq.mp3")


def test_collect_applies_licence_policy(tmp_path):
    library = Library(tmp_path, [])
    cands = ccmixter.search(fetch=lambda url, params: CCMIXTER_RESULTS)
    report = collect(library, cands, LicensePolicy(), download=_fake_download, log=lambda *_: None)
    assert [s.id for s in report.added] == ["ccmixter-1001"]
    reasons = dict(report.skipped)
    assert "non-commercial" in reasons["Night Bus - vox2"]
    assert "forbids remixing" in reasons["No Remix Please - vox3"]

    song = Library.load(tmp_path).songs["ccmixter-1001"]
    assert song.vocals == song.audio  # a cappella: no separation needed
    assert song.moods == ["calm"] and song.source_url.endswith("/1001")
    assert (tmp_path / song.audio).exists()

    # personal mode picks up the NC track; running again doesn't duplicate
    report = collect(library, cands, LicensePolicy(allow_noncommercial=True), download=_fake_download, log=lambda *_: None)
    assert [s.id for s in report.added] == ["ccmixter-1002"]


def test_nc_songs_are_not_indexed_by_default(tmp_path):
    library = Library(tmp_path, [])
    cands = ccmixter.search(fetch=lambda url, params: CCMIXTER_RESULTS)
    collect(library, cands, LicensePolicy(allow_noncommercial=True), download=_fake_download, log=lambda *_: None)
    for song in library.songs.values():
        library.save_transcript(song, [Word("hello", 1.0, 1.4)])
    assert len(PhraseIndex.from_library(library).lookup(("hello",))) == 1
    assert len(PhraseIndex.from_library(library, LicensePolicy(allow_noncommercial=True)).lookup(("hello",))) == 2


def test_add_local_royalty_free_needs_a_note(tmp_path):
    src = tmp_path / "pack.wav"
    src.write_bytes(b"RIFF")
    library = Library(tmp_path / "lib", [])
    with pytest.raises(ValueError, match="license-note"):
        add_local(library, src, title="Hey", artist="Pack", license="ROYALTY-FREE")
    with pytest.raises(ValueError, match="not recognised"):
        add_local(library, src, title="Hey", artist="Pack", license="all rights reserved")
    song = add_local(library, src, title="Hey", artist="Pack", license="ROYALTY-FREE",
                     license_note="Bought from X; licence allows app use", a_cappella=True)
    assert song.id == "local-pack-hey" and song.vocals == song.audio


def test_moods_from_tags():
    assert moods_from_tags(["Chill", "love", "rap"]) == ["calm", "hiphop", "romantic"]


def test_fetch_errors_are_one_line_not_a_crash(tmp_path, monkeypatch, capsys):
    import http.client

    from songspeak.cli import main

    def broken(*args, **kwargs):
        raise http.client.LineTooLong("header line")

    monkeypatch.setattr(ccmixter, "get_json", broken)
    monkeypatch.setattr(ccmixter.search, "__defaults__", ("acappella", None, 50, 0, "rank", broken))
    assert main(["fetch", "ccmixter", "--library", str(tmp_path / "lib")]) == 1
    assert "error:" in capsys.readouterr().err


def test_non_json_reply_is_explained(monkeypatch):
    import io

    from songspeak.sources import http as http_mod

    class Resp(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    monkeypatch.setattr(http_mod.urllib.request, "urlopen", lambda req, timeout: Resp(b"<html>maintenance</html>"))
    with pytest.raises(RuntimeError, match="isn't JSON"):
        http_mod.get_json("https://ccmixter.org/api/query", {"f": "json"})


def test_download_retries_https_and_sends_referer(tmp_path, monkeypatch):
    import io
    import urllib.error

    from songspeak.sources import http as http_mod

    seen = []

    class Resp(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    def fake_urlopen(req, timeout):
        seen.append((req.full_url, req.get_header("Referer"), req.get_header("User-agent")))
        if req.full_url.startswith("http://"):
            raise urllib.error.HTTPError(req.full_url, 403, "Forbidden", {}, None)
        return Resp(b"ID3audio")

    monkeypatch.setattr(http_mod.urllib.request, "urlopen", fake_urlopen)
    dest = tmp_path / "a.mp3"
    http_mod.download("http://ccmixter.org/content/x/a.mp3", dest, referer="https://ccmixter.org/files/x/1")
    assert dest.read_bytes() == b"ID3audio"
    assert [u for u, _, _ in seen] == ["http://ccmixter.org/content/x/a.mp3", "https://ccmixter.org/content/x/a.mp3"]
    assert seen[0][1] == "https://ccmixter.org/files/x/1" and "Mozilla" in seen[0][2]


def test_download_failure_names_the_link(tmp_path, monkeypatch):
    import urllib.error

    from songspeak.sources import http as http_mod

    def always_403(req, timeout):
        raise urllib.error.HTTPError(req.full_url, 403, "Forbidden", {}, None)

    monkeypatch.setattr(http_mod.urllib.request, "urlopen", always_403)
    with pytest.raises(RuntimeError, match=r"HTTP 403 / HTTP 403 for http://x.org/a.mp3"):
        http_mod.download("http://x.org/a.mp3", tmp_path / "a.mp3")


@pytest.mark.parametrize(
    "body, expected",
    [
        (b'[{"upload_name": "In Out", "d": "line one\nline two\ttab"}]', "line one\nline two\ttab"),  # raw control chars
        (b'[{"upload_name": "In Out", "d": "don\\\'t stop"}]', "don\\'t stop"),  # PHP-style \' escape
        (b'[{"upload_name": "In Out", "d": "C:\\\\Users\\\\x \\u00e9"}]', "C:\\Users\\x \u00e9"),  # valid escapes kept
        (b'[{"upload_name": "In Out", "d": "caf\xe9"}]', "caf\ufffd"),  # not UTF-8
    ],
)
def test_lenient_json_repairs_common_catalogue_glitches(body, expected):
    from songspeak.sources.http import parse_json_leniently

    data = parse_json_leniently(body)
    assert data[0]["upload_name"] == "In Out" and data[0]["d"] == expected


def test_freesound_keeps_only_human_voices():
    def sound(i, name, tags):
        return {"id": i, "name": name, "username": "u", "license": "http://creativecommons.org/licenses/by/4.0/",
                "tags": tags, "previews": {"preview-hq-mp3": f"https://cdn.freesound.org/{i}.mp3"}}

    results = {"results": [
        sound(1, "LFOs Manipulating Waveform Generators-074.wav", ["synth", "lfo", "modular"]),
        sound(2, "Cetti's Warbler", ["bird", "singing", "nature"]),
        sound(3, "female voice says hello", ["voice", "hello", "female-voice"]),
        sound(4, "sung word: welcome", ["sung", "word"]),
        sound(5, "door creak", ["door", "creak"]),
    ]}
    cands = freesound.search(api_key="k", fetch=lambda url, params: results)
    assert [c.source_id for c in cands] == ["3", "4"]


def test_songs_and_remove_commands(tmp_path, capsys):
    from songspeak.cli import main
    from songspeak.demo import build_demo_library

    library = build_demo_library(tmp_path / "lib")
    audio = library.root / library.songs["night-market"].audio
    assert main(["songs", "--library", str(library.root)]) == 0
    out = capsys.readouterr().out
    assert "night-market" in out and "Night Market - Demo Band B" in out and "words" in out

    assert main(["remove", "night-market", "--library", str(library.root)]) == 0
    assert "night-market" not in Library.load(library.root).songs
    assert not audio.exists()
    assert main(["remove", "nope", "--library", str(library.root)]) == 1
