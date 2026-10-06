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
* `scripts/r1_deepcapture.sh` + `scripts/r1_deep_diff.py` — DEEPER CAPTURE
  (2026-10-05k): boots the game, clicks title New Game (window 318,293 =
  root 333 law), VERIFY_NEEDLE-gated retry (needle = post-screen string,
  checked against the newest autosave; max 5 extra clicks at 11 s cadence —
  synthetic clicks are flaky, run2 warped without a button event), then
  diffs earliest-vs-latest guest RAM. Exit 0 = payload anchored AND deep
  (>=100k bytes changed, >=50 live image refs, >=5 new strings). First
  verified run r1deep-20261005-204919: changed 744,840 / heap 741,556 /
  live image refs 195 / new strings 3,932 (newgame.txt race blurbs — click
  proven landed by needle in slot content, deep_census.txt persisted).
  CORRELATION (same capture, scripts inline): word-like census strings (>=4
  letter word + 2 more) = 22, ALL 22 substrings of extracted/ — 21 = every
  newgame.txt race blurb (21/21 lines fully resident in late-slot RAM; the
  New Game setup screen had loaded its complete table), rest = VOC headers
  (audio bank load). Membership hazard: census lines carry the trailing
  newline — strip before substring tests (un-stripped it falsely reported
  0/22; artifact-encoding check before any membership claim).
  LAWS learned: slot ORDER = file mtime not slot number (autosave rotates
  41-60; post-wrap the LOWEST number is the NEWEST — numeric sort produced
  a false shallow); BASELINE = early slot must lack the needle (first
  autosave lands ~62 s after Xvfb start; a click before it leaves no
  pre-click frame => exit 2, schedule click t>=75).
  NEW-CAMPAIGN LAUNCH LAW (run r1deep-20261005-215445, byte-proved, NO
  vision needed): planet table at phys 0x26d07b (same address as the resumed
  campaign) changes its record-0 name between consecutive mtime-ordered
  slots — 'Ajax I' (pre-launch campaign, slots 46-51) -> 'Bodkin I' (new
  campaign, slots 52-45). Detector is now scripts/r1_campaign_probe.py
  (exit 0 = transition captured in this run, 1 = single campaign, 2 =
  harness). Detect campaign start byte-wise; vision is only for WHERE.
  SETUP-SCREEN START CONTROL: WINDOW-RELATIVE (600,440) (run
  r1deep-20261005-221429, proven by ELIMINATION: the run made exactly two
  clicks, New Game at 75 s and (600,440) at 115 s; every one of the 20
  autosave slots holds a FRESH campaign (rec0 'Alpheratz I', a names.txt
  pool name; the boot campaign is 'Ajax I') => the second click completed
  the new-game flow). Note the fresh campaign was already resident in the
  FIRST post-click slot (10 s autosave cadence beats vision round-trips).
  tools/xsend grew a `key KEYSYM [ch]` mode (compiled clean; synthetic key
  delivery to the DOS guest still UNVERIFIED — prove with a text-entry
  screen before relying on it).
  STRATEGY-SCREEN CONTROL COORDS [verified from extracted/ascend00/
  windows.txt §TURNCOUNT/NEXTTURN/NEXTTURNCONT]: NEXTTURN rect X0 474 Y0 52
  X1 548 Y1 82 -> click center (511,67), SENDMESSAGE 7; NEXTTURNCONT rect
  557/52-632/82 -> center (594,67), SENDMESSAGE 8; TURNCOUNT display 474/7-
  632/43 (SHAPEFRAME 65 + DIGITFRAMES 55 = digit-glyph rendering, ties to
  shp spec). COORD LAW CONFIRMED INDEPENDENTLY: FRESHGAME rect 159/280-
  477/310 -> center (318,295); measured landing click (318,293) — exact X
  center, 2 px off center Y, both inside rect. Game coords == window-relative
  for two windows.txt-derived predictions (FRESHGAME, and setup-start
  elimination at (600,440)). Next capture
  schedule: 75:318:293;115:600:440; then NEXTTURN every ~20 s to advance
  turns; adjacent-slot deltas then isolate TURN-PROCESSING mutations
  (scripts/r1_slot_delta.py, --mask 0x370000-0x3c0000).
  IDLE-CHURN FINDING (run 221429, r1_slot_delta first blood): with the render
  buffer masked, an IDLE campaign still mutates ~6 KB/10 s at phys 0x2e0000
  (same page as the star-name pool), intermittently (pairs 54-56 ~zero);
  0x1040000/0x1b0000 trickle ~50-100 B. 0x2e0000 is the primary game-state
  mutation page candidate; idle churn source [unverified — animation/clock].
  Render-buffer law: phys 0x370000-0x3bffff churns ~64 KB/10 s with smooth
  byte gradients (entropy 6.4) while merely displaying — ALWAYS mask before
  game-state census.

