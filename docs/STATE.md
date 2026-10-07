# STATE — machine-readable working memory for the closeout loop (v2)
# Update EVERY turn. A fresh session must be able to resume from THIS file alone.
# v1 history (full turn log 2026-10-03..2026-10-05l): archive/ralph-v1/STATE.md
# Patch discipline inherited: ONE patch per region, read_file verify after
# (multi-patch batches mangled v1 twice).

phase: P7-closeout
milestone: 6  # keep 6: gate.sh keys build/test/boot stages off milestone >= 3; lowering it silently guts the gate
updated: 2026-10-06T22:40
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
    - "OQ-013 RESTREE LIVE TABLE LAW: in play = 66 main rows only (loader
      FUN_00046870 row loop bounded by count line 66; variants 0/40 in 27 slots
      x 13 captures); record = stride 75 (count u16@+0, name 60B@+2 ^->space,
      runtime cost u16@+62, prereq bytes@+64 (0FF term, <=5), child slots@+69..72
      (second pass, 66/66 exact), field0 u8@+76); MEASURED COST LAW runtime =
      file_cost x (2row-20) for row>10 clamp 65000 (instructions 0x4691d..0x46a15,
      reproduced 66/66; row65 300->33000); resume.gam block byte-identical to
      fresh RAM (static data); rewrite upgraded (Tech::runtimeCost,
      includeVariants default false) + 2 pinned tests; docs/re/research.md 6"
  open:
    - "OQ-010 combat application formula — R1 frontier; static half bounded
      2026-10-06 (no disp32 orbit/table reads; shape tie FUN_00025604), path =
      click-diff capture (STATE NEXT ACTION)"
    - "OQ-003 .gam full record map — joint with OQ-010 (planet records joined
      151/151 @ stride 123; STAR TABLE + ORBIT laws closed 2026-10-06 give the
      neighbourhood map: star stride 96, planet ptrs name+0x2A, orbit pair
      planet-name+0x57/+0x5f; field semantics open)"
    - "OQ-021 end-ctrl threshold: comment 'over half' vs prose 'two-thirds' — needs code-side constant"
    - "OQ-020 ability charge days (%d in vendor text, no data file) — R1: read the constant in code"
    - "OQ-005 .shp pixel codec — static route exhausted (6 angles, docs/REFUTED-ROUTES.md); needs exe shape loader via live image"
    - "OQ-006 headerless sample rate — needs exe audio-init constant"
    - "OQ-004 which tables the exe loads + .tsv grammar — needs open-file thunk via live image"
    - "OQ-012 mapgen: ONLY (a) size options open; (b) closed 06o (pps U{1..5}),
      (c) closed 06p/06q (shell position law; rewrite upgraded + tested),
      (d) closed 06k (sphere extent, refined by (c))"
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
- STAR TABLE LAW CLOSED 2026-10-06 (battery scripts/r1_star_table.py, gate 3s,
  green 259/259 slots x 13 captures): stride-96 name-anchored star records;
  idx u32 @name-0x18; pos f32[3] @name-0x14; planet ptrs u32[5] @name+0x2A
  targeting planet-NAME-0x24, LIVE iff name prefix matches, single-owner law;
  sub-pool 0x258xxx stride 39 permutation. ORBIT LAW: centered radius constant
  (0 violations 277 planets); per-planet constant dtheta/turn applied by turn
  loop (sample r=544 -> -13.52 deg); unassigned planets subset of static.
  Full field table docs/re/r1-savestate.md "STAR TABLE + ORBIT LAWS". Census
  tool scripts/r1_record_census.py (per-record per-offset planet churn).
- Restored image for Ghidra: work/ascend_restored.bin (built by
  scripts/r1_restore_sites.py; base-0 address space; validation: pointer
  runs >=8 hit Watcom starts 60% vs 15% control). Full analysis ghp5:
  1,144 functions (work/functions_full.tsv).
- Module attribution LIVE: scripts/attribution_scan.py + gate 3r,
  work/attribution.tsv (225 E1 refs, 62% on true fixup sites; flic 43,
  winmgr 24, gsystem 23, race 20, cosmos/batmode 10, planet 8).
- Restree law tool LIVE: scripts/r1_restree_law.py (anchor on row-0 name, walk
  stride 75, no hard-coded address; exit 0 only if the cost law cross-checks
  >=90% of located rows). Green on every banked capture (66/66 rows, 27 slots).
