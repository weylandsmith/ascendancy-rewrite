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

---

# CYCLE 2 ADDENDUM (t423 CONT cycle 2, LANDED 2026-11-18)

Full working log: docs/re/_wip_t423c2.md (C2-F0..F7). Laws below SUPERSEDE
cycle-1 SS6/SS7 where noted.

## 9. RING LAW REFINED: racering index == player-colour index [verified]
racering.shp is 8 COLOUR-TINTED 53x53 rings (run-decoded dominant palette
colours, game.pal 6-bit): k0 green (0,141,68), k1 purple, k2 yellow, k3
pink, k4 tan, k5 blue, k6 orange, k7 NEUTRAL GREY (28,28,28)+(165,165,165)
— the SAME 7 hues + neutral as the measured chip palette (t414 S2d), same
order. SITE LAW (pinned-original census C2-F6): DESC ring =
racering k<playerColourIdx> (capture default 0; measured (0,142,69) == k0
(0,141,68) exact); RACELIST row rings = racering k7 NEUTRAL (row ring
edges greys 35..186, ZERO chroma pixels). Cycle-1's fixed k0 at both sites
was a port bug for every non-green race and for the rows. Port: title.cpp
DESC ring blitShapeScaled(racering, playerColourIdx, 2); rows k7.

## 10. PLAYER-COLOUR REASSIGN LAW [verified capstone 0x232ec..0x23385]
windows.txt MSG 0 on Player^Color means "sends no message" — the handler
IS REAL (0x529d2): zone x379..493 y420..472 (BELOW the windows.txt label
rect), chip idx = (x-0x17b)>>4 (16-px grid from 379; idx 0..7 reachable);
FUN_000232ec(0x12e10, idx): byte[raceRow0+8]=idx VERBATIM (7 = neutral
allowed); for i=1..count-1 (guard 1 < word[base+0xd88]) draw cand =
rand()%7 (Borland LCG FUN_0007824f) re-picked while cand equals any
ALREADY-WRITTEN out[j] (scan bound j<i — the first decompiler read
INVERTED the collision flag; capstone settles it). All count colours
DISTINCT; player keeps the clicked idx. Colour index field = race-record
byte +8 (stride 0x1ee); +7 = species lib id (FUN_00023388 preload law).
FUN_00020fd4 (init) runs the SAME routine at startup — initial colours
are a default-idx call of it. PORT: menulaw.cpp newgameChipAt +
assignRaceColours (pure, tested test_racecolour_t423c.cpp); title.cpp chip
click -> reassign + DESC ring follows. Witness scripts/t423c_chip_shot.sh:
click (435,446) -> log "player colour idx 3", DESC ring green->pink,
1105-px diff. NAMED SEAMS: LCG seed value (vendor srand chain from saved
state; no cited fresh-game initial), and the 78 stride-0x1ee consumers of
byte+8 in the CAMPAIGN (map tints etc.) — traced to ui/kOwnerRgb only
partially; the campaign-side colour plumbing stays owed (cycle 3).

## 11. SCALE LAW (d) — HONEST NEGATIVE [measurements + elimination]
Planet: measured chromatic zone w38 (t401 37) vs planets.shp 35px class
NATIVE — no scaling evidence; port stands (group mapping = named seam).
Portrait: art run 94..101 px (this session, rows 2/3 chromatic bboxes 97
x 94 and 94 x 73) vs smrace 49x49; FULL-ARCHIVE census: NO lib has a
~98 SQUARE record (only planal* 103x103, planind/pro/res 107x99 = building
art, sg48expl k8 93x98 explosion); lgrace 296x199 stretched to 98 wide =
66 tall (wrong aspect, and lgrace is the race-INTRO full portrait per the
0x23388 preload cluster). => vendor draws smrace STRETCHED 2x via the
cited affine blitter FUN_0005d5a1; the per-site scale SOURCE (TYPE-10
paint field) was NOT located: RACELIST string has ZERO data refs (the
0x52xxx dispatcher family matches window objects by other means; class
vtable slot for TYPE 10 unidentified; restored-DB coverage sparse).
"2x" is a MEASURED law (two independent bboxes + elimination census), NOT
a cited field read. Defect (d): grade-clean in the t412 witness, LAW
UNCLOSED — cycle 3 owns the TYPE-10 paint-site hunt (route: walk the
0x52xxx handler family's invalidate/paint vtable via [win+0xa7]+0xc, or
live-RAM frame pair).


