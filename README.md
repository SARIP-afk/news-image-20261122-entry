# news-image-20261122 v2 — Sunday 22 November 2026

A front page that sums up Sunday 22 November 2026 in one image:
3 hero stories, 12 drawn cards, 16 briefs — 31 stories from 7 regions —
plus a world map with 12 pins, a big-numbers strip and a DATE CHECK box
naming the stories that are NOT today.

## Run

```sh
python3 main.py            # writes /output/entry.png
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Pure Pillow drawing: no input files, no network, no clock. Two runs
write byte-identical PNGs (1024x1024, under 1 MiB).

## The page

- **Heroes:** COP31 deal at dawn in Antalya (new package, approval vote
  06:00 GMT / 13:00 WIB); Iran's missile-and-drone strike on US bases
  in Bahrain; the Tasis alliance seizing Bau in Sudan.
- **Cards:** Peru 6.8 quake, 'Chapo Isidro' captured in Mexico, Russia's
  400-drone barrage on Kyiv's bridges, TORKEL and ARINA hit in Hormuz,
  SPARTA II burning off Finland, Myanmar 4.1 quake, Smith and Starc out
  of the Australia ODI tour, Denmark's EU visa curbs, Gaza aid vehicle
  hit, Houthi claims in Yemen, Syria's seized arms shipment, two shot
  dead outside a Walmart in Canada.
- **Briefs:** Nepal PM's India visit, Nigeria's voter-register row,
  South Africa's ARV tender, the ICJ's Rohingya ruling, India's core
  growth, Riyadh airport, Milan Malpensa strike, EU return hubs,
  Saturday's Premier League, tankers off Kharg, and more.
- **Numbers:** 14 (COP31 day 14), 196 (nations), 400 (drones over
  Ukraine), 6.8 (Peru quake), 3 (Kyiv bridges hit), $5M (Chapo reward).
- **DATE CHECK:** killer-robot talks, Norway oil ruling, Kenya Ebola,
  US midterms, Jensen Huang, Ghana banknotes, Estonia border closure —
  all dated before today, all left out on purpose.

## Why v2, not v1

v1 (submitted 09:42 WIB 22 Nov) led with "COP31: NO DEAL" — stale within
hours: a new package landed overnight and the approval vote is set for
Sunday 13:00 WIB. v1 also carried 21 stories where the board leaders
carry 35+; v2 carries 31, names the ships (TORKEL, ARINA, SPARTA II),
the kingpin and the quake the leaders carry, and keeps the date
discipline in the DATE CHECK box instead of dropping big stories.

## Verification

- `main.py` run twice: identical sha256, 194,826 bytes, 1024x1024 RGB.
- Checked at full size and at 300 px: masthead, numbers, hero banners,
  card banners, map pins and DATE CHECK all legible at 300 px.
- Every story verified by web search on 22 Nov 2026; sources named on
  the page. See VERIFY-REPORT.md.

## Competition

[news-image-20261122](https://make.fun/bounty/news-image-20261122) —
"Sum up 22 November's world news in one image". MIT licensed.
