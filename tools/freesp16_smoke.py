# SPDX-License-Identifier: GPL-2.0-or-later
"""freesp16's emulator smoke test (its scripts/emulator-smoke.sh), on this emulator.

freesp16 is an open firmware for the SP-16, started from the community boot
menu. Its own smoke test needs another emulator (Apple silicon only). This one
does the same steps with this emulator's tools, so it runs on Windows (WSL) and
Linux too, and on the DJS-1000:

  1. a slot's stick gets the boot menu, the freesp16 build, its settings and its
     16-sample test kit (freesp16's tools/gen-test-kit.py), the menu set to
     start freesp16
  2. the slot starts (start.py --no-deck), the script waits for "KIT ready"
  3. it hits pads 1-16 500 ms apart while recording MAIN over the deck link
     (tools/session.py), turns knob 1 down 20 detents and back, takes the screen
  4. freesp16's tools/analyze-wav.py checks the recording against the kit (16
     onsets in order, peak, clicks), and the app's log is read for xruns
  5. the slot stops (--keep leaves it running)

    python tools/freesp16_smoke.py --freesp16 PATH [options]

  --freesp16 PATH    the freesp16 checkout (its tools are used from there)
  --binary FILE      the armel build (default: PATH/out/armel/freesp16)
  --bootmenu FILE    the boot menu's autoexec.bin (default: the one already on the slot's stick)
  --unit NAME        sp16 (default) or djs1000
  --slot N           the slot (default 47, port 7300 + N). Only a new slot or one this runner made (it marks
                     its home): it sets the stick up again. Not a slot that runs, nor 10, 20 or 30 (the ports of
                     an emulator without a slot), nor one whose port something already answers on
  --tone             the tone check instead of the kit (no kit: the 440 Hz test tone on track 1)
  --out DIR          where the WAV, the screens and the log go (default: demo/freesp16-smoke, ignored by git)
  --distro NAME      the WSL distribution (default: $DJS_WSL_DISTRO, else WSL's default)
  --keep             leave the slot running

Exit 0 = every check passed. The timings are qemu's: xruns are gated, the
engine's load is only reported (as freesp16's own test does).
"""
import functools
import os
import shlex
import socket
import sys
import time

print = functools.partial(print, flush=True)  # in order with start.py's output

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, REPO)

from session import Session, save_wav  # noqa: E402
import start  # noqa: E402

NAME, TAG = "freesp16", "FREESP16"   # the app's id on the stick and its log prefix
PAD_SPACING = 0.5                    # s: the emulator's input jitter, as freesp16's own test
LEAD, TAIL = 1.0, 1.5                # s of recording before the first hit and after the last


def option(args, name, default=None):
    if name in args:
        i = args.index(name)
        value = args[i + 1]
        del args[i:i + 2]
        return value
    return default


def flag(args, name):
    if name in args:
        args.remove(name)
        return True
    return False


MARK = ".freesp16-smoke"   # in a slot's home: the runner made it, and may set its stick up again
UNSLOTTED_PORTS = (7310, 7320, 7330)   # an emulator without a slot: its deck link, audio and feed


class Bench:
    def __init__(self, unit, slot, distro):
        self.unit, self.slot, self.distro = unit, slot, distro
        self.port = 7300 + slot
        os.environ["DJS_SLOT"], os.environ["DJS_PORT"] = str(slot), str(self.port)
        os.environ.pop("DJS_USB", None)
        self.emu = start.Emulator(distro, self.port, unit=unit)
        # The stick is the slot's own: a DJS_USB from a login profile would attach another one than the one staged here.
        self.emu.prelude += "unset DJS_USB\n"

    def sh(self, script):
        """Runs bash where the emulator lives ($DJS_HOME is the slot's home)."""
        return self.emu.sh(script)

    def path(self, local):
        """A path of this machine as the emulator's shell sees it."""
        local = os.path.abspath(local)
        if not start.WINDOWS:
            return local
        code, out = self.sh("wslpath -u %s" % shlex.quote(local.replace("\\", "/")))
        if code:
            sys.exit("cannot reach %s from WSL: %s" % (local, out))
        return out.splitlines()[-1]

    def port_answers(self):
        try:
            socket.create_connection(("127.0.0.1", self.port), timeout=1).close()
            return True
        except OSError:
            return False

    def claim(self):
        """Makes the slot this runner's, in one step: a new home is made here (mkdir fails if another launcher made
        it first), an existing one must carry the mark. False when the slot is someone else's."""
        return self.sh('if mkdir "$DJS_HOME" 2> /dev/null; then : > "$DJS_HOME/%s"; else [ -e "$DJS_HOME/%s" ]; fi'
                       % (MARK, MARK))[0] == 0

    def lock(self):
        """One run at a time in the slot: a lock folder for the run's length (mkdir fails if another run holds it)."""
        return self.sh('mkdir "$DJS_HOME/%s.lock" 2> /dev/null' % MARK)[0] == 0

    def unlock(self):
        self.sh('rmdir "$DJS_HOME/%s.lock" 2> /dev/null' % MARK)

    def start(self):
        """Starts the slot as start.py --no-deck does, with this runner's environment (no DJS_USB)."""
        self.emu.start()
        return self.emu.wait()

    def stop(self):
        self.emu.stop()

    def log(self):
        return self.sh('cat "$DJS_HOME/usb/bootmenu.log" 2> /dev/null')[1]

    def wait_log(self, needles, timeout):
        end = time.time() + timeout
        while time.time() < end:
            text = self.log()
            for n in needles:
                if n in text:
                    return n
            time.sleep(2)
        return None


