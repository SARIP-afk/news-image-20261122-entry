#!/usr/bin/env python3
"""news-image-20261122 v2: one front page summing up Sunday 22 November 2026.

Draws the whole page with Pillow and writes /output/entry.png (or
$MAKEFUN_OUTPUT_DIR/entry.png). No network, no input files, no clock:
two runs write byte-identical PNGs.

31 stories, 7 regions: 3 hero scenes + 12 drawn cards + 16 briefs,
a world map with 12 pins, a big-numbers strip and a DATE CHECK box
naming the stories that are NOT today.
"""
import hashlib
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (248, 244, 233)
INK = (20, 20, 20)
GREY = (90, 86, 76)
FAINT = (168, 160, 140)
RED = (176, 30, 36)
NAVY = (28, 47, 87)
TEAL = (15, 107, 92)
ORANGE = (194, 94, 16)
PURPLE = (91, 58, 140)
GOLD = (180, 138, 20)
CREAM = (255, 250, 235)
MAPSEA = (22, 38, 63)
MAPLAND = (232, 220, 192)
PINRED = (214, 38, 38)

FONTDIR = "/usr/share/fonts/truetype/dejavu"


def F(kind, size):
    name = {
        "serif": "DejaVuSerif.ttf",
        "serifb": "DejaVuSerif-Bold.ttf",
        "sans": "DejaVuSans.ttf",
        "sansb": "DejaVuSans-Bold.ttf",
    }[kind]
    return ImageFont.truetype(os.path.join(FONTDIR, name), size)


