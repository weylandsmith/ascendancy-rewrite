# _wip_t276 — PLANETALLOC WINDOW WIRING (pure code, machine-free)

Assigned: docs/STATE.md NEXT ACTION t276 (queue row VERBATIM): "the five-panel
planet screen geometry from windows.txt (PLRES/PLIND/PLPRO/PLPOP/PLBUILD,
type-29, left-to-right) + header getters (static.txt #147/149/151/152/153 law,
selfplay.md) + gauge selector (ui::gaugeSelector clamp law) + poppanel (t263)
+ planitem hypothesis -> wire into rewrite/src/ui/ as the planet window
composition; tests pin panel order + header format strings."

Machine state at task start (2026-11-02 ~16:20): production :9 LIVE
(dosbox-x pid 576895, -time-limit 172800), x11vnc ESTAB on :5910 -> drive-class
work STAYS HELD per t275. No new sitting: scripts/r214_triage.py prints
"sitting delta: True" against the t214 TRIGGER-A baselines (stale, expected),
but the tail census is turn 645 ONLY (last 2 MB: 613 rows, all turn 645, wall
14:40:03 -> 16:19:39, bad json 0) and r1_stream dedupes per the t85b `seen`
law, so there is NO new sitting -> r1_t85g_sitting.py correctly NOT run (t152
stale-replay trap).

## S1. windows.txt PLANETALLOC family [verified verbatim, extracted/ascend00/windows.txt]

Parent (line 1485 block): TYPE 7 NAME PLANETALLOC PARENT NONE rect 0,0..639,479
SHAPEFRAME 0 SENDMESSAGE 3 HELPINDEX planal WINITEMS 0.
Children in FILE ORDER (= declaration order; no WINITEMS children anywhere in
this family, so there is no separate child list to reconcile):

  line  NAME        TYPE X0   Y0  X1   Y1  SENDMSG PARAM1 PARAM2 HELPINDEX
  1503  PLANLIST    10   120 120 520  420 0       0      0      0
  1519  PLSQUARE    14   152 120 487  375 1       0      0      0
  1536  PLRES       29     7   7  114  106 50      0      0      plres
  1553  PLIND       29   123   7  230  106 50      1      0      plind
  1570  PLPRO       29   239   7  346  106 50      2      0      plpro
  1587  PLPOP       29   355   7  454  106 50      4      0      plpop
  1604  PLBUILD     29   463   8  632  106 51      1      0      plbuild

All five TYPE-29 panels carry STATE '1 17', MOUSEFOCUS 0, SHAPEFRAME -1,
SOUNDCHANNEL 0, WINITEMS 0. X-bands are DISJOINT with a uniform 9 px gutter
(114->123, 230->239, 346->355, 454->463) and the first panel starts at x=7:
left-to-right order == file order == PLRES,PLIND,PLPRO,PLPOP,PLBUILD. Panel
sizes: 108x100 x4, PLBUILD 170x99 (its Y0 is 8, the only off-grid Y0).
PLPOP rect 355,7..454,106 == 100x100 (the t254 grid arithmetic anchor).
SHAPEFRAME -1 on all five = NO windows.txt shape binding (planets-ui.md S1
structural fact): level->record selection is 100% code-side.

## S2. static.txt getter records [verified, extracted/ascend00/static.txt]

getter(n) == recs[n] with recs = quoted-string scan, 0-INDEXED (selfplay.md
S/t246 pins getter(151) to the occupied-planets header; extraction reproduces
it exactly, so the index convention is confirmed against a cited record).
Total quoted records 191 == the live count law (aicode.md:700-706, 0xbf).

  #147 'Under Construction at %s'
  #148 'Being Refitted at %s'
  #149 '\nMoving to Planet'
  #150 '\nMoving to Starlane'
  #151 '%s  (%d Planet%s Occupied, %d System%s Controlled)'
  #152 '%s  (%d Ship%s, %d more allowed)'
  #153 'Player Species'

