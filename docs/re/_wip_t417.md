# t417 — PLANETS LIST BACKGROUND (D15) — working log

## Premise identification [verified from disk]
- D15 verbatim (docs/DECISIONS.md L368): "the planets list screen is looking
  better but the background is still off, it seems to be using one of those
  images we determined wasn't used anywhere as a background."
- The "wasn't used anywhere" images = the A-series, and specifically the
  D1 ask block (docs/DECISIONS.md L64): "A6-A8 the 10status/2savegam/4loadgam
  triad you called 'possibly junk data' — now a live keep/junk call from the
  thumbnails (they decode cleanly as 639x479 menu panels; we have never seen
  them drawn)." USER ruling 2026-11-09 (shp.md S28): "A series 'historical
  curiosity' keep".
- Our code paints exactly that asset: ui.cpp:274-282 backdropFor() passes the
  FULL-BACKDROP size test for 10status k0 (639x479), and ui.cpp:752 blits
  record 0 full-frame on the status screen. So the user is looking at
  10status k0 = the asset the D1 batch called unused. Premise CONFIRMED.

## Evidence set
- USER ORIGINAL (allowed evidence): scratchpad/planets-screen-original.png
  (browser screenshot of classicreload play/dosx/ascendancy — the ORIGINAL
  game). Vision read: interior BLACK, mottled dark-grey-teal band at top,
  bevel frame around everything, green header text.
- VENDOR LIVE capture of the MAP screen (not status):
  work/r1/dbg-t330-20261107-073530/11_scr_status.png — sidebar uses
  1starmap art, map interior black.
- windows.txt state 10 census (re-run this iteration): NO TYPE-100 section
  for state 10 — the nine SHAPEFILE records are states 0,1,3,7,8,13,16,20,
  TESTDLG. STATUSWND TYPE 16 SHAPEFRAME 0 (no frame art), child STATPLANLST
  TYPE 10 SHAPEFRAME 7. [t391 already banked: five headerless TYPE-100
  sections incl status 10 — 10status exists on disk but NO windows.txt
  record binds it; "status 10" in the t391 wording = the lib's filename
  prefix, not a STATENUMBER.]

## F1 [measured 2026-11-17] — user original pixel census
(2048x1096 browser shot; game rect detected, mapped /2 to 640x480 space)
(results appended below as measured)

## F1 [measured 2026-11-17] — 10status k0 REGISTERS FAILING on the vendor screen
scripts/t417_k0_register.py (index plane via t391 law, colour through
game.pal + DOSBox conv) vs the t3 LIVE capture work/screens/t3/
planets_header_t1086_after_open.png (game rect rows 100..579, cols 80..719
-> /tmp/t417_t3_game640.png):
  shift(0,0): 299,014 written px; exact 4.5%, |d|<=30 6.4%, mean|d| 149.
  zones: header 17%, tablehdr 7%, ROWS ZONE 3.9%, scroll col 51%,
  right panel (k0 TOTEM/MOBY zone) 1.9%.
  k0 interior is idx 242 navy (12,32,48) x186,722; the vendor interior is
  (0,0,0) x153,162/288k. => THE VENDOR DOES NOT PAINT 10status k0. The D1
  user note ("A series... I don't think the A series are used anywhere") is
  now MEASURED, not recalled. Our ui.cpp:752 full-frame blit of exactly
  that record IS the D15 "background is off / unused image" defect.

## F2 — what the vendor DOES paint (both independent shots agree)
- t3 capture (pixel-exact 640x480, numpy): top band y0-6 p_tex 0.936;
  left band x0-6 p_tex 1.0; right band x633-639 p_tex 1.0; interior
  y48-470 x8-632 p_black 0.77. Header band y7-39: mix black+dark noise
  (top cols (0,0,0) 6780, (8,12,16) 6335, (8,12,8) 3356) + green title.
- user original scratchpad/planets-screen-original.png (browser shot,
  game rect detected 415..1456 x 224..1006, mapped /640x480): texture
  frame = left x0..6, right x633..639, top rows 0..6, bottom rows 473..479
  (column/row texture-fraction scan); interior rows zone p_black 0.925;
  pale divider line (125,182,182) at y~40; sub-header zone y39-115 mixed.
