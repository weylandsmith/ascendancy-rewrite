# tA1 WIP — BLIT-SCALE LAW (PHASE-17 STAGE A) — in progress

## T0 — trigger + state checks [verified this session]
- DECISIONS.md: last USER: block = D19 (line 496); no USER: lines after it
  (file ends at the D19 defect-seed list, 543 lines). Assignment stands: tA1.
- Sitting test scripts/t368_ring_turn.py: 20/20 saves turn=1086 == expected ->
  NO new sitting; no r1_t85g_sitting re-run needed.
- scripts/t441_screen_diff.py DOES NOT EXIST yet (tA1 must build it; the
  PHASE-17 QUEUE G2 note "BUILD it in tA1" is accurate despite the t441 name).
- scripts/t442_disasm.py exists (capstone over work/ascend_restored.bin).

## Inputs already banked (do NOT re-derive)
- FUN_0005d5a1 = affine STRETCH blit; identity test (param_7,8,9)==(0,0x10000,
  0x10000) -> plain FUN_0005caac native 1:1; else FUN_000604e9 builds 16 vertex
  sets (table 0x8408..0x8457). ABI doc: _wip_t423c3.md C3-F5/F8.
- Newgame portrait stretch SITE cited: 0x52834..0x52877 pushes
  (0, 0x8000, 0x8000, 0, rect@0x48c44, [win+0xb1]>>16, colour 0x62,
  sel=word ds:[0x6fd98]) -> FUN_0001fc34 -> FUN_0005d5a1. smrace 49x49 drawn
  ~94..101 px = MEASURED 2x; scale SOURCE not yet cited (t423 honest negative).
- Cosmos site 0x18635 pushes FPU-computed size into the same slots (same
  rect@0x48c44 template).
- PITFALL (_wip_t423c3 C3-F8): do NOT re-derive param semantics from the
  decompile alone; reconcile the two sites; x87 chain unread.

## Open questions for tA1
Q1 dest-dims SOURCE per class: rect template 0x48c44 contents; does 0x5d5a1
   derive dest size from rect * scale, or from record dims?
Q2 port call sites vs law: newgame portrait / species column / planet disc /
   planets-list sun+planet (D19 quadrant family).
Q3 build scripts/t441_screen_diff.py region harness.

## F1 — 0x5d5a1 AFFINE BLITTER LAW [verified decompile 0x5d5a1 + 0x604e9 + 0x61058]
- Identity dispatch head: (p7, p8, p9)==(0, 0x10000, 0x10000) -> NATIVE 1:1
  (p10&1 ? 0x5cf96 : 0x5caac). p7 = shear/rotation, p8 = X-scale, p9 = Y-scale,
  ALL 16.16 (0x10000 = 1.0). [confirms C3-F5]
- Affine path: src dims from FUN_00061058(recptr, drawable) = record header
  u16 pair (W-1, H-1) at rec+0x10/+0x12 (i.e. the SAME dims the native decoder
  reads at rec+4/+8 +1? NO — 0x61058 reads rec_ptr[+0x10..0x14] fields of the
  CACHE DESCRIPTOR: short(x1-x0+1), short(y1-y0+1) — the descriptor rect, see
  decompile). Row count = (H-1), col loop = clip width; source stepping per
  dest pixel = delta = (src_extent_16_16 * p8)>>32-ish (0x604e9:
  ((p1-p3)<<16)*p5 then *cos/sin) => THE SCALE IS A ZOOM MULTIPLIER:
  dest size ~= (src_extent) * p8/0x10000 per axis. [verified arithmetic form]
- WITNESS for direction: cosmos site 0x18646 pushes ebx = fistpl of
  fild(size)*float — an INTEGER size pushed into the p8/p9 slots => vendor
  zoom = size<<16. p8=0x8000 = 0.5 = DOWNSCALE.