TURN-CLOCK + TURN-BOUNDARY LAWS (run r1deep-20261005-230146 vs idle controls
221429/224916, same harness, clicks 75:318:293;115:600:440 then 10x NEXTTURN
at (511,67) every ~25 s):
  TURN COUNTER u16 physical 0x254e10 (identical sequences at 0x254fb4/
  0x2551a2/0x255390/0x25576c and planet-table-relative 0x26dbb2; doubled
  mirrors at phys 0x26e080/82/830/832 = value*2 [field meanings unverified]).
  Monotone nondecreasing across ALL slots; IDLE campaigns pin it at 0 in
  EVERY slot of BOTH control runs; the click run walked 2->9. NEXTTURN at the
  windows.txt-derived (511,67) WORKS — turn advancement confirmed byte-wise.
  Counter offset semantics [unverified]: value 2 by the first autosave; do
  NOT assume turn# == value until a timed run pins the mapping.
  TURN-BOUNDARY LAW: planet records (phys 0x26d07b, stride 123) mutate ONLY
  between slots whose turn counter differs — 0 changed record bytes across
  all 12 non-boundary pairs; ~600-950 per hot offset across the 7 boundary
  pairs. CONVENTION: offsets below are relative to rec0 NAME position
  (phys 0x26d07b); the DEEP-HEAP census aligned records with the name at
  +0x59, so a name-anchored 123-B window = [tail of anchored record
  (name-rel 0x00..0x21 = old +0x59..0x7A)] + [head of the NEXT record
  (name-rel 0x22.. = old +0x00..)]. All hot offsets below are >= 0x57 and
  therefore HEAD fields of the record whose name anchors the next window:
  convert with o'=o-0x22. Hot per-record fields: the +0x57..0x61
  block (counts ~940/151 recs; = older-convention +0x35..+0x3F) plus +0x5a
  (124) and +0x5e (91). The +0x57..0x5f u16 values read as high-
  entropy per-record noise changing every turn (33281->9351 etc.) —
  consistent with RNG/state-mixing fields, NOT counters [interpretation
  flagged; the census is the fact]. Name fields +0x00..0x12 NEVER change.
  IDLE CHURN REFINED: idle page 0x2e0000 churn (~6 KB/10 s) is NOT the planet
  table (zero planet churn off-boundary) — name-pool neighborhood or adjacent
  runtime animation; mask remains required.
  Harness lessons: (1) VERIFY_NEEDLE="" was silently overridden by
  ${VAR:-default} -> false exit-2 baseline fire; fixed to ${VAR-default}.
  (2) A 420 s foreground tool timeout kills the WRAPPER mid-run while dosbox
  and autosave continue (slots stayed 20/20, clicks all delivered) — read the
  run dir directly; never trust the missing wrapper log as run failure.

  +0x69 IS NOT a turn clock: REFUTED same-minute (run 215445) — rec0
  (+0x68,+0x69) = (152,37) in all 20 slots across a campaign restart AND
  an idle stretch; rec0 reads (152,37) in BOTH independently-generated new
  campaigns (Ajax I, Bodkin I). Consistent with per-record STATIC
  generation data (rec0 likely unowned-planet defaults) whose save-vs-live
  delta (+192/+5/+6 on the resumed Xerxes campaign) is per-campaign init
  state [unverified origin; do not mine further until code xrefs land].

