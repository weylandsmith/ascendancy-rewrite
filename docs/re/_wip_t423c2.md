# t423 CONT cycle 2 — WIP (scale law (d) + player-colour reassign)

## C2-F0 — trigger check [verified]
Timeline mtime Nov 12 (no new sitting); last USER: line 301 (D11b). Assignment stands.

## C2-F1 — portrait lib name strings [verified restored-image bytes]
String cluster @0x836e8 (after "names.txt"):
  0x836f2 "XM%02d" ; 0x836fc = "%s" (used as float fmt at 0x22ad6 fadd);
  0x83702 "HBDATA\\SMRACE%02d.SHP"  <- note HBDATA\\ not DATA\\
  0x83718 "DATA\\LGRACE%02d.SHP"
  0x8372c "DATA\\SMSHIP%02d.SHP"
  0x83740 "DATA\\DKSHIP%02d.SHP"
Dword-pointer census over the WHOLE image for pointers into 0x836e0..0x83770:
only 0x22894->0x836e8 (names.txt), 0x22ad8->0x836fc ("%s"),
0x23400->0x83718 (LGRACE), 0x23428->0x8372c (SMSHIP).
=> SMRACE and DKSHIP strings are referenced by ADDRESS ARITHMETIC off these
(base+8/+16), i.e. inside FUN_00023388's inlined sprintf calls.

## C2-F2 — vendor shape-scale blitter family [verified decompile+disasm]
FUN_0001fc34(0x9f10c, ...) = shape-cache fetch (record -> drawable).
FUN_0005d5a1(cacheRec, x, y, ?, srcSel?, w, h, ...) = affine STRETCH blit
  (t422 F13). Call-site shape (0x1863e..0x18676): computes size dword then
  pushes (dstx, dstY, 0, shapeId, sel, rec).
FUN_000185d8 (COSMOSWnd class, 'COSMOSWnd'@0x8478b): reads obj field
  [obj+0x4f38]; if <0x14: fild(v) - 20.0; else fild(v) + 20.0; *0.3 ->
  SIZE PARAM passed to the stretch blitter. => THE VENDOR SCALES SHAPE
  RECORDS by a computed float at paint time (scale-from-field law).
Dispatcher 0x18591: type=byte[obj+0x4f37]-4, [type]<=0xa -> jump table
  @0x39b4 -> {0x185d8, 0x18688, 0x1a1e0}. Field cluster 0x4f37/0x4f38 has
  35 code sites 0x172d6..0x1a0ae (disp32 census) = one object class.
  [obj+0x4f3c] read in FUN_00018686 with `cmp 0xa; jle skip` gate.
