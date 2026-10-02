# Build a first Creative Commons library on Windows (PowerShell version of build_cc_library.sh).
# Run from the learning\songspeak folder with the virtual environment active:
#   .\scripts\build_cc_library.ps1                      # library folder "library", 3 pages of 20 ccMixter tracks
#   .\scripts\build_cc_library.ps1 -Library mylib -Pages 5
param(
    [string]$Library = "library",
    [int]$Pages = 3
)
$ErrorActionPreference = "Stop"

function Invoke-SongSpeak {
    python -m songspeak @args
    if ($LASTEXITCODE -ne 0) { throw "songspeak $($args[0]) failed (exit code $LASTEXITCODE)" }
}

# A catalogue page that fails (site busy, odd data) is reported and skipped: whatever was
# downloaded still gets transcribed below, and running the script again retries the page.
function Invoke-Fetch {
    python -m songspeak fetch @args
    if ($LASTEXITCODE -ne 0) { Write-Warning "That fetch failed; carrying on with the next one." }
}

for ($page = 0; $page -lt $Pages; $page++) {
    Invoke-Fetch ccmixter --library $Library --limit 20 --offset ($page * 20)
}

if ($env:FREESOUND_API_KEY) {
    foreach ($query in @("sung word", "singing hello", "choir word", "vocal phrase")) {
        Invoke-Fetch freesound --library $Library --query $query --limit 30 --max-seconds 20
    }
} else {
    Write-Host "FREESOUND_API_KEY not set: skipping Freesound (get a free key at https://freesound.org/apiv2/apply)"
}

Invoke-SongSpeak ingest --library $Library --model small
Invoke-SongSpeak stats --library $Library --coverage (Join-Path $PSScriptRoot "..\docs\starter-words.txt")
