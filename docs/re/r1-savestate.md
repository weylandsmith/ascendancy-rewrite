# R1 via SAVESTATE — the live-image route that replaced ptrace (2026-10-05)

Status: R1 LIVE. The tracer route (docs/BLOCKED.md) is superseded, not
repaired: dosbox-x 2025.02.01 blocks PTRACE_ATTACH/SEIZE on this box
(re-confirmed by an attempt mid-session this date, rc=1 negative), but the
emulator's OWN autosave feature hands us full guest RAM without ever
attaching to a process.

## Measured laws (all reproduced 2026-10-05, several runs)

1. `autosave=<interval> <slotlo>-<end>` + `saveremark=false` in [dosbox]
   writes slot files every <interval> s with no prompts, headless-safe
   (output=x11 under Xvfb; stdin=/dev/null; -time-limit still bounds it).
2. SLOT PATH LAW: saves land at `<dirname(captures)>/save/NN.sav` —
   dosbox-x strips the last path component of `captures` for state files.
   (Measured twice: captures=$ROOT/work/r1/r1sav-X  ->  work/r1/save/;
   captures=$RUN/caps -> $RUN/save/. Both match one rule.)
3. A slot file is a ZIP. Members of interest: `Memory` = 17,055,880 B
   uncompressed for memsize=16 (= 16 MiB + 278,664 B extra, presumed ROM/
   extra storage — unverified); `Program_Name` = `ASCEND` proves the real
   game process was captured; `CPU` = 21 MB of register/emulator state.
4. NEEDLE LAW: the payload FILE HEAD is a useless needle — at runtime the
   first 0x18000 bytes carry fixups (head 'LE\0\0' -> runtime 0710ec03...,
   ~136 differing bytes per 4 KB block, low-word-dominated). Correct law:
   high-entropy, zero-free windows at payload offset P appear at member
   offset B+P for ONE constant B.
5. BASE (this capture set): B = 0x1BF4D8, 6/6 unanimous high-entropy
   128-byte anchors, 6/6 consistent, identical in all 6 slots.
   B is per-run data, not a constant to hard-code — scripts re-derive it
   every capture (the OQ-011 lesson: never trust an unreplicated vote).
   B is a MEMBER offset; member -> guest physical is member - H (H=136,
   derived below), and guest LINEAR == guest PHYSICAL for this game (flat
   DPMI — established by the POINTER LAW section below, 2026-10-05i).
   The pointer law that was ambiguous here (D=R 289 / D=0x242000 573 vs
   controls <=115) is CLOSED below: the clusters are artefacts of one law,
   runtime_u32 = P0 + payload_file_offset(target).

## Tooling

* `scripts/r1_savestate.sh [boot-seconds]` — safe by construction (same
  invariants as r1_attempt.sh: scratch copy only, never mounts game/;
  pkill -x; -time-limit; bounded run dir work/r1/r1sav-<stamp>/). Exit 0
  only when `r1_sav_scan.py` finds the base unanimously.
* `scripts/r1_sav_scan.py --run-dir <dir with save/> --needle
  work/ascend_payload.bin` — unanimous-vote base finder (ambiguous windows
  do not vote; min 5 votes).
* `scripts/r1_base.py` — earlier exploration variant (kept; same vote core).
* `scripts/r1_validate.py` — pointer-density base validator (set-based, one
  pass over guest RAM; results above recorded here).
* `scripts/r1_pointer_law.py` — THE pointer-law battery (C1-C5 above); gate
  3q runs it over every captured slot dir. Exit 0 iff the law holds.
* `scripts/le_tables_anchored.py` — negative-result tool: object/page/fixup
  table attempts anchored to le_header_dump.py values (all V1 parses refuted;
  kept so the field-map route is not re-walked).
* `scripts/r1_pointer_measure.py`, `scripts/r1_live_probe.py` — the two
  measurement passes behind the CLOSED section's numbers (delta/pv censuses;
  single-copy proof). Superseded by r1_pointer_law.py for gating.
