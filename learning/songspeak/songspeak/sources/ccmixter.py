"""ccMixter (ccmixter.org): a community remix site full of Creative Commons *a cappella* uploads.

A cappellas are ideal for SongSpeak: the vocals are already isolated, so transcription is more
accurate and the clips are clean. No API key is needed.

API: https://ccmixter.org/api/query?f=json&tags=acappella&limit=..&offset=..&sort=..
Each upload lists its licence URL and its files; we take the first MP3.
"""

from __future__ import annotations

from songspeak.sources import Candidate
from songspeak.sources.http import get_json

API = "https://ccmixter.org/api/query"


def search(
    tags: str = "acappella",
    query: str | None = None,
    limit: int = 50,
    offset: int = 0,
    sort: str = "rank",
    fetch=get_json,
) -> list[Candidate]:
    params = {"f": "json", "tags": tags, "search": query, "limit": limit, "offset": offset, "sort": sort}
    return [c for item in fetch(API, params) or [] if (c := parse_upload(item))]


def parse_upload(item: dict) -> Candidate | None:
    mp3 = next(
        (
            f
            for f in item.get("files") or []
            if "mp3" in str((f.get("file_format_info") or {}).get("mime_type", "")) + str(f.get("file_name", "")).lower()
            and f.get("download_url")
        ),
        None,
    )
    if not mp3 or not item.get("license_url"):
        return None
    tags = _tags(item)
    return Candidate(
        source="ccmixter",
        source_id=str(item["upload_id"]),
        title=item.get("upload_name") or f"Upload {item['upload_id']}",
        artist=item.get("user_real_name") or item.get("user_name") or "Unknown artist",
        license=item["license_url"],
        page_url=item.get("file_page_url") or f"https://ccmixter.org/files/{item.get('user_name', '')}/{item['upload_id']}",
        download_url=mp3["download_url"],
        tags=tags,
        a_cappella="acappella" in tags,
        seconds=_seconds((mp3.get("file_format_info") or {}).get("ps")),
    )


def _tags(item: dict) -> list[str]:
    raw = item.get("upload_tags") or ""
    extra = item.get("upload_extra") or {}
    raw += "," + str(extra.get("usertags") or "") + "," + str(extra.get("systags") or "")
    return sorted({t.strip().lower() for t in raw.split(",") if t.strip()})


def _seconds(playtime: str | None) -> float | None:
    """ccMixter gives play time as "m:ss"."""
    try:
        minutes, seconds = str(playtime).split(":")[-2:]
        return int(minutes) * 60 + float(seconds)
    except (ValueError, TypeError):
        return None
