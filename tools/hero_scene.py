#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Takes the pictures of the decks that the hero picture is made from, each deck's window saved as a PNG.

    hero_scene.py [--patch autoexec.bin] [--out demo/hero/deck.png] [--hover MOD]
    hero_scene.py --unit sp16 [--out demo/hero/sp16.png]

The DJS-1000 (the default): a fresh unit with the test kit loaded, the first track's kick on the beats, and the mods' list
with --patch. The window is 2196x1800, so that the app's screen is 800x480 in it.

The SP-16: a fresh unit that opens the project the regression session saved (tools/regress.py: its kick, snare and hat
from the test kit, the kick on the beats), so run that session first. The window is 2400x1160.

Starts an emulator of its own, like tools/demo.py (stop a running one first). tools/hero.py cuts the pictures up. Run on
the host, like start.py. Nothing here is committed: the pictures show the firmware's screen.
"""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "app"))

import demo  # noqa: E402
import regress  # noqa: E402
import start  # noqa: E402
from session import Session  # noqa: E402

# The SP-16 gets a fresh stick and settings next to its home. The project and the kit come from the last regression
# session on the DJS-1000 (its folder is ~/djs/regress, or DJS_REGRESS names it).
SP16_ENV = 'DJS_USB="${DJS_HOME:-$HOME/sp16}/hero/usb" DJS_DATA="${DJS_HOME:-$HOME/sp16}/hero/data"'
SP16_PREPARE = '''
D="${DJS_HOME:-$HOME/sp16}/hero"; R="${DJS_REGRESS:-$HOME/djs/regress}/usb/PIONEER DJ SAMPLER"
[ -f "$R/Projects/reg.prj" ] && [ -d "$R/Samples/Test Kit" ] \\
  || { echo "no regression project in $R: run python tools/regress.py first"; exit 1; }
rm -rf "$D"; mkdir -p "$D/usb/PIONEER DJ SAMPLER/Projects" "$D/usb/PIONEER DJ SAMPLER/Samples" "$D/data"
cp "$R/Projects/reg.prj" "$D/usb/PIONEER DJ SAMPLER/Projects/"
cp -R "$R/Samples/Test Kit" "$D/usb/PIONEER DJ SAMPLER/Samples/"
'''
SP16_PROJECT = (55, 60)          # HOME's project icon, top left
SP16_OK = (486, 333)             # OK in OPEN PROJECT's warning


def open_project_sp16(s):
    """PROJECT > OPEN > the stick's only project, then OK. The lists follow the selector, not the touch screen."""
    s.touch(*SP16_PROJECT)
    s.turn(1)                    # CREATE NEW > OPEN
    s.push()
    s.push()                     # reg.prj
    s.touch(*SP16_OK)
    s.pump(4.0)
    s.settle()


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--unit", choices=("djs1000", "sp16"), default="djs1000")
    ap.add_argument("--patch", help="the djs1000-mods autoexec.bin: the list of mods (DJS-1000)")
    ap.add_argument("--out", default=None, help="default: demo/hero/deck.png, or demo/hero/sp16.png for the SP-16")
    ap.add_argument("--hover", default="rec-length", help="the mod whose text shows under the list (DJS-1000)")
    args = ap.parse_args()
    sp16 = args.unit == "sp16"
    out = os.path.abspath(args.out or os.path.join(REPO, "demo", "hero", "sp16.png" if sp16 else "deck.png"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    distro = os.environ.get("DJS_WSL_DISTRO")
    emu = start.Emulator(distro, 7310, env=SP16_ENV, unit="sp16") if sp16 else start.Emulator(distro, 7310, env=demo.ENV)
    if emu.running():
        sys.exit("An emulator is running: stop it first (start.py stop).")
    if sp16:
        code, text = emu.sh(SP16_PREPARE)
        if code:
            sys.exit("could not prepare the unit:\n" + text)
    else:
        demo.prepare(emu, args.patch)
    emu.start()
    try:
        if not emu.wait():
            sys.exit("the emulator did not answer:\n" + emu.log_tail())
        s = Session()
        if not s.wait_screen(quiet=1.5, timeout=120):
            sys.exit("the app never drew its first screen")
        s.wait_usb()
        if sp16:
            open_project_sp16(s)
            size = ["--unit", "sp16", "--width", "2400", "--height", "1160"]
        else:
            if args.patch:
                regress.wait_patch(emu, s)
            demo.load_kit(s)
            s.touch(*regress.TRACK[0])
            s.press(regress.HOME)
            for n in (0, 4, 8, 12):                  # the kick on the beats
                s.press(regress.STEP[n])
            s.settle()
            size = ["--width", "2196", "--height", "1800", "--hover", args.hover]
        cmd = [sys.executable, os.path.join(REPO, "app", "virtual_djs.py"), "--port", str(emu.port), "--no-audio",
               "--no-input", "--snapshot", out] + size
        usb, modlist = emu.usb(), emu.modlist()
        if usb and args.patch and not sp16:
            cmd += ["--usb", usb]
        if modlist and args.patch and not sp16:
            cmd += ["--modlist", modlist]
        env = dict(os.environ, SDL_VIDEODRIVER="dummy", PYGAME_HIDE_SUPPORT_PROMPT="1")
        deck = subprocess.Popen(cmd, env=env)
        while deck.poll() is None:
            s.pump(0.2)
        print("wrote", out)
    finally:
        emu.stop()


if __name__ == "__main__":
    main()
