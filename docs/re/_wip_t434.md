# t434 WIP — SHIPS SCREEN CYCLE (PHASE-16 row, re-tagged)

## F0 PREMISE + CONTROL PLANE (read this session)
- Assignment: docs/STATE.md NEXT ACTION t434 (queue row STATE.md:2523-2526):
  "full pass — derive the fleet list paint (fleetlist law banked t402 era;
  grade it against vendor now), row art (ship class sprites), selection/info
  panel, per close law."
- No new play data: work/r1/playcap/live-timeline.jsonl mtime 2026-11-12
  06:45 predates the t424b landing -> no re-sitting, assignment stands.
- REFUTED-ROUTES consulted: t298 (fleet-row-by-array-rank nav DEAD),
  t314 amendment (digit-key under FLEET focus DEAD; rowjump click (200,93)
  CLOSES the window law), t316/317 (STATSHIPLST msg paths). None bind a
  rewrite-side derive-from-RE paint pass.
- INHERITED: t407 landed the fleetlist laws + pins (docs/re/fleet-screen.md
  F0-F13): header #152, location #143/#146 (fn 0x50d12), geometry ROWS TOP 52
  PITCH 106 x4 rows (work/screens/t253/fleet_open_game.png), arrows x606..635.
  Row ART was never derived — t407 F6 census saw a "blue-sphere column"
  x358..382 (planet sprite, fn 0x50d12 ORBIT case) and a "chevron chain
  x270..323" that is UNEXPLAINED. That is the derive target.
- windows.txt: FLEETWND TYPE 17 rect 7,7-632,472 SHAPEFRAME 0; STATSHIPLST
  TYPE 10 child rect 7,46-632,472 SHAPEFRAME 7; NO TYPE-100 SHAPEFILE binds
  state 18 -> the ships-screen chrome is CODE-DRAWN like status/planet
  (precedent t417/t428).
