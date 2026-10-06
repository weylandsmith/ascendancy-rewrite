# Ascendancy Reverse-Engineering & Reimplementation — MASTER PLAN

Objective: re-implement the complete single-player game of Ascendancy
(Logic Factory, 1995, DOS/Watcom) natively in C++17 + SDL2/SDL2_mixer,
driven entirely from reverse-engineered evidence in this repository.

Authoritative inputs (in this folder):
  game/           original shipped files (DO NOT MODIFY — read-only ground truth)
  extracted/      decoded from the .cob archives (regenerate: scripts/cob.py)
  docs/           all RE findings; every claim cites its evidence
  rewrite/        the C++17/SDL2 reimplementation (CMake project)
  scripts/        tooling (cob.py, gate.sh, ghidra_headless_up.sh, ...)

--------------------------------------------------------------------------
EVIDENCE RULES (violate none — the whole value of this repo is trust)
--------------------------------------------------------------------------
1. Every constant, formula, or table entry copied into rewrite/ MUST cite a
   docs/ file, which itself cites its source: a Ghidra address
   (ascend.exe:OFFSET), an extracted data file + record offset, or a quoted
   passage from the manual.
2. If two sources conflict, record BOTH in docs/OPEN-QUESTIONS.md and pick
   the one with better evidence; note the reasoning.
3. Never invent formats. Unknown bytes are "unknown" until shown otherwise
   by cross-referencing binary use (xrefs) or data correlation.
4. game/ must stay byte-identical (gate checks checksums).

--------------------------------------------------------------------------
KNOWN FACTS (verified 2026-10-03, see docs/FINDINGS.md for detail)
--------------------------------------------------------------------------
- ascend.exe (587 KB) = DOS4GW (Watcom) stub+client, 32-bit LE, Watcom RT
  1988-1993 strings present. dos4gw.exe is the extender.
- .cob archives: u32 count | NUL-term names zero-padded to 4B | (N+1) u32
  LE offsets | concatenated blobs. scripts/cob.py decodes all three files
  cleanly; NO compression. 468 files extracted.
- ascend00 = plaintext (.txt/.dip): help, help-gizmos, species diplomacy
  text, music.txt, planitem.txt etc.
- ascend01 = data\*.shp shape/sprite sets + misc; ascend02 = paired
  name.bin + name.tsv tables (battle, beginnew, galactic, planet, ship,
  species, tutintro) + data\ subdir. The .tsv are the SAME tables as
  .bin in text form — cross-check both.
- logic.flc = Autodesk Animator FLIC (magic 0xAF12... header starts
  with size+magic little-endian: first u32=3835618=file size, magic
  0xAF12 at +4 — VERIFY before assuming).
- resume.gam = 81 KB savegame, plain u32 LE fields at least in part
  (0x07, 0x02, 0x04, 0x03... readable at head).
- Toolchain installed: Ghidra 12.1.4 (~/tools/ghidra, sha256 verified),
  GhidraMCP headless+bridge (~/tools/ghidra-mcp; bridge registered in
  Hermes as mcp_servers.ghidra), gcc 14, cmake 3.31, SDL2 + mixer/image/ttf,
  dosbox 0.74, dosbox-x 2025.02, Xvfb, imagemagick, radare2 NO (not in
  Debian 13 repos — use binutils+capstone+Ghidra instead), python venv
  ~/tools/revenv (pyelftools, capstone, pillow, Pillow, mcp).

--------------------------------------------------------------------------
PHASES (execute top to bottom; do NOT skip ahead past missing data)
--------------------------------------------------------------------------
P0  Environment verify          — scripts/env_check.sh passes.            [done]
P1  Data formats                — every extracted format has a docs/ spec
      1a .cob (done — docs/FINDINGS.md)
      1b .tsv/.bin table pair: column layout, types, cross-mapping
      1c .shp sprite sets (format + sample renders to PNG in docs/assets/)
      1d .gam save format (use resume.gam; correlate with .bin tables)
      1e FLIC video + .bam/.dig audio inventory; music.txt mapping
      1f .dip, .txt text encodings (CP437->UTF-8 conversion table)
