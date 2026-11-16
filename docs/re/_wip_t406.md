# t406 WIP — PLANETS: OWNED-ONLY + PLANET VIEW + PROJECT SET (2026-11-16)

## F0 — SCOPE (queue row STATE.md:972 + t405 aftercare STATE.md:985)
(a) membership filter to OWNER == player AND inhabited (the owner's "displays
planets I don't own" complaint); (b) the state-17 planet view opened by a row
click, incl. the PROJECT slot SET interaction ("can't set a project on my home
planet"); aftercare: row-0 frame clips the backdrop "name" header cell.

## F1 — DEFECT MEASURED (repro, this session, scripts/t402_status_witness.sh
## OUT=/tmp/t406_repro, seed 5, Xvfb :96, pre-change build)
/tmp/t406_repro/status-open.png native grade: header "Player  (2 Planets
Occupied, 1 System Controlled)" (correct for seed 5: 1 owned star), and exactly
TWO rows — "Amoroso I (Small Husk Planet) / No Project" and "Amoroso II (Small
Husk Planet) / No Project". The campaign model has ONE PlanetState per STAR
(campaign.h:701, "per star (only owned stars use it)"); Amoroso II..N are
star-record planet NAMES (mapgen.cpp:177 `p.name = pool[i] + " " + roman(...)`)
with NO pop, NO items, NO queue — the port paints a row per name. The t249
vendor law (selfplay.md t248 PROOF 2) counts NAMED planets with
NAME+0x33 == race0, and PROOF 1 ties ownership to the star mask; the vendor
list at t1086/t1254 held colonised worlds only (104/124 colonised planets,
header 60/102). THE PORT'S statusPlanets() therefore fabricates rows for
UNINHABITED worlds of owned stars = the owner's exact complaint
("displays planets I don't own"). Selection logs the star name only
("ui status select Amoroso"), so two rows of one star are indistinguishable.
AFTERCARE visible in the same shot: the backdrop's art "name" header cell at
the left edge reads "na" — row 0's PORT frame starts at y 46 and covers the
header cell band (art header cells y~48..82 per t405 F8).

## F2 — VENDOR TABLE GROUNDING FOR THE STATE-17 SCREEN (windows.txt, verbatim,
## extracted/ascend00/windows.txt lines cited)
PLANETALLOC TYPE 7 ln1486 rect 0,0-639,479 msg 3 HELPINDEX planal; children
STATE "1 17": PLANLIST TYPE 10 ln1504 120,120-520,420 SHAPEFRAME 7 msg 0;
PLSQUARE TYPE 14 ln1520 152,120-487,375 msg 1; five TYPE-29 panels
PLRES 50/0 (7,7-114,106), PLIND 50/1 (123,7-230,106), PLPRO 50/2 (239,7-346,106),
PLPOP 50/4 (355,7-454,106), PLBUILD 51/1 (463,8-632,106) — already tabled in
ui/planetwin.h (t276). PLSQUARE children PLSQBUT0..5 TYPE 0 ln1620..1706
MOUSEFOCUS 1: y-bands 300-330, 265-295, 230-260(PLSQBUT5), 195-225, 160-190;
PLSQBUT0..4 SENDMESSAGE 0, PLSQBUT5 SENDMESSAGE 55 p1 0. NOTE the file has
FIVE distinct y-bands and TWO buttons sharing 265-295 (PLSQBUT1/2) — the table
alone cannot order the six buttons; NAMED SEAM until the consumer is read.
Backdrop candidate: 17np.shp k0 639x479 + k4 625x357 (ui-runtime.md:493,
banked not cited).
## F2b — OPEN: the vendor project-SET consumer (PLBUILD msg 51 / PLANLIST).
REFUTED-ROUTES t341(2) pins the queue WRITER census: ONLY stores of +0x52
cell / +0x54 item are fn 0x38840 0x38af5..0x38b26 (chain 0x38818->0x3875c->
0x38718->0x38753; 17 direct callers incl. UI leg fn 0x3aa0a). Selector legs
fn 0x3f130 run ONLY when [p+0x54]==0xff (caller gate 0x3ea). t342: the human
queue is PLAYER-INPUT class (vendor never auto-queues for owner 0).

## F3 — STATE-17 OPEN PATH + PROJECT-SET LAW, MEASURED FROM BANKED DISASM
planet.txt (extracted/ascend00, vendor tutorial text, verbatim):
- info00: "There are two ways to access a planet. The first is by entering
  the System Display, and then selecting the planet by clicking on it";
  info01: "Once the planet is selected, clicking on it again will take us to
  the Planetary Display." (system-view route = t410; the STATUS-LIST route:
  info05 "the ability to click on either the planet or the star to go
  directly to them" from the Planets screen — OUR route, row click -> 17.)
