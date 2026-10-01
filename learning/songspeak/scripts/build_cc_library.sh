#!/usr/bin/env bash
# Build a first Creative Commons library: ccMixter a cappellas, plus Freesound sung words if you have a key.
# Usage: scripts/build_cc_library.sh [library-dir] [pages]
set -euo pipefail
LIB="${1:-library}"
PAGES="${2:-3}"   # 20 tracks per page

for ((page = 0; page < PAGES; page++)); do
  songspeak fetch ccmixter --library "$LIB" --limit 20 --offset $((page * 20))
done

if [[ -n "${FREESOUND_API_KEY:-}" ]]; then
  for q in "sung word" "singing hello" "choir word" "vocal phrase"; do
    songspeak fetch freesound --library "$LIB" --query "$q" --limit 30 --max-seconds 20
  done
else
  echo "FREESOUND_API_KEY not set: skipping Freesound (get a free key at https://freesound.org/apiv2/apply)"
fi

songspeak ingest --library "$LIB" --model small
songspeak stats --library "$LIB" --coverage "$(dirname "$0")/../docs/starter-words.txt"
