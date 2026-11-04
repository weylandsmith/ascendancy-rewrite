# t298 WIP — LIVE move-order witness #2 (fixed picker, correct gates)

Session start 2026-11-04 ~16:10 EST. Fresh session; resumed from STATE.md alone.

## Pre-flight (verified this session)
- Tree clean; production :9 alive (dosbox pid 1957), ring rows pinned t=1086
  through wall 15:47 => NO new sitting => r1_t85g_sitting.py NOT required.
- t297 run rings re-read: owner-0 fleet at t=1086 = 11 ships kinds {3,5}
  (NO kind-4); at t=1087 slot 8 = kind 4 MOVES=12 (owner 0, design 12).
  owner-0 slot indices [3,5,7,8,16,18,22,24,25,26,27] -> slot 8 is the 4th
  player ship in array order.
- Ship record +0x2c = ASCII ship name ("Enterprise B" seen at rec8+0x2c) —
  NAME-based fleet-row identification possible.

## T298-A. POINTER-VALUE COORDINATE LAW (MEASURED, code-relocation cross-check)
The t297-B negative "batwin instance NOT findable via handler-ptr scan" used
MEMBER-coordinate values. Measured on t297 save 48 (system view, t=1086,
B=0x1bf4d8):
- Code immediates in RAM are relocated to GUEST-PHYSICAL: dumping the
  immediate-free anchor 8b9eb300000039d8752a84ed7526b90100 0000 at member
  0x1daf64 shows `mov dl,BYTE ds:0x7458e` carrying imm 0x2b658e =
  0x7458e+0x242000; `mov ds:0x43508,eax` imm 0x285508; game obj 0x7a35c ->
  0x2bc35c; hit-test 0x78638 -> 0x2ba638. So data-segment scalar X lives at
  physical X+0x242000 == member X+0x242088 == B+OFF+X (B+0x82bb0=0x242088 for
  this run) — t297-A's scalar law CONFIRMED correct (member coords).
- POINTER VALUES stored in RAM are physical: value v -> read target at
  member index v+0x88. Proof: ds:0x43504 (member B+OFF+0x43504) holds
  0x256825; mem[0x256825+0x88+0x1c] reads "Icarus" (a star name) — the value
  is a star-record address in physical coords. Searching for member-value
  0x2568ad finds nothing; searching (member-0x88) finds it.
- Consequence RE-TESTED: handler 0x1aef8 as physical value (B+0x1aef8-0x88)
  has exactly ONE hit in RAM: member 0x247978 (a data structure, NOT the
  payload-image copy t297 found with the wrong pattern) — the
  t297-B "zero u32 refs" negative is REFUTED for the physical convention.
  Ship-record pointers likewise found (slot->member hits at 0xfd3ca6,
  0xfd43f3..0xfd4597 (a stride-0x15 table = design/ship index?), 0x26d430,
  0x26ddcc, 0xfe7c0f..0xfe7c5f).
- CLIP POOL (stride-0x35 {u8 kind, u32 objptr}) scan with physical ptrs at
  save 48 (system view open per session log 15:22:01): ZERO hits for
  kind in {2,3}. Either clips are rebuilt per-frame and the autosave caught
  count=0, or the pool lives outside the Memory member. ORACLE UNPROVEN —
  do not build the session on it; keep as opportunistic witness.

## T298-B. BATCON RE-READ (0x1b91c verbatim, disasm lines 8067-8215)
dl = BYTE [[win+0xaf]] = kind of the clip the router hit-test (0x4fb30)
stored for THIS click (not a separate pending field):
- dl==2 (ship clip) @0x1b9f6: SELECT iff [win+0xb7]==0 (mode 0) + owner +
  MOVES>0 -> [win+0xb3]:=clip, [win+0xb7]:=2. At mode 2 clicking a ship clip
  is a NO-OP (jmp 0x1bb1f) — NOT a deselect.
- dl==1 (empty/space) @0x1ba45: mode==2|3 -> mode:=0 + relay 0x326 ecx=2
  (ship, ecx=2 dest-type); mode==0: if clicked clip==[win+0xb3] && mode==0
  -> PUBLISH leg 0x1ba8c (ds:0x43508:=[[clip+1]], ring code 0x11,
  [win+0xaf]:=-1); else re-copy [win+0xb3]:=[win+0xaf].
- dl==3 (planet clip) @0x1bad3: mode==2 or bh==3 -> relay 0x326 ecx=4,
  mode:=0. ORDER leg.
- Router 0x1b070: hit-test stores [win+0xaf]; NON-NULL -> batcon(ecx=1);
  NULL + mode==2 + [win+0xbc]==0xffff -> mode:=0 (deselect happens only when
  the hit-test found NOTHING).