PLANET RECORD RECOVERED FROM DEEP HEAP (2026-10-05k, run r1deep-20261005-210149):
the title screen ALREADY carries resume.gam's loaded map (game restores the
current campaign at startup — 'Xerxes II', 'Mukwonago V' present pre-click;
'Star Lane Anatomy' is a static.txt HELP topic name, not a screen name —
needles must be proven absent from the title baseline, this one wasn't).
CONFIRMED by file<->RAM join (scripts/r1_planet_layout.py, deterministic):
game/resume.gam (81,647 B — gate 3f pins THIS size; the scratch copy under
work/r1/game/ converges to the same 81,647 B by run end) holds 151 planet
records, stride 123, first name at file 0x9b1a; the same
151 records, same order, live verbatim at phys 0x26d07b in the resumed slot
(pointer law H=0x88) with EXACTLY two differing fields (r1_planet_layout.py
counter census): +0x68 u8 = a monotone-nondec order-preserving COUNTER on
both sides (file 0..255 wraps=2, ram 0..255 wraps=2, constant delta +192
mod 256 on all 150 differing records — NOT owner: 50 systems can't share one
byte identity, so it is a per-slot scan/serial counter whose origin differs
[unverified]) and +0x69 u8 {0..32} -> {..38}, delta +5 (98 recs) or +6 (52)
— GROWTH-shaped: the live campaign advanced after the save [unverified
semantics]. Earlier drafts of this paragraph claimed '+136' and 'owner-
dependent'; both were wrong, superseded by the counter census.) Name field
+0x00..0x12 mismatch count 0. So resume.gam
is an ON-DISK MIRROR of the live map tables: static file offsets read the
same record layout the game uses at runtime [verified 151/151].
Star-side settled WITHOUT new law: naming already closed in docs/re/mapgen.md
(names.txt pool + shuffle); the pool is resident verbatim in new-game slots
(phys 0x2e8338 run-204919 slot 48, stride-20 name[12]+f32+f32+u32 records)
and absent from resumed slots — as expected for a loaded-save campaign. An
interim "50-star roster stride-51" claim made mid-turn was NOT reproducible
from any byte source and was retracted the same turn (vision text is not
evidence; only mem/file searches are).
Name-region census in physical 0x26d000+: 121 '[Star] [Roman]' planet names
at a CONTIGUOUS stride of exactly 0x7b with the name at record offset +0x59
(all 121 satisfy (o-base)%0x7b==0x59; base found by the +0x59 law). 50
distinct star systems, up to V moons each (~150 record slots incl. blanks).
SEMANTIC UPGRADE (honest chain): FUN_0004ae24, recorded this morning as bare
'operator new (stride divides 0x7b/0x60/0x27)', divides exactly 0x7b AND
addresses name-adjacent field +0x59 — it is the PLANET record
allocator/accessor [inferred from the RAM-matching constants: stride 0x7b +
+0x59 both verified]. The other two strides (0x60=96, 0x27=39) are candidate
record sizes for further correlation (star records? lanes?). rec0 byte census
(31 nonzero-at-some-record u32 columns) is raw material for the savegame
map (OQ-003); semantics of individual fields remain [unverified] until code
xrefs or a gameplay-delta diff pin them.

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

## STAR TABLE + ORBIT LAWS — 2026-10-06 (battery `scripts/r1_star_table.py`,
## run green on ALL 13 captures, 259/259 slots; conventions: same per-run base
## finder (H), name grids guest-phys 0x255b00-ish / planet NAME grid 0x26d07b
## + 123j — hint anchors only, always re-derived)

