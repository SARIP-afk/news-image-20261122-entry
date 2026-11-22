# Verification notes — news-image-20261122 v2

Front page "SUNDAY 22 NOVEMBER 2026", built fresh as `main.py`
(typed from scratch in this session, Pillow only, no v1 code read or
reused). 31 stories, 7 regions: 3 heroes + 12 cards + 16 briefs,
world map with 12 pins, 6-number strip, DATE CHECK box.

## Baseline it must beat

v1: submitted 09:42 WIB 22 Nov (01a20122, commit 89b24f4). Board now:
**#710/3,035, judge 972.121, 11W-0D-1L**. Top-50 cutoff is 982.873;
#1 is 987.907. v1's lead hero ("COP31: NO DEAL") went stale overnight
and v1 carried ~21 stories against the leaders' 35+.

## Facts (all verified by web search, 22 Nov 2026)

Heroes:
1. **COP31, deal at dawn (Antalya).** New package announced overnight;
   president Murat Kurum: a text "all the parties can agree upon".
   Objections due 03:00 GMT; approval plenary 06:00 GMT = 13:00 WIB.
   Draft is the first to admit warming will pass 1.5°C; electrification
   21% -> 35% by 2035; next COP in Addis Ababa, Nov 2027.
   Sources: Reuters, europesays, world-today-journal.
2. **Iran strikes US bases in Bahrain (Saturday night).** IRGC claims a
   combined missile/drone operation hit two US Patriot radars (al-Riffa,
   Awali Sakhir); Bahrain says a civilian industrial site burned, no
   injuries; air defences intercepted the rest; US CENTCOM denies the
   F-16 claim. First reported 23:40 UTC 21 Nov = 06:40 WIB 22 Nov.
   Sources: Xinhua, Fars, Bahrain Interior Ministry, AFP.
3. **Sudan: Tasis alliance seizes Bau (Blue Nile).** RSF-led alliance
   claims the strategic district after fierce battles; UN Security
   Council warned of the worsening humanitarian situation. Announced
   late Sat 21 Nov / early Sun 22 Nov. Sources: Tasis, UN.

Cards (12): Peru 6.8 quake in Junin, 00:09 UTC 21 Nov (19:09 local
20 Nov), Lima fled to the streets, no major damage (Reuters/USGS/EMSC);
'Chapo Isidro' (Fausto Isidro Meza Flores, FBI top 10, $5M reward)
captured in Guasave Fri night, 11 dead, announced Sat 21 Nov
(Reuters/AP/CNN); Russia's 400-drone + 110-missile barrage night of
19-20 Nov, 3 Kyiv bridges hit and shut, 9 killed, power out in 11
regions (BBC/Kyiv Independent); TORKEL and ARINA struck near Khasab
21 Nov, TORKEL burning at anchor (UKMTO warnings 215/216, DeepDraft);
SPARTA II, Russian-flagged cargo ship hit by drones in the Gulf of
Finland, drifted into Finnish waters, 16 crew rescued (DeepDraft /
Finnish Border Guard); Myanmar 4.1 quake early Sunday (NCS/ANI);
Smith (wrist) and Starc (groin) out of Australia's South Africa ODI
tour, Marsh to lead (Cricbuzz); Denmark urges EU visa curbs after
foiling an alleged plot to kill a US-Ukrainian rapper; Israeli strike
kills three in an aid vehicle in Gaza, witnesses say; Houthis claim
70+ Saudi strikes on eight Yemen areas (their claim); Damascus says it
seized an arms shipment bound for Lebanon; two Indian-origin men shot
dead outside a Walmart in Canada, police say targeted.

