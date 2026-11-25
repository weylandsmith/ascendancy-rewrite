# _wip_tPF3 — TILE OVERLAY + COLONY-BASE ANCHOR (D28 P2/P6)

Pre-flight (2026-11-25, this session):
- SITTING CHECK ran FIRST (r1_t85g_sitting exit 0, work/r1/tPF3_pre_sitting.out):
  trusted turn-change rows 45,227, newest t=1335 — IDENTICAL to tPF2/tRS-V2w
  baselines. No user sitting; assignment stood.
- Assignment (STATE.md): overlays are SEMI-TRANSPARENT colored squares, SMALLER
  when not adjacent (refcap planet-screen-iter-433-v-original.png — ours opaque);
  derive alpha + both sizes + per-class colors from vendor paint fn
  0x3bbd6..0x3bc52 family in work/ascend_restored.bin. CB art misaligned since
  tPL-V1: re-anchor to (410+34*(col-row), 127+17*(col+row)).

## F1 [measured, raw asm work/tPF3_paint.asm + tPF3_mid/tail] — THE OVERLAY IS
## A SEPARATE SMALL DIAMOND PAINTED ONLY ON LEGAL BUILD SITES

Loop structure 0x3bb19..0x3c335 (per slot idx esp+0x330):
- 0x3c274..0x3c295: full-diamond vertex table esp+0x260..0x2ac built from
  centre law (ecx*0x22 x-cursor, ecx*0x11 y-cursor): vertices
  (x, y+17),(x+34, y),(x, y-17),(x-34, y) — the tPL-V1 diamond.
- 0x3c2da call 0x3830c (THE PLACEMENT CHECKER, tPL-B1 law); return EDI/EDX
  saved at 0x3c2df/0x3c2ef (edx = checker grant value).
- 0x3bbc3 gate: [ebp+0x18b] bit0 must be SET else jump 0x3be53 (overlay
  skipped entirely). SEAM TPF3-A: who sets 0x18b bit0 (was TPLV1-A).
- 0x3bbdd..0x3bc52 COLOUR TABLE on the class byte (word esp+0x374 = cell
  class byte, rock byte|8 matches no compare -> default):
    class 0 -> outline pal 7, fill blk 0 (skip)
    class 2 -> outline pal 8,  fill blk 0x75 (117 red)
    class 3 -> outline pal 9,  fill blk 0x92 (146 green)
    class 4 -> outline pal 10, fill blk 0xff (255 blue)
    default -> outline pal 13, fill blk 0xc (12 white)
  (pal 7/8/9/10/13 = the grey-ramp selector tPLV1 named — it is the OVERLAY
  OUTLINE pen, NOT a tile fill selector.)
- 0x3bc52 cmp edx,-1:
    edx != -1 (0x3bd4d branch): 0x5bf71 x4 draws the diamond OUTLINE ONLY,
      FULL size (same vertices), pen di.
    edx == -1 (legal build site, fallthrough 0x3bc5b): SMALL vertex table —
      x offsets {0,+34,0,-34} (SAME width 68), y offsets {+14,0,0,-14}
      => height 28 vs 34 (HALF-HEIGHT 14 vs 17). 0x5bf71 x4 outline pen di,
      then 0x3bd3a: fill block ptr := [0x48c33] + colour*0x100 passed to
      FILLER 0x62d15 (push blk, push rect-table, push 4, push 0x4850c).
  => D28 "SMALLER when not adjacent" RE-READ: the small+filled diamond is
     the LEGAL-BUILD indicator (checker grant -1 = empty + ACTIVE neighbour
     per tPL-B1b law); illegal tiles get the full-size OUTLINE-only diamond.
     "Smaller" and "colored" are ONE indicator, not two states.
- 0x3be53 hover leg: hovered slot == idx (word ebp+0xac) && ebp+0xab==0xff &&
  owner byte match -> 0x5bf71 x4 outline pal 0x96 (150 teal) FULL diamond
  (this is the existing hover law).
- 0x3bed1: class byte == 0xff -> shape sprite via 0x3c8b0+0x1fc34 (structure
  art pass); rock bit test 'and al,8' at 0x3bee4 gates the 0x3c148 branch.

## F2 [measured raw asm 0x3bc52..0x3be50 + tPL-B1 EDI law] — SIZE SELECTOR +
## SMALL-DIAMOND GEOMETRY + ANCHOR LAW FOR STRUCTURE ART

- 0x3c2ef 'mov edx, eax' — edx at the 0x3bc52 'cmp edx,-1' IS THE CHECKER
  0x3830c RETURN (eax saved to esp+0x315/0x311 then edx). Per tPL-B1 the
  checker returns 0xffffffff iff LEGAL (grant accumulator EDI!=0), 0 when a
  veto fired (0x386fc xor edi,edi path). =>
    LEGAL site (checker -1):  SMALL diamond + FILLED (0x3bc5b fallthrough:
      vertex table esp+0x200.. = x {0,+34,0,-34}, y {+14,0,0,-14} — width
      68 SAME, HALF-HEIGHT 14 vs 17 — 0x5bf71 x4 outline in pen di, then
      [0x48c33]+fill*0x100 -> polygon filler 0x62d15).
    ILLEGAL site (checker 0): 0x3bd4d branch, FULL diamond OUTLINE ONLY
      (no fill call).
  So the COLOURED SMALL diamond = the legal-build indicator (empty +
  ACTIVE 4-neighbour + no veto), NOT a per-class terrain paint. D28's
  'colored when adjacent, smaller when not' is the user's reading of the
  SAME indicator family; the raw law is: adjacent&empty -> small+filled,
  else -> full outline-only. Both drawn OVER the uniform 150 tile fill.
- CLASS COLOUR TABLE (0x3bbdd..0x3bc4b, on slot class byte):
    0 -> outline pen 7,  fill blk 0    (skip: 'test di,di je 0x3be53')
    2 -> outline pen 8,  fill blk 117 (red)
    3 -> outline pen 9,  fill blk 146 (green)
    4 -> outline pen 10, fill blk 255 (blue)
    else -> outline pen 13, fill blk 12 (white)
  (tPL-V1 mislabelled the 7/8/9/10/13 as a 'grey-ramp fill selector' — they
  are the OVERLAY OUTLINE pens paired with the fill blocks.)
