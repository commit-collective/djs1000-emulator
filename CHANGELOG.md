# Changelog

Newest first. A release is a tagged commit.

## v0.5.0

The TORAIZ SP-16 runs in the emulator, with its own deck.

### Compatibility changes

- The repository is now `djs1000-emulator`. GitHub forwards the old name.

### SP-16

- Run SP-16 firmware 1.60 with `--unit sp16`, on a deck laid out like the unit.
- Its assignable outputs OUT 3-4, 5-6 and 7-8 can be heard, chosen on the status line.
- It syncs over Pro DJ Link.

### The deck

- PANEL, right of TOOLS (or F10), hides the side panel and narrows the window to the face. `--compact` starts that
  way, and the SP-16 always does unless `--panel` is given.

### Tools

- `tools/freesp16_smoke.py` and `tools/freesp16_bench.py` run freesp16's smoke test and device benches on either unit.

### Fixes

- A boot menu from the stick that stopped the app no longer ends the emulator after 25 seconds.
- A boot menu in one slot no longer stops the app in the others.
- With `DJS_FAST_BOOT`, a stick that shows a boot menu or starts its own app is no longer stopped after 3 minutes.

## v0.4.0

The emulator runs on a Mac through a Linux VM, and works with real players on the network through Deckbench.

### Compatibility changes

- The app keeps the host's clock by default, as the unit has one clock. `--pace` paces it to the sound card instead.
- A Deckbench started by an older launcher is not tracked. Stop it by hand once, or attach to it with `--bench-url`.

### Platforms

- On a Mac, the emulator runs in a Linux VM made from the Lima template, `scripts/lima/djs1000.yaml`.
- The launcher says when `systemd-timesyncd` and WSL both set WSL's clock, which made the app's tempo swing.

### Network and Deckbench

- The backend's network adapter and address are chosen in the Tools menu or with `--network-picker`.
- With a DJ adapter chosen, the launcher starts a Deckbench that watches the real players and the DJS.
- `--bench-url URL` uses a Deckbench that is already running, and `--no-bench` runs without one.
- The launcher's Deckbench takes a free port when a bench closed a moment ago still holds 8750.

### The deck

- The mouse wheel turns the selector anywhere on the deck but over another knob.
- The deck's mod switches and input watch use the stick's `djs1000-mods` folder, or its top for older patches.

### Fixes

- `start.py stop` ends only its own emulator, and no longer the test slots' ones.
- Each test slot has its own Deckbench ports.
- A first setup that failed can be run again without clearing the folder by hand.
- A slow start is waited for, up to three minutes, and a failed start is stopped.
- The deck stays open when the video encoder stops.
- Switching a mod on the deck keeps the settings file whole, CRLF line endings included.
- A script that stops reading the deck link no longer holds up the deck's screen and sound.

## v0.3.1

The app's sound keeps time with the deck, with no more skipped beats on WSL.

### Compatibility changes

- The app's sound is paced by the deck's sound card, not the host's clock. `--no-pace` brings back the old pacing.
- The deck keeps 250 ms of sound waiting by default (`--audio-buffer`, 150 before).

### The deck

- The status line's hint for the sound device counts the sound's cuts and late requests. The device's name turns
  orange once either has happened.
- `DJS_AUDIO_STATS=1` prints the sound's speeds every 10 seconds.

### Docs

- The docs keep to what runs the emulator. The hardware and power pages are gone, and the update file page is shorter.

### Fixes

- On WSL, the app no longer skips a beat about once a pattern, and its sound no longer lags behind the screen.

## v0.3.0

The deck records itself, and the videos made from it come in more sizes. Setup no longer overwrites an installation.

### Compatibility changes

- Setup refuses to replace an existing installation unless `--rebuild` is given, which backs up its firmware files
  and settings.

### The virtual deck

- REC (the first row of the TOOLS menu, or F7) records the window, its sound and a script of every command to
  `demo/captures`. `tools/reel.py` plays the script again on a fresh unit. It needs `ffmpeg`.
