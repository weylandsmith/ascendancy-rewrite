# tPL-V1 WIP — TILE GRID PITCH + COLORS (D26)

Assignment (STATE.md 2026-11-23): isometric grid rows ADJACENT/TOUCHING on
both axes (ours has gaps); colors LIGHT white/blue/green/red + black drawn
distinctly (derive from vendor tile-class law); shape/size/angle APPROVED —
do not change.

## F0 — STATE OF THE PORT (before this iteration)
- tileCenter planetview.cpp:129-135: `110 + col*34 + row*17, 410 + col*17 - row*34`
  (t418 F2 shorthand "center = origin + col*(34,17) + row*(17,-34)").
- ui.cpp:2086-2114: bare fill pal[150] uniform + rock cells halved
  [documented default], diamond 68x34 (corners ±34/±17), outline (24,24,32).
- t421 CLOSED the "per-class colour table 0x892ac" as a MISPARSE — uniform
  pal[150] "matches the cited law" FOR THE FILL. The D26 task says the
  vendor grid shows white/blue/green/red — so a colour law exists SOMEWHERE
  in the paint path; find it (candidate: the cell state byte word+2 bit0
  active flag, or the tile/structure art itself).
- Witness disagreement on whether the vendor paints the lattice at all:
  t428 F3 (witness A field BLACK) vs witness B (t254/02_planet_detail.png
  = sphere + full lattice). t428e PROVED the paint body reaches the lattice
  region site (no ret between head and 0x3c7bc).

## F1 — THE PITCH LAW RE-DERIVED: THE PORT TRANSPOSED THE TWO CURSORS
work/t198_planwin.asm paint body 0x3b96c, grid region. Cursor setup 0x3bb19..
0x3bb46 [verified verbatim this iteration]:
  0x3bb19 edx := [esp+0x340] = size; 0x3bb20 ecx := 0x6e; 0x3bb27 esi := 0x19a
  0x3bb2c shl 4 / 0x3bb36 sub edx => eax = size*15 (the ROW-TABLE index,
  stride 15 per size class — NOT a row counter; 0x3bb63 inc edx per row, and
  0x3bb8e mov al,[0x7445c+edx] indexes grid B[size][row])
  0x3bb2f [esp+0x354] := 110 ; 0x3bb38 [esp+0x320] := 410
Per-row step 0x3bb5d..0x3bb72: [0x354] += 0x11 (17), [0x320] -= 0x22 (34),
row-table idx += 1, loop exits when [0x354] == 0x16d (=110+17*15, 15 rows).
Row head 0x3bb9b..0x3bbb7: [esp+0x33c] := [0x320] (the 410/−34 cursor),
[esp+0x350] := [0x354] (the 110/+17 cursor).
PER-CELL 0x3c211..0x3c25f [verified verbatim]:
  eax = 0x22*col ; edx = [0x33c] + eax ; [esp+0x260] := edx
  [esp+0x278] := edx + 0x22 ; [esp+0x290] := edx ; [esp+0x2a8] := edx − 0x22
  eax = 0x11*col ; edx = [0x350] + eax ; [esp+0x264] := edx
  [esp+0x27c] := edx + 0x11 ; [esp+0x294] := edx + 0x22
WHICH FIELD IS SCREEN X — the diamond corner arithmetic decides it: the field
carrying the SYMMETRIC ±0x22 offsets (0x260 → 0x278/0x2a8 = ±34) is the
HORIZONTAL extent (68 wide), the field carrying 0 / +0x11 / +0x22
(0x264 → 0x27c mid, 0x294 bottom) is the VERTICAL extent (34 tall). So
  X = 410 + 34*col − 34*row   (from the 410/−34 cursor)
  Y = 110 + 17*col + 17*row   (from the 110/+17 cursor)
