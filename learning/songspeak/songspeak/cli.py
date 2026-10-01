"""songspeak make | ingest | search | demo"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from songspeak import ingest as ingest_mod
from songspeak.demo import DEMO_MESSAGE, build_demo_library
from songspeak.index import PhraseIndex
from songspeak.library import Library
from songspeak.matcher import plan
from songspeak.render import MISSING_SILENCE, MISSING_TONE, RenderSettings, credits_text, render, write_credits
from songspeak.text import TextTooLong, normalize_words, tokenize
from songspeak.tiers import MIX_FEWEST_SONGS, MIX_VARIETY, TIERS, TierError, check_request


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="songspeak", description="Say anything with words sung in songs.")
    sub = parser.add_subparsers(dest="command", required=True)

    make = sub.add_parser("make", help="turn a message into audio")
    make.add_argument("message", nargs="?", help="what to say (or use --file)")
    make.add_argument("--file", type=Path, help="read the message from a text file")
    make.add_argument("--library", type=Path, required=True)
    make.add_argument("--out", type=Path, default=Path("out/message.wav"), help=".wav or .mp3")
    make.add_argument("--tier", choices=sorted(TIERS), default="free")
    make.add_argument("--mood", help="prefer songs tagged with this mood (premium)")
    make.add_argument("--mix", choices=[MIX_VARIETY, MIX_FEWEST_SONGS], default=MIX_VARIETY)
    make.add_argument("--seed", type=int, help="shuffle: pick different songs for the same message")
    make.add_argument("--missing", choices=[MISSING_SILENCE, MISSING_TONE], default=MISSING_SILENCE)
    make.add_argument("--full-mix", action="store_true", help="cut from the full song even when vocals exist")

    ing = sub.add_parser("ingest", help="transcribe new songs in a library")
    ing.add_argument("--library", type=Path, required=True)
    ing.add_argument("--isolate-vocals", action="store_true", help="separate vocals with Demucs first")
    ing.add_argument("--model", default="small", help="Whisper model size: tiny, base, small, medium, large-v3")
    ing.add_argument("--language", default="en", help="language code, or 'auto'")
    ing.add_argument("--force", action="store_true", help="re-transcribe songs that already have a transcript")

    search = sub.add_parser("search", help="where is this word or phrase sung?")
    search.add_argument("phrase")
    search.add_argument("--library", type=Path, required=True)

    demo = sub.add_parser("demo", help="build a synthetic library and render an example")
    demo.add_argument("--dir", type=Path, default=Path("out/demo"))
    demo.add_argument("message", nargs="?", default=DEMO_MESSAGE)

    args = parser.parse_args(argv)
    try:
        return {"make": _make, "ingest": _ingest, "search": _search, "demo": _demo}[args.command](args)
    except (TextTooLong, TierError, RuntimeError, FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


def _make(args) -> int:
    if args.file:
        message = args.file.read_text(encoding="utf-8")
    elif args.message:
        message = args.message
    else:
        raise ValueError("give a message or --file")
    tier = TIERS[args.tier]
    check_request(tier, args.mood, args.mix)
    library = Library.load(args.library)
    settings = RenderSettings(missing=args.missing, prefer_vocals=not args.full_mix)
    _make_message(message, library, args.out, tier.max_chars, args.mood, args.mix, args.seed, settings)
    return 0


def _make_message(message, library, out, max_chars, mood, mix, seed, settings) -> None:
    tokens = tokenize(message, max_chars)
    if not tokens:
        raise ValueError("the message has no words in it")
    index = PhraseIndex.from_library(library)
    segments = plan(tokens, index, library, mood=mood, mix=mix, seed=seed)
    result = render(segments, library, out, settings)
    credits_path = Path(out).with_suffix(".credits.json")
    write_credits(segments, credits_path)

    print(credits_text(segments))
    print(f"\n{result.path}  ({result.seconds:.1f}s, {result.clips} clips from {result.songs} songs)")
    print(f"credits: {credits_path}")
    if result.missing:
        print(f"not in the library yet: {', '.join(result.missing)}")


def _ingest(args) -> int:
    library = Library.load(args.library)
    language = None if args.language == "auto" else args.language
    n = ingest_mod.ingest(library, isolate=args.isolate_vocals, model_size=args.model, language=language, force=args.force)
    print(f"Ingested {n} song(s).")
    return 0


def _search(args) -> int:
    library = Library.load(args.library)
    index = PhraseIndex.from_library(library)
    hits = index.lookup(tuple(normalize_words(args.phrase)))
    for occ in hits:
        start, end, conf = index.span(occ)
        print(f"{library.songs[occ.song_id].credit}  {start:.2f}-{end:.2f}s  confidence {conf:.2f}")
    if not hits:
        print("not sung anywhere in this library")
    return 0


def _demo(args) -> int:
    library = build_demo_library(args.dir / "library")
    print(f"Demo library: {len(library.songs)} synthetic songs in {library.root}\n")
    _make_message(args.message, library, args.dir / "message.wav", None, None, MIX_VARIETY, None, RenderSettings())
    return 0
