#!/usr/bin/env python3
"""news-image-20261122 — front page, Sunday 22 November 2026.

Pure-stdlib renderer (os/sys/zlib/struct only). No Pillow, no numpy,
no network, no clock, no randomness. Draws into an RGB bytearray with
its own 5x7 bitmap font and writes a PNG with zlib+struct.

Deterministic: identical input -> byte-identical output.
"""
import os
import struct
import sys
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- font
# 5x7 bitmap font, written from scratch for this page.
# Each glyph: 7 rows of 5 characters, '#' = ink.
FONT = {
    "A": (" ### ", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "B": ("#### ", "#   #", "#   #", "#### ", "#   #", "#   #", "#### "),
    "C": (" ### ", "#   #", "#    ", "#    ", "#    ", "#   #", " ### "),
    "D": ("#### ", "#   #", "#   #", "#   #", "#   #", "#   #", "#### "),
    "E": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"),
    "F": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#    "),
    "G": (" ### ", "#   #", "#    ", "#  ##", "#   #", "#   #", " ### "),
    "H": ("#   #", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "I": (" ### ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "),
    "J": ("  ###", "   # ", "   # ", "   # ", "   # ", "#  # ", " ##  "),
    "K": ("#   #", "#  # ", "# #  ", "##   ", "# #  ", "#  # ", "#   #"),
    "L": ("#    ", "#    ", "#    ", "#    ", "#    ", "#    ", "#####"),
    "M": ("#   #", "## ##", "# # #", "# # #", "#   #", "#   #", "#   #"),
    "N": ("#   #", "##  #", "# # #", "#  ##", "#   #", "#   #", "#   #"),
    "O": (" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "P": ("#### ", "#   #", "#   #", "#### ", "#    ", "#    ", "#    "),
    "Q": (" ### ", "#   #", "#   #", "#   #", "# # #", "#  # ", " ## #"),
    "R": ("#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"),
    "S": (" ####", "#    ", "#    ", " ### ", "    #", "    #", "#### "),
    "T": ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "),
    "U": ("#   #", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "V": ("#   #", "#   #", "#   #", "#   #", "#   #", " # # ", "  #  "),
    "W": ("#   #", "#   #", "#   #", "# # #", "# # #", "## ##", "#   #"),
    "X": ("#   #", "#   #", " # # ", "  #  ", " # # ", "#   #", "#   #"),
    "Y": ("#   #", "#   #", " # # ", "  #  ", "  #  ", "  #  ", "  #  "),
    "Z": ("#####", "    #", "   # ", "  #  ", " #   ", "#    ", "#####"),
    "0": (" ### ", "#   #", "#  ##", "# # #", "##  #", "#   #", " ### "),
    "1": ("  #  ", " ##  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "),
    "2": (" ### ", "#   #", "    #", "  ## ", " #   ", "#    ", "#####"),
    "3": ("#####", "   # ", "  #  ", "   # ", "    #", "#   #", " ### "),
    "4": ("   # ", "  ## ", " # # ", "#  # ", "#####", "   # ", "   # "),
    "5": ("#####", "#    ", "#### ", "    #", "    #", "#   #", " ### "),
    "6": ("  ## ", " #   ", "#    ", "#### ", "#   #", "#   #", " ### "),
    "7": ("#####", "    #", "   # ", "  #  ", " #   ", " #   ", " #   "),
    "8": (" ### ", "#   #", "#   #", " ### ", "#   #", "#   #", " ### "),
    "9": (" ### ", "#   #", "#   #", " ####", "    #", "   # ", " ##  "),
}

FONT.update({
    "a": ("     ", "     ", " ### ", "    #", " ####", "#   #", " ####"),
    "b": ("#    ", "#    ", "#### ", "#   #", "#   #", "#   #", "#### "),
    "c": ("     ", "     ", " ### ", "#    ", "#    ", "#   #", " ### "),
    "d": ("    #", "    #", " ####", "#   #", "#   #", "#   #", " ####"),
    "e": ("     ", "     ", " ### ", "#   #", "#####", "#    ", " ### "),
    "f": ("  ## ", " #  #", " #   ", "#### ", " #   ", " #   ", " #   "),
    "g": ("     ", "     ", " ####", "#   #", "#   #", " ####", "    #"),
    "h": ("#    ", "#    ", "#### ", "#   #", "#   #", "#   #", "#   #"),
    "i": ("  #  ", "     ", " ##  ", "  #  ", "  #  ", "  #  ", " ### "),
    "j": ("   # ", "     ", "  ## ", "   # ", "   # ", "   # ", "   # "),
    "k": ("#    ", "#    ", "#  # ", "# #  ", "##   ", "# #  ", "#  # "),
    "l": (" ##  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "),
    "m": ("     ", "     ", "## # ", "# # #", "# # #", "# # #", "# # #"),
    "n": ("     ", "     ", "#### ", "#   #", "#   #", "#   #", "#   #"),
    "o": ("     ", "     ", " ### ", "#   #", "#   #", "#   #", " ### "),
    "p": ("     ", "     ", "#### ", "#   #", "#   #", "#### ", "#    "),
    "q": ("     ", "     ", " ####", "#   #", "#   #", " ####", "    #"),
    "r": ("     ", "     ", "# ## ", "##  #", "#    ", "#    ", "#    "),
    "s": ("     ", "     ", " ####", "#    ", " ### ", "    #", "#### "),
    "t": (" #   ", " #   ", "#### ", " #   ", " #   ", " #   ", "  ## "),
    "u": ("     ", "     ", "#   #", "#   #", "#   #", "#  ##", " ## #"),
    "v": ("     ", "     ", "#   #", "#   #", "#   #", " # # ", "  #  "),
    "w": ("     ", "     ", "#   #", "# # #", "# # #", "# # #", " # # "),
    "x": ("     ", "     ", "#   #", " # # ", "  #  ", " # # ", "#   #"),
    "y": ("     ", "     ", "#   #", "#   #", "#   #", " ####", "    #"),
    "z": ("     ", "     ", "#####", "   # ", "  #  ", " #   ", "#####"),
    " ": ("     ", "     ", "     ", "     ", "     ", "     ", "     "),
    ".": ("     ", "     ", "     ", "     ", "     ", " ##  ", " ##  "),
    ",": ("     ", "     ", "     ", "     ", " ##  ", "  #  ", " #   "),
    ":": ("     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", "     "),
    ";": ("     ", " ##  ", " ##  ", "     ", " ##  ", "  #  ", " #   "),
    "!": ("  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "     ", "  #  "),
    "?": (" ### ", "#   #", "    #", "  ## ", "  #  ", "     ", "  #  "),
    "'": ("  #  ", "  #  ", " #   ", "     ", "     ", "     ", "     "),
    '"': (" # # ", " # # ", " # # ", "     ", "     ", "     ", "     "),
    "-": ("     ", "     ", "     ", "#####", "     ", "     ", "     "),
    "(": ("   # ", "  #  ", " #   ", " #   ", " #   ", "  #  ", "   # "),
    ")": (" #   ", "  #  ", "   # ", "   # ", "   # ", "  #  ", " #   "),
    "/": ("    #", "   # ", "   # ", "  #  ", " #   ", " #   ", "#    "),
    "%": ("##  #", "## # ", "   # ", "  #  ", " #   ", "# ## ", "#  ##"),
    "$": ("  #  ", " ####", "# #  ", " ### ", "  # #", "#### ", "  #  "),
    "#": (" # # ", " # # ", "#####", " # # ", " # # ", "#####", " # # "),
    "&": (" ##  ", "#  # ", "# #  ", " #   ", "# # #", "#  # ", " ## #"),
    "+": ("     ", "  #  ", "  #  ", "#####", "  #  ", "  #  ", "     "),
    "=": ("     ", "     ", "#####", "     ", "#####", "     ", "     "),
    "*": ("     ", "# # #", " ### ", "#####", " ### ", "# # #", "     "),
    "_": ("     ", "     ", "     ", "     ", "     ", "     ", "#####"),
    "<": ("   # ", "  #  ", " #   ", "#    ", " #   ", "  #  ", "   # "),
    ">": (" #   ", "  #  ", "   # ", "    #", "   # ", "  #  ", " #   "),
    "[": (" ### ", " #   ", " #   ", " #   ", " #   ", " #   ", " ### "),
    "]": (" ### ", "   # ", "   # ", "   # ", "   # ", "   # ", " ### "),
    "@": (" ### ", "#   #", "# ###", "# # #", "# ## ", "#    ", " ### "),
    "|": ("  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "),
    "\\": ("#    ", " #   ", " #   ", "  #  ", "   # ", "   # ", "    #"),
    "{": ("  ## ", " #   ", " #   ", "##   ", " #   ", " #   ", "  ## "),
    "}": ("##   ", "   # ", "   # ", "   ##", "   # ", "   # ", "##   "),
    "~": ("     ", "     ", " # # ", "# # #", "     ", "     ", "     "),
    "^": ("  #  ", " # # ", "#   #", "     ", "     ", "     ", "     "),
    # typographic variants (same 5-wide cell)
    "\u2014": ("     ", "     ", "     ", "#####", "     ", "     ", "     "),
    "\u2013": ("     ", "     ", "     ", "#####", "     ", "     ", "     "),
    "\u00b7": ("     ", "     ", "     ", " ##  ", " ##  ", "     ", "     "),
    "\u2022": ("     ", "     ", " ##  ", " ##  ", " ##  ", "     ", "     "),
    "\u00b0": (" ##  ", "#  # ", "#  # ", " ##  ", "     ", "     ", "     "),
    "\u00d7": ("     ", "#   #", " # # ", "  #  ", " # # ", "#   #", "     "),
})

# Normalise curly quotes / dashes / spaces to the glyphs above.
ALIASES = {
    "\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"',
    "\u00a0": " ", "\u2026": "...",
}


def norm(text):
    return "".join(ALIASES.get(ch, ch) for ch in text)


def text_width(text, scale, gap=None):
    if gap is None:
        gap = scale
    text = norm(text)
    if not text:
        return 0
    return len(text) * (5 * scale + gap) - gap


def wrap_text(text, scale, maxw, gap=None):
    """Greedy word wrap. Returns a list of lines, each fitting maxw."""
    if gap is None:
        gap = scale
    words = norm(text).split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale, gap) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bytes(bg) * (w * h))

    def set_px(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = color[0]
            self.px[i + 1] = color[1]
            self.px[i + 2] = color[2]

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def border(self, x, y, w, h, color, t=1):
        self.fill_rect(x, y, w, t, color)
        self.fill_rect(x, y + h - t, w, t, color)
        self.fill_rect(x, y, t, h, color)
        self.fill_rect(x + w - t, y, t, h, color)

    def hline(self, x, y, w, color):
        self.fill_rect(x, y, w, 1, color)

    def vline(self, x, y, h, color):
        self.fill_rect(x, y, 1, h, color)

    def line(self, x0, y0, x1, y1, color):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set_px(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.hline(cx - dx, cy + dy, 2 * dx + 1, color)

    def ring(self, cx, cy, r, color, t=1):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            for k in range(t):
                self.set_px(cx - dx + k, cy + dy, color)
                self.set_px(cx + dx - k, cy + dy, color)

    def ellipse(self, cx, cy, rx, ry, color):
        for dy in range(-ry, ry + 1):
            dx = int(rx * (1.0 - (dy * dy) / float(ry * ry)) ** 0.5)
            self.hline(cx - dx, cy + dy, 2 * dx + 1, color)

    def poly(self, pts, color):
        """Scanline fill of a polygon given as [(x, y), ...]."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    x = x0 + (y - y0) * (x1 - x0) / float(y1 - y0)
                    xs.append(x)
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                xa = int(xs[k] + 0.5)
                xb = int(xs[k + 1] + 0.5)
                if xb >= xa:
                    self.hline(xa, y, xb - xa + 1, color)

    def triangle(self, x0, y0, x1, y1, x2, y2, color):
        self.poly([(x0, y0), (x1, y1), (x2, y2)], color)

    # -- text -------------------------------------------------------------
    def glyph(self, x, y, ch, scale, color, bold=False):
        rows = FONT.get(ch)
        if rows is None:
            return
        for r, row in enumerate(rows):
            for c in range(5):
                if row[c] == "#":
                    px = x + c * scale
                    py = y + r * scale
                    self.fill_rect(px, py, scale, scale, color)
                    if bold:
                        self.fill_rect(px + 1, py, scale, scale, color)

    def text(self, x, y, s, scale, color, bold=False, gap=None, align="left"):
        if gap is None:
            gap = scale
        s = norm(s)
        w = text_width(s, scale, gap)
        if align == "center":
            x = x - w // 2
        elif align == "right":
            x = x - w
        cx = x
        for ch in s:
            self.glyph(cx, y, ch, scale, color, bold=bold)
            cx += 5 * scale + gap
        return w

    def text_block(self, x, y, lines, scale, color, lh=None, bold=False,
                   gap=None):
        if lh is None:
            lh = 7 * scale + 2
        for line in lines:
            self.text(x, y, line, scale, color, bold=bold, gap=gap)
            y += lh
        return y


# ---------------------------------------------------------------- png
def png_bytes(cv):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]

    def chunk(typ, data):
        out = struct.pack(">I", len(data)) + typ + data
        out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


# ---------------------------------------------------------------- colors
PAPER = (247, 243, 232)
INK = (26, 26, 26)
RED = (178, 34, 42)
DARKRED = (148, 24, 32)
NAVY = (31, 42, 92)
SKY = (96, 138, 196)
ORANGE = (182, 92, 26)
TEAL = (0, 118, 110)
PURPLE = (108, 58, 138)
BROWN = (138, 90, 38)
GOLD = (214, 164, 42)
CREAM = (232, 220, 192)
LAND = CREAM
MAPBG = (22, 33, 62)
MAPGRID = (58, 74, 110)
GREY = (120, 118, 110)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


# ---------------------------------------------------------------- scenes
def scene_cop31(cv, x, y, w, h):
    """Antalya at dawn: orange sky, sun, purple hills, hall, flags."""
    # sky bands
    for i in range(5):
        cv.fill_rect(x, y + i * h // 5, w, h // 5 + 1,
                     [(250, 190, 90), (244, 160, 70), (232, 130, 70),
                      (205, 105, 80), (150, 80, 110)][i])
    cv.disc(x + int(w * 0.62), y + int(h * 0.42), 16, (255, 226, 140))
    cv.disc(x + int(w * 0.62), y + int(h * 0.42), 11, (255, 240, 180))
    # hills
    cv.triangle(x, y + h, x + int(w * 0.30), y + int(h * 0.45),
                x + int(w * 0.55), y + h, (88, 52, 110))
    cv.triangle(x + int(w * 0.45), y + h, x + int(w * 0.75), y + int(h * 0.38),
                x + w, y + h, (64, 40, 92))
    # hall: cream block + red roof + columns
    hx, hy = x + 14, y + int(h * 0.52)
    hw, hh = int(w * 0.52), int(h * 0.44)
    cv.fill_rect(hx, hy, hw, hh, (238, 226, 196))
    cv.triangle(hx - 4, hy, hx + hw // 2, hy - 12, hx + hw + 4, hy, RED)
    for k in range(5):
        cx = hx + 8 + k * (hw - 16) // 4
        cv.fill_rect(cx, hy + 4, 4, hh - 4, (120, 90, 50))
    cv.fill_rect(hx, hy + hh - 3, hw, 3, (120, 90, 50))
    # flags
    for k, col in enumerate((RED, (0, 110, 70), NAVY, GOLD)):
        fx = x + int(w * 0.72) + k * 14
        cv.vline(fx, y + int(h * 0.30), int(h * 0.42), INK)
        cv.triangle(fx, y + int(h * 0.30), fx + 11, y + int(h * 0.36),
                    fx, y + int(h * 0.42), col)


def scene_bahrain(cv, x, y, w, h):
    """Night Gulf: dark sky, stars, moon, radar dishes, missile trails."""
    cv.fill_rect(x, y, w, h, (16, 22, 52))
    for sx, sy in ((12, 8), (40, 18), (80, 6), (120, 14), (160, 8),
                   (200, 20), (240, 10), (280, 16), (60, 26), (180, 28)):
        if sx < w:
            cv.set_px(x + sx, y + sy, WHITE)
    cv.disc(x + int(w * 0.82), y + 16, 10, (235, 232, 210))
    cv.disc(x + int(w * 0.82) + 4, y + 13, 9, (16, 22, 52))
    # ground
    cv.fill_rect(x, y + int(h * 0.72), w, h - int(h * 0.72), (24, 28, 44))
    # radar dishes: mast + dish arc
    for dx in (int(w * 0.18), int(w * 0.55)):
        cv.vline(x + dx, y + int(h * 0.42), int(h * 0.32), GREY)
        cv.disc(x + dx, y + int(h * 0.40), 9, (150, 150, 150))
        cv.disc(x + dx - 2, y + int(h * 0.40) - 2, 8, (16, 22, 52))
    # missile trails (bright diagonal streaks)
    for tx, ty in ((int(w * 0.30), int(h * 0.18)), (int(w * 0.62), int(h * 0.10))):
        cv.line(x + tx, y + ty, x + tx + 46, y + ty + 22, (255, 210, 90))
        cv.line(x + tx, y + ty + 2, x + tx + 40, y + ty + 22, (255, 170, 60))
        cv.disc(x + tx, y + ty, 3, (255, 240, 160))
    # smoke puffs
    for sx, sy, r in ((int(w * 0.38), int(h * 0.55), 9),
                      (int(w * 0.46), int(h * 0.50), 11),
                      (int(w * 0.72), int(h * 0.58), 8)):
        cv.disc(x + sx, y + sy, r, (90, 90, 96))
        cv.disc(x + sx - 3, y + sy - 3, r - 4, (120, 120, 126))


def scene_sudan(cv, x, y, w, h):
    """Blue Nile town: hazy sky, brown hills, flat-roof town, river."""
    for i in range(4):
        cv.fill_rect(x, y + i * h // 4, w, h // 4 + 1,
                     [(238, 214, 160), (230, 196, 140),
                      (216, 176, 120), (196, 156, 104)][i])
    cv.disc(x + int(w * 0.80), y + 14, 11, (255, 232, 170))
    cv.triangle(x, y + int(h * 0.62), x + int(w * 0.30), y + int(h * 0.34),
                x + int(w * 0.55), y + int(h * 0.62), (150, 108, 66))
    cv.triangle(x + int(w * 0.48), y + int(h * 0.62),
                x + int(w * 0.78), y + int(h * 0.28),
                x + w, y + int(h * 0.62), (132, 94, 58))
    # town: flat-roof blocks with red trim
    for bx, bw, bh in ((8, 44, 26), (58, 38, 34), (102, 46, 24),
                       (154, 40, 30), (200, 44, 22), (250, 40, 28)):
        if bx + bw > w:
            break
        by = y + int(h * 0.62) - bh
        cv.fill_rect(x + bx, by, bw, bh, (244, 234, 210))
        cv.fill_rect(x + bx, by, bw, 3, RED)
        cv.fill_rect(x + bx + 6, by + 8, 6, 8, (90, 70, 50))
        cv.fill_rect(x + bx + bw - 14, by + 8, 6, 8, (90, 70, 50))
    # river
    cv.fill_rect(x, y + int(h * 0.82), w, h - int(h * 0.82), (70, 130, 180))
    cv.hline(x + 20, y + int(h * 0.88), 60, (160, 205, 235))
    cv.hline(x + 150, y + int(h * 0.92), 80, (160, 205, 235))


CARD_SCENES = {
    "quake": (SKY, "crack"),
    "kingpin": (GOLD, "hills"),
    "bridges": (NAVY, "arcs"),
    "tankers": (TEAL, "ship"),
    "sparta": (NAVY, "shipfire"),
    "myanmar": (ORANGE, "crack"),
    "cricket": (TEAL, "ball"),
    "visas": (PURPLE, "stamp"),
    "gaza": (RED, "truck"),
    "yemen": (ORANGE, "burst"),
    "syria": (BROWN, "truck"),
    "canada": (NAVY, "store"),
}


def scene_card(cv, x, y, w, h, kind):
    bg, motif = CARD_SCENES[kind]
    cv.fill_rect(x, y, w, h, bg)
    cv.fill_rect(x, y + h - 6, w, 6, (0, 0, 0))
    if motif == "crack":
        cv.line(x + 8, y + 4, x + w // 3, y + h - 10, (255, 80, 60))
        cv.line(x + w // 3, y + h - 10, x + 2 * w // 3, y + 6, (255, 80, 60))
        cv.line(x + 2 * w // 3, y + 6, x + w - 10, y + h - 12, (255, 80, 60))
        cv.triangle(x + int(w * 0.72), y + h - 6, x + int(w * 0.80),
                    y + 4, x + int(w * 0.88), y + h - 6, (200, 170, 110))
    elif motif == "hills":
        cv.triangle(x, y + h, x + int(w * 0.30), y + 4,
                    x + int(w * 0.55), y + h, (150, 100, 40))
        cv.triangle(x + int(w * 0.45), y + h, x + int(w * 0.72), y + 8,
                    x + w, y + h, (120, 80, 30))
        cv.disc(x + int(w * 0.85), y + 8, 6, (255, 240, 180))
    elif motif == "arcs":
        # bridge arches: rings first, river covers their lower halves
        for ax in (int(w * 0.22), int(w * 0.50), int(w * 0.78)):
            cv.ring(x + ax, y + int(h * 0.62), 13, WHITE, 2)
        cv.fill_rect(x, y + int(h * 0.62) + 1, w,
                     h - int(h * 0.62) - 1, (70, 130, 180))
        cv.hline(x, y + int(h * 0.62), w, WHITE)
    elif motif in ("ship", "shipfire"):
        # hull + containers + smoke
        cv.poly([(x + 12, y + h - 14), (x + w - 12, y + h - 14),
                 (x + w - 26, y + h - 4), (x + 26, y + h - 4)], (40, 40, 44))
        cv.fill_rect(x + int(w * 0.30), y + 4, 16, 8, RED)
        cv.fill_rect(x + int(w * 0.48), y + 4, 16, 8, GOLD)
        cv.fill_rect(x + int(w * 0.66), y + 4, 16, 8, WHITE)
        if motif == "shipfire":
            cv.disc(x + int(w * 0.55), y + 6, 5, (255, 120, 30))
            cv.disc(x + int(w * 0.60), y + 3, 4, (255, 200, 60))
    elif motif == "ball":
        cv.fill_rect(x, y + int(h * 0.55), w, h - int(h * 0.55), (60, 140, 70))
        cv.disc(x + int(w * 0.70), y + 8, 6, RED)
        cv.line(x + 10, y + h - 8, x + int(w * 0.45), y + 6, (220, 200, 150))
    elif motif == "stamp":
        cv.border(x + int(w * 0.55), y + 3, 62, 14, WHITE, 2)
        cv.text(x + int(w * 0.55) + 31, y + 6, "DENIED", 1, WHITE, bold=True,
                align="center")
        cv.line(x + 8, y + h - 8, x + int(w * 0.40), y + 5, GOLD)
    elif motif == "truck":
        cv.fill_rect(x + 12, y + 6, 34, 10, WHITE)
        cv.fill_rect(x + 46, y + 9, 12, 7, WHITE)
        cv.disc(x + 20, y + h - 5, 3, BLACK)
        cv.disc(x + 50, y + h - 5, 3, BLACK)
        cv.fill_rect(x + 16, y + 8, 8, 6, RED)
    elif motif == "burst":
        for bx, by in ((int(w * 0.25), 8), (int(w * 0.60), 6), (int(w * 0.85), 10)):
            for k in range(6):
                ang = k * 3.14159 / 3.0
                cv.line(x + bx, y + by, x + bx + int(9 * (1 if k % 2 == 0 else -1) * 0.7),
                        y + by + int(7 * (1 if k < 3 else -1)), (255, 210, 90))
            cv.disc(x + bx, y + by, 3, (255, 150, 40))
    elif motif == "store":
        cv.fill_rect(x + 10, y + 4, w - 20, 10, (200, 60, 60))
        cv.fill_rect(x + 14, y + 14, w - 28, 6, WHITE)
        for k in range(4):
            cv.fill_rect(x + 16 + k * 22, y + 6, 14, 3, (255, 220, 80))


# ---------------------------------------------------------------- world map
# Rough continent outlines in (lon, lat). Equirectangular projection.
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 71), (-110, 68), (-95, 69), (-85, 66),
     (-80, 73), (-70, 62), (-65, 60), (-55, 52), (-60, 47), (-70, 42),
     (-75, 35), (-80, 32), (-81, 26), (-84, 30), (-90, 21), (-95, 19),
     (-97, 16), (-92, 15), (-86, 13), (-83, 9), (-79, 9), (-83, 15),
     (-90, 14), (-97, 16), (-105, 20), (-110, 23), (-114, 28), (-120, 34),
     (-125, 40), (-124, 48), (-130, 55), (-145, 60), (-155, 58),
     (-165, 60), (-168, 66)],
    # Greenland
    [(-45, 60), (-40, 64), (-32, 68), (-25, 70), (-20, 74), (-25, 78),
     (-35, 80), (-50, 78), (-55, 75), (-58, 70), (-55, 64), (-50, 60),
     (-45, 60)],
    # South America
    [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12), (-72, -18),
     (-70, -23), (-70, -30), (-72, -37), (-73, -44), (-74, -50),
     (-70, -54), (-66, -55), (-68, -50), (-65, -45), (-62, -40),
     (-58, -34), (-52, -32), (-48, -28), (-41, -23), (-35, -9),
     (-35, -6), (-40, -3), (-44, -2), (-50, 0), (-53, 4), (-60, 8),
     (-68, 11), (-75, 11), (-79, 9)],
    # Africa
    [(-17, 15), (-17, 21), (-15, 27), (-10, 31), (-5, 35), (0, 36),
     (10, 37), (11, 34), (20, 32), (30, 31), (32, 31), (34, 28), (35, 23),
     (37, 18), (39, 15), (43, 12), (48, 11), (51, 12), (46, 5), (42, 0),
     (40, -5), (40, -10), (36, -18), (33, -26), (28, -33), (20, -35),
     (17, -32), (15, -27), (12, -18), (13, -12), (12, -6), (9, -1),
     (9, 4), (-8, 4), (-13, 8), (-17, 12), (-17, 15)],
    # Eurasia
    [(-10, 36), (-9, 43), (-2, 44), (0, 46), (-4, 48), (-1, 49), (3, 51),
     (5, 53), (8, 55), (8, 57), (10, 59), (5, 60), (5, 62), (10, 64),
     (12, 66), (18, 69), (25, 71), (30, 70), (35, 68), (40, 68),
     (45, 68), (50, 69), (55, 68), (60, 69), (65, 69), (70, 72),
     (75, 72), (80, 73), (85, 74), (90, 75), (95, 76), (100, 77),
     (105, 77), (110, 74), (115, 73), (120, 73), (125, 72), (130, 72),
     (135, 72), (140, 72), (145, 72), (150, 70), (155, 69), (160, 69),
     (165, 66), (170, 66), (178, 65), (178, 62), (170, 60), (162, 60),
     (158, 56), (156, 52), (150, 59), (142, 59), (140, 53), (140, 47),
     (138, 43), (135, 43), (130, 42), (127, 40), (126, 38), (122, 39),
     (120, 35), (122, 32), (120, 28), (118, 25), (112, 22), (108, 18),
     (105, 10), (103, 8), (100, 8), (98, 10), (94, 17), (92, 21),
     (90, 22), (88, 22), (86, 20), (83, 18), (80, 15), (80, 13),
     (77, 8), (75, 12), (73, 16), (70, 20), (66, 25), (62, 25),
     (58, 25), (56, 26), (54, 26), (52, 25), (50, 29), (48, 30),
     (50, 26), (54, 24), (57, 22), (58, 20), (55, 17), (52, 15),
     (48, 14), (44, 13), (43, 12), (40, 15), (39, 20), (38, 22),
     (36, 28), (35, 30), (34, 31), (33, 31), (30, 36), (27, 37),
     (23, 36), (20, 40), (19, 42), (16, 44), (14, 45), (12, 44),
     (10, 44), (8, 44), (6, 43), (3, 43), (0, 40), (-2, 37), (-6, 36),
     (-9, 37), (-10, 36)],
    # Australia
    [(113, -22), (114, -30), (115, -34), (118, -35), (124, -33),
     (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
     (145, -38), (150, -37), (153, -32), (153, -27), (150, -23),
     (146, -19), (142, -15), (142, -11), (137, -12), (135, -15),
     (132, -12), (130, -13), (126, -14), (122, -17), (118, -20),
     (113, -22)],
    # UK
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51),
     (-5, 50)],
    # Japan
    [(130, 31), (132, 33), (134, 34), (137, 35), (139, 36), (140, 38),
     (141, 40), (141, 42), (143, 42), (145, 44), (142, 44), (140, 42),
     (139, 38), (137, 37), (135, 34), (132, 33), (130, 31)],
    # Indonesia
    [(95, 5), (98, 8), (100, 7), (102, 2), (104, -2), (106, -6),
     (110, -7), (114, -8), (119, -9), (122, -10), (120, -11),
     (115, -10), (110, -8), (105, -5), (102, 0), (98, 3), (95, 5)],
    # New Guinea
    [(131, -1), (136, -2), (141, -3), (146, -6), (150, -9), (147, -9),
     (143, -8), (138, -8), (134, -4), (131, -1)],
]

# (lon, lat, pin number) — 12 stories pinned
PINS = [
    (10, 56, 1),    # Denmark
    (32, 49, 2),    # Ukraine
    (34, 31, 3),    # Gaza
    (-76, -10, 4),  # Peru
    (-102, 23, 5),  # Mexico
    (50, 26, 6),    # Bahrain
    (96, 20, 7),    # Myanmar
    (25, 62, 8),    # Finland
    (45, 15, 9),    # Yemen
    (134, -25, 10),  # Australia
    (-106, 56, 11),  # Canada
    (30, 13, 12),   # Sudan
]


# ---------------------------------------------------------------- content
NUMBERS = [
    ("14", "DAY 14", "OF COP31"),
    ("196", "NATIONS", "AT THE TABLE"),
    ("400", "DRONES", "OVER UKRAINE"),
    ("6.8", "PERU", "QUAKE"),
    ("3", "KYIV BRIDGES", "HIT"),
    ("$5M", "REWARD FOR", "CHAPO ISIDRO"),
]

REGIONS = "MIDDLE EAST 9 \u00b7 EUROPE 8 \u00b7 AFRICA 6 \u00b7 ASIA 3 \u00b7 AMERICAS 3 \u00b7 OCEANIA 1 \u00b7 GLOBAL 1"

HEROES = [
    dict(banner="COP31: DEAL AT DAWN", color=RED, tag="CLIMATE \u00b7 ANTALYA",
         scene="cop31", headline="Deal at dawn in Antalya",
         body="A new package lands overnight; president Murat Kurum calls it a text \"all the parties can agree upon\". Objections due 03:00 GMT; approval vote 06:00 GMT \u2014 13:00 WIB. First draft to admit warming will pass 1.5\u00b0C.",
         source="Reuters"),
    dict(banner="BAHRAIN: MISSILES", color=NAVY, tag="GULF \u00b7 SATURDAY NIGHT",
         scene="bahrain", headline="Iran strikes Bahrain bases",
         body="The Revolutionary Guard says it hit two US Patriot radars at al-Riffa and Awali Sakhir in a missile-and-drone attack. Bahrain says a civilian site burned; no one was hurt. The US denies its F-16 claim.",
         source="Xinhua / Bahrain"),
    dict(banner="SUDAN: BAU FALLS", color=ORANGE, tag="WAR \u00b7 BLUE NILE",
         scene="sudan", headline="Tasis alliance seizes Bau",
         body="The RSF-led alliance claims the strategic Blue Nile district after fierce battles. The UN Security Council warns the humanitarian crisis is worsening as the war spreads.",
         source="Tasis / UN"),
]

CARDS = [
    ("PERU: QUAKE", RED, "6.8 quake rattles Peru",
     "A 6.8 quake shook Junin; Lima fled to the streets. No major damage reported.",
     "Reuters", "quake"),
    ("MEXICO: KINGPIN CAUGHT", NAVY, "Kingpin seized in Sinaloa",
     "FBI-most-wanted 'Chapo Isidro' seized in Guasave; 11 die in the raid.",
     "Reuters / AP", "kingpin"),
    ("UKRAINE: BRIDGES HIT", NAVY, "Kyiv bridges shut",
     "400 drones and 110 missiles; three Kyiv bridges shut, nine killed.",
     "BBC", "bridges"),
    ("HORMUZ: TANKERS HIT", TEAL, "Two tankers hit in Hormuz",
     "TORKEL and ARINA struck near Khasab; TORKEL burns at anchor.",
     "UKMTO", "tankers"),
    ("FINLAND: SPARTA II", NAVY, "Sparta II burns, crew saved",
     "Russian cargo ship hit by drones off Finland; 16 crew saved.",
     "Border Guard", "sparta"),
    ("MYANMAR: QUAKE", ORANGE, "4.1 quake rattles Myanmar",
     "A 4.1 tremor rattles the country early on Sunday.",
     "ANI / NCS", "myanmar"),
    ("CRICKET: OUT", TEAL, "Smith, Starc out of SA tour",
     "Smith (wrist) and Starc (groin) out of the SA tour; Marsh to lead.",
     "Cricbuzz", "cricket"),
    ("DENMARK: VISAS", PURPLE, "Denmark wants EU visa curbs",
     "Denmark urges EU visa curbs after police foil a plot to kill a US-Ukrainian rapper.",
     "reports", "visas"),
    ("GAZA: AID HIT", RED, "Three killed in aid vehicle",
     "An Israeli strike kills three in an aid vehicle, witnesses say.",
     "witnesses", "gaza"),
    ("YEMEN: STRIKES", ORANGE, "Houthis claim 70+ strikes",
     "Houthis claim 70+ Saudi strikes on eight areas; the claim is theirs alone.",
     "Houthis", "yemen"),
    ("SYRIA: SEIZED", BROWN, "Arms shipment seized",
     "Damascus says it seized an arms shipment bound for Lebanon.",
     "Syria", "syria"),
    ("CANADA: SHOT DEAD", RED, "Two shot dead outside Walmart",
     "Two Indian-origin men shot dead outside a Walmart; police call it targeted.",
     "police", "canada"),
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
    ("FOOTBALL", "Leeds stun Chelsea 4\u20131; Newcastle hold Arsenal 2\u20132."),
    ("GULF", "14 Iranian tankers mass off Kharg to test the US blockade."),
    ("UAE", "President meets the US homeland security chief."),
    ("GAZA", "Children watch 'Alice in Wonderland' in Gaza."),
    ("POLAND", "Russian projectile crossed into Poland; NATO defences activated."),
    ("SUDAN", "RSF killed civilians, three of them children, in West Kordofan."),
    ("TIGRAY", "New mayor vows elections within six months."),
]

DATE_CHECK = ("DATE CHECK \u2014 NOT TODAY: Killer-robot talks ended Sat 04:45 "
              "\u00b7 Norway oil ruling \u2014 13 Nov \u00b7 Kenya's last Ebola "
              "patient \u2014 11 Nov \u00b7 US midterms called \u2014 3\u201317 Nov "
              "\u00b7 Jensen Huang resignation \u2014 12 Nov \u00b7 Ghana "
              "banknotes \u2014 12 Nov \u00b7 Estonia border closure \u2014 20 Nov")

SUBLINE = ("COP31 deal at dawn \u00b7 Iran hits US bases in Bahrain \u00b7 "
           "Sudan's Tasis takes Bau \u2014 and 28 more stories")


# ---------------------------------------------------------------- layout
def draw_brief(cv, x, y, keyword, text, width):
    """One brief: red bold keyword + ink text, wrapped to width."""
    first = keyword + " " + text
    lines = wrap_text(first, 1, width)
    # re-split so the keyword stays on line 1 even if wrap moved it
    cv.text(x, y, keyword, 1, RED, bold=True)
    kw = text_width(keyword + " ", 1)
    rest = wrap_text(text, 1, width - kw)
    yy = y
    cv.text(x + kw, yy, rest[0] if rest else "", 1, INK)
    yy += 9
    for line in rest[1:]:
        cv.text(x, yy, line, 1, INK)
        yy += 9
    return yy


def render():
    cv = Canvas(W, H, PAPER)
    # frame
    cv.border(4, 4, W - 8, H - 8, INK, 2)

    # top strip
    cv.text(10, 9, "ONE DAY \u00b7 ONE PAGE \u00b7 31 STORIES \u00b7 7 REGIONS",
            1, INK, bold=True)
    cv.text(1014, 9, "SUNDAY 22 NOVEMBER 2026", 1, RED, bold=True,
            align="right")

    # masthead
    cv.text(512, 24, "SUNDAY 22 NOVEMBER 2026", 7, INK, bold=True,
            gap=5, align="center")
    cv.fill_rect(10, 76, 1004, 3, RED)
    cv.text(512, 84, SUBLINE, 1, INK, bold=True, align="center")

    # numbers strip
    cv.border(10, 96, 1004, 60, INK, 2)
    bounds = [10, 177, 345, 512, 680, 847, 1014]
    for i, (num, lab1, lab2) in enumerate(NUMBERS):
        cx = (bounds[i] + bounds[i + 1]) // 2
        if i:
            cv.vline(bounds[i], 96, 60, INK)
        cv.text(cx, 100, num, 5, INK, bold=True, align="center")
        cv.text(cx, 139, lab1, 1, RED, bold=True, align="center")
        cv.text(cx, 148, lab2, 1, RED, bold=True, align="center")

    # region strip
    cv.text(512, 161, REGIONS, 1, INK, bold=True, align="center")

    # heroes
    hero_y = 172
    hero_xs = [10, 348, 686]
    hero_w = 328
    body_lines = []
    for hero in HEROES:
        body_lines.append(wrap_text(hero["body"], 2, hero_w - 16))
    max_body = max(len(lines) for lines in body_lines)
    hero_h = 24 + 12 + 72 + 4 + 16 + 4 + max_body * 15 + 16
    for xi, hero in zip(hero_xs, HEROES):
        cv.fill_rect(xi, hero_y, hero_w, 24, hero["color"])
        cv.text(xi + 8, hero_y + 5, hero["banner"], 2, WHITE, bold=True)
        cv.text(xi + 8, hero_y + 28, hero["tag"], 1, (100, 98, 92),
                bold=True)
        scene = {"cop31": scene_cop31, "bahrain": scene_bahrain,
                 "sudan": scene_sudan}[hero["scene"]]
        scene(cv, xi, hero_y + 40, hero_w, 72)
        cv.text(xi + 8, hero_y + 116, hero["headline"], 2, INK, bold=True)
        y = hero_y + 134
        for line in wrap_text(hero["body"], 2, hero_w - 16):
            cv.text(xi + 8, y, line, 2, INK)
            y += 15
        cv.text(xi + 8, hero_y + hero_h - 12, "\u2014 " + hero["source"],
                1, GREY)

    # cards: 4 rows x 3 cols
    cards_y = hero_y + hero_h + 8
    card_h, card_gap = 78, 6
    for row in range(4):
        for col in range(3):
            banner, color, headline, body, source, kind = CARDS[row * 3 + col]
            cx0 = hero_xs[col]
            cy0 = cards_y + row * (card_h + card_gap)
            cv.border(cx0, cy0, hero_w, card_h, INK, 1)
            cv.fill_rect(cx0 + 1, cy0 + 1, hero_w - 2, 15, color)
            cv.text(cx0 + 6, cy0 + 5, banner, 1, WHITE, bold=True)
            scene_card(cv, cx0 + 1, cy0 + 16, hero_w - 2, 18, kind)
            cv.text(cx0 + 6, cy0 + 36, headline, 2, INK, bold=True, gap=1)
            y = cy0 + 52
            for line in wrap_text(body, 1, hero_w - 12)[:2]:
                cv.text(cx0 + 6, y, line, 1, INK)
                y += 9
            cv.text(cx0 + 6, cy0 + card_h - 9, "\u2014 " + source, 1, GREY)

    # map + briefs
    map_y = cards_y + 4 * card_h + 3 * card_gap + 8
    date_y = H - 36
    map_h = date_y - map_y - 26
    cv.text(10, map_y, "WHERE IT HAPPENED", 2, INK, bold=True)
    cv.text(510, map_y, "ALSO TODAY \u2014 16 MORE STORIES, EACH VERIFIED",
            1, INK, bold=True)
    cv.text(1014, map_y + 9,
            "12 STORIES PINNED \u00b7 NUMBERS MATCH THE PAGE", 1, INK,
            bold=True, align="right")
    my = map_y + 20
    cv.fill_rect(10, my, 490, map_h, MAPBG)
    # grid
    gx = 10
    while gx <= 500:
        cv.vline(gx, my, map_h, MAPGRID)
        gx += 41
    gy = my
    while gy <= my + map_h:
        cv.hline(10, gy, 490, MAPGRID)
        gy += 34
    # continents
    for poly in CONTINENTS:
        pts = [(10 + int((lon + 180) / 360.0 * 490),
                my + int((80 - lat) / 138.0 * map_h)) for lon, lat in poly]
        cv.poly(pts, LAND)
    # ocean labels
    cv.text(30, my + map_h - 22, "PACIFIC", 1, (140, 165, 210), bold=True)
    cv.text(185, my + map_h - 22, "ATLANTIC", 1, (140, 165, 210), bold=True)
    cv.text(330, my + map_h - 14, "INDIAN", 1, (140, 165, 210), bold=True)
    # pins (small offsets keep the Gulf/Europe cluster readable)
    offsets = {1: (-12, -6), 2: (8, 6), 3: (-10, 2), 6: (8, -6),
               8: (12, -8), 9: (2, 8), 12: (-6, 2)}
    for lon, lat, num in PINS:
        px = 10 + int((lon + 180) / 360.0 * 490)
        py = my + int((80 - lat) / 138.0 * map_h)
        dx, dy = offsets.get(num, (0, 0))
        px += dx
        py += dy
        cv.disc(px, py, 9, RED)
        cv.ring(px, py, 9, WHITE, 1)
        cv.text(px, py - 3, str(num), 1, WHITE, bold=True, align="center")

    # briefs, two columns x eight rows
    by = my
    for col in range(2):
        bx = 510 + col * 257
        yy = by
        for k in range(8):
            keyword, text = BRIEFS[col * 8 + k]
            yy = draw_brief(cv, bx, yy, keyword, text, 247)
            yy += 2
    # date check: red bold prefix, then ink text
    cv.border(10, date_y, 1004, 28, RED, 2)
    prefix = "DATE CHECK \u2014 NOT TODAY: "
    lines = wrap_text(DATE_CHECK, 1, 1004 - 20)
    yy = date_y + 5
    for li, line in enumerate(lines[:2]):
        if li == 0:
            cv.text(20, yy, prefix, 1, RED, bold=True)
            cv.text(20 + text_width(prefix, 1), yy,
                    line[len(prefix):], 1, INK)
        else:
            cv.text(20, yy, line, 1, INK)
        yy += 9
    return cv


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    cv = render()
    data = png_bytes(cv)
    with open(os.path.join(outdir, "entry.png"), "wb") as f:
        f.write(data)
    return 0


if __name__ == "__main__":
    sys.exit(main())
