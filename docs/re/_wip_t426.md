# t426 WIP — GALAXY MAP VISUALS CYCLE

Assignment (STATE.md 2026-11-18): map BORDER missing; PLAYER ICON UPPER LEFT
(user verbatim 2026-11-17); HOME STAR = player icon + TWO rings at game start
(derive which condition paints each, do NOT copy the guess); chrome texture per
t422. Authority: docs/assets/refcap/original-strategic-map.png, png = screen+40,
palette-PURE (R-t425c: do NOT read race-strip/slot pixels from it — clipped).
scratchpad/galaxymap-original.png = 642x481 identity, NOT palette-pure.

## F0 — orientation
- Port draw site: rewrite/src/ui/ui.cpp ~1000-1120 (mapVisible block): bevel =
  two SDL rects (kBevelMid outset at kCosmosWnd-1, kBevelIn at the window rect),
  home marker = WHITE SQUARE ring at r+3 (named seam, ui.cpp:1103-1113).
- No sitting since last iteration (timeline tail 12 recs, turn 1254 == floor).

## F1 — BORDER measurement [VERIFIED, scripts/t426_border_measure.py]
Cosmic-frame law in the PURE refcap (note: my conv map used *255//63 floor;
vendor renders at round(v*255/63) — OFF(77,113,117)==idx19 raw(19,28,29),
OFF(89,134,138)==idx24 etc; treat OFF labels as +1-scale palette px):
- TOP BAND screen rows 0..6 = CHROME TEXTURE full width (x60..420 scan):
  y0-1 bright teal ramp (idx 6/19/24/56/176 + grey 81,81,81=idx~?), y2 mid
  (grey 52/53 + 157/201 accents), y3..y6 DARKENING to near-black teal
  (48/49/2/1/200, (40,65,69)); screen row 7+ = PURE BLACK (BACKGRNDCOLOR 0).
- LEFT BAND screen cols 0..6 = chrome, same gradient law (col0-1 bright teal
  29/27/22%, col6 dark 49:32% 3:27% (40,65,69):20%); col 7.. = 100% black
  rows 60..460. [t411's "x7 (49,54,53)" scan was the SCRATCHPAD — the pure
  refcap says col7 is black; the two-line flat bevel is NOT vendor.]
- RIGHT transition: cols 460..465 black, col 466+ chrome at y100/200/300/400
  (sidebar). COSMOSWnd x1=465 exact.
- BOTTOM: screen rows 473.. = chrome (scratchpad rows 473..477 non-pure but
  same ramp families; refcap CLIPS screen 440..479 — bottom law must come
  from the scratchpad + top/bottom symmetry).
- PORT DEFECT: ui.cpp:1020-1031 draws two FLAT rect lines (kBevelMid/kBevelIn)
  at the window edge; vendor has NO line — chrome texture runs INTO the window
  edge, field interior is pure black to 7,7..465,472.
- Upper-left png block y50..62 x10..24 shows a BRIGHT rounded object INSIDE
  the black field at screen ~(10..40, 10..40) with green (0,170,81)/(0,142,69)
  + idx242 + idx16 px — THE PLAYER ICON lead (F2).

