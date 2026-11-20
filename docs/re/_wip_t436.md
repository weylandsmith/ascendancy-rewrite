# t436 WIP — SPECIES SCREEN + SPECIAL ABILITY CYCLE

Assignment (docs/STATE.md NEXT ACTION t436): (A) species screen "quite off" —
derive its window paint chain + race art records; (B) SPECIAL ABILITY BUTTON
DOES NOTHING — windows.txt button SENDMESSAGE -> which handler? decompile the
target; implement or bank the honest negative IF the handler provably requires
unreachable state (name the witness).

Pre-flight: live-timeline.jsonl mtime 2026-11-12 < last landing 2026-11-20 =>
no new sitting, assignment stands. Tree clean at c62c025.

## F0 in-hand starting points
- windows.txt: "Special^Ability" TEXTITEM ln516; ABILITYWIN NAME ln2136 with
  two children PARENT ABILITYWIN ln2154/ln2171.
- docs/re/abilities.md (roster + effects), docs/re/species.md (history.txt
  specnum blocks), t412/t415 race-intro chain (FUN_0002b48a history parser).
- t435 tooling notes: rail switches = rail widgets; census scripts need
  ~/.hermes/hermes-agent/venv/bin/python; windows.txt child rects for
  SHAPEFRAME buttons are HALF-OPEN.

## F1 [MEASURED windows.txt parse + extracted tree] THE SPECIES SCREEN'S CHROME LIB IS 7RACESEL.SHP AND THE PORT LOADS NONE OF IT
windows.txt ln720-723: TYPE 100 / STATENUMBER 7 / SHAPEFILE DATA\7RACESEL.SHP —
the eight TYPE-100 blocks are 0 0OPENING, 1 1STARMAP, 3 3CFGNEW, 7 7RACESEL,
8 8SHIPDES, 13 13NEGOT, 16 16BATTLE, 20 20RES (parser: 132 records total).
The file EXISTS on disk: extracted/ascend01/data/7racesel.shp (+ .tmp).
rewrite/src/ui/ui.cpp kLibFiles[8] = {1starmap,10status,14intel,20res,planets,
17np,16battle,suns} — 7racesel is NOT loaded, so state 7 can paint NO chrome.

STATE-7 RECORD CENSUS (21 records, parse of extracted/ascend00/windows.txt):
  COSMOSWnd TYPE 2 rect 7,7-465,472 (map stays visible behind the rows)
  dials ROTRIGHT/LEFT/UP/DOWN + ZOOMOUT/IN + CENTERHOLO TYPE 0, STATE "3 1 7 13",
    SHAPEFRAME 8..14, msgs 51/50/52/53/55/54/56 — SAME records as state 1
  toggles TOGLANES/TOGEMPIRE/TOGSHIPS/TOGCOLONIES TYPE 25 SF 15..18 msgs 57/60/58/61
  RACECONTROLS TYPE 3 rect 474,442-632,472 SF 19 msg 62 (the race filter)
  RACE_1..7 TYPE 6 rect 474,(7|46|85|124|163|202|241)-632,+30 STATE "1 7"
    SHAPEFRAME -1 WINITEMS 0 msg 1 p1 13  <-- NO SHAPEITEM, NO TEXTITEM
  Intelligence TYPE 0 474,303-632,333 SF -1 msg 1 p1 14
NOTE the RACE rows carry WINITEMS 0 (the port comment/speciesmenu.h says the
same) — so the row CONTENT is code-drawn, but the screen FRAME is 7racesel.

## F2 [MEASURED] 7racesel.shp CONTENT: k0..k6 = FLAT navy, k7 = the filter strip
tools/shp_pngdump over extracted/ascend01/data/7racesel.shp (N=8, all decode
ok, 158x30 each): decoded md5 k0..k6 BYTE-IDENTICAL (e1c2578c0645, ALL 4740
px = idx 242 = (12,32,48) navy); k7 = 3985 navy + arrow/dial glyphs
(idx 13/15/147/145/146) — ASCII render == the RACECONTROLS bottom strip
(dots ring + 4 dials + 4 squares + 3 dots). Container law: slots are
table_end-RELATIVE (rec i>0 at table_end+slot[i-1]).
=> t393's "size-match witness" for row faces is REFUTED as art: k0..k6 are
   solid navy panels, not row art. k7 is the RACECONTROLS SHAPEFRAME 19 face
   (rect 474,442-632,472 = 158x30 exact).

