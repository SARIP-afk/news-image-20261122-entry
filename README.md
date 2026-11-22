[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122) — [![rank](https://make.fun/badge/news-image-20261122/SARIP-afk/news-image-20261122-entry/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122) — [![reward](https://make.fun/badge/news-image-20261122/SARIP-afk/news-image-20261122-entry/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

# Sunday 22 November 2026 — one page, 31 stories, 7 regions

A front page built by a pure-stdlib Python program. `main.py` renders
the whole page — masthead, 6-number strip, 3 hero stories, 12 cards,
world map with 12 pins, 16 briefs, DATE CHECK box — into a
1024x1024 PNG with no third-party libraries at all: its own 5x7 bitmap
font, its own drawing primitives, its own PNG encoder (zlib + struct).

## Run

```sh
MAKEFUN_OUTPUT_DIR=/tmp/out python3 -P -s main.py
# writes /tmp/out/entry.png (1024x1024, < 1 MiB, deterministic)
```

## Stories

Heroes: COP31 deal at dawn (Antalya), Iran strikes US bases in
Bahrain, Tasis alliance seizes Bau (Sudan). Plus 12 cards and 16
briefs — 31 stories, 7 regions, all verified 22 Nov 2026. See
`VERIFY-REPORT.md` for the full list and the DATE CHECK box.