## F2 — PLAYER ICON upper-left [CLOSED ON EVIDENCE 2026-11-19]
THE PLAQUE IS raceflag.shp RECORD k0 — 100.0% EXACT-EQUAL on opaque px
(vendor round(v*255/63) palette scale, tol<=3/px) at png (10,52) == SCREEN
(10,12), 14x24. scripts/t426_plaque_match.py over EVERY record of EVERY
extracted/ascend01/data/*.shp (dims 10..40 x 15..40, offsets -6..+6);
runner-up 52.3% (8shipdes k0) — no ambiguity. (probe 2's bbox was chrome
contaminated: it cropped from screen (2,2) and swallowed the top/left bands;
its ASCII "object" rows 50..74 were png rows == screen 10..34, and the
"green rounded thing" is this plaque, nothing else is non-black inside the
field above screen row 40 except the race-strip band at png rows 80..86.)
PLAQUE COMPOSITION [verified, grid in probe output]: border ring idx19
(0,170,81), interior idx242 navy (12,32,48), glyph strokes idx16/17/18
(0,85,40)/(0,113,56)/(0,142,69) — i.e. the species flag face for the
PLAYER's species at game start. k0 = first record; census which species
k-index maps to (raceflag lib order) before wiring a per-species index.

## F2b — PLAQUE FRAME LAW [VERIFIED, exact — SUPERSEDES the +2-offset draft]
raceflag k0 header law: k0 stream sits at rec+8 (NOT rec+0x18; that is the
k>=1 offset — t425b law, and my probe's k0 decode was wrong until corrected
by the C++ decoder's disagreement). Correct k0 decode: EVERY row opaque;
row 0 = 14x idx19 (green top line), col 0 = idx19 every row, navy + glyph
interior — the record IS a 14x24 half-frame. LAW (identical at both
anchors, probe /tmp/ph.py): vendor draws 15x25 idx19 outline + navy
interior at anchor A, blits raceflag k<specnum> AT THE SAME A:
  k0@A  = 336/336 opaque px EXACT (tol<=3), residual 39 = frame right
          column (25) + bottom row (14), both idx19.
  k0@A+2 = 322/322 "exact" was the same pixels shifted (47.8% at A) — the
          +2 draft is VOID; anchors are A=(10,10) plaque, (285,77) crest.
Plaque A = screen (10,10) — the frame's bottom/right lines complete the
record's half-frame. [correction trail: pd.py row-scan + ph.py soff test.]

## F3 — HOME STAR marker [MEASURED 2026-11-19]
Pure refcap home star: core-dot centroid (idx97/39/99/100, n=20) png
(114,292) == SCREEN (74,292).
- WHITE RING: idx15 n=22, abs extent png y108..116, x286..298 — flat top
  (y108 x290..294), sides to x286/x298 at y112..116; bottom hidden under
  the crest frame (png 117+). NOT a shape record (census over all 8..20px
  records: best 37.1% mouse.shp junk) -> code-drawn ellipse centre
  (starx, stary-2) rx 6 ry 4.
- CREST: frame+raceflag k0 at png (285,117) == SCREEN (285,77) ==
  (starx-7, stary+3) — 336/336 EXACT at the SAME anchor (F2b law).
- idx111 (150,215,255) diagonal up-right + idx115 (142,0,0) rows 113-114
  LEFT are TRANSIT/LANE TRACES through the home star, not marker rings.
VERDICT on "player icon + TWO rings" (user verbatim): MEASURED = ONE white
ellipse ring + the raceflag crest; the apparent second ring is the lane-
trace diamond around the star in the same shot [inferred]. No vendor ring at
any other constant radius exists in the palette-pure shot (census by radius
from the dot: only crest colours idx16/17/18/19/242 at r 5..27 and traces).

## F4 — PORT + PINS + WITNESS [SHIPPED 2026-11-19]
PORT (ui.cpp mapVisible block):
(i) BEVEL REMOVED (F1 law): the two kBevelMid/kBevelIn rect lines are gone;
    the field is a pure-black FILL at 7,7..465,472 and the clip rect is the
    field itself. kBevelMid/kBevelIn constants stay in mapchrome.h (the
    t411 pin test still reads them) but are no longer painted.
(ii) FRAME TEXTURE extended to FOUR bands (mapchrome.h): top rows 0..6 x
    7..465 and bottom rows 473..479 x 7..465 join the left/right bands;
    frameTex build loop is generic over kTextureBandCount. The in-band
    luminance GRADIENT toward the field edge (F1: y0-1 bright -> y3..6
    near-black) is NOT modelled (textureColourAt is a flat census mix) —
    NAMED SEAM.
(iii) PLAQUE: 15x25 navy fill + idx19 (chromePaletteArgb(19)) outline rect
    at (10,10) + raceflag k<playerSpecies> blit at the SAME anchor, inside
    the field clip. human (-1) = honest-empty frame (rail precedent).
(iv) HOME MARKER: white-square seam replaced by (a) white ellipse ring
    centre (q.x, q.y-2) rx 6 ry 4 (64-point parametric; idx15 law) and
    (b) the same plaque frame+flag composite at (q.x-7, q.y+3).
PINS rewrite/tests/test_plaque_t426.cpp x3: palette colours named (idx19
(0,170,81), idx242 (12,32,48)); raceflag k0 decode law (14x24, row 0 = 14x
idx19, col 0 idx19 every row, all px nonzero rows 0..23, count 21) — this
pin is what CAUGHT my probe's wrong k0 stream offset; composite geometry
(anchors, residual 39 = 25+14). SUITE 434/0/0 (+3; test_rail_t400 band
count updated 2->4 with the law comment).
WITNESS scripts/t426_plaque_witness.sh (--species 0 = the refcap's own k0):
top band y3 360/360 nonblack, bottom band y473 360/360, plaque outline 76
green px, crest frame 76 green px at the LOGGED home-star anchor
(254,438)->(247,441), and THE BAR: plaque 15x25 block exact-diff vs the
palette-pure refcap = 375/375, ZERO residual. VERDICT PASS.
MUTATION x2: plaque anchor 10->11 FAILS (166/375); bottom band y0 473->474
FAILS (band black at y473 — first sample row was y476, which survived the
mutant; tightened to the measured edge row).

## F5 — ledger + residuals
- OQ rows: galaxy-map visuals have NO OQ owner (t414..t425c precedent);
  closes NOTHING — honest negative. OQ-027 stays open pending the final
  hearing verdict; OQ-016/OQ-019 DEFERRED per assignment.
- NAMED SEAMS left open: (a) top/bottom band in-band gradient; (b) the
  ring's exact ellipse params under projection (vendor code-drawn ring law
  not decompiled — Ghidra instance not running this iteration; the
  64-point ellipse reproduces the measured idx15 extent png y108..116
  x286..298 at the rest pose); (c) raceflag k-index <-> species mapping for
  species != 0 (t401 uses k<specnum> verbatim at (9,10) in the newgame
  DESC panel — same convention adopted here, unverified for this site).
