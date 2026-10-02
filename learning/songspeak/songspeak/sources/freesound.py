"""Freesound (freesound.org): CC0 and CC BY sound clips, including many single sung words and phrases.

Good for filling gaps the songs don't cover ("Singapore", names, numbers). Needs a free API key
from https://freesound.org/apiv2/apply, passed as FREESOUND_API_KEY. We download the HQ MP3
preview, which the API serves without OAuth and is plenty for short vocal clips.
"""

from __future__ import annotations

import os

from songspeak.sources import Candidate
from songspeak.sources.http import get_json

API = "https://freesound.org/apiv2/search/text/"
FIELDS = "id,name,username,license,url,tags,duration,previews"
LICENSE_FILTER = 'license:("Creative Commons 0" OR "Attribution")'  # NC is filtered out at the source

# Freesound is mostly sound effects. Keep a sound only if it's tagged as a human voice and not as
# something else that "sings" (birds) or makes tones (synths): the speech recogniser invents words
# when fed non-speech, and those would pollute the library.
HUMAN_VOICE_TAGS = {
    "voice", "vocal", "vocals", "sung", "singer", "acapella", "acappella", "a-cappella", "choir",
    "female-voice", "male-voice", "female-vocal", "male-vocal", "human-voice", "spoken", "speech", "word", "words",
}  # fmt: skip
NOT_VOICE_TAGS = {
    "bird", "birds", "birdsong", "bird-song", "animal", "animals", "insect", "frog", "nature", "field-recording",
    "synth", "synthesizer", "synthesiser", "modular", "lfo", "waveform", "oscillator", "glitch", "noise",
}  # fmt: skip


def search(
    query: str = "singing word",
    limit: int = 50,
    page: int = 1,
    api_key: str | None = None,
    max_seconds: float = 60,
    fetch=get_json,
) -> list[Candidate]:
    api_key = api_key or os.environ.get("FREESOUND_API_KEY")
    if not api_key:
        raise RuntimeError("Freesound needs an API key: get one at https://freesound.org/apiv2/apply, set FREESOUND_API_KEY")
    params = {
        "query": query,
        "filter": f"{LICENSE_FILTER} duration:[0 TO {max_seconds}]",
        "fields": FIELDS,
        "page_size": 150,  # ask for a full page: many results are dropped as not-a-voice below
        "page": page,
        "token": api_key,
    }
    data = fetch(API, params) or {}
    return [c for item in data.get("results", []) if (c := parse_sound(item))][:limit]


def parse_sound(item: dict) -> Candidate | None:
    previews = item.get("previews") or {}
    url = previews.get("preview-hq-mp3") or previews.get("preview-lq-mp3")
    if not url or not item.get("license"):
        return None
    tags = sorted({str(t).lower() for t in item.get("tags") or []})
    if not is_human_voice(tags):
        return None
    return Candidate(
        source="freesound",
        source_id=str(item["id"]),
        title=item.get("name") or f"Sound {item['id']}",
        artist=item.get("username") or "Unknown",
        license=item["license"],
        page_url=item.get("url") or f"https://freesound.org/s/{item['id']}/",
        download_url=url,
        tags=tags,
        a_cappella=True,  # a vocal one-shot: the whole file is voice
        seconds=item.get("duration"),
    )


def is_human_voice(tags: list[str]) -> bool:
    tags = set(tags)
    return bool(tags & HUMAN_VOICE_TAGS) and not tags & NOT_VOICE_TAGS