- info04 (PROJECT SET, the user's missing interaction): "Clicking on the
  Current Project panel ... A list of possible projects will be displayed.
  To select a project, choose it from the list, and then click on the colored
  square where the structure should be built." PLBUILD = "Project Display"
  (help.txt 1622-1628); PLANLIST/PLSQUARE helpindex 0.
QUEUE-ARM GATES (fn 0x38840 cmd0 leg, work/r331_disasm.txt verbatim, the
t341-census'd sole writer 0x38af5..0x38b26):
  0x388e2 slot byte == 0xff (queue empty)   0x388ec item < 0x27 (39)
  0x388f7..0x38922 free-pop gate: (WORD[+0x42]-WORD[+0x4c]) >= UPOP(item)
      else 0x38b92 (reject; recalc runs, nothing stored)
  0x3892a..0x38940 item == WORD ds:0x73e3c (first-table-row bound leg)
  0x38b16 item != 0x23 -> slot byte := item; 0x38b26 +0x54 := item;
  0x38af5 +0x52 := 0xffff unless flags&2 item (t341 S1 class).
  The ACC WORD +0x50 is NOT touched by the arm (reset lives at 0x39290
  completion / 0x37f8d worldgen / 0x3a153 demolish) — port mirrors.
  The CELL word the UI passes is consumed by the checker 0x3a65 leg only;
  COMPLETION always routes through the picker (t43 law, campaign.cpp
  buildPhase) — so the port's order sets item + gates, cell assignment
  stays the cited picker (the vendor's click-a-cell step is a NAMED SEAM:
  the rewrite has no surface-grid painter yet).
  REJECT SHAPE: silent (recalc + return; no sound channel — SOUNDCHANNEL 0
  on every PLANETALLOC child).

## F4 — BACKDROP GRID vs LIVE GRID (aftercare, measured numpy + native vision)
10status k0 decoded (/tmp/t405/10status-RGB.png, numpy this session):
  header cells y 48..85 ("name" x 7..~135, planet-icon cell ~136..167,
  "size and type" from ~175, wide third cell to 618; HLINEs y48/49/51/83/85
  span 612 px); row dividers y 117/119,151/153,185/187,219/221,253/255,
  287/289/291 = pitch 34 DECORATIVE GRID (seven empty cells, size-ladder
  icons per cell); bottom arrows y 425..478.
  The LIVE t3 capture (planets_header_t1086_after_open.png) shows the
  SELECTION markers at pitch 112.8 (t402 law) — the runtime list draws its
  OWN rows over the art, one row = 3 art cells. => the art grid is NOT the
  row law; the header cells (48..85) ARE (native-vision: "name" leftmost,
  2x crop confirms). THE t405 AFTERCARE DEFECT: port rows top 46 -> row 0's
  dark frame paints OVER the "name" cell (renders "na"). FIX (measured):
  rows top 117 = the first art divider line (t3 capture: table top border
  native y 117.2, marker centres 135.6/248.8/360.8 vs pitch-112-from-117
  centres 136/248/360 — EXACT +-0.4). Text columns move to the art's:
  sphere x ~140 (icon cell), line1/line2 x ~180 ("size and type" column).

## F5 — LEDGER TARGETS FOR THIS ROW
- membership: statusPlanets + statusHeaderFor must count INHABITED owned
  planets (pop>0 analog of the vendor owner byte + NAMED filter, t248
  PROOF 2) — the port currently emits one row per star-record NAME
  (Amoroso II..N have no PlanetState) = "displays planets I don't own".
- new pure module ui/planetview.{h,cpp}: screen-17 composition (reuses the
  t276 panel table), project LIST law (research-gated, item<39), order gate
  (free-pop cmd0), Campaign::orderProject thin setter (pendingItem only;
  completion keeps the cited picker).
- statuslaw: kScreenPlanet=17 joins the known set (row-click opens it; the
  rail never does — no rail button targets 17, t405 F1).

## F6 — 17np.shp k0 DECODED (tools/shp_pngdump + game.pal, native vision)
/tmp/t406_17np0.png (639x479): FIVE framed panel boxes across the top strip
(borders land on the PLRES/PLIND/PLPRO/PLPOP/PLBUILD windows.txt rects) over
a full-size black field with an outer frame; k4 (625x357) is a near-empty
dark record. => k0 IS the PLANETALLOC backdrop candidate (prefix law +
size + panel-border agreement; the panel rects are the CITED part, the
binding stays [inferred] per the ui-runtime naming caveat). The planet
surface grid (PLSQUARE) is NOT in the art — runtime-drawn (help.txt: "the
planet's surface is divided into individual squares... Orbital items ...
only visible when hilighted") => the port's surface-grid painter is a named
seam; the state-17 screen ships backdrop + panels + project list.

## F7 — STATUS ROW LAYOUT, MEASURED ON THE t3 CAPTURE (numpy, 1.25x)
Table border HLINEs at capture y 146 (=native 116.8, top) and 572..579
(=457.6+ bottom) — CONFIRMS kStatusInterior top 117, not 46. Row-0 content
runs (native x): selection marker 64..69; system name (cyan) 206..258;
planet text column starts ~260; the big sphere art 74..182 overlaps the
icon cell + name column (the vendor paints the sphere BIG left of centre).
ART HEADER CELLS (10status k0 numpy): "name" x 7..135, icon cell 136..167,
"size and type" 168..~297, third cell to 618; cells y 48..85.
=> PORT LAW CHANGES THIS ROW: kStatusRowsTop 46 -> 117 (kills the "na"
clip); row text moves into the art columns (sphere in the icon cell region,
lines at x >= 175); row 0's dark FRAME fill must not paint the header band
(rows start below y 85 anyway).

## F8 — IMPLEMENTED + PINS + WITNESS (this session)
Code (rewrite; suite 356->360/0):
- statuslist.cpp statusPlanets + statusHeaderFor: ONE COLONISED PLANET per
  owned star (the port's PlanetState is per star; the old per-star-record-NAME
  loop emitted "Amoroso II" etc. = D13 "displays planets I don't own").
  Vendor basis: t248 PROOF 1/2 (owner byte set == colonised; header counts
  NAMED+owner). Pins updated with a regression fence (old shape > new count).
- statuslist.h kStatusRowsTop 46->117 MEASURED (F4/F7): kills the t405
  aftercare "na" clip; row text/sphere/marker moved into the art's columns
  (marker x62, sphere centred in the icon cell 136..167, text x 200, bands
  x380). Row frame starts x 60.
- NEW ui/planetview.{h,cpp} (pure; run_tests): PlanetView readout (title via
  the shared statusLine1 assembly, pop/used/cap, gauge selectors, project +
  days, noFreePopulation = the 0x508da predicate); projectOptionsFor
  (REQUIRES-gated, table order, item<39; free-pop is an ORDER gate not a
  list filter); projectOrderable (cmd0 gates 1/2/3); PLANLIST hit-map
  (rect verbatim ln1504, PORT pitch 24 named seam).
- Campaign::orderProject (campaign.h/cpp): arms pendingItem iff queue empty
  && item<39 && freePop >= UPOP; acc word untouched (resets 0x39290 law);
  silent false = vendor reject shape. Completion picker unchanged (t43).
- statuslaw: kScreenPlanet=17 joins the known set (screenKnown/shapeLib
  17np.shp); NO rail change (no button targets 17 — t405 F1). t388 pin
  re-scoped: no-clamp pinned on 13/99; 17 asserted known.
- ui.cpp: row click -> screen 17 ("ui status select <planet> -> planet view
  (state 17)"); state-17 painter (17np k0 backdrop + panel frames +
  readout + PLBUILD slot text); PLBUILD click toggles the PLANLIST; list-row
  click -> orderProject ("ui planet project <planet> <item> (ordered|
  rejected)"; ordered closes the list).
PINS test_planetview_t406.cpp x4 (hitmap; gates incl. silent-reject-leaves-
state + queue-busy + domain 39; list membership incl. Interstellar-Trucking
absent; readout + rows-top fence + screenKnown 17).
WITNESS scripts/t406_planetview_witness.sh VERDICT PASS: one row per owned
star; row click opens 17; PLBUILD opens the list; "Amoroso I Factory
(ordered)". NATIVE VISION GRADES: status-open — ONE row "Amoroso I (Small
Husk Planet)", art "name"/"size and type" headers FULLY VISIBLE (clip fixed);
planet-view — title/pop/gauges/project panel + 8-item gated list readable.
REMAINING DEFECTS (honest, banked for t411+/t410): (a) the 17np backdrop
paints a flat green field (palette/key seam — same class as t388's
luminance-ramp note); (b) the PLANLIST overlaps the readout text (PORT list
placement; vendor PLANLIST rect is ln1504 verbatim — the readout position is
the PORT's, PLSQUARE grid unimplemented); (c) the decorative 34px art grid
still shows through where our 112px rows don't cover (vendor does too — the
live capture shows the same empty cells); (d) no surface grid / orbital
squares (PLSQUARE seam, F6); (e) Esc from 17 goes to the MAP (escapeToMap
law) — the vendor returns to the opener [unmeasured; t410 will pin the
chain depth].

## F9 — LEDGER (strict-close)
Closes NOTHING: no OQ row owns D13 chrome/function rows (checked
OPEN-QUESTIONS rows touched by t402..t405 — same disposition). The owned-
only list, the planet view, and the project SET are D13 queue-row t406
deliverables, witnessed by F8, dispositioned when the OWNER re-plays. OQ-027
still awaits the user's final audio verdict. No REFUTED-ROUTES additions
needed (no dead route was re-tried; the t341/t342 writer census was REUSED
as banked law, not re-run).