=> LAW: status background = BLACK interior + full-perimeter mottled chrome
   band (~7 px, the t400/t411 texture family) + pale divider lines; NOT a
   shape-record backdrop. Same family as the map screen (t400 S12) and the
   newgame chrome page (t414).

## F3 [measured] — t3 row geometry: PITCH IS 141, NOT 112; ROWS TOP 57
scripts run on /tmp/t417_t3_game640.png (game rect of work/screens/t3/
planets_header_t1086_after_open.png, rows 100..579 cols 80..719):
- flag-icon bands (x8..26 nonblack >=10 px): y57..82, y198..223, y339..364
  -> tops 57/198/339, period EXACTLY 141.
- big-sphere bright rows x60..140: 67..175 / ~235..297 / ~376..435 — same
  period.
- column-profile autocorrelation (x8..610, y48..470): single dominant peak
  lag 141 (0.634).
- t402's "markers native y 135.6/248.8/360.8" ARE REAL but they are the
  SURFACE-THUMBNAIL art row-centres (thumbnails sit ~78 px into the row,
  135.6+113 != row-top spacing law); reading them as row tops + fitting 112
  was the error. The user original agrees: sphere band y72..173, next
  bright band starts ~212 (pitch ~140, browser resample +-2).
=> VENDOR LAW: rows top 57, pitch 141, exactly 3 visible rows
   (57+3*141 = 480). kStatusRowsTop 117 / kStatusRowPitch 112 are REFUTED
   by the capture t402 itself cited. Pins updated with this measurement
   (t406 precedent: re-scope, don't delete).

## F4 [measured] — the vendor status FRAME law (t3 + user original agree)
- perimeter mottled band (texture family, texfrac 0.94..1.0): x0..6 and
  x633..639 full height; y0..6 top; y472..479 bottom.
- HEADER band y8..36 x8..630: DARK speckle (t3 census): (0,0,0) 34.9%,
  (8,12,16) 32.7%, (8,12,8) 17.2%, (8,28,49) 6.2%, green title
  (0,170,82) 5.2%, minor (8,32/36,49), (41,20,33), (41,28,66).
- title green text rows y20..26 (x-scan at 320) => draw at y~18-20 centred.
- divider ramp below header (full width x7..631): y38 (74,113,115)/(82,125,123);
  y39-40 PALE (123,182,181); y41 (90,134,140)-mix; y42 (66,105,107);
  y44 (24,48,41)/(33,56,57); y46 SOLID (33,56,57) x625.
- interior x8..629 y47..471 BLACK (p_black 0.77 incl row art; row zone
  0.925 outside art); NO row separator lines anywhere (hline scan: zero
  rows with >300 mid px in y100..470).
- left border line: x7 (33,56,57) y48..470 (423/423). right border: x630
  pale (189,255,255) segment y48..97 (50 px, the scrollbar box edge);
  x612..629 interior right of rows: mostly black + navy (8,32,49) box fill
  at the arrow wells.
- arrow wells (t405 F8 cited): up box x619..638 y48..94, down y425..478.

## F5 [measured] — header speckle, divider ramp, row-0 column law (t3)
- Header speckle census y8..36 x8..630 (share): (0,0,0) .349, (8,12,16)
  .327, (8,12,8) .172, (8,28,49) .062, title green (0,170,82) .052,
  (8,32,49) .011, (8,36,49) .006, (41,20,33) .009, (41,28,66) .006.
  lag-1/dev = 1.304 => PER-PIXEL noise (the perimeter texture band's
  lag-1/dev 0.877 is smoother; the t411 6x6-cell generator suits the
  PERIMETER, the header wants per-pixel draws). NOTE [honest negative]:
  these capture values do NOT map to game.pal under the (v<<2)|(v>>4)
  conv by exact lookup (checked 20 colours, all None) — the t3 capture is
  a DOSBox X11 grab; treat the census as DISPLAY-space values (draw them
  verbatim), do not claim palette indices.
- Divider ramp below the header (full width x7..631):
  y38 (74,113,115)/(82,125,123) mix; y39-40 PALE (123,182,181) solid-ish
  (454-461/623); y41 (115,117,115)/(90,134,140); y42 (66,105,107)/(57,85,90);
  y43 (24,48,41)/(33,56,57); y45 (24,28,24)/(8,12,16); y46 SOLID
  (33,56,57) x623; y47 black.
- Row 0 (y57..197) x-cluster census (>=8 px tall): flag well x12..144
  (marker red x16..69 y59..82 + big sphere), small sphere x174..242,
  system-name cyan text ~x190..260 (t402 band 224-252 agrees), planet-name
  green x288..341, "(type)" x358..411, thumbnails x428..481 (+284..341
  leg), gauge-dot block x498..559, scrollbar box edge x604..630.
  => PORT text column x200 lands INSIDE the cyan system-name zone; the
  vendor text columns are 288 (name) — port seam, geometry table for the
  implementation session: rows top 57, pitch 141, name x288, line2 below,
  thumbnails x~428, gauges x~498.
- Selection marker: red (123..189 r-dominant) x16..69, rows 59..82 (row 0)
  => marker top == row top + ~2, height ~24, x16..69 (PORT green bar law
  REFINED: vendor marker is RED, x16..69, not x62..72).

## F6 — windows.txt corroboration (this session, re-run)
- TYPE-100 SHAPEFILE census = states 0,1,3,7,8,13,16,20,TESTDLG ONLY:
  NO record binds 10status.shp (or 14intel/2savegam/4loadgam/17np) to ANY
  state. The t391 "five headerless sections" note = the libs exist on disk
  with the state-prefix names, NOT table bindings. The vendor paints the
  status chrome in CODE (speckle + ramp + wells), which is exactly what
  the pixel census shows.
- STATUSWND TYPE 16 SHAPEFRAME 0; STATPLANLST TYPE 10 SHAPEFRAME 7 —
  SHAPEFRAME 0/-1 = no frame art (t391 law), consistent.

## F7 — VERDICT + remaining work (session ended on run-budget, NOT blocked)
DEFECT ROOT CAUSE ESTABLISHED [measured]: ui.cpp blits 10status k0
full-frame as the status backdrop (ui.cpp:752 via backdropFor 274-282);
the vendor never paints that record (F1: 4.5% registration; interior navy
vs vendor black); k0 is the D1 "A-series historical curiosity" asset.
IMPLEMENTATION (next session, t417b) — all laws measured above:
 1. statuslaw.h: new pure backdrop law (perimeter texture bands x0..6/
    x633..639/y0..6/y472..479 via textureColourAt; header speckle rect
    8,8-630,36 per-pixel weighted set F5; divider ramp table F5; black
    interior; left border x7 (33,56,57); NO k0 blit on state 10).
    backdropFor() must DECLINE 10status (mechanical test today says
    "backdrop" — replace with an explicit no-backdrop screen set or an
    index-exclusion, citing F1).
 2. geometry: kStatusRowsTop 117->57, kStatusRowPitch 112->141 (F3),
    text col 200->288, marker red x16..69 (F5), gauge/thumbnail x per F5.
    Pins to re-scope with the F3 measurement: test_planetview_t406:188-191,
    test_statuslist_t402:262-278, test_statusnav_t405 (kTop uses).
    kStatusVisibleRows stays 3 (57+3*141=480 exact).
 3. witness: Xvfb shot + census script (t417_statusbg_witness.sh):
    interior p_black > .9 outside row art; perimeter texfrac > .9; header
    speckle census; NO k0 navy fill (12,32,48) band >100k px anywhere.
 4. mutation per skill rules; seed regression (display-only, expect md5s
    7e794a6d/332a8cf3/0a6b7876 unchanged).
LEDGER: closes NOTHING (strict-close honest negative — D15 chrome rows
have no OQ owner, t414/t415/t416 precedent). Tools banked:
scripts/t417_k0_register.py (game.pal-space registration + zone census).
