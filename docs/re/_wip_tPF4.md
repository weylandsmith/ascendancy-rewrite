# _wip_tPF4 — PLANLIST PAINT FN 0x3cbb4: CASE-BODY WALK (row-art source law)

Assignment (docs/STATE.md NEXT ACTION): read the vendor PLANLIST case-bodies
(the D10 fallthrough walk, no jump table needed), derive the ROW-ART SOURCE
law, port into the home-planets UI path with pins, witness.

## P0 — SITTING CHECK (ran FIRST, exit 0)
work/r1/tPF4_pre_sitting.out: trusted turn-change rows 45,227, newest t=1335 —
identical baseline to the tPF-2d/2b/3 checks. NO new user sitting; the stale
assignment stood. Production ring untouched; no scratch servers spawned.

## P1 — DISPATCH RE-ALIGNED (the D10 walk's blocking trap)
The prior note said "walk 0x3cca4..0x3d1bc". 0x3cca4 is the MIDDLE of the
dispatch instruction. Bytes: 0x3cc9d `89 f8` mov eax,edi; then the 8-byte
`2e ff 24 85 e8 7f 02 00` = `jmp dword ptr cs:[eax*4+0x27fe8]` (disp32
0x27fe8 confirmed from the bytes). THE DISPATCH ENDS AT 0x3cca7, so the first
case body begins at 0x3cca7, NOT 0x3cca4 — that is why both capstone passes
(the 0x3cca4 window and t442_disasm) printed garbage (`jg`/`add [esi-0x5f],ah`)
for the first body. Stepping from 0x3cca7 re-syncs immediately:
  3cca7: mov ax,[ds:0x6fd90]        <- shape-id word (case A)
  3ccad: mov edx,[ds:0x43508]       <- the record this fn paints
  ...
Head leg (verbatim, 0x3cbb4..0x3cca7): key = [widget+0x47] (0x3cc15), remap
4->3 (0x3cc21), SENDMESSAGE hiword ([widget+0x43] sar 16)==0x33 -> key 4
(0x3cc38); cmp key,4 / ja default 0x3d1bc (0x3cc94..0x3cc97). Two pre-tests
before the key: edx==2 -> skip-to-0x3ccb5; else [ds:0x7d35e]==[eax+0x41] ->
same, and edx==1 sets [esp+0x48]=0xffffffff (the "selected" sentinel).
Also 0x3cbff/0x3cc05: two shape records fetched via 0x1a168(0x7a35c, 0x1f6b /
0x1f74) gate whether the sentinel is cleared ([rec+0x35] tests).

## P2 — THE RECORD IS THE PLANITEM RAM TABLE (stride 0x28, OQ-014 layout)
Decisive arithmetic inside the bodies:
  0x3cefd/0x3cfbd `lea eax,[edx*4]; add eax,edx; shl eax,3; add eax,0x73e40`
    == 40*idx + 0x73e40  -> PLANITEM record base (OQ-014 stride 0x28)
  0x3cfbd `mov ax,[eax*8+0x73e46]` == FLAGS u16 @ +6 (OQ-014 field map),
    then `and al,0x20` -> bit5 set = row SKIPPED (0x3cfd2 jne 0x3d036)
  0x3cffe.. `push eax(0x26)/0x27` + 0x21a20 = the getter idiom (static.txt),
    0x3d004 call 0x76c79 = sprintf-style composition
  So the index the bodies carry is a BUILD-ITEM index, i.e. these are the
  build-list rows. Confirms fn 0x3cbb4 == the PLANLIST painter.

## P3 — CASE-BODY SHAPES (raw walk, 0x3cca7..0x3d1bc)
Four "single blit" bodies then a row loop. Every blit is
0x5caac(lib=0x1fc34(0x9f10c, WORD), x=[esp+0x60], y=[esp+0x64], 0,0) or the
scaled twin 0x5d5a1; every y goes through the SAME clamp chain
pow(v,0.5) [0x78a90 with 0x3fe80000:0x33333333 == double 0.5] -> 0x76e08
chop -> clamp [0,20] (tRS-V2 law family, same instrument).
  body A 0x3cca7: shape word [ds:0x6fd90]; y from [rec+0x46]
  body B 0x3cd3b: shape word [ds:0x6fd92]; y from pow([ds:0x43508->rec]+0x44)
  body C 0x3cdcf: shape word [ds:0x6fd94]; y from [rec+0x48]
  body D 0x3ce39: ROW LOOP — count = word[rec+0x4a], two special rows
    word[rec+0x4c] and word[rec+0x42] each +1 to a slot value, shape word
    [ds:0x6fd9c], text via 0x5e940 palette 0xf2 / 0x96 when [esp+0x48]!=0,
    y advances by idiv-10 legs (row = idx%10, ebp/edi += 10)
  body E 0x3cf01: like D but the highlight test is
    byte[rec+0x57] == byte[ds:0x7458e] (THE RACE/specnum field, t423 law)
  body F 0x3cf9b: byte[rec+0x54] vs byte[ebp+0xab]; 0x3d03b special-cases
    byte[rec+0x54]==0x23 (35) and takes word[rec+0x52]; then the SCALED path
    0x5d5a1 with item 0x17 (23) getting scale 0x8000 else 0x10000, art from
    the item record name-field arithmetic above.