def wrap(d, text, font, width):
    """Greedy word wrap to a list of lines fitting `width` pixels."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if d.textlength(trial, font=font) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def block(d, x, y, text, font, width, fill=INK, leading=None, max_lines=None):
    """Draw wrapped text; return y just below the last line."""
    if leading is None:
        leading = font.size + 3
    lines = wrap(d, text, font, width)
    if max_lines is not None:
        lines = lines[:max_lines]
    for ln in lines:
        d.text((x, y), ln, font=font, fill=fill)
        y += leading
    return y


def hline(d, x0, x1, y, fill=INK, width=2):
    d.line([(x0, y), (x1, y)], fill=fill, width=width)


def sky(d, box, top, mid, bottom):
    """Vertical 3-stop gradient inside box (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = box
    h = y1 - y0
    for yy in range(y0, y1):
        t = (yy - y0) / max(1, h)
        if t < 0.5:
            a, b, u = top, mid, t * 2
        else:
            a, b, u = mid, bottom, (t - 0.5) * 2
        c = tuple(int(a[i] + (b[i] - a[i]) * u) for i in range(3))
        d.line([(x0, yy), (x1, yy)], fill=c)


# ---------------------------------------------------------------- data
NUMBERS = [
    ("14", "DAY 14\nOF COP31"),
    ("196", "NATIONS\nAT THE TABLE"),
    ("400", "DRONES\nOVER UKRAINE"),
    ("6.8", "PERU\nQUAKE"),
    ("3", "KYIV BRIDGES\nHIT"),
    ("$5M", "REWARD FOR\nCHAPO ISIDRO"),
]

# region counts, computed from the story list below (must sum to 35)
REGIONS = [
    ("MIDDLE EAST", 9),
    ("EUROPE", 8),
    ("AFRICA", 6),
    ("ASIA", 3),
    ("AMERICAS", 3),
    ("OCEANIA", 1),
    ("GLOBAL", 1),
]

HEROES = [
    {
        "banner": "COP31: DEAL AT DAWN",
        "color": RED,
        "tag": "CLIMATE \u00b7 ANTALYA",
        "scene": "cop31",
        "headline": "Deal at dawn in Antalya",
        "body": "A new package lands overnight; president Murat Kurum calls it a text \u201call the parties can agree upon\u201d. Objections due 03:00 GMT; the approval vote is at 06:00 GMT \u2014 13:00 WIB. First draft to admit 1.5\u00b0C will be passed.",
        "source": "\u2014 Reuters",
    },
    {
        "banner": "BAHRAIN: MISSILES",
        "color": NAVY,
        "tag": "GULF \u00b7 SATURDAY NIGHT",
        "scene": "bahrain",
        "headline": "Iran strikes Bahrain bases",
        "body": "The Revolutionary Guard says it hit two US Patriot radars at al-Riffa and Awali in a missile-and-drone attack. Bahrain says a civilian site burned; no one was hurt. The US denies its F-16 claim.",
        "source": "\u2014 Xinhua / Bahrain",
    },
    {
        "banner": "SUDAN: BAU FALLS",
        "color": ORANGE,
        "tag": "WAR \u00b7 BLUE NILE",
        "scene": "sudan",
        "headline": "Tasis alliance seizes Bau",
        "body": "The RSF-led alliance claims the strategic Blue Nile district after fierce battles. The UN Security Council warns the humanitarian crisis is worsening as the war spreads.",
        "source": "\u2014 Tasis / UN",
    },
]

CARDS = [
    ("PERU: QUAKE", RED, "peru",
     "A 6.8 quake shook Jun\u00edn; Lima fled to the streets. No major damage reported.",
     "\u2014 Reuters"),
    ("MEXICO: KINGPIN CAUGHT", NAVY, "mexico",
     "FBI most-wanted \u2018Chapo Isidro\u2019 seized in Guasave; 11 die in the raid.",
     "\u2014 Reuters / AP"),
    ("UKRAINE: BRIDGES HIT", PURPLE, "ukraine",
     "400 drones and 110 missiles; three Kyiv bridges shut, nine killed.",
     "\u2014 BBC"),
    ("HORMUZ: TANKERS HIT", TEAL, "hormuz",
     "TORKEL and ARINA struck near Khasab; TORKEL burns at anchor.",
     "\u2014 UKMTO"),
    ("FINLAND: SPARTA II", NAVY, "sparta",
     "Russian cargo ship hit by drones off Finland; 16 crew saved.",
     "\u2014 Border Guard"),
    ("MYANMAR: QUAKE", ORANGE, "myanmar",
     "A 4.1 tremor rattles the country early on Sunday.",
     "\u2014 ANI / NCS"),
    ("CRICKET: OUT", TEAL, "cricket",
     "Smith (wrist) and Starc (groin) out of the SA tour; Marsh to lead.",
     "\u2014 Cricbuzz"),
    ("DENMARK: VISAS", PURPLE, "denmark",
     "Denmark urges EU visa curbs after police foil a plot to kill a US-Ukrainian rapper.",
     "\u2014 reports"),
    ("GAZA: AID HIT", RED, "gaza",
     "An Israeli strike kills three in an aid vehicle, witnesses say.",
     "\u2014 witnesses"),
    ("YEMEN: STRIKES", ORANGE, "yemen",
     "Houthis claim 70+ Saudi strikes on eight areas; the claim is theirs alone.",
     "\u2014 Houthis"),
    ("SYRIA: SEIZED", TEAL, "syria",
     "Damascus says it seized an arms shipment bound for Lebanon.",
     "\u2014 Syria"),
    ("CANADA: SHOT DEAD", RED, "canada",
     "Two Indian-origin men shot dead outside a Walmart; police call it targeted.",
     "\u2014 police"),
]

BRIEFS = [
    ("NEPAL", "PM Balen Shah begins a two-day state visit to India."),
    ("NIGERIA", "Voter-register row sparks fears of manipulation in 2027 polls."),
    ("SOUTH AFRICA", "MPs grill minister over R12.6bn ARV tender."),
    ("NIGERIA", "Bayelsa boat death toll rises to 23."),
    ("ICJ", "Court finds Myanmar liable for the Rohingya genocide, 9\u20136."),
    ("INDIA", "Core industries grow 10.9% in October, a 13-month high."),
    ("SAUDI", "Riyadh airport still only partly open after Houthi attacks."),
    ("ITALY", "24-hour strike at Milan Malpensa today."),
    ("EU", "Five states plan offshore return hubs in Rwanda."),
    ("FOOTBALL", "Leeds stun Chelsea 4-1; Newcastle hold Arsenal 2-2."),
    ("GULF", "14 Iranian tankers mass off Kharg to test the US blockade."),
    ("UAE", "President meets the US homeland security chief."),
    ("GAZA", "Children watch \u2018Alice in Wonderland\u2019 in Gaza."),
    ("POLAND", "Russian projectile crossed into Poland; NATO defences activated."),
    ("SUDAN", "RSF killed civilians, three of them children, in West Kordofan."),
    ("TIGRAY", "New mayor vows elections within six months."),
]

DATE_CHECK = (
    "Killer-robot talks ended Sat 04:45 \u00b7 Norway oil ruling \u2014 13 Nov \u00b7 "
    "Kenya\u2019s last Ebola patient \u2014 11 Nov \u00b7 US midterms called \u2014 3\u201317 Nov \u00b7 "
    "Jensen Huang resignation \u2014 12 Nov \u00b7 Ghana banknotes \u2014 12 Nov \u00b7 "
    "Estonia border closure \u2014 20 Nov"
)

# pins: (number, lon, lat, dx, dy) -- dx/dy nudge the label off the point
PINS = [
    (1, 30.7, 36.9, -18, -16),    # Antalya
    (2, 50.6, 26.2, 18, -10),     # Bahrain
    (3, 34.0, 11.3, 0, 12),       # Bau, Sudan
    (4, -75.9, -11.2, -14, 8),    # Junin, Peru
    (5, -108.5, 25.6, -16, -10),  # Guasave, Mexico
    (6, 30.5, 50.4, 18, 2),       # Kyiv
    (7, 56.2, 26.2, 20, 12),      # Khasab / Hormuz
    (8, 27.0, 60.0, 16, -18),     # Gulf of Finland
    (9, 96.0, 21.0, 12, 10),      # Myanmar
    (10, 151.2, -33.9, 10, 10),   # Sydney
    (11, 12.6, 55.7, -14, -14),   # Copenhagen
    (12, 34.5, 31.5, -20, 14),    # Gaza
]

# ---------------------------------------------------------------- scenes
def scene_cop31(d, box):
    x0, y0, x1, y1 = box
    sky(d, box, (255, 196, 110), (255, 150, 80), (120, 70, 110))
    cx, cy, r = x0 + (x1 - x0) * 0.72, y0 + (y1 - y0) * 0.42, 26
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 240, 180))
    d.polygon([(x0, y1), (x0, y1 - 34), (x0 + 60, y1 - 52), (x0 + 150, y1 - 40),
               (x0 + 210, y1 - 56), (x0 + 280, y1 - 38), (x1, y1 - 46), (x1, y1)],
              fill=(58, 32, 66))
    # conference hall: columns + roof
    hx, hy = x0 + 18, y1 - 58
    d.rectangle([hx, hy, hx + 120, y1 - 8], fill=(30, 26, 40))
    d.polygon([(hx - 8, hy), (hx + 128, hy), (hx + 110, hy - 14), (hx + 10, hy - 14)],
              fill=(200, 60, 50))
    for i in range(5):
        px = hx + 12 + i * 24
        d.rectangle([px, hy + 6, px + 8, y1 - 8], fill=(255, 214, 130))
    # flags
    for i, c in enumerate([(176, 30, 36), (28, 47, 87), (15, 107, 92), (180, 138, 20)]):
        fx = x1 - 78 + i * 18
        d.line([(fx, y1 - 52), (fx, y1 - 18)], fill=INK, width=2)
        d.polygon([(fx, y1 - 52), (fx + 14, y1 - 48), (fx, y1 - 44)], fill=c)
    # gavel
    gx, gy = x0 + 150, y1 - 26
    d.line([(gx, gy), (gx + 34, gy - 16)], fill=(90, 50, 20), width=5)
    d.rectangle([gx + 28, gy - 26, gx + 52, gy - 12], fill=(120, 70, 30))
    d.ellipse([gx - 4, gy + 2, gx + 14, gy + 10], fill=(90, 50, 20))