STAR RECORD (stride 96 exact — 49 consecutive name deltas all == 96, both
campaign runs; records NAME-anchored, k capped at 50 because the chain runs
into the names.txt pool past record 50; every field offset is name-relative):

    name        char[]   star display name, NUL-terminated (chain start)
    name-0x18   u32      system index, 0-based == k — verified 50/50
    name-0x14   f32[3]   the STAR's own strategic-map position (x, y, z),
                         NOT the planets' orbit centre (orbit pair is
                         galacto-centric — see ORBIT LAW). Extents run230146:
                         x -391.4..379.2 y -426.7..410.8 z -346.1..432.5;
                         run 233706 similar (all abs(coord) < 440). [012(d)
                         map extent corroboration: playable galaxy is a
                         ~880-unit cube centred on (0,0,0); NOT a closure —
                         generator controls untested.]
    name-0x1C   u32      small value 0..12 [semantics UNVERIFIED — measured
                         NOT moon count: agrees with live-assigned count 4/50,
                         raw-ptr count 6/50; Elwyssen reads 9 with 4 planets]
    name-0x20   u32      sentinel 0xFFFFFFFF: present 49/50 (first record
                         reads 0) in every campaign run, ABSENT (0/50) in
                         idle run 221429 — presence is campaign-state-shaped,
                         not structural law; battery counts it as a note only
    name+0x10   u32[3]   sub-struct pointers into pool 0x258000..0x25a000 of
                         stride-0x27 (39 B) records; systems draw pool slots
                         in PERMUTATION order (every delta a multiple of 39;
                         two systems may SHARE a slot — Elwyssen and Syzygifer
                         both reference 0x258147) [semantics unverified]
    name+0x2A   u32[5]   planet pointers, 0-padded; TARGET = planet NAME addr
                         - 0x24 (the pointed-to record START precedes the
                         planet name by 0x24 bytes). A pointer is LIVE iff the
                         target planet name prefix == this star name. Verified
                         law: at most ONE system live-owns any planet (136/151
                         run230146, 141/167 run233706, 158/158 idle 221429).
                         Tail slots beyond the live run hold GARBAGE pointers
                         (off-grid or foreign-prefix) — present even on a
                         BRAND-FRESH map (43 on fresh r1ad-131350), so NOT
                         campaign carryover; the LIVE prefix rule is the law,
                         stale entries are allocator residue to ignore.

PLANET ORBIT LAW (orbit pair f32 x @ planet-name+0x57, f32 y @ +0x5f; 8-byte
gap, +0x5b..0x5e zero padding):
  - The pair is a position ORBITING THE GALACTIC ORIGIN (0,0), NOT the owning
    star. RADIUS sqrt(x^2+y^2) about the ORIGIN is CONSTANT to f32 precision
    across every slot and every turn boundary: 0 violations /151 (230146),
    /157 (r1ad-131350), plus 233706. STAR-CENTRED radius is REFUTED: 156/157
    records drift when measured w.r.t. star name-0x14 (r1ad-131350). [Both
    '0-violation centered' claims earlier in this file came from analysis
    CODE that never subtracted the center — the label was wrong, the number
    was origin-based all along. Fixed 2026-10-06e.]
  - ANGULAR VELOCITY IS A PER-PLANET CONSTANT, applied by the turn loop:
    dtheta/turn (origin-relative angles) identical across ALL boundaries for
    every moving planet (135/151 run 230146; 139-row cross-run fit).
    Retrograde. Sample: r=544 -> -13.52 deg/turn; r=1983.5 -> -1.02;
    r=2216.3 -> -0.81. Cross-run fit w*r^2 cv 0.35 — NOT a clean power law
    (w is effectively a per-planet constant, and same-radius planets share w:
    only 3 of 25 distinct radii in the fit band showed >1 omega, all borderline
    rounding). Lift per-planet (radius, dtheta) pairs, not a formula.
    Fresh-map seed: all planets start theta 0 or 180 (y==0 exactly, radii
    quantized 896/672/544/384...).
  - STATIC-PAIR SET: planets whose (x,y) never change any slot: 16/151 run
    230146, 28/167 run 233706. The UNASSIGNED set (no live star pointer) is a
    strict SUBSET of the static set in BOTH runs (orphan<=static verified) —
    [INFERRED] a planet not attached to a system's live pointer array has its
    orbit advance skipped by the turn loop; not yet code-proven.
  - Orphan system prefixes differ per campaign (230146: Icarus/Pendulon/
    Masticon/Buntrusol — Pendulon is NOT a star in that run's chain; 233706
    adds Ephemera/Pulveran/Phoebe): orphan membership is generated per-map,
    NOT a fixed vendor reserve.

Allocator tie (pinned): FUN_0004ae24 divides exactly by {0x7b, 0x60, 0x27};
live strides now MEASURED for all three families: planet 123, star 96,
sub-pool 39. The three pooled record families the allocator serves are
IDENTIFIED.

Battery: `python3 scripts/r1_star_table.py --run-dir work/r1/<run> [--slot N]
[--verbose]`; exit 0 law confirmed every slot / 1 negative / 2 harness.
Checks: stride law, chain length >=45, per-record idx==k, single-owner law,
sub-ptr window + delta-multiple-of-39.

### Static tie: FUN_00025604 stride table (2026-10-06, Ghidra re-analysis of
work/ascend_payload.bin base-0, 980 functions)