---

## SS12 — Paint-vtable architecture + cited stretch paint site (t423 cycle 3)

PAINT DISPATCH [verified disasm 0x52daa/0x52e28/0x52e49 + ctor census
scripts/t423c3_a7census.py]: window objects carry a class vtable pointer at
field +0xa7; invalidate/repaint = `call dword [win+0xa7]+0xc` (eax=window,
edx=0). FOUR classes register data-pool vtables (ctors 0x1abe6/0x31c5a/
0x4d956/0x5b265 -> 0x88498/0x88838/0x88ac4/0x88c24, stride-4 entries, slot
+0xc = 3rd entry). Base defaults recur: 0x30d08/0x311b8/0x316f0. The
low-region (+0xa7) imms in the census land in the script region = a
DIFFERENT object class (movsd chains), not vtables. PITFALL: 0x49359
`mov [ebx+0xa7],ecx` is a memset ZEROING loop, not a registration.

GENERIC SHAPEITEM-LIST PAINT (vtable 0x88838 slot 0x32314) [verified disasm]:
fetch FUN_0001fc34(cache 0x9f10c, sel=word[win+0x18]) -> FUN_0005caac NATIVE
1:1 run-decode blit; then loop child records (stride 0xe at [win+0xab], count
word[win+0xaf]): child+0xa type byte -> jump table 0x322f4 (tint 0..4; >7
asserts shapefile.cpp:0x186b) -> SAME lib re-fetch sel=type+child[0xa], blit
at child rect minus window origin. FUN_0005caac is THE native blitter
(75 call sites; RLE, zero scale math).

CITED STRETCH PAINT SITE FOR THE NEW-GAME PORTRAIT (defect d) [verified
disasm 0x526b4 whole function; sole rel32 caller 0x52174]: the state-3 paint
function (frame bounds x379..632 y472 == bottom panel EXACT) contains at
0x52834..0x52877: push (0, 0x8000, 0x8000, 0, rect@0x48c44, [win+0xb1]>>16,
colour 0x62, sel=word ds:[0x6fd98]) -> FUN_0001fc34 -> FUN_0005d5a1. Per the
blitter's head (decompile): (param_7,8,9)==(0,0x10000,0x10000) = identity ->
plain native path; the site's 0x8000 args are 16.16 AFFINE parameters fed to
FUN_000604e9 (sin/cos vertex builder, table 0x8408..0x8457) — a NON-IDENTITY
stretched draw of the selector's record AT THIS SITE. The 0x62=98 immediate
is the COLOUR arg (pal[62] frame-colour law t415), NOT a width (the
w=0x62=98 coincidence is superseded). Exact param semantics UNRESOLVED
statically (cdecl stack model defeats the decompiler; the cosmos site 0x18635
pushes an FPU-computed size into the same slots) — MEASURED 2x (C2-F4
elimination census) remains the operative scale law; the remaining named
seam = selector word ds:[0x6fd98] -> record binding (decider: live BPLM at
0x52867 reading ecx/edx).

