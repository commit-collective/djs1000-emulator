#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Makes the hero picture of the README and the website from pictures of the decks, keeping the layout of the one it replaces.

    hero.py [--scene demo/hero/deck.png] [--sp16 demo/hero/sp16.png] [--template HERO.png] [--out HERO.png] [--font TTF]

The picture has three parts on a dark grid: the DJS-1000 on the left, the SP-16 and the list of mods on the right, with a
title over each of the two (TITLES, in the website's monospace font, JetBrains Mono). It is made on the picture it replaces
(--template, by default the website's, which is also where it is written): the grid and the frames stay, and the decks, the
card and the titles are replaced by what tools/hero_scene.py saved (run it for each unit). So nothing moves from one version
to the next, and a new look of a deck is a new scene and one run of this.

Needs Pillow. Nothing here is committed: the picture shows the firmware's screen.
"""
import argparse
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SITE_HERO = os.path.join(REPO, "..", "commitcollective.cc", "public", "djs1000", "emulator", "hero.png")
SITE_FONT = os.path.join(REPO, "..", "commitcollective.cc", "public", "assets", "fonts", "jetbrains-mono-v24-latin.woff2")
FONT_SIZE = 20

# The titles: where the text's top is, the box cleared behind it, the text.
TITLES = (((1181, 112), (1170, 100, 2100, 140), "TORAIZ SP-16, UNMODIFIED"),
          ((1181, 744), (1170, 732, 2100, 772), "DJS-1000 MODS, SWITCHED LIVE"))

# Where the three cards are in the picture (x0, y0, x1, y1, as the last version has them), and what of the deck's window (2196x1800)
# goes in each.
DECK_AT = (110, 110, 1086, 1331)
SP16_AT = (1176, 154, 2058, 685)               # the SP-16, centred in it (where the DJS app's screen card was)
MODS_AT = (1176, 785, 2058, 1332)
FRAME = (46, 46, 46)                         # the frame of a card: one dim line, the same on all four sides
DECK_FROM = (0, 25, 1358, 1754)              # the unit, from the top of the housing to the foot of the case
MODS_FROM = (1380, 515, 2180, 1015)          # the list of mods and the text of the one pointed at


def outside(img):
    """A mask of what is round the unit: the black joined to the picture's corners (the screen is black inside, so not all black)."""
    flood = img.convert("L").point(lambda v: 255 if v <= 1 else 0)
    w, h = flood.size
    for corner in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
        if flood.getpixel(corner) == 255:
            ImageDraw.floodfill(flood, corner, 128)
    return flood.point(lambda v: 255 if v == 128 else 0)


def clear_background(base, box):
    """Puts back what the picture has behind the deck (a vignette and a grid of lines every 64 pixels) where the deck was."""
    px = base.load()
    x0, y0, x1, y1 = box
    lx, rx = x0 - 8, x1 + 6                                   # a column beside the box on each side, off the grid lines
    for y in range(y0, y1):
        a, b = px[lx, y][0], px[rx, y][0]
        for x in range(x0, x1):
            v = a + (b - a) * (x - lx) / float(rx - lx)
            if x % 64 == 0 or y % 64 == 0:
                v += 4
            v = int(round(v))
            px[x, y] = (v, v, v + 1)


def rounded(size, radius):
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255)
    return mask


def card(base, scene, source, at, radius=0):
    w, h = at[2] - at[0], at[3] - at[1]
    part = scene.crop(source).resize((w, h), Image.LANCZOS)
    base.paste(part, at[:2], rounded((w, h), radius) if radius else None)
    ImageDraw.Draw(base).rounded_rectangle((at[0], at[1], at[2] - 1, at[3] - 1), radius=radius, outline=FRAME, width=1)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--scene", default=os.path.join(REPO, "demo", "hero", "deck.png"), help="the DJS-1000's window")
    ap.add_argument("--sp16", default=os.path.join(REPO, "demo", "hero", "sp16.png"), help="the SP-16's window")
    ap.add_argument("--font", default=SITE_FONT, help="the titles' font (the website's JetBrains Mono)")
    ap.add_argument("--template", default=SITE_HERO)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    out = args.out or args.template
    base = Image.open(args.template).convert("RGB")
    scene = Image.open(args.scene).convert("RGB")

    unit = scene.crop(DECK_FROM).resize((DECK_AT[2] - DECK_AT[0], DECK_AT[3] - DECK_AT[1]), Image.LANCZOS)
    clear_background(base, DECK_AT)
    base.paste(unit, DECK_AT[:2], outside(unit).point(lambda v: 255 - v))     # the background shows round the unit
    sp16 = Image.open(args.sp16).convert("RGB")
    sp16 = sp16.crop((0, 0, sp16.width, sp16.height - 40))                  # the window's status bar off
    sp16 = sp16.crop(sp16.convert("L").point(lambda v: 255 if v > 6 else 0).getbbox())
    x0, y0, x1, y1 = SP16_AT
    clear_background(base, (x0 - 4, y0 - 4, x1 + 4, y1 + 4))
    w, h = x1 - x0, round(sp16.height * (x1 - x0) / sp16.width)
    if h > y1 - y0:
        w, h = round(sp16.width * (y1 - y0) / sp16.height), y1 - y0
    sp16 = sp16.resize((w, h), Image.LANCZOS)
    base.paste(sp16, (x0 + (x1 - x0 - w) // 2, y0 + (y1 - y0 - h) // 2), outside(sp16).point(lambda v: 255 - v))
    card(base, scene, MODS_FROM, MODS_AT, 6)
    font = ImageFont.truetype(args.font, FONT_SIZE)
    draw = ImageDraw.Draw(base)
    for (tx, ty), box, text in TITLES:
        clear_background(base, box)
        draw.text((tx, ty - font.getbbox(text)[1]), text, font=font, fill=(255, 255, 255))
    base.save(out)
    print("wrote", os.path.abspath(out), base.size)


if __name__ == "__main__":
    main()
