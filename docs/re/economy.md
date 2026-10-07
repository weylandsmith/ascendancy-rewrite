# items and planetary economy — `planitem.txt` measurement
Source: `extracted/ascend00/planitem.txt` (3,180 B, CP437/CRLF, 0x1A EOF). Vendor-documented above `#`; produced by `scripts/gizmo_probe.py`; gate stage 3j.

## 1. Item grammar [verified against 39/39 records]
```
NAME IND RES PROS MPOP UPOP COST REQUIRES {flags} 255
```
(vendor header line, verbatim: `NAME IND RES PROS MPOP UPOP COST   REQ      FLAG DELIMITER`). Field roles by that header: IND/RES/PROS = industry/research/prosperity contribution; MPOP/UPOP = pop maintenance/upkeep pop; COST = industry; REQUIRES = restree node or 255. Field counts vary 8/9/10 because the flag list, when present, shares the 255 terminator — same trap as gizmos.md §1.
- **39 items** after the count triple `39 22 9`. The `39` equals the record count (verified). `22` and `9` match no property we could test (sentinel REQUIRES: 6; gated: 33; rows with a flag list: 19; nonzero IND/RES/PROS/MPOP/UPOP: 5/6/4/35/39) — semantics unknown, OQ-014; recorded verbatim, never forced. Names unique.
- REQUIRES (field 7 of the row, v[6]): 33 rows carry real restree indices, 5 rows carry 255 (vendor: no research required), and exactly ONE row — Interstellar Trucking — carries **254**, a second sentinel the vendor comment does not define (OQ-014). Sampled gates are semantically coherent (Shipyard->Orbital Structures, Terraforming->Planetary Replenishment, Surface Shield->Superconductivity), which cross-validates the restree row numbering a third time.
- parse trap (caught by this probe mid-run): testing v[7] for tech-range passes VACUOUSLY because flag bit-positions 0..7 also fall in [0, 106). Always test the vendor-named field index, not a neighbour.
- CONTROL (disambiguates v[6] vs v[7] on the 19 longer rows): reading v[7] as REQUIRES gives semantically broken gates — Surface Shield -> Spacetime Surfing, Orbital Missile Base -> Tonklin Diary, Terraforming -> Orbital Structures. The v[6] reading gives Surface Shield -> Superconductivity, Orbital Missile Base -> Power Conversion, Terraforming -> Planetary Replenishment. Vendor header order + meaning both select v[6]; v[7..] are the flag bit-positions.

## 2. Planet-type order and grids [verified, semantics inferred]
- vendor lists the order: HUSK PRIMORDIAL CONGENIAL EDEN MINING MOFFET CHAPEL CATHEDRAL RICH TYCOON CORNUCOPIA (11 types).
- numeric blocks between `#` and the count triple, shapes [(1, 1), (11, 4), (5, 15), (5, 15)]:
  - `50` alone = "pop growth amount" (vendor sentence: *first, note we have pop growth amount number*).
  - 11x4 = per planet type: first column reads as a decline curve (100,50,20,0,...) and cols 2-4 as [?]. Semantics NOT documented -> OQ-014.
  - 5x15 and 5x15 = two more matrices (rows = 5 of something; cols = 15). Values 0..9, ridge-shaped. Semantics undocumented -> OQ-014.