CHIP ROW + CLICK FULL CHAIN [verified disasm 0x525eb..0x52647 + 0x529d2]:
8 native chip blits x=379+16i (sel word ds:[0x6fd84]) via 0x53ee0 (tinted
blit — builds a 5-entry ramp pal[byte*4+0x13 - k] from the race-record +8
colour byte, then 0x5cf96); selected slot (si==word[win+0xb5]) paints the
0xf3 well instead. Click: zone test x379..493 y420..472 -> idx=(x-379)>>4 ->
STORE word[win+0xb5] -> FUN_000232ec(0x12e10, idx) -> [win+0xa7]+0xc repaint.
The port's click->assign->ring-update law is EXACT including the field.
[SS12 READING CORRECTED by tNG-C: SEVEN blits at 381+16i (seed ebx=0x17d,
loop cmp 7 at 0x525ee), 0x53ee0 rewrites FOUR slots 16..19 := pal[16+4i..
19+4i] (not a 5-entry ramp), and the selected chip gets a WHITE FRAME, not
"the 0xf3 well" — 0xf3=pal243=(255,255,255), drawn via FUN_0002fe04 line
family. SS14 below is the cited law.]

## SS14 — DESC PLANET INDEX LAW (tNG-C cycle 1+2, D19 seed #2 CLOSED)

[verified disasm 0x5231d..0x5236d + bbox census + windows.txt L584] The
DESC-panel planet is smhome.shp record k<SELECTED RACE ROW> (word[win+
0xb3]), NATIVE 1:1 via 0x5caac, pushed at NEWGAMEWND-relative (72,205).
windows.txt NEWGAMEWND X0=334 Y0=12 -> anchor screen (406,217); every
smhome record's bbox quad = (-24,-26,27,25) -> content 52x52 at screen
(382,191). Bounds 0x523b1: race row < 0x15 == 21 records (assert). The
t414 planets.shp k[(sel%11)*5+1] size-class mapping was INVENTED and is
REPLACED. Port site title.cpp smhomeLib; constants kDescPlanetCentre
{406,217}; pins test_newgame_content_tNGC tngc_smhome_index_law; witness
scripts/r1_tNGC_chip_witness.py planet zone (52+-2 measured 51x51 vendor,
51x50 ours).

## SS15 — CHIP ROW LAW (tNG-C cycle 1+2, D19 seed #4 CLOSED)

[verified head 0x5258d..0x52647 + FUN_00053ee0 decompile + refcap census]
SEVEN blits, chip i rect (381+16i,433)..(395+16i,463); record = raceflag
k<word[+0xb3] SELECTED race row> (0x525f6/0x52603), 15x25 content, bbox
(0,0) -> emblem occupies rows 433..457. Chip i renders with palette slots
16..19 := game.pal[16+4i..19+4i] (0x53ee0 four-slot rewrite, loop eax
0..3); ONLY indices {16,17,18,19} shift (ink census k3/k5; navy 242 and
strays 151/196 pass through). Witness: chip-i brightest ink == pal[4i+19]
EXACT i=1..6 (chip0 = framed chip: frame greys outshine the ink on BOTH
vendor and ours -> presence check). Selected chip (i == word[+0xb5],
0x52621): FUN_0002fe04 frame — WHITE (255,255,255) hlines rows 434 and
458 x 381..395 (+16i); vlines rows 435..457 measured (164,171,177) left /
(225,227,229) right (line colours not statically decidable, refcap is
authority). Port: blitShapePalRamp (vendortext.cpp) + chipInkSlot;
constants menulaw.h; pins tngc_chip_ramp_law + tngc_chip_ramp_data_
witness; witness r1_tNGC_chip_witness.py (framed-chip count = 1 law).

## SS16 — WHEEL CHILD LAW CONFIRMED + BEGIN STARFIELD (tNG-C cycle 1)

