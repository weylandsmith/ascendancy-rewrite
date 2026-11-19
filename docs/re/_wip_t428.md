# _wip_t428.md — PLANET SCREEN CYCLE, cycle 1 (measure + derive)

Task: docs/STATE.md NEXT ACTION t428. Frame is ALREADY EXACT (t406: 17np k0
backdrop) — do not touch. Seed defects: top-row TYPE-29 panel art, planet
BACKGROUND record, planet art too small / z-order under the cell squares,
diamond FILL/OUTLINE law, tile-click content-dependent popup, orbital
structures column on the LEFT.

Authority for all vendor pixel numbers this cycle:
docs/assets/refcap/original-planet-view.png — 640x480 P-mode, 165 colours,
palette-pure (t426 law: png y = screen y + 40; the shot CLIPS screen 440..479).
Header text "Minions (1 Planet Occupied, 1 System Controlled)" +
"Xerxes I (Enormous Supermineral Planet)" / "No Project" — state 17
PLANETALLOC, the same screen the t418b witness opens.

## F1 — VENDOR PLANET-SCREEN LAYOUT MEASURED ON THE PURE REFCAP (t428)
Luminance-threshold bboxes + column/row runs (probe: numpy over the P image;
threshold lum>12 unless stated). png coords, screen = png y - 40.

* CHROME: rows 40..59 fully nonblack (640 px) = top band + header line 1;
  rows 473..479 only 16 nonblack = the two side borders (x0..6, x633..639).
  Interior black. Consistent with the t426 border law.
* HEADER LINE 1 (green title text) png rows 50..61 (peak counts 56..61),
  centred-ish; flag icon box png x0..29 y40..59 (n=569).
* HEADER LINE 2 band png 80..109 (screen 40..69): flag icon box png x0..29
  y80..109 (n=589, i.e. 30x30), green text rows 102..109, WHITE text rows
  102..139 -> the two info lines "Xerxes I (Enormous Supermineral Planet)"
  (row ~105) and "No Project" (row ~119) sit BELOW the header-2 band, in the
  field, starting at png x ~283.
* STAR DISC: png x0..151 y80..244 (w152 h165, n=14972, lum>20), centroid
  (73.6, 155.6) png = screen (74, 116). It is CLIPPED by the left screen edge
  (bbox starts at x=0) -> the star art extends off-screen left.
* PLANET DISC: png x150..284 y102..208 (w135 h107, n=7071, lum>20), centroid
  (207.7, 161.2) png = screen (208, 121). Per-row widths (png y: w):
  111:135 119:97 127:65 135:79 143:87 151:92 159:95 167:94 175:91 183:85
  191:74 199:58 207:26. The left edge runs 188->161->161->179->195 and the
  right edge 284->240->255->236->220: the two 135-wide extremes (y111 and the
  y119 partial) are NOT the disc — they are the adjacent art touching the
  window. The disc's own round envelope is x161..255 (w~95) y127..207,
  i.e. DIAMETER ~93 px, centre png (208,167) = screen (208,127).
  [inferred] the 2 extra extremes = a highlight/terminator artifact.
* THREE SURFACE THUMBNAILS: column runs x288..341, x358..411, x428..481
  => PITCH EXACTLY 70, WIDTH 54. Art rows png 147..196 => HEIGHT 50.
  So three 54x50 tiles at png (288,147) (358,147) (428,147),
  screen y 107. n px 2886 / 2194 / 2738 (all three painted, different art).
* POP PIP GRID: bbox png x490..545 y147..159 (the 105..110 run in that box
  is the white info text, excluded). COLUMN runs at 490, 492-494, 496-500,
  503-505, 508-510, 513-515, 518-520, 523-525, 528-530, 533-535, 538-540,
  543-545 -> 12 columns, pitch 5 (dot 3 px wide). ROW runs 147-149, 152-154,
  157-159 -> 3 rows, pitch 5. Grid origin png (490,147) = screen (490,107)
  — SAME y as the thumbnails, so the top row is one aligned strip.
  Index census inside the grid: idx62 (16,69,77) dark teal n=84,
  idx123 (16,134,73) green n=84, idx58 white n=17,
  then the amber/orange family idx122 (255,207,24) n=6, idx127 (255,166,0)
  n=6, idx130 (255,134,8) n=6, idx121 (186,36,56) n=3, idx116 n=3.
  -> the pip grid is 12x3 with a dark EMPTY colour and per-slot content
  colours (green/amber/red family): a per-cell STATE grid, not one bar.