LIVE ROUTE (sharper than STATE.md's): select ship (click its sprite, mode 0
-> 2), then click a PLANET clip (dl==3 -> relay 0x326 = order to that
planet) or empty space (dl==1 -> relay ecx=2). The 0x1ba8c ds:0x43508+ring
publish leg needs mode==0 + re-click of the SAME clip — reachable only AFTER
an order reset the mode; secondary.
CORRECTION to STATE.md battery rationale: right-click-EMPTY in mode 2 also
takes 0x1ba45 (mode:=0 + relay ecx=2) — same leg as left-click empty; the
button byte is edx=[esp+0x10], NOT consumed by these legs. Battery should
try: ship-select -> planet-click -> (re-select) -> empty-click, watching the
command ring after each.

## T298-C. COMMAND RING INSTRUMENT (measured layout)
Game object member = B+OFF+0x7a35c (verified: widx u16 @ +0x44ac sane,
entries readable; the B+0x7a35c read is garbage code bytes). Entry stride is
10 BYTES (0x56ad4: eax=widx*5, writes [esi+eax*2+0x422c..0x4235]):
{code u16 @+0, param u32 @+2, extra u32 @+6}, cap 0x20 (assert 0x56ae9).
MEASURED t297 run: entry0 evolves 0x1/0x1 -> 0x1/0x11 (t=1086, system view)
-> 0x3 -> 0x7 (post-turn) — ring codes CHURN with turn processing, so ring is
DELTA-only too; a NEW entry appearing right after a click is the signal
(widx [u16 @ +0x44ac] increments per push).
Production ring (no input): entry0 EMPTY (0/0/0) — clean.
ds:0x43508 churn confirmed (0x26fe77->0x26f00d across autosaves, idle map).

## T298-D. SYSTEM-VIEW IDENTITY ORACLE (new)
ds:0x43504 (member B+OFF+0x43504) = current-star/star-context record pointer
(physical coords; +0x88 -> star name at +0x1c: "Icarus" at save 48 = the
system view t297 opened via owner-1 row-1). Constant 0x256825 all t297 run
(their navigation never changed system) — a click battery that NAVIGATES
will move this value; a battery that selects/orders will NOT. Cheap oracle
for "which system am I looking at" + "did the click navigate".

## Session design (r297_order_session.py r2, changes per STATE.md t298 +
these notes)
1. enter_campaign + drain; End Turn ONCE (verified-advance) -> slot 8 kind-4.
2. Target from NEWEST ring rows: owner==0 && kind==4 && MOVES>0 (expect {8}).
3. Fleet-row picker: rows 4/page; click rows y in (93,188,283,378) until
   ds:0x43504 star == slot-8 star (star identity via r1_star_table names or
   the +0x88/+0x1c name read; fallback: nearest-star to slot xyz).
4. Colour-class ship sprite finder (tan/gold R>150 G>110 B<90, exclude
   y<112 icon strip) validated OFFLINE on t297 system-view capture first.
5. Battery: S1 click ship sprite; S2 click planet blob; re-select S3 (click
   ship again is no-op at mode 2 — instead Escape once? NO: mode lives in
   window; plain click on ship clip at mode 2 = no-op per 0x1b9f6 — the
   re-select step is unnecessary); S3 click empty space; S4 right-click
   planet; S5 right-click empty. Witness after EVERY click: kind2 census,
   ds deltas, ring widx+entry0, clip-pool scan, batwin-ptr scan.
6. Escape ladder to map, End Turn x2 + drain, verdict: slot-8 kind 4->2 +
   movement with order evidence (t293 law: the ORDERED slot must move).

## T298-E. FLEET-ROW ROUTE, MEASURED GEOMETRY + RANK LAW
- Row hit-points (validated off t297 10_fleet.png green-name bands y
  52-64/160-170/264-276/372-382, pitch ~104): (200, 93/200/305/413). Row-1
  93 matches t253's measured point exactly.
- FLEETWND lists the PLAYER'S fleet only (header "25 Ships" law) in
  ship-ARRAY order [inferred: t293 row-1 -> slot 1]. Slot 8 = rank 4
  (1-based) among owner-0 [3,5,7,8,...] -> PAGE 1, ROW 4 (y=413).
  Paging = right-rail down arrow (620,453) (t253 scroll pair).
- NEAREST-STAR MATCHING IS INVALID for locating a kind-4 ship: kind-4 xyz is
  SYSTEM-LOCAL (slot 8 t1087 (-352,-2080,-992) is 1911 units from any star;
  exact triple exists only in the ship record). Star grid positions are
  GALAXY-space. ds:0x43504 star name is logged as a system-identity witness
  only, never a picker gate.
- rec8 turn-boundary diff (t297 49->51.sav): +0x58 kind 5->4, +0x5d 01->00,
  +0xa0/+0xa4/+0xa8 position floats — no order-list fields touched without
  an order: raw3060 (name+order region) is a CLEAN delta witness.