- DEST RECT law: p6 = caller rect pointer; the 0x48c44 immediate at the
  stretch sites is a MID-STRUCTURE pointer (disasm 0x48c29..0x48c6d shows real
  CODE at 0x48c44 — it is `lea 0xcc(%esp)` of a caller whose frame puts esp at
  -0xa8: a STACK rect buffer in the window-manager frame, fields
  x0=7 y0=37 x1=639 (t412 dump), NOT a static template. Clip clamp: dest cols
  = clip x-extent clamped, rows = clip y-extent.
- 24 rel32 call sites (scripts/ta1_scale_census.py): 0x165b3 0x18676 0x186f9
  0x1a25e 0x1a702 0x2837d 0x2c883 0x2cdcc 0x2ce9c 0x3508f 0x367d8 0x37471
  0x3a9b8 0x3c451 0x3c708 0x3d11b 0x483f2 0x48b4c 0x48dbc 0x509fd 0x50aca
  0x50b8a 0x50c1f 0x52872.
- CONSEQUENCE (big): the newgame portrait site 0x52834 pushes p8=p9=0x8000 =
  0.5 DOWNSCALE. A 49px smrace at 0.5 = 25px — CANNOT produce the measured
  94..101 px art. => the selector word ds:[0x6fd98] resolves to a LARGER
  record (~197x197 * 0.5 = 99) OR t423's measured-2x law is wrong. The D19
  quadrant signature ("top-left quadrant of a 4x render") is EXACTLY what
  drawing a 49px quarter as if it were the whole image looks like => INDEX/
  SELECTOR law is the root cause family; per-class scale must be re-cited.

## F2 — TRUE DIMS LAW FOUND: BBOX-DIFF (four witnesses) [verified this session]
RECORD TRUTH (file layout, suns k1 @0x2fc3 verbatim bytes):
  [u16 cw-1,u16 ch-1][u16 ~half][i32 L,T,R,B][RLE stream]
  canvas pair = (149,149); bbox = (-67,-63,62,63) -> CONTENT 130x127;
  stream walks EXACTLY 130x127 to span_end 0x5c4c (delta 0).
WITNESSES:
  (1) CODE: FUN_00061058 (the affine path's dims source, called verbatim at
      0x5d5d3) = (short)[desc+0x10]-[desc+8]+1, (short)[desc+0x14]-[desc+0xc]+1
      = BBOX DIFFERENCE. FUN_0006108c returns the (L,T) corner; 0x5d5a1
      negates it (local_40/44) and adds to the caller anchor = PLACEMENT LAW
      dest = anchor + (L,T).
  (2) EXACT-SPAN CENSUS (scripts/ta1_dims_law.py pattern, full run):
      bbox-at-dir+8 law 1247/1436, bbox-at-dir-8 119, canvas-pair 36, none 39
      (the 0x7FFFFFBB expl-header variant already flagged unmodelled shp.md S3).
      The OLD port law (u32@rec+0 k0 / u32@rec+0x10 k>=1) matched 1 + 30 —
      it reads SUB-FIELDS (canvas W-1 or the R,B corner), not dims.
  (3) PIXEL RENDER: suns k1 decoded at bbox dims = a complete coherent sun disc
      centred in 130x127 (ascii proof /tmp run); at old dims (62x63) the walk
      runs SHORT (pos 0x46c7 vs 0x5c4c) = row-sheared top-left slice.
  (4) MEASURED VENDOR DRAWN SIZES == bbox dims 1:1 EVERYWHERE:
      suns k1 bbox 130x127 vs t427 drawn 130x126; racering k1..7 bbox 109x109
      vs measured ring diameter ~106-107 (r53); smrace bbox 100x100 vs measured
      art 94..101; planets k1 bbox 38x38 vs measured zone 37-38.
=> THE VENDOR BLITS ART RECORDS 1:1 AT BBOX DIMS. The port's fake 2x scales
   (kRacePortraitScale, racering 2x, kStatusArtScale) compensated the port's
   OWN truncated dims read; the D19 "top-left quadrant of a 4x render" IS the
   canvas-width misparse of a content-width stream, drawn 2x.
L,T PLACEMENT: content rect offset from the ANCHOR the caller passes
  (racering/smrace/planets L,T ~ -W/2,-H/2 = centred; suns k1 L=-67,T=-63 =
  star-centre anchor). Port sites must draw at (anchor.x+L, anchor.y+T).

## F3 — scale direction of the affine path [honest negative, carried]
0x52834 pushes p8=p9=0x8000; 0x604e9 delta math + the render loop could not be
direction-resolved statically this session (t423 C3-F8 pitfall stands). NOT
needed for tA1: every NAMED port site reproduces the vendor's MEASURED drawn
size at 1:1 native bbox dims, so the port law = native 1:1; the affine site's
internal semantics stay a named seam (selector word ds:[0x6fd98] binding too).

## F4 — IMPLEMENTATION PLAN (in flight)
shp.{h,cpp}: per-record dims = bbox-diff; bbox quad candidate at rec+8
  (primary) and rec-8 (fallback, 119 records), accepted by the canonical walk
  completing (exact-span preferred, file-bound as today); Record gains left/top;
  canvas-pair reading KEPT only where it already walked (1+30 records are the
  same bytes under bbox? verify in tests). Named art sites drop scale=2 and use
  anchor+(L,T): title.cpp DESC ring+portrait+planet, RACELIST rows,
  statuslist sun/planet. Risk flag: chrome libs (1starmap) dims change — run
  the 471-test suite; update pins ONLY to newly cited values.

## F5 — IMPLEMENTATION LANDED + SUITE GREEN [verified this session]
FORMAT (rewrite/src/formats/shp.{h,cpp}): record dims = BBOX-DIFF; quad at
stream-0x10 (k0 quad = final directory slot); Record gains left/top; parse
gate = bounds only. Census: bbox law completes 1413/1436 (exact-span 1403;
t197 cross-span class 10; 0x7FFFFFBB variant 1starmap k1 decodes 3x3;
cos_star k40..k51 + sg50expl k9 = 1x1 degenerate placeholders that DECODE);
all 31 old-law passers still complete (no regression, script run recorded).
RENDER (all fake scales -> NATIVE blit at anchor+(L,T)):
 title.cpp DESC ring (racering k<colour>), DESC portrait (smrace 100x100),
 DESC planet (size index +3 -> +1: bbox ladder {24,38,52,71,95}, measured
 zone 37x42 == 38 ONLY), RACELIST rows; ui.cpp state-7 species portraits +
 rings; planets-list sun (bbox 130x127 == measured 130x126) + planet.
CONSTANTS: kRacePortraitScale 2->1, kStatusArtScale 2->1,
 kSpeciesPortraitScale 2->1 / ClipR 49->50 / RingHalf 53->55,
 kFieldRecordW/H 625x357 -> 626x358, popSlotLibraryConforms want
 {9x9,6x9,8x8}, stripGaugeLibraryConforms width 107->108 (heights VARY per
 record under bbox law, dropped from the identity term).
PINS RE-CITED to bbox values: t263 poppanel, t394 mapchrome (content ==
FULL inclusive rect — the old minus-1 parity WAS the misparse), t425c
toggle faces 31x31/961, t435 resfaces full-rect, t426 plaque 15x25, t399
digits w[1]=9 thin-one + rest >=18, t410 sysview full-rect, t401 raceflag
15x25 + smrace 100x100, t427 suns ladder <=140/142 + k0 127x133 + planets
ladder 24/95/24, t436 flags 15x25 + ring 109 + disc 100, t428d field
626x358, t428 gauge census, test_shp corner-anchor/zero-header/1starmap-k1
assertions CORRECTED (reject -> decode).
SUITE: ctest 100% pass (62.25s). Chrome draw sites (1starmap k8..k19,
k55..k64, 20res, mouse, 7racesel) keep their rect-anchored blits — under
the new law dims == rect span, and every affected parity pin was re-cited
to the full-rect law and passes.
REMAINING FOR tA1 CLOSE (not done this iteration): build
scripts/t441_screen_diff.py (region table + dims assertion + presence mass,
G2), witness newgame + planets-list renders at 1:1 (quadrant signature
GONE), mutation-verify each changed constant. Honest status: LAW LANDED,
CLOSE UNVERIFIED — tA1 stays open, next row finishes it.