def app_lines(log):
    """The app's own lines, without their prefix."""
    out = []
    for line in log.splitlines():
        at = line.find(TAG + " ")
        if at >= 0:
            out.append(line[at + len(TAG) + 1:])
    return out


def main():
    args = sys.argv[1:]
    if not args or flag(args, "-h") or flag(args, "--help"):
        print(__doc__)
        return 0
    checkout = option(args, "--freesp16")
    if not checkout:
        sys.exit("--freesp16 PATH: the freesp16 checkout")
    binary = option(args, "--binary", os.path.join(checkout, "out", "armel", NAME))
    bootmenu = option(args, "--bootmenu")
    unit = option(args, "--unit", "sp16")
    slot = int(option(args, "--slot", "47"))
    out = os.path.abspath(option(args, "--out", os.path.join(REPO, "demo", "freesp16-smoke")))
    distro = option(args, "--distro", os.environ.get("DJS_WSL_DISTRO"))
    tone, keep = flag(args, "--tone"), flag(args, "--keep")
    if args:
        sys.exit("unknown arguments: %s" % " ".join(args))
    if unit not in ("sp16", "djs1000"):
        sys.exit("--unit sp16 or djs1000")
    for f in [binary] + ([bootmenu] if bootmenu else []):
        if not os.path.isfile(f):
            sys.exit("no %s" % f)
    os.makedirs(out, exist_ok=True)

    if 7300 + slot in UNSLOTTED_PORTS:
        sys.exit("slot %d would use port %d, an emulator without a slot's: pick another --slot" % (slot, 7300 + slot))
    b = Bench(unit, slot, distro)
    if b.emu.starting():
        sys.exit("slot %d is in use: stop it first (DJS_SLOT=%d start.py --unit %s stop), or pick another --slot"
                 % (slot, slot, unit))
    if b.port_answers():
        sys.exit("something already answers on port %d: pick another --slot" % b.port)
    if not b.claim():
        sys.exit("slot %d already has a home that this runner did not make (its stick would be set up again): "
                 "pick a new --slot" % slot)
    if not b.lock():
        sys.exit("another run holds slot %d (%s.lock in its home: remove it if no run is going)" % (slot, MARK))
    try:
        # Again under the lock: a run that ended with --keep leaves its emulator running after it lets the lock go.
        if b.emu.starting() or b.port_answers():
            print("slot %d is in use (a run left it running with --keep?): stop it first "
                  "(DJS_SLOT=%d start.py --unit %s stop), or pick another --slot" % (slot, slot, unit))
            return 2
        return run(b, checkout, binary, bootmenu, unit, slot, out, tone, keep)
    finally:
        b.unlock()