## F1 FLEET PAINT FAMILY CLOSED [verified asm work/t434_fleetwin.asm =
r331_disasm 0x50d12..0x516ff + runtime census]: fn 0x50d12 IS THE FLEET
NAME/ART PAINTER (status.cpp family; the assert string "..\\status.cpp" sits
at payload 0x85699 right beside the "DATA\\planets.shp" string 0x85688 the
same fn references). FOUR blits + THREE text draws, all into a 20-entry
shape-item list (stride 0xe, same composition grammar as the t427 planets
row 0x500e0 and the generic vtable painter 0x32314):
  (i) 0x50d28 NAME-ART: cache 0x9f10c, SLOT GLOBAL WORD ds:0x895c2, record
      IMMEDIATE 0x41=65, colour = game.pal[racebyte*4+0x13] (race row +0x1,
      stride 0x1ee — the t415/t412 ink law VERBATIM, 0x50d50..0x50d77),
      SELECTED OVERRIDE edi!=0 -> 0xf3 = pal[243] WHITE (0x50d86) — THE
      FLEET SELECTION LAW IS TEXT/ART COLOUR, THE t427 PLANETS-ROW LAW
      EXACTLY (white selected, race ink unselected).
  (ii) ORBIT case (kind 1, 0x50db2..0x50e13): PLANET SPRITE planets.shp
      (slot global WORD ds:0x895c6), record selector 5*TYPE+SIZE
      (ecx=WORD[planet+0x16] type; eax=4*ecx+ecx+ebx(size); t427 law AGAIN,
      third independent consumer), blit 0x5caac args (p3=0x31 font,
      x=selector, y=0x24e).
  (iii) LANE case (kind 2 tail 0x51061..0x510ca): slot global WORD ds:0x6a14
      (a FOURTH slot global, ZERO code refs besides this read — the t427-A
      same-shape vendor defect; slot identity UNNAMED = named seam), record
      = [starRec+0] (the star's own index), args (0, 0x24e, selector).
  (iv) NAME TEXT: static #144 (0x90) at (0x17c=380, 0x96=150) + record 0x103
      composite; the design-name string law (rec+0x34 hull-name copy,
      SKIPPED for player-designed ships -> design name; fleet-screen.md F2 +
      t379 death witness 'Medium'@+0x34) — confirms t407 F6: row name is the
      DESIGN name, not the hull class.
RUNTIME WITNESS [measured, pointer-law B + cache-name-table law shp.md
(ctx+0x7d0+idx*0x32, ctx found by the verbatim 'DATA\planets.shp' string)]:
32/32 in-game saves (FLEET opened, 0x895c2!=0xffff): slot 14 name =
'DATA\SMSHIP19.SHP', slot 29 = 'ata\planets.shp', 32 = 'ata\raceflag.shp',
52 = 'ata\suns.shp' (29/32/52 re-confirm the t427 banked slots). => THE
FLEET ROW-ART LIBRARY SLOT HOLDS THE PLAYER-RACE smship LIB (race 19 =
player species in those saves; preload cluster t415 loads
DATA\SMSHIP%02d.SHP per race). 148/180 run slots hold 0xffff = pre-open.
REFUTED PREMISE: t407 F4's "row art = honestly-vector DECISIVE (no 18*.shp)"
was HALF right — no 18*.shp exists, but row art EXISTS: the race smship lib
record 65. (t391/t407 keep-honour: they only ever censused 18*.shp.)

## F2 BLIT ARG SHAPE + UNRESOLVED ARG-OFFSET SEAM [verified pushes vs
t428d arg law (y,x,rec)]
  * NAME/ART blit 0x50d39: pushes $0x32(y=50), $0x41(x=65), then
    edx = BYTE_HI([ship+0xa7]) (0x50d3b..0x50d46: mov edx,[esi+0xa7];
    sar 0x18) => record = the ship record's +0xa7 high byte = SHIP CLASS
    SPRITE SELECTOR (the row-art the task names). smship libs carry EXACTLY
    4 records [measured: every extracted smshipNN.shp count=4] => class
    selector domain 0..3 = hull size class. Colour var [esp+0x154] =
    pal[racebyte*4+0x13], OVERRIDE 0xf3 when edi (selected) != 0.
  * ORBIT blit 0x50def: pushes $0x31, $0x24e, rec=5*TYPE+SIZE. x-immediate
    0x24e=590 does NOT match the measured sphere column x358..382 => the
    0x5caac composition (x = p4 + struct[+4] + payload-rect, t428e law)
    carries the correction; PORT USES THE MEASURED t407 F6 ANCHORS and the
    arg-offset stays a NAMED SEAM (do not "fix" geometry from immediates).
  * GIZMO-ICON LOOP 0x51415..0x515a3: EIGHT stride-0xe icon items, counts
    from ship fields +0x88/+0x8c/+0x98, slot global spilled from the fn
    head, record selector per item; x += 0xe, bar width 0x66-ish scaled by
    count/idiv (0x5150d imul 0x62, idiv). = the small icon ROWS under the
    name (red starburst / shield / gold-bar strips in the t253 shot). NOT
    ported this cycle (needs the ship gizmo inventory the port lacks) ->
    CONT cycle-2 item, named seam.
  * 9-iteration chain loop 0x5126b..0x51340 (selector HIWORD[ship+0x54],
    slot global ds:0x6fd8a, x += 9) = the green CHEVRON pips x270..323.
    Slot identity unnamed (zero writers in the disasm window like t427-A).
## F3 RUNTIME WITNESS CORRECTION + FINAL SLOT LAW
32/32 fleet-open saves: 0x895c2 = 14 and cache ctx 0x2e1194 slot 14 name
= 'DATA\SMSHIP19.SHP' [measured; ctx located by the verbatim
'DATA\planets.shp' string at slot 29; slots 29/32/52 = planets/raceflag/
suns RE-CONFIRM the t427 banked numbers]. All those runs are ONE run
family (same B, same race) — so the slot is the preload-cluster slot of
the PLAYER race's smship lib (race 19 in the witnessed saves; the t253
shot header reads Chamachies). Writer of 0x895c2: ZERO direct writers in
r331_disasm (same t427-A/B family: slot globals written by a generic
resolver); the slot VALUE law is witnessed, the per-race mapping is
[INFERRED] from the preload string law (t415: DATA\SMSHIP%02d.SHP pool
0x8372C loaded per race). Port: load smship<playerSpecies>.shp from the
extracted data dir DIRECTLY (no cache-slot simulation), record selector =
documented default 0 (the port has ONE design; class-field law cited but
the model carries no per-ship class field — t256c boundary), named seam.
## F4 SELECTION LAW (the gradeable defect fix this cycle)
Vendor fleet row: name+art colour = pal[racebyte*4+0x13] UNSELECTED,
pal[243] WHITE SELECTED (0x50d77/0x50d86 cited; t427 planets-row law
VERBATIM, second screen). Port today: fixed green (0,230,90) + synthetic
green marker bar + synthetic navy row frame. t253 native-vision grade:
NO row frames anywhere (pure black field), no marker glyph — the t407
frame/marker are PORT INVENTIONS. LANDED: ink law + white selection,
frame+marker DELETED, ship sprite column smship<race> rec 0 at the
measured art anchors (x10, row top).