## 3. Full item table
```
Factory                1 0 0 0 1 30 255 255
Agriplot               0 0 2 0 1 30 255 255
Laboratory             0 1 0 0 1 50 255 255
Habitat                0 0 2 3 1 160 26 255
Metroplex              1 1 1 2 1 200 31 255
Colony^Base            1 0 1 2 1 120 5 0 255
Industrial^Megafacility 3 0 0 0 1 110 22 255
Artificial^Hydroponifer 0 0 3 0 1 100 10 255
Research^Campus        0 3 0 0 1 160 14 255
Logic^Factory          0 1 1 0 1 80 41 255
Engineering^Retreat    1 1 0 0 1 80 45 255
Surface^Cloaker        0 0 0 0 1 40 15 255
Hyperpower^Plant       0 0 0 0 1 200 25 255
Fertilization^Plant    0 0 0 0 1 200 52 255
Internet               0 0 0 0 1 250 59 255
Cloning^Plant          0 0 0 0 1 250 38 255
Observation^Installation 0 0 0 0 1 40 20 255
Tractor^Beam           0 0 0 0 1 50 34 2 255
Surface^Shield         0 0 0 0 1 100 4 3 255
Surface^Mega^Shield    0 0 0 0 1 180 61 3 255
Outpost                0 0 0 1 1 120 255 6 255
Transport^Tubes        0 0 0 0 1 10 255 0 6 255
Shipyard               1 0 0 0 1 240 0 255
Ship                   0 0 0 0 1 20 1 255
Orbital^Docks          1 0 0 0 1 170 16 255
Orbital^Cloaker        0 0 0 0 1 40 15 255
Orbital^Shield         0 0 0 0 1 60 0 3 255
Orbital^Mega^Shield    0 0 0 0 1 120 43 3 255
Orbital^Missile^Base   0 0 0 0 1 60 9 2 255
Short^Range^Orbital^Whopper 0 0 0 0 1 90 37 2 255
Long^Range^Orbital^Whopper 0 0 0 0 1 180 61 2 255
Alien^Hospitality      0 0 0 0 0 1 20 1 5 255
Interstellar^Trucking  0 0 0 0 0 1 254 1 5 255
Endless^Party          0 0 0 0 0 1 41 1 5 255
Scientist^Takeover     0 0 0 0 0 1 32 1 5 255
Automation             0 0 0 0 1 1 51 0 255
Terraforming           0 0 0 0 1 50 26 0 255
Lush^Growth^Bomb       0 0 0 0 1 200 62 1 255
Xeno^Archeological^Dig 0 0 0 0 1 50 6 0 255
```

## 6. Colony income recomputation law — FUN_00038ba4 (OQ-016 income half, t18)

Static law [verified, work/ascend_restored.bin disassembly 0x38ba4..0x38f65;
the Ghidra decompiler mangles several slot offsets, so every claim below cites
raw instructions]. Callers: FUN_00037d80 (build/dismantle), FUN_00038840
(governor/slot ops), FUN_00038f68 (per-planet turn tick), FUN_0003a174,
FUN_0003aa0a (system event dispatch).

Planet record stride 123, base = planet-NAME - 0x24 (OQ-014 anchor law).
Slot array pointer = u32[rec+0x10] READ RAW (@0x38c8b `MOV ESI,[EBX+0x10]`,
loop @0x38c7d bounds `u16[rec+0x1a]` = cap; member = ESI+EDX, EDX += 4 —
no -0x88 rebasing, an earlier draft of this section was WRONG). Slot dword:
byte0 terrain class, byte1 itemIdx (0xff = empty), u16 flags @+2 (bit0 ACTIVE).
Item record stride 0x28 at Ghidra 0x73e40 (`IMUL EAX,0x28; ADD 0x73e40`
@0x38c97/0x38c9a): byte0 IND, +1 RES, +2 PROS, +3 MPOP, +4 UPOP, u16@6 flags.

Accounting loop, per slot i in [0, cap):
  empty (item 0xff) @0x38c4d:  i >= u16[rec+0x18]  -> c1e++            (+0x1e)
                               else cls&8           -> nothing
                               else c0++ (cls==0 additionally c20++)   (+0x1c/+0x20)
  ACTIVE (u16 bit0) @0x38cbe..0x38d1f:
       IND  += s8 item.IND  (+1 extra if slot cls==2) @0x38cc4/0x38cce
       PROS += s8 item.PROS (+1 extra if slot cls==3) @0x38cde/0x38cf2
       RES  += s8 item.RES  (+1 extra if slot cls==4) @0x38d07/0x38d17
       item flags&4 -> c24++ (byte +0x58) and NOTHING ELSE for that slot
         (@0x38d23 tests [item+6]&4, jumps past the MPOP block);
       else { if item flags&8 -> c59++ (byte +0x59) @0x38be5; c4a += MPOP }
  INACTIVE with item @0x38c07: skip item 23 (Ship), skip slot flag&2, skip
       item flags&0x40, else c18 += UPOP                                (+0x4c)

Post-loop @0x38d3f/0x38d7a/0x38db5 (slot finder FUN_0003958c = first slot
whose byte1 == k, returns 0xffff if none): if that slot's u16 flag bit0 is set,
  k=12 Hyperpower Plant -> IND  += IND>>1
  k=13 Fertilization    -> PROS += PROS>>1
  k=14 Internet         -> RES  += RES>>1