- STRUCTURE-ART BLIT (0x3bed1 class==0xff branch -> 0x5cf96 with rect table
  esp+0x260): dest = tile CENTRE (same esp+0x260/0x264 as the diamond) +
  record signed bbox (tRSV1d blitter anchor law, research.md S8(h)).
  => PORT CB MISALIGNMENT ROOT CAUSE [inferred, verify next]: ui.cpp:2430
  centres with 'c.x - width/2, c.y - height/2' (bbox ASSUMED symmetric);
  the vendor composes dest = c + bbox.left/top. Fix = blit at
  (c.x + rec.left, c.y + rec.top) like researchview.
- 0x3bed1/0x3bedb: art pass runs iff slot byte == 0xff (item present);
  shape id via 0x3c8b0 (word [0x6fd80] default = cache, selector==item) +
  0x1fc34 cache 0x9f10c. Rock branch 0x3c148 uses 0x3c84c (race table
  [0x6fd60] for item 0x17).

## F3 [measured raw asm 0x3bc5b..0x3be50 RE-READ + refcap zoom] — EXACT
## OVERLAY GEOMETRY (F2's y-offset reading CORRECTED)

Full-diamond vertex table (0x3c211..0x3c274): TOP vertex (x, y), spans
y..y+34 — the PORT's tileCenter is the CENTRE (x, y+17 of the vendor table).
- LEGAL (checker -1, 0x3bc5b): INSET diamond vertices (x, y+1), (x+32, y+17),
  (x, y+33), (x-32, y+17) = 64x32, SAME centre, 2px in on x / 1px in on y.
  Lines via 0x5bf71 x4, colour di (class colour: 0 black/117 red/146 green/
  255 blue/12 white — the FIRST pushed arg of 0x5bf71 is `mov ax,di`, so di
  IS the line colour; tPL-V1's edge-colour law was RIGHT for the lines).
  The pen 7/8/9/10/13 selects the 256-byte DRAW-STATE block
  [0x48c33]+pen*0x100 for the polygon filler 0x62d15 (fill style, NOT a
  colour). DAT_00048c33 == 0 in every banked save (window-runtime alloc) —
  block contents UNRECOVERED statically (SEAM TPF3-B).
- ILLEGAL (checker 0, 0x3bd4d): TINY diamond (x, y+14), (x+6, y+17),
  (x, y+20), (x-6, y+17) = 12x6 at the same centre, lines colour di.
  THESE ARE THE SMALL BLACK DIAMONDS VISIBLE IN THE VENDOR ZOOM inside
  non-adjacent tiles — the D28 'smaller colored squares when not adjacent'.
- So the user's sentence maps: adjacent&empty -> checker -1 -> LARGE (64x32)
  inset diamond; not adjacent -> checker 0 -> TINY (12x6) diamond. Both are
  drawn IN ADDITION to the uniform-150 fill + full class-colour outline.
- 0x18b bit0 gate (0x3bbcb): overlays skipped when clear (SEAM TPF3-A —
  refcap shows them ON in the planet view; port default: always on).
- FILL STATE: pixel census of the vendor refcap found NO colour delta
  between inset-interior and tile field (both exactly (16,69,77)=conv150,
  20495 px) — the state-block fill neither lightens nor darkens the teal
  field measurably. PORT DEFAULT: outline-only overlays; fill skipped,
  seam TPF3-B named (honest: alpha law NOT recovered, and the refcap does
  not constrain it).

## F4 — CB ANCHOR (D28 P7)
Vendor structure blit 0x3bed1 branch: 0x5cf96(cache 0x4850c, rect=tile TOP-
vertex table esp+0x260, shape via 0x3c8b0/0x1fc34) — dest = TOP VERTEX +
record signed bbox (tRSV1d anchor law). Port tileCenter == centre == vendor
(x, y+17), so port dest = (c.x + rec.left, c.y - 17 + rec.top).
The port currently centres with (c.x - w/2, c.y - h/2) = wrong unless the
bbox is symmetric. SEE bbox census below.

## F5 [measured] — OVERLAY LEGALITY WITH THE PAINTER'S ITEM ARG + CB ANCHOR CENSUS

Checker call in the paint loop (0x3c2c5..0x3c2da): the class byte goes to
esp+0x374 and the ITEM ARG IS 0xff (mov edx,0xff at 0x3c2c7; ebx=slot idx).
With item 0xff the checker legs reduce to (t42/tPL-B1 leg map):
  rule B 0x38493: skipped for item 0xff -> class==0 leaves EDI=0 -> RETURN 0
                  (class!=0 granted -1 earlier -> survives);
  rule C 0x384db: item<31 gate -> SKIPPED (0xff>=31);
  rule D 0x38519: rock (byte0 bit3) XOR (item==38 false) -> VETO on rock;
  rule G 0x385b7: own-active skip; else ACTIVE neighbour -> legal tail;
                  ALL-inactive -> xor edi,edi -> RETURN 0.
=> OVERLAY LAW: Inset (64x32, lines colour di + polygon fill via state
   block) iff class!=0 AND NOT rock AND (own OR active-4-neighbour);
   else Tiny (12x6, lines colour di, NO fill). Drawn on EVERY cell incl.
   occupied ones (own-active leg). class==0 (barren) -> TINY always.
   The tPL-V1 'full-size class-colour outline' is NOT in this function:
   the class-colour lines ARE the inset/tiny overlay (2px inside each cell,
   which the lattice witness's tolerance read as boundary colour).
   PASS 2 in ui.cpp is REPLACED by the overlay law.
- CB ANCHOR [measured]: structure blit 0x3bed1 -> 0x5caac at 0x3c1ab with
  x=esp+0x260 y=esp+0x264 = the TOP VERTEX of the diamond (centre is
  (x, y+17)); dest = anchor + record signed bbox (tRSV1d law).
  MEASURED planitem.shp bboxes (extracted/ascend01/data/planitem.shp,
  header law shp.cpp:148-183): ALL 40 records L=-34; T in {-1..-18}
  (rec0 CB: T=-9 H=43 -> content spans top-9..bottom+0). The port's
  (c.x - w/2, c.y - h/2) is 5 px LOW for the CB and wrong per-record.
  FIX: blit at (c.x + r.left, c.y - 17 + r.top).

## F6 [measured + pixel census] — THE POLYGON FILL IS VISUALLY A NO-OP AT
## THE REFCAST STATE; OVERLAY GEOMETRY FINAL

- 0x62d15 (polygon filler) gets state block [0x48c33]+idx*0x100 (idx = di
  class-colour on the legal/inset branch 0x3bd3a, idx = pen 7..13 on the
  tiny branch 0x3be2c). DAT_00048c33 == 0 in every banked save (runtime
  window alloc) -> block contents UNRECOVERABLE statically.
- DECISIVE PIXEL CENSUS on the vendor refcap (planet-screen-iter-433-v-
  original.png left half, logical field 250..580 x 150..420): 20,495 px of
  EXACTLY (16,69,77) == conv(pal 150) tile fill, ZERO pixels of any
  class-colour or class-blend shade INSIDE the tiles. If the overlay
  polygon filled solid/dithered red-green-blue, interiors would show it.
  => at the refcap's state the fill paints the SAME colour as the tile
  base. PORT: outline-only overlays (fill skipped, seam TPF3-B named —
  matches the refcap pixels exactly; an alpha law was NOT recovered and
  the refcap does not constrain one).
- FINAL GEOMETRY (centre-relative; vendor table top-vertex based, centre =
  (x, y+17)):
    INSET  (legal)  : (0,-16) (+32,0) (0,+15) (-32,0)  [64x31-ish, 2px in]
    TINY   (illegal): (0,-3)  (+6,0)  (0,+3)  (-6,0)   [12x6]
  Line colour = di: 0 black / 117 red / 146 green / 255 blue / 12 white
  (same table tPL-V1 pinned as tileEdgePaletteIndex).
- LEGALITY = checker 0x3830c with ITEM ARG 0xff (mov edx,0xff 0x3c2c7
  [verified]): rule B grants always (0xff exempt), rule C skipped (item
  >=31), rule D vetoes ROCK, rule G: own-active skip OR active-4-neighbour
  legal, all-inactive veto. => inset iff !rock AND (own OR active nbr);
  tiny otherwise. Barren non-adjacent tiles = TINY BLACK diamonds —
  exactly what the vendor zoom shows (no full outline on them).
- USER-LAW MAPPING D28 P2: 'colored squares when adjacent' = the inset
  class-colour diamond; 'smaller colored squares when not adjacent' = the
  12x6 tiny diamond. 'Semi-transparent' = refcap census shows the tile
  interior is uniformly pal150 (no class blend) — the COLOUR is the
  outline; we reproduce the refcap pixels without an invented alpha.

OPEN LEGS (residual): 0x18b bit0 writer (TPF3-A); [0x48c33] block contents
(TPF3-B); checker-value semantics beyond -1/0; the F7 witness conflict below.


## F7 [UNRESOLVED CONFLICT — carried to tPF-3b, do NOT silently pick a side]

The tPL-V1 lattice witness (tplv1_lattice_witness.py, 100.0% edge support on
t254/02_planet_detail.png) matched EDGE pixels at FULL-diamond boundaries,
and the 433 refcap zoom shows what reads as single full-boundary white/green/
red grid lines. The paint fn 0x3bc52..0x3be50 as read THIS session draws
lines only 2px INSET (64x31) or TINY (12x6) — no full-boundary diamond in
this function. Possible resolutions (probe, don't assume):
 (a) the witness tolerance (t254 is 800x600 = 1.25x; 2px inset -> 2.5 shot px)
     absorbed the inset lines as 'boundary support' — then F5 is complete;
 (b) a SEPARATE full-outline pass exists outside 0x3bb19..0x3c335 (grep
     0x5bf71 callers in the planet painter; the hover pass at 0x3be53 IS
     full-size — maybe the 1174 white px in t254 are hover+structure-edge
     pixels, not grid lines);
 (c) the checker grant for ADJACENT tiles draws the inset at the SHARED
     edge because neighbour inset lines coincide at ±2px — a single
     perceived line.
DECISIVE PROBE for tPF-3b (cheap, no debugger): on the 433 refcap left half,
measure the perpendicular profile ACROSS a known tile boundary (centre law):
if the coloured pixels sit at boundary, boundary±1 -> full outline (b);
if they sit at boundary-2 and boundary+2 with teal between -> inset doubled
(a/c). Record the profile in _wip.
NOTE: t254 has ZERO (16,69,77) px (different render/palette state) — that
screenshot's colours are NOT the 433 conv set; do not mix the two witnesses.

---

# tPF-3b SESSION BLOCK (2026-11-25) — F7 RESOLVED + RULE-B CORRECTION

Pre-flight: SITTING CHECK first (r1_t85g_sitting exit 0, work/r1/
tPF3b_pre_sitting.out): trusted turn-change rows 45,227, newest t=1335 —
IDENTICAL to the tPF2/tPF3/tRS-V2w baselines. No user sitting; assignment stood.

## F8 [measured, bytes work/tPF3b_inset.asm] — THE TWO BRANCHES ARE PURE
## SHRINKS OF THE SAME FULL VERTEX TABLE (F3's geometry CONFIRMED at 0x3bc5b)

Full table = esp+0x260/264 (V0), 0x278/27c (V1), 0x290/294 (V2), 0x2a8/2ac (V3).
- LEGAL 0x3bc5b (edx==-1): V0 y+1 (inc), V1 x-2 (sub eax,2), V2 y-1 (dec),
  V3 x+2 (add eax,2) -> half-extents (32,16) = 64x32 about the SAME centre.
- ILLEGAL 0x3bd4d: V0 y+14, V1 x-28, V2 y-14, V3 x+28 -> half-extents (6,3) =
  12x6. The branches differ ONLY in the shrink amount; both then `mov ax,di /
  push eax` + 0x5bf71 x4 (0x3bd1d / 0x3be13) and both then the state-block
  filler 0x62d15 with [0x48c33]+pen*0x100 (0x3bd3a / 0x3be2c, skipped when the
  value is 0 via `test di,di je 0x3be53`).

## F9 [measured] — THE LINE PEN IS THE CLASS COLOUR, NOT THE GREY RAMP
## (F1's "pen di" reading is RIGHT; F1's 7/8/9/10/13 table is the FILL block idx)

0x3bbd6..0x3bc52 writes TWO registers off the same class byte (esp+0x374):
  EDI = 0xc default / 0 (class 0) / 0x75 (2) / 0x92 (3) / 0xff (4)  <- LINE
  esp+0x364 = 0xd / 7 / 8 / 9 / 0xa                                  <- FILL idx
The line call pushes `mov ax,di` (0x3bcd7/0x3bdcd) => line colour = EDI = the
class colour table (black/117 red/146 green/255 blue/12 white). The hover pass
0x3be53 pushes immediate 0x96 (pal 150). So tileEdgePaletteIndex IS the line
pen law and stays; the 7/8/9/10/13 ramp is only the filler state-block index
(TPF3-B, contents unrecoverable).

## F10 [measured, bytes 0x38493..0x384b2] — RULE B GRANTS UNCONDITIONALLY FOR
## ITEM 0xff: F5's CLASS GATE WAS WRONG

0x38493 rule B reads the CELL-CLASS byte; `jne 0x384d6` grants when class != 0;
when class == 0 it falls to `0x384af cmp dl,0xff / 0x384b2 je 0x384d6` = GRANT
for the painter's item arg. So for item 0xff rule B NEVER vetoes, and
OVERLAY LEGALITY REDUCES TO:  NOT ROCK (0x38519) AND (own slot ACTIVE
(0x385ee skip) OR any ACTIVE 4-neighbour (0x385b7..0x386fc)).
=> BARREN (class 0) non-rock adjacent cells get the INSET diamond too, drawn in
BLACK lines (EDI=0). F5's "class==0 -> TINY always" is REFUTED; F6's "barren
non-adjacent = tiny black" stands (the adjacency veto, not the class, is what
shrinks it). CORRECTION to F3's fill-gate reading: the `test di,di / je 0x3be53`
at 0x3bd31 tests esp+0x364 (grey ramp 7/8/9/0xa/0xd — NEVER zero for any class),
so the filler call is NOT class-skipped; the guard is dead for this selector.

## F11 [MEASURED, DECISIVE] — F7 RESOLVED: THE VENDOR GRID LINES ARE AT THE
## FULL BOUNDARY, NOT 2px INSET. Hypothesis (b) CONFIRMED, (a)/(c) REFUTED.

Static leg (census work/tPF3b_5bf71_census.txt, scripts/_tpf3b_callsites.py):
50 CALL 0x5bf71 sites image-wide; exactly THREE inside the surface painter
0x3bb19..0x3c335 — 0x3bd1d (inset), 0x3be13 (tiny), 0x3bec4 (the HOVER pass,
the only one reading the UNSHRUNK 0x260-family table, colour immediate 0x96).
So NO second full-size pass exists INSIDE this function; any full-boundary
lines must come from elsewhere (the planet picture / another widget) — (b).

Pixel leg (scripts/_tpf3b_f7_control.py, work/r1/screens/t254/
02_planet_detail.png, lattice FIXED at the tPL-V1 witness fit: law B, size 0,
dx=-23, dy=48, png origin (80,100)):
  FULL  half-extents (34,17): 28/28 edges hit  = 100.0%
  INSET half-extents (32,16):  3/28 edges hit  =  10.7%
  TINY  half-extents ( 6, 3):  6/28 edges hit  =  21.4%
The two sample sets are DISJOINT (|FULL n INSET| = 0; 134 vs 196 distinct px),
so this is a genuine either/or on the same mask, not a tolerance artifact.
Discriminative pixels: FULL-only 134 px -> 30 real hits; INSET-only 196 px -> 2.
ANTI-VACUITY CONTROL: a density-matched (731 px in the same 14,111-px field
bbox, 5.2%) uniformly scattered mask scores 0.0% (min=median=max over 60 seeds)
on the FULL geometry — scoring 100% is NOT automatic.
=> The vendor's visible grid lines lie ON the full diamond boundary. The 2px
inset overlay family is NOT what t254 shows.

WHY THE TWO FACTS COEXIST (no contradiction, and the port consequence):
the inset/tiny pass is gated by [ebp+0x18b] bit0 (0x3bbc3, SEAM TPF3-A — writer
UNRECOVERED) and by the checker; t254 evidently had it OFF (only hover+other-
source lines), while the 433 refcap (the user's own screenshot) evidently has
overlay lines ON. Both are the vendor. THEREFORE: the port keeps its EXISTING
full-boundary class-colour outline pass (tPL-V1, pixel-validated by F11 at
28/28) and ADDS the inset/tiny overlay family as the checker-gated second
layer, rather than REPLACING pass 2 as F5 instructed. F5's "PASS 2 in ui.cpp is
REPLACED by the overlay law" is SUPERSEDED by F11.

MEASUREMENT HAZARDS BANKED THIS SESSION:
- The 433 side-by-side composite is RESAMPLED: exact class-colour values are
  gone (green 7 px, red 2, blue 2 image-wide). Pixel laws must use the
  unscaled t254 capture, never the composite. (F7's "decisive probe on the 433
  refcap" spec was UNEXECUTABLE as written — not a failure of the hypothesis.)
- tplv1_lattice_witness.score() samples 8 INTEGER points per 38-px edge that
  COLLAPSE to ~1 distinct pixel per edge group (hit 28 / tot 28 for 7 cells),
  and breaks on first hit. Its "edge support" is an any-hit-per-edge statistic:
  sharp against a scattered mask (control 0%) but NOT a per-pixel fit. Any
  future geometry discrimination must use the disjoint-sample comparison above.
- Do NOT read whole lines of work/r1/playcap/live-timeline.jsonl (10 GB; one
  tail -3 cost ~30k tokens). Use the sitting script or jq with keys only.

## F12 [SHIPPED + PINNED + WITNESSED] — tPF-3b LANDS THE OVERLAY AND THE ANCHOR
- CODE: planetview.h/.cpp gain `TileHalfExtents tileOverlayHalfExtents(bool)`
  ({32,16,32,16} inset / {6,3,6,3} tiny) and `bool tileOverlayInset(camp,star,
  cell)` (item-0xff reduction of checker 0x3830c: rock veto -> own-active skip
  -> ACTIVE-4-neighbour grant -> else refuse) and `Pt structureBlitPos(centre,
  recLeft, recTop)` = (x+L, y-17+T). ui.cpp: overlay is a NEW pass 3 after the
  retained full-boundary pass 2; tile structure art blits via structureBlitPos
  (the invented (w/2,h/2) centring is GONE from that site).
- PINS tests/test_tileoverlay_tpf3b.cpp x5 (geometry, legality incl. the F10
  barren-INSET leg + rock-on-own-slot + out-of-range, anchor arithmetic, the
  MEASURED planitem.shp bbox census through the port's own loader, paint
  wiring). Suite 556 tests / 0 skipped / 0 failed.
- MUTATION 4/4 CAUGHT: anchor offset 17->0 (2 tests fail), F5's refuted barren
  gate re-inserted (legality FAILs at the barren CHECK line 194), tiny bottom
  3->4 (geometry FAIL), rock veto dropped (legality FAIL line 190). Tree
  restored and re-verified green after each.
- WITNESS scripts/tPF3b_witness.sh + tPF3b_overlay_measure.py (Xvfb :99, seed 5,
  nav verbatim from tPF2_witness.sh; centres from the tileCenter() law X=410+
  34col-34row, Y=110+17col+17row+17). Measures class-colour px ON the tiny
  (6x3) paths and OFF the full lattice — a path pass 2 cannot paint:
    SHIPPED  black 395 / green 24 / blue 72 / white 121
    CONTROL  black 323 / green  0 / blue  0 / white   1   (overlay forced onto
      the full boundary, same shot path, same cell set: 2208 tiny-path px)
  The BLACK figure is confounded by structure-art sprite pixels (323 even with
  no overlay), so the honest claim rests on green/blue/white: +24/+72/+120 ONLY
  with the overlay law. Overlay pass is VISIBLE in the port. Shot
  /tmp/tpf3b_shots/03_planet.png.
- NOT CLAIMED: that the overlay's per-cell inset/tiny CHOICE matches the vendor
  on this shot (no vendor capture of the same planet), and the FILL (seam
  TPF3-B) is still not painted — outline-only, per F6's conv(150) census.

## tPF-3c STEP 1 [measured code grep, 2026-11-25] — tPF-1b PRECONDITION FAILS: PORT BEGIN BUILDS turn_ == 0

Question (STATE.md tPF-3c step 1): does the Begin path boot turns!=0? ONE grep,
STOP on fail. ANSWER: NO.
  - campaign.h:850 `int turn_ = 0;` member default.
  - ONLY increment site in the whole rewrite: campaign.cpp:2320 `++turn_;`
    inside Campaign::advance().
  - Begin apply path main.cpp:643-661 (buildCampaign(o,&aerr,&newGame)) sets
    cfg.aiCount/starCount/govByte ONLY — no turn write anywhere on the path
    (grep 'turn_ *=' over rewrite/src/game+ui: no assignment outside advance).
  => A Begin-built PORT campaign enters play at turn 0, structurally identical
     to the seeded builds the tPF-1 soak already ran 30 turns on. A port soak
     adds nothing about the vendor day-20 exit; and the vendor side is
     user-time-gated (D30: user denied --campaign). tPF-1b: precondition
     FAILED -> STOPPED per assignment. The day-20 exit stays OPEN awaiting a
     VENDOR witness (user's own Begin-built game), not a port soak.

## tPF-3c STEP 2 [measured pixels + vision, 2026-11-25] — F6 FILL NO-OP DOES
## NOT GENERALISE: TINY DIAMONDS ARE SOLID CLASS-COLOUR FILLED (433 right half)

Targeted census scripts/tPF3c_fill_census.py + tPF3c_fill_interior.py on the
433 refcap (the only capture with red/green/blue class px), + 400% zoom crops:
 - LEFT half (F6's field): flat teal, interior5x5 blobs of teal150 = 24,727 —
   no class interiors anywhere. F6's no-op reading stands AT THAT STATE.
 - RIGHT half (different zoom, textured tile art): the class-colour px form
   TINY diamonds ~8-24 ref-px wide whose INTERIORS are solid class colour:
   red tiny bbox (1385,447)-(1400,448): interior px (184,40,16)/(176,40,16)
   == conv(117) family (outside = teal (16,64,72)); blue tiny interiors
   (0,0,248) == conv(255); white tiny interiors (160,168,176) == conv(12)
   family; a BLACK tiny diamond's interior stays the dark field (class 0 fill
   skip 0x3be2a 'test si,si je' — byte-consistent). Vision on the crop
   confirms: solid red / solid blue / light-grey tiny diamonds + one large
   blue-outlined diamond whose interior is TEXTURED BLUE (visibly tinted vs
   the teal field, indistinguishable between fill-over-art and blue tile art
   at this resampled scale).
 => THE NO-OP CLAIM IS REFUTED FOR NON-TEAL CELLS. The filler 0x62d15 paints
    the tiny-diamond interior with the CLASS colour (state-block law opaque,
    pixels decisive). F6's teal no-op was the special case fill-colour ==
    base-colour... no: teal field interiors had ZERO class px because teal
    cells' class is the field itself at that zoom. LARGE/inset-diamond fill
    law stays OPEN (stipple vs solid vs tile-art indistinguishable on the
    resampled 433; unscaled t254 has NO non-teal cell: red 6 px / green 6 px
    scattered, no interior).

## F13 [tPF-3c MEASURED — MAJOR CORRECTION] — THE 433 COMPOSITE: LEFT HALF IS
## THE PORT; THE VENDOR FILL IS NOT A NO-OP; FILL MECHANISM = COLOUR-TRANSLATION MAP

1) HALF IDENTITY (vision on the full composite + per-half exact-px census):
   - per-half EXACT conv(150) teal: LEFT 34,194 px / RIGHT 555 px; green146
     127/1; blue255 0/101. An upsampled image CANNOT hold 34k exact palette
     values — the LEFT half is a pixel-exact paste of the PORT's flat-teal
     planet view (opaque tiles + CB sprite = exactly the D28 complaint text);
     the RIGHT half is the VENDOR (textured tile art, structure sprites, the
     t254 art style, scattered TINY diamonds + a few LARGE blue-outlined ones).
   - CONSEQUENCE: F6's "DECISIVE PIXEL CENSUS ... vendor refcap left half,
     20,495 px EXACTLY conv(150)" measured OUR OWN OUTPUT, not the vendor.
     RETRACT: "the vendor interior is 20,495 px of exactly conv(150)" is NOT
     a vendor fact. (tPF-3b's F7 disjoint test used the unscaled VENDOR t254
     capture, so the geometry law stands; only the F6 fill inference falls.)
2) VENDOR FILL IS NOT A NO-OP (assignment step 2 answer, NEGATIVE): on the
   RIGHT (vendor) half, tiny class-colour diamonds have SOLID class interiors:
   red blob bbox (1384,443)-(1400,451) 58 strong-red px / 73 bbox-diamond
   cells = 0.79 FILL (raw px e.g. (188,44,17),(175,47,22) == conv(117) family;
   surrounding field teal (16,64,72)); blue tiny interiors (0,0,248)==conv(255)
   family; white tiny interiors (160,168,176) family; the black tiny diamond's
   interior stays field-dark (class-0 fill skip 0x3be2a — byte-consistent).
   The large blue-outlined diamonds' interiors are TEXTURED BLUE (modulated,
   not flat) — see 3).
3) FILLER 0x62d15 INTERNAL LAW [measured raw disasm 0x62d15..0x63175]:
   args (esp): +8 state block ([0x48c33]+pen*0x100, per-pen CLIP/BOUNDS ctx:
   reads +0 base,+4/+8 extents,+c/+10 limits), +0xc vertex count (4),
   +0x10 = 0x4850c DRAW CONTEXT, +0x14 = FILL MAP POINTER read at 0x63015.
   Interior loop (0x63015..): esi=[ebp+0x14]; per pixel screen := MAP[old
   screen byte] (0x63023/0x63026 mov dl,[eax+esi] / mov [edi],dl; word/dword
   unrolled paths write the SAME byte replicated). So the fill is a 256-entry
   COLOUR TRANSLATION of what is already on screen: texture survives as
   in-family modulation (matches the textured-blue interiors EXACTLY), and an
   IDENTITY map is a pixel-exact no-op. THIS is the mechanism behind the user's
   "SEMI-TRANSPARENT colored squares" — no alpha arithmetic, a per-colour ramp.
   The scanline geometry (0x62d21..0x62f81) is a standard edge-walk into the
   clip ctx; bounds come from the state block.