* FIELD BELOW png y200..439, x7..465 at lum>2: n=2443 with bbox x0..228 —
  i.e. EVERYTHING beyond x228 below png y200 is BLACK. The star-disc glow
  (to x151/y244) plus a few disc-edge px account for it. => ON THIS PLANET
  THE VENDOR PAINTS NO ISOMETRIC DIAMOND GRID. PLSQUARE's declared rect is
  152,120-487,375 (windows.txt:1520 children) = png y160..415; the region
  x229..487 y200..415 is EMPTY (0 px at lum>2).
  SEAM QUESTION (F-next): is the grid conditional (structures present / pop
  to allocate / a mouse-over or key state), or is this capture's planet
  simply unimproved? "No Project" + 1 pop suggests unimproved.

## F2 — THE STRIP IS THE FIVE TYPE-29 PANELS: RECT->CONTENT MAPPING (t428)
windows.txt rects (screen coords; +40 = png y): PLRES 7,7-114,106 param0;
PLIND 123,7-230,106 param1; PLPRO 239,7-346,106 param2; PLPOP 355,7-454,106
param4; PLBUILD 463,8-632,106 msg51. All SHAPEFRAME -1 (no shape binding —
paint is 100% code-side in fn 0x3b96c, planets-ui S1). Mapping the measured
refcap content onto these rects:
- PLRES rect   = the STAR DISC (png centre (74,116) screen (74,76); disc
  bleeds past the rect's left edge — the paint x is rect-relative and the
  disc centre sits LEFT of the panel x0=7, i.e. off-screen clip).
- PLIND rect   = the PLANET DISC (round envelope w~95, centre screen
  (208,127); rect centre x = 176).
- PLPRO+PLPOP  = the THREE 54x50 SURFACE THUMBNAILS at screen x288/358/428
  y107, pitch 70 — one per panel-ish slot (288 in PLPRO, 358 at the PLPOP
  left edge, 428 inside PLPOP).
- PLBUILD rect = the 12x3 PIP GRID at screen (490,107) pitch 5 + the
  project text lines ("Xerxes I (Enormous Supermineral Planet)" /
  "No Project") at screen x~243.. y~65/79 — NOTE the text starts at x243
  (PLPRO rect), NOT inside PLBUILD.
- The green "Xerxes" label at screen y~62 x120-ish belongs to the header-2
  band, separate.
=> the t428 seed-defect "top-row art missing" resolves to: paint fn 0x3b96c
cases 0..4 draw EXACTLY these five regions; our port draws none of the
disc/thumb/pip art. The "orbital structures column on the LEFT" = the
PLRES star-disc region (user saw the vendor column, ours is empty).

## F3 — THE VENDOR PAINTS NO ISOMETRIC GRID ON THIS PLANET (t428)
Measured (F1): PLSQUARE's whole declared rect 152,120-487,375 is BLACK
below png y200 beyond x228 (0 px lum>2 in x229..487/y200..415). So the
t418b diamond-grid paint is CONDITIONAL in the vendor, and this screen —
"No Project", 1 pop — shows no grid at all. The port painting a full
diamond lattice for every planet is a z/content DEFECT, not just a look
defect. Gate location hunt: paint body 0x3b96c; the grid loop t418 cited
0x3bb2c..0x3c26d. [inferred] candidate gate = per-cell ACTIVE state
(word+2 bit0, t418 adjacency law) — a brand-new planet may have zero
active cells; needs the asm read of the loop head.

