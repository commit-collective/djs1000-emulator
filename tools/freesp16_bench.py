# SPDX-License-Identifier: GPL-2.0-or-later
"""freesp16's device benches (its scripts/emulator-bench.sh), on this emulator.

freesp16 times its audio-path code with benches under tests/bench. Its own
script runs them as the device binary in another emulator (Apple silicon
only). This one does the same steps with this emulator's tools:

  1. the bench harness (tests/bench/harness/device) and the chosen bench
     sources are built for the unit, linked against an existing armel build
     of freesp16, with that build's own toolchain
  2. a slot's stick gets the boot menu and the harness as a folder app
     (apps/freesp16-bench, no data folder, the filter in FREESP16_BENCH), the
     menu set to start it
  3. the slot starts, the script waits for "BENCH DONE", the slot stops
  4. the BENCH lines are printed and saved

    python tools/freesp16_bench.py --freesp16 PATH --armel-build DIR [options] BENCH

  BENCH              a bench file stem (tests/bench/<stem>.cpp, <stem>*.cpp or bench_<stem>*.cpp: every BENCH
                     in them) or the name of one BENCH (the file that defines it, that bench only)
  --freesp16 PATH    the freesp16 checkout
  --armel-build DIR  its armel build, as the emulator's shell sees it (default: PATH/build/armel). Its
                     CMakeCache.txt gives the toolchain, the generator and cmake
  --toolchain FILE   another CMake toolchain file (when the build's own is only valid in a container)
  --bootmenu FILE    the boot menu's autoexec.bin (default: the one already on the slot's stick)
  --unit NAME        sp16 (default) or djs1000
  --slot N           the slot (default 47, port 7300 + N), with the same rules as freesp16_smoke.py
  --out DIR          where the report goes (default: demo/freesp16-bench, ignored by git)
  --timeout S        how long the benches may run (default 900)
  --distro NAME      the WSL distribution (default: $DJS_WSL_DISTRO, else WSL's default)

Exit 0 = every selected bench ran. The timings are qemu's: relative only, never
the unit's numbers (as freesp16's own script says).
"""
import functools
import glob
import os
import re
import shlex
import sys

print = functools.partial(print, flush=True)

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from freesp16_smoke import TAG, app_lines, flag, option, with_slot  # noqa: E402

APP = "freesp16-bench"   # the folder app's id on the stick
BENCH_RE = re.compile(r"^\s*BENCH\(\s*([A-Za-z0-9_]+)\s*,", re.M)


def sources_for(checkout, arg):
    """The bench sources (repository-relative) and the run-time filter, as scripts/emulator-bench.sh picks them."""
    bench = os.path.join(checkout, "tests", "bench")
    files = set()
    for pattern in (arg + ".cpp", arg + "*.cpp", "bench_" + arg + "*.cpp"):
        files.update(f for f in glob.glob(os.path.join(bench, pattern)) if os.path.isfile(f))
    flt = ""
    if not files:
        for root, _, names in os.walk(bench):
            if os.path.relpath(root, bench).replace("\\", "/").startswith("harness"):
                continue
            for n in names:
                if n.endswith(".cpp"):
                    f = os.path.join(root, n)
                    with open(f, encoding="utf-8", errors="replace") as h:
                        if arg in BENCH_RE.findall(h.read()):
                            files.add(f)
        flt = arg
    if not files:
        sys.exit("no bench file or BENCH named '%s' under tests/bench" % arg)
    found = False
    for f in files:
        with open(f, encoding="utf-8", errors="replace") as h:
            found = found or bool(BENCH_RE.search(h.read()))
    if not found:
        sys.exit("%s: define no BENCH() (Catch2-only benches run on the host: ctest --preset host-release -L bench)"
                 % arg)
    rel = sorted(os.path.relpath(f, checkout).replace("\\", "/") for f in files)
    return rel, flt


