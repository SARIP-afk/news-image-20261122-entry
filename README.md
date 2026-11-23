# Sunday 22 November 2026 — THE WORLD, globe edition (TOP10 candidate V3.2)

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/SARIP-afk/news-image-20261122-entry/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/SARIP-afk/news-image-20261122-entry/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

A premium international newspaper front page built around one big 3D
globe: masthead "THE WORLD" (with a small globe in the O), "THE DAY IN
WORLD NEWS" across the globe, three hero stories, six region panels,
14 more stories, a DATE CHECK line and a sources footer — 1024x1024,
35 dated stories, 6 regions.

## What V3.2 is

Final candidate refinement on the V3.1 baseline (V3.1 is the best
candidate baseline; V3.2 changes ONLY what the audit and the brief
required). Fact work: third independent from-scratch audit
(AUDIT-V32.md, adopted as FINAL-FACT-CHECK.md) — 34 VERIFIED / 1
CORRECTED / 0 REPLACED / 0 UNVERIFIED as printed on V3.1; the one
remaining error was the Dymer deck ("2 killed, 14 missing" understated
the Sunday toll — now "at least 3 killed, 11 feared buried" per AP).
Visual work:
- Hero 2 (Bahrain) smoke rebuilt AGAIN for volume: V3.1's wisps were
  lobe-free but nearly invisible. V3.2 stacks three layers (dense warm-lit
  core, mid wisps, faint top drift) with bigger shapes, higher alpha and
  a softer blur, so the column reads as smoke with volume, layers and a
  rightward drift — still no round lobes (every shape rx/ry >= 2.4).
- Hero 3 (Dymer): ladder chain kept; added a second crew member guiding
  the ladder, a dangling wire, a facade crack, an extra dusk cloud, and
  the same volume smoke treatment for the notch column.
- Readability: BODY/MUTED brightened one step, panel detail brighter
  (228,235,248), bullet gap 13→14 px.
- Globe: 6→8 cloud swirls + 3 faint ocean swirl arcs.
- main.py is a FRESH stdlib loader written in this session (argv path
  or stdout output); the V3.1 loader is never copied.

## What V3.1 is

Final factual integrity + visual readability pass on the V3 baseline
(V3 is accepted as the best visual baseline; V3.1 changes ONLY what
the audit and the readability brief required). Visual work:
- Hero 2 (Bahrain) smoke rebuilt with a genuinely different approach:
  the blurred discs are gone; the column is now 7 layered ELONGATED
  soft wisps (wide, short ellipses, drifting right as they rise,
  GaussianBlur 5) + 2 thin wavy filaments. Flames have rounded tips +
  a warm glow disc. Verified at 3x: NO round lobes remain.
- Hero 3 (Dymer) truck → ladder → rescuer → damage chain rebuilt:
  truck moved under the destroyed stairwell notch; ladder runs from
  the truck roof straight INTO the notch opening; rescuer enlarged and
  placed ON the ladder at the notch with a warm work-light behind him;
  light-bar glow on the building base; notch smoke uses the same
  elongated-wisp treatment.
- Panel readability: illustrations 74→70px to buy type room; headlines
  sans bold 12→13px (leading 14), all 18 measured to fit 2 lines at
  max width 142px; details brightened to (214,223,238) on the dark
  bullet band; bullet gap 14→13px. Nothing else on the page moved.
- Gold arcs stay in empty navy only — none crosses a hero.

## What V3.1 fixed that V3 got wrong (facts)

The fact set was re-audited AGAIN from scratch by an independent
auditor (full report: FINAL-FACT-CHECK.md). The V3 audit's own
"35/35 verified" claim was wrong a second time: the re-audit found
23 verified / 12 corrected / 0 cannot-verify — and the coordinator
spot-checked the two gate failures and confirmed both. Final tally as
printed: 24 verified / 11 corrected / 0 cannot-verify / 1 replaced.
- Walmart CUT: IHIT named the victims on 18–19 Nov, NOT 22 Nov (the
  V3 audit's "reported 21–22 Nov" was wrong). Replaced by Wembanyama's
  50-point game (Sat 21 Nov, reported Sun 22 Nov; ESPN + BBC Sport).
- Cikande: "24 dead" was only confirmed Mon 23 Nov — the page prints
  "24 body bags in Cikande fire" (Sunday fact). Bayelsa toll 29, not
  24 (Gov. Diri, Sunday afternoon). Democrats: "258+" not "258" (AP:
  "at least 258"). Malpensa: 4-hour strike, 13:00–17:00, not 24-hour.
  Kharg: "14+" tankers, convoy unconfirmed. Gaza film: "in Gaza City",
  not "in shelter". Kremlin: reframed to Lavrov's "traditionally
  Russian lands" quote (ISW + multiple outlets) — not a Kremlin
  war-aims statement. Norway (COP31 refuser), "2 wounded" (Bahrain),
  €32bn (Czech budget) and the Hormuz mine as a third vessel were
  never printed on the page and stay out.
- The V3 replacements all survived the re-audit in substance (Tonj
  East, Black Foils, India–China talks, Czech budget, Khartoum drones).
- "196 nations at the table" is NOT verified (sources say "more than
  190 countries" / 194 delegations / "nearly 200") — the page does not
  print 196 anywhere.

How it is built: the page is rendered at build time with Pillow and
real serif/sans fonts (`render.py`, run in this session). `main.py`
itself is a tiny pure-stdlib loader written fresh in this session: it
reads `entry.png` from beside it, validates it (under 1 MiB, PNG
signature, every chunk CRC-checked, IHDR 1024x1024 8-bit RGB, IEND at
the end, IDAT decompressing to a full RGB frame), and writes the
identical bytes to `$MAKEFUN_OUTPUT_DIR/entry.png`. The grader runs
vanilla Python, and `main.py` imports nothing beyond the standard
library — no Pillow at run time.

Facts: see `FACTS.md` — 35 stories, all dated 22 Nov 2026 with
sources. Layout: see `STORYBOARD.md`. The three heroes are the
verified leads: COP31 collapses with no deal (Antalya), Iran claims
Bahrain strikes, 186 drones over Kyiv / Dymer block hit.

## Run

```sh
MAKEFUN_OUTPUT_DIR=/tmp/out python3 -P -s main.py
# writes /tmp/out/entry.png (1024x1024, < 1 MiB, deterministic,
# byte-identical to entry.png)
```

## Status

Candidate only — NOT submitted, NOT bundled, NOT pushed. V1, V2, V3
and the standing entry (v3, newspaper style) are untouched in their
own directories. Verified hashes (see BACKUP-HASHES.md): V1 entry.png
a3bd073b…, V2 entry.png 860426ab…, V3 entry.png 831c9256…, v3 entry.png
050d3d6e…. This candidate: entry.png 226,162 bytes, sha256
dc9ef0b37943714d433668552e53ab190fdfec867fe8c84d918512f17b97b0c8.