## F3 [MEASURED vendor capture + NATIVE VISION] WHAT THE SPECIES SCREEN IS
work/screens/t252/species_menu_game.png (640x480, 1:1): LEFT = the star map
CONTINUING (COSMOSWnd STATE list contains 7) WITH FOUR LARGE CIRCULAR RACE
PORTRAITS ringed in owner colour; RIGHT column = header "3 of 3 Species
Known" (white, ~y14), SEVEN 158x31 navy row panels at 474,7/46/85/124/163/
202/241 (rows 1-3 carry flag 14x24 + name/Extinct; rows 4-7 EMPTY navy),
INTELLIGENCE button ~y303-333, then the dial/toggle cluster + the
RACECONTROLS strip. Pixel census rail column y0..300 species vs baseline:
40878 px differ; species-dominant NEW colour (8,12,16) x11020 = the empty
interior of the row panels vs map colours behind.
PORT DEFECTS vs this witness: (1) no navy row panels (only a grey 1px
SDL_RenderDrawRect outline); (2) no portraits (t409 named seam — now
routable: lgrace class, composite = circular clip + coloured ring);
(3) RACECONTROLS strip face unblitted (7racesel k7 IS cited via SHAPEFRAME 19).

## F4 [MEASURED t252 capture, 1:1 640x480] SPECIES COLUMN LAYER LAW
work/screens/t252/species_menu_game.png vs its own baseline_game.png (map,
turn 1255; _state.json). Percentages are of the 158x30 slot area:
  slot0 header y7..37   : (8,12,16) 52% + (0,0,0) 31% = DARK SPECKLE + white
                          title bbox x493..612 y15..25
  slot1 y46..76  KNOWN  : (8,32,49) 91% NAVY PANEL + flag/name ink
  slot2 y85..115 KNOWN  : navy dominant   slot3 y124..154 KNOWN: navy 94%
  slot4 y163..193 EMPTY : (8,12,16) 54% + (0,0,0) 36% = DARK SPECKLE
  slot5 y202..232 EMPTY : speckle 63/26   slot6 y241..271 EMPTY: speckle
  gaps y37..46 etc      : chrome family (123,182,181)/(148,150,148)/(24,28,24)
  y271..303, y333..360  : chrome mottle (74,113,115) 33-35% dominant
  Intelligence y303..333: (8,32,49) 94% NAVY + white centred text
  RACECONTROLS y442..472: speckle/chrome mix (the strip face over chrome)
  FULL right column vs baseline: 43.9% identical; the dial/toggle cluster
  y360..472 is 99.85% IDENTICAL to the map screen => the cluster is painted
  unchanged; the species overlay is ONLY the column + panels.
COLOUR LAW [decisive]: (12,32,48) — the colour 7racesel k0..k6 decode to via
game.pal+conv — occurs ZERO times in BOTH captures; (8,32,49) occurs 22150x
(species) / 25890x (baseline). So the vendor navy PANEL colour is (8,32,49)
(the port kStatusWellNavy), and the 7racesel flat-navy faces are NOT the
panel source on this capture (palette seam title-art.md S4 / t425b).
=> LAW (measured): state-7 right column = CHROME mottle background (t422
   textureColourAt family); header slot + EMPTY slots = DARK SPECKLE
   (t424b introSpeckleAt family); POPULATED species rows + the Intelligence
   button = flat navy (8,32,49) panels at the verbatim windows.txt rects.
   The port today paints a flat (16,16,24) column + grey 1px SDL outlines —
   the root cause of "quite off".

## F5 [MEASURED] THE FOUR PORTRAITS ARE HOME-STAR RINGS
Blob census of the species capture (left field x<466): FOUR blobs ~110px
acat bbox: centres (236,71) (65,236) (403,238) (233,407), each 109..116 px.
Radial profile: CONTENT to r~47-49, RING band r50..55 (3-tone shade of ONE
hue: e.g. (0,142,66)/(0,113,57)/(0,85,41) green; (132,69,140)/(99,52,107)/
(74,40,74) purple; (198,146,33)/(140,93,49)/(57,40,16) gold; (156,73,0)/
(115,48,0)/(57,40,16) orange), BLACK outside r56.
The baseline (map screen) has a STAR MARKER at every one of those four
centres (brightest px within 12 px = (255,255,255)/(148,215,255) star
colours) => the portraits are centred on the AI species HOME STARS, ringed
in the OWNER colour. N=4 blobs vs 3 known species in the header: the capture
has one extra ringed portrait (the player home? or an uncontacted race) —
COUNT LAW UNRESOLVED, named seam.

## F6 ABILITY LEG STATUS (no new measurement needed)
The msg-5 path is WIRED and witnessed since t409 (winmgr 0x55ffb -> opener
0x37b14 -> ABILITYWIN + help.txt abilNN; scripts/t409_species_witness.sh
VERDICT PASS). The remaining vendor behaviour the port does NOT have is the
USE-ABILITY fire (dispatcher 0x37b6a DX==1 -> CALL 0x43b50 edx=1): the sim
model is auto-fire (abilities.md S3) and wiring click-to-fire moves the
seed-regression md5s, so it stays a NAMED SEAM, not a defect I can close in
a display iteration. This iteration re-witnesses OPEN/DISMISS live.

