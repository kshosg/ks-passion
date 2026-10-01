"""songspeak make | fetch | add | ingest | stats | search | serve | demo"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from songspeak import ingest as ingest_mod
from songspeak.demo import DEMO_MESSAGE, build_demo_library
from songspeak.library import MANIFEST, Library
from songspeak.licenses import LicensePolicy
from songspeak.render import MISSING_SILENCE, MISSING_TONE, RenderSettings, credits_text, write_credits
from songspeak.studio import Studio
from songspeak.text import TextTooLong, normalize_words
from songspeak.tiers import FREE, MIX_FEWEST_SONGS, MIX_VARIETY, TIERS, TierError


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):  # song titles can contain characters an old Windows console can't show
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="replace")
    parser = argparse.ArgumentParser(prog="songspeak", description="Say anything with words sung in songs.")
    sub = parser.add_subparsers(dest="command", required=True)

    def lib_arg(p, create=False):
        p.add_argument("--library", type=Path, required=True, help="library folder" + (" (created if new)" if create else ""))

    def nc_arg(p):
        p.add_argument("--allow-nc", action="store_true", help="also use NonCommercial songs (personal use only)")

    make = sub.add_parser("make", help="turn a message into audio")
    make.add_argument("message", nargs="?", help="what to say (or use --file)")
    make.add_argument("--file", type=Path, help="read the message from a text file")
    lib_arg(make)
    nc_arg(make)
    make.add_argument("--out", type=Path, default=Path("out/message.wav"), help=".wav or .mp3")
    make.add_argument("--tier", choices=sorted(TIERS), default="free")
    make.add_argument("--mood", help="prefer songs tagged with this mood (premium)")
    make.add_argument("--mix", choices=[MIX_VARIETY, MIX_FEWEST_SONGS], default=MIX_VARIETY)
    make.add_argument("--seed", type=int, help="shuffle: pick different songs for the same message")
    make.add_argument("--missing", choices=[MISSING_SILENCE, MISSING_TONE], default=MISSING_SILENCE)
    make.add_argument("--full-mix", action="store_true", help="cut from the full song even when vocals exist")

    fetch = sub.add_parser("fetch", help="add Creative Commons songs from ccMixter or Freesound")
    fetch.add_argument("source", choices=["ccmixter", "freesound"])
    lib_arg(fetch, create=True)
    nc_arg(fetch)
    fetch.add_argument("--limit", type=int, default=20)
    fetch.add_argument("--offset", type=int, default=0, help="ccMixter: skip this many results (to page)")
    fetch.add_argument("--tags", default="acappella", help="ccMixter tags, comma-separated (default: acappella)")
    fetch.add_argument("--query", help="search text (Freesound default: 'singing word')")
    fetch.add_argument("--max-seconds", type=float, default=600, help="skip tracks longer than this")
    fetch.add_argument("--ingest", action="store_true", help="transcribe what was added straight away")

    add = sub.add_parser("add", help="add an audio file you have rights to (royalty-free, CC, owned)")
    add.add_argument("path", type=Path)
    lib_arg(add, create=True)
    add.add_argument("--title", required=True)
    add.add_argument("--artist", required=True)
    add.add_argument("--license", required=True, help="CC URL/code (CC-BY-4.0, CC0-1.0), ROYALTY-FREE, OWNED or PD")
    add.add_argument("--license-note", default="", help="required for ROYALTY-FREE: where bought, what it allows")
    add.add_argument("--source-url", default="")
    add.add_argument("--moods", default="", help="comma-separated, e.g. upbeat,romantic")
    add.add_argument("--a-cappella", action="store_true", help="the file is vocals only")

    ing = sub.add_parser("ingest", help="transcribe new songs in a library")
    lib_arg(ing)
    ing.add_argument("--isolate-vocals", action="store_true", help="separate vocals with Demucs first (not needed for a cappellas)")
    ing.add_argument("--model", default="small", help="Whisper model size: tiny, base, small, medium, large-v3")
    ing.add_argument("--language", default="en", help="language code, or 'auto'")
    ing.add_argument("--force", action="store_true", help="re-transcribe songs that already have a transcript")

    stats = sub.add_parser("stats", help="what's in a library, and how much of a message it covers")
    lib_arg(stats)
    nc_arg(stats)
    stats.add_argument("--coverage", type=Path, help="text file of words/messages to check coverage against")

    search = sub.add_parser("search", help="where is this word or phrase sung?")
    search.add_argument("phrase")
    lib_arg(search)
    nc_arg(search)

    serve = sub.add_parser("serve", help="run the web app")
    lib_arg(serve)
    nc_arg(serve)
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)

    demo = sub.add_parser("demo", help="build a synthetic library and render an example")
    demo.add_argument("--dir", type=Path, default=Path("out/demo"))
    demo.add_argument("message", nargs="?", default=DEMO_MESSAGE)

    args = parser.parse_args(argv)
    commands = {
        "make": _make, "fetch": _fetch, "add": _add, "ingest": _ingest, "stats": _stats,
        "search": _search, "serve": _serve, "demo": _demo,
    }  # fmt: skip
    try:
        return commands[args.command](args)
    except (TextTooLong, TierError, RuntimeError, OSError, ValueError) as exc:  # OSError: files, network
        print(f"error: {exc}", file=sys.stderr)
        return 1


def _policy(args) -> LicensePolicy:
    return LicensePolicy(allow_noncommercial=getattr(args, "allow_nc", False))


def _open_or_create(root: Path) -> Library:
    if (root / MANIFEST).exists():
        return Library.load(root)
    root.mkdir(parents=True, exist_ok=True)
    library = Library(root, [])
    library.save()
    return library


def _make(args) -> int:
    if args.file:
        message = args.file.read_text(encoding="utf-8")
    elif args.message:
        message = args.message
    else:
        raise ValueError("give a message or --file")
    studio = Studio(Library.load(args.library), _policy(args))
    settings = RenderSettings(missing=args.missing, prefer_vocals=not args.full_mix)
    _make_and_report(studio, message, args.out, TIERS[args.tier], args.mood, args.mix, args.seed, settings)
    return 0


def _make_and_report(studio, message, out, tier, mood=None, mix=MIX_VARIETY, seed=None, settings=None) -> None:
    made = studio.make(message, out, tier, mood=mood, mix=mix, seed=seed, settings=settings)
    credits_path = Path(out).with_suffix(".credits.json")
    write_credits(made.segments, credits_path)
    result = made.result
    print(credits_text(made.segments))
    print(f"\n{result.path}  ({result.seconds:.1f}s, {result.clips} clips from {result.songs} songs)")
    print(f"credits: {credits_path}")
    if result.missing:
        print(f"not in the library yet: {', '.join(result.missing)}")
    d = made.to_dict()
    print(f"\n{d['terms']}")
    for line in d["attribution"]:
        print(f"  {line}")


def _fetch(args) -> int:
    from songspeak.sources import ccmixter, freesound
    from songspeak.sources.collect import collect

    library = _open_or_create(args.library)
    if args.source == "ccmixter":
        candidates = ccmixter.search(tags=args.tags, query=args.query, limit=args.limit, offset=args.offset)
    else:
        candidates = freesound.search(query=args.query or "singing word", limit=args.limit, max_seconds=args.max_seconds)
    print(f"{len(candidates)} result(s) from {args.source}")
    report = collect(library, candidates, _policy(args), max_seconds=args.max_seconds)
    for title, reason in report.skipped:
        print(f"- {title}: {reason}")
    print(f"\nAdded {len(report.added)}, skipped {len(report.skipped)}. Library now has {len(library.songs)} songs.")
    if args.ingest and report.added:
        ingest_mod.ingest(library)
    elif report.added:
        print(f"Next: songspeak ingest --library {args.library}")
    return 0


def _add(args) -> int:
    from songspeak.sources.collect import add_local

    library = _open_or_create(args.library)
    song = add_local(
        library,
        args.path,
        title=args.title,
        artist=args.artist,
        license=args.license,
        license_note=args.license_note,
        source_url=args.source_url,
        moods=[m.strip() for m in args.moods.split(",") if m.strip()],
        a_cappella=args.a_cappella,
    )
    print(f"Added {song.credit} as {song.id} [{song.lic.label}]. Next: songspeak ingest --library {args.library}")
    return 0


def _ingest(args) -> int:
    library = Library.load(args.library)
    language = None if args.language == "auto" else args.language
    n = ingest_mod.ingest(library, isolate=args.isolate_vocals, model_size=args.model, language=language, force=args.force)
    print(f"Ingested {n} song(s).")
    return 0


def _stats(args) -> int:
    studio = Studio(Library.load(args.library), _policy(args))
    s = studio.stats()
    print(f"Songs: {s['songs']} ({s['usable_songs']} usable under this licence policy, {s['transcribed']} transcribed)")
    print(f"Distinct words sung: {s['vocabulary']}")
    print("Licences: " + (", ".join(f"{k} x{v}" for k, v in s["licenses"].items()) or "-"))
    print("Sources:  " + (", ".join(f"{k} x{v}" for k, v in s["sources"].items()) or "-"))
    print("Moods:    " + (", ".join(s["moods"]) or "-"))
    if args.coverage:
        lines = args.coverage.read_text(encoding="utf-8").splitlines()
        words = normalize_words("\n".join(line for line in lines if not line.lstrip().startswith("#")))
        unique = sorted(set(words))
        missing = [w for w in unique if not studio.index.lookup((w,))]
        found = len(unique) - len(missing)
        print(f"\nCoverage of {args.coverage.name}: {found}/{len(unique)} distinct words ({100 * found / max(1, len(unique)):.0f}%)")
        if missing:
            print("Missing: " + ", ".join(missing[:100]) + (" ..." if len(missing) > 100 else ""))
    return 0


def _search(args) -> int:
    studio = Studio(Library.load(args.library), _policy(args))
    hits = studio.index.lookup(tuple(normalize_words(args.phrase)))
    for occ in hits:
        start, end, conf = studio.index.span(occ)
        song = studio.library.songs[occ.song_id]
        print(f"{song.credit}  {start:.2f}-{end:.2f}s  confidence {conf:.2f}  [{song.lic.label}]")
    if not hits:
        print("not sung anywhere in this library")
    return 0


def _serve(args) -> int:
    try:
        import uvicorn
    except ImportError as exc:
        raise RuntimeError("the web app needs: pip install -e .[web]") from exc
    from songspeak.web import create_app

    app = create_app(Library.load(args.library), _policy(args))
    print(f"SongSpeak on http://{args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port)
    return 0


def _demo(args) -> int:
    library = build_demo_library(args.dir / "library")
    print(f"Demo library: {len(library.songs)} synthetic songs in {library.root}\n")
    studio = Studio(library)
    _make_and_report(studio, args.message, args.dir / "message.wav", FREE)
    return 0