P2  Binary RE (Ghidra)          — import ascend.exe; analyze; name &
      document by SUBSYSTEM (not function-by-function): startup/init,
      main loop, map/planet gen, economy, research, production/ships,
      combat, AI (per-race), diplomacy, save/load, UI/render primitives,
      input, audio. Deliverable per subsystem: docs/re/<name>.md with
      pseudocode-level spec + constants table + addresses.
      Ghidra: headless server on 127.0.0.1:8089 (scripts/ghidra_headless_up.sh).
      Watcom RE32 caveat: Ghidra parses with 'x86:LE:32:default' +
      watcom calling convention conventions; overlay/flat model at
      imagebase; verify function boundaries via Watcom RTTI/strings.
P3  Engine skeleton (rewrite/)  — CMake C++17+SDL2; importer lib that reads
      extracted/ (verified vs docs specs); headless sim core; deterministic
      seeded map-gen matching original for the same seed (test vs
      galaxy data from a fresh save created in dosbox).
P4  Systems port                — in order: game setup/races -> turn
      economy -> research/tech tree -> planetary dev -> ship design &
      movement -> combat resolution -> AI -> diplomacy -> victory.
      Each: unit tests + a golden comparison against original
      behaviour where feasible (savegame N->N+1 diffs from dosbox).
P5  UI & media                  — strategic map rendering, planet view,
      sprite import, palette, text, dialogs, sound (SDL2_mixer);
      screenshot comparisons vs dosbox captures in docs/assets/.
P6  Integration & completeness  — full campaign playable to victory;
      open-questions list empty or marked cosmetic-only; README with build
      + play instructions.

--------------------------------------------------------------------------
VERIFICATION (what the goal judge + gate use)
--------------------------------------------------------------------------
Gate: bash scripts/gate.sh  (fast, deterministic, see script for stages:
checksums always; extractor always; rewrite build+tests once
STATE.md milestone >= P3).
Playtest harness (P3+): dosbox-x headless (Xvfb) runs the ORIGINAL for
reference captures; rewrite runs headless smoke tests; imagemagick compare
for UI stages.

--------------------------------------------------------------------------
LOOP OPERATING PROCEDURE (for the autonomous /goal loop)
--------------------------------------------------------------------------
Every turn:
 1. Read docs/STATE.md (phase, milestone, next-actions, known-issues).
 2. Pick the SINGLE next action from the first unfinished item (do not
    reorder phases unless STATE.md says why).
 3. Do the work. Keep turns productive: if an action needs >30 min of
    Ghidra analysis, checkpoint partial findings into docs/ before ending.
 4. Update docs/STATE.md: what changed, current phase/milestone, exact next
    action, anything learned that a fresh session must know.
 5. git add -A && git commit -m "<phase>: <action>" (small, frequent).
 6. Run bash scripts/gate.sh; fix failures before ending the turn.
Never: modify game/; invent data; mark STATE.md items done without
evidence; leave the tree broken (gate failing) at end of turn.
Option C (decided 2026-10-04, docs/BLOCKED.md; cadence window ABOLISHED
2026-10-05 by user): R1 runs via save states (scripts/r1_savestate.sh,
docs/re/r1-savestate.md) with NO rate limit; per-run safety invariants are
mandatory (scratch copy, -time-limit, pkill -x, bounded output). A negative
(exit 1) is recorded in one line, never retried in-turn; exit 0 means the
base was derived; pointer law CLOSED 2026-10-05i so formula upgrades are
unlocked (docs/re/r1-savestate.md); exit 2 is a
harness bug, not a research result.
When ALL P6 items are done and gate passes: state EXPLICITLY that the
goal contract is complete and stop.