* `scripts/r1_restore_sites.py` — UPGRADE PASS 1 artifact builder: writes
  work/ascend_restored.bin (payload + 2,080 IMAGE-class pointer slots
  rewritten to d = rv - P0, the payload-file-offset address space Ghidra
  uses) and work/fixup_sites.tsv (ALL 34,326 differing slots, classed
  image-payload / image-bss / conventional / heap-other; heap & conventional
  are RUNTIME mutations of globals, deliberately not written). Verified on
  the artifacts: restored pointer-table runs (>=8) hit Watcom function-start
  bytes in the FILE at 101/167 = 60% vs the 15% static-refutation control;
  the code object starts at payload file 0x14bb0 with Watcom linked base
  0x1d4000 = P0 + 0x14bb0 (restored table entry file-intra 0x1349 ->
  d 0x15ef9 = 0x14bb0 + 0x1349, exact).
* `scripts/seed3_run.sh` + `scripts/ghidra/Seed3.java` — headless Ghidra
  bootstrap/xref-export on the RESTORED image (see Seed3 section below);
  writes work/functions3.tsv, work/code2data.tsv, work/vtables3.tsv.
* `scripts/attribution_scan.py` — module attribution via debug strings
  (E1 exact / E2 hint; gate 3r). Writes work/attribution.tsv.

## Save-state internals — source-cited (subagent verified tag dosbox-x-v2025.02.01) + measured cross-checks

Canonical repo is joncampbell123/dosbox-x. Primary paths:
* src/misc/savestates.cpp:1113-1134 — slot path law: without `-savedir`,
  `path = dirname(capturedir) + "/save"`, entry name `<slot>.sav` (1-based).
  MATCHES the measured law exactly. `-savedir <abs>` overrides to
  `<path>/<N>.sav` — prefer it for determinism.
* savestates.cpp:1078-1084 + hardware.cpp:2145/2166-2173 — autosave never
  prompts (dialog only when `!auto_save_state && !noremark`); remark entry
  = literal "Auto-save"; interval is HOST wall-clock seconds checked at
  vblank, first save just after t=interval; slot range walks A-B then wraps.
  REQUIRES video timer activity — must run with real output (x11 under
  Xvfb), NOT `output=dummy` for the *game* run (dummy smoke tests still
  saved here because dosbox-x reset dummy->default; do not rely on it).
* src/hardware/memory.cpp:2803-2853 (`SerializeMemory::getBytes`) — the
  `Memory` entry layout: [0] MemoryBlock struct header, then MemBase =
  COMPLETE guest RAM contiguous from guest PHYSICAL 0 (pages*4096), then
  mhandles (pages*4), then pagehandler_idx (262,144 B; 1=ram 2=rom
  3-16=VGA). MEASURED: header = 136 B EXACT (136 + 16 MiB + 16,384 +
  262,144 = 17,055,880 = member size, zero slack). The subagent's compiled
  estimate of 104 was 32 B short — trust the census AND the BDA scan below,
  and DERIVE H per build rather than hard-coding.
* dosbox.cpp:1708 — `savefile` replaces the slot name for ALL saves
  INCLUDING autosave (savestates.cpp:1134 ternary): must stay EMPTY or the
  slot rotation dies.

### Derived law (2026-10-05, slot 46 of r1sav-20261005-151634)
MEMBER OFFSET = GUEST PHYSICAL + H, H = 136 for this build. Two independent
confirmations: (1) size census above; (2) BDA signature scan — the unique
h in [0,0x2000) with u16@h+0x413 == 0x280 (640 KB) AND u16@h+0x44A == 80
returns h=0x88 exactly; with that offset the IVT reads coherently
(INT0 f000:ca60, INT10 c000:00ee video BIOS, INT21 f000:d0e0, INT33
c402:0010 mouse). The earlier "BDA all-zero" oddity was MY misalignment
(reading at member 0x400, not 0x488) — recorded so nobody re-chases it.
Consequence: this capture's image base in GUEST PHYSICAL = B - 136 =
0x1BF450 (B=0x1BF4D8 member-offset, per-run data as always).