def scene_bahrain(d, box):
    x0, y0, x1, y1 = box
    sky(d, box, (10, 14, 40), (16, 28, 66), (40, 50, 90))
    for sx, sy in [(30, 12), (90, 26), (180, 10), (250, 30), (300, 14), (140, 34)]:
        d.ellipse([x0 + sx - 2, y0 + sy - 2, x0 + sx + 2, y0 + sy + 2], fill=(240, 240, 220))
    d.ellipse([x1 - 62, y0 + 8, x1 - 26, y0 + 44], fill=(235, 230, 200))
    # missile trails
    for tx, ty, ln in [(40, 66, 90), (120, 58, 110), (210, 70, 80)]:
        d.line([(x0 + tx, y0 + ty), (x0 + tx + ln, y0 + ty - 34)], fill=(255, 200, 90), width=3)
        d.ellipse([x0 + tx + ln - 4, y0 + ty - 38, x0 + tx + ln + 6, y0 + ty - 28],
                  fill=(255, 230, 150))
    # radar dishes
    for rx in [70, 250]:
        d.line([(x0 + rx, y1 - 30), (x0 + rx + 26, y1 - 58)], fill=(200, 200, 200), width=3)
        d.pieslice([x0 + rx + 8, y1 - 78, x0 + rx + 44, y1 - 42], 200, 340, fill=(210, 210, 210))
    # sea + ship + smoke
    d.rectangle([x0, y1 - 26, x1, y1], fill=(12, 30, 56))
    d.rectangle([x0 + 130, y1 - 40, x0 + 210, y1 - 26], fill=(20, 20, 24))
    d.rectangle([x0 + 150, y1 - 52, x0 + 170, y1 - 40], fill=(20, 20, 24))
    for sx, sy, r in [(150, 44, 12), (166, 34, 15), (186, 44, 10)]:
        d.ellipse([x0 + sx - r, y0 + sy - r, x0 + sx + r, y0 + sy + r], fill=(120, 120, 125))