SMRACE string law: "HBDATA\SMRACE%02d.SHP" @0x83702 — HBDATA\ dir does NOT
exist in any .cob (census: 0 hits in game/*.cob) and no extracted dir;
FUN_00023388 (preload, callers 0x2634b/0x2156e) sprintfs LGRACE/SMSHIP/0xb90
per race row (stride 0x1ee, count word[mgr+0xd88]) into the name table
(FUN_0001fa60 = table insert, 2000+idx*0x32). SMRACE is loaded via the
+8-offset sibling string inside FUN_00023388's inlined sprintfs.
smraceNN.shp record dims CENSUSED: 21 libs x count=1 x 49x49 (all).
planets.shp: 55 recs, rec3 = 35x34 (0x23/0x22). racering k0 53x53.

## C2-F3 — FUN_000232ec (player-colour reassign) FULL DECOMPILE [verified]
FUN_000232ec(0x12e10, idx) @0x232ec [decompile + CAPSTONE VERIFIED
0x232ec..0x23385; the first decompiler read INVERTED the collision flag]:
  byte[raceRow0 + 8] = idx;                       // slot 0 = clicked chip
  for i = 1 .. count-1:                            // count = word[base+0xd88]
      cand = rand()%7;                             // LCG FUN_0007824f
      scan j = 0..i-1 ONLY (cmp ax,cx at 0x23360 = current slot index,
      NOT count): cand collides with an ALREADY-WRITTEN slot -> re-pick;
      edi=0 WRITE / edi=0xffffffff RETRY (0x2333a test edi,edi je 0x23314)
      byte[raceRow_i + 8] = cand;
  => all count colours DISTINCT; player keeps exactly the clicked idx;
  AI races get a rand()%7 permutation of the remaining values. No stale-
  slot quirk. (Scan bound j<i verified: 0x2335e inc eax / cmp ax,cx / jge
  0x2333a writes when j reaches i.)
  Field law: PLAYER COLOUR INDEX = byte at race-record +8 (stride 0x1ee,
  base 0x12e10). FUN_00023388 (same base) reads byte[row+7] = species/lib
  number for LGRACE/SMSHIP preload — so +7 = species lib id, +8 = colour.
  NOTE FUN_00020fd4 (main init) calls FUN_000226e4 -> FUN_000238e8 ->
  FUN_000232ec() at startup: the INITIAL colour assignment uses the SAME
  routine (idx from save/default), then FUN_00023388 preloads art.

## C2-F4 — scale-law MEASUREMENTS (this session, pinned user original) [verified]
scratchpad/newgame-original.png (643x481 — the t422 pitfall says texture
STATS need the 640x480 refcaps, but GEOMETRY bboxes by colour class are
interpolation-tolerant at >3px scale; t401/t414 used the same file):
- RACELIST chromatic row bands y 49..149 / 163..253 / 271..343; row-1
  chromatic bbox w=120 h=101 (x512..631 includes bevel), row-2 w=97 h=94
  x511..607 — PORTRAIT ART run ~94..101 px.
- DESC portrait chromatic inside ring: w=91 h=91 (clipped by my r45 window;
  true run >=91, t401 said art run 96 px x512..607 for rows).
- Planet zone chromatic w=38 h=47 (t401: 37x42) vs planets.shp rec3 35x34.
- Crest chromatic w=15 h=25 vs raceflag 14x24 NATIVE (exact).
LIB DIMS CENSUSED (all extracted data): smrace00..20 + smraces = 49x49;
racering k0..k7 = 53x53; raceflag = 14x24; lgrace00..20 = 296x199;
7racesel = 158x30; 90..110-range libs = planal* 103x103, plan* 107x99,
sg48expl k8 93x98 — NONE square ~98 except NO candidate at all:
=> the ~98 px portrait CANNOT be a native record from any lib; it is smrace
49 STRETCHED x2 (the ONLY lib whose 2x matches both axes; lgrace 0.33x
would be 98x66 — wrong aspect). Cited law of the stretch MECHANISM:
FUN_0005d5a1 affine stretch blitter (t422 F13) fed by class-handler sizes.

## C2-F5 — RACERING RECORD INDEX == PLAYER COLOUR INDEX [verified, DECISIVE]
racering.shp 8 records, all 53x53. Run-decoded dominant palette indices
(game.pal 6-bit *255/63):
  k0 (0,113,56)+(0,141,68)   GREEN
  k1 (101,52,109)+(129,68,141) PURPLE
  k2 (226,190,64)            YELLOW
  k3 (202,93,117)+(218,125,145) PINK
  k4 (85,72,48)+(105,89,60)  TAN
  k5 (24,76,133)+(32,97,170) BLUE
  k6 (157,72,4)+(194,97,4)   ORANGE
  k7 (28,28,28)+(165,165,165) NEUTRAL GREY
Cross-check vs the MEASURED chip colours (menulaw kPlayerChipRgb, t414 S2d):
green(5,118,69) purple(103,63,127) yellow(255,235,97) pink(239,154,174)
tan(121,105,69) blue(27,85,147) orange(151,88,20) — SAME 7 hues in the SAME
ORDER, plus a neutral 8th. => LAW: the species ring is racering
k<playerColourIdx>, NOT always k0. The port's fixed k0 (t423 cycle 1) is a
BUG for every non-green race: the vendor tints each race's ring with that
race's ASSIGNED PLAYER COLOUR (race record byte +8, C2-F3).
CONSEQUENCE for defect (d)+(colour row): the ring and the chip are the SAME
index space, so the click-reassign is VISIBLE on this screen — clicking a
chip re-rolls byte+8 per race and the rings (and the port's owner colours)
follow. This also explains D17 "species rings" complaint persisting.

## C2-F6 — ring-site colour census (pinned original) [verified]
RACELIST row ring EDGES (x502..515 + x602..615, rows 1..3): chromatic
pixels = ONLY navy (12,32,48) + its antialiasing; NO k0-green (0,113,56),
no other hue. => the ROW rings are NEUTRAL = racering k7 class
((28,28,28)+(165,165,165) greys; t401 S5 "bevel greys 48..209").
DESC ring (t401 S10): GREEN (0,142,69) == racering k0 (0,141,68) EXACTLY.
=> SITE LAW: DESC ring = racering k<playerColourIdx> (capture default
idx 0 = green); RACELIST row rings = racering k7 NEUTRAL (record, not
vector). The port's fixed k0 at BOTH sites is wrong for the rows.
Chip hit law (F2 disasm 0x529d2): zone x379..493 y420..472, idx =
(x-0x17b)>>4 — 16-px pitch from 379, idx 0..7 reachable (idx 7 = neutral,
only x>=491 sliver); 7 COLOURED chips measured at x384+16k w14 (t414).
FUN_000232ec rand()%7 keeps AI colours in 0..6; the clicked idx is stored
VERBATIM (byte) — vendor allows 7 via the sliver, no clamp in code.

## C2-F7 — scale law (d) final reading [verified measurements + cited mechanism]
- Planet: measured chromatic zone w38 (t401: 37) vs planets.shp 35px class
  NATIVE — no scaling evidence; port's (specnum%11)*5+3 35px record stands
  (group mapping stays the named seam).
- Portrait: art run 94..101 px (this session rows 2/3 + t401 S8 96px) vs
  smrace 49x49; NO lib in the archive has a ~98 SQUARE record (census
  C2-F4); lgrace 296x199 stretched to 98 wide = 66 tall — wrong aspect;
  => vendor draws smrace STRETCHED 2x via the cited affine blitter
  FUN_0005d5a1 (t422 F13). The per-site scale SOURCE (TYPE-10 list
  handler field) was NOT located: RACELIST string has zero data refs
  (dispatcher matches by strcmp chain in the 0x52xxx handler family; the
  class paint vtable slot for TYPE 10 remains unidentified). HONEST
  NEGATIVE: 2x stays a MEASURED law (two independent bboxes + elimination
  census), not a cited field read. Port keeps 2x; row (d) stays OPEN with
  the named seam — grade may pass, law does not.
