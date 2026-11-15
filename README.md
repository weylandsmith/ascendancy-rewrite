# Ascendancy — a native rewrite

This is an AI-facilitated re-implementation of Ascendancy, a 1995 space 4x 
game by The Logic Factory. It's a wonderful game that was, sadly, hampered
by poor AI in the computer opponents, and tedious micro-management in the
midgame. This rewrite aims to create a faithful base upon which improvements
can be layered. This is the engine only, you'll need to seperately obtain a 
copy of the original game in order to play it.

As far as I'm aware the original game is no longer offered for sale anywhere,
but you should try to buy the game legitimately if you can (I bought a retail
boxed copy in the 1990s, and still have it), or support the creators in other 
ways. Todd Templeman has a new project at motesandbeams.com, and he also has 
a few published books out for sale. I'll add links for the other original 
creators as I find them.

Begin AI-generated content:

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
`brew install sdl2 sdl2_mixer`. Windows: the same libraries via vcpkg;
the port matrix for this repo has not been CI-verified yet, so treat the
Windows build as expected-to-work, not tested. (UI text renders from the
vendor .fnt faces — no SDL2_ttf; the codec is docs/re/fnt.md.)

## Run

    ./build/ascendancy --data DIR --campaign 600 --seed 2024   # headless to victory
    ./build/ascendancy --data DIR --ui                          # interactive window

`--data DIR` is the directory containing `extracted/` (§ below; default:
repo root). The binary reads the ORIGINAL extracted data (manifests,
star/tech/economy tables, race diplomacy files, audio samples) — never
generated stand-ins — and plays a seeded, deterministic campaign to a
victory condition. UI: click NEXT TURN or Enter/Space; click a star to
select; ESC quits. On the `--ui` path audio is ON by default (t395 — the
startup prints an `audio: driver=... sfx=N tunes=N vol=N` line, or a
`degraded: silent` line naming what it could not open; `--no-audio` opts
out). More flags: `--autoplay`, `--mute`,
`--species N`, `--flic`, `--intro N`, `--fonts` — see `--help`.

## Supply your own data

This project ships no copyrighted game content. To play:

1. Obtain your own copy of MS-DOS *Ascendancy* (1995).
2. Unpack the three archives with the included importer:

       python3 scripts/cob.py extract ascend00.cob extracted/ascend00
       python3 scripts/cob.py extract ascend01.cob extracted/ascend01
       python3 scripts/cob.py extract ascend02.cob extracted/ascend02

   (Verified end-to-end 2026-11-11 against a reference tree: 54 / 328 / 89
   files, `diff -r` clean — including the compressed entries on the
   ascend01/02 side. `docs/re/datafiles.md` is the container spec.)
3. Run with `--data` pointing at the result, or set `ASCENDANCY_DATA=<dir
   containing the .cob archives and ascend.exe>` and run
   `bash scripts/gate.sh --portable`, which performs steps 2–3 for you.

## Verification

    bash scripts/gate.sh              # full gate (needs the vendor data above)
    bash scripts/gate.sh --portable   # on a clone without vendor data: skips
                                      # vendor stages with notes, exits 0

One command: format probes, unit tests, headless victory smoke, Xvfb UI
boot, injected-input click test, audio load. Recorded outputs of real runs
(headless victory, Xvfb victory, injected-input UI turn, audio boot — exact
commands and outputs) are in `docs/PLAYTHROUGH.md`.

## What is authentic vs. what is a documented default

AUTHENTIC (cited to extracted-file offsets or Ghidra addresses in
`docs/re/*.md`, and asserted by the gate/unit tests): the .cob archive
format; the seven .bin tables; star/planet statistics, research tree,
gizmos, planetary items, species data, diplomacy files, star names,
map-grid and lane rules, victory-condition files (end-*.txt), the 21 species
special-ability effects and their charged/passive split (help.txt
L1713-2511, docs/re/abilities.md), sound manifests and the vendor .voc
sample container, the vendor FLC intro videos (both decode frame-exact to
hashes + a visually checked PNG; docs/re/flc.md), CP437 text handling, and
the combat/relation/end-game laws measured from live captures
(`docs/re/combat.md`, `docs/re/diplomacy.md`, `docs/re/score.md`).

DOCUMENTED DEFAULTS (kept where the original's rule could not be recovered
or was dispositioned by the project's standing decisions; each row and its
disposition is in `docs/OPEN-QUESTIONS.md`): window colours —
BACKGRNDCOLOR indices have no documented palette mapping, so a
deuteranopia/protanopia-verified palette is used; mono playback of
headerless vendor audio (the 22050 Hz device rate is measured, the channel
count is not stated by any vendor field). The UI font is NOT a default: the
vendor smfont/bigfont .fnt faces are decoded and rendered per
docs/re/fnt.md.

OPEN AS OF 2026-11-11 (stated, not silently stubbed — 2 of 26 ledger rows):
OQ-016 (AI build/expansion orderings: eight capture routes cited dead,
residues dispositioned, row awaiting the project owner's final ruling) and
OQ-019 (per-ship design model and order-entry micro-law: partially closed by
live-witness measurement, residues annotated and open). The map draws
documented circles instead of invented art — the sprite pixel codec's
remaining record class was closed by owner ruling; nothing here is faked.

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
