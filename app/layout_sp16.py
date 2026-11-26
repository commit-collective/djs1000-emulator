# SPDX-License-Identifier: GPL-2.0-or-later
"""Front panel geometry and wire mapping for the TORAIZ SP-16."""

from layout import AMBER, BLUE, GREEN, RED, WHITE, Key, Knob, Text, POT_STEPS, STEP_KEYS, rgb_lamp

MODEL = "TORAIZ SP-16"
W, H = 1750, 1000
BODY = (2, 2, 1748, 998)
TOP_BLOCK = (889, 180, 1535, 560)
LCD = (907, 187, 1517, 553)
LCD_W, LCD_H = 800, 480
LCD_ORIGIN = (1, 1)
FILTER_PANEL = (238, 56, 819, 160)
STRIP_PANEL = (92, 180, 192, 758)
STRIP = (92, 424, 192, 758)
STRIP_TOUCH = (103, 444, 157, 738)
STRIP_HIT = (99, 425, 175, 757)
USB_PORT = (1587, 69, 1674, 174)
SLIDER_FRAME = SLIDER = SLIDER_WORD = SLIDER_REF = SLIDER_CENTRE = None

PAD_X = (300, 452, 604, 756)
PAD_Y = (607, 482, 358, 234)
STEP_X = tuple(round(126 + i * 80.5) for i in range(16))
BAR_X = (1460, 1523, 1586, 1649)
PARAM_X = (947, 1054, 1160, 1267, 1373, 1479)


