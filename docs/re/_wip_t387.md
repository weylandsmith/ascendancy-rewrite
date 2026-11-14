# WIP t387 — MAIN MENU WIRING: NEW GAME + LOAD + RESUME (started 2026-11-14)

Assignment: docs/STATE.md NEXT ACTION t387. Row text: New Game opens
NEWGAMEWND (windows.txt L580 + PARENT controls; art 3cfgnew.shp k0..k11 +
7racesel.shp); Load opens 4loadgam.shp chrome over the SAVE-slot list (slot
law: raw .SAV u32@0 = game-day; supply-your-own dir ONLY, NEVER game/);
Resume = user-chosen slot (do NOT fake RESUME.GAM in game/). Implement window
frame + button hit-map + slot list render via shp decode + VendorText. Pins:
hit-map geometry, slot listing from REAL files in a temp dir (torn-tolerance
law), refusal-not-clamp on junk saves. Campaign-start seed may be a named
seam.

Context already banked (read this iteration):
- docs/re/boot.md §1/§2/§4 — seven-button law, pure machine bootClick/
  bootHotkey, window-reuse law (first synthetic click on NEW window dropped).
- docs/re/title-art.md §7 — title render checklist; verification instrument =
  registration conflict counts, NOT palette membership, NOT self-graded vision.
- Seam sites in title.cpp: st==Load seamLoop + RaceConfig overlay both say
  "lands t387".
- No new play since last iteration (live-timeline.jsonl mtime Nov 12 06:45 <
  t386 landing Nov 14) — r1_t85g_sitting.py NOT run (stale-check done).

## Census results (measured this iteration)
- shp chrome census (extracted/ascend01/data, V/A dims law):
  4loadgam N=1 k0 639x479 (FULLSCREEN frame); 2savegam N=1 k0 639x479;
  3cfgnew N=13 k0..k12 84x79/80 (k11 88x79; k12 = known EOF truncation);
  7racesel N=8 k0..k7 all 158x30; 0opening N=7 k0..k6 318x30.
- windows.txt NEWGAMEWND block (L575-717 read verbatim): TYPE 100
  STATENUMBER 3 SHAPEFILE DATA\3CFGNEW.SHP; TYPE 18 NEWGAMEWND rect
  (334,12)-(488,364) PARENT NONE STATE "1 3" SHAPEFRAME 0 HELPINDEX ngwnd;
  children GALAXY_MORE (7,381)-(122,472) msg 501/0/0 TEXTITEM "Star^Density",
  PLAYERS_MORE (131,381)-(246,472) msg 503 "Species", DIFFICULTYMORE
  (255,381)-(370,472) msg 505 "Atmosphere" (all PARENT NEWGAMEWND STATE 1 3,
  SHAPEITEM 1 data\3cfgnew.shp 0 0 0, SHAPEFRAME -1); Player^Color TYPE 0
  PARENT NONE (379,381)-(493,419) SENDMESSAGE 0; RACELIST TYPE 10 PARENT
  NEWGAMEWND (502,45)-(632,372) SHAPEFRAME 7; LOADSCREEN TYPE 11 PARENT NONE
  (7,7)-(632,37) STATE "3 2 4 15"; LOADLIST TYPE 10 PARENT LOADSCREEN
  (7,46)-(632,472) SHAPEFRAME 7. RACE_1..RACE_7 TYPE 6 PARENT NONE STATE 1 7
  (474,Y)-(632,Y+30) Y=7,46,85,124,163,202,241 msg 1/13/1; Intelligence
  TYPE 0 (474,303)-(632,333) msg 1/14/1.
- COORDINATE SPACE LAW [inferred, geometry-decisive]: PARENT is NOT a coord
  offset — child rects are ABSOLUTE screen coords. Witness: the bottom row
  GALAXY_MORE/PLAYERS_MORE/DIFFICULTYMORE/Player^Color spans x 7-122,
  131-246, 255-370, 379-493 (equal 115-px widths, 9-px gutters, disjoint) in
  absolute space; read relative to NEWGAMEWND (334,12) they would land at
  x 341..484 with y past 393..856 (off-screen, mutually overlapping) and
  RACELIST at x=836 — impossible. Decisive.
- 4loadgam.shp is referenced by NO TYPE 100 block (STATENUMBER census has no
  2/4 entry): the engine must open it by name, like 0opening.gif. Its role as
  the load-screen backdrop is [inferred] from the name + the single
  full-screen record; blit = k0 at (0,0).
- Palette: chrome shp index sets are DISJOINT from the t386 title palette TSV
  (4loadgam k0 19 distinct indices, all 19 absent from the 52-entry TSV;
  3cfgnew k0 44/31 absent). No cited chrome palette exists in docs/, and
  game.pal/logo.pal/subfont.pal were already refuted for the title
  (title-art.md §4). Consequence: chrome renders through a documented
  placeholder luminance ramp; COLOUR fidelity is a named seam — phase-10
  verification is geometry + hit-maps + routing lines, not pixels.
- Slot listing law: raw .SAV u32@0 = game-day (Observer::rawDay, 4/4 corpus);
  a file shorter than 4 B is TORN (listed and marked, never clamped — t366/
  t369 torn-tolerance law); picking an out-of-range or torn slot REFUSES.
- Supply-your-own dir: new `--saves DIR` flag; NEVER game/. Default
  repoRoot/saves when it exists, else an empty list plus one honest line.

## Design (landed this iteration)
- NEW rewrite/src/ui/menulaw.{h,cpp} PURE (no SDL): rect tables +
  newgameControlAt(Pt) hit-map + listSaveSlots(dir) + loadPickAt(index)
  refusal law. Headless-unit-testable by construction.
- title.cpp: the Load seamLoop becomes a real load window (4loadgam k0 blit +
  slot rows via VendorText + click/ESC routing, printing
  'ui load open slots=N', 'ui load pick NAME day D', 'ui load refuse REASON');
  the RaceConfig placeholder overlay becomes the NEWGAMEWND frame + three
  labelled child buttons + the RACELIST frame (clicks print, refuse-not-
  clamp). Campaign-start seed wiring stays a named seam.
- Masked decode: two-buffer prefill diff (0xAA/0x55) marks written px;
  unwritten px -> alpha 0, mirroring the vendor untouched-destination
  semantics documented in shp.h.
- Gate: 4c-c LOAD-click smoke ADDED (xsend 318,375 -> grep open line with
  slot count + backdrop, Esc cancel, RESUME still reaches campaign).

## Live witness (scripts/t387_menu_check.sh, Xvfb :79, ONE window, 2026-11-14)
    ui title click LOAD -> load
    ui load open slots=4 backdrop=4loadgam.shp k0
    ui load pick 07.sav day 300
    ui title click LOAD -> load
    ui load open slots=4 backdrop=4loadgam.shp k0
    ui load refuse 43.sav (slot is torn (partial autosave))
    ui load cancel
    ui title click FRESHGAME -> raceconfig
    ui raceconfig click GALAXY_MORE msg 501
    ui title click RESUME -> campaign
    ui click next-turn
    ui ok: turn 1
  (4 slots = 07/41/42 + torn 43; day 300 == the u32@0 written for 07.sav.)
- Suite: 276 -> 281 tests, 0 failed (test_menulaw_t387.cpp x5: geometry,
  hitmap incl. off-by-one no-clamp, real temp-dir listing w/ torn + case,
  missing-dir honest zero, row geometry + refusal reasons).
- Durable law distilled to docs/re/boot.md §6 (coordinate-space law, tables,
  slot law, blit mask law, palette seam).