## F4 — PAINT BODY 0x3b96c HEAD DECODED: THE PLSQUARE PAINT SEQUENCE (t428)
(work/t/t198_planwin.asm 0x3b977..0x3ba5e; blit arg law S12.1:
FUN_0x5caac(desc, payload, selector, x, y); payload = FUN_0x1fc34(cache
0x9f10c, slot))
- 0x3b979 PL := [0x43508]; size := WORD[PL+0x14] (saved esp+0x340).
- 0x3b98b slot idx := WORD[0x6fd9c] (the SHAPEFILE cache-slot global —
  the SAME global the gauge cases read at 0x3cc15 per planets-ui S3).
- 0x3b992 selector base := WORD[PL+0x16] (the TYPE word the row-string
  also reads, t427) indexed via [EBP+0x175+2*idx] -> esp+0x368 (a per-
  widget-record selector table).
- GATE 0x3b9b1: `MOV EAX,[EBP+0x1c]; SAR 16; CMP -1; JE 0x3ba5e` — the
  widget paints ONLY IF its SENDMESSAGE field != 0xffff. PLSQUARE carries
  SENDMESSAGE 1 (windows.txt ln:1529) -> passes. [verified structural]
- BLIT 1 @0x3b9df: selector = [EBP+0x1c]>>16 = SENDMESSAGE = 1 for
  PLSQUARE, at x=7, y=115 (push $0x73,$0x7; S12.1 order x-then-y pushes
  $y,$x? NO — see F4a note), lib = slot [0x6fd9c] = the widget's
  SHAPEFRAME lib. PLSQUARE's SHAPEFRAME is 0 — [unverified] which lib
  resolves; the t406 finding "the planet screen's frame IS the 17np k0
  backdrop" (ui.cpp:1458) says 17np; k1 is the prime candidate for this
  blit (k4/k5 were t418's backdrop candidates).
- COND 0x3b9e4: `BYTE[EBP+0x18b] & 4` -> BLIT 2 @0x3ba1e at x=0x198=408,
  y=0x128=296, selector [esp+0x374] (a value stored earlier in the frame;
  NOT yet traced — F4b).
- BLIT 3 @0x3ba4a: selector = [EBP+0x1c]>>16 again, at x=0, y=0.
- TAIL 0x3ba52: call 0x55240(0x7a35c, desc) (the banked S12 tail fn?
  identity UNRESOLVED).
- F4a NOTE (push order): pushes are ($0x73 then $0x7) and the S12.1 law
  says arg4=x,arg5=y with pushes in reverse — so x=7,y=115 for blit1
  (x near-LEFT, y mid-screen) — consistent with a full-window frame whose
  left edge sits at screen x7. For blit2 x=408? or 296? — same order:
  pushes $0x128,$0x198 => x=0x128=296, y=0x198=408 (off the clipped refcap
  bottom; screen y 408 is below the visible band? NO — 408 is ON screen;
  the refcap shows BLACK at 296..? -> census F1 field says x7..465 y200..439
  is black EXCEPT star glow -> blit2's condition bit was CLEAR on this
  planet, or its art is transparent/black there).
- 0x3ba7f..0x3bace (pre-grid): sel := 0xffff; if BYTE[EBP+0xab] != 0xff and
  WORD[EBP+0xac] < 0xffff and BYTE[[PL+0x10]+4*bx+1] == 0xff and
  FUN_0x3830c(byte[EBP+0xab], edx=0) != 0 then sel := WORD[EBP+0xac].
  (0x3830c = the t418 cell-legality checker.)
- GRID GATE 0x3bad8..0x3bb13: dl := BYTE[PL+0x57]; dh := BYTE[0x7458e]
  (= PLAYER INDEX per aicode.md §7.3 [verified]); if dl != dh then
  eax := FUN_0x3958c(edx=11) [the t418 grid helper called with size 11 —
  an out-of-domain size]; if eax != 0xffff -> JUMP 0x3c33a (SKIPS THE
  ENTIRE GRID LOOP 0x3bb2c..0x3c26d). If dl == dh -> grid paints.
  => CANDIDATE LAW: the diamond grid paints ONLY when [PL+0x57] == player
  index. [PL+0x57] semantics UNRESOLVED at the time of first reading —
  SUPERSEDED by F6 (owner byte = [PL+0x57] per income-law.md:358, and the
  jump target 0x3c33a is NOT the grid-skip).

## F5 — LIBRARY RESOLUTION FOR THE STATE-17 PAINT (t428)
shp.md S23.1 [verified live-RAM]: u16[0x6fd90..0x6fd9c] = 38,39,40,41,42,
43,44 = cache slots whose gwshare.txt (0-based) names are
38 planres.shp / 39 planind.shp / 40 planpro.shp / 41 14intel.shp /
42 smraces.shp / 43 9endgame.shp / 44 17np.shp. So:
- the gauge cases (S3) blit planres/planind/planpro via [0x6fd90/2/4];
- the PLPOP pop grid (S4) blits 17np k1/k2/k3 via [0x6fd9c];
- the paint-body 0x3b96c head trio reads slot [0x6fd9c] (=17np) at
  0x3b98b -> the PLSQUARE-region backdrop/frame candidates are 17np
  records (k0 639x479 frame, k4 625x357, k5 416x316 — S23.2).
- gwshare slot == line-1 law [verified S23.1].
planal00..10.shp: 5 records each, dims ladder 47/75/103/140/189 (S23.3).
The refcap planet-disc envelope (~93 px, F1) sits closest to the size-2
rung 103 at 1:1 — CONSISTENT with the port's current planal
record(sizeIdx) [inferred] pick; no 2x factor on the disc.

## F6 — GRID-GATE HUNT: BOTH CANDIDATES RESOLVED AS NON-GATES (t428)
The two owner-vs-player tests in the listing are NOT the grid switch:
- 0x3baf4..0x3bb13 (head): if owner([PL+0x57]) != player([0x7458e]) AND
  FUN_0003958c(PL, edx=11) != 0xffff -> jmp 0x3c33a. 0x3958c [verified
  disasm r331 0x395c4 region, read this iteration] = search array
  [rec+0x10] (stride 4) length WORD[rec+0x1a] for BYTE+1 == cl; returns
  idx or 0xffff. It searches the CELL array for byte+1 == 11.
- 0x3c352..0x3c381 (tail loop): same shape with edx=0x19 (=25).
Both legs SKIP FORWARD (to the tail / out), and the tail loop 0x3c4d9
walks cells with owner-dependent art. The GRID LOOP 0x3bb2c..0x3c26d is
reached for every planet that gets this paint at all — the F3 black field
therefore means the paint body (or the PLSQUARE widget) WAS NOT INVOKED
IN THIS SCREEN STATE, not that a per-planet gate hid the grid.
HYPOTHESis H-GRID-INVOCATION [unverified]: 0x3b96c is the PLSQUARE
widget paint; windows.txt binds PLSQUARE STATE "1 17" and the refcap
header "Minions (1 Planet Occupied, 1 System Controlled)" identifies a
PLANETALLOC render... closer = which widget the paint fn is attached to
(TYPE-29 generic vs PLSQUARE-14 specific) + whether a key/mouse mode
toggles it. NOT closed this iteration; the F3 measurement stands.
The port's always-on diamond lattice therefore stays (removing it on one
capture = a guess); NAMED SEAM T428-A.

