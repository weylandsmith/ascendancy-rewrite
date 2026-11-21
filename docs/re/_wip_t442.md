# t442 WIP — state-7 portrait PAINTER static hunt (offline, zero capture)

Goal (STATE.md t442): find the function that, on COSMOSWnd state 7, iterates
the race table and blits smrace<specnum> + racering k<colour> at the r=170
slots. Settle three NAMED caveats from t441: (a) angle pitch for n>4,
(b) count filter (rows vs known), (c) ring index byte +8 verbatim.

Inputs re-read this session: _wip_t441.md T2/T5/T6, ui-runtime.md t441 block,
_wip_t423c2.md C2-F1/F2 (string cluster 0x836e8: SMRACE template 0x83702
"HBDATA\SMRACE%02d.SHP" [corrupt H], LGRACE 0x83718; pointer census: only
0x23400->LGRACE + 0x23428->SMSHIP hold direct dwords, SMRACE/DKSHIP reached
by base+8/+16 arithmetic inside FUN_00023388; blitter family FUN_0001fc34
cache fetch + FUN_0005d5a1 affine stretch; race count word word[base+0xd88],
base 0x12e10, row stride 0x1ee).

## P0 — substrate checks [verified]
- work/ascend_restored.bin present (576643 B), Ghidra headless :8089 UP,
  program /ascend_restored.bin loaded (image_base 0, function_count 0 —
  names come from decompile-on-demand + functions_full.tsv spans).
- work/functions_full.tsv: 1144 rows (file_off, size HEX per t200 pitfall).
- Raw bytes 0x83704 == b'DATA\\SMRACE%02d.SHP\\x00DATA\\LGR' (string offsets
  consistent with t423c2).
- Sitting test: t368_ring_turn.py max_turn=1086 == baseline -> no new play,
  assignment stands.

## P1 — race-table consumer census [verified, capstone over 1143 tsv spans]
- Ghidra re-analysis of work/ascend_restored.bin: 1143 functions (matches tsv
  1144 rows incl header) — decompiles now work; earlier "No function" was an
  UNANALYZED program, not a wrong image.
- byte-pattern sweeps found NO 'RACERING' string and NO float32/float64 170.0
  constant and NO dword 0xaa (as standalone 4-byte) outside noise => the ring
  lib name is NOT a payload string (racering.shp must come via shape-lib index
  or a table), and r=170 is NOT an immediate float — likely an integer radius
  or computed.
- Functions touching stride 0x1ee AND byte +7 AND byte +8 (specnum+colour):
  0x156d4 0x196c8 0x19e94 0x20fd4 0x22878 0x22ce4 0x232ec 0x23388 0x2351c
  0x238e8 0x284bc 0x2925c 0x3d2fe 0x3ea54 0x3eb88 0x41260 0x41e34.
  Known: 0x232ec colour assign, 0x23388 preload (t423c2), 0x22ce4 big mgr
  (8805 B), 0x20fd4 main init.
- word[STATE+0xd88] disp32 census (mov/lea forms): 18 read sites all inside
  0x22ce4/0x232ec/0x23388/0x2547c/0x25604/0x2635c; 2 write sites (0x22d06,
  0x26123). 0x2635c = a SPREAD metric (pairwise 3D distance accumulators,
  writes word[mgr+0x32dd3]) — NOT the painter. 0x2547c = builds a filtered
  owner list (contacted bitset param_2+0x14/0x15, skips DAT_0007458e) then
  calls FUN_00041260/0x2a438/0x39c10/0x49f28 per owner — diplomacy/known-list
  family, not a painter.

## P2 — negative + structural census [verified]
- NO 'RACERING' string anywhere in the restored image (case-insensitive, 0 hits;
  only data\resring.shp x2 at 0x850c4/0x850d5 — a DIFFERENT lib, research-panel
  ring, consumers 0x48476/0x487ad per datafiles.md). NO float 170.0 (f32/f64) and
  no RACERING sprintf template => racering.shp records are NOT opened by name at
  runtime; the ring art must come from the SHAPE CACHE by index/name-table slot,
  and r=170 is NOT an immediate float.
