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