## F7 — TWO VENDOR WITNESSES, ONE SCREEN: THE LAYOUT LAW (t428)
Witness A = docs/assets/refcap/original-planet-view.png (turn-1 empire,
"Xerxes I (Enormous Supermineral Planet)", "No Project"; palette-pure).
Witness B = work/r1/screens/t254/02_planet_detail.png (developed planet,
t254 [verified] — pop grid 37 busy/2 free, structures on the grid).
COMPOSITION (both): TOP STRIP (screen y0..~115) = star disc (left, bleeds
off x0), planet disc, three 54x50 SURFACE THUMBNAILS pitch 70, POP PIP
GRID pitch 5 (cap-sized, 10/row), project panel (thumbnail + project name
text "Scientist Takeover" in B; "No Project" in A). FIELD = the planet
sphere with the isometric diamond grid + structure art ON it (B), or
BLACK (A).
=> the t428 seed defects resolve as: (1) "top-row art missing" = the port
paints none of the strip content; (2) "planet art too small + covered by
squares" = the port centers the planal disc UNDER the lattice; the vendor
shows the planet DISC (planets.shp class art) in the STRIP and the big
sphere+grid only in the field; (3) "orbital column on the LEFT" = the
star disc at the strip's left end.
DISC ART PROVENANCE [inferred, strong]: strip star disc = suns.shp (same
raw star-type selector as the t427 row suns — same art family visually);
strip planet disc = planets.shp selector 5*type+size (same law as row);
thumbnails = planalNN surface crops (B: the factory thumbnail in the strip
is the SAME art as the factory structure tiles on the grid — planal/
planitem family). Disc size in A ~93 px vs planal ladder rung 103 vs
planets.shp record dims — the strip discs render ~ their record size;
NO 2x factor here (unlike the t427 row suns).
FIELD-GRID CONDITIONALITY: A (unimproved, No Project) = field BLACK;
B (developed) = sphere + full lattice. The static hunt (F6) found NO
owner/pop gate on the grid loop inside paint fn 0x3b96c. H-FIELD-STATE
[unverified]: the field sphere+grid paints only when the planet has
allocated cells/structures. CLOSER (cheap, next): our own save corpus —
grep work/r1 saves for a state-17-era frame at turn 1 vs developed. NOT
changed in the port this iteration (removing the field lattice on one
capture = a guess). SEAM T428-A stands.

