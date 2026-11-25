#!/usr/bin/env python3
"""The World - 25 November 2026.

Draws a 1024x1024 newspaper front page summing up the world news of
Wednesday 25 November 2026, using only the Python 3.13 standard library:
its own PNG encoder, its own 5x7 bitmap font, and all artwork drawn
programmatically with shapes. No network, no external fonts or images.
Fully deterministic: two runs write byte-identical files.

Stories (freshest of the 25 November news cycle, first reported late
24 Nov / overnight into 25 Nov across time zones; the 25 Nov UTC day
had barely begun at build time, 01:19 UTC):
  1. HERO - Hormuz: Iran says a fourth oil tanker hit a naval mine and
     caught fire in the Strait of Hormuz, the fourth in two days, under
     US escort. Sources: IRGC Navy via IRNA/Tasnim, Reuters, UKMTO.
  2. Ukraine: Zelenskiy confirms Ukraine sank a Russian warship and hit
     a cargo vessel off Libya; Kyiv's strikes now reach beyond Europe.
     Source: Reuters.
  3. Iraq: Baghdad orders the federal takeover of Kurdish oilfields and
     all border crossings; the Kurdistan government rejects it.
     Sources: INA, Financial Times.
  4. Senegal: CAS reinstates Senegal as 2025 Africa Cup of Nations
     champions; Morocco vows to appeal. Source: Reuters.
  5. Colombia: car bomb in Villavicencio wounds 23 on the eve of the
     10th anniversary of the FARC peace deal; president blames FARC
     dissidents. Source: AP.
  6. France: Nicolas Sarkozy and Carla Bruni ordered to stand trial in
     the Libya corruption case; pre-trial hearing 1 April 2027.
     Source: Reuters.
"""

