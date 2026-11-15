# t391 WIP — PRESENTATION SWEEP (art-backed-or-honestly-vector per screen)

Assignment: STATE.md NEXT t391. Audit campaign STATUSWND / NEWGAMEWND / LOAD /
other screens for chrome drawn as vector where the vendor has ART. Deliverable:
per-screen verdict citing the windows.txt record, or named seam. NO engine
touches. Screenshot-per-screen handoff like t390.

## S0 sitting check
- scripts/t368_ring_turn.py: parsed=20/20 max_turn=1254 min_turn=1254 (same
  sitting as t380..t383). No new play; assignment stands. Tree clean at launch.

## S1 windows.txt census (extracted/ascend00/windows.txt, 2238 L, 132 records)
[verified] TYPE census: 0 x69, 10 x10, 100 x8, 25 x7, 6 x7, 29 x5, others x1.
[verified] SHAPEFILE census: EXACTLY 9 files carry a SHAPEFILE line:
  the eight TYPE-100 STATENUMBER blocks (0 0OPENING, 1 STARMAP, 3 CFGNEW,
  7 RACESEL, 8 SHIPDES, 13 NEGOT, 16 BATTLE, 20 RES) + TESTDLG.
  => NO windows.txt record names 10status/14intel/2savegam/4loadgam.
  The t388 naming law "STATE-id N screen's art file is <N><name>.SHP" is a
  FILESYSTEM-PREFIX inference [inferred], NOT a windows.txt citation. This is
  the audit's key structural fact: windows.txt can never itself tell us a
  STATUSWND backdrop exists; only the .shp record inventory + the blit-chain
  can.
[verified] SHAPEFRAME != -1 on 48 records (frames 0..19, 65, 66) — child
  widgets pick frames from their PARENT TYPE-100 lib (the records with
  SHAPEFILE='?' inherit it).

## S2 chrome-lib record inventory (r1_shp_unifiedlaw V/A dims, measured)
[verified] record counts + dims: 10status 2 recs (k0 639x479, k1 32x31);
4loadgam 1 rec 639x479; 2savegam 1 rec 639x479; 3cfgnew 13 recs ALL 84x79/80
(wheel faces, max 88x79); 14intel 10 recs max 28x28 (element art only, NO
backdrop); 20res 6 recs 15x30-ish (the RESROT/RESMOVE arrow faces — rects
524,442-539,472 = 15x30 EXACT match to k0); 7racesel 8 recs ALL 158x30;
8shipdes 9 recs max 69x30; 1starmap 68 recs k0 158x75 (k1 header reads
garbage at the canonical +0x10 offset — 2147483067-ish pair, NOT a backdrop
candidate); 13negot 2 recs 296x101/108; testdlg 1 rec 335x323;
17np 9 recs k0 639x479 + k4 625x357 (NEW: state-17 backdrop candidate).