def button(name, label, x, y, width, bit, lamp=None, *, keycap="", color=WHITE, symbol=""):
    return Key(name, "rect", box=(x - width // 2, y - 19, x + width // 2, y + 19),
               label=label, bit=bit, lamp=lamp, keycap=keycap, color=color, symbol=symbol, font=15)


KEYS = [
    Key("filter", "dome", circle=(856, 105, 18), bit=(5, 5), lamp=23, color=RED),
    Key("usb_stop", "dome", circle=(1488, 105, 24), bit=(5, 6), lamp=24, color=RED),
    Key("usb_lamp", "led", box=(1609, 148, 1652, 157), lamp=25, color=GREEN),
    Key("back", "dome", box=(1574, 218, 1627, 249), bit=(1, 2), keycap="Esc"),
    Key("home", "dome", circle=(1674, 234, 17), bit=(1, 3), keycap="H"),
    Key("over", "led", box=(365, 101, 387, 110), lamp=34, color=AMBER),
    button("mode", "MODE", 142, 213, 66, (2, 5), keycap="M"),
    button("hold", "HOLD", 142, 390, 66, (2, 4), 10, keycap="O"),
    button("shift", "SHIFT", 947, 714, 84, (2, 0), keycap="Left Shift"),
    button("rec", "", 1102, 714, 84, (2, 1), 5, keycap="N", color=RED, symbol="rec"),
    button("stop", "", 1213, 714, 84, (2, 2), 6, keycap="B", symbol="stop"),
    button("play", "", 1324, 714, 84, (2, 3), 7, keycap="Space", color=GREEN, symbol="play"),
    button("scene", "SCENE", 1479, 714, 84, (2, 6), 8, keycap="C"),
    button("pattern", "PATTERN", 1630, 714, 84, (2, 7), 9, keycap="G"),
]
for index, label in enumerate(("TRACK", "MUTE", "SLICE", "SCALE")):
    KEYS.append(button(label.lower(), label, PAD_X[index], 714, 126, (1, index + 4), index))
for index, x in enumerate(BAR_X):
    KEYS.append(Key(f"bar{index + 1}", "bar", box=(x - 23, 836, x + 23, 910),
                    bit=(5, index), lamp=26 + index, color=BLUE))
    KEYS.append(Key(f"bar_position{index + 1}", "led", box=(x - 22, 810, x + 22, 819),
                    lamp=30 + index, color=GREEN))
for index in range(16):
    x, y = PAD_X[index % 4], PAD_Y[index // 4]
    KEYS.append(Key(f"pad{index + 1}", "pad", box=(x - 63, y - 50, x + 63, y + 50),
                    rgb=index, pad=index))
    x = STEP_X[index]
    KEYS.append(Key(f"step{index + 1}", "step", box=(x - 30, 806, x + 30, 910),
                    bit=(3 + index // 8, index % 8), rgb=16 + index, keycap=STEP_KEYS[index]))
for index in range(8):
    y = 717 - index * 36
    KEYS.append(Key(f"strip_led{index + 1}", "led", box=(162, y - 16, 170, y + 16),
                    lamp=15 + index, color=BLUE))
for index, (label, lamp) in enumerate((("PITCH", 12), ("REPEAT", 11), ("USER 1", 13), ("USER 2", 14))):
    y = 267 + index * 23
    KEYS.append(Key(label.lower(), "led", box=(108, y - 8, 176, y + 8),
                    label=label, lamp=lamp, color=GREEN, font=13))

KNOBS = [Knob("selector", (1630, 371, 61), enc=0, push=(1, 1), look="selector")]
KNOBS += [Knob(f"knob{i}", (x, 624, 37), enc=i, keycap=f"F{i}") for i, x in enumerate(PARAM_X, 1)]
KNOBS += [
    Knob("master", (140, 105, 32), word=0x28, look="pot", at=23),
    Knob("drive", (300, 105, 31), word=0x26, look="pot", reverse=True),
    Knob("low_pass", (452, 105, 34), look="pot", at=POT_STEPS),
    Knob("resonance", (604, 105, 31), look="pot"),
    Knob("high_pass", (756, 105, 34), word=0x2A, look="pot", reverse=True),
]

TEXTS = [
    Text(140, 56, "MAIN OUT", 15),
    Text(452, 56, "LOW PASS", 15),
    Text(756, 56, "HIGH PASS", 15),
    Text(300, 150, "DRIVE", 14),
    Text(376, 123, "OVER", 13),
    Text(452, 150, "CUTOFF", 14),
    Text(604, 150, "RESONANCE", 14),
    Text(756, 150, "CUTOFF", 14),
    Text(856, 150, "ACTIVE", 14),
    Text(1488, 66, "USB STOP", 14),
    Text(1488, 148, "WAKE UP", 13),
    Text(1630, 50, "USB", 14),
    Text(1600, 199, "BACK", 14),
    Text(1674, 199, "HOME", 14),
    Text(1630, 596, "PROFESSIONAL", 14),
    Text(1630, 614, "SAMPLER", 14),
    Text(1630, 751, "LENGTH", 13),
]
TEXTS += [Text(x, 793, str(i), 15) for i, x in enumerate(BAR_X, 1)]
TEXTS += [Text(PAD_X[i % 4] - 63, PAD_Y[i // 4] - 60, str(i + 1), 14, anchor="lm") for i in range(16)]
TEXTS += [Text(x, 793, str(i), 15) for i, x in enumerate(STEP_X, 1)]

# Mono channels are packed as on bits with separate dim flags.
LAMPS = dict(enumerate((
    (0x63, 4, 0x6A), (0x63, 1, 0x6A), (0x63, 2, 0x6A), (0x63, 3, 0x6A),
    (0x63, 7, 0), (0x63, 6, 0x6A), (0x63, 5, 0x6A), (0x64, 4, 0x6B),
    (0x64, 6, 0x6B), (0x64, 5, 0x6B), (0x63, 0, 0x6A), (0x64, 1, 0),
    (0x64, 0, 0), (0x64, 2, 0), (0x64, 3, 0),
    *((0x62, bit, 0) for bit in range(8)),
    (0x65, 3, 0), (0x65, 2, 0), (0x65, 0, 0),
    *((0x61, bit, 0x69) for bit in (4, 5, 6, 7, 0, 1, 2, 3)),
    (0x65, 1, 0),
)))

BUTTON_IDS = {}


def unknown_bits():
    return []


def lamp_level(frame, lamp):
    byte, bit, dim = LAMPS[lamp]
    mask = 1 << bit
    if not frame[byte] & mask:
        return 0
    return 1 if (dim and frame[dim] & mask) or frame[0x6E] in (1, 2) else 2