4) STILL OPEN (TPF3-B refined): (a) WHO writes 0x48c33 (payload-wide census:
   17 a1-READ sites incl 0x3be31, ZERO direct write encodings a3/89 */c7 05
   for imm 0x48c33 -> written indirectly via [reg+disp], window-runtime alloc —
   consistent with DAT_00048c33==0 in every banked save); (b) the identity of
   the MAP at draw-ctx+0x14 (the ramp TABLE — the real alpha law) and its
   writer. The pixel evidence constrains it: for pen=class colour the map sends
   field colours INTO the class family (tiny = near-solid => map is nearly
   constant-class on the sampled colours; large = modulated => identity-ish on
   some colours). NOT recovered; do not invent a ramp.

## F14 [tPF-3c SHIPPED + PINNED + MUTATED + WITNESSED] — TINY FILL LAW IN THE PORT
- CODE: planetview.h/.cpp `bool tileOverlaySolidFill(bool inset,int cls)` =
  `!inset && cls != 0` (law block cites F13); ui.cpp pass 3 fills the TINY
  diamond solid in the class colour before outlining it; inset stays
  outline-only. Stale comment citing the retracted 20,495-px census replaced.
- PIN tiny_fill_law_tpf3c (7 law checks + wiring): suite 557/0/0 (was 556).
  MUTATION 2/2 CAUGHT: drop the cls!=0 term -> FAIL line 278; invert the law
  (fill inset, never tiny) -> 6 FAILs; restored green both times.
