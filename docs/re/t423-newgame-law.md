# t423 — New Game screen cycle: wheel/spin/preview/starfield laws (LANDED 2026-11-17)

Task: PHASE-16 row t423 (seed defects D17 a–g). Full working log:
docs/re/_wip_t423.md (F0–F10); this doc is the law summary. All addresses
are base-0 restored-image (work/ascend_restored.bin) unless noted.

## 1. State-3 window table [verified windows.txt L575-684, F0]
TYPE 100 STATENUMBER 3 -> DATA\3CFGNEW.SHP. Objects (all STATE "1 3"):
NEWGAMEWND (334,12-488,364 SF0); GALAXY_MORE SENDMESSAGE 501; PLAYERS_MORE
503; DIFFICULTYMORE 505; Player^Color (379,381-493,419) MSG 0; RACELIST
TYPE 10 (502,45-632,372) SF7. beginnew.txt is the TUTORIAL script (9 help
pages, every button msg 0) — the queue row's premise that it names the
per-state records is FALSE. The per-state record is a RUNTIME field: the
SHAPEITEM parse law writes child+0x72 = frame idx at paint time (F1),
which is why windows.txt shows k0 for all three wheels.

## 2. WHEEL FRAME LAW [verified dispatcher 0x528eb..0x52f54, capstone, F1]
Counter fields on the window mgr: +0xb5 hi = density idx (mod 5), +0xb7
hi = species COUNT (3..7, wraps at 8->3), +0xb9 hi = atmosphere val
(0..2). Frame stores into the child's +0x72:
- density    -> 3cfgnew k(densityIdx)        k0..k4
- species    -> 3cfgnew k(count + 2)         k5..k9  (Five -> k7 == t401
  S8 anchor; 0x52ec9 `add edx,2`)
- atmosphere -> 3cfgnew k(10 + val)          k10/11/12 (k12 = Hostile)
Star counts live in the 5-dword table @0x895c8 = {15,25,50,75,100}; the
port's ladder {50,75,100,15,25} is the same ring (t78 live witness), and
its sorted-rank mapping is the same count->k0..k4 bijection — EQUIVALENT
(F3-correction: the WIP "species off-by-three" was a misread; the port
already returns 2+value for value 3..7).

## 3. k12 HOSTILE ORB: shipped-archive truncation + partial paint [verified F5b]
3cfgnew.shp k12 (84x79, bbox (30,25,84,79) => 55x55 glyph) ends mid-row
~55/79 IN THE SHIPPED ARCHIVE: ascend01.cob entry data\3cfgnew.shp blob
size 27349, md5 b2550068bb6260f8980d5de65d680db4 == extracted twin
(scripts/t423_f5_sibling.py). k0..k11 streams are exactly span-sized and
desync into the next record (t197 X class). The vendor blit has no length
arg (shp.md S20.2) so the vendor paints the glyph rows + resident bytes;
the port's whole-record refusal was a PORT bug. FIX: walkRows partialOk
for the LAST record only (rewrite/src/formats/shp.{h,cpp}); rows below
EOF stay untouched (named seam: past-EOF bytes are vendor heap). Witness:
scripts/t423_hostile_shot.sh -> /tmp/t423_shots/t423-hostile.png shows the
red spiked orb + "Hostile Atmosphere" (pre-fix: blank panel). Test pin
flipped: TEST shp_span_free_t197 now asserts k12 decodes with glyph
content rows 25..50 nonzero.