i.e. center(row,col) = (410 + 34*(col−row), 110 + 17*(col+row)).
TILING TEST: col step (34,17), row step (−34,17) => |det| = 34*17+34*17 =
1156 = the diamond area (68*34/2) => an EXACT edge-to-edge tiling, ZERO gaps.
The PORT law (planetview.cpp:129 `110+col*34+row*17, 410+col*17−row*34`)
assigns the cursors the OTHER way — col step (34,17), row step (17,−34) =>
|det| = 34*34+17*17 = 1445 > 1156 => 80% coverage, i.e. the reported GAPS.
The t418b F7 witness note "diamond area 1156 < lattice cell 1445" recorded
the gap arithmetic without noticing it refuted the tiling claim.
CORROBORATION [inferred]: size-class-4 (73 cells, B4/C4 of _wip_t418 F1)
under the corrected law spans X 274..546, Y 110..467 — inside 640x480; under
the port law X reaches 654, off-screen right.
ORIENTATION: with the corrected law the four adjacency probes (row±1,col),
(row,col±1) land at screen offsets (∓34,+17) and (+34,+17)/(−34,−17) — the
four VISUAL edge-neighbours of the diamond, which is what the t418 F3
adjacency law requires. CONFIRMATION WITNESS still owed: measure the vendor
lattice orientation/pitch on work/r1/screens/t254/02_planet_detail.png.

