# SPDX-License-Identifier: GPL-2.0-or-later
"""Original virtual panel and wire mapping for the TORAIZ SP-16."""

from layout import BLUE, GREEN, RED, WHITE, Key, Knob, Text, POT_STEPS, STEP_KEYS, rgb_lamp

MODEL = "TORAIZ SP-16"
W, H = 1540, 1660
BODY = (10, 10, 1530, 1648)
TOP_BLOCK = (310, 36, 1430, 636)
LCD = (346, 75, 1136, 549)
LCD_W, LCD_H = 800, 480
LCD_ORIGIN = (1, 1)
PAD_FRAME = (415, 680, 1130, 1394)
STRIP = (122, 861, 238, 1295)
USB_PORT = (56, 72, 146, 127)
SLIDER_FRAME = SLIDER = SLIDER_WORD = SLIDER_REF = SLIDER_CENTRE = None

PAD_X = (510, 685, 860, 1035)
PAD_Y = (1298, 1124, 950, 776)
STEP_X = tuple(93 + i * 90 for i in range(16))
PARAM_X = (426, 551, 676, 801, 926, 1051)

KEYS = []


def button(name, label, x, y, bit, lamp=None, keycap="", color=WHITE):
    KEYS.append(Key(name, "rect", box=(x - 57, y - 26, x + 57, y + 26),
                    label=label, bit=bit, lamp=lamp, keycap=keycap, color=color))


button("usb_stop", "USB STOP", 113, 185, (5, 6))
button("back", "BACK", 1219, 499, (1, 2), keycap="Esc")
button("home", "HOME", 1357, 499, (1, 3), keycap="H")
button("shift", "SHIFT", 1219, 586, (2, 0), keycap="Left Shift")
button("filter", "ACTIVE", 181, 750, (5, 5), 23, color=BLUE)
button("mode", "MODE", 180, 810, (2, 5), keycap="M")
button("hold", "HOLD", 180, 1340, (2, 4), 10, "O")
button("scene", "SCENE", 1322, 750, (2, 6), 8, "C")
button("pattern", "PATTERN", 1322, 829, (2, 7), 9, "G")
button("rec", "REC", 1322, 1146, (2, 1), 5, "N", RED)
button("stop", "STOP", 1322, 1237, (2, 2), 6, "B")
button("play", "PLAY", 1322, 1328, (2, 3), 7, "Space", GREEN)
for index, label in enumerate(("TRACK", "MUTE", "SLICE", "SCALE")):
    button(label.lower(), label, 510 + index * 175, 1434, (1, index + 4), index)
for index in range(4):
    y = 912 + index * 53
    KEYS.append(Key(f"bar{index + 1}", "bar", box=(1265, y - 19, 1379, y + 19),
                    bit=(5, index), lamp=26 + index))
    KEYS.append(Key(f"bar_position{index + 1}", "led", box=(1400, y - 7, 1414, y + 7),
                    lamp=30 + index))
for index in range(16):
    x, y = PAD_X[index % 4], PAD_Y[index // 4]
    KEYS.append(Key(f"pad{index + 1}", "pad", box=(x - 74, y - 74, x + 74, y + 74),
                    rgb=index, pad=index))
    x = STEP_X[index]
    KEYS.append(Key(f"step{index + 1}", "step", box=(x - 36, 1519, x + 36, 1609),
                    bit=(3 + index // 8, index % 8), rgb=16 + index, keycap=STEP_KEYS[index]))
for index in range(8):
    y = 1260 - index * 52
    KEYS.append(Key(f"strip_led{index + 1}", "led", box=(250, y - 5, 270, y + 5),
                    lamp=15 + index))
for index, label in enumerate(("REPEAT", "PITCH", "USER 1", "USER 2")):
    y = 934 + index * 91
    KEYS.append(Key(label.lower(), "led", box=(291, y - 5, 303, y + 7), lamp=11 + index))
KEYS.append(Key("over", "led", box=(244, 458, 261, 473), lamp=34, color=RED))

KNOBS = [Knob("selector", (1289, 368, 61), enc=0, push=(1, 1), look="selector")]
KNOBS += [Knob(f"knob{i}", (x, 593, 31), enc=i, keycap=f"F{i}") for i, x in enumerate(PARAM_X, 1)]
KNOBS += [
    Knob("master", (181, 273, 44), word=0x28, look="pot", at=23),
    Knob("drive", (181, 420, 39), word=0x26, look="pot", reverse=True),
    Knob("high_pass", (181, 549, 39), word=0x2A, look="pot", reverse=True),
]

TEXTS = [
    Text(113, 147, "USB", 20),
    Text(181, 335, "MASTER", 21),
    Text(181, 477, "DRIVE", 20),
    Text(181, 605, "HIGH PASS", 20),
    Text(253, 484, "OVER", 14),
    Text(181, 694, "ANALOG FILTER", 20),
    Text(1289, 250, "SELECTOR", 21),
    Text(1322, 872, "BAR", 18),
]
TEXTS += [Text(1248, 912 + i * 53, str(i + 1), 18) for i in range(4)]
TEXTS += [Text(x, 552, str(i), 16) for i, x in enumerate(PARAM_X, 1)]
TEXTS += [Text(PAD_X[i % 4] - 76, PAD_Y[i // 4] - 80, str(i + 1), 14) for i in range(16)]
TEXTS += [Text(x, 1501, str(i), 18) for i, x in enumerate(STEP_X, 1)]
TEXTS += [Text(313, 935 + i * 91, label, 16, anchor="lm")
          for i, label in enumerate(("REPEAT", "PITCH", "USER 1", "USER 2"))]

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
