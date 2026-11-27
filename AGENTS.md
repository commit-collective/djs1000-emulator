# djs1000-emulator: working rules

- This repo is public. Its docs and code comments stay high level: byte-level protocols are fine, but no firmware addresses,
  no Ghidra symbols (`FUN_...`) and no cipher details. Those are kept outside the repo.
- Firmware and anything unpacked from it never go in any repo. That includes the skin's pictures, the unit's factory samples and
  projects, and its manuals. The virtual deck's face is drawn here in code, not traced or copied from a photo or a Pioneer DJ
  picture. Tests and tools read the user's own firmware from `$DJS_HOME` and never copy it into the checkout. Do not commit
  pictures, samples or screenshots taken from the unit or its skin.
- `docs/` is for running, using and building the emulator. What is learned about the firmware itself (hardware, internals,
  the update's contents) goes in the private notes, not here.
- Media (videos, renders) is never committed. Reels are generated into the git-ignored `demo/` folder, and personal episodes
  stay in `demo/episodes`.
- Always commit completed changes locally on main. Ask before pushing, tagging or deploying, and never amend a pushed commit.
  Amending the latest commit is fine while it is not pushed and the change iterates on it.

## Make and verify changes

- Read the README, then only the relevant documents. Running and platform
  details are in `docs/running.md`, the agent-facing TCP client in
  `tools/session.py`, and architecture in `docs/emulation.md`.
- Keep the README a first-run guide. Put command catalogues and implementation
  detail in the relevant document. Do not describe untested platforms as either
  working or impossible. Distinguish main, the latest tag and the live site.
- Keep shared UI wording platform-neutral. Host and VM setup details belong
  in platform documentation, not adapter labels or general instructions.
- Before launching or stopping anything, check for an active test or recording
  session. Do not overlap them or stop processes owned by another session.
  Use `python start.py stop`, never a blanket process kill.
- Use `python start.py --no-deck` for scripted work. Changing the virtual deck
  calls for `python tools/deck_selftest.py`. Backend changes call for the
  relevant scripted checks and regression. Doc-only work does not require
  starting the firmware. Say what was and was not validated on hardware.
- Keep setup destructive operations inside a resolved, dedicated workspace.
  Preserve existing settings and backups. Exercise rejection paths without
  using real firmware before trying an extraction.
  Run `python3 tools/test_setup.py` in Linux or WSL after setup changes.
- Commit subjects start with an action verb and stay under 50 characters.
  A body is optional, otherwise use a blank line and lines under 72 characters.
  No semicolons in prose, emojis or attribution. Omit routine check boilerplate,
  but name CI or test changes when they are the purpose of the commit.
- The hero picture of the README and the website (`public/djs1000/emulator/hero.png` in the website repo) is made by
  `tools/hero_scene.py` then `tools/hero.py`. When the look of the deck changes, run both and commit the new picture in the
  website repo, not here. The README links to it there.

## The changelog

`CHANGELOG.md` tells someone upgrading from the last release what changed for them, not the history of the work.

- The file opens with `# Changelog` and the line "Newest first. A release is a tagged commit."
- What is not released yet goes under `## Not yet released`. A release renames that heading to `## vX.Y.Z`.
- An entry opens with one or two plain sentences: what the release brings, for the person who installs it.
- Its items go under `###` headings: `Compatibility changes` first when there are any, then the repository's own
  areas, then `Fixes` last.
- One short line per item, in plain words for the person who uses it: what changed, not how it was found, why it
  broke or how it was tested. No internal formats or maintainer tooling. A compatibility note may take a second
  sentence.
- A feature new in the coming release is described as it works now. A fix to it, or a change of it, before the
  release amends that feature's line. It never gets a line of its own.
- A fix line is only for a bug that was in a published release.
- A behaviour that changes from the last release goes under `Compatibility changes`.
- Nothing that is not checked yet ("untried", "pending", "experimental") goes in unless the owner wants it said.