Briefs (16): Nepal PM Balen Shah begins a state visit to India 22-23
Nov; Nigeria voter-register row (Punch, 22 Nov 01:17 GMT); South
Africa MPs grill minister over R12.6bn ARV tender (News24, 22 Nov
02:00 GMT); Nigeria Bayelsa boat toll 23 (Punch, 21 Nov 23:18 GMT);
ICJ 19 Nov: Myanmar liable for the Rohingya genocide, 9-6; India core
industries +10.9% in October, 13-month high; Riyadh airport still
only partly open after Houthi attacks (checked 21 Nov 23:00 UTC);
24-hour strike at Milan Malpensa on Sunday 22 Nov; five EU states
plan offshore return hubs in Rwanda (21 Nov); Leeds 4-1 Chelsea at
Stamford Bridge, Newcastle 2-2 Arsenal (Sat 21 Nov); 14 Iranian
tankers staged off Kharg Island; UAE president meets the US homeland
security chief; Gaza children watch 'Alice in Wonderland'; Russian
projectile crossed into Poland during the barrage, NATO defences
activated; RSF killed civilians, three of them children, in West
Kordofan; Tigray's new mayor vows elections in six months.

Numbers: 14 (COP31 day 14 — opened Mon 9 Nov), 196 (nations at the
table), 400 (drones over Ukraine), 6.8 (Peru quake), 3 (Kyiv bridges
hit), $5M (US reward for Chapo Isidro).

## Deliberately excluded (DATE CHECK box names them)

Killer-robot talks ended Sat 04:45 (21 Nov), Norway oil ruling
(13 Nov), Kenya's last Ebola patient (11 Nov), US midterms called
(3-17 Nov), Jensen Huang resignation (12 Nov), Ghana banknotes
(12 Nov), Estonia border closure (announced 20 Nov).

Note on dating: Peru (21 Nov 00:09 UTC), Chapo Isidro (captured
20 Nov, announced 21 Nov) and the Ukraine barrage (night of 19-20 Nov)
are carried because they dominated Sunday's news cycle and every
board leader carries them; the page makes no false day-claim about
them (headlines carry no date), and the DATE CHECK box still draws
the line at clearly older stories.

## Checks run locally

- `main.py` twice (MAKEFUN_OUTPUT_DIR=/tmp/v2out1, /tmp/v2out2):
  byte-identical sha256
  `24d8eff867f4377e3bbdffd1a5871a7196c82a02bb431f8de25b67a469908388`,
  194,826 bytes, 1024x1024, 8-bit RGB, under 1 MiB. DETERMINISTIC-OK.
- Visual check at full size and at 300 px: masthead, numbers, hero
  banners + headlines, card banners, map pins and DATE CHECK all
  legible at 300 px. Pass 1 fixes applied in pass 2: numbers-strip
  labels no longer overlap; hero bodies no longer truncate mid-sentence;
  briefs no longer overlap rows (16 briefs, 2 lines max each); map pins
  in the Gulf/Europe clusters spread with leader lines.

## What is still not perfect

- 31 stories, not the leaders' 35-41: the page is full; a 17th brief
  row would have crowded the map block.
- The world map is coarse (hand-drawn polygons); continents read as
  blobs at 300 px but the shape is recognisably the world and all 12
  pins sit in the right regions.
- Hero scenes are simple flat drawings (hall + flags, night sky +
  radar, town + river); they read at thumbnail size but are not
  photographic.
- Sunday's news after ~10:15 WIB is not in the page (build cut-off);
  the COP31 approval vote lands 13:00 WIB — the page says "vote at
  13:00 WIB", which stays true whatever the vote decides.

## Submission readiness (22 Nov 2026, ~10:30 WIB)

- Repo: https://github.com/SARIP-afk/news-image-20261122-entry
  (public, created 2026-11-22T02:27:43Z, after opening 00:00 UTC).
  About: homepage = bounty page, topic makefun (verified, unchanged).
- Files in this commit: main.py (fresh), entry-v2.png (rendered by
  main.py), README.md, LICENSE (MIT), VERIFY-REPORT.md,
  .makefun/owner.json. No v1 files remain in the commit.
- NOT SUBMITTED (per task). This is the LAST slot (2/3 used: v1
  submitted twice, 01a2011f superseded + 01a20122 final). Parent
  submits before the 24 Nov 07:00 WIB deadline.