## F7 [MEASURED] ROW CONTENT GEOMETRY (t252 species capture, 1:1)
- FLAG: raceface bbox x488..502 y(rowTop+3)..(rowTop+27) on all three rows =>
  row-local (14,3), 14x24 = the raceflag face native size (t426 plaque law).
  Flag hue tracks the row (purple/orange/yellow) = raceflag k<specnum>.
- NAME: CENTRED in the row [decisive]: "Orfa" x542..564 centre 553;
  "Ungooma" x531..575 centre 553; "Extinct" x536..570 centre 553; row centre
  (474+632)/2 == 553 EXACT. Text rows y(rowTop+8)..(rowTop+17). The port
  draws LEFT-aligned after the flag -> defect.
- NAME/FLAG INK colour = the row species colour (Orfa (156,81,173) purple,
  Ungooma (239,121,0) orange); Extinct reads WHITE (255,255,255).
- Intelligence button: navy (8,32,49) 94% + centred white text bbox
  x526..580 y304..321 (centre 553 == the same centring law).
- EMPTY slots are NOT navy: slot4/5/6 census (8,12,16) 54-63% + (0,0,0)
  26-36% = the t424b DARK SPECKLE family; POPULATED rows are (8,32,49) 91-94%.
- PORTRAIT GEOMETRY: content disc to r~48, three-tone OWNER-COLOUR ring band
  r50..55, black beyond r56. smrace rec 49x49 x2 = 98 (r49) and racering
  53x53 x2 = 106 (r53) == the measured band EXACTLY (t423c2 ring law reused).
  FOUR portraits in the capture vs 3 known rows; the player home star (white
  marker, baseline (129,410)) carries NO portrait -> COUNT LAW UNRESOLVED,
  named seam T436-A (do not invent a fourth).

## F8 [MEASURED] EMPTY-WELL GRAIN + RACERING PALETTES (ready for t436b)
- Empty-well grain census (slot4/5): lag-1 |lum| h 3.09/2.96, v 3.07/2.99,
  same-colour adjacency 0.74 — correlated, much smoother than the intro
  speckle (3.41 at lag1) and than iid. The t424b introSpeckleAt chain
  (copy-left 5 / repeat-up 25) is the closest in-hand generator; census
  families match (200/0/196 dominant). t436b should RE-FIT weights on the
  species wells (200:63 0:26 196:9 renormalised over the 3-family base) —
  a distinct salt, same chain shape; grade with these exact statistics.
- racering.shp decoded palettes (game.pal conv): k0 (0,113,56)/(0,85,40)
  GREEN; k1 (101,52,109)/(73,40,77) PURPLE; k2 (199,146,36)/(60,40,16)
  GOLD; k6 (158,73,4)/(117,48,4) ORANGE; k7 NEUTRAL grey (166,166,166).
  The four measured portrait rings are exactly green/purple/gold/orange
  (F5) => the portrait ring IS a racering-class face (or the same 3-tone
  ramp law), ring index == colour index, t423c2 law RECORROBORATED on a
  second screen.
- The player home star (129,410) on the species capture shows the plain
  white home marker + NO portrait ring => portraits are NOT "every home
  star"; count law stays seam T436-A (capture: 4 rings, 3 known rows).
## F9 ITERATION STATE (honest)
This iteration = MEASUREMENT ONLY (budget). A first code pass (speciesmenu.h
law constants) was written then REVERTED (git checkout) when the run-time
budget hit — the tree carries NO code delta; suite untouched. The complete
t436b implementation brief (all inputs now measured):
 1. ui.cpp state-7 branch: paint frameTex-equivalent CHROME over x466..639
    (reuse t400 textureColourAt; the map screen already builds it — extend
    its draw to kScreenSpecies), then per-slot fill via speciesSlotKind:
    Header/Empty = dark-speckle texture (t424b chain, re-weighted F8),
    Populated = flat (12,32,48); Intelligence button navy (already drawn by
    the rail loop — verify it survives).
 2. Row content: flag raceflag k<specnum> at (slot.x0+14, slot.y0+3);
    name CENTRED at kSpeciesTextCentreX=553 (extinct -> "Extinct" white,
    else owner colour); DELETE the grey SDL_RenderDrawRect outline.
 3. Portraits over the cosmos: per known AI owner, project homeStarFor(o),
    blitShapeCircular(smrace<specnum>, x-r49, y-r49, scale 2, clipR 49) +
    racering k<owner%7> at scale 2 centred; NAMED SEAM T436-A on the count.
 4. Pins: test_speciesmenu_t436 (slot-kind table, text-centre constant vs
    the t252 bboxes, flag offset, ring radii vs racering/smrace record dims,
    navy == game.pal 242 conv). Witness: extend scripts/t409_species_witness.sh
    with a census leg (populated-row navy dominant, empty-slot speckle
    families, centred-text bbox, zero grey-outline px, portrait ring hue).
