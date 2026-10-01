import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from songspeak.demo import build_demo_library  # noqa: E402
from songspeak.web import create_app  # noqa: E402


@pytest.fixture
def client(tmp_path):
    return TestClient(create_app(build_demo_library(tmp_path / "lib"), renders_dir=tmp_path / "renders"))


def test_page_and_library(client):
    assert "SongSpeak" in client.get("/").text
    info = client.get("/api/library").json()
    assert info["usable_songs"] == 5 and info["tiers"]["free"]["max_chars"] == 300
    assert "upbeat" in info["moods"]


def test_make_returns_audio_and_credits(client):
    res = client.post("/api/make", json={"message": "Hello, everybody. Welcome to Singapore!"})
    assert res.status_code == 200, res.text
    data = res.json()
    assert [s["text"] for s in data["segments"]] == ["Hello", "everybody", "Welcome to", "Singapore"]
    assert data["missing"] == [] and data["songs"] == 4
    audio = client.get(data["audio_url"])
    assert audio.status_code == 200 and len(audio.content) > 1000


def test_tier_limits(client):
    assert client.post("/api/make", json={"message": "x" * 301}).status_code == 400
    assert client.post("/api/make", json={"message": "hello", "mood": "calm"}).status_code == 403
    res = client.post("/api/make", json={"message": "hello " * 100, "tier": "premium", "mood": "calm", "mix": "fewest-songs"})
    assert res.status_code == 200


def test_render_path_traversal_blocked(client):
    assert client.get("/renders/..%2F..%2Fetc%2Fpasswd").status_code == 404