- A TOOLS menu (F8) and a status line with the master's level and the sound's timing. Over nothing, the line shows
  your last action as a line for a script, and a click copies it.
- A right click on a pad or a step key holds it down until it is clicked again. The pad velocity is set in the menu.
- `--audio-buffer MS` (default 150) and `--audio-block FRAMES` set the sound's buffering. Its cuts are counted.
- The deck has a window icon and a centred layout. The status line's buttons light up under the mouse.
- A DECKBENCH button beside TOOLS. Deckbench's actions are recorded with a REC and played back, and the INPUT SOURCE
  knob of LIVE SAMPLING picks the Deckbench deck the app hears.
- The unit's internal storage is bound in from `$DJS_EMMC`, or from `~/djs/emmc` when that holds a `PIONEER DJ
  SAMPLER` folder.

### Videos

- Resolutions (`--res hd`, `2k`, `4k`), keyable backgrounds (`--bg black`, `green`, `transparent`) and a clean video
  without text. A reel is made in the website's hero shape at 2K unless the episode says another.
- The video is H.264 at a higher quality for editing. The sound is also written whole beside it, at 48 kHz.
- A reel can replay a REC with its project and moving knobs, and show the mods panel. `--status` shows the deck's
  status line. A step can take `# before:` setup lines.

### Setup

- Setup extracts into a staging folder first, and stops on an extraction error instead of leaving an incomplete
  installation. Unsafe or unrecognised destinations are refused.

### Docs

- The README is about first use. `docs/running.md` covers scripting and platform details.
- Linux virtual machines on macOS are described as untested, not unsupported.

### Fixes

- Deckbench's address is given as 127.0.0.1, since from Windows to WSL `localhost` waited 2 seconds per connection.

## v0.2.0

The deck looks like the unit, and makes short videos of itself.

### The virtual deck

- The face looks like the unit (`--face real`, the default). `--face flat` is the first look.
- The bright last column and row along the right and bottom of the screen are gone.
- `--mute` plays nothing but still shows the MASTER / PHONES switch, for recordings.

### Videos

- `tools/reel.py` makes short videos of the emulator from an episode, a script of scenes. `--shape` picks 1080x1920
  for Reels and Shorts, 1920x1080, the website's picture, or the deck's window.
- `tools/reels/example.py` is the one to start from. Your own episodes go in `demo/episodes`, which git ignores.
- `--check` looks at an episode without a unit.
- A reel can record from the simulated decks (`INPUT = True`) for live sampling, with the headphones in its sound.
- A recording script can move the tempo slider and hold a key down (`slider`, `key`).

### Docs

- The README says where `autoexec.bin` goes to try the mods, and describes scripted use.

### Fixes

- On Windows, commands in a recording script no longer run again or late.

## v0.1.0

The first release: the DJS-1000's own app on a computer, with a virtual deck. MIDI, real players on a physical
network and macOS are not supported yet.

### The emulator

- The DJS-1000's app (firmware 1.22) runs unmodified under `qemu-arm` user mode, in the unit's root filesystem.
- Several emulators can run side by side.
- It needs no root. `proot` is the fallback, about three times slower to start the app.

### The virtual deck

- Draws the machine: the screen, every lamp and every control.
- Master and headphone outputs, and a recording device as the input.
- Lists the mods of the patch on the drive, with a switch for each.

### USB drive and mods

- A USB drive is a host folder. Samples load from it, and projects are saved, opened, deleted and rendered there.
- An `autoexec.bin` in that folder runs as it does on a stick, to try the mods before a real unit.
- The mods' settings are read from `djs1000-mods.txt` on the drive.

### Pro DJ Link

- Works with Deckbench's simulated decks, which `start.py` runs. The unit announces itself as player 1, so SYNC,
  MASTER and the mods that read the decks all work.

### Tools

- `tools/session.py` scripts the app.