Governor byte @+0x54 (0xff = none) @0x38df0: value 0x21 -> PROS += IND>>2;
value 0x22 -> RES += IND>>2; value 0x23 -> c18 += (DAT_000743b9>>16).

Compression @0x38e2d..0x38e89 (both channels, ONLY if accumulator != 0;
V==0 skips the block and stores 0): `FILD dword (V+1)` ; `FSTP qword` ; CALL
0x78a90 = pow (stack args base=V+1 at [ESP'+4], exp=0x3FEB333333333333 at
[ESP'+0xc], verified by manual ESP walk; callee 0x78954 = MSVC pow core) ;
CALL 0x76e08 ; `FISTP` back. 0x76e08 is NOT round-half: it sets control word
high byte to 0x1f -> RC=11 = FRNDINT TOWARD ZERO (@0x76e11). Banked:
V = trunc((V+1)^0.85) double. Live check: acc1->1, acc2->2, acc3->2
(trunc 4^0.85 = 2.9970) — all acc>=1 records fit; the earlier
"round((V+1)^0.85)" draft was WRONG (banker's/round would give acc3->3). Prosperity then loses upkeep:
  PROS -= (i16[rec+0x42] SAR 2)  @0x38e8d (arithmetic shift = floor-div 4),
  floored at 0 @0x38eac. Industry and Research are NOT reduced by +0x42.
Research is LINEAR (no pow) — no compression block exists on that channel.

Tail clamps @0x38f01..0x38f58: c4a = clamp(0..100) into +0x4a;
u = max(0, min(u16[+0x42], c4a)) back into +0x42; c18 = clamp(0..u) into +0x4c.
Stores @0x38eb4..0x38efe: +0x1c=c0 +0x20=c20 +0x1e=c1e +0x44=IND +0x46=RES
+0x48=PROS +0x4a=c4a +0x4c=c18 +0x58=c24 +0x59=c59.

POP GROWTH (same tick path, FUN_00038f68, t18): counter word +0x4e accumulates
`+ i16[+0x12]` (per-turn growth from slot ops) and gains +1 for non-owner when
i16[+0x12] < 4; once `u16[+0x4e] >= DAT_000066e4` (Ghidra 0x66e4 = raw word
0x0700 — value NOT yet interpreted; the region is pointer-fixup territory) the
counter resets to 0, u16[+0x42] += 1, plus +1 more if the first ACTIVE slot's
bit0 is set, then capped to +0x4a. `DAT_000066e4` semantics = OPEN below.

LIVE VERIFICATION STATUS (battery scripts/r1_income_fit.py, 139 owned records
across every R1 capture's last slot): accumulator structure reproduces the
empty-slot census family exactly (u16[+0x1e]==10 on 153/153 records — the
cap-cells reservation; u16[+0x1c]==cells on 115/153). It does NOT reproduce
+0x44/+0x48: 52/139 records match, and the dominant residual is exactly
acc=(0,0) vs stored=(1,1) on facility-free owned planets (79 records), plus
one non-monotone point (INDpre 3 -> stored 2). That pattern is NOT producible
by any monotone post-transform of the accumulators, so at least one term is
missing from the loop model — candidates in priority order: (a) species-record
per-planet-type IND/PROS modifiers (species table DAT_00013bc4 stride 0x60
holds nonzero small bytes at +0x15..+0x17 that no code site in the recalc
reads — readers not yet censused), (b) captured slots are load-time stale
values (recalc does not run on load, so early-game values bake a pre-pow
base), (c) an accumulator initialised outside 0x38ba4 (all eight accumulators
are zeroed at entry @0x38bb5..0x38bd0, which argues against (c)).
HONEST STATUS: loop structure banked [verified]; curve and base OPEN.

Rewrite status: campaign.cpp currently charges gizmo/facility IND as file
values with no pow compression and no governor channel; DO NOT upgrade to
round((V+1)^0.85) until the base term resolves — a pow-only upgrade would
regress colony output against captured originals (stored values sit ABOVE
the pow curve at V=0..1: stored 1 where pow gives 1, stored 2 where pow gives
2/1 ambiguously). Blocked-on-decision entry: docs/BLOCKED.md OQ-016-base.