### POINTER LAW — CLOSED 2026-10-05i [verified 12/12 slots, gate 3q]
THE LAW: the payload image is loaded ONCE, verbatim, at guest-physical
P0 = B - H (this capture: 0x1BF450), guest LINEAR == guest PHYSICAL (flat
DPMI), in TWO objects (Watcom link layout, file order == memory order):

    obj0 code: storage payload [0x14bb0, 0x82bb0)  mem base 0x1d4000
    obj1 data: storage payload [0x82bb0, 0x8cc83)  mem base 0x242000

The linker stored INTRA-OBJECT offsets at pointer slots; the loader added the
target object's mem base:
    runtime_u32 = mem_base(obj of target) + stored_intra_offset
and since mem_base(obj) = P0 + storage_start(obj), this is IDENTICAL to the
flat form
    runtime_u32 = P0 + payload_file_offset(target)      (file_offset = rv-P0)
The 2026-10-05h reading ("clusters are per-object linear bases; 0x6E000 =
obj0 size") is CONFIRMED by this arithmetic: L1 - L0 = 0x6E000 = obj0 storage
size exactly, and mid-session revisions of this file that called it retracted
were WRONG — both formulations hold and convert through storage_start.
CONFIRMED arithmetic anchors: restored vtable entry file-intra 0x1349 ->
d 0x15ef9 = 0x14bb0 + 0x1349 exact (scripts/r1_restore_sites.py); obj0 mem
base 0x1d4000 = P0 + 0x14bb0; obj1 mem base 0x242000 = P0 + 0x82bb0.
OPEN SUBITEM (does NOT affect the law or the flat conversion): obj1's memory
size. L1-delta sites carry stored values up to 0xa28e2 (max rv 0x2e48e2),
so obj1 mem >= 0xa28e3; header dword +0x24 = 0xa7710 cannot then be the two
objects' summed memory (0x6E000+0xa28e3 > 0xa7710) — its identity (cbImage?
debug-area end?) stays [unverified]; the LE field-map route that would settle
it is closed-negative below (le_tables_anchored.py). obj1 file storage is
0xa0d3 B + BSS; the 885 L1 sites with stored >= 0x6E000 all sit in obj0's
file range and point into obj1 BSS — consistent, no contradiction.

CONFIRMATIONS (scripts/r1_pointer_law.py, exit 0 iff all hold, all 12 slots of
r1sav-20261005-{151634,160721} pass):
  C1 image windows at six spread file offsets are verbatim at member B+file
     offset (>=12/16 bytes, window unique in the payload to <=2 occurrences);
  C2 all 8 EXE-proven path-template strings (loader.md §5) occur live at
     physical P0+file_offset (unique occurrences; duplicates found elsewhere
     in RAM are game-loaded copies of the .txt data, not law violations);
  C3 pointer tables (runs >=8 of image-span u32) hit Watcom function-start
     bytes at pay[rv-P0] 100/151 = 66% vs 15% control (loader.md §4.1);
  C4 252 of 9,927 fixed-up sites (scan to file 0x70000) decode to printable
     ASCII — e.g. site 0x14fa0: runtime 0x242020 -> payload 0x82bd0
     '..\\batcon.cpp' (Watcom debug source names; the 0x1c=0x63774 header
     field is that debug/line-info area per loader.md §1);
  C5 a CPU-member u32 (build offset +0x20 — EIP by value range; layout NOT
     parsed) lies inside [P0, P0+0xa7710) in every slot: the captured CPU was
     executing inside the image.

REFUTED en route (do not re-try): (a) second-copy reading 'live code at
linear 0x1d4000' — mem[H+0x1d4000] bytes match pay[0x15bb0] i.e. P0+0x15bb0 =
0x1d4000, the SAME single copy; (b) the LE header field-map route — with
offsets taken from header values measured by le_header_dump.py, no object
table parse has sum(cbObject)==cbImage (scripts/le_tables_anchored.py V1), and
the +0x100-stride u32 'page table' is code bytes (first value 0x90c300cd =
`int3; xchg cl,al` pattern repeated — flag-free stride runs are NOT page
tables; loader.md §1's reading of that run as the LE page table is WEAKENED
accordingly: file order == memory order stands on le_contiguity_test.py, not
on this run); (c) raw u32==0x1d4000/0x242000 searches in the payload: zero
occurrences (the bases exist only after fixup).

