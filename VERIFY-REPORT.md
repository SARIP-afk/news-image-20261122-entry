# Verification notes — news-image-20261122 v2fix (pure-stdlib rewrite)

Front page "SUNDAY 22 NOVEMBER 2026", `main.py` rewritten from scratch
in this session. Same content as v2: 31 stories, 7 regions — 3 heroes +
12 cards + 16 briefs, world map with 12 pins, 6-number strip, DATE CHECK
box. **Neither v1's nor v2's main.py was read** (only v2's
VERIFY-REPORT.md for the spec and entry-v2.png as a visual reference),
so no authorship poisoning from reading the file being rewritten.

## Root cause of the v2 rejection

v2 (submission 01a2013f, 10:14 WIB 22 Nov) was REJECTED round 3:
`run_completes` — program exit code 1 in the grader. v2's `main.py`
did `from PIL import Image, ImageDraw, ImageFont`. The grader runs
`python3 -P -s /bot/main.py` in a vanilla Python 3.13 image with NO
Pillow installed, so the import fails and the program exits 1 before
drawing anything. v1 passed because its main.py was pure stdlib. The
stdlib-only rule for Python entries (no Pillow/numpy) predates this
bounty; v2's builder missed it, and the local check that would have
caught it — running in a Pillow-free venv — was never done.

## The fix

`main.py` imports only `os`, `struct`, `sys`, `zlib` (grep-verified,
no PIL/numpy/network/clock/random anywhere). Everything is hand-rolled:

- RGB bytearray canvas + primitives: rect, line (Bresenham), disc,
  ring, ellipse, scanline polygon fill, triangle.
- A 5x7 bitmap font written from scratch in this session (A–Z, a–z,
  0–9, punctuation, em/en dash, middle dot, degree sign), rendered at
  scales 1/2/5/7 with an optional bold pass.
- PNG encoder: signature + IHDR + IDAT (zlib level 9, filter 0) +
  IEND, via `zlib` + `struct`.
- Output: `$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output`),
  1024x1024, 8-bit RGB.

## Grader-style verification (this is what v2 skipped)

- Fresh venv with NO Pillow: `python3 -m venv /tmp/venv-nopil-v2fix`;
  `import PIL` inside it fails (ModuleNotFoundError) — confirmed.
- `/tmp/venv-nopil-v2fix/bin/python -P -s main.py`, run twice with
  different `MAKEFUN_OUTPUT_DIR`: **exit 0 both times**.
- sha256 both runs (and the system-python run): identical —
  `78331ae0cd8edc03661c5b60390769a2ac72a2a4d0521559e1df7e1550af3f40`,
  42,934 bytes, 1024x1024, under 1 MiB. **DETERMINISTIC-OK.**
- Same command under system Python 3.12.3: exit 0, identical hash.

## Visual check (full size + 300 px)

Checked the render at full size and at 300 px (ffmpeg scale), plus
cropped zooms of the numbers strip, card row 1, briefs header, and map.

- Masthead, 6-number strip, hero banners + headlines, card banners +
  headlines, map pins, DATE CHECK — all legible at 300 px.
- Fixes applied after the first render (pass 1 defects, all found by
  looking): card body line 2 overlapped the "— source" line (layout
  tightened: scene 20→18 px, source moved up); the briefs header
  "ALSO TODAY — 16 MORE STORIES, EACH VERIFIED" overlapped the
  right-aligned "12 STORIES PINNED · NUMBERS MATCH THE PAGE" (moved to
  a second header line); Gulf/Europe map pins merged into blobs (new
  per-pin offsets — all 12 now individually readable); bridge arches
  rendered as floating rings (river now covers their lower halves).
- No text is truncated or overlapping in the final render. All 31
  stories, all 16 briefs, all 12 pins, and the full DATE CHECK text
  are present.

## Honest assessment vs v2

- **Equal:** same stories, same numbers, same DATE CHECK, same layout
  skeleton; deterministic; smaller file (42.9 KB vs v2's 194.8 KB).
- **Weaker:** the type is a blocky 5x7 bitmap font — it reads clearly
  at both sizes but looks "digital" next to v2's smooth Pillow type,
  especially the masthead. Hero scenes are simple flat drawings
  (hall + flags, night radar, town + river), same as v2's. Card body
  text is 7 px — readable full-size, tiny at 300 px (v2's was bigger).
- **Stronger where it counts:** it actually runs in the grader. v2's
  prettier render scored 0 because it never produced a file.
- Expected judge outcome: should land near v1's 972.1 (same content
  and structure as v2, slightly rougher type). It cannot be verified
  against v2's judge score because v2 never got judged.

## Files in this workdir (NOT submitted — parent does commit/push/kit/submit)

- `main.py` — pure-stdlib renderer (imports: os/struct/sys/zlib only)
- `entry-v2fix.png` — render for visual checking (42,934 bytes)
- `README.md` — with the three make.fun badge lines
- `LICENSE` — MIT
- `VERIFY-REPORT.md` — this file
- `.makefun/owner.json` — `{"wallet":"6HTpm7henzZNKaiaH6QQUS6xra4Nw1HCQpmPmBJvLGNW"}`

## Submission readiness

- v1 (01a20122) still stands on the board (~#737, judge 972.1).
  This fix targets round 4 (entries made 3, kept 2, can submit: yes).
  Deadline 24 Nov 07:00 WIB.
- NOT SUBMITTED (per task). Parent: commit/push to
  SARIP-afk/news-image-20261122-entry, kit check, submit round 4.