- Shape-cache fetch = FUN_0001fc34 (130 call sites, 31 functions); affine blitter
  = FUN_0005d5a1 — callers are ONLY the window-item paint family:
  0x185d8, 0x18688, 0x1a1e0 (COSMOSWnd dispatch 0x18591, t423c2), 0x34a04, 0x3634a,
  0x37268, 0x3aa0a, 0x500e0. None is a race-row painter.
- Name-table insert FUN_0001fa60 has EXACTLY ONE caller: FUN_00023388 (4 inserts
  per race row: pools 0xb54 (SMRACE), LGRACE, SMSHIP, 0xb90; running slot idx
  starts 7). So smrace NN is fetched downstream by TABLE INDEX, not string.
- word[STATE+0xd88] disp32 consumers (exhaustive): 0x22ce4 (new-game init),
  0x232ec (colour assign), 0x23388 (preload), 0x2547c (known-owner list builder),
  0x25604, 0x2635c (spread metric). PAINTER NOT among them => it reads the race
  count from a mirror: DAT_00013b96._2_2_ is a second race-count (loop bound in
  0x3ef2c and 0x3aa0a) and DAT_0007458e = player owner index.
- Ruled out this session by decompile: 0x2635c (pairwise-distance metric),
  0x2547c (known list + AI-attack eval), 0x41260 (fleet/engagement AI),
  0x196c8/0x19e94 (ship animation state machines), 0x284bc (star/planet label
  sprite placement), 0x2925c (save/load of cosmos-wnd view params),
  0x3aa0a (COSMOSWnd msg dispatcher; species-related branches call
  0x3830c/0x38840/0x396cc), 0x16e4c/0x16f18 (fleet-cycle driver),
  0x16cf0 (window clip rects), 0x22878 (star-name gen), 0x156d4 (COSMOSWnd
  message handler: msg 0x320 sets byte[obj+0xab]=STATE and maps STATE->obj+0xb9
  {0->1,2->3,3->2}, then FUN_00016cf0 + vtable+0xc repaint; state 7 => b9 stays
  0 branch; NOT the portrait painter itself but the INVALIDATE path).
- COSMOSWnd class-name string sites: 0x8478b, 0x8578b, 0x857b2, 0x85a4a (next:
  class descriptor -> vtable paint slot).

## P3 — THE PAINTER REGION LOCATED + shape-slot indirection law [verified disasm]
- The species-screen painter lives in the UNINDEXED GAP 0x2c4ec..0x2c90a (no
  functions_full.tsv row; Ghidra auto-analysis found 1143 fns = tsv count, so
  every GAP body is deliberately opaque to tsv tooling — disasm via
  scripts/t442_disasm.py). Caller chain INTO the region: 0x2b774->0x2c034,
  0x2b866->0x2c126, 0x2b94e->0x2c40e, 0x2ba35->0x2c4f5, 0x2bb09->0x2c2c9 (one
  caller function, itself GAP ~0x2b3d2..0x2bf90, dispatches via jumptable
  0x2bf90 on byte[0x43510] (display state)).
- SHAPE-SLOT INDIRECT TABLE (the answer to "no RACERING string"): a boot-patch
  table at 0x32f0..~0x3478 of 10-byte entries {u16 opcode 0x0710, u32 dst,
  u32 val} (decoder scripts/t442_bootpatch.py) writes shape-cache slot words:
    0x6fd9a <- 6         (a fixed shape id)
    0x6fd96 <- 0x76      (118; the RING shape slot — painter reads word[0x6fd96])
    0x6fd52 <- 0x12e10   (race-table base -> per-owner SMRACE slot array)
    0x6fd44 <- 0x48c44 ; 0x6fd60 <- 0x6fd06?? ; 0x6fd38 <- 0x9f10c (shape cache)
    0x48c44 <- 11 ; 0x4850c <- 4 ; 0x13b96 <- 14 (draw-list capacity words)
    0x7458e <- -1 initial (player owner), 0x43510/0x43489 etc.
  The painter then fetches via FUN_0001fc34(cache=0x9f10c, shapeId=word[slot]).