ABILITY LEG: nothing further measured — wired+witnessed since t409 (F6); the
Use-Ability FIRE stays the named sim seam (seed-md5 law).

---
# t436b IMPLEMENTATION ITERATION (2026-11-20)

## G1 [MEASURED re-census, venv PIL, work/screens/t252/species_menu_game.png]
Per-slot family census (x474..632 inclusive, DISPLAY-space colours):
  slot4 y163..192: (8,12,16) 54.1% (0,0,0) 35.6% | lag1h 2.60 lag1v 2.54 same 0.890
  slot5 y202..231: (8,12,16) 62.5% (0,0,0) 25.7% (8,28,49) 9.0% | 2.81/2.89 0.881
  slot6 y241..270: (8,12,16) 50.0% (0,0,0) 46.7% | 2.79/2.70 0.877
  header y7..36 : (8,12,16) 52.3% (0,0,0) 31.3% (8,28,49) 6.6% +white 5.8% | 2.78/2.82 0.882
Run-length census over the three fam-restricted slots: mean run h 4.03, v 3.74
(N=3434/3694) — the discriminating statistic (iid gives 1.92, same-adj 0.48).
CHAIN FIT (splitmix chain, same shape as introSpeckleAt, weights 625/257/90):
best on (lag1h,lag1v,meanrun) target (2.78,2.82,3.88) = COPY-LEFT 45% +
REPEAT-UP 35% -> h 3.20 v 3.50 run 3.92 (residual ~+0.4 lag — the vendor shot
carries display interpolation the port cannot reproduce at 1:1; same-adj 0.74
vs 0.88 is the same interpolation effect: measured run census is robust, the
pixel-diff stats are NOT — fit to run length, grade loosely on lag).
CORRECTION to F9 item (1): populated-row fill = kStatusWellNavy (8,32,49)
(the F4 decisive colour law: (12,32,48) occurs ZERO times in both captures;
F9's "(12,32,48)" was a stale re-quote of the 7racesel decode colour).

## G2 t436b IMPLEMENTATION LANDED (all F9 items executed)
1. CHROME: frameTex draw extended to kScreenSpecies (ui.cpp — the measured
   99.85% cluster-zone identity justifies it; kTextureBands already covers
   x466..639 full height).
2. WELLS: mapchrome.cpp speciesWellAt — t424b chain shape, distinct salt
   0x436b..., census {pal200 625 / pal0 257 / pal196 90}, chain 45% copy-
   left + 35% repeat-up (G1 fit on mean run 3.88; iid floor 1.92). Built
   once as speciesWellTex over the seven kRaceRows rects; drawn after
   frameTex on state 7 only.
3. ROWS: populated slot = flat kStatusWellNavy fill (grey outline DELETED);
   flag at row-local (14,3) via kSpeciesRowFlagDx/Dy; name CENTRED at the
   slot centre (bbox centre 553 law); Extinct ink WHITE.
4. PORTRAITS: per KNOWN AI owner (never the player), centre =
   projectStar(homeStarFor(o)), smrace<specnum> rec0 blitShapeCircular
   scale2 clipR49 + racering k<owner%7> blitShapeScaled at (cx-53,cy-53)
   scale2 (drawn ring-LAST so the band sits over the disc edge). Honours
   the t425 raceVisibleMask filter. Witness log line
   "ui species portrait owner N at x,y" (printed once per owner) so the
   census grades the annulus at the projection law's OWN output.
   SEAMS kept open: T436-A count law (port = known owners only; vendor
   capture had 4 rings vs 3 known rows), T436-B owner->ring index.
5. PINS tests/test_speciesmenu_t436.cpp x6 (rects/553 centre, navy, flag
   offset + raceflag 14x24 record dims, ring radii + racering 53/smrace 49
   record dims, well speckle correlated-not-iid + family set + census
   shares, determinism + salt decorrelation). Suite 466/0.
6. WITNESS: scripts/t409_species_witness.sh VERDICT PASS unchanged +
   scripts/t436b_witness_census.py on the live shot: row1 navy 90.4%,
   empty slots well-family 100.0%, ink centre 553 EXACT, grey-outline 0 px,
   logged centre (216,417) disc 4668 px + ring band 244 chromatic px —
   VERDICT PASS. Census lesson: point-sampling a ring circle is brittle
   (art gaps); the annulus census at the LOGGED centre is the robust law.