FUN_00025604 prologue loads an array of record-SIZE constants into locals:
`0x60, 0x7b, 0x27, 0x1ee (494), 0x19e (414), 0xd (13)` (local_80..local_6c),
and the SAME function contains a true indexed loop `base + idx*0x27` iterating
`*(short*)(base+0x49c3)` records of >=0x27 bytes (fields at +0, +4 deref'd as
pointers >>0x10, u16 @+0x21, u32 @+0x23) plus another `base + idx*0x19e` loop
copying 100 dwords + u16 count + trailing fields. Trust status per the
IMMEDIATE-ENCODING FRAME: the multipliers 0x27/0x19e and all field
displacements are encodings (1)/(2)-safe ONLY at rewritten sites; in the raw
payload this range differs from ascend_restored.bin, so the decompile is read
as SHAPE evidence, not address evidence.

WHAT IT PROVES (shape-level): the three live-measured record families are the
same families the code indexes with literal size constants — planet 123
(0x7b), star 96 (0x60), sub-pool 39 (0x27). Corroborates the earlier
FUN_0004ae24 divide-by-{0x7b,0x60,0x27} tie with a second, independent site.
Additional code-side stride constants 13, 414, 494 exist (13 = 0xd divides
39; 75 (restree) = 13x5; blob-internal pointer census shows a pool whose
targets are all multiples of 13 from pool base — consistent, [inferred]).
NOT proven: which loop is the turn-loop orbit writer; no f32 +0x57/+0x5f
disp32 accesses exist in the payload (orbit reads are register-relative or
through un-restored immediates — disp32 scan found only 2 bogus hits, both
outside code ranges).

### Controlled-boundary capture, run r1deep-20261006-123049 (2026-10-06c)

Scheduled-click capture (8 clicks, 3 NEXTTURN landings, turn 0->3, battery
green 20/20 slots). TWO OUTCOMES:

(1) NEGATIVE (exit-1): the scheduled in-game clicks (map 115,251, planet
screen 250,195) produced ZERO planet-record change on their bracketing
intra-turn slot pairs (55->56, 58->59, 41->42 all 0/151). ROOT CAUSE
[verified by reasoning + old-run cluster math]: the click point was a
centroid of run 230146's map; every new campaign generates a NEW random map,
so the point hit empty space. Static SCHEDULE schedules cannot target a
random map — the click must be positioned from a LIVE screenshot of the SAME
campaign. Next attempt = adaptive (background capture, vision-read a shot,
xsend the click into the live run, autosaves bracket automatically).

