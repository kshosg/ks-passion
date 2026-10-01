# SongSpeak — Product Spec (v0.2)

> Type a message. Hear it "sung" back, one word or phrase at a time, by a different song for each piece.
> Think of a ransom note cut from magazine letters, made from songs instead.

**Status:** the Creative Commons MVP is built (`learning/songspeak/`): ccMixter + Freesound connectors,
royalty-free import, licence enforcement, and a web app. **Decision taken:** launch on path 2 (Creative Commons +
royalty-free), keeping path 1 (owned word bank) for premium. Next: build the first real library and test with friends (§5).

---

## 1. Working name — options

| Name | Why it works | Risk |
|---|---|---|
| **SongSpeak** (working) | Plain, says what it does | Generic, so hard to trademark |
| **Lyric Ransom** | The ransom-note image makes the idea click immediately | "Ransom" reads a little dark |
| **Mixtape Message** | Warm and nostalgic, easy to gift ("send a mixtape message") | Long |
| **SingSay** | Short, sticky, works as a verb ("SingSay it") | Could be confused with karaoke apps |
| **Chorus Note** | Sounds like a greeting card, which fits gifting | Less obvious what it does |

---

## 2. The user flow (MVP)

1. **Type** a message, up to **300 characters**. Example: *"Hello, everybody. Welcome to Singapore!"*
2. **Match**: the app looks for each word or phrase in its indexed song library and **prefers the longest
   sung phrase** it can find. If "welcome to" is sung somewhere, it uses that instead of cutting two separate words.
3. **Stitch**: cut each clip, level the volume, add short fades so the cuts don't click, and pause where the
   punctuation says to (a short pause for commas, a longer one for full stops).
4. **Output**: an MP3/WAV, a **credits list** (which word came from which song and at what timestamp), and a
   list of any words the library doesn't have yet.
5. **Shuffle**: the same message re-rendered with different songs.

Credits come with every output. That's partly for the law and partly for fun: half the joy is seeing *where* each word came from.

---

## 3. Reality check: where can the songs come from?