- TAN SPRITE CLASS VALIDATED OFFLINE: r>100, r-b>45, r>=g>=b, g-b>12,
  y>=112, bbox<=64, >=60px, exclude >80px planet neighbourhood finds the
  ship at (48,151) in t297 11_orbital.png (vision said (48,148)); planet
  hull (154,121,89-class) mostly excluded by the bbox/planet rules.

## LAUNCH (session 7)
run dir work/r1/t298-order-<stamp>, Xvfb :97, scratch game-wp, venv python,
tl 1500. Launched wall ~16:5x. Production :9 t=1086 untouched (verified
pre-launch: ring tail 54.sav t1086, dosbox pid 1957 only).

## RUN AUTOPSIES (same session)
- RUN 1 (t298-order-FAILED-keyerror-172935): own bug — recs0 keys are INT
  (ring_mem_rows) but I indexed recs0[str(target)] (sample() JSON uses str).
  KeyError AFTER a successful End Turn (t=1087 reached, cand=[8] correct).
  ~80 s of boot burned; fixed, renamed dir.
- RUN 2 (t298-run2-swallowed-popup): End Turn OK (t=1086->1087 press 1),
  cand=[8] correct, but the POST-TURN CONSTRUCTION POPUP (EVENTWIN "Industrial
  Megafacility complete on Cornicob I") swallowed EVERY later click: FLEET
  diff 216, row-jump diff 184, star stayed 'Icarus'. ROOT CAUSE: r293
  drain_popups() uses the white-TEXT detector which is BLIND to the
  light-background EVENTWIN (t293 banked this law — I re-broke it). FIX LANDED
  run #3: close_eventwin() after every End Turn + hard gate before the fleet
  route + FLEET-click retry (close, click again) + drop the useless rails>=6
  condition (blue rails read 170 even with the popup up — sidebar chrome).
  LAW RESTATED: after ANY turn advance, close_eventwin() BEFORE any click
  that must land; popup_ok_center() only catches dark popups with white text.
- RUN 3 (t298-order-20261104-174236, FULL BATTERY, rc=1 honest): route
  reached the system view and the battery ran clean (no title ejects,
  EVENTWIN guards worked, End Turn x2 landed t1087->1089). NEGATIVE: no
  kind-2, no tgt_raw3060 delta, no attributable movement. BUT the negative
  is a HARNESS negative, not a route refutation — two own-bugs:
  (a) FLEET-LIST ORDER IS NOT SHIP-ARRAY ORDER (MEASURED, vision on run-3
      23_fleet.png: rows top->bottom Sparrowhawk/Erebor/Erchamion/Ignatz =
      slots 18/7/16/22 — row 4 was Ignatz (slot 22, kind 5, IN STARLANE),
      not Enterprise B. The rank->page math was built on a false law.
      Sorting law of the list: UNKNOWN (S,E,E,I is neither name order nor
      kind order nor array order).
  (b) my tan finder had NO x-bounds: every "sprite" it returned (597,140),
      (612,259), (576,300)... was SIDEBAR CHROME (x>466, outside BatModeWnd
      client rect 7..465). Re-run offline WITH x<=465 bounds on the SAME
      screenshot: client-rect tan comps = two tiny blobs (72px @ (24,317),
      70px @ (25,314)) = station art; NO ship-sized tan sprite exists in
      the Icarus system view. Enterprise B was not in that view (wrong row).
  (c) ship_array_law count=30 UNDERCOUNTS: named owner-0 records live at
      indices 31/32/33 too (Eregion B, Ereinion B, Escutcheon B) — 14 named
      owner-0 records == the FLEET header "14 Ships" exactly. The count
      word (0x43489>>16=30) is stale/partial; any picker must scan to
      n>=52 or match the header count. (Banked law, check r1_slot.py users.)
  (d) COMMAND RING churns entry0 even from non-order activity in a scratch
      session (baseline [[7,0,0]] -> [[1,18,1]] after an EMPTY right-click;
      [[5,0,1]] later). Ring codes 1/3/5 with small-int params — NOT the
      0x11/pointer shape the publish leg writes. Ring is NOT an order oracle
      at this granularity; kind-2 census + raw3060 remain the witnesses.
VERDICT: mouse route NOT refuted, but two more blind-guess launches are a
worse bet than the instrument that ends guessing. t299 = DEBUGGER WITNESS
(BPLM on the exact legs; t290/t292 precedent, master-built dosbox-x):
  0x1ba39  SELECT success ([win+0xb7]:=2)      <- did a click EVER select?
  0x1ba5e  dl==1 mode2/3 order relay leg
  0x1baa7  PUBLISH (ds:0x43508 := dest + ring 0x11)
  0x1bad3  dl==3 planet order leg (relay 0x326 ecx=4)
  0x1b114  mode-2 DESELECT
Hits + registers + [ebp+0xab] clip + [[clip+1]] object answer every open
sub-question in ONE launch, including which fleet-row click lands where
(BPPM/BPLM on the row handler once known) and what clip the hit-test
returns for a given pixel.