def scene_sudan(d, box):
    x0, y0, x1, y1 = box
    sky(d, box, (232, 190, 130), (214, 150, 90), (150, 100, 70))
    d.ellipse([x0 + 250, y0 + 8, x0 + 300, y0 + 58], fill=(255, 226, 150))
    # hills + town
    d.polygon([(x0, y1 - 40), (x0 + 90, y1 - 78), (x0 + 190, y1 - 52), (x0 + 260, y1 - 70),
               (x1, y1 - 44), (x1, y1), (x0, y1)], fill=(120, 84, 52))
    for bx, bw, bh in [(20, 46, 30), (74, 38, 42), (120, 52, 26), (180, 40, 36), (228, 48, 28)]:
        d.rectangle([x0 + bx, y1 - 26 - bh, x0 + bx + bw, y1 - 26], fill=(238, 226, 200))
        d.rectangle([x0 + bx, y1 - 26 - bh, x0 + bx + bw, y1 - 22 - bh], fill=(176, 60, 40))
    # river
    d.rectangle([x0, y1 - 26, x1, y1], fill=(70, 130, 160))
    d.line([(x0, y1 - 14), (x1, y1 - 14)], fill=(180, 220, 235), width=2)
    # smoke columns
    for sx, sy, r in [(90, 30, 11), (104, 20, 14), (240, 26, 12)]:
        d.ellipse([x0 + sx - r, y0 + sy - r, x0 + sx + r, y0 + sy + r], fill=(90, 80, 78))
    # two figures
    for fx in [280, 298]:
        d.ellipse([x0 + fx, y1 - 66, x0 + fx + 8, y1 - 58], fill=(40, 30, 26))
        d.rectangle([x0 + fx + 1, y1 - 58, x0 + fx + 7, y1 - 40], fill=(60, 40, 90))