NOTE the double space in #151/#152 between %s and '(' — byte-exact, pinned by
the test. #149/#150 are LEADING-NEWLINE fragments (appended to a planet/system
name, not standalone titles).

## S3. Dispatch + wiring inputs re-verified this session
- planets-ui.md S2 [verified t198, re-read]: switch key = SENDPARAM1-slot byte
  with two code-side remaps — 0x3cc1c maps value 4 -> 3 (PLPOP); 0x3cc29 maps
  ANY widget with SENDMESSAGE == 0x33 (51) -> key 4 (PLBUILD). Case bodies
  [verified LIVE from 41.sav member 0x3cb98]: [0x3cca7 PLRES, 0x3cd3b PLIND,
  0x3cdcf PLPRO, 0x3ce39 PLPOP, 0x3cefd PLBUILD]. STRUCTURAL CONSEQUENCE:
  PLBUILD's SENDPARAM1 is 1 — WITHOUT the msg-51 remap it would collide with
  PLIND's key 1. The remap is load-bearing; the t276 test pins exactly that
  collision (paintKey(51,1)==4 while paintKey(50,1)==1).
- poppanel.h t263: popPanelCells/popPanelFor(bands, origin) exist; the
  composition supplies origin (355,7) == kPlPopRect corner.
- gauge law S3 table: PLRES <- +0x46 RES, PLIND <- +0x44 IND (both
  clamp0..20 round(L^0.75) == ui::gaugeSelector), PLPRO <- +0x48 PROS
  identity clamp0..20 == ui::prosSelector. Campaign::channelWordsFor(star)
  returns exactly {ind,res,pros} (+0x44/+0x46/+0x48 analogs, t45 governor
  branch included).
- planitem hypothesis shp.md S23.4 [verified ONE item]: live PLBUILD icon
  (Vega IV, "Scientist Takeover" == item idx 34 per income-law.md S6h) matches
  planitem.shp rec k34 at MAD 1.5 (next best 42.1). record-index == itemIdx
  cited for k34 ONLY; other 39 ids stay a contact-sheet fold (OQ-005 scope) —
  plbuildIcon() is documented [inferred] for idx != 34 and the test asserts
  only k34 + the shape-file string.
- PLURAL PAIR [inferred for #151/#152]: static.txt #28 '' / #29 's' is the
  vendor's generic plural pair (aicode.md §8.2: countdown singular iff ==1
  picks [0x1c]/[0x1d] == records 28/29). No cited call-site evidence exists
  that #151/#152 consume exactly this pair with singular-iff-==1; live
  testimony only shows plural forms (60/26 @t1086, 25 Ships @t1255). The
  module implements singular-iff-==1 with this pair, labelled [inferred];
  the test pins the FORMAT STRINGS byte-exact (cited) and the plural shape as
  a rewrite-default, NOT as vendor law.
- static.txt extraction check: 382 quote chars == 2x191 records, zero escaped
  quotes — the naive quoted-pair scan IS the record law at this file.
- #149/#150 carry a LITERAL two-char backslash-n in the file; live fleet rows
  render location on a second line (ui-runtime.md §6c), so the loader
  interprets \n [inferred]. Module stores a real newline; test pins the file
  record (literal backslash-n) AND the module constant (real newline).

## S4. Deliverable
rewrite/src/ui/planetwin.{h,cpp} (pure, ascend_ui + run_tests) +
rewrite/tests/test_planetwin_t276.cpp; CMakeLists gains both lines. API:
  enum PlanetPanel {PlRes,PlInd,PlPro,PlPop,PlBuild}; kPlanetPanels[5]
  (rect,msg,param,help) verbatim; planetPanelFor(Pt) hit-test; paintKey
  (dispatch remaps); kPlanetAllocRect/kPlanListRect/kPlSquareRect;
  header strings kFmt* verbatim + formatPlanetHeader/formatShipHeader/
  constructionText/refitText/movingText; planetGaugesFor(Campaign,star);
  plbuildIcon(itemIdx).