(2) POSITIVE (boundary census, new campaign, slots mtime-ordered
56,57,58,59,60,41,42,43 = turns 0,1,1,2,2,2,3,3):
  - MASS-WRITER LAW (clean): across all three turn boundaries the ONLY
    planet-record offsets changing en masse (146/151 movers) are the orbit
    f32 pair at NAME+0x57..0x5a (x) and NAME+0x5f..0x62 (y). 5 planets
    static (this map's unassigned set). No other offset moves more than 5
    records per boundary. Turn loop = orbit advance + a handful of state
    fields; NOTHING else churns.
  - COLONIZED-PLANET BLOCK (semantics UNVERIFIED, shapes pinned): exactly 5
    records (the player's colonies: Tensoric I, Gasball III, Feculon II,
    Freblinsee I, Smorgasbord III — all LIVE-owned, owner empire = player)
    mutate at NAME+0x28..0x30 on turn boundaries ONLY:
      NAME+0x28 u8   01 -> 02 at the FIRST boundary only (turn-counter-
                     shaped? colonized-age?)
      NAME+0x2a u8   per-turn increment PER-PLANET CONSTANT over 3 turns:
                     +3/turn Tensoric+Feculon, +2/turn Gasball+Freblinsee,
                     +1/turn Smorgasbord, and the byte STAYS 0 on all 146
                     uncolonized planets (0,1,2,3 deltas over 3 turns;
                     histogram {0:146, 3:1, 6:2, 9:2}). Production/income
                     accumulator shape [UNVERIFIED which channel].
      NAME+0x2c u8   0 -> 2 on the 4 faster-growing colonies, stays 0 on
                     Smorgasbord III.
      NAME+0x2e..30  ff ff ff -> small u24 value (35,21,36,19,0) at FIRST
                     boundary — 'unset' sentinel initialising.
  - The +3/+2/+1 per-planet rate is OQ-016 (income/growth formula) evidence:
    it's a per-planet CONSTANT (not global), correlates with colony set, and
    is measurable straight from these fields. Cross-check against
    extracted/ascend02 size/production tables + more turns (need 5+ to
    distinguish e.g. pop-growth vs build-queue accrual) rides with the
    adaptive capture.
  - Slot hygiene: slots 47..55 belong to the PREVIOUS campaign at the same
    base (grid names Ajax/Almaviva); campaign identity check is planet
    NAME@j, not slot index. Any census on a run MUST pin the campaign
    boundary via turn counter first.

### Adaptive capture run r1ad-20261006-131350 (2026-10-06d): boundary law holds
on a THIRD campaign; orbit law NOT reproduced under unknown screen state;
colonized-block increments refined.

Harness lessons (all fixed in scripts/r1_adcapture.sh):
  1. campaign-entry gate: 'cosmic exiles' needle is on the SETUP screen, not
     campaign-only -> false breaks. Reliable law: planet-grid hash at the
     pointer-law base changes when a game actually starts (residual residual
     names until then).
  2. autosave writes slots IN PLACE; a raw `cp` can catch a torn file
     (BadZipFile — hit ck001/ck011). Checkpoint now requires two identical
     Memory-member size reads 2 s apart before copying.
  3. dosbox -time-limit kills the game mid-drive if the tour slips; the
     adaptive phase must fit inside BOOT (600 s worked once the tour fired
     at t=75/100).

Verified this run (checkpoints ck008..ck016 = turns 0,0,0,0,0,1,1,2 on a
fresh Ephemera map, 157 planets):
  - TURN-BOUNDARY PLANET CHURN LAW reproduces: zero record change at five
    intra-turn checkpoint pairs; exactly 156/157 records change per turn
    boundary, mass-writer = NAME+0x57/0x5f pair again (offsets 87,88,89,95,
    96,97 top), plus the SAME handful: +0x2a/+0x2c/+0x2e block on exactly the
    5 colonized planets, +0x42..0x46 (4), +0x73 (4).
  - COLONIZED BLOCK dynamics (2nd campaign, clean slots): u8@NAME+0x28: 1->2
    at first boundary on 4/5 colonies (Ignatius I STAYS 1); u8@NAME+0x2a
    increments per turn: +2 on four colonies, +1 on Sophia I (0->1->2 over
    two boundaries; matches the 230146 per-planet +1/+2/+3 family — per-planet
    CONSTANT confirmed across campaigns); u24@NAME+0x2e: ff.. -> small value
    (65576, 65554, 65588, 1376273 = 0x150491) at first boundary EXCEPT
    Sophia I, which KEEPS 0xFFFFFFFF (unset) — initialization is per-colony
    conditional [semantics unverified; candidate: build-queue/economy slot].
  - ORBIT LAW REPRODUCES on this THIRD campaign (0/157 radius violations at
    both boundaries; same per-planet dtheta distribution family as 230146 —
    modes 355.0/357.3/351.1 deg, e.g. Hurble IV -0.82 deg/turn constant;
    quantized initial radii 896/672/544/384 all theta at 0/180 exactly on a
    fresh map — the generator seeds phase 0/180 with x/y assignment by
    sign). PITFALL THAT FAKED A CONTRADICTION for one full analysis pass:
    the orbit pair is f32 x @NAME+0x57 and f32 y @NAME+0x5f (8-BYTE GAP);
    NAME+0x5b..0x5e is padding that reads 0.0. Reading '<ff' CONSECUTIVELY
    from 0x57 yields (x, 0.0) and makes every orbit look radial. Always
    unpack the two components separately at their own offsets.
  - Star-chain law holds on the new map (chain of 50 from Ephemera k=0,
    idx==k; planet-pointer single-owner law: every planet LIVE-owned, 157
    distinct owners map-wide). STALE pointers are NOT campaign carryover:
    a brand-fresh map still has 43 off-grid/stale tail entries (2 stars even
    hold a duplicate LIVE entry: 159 LIVE pointer slots for 157 planets).
    Reading hardened: tails are allocator garbage; the LIVE prefix rule is
    the law, per-map orphan membership is generation-shaped.