- PAINTER LOOP (0x2c823..0x2c90a, capstone-verbatim): bound =
  `eax>>16` of dword[0x13b96] (race count mirror); per row k:
    0x2c867: mov ax, word [eax*2 + 0x6fd44]  (colour-indexed slot, eax=row k)
    0x2c878: call 0x1fc34 ; 0x2c883: call 0x5d5a1   (blit #1)
    0x2c892: mov ax, word [0x6fd96]  (RING shape) ; 0x2c8ae: call 0x1fc34
    0x2c8ba: call 0x53e58 (rect intersect) ; 0x2c8cc: call 0x53dd8 (blit #2)
    0x2c8d3..0x2c8fa: dl = byte[0x12e16 + owner*0x1ee + 0x1c0] (relation matrix
      row for PLAYER: cmp dl,3 -> WAR branch 0x2c7c7 sets ebx=8, else ebx=3/-1
      — the ring FRAME choice by relation!)
    loop steps esi += 0x3e (62), edi += ..., ebp += 2  — LINEAR STRIP positions,
    NOT the r=170 ring. Also at 0x2c83a: k==4 special-cases esi=0x15b edi=0x85.
  CAUTION [unverified interpretation]: 0x15b/0x13cb are ALSO plausible as
  cosmos.cpp LINE NUMBERS passed to debug helpers 0x340e8/0x2a428 (those calls
  take line-number first args elsewhere in the region: 0x2c436 call 0x2a428 with
  ebx=0x3b3 edx=0x83f55 = file/line). So esi/edi may be coordinates carried in
  registers that HAPPEN to be reloaded with line numbers on error paths. The
  strip pitch 62 and k==4 override do not match the measured r=170 cardinal
  ring => this loop is likely the RIGHT-COLUMN race list (RACE_1..7 windows.txt,
  flag faces word[0x6fd44+k*2] = SMRACE by COLOUR — consistent with t441's
  colour-byte law at the row-ink site!) and the portrait-ring blits 0x2c772
  (word[0x6fd52+owner*2] via player) + 0x2c7e4 (ring) inside the same function
  are the species-screen PORTRAITS.
- FUN_0001fc34 shape-cache fetch law [verified decompile]: cache obj 0x9f10c,
  slot table at obj+0x7cd+id*0x32 (name entries, 200 max), item ptrs obj+id*4,
  LRU list obj+0x63e/0x640 — ids are GLOBAL shape-lib slots, which is why no
  per-file string appears at the painter.
- Trig helper family [verified]: FUN_00077514 = fsin wrapper, FUN_00077556 =
  sin/cos pair (callers 0x26cb5 GAP, 0x3ef2c race-row orbit, 0x53210 GAP,
  0x5324c rotation-matrix apply). No float-170 constant anywhere (P2) => ring
  radius 170 must be an INTEGER computation or a table read in the painter.

## T-OPEN handoff (next iteration resume here)
1. Full linear disasm 0x2b3d2..0x2c050 and 0x2c90a..0x2cf04 (region ends) to
   attribute esi/edi precisely (coordinates vs line numbers) — print ONLY
   windows around 0x2c700..0x2c830 with operand tracking.
2. Read slot VALUES at runtime-equivalent boot state: after applying the
   0x32f0 boot table, what shape id sits at word[0x6fd52+owner*2]? The race
   table base 0x12e10 is written there — so word[0x6fd52+2*o] = SMRACE shape id
   per owner — VERIFY the stride-2 word array vs stride 0x1ee (the boot entry
   writes the BASE; the painter indexes owner*2 — so a DIFFERENT per-owner word
   array must live at 0x6fd52... check overlaps with the boot table's other
   writes 0x6fd60/0x6fd38).
3. The relation gate at 0x2c8ec (relation==3 WAR -> ebx=8) picks the ring frame:
   candidate law "ring shape 118 drawn in 2 frames (relation-styled)" — check
   racering.shp record count (t423c2: racering k0 53x53; census how many recs).
4. Do NOT re-measure t441 image laws. The r=170 cardinal law STANDS from image
   evidence; the code hunt must explain it or contradict it with cited disasm.