def mini(d, box, kind):
    """Small 247x34-ish scene for a card."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    if kind == "peru":
        sky(d, box, (250, 220, 170), (220, 180, 130), (170, 130, 90))
        d.polygon([(x0, y1), (x0 + 60, y0 + 6), (x0 + 130, y1), (x0 + 190, y0 + 10),
                   (x1, y1)], fill=(110, 85, 60))
        d.line([(x0 + 20, y1 - 4), (x0 + 60, y1 - 12), (x0 + 100, y1 - 4),
                (x0 + 150, y1 - 14), (x0 + 200, y1 - 6)], fill=(60, 30, 20), width=3)
        d.rectangle([x0 + 210, y1 - 18, x0 + 232, y1], fill=(200, 180, 150))
    elif kind == "mexico":
        sky(d, box, (240, 200, 140), (220, 160, 90), (180, 120, 70))
        d.polygon([(x0, y1), (x0 + 80, y0 + 14), (x0 + 170, y1)], fill=(150, 110, 60))
        d.ellipse([x0 + 30, y0 + 4, x0 + 70, y0 + 16], fill=(40, 40, 46))
        d.line([(x0 + 20, y0 + 8), (x0 + 80, y0 + 8)], fill=(40, 40, 46), width=2)
        d.polygon([(x0 + 150, y1), (x0 + 170, y1 - 16), (x0 + 190, y1)], fill=(220, 90, 20))
        d.polygon([(x0 + 185, y1), (x0 + 200, y1 - 12), (x0 + 215, y1)], fill=(255, 160, 40))
    elif kind == "ukraine":
        sky(d, box, (200, 210, 225), (160, 170, 190), (120, 130, 150))
        d.rectangle([x0, y1 - 10, x1, y1], fill=(70, 110, 150))
        for ax in [40, 120, 200]:
            d.arc([x0 + ax - 26, y0 + 8, x0 + ax + 26, y1 + 6], 180, 360, fill=(50, 50, 58), width=4)
            d.line([(x0 + ax - 26, y1 - 8), (x0 + ax - 26, y0 + 22)], fill=(50, 50, 58), width=3)
            d.line([(x0 + ax + 26, y1 - 8), (x0 + ax + 26, y0 + 22)], fill=(50, 50, 58), width=3)
        d.ellipse([x0 + 100, y0 + 2, x0 + 122, y0 + 24], fill=(255, 200, 60))
        d.ellipse([x0 + 108, y0 + 10, x0 + 114, y0 + 16], fill=(255, 120, 30))
    elif kind == "hormuz":
        sky(d, box, (250, 200, 130), (230, 160, 90), (200, 120, 70))
        d.rectangle([x0, y1 - 14, x1, y1], fill=(40, 90, 120))
        d.rectangle([x0 + 40, y1 - 26, x0 + 190, y1 - 14], fill=(30, 30, 34))
        d.rectangle([x0 + 150, y1 - 34, x0 + 168, y1 - 26], fill=(30, 30, 34))
        d.polygon([(x0 + 90, y1 - 26), (x0 + 104, y1 - 40), (x0 + 118, y1 - 26)], fill=(255, 140, 30))
        d.polygon([(x0 + 108, y1 - 26), (x0 + 120, y1 - 38), (x0 + 132, y1 - 26)], fill=(255, 200, 60))
    elif kind == "sparta":
        sky(d, box, (190, 200, 210), (150, 165, 180), (120, 135, 150))
        d.rectangle([x0, y1 - 12, x1, y1], fill=(90, 110, 125))
        d.polygon([(x0 + 50, y1 - 12), (x0 + 60, y1 - 30), (x0 + 190, y1 - 22),
                   (x0 + 200, y1 - 12)], fill=(60, 60, 66))
        d.rectangle([x0 + 150, y1 - 38, x0 + 166, y1 - 22], fill=(60, 60, 66))
        d.ellipse([x0 + 80, y0 + 2, x0 + 100, y0 + 22], fill=(100, 100, 105))
        d.ellipse([x0 + 92, y0 + 10, x0 + 112, y0 + 30], fill=(120, 120, 125))
        d.ellipse([x0 + 205, y1 - 10, x0 + 225, y1 - 2], fill=(220, 90, 30))
    elif kind == "myanmar":
        sky(d, box, (245, 225, 180), (230, 200, 150), (200, 170, 120))
        d.polygon([(x0 + 190, y1), (x0 + 200, y0 + 8), (x0 + 210, y1)], fill=(140, 90, 40))
        d.rectangle([x0 + 196, y0 + 14, x0 + 204, y1], fill=(160, 110, 50))
        pts = [(x0 + 10, y0 + 20), (x0 + 40, y0 + 8), (x0 + 60, y0 + 26), (x0 + 90, y0 + 6),
               (x0 + 110, y0 + 28), (x0 + 140, y0 + 10), (x0 + 170, y0 + 24)]
        d.line(pts, fill=(176, 30, 36), width=3)
        d.line([(x0, y0 + 30), (x1, y0 + 30)], fill=(120, 100, 70), width=1)
    elif kind == "cricket":
        sky(d, box, (180, 220, 240), (200, 230, 240), (220, 235, 200))
        d.rectangle([x0, y1 - 12, x1, y1], fill=(90, 160, 80))
        d.rectangle([x0 + 100, y0 + 10, x0 + 150, y1 - 12], fill=(210, 190, 140))
        d.ellipse([x0 + 118, y0 + 2, x0 + 130, y0 + 12], fill=(40, 30, 26))
        d.rectangle([x0 + 121, y0 + 12, x0 + 127, y1 - 12], fill=(255, 240, 200))
        d.line([(x0 + 127, y0 + 14), (x0 + 142, y0 + 4)], fill=(150, 100, 40), width=3)
        d.ellipse([x0 + 60, y0 + 26, x0 + 66, y0 + 32], fill=(176, 30, 36))
    elif kind == "denmark":
        sky(d, box, (230, 235, 240), (210, 220, 230), (190, 200, 215))
        d.rectangle([x0 + 90, y0 + 4, x0 + 160, y1 - 4], fill=(20, 40, 110))
        d.ellipse([x0 + 112, y0 + 8, x0 + 138, y0 + 30], outline=(255, 200, 60), width=3)
        d.line([(x0 + 170, y0 + 8), (x0 + 235, y0 + 26)], fill=(176, 30, 36), width=4)
        d.rectangle([x0 + 168, y0 + 6, x0 + 238, y1 - 6], outline=(176, 30, 36), width=3)
        d.text((x0 + 176, y0 + 10), "DENIED", font=F("sansb", 11), fill=(176, 30, 36))
    elif kind == "gaza":
        sky(d, box, (235, 220, 190), (220, 200, 165), (200, 180, 140))
        d.rectangle([x0, y1 - 10, x1, y1], fill=(180, 160, 120))
        d.rectangle([x0 + 80, y0 + 8, x0 + 170, y1 - 10], fill=(245, 245, 240))
        d.rectangle([x0 + 92, y0 + 12, x0 + 158, y0 + 22], fill=(180, 220, 235))
        d.rectangle([x0 + 118, y0 + 24, x0 + 124, y0 + 34], fill=(200, 30, 30))
        d.rectangle([x0 + 112, y0 + 27, x0 + 130, y0 + 31], fill=(200, 30, 30))
        d.ellipse([x0 + 92, y1 - 14, x0 + 102, y1 - 4], fill=(30, 30, 30))
        d.ellipse([x0 + 148, y1 - 14, x0 + 158, y1 - 4], fill=(30, 30, 30))
        d.ellipse([x0 + 185, y0 + 2, x0 + 205, y0 + 22], fill=(120, 115, 110))
    elif kind == "yemen":
        sky(d, box, (240, 210, 160), (220, 180, 120), (190, 150, 100))
        d.polygon([(x0, y1), (x0 + 70, y0 + 6), (x0 + 140, y1), (x0 + 200, y0 + 12),
                   (x1, y1)], fill=(120, 95, 65))
        for ex, ey in [(60, 14), (150, 10), (210, 18)]:
            d.ellipse([x0 + ex - 8, y0 + ey - 8, x0 + ex + 8, y0 + ey + 8], fill=(255, 190, 60))
            d.ellipse([x0 + ex - 3, y0 + ey - 3, x0 + ex + 3, y0 + ey + 3], fill=(255, 120, 30))
    elif kind == "syria":
        sky(d, box, (235, 225, 200), (215, 205, 175), (190, 180, 150))
        d.rectangle([x0, y1 - 10, x1, y1], fill=(170, 150, 110))
        d.rectangle([x0 + 40, y0 + 10, x0 + 150, y1 - 10], fill=(150, 110, 60))
        d.rectangle([x0 + 150, y0 + 14, x0 + 185, y1 - 10], fill=(90, 70, 40))
        d.rectangle([x0 + 158, y0 + 17, x0 + 178, y0 + 26], fill=(180, 220, 235))
        d.ellipse([x0 + 60, y1 - 12, x0 + 72, y1], fill=(30, 30, 30))
        d.ellipse([x0 + 120, y1 - 12, x0 + 132, y1], fill=(30, 30, 30))
        d.ellipse([x0 + 162, y1 - 12, x0 + 174, y1], fill=(30, 30, 30))
        d.line([(x0 + 190, y0 + 6), (x0 + 235, y0 + 28)], fill=(176, 30, 36), width=3)
    elif kind == "canada":
        sky(d, box, (200, 210, 225), (180, 195, 210), (160, 175, 195))
        d.rectangle([x0 + 60, y0 + 6, x0 + 190, y1 - 8], fill=(210, 210, 205))
        d.rectangle([x0 + 60, y0 + 6, x0 + 190, y0 + 20], fill=(20, 60, 160))
        d.text((x0 + 92, y0 + 8), "WALMART", font=F("sansb", 11), fill=(255, 255, 255))
        d.line([(x0, y1 - 12), (x1, y1 - 18)], fill=(240, 200, 30), width=6)
        d.line([(x0, y1 - 6), (x1, y1 - 12)], fill=(240, 200, 30), width=6)


# ---------------------------------------------------------------- map
LAND = [
    # North America
    [(-168, 66), (-140, 70), (-125, 71), (-110, 68), (-95, 69), (-85, 66), (-80, 73),
     (-65, 60), (-55, 52), (-60, 45), (-70, 42), (-75, 35), (-80, 32), (-85, 29),
     (-90, 21), (-95, 19), (-100, 16), (-105, 20), (-115, 28), (-125, 40),
     (-125, 48), (-135, 58), (-155, 60)],
    # Greenland
    [(-58, 64), (-45, 60), (-40, 64), (-30, 68), (-25, 70), (-40, 76), (-58, 74)],
    # South America
    [(-80, 10), (-75, 7), (-70, 11), (-62, 10), (-52, 5), (-50, 0), (-40, -5),
     (-35, -8), (-40, -20), (-48, -28), (-55, -35), (-65, -45), (-70, -52),
     (-73, -50), (-73, -40), (-72, -30), (-70, -18), (-77, -12), (-80, -5)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (-5, 50), (0, 51), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 58), (28, 60), (30, 62), (32, 66), (40, 68), (45, 66),
     (40, 60), (35, 55), (30, 50), (28, 45), (23, 40), (26, 38), (22, 37), (19, 42),
     (12, 44), (8, 44), (3, 42), (0, 40), (-2, 37), (-6, 36)],
    # Africa
    [(-17, 15), (-17, 21), (-10, 27), (-5, 32), (0, 36), (10, 37), (11, 34),
     (20, 32), (30, 31), (32, 31), (35, 28), (34, 27), (37, 22), (40, 15),
     (43, 11), (48, 11), (51, 12), (44, 5), (41, -2), (40, -10), (36, -18),
     (33, -26), (28, -33), (20, -35), (17, -32), (14, -22), (12, -12), (13, -5),
     (9, 4), (4, 6), (-8, 5), (-13, 8)],
    # Asia
    [(40, 68), (50, 70), (60, 69), (70, 72), (80, 73), (90, 75), (100, 76),
     (110, 74), (120, 73), (130, 72), (140, 72), (150, 70), (160, 69), (170, 66),
     (178, 65), (178, 62), (170, 60), (162, 56), (158, 52), (150, 59), (142, 55),
     (140, 45), (135, 43), (130, 42), (127, 40), (122, 38), (120, 32), (122, 28),
     (118, 25), (110, 20), (108, 18), (105, 10), (103, 8), (100, 7), (98, 10),
     (95, 15), (92, 21), (89, 22), (86, 20), (82, 17), (80, 13), (77, 8),
     (75, 12), (72, 20), (68, 23), (66, 25), (62, 25), (58, 26), (56, 27),
     (52, 28), (50, 30), (48, 30), (44, 29), (40, 28), (42, 35), (40, 42),
     (38, 46), (40, 52), (42, 58)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (120, -34), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (150, -22), (146, -19), (142, -15), (142, -11),
     (137, -12), (135, -15), (132, -12), (130, -13), (126, -14), (122, -17),
     (118, -20)],
    # Indonesia islands (rough)
    [(95, 5), (100, 0), (106, -6), (114, -7), (120, -8), (128, -4), (135, -3),
     (140, -2), (138, 1), (130, 1), (122, 0), (115, 1), (108, 3), (100, 5)],
    # Japan
    [(130, 31), (132, 33), (135, 34), (137, 35), (139, 37), (140, 39), (141, 41),
     (142, 43), (143, 44), (145, 44), (143, 42), (141, 39), (139, 36), (136, 34),
     (133, 34), (131, 32)],
    # Britain
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (0, 57), (1, 52), (0, 51)],
    # New Zealand
    [(167, -45), (170, -43), (173, -41), (176, -38), (178, -38), (175, -40),
     (172, -43), (168, -46)],
]


def lonlat(box, lon, lat):
    x0, y0, x1, y1 = box
    x = x0 + (lon + 168) / 360.0 * (x1 - x0)
    y = y0 + (78 - lat) / 136.0 * (y1 - y0)
    return x, y


def draw_map(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=MAPSEA)
    # graticule
    for lon in range(-150, 181, 30):
        gx, _ = lonlat(box, lon, 0)
        d.line([(gx, y0), (gx, y1)], fill=(52, 72, 102), width=1)
    for lat in [60, 30, 0, -30]:
        _, gy = lonlat(box, 0, lat)
        d.line([(x0, gy), (x1, gy)], fill=(52, 72, 102), width=1)
    for poly in LAND:
        pts = [lonlat(box, lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=MAPLAND)
    f_ocean = F("sansb", 10)
    for txt, lon, lat in [("PACIFIC", -150, -8), ("ATLANTIC", -30, -12),
                          ("INDIAN", 85, -28)]:
        ox, oy = lonlat(box, lon, lat)
        d.text((ox - 26, oy - 6), txt, font=f_ocean, fill=(140, 165, 195))
    # pins with leader lines
    f_pin = F("sansb", 11)
    for num, lon, lat, dx, dy in PINS:
        px, py = lonlat(box, lon, lat)
        lx, ly = px + dx, py + dy
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(255, 255, 255))
        if dx or dy:
            d.line([(px, py), (lx, ly)], fill=(255, 255, 255), width=1)
        r = 10
        d.ellipse([lx - r, ly - r, lx + r, ly + r], fill=PINRED, outline=(255, 255, 255), width=2)
        tw = d.textlength(str(num), font=f_pin)
        d.text((lx - tw / 2, ly - 7), str(num), font=f_pin, fill=(255, 255, 255))

# ---------------------------------------------------------------- layout
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    X0, X1 = 12, 1012

    # kicker
    f_kick = F("sansb", 13)
    d.text((X0, 10), "ONE DAY \u00b7 ONE PAGE \u00b7 31 STORIES \u00b7 7 REGIONS",
           font=f_kick, fill=INK)
    right = "SUNDAY 22 NOVEMBER 2026"
    d.text((X1 - d.textlength(right, font=f_kick), 10), right, font=f_kick, fill=RED)

    # masthead
    f_mast = F("serifb", 54)
    title = "SUNDAY 22 NOVEMBER 2026"
    tw = d.textlength(title, font=f_mast)
    d.text(((W - tw) / 2, 28), title, font=f_mast, fill=INK)
    hline(d, X0, X1, 92, fill=RED, width=3)

    # subhead
    f_sub = F("serif", 15)
    sub = ("COP31 deal at dawn \u00b7 Iran hits US bases in Bahrain \u00b7 "
           "Sudan\u2019s Tasis takes Bau \u2014 and 28 more stories")
    tw = d.textlength(sub, font=f_sub)
    d.text(((W - tw) / 2, 98), sub, font=f_sub, fill=INK)

    # numbers strip
    y = 116
    d.rectangle([X0, y, X1, y + 68], outline=INK, width=2)
    cw = (X1 - X0) / 6.0
    f_num = F("serifb", 34)
    f_lab = F("sansb", 10)
    for i, (num, lab) in enumerate(NUMBERS):
        cx = X0 + cw * i
        if i:
            d.line([(cx, y), (cx, y + 68)], fill=INK, width=1)
        nw = d.textlength(num, font=f_num)
        d.text((cx + (cw - nw) / 2, y + 2), num, font=f_num, fill=INK)
        for j, ln in enumerate(lab.split("\n")):
            lw = d.textlength(ln, font=f_lab)
            d.text((cx + (cw - lw) / 2, y + 40 + j * 12), ln, font=f_lab, fill=RED)

    # region bar
    f_reg = F("sansb", 11)
    reg = "  \u00b7  ".join("%s %d" % (name, n) for name, n in REGIONS)
    tw = d.textlength(reg, font=f_reg)
    d.text(((W - tw) / 2, 190), reg, font=f_reg, fill=INK)

    # heroes
    hy, hh = 208, 226
    hw = 325
    scene_fn = {"cop31": scene_cop31, "bahrain": scene_bahrain, "sudan": scene_sudan}
    for i, hro in enumerate(HEROES):
        hx = X0 + i * (hw + 8)
        d.rectangle([hx, hy, hx + hw, hy + hh], outline=INK, width=2)
        d.rectangle([hx, hy, hx + hw, hy + 22], fill=hro["color"])
        f_ban = F("sansb", 15)
        d.text((hx + 10, hy + 3), hro["banner"], font=f_ban, fill=(255, 255, 255))
        f_tag = F("sansb", 10)
        d.text((hx + 10, hy + 26), hro["tag"], font=f_tag, fill=GREY)
        scene_fn[hro["scene"]](d, (hx + 2, hy + 40, hx + hw - 2, hy + 128))
        f_head = F("serifb", 18)
        yy = block(d, hx + 10, hy + 132, hro["headline"], f_head, hw - 20,
                   leading=20, max_lines=1)
        f_body = F("sans", 11)
        yy = block(d, hx + 10, yy + 2, hro["body"], f_body, hw - 20,
                   leading=13, max_lines=4)
        f_src = F("sans", 10)
        d.text((hx + 10, hy + 212), hro["source"], font=f_src, fill=GREY)

    # cards: 4 cols x 3 rows
    cy0, ch, cgap = 442, 96, 4
    cw2 = 247
    for idx, (banner, color, kind, body, source) in enumerate(CARDS):
        r, c = divmod(idx, 4)
        cx = X0 + c * (cw2 + 4)
        cy = cy0 + r * (ch + cgap)
        d.rectangle([cx, cy, cx + cw2, cy + ch], outline=INK, width=1)
        d.rectangle([cx, cy, cx + cw2, cy + 15], fill=color)
        f_cb = F("sansb", 11)
        d.text((cx + 6, cy + 2), banner, font=f_cb, fill=(255, 255, 255))
        mini(d, (cx + 1, cy + 16, cx + cw2 - 1, cy + 46), kind)
        f_ch = F("sansb", 12)
        yy = cy + 48
        headlines = [
            "6.8 quake rattles Peru",
            "Kingpin seized in Sinaloa",
            "Kyiv bridges shut",
            "Two tankers hit in Hormuz",
            "Sparta II burns, crew saved",
            "4.1 quake rattles Myanmar",
            "Smith, Starc out of SA tour",
            "Denmark wants EU visa curbs",
            "Three killed in aid vehicle",
            "Houthis claim 70+ strikes",
            "Arms shipment seized",
            "Two shot dead outside Walmart",
        ]
        d.text((cx + 6, yy), headlines[idx], font=f_ch, fill=INK)
        f_cbody = F("sans", 10)
        block(d, cx + 6, yy + 13, body, f_cbody, cw2 - 12, leading=11, max_lines=2)
        f_csrc = F("sans", 9)
        d.text((cx + 6, cy + ch - 11), source, font=f_csrc, fill=GREY)

    # bottom: map + briefs
    by = 746
    f_sec = F("sansb", 11)
    d.text((X0, by), "WHERE IT HAPPENED", font=f_sec, fill=INK)
    right = "12 STORIES PINNED \u00b7 NUMBERS MATCH THE PAGE"
    d.text((X1 - d.textlength(right, font=f_sec), by), right, font=f_sec, fill=GREY)
    my0, my1 = by + 18, by + 212
    draw_map(d, (X0, my0, 532, my1))
    d.rectangle([X0, my0, 532, my1], outline=INK, width=2)
    bx = 544
    d.text((bx, by + 18), "ALSO TODAY \u2014 16 MORE STORIES, EACH VERIFIED",
           font=f_sec, fill=INK)
    hline(d, bx, X1, by + 36, fill=INK, width=1)
    f_btag = F("sansb", 10)
    f_btxt = F("sans", 10)
    colw = 230
    for i, (tag, txt) in enumerate(BRIEFS):
        col, row = divmod(i, 8)
        x = bx + col * (colw + 8)
        y = by + 42 + row * 24
        d.text((x, y), tag, font=f_btag, fill=RED)
        tx = x + d.textlength(tag + " ", font=f_btag)
        lines = wrap(d, txt, f_btxt, x + colw - tx)
        if len(lines) > 2:
            # reflow: first line stays beside the tag, the rest uses full width
            lines = [lines[0]] + wrap(d, " ".join(lines[1:]), f_btxt, colw)
        # first line sits beside the tag; a second line goes below
        d.text((tx, y), lines[0] if lines else "", font=f_btxt, fill=INK)
        if len(lines) > 1:
            d.text((x, y + 11), lines[1], font=f_btxt, fill=INK)

    # date check
    dy = 982
    d.rectangle([X0, dy, X1, dy + 34], fill=(240, 232, 208), outline=INK, width=1)
    f_dc = F("sansb", 10)
    f_dct = F("sans", 10)
    label = "DATE CHECK \u2014 NOT TODAY:  "
    d.text((X0 + 8, dy + 4), label, font=f_dc, fill=RED)
    lx = X0 + 8 + d.textlength(label, font=f_dc)
    lines = wrap(d, DATE_CHECK, f_dct, X1 - 8 - lx)
    d.text((lx, dy + 4), lines[0], font=f_dct, fill=INK)
    if len(lines) > 1:
        d.text((X0 + 8, dy + 18), " ".join(lines[1:]), font=f_dct, fill=INK)
    return img


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    img = build()
    path = os.path.join(outdir, "entry.png")
    img.save(path, "PNG")
    data = open(path, "rb").read()
    print("wrote %s %d bytes sha256=%s" % (path, len(data), hashlib.sha256(data).hexdigest()))
    print("size %dx%d" % img.size)


if __name__ == "__main__":
    main()