- WITNESS (scripts/tPF3b_witness.sh re-run, same nav, /tmp/tpf3c_shots):
  class-colour px OFF the full lattice on the tiny (6x3) paths went 24->46
  green, 72->138 blue, 121->231 white vs the tPF-3b outline-only build — the
  FILL paints (edge px + interior px); black 395->395 unchanged (class-0 skip
  is a no-op against field-dark, as designed). VERDICT(a) OVERLAY PASS VISIBLE,
  WITNESS_RC=0. GATE_EXIT=0.
- STEP 3 (per-cell inset/tiny CHOICE vs vendor): HONEST NEGATIVE. No same-
  planet vendor capture exists (the 433 vendor half is a DIFFERENT planet and
  its checker states are unknown), and no D28 ruling page covers it. The
  choice LAW is byte-pinned (checker 0x3830c item-0xff reduction, tPF-3b); the
  per-cell corroboration stays UN-WITNESSED, named not claimed.

## tPF-3d STEP 0 [measured, census in progress] — RAMP MAP + 0x18b WRITER
- Sitting check: live-timeline.jsonl tail turn=1086 (unchanged since t316-era
  sittings; no new play) -> no r1_t85g_sitting.py rerun needed.
- Census method: objdump -b binary -M intel -D work/ascend_payload.bin ->
  /tmp/payload_all.asm (linear==file offset, P0-law linearity; same windowing
  as scripts/r290_disasm.py).