## F2 — THE TILE FILL COLOUR LAW IS A TERRAIN-CLASS SELECTOR (0x3bbcb..0x3bc52)
Per-cell the paint body caches the slot bytes: 0x3c2aa al := BYTE[[0x34c]+1]
-> [esp+0x37c] (itemIdx; 0xff = empty, confirmed by the three
`cmp $0xff,[esp+0x37c]` gates at 0x3be72/0x3bed1/0x3c2ff) and 0x3c2c5 al :=
BYTE[[0x34c]+0] -> [esp+0x374] (TERRAIN CLASS; bit3 = rock, tested at
0x3bedb `and $0x8,al`). Selector chain, fill-colour slot [esp+0x364]:
  default 0x364 := 13 (0x3bbd6/0x3bbea)
  [0x374]==0 -> 7   (0x3bbf5)      [0x374]==2 -> 8  + edi 0x75 (0x3bc11)
  [0x374]==3 -> 9   + edi 0x92     [0x374]==4 -> 10 + edi 0xff
  (edi/0x364's companion is DEAD here — reloaded at 0x3bd2a/0x3be20)
Then 0x3bd3a/0x3be2c: fill block ptr := [0x48c33] + colour*0x100 (256-byte
draw-state blocks per colour) passed to the polygon filler 0x62d15 with
count 4. TWO vertex-struct variants: REFUSED cell (checker 0x3830c returned
0xffffffff for item 0xff, edx==-1 at 0x3bc55) uses a HAIRLINE inset of 2/1
px; GRANTED cell uses 0x1c/0x0e (28/14) — a much smaller inset diamond.
OPEN: is the block index a game.pal palette index? Probe = converted game.pal
indices 7/8/8/9/10/13 vs the user's "white/blue/green/red".

## F3 — WITNESS VERDICT: CANDIDATE B (EXACT TILING) 100% vs PORT LAW 26%
scripts/tplv1_lattice_witness.py on the VENDOR capture
work/r1/screens/t254/02_planet_detail.png (png 800x600 16-bit; screen origin
(80,100) per t428 F9): edge-colour census found class-1 WHITE (idx 12 ->
conv 203,203,203) 2354 px (1830 in the field), class-2 red 6, class-3 green
6, class-4 blue 0, class-0 black 337933 (dominated by the starfield —
excluded from lattice scoring). Brute-force alignment (centroid-seeded
coarse +-34 step2 + 1px refine, all 5 size classes):
  law A (PORT, transposed cursors): best 26.0% edge support
  law B (re-derived F1):            best 100.0% edge support (size0, dx,dy)
  control: shift the best fit by (0,-10) -> 0.9%; (23,-48) -> 1.9%
  baseline white density in the field: 0.6% — the 100% is not luck.
The 7 fitted cells (size 0 = 7-cell home planet) ALL have white edges — the
t254 planet IS a size-0 developed world; its classes are class-1-dominated,
which is why only white shows. THE COLOUR LAW ITSELF (edge idx per class
0:0 1:12 2:117 3:146 4:255 = black/white/red/green/blue in game.pal-conv)
is exactly the user's D26 list "white/blue/green/red (+black distinctly)" —
class semantics per income-law.md S6h: 0 BARREN, 1 base, 2/3/4 the bonus
terrain weights (w0..w3 roll @0x37f0e region; orbital cells FORCED class 1).
GREY-RAMP ARM (F2's 7/8/9/10/13): gated by BYTE[EBP+0x18b] bit0 (0x3bbcb je
0x3be53 — when CLEAR the cell draws ONLY the bare 0x96 fill: no edges, no
grey fill); FILL colour counts in t254 = ZERO -> in this witness the arm was
not taken; the visible tile INTERIOR is the uniform pal[150] fill (measured
(123,121,140) at fitted centres == conv pal idx 150 within jpg noise). NAMED
SEAM TPLV1-A: what sets 0x18b bit0 (widget-mode?) and the 0x48c33 block
contents (palette vs draw-state) stay unresolved; the port ships the
witnessed path (fill 150 + class-coloured edges).

## F4 — PORT LANDING (tPL-V1)
PORT: planetview.cpp tileCenter CORRECTED to (410+34*(col-row),
127+17*(col+row)) (exact tiling; the +17 is anchor->centre); NEW pure law
tileEdgePaletteIndex (0->0 black, 2->117 red, 3->146 green, 4->255 blue,
else 12 white — EXACT compares, rock-flagged byte takes white); ui.cpp
painter: uniform pal[150] fills PASS 1 then class-coloured outlines PASS 2
(shared edges stay visible), invented (24,24,32) outline and rock-darker
fill DELETED (neither had a vendor basis; t421: uniform fill).
PINS: planetgrid_lattice_t418b RE-DERIVED (steps (34,17)/(-34,17), origin
(410,127), size-2 row2col3 -> (444,212), per-cell edge-mid probe (+17,+8)
must hit its OWN tile — 595+ vs 561 discriminator); NEW
planettile_edge_colour_tPLV1 (incl. 9/10/0xff -> white). SUITE 502/0/0
(was 501; +1 test).
LIVE WITNESS scripts/tplv1_port_witness.sh seed 5: under the CORRECTED law
clicks at the computed centres (410,297) and (444,280) both LAND on the
adjacent tiles they name (log "ui planet tile 5 selected" then "tile 3" —
size-1 planet Amoroso I, home-cb cell 1). HONEST NEGATIVE: the pixel census
scripts/tplv1_port_census.py did NOT reach VERDICT PASS this iteration —
the first run's root grab was 800x600 (a stale Xvfb :97 offset the 640x480
window; a stray :9 Xvfb exists too), and the corrected-law fit on that shot
found the lattice at a constant (dx,dy) offset with 11/11 fill hits at
size 1 — i.e. THE PORT'S OWN RENDER ALREADY SATISFIES LAW B (11/11 == the
full size-1 cell set; law A maxed 10/23), only the census's zero-offset
assumption failed. The script now grabs the app window by name on a fresh
display (:99); that re-run was cut by the iteration budget. NEXT iteration
should re-run scripts/tplv1_port_witness.sh + tplv1_port_census.py for the
formal PASS before tPL-V2 consumes this grid law.
HAZARD BANKED: never trust `import -window root` on this host — stale Xvfbs
(:9, :97) sit on other displays AND the production dosbox may hold :97;
grab the app window by name and assert the png is 640x480.

