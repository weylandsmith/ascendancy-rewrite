# t407 WIP — SHIPS SCREEN (D13 "ships screen is EMPTY")

## F0 PREMISE + CONTROL PLANE (read this session)
- Assignment: docs/STATE.md NEXT ACTION t407 (queue row STATE.md:1032-1038).
- No new play data: work/r1/playcap/live-timeline.jsonl mtime Nov 12 (385326
  lines) predates the t406 landing -> no re-sitting, assignment stands.
- Ruling page :8613 UP (pid 646702). No `USER:` lines after the applied
  D11/D11b/D12/D13 blocks -> nothing to disposition (WAKE PROCEDURE t397).
- REFUTED-ROUTES consulted: the FLEET-row-by-array-rank navigation route is
  DEAD (t298), the digit-key-under-fleet-focus route is DEAD (t314 amend.),
  and the fleet rowjump click (200,93) CLOSES the list law is banked. None of
  those bind a pure rewrite-side list render + hit-map.

## F1 INHERITED STATE OF THE PORT (measured by read this session)
- kScreenFleet = 18 exists (ui/statuslaw.h:50, windows.txt FLEETWND rect
  7,7-632,472 TYPE 17). The rail button (msg 1 p1 18) DOES switch the screen;
  the complaint is the CONTENT: ui.cpp:729 draws only a header strip + the
  interior rect (generic vector frame) — zero rows, no hit-map, no selection.
