# STATE — machine-readable working memory for the closeout loop (v2)
# Update EVERY turn. A fresh session must be able to resume from THIS file alone.
# v1 history (full turn log 2026-10-03..2026-10-05l): archive/ralph-v1/STATE.md
# Patch discipline inherited: ONE patch per region, read_file verify after
# (multi-patch batches mangled v1 twice).

phase: P7-closeout
milestone: 6  # keep 6: gate.sh keys build/test/boot stages off milestone >= 3; lowering it silently guts the gate
updated: 2026-10-06T08:40
policy: strict-close  # FINAL-DEFAULT never closes an OQ; only cited measurement does (docs/GOAL.txt)

## LEDGER (statuses mirror docs/OPEN-QUESTIONS.md; that file is the record of
## resolution evidence — this block is the fast index. Update BOTH or neither.)
ledger:
  closed:
    - "OQ-001 .cob offsets = N not N+1"
    - "OQ-002 FLIC codec (both vendor videos, golden-pinned)"
    - "OQ-007 text encodings CP437"
    - "OQ-008 loader model usable for control flow (imagebase 0)"
    - "OQ-009 AI data side (21 raceNN.dip parameter sets)"
    - "OQ-011 POINTER LAW: runtime_u32 = P0 + payload_file_offset(target); P0 = B - H per-run; guest linear == physical; obj0 code [0x14bb0,0x82bb0)@0x1d4000, obj1 data [0x82bb0,0x8cc83)@0x242000 (battery scripts/r1_pointer_law.py 12/12 slots, gate 3q)"
    - "OQ-017 vendor .fnt codec + wired into UI"
  open:
    - "OQ-010 combat application formula — R1 frontier (planet-field semantics path; see NEXT ACTION)"
    - "OQ-003 .gam full record map — joint with OQ-010 (planet records joined 151/151 @ stride 123; field semantics open)"
    - "OQ-021 end-ctrl threshold: comment 'over half' vs prose 'two-thirds' — needs code-side constant"
    - "OQ-020 ability charge days (%d in vendor text, no data file) — R1: read the constant in code"
    - "OQ-005 .shp pixel codec — static route exhausted (6 angles, docs/REFUTED-ROUTES.md); needs exe shape loader via live image"
    - "OQ-006 headerless sample rate — needs exe audio-init constant"
    - "OQ-004 which tables the exe loads + .tsv grammar — needs open-file thunk via live image"
    - "OQ-012 mapgen (a) size options (b) pps distribution shape (c) type/position correlation (d) map extent"
    - "OQ-013 restree variant field0 semantics — needs research-screen code"
    - "OQ-014 planitem unknown fields (254 sentinel, 22/9, grids, item flag bits)"
    - "OQ-015 DA_ template selection order + full %token table"
    - "OQ-016 campaign per-turn constants (income, growth, build order, cadence, home placement)"
    - "OQ-019 ship design model (hull+gizmo inventory, cost hack, Orbital Docks)"
    - "OQ-018 soundfx.txt header pairs, VOC u16@25, theme selection mapping"

## WHAT IS IN HAND (tools + laws — a fresh session starts here, not from scratch)
- R1 save-state capture LIVE: scripts/r1_savestate.sh (boot -> autosave ZIP,
  full guest RAM) + scripts/r1_sav_scan.py (per-run base B, NEVER hard-code;
  member = physical + H, H=136 for dosbox-x 2025.02.01, re-derive per build).
- Deep capture LIVE: scripts/r1_deepcapture.sh (title -> New Game clicks
  318,293 then (511,67) cadence, needle-gated); campaign start proven
  byte-wise (scripts/r1_campaign_probe.py); planet records resume.gam<->RAM
  join 151/151, stride 123 (scripts/r1_planet_layout.py).
- Turn counter: u16 guest-phys 0x254e10 (idle-pinned 0, NEXTTURN-advanced,
  byte-verified). TURN-BOUNDARY law: planet records mutate only across
  counter-changing slot pairs; hot head-block = older-convention
  +0x35..0x3F (name-based +0x57..0x61), high-entropy u16s every turn.
- Restored image for Ghidra: work/ascend_restored.bin (built by
  scripts/r1_restore_sites.py; base-0 address space; validation: pointer
  runs >=8 hit Watcom starts 60% vs 15% control). Full analysis ghp5:
  1,144 functions (work/functions_full.tsv).
