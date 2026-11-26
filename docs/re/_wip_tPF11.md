# tPF-11 WIP — RESEARCH-SCREEN MINERAL FRAMING (D28 item 22) + TPF5-A

Task: STATE.md NEXT ACTION 2026-11-26b. D28 item 22 verbatim
(scratchpad/t433-build-feedback.txt:22): "The mineral framing is missing
from this screen." (research screen).

## P1 — GATE AUDIT (step 1): STATE note "help.shp-k0 FRAME SHIP stays gated
## on the user's OQ-005 ruling (D1)" is STALE. [verified]

- docs/OPEN-QUESTIONS.md:25-27 — OQ-005 row: "CLOSED 2026-11-09 t367 — D1
  USER RULING, the row's own named closer". Ruling text recorded verbatim
  (DECISIONS.md:192-196): "D1 mouse k5/k6/k7 = keep as-is / D1 batch 41
  dispositions = accept all 41 / ...".
- The ruling COVERS shipping decoded .shp frame art: batch dispositions
  "accept all 41" + t367 already shipped the corner-anchor fallback in
  rewrite/src/formats/shp.cpp (decode(), TEST shp_corner_anchor_fallback_t367).
- No residual gate on frame ART exists in the row; residues listed are
  decoder-side (zero-byte ladder slots, cos_star k40..k51, invalid-dims,
  vendor EOF truncation) — none touches help.shp k0 (a decode-PASS record,
  336x256 measured tPF-5).
=> CONCLUSION: no gate stands. TPF11 proceeds with the help.shp-k0 frame
   ship on the research screen. Honest scope note: the ruling covers the
   corpus batch + mouse rows; help.shp was inside the accepted decode
   corpus (208 libs/1557 recs census), not individually named. Proceed.

## P2 — FRAME LAW FOUND (windows.txt TYPE-100 header, no Ghidra needed)

- extracted/ascend00/windows.txt:1756-1758 — TYPE 100 / STATENUMBER 20 /
  SHAPEFILE "DATA\20RES.SHP". The full TYPE-100 census (grep '^TYPE 100'
  -A3): STATENUMBERs 0,1,3,3? no: {0:0OPENING, 1:1STARMAP, 3:3CFGNEW,
  7:7RACESEL, 8:8SHIPDES, 13:13NEGOT, 16:16BATTLE, 20:20RES} — a
  STATE-number -> screen-frame-LIB table. This is the generic
  STATE-composition law t333/(2)(4) called "composition-invisible": the
  winmgr composes the widget record from the TYPE-100 header when the
  window's STATE matches STATENUMBER.
- RESWIN (windows.txt:1761-1775): TYPE 9, PARENT NONE, STATE "1 20",
  rect 7,46-476,472, SHAPEFRAME 0. STATE 20 hits the header row ->
  lib = 20res.shp; SHAPEFRAME 0 -> frame record 0.
- Blit law (tPF-2c C2, [verified asm]): FUN_00030fb8 @0x31004 reads
  HIWORD dword[rec+0x1c] (frame id; -1 = none), pushes u16[rec+0x18]
  (cache slot = lib) + 0x9f10c, FUN_0001fc34, blits via FUN_0005caac at
  widget+4 (window origin). => VENDOR RESEARCH SCREEN FRAME =
  20res.shp record 0 blitted at the RESWIN window origin (7,46).
- The tPF-5 P7 gate note ("help.shp-k0 gated on OQ-005/D1") is STALE per
  P1, AND help.shp k0 is the POPUP answer (336x256 == popup rect, cut-out
  == button band) — NOT the reswin answer, exactly as STATE warned.
- File exists: extracted/ascend01/data/20res.shp (2294 B) (+ 20res.tmp).
- NEXT: decode 20res.shp k0 dims — parity law: dims should match the
  RESWIN rect 470x427 (476-7+1 x 472-46+1) or be a frame band set.
  2294 bytes is SMALL for 470x427 — expect a sparse frame-border record
  (runs of transparent interior), like help k0's cut-out pattern.

## P2c — REFRAME: 20res.shp is NOT the mineral frame (measured)