def run(b, checkout, binary, bootmenu, unit, slot, out, tone, keep):
    """Everything after the slot is claimed and locked: the stick, the run, the checks."""
    b.emu.ensure_home()

    # 1. the stick
    q = shlex.quote
    tools = b.path(os.path.join(checkout, "tools"))
    settings = "test_tone=1" if tone else "dev_kit=Samples/TestKit"
    code, text = b.sh(f"""
set -e
USB="$DJS_HOME/usb"; DATA="$USB/{NAME}-data/{NAME}"; RUN="$DJS_HOME/run/{NAME}-smoke"
mkdir -p "$USB" "$DATA" "$RUN"
{"cp " + q(b.path(bootmenu)) + ' "$USB/autoexec.bin"' if bootmenu else ""}
[ -f "$USB/autoexec.bin" ] || {{ echo "no boot menu on the stick: give --bootmenu FILE"; exit 1; }}
cp {q(b.path(binary))} "$USB/{NAME}"
printf 'default={NAME}\\ntimeout=1\\nssh=0\\n' > "$USB/bootmenu.conf"
printf '%s\\n' {q(settings)} > "$DATA/{NAME}.conf"
{"" if tone else 'rm -rf "$DATA/Samples/TestKit"; '
 f'python3 {q(tools)}/gen-test-kit.py "$DATA/Samples/TestKit" --json "$RUN/kit.json" > /dev/null'}
: > "$USB/bootmenu.log"
echo "stick ready: $USB"
""")
    print(text)
    if code:
        return 2

    # 2. the slot
    print("starting slot %d (%s, port %d)..." % (slot, unit, b.port))
    if not b.start():
        print("the slot did not start:\n" + b.emu.log_tail())
        b.stop()
        return 2
    rc = 0
    try:
        found = b.wait_log([TAG + " RUN", "runner: " + NAME + " exited"], 240)
        if found != TAG + " RUN":
            print("the app did not reach RUN")
            print("\n".join(app_lines(b.log())[-20:]))
            return 1
        if not tone:
            found = b.wait_log([TAG + " KIT ready", TAG + " KIT FAILED"], 120)
            if found != TAG + " KIT ready":
                print("the kit did not load")
                print("\n".join(app_lines(b.log())[-20:]))
                return 1
        s = Session(port=b.port)
        if not s.wait_screen(timeout=30):
            print("no screen from the app on port %d" % b.port)
            s.close()
            return 1
        s.pump(2.0)

        # 3. the pads, the knob, the screen
        # The kit: pads 1-16 in order. The tone: pads 5 and 1, as freesp16's own test (the tone is on track 1).
        pads = [4, 0] if tone else list(range(16))

        def hits():
            s.pump(LEAD)
            first = time.time()
            for i, n in enumerate(pads):
                s.pad(n, level=800, hold=0.3 if tone else 0.05)
                s.pump(max(0.0, first + PAD_SPACING * (i + 1) - time.time()))

        seconds = LEAD + PAD_SPACING * len(pads) + TAIL + (2.0 if tone else 0.0)
        sound = s.record(seconds, hits, which=0)
        wav = os.path.join(out, "master.wav")
        save_wav(wav, sound)
        s.turn(-20, enc=1)
        s.pump(1.5)
        s.shot(os.path.join(out, "home-turned.png"))
        s.turn(20, enc=1)
        s.pump(4.0)
        s.shot(os.path.join(out, "home.png"))
        s.pump(8.0)                       # one 10 s FRAME and LOAD report of the app
        s.close()

        # 4. the checks
        print("--- audio (%s, %.1f s)" % (wav, len(sound) / 2 / 44100))
        run = '"$DJS_HOME/run/%s-smoke"' % NAME
        data = '"$DJS_HOME/usb/%s-data/%s"' % (NAME, NAME)
        if tone:
            check = f"python3 {q(tools)}/analyze-wav.py {q(b.path(wav))} --channels 0,1 --expect-hz 440 --seconds 3"
        else:
            check = (f"python3 {q(tools)}/analyze-wav.py {q(b.path(wav))} --channels 0,1 --kit {run}/kit.json"
                     f" --kit-dir {data}/Samples/TestKit")
        code, text = b.sh(check)
        print(text)
        rc |= 1 if code else 0

        log = b.log()
        lines = app_lines(log)
        with open(os.path.join(out, "app.log"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        print("--- engine")
        for line in [l for l in lines if l.startswith(("AUDIO alsa", "LOAD", "FRAME run"))][-3:]:
            print(line)
        load = [l for l in lines if l.startswith("LOAD ")]
        if not load:
            print("no LOAD line")
            rc = 1
        else:
            fields = dict(w.split("=", 1) for w in load[-1].split() if "=" in w)
            xruns, overruns = fields.get("xruns", "?"), fields.get("overruns", "?")
            print("xruns=%s overruns=%s LOAD p95=%s cycles/block (qemu timing: relative only)"
                  % (xruns, overruns, fields.get("p95", "?")))
            if xruns != "0":
                print("xruns: FAILED")
                rc = 1
            if overruns not in ("0", "?"):
                print("note: %s engine overruns (qemu timing, not gated)" % overruns)
        if not tone and any(l.startswith("SAMPLE ") for l in lines):
            print("sample errors:\n" + "\n".join(l for l in lines if l.startswith("SAMPLE ")))
            rc = 1
        print("--- screens and log: %s" % out)
        print("PASS" if rc == 0 else "FAIL")
        return rc
    finally:
        if not keep:
            b.stop()


if __name__ == "__main__":
    sys.exit(main())
