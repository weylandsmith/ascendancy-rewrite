# _wip_t418 — PLANET VIEW: THE PLANET ITSELF + TILE GRID (phase 15, D15)

Task (STATE queue row t418): planet view renders NO planet; vendor = PICTURE
of the planet overlaid with colored ISOMETRIC squares, selectable,
adjacent-to-structure -> build order. Reuse the t406 project-set seam.

## F0. Session-start facts (from disk, before probing)
- Current port state-17 painter: ui.cpp ~1395-1465 — text-only readout +
  vector panel rects + PLANLIST overlay. NO planet art, NO tile grid.
- planetview.{h,cpp} = pure law (readout, projectOptionsFor,
  projectOrderable, projectRowFor). t406 pins test_planetview_t406 x4.
- Slot-array law (income-law.md S4/S6h, verbatim): slot = 4 bytes
  {byte0 terrain class, byte1 itemIdx (0xff empty), u16 flags@+2 bit0
  ACTIVE}; slot ptr [rec+0x10]; terrain cells = u16[rec+0x18]; total slots
  = +0x1a (terrain + 10 orbital ring); row table stride 15 (0x3c211 imul
  0x22 / 0x395f5 imul 0x4-1 pattern).
- ADJACENCY law cited (income-law.md S4 last bullet): new item on terrain
  cell with slot word+2 bit0 CLEAR -> FUN_0003965c + four FUN_000395c4
  probes (call sites 0x3860e..0x38661 in work/r331_disasm.txt); ANY ACTIVE
  (word+2 bit0) neighbour refuses.
- FUN_000395c4 (disasm 0x395c4..0x395c4+0xc4, VERIFIED this session):
  (eax=rec, edx=row 0..14, ebx=col) -> slot idx or 0xffff. Row start =
  SUM(table[i] i<row) where table = BYTE[rec_row_base + i*15 + 11]; col in
  [0,width=BYTE[base+row*15]); idx = start+col. => THE GRID IS 15 ROWS of
  per-row widths (a row-width table at stride 15, byte +11). The paint body
  uses the SAME row-start/width reads (0x3bb8e mov al,[0x7445c+edx] /
  0x3c1fa mov al,[0x744a8+ebx]).
- FUN_0003965c (VERIFIED): (eax=rec, edx=cell) -> packed (lo16=row,
  hi16=col) for terrain cells (cell < u16[rec+0x18]); 0xffffffff otherwise.
- Paint body = 0x3b96c (planets-ui.md S1; full listing work/t198_planwin.asm).
  Per-row loop 0x3bb2c: rowStart = row*15 - row (i.e. *14) at 0x3bb2c..;
  x-cursor starts 0x6e=110 and steps +17 per row (0x3bb5d), y-cursor starts
  0x19a=410 stepping -34 per row; per-cell 0x3c211 idx = rowStart + col*34
  (imul 0x22) x-field, 0x3c23f col*17 y-field; 0x3c200 skips cells with
  col >= width.
- NATIVE VISION grade of the vendor capture
  work/r1/screens/t254/02_planet_detail.png (this session): TOP strip = 5
  gauge panels (x~64..636, y~95..185); BELOW: black starfield field; LARGE
  planet sphere centred ~ (390,320) diameter ~250; tiles are ISOMETRIC
  DIAMONDS overlaid on the disc (blue-water tiles visible at the top rows,
  green/brown lower), structures drawn ON the diamonds; small ship sprite
  upper-left + a small structure-cluster sprite lower-left; NO visible text
  in the field area.
- t254 census note (shp.md S23.2): same capture, pop grid 39 slots painted
  region; PLPOP grid uses 17np k1/k2/k3 10px icons.

## F1 GRID LAW [verified verbatim, FUN_000395c4 + FUN_0003965c disasm
work/r331_disasm.txt 0x395c4..0x395c8 + 0x3965c..0x396cb, this session]
The surface grid = 15 row-slots; per size class (rec+0x14 = min(size,4)):
  rowWidth  C[size][0..14]  (DAT 0x744a8, grid C of planitem.txt)
  rowOffset B[size][0..14]  (DAT 0x7445c, grid B of planitem.txt)
row valid cols: B[size][row] <= col < B[size][row] + C[size][row]
  (0x3962b cmp edi(col), GridB -> jl fail; 0x3963b cmp col, B+C -> jge fail)
CELL INDEX = cumWidth(size,row) + col - B[size][row]
  (0x395f5..0x39612 ebx = SUM GridC[size][0..row-1]; 0x3963f..0x39647
   ebx = cum + col - B). 0xffff outside. row in [0,15), col >= 0 (0x395dc..).
INVERSE FUN_0003965c: cell < WORD[rec+0x18] (terrainCells) required, else
  0xffffffff; walks rows while cum+B+C <= target; returns (row<<16)|col
  with col = target - cum + B[size][row]  [verified: 0x396af..0x396c2;
  caller 0x38613..0x3861b splits hi16=row lo16=col].