## P4 — ROW-ART PRODUCERS READ (0x3c84c / 0x3c8b0 verbatim, THE citation owed)
0x3c84c (tile-click leg, item arg dl):
    out_shape := WORD[ds:0x6fd80]                    ; the DEFAULT row lib
    out_sel   := 0; if item != 0xff: out_sel := item byte
    if item == 0x17 (23, SHIP): out_shape := WORD[ds:0x6fd60 + 2*race]
                                 (race = byte[rec@ds:0x43508 + 0x57]),
                                 out_sel := 0
0x3c8b0 (orbital leg): out_shape := WORD[0x6fd80]; sel from the item-record
    sub-table at [rec+0x10] + 4*idx (byte[+1] != 0xff ? that byte : byte[0]&8).
Asserts: item < 0x27 (0x3c855, msg 0x84abf "planet.cpp") and idx <= word[rec+0x1a].
So the ROW-ART SOURCE LAW = shape-id slot -> .shp lib; the selector = the ITEM
INDEX. The port's tPF-2b premise (planitem record == itemIdx) is CONFIRMED at
bytes — upgraded [inferred] -> [verified] — and the Ship row takes a per-race
lib with selector 0 (SEAM TPLV2-A material).

## P5 — RUNTIME JUMP TABLE RECOVERED FROM BANKED SAVES (D10 CLOSED)
scripts/tPF4_jt_and_registry.py + the whole-member value-law scan: the table
is NOT in the data segment (D10's BSS read was the wrong segment) — it lives
in the CODE image at member offset 0x1fc070 (guest-physical target values,
POINTER-VALUE LAW t298: read value+0x88... here the values ARE targets).
Five u32 entries, unanimous across every decoded save, converting (value - P0,
P0 = B-H = 0x1bf450 for bank-t377) to payload FILE offsets:
    case0 -> 0x3cca7   case1 -> 0x3cd3b   case2 -> 0x3cdcf
    case3 -> 0x3ce39   case4 -> 0x3cefd
Exactly the five bodies the fallthrough walk found. D10 CLOSED: no debugger
stop was needed; code verbatim at B+0x3cbac re-verified against the payload.

## P6 — SHAPE-REGISTRY JOIN: THE SHAPE IDS ARE FILE NAMES (60/60 saves)
Cache ctx = ds:0x9f10c -> member 0x242000+0x9f10c+H (pointer law; the FIRST
attempt used B+VA = the code segment and read zeros — base trap banked).
Registry name law shp.md S2: ctx + 0x7d0 + id*0x32, cp437, NUL-terminated.
Measured (scripts/tPF4_rowart_runtime.py values x registry names, UNANIMOUS
60/60 across bank-t377 + -late + bank-t1086-preplay):
    WORD[ds:0x6fd80] = 30 = 'data\planitem.shp'   (DEFAULT row/shape lib)
    WORD[ds:0x6fd90] = 38 = 'data\planres.shp'    (case 0 body art)
    WORD[ds:0x6fd92] = 39 = 'data\planind.shp'    (case 1)
    WORD[ds:0x6fd94] = 40 = 'data\planpro.shp'    (case 2)
    WORD[ds:0x6fd9c] = 44 = 'data\17np.shp'       (case 3 row loop)
    WORD[ds:0x6fd60 + 2r] for r=0..20 = ids 14..34 SEQUENTIAL, registry:
      r0..6 -> SMSHIP19, SMSHIP02, SMSHIP11, SMSHIP00, SMSHIP09, smship05,
               smship06   (a PERMUTATION of the 21 smship files, not rNN)
      r7..13 -> DKSHIP19/02/11/00/09/05/06 (the same permutation, DK names;
               NO dkship files exist in ascend01.cob — registered-but-absent,
               never fetched for the shipped 7-race scenario [inferred])
      r14..20 -> gizmos, planets, planitem, restree, raceflag, racering,
               smhome (these slots serve OTHER consumers; the Ship read is
               race-indexed and races 0..6 are all the shipped scenario has)
=> SEAM TPLV2-A CLOSED: the item-23 Ship row art = smship{P[r]}.shp record 0
   with P = (19,2,11,0,9,5,6), cited by live-RAM registry join, NOT guessed.
Corpus note: extracted/ascend01/data/ HAS smship00..20 (21 files, 4 records
each) — the files the Ship rows blit.

## P6b — RUNTIME CORROBORATION of the +0x57 race field
ds:0x43508 pointer value 0x26e21e -> record at member 0x26e2a6 (POINTER-VALUE
LAW value+0x88): byte+0x57 = 0 (race 0), word+0x1a = 33 (the 0x3c8b0 assert
bound), words +0x44..+0x4c = (7,14,0,15) — the case-body y/count fields are
populated live. The record IS the planet window's PLANLIST feed.

## P7 — PORT DELTA (what shipped)
planetview.{h,cpp}: planRowShapeSource(item, race) — pure law, cited per leg:
  item==23 -> {smship P[race], record 0, scale-half flag} (0x3c84c Ship leg +
  body F's 0x8000 scale constant at 0x3d08c..0x3d091);
  else -> {planitem.shp, record item, scale 1.0} (P4 default leg).
ui.cpp PLANLIST row render: Ship rows blit the race smship lib record 0 at
half scale (blitShapeScaleF, tRS-V2p instrument) instead of the planitem icon;
the seven permutation libs load at screen init (refusal = per-race planitem
fallback, the lib-refusal precedent). OWNER->SPECNUM via speciesSpecnumOfOwner
(the species-rail law). WITNESS-CAUGHT BUG (hazard banked): smshipLibs is
indexed by SPECNUM (libs loaded in specnum order); shipShapeFileNum returns
the FILE NUMBER — conflating the two (smshipLibs[19]) silently skipped the
leg (count()==0 guard swallowed it); the first witness run caught it.

## P8 — PINS + MUTATIONS + WITNESS (all real runs)
PINS tests/test_rowart_tpf4.cpp x3 (permutation 7 legs + non-Ship sweep 78
checks + specnum bounds; corpus-file existence for all seven smshipNN.shp;
source-text wiring incl. record(0) selector and the 0.5 blit). Suite
561->564/0/0 (file needed a CMakeLists entry — first run silently shipped 0
new tests, caught by the count).
MUTATIONS: M1 permutation 19->0 -> 1 FAIL; M2 polarity flip (== instead of !=)
-> 85 FAILs; M3 wiring removed (shipFile := -1) -> wiring pin FAILS (first M3
attempt was VACUOUS — the mutation left "shipShapeFileNum(" present in a dead
initializer; re-run with a true removal). All restored, md5-verified, green.
WITNESS scripts/tPF4_witness.sh (seed 5 --species 0, Xvfb :99, BY-PID kill):
LOG PASS "ui planlist ship row file 19 scale 0.5" (specnum 0 -> 19 = the
measured permutation, live). Membership log instrument: opts n=8
[0,1,2,20,21,22,23,26] — Ship visible at first=4 slot 2.
PIXEL CENSUS (differential, control = SAME script without --species so
specnum=-1 -> planitem fallback): Ship-row strip (132,266)-(210,338): 2726/
5600 differing px (48.5%), adjacent slot-1 strip 0 differing (anti-vacuity:
the runs are otherwise pixel-identical). VERDICT PASS.
NOT claimed: pixel-identity with the VENDOR's list (no vendor build-list
capture holding a Ship row; D28 refcap rows are surface items only).

## HONEST NEGATIVES
- No OQ row closed (tPF tracks none); open=[016,019] unchanged.
- DKSHIP19..06 (specnums 7..13) are registered names with NO files in
  ascend01.cob — any consumer that fetched them would cache-miss; not needed
  for the 7-race shipped scenario [inferred].
- Case bodies A/B/C (planres/planind/planpro gauge art + 17np row loop):
  READ and cited this iteration, but the port's STRIP gauges already use the
  planres/planind/planpro libs via the t428 strip law; the 17np consumer (the
  popup body-D loop, count word[rec+0x4a]) is NOT ported (named-open TPF4-A:
  what the 17np 10-row loop paints in the popup).
- The [esp+0x48] sentinel pre-tests (0x3cbff/0x3cc05 shape+0x35 gates) are
  not modelled (no port-side observable yet).