- Module attribution LIVE: scripts/attribution_scan.py + gate 3r,
  work/attribution.tsv (225 E1 refs, 62% on true fixup sites; flic 43,
  winmgr 24, gsystem 23, race 20, cosmos/batmode 10, planet 8).
- Static trust boundary (from v1 attempt 3): trust rel32 edges + rewritten-
  site immediates ONLY; batch-4-style blind decompile sweeps of E1 batches
  skew UI/allocators (4ae24 = operator-new).
- Gate: bash scripts/gate.sh is the single verification command; ~2-3 min;
  R1 attempts are NEVER gate stages (gate stays fast, side-effect-free).

## NEXT ACTION (exactly one)
PLANET-FIELD SEMANTICS (closes into OQ-010 + OQ-003). Do in THIS order —
(b) first is deliberate: it is the cheapest probe and its result tells you
whether (a) is worth a Ghidra cycle:
  (b) TARGETED CLICK-DIFF CAPTURE: in a deep-capture run, settle ONE planet
      (ownership/production via clicks) between two NEXTTURN clicks, take
      autosave slots bracketing each mutation, diff ONLY the touched 123-B
      record; decode changed u32s by the pointer law; correlate hot regions
      against extracted/ascend02 tables.
  (a) GHIDRA XREF PASS: planet-table stride-0x7b accesses (FUN_0004ae24
      family is allocator — start from work/attribution.tsv planet/cosmos
      entries instead) and which code READS u16 at intra-offsets 0x35..0x3f.
  (c) COUNTER-OFFSET TIMING CHECK: click NEXTTURN at a measured autosave
      phase, compare counter delta to expected turns.
Exit codes drive the loop (R1: 0=upgrade formulas + close OQs, 1=record one
line in this file, 2=fix harness). Do NOT re-run docs/REFUTED-ROUTES.md
routes. If (b) lands clean, update the field map in docs/re/r1-savestate.md
and docs/re/savegame.md with guest-phys addresses per field.

## KNOWN-ISSUES / PARKING LOT (operational; research negatives live in
## docs/REFUTED-ROUTES.md)
- DOSBOX RULE: never launch dosbox with stdout/stderr to a log unless you
  first confirmed it will not sit at an interactive prompt (EOF at a prompt =
  infinite "Are you sure to quit anyway now?" -> the 12 GB incident). Bound
  with timeout + head -c, or drive via pty. nosound=true.
- Kill dosbox ONLY by pkill -x dosbox-x (pkill -f once matched the gate
  shell's own cmdline and killed the gate mid-run).
- dosbox-x has NO gdb stub; -break-start exists but is DO-NOT-PILOT
  (docs/REFUTED-ROUTES.md).
- Ghidra MCP may be down: restart via scripts/ghidra_headless_up.sh
  (127.0.0.1:8089). After restart verify loaded memory is NONZERO before
  trusting results. API contract: docs/re/loader.md footer + v1 lessons
  (getReferencesFrom -> Reference[]; r.isCall()/r.isJump(), NOT isCALL()).
- gam_probe.py bare run (no --out) TRUNCATES hand-written savegame.md
  sections — always pass --out or read the script before running (hit
  2026-10-05k, restored via git checkout).
- restree separators are literal '^' (0x5E) bytes — normalise BEFORE
  comparing names (v1 miscount bug).
- radare2 unavailable on Debian 13; no LE-capable Python pkg cached; do not
  hunt for either. dosbox-x -help hangs: use strings on the binary.
- rsync NOT installed (cp -a). numpy absent host-wide; revenv PIL is the
  image host (~/tools/revenv/bin/python).

## DEFINITION-OF-DONE (v2 — strict)
gate.sh exit 0 AND ledger.open EMPTY: every OQ moved to closed with (1) its
evidence (Ghidra address / extracted-file offset / pointer-law guest-phys
measurement), (2) the rewrite code site upgraded to the original behaviour,
(3) docs/re/ spec updated, (4) a gate or unit-test assertion pinning it.
Items whose evidence genuinely cannot exist on this box are NOT closed
quietly — they get a BLOCKED.md entry with what machine/evidence would be
needed, and stay open. Under this policy "loop ends" may mean "you tell the
user the remaining items need X", not silent completion.