import binascii
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- font
# 5x7 bitmap font, uppercase + digits + punctuation only. Each glyph is
# seven rows of five cells, '#' = ink, '.' = empty.
FONT = {
    "A": ("..#..", ".#.#.", "#...#", "#...#", "#####", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#..##", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "####.", "#...#", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "/": ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.#.#", "#..##"),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "#": (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    "@": (".###.", "#...#", "#.###", "#.#.#", "#.###", "#....", ".###."),
    "*": (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    "_": (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    "[": (".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."),
    "]": (".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###."),
}

CHAR_ADV = 6  # glyph width 5 + 1 spacing, in font units


def text_width(text, scale):
    return (len(text) * CHAR_ADV - 1) * scale


def wrap_text(text, scale, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = text.split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
def _lerp(a, b, t):
    return min(255, max(0, int(a + (b - a) * t)))


def mix(c1, c2, t):
    return (_lerp(c1[0], c2[0], t), _lerp(c1[1], c2[1], t), _lerp(c1[2], c2[2], t))


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.buf = bytearray(w * h * 3)
        self.rect(0, 0, w, h, bg)

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i], self.buf[i + 1], self.buf[i + 2] = c

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                self.buf[i], self.buf[i + 1], self.buf[i + 2] = c
                i += 3

    def vgrad(self, x, y, w, h, top, bottom):
        for yy in range(h):
            t = yy / max(1, h - 1)
            self.rect(x, y + yy, w, 1, mix(top, bottom, t))

    def hgrad(self, x, y, w, h, left, right):
        for xx in range(w):
            t = xx / max(1, w - 1)
            self.rect(x + xx, y, 1, h, mix(left, right, t))

    def circle(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for dy in range(-ry, ry + 1):
            t = 1.0 - (dy * dy) / float(ry * ry)
            dx = int(rx * (t ** 0.5)) if t > 0 else 0
            self.rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)

    def line(self, x0, y0, x1, y1, c, thick=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.rect(x0 - thick // 2, y0 - thick // 2, thick, thick, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def poly(self, pts, c):
        """Even-odd scanline fill for a simple polygon."""
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
                    t = (y - y0) / float(y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                self.rect(int(xs[j]), y, int(xs[j + 1]) - int(xs[j]) + 1, 1, c)

    def text(self, x, y, s, scale, color, align="left", grad=None):
        """Draw text; top-left origin. grad=(top,bottom) tints per row."""
        w = text_width(s, scale)
        if align == "center":
            x -= w // 2
        elif align == "right":
            x -= w
        for ci, ch in enumerate(s):
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                if grad is not None:
                    t = row / 6.0
                    col = mix(grad[0], grad[1], t)
                else:
                    col = color
                bits = glyph[row]
                for col_i in range(5):
                    if bits[col_i] == "#":
                        gx = x + (ci * CHAR_ADV + col_i) * scale
                        gy = y + row * scale
                        self.rect(gx, gy, scale, scale, col)
        return w

    def text_block(self, x, y, lines, scale, color, leading=None, align="left",
                   max_w=None, grad=None):
        """Draw lines top to bottom; returns the y just below the block."""
        lh = leading if leading is not None else 7 * scale + 4
        cy = y
        for ln in lines:
            lx = x
            if align == "center" and max_w is not None:
                lx = x + (max_w - text_width(ln, scale)) // 2
            self.text(lx, cy, ln, scale, color, grad=grad)
            cy += lh
        return cy


# ---------------------------------------------------------------- png
def png_bytes(cv):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.buf[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))

# ---------------------------------------------------------------- palette
CREAM = (245, 237, 218)
PAPER = (251, 246, 233)
INK = (31, 36, 48)
NAVY = (22, 35, 63)
NAVY2 = (30, 50, 87)
GOLD = (242, 201, 76)
GOLD_D = (212, 160, 23)
RULE = (216, 201, 163)
ACCENT = (176, 92, 43)   # terracotta kicker
TEAL_D = (11, 37, 49)
TEAL = (20, 58, 74)
SKY_DUSK = (232, 168, 92)
SKY_DUSK2 = (201, 111, 59)
FIRE = (245, 158, 11)
FIRE2 = (239, 68, 68)
FLAME = (253, 230, 138)
SMOKE = (107, 114, 128)
DARK = (26, 26, 34)


def panel(cv, x, y, w, h):
    """Warm paper panel with a soft shadow and a thin rule border."""
    cv.rect(x + 3, y + 4, w, h, (222, 208, 178))
    cv.rect(x, y, w, h, PAPER)
    cv.rect(x, y, w, 2, RULE)
    cv.rect(x, y + h - 2, w, 2, RULE)
    cv.rect(x, y, 2, h, RULE)
    cv.rect(x + w - 2, y, 2, h, RULE)


def explosion(cv, cx, cy, r):
    """Layered fireball: pale core, orange mid, red rim, grey smoke."""
    cv.circle(cx, cy + int(r * 0.55), int(r * 0.95), (150, 148, 140))
    cv.circle(cx - int(r * 0.5), cy + int(r * 0.35), int(r * 0.6), (130, 128, 120))
    cv.circle(cx, cy, r, FIRE2)
    cv.circle(cx, cy - int(r * 0.12), int(r * 0.72), FIRE)
    cv.circle(cx, cy - int(r * 0.2), int(r * 0.42), FLAME)
    cv.circle(cx - int(r * 0.28), cy - int(r * 0.35), int(r * 0.2), (255, 251, 235))


def mine(cv, cx, cy, r):
    """Naval mine: dark sphere with eight spikes."""
    for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1), (0, -1), (0, 1),
                   (-1, 0), (1, 0)):
        cv.line(cx, cy, cx + dx * (r + 7), cy + dy * (r + 7), DARK, 3)
    cv.circle(cx, cy, r, DARK)
    cv.circle(cx - r // 3, cy - r // 3, max(2, r // 4), (70, 70, 80))


def tanker(cv, x, y, w, h):
    """Dark oil tanker silhouette on the water."""
    hull = h // 2
    cv.poly([(x, y + hull), (x + w, y + hull), (x + w - 14, y + h),
             (x + 10, y + h)], (24, 24, 30))
    cv.rect(x + int(w * 0.62), y + 8, int(w * 0.2), hull - 6, (30, 30, 38))
    cv.rect(x + int(w * 0.66), y - 2, 6, 12, (30, 30, 38))
    cv.rect(x + int(w * 0.12), y + 14, int(w * 0.3), hull - 12, (38, 38, 48))
    for i in range(3):
        fx = x + int(w * (0.2 + i * 0.14))
        cv.rect(fx, y + hull + 4, 10, 8, (52, 52, 64))


def warship(cv, x, y, w, h):
    """Grey warship silhouette with a mast and a bow blast."""
    cv.poly([(x, y + h // 2), (x + w, y + h // 2), (x + w - 18, y + h),
             (x + 12, y + h)], (52, 56, 64))
    cv.rect(x + int(w * 0.42), y + 12, int(w * 0.3), h // 2 - 10, (62, 66, 74))
    cv.line(x + int(w * 0.55), y + 12, x + int(w * 0.55), y - 14, (62, 66, 74), 4)
    cv.line(x + int(w * 0.55), y - 14, x + int(w * 0.68), y - 4, (62, 66, 74), 3)
    cv.rect(x + int(w * 0.18), y + 22, int(w * 0.16), h // 2 - 20, (70, 74, 82))


def pumpjack(cv, x, y, w, h):
    """Oil pumpjack silhouette against a desert sky."""
    base = y + h
    cv.poly([(x + 8, base), (x + int(w * 0.42), y + 26),
             (x + int(w * 0.55), y + 26), (x + int(w * 0.8), base)], (43, 33, 24))
    cv.line(x + int(w * 0.14), base - 6, x + int(w * 0.5), y + 26, (43, 33, 24), 5)
    cv.line(x + int(w * 0.5), y + 26, x + int(w * 0.94), y + 44, (43, 33, 24), 6)
    cv.rect(x + int(w * 0.88), y + 40, 12, 16, (43, 33, 24))
    cv.line(x + int(w * 0.5), y + 26, x + int(w * 0.5), base - 4, (43, 33, 24), 4)
    cv.circle(x + int(w * 0.5), y + 26, 6, (43, 33, 24))


def trophy(cv, cx, cy, s):
    """Gold trophy cup on a green pitch."""
    cv.poly([(cx - 34 * s // 10, cy - 26 * s // 10),
             (cx + 34 * s // 10, cy - 26 * s // 10),
             (cx + 20 * s // 10, cy + 18 * s // 10),
             (cx - 20 * s // 10, cy + 18 * s // 10)], GOLD)
    cv.poly([(cx - 34 * s // 10, cy - 26 * s // 10),
             (cx + 34 * s // 10, cy - 26 * s // 10),
             (cx + 30 * s // 10, cy - 18 * s // 10),
             (cx - 30 * s // 10, cy - 18 * s // 10)], GOLD_D)
    cv.ellipse(cx - 38 * s // 10, cy - 8 * s // 10, 12 * s // 10, 16 * s // 10,
               GOLD_D)
    cv.ellipse(cx + 38 * s // 10, cy - 8 * s // 10, 12 * s // 10, 16 * s // 10,
               GOLD_D)
    cv.rect(cx - 3 * s // 10, cy + 18 * s // 10, 6 * s // 10, 16 * s // 10, GOLD_D)
    cv.rect(cx - 16 * s // 10, cy + 34 * s // 10, 32 * s // 10, 8 * s // 10, GOLD)
    cv.circle(cx + 52 * s // 10, cy + 30 * s // 10, 12 * s // 10, (250, 250, 245))
    cv.line(cx + 44 * s // 10, cy + 24 * s // 10, cx + 60 * s // 10,
            cy + 36 * s // 10, INK, 2)


def city_blast(cv, x, y, w, h):
    """City blocks at dusk with a blast rising between them."""
    cv.vgrad(x, y, w, h, (107, 91, 122), (62, 51, 80))
    for bx, bw, bh in ((0, 46, 120), (56, 60, 170), (128, 52, 100),
                       (190, 56, 150)):
        cv.rect(x + bx, y + h - bh, bw, bh, (46, 42, 51))
        for wy in range(y + h - bh + 12, y + h - 8, 22):
            for wx in range(x + bx + 8, x + bx + bw - 8, 18):
                cv.rect(wx, wy, 7, 9, (242, 201, 76))
    explosion(cv, x + w // 2, y + 66, 34)


def courthouse(cv, x, y, w, h):
    """Courthouse portico: pediment, columns and steps."""
    cv.vgrad(x, y, w, h, (231, 220, 195), (201, 191, 169))
    cv.poly([(x + 14, y + 58), (x + w // 2, y + 12), (x + w - 14, y + 58)],
            (138, 127, 104))
    cv.rect(x + 14, y + 58, w - 28, 8, (120, 110, 90))
    for i in range(4):
        cx = x + 34 + i * ((w - 68) // 3)
        cv.rect(cx - 9, y + 66, 18, h - 66 - 26, (168, 156, 130))
        cv.rect(cx - 13, y + 62, 26, 8, (150, 138, 114))
        cv.rect(cx - 13, y + h - 30, 26, 8, (150, 138, 114))
    cv.rect(x + 8, y + h - 22, w - 16, 7, (120, 110, 90))
    cv.rect(x + 2, y + h - 12, w - 4, 7, (104, 95, 78))
    cv.rect(x + 8, y + h - 46, 12, 40, (0, 85, 164))
    cv.rect(x + 20, y + h - 46, 12, 40, (250, 250, 245))
    cv.rect(x + 32, y + h - 46, 12, 40, (239, 65, 53))


# ---------------------------------------------------------------- scenes
def scene_hero(cv, x, y, w, h):
    cv.vgrad(x, y, w, h, SKY_DUSK, SKY_DUSK2)
    cv.circle(x + w - 70, y + 42, 26, (255, 214, 140))
    sea_y = y + int(h * 0.52)
    cv.vgrad(x, sea_y, w, h - (sea_y - y), TEAL, TEAL_D)
    for i in range(5):
        wy = sea_y + 14 + i * 16
        cv.rect(x + 12 + (i % 2) * 30, wy, w - 60, 2, (46, 96, 116))
    tanker(cv, x + 24, sea_y - 58, w - 120, 92)
    explosion(cv, x + w - 92, sea_y - 96, 44)
    mine(cv, x + 52, sea_y + 62, 13)
    mine(cv, x + w - 56, sea_y + 78, 10)


def scene_ukraine(cv, x, y, w, h):
    cv.vgrad(x, y, w, h, (217, 201, 168), (150, 158, 150))
    sea_y = y + int(h * 0.55)
    cv.vgrad(x, sea_y, w, h - (sea_y - y), (44, 74, 94), (24, 44, 60))
    warship(cv, x + 18, sea_y - 52, w - 60, 84)
    explosion(cv, x + w - 58, sea_y - 62, 30)
    for i in range(4):
        wy = sea_y + 12 + i * 15
        cv.rect(x + 10 + (i % 2) * 26, wy, w - 50, 2, (96, 130, 150))


def scene_iraq(cv, x, y, w, h):
    cv.vgrad(x, y, w, h, (233, 192, 122), (217, 154, 78))
    cv.circle(x + w - 46, y + 34, 20, (255, 226, 160))
    cv.rect(x, y + h - 42, w, 42, (227, 192, 138))
    pumpjack(cv, x + 30, y + 26, w - 60, h - 68)


def scene_senegal(cv, x, y, w, h):
    cv.vgrad(x, y, w, h, (14, 122, 61), (10, 92, 46))
    cv.ellipse(x + w // 2, y + h - 8, w // 2 + 20, 12, (18, 140, 72))
    cv.rect(x, y, w, 10, (242, 201, 76))
    trophy(cv, x + w // 2 - 14, y + h // 2 - 6, 10)


def scene_colombia(cv, x, y, w, h):
    city_blast(cv, x, y, w, h)


def scene_france(cv, x, y, w, h):
    courthouse(cv, x, y, w, h)


# ---------------------------------------------------------------- layout
def headline_block(cv, x, y, max_w, kicker, lines, sub, kcolor, scale=3):
    """Kicker + wrapped headline + sub-line inside a panel."""
    for ln in lines:
        if text_width(ln, scale) > max_w:
            raise ValueError("headline line %r too wide for panel" % ln)
    if kicker:
        cv.text(x, y, kicker, 2, kcolor)
        y += 18
    y = cv.text_block(x, y, lines, scale, INK, leading=7 * scale + 5)
    if sub:
        y += 2
        for ln in wrap_text(sub, 2, max_w):
            cv.text(x, y, ln, 2, (90, 84, 70))
            y += 17
    return y


def build():
    cv = Canvas(W, H, CREAM)

    # Masthead: navy band, giant gold 3D title, gold dateline.
    cv.vgrad(0, 0, W, 150, NAVY, NAVY2)
    cv.text(W // 2 + 5, 23, "THE WORLD", 11, (10, 16, 32), align="center",
            grad=((16, 26, 50), (16, 26, 50)))
    cv.text(W // 2, 18, "THE WORLD", 11, GOLD_D, align="center",
            grad=(GOLD, GOLD_D))
    cv.rect(60, 136, W - 120, 2, GOLD)
    cv.text(W // 2, 104, "WEDNESDAY 25 NOVEMBER 2026", 4, GOLD, align="center")

    # Hero: Hormuz tankers.
    hx, hy, hw, hh = 20, 168, 620, 408
    panel(cv, hx, hy, hw, hh)
    scene_hero(cv, hx + 2, hy + 2, hw - 4, 236)
    headline_block(cv, hx + 16, hy + 256, hw - 32, "GULF CRISIS",
                   ["FOUR TANKERS HIT", "MINES IN HORMUZ"],
                   "IRAN CLAIMS A 4TH BLAST IN TWO DAYS", ACCENT, scale=5)

    # Side: Ukraine warship off Libya.
    sx, sy, sw, sh = 660, 168, 344, 408
    panel(cv, sx, sy, sw, sh)
    scene_ukraine(cv, sx + 2, sy + 2, sw - 4, 236)
    headline_block(cv, sx + 14, sy + 256, sw - 28, "UKRAINE",
                   ["UKRAINE SANK", "A WARSHIP", "OFF LIBYA"],
                   "ZELENSKIY CONFIRMS IT", ACCENT, scale=4)

    # Bottom row: Iraq, Senegal, Colombia, France.
    bw, bh = 237, 408
    by = 596
    panels = [
        (20, scene_iraq, "IRAQ",
         ["BAGHDAD", "SEIZES KURD", "OILFIELDS"], "ERBIL SAYS NO"),
        (269, scene_senegal, "FOOTBALL",
         ["SENEGAL WIN", "AFCON BACK"], "CAS RESTORES TITLE"),
        (518, scene_colombia, "COLOMBIA",
         ["CAR BOMB", "WOUNDS 23", "IN COLOMBIA"], "EVE OF FARC PEACE DEAL"),
        (767, scene_france, "FRANCE",
         ["SARKOZY", "AND BRUNI", "FACE TRIAL"], "LIBYA CASE, APRIL 2027"),
    ]
    for bx, scene, kicker, lines, sub in panels:
        panel(cv, bx, by, bw, bh)
        scene(cv, bx + 2, by + 2, bw - 4, 190)
        headline_block(cv, bx + 12, by + 206, bw - 24, kicker, lines, sub,
                       ACCENT, scale=3)

    return png_bytes(cv)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(build())
    os.chmod(path, 0o644)


if __name__ == "__main__":
    main()