(a) Parent writes child[win+0x67][j]->obj+0x72: density rank VERBATIM
k0..k4, species COUNT+2 k5..k9, atmosphere idx+10 k10..k12 — the port's
newgameWheelFrame bijection matches EXACTLY (no delta); wrap laws verbatim
(density 0..4, species 3..7 wrap 8->3, atmosphere 0..2 wrap 3->0); pins
tngc_wheel_frame_bijection_wrap_terms. (b) Begin-panel starfield = SHRUNK
VOLUME: full-field coords /5 + 5 (idiv 5 at 0x527a4/0x527c9), NOT
same-field-scaled (D19 open question answered; per-sprite sprite-class law
body 0x52787..0x5282f banked _wip_tNGC F11). (c) The 0x52389 crest call is
RACELIST row0's flag (window-rel 193,107), NOT the DESC crest — DESC crest
index stays a named caveat (do not touch).

## SS13 — byte+8 consumer census CLOSED "UI-only" (t423 cycle 3)

[verified] imm 494 (stride 0x1ee) exists at EXACTLY 3 code sites (0x25627,
0x44207, 0x4425f); the 0x44xxx pair is a 494-byte `rep movsd` RECORD COPY
(load/insert path), not a tinting consumer. Direct byte reads [reg+8]
(8A mod01 disp8=8): 4 sites image-wide, none race-record-adjacent; SIB/movzx
variants: zero. CONCLUSION: the vendor consumes race-record byte+8 ONLY in
the UI/intro paths the port already models (ring index SS9/SS10 law, chip
tint ramp 0x53ee0, intro ink game.pal[byte*4+0x13] t412, FUN_000232ec
write). No campaign/map tinting consumer exists; the cycle-2 "78 stride
sites" premise was record copies. SEAM CLOSED.