DECODED LANDMARKS (guest physical this capture; re-derive per run): lowest
C1-verified verbatim code window at P0+0x14bb0 (`0xcc 0xebf 0x90-pad` then
56 57 55 push triple); debug source-name strings begin at
P0+0x82bd0 ('..\\batcon.cpp'); live game data (Xerxes etc.) lives at
0x253000..0x256000+ as runtime structures, NOT in the image span's file bytes.

## What this unlocks (per BLOCKED.md upgrade branch) — UPDATED 2026-10-05i

Pointer law is CLOSED (above), so EVERY captured guest address now maps
two ways without further evidence work:
  guest phys -> payload file offset  (f = rv - P0)   [image bytes, code]
  guest phys -> runtime structure    (direct member read)  [live game state]
The next R1 work items, in order of leverage:
  1. Ghidra fixed-base re-analysis: load the payload at base 0 (file order ==
     memory order, loader.md §2) — every immediate/disp that the fixups
     rewrote can be restored from the capture (site list = aligned u32 where
     mem[B+f] != pay[f]), giving true data xrefs for the 269 bootstrap
     functions and their callees: combat arithmetic (OQ-010), AI orderings
     (OQ-015/016), .shp loader (OQ-005).
  2. Deeper captures: click into a real game via ref_capture.sh coords before
     autosave fires (60 s interval is plenty) so loaded DATA structures
     (ships, techs, diplomacy) are present, not just title-screen state;
     correlate against extracted/ tables for the savegame map (OQ-003).
  3. The CPU member u32 at +0x20 tracks the executing address (0x20eeec ->
     0x22d820 across slots): stepping through gameplay is observable without
     any debugger — slot diffs of guest RAM around a clicked action isolate
     the code that ran (rv - P0 -> file offset -> disassemble).

## Seed3 + MODULE ATTRIBUTION — 2026-10-05j

scripts/seed3_run.sh runs scripts/ghidra/Seed3.java headless on
work/ascend_restored.bin (-noanalysis; API fixes found by compiler:
Instruction.getReferencesFrom() returns Reference[] not an iterator; this
RefType build has no isCALL()/isJUMP(), test r.isCall()/r.isJump()). Result:
292 functions (Seed2 static: 269), 741 code->data refs / 280 distinct targets.
Vtable seeding found 21 pointer tables >=4 entries (work/vtables3.tsv), e.g.
file 0x88400 -> 6 distinct code entries; extra seeds were few because table
entries often sit mid-padding (isPrologue gate).

