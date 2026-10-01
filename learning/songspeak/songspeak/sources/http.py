"""Tiny HTTP helpers on the standard library (honours HTTPS_PROXY like any urllib client)."""

from __future__ import annotations

import http.client
import json
import urllib.parse
import urllib.request
from pathlib import Path

USER_AGENT = "SongSpeak/0.1 (Creative Commons remix tool)"
MAX_DOWNLOAD_BYTES = 40 * 1024 * 1024

# Some catalogue servers (seen with ccMixter) send a single header line over Python's 64 KB limit,
# which makes urllib give up with LineTooLong. Allow up to 1 MB.
http.client._MAXLINE = max(http.client._MAXLINE, 1 << 20)


def get_json(url: str, params: dict | None = None, timeout: float = 30) -> object:
    if params:
        url = f"{url}?{urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read()
    try:
        return json.loads(body)
    except ValueError as exc:
        host = urllib.parse.urlsplit(url).netloc
        raise RuntimeError(f"{host} sent back something that isn't JSON (starts: {body[:80]!r}); try again later") from exc


def download(url: str, dest: Path, timeout: float = 120) -> None:
    """Stream a file to disk, refusing anything implausibly large for one song."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp, open(tmp, "wb") as out:
        total = 0
        while chunk := resp.read(1 << 16):
            total += len(chunk)
            if total > MAX_DOWNLOAD_BYTES:
                out.close()
                tmp.unlink()
                raise RuntimeError(f"{url} is over {MAX_DOWNLOAD_BYTES // 2**20} MB; skipped")
            out.write(chunk)
    tmp.replace(dest)