## SS17 — SPECIES WHEEL ARM + RACE-ASSIGNMENT LAW (tNG-B cycle 2, 2026-11-21)
PLAYERS_MORE (msg 503/0x1f7) arm [verified disasm work/tNGC_paint526b4.asm
0x52e58..0x52ecc]: word[win+0xb9]++ ; if the incremented word == 8 write 3
(0x52e6b..0x52e6d; domain 3..Seven) ; call FUN_00022ce4(0x12e10,
ebx=word[+0xb3] selected race row, edx=word[+0xb9] count) ; repaint ;
child[1] (= [[win+0x67]+4]) +0x72 = count+2 (0x52ec9, k5..k9 law).
WINDOW-INIT DEFAULT [verified 0x52c55]: word[+0xb9]=5, child art +0x72=7
(k7 'Five' — the t401 anchor). Density default 2 (Average, 0x52c40), atmos 1
(Neutral, 0x52c6b). The pre-B2 port default 7 was a campaign-coupling
invention; fixed (title.cpp), and the B3 'species content confound' died
with it (panel agreement 80.0 -> 88.8 @(0,0) vs refcap).
FUN_00022ce4 [verified decompile 2026-11-21 Ghidra :8089] = RACE ASSIGNMENT,
NOT a regenerate: word[state+0xd88]=N (player count); zeroes star owner/OR
bytes (+0x14..+0x17 of the stride-0x60 records, base state+0xdb5) and the
anomaly table bits; per player k<N draws home stars
star = state+0xdb5 + (FUN_0007824f()%starcount)*0x60 retry-until-free;
species ids via FUN_0003e6bc (rand%0x15, distinct); colours via its tail
FUN_000232ec (the chip-click law fn runs on EVERY species click too);
relation matrix +0x1b8 reset arms (type 3/4/0xf). STAR POSITIONS (+0x30/+0x34)
ARE NEVER WRITTEN — the species click PRESERVES the galaxy (opposite of the
density arm's full regen 0x226e4). OQ-016 NOTE (not a close): this is the
static home-placement ASSIGNMENT law the open row's 'home placement
verification' residue needs; the rand-law (LCG FUN_0007824f, retry-until-free)
is now cited, live verification still owed.
Chip-row hypothesis REFUTED: painter-head loop 0x525eb..0x5264c binds to
LITERAL 7 (cmp eax,7 at 0x525f1) — all seven chips always draw; only the
white frame tracks word[+0xb5] (player colour). Chip count does NOT follow
the species wheel.
Port model: species click = speciesRankNext (menulaw.h pure) + re-derive
assignRaceColours + law line 'ui raceconfig roster n N wheelgen G h15 H'
(h15 CONSTANT across species clicks = the positions-preserved witness term;
a regen mutant moves it, S3 caught). Pins tngb_species_rank_cycle; witness
scripts/tNGB_species_shot.sh + tNGB_species_witness.py; mutation
scripts/tNGB2_mutate.py 4/4. Full log: docs/re/_wip_tNGB.md.

## SS18 — BEGIN-PRESS -> SETTINGS-APPLY SEAM (tNG-B cycle 3, 2026-11-21)
STATE-IDENTITY LAW [verified disasm work/tNGC_paint526b4.asm]: every wheel
arm passes eax=0x12e10 — THE play state base (density 0x52dd7, species
0x52e76; t295 S2) — so the wheel writes the PLAY state at CLICK time; there
is no deferred "apply" for density/species. The Begin block 0x52a44..0x52b75
passes ebx=0 to worldgen 0x238e8 (0x52a65) and reads NO wheel word for them.
Begin's actual delta is exactly two things:
 (1) the WORLD layer: 0x238e8 draws planets over the CURRENT starfield (the
     click-regen'd one; planet-total += word[state+0x27283] after the outer
     loop, t295 S1) — new-game init 0x2142e+0x21438 is the same call pair;
 (2) THE ATMOSPHERE GLOBAL: byte[win+0xbb] -> byte[0x13bc4] at
     0x52b3c/0x52b44, the SOLE wheel writer of the global (window-init
     0x52c86 stores 1 unconditionally, wheel-independent). The atmosphere
     arm itself (0x52eec..0x52f0a: word[+0xbb]++ wrap 3 via the straddle
     dword[+0xb9] sar 16) makes NO state-fn call.
byte[0x13bc4] CONSUMERS [verified]: dip-on-attack subtrahend 10*(gov+1)
(diplomacy.md §17.1, 0x43a99), AI gov==2 gates (aicode.md), the race-intro
PEACE/NEUTRAL/HOSTILE section gate (raceintro.h). Wheel domain 0..2 == gate
domain; identity value 1 == window-init default AND the 20/20 playcap census.
WINDOW-INIT RUNS THE DENSITY ARM INLINE [verified 0x52c3d..0x52ce4]:
defaults 2/5/1 then 0x226e4 regen then 0x232ec colours — the state is
density-configured at window open, before any click.
RACE-COUNT IDENTITY: species word -> word[state+0xd88] (== the race-count
global 0x13b98, census 4 in the shipped scenario) = TOTAL races INCLUDING
the player => port owners = species, aiCount = species-1 (NUMCONTROLS 7 cap).
PORT (closes the t393 named seam): menulaw.h atmosphereRankNext +
newGameSettings (pure identity map); title.cpp Begin fills the
NewGameSettings out-param + law line 'ui newgame apply stars S owners O gov
G'; main.cpp rebuilds the campaign from the triple on Begin exit ('newgame
live stars S owners O gov G' = LIVE terms via Campaign::govByte()), honest
degrade on build failure; CampaignConfig.govByte feeds the dip charge
(campaign.cpp:2126, was the constant). --resume/no-Begin: untouched.
PINS tngb_atmosphere_rank_cycle + tngb_newgame_settings_identity; witness
scripts/tNGB4_begin_shot.sh + tNGB4_begin_witness.py GREEN (apply
(75,6,2) from one click each wheel off defaults 2/5/1; live == apply; intro
rides gov); mutation scripts/tNGB4_mutate.py 4/4 CAUGHT (T1 wrap term, T2
owners-minus-one, T3 apply-never-runs, T4 gov-not-plumbed). Full log
docs/re/_wip_tNGB.md.