- Decoded 20res.shp (scripts/tPF11_res_frame.py): 6 records, k0 16x31 +
  k1..k5 ~15x31 — the FOUR PAN-BUTTON arrow faces + 2 spares. Consistent
  with the t391 note in researchview.h ("20res.shp holds the four arrow
  faces ONLY"). SHAPEFRAME 0 on RESWIN composes NOTHING window-sized; the
  TYPE-100 STATENUMBER-20 binding supplies the BUTTON lib, not a frame.
- => "The mineral framing is missing from this screen" = the FULL-SCREEN
  CHROME family, not a window shape.

## P3 — CHROME LAW MEASURED on the vendor research capture
(work/screens/t252/research_open_game.png, scripts/tPF11_chrome_measure.py):

A. PERIMETER TEXTURE BANDS ~7px, texfrac 1.000 all four edges
   (x0..6, x633..639 full height; y0..6; y473..479) — colour census
   (82,125,123)/(74,113,115)/(66,105,107)/(57,93,99)/(74,73,82) = the
   textureColourAt family. IDENTICAL law to the status screen
   (statusbg.h kStatusTextureBands).
B. HEADER SPECKLE y8..36 x8..630: (0,0,0) 47.1%, (8,12,16) 26.4%,
   (8,12,8) 13.5%, (8,28,49) 4.7%, (8,32,49) 1.1%, (41,20,33) 0.6%,
   (41,28,66) 0.5%, (8,36,49) 0.3% + green TEXT (0,170,82) 3.7%.
   The statusbg.h kSpeckle weights (0,0,0 .349 / 8,12,16 .327 / 8,12,8
   .172 / ...) differ in raw shares because (a) the t3 status capture has
   row content under the header, (b) text share differs per screen —
   [inferred] SAME generator, same six non-text colours.
C. DIVIDER RAMP y38..45 then BLACK at y46+ (x8..476 span; the right panel
   starts ~x477): y38 (82,125,123), y39-40 (123,182,181), y41
   (115,117,115), y42 (66,105,107), y43 (33,56,57)/(24,48,41), y44
   (24,48,41), y45 (24,28,24), y46 (0,0,0) 580/580.
   vs statusRampColourAt (status screen): same families rows 38..45, but
   the status ramp ends SOLID (33,56,57) AT y46 and the left border line
   x7 (33,56,57) runs y48..470. On the RESEARCH capture BOTH differ:
   y46 is BLACK and x7 y48..470 is BLACK 423/423 — the tree field is
   flush-black to x7. [verified] The ramp/border tail is per-screen; the
   research variant = ramp y38..45, black y46+, NO x7 line.
D. RIGHT PANEL: mineral-texture border band x477..~485 (transitions at
   every scan row), black interior to y434, bottom well x477..639
   y434..472 (pan buttons paint over it). CODE-DRAWN (STATE 20 census =
   RESWIN + 4 buttons). SHIPPED (kResChromeBands bands 5-7; the t408 gray
   panel rect deleted) — superseded by the P4 edge measurement below.
=> SHIP: research screen paints the statusbg chrome family — perimeter
   bands + header speckle + ramp rows 38..45 — and DROPS the tan header
   box + gray kLane interior rect (port inventions; vendor tree field is
   flush-black x7..476 under the speckle chrome). Ramp tail y46 solid +
   x7 line stay STATUS-ONLY [verified by D above].

## P4 — PANEL EDGE MEASUREMENT + SHIP (scripts/tPF11_panel_edges.py)
Left band x477..484 continuous y46..433 (per-col tex 331/331 x477..483 in
y100..430; x485 BLACK 0/331); bottom well y434..438 runs 477..639; top
edge inside the ramp rows (y38..42 x460+ runs reach 639). Tree-field
bottom flush-black to y472 (x10..469 tex 0), resumes y473 — one row lower
than the status band (kStatusTextureBands y472). SHIPPED as
kResChromeBands (7) + resRampColourAt + the ui.cpp research arm; tan-box
and kLane-rect conditions decline kScreenResearch; the t408 gray
SDL_RenderDrawRect panel border deleted (invention). Pins
tests/test_reschrome_tpf11.cpp x5 incl the ui.cpp wiring window-pin
(arm anchor + decline conditions + the retired invention colour must be
absent ENTIRELY from ui.cpp — de-literalised comment law tPF-1b).
MUTATION 5/5 CAUGHT (tPF11_mutate.sh; M5 anchored at the .h inline table
after a round-1 .cpp anchor miss — tPF-10 M2 lesson re-learned), md5-
verified restore 4a554e96/95395ebe/606a0994. WITNESS PASS seed 5 at rest
AND after Escape re-entry (tPF11_witness.sh); vision confirms mineral
frame + speckle header + panel band/well, zero gray/tan artifacts.
CENSUS TRAP: the port textureColourAt family includes DARK mottle cells
((12,12,12),(24,49,40)) — the vendor-bright min>=40 classifier reads them
unpainted (round 1 VERDICT FAIL); band census in THESE regions = non-black
frac (the alternative state is the black interior).
