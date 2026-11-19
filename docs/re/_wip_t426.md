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

## F2 — PLAYER ICON upper-left (vendor pixels + 10status.shp census)
(pending)

## F3 — HOME STAR two rings (Ghidra paint-code derivation)
(pending)

## F4 — port + pins + witness
(pending)