## F8 — WITNESS A IS NOT STATE-17 GEOMETRY: CAPTURE-LINEAGE SEAM T428-B
A's header format "Minions (1 Planet Occupied, 1 System Controlled)" is
the STATUS-LIST header shape (t402 S1: t3 capture header "Chamachies
(80 Planets Occupied, 26 Systems Controlled)"), and A's row content
(star disc + planet disc + THREE thumbnails at x288/358/428 pitch 70 +
pip grid at x490) is the STATUS ROW content of t427 — while B
(t254/02_planet_detail.png) has NO header rows and its strip sits flush
at screen y0 with the POP GRID INSIDE PLPOP x355..459 (pitch-10 k1/k2/k3
humanoids, S4 law) and a PROJECT PANEL (thumbnail + "Scientist Takeover")
in PLBUILD. A's dot grid (12 col x 2 row, pitch 5, 2x2 dots = 17np
k6/k7/k8 legend colours, census row1 = 1 red + 3 amber + 8 green, row2 =
12 green) is NOT the S4 code path (S4 = 10/row, pitch 0x0a; A = 12/row,
pitch 5).
Anchor disagreement vs the t3-derived t417/t427 laws (A png coords,
assuming png==screen): flag box y80..109 vs t417 row-top 57; sun centre
(74,156) vs t427 law (80, row+64); planet centre (208,161) vs law (215,
row+53) — the sun/planet VERTICAL ORDER IS REVERSED (A: planet BELOW sun;
t3 law: planet ABOVE sun by 11). Thumbnails x288/358/428 MATCH t427's
T427-E band x288..445 exactly.
CONCLUSION [inferred]: A and the t3 capture are DIFFERENT layouts or
different capture offsets; A cannot be merged into the t3-pinned law set
without a lineage ruling (which screen/version/crop A is). NAMED SEAM
T428-B (ruling-page material): "original-planet-view.png layout
disagrees with t3-derived status-row anchors; treat A as the authority
for the 1-planet-empire composition ONLY, not for anchor geometry."
AUTHORITY SPLIT GOING FORWARD: B = state-17 strip+field layout (it IS
the t254 live capture of the vendor detail screen); A = the only
palette-pure source for row THUMBNAIL art (T427-E closer candidate) and
the legend-dot pip variant.

## F9 — WITNESS B STRIP = THE FIVE TYPE-29 PANELS, MEASURED 1:1 (t428)
B = work/r1/screens/t254/02_planet_detail.png, 800x600, screen origin
(80,100) at 1:1 scale [verified: content bbox 80..719 x 100..579 = 640x480].
Measured panel content (screen coords) vs windows.txt rects:
- PLRES rect 7,7-114,106: content x0..124 y0..114 (incl. teal border) =
  STARBURST PHOTO on navy = planres.shp record. LIB DECODED THIS
  ITERATION (tools/shp_pngdump, /tmp/t428_g): planres/planind/planpro
  each EXACTLY 21 records, ALL 107x99 — fits the 108x100 rects; 21 ==
  the clamp0..20 gauge domain of the S3 law. The rec0 navy mottle = the
  0-level panel; selector = the compressed level. [verified byte-level]