def run(b, checkout, arg, sources, flt, armel, toolchain, bootmenu, out, timeout):
    q = shlex.quote
    src = b.path(checkout)
    armel = armel or src + "/build/armel"
    bench_build = armel.rstrip("/") + "-bench"

    # 1. the harness, with the armel build's toolchain, generator and cmake
    print("bench sources: %s%s" % (" ".join(sources), " (filter %s)" % flt if flt else ""))
    code, text = b.sh(f"""
set -e
A={q(armel)}; C="$A/CMakeCache.txt"
[ -f "$C" ] && [ -f "$A/generated/ProjectIdentity.h" ] || {{ echo "no armel build at $A (its CMakeCache.txt)"; exit 1; }}
get() {{ sed -n "s/^$1:[A-Z]*=//p" "$C" | head -n 1; }}
CMAKE=$(get CMAKE_COMMAND); [ -x "$CMAKE" ] || CMAKE=cmake
TC={q(toolchain) if toolchain else '$(get CMAKE_TOOLCHAIN_FILE)'}
[ -f "$TC" ] || {{ echo "the toolchain file $TC is not here: give --toolchain FILE"; exit 1; }}
GEN=$(get CMAKE_GENERATOR); MAKE=$(get CMAKE_MAKE_PROGRAM)
"$CMAKE" -S {q(src)}/tests/bench/harness/device -B {q(bench_build)} -G "$GEN" ${{MAKE:+-DCMAKE_MAKE_PROGRAM="$MAKE"}} \\
  -DCMAKE_TOOLCHAIN_FILE="$TC" -DCMAKE_BUILD_TYPE=Release -DAPP_ARMEL_BUILD="$A" \\
  -DAPP_BENCH_SOURCES={q(";".join(sources))} > {q(bench_build)}.configure.log 2>&1 \\
  || {{ tail -n 20 {q(bench_build)}.configure.log; exit 1; }}
"$CMAKE" --build {q(bench_build)} > {q(bench_build)}.build.log 2>&1 || {{ grep -E "error" -A3 {q(bench_build)}.build.log | head -n 30; exit 1; }}
ls {q(bench_build)}/bin/*_device_bench
""")
    print(text)
    if code:
        print("the harness did not build")
        return 2
    binary = text.strip().splitlines()[-1]

    # 2. the stick: the harness as a folder app, started by the menu
    env = "env=FREESP16_BENCH=%s\\n" % flt if flt else ""
    code, text = b.sh(f"""
set -e
USB="$DJS_HOME/usb"; APPDIR="$USB/apps/{APP}"
mkdir -p "$USB"
{"cp " + q(b.path(bootmenu)) + ' "$USB/autoexec.bin"' if bootmenu else ""}
[ -f "$USB/autoexec.bin" ] || {{ echo "no boot menu on the stick: give --bootmenu FILE"; exit 1; }}
rm -rf "$APPDIR"; mkdir -p "$APPDIR"
cp {q(binary)} "$APPDIR/{APP}"; chmod 0755 "$APPDIR/{APP}"
printf 'name=freesp16 benches\\ndata=none\\n{env}' > "$APPDIR/app.ini"
printf 'default={APP}\\ntimeout=1\\nssh=0\\n' > "$USB/bootmenu.conf"
: > "$USB/bootmenu.log"
echo "stick ready: $USB"
""")
    print(text)
    if code:
        return 2

    # 3. run until BENCH DONE
    print("starting slot %d (%s, port %d)..." % (b.slot, b.unit, b.port))
    try:
        if not b.start():
            print("the slot did not start:\n" + b.emu.log_tail())
            return 2
        print("waiting for the benches (BENCH DONE, at most %d s)..." % timeout)
        found = b.wait_log([TAG + " BENCH DONE", "runner: " + APP + " exited"], timeout)
        if found is None:
            print("no BENCH DONE within %d s" % timeout)
    finally:
        b.stop()
        b.sh('rm -rf "$DJS_HOME/usb/apps/%s"' % APP)

    # 4. the report
    lines = [l for l in app_lines(b.log()) if l.startswith("BENCH")]
    report = os.path.join(out, arg.replace("/", "_") + ".txt")
    with open(report, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("--- device benches (emulator: relative timings only) - %s" % report)
    print("\n".join(lines) or "no BENCH line")
    done = [l for l in lines if l.startswith("BENCH DONE")]
    if not done or not re.match(r"BENCH DONE ran=[1-9][0-9]* over=[0-9]* failed=0", done[-1]):
        print("the benches did not finish")
        return 1
    return 0


def main():
    args = sys.argv[1:]
    if not args or flag(args, "-h") or flag(args, "--help"):
        print(__doc__)
        return 0
    checkout = option(args, "--freesp16")
    if not checkout:
        sys.exit("--freesp16 PATH: the freesp16 checkout")
    armel = option(args, "--armel-build")
    toolchain = option(args, "--toolchain")
    bootmenu = option(args, "--bootmenu")
    unit = option(args, "--unit", "sp16")
    slot = int(option(args, "--slot", "47"))
    out = os.path.abspath(option(args, "--out", os.path.join(REPO, "demo", "freesp16-bench")))
    timeout = int(option(args, "--timeout", "900"))
    distro = option(args, "--distro", os.environ.get("DJS_WSL_DISTRO"))
    if len(args) != 1 or args[0].startswith("-"):
        sys.exit("one BENCH (a bench file stem or a BENCH name); unknown arguments: %s" % " ".join(args))
    arg = args[0]
    if not re.fullmatch(r"[A-Za-z0-9_/-]+", arg) or ".." in arg or arg.startswith("/"):
        sys.exit("bench names contain only letters, digits, '_', '-', '/'")
    if unit not in ("sp16", "djs1000"):
        sys.exit("--unit sp16 or djs1000")
    if bootmenu and not os.path.isfile(bootmenu):
        sys.exit("no %s" % bootmenu)
    sources, flt = sources_for(checkout, arg)
    os.makedirs(out, exist_ok=True)
    return with_slot(unit, slot, distro,
                     lambda b: run(b, checkout, arg, sources, flt, armel, toolchain, bootmenu, out, timeout))


if __name__ == "__main__":
    sys.exit(main())