- RAW-NEEDLE RESULT (payload-wide, tPF-3d): occurrences of imm32 0x48520 as a
  PUSH-IMM32 = 0; a3/c7 05 direct-write encodings to 0x4850c OR 0x48520 = 0.
  push-imm32 0x4850c = 26 sites (callers passing the draw ctx, incl the three
  filler callsites 0x3bd17/0x3be0d/0x3be46 region). => no STATIC initializer
  writes the ramp pointer; consistent with F13(4)(a)'s indirect-write finding.
- [reg+0x14] WRITE CENSUS (42 sites, full list in this doc's scratch): the
  dword-wide candidates that could plausibly be the draw-ctx init are few;
  analysis of register provenance in progress (next section).

## tPF-3d F15 [MEASURED, MAJOR] — THE FILLER ARG LAW IS CORRECTED; THE "RAMP
## TABLE" IS RUNTIME-HEAP AT [ds:0x48c33]+idx*0x100 AND READABLE FROM SAVES
1) ARG LAW FIX (bytes 0x62d15..0x62d9b + callsites 0x3bd3a..0x3be4b, 0x55502):
   filler 0x62d15 stdcall args: [ebp+8]=SURFACE DESCRIPTOR (0x4850c — reads
   +0 bits-ptr, +4/+4-cmp vs the vertex bbox; NOT a clip ctx), [ebp+0xc]=vertex
   count 4, [ebp+0x10]=vertex ARRAY, [ebp+0x14]=MAP POINTER. The painter's
   fill push sequence (0x3be31..0x3be4b) is: eax = [0x48c33] + fillidx*0x100;
   push eax (MAP, arg4) / lea vertex / push / push 4 / push 0x4850c — i.e.
   THE MAP IS THE PER-INDEX 256-BYTE TABLE ITSELF, block base [ds:0x48c33].
   tPF-3c F13(3)'s "MAP = [draw-ctx 0x4850c + 0x14]" is REFUTED at runtime:
   ds:0x48520 holds 640/480 (ds:0x48518..0x48524 = 639,479,640,480 and
   ds:0x48528 = ASCII 'DATA') — 0x4850c is a SURFACE DESCRIPTOR
   {bits=0x28a4f8, 0, 0, 639, 479, 640, 480, 'DATA'}, not a map holder.