ATTRIBUTION (scripts/attribution_scan.py, gate 3r): E1 = code u32 (any byte
offset — immediates needn't be 4-aligned, e.g. push imm32 at site-3) equal to
a data-object ..\module.ext string byte position, on the RESTORED image;
E2 = raw-file intra-object value in imm32-operand position (hint column only,
false-positive-prone; batcon.cpp E2=1825 is that noise, E1=5 real).
SIGNIFICANCE (measured 2026-10-05j, do not re-derive): E1 total 225 sites.
Random-position expectation for 7,656 distinct string byte-positions over
0x6D000 code bytes at file-value density would be ~6,000 hits — observed 225,
i.e. code u32s are NOT uniform (small immediates dominate), so raw count is
not the quality signal. THE quality signal: 139/225 = 62% of E1 sites lie on
(s..s+3 of) an actual rewritten fixup site from fixup_sites.tsv, vs ~2%
expected if E1 were coincidence. The 86 off-site E1s are data blobs in code
storage / heap-class diffs landing on strings, and are kept (attribution is
per-site and usable either way). Locality per module is MIXED — batmode span
0x4fd7 (one bucket), cosmos 0x4000, but flic spans 0x63e2f across buckets
0,1,3,5,6 (Watcom interleaves template/util code; do not treat locality as a
validity test). Per-module E1: flic 43, winmgr 24, gsystem 23, race 20,
cosmos/batmode 10, planet 8; 33 modules total. Full table:
work/attribution.tsv (module, site, encoding, est_func by
nearest-preceding-prologue rule).

FRAME SCARE, RESOLVED THE SAME TURN (third re-derivation of the pointer law,
kept so it isn't re-walked): an ad-hoc check printed 'diffs' computed as
MATCH counts and briefly suggested d = rv - B (+0x88 off). Its own printed
evidence refuted it (D1: rv-B=0x82b48 lands on zero padding, rv-P0=0x82bd0
lands on '..\batcon.cpp'; page census: 74 pages verbatim at delta B, and the
'game.pal' live copy sits at physical P0+q, not B+q). The law as CLOSED above
stands unchanged. Lesson already in memory: re-derive both directions before
writing retraction language; addendum: also check WHICH way a helper counts
before trusting its label.

## FIRST DECOMPILE BATCH (OQ-010 attempt 1) — 2026-10-05j

scripts/ghidra/DecompileCombat.java reads hex targets one-per-line from
work/combat_decomp_targets.txt and writes work/combat_decomp/<addr>.c
(against ghp4/ascend4; -process takes the IMPORTED FILE NAME
ascend_restored.bin, not the project name — measured). Batch 1: the five
batmode/batcon E1 functions (0x14bc0, 0x156d4, 0x1aef8, 0x1b91c, 0x1ce1c) +
top callees (0x56ca4, 0x5cf96, 0x5caac, 0x336b4); 9/9 decompiled ok.

HONEST RESULT: these are battle-MODE UI and window-message dispatch
(batmode.cpp/batcon.cpp are the combat screens), e.g. FUN_000336b4 is a
case-split message handler over param_2<7 touching object fields 0x35/0x39/
0x41 + vtable calls (offset +0xc, +0x10 into vtable at field 0xa7);
FUN_00056ca4 is a bounds-check + vtable thunk. No hit/damage arithmetic in
this batch. STRUCTURAL GOLDMINE instead: Watcom thiscall confirmed
(vtable at object+0xa7, methods at +8/+0xc/+0xc slots), fields carry packed
16-bit pairs (>>0x10 idiom everywhere), 56 direct call sites of FUN_00056ca4
including 6 inside FUN_0001aef8. The COMBAT ARITHMETIC therefore lives where
the battle UI CALLS INTO. FOLLOW-UP MEASURED SAME TURN (attempt 2 batch:
gsystem funcs 0x2fed0/0x528ec/0x70790 + the 'damage-ish' pair): FUN_0005cf96
and FUN_0005caac are REFUTED as damage arithmetic — their bodies are packed
comparisons *2 + quadrant-bit assembly (`((a<b)*2+(c<d))*2+...`) feeding
byte >>1 draw loops: graphics/fill code shape, not combat (the earlier
'heavy byte/uint mixing — damage-ish' label was a shape-overclaim caught by
reading the bodies; only 3 of the 10 engine-module est_funcs were real
functions, the rest mid-stream). STRATEGY CORRECTION for attempt 3: stop
following shape hunches from 292 dark-stream functions; the ceiling problem
is function-reach, so either (a) run Ghidra's FULL auto-analysis on the
restored image (data refs now exist, which is exactly what makes auto
function detection work — earlier Seed runs deliberately used -noanalysis
because the raw image had none), then attribution-filter the resulting
function set by module; or (b) deeper capture so slot-diff pinpoints
executed code (unlock item 3).
PRNG census in code storage: u32 0x343FD appears ONCE (0x30aa8) but the
context bytes REFUTE it as a constant — the encoding there is `ret; mov
edx,esi; mov eax,ecx; e8 fd 43 03 00`, i.e. a CALL whose rel32 coincidentally
equals 0x343FD (target 0x34ea9). With its companion add 0x269EC3 also absent
(zero u32 occurrences), the MSVC/Watcom rand() is NOT in code storage
(runtime-lib call elsewhere or not used). The pair 0x41C64E6D + 0x3039 sits
at 0x7825b/0x78261: `69 10 6d 4e c6 41` = `imul dword [eax],0x41c64e6d` then
`81 c2 39 30 00 00` = `add edx,0x3039` — a hand-rolled LCG (glibc constants),
container not yet mapped: NOT inside any of the 292 seeded functions. Lesson
pinned: constant scans must check the instruction encoding before claiming a
constant (immediate vs coincidental rel32). 'which RNG does combat use' =
OQ-010 subquestion, answerable by call-graph reach once more functions are
seeded.

## ATTEMPT 3: FULL AUTO-ANALYSIS + BATCH 3 — 2026-10-05j/early 05k

ghp5/ascend5 (import ascend_restored.bin base 0x100000, FULL analysis,
postScript ExportFunctions.java): 1,144 functions -> work/functions_full.tsv
(vs 292 from the -noanalysis Seed bootstrap — confirms the reach hypothesis).
analyzeHeadless mechanics measured: project DIRECTORY must pre-exist
('Directory not found' abort); -process matches the IMPORTED FILE NAME
(ascend_restored.bin), not the project name. Decompiler stream quality is now
GOOD: only 3 of 40 exported batch files carry 'bad instruction data'
warnings (156d4, 4ae24, 44848) — earlier warnings were the -noanalysis dark
streams, not the code.

BATCH 3 (27 engine-module E1 functions resolved under full analysis: cosmos
8, race 6, gsystem 6, planet 6, ship 3, raceneg 3, ... joined
attribution x functions_full; work/combat_decomp_targets.txt; files keyed by
FILE OFFSET after the imgBase fix in DecompileCombat.java): arithmetic-scan
top hits (imul/div/>> per file): 41e34 (race, 6087B), 25604 (flic+cosmos),
41260 (race), 3f758 (race), 4ae24 (ship), 44a44 (raceneg). RESULT: 4ae24 is
OPERATOR NEW / record allocation — `(x + -0x2b057)/0x7b` divides a pointer by
record strides 0x7b/0x60/0x27 (three pooled record types), not combat math.
No hit/damage/shield formula located yet. The E1-attributed corpus covers UI
+ allocators heavily because assert/trace strings cluster there.

IMMEDIATE-ENCODING FRAME (hazard, pinned): absolute-address immediates come
in THREE encodings and mixing them invents tables: (1) rewritten fixup sites
(restored) = file offsets, trustworthy; (2) same-object link-time refs =
intra-object offsets; (3) cross-object link-time refs = intra-TARGET-object
offsets — NOT resolvable statically without the LE object table (route closed
negative 05i). Worked refutation: immediate 0x7478b at site 0x41485
(0x41260/race.cpp, payload==restored so encoding (2)/(3)): read as-is it
lands mid-code-stream; an earlier draft of this section claimed the
code-intra reading (+0x14bb0 -> 0x8933b) showed a 'u16-pair table' —
REFUTED: 0x8933b bytes are UTF-16 text (0x64 'd', 0x3e '>', 0x4d 'M', 0x5a
'Z', CJK 0x96, 0x46C). So for 0x7478b all file-readable interpretations are
garbage -> it is an encoding-(3) cross-object value whose runtime target is
unknowable from the static image. Corroborating tell: Ghidra itself labeled
sibling constants in the same functions as 'bRam00077429' (EXTERNAL/RAM
space), and the recurring race.cpp guard idiom
`*(idx*0x4b + X) >> 0x18 & 1 << (bit & 0x1f)` (bitset, stride 0x4b=75) runs
on such unresolvable X values. HARD BOUNDARY for OQ-010 static work: trust
(a) rel32 call/cross edges always, (b) rewritten-site immediates always,
(c) NOTHING else absolute. Data-driven inputs therefore need the DEEPER
CAPTURE (slot-diff of in-battle RAM: pointer values there resolve by the
pointer law even in pages we did not restore) — that is the critical path,
not more static batches.
