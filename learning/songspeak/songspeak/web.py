"""The web MVP: one page (type, play, download, credits) and a small JSON API.

There are no accounts yet, so the page sends the tier itself. That's fine for a demo but must be
replaced by real auth before premium is sold.
"""

from __future__ import annotations

import shutil
import tempfile
import uuid
from importlib import resources
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, Field

from songspeak.library import Library
from songspeak.licenses import LicensePolicy
from songspeak.render import MISSING_SILENCE, RenderSettings
from songspeak.studio import Studio
from songspeak.text import TextTooLong
from songspeak.tiers import MIX_VARIETY, TIERS, TierError

KEEP_RENDERS = 200


class MakeRequest(BaseModel):
    message: str = Field(max_length=max(t.max_chars for t in TIERS.values()))
    tier: str = "free"
    mood: str | None = None
    mix: str = MIX_VARIETY
    seed: int | None = None
    missing: str = MISSING_SILENCE


def create_app(library: Library, policy: LicensePolicy | None = None, renders_dir: Path | None = None) -> FastAPI:
    studio = Studio(library, policy)
    renders = Path(renders_dir or tempfile.mkdtemp(prefix="songspeak-renders-"))
    renders.mkdir(parents=True, exist_ok=True)
    ext = ".mp3" if shutil.which("ffmpeg") else ".wav"
    page = resources.files("songspeak").joinpath("static/index.html").read_text(encoding="utf-8")

    app = FastAPI(title="SongSpeak", docs_url="/api/docs")

    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        return page

    @app.get("/api/library")
    def library_info() -> dict:
        return {
            **studio.stats(),
            "tiers": {
                t.name: {"max_chars": t.max_chars, "moods": t.moods, "mix_modes": list(t.mix_modes)}
                for t in TIERS.values()
            },
            "personal_mode": studio.policy.allow_noncommercial,
        }

    @app.post("/api/make")
    def make(req: MakeRequest) -> dict:
        tier = TIERS.get(req.tier)
        if tier is None:
            raise HTTPException(400, f"Unknown tier {req.tier!r}")
        name = f"{uuid.uuid4().hex}{ext}"
        try:
            made = studio.make(
                req.message,
                renders / name,
                tier,
                mood=req.mood or None,
                mix=req.mix,
                seed=req.seed,
                settings=RenderSettings(missing=req.missing),
            )
        except TierError as exc:
            raise HTTPException(403, str(exc)) from exc
        except (TextTooLong, ValueError) as exc:
            raise HTTPException(400, str(exc)) from exc
        _prune(renders)
        return {"audio_url": f"/renders/{name}", **made.to_dict()}

    @app.get("/renders/{name}")
    def rendered(name: str) -> FileResponse:
        path = renders / Path(name).name  # no path traversal
        if not path.is_file():
            raise HTTPException(404, "Render expired or not found")
        return FileResponse(path, filename=f"songspeak{path.suffix}")

    return app


def _prune(renders: Path) -> None:
    files = sorted(renders.glob("*.*"), key=lambda p: p.stat().st_mtime)
    for old in files[:-KEEP_RENDERS]:
        old.unlink(missing_ok=True)
