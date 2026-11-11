# DRAFT README.md for the public repo (t371; lands at repo root in t373)

<!-- t371 working note: this is the public-tree README draft per the phase-8
     queue row. The in-repo README.md is NOT replaced here — t373 swaps
     README + LICENSE + NOTICE + .gitignore atomically. Placeholders marked
     <TBD-...> resolve at t372/t373 (license text, repo name, contact). -->

---

# Ascendancy — a native rewrite

A C++17 + SDL2/SDL2_mixer re-implementation of the single-player game of
**Ascendancy** (The Logic Factory, 1995), written from scratch by
reverse-engineering the original distribution's **data formats and game
tables**. No original machine code is used. The engine reads the original
data files — which you supply from your own copy of the game (§ Supply your
own data); this repository ships **no vendor data**.

## What is here

    rewrite/          the engine: src/formats (file parsers), src/game
                      (simulation), src/ui (SDL2), tests
    docs/re/          the evidence: every format and system law this project
                      claims, cited to a file offset, an address, or a
                      measured measurement run
    docs/             control plane, playthrough record, open questions
    scripts/          verification gate + the RE probe/capture tooling
    artifacts/        provenance notes for reproducible RE artifacts
    tools/            small C helpers used by the gate

## The evidence rule

Every authenticity claim in this repository traces to a citation: a byte
offset in a vendor data file, an address in the original executable, or a
reproducible probe (`scripts/`). Where the original's rule could **not** be
recovered, we say so instead of inventing one — `docs/OPEN-QUESTIONS.md`
lists every documented default and every open item. A plausible guess never
closes a question; only cited measurement does.

## Build

    cmake -S rewrite -B build
    cmake --build build -j4
    ./build/run_tests            # 226 tests, no display required

Dependencies: a C++17 compiler, SDL2 (≥2.32), SDL2_mixer (≥2.8).
Linux: `apt install libsdl2-dev libsdl2-mixer-dev`. macOS:
`brew install sdl2 sdl2_mixer`. Windows: vcpkg manifest route <TBD-t373:
verified vcpkg ports matrix>.

## Run

    ./build/ascendancy --data DIR --campaign 600 --seed 2024   # headless to victory
    ./build/ascendancy --data DIR --ui                          # interactive window

`--data DIR` is the directory containing `extracted/` (§ below; default:
repo root). UI: click NEXT TURN or Enter/Space; click a star to select; ESC
quits. More flags: `--autoplay`, `--audio`, `--mute`, `--species N`,
`--flic`, `--intro N`, `--fonts` — see `--help`.

## Supply your own data

This project ships no copyrighted game content. To play:

1. Obtain your own copy of MS-DOS *Ascendancy* (1995).
2. Point `scripts/cob.py` at the archives to unpack the data tables:
   `python3 scripts/cob.py extract ascend00.cob extracted/ascend00`
   (ascend01/02 importer: <TBD-t373 — extraction of the compressed side is
   not yet a one-command flow; until then this README states the limitation
   rather than pretending otherwise>.)
3. Run with `--data` pointing at the result.

## Verification

    bash scripts/gate.sh

One command: format probes, unit tests, headless victory smoke, Xvfb UI
boot, injected-input click test, audio load. Recorded outputs of real runs
are in `docs/PLAYTHROUGH.md`.

## Status of the original game, and credit

**Ascendancy** was developed by **The Logic Factory** — founded 1993 by
**Todd Templeman** and Jason Templeman — and released in 1995 (publishers:
Virgin Interactive / Broderbund / Softgold). The company's website was
discontinued in June 2014. The Internet Archive's item for the game states:
"Ascendancy is currently abandonware"
(<https://archive.org/details/msdos_ascendancy>). Abandonware is a
distribution norm, not a license — which is one reason this repository
redistributes nothing from the original release.

**License-grant offer.** The engine code in this repository is licensed
GPL-3.0-or-later (see LICENSE). To Todd Templeman, Jason Templeman, and any
successor or rights-holder of The Logic Factory: we additionally offer, at
your option and in writing on request, an unrestricted license to this
codebase including commercial use, so that an official re-release would
never be encumbered by our copyleft. This offer changes nothing for anyone
else: everyone else's terms remain GPL-3.0-or-later. Contact:
contact@motesandbeams.com (Todd Templeman — per his company about page,
co-founder of The Logic Factory; fetched 2026-11-11, quoted in
docs/re/packaging.md S8) or via this repository's issue tracker.