planitem.txt grids [verified, extracted/ascend00/planitem.txt after '#',
tokens 45..119 = B, 120..194 = C; loader FUN_00037fc0 t294 law; C row sums
7/11/23/45/73 == +0x18 census]:
  B0 0 0 0 0 4 4 5 0 0 0 0 0 0 0 0   C0 0 0 0 0 2 3 2 0 ...           (sum 7)
  B1 0 0 0 4 3 4 5 6 0 0 0 0 0 0 0   C1 0 0 0 1 3 3 3 1 ...           (11)
  B2 0 0 3 2 3 3 4 5 7 0 0 0 0 0 0   C2 0 0 1 4 4 5 4 4 1 ...         (23)
  B3 0 2 1 1 2 2 3 4 5 7 0 0 0 0 0   C3 0 2 5 6 6 7 6 6 5 2 ...       (45)
  B4 1 0 0 0 1 1 2 3 4 5 7 0 0 0 0   C4 3 6 7 8 8 9 8 8 7 6 3 ...     (73)
WORKED EXAMPLE size class 2 (23 cells): rows with C>0 are rows 2..8, widths
1,4,4,5,4,4,1, offsets 3,2,3,3,4,5,7 — a diamond silhouette; row2 col3 ->
cell0; row8 col7 -> cell22. CUM WIDTHS 0,1,5,9,13,17,21,25,26.

## F2 ISOMETRIC SCREEN LAW [verified immediates, paint body 0x3b96c,
work/t198_planwin.asm 0x3bb2c..0x3c26d]
Per-row loop: x-cursor 0x354 starts 0x6e=110, +=0x11=17 PER ROW (0x3bb5d),
terminates at 0x16d=365; y-cursor 0x320 starts 0x19a=410, -=0x22=34 PER ROW.
Inner loop iterates col over [B[row], B[row]+C[row]) (0x3bb8e..0x3c20b:
counter 0x318 initialised to BYTE[0x7445c+i], runs while < B+C); per-cell
position step: x += 0x22=34 (0x3c211 imul 0x22), y += 0x11=17 (0x3c23f imul
0x11). => center(row,col) = origin + col*(34,17) + row*(17,-34) (col ABSOLUTE
incl. B). Tile DIAMOND corners pushed at 0x3c224/0x3c252/0x3bc78..: x±0x22,
y..y+0x22 with mid y+0x11 => diamond 68 wide x 34 tall; lattice spacings
(34,17) and (17,-34) are EXACTLY the diamond-tiling half-steps (verified:
neighbour left-vertex == current bottom-vertex), so the four probe
neighbours (row±1,col),(row,col±1) ARE the four visual edge-neighbours.
Hit-test = diamond inequality |px-cx|/34 + |py-cy|/17 <= 1 over cells.
Bare-tile fill immediate 0x960000 stored 4x at 0x3c274..0x3c295 => palette
index 0x96=150 per diamond vertex block; the 8-byte table at 0x892ac
{00 00 01 03 01 03 02 02} (copied to esp+0x310 at 0x3c2a3) selects a
24-byte-stride vertex-parameter set per something-per-class — NOT resolved;
NAMED SEAM (per-class colour law unmapped; port fills pal[150] + rock
darker, documented default).

## F3 ADJACENCY LAW [verified verbatim, build-checker 0x385b7..0x3870d +
probes 0x3860e..0x38661; income-law.md S4 bullet confirmed at asm level]
For a NEW item on cell bx: skipped entirely when cell >= WORD[rec+0x18]
(0x385b7 jae -> accept), when the cell's own slot word+2 bit0 (ACTIVE) is
SET (0x385ee jne -> accept), when item==5 Colony (0x385f6) or item==38
Xeno Dig (0x385ff). Else FUN_0003965c(rec,cell) -> (row,col); four probes
via FUN_000395c4: (row-1,col) 0x38624..2b, (row+1,col) 0x3863a..3d,
(row,col-1) 0x3864a..4f, (row,col+1) 0x3865c..61. Each probe: if cellIdx
!= 0xffff AND slot[cellIdx] word+2 bit0 (ACTIVE) -> REFUSE (0x386fe, edi=1
-> return 0xffffffff). i.e. an inactive new item may NOT touch an ACTIVE
neighbour. (The engine's completion picker rule G — assign cell ADJACENT to
an active item — is the OTHER law, income-law S13, census r1_built_cell_law.py.)

## F4 DISC RECORD [inferred, seam named]
planalNN.shp: 11 libs (gwshare/TOC; named for PLANETALLOC's HELPINDEX
planal), each 5 recs, dims ladder 47/75/103/140/189 (shp.md S23.3). Port
blits planal[terrainRow].record(sizeIdx) centred on the grid as THE PLANET
PICTURE. [unverified] rung==size-class and terrainRow==lib choice are
contextual inferences (11 rows x 5 sizes matches terrainRow 0..10 x size
0..4 exactly; t196 vision read called planal00 "crescent + 4 closeups").
NAMED SEAM: vendor disc provenance inside 0x3b96c unresolved (the 0x3b98b
site blits slot 44=17np k4/k5 BACKDROP panels, not the disc); witness that
would close it = live-RAM census of cache 0x9f10c slot ids + rec selectors
during a vendor planet-view frame.

## F5 structure art [verified t254]
planitem.shp record index == itemIdx (1:1 pixel match law, shp.md S23.4).
Port blits planitem k[item] at the tile centre for occupied cells.

## F5 implementation + pins + witness (in progress)
