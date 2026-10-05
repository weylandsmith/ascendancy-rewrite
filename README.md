# Ascendancy — native rewrite

A C++17 + SDL2/SDL2_mixer re-implementation of the single-player game of
**Ascendancy** (Logic Factory, 1995), built from reverse-engineering the
original distribution files in `game/` — no original code is used, only
data formats and game tables read from the extracted originals.

## Build

    cmake -S rewrite -B rewrite/build && cmake --build rewrite/build -j4

Requires: libsdl2-dev (2.32), libsdl2-mixer-dev (2.8), libsdl2-ttf-dev,
a C++17 compiler. Tests: `./rewrite/build/run_tests` (no display needed).

## Run

The binary reads the ORIGINAL extracted data from `extracted/` (manifests,
star/tech/economy tables, race diplomacy files, audio samples) — never
generated stand-ins. It plays a seeded, deterministic campaign to a victory
condition.

    ./rewrite/build/ascendancy --campaign 600 --seed 2024   # headless to victory
    xvfb-run -a ./rewrite/build/ascendancy --ui --campaign 3 --autoplay
    ./rewrite/build/ascendancy --ui                          # interactive window
    SDL_AUDIODRIVER=dummy ./rewrite/build/ascendancy --ui --audio --mute

Flags: `--data DIR` data root (default: repo root) · `--headless` dummy
video driver · `--ui` window (cosmos map, NEXT TURN, event pane) ·
`--autoplay` 250 ms turns · `--audio` load + play all 86 vendor SFX and
theme00 music · `--mute` load but silent · `--campaign N`/`--seed S` ·
`--species N` play as species specnum N (0..20 — each species' SA_ special
ability fires every ~30 turns; default human = no ability) ·
`--flic` decode both vendor intro videos end-to-end (codec report) ·
`--intro N` play the vendor intro (intro65a.flc) at real speed, N-frame cap ·
`--fonts` load all vendor .fnt faces with ink census (OQ-017 closed: 1 byte
per pixel, 0xFF background, 0xF3 solid ink / 0xF0-FE anti-alias ramp).
In the UI: click NEXT TURN or Enter/Space advances a turn, clicking a star
selects it (status line), ESC quits.

## Verification

    bash scripts/gate.sh    # checksums on game/, format probes, tests,
                            # headless victory smoke, Xvfb UI boot,
                            # injected-input click, audio load — all in one

Recorded runs (headless victory, Xvfb victory, injected-input UI turn,
audio boot) are in `docs/PLAYTHROUGH.md`, including exact commands and
outputs.

## What is authentic vs. what is a documented default

AUTHENTIC (cited to extracted-file offsets or Ghidra addresses in
`docs/re/*.md`, and asserted by the gate/unit tests): the .cob archive
format; the seven .bin tables; star/planet statistics, research tree,
gizmos, planetary items, species data, diplomacy files, star names,
map-grid and lane rules, victory-condition files (end-*.txt), the 21 species
special-ability effects and their charged/passive split (help.txt L1713-2511,
docs/re/abilities.md), sound manifests and the vendor .voc sample container,
the vendor FLC intro videos (both decode frame-exact to hashes + a visually
checked PNG; docs/re/flc.md), CP437 text handling.

DOCUMENTED DEFAULTS (the original's exact rule is not recoverable from
static data; each is listed in `docs/OPEN-QUESTIONS.md` and cited from
code back to docs): campaign combat arithmetic (OQ-010); AI build/expansion
orderings (OQ-015/016); ability charge time — 30 turns for all 14 charged
species abilities (OQ-020); sample rate of headerless audio files — 22050 Hz
mono (OQ-006); UI font — Liberation Sans stands in for the vendor .fnt
codec (OQ-017); window colours — BACKGRNDCOLOR indices have no documented
palette mapping, so a deuteranopia/protanopia-verified palette is used.

OPEN, NOT FAKE-IMPLEMENTED (stated, not silently stubbed): original sprite
pixel codec (OQ-005 — the map draws documented circles instead of invented
art), save/load (OQ-003), the exe's runtime data base (R1 in
`docs/BLOCKED.md`). All five vendor end-*.txt victory conditions ARE now
evaluated (end-capt and end-unit under documented readings — turnloop.md §1;
their exact vendor thresholds/priority remain R1).

## Layout

    rewrite/src/formats/   file parsers (cob, bin tables, voc, flic) — no SDL
    rewrite/src/game/      simulation (mapgen, economy, research, campaign)
    rewrite/src/ui/        SDL2 window, layout math, SDL2_mixer engine
    docs/re/               every reverse-engineered format/system spec
    scripts/gate.sh        the one verification command
    tools/xsend.c          synthetic-X-input helper used by the gate