2) FILL INDEX IS THE GREY-RAMP SLOT, NOT THE CLASS COLOUR (bytes 0x3bbd6..
   0x3bc4b): [esp+0x364] = 13 default (0x3bbea), overridden by WORD[esp+0x374]:
   0->7, 2->8, 3->9, 4->10 (the second 9-write 0x3bc29 path); the LINE pen EDI
   separately carries the class colour (F9 stands). Fill skip when [esp+0x364]==0
   (0x3bd31/0x3be2a).
3) RUNTIME TABLE READ (bank-play-20261111-t377/60.sav, H=0x88, data base
   0x242000 self-verified via the 639/479/640/480+'DATA' signature):
   [ds:0x48c33] = 0xfcdc7c (HEAP). 256-byte tables at base+idx*0x100:
     idx 0:  39 distinct — many-to-one TRANSLATION (10 11 11 94 94 94 b3 b4 b4
             fe fe a9 a9 a9 3b 3c ...)
     idx 1:  IDENTITY except 0x79->0x80, 0x7f->0x57, 0xf1->0xf0, 0xf3->0x0f (252 distinct)
     idx 7:  103 distinct | idx 8: 92 | idx 9: 80 | idx 10: 83 | idx 13: 112
   => the translucent fill law IS `screen := TABLE[idx][old]` with per-ramp-slot
   many-to-one maps; the tables are RUNTIME-COMPUTED heap data, NOT a static
   block (zero write encodings to 0x48c33 payload-wide, tPF-3c census; zero
   push-imm32/a3/c7-05 to 0x48520, re-run tPF-3d). The table PRODUCER (who
   computes TABLE[idx][i] at init) is NOT located — named-open leg TPF3d-A;
   static [reg+0x14] write census (42 sites) has NO provable 0x4850c-ctx hit
   (the ctx is passed by imm32 push, never held in a reg across a +0x14 write).