- PLIND rect 123,7-230,106: content x128..279 = CITY PHOTO (developed
  planet) = planind record at the IND level.
- PLPRO rect 239,7-346,106: ALIEN-PLANT PHOTO = planpro record.
- PLPOP rect 355,7-454,106: pop grid x355..459 y5..109, 10/row pitch 10,
  red busy k1 + yellow free k2 sprites (t254 S4 census [verified]).
- PLBUILD rect 463,8-632,106: content x463..632 y7..105 = project name
  WHITE TEXT top-centre ("Scientist Takeover") + photo THUMBNAIL below =
  planitem.shp record[item] (same k[item] law as the grid structures,
  t418 F5). A ("No Project"): text-only variant.
=> STRIP LAW FOR THE PORT: blit planres/planind/planpro records at the
three gauge rect origins with the EXISTING selector laws (gaugeSelector/
prosSelector, t276); pop grid via popPanelCells at origin (355,7) with
17np k1/k2/k3 (poppanel t263 law, already pure+pinned); PLBUILD = name
text + planitem k[pendingItem] thumbnail, or "No Project" (static.txt
#141). The port currently paints only grey outlines there — that IS seed
defect "top-row art missing". The "orbital column LEFT" = the PLRES
starburst photo (user saw art where we draw a rectangle).
FIELD (below strip): B shows the large sphere + diamond lattice; A shows
BLACK (T428-A seam stands). 17np k4 625x357 = field-backdrop candidate
via the 0x3b98b site (t418 note); field sphere provenance stays OPEN —
the field painter is NOT touched this iteration.
A's strip (star-disc-at-left layout) is the STATUS-ROW composition per F8
— NOT the state-17 panels; the t427 row laws keep their t3 authority.

## F10 — LANDING (t428)
PORT: NEW pure module ui/planetstrip.{h,cpp} (StripPlan: gauge
lib/rec/rect x3 + popPanelCells at origin (355,7) + projectItem);
stripGaugeLibraryConforms census gate (21 x 107x99; 17np refused);
ui.cpp kScreenPlanet: the grey-outline loop DELETED, replaced by the
strip painter (planres/planind/planpro blit at rect origins, 17np
k1/k2/k3 pop grid, PLBUILD centred name + planitem k[item] thumbnail /
"No Project"; the t406 "Project: X - N days" line DELETED per witness B
name-only). Libs loaded via kStripGaugeLibs (3 new ShapeLibrary slots,
kLibs stays 8). PINS test_planetstrip_t428 x4 (rects verbatim + selector
law, library census + 17np control, pop anchor/pitch, star domain +
pendingItem mirror). SUITE 447/0/0.
WITNESS scripts/t428_strip_witness.sh + t428_witness_census.py VERDICT
PASS on our Xvfb render (seed 5 --species 0): PLRES 8-colour mottle rec0
(low gauge — threshold per record), PLIND/PLPRO photo art (>40 cols),
PLPOP sprites painted, PLBUILD white "No Project" n=111. Vision grade:
the strip matches witness B's composition (photo panels, pop sprites,
centred project text); OUR DEFECTS REMAINING: the seed-5 home planet's
IND/PROS gauge photos show terrain crops WITH a tiny structure sprite +
a pole artifact at the panel bottom edge (the planind/planpro low-level
records themselves — vendor art, painted per law; NOT a port defect
[unverified], and the field below the strip unchanged (T428-A)).
SEAMS CARRIED: T428-A (vendor field BLACK on witness A vs our lattice —
H-FIELD-STATE open), T428-B (witness A lineage vs t3 anchors — ruling
page), field sphere provenance (17np k4 candidate), tile-click popup law
and diamond FILL/OUTLINE records NOT touched this iteration.