The original idea was to pull songs from YouTube, Spotify, Genius and lyrics.com. **I recommend against building on those.**
The reasons are below. *(I'm not a lawyer, so talk to an IP lawyer in Singapore before any public launch.)*

| Source | What it actually offers | Can we use it for this? |
|---|---|---|
| **YouTube** | Videos with audio | **No.** The Terms of Service forbid downloading content unless YouTube provides a download option. The Data API gives metadata only, not audio. |
| **Spotify** | Streaming, metadata | **No.** The developer terms forbid downloading or stream-ripping audio. In late 2024 Spotify also restricted 30-second previews and audio-analysis endpoints for new apps. |
| **Genius / lyrics.com** | Lyrics text | **Not for audio.** Lyrics are themselves copyrighted (licensed through companies like LyricFind/Musixmatch), scraping breaks those sites' terms, and plain text has **no timestamps**, so it can't tell us *when* a word is sung. |
| **Musixmatch API** | Licensed lyrics, including word-level time-synced lyrics on commercial plans | **Maybe, for search/alignment only.** It still provides no audio. Check current plans and pricing. |

### The copyright core

Each clip copies **two** copyrights: the **sound recording** (owned by the label) and the **song itself**
(the publisher/songwriter). Even very short samples are risky:
- *Bridgeport Music v. Dimension Films* (US 6th Cir., 2005): "Get a license or do not sample." In that circuit, no sample is too small.
- *VMG Salsoul v. Ciccone* (US 9th Cir., 2016) went the other way for a sliver of a sample (*de minimis*).
- **Singapore's Copyright Act 2021** has a fair-use exception, but it is decided case by case, and a **paid** product that takes
  from many famous recordings weighs against it.

**Bottom line:** a public, paid app that cuts words out of chart hits needs licences. For major-label catalogues those are
expensive and slow, and labels usually won't negotiate with a startup that has no traction yet.

### Paths that can work (best first)

1. **Own the "word bank"** ⭐ *Recommended for launch.* Hire session singers (Fiverr, local music schools,
   LASALLE/NAFA students) to sing the ~3,000 most common English words plus Singapore/SEA place names, in several
   **moods and styles** (soul, pop, rock, ballad, Mandopop-style English). You own everything, so there's no licensing risk.
   **Mood selection becomes a real premium feature instead of a guess**, and the clips are clean because they're recorded
   one word at a time. Words like *Singapore*, *lah*, *Merlion*, *makan* are a local moat no one else has.
2. **Creative Commons / royalty-free catalogues.** Free Music Archive, Jamendo (offers commercial licences) and ccMixter
   (which has CC-licensed *a cappella* tracks, ideal for us). Licences vary per track, so store the licence for every
   song (the engine already requires this). Fine for a prototype; the vocabulary is patchy.
3. **Bring your own audio (personal mode).** Users upload songs they own, and the app indexes them privately for personal use.
   The tech already supports this. It's a grey area as soon as people **share** the output publicly, so keep it private
   and on-device if possible.
4. **Label/publisher licensing.** This is the long-term "real songs" version. Revisit once there's traction to show,
   possibly through a music-licensing aggregator rather than labels directly.

> The "Hello from *Hello*, Everybody from *Everybody*" version from the original brief is the dream product, and it's
> exactly path 4. Paths 1–2 let you launch, learn and build an audience now, without legal exposure.

---

## 4. How it works (architecture)

```
                INGEST (once per song)                          MAKE (per request, ~seconds)
 ┌───────────┐   ┌──────────────┐   ┌───────────────────┐    ┌──────────┐   ┌────────────┐   ┌──────────┐
 │ song file │──▶│ Demucs:      │──▶│ Whisper: every    │──▶ │ phrase   │◀──│ message →  │──▶│ cut, level│──▶ MP3 + credits
 │ + licence │   │ split vocals │   │ word + start/end  │    │ index    │   │ fewest-clip│   │ fade,     │
 │ + moods   │   │ (optional)   │   │ + confidence      │    │ (n-grams)│   │ match      │   │ pause     │
 └───────────┘   └──────────────┘   └───────────────────┘    └──────────┘   └────────────┘   └──────────┘
```

| Piece | MVP (built) | At scale |
|---|---|---|
| Vocal isolation | Demucs `htdemucs` (CLI) | Same, on a GPU worker queue |
| Word timestamps | faster-whisper, `word_timestamps=True` | Plus forced alignment against licensed lyrics (Musixmatch richsync or WhisperX) for accuracy on sung vocals |
| Index | In-memory n-gram map (1–8 words) | Postgres `words(song_id, pos, word, start, end, prob)` plus trigram/phrase lookups; pre-cut clips in object storage (S3/R2) |
| Matcher | DP for fewest clips, then score candidates | Same, plus pitch/tempo features for "smooth" mixes |
| Render | numpy + ffmpeg, streamed to disk | Same, as a background job; cache popular words |
| App | CLI | Web app (Next.js) + API (FastAPI) + job queue; shareable links; TikTok-ready 9:16 lyric video export |

### Matching rules (what makes it sound good)
- **Longest phrase wins.** Fewer cuts sound more natural.
- **Never sing through punctuation.** "Hello, everybody" stays two clips with a pause between them.
- **Avoid held notes.** A three-second "hellooooo" scores worse than a crisp one.
- **Prefer confident transcriptions.** Whisper on singing is imperfect, so low-confidence words get skipped.
- **Mood and mix** are a scoring bonus, not a hard filter, so the output never gets stuck.
- **Missing words** become silence or a beep and get reported. They never disappear silently.

### Known quality challenges
- Whisper is trained on speech, and **sung** words get mis-heard or mis-timed. Mitigations: isolate the vocals first,
  use a larger model, use forced alignment when lyrics are licensed, and run a human QA pass on the top words.
- In singing, word boundaries blur together (legato), so we pad the clips and add short fades.
- Jumps in pitch and key between clips are part of the charm in "ransom note" mode. A premium "smooth" mode can pitch-shift
  and time-stretch clips toward a common key and tempo.

---

## 5. MVP scope — definition of done

- [x] Message input, 300-character limit, punctuation-aware pauses
- [x] Library with a required licence field per song, moods and optional vocal stems
- [x] Ingest: vocal isolation + word-level transcription
- [x] Longest-phrase matcher with variety, shuffle and missing-word reporting
- [x] WAV/MP3 output + credits (JSON and text)
- [x] Synthetic demo library, automated tests (28)
- [x] **Creative Commons sourcing**: ccMixter a cappellas (no key), Freesound CC0/CC BY sung clips (free key),
      `add` for bought royalty-free packs (requires a written licence note)
- [x] **Licence engine**: ND always refused; NC only in personal mode and never in paid renders; SA output terms
      calculated; attribution in title-author-source-licence form generated for every render
- [x] **Web MVP**: type → play → download → copy credits; free/premium toggle; shuffle; mobile + dark mode
- [ ] **Library v1**: run `scripts/build_cc_library.sh`, aim for **≥ 60% coverage** of `docs/starter-words.txt`
      on commercial-safe licences, and spot-check the 50 most-used words by ear
- [ ] Fill gaps: commission recordings of missing high-value words (Singapore, lah, Merlion, names) — the first
      step toward path 1
- [ ] Deploy (a small VPS, e.g. Hetzner/DigitalOcean, behind Caddy) and get 10 friends testing it: does it make them smile? Would they share it?

### What to expect from a CC library
- **Licence mix:** many ccMixter a cappellas are CC BY-NC, so the commercial-safe library is smaller. `songspeak stats`
  shows the split, and `--allow-nc` turns on a personal mode for your own experiments.
- **Accuracy:** Whisper mishears sung words. A cappellas help a lot. Use `--model medium` once the pipeline works,
  and remove bad clips after listening.
- **Vocabulary:** songs cover common words well but miss names and places. Freesound one-shots and commissioned words fill those gaps.
- **Attribution is part of the product:** the credits panel lists "Title" by Artist (link), licence (link), and notes
  the excerpts were cut and rearranged. Users must keep it with anything they post.

## 6. Premium (paid) — future

| Feature | Free | Premium |
|---|---|---|
| Characters per message | 300 | **30,000** (rendered as a background job; the engine already streams to disk) |
| Mood selection | — | **Upbeat, calm, romantic, dramatic, funny…** (built as a scoring hook) |
| Mix modes | Variety ("ransom note") | + **Fewest songs** (built), **Smooth** (key/tempo-matched), **Beat** (clips laid on a backing track, on the beat), **Single artist / era / genre** |
| Output | MP3 + credits | + WAV, stems, 9:16 lyric video for TikTok/Reels, no watermark |
| Shuffle / regenerate | 3 per message | Unlimited, plus swapping a single word's source by hand ("pick a different *Hello*") |
| Custom words | — | Request a word; it gets sung within X days (path 1 makes this possible) |

**Pricing ideas to test:** SGD 4.98/month or SGD 39/year; one-off "gift pack" credits for birthdays and weddings.
Use cases to market: birthday shout-outs, wedding/event intros, podcast and livestream stingers, TikTok hooks,
office farewell messages.

## 7. Roadmap

| Phase | Weeks | Outcome |
|---|---|---|
| 0. Engine | done | This repo: CLI, tests, demo |
| 1. Library v1 | 1–2 | Connectors done; next: fetch + ingest the CC library, QA by ear, list gaps to commission |
| 2. Web MVP | built; 1 to deploy | Single-page app + credits panel built; next: deploy, shareable links |
| 3. Creator loop | 2 | Build in public on TikTok: "I turned your comments into a song" series. Content and user research at once |
| 4. Premium | 4+ | Auth + Stripe, 30k chars as background jobs, moods, mix modes, video export |
| 5. Licensing | ongoing | Lawyer review; approach aggregators/labels with traction numbers |

## 8. Open questions for KS

1. ~~**Library path**~~ → Creative Commons + royalty-free first (decided). Owned word bank later, for premium moods.
2. **Personal tool or public product?** A private bring-your-own-songs tool can ship this week; a public app needs path 1/2.
3. **Languages:** English only for MVP, or Singlish/Mandarin/Malay words early as the local differentiator?
4. **Tie-in with the creator brand:** run it as a TikTok series from day one (content pillar 4, "building in public")?

---

*Next concrete step:* on your own machine, run `scripts/build_cc_library.sh library 3` and then `songspeak serve --library library`.
Type five messages you'd actually send and note which words are missing or sound wrong. That list becomes the brief for library v2.