4) TPF3-A GATE WRITER CENSUS [CLOSED at bytes, payload-wide]: exactly FIVE
   references to [reg+0x18b]:
     0x3a7cf  mov BYTE PTR [ecx+0x18b],0x5   (ctor 0x3a7b0; bits 0 AND 2 SET at
              construction -> overlay pass + BLIT-2 enabled by DEFAULT)
     0x3ae66  xor BYTE PTR [eax+0x18b],0x1   (interactive bit0 TOGGLE, message-
              handler region 0x3adfc..0x3ae6d; widget ptr = [ebp-0x8])
     0x3b9e4  read &4 (BLIT-2 gate, t428d)   0x3bbc3  read bit0 (overlay gate)
     0x3ca85  lea edx,[ecx+0x18b] + ebx=1 -> call 0x1db44/0xec48 (bit-set/clear
              helper pair, ebx discriminates)
   Ctor chain: alloc wrapper 0x3a750 (sole caller 0x577b5) -> call 0x3a7b0 at
   0x3a762. So no code ever CLEARS bit0 except the toggle: a widget built by
   this ctor shows overlays from birth; the port's unconditional overlay is
   CONSISTENT with the vendor default (corroboration, not a new law).

## tPF-3d F16 [MEASURED, DECISIVE] — THE SEVEN RAMP TABLES ARE BYTE-STABLE
## ACROSS 60/60 BANKED SAVES: THE SEMI-TRANSPARENCY LAW IS NOW CITED DATA
scripts/tPF3d_ramp_runtime.py over bank-play-20261111-t377 + -late +
bank-t1086-preplay (60 saves): every save passes the base self-verification
(ds:0x48518..0x48524 == 639,479,640,480 and ds:0x48528 == 'DATA'), every save
reads [ds:0x48c33] == 0xfcdc7c, and all 7 tables at base+idx*0x100 for
idx in {0,1,7,8,9,10,13} hash to EXACTLY ONE variant across 60/60 saves
(FULL HEX PRINTED BY THE SCRIPT — the authoritative copy; do not retype it
from this doc). Key structural facts read from the tables:
  idx 1  = IDENTITY except FOUR swaps 0x79->0x80, 0x7f->0x57, 0xf1->0xf0,
           0xf3->0x0f (252 distinct; tPF-3e byte re-count — the first draft of this line
           had the first pair transposed and omitted 0x7f)  (a "solid/no-op"
           slot: filling with it leaves the screen as-is -> explains how a fill
           call can be visually a no-op WITHOUT the map being an identity)
  idx 0  = 39 distinct values, many-to-one (field colours collapse into a small
           family: 0x94/0xb3/0xb4/0xa9/0xe1/0xfe dominate)
  idx 7/8/9/10/13 = 103/92/80/83/112 distinct — graded blends (the ramp ladder)
CONSEQUENCE FOR THE PORT: the vendor fill law is not "paint class colour" but
`dst[i] := TABLE[idx][dst[i]]` with the tables above. A faithful port either
embeds these 7x256 tables as data (they are vendor law data, byte-stable, and
the corpus is the citation) or reproduces the map law; the producer that
computes them at init is still unnamed (TPF3d-A below).

## TPF3d-A [NAMED OPEN, honest negative] — THE TABLE PRODUCER IS NOT LOCATED
Static routes tried and exhausted this session (do NOT repeat): (a) payload-wide
write census for imm32 0x48c33 — 38 occurrences, ALL reads (a1/a3-absent,
0x8b 0d, add-imm, push); ZERO write encodings, so the block base is stored
indirectly; (b) write census for 0x48520 — zero hits of any kind (the F13(3)
route was a dead end, see F15(1)); (c) [reg+0x14] write census — 42 sites, none
provable against the 0x4850c ctx (the surface descriptor is always passed as an
imm32 push, never held in a register across a +0x14 store); (d) the 24
mov-reg,0x4850c sites are all consumer-side (rep movs sources / push args).
Best remaining route (NEXT): the heap block is 0x100*256 = 64 KiB-strided, so
the allocator is asked for a large block near session start — search for the
alloc whose size/stride matches and for a loop writing 256 iterations per slot
(indexed [reg+idx] stores with a table-of-256 source), OR observe it live with
scripts/r1_wp_session.py --target data:0x48c33 (write-watchpoint, one-shot,
already-built harness). The 60/60-stable tables are enough to SHIP the law
without the producer; the producer only matters if a table must be generated
for a palette the corpus never covered (it is 640x480 game.pal only).

## tPF-3e F17 [MEASURED, bytes 0x3c2c5/0x3c2cc + 0x3bbd6..0x3bc52] — THE LADDER
## INPUT WORD[esp+0x374] IS THE CELL CLASS BYTE; THE OVERLAY FILL INDEX LAW IS
## FULLY DERIVABLE (and tPF-3c's "class-0 NEVER filled" is SUPERSEDED)
- Writer of the ladder input (0x3c2cc): `mov al,BYTE PTR [edx]` (0x3c2c5, EDX =
  [esp+0x34c] = the per-cell record pointer loaded at 0x3c2ad; record byte 0 =
  the slot CLASS byte — same byte tileEdgePaletteIndex consumes), then
  `mov DWORD PTR [esp+0x374],eax` (0x3c2cc, eax zero-extended AL). Immediately
  before: `mov edx,0xff` (0x3c2c7) — the F5 item-0xff overlay pass.