- DATA-FILE STRING -> LOADER ROUTE (proven on OQ-013, 2026-10-06r; the general
  key to the "needs code path" items): the payload holds literal data-file
  names next to their module's debug path (e.g. 'restree.txt' at payload
  offset 0x85014 beside '..\research.cpp'). Tool scripts/r1_datafile_strings.py
  scans guest RAM for u32 == P0 + payload_offset and prints the Ghidra address
  d = (member_off - H) - P0 of every referrer (never hard-code bases). Census
  06r (r1deep-20261006-123049, 20 slots): ALL 23 .txt names referenced --
  batfx 0x1ad97, help 11 refs (0x1bee3...), music 0x212d5, cosmos 0x2140e,
  static 0x218c1, names 0x22894, history 0x2b4d5, end-{xtnc,dest,capt,unit,
  ctrl} 0x2c04e/0x2c065/0x2c07c/0x2c093/0x2c0aa, gwshare 0x31563, tutindex
  0x35a7b, planitem 0x37fcd, restree 0x468d3 (== the independently-found
  loader site -- self-validating), reswin 0x4712b+0x47579, gizmos 0x49081,
  soundfx 0x4ff42, newgame 0x5212c, gizhelp 0x56105, planhelp 0x561f0,
  windows 0x575c3. .shp names (data\planets.shp 0x83d2b..., DATA\planets.shp
  0x85694, 02d/resring/suns/smhome) have ZERO direct u32 referrers -- shape
  libs are not opened via an image-absolute string pointer; the open-file
  thunk is FUN_000206c0 (what FUN_00046870 calls; enumerating ITS callers is
  the sanctioned next step for OQ-004/OQ-005). Two verified caveats: (1) at
  such a site the RESTORED image keeps the file/obj-relative immediate
  (ascend_restored.bin @0x468d3 = 0x2464), so Ghidra's printed
  'MOV EAX,0x2464' is not an address -- the live RAM imm there is 0x244464 =
  P0+0x85014, and the referrer address comes from the RAM scan, not from
  reading the image; (2) not every referrer address lands inside a Ghidra
  function (end-ctrl.txt's 0x2c0aa -> 'No function found'), so use
  disassemble/disassembly context around it rather than assuming a body.
- Static trust boundary (from v1 attempt 3): trust rel32 edges + rewritten-
  site immediates ONLY; batch-4-style blind decompile sweeps of E1 batches
  skew UI/allocators (4ae24 = operator-new).
- Gate: bash scripts/gate.sh is the single verification command; ~2-3 min;
  R1 attempts are NEVER gate stages (gate stays fast, side-effect-free).

## NEXT ACTION (exactly one)
OQ-021 END-CTRL THRESHOLD (offline, zero capture cost; the string->loader route
was proven this turn and self-validated on restree). The end-ctrl.txt referrer
is guest-phys -> Ghidra 0x2c0aa (scripts/r1_datafile_strings.py, verified 20
slots), but get_function_by_address(0x2c0aa) says "No function found", so the
route is: get_assembly_context(xref_sources="0x2c0aa", context_instructions=12)
to read the surrounding instructions and walk to the enclosing function start
(prologue = PUSH regs / SUB ESP pattern; the file is opened by the victory
checker that also reads the "over half" comment file), then decompile that
function and read the ACTUAL comparison and its constant/multiplier: vendor
comment says "over half", same file's prose says "two-thirds" — decide with the
cmp/operand, not the prose. Check the sibling end-*.txt referrers
(0x2c04e/0x2c065/0x2c07c/0x2c093) the same way: they share the cluster, so one
function walk likely covers all five conditions. If the lifted threshold differs
from the rewrite's >1/2, upgrade the check in rewrite (grep the control-victory
site; note 2026-10-06 entry correction: NO boundary test currently pins >1/2, so
add one that pins the LIFTED value) + docs/re/ section + gate stays green. If
the constant is not present (computed from a table read), record the exit-1 line
with the disassembly quoted and move NEXT ACTION (no spiral). Doc target:
docs/re/ (victory/endgame section; check what exists before creating).

## KNOWN-ISSUES / PARKING LOT (operational; research negatives live in
## docs/REFUTED-ROUTES.md)
- ORBIT PAIR = ORDINAL-KEYED SHARED TABLE, NOT planet position: value is
  keyed by planet ordinal (I=(320,-960) etc., identical across campaigns);
  reading per-planet 'position' or extents from name+0x57/+0x5f is RETRACTED
  law (2026-10-06k). f32 x @+0x57, f32 y @+0x5f (gap 8; +0x5b zero pad — the
  "<ff" read fakes a radial law, hit 06d).
- NO xdotool on this host: synthetic keys go via tools/xsend key KEYSYM
  (rebuild: gcc -O1 -o xsend xsend.c -lX11). ESC closes the sticky planet
  view. r1_adcapture has a cmd_key channel using this.
- ckdiff planets() window-base law: name offsets key off H+0x255b00 (adding
  only H silently decodes nothing / garbage — hit twice); colonized test =
  u16@NAME+0x28 ONLY (ffffff@+0x2e is residue on every fresh-map planet).
- ADAPTIVE CAPTURE (scripts/r1_adcapture.sh): campaign-entry law = planet
  grid hash AT POINTER-LAW BASE CHANGES ('cosmic exiles' needle is the SETUP
  screen, NOT campaign — false breaks); checkpoint must double-read slot
  size (autosave rewrites in place -> torn BadZipFile copies); adaptive
  phase fits inside BOOT (-time-limit kills the game mid-drive); fresh-
  campaign LORE screen needs 2-3 center clicks (drive by shot-classify).
- vision_analyze intermittent 500 ('image input is not supported') — pixel
  statistics (panel dark-frac, color histogram) classify screens without it.
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