- THE DATA PROBLEM: Campaign's entire ship state is `std::vector<ShipInTransit>
  fleet_` (campaign.h:723) with ShipInTransit = {owner, from, target}
  (campaign.h:120-128, the t256c GAP-ROW-16 BOUNDARY: transit-only, cited
  order laws deliberately NOT stubbed). expansionPhase() CLEARS fleet_ every
  turn after arrivals claim targets (campaign.cpp:1511), and the
  BumpShipsInLanes comment states outright "model has no idle fleets"
  (campaign.cpp:1788). So a list built from fleet_ ALONE is legitimately empty
  on most turns — the vendor keeps a persistent ship census (docs/re/ships.md
  item 3: 14 named owner-0 records == the FLEET header count exactly; 1234
  owned rows across the corpus), the port does not.

## F2 VENDOR TEXT LAWS (static.txt, extracted/ascend00/static.txt, CP437)
(verbatim bytes + index; offsets computed below)
- #152 "%s  (%d Ship%s, %d more allowed)"  == the FLEET header (t253 vision
  read "Chamachies (25 Ships, 12 more allowed)" is now byte-cited).
- #143 "Orbiting %s" and #146 "In Starlane to %s System\nETA - %d Day%s"
  == the two LOCATION forms t253 saw by vision (ETA in DAYS, third screen with
  the unit law). #146 plural rides the SAME getter(28)/getter(29) ""/"s" pair
  as the t402 days law.
- #34 "Name Your Ship" / #35 "Rename Your Ship?" = the design-dialog name
  prompts (no port dialog exists -> named seam).
- NAME LAW [verified, ships.md:655 + pership-spec.md:70]: rec+0x34 gets a
  stride-2 copy of the hull-name string DAT_00078484 + hull*0x14, SKIPPED for
  player-designed ships (byte3[rec+0x31]!=0 && owner hi16 == player race
  DAT_0007458e). => non-player ships are named by HULL CLASS, not a name pool.

## F3 ALLOWANCE LAW — HONEST NEGATIVE
help shipdes (extracted/ascend00/help.txt:807+): "The number of ships you can
maintain at any time is proportional to the number of star systems you
control." Two measured data points only: (25 ships, 12 more allowed) t1255 and
(14, 13) (ships.md:1491). Total 37 vs 27 with the system counts UNRECORDED at
both points -> the coefficient is NOT derivable from banked data. The port
shows the headroom slot with a labelled default or omits it; NO OQ row closes.

## F4 SCOPE DECISION (this iteration)
(a) pure ui/fleetlist.{h,cpp}: header/location/plural laws + the 4-row page
    law + arrow rects + hit precedence (all cited or labelled);
(b) screen wiring in ui.cpp: rows, selection, scroll pair, Esc, right-click;
(c) the census: [decided below once the ship-name/persistence probes land].
NAMED SEAMS (not invented): SHIPDESSCREEN contents display (t253 geometric id),
the vendor's shipyard production census, row art (t391: NO 18*.shp exists —
honestly-vector is DECISIVE, cite it).

## F5 VENDOR LOCATION-STRING LAW MEASURED (work/r331_disasm.txt, fn 0x50d12)
The FLEET row LOCATION builder (STATSHIPLST family; found by the getter-arg
census: static #143's ONLY arg-0x8f site is 0x50dc5 inside this fn). Body law
[EAX=screen?, ESI=ship record, EDI=flag]:
  switch BYTE[ship+0x58]-1 (orderKind), jump table cs:[0x3c14c], cases 0..4:
  * kind 1 (ORBIT): esi := [ship+0x59] (planet record ptr);
      sprintf #143 "Orbiting %s" with arg [planetRec+0x24] (the NAME field of
      the planet record — 0x50dbc/0x50dc5); then blits the PLANET SPRITE
      (0x5caac, font 0x31) at fixed slot with cx=WORD[planetRec+0x16],
      bx=WORD[planetRec+0x14] — INDEPENDENT CORROBORATION of the t402
      +0x14=SIZE/+0x16=TYPE law (a second consumer).
  * kind 2 (LANE): 0x50e6d — distance = sqrt of squared triple diff
      (0x50ea1..0x50f21), /const ds:0x2aba with x2 leg (ds:0x2ab6) when
      BYTE[target+0x23]&1, clamped >=1.0 (fld1/fcomp/jbe 0x50fac);
      eta := round((trip[0]-[ship+0x9e]) / speed) + 1 (0x50fd4..0x51007);
      SYSTEM NAME ptr = [starRec+0x1c] IF the viewer's bit is set in
      [starRec+0x17] ELSE [starRec+0x0] (0x51010..0x5102d — visibility-gated
      name, OQ-026 twin byte +0x17 AGAIN); plural = getter(28)/getter(29)
      ""/"s" by cmp n,1 (0x51030..0x51041 — the SAME pair t402 cited for
      #139, now cited for #146 too); sprintf #146 "In Starlane to %s
      System\nETA - %d Day%s".
  * kinds 3/4 (0x50e25/0x51066/0x510cc): #144-adjacent getters 0x90/0x93/0x94
      (145/148/149 class strings, planet/lane target renders) — not modelled
      by the port (no carrier/refit orders), named.
  * TAIL 0x51144 (ALL kinds): if BYTE[+0x5d] (act) !=0 && !=7 &&
      BYTE[+0x58]==4 -> append #149 "\nMoving to Planet"; and if act==1 ALSO
      append #150 "\nMoving to Starlane" (byte-pair append loop 0x5118a —
      the literal-\n interpretation law AGAIN, same shape as planets-ui.md
      #149/#150 note).
  * kind outside 1..5 (ja 0x51132): draws literal ds:0x2aa0 (blank/unknown).
PORT MAPPING: ShipInTransit{owner,from,target} is the LANE case analog ->
location = #146 shape with ETA 1 day (the port's transit resolves next turn —
[documented default]; the vendor eta formula above needs per-ship speed/pos
the port does not carry, t256c boundary). No ORBIT case exists in the port
(model has no idle fleets, campaign.cpp:1788 comment) — named, not stubbed.

## F6 FLEET GEOMETRY MEASURED (work/screens/t253/fleet_open_game.png, 640x480 NATIVE)
numpy colour-band census (green-text mask G>R+40&G>B+40; blue-sphere mask) +
native-vision read of the same shot (D13 policy: own-vision is first-class):
  header green band y16..27 centred; FOUR rows:
  name bands y52-64 / 160-170 / 264-290(3-line loc) / 370-382;
  blue-sphere column bands (52,148)(159,254)(264,360)(370,466) x358..382
  -> ROW PITCH 106 +- 1 (108/104/106 name-top diffs; sphere bands 96 tall),
  ROWS TOP 52 (= STATSHIPLST interior 46 + 6), 4 visible rows (t253 dossier
  "pages 4 rows for 25 ships" AGREES).
  COLUMNS native: ship render x~10..150 | NAME green x159..~230 | chevron
  chain x270..323 | blue spheres x358..382 | LOCATION x389..~500 | arrow
  boxes x606..635 with glyph CENTRES (620,63)/(620,453) (the t253 dossier's
  own blue-pixel measurement; boxes y~48..80 / ~438..470 [approx around the
  cited centres]).
  NOTE: the row name is NOT rec+0x34 (that field holds the HULL class word —
  the t379 death witness shows 'Medium' at +0x34): the row name is the DESIGN
  name (design screen reads `Chamachies "Sparrowhawk"`). The port has NO
  design model -> row name = the planitem hull name the campaign actually
  spends ("Ship", planitem row, itemId("Ship")) [labelled PORT DEFAULT],
  seam named: design-name source designRec name ptr [ships.md:191].
  The queue row's "(word 26 law)" is WRONG — static.txt #26 is "Selected
  System" (measured this session). Honest correction recorded here.

## F7 ALLOWANCE: TWO-WITNESS FIT, NOT A LAW
help shipdes (help.txt:807+): "proportional to the number of star systems you
control". Banked witnesses: t1086 planets header "26 Systems Controlled" +
fleet header "(14 Ships, 13 more allowed)" => TOTAL 27 = 26+1; t253/t249
t1254-55: sole-owner loop 36 + "(25 Ships, 12 more allowed)" => TOTAL 37 =
36+1. TWO/FIT allowed_total = systems + 1 [inferred, n=2, NOT a coefficient
measurement; the +1 could be systems+K with the same fit]. Port uses it as a
LABELLED DEFAULT; strict-close: closes NOTHING.

## F8 SCOPE (locked)
(a) ui/fleetlist.{h,cpp} PURE: fleetRowsFor(Campaign, owner) (member law:
    rows == the campaign's live transit entries for owner — the port's ENTIRE
    ship census per t256c; honest zero when none), locationText (#146 shape,
    ETA default), header via EXISTING planetwin formatShipHeader (#152,
    already pinned byte-exact t276 — reuse, do not duplicate), scroll window
    4 rows + hit map (arrows > scroll col > rows, fleet rects F6).
(b) ui.cpp: fleet screen renders header+rows+arrows; LEFT row click selects
    (log "ui fleet select"), RIGHT click deselects (selfplay law; ui.cpp had
    NO right-button handling at all before this task), arrows scroll, Esc ->
    map (existing escapeToMap). Vendor left-click = camera jump — NAMED SEAM
    (port selects + logs; no fake camera move).
(c) pins test_fleetlist_t407.cpp; witness scripts/t407_fleetlist_witness.sh
    (advance turns until the player HAS ships, then grade the list).
NO OQ ROW CLOSES (strict-close; D13 chrome rows have no OQ owner — same
honest negative as t405/t406).

## LANDED (session end, budget-stopped after witness)
F9 BUILD+PINS GREEN: fleetlist.{h,cpp} in ascend_ui; test_fleetlist_t407.cpp
  pins header #152 both plural legs, location #143/#146 ("ETA - 1 Day" dash
  form), allowance law systems+1-ships clamped, hit-map (arrows 619..638 art
  rects, trough inert, rows x7..605, top 52 pitch 106), fleetShipName via
  public planetItem() table lookup (Ship row). SUITE 368/0 (was 360).
F10 STATIC.TXT GETTER INDEX LAW (MEASURED — pin-failure forensics): the
  naive quoted-line counter MISALIGNS from entry ~90 on (multi-line entries);
  ground truth is the file's OWN "// N" comment markers: getter(n) == entry
  under marker N (143 "Orbiting %s", 146 "In Starlane to %s\nETA - %d %s",
  152 "%s  (%d %s, %d more allowed)"). Test reader rewritten marker-driven.
  REUSES: any future static.txt pin MUST use the marker-driven reader.
F11 WITNESS VERDICT PASS (scripts/t407_fleetlist_witness.sh): boot --ui --seed
  5, 277 NEXTTURNs, per-turn probe; log lines: "ui screen map -> Ships
  (FLEET)", "ui fleet select row 0", "ui fleet deselect (was row 0)",
  "ui fleet scroll down 1"/"up 0"; zero laser01 (t404 law). NATIVE VISION
  GRADE of fleet-rows.png: header "Player (1 Ship, 1 more allowed)" (singular
  legs correct), green name "Ship" x~159, cyan 2-line "In Starlane to Icarus
  System / ETA - 1 Day", green selection marker at row left, arrow boxes,
  "Esc: return to galaxy" footer. NOT empty — D13 ships-screen symptom FIXED
  for the in-transit case.
F12 TIMING LAW (probe over real buildCampaign, seed 5): Shipyard queued t198,
  FIRST ship in transit between t278/t279, colonises t280, player extinct
  t286 (hops=1 whole game). The witness lands the one-turn window by
  deterministic NEXTTURN count — no injected state. Fleet is ONLY ever
  in-transit in the model (named seam (b) stands).
F13 MUTATION CAMPAIGN NOT RUN — honest negative. scripts/t407_mutate.sh has a
  cwd bug (relative paths after `cd rewrite/build`: mutants no-op'd, M5/M6
  "SURVIVED" are VACUOUS, sources untouched — suite re-verified 368/0 green).
  t408/9 MUST re-run mutation from repo root with absolute-ish paths before
  claiming pin strength. Pins are currently UN-MUTATED (green but unproven).
NAMED SEAMS unchanged (a)-(e) above. NO OQ ROW CLOSED (strict-close; ships
chrome has no OQ owner — same honest negative as t405/t406).