## S3 windows.txt STATE-section law (the audit's decisive structure)
[verified ln34..1756] the eight TYPE-100 blocks sit at the HEAD of their
state's window section: 0OPENING ln34 -> title buttons; 1STARMAP ln176 ->
state-1 block ln180-556; 3CFGNEW ln575 -> NEWGAMEWND ln579; 7RACESEL ln720 ->
RACE_1..7 ln724; 8SHIPDES ln862 -> SHIPDESSCREEN ln866; 13NEGOT ln1051 ->
NEGSCREEN ln1055; 16BATTLE ln1140 -> battle ln1144; 20RES ln1756 -> RESWIN
ln1760. FIVE screen sections have NO TYPE-100 header: states 2-4-15
(LOADSCREEN ln686), 10 (STATUSWND ln1017), 14 (INTELSCREEN ln1106), 17
(PLANETALLOC ln1485), 18 (FLEETWND ln1722).
[verified] On disk the numeric-prefix file EXISTS for all five except 18:
2savegam/4loadgam/10status/14intel/17np are present, NO 18*.SHP exists
among the 165 .shp files. => FLEETWND SHAPEFRAME 0 (ln1731) cites nothing
resolvable — fleet chrome is honestly-vector in ANY faithful port.
[verified] LOADSCREEN+LOADLIST STATE "2 4 15" (count 2, ids {4,15}) — the
same two windows serve BOTH load and save; title LOAD button SENDPARAM1 4
cites state 4 as the load side; state 15 owns no windows of its own and is
[inferred] the save-side variant, with 2savegam.shp k0 (single 639x479 rec)
the only save-named backdrop on disk.
[verified] TYPE-18 census = EXACTLY ONE record: NEWGAMEWND (ln579), SHAPEFRAME
0 -> 3cfgnew k0 84x79. NEWGAMEWND rect 334,12-488,364 (154x352) has NO
backdrop-size record anywhere in its library (13 recs max 88x80) — the frame
line we draw is honestly-vector; the wheel faces ARE the art (t387 blits k0).
[verified ln456,477,498,517,612,631,650] SHAPEITEM keyword EXISTS (7 uses —
my first-pass keyword grep missed it; ui.md §1 had it all along): grammar
`SHAPEITEM 1 data\<lib> <frame> <dx> <dy>`. The seven: RESEARCH/FLEET/
STATUS/SPECIALAB rail buttons -> 1starmap.shp frames 3/4/5/7 (EXACTLY the
t388 sidebarIcon law — CONFIRMS the port's rail icons are vendor-cited), and
GALAXY_MORE/PLAYERS_MORE/DIFFICULTYMORE -> 3cfgnew.shp frame 0 (the wheel
face t387 already blits). NO SHAPEITEM exists for STATUSWND/FLEETWND/
INTELSCREEN/NEWGAMEWND backdrops — item-level art census is exhausted and
the port covers every cited SHAPEITEM.
[verified] RACE_1..7 + Intelligence rows: SHAPEFRAME -1 on ALL EIGHT (ln724,
741, 758, 775, 792, 809, 826, 843) — windows.txt assigns NO shape to the
species rows. But 7racesel.shp k0..k7 are EIGHT records of EXACTLY the row
rect size (474,x-632,x+30 = 158x30, all 8 rows incl. Intelligence 303-333).
Strip role = [inferred] size-match witness, NOT a table citation -> named
seam, do NOT implement without a stronger witness (palette seam compounds).

## S4 verdicts (draft, screenshot to confirm blit lands)
- TITLE: art-backed (t390 GIF + t386 TSV). DONE.
- MAP state 1: honestly-vector (1starmap k0 158x75 element art; no backdrop).
- STATUS state 10: art-backed — 10status k0 639x479, t388 measured 306081
  opaque px == 639*479 EXACTLY, zero skip rows = FULL backdrop CONFIRMED
  (task (a) answered: k0 IS the backdrop, not a strip); ui.cpp:243 blits it.
- INTEL state 14: honestly-vector — 14intel.shp has NO record >= 600x400
  (max 28x28); element art unused = named seam (row icons).
- FLEET state 18: honestly-vector — NO 18*.SHP exists (165-file census) and
  no windows.txt SHAPEFILE names one.
- RESEARCH state 20: honestly-vector backdrop (20res max 30x15); art that
  exists and we skip = 20res arrow faces (15x30 rect match) + restree.shp
  tech-tree content art — named seams.
- LOAD state 4: art-backed (4loadgam k0 639x479 single rec, t387 blits).
  SAVE state 15: art EXISTS (2savegam k0 639x479) but our port has no save
  screen (no campaign writer, t382) — named seam, art-in-hand.
- NEWGAME state 3: honestly-vector frame + art wheel faces (3cfgnew 13x
  84x79); RACELIST inherits 3cfgnew section lib (frame 7 = 84x80).
- SPECIES state 7: map visible (COSMOSWnd "4 1 3 7 13"); our race-row
  frames are vector; vendor strips 7racesel 8x158x30 = named seam (S3).
- STATE 17 (PLANETALLOC): not implemented in port; 17np.shp k0 639x479 is
  the backdrop-per-prefix-law — banked for whoever implements state 17.

## S5 witness runs (all real)
- scripts/t391_screen_shot.sh (Xvfb :96, ONE window; app log confirms every
  transition: LOAD->cancel->Title->RESUME->map->Planets->map->Ships->map->
  Research->map->Species->Intelligence->map->quit): 8 shots banked
  work/r1/loop/t391-<screen>.png.
- scripts/t391_screen_mass.py PASS 8/8: title mass 232,554 (52 distinct);
  load 59,803; status 53,438 (72 distinct); fleet 4,035; research 2,447;
  intel 4,124; map 32,096 + species 12,768 = 'content' class (vector map
  content on screen, honestly NOT art-backed — matches S4).
  Instrument pitfall banked: per-shot dominant colour must be the background
  (kBg differs per screen: (16,16,24) campaign vs (215,138,56) title band);
  a fixed BG constant false-fails every screen.
- scripts/t391_registration.py (S9 walk re-implemented value-emitting per the
  imported rowwalk_free grammar incl. the C==1 p-does-not-advance quirk;
  mask replicates the 0xAA/0x55 prefill-collision law): 10status k0 shift
  (0,0) 295,063 ramp-matching px 0 conflicts PASS; 4loadgam k0 shift (0,0)
  50,296 px 0 conflicts PASS. Off-shift shifts strictly degrade the ramp
  match (268,911 @ (0,+1)) — registration is sharp, not vacuous.

## S6 landing
- Law banked docs/re/ui-runtime.md t391 block (hand-authored; ui.md is
  REGENERATED by scripts/ui_probe.py:271 — do NOT bank there).
- LEDGER: NO row touched (strict-close; the sweep moves no measurement on
  OQ-016/019/027). HONEST NEGATIVE: zero code change — the sweep found no
  screen where the vendor has backdrop art and the port paints vector.