- LADDER (0x3bbd6..0x3bc4b, re-disassembled verbatim tPF-3e): default
  [esp+0x364]=13 (0x3bbea, ESI=0xd preloaded 0x3bbd6); WORD[esp+0x374]:
  0 -> 7 (0x3bbf5), 2 -> 8 (0x3bc1b), 3 -> 9 (0x3bc33), 4 -> 10 (0x3bc4b);
  any other class byte KEEPS 13. Parallel EDI (line pen, F9): default 12,
  2->0x75(117), 3->0x92(146), 4->0xff(255) — class 0 keeps pen 0 (black lines).
- CONSEQUENCE (byte-level, supersedes tPF-3c F13's "TINY class-0 never
  filled"): the fill-skip tests 0x3bd31/0x3be2a read [esp+0x364] — the FILL
  INDEX — not the pen. In the overlay pass the ladder yields 7/8/9/10/13,
  NEVER 0, so BOTH branches always call the filler 0x62d15 (gated only by
  +0x18b bit0, TPF3-A). A black (class-0) tiny diamond IS map-filled with
  TABLE[7]; its interior stays dark because TABLE[7] maps dark -> dark
  (7->0xc8, 0xc8->0xc6... per F16 hex). The tPF-3c pixel observation (black
  interior = field-ish) is CONSISTENT with map-fill through idx7; the
  "never filled" reading was the wrong mechanism.
- NO ROCK LEG in the ladder: a rock-flagged byte (class|8, e.g. 8/10/11/12)
  matches none of {0,2,3,4} -> fill idx 13 (the line pen keeps the rock-white
  default per the tPL-V1 law).

## tPF-3e F18 [measured law data + SHIPPED] — MAP-FILL IN THE PORT: ANALYTIC
## SOURCE SET, PEN FIXED POINTS EXPLAIN THE VENDOR PIXELS
- scripts/tPF3e_gen_tables.py reads the 7 tables from the banked corpus with
  the tPF3d law + self-verification (60/60 saves, one variant each) and emits
  rewrite/src/ui/rampfill_law.h (byte-exact rows + sha256 provenance). Header
  rows verified EQUAL to the tPF3d printed hex for all 7 slots. (Trap hit:
  the ds:0x48518 signature dims are FOUR u32, not u16 — "<4I" over 16 bytes.)
- FIXED POINTS (decisive for why the vendor screen shows class-coloured lines
  even though the filler runs AFTER the line loop 0x3bcd7..0x3be28): each
  class pen is a fixed point of ITS OWN ladder table: T7[0]==0, T8[117]==117,
  T9[146]==146, T10[255]==255; the exception is class 1 (pen 12, T13[12]==13
  -> the vendor maps its own white line to ramp-13). tPF-3c's "solid red tiny"
  is EXPLAINED: the 12x6 diamond is nearly ALL outline, outline red survives
  the map (fixed point), and the field between outline lines maps 150->201
  (61,53,57 grey-red) — the 0.79 fraction was line-dominated.
- PORT SHIP SHAPE (ui.cpp pass 3, replaces tileOverlaySolidFill): per overlay
  row, span = he.left*(ht-|dy|)/ht (the port's own floor-span raster); the two
  ENDPOINT pixels are pen pixels (SDL_RenderDrawLine's edges land there) and
  map through row[tileEdgePaletteIndex(cls)]; the interior run maps the pass-1
  screen value pal 150 through row[150]. Analytic source set == what the
  vendor filler would READ at that moment (pass 1 fill 150 + the overlay's own
  lines; no other pass overlaps the strictly-inside diamond; structure art
  blits AFTER). Seam named: if SDL's line raster deviates from the endpoint
  law mid-edge, a pixel or two maps as fill instead of pen (1-step ramp
  difference; the law itself is unaffected).

## tPF-3e F19 [witness-measured, Xvfb 640x480] — MAP SHIPPED: CLASS-PX COUNTS
## DROP AS THE INTERIOR MODULATES; THE OVERLAY BECOMES A SINGLE EDGE-SET PASS
- WITNESS TRAP (first run misled me, recorded so no one re-runs it):
  scripts/tPF3b_witness.sh runs ./rewrite/build/ascendancy — building ONLY
  run_tests witnesses the OLD app. Run 1 (stale 15:28 binary) reproduced the
  tPF-3c numbers EXACTLY (green 46/blue 138/white 231/black 395/red 0), which
  is how I caught it. Always `make run_tests ascendancy` before witnessing.
- MAP-SHIPPED WITNESS (fresh binary): green 46->18, blue 138->54, white
  231->~1..31, black 395->377, red 0 (red is ZERO on this witness in EVERY
  build — there are no tiny red cells on the home planet; it is NOT evidence
  either way). The drop IS THE LAW WORKING: the interiors are no longer
  solid/equal class colour — they are TABLE[idx][150] (never a class colour,
  F18) — while the DIAMOND EDGES keep the class colour because each pen is a
  FIXED POINT of its own table (T7[0]=0, T8[117]=117, T9[146]=146,
  T10[255]=255). VERDICT(a) still OVERLAY PASS VISIBLE (strong off-lattice
  449 >= 20). The absolute counts are fit-dependent (the measure script's
  +-1 band about its own lattice fit), so the DIRECTION + edge survival is
  the signal, not the numbers.
- SHIP SHAPE (supersedes the endpoint heuristic AND the SDL line draw): the
  overlay paints ONE pass over the diamond span; source = pen index iff the
  pixel is on the diamond EDGE SET (four edges rasterised by our own integer
  Bresenham through the vertex deltas, deterministic), else 150; the pixel
  drawn is ALWAYS conv(TABLE[idx][source]). "Draw pen then map" collapses to
  this because of the fixed points, so no separate line pass is needed.
  For these two diamond shapes (32,16)/(6,3) the span endpoints and the
  Bresenham edge set COINCIDE (span is exact: 32*(16-dy)/16 and 6*(3-dy)/3
  never floor off) — the edge-set form is shipped because it states the law
  geometrically instead of accidentally.
- WHY NO RAW STRAY PX (measured side-effect): the tPF-3c build drew SDL lines
  whose raster deviates ~1px from the ideal boundary OUTSIDE the mapped span,
  leaving raw class-colour stray px (white 31 -> 1 after the line pass was
  removed). The single-pass form cannot emit unmapped pixels.