## F5 — tPL-V1f FORMAL PORT CENSUS: VERDICT PASS (2026-11-24)
CENSUS v2 scripts/tplv1f_census_v2.py on a CLEAN window grab
(scripts/tplv1_port_witness.sh, fresh Xvfb :99, seed 5, OUT=/tmp/tplv1_shots_f2):
  VERDICT PASS (exit 0), REPRODUCED 2x (f1 + post-mutation-restore f2):
  old (24,24,32) outline px 0; size1 fill 11/11 (10 exact + 1 art-covered
  cell (4,3) = structure blit (113,81,40) at centre); adjacency 12/12 pairs
  OK (3px-inside probe each side non-black, midpoint black|edge|art);
  CONTROL: 5 law-A centres fall OUTSIDE the B-cell union — ALL black (had
  the port painted law A they'd carry fill). Anti-vacuity PROVEN: mutant
  M-T1 (tileCenter re-transposed to law A, scripts/tplv1f_mutate_census.sh)
  -> census FAIL "best size class 4 != expected 1"; source restored (md5
  9c55fe6a3ccfb7130013048f57bd9b39), rebuild green, suite 502/0/0.
WHY v1 failed (its two premises were WRONG for this shot, not the law):
  (a) >=200 white edge px: the seed-5 home planet's SURFACE classes are ALL
      0 (app log "ui planet classes 0 0 0 0 0 ..."), and class 0 draws BLACK
      edges per law 0x3bbd6 — indistinguishable from starfield. Edge-COLOUR
      pixels are pinned by planettile_edge_colour_tPLV1, not by pixels here;
      census v2 reports them (white 94) without asserting.
  (b) "midpoint non-black": the midpoint sits ON the shared edge line, which
      is legitimately black for class-0 tiles. Gap signature is instead a
      BLACK point that should be INSIDE a diamond -> census v2 probes 3px
      inside each side of every adjacent pair.
GRAB LAW (supersedes the F4 hazard note): `import -window NAME` needs an
EXACT WM_NAME match; the campaign window is titled "Ascendancy" (title.cpp:
135) but becomes "Ascendancy rewrite (P5a)" (ui.cpp:114/122) at the RESUME
transition -> name-grab hung/failed exactly after that click. WORKING
RECIPE (shipped in tplv1_port_witness.sh shot()): ./tools/winpos
"Ascendancy" resolves substring + geometry, then `import -window root
-crop WxH+X+Y +repage` + assert 640x480. Also: DISPLAY must be EXPORTED in
the script (per-command DISPLAY= prefixes did not reach `import` in the
probed shell); kill stale lock files (/tmp/.X99-lock, /tmp/.X11-unix/X99)
before starting Xvfb.
DIAG SCRIPTS KEPT: scripts/tplv1f_census_diag.py (per-cell centre dump),
scripts/tplv1f_pair_probe.py (adjacency pair probe), scripts/tplv1f_probe.sh
(grab recipe), scripts/tplv1f_mutate_census.sh (M-T1). The v1 census
scripts/tplv1_port_census.py stays on disk as the refuted-premises witness;
tplv1f_census_v2.py is THE census for tPL-V2 onward.

## F6 — PRODUCTION-RING KILL INCIDENT + t439 RECOVERY (tPL-V1f, 2026-11-24)
HAZARD SELF-INFLICTED, BANKED SO NO REPEAT: cleanup commands
`pkill -x Xvfb -u $USER --older 3600` (and a second at --older 1200) intended
for my own stale witness Xvfbs ALSO killed the PRODUCTION Xvfb :9 -> dosbox-x
pid 1470999 lost its display at 00:01:33 (dosbox.log ends `X connection to :9
broken` — the t277 golden farewell, NOT a crash). NEVER bulk-pkill Xvfb by
user/age on this host: the production ring's Xvfb (:9) and the VNC Xvfb (:97)
are indistinguishable that way. Kill BY PID only (pgrep -a Xvfb first;
production pids are the ones matching the vnc/session.conf lineage).
RECOVERY (t439 pattern, verbatim): pre-gate `ss -tn | grep 5910` empty (no
human VNC client) -> `bash scripts/r1_playcap_vnc.sh start` -> NEW dosbox-x
pid 1623906, ring rotating again by 00:30:38 (44..47.sav at the 10 s cadence,
live-timeline growing). Ring bank bank-t438-ring-2200 untouched. No OQ row
touched by the incident or the recovery (measures nothing).