## 4. PREVIEW STARFIELD: volume placement + sprite law [verified FUN_00022728, F4/F8/F9]
Density click -> FUN_000226e4 regenerate = FUN_00022878 (full galaxy gen,
N=100 LCG candidates) -> FUN_00022728 (preview table stride 0xd, base
DAT_0003067e) -> FUN_000234a4 (galaxy GRAPH post-process, NOT a paint
site) -> FUN_00022ce4 (race assignment). FUN_00022728 per star: vector
(·, 1000.0, 300.0, 0) rotated about Y by rand%seedword via FUN_0005324c,
then z += rand%600 - 300. => circle radius 300, depth 1000 +- 300 = a
FILLED CYLINDER VOLUME (the D17 "fills the VOLUME not a shell" complaint
was against the port's sphere-SHELL model). RNG = Borland LCG
FUN_0007824f — the preview IS a rand() consumer (no conflict with
R-t422c: that census covered chrome paint paths, not this click path).
Sprite law: COSMOSWnd STAR_SHAPES = cos_star.shp via SEL = 4*K + cls,
cls 4-band ladder on transformed depth (>=220/1..219/-220..0/<=-220;
planets-ui.md §6). cos_star census (scripts/t423_f5b_decode.py): k1..k15
2x2, k16..k39 1x1, k40..k51 zero-header (cannot-draw, banked), k52 3x6,
k53/k54 8x8 in 17x17 bbox. The stride-0xd preview records carry NO type
byte => K=0 (NAMED SEAM) -> k1..k3 native 2x2 (larger than the old 1px
point; pixelated per the record). Port edit: title.cpp preview block.

## 5. BEGIN-BUTTON SPIN PUMP [verified F2/F7]
The Begin box is NOT a windows.txt object (negative re-confirmed) — no
SENDMESSAGE route exists. The spin rides the mouse: dispatcher 0x52993 /
0x529c1 call FUN_00056ad4(0x7a35c, 5, @0x69b8|@0x69c4) when the cursor is
inside x379..493 y420..472 (cmp ebx 0x17b/0x1ed, ecx 0x1a4/0x1d8).
FUN_00056ad4 = timer/script arm; script @0x69b8 bytes
`02 8e450700 | 07 003b0e` = op2 SET ds:0x7458e (verified restored bytes),
the specnum global the cosmos repaint reads (43 xrefs; sole writer
FUN_00021a84; ZERO writers inside the state-3 dispatcher). Port law: yaw
advances kPreviewSpinPerFrame x6 while that zone is hovered, on top of the
idle spin (exact vendor pump rate UNMEASURED — named seam).

## 6. RINGS = racering.shp RECORD [verified census + witness, F8]
racering.shp: 8 records, k0 53x53 walk-OK (bbox zero header), k1..k7
53x53 bbox(-55,-55,53,53). The measured ring radius 53 (t401) == record
53 drawn 2x — the SAME class scale as the smrace portraits (49 -> 98,
t401 S8 measured zone 96..109). Port: blitShapeScaled(racering k0, 2) at
both ring sites (desc panel + race-list rows), 1px vector fallback only
on lib refusal (defect e).

## 7. Player-colour chips [verified F2]
Zone x379..493 y420..472, 16-px chips from x=379 (idx = (x-0x17b)>>4);
click -> FUN_0004fb30(0x78638,0) + word [win+0xb5]=idx + FUN_000232ec
(0x12e10, idx) re-assigns race-slot colours (stride 0x1ee arrays,
rand()%7 distinct-adjacent via LCG). Port paints the seven MEASURED chips
(t414) but the click-reassign behaviour is NOT ported — owed.

## 8. 3cfgnew.tmp = sparse chrome layer, not a screenshot [verified F6]
Magic '1.10', count=1 tsz=16, ONE record dims (479,639) swapped pair =
639x479; k0-law walk completes 479/479 rows but only ~10% pixels non-
transparent: dense bands rows 0..47 + 368..479 and columns x<64, x>=448 —
the screen's saved CHROME FRAME layer (texture margins), no wheel/
starfield content. Grading use: frame extents only. Sibling .tmp files
(10status, 1starmap, 7racesel, ...) are the same class.

## DEFECT SCOREBOARD (D17 a–g)
- (a) wheel icons repeat: law-equivalence established (SS2); the pre-t414
  k0,k1,k2,k2,k3 mapping was the repeat; t414 bijection + this law
  confirm distinct k per step. Witness shot: three distinct panel arts.
- (b) hostile variant missing: FIXED (SS3, witness shot).
- (c) extra art below circles: the vendor draws ONE record per wheel
  (child+0x72); the port's panel-clip already models the visible result;
  k12 partial paint is consistent (SS3). No further port delta.
- (d) species + planet art 4x: NOT closed. Measured law remains 2x
  (t401 S8 zone 96..109 == 49x2; racering 53 == kDescRingR). The vendor
  scale-source (TYPE 10 list handler / window-class scale field) is NOT
  yet decompiled — carried to the next cycle.
- (e) rings thick textured: FIXED via racering k0 record (SS6, witness).
- (f) starfield volume + larger pixelated stars: FIXED placement law +
  cos_star sprites (SS4, witness: stars spread through the rect).
- (g) Begin-button spin pump: FIXED hover pump x6 (SS5); the exact vendor
  rate and the ds:0x7458e semantics beyond "repaint reads it" are named
  seams (op 0x07 imm 0x3b UNDECODED).

## PORT CHANGE SITES
rewrite/src/formats/shp.{h,cpp} (last-record partial walk),
rewrite/src/ui/title.cpp (preview volume+sprites+hover pump; racering at
both ring sites; k12 refusal comment), rewrite/tests/test_shp.cpp (k12
pin flipped). Tests 421/0/0; gate GATE_EXIT=0; ledger 17/3 unchanged
(OQ-005 residue note updated with the shipped-archive measurement).