## F5 ROW-ART IDENTITY HONEST NEGATIVE + SELECTION MEASURED (t253 pixels)
* MEASURED [numpy t253]: sprite bbox row0 x27..121 y71..112 (95x42, 2414
  px); row1 name band WHITE 48 px vs rows0/2/3 green (0,170,82) — the
  SELECTED ROW IS ROW 1 (Erebor) and the selection is TEXT COLOUR, exactly
  the 0x50d86 law; NO row frames ANYWHERE (t407's navy frame + green marker
  bar are port inventions — DELETE). Unselected ink (0,170,82) ==
  chromePaletteArgb(byte*4+0x13) for Chamachies static byte kIntroRaceBytes
  [19]=0 -> pal[19] (t424b witnessed pal[19] = (56,170,85)-class green) —
  the law and the pixels AGREE.
* ROW-ART LIB/RECORD NOT RESOLVED: the blit site 0x50d39 reads slot global
  ds:0x895c2 (zero writers in the disasm, t427-A family) + record
  [ship+0xa7]>>>24; the cache slot WITNESSED (32/32 saves, ctx 0x2e1194
  name table) is 'DATA\SMSHIP19.SHP' — but smship libs carry 4 records
  (dims 32x9/49x15/49x17/67x22 [measured]) and record immediate 0x41=65
  cannot exist in a 4-record lib; dkship = 314x222; the DRAWN sprite is
  95x42. => the fleet row render is NOT one of these records as-is
  [measured dims disagree]; per-design composite (hull+gizmo) or a
  different-slot stretch remains OPEN with named evidence gaps. PORT DOES
  NOT DRAW FAKE SHIP ART (D17 law (1)); the art column stays the named
  seam, closer = debugger BPPM/BPLM at 0x50d49 (cache arg) — QUEUABLE.
## F6 LANDED THIS CYCLE (cited law -> code)
fleetlist.{h,cpp}: fleetRowPalIndex(selected, raceByte) pure law
(selected ? 0xf3 : raceByte*4+0x13, cites 0x50d77/0x50d86); ui.cpp fleet
rows: NAME + LOCATION drawn with chromePaletteArgb(fleetRowPalIndex(...))
(was fixed green name + FIXED CYAN location — location colour was WRONG,
t253 loc band measured green); synthetic navy row frame DELETED, synthetic
green marker bar DELETED (witness F5). Pins test_fleetlist_t434.cpp.

## F6 LANDED THIS ITERATION (build+tests real, witness PENDING)
* IMPLEMENTED [rewrite]: fleetRowPalIndex(selected, raceByte) in
  ui/fleetlist.h (selected -> 0xf3; else byte*4+0x13, byte-masked);
  ui.cpp row paint now uses it for NAME and LOCATION (cyan defect removed);
  synthetic navy frame + green marker DELETED (t253 census: vendor has
  neither). Tests: tests/test_fleetlist_t434.cpp (3 pins: byte*4+0x13 law
  incl. truncation, selected-white unconditional, witness legs specnum19/0
  -> pal[0x13] + non-alias). BUILD clean; run_tests 457/457 (was 454).
* PENDING [next session]: scripts/t434_witness_census.py exists but has NOT
  been run yet (needs OUT=/tmp/t434_shots bash scripts/t407_fleetlist_witness.sh
  then python3 scripts/t434_witness_census.py /tmp/t434_shots/fleet-rows.png).
  It censuses green-family ink, zero-cyan, white-on-selected, no navy frame.
* ROW ART (sprite column x27..122): identity NOT closed this iteration —
  honest negative stands in F5; smship/dkship TOC probes inconclusive on
  which library the row art blits from. OQ row STAYS OPEN.
