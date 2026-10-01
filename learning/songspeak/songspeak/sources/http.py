"""Tiny HTTP helpers on the standard library (honours HTTPS_PROXY like any urllib client)."""

from __future__ import annotations

import http.client
import json
import urllib.error
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


# Some file servers (ccMixter's included) answer 403 to requests that don't look like a browser download.
BROWSER_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) SongSpeak/0.1"


def download(url: str, dest: Path, referer: str | None = None, timeout: float = 120) -> None:
    """Stream a file to disk, refusing anything implausibly large for one song.

    Tries the URL as given and its https:// form, sending the song's page as the Referer,
    because some catalogues refuse "hotlinked" downloads.
    """
    urls = [url]
    if url.startswith("http://"):
        urls.append("https://" + url[len("http://") :])
    errors = []
    for candidate in urls:
        try:
            _download_once(candidate, dest, referer, timeout)
            return
        except urllib.error.HTTPError as exc:
            errors.append(f"HTTP {exc.code}")
    raise RuntimeError(f"{' / '.join(errors)} for {url} (try opening that link in your browser)")


def _download_once(url: str, dest: Path, referer: str | None, timeout: float) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    headers = {"User-Agent": BROWSER_USER_AGENT, "Accept": "audio/*,*/*;q=0.8"}
    if referer:
        headers["Referer"] = referer
    req = urllib.request.Request(url, headers=headers)
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
