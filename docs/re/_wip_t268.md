# _wip t268 — LIVE SCREEN SWEEP 3: NEGSCREEN flow + intel detail + tech tree detail

Pre-flight (05:22): r1_game_health.py RC=0 HEALTHY (game pid 535172 verified,
watcher 535187, ring 48.sav age 3 s, TL expiry 07:03:58). No warning windows
(xwininfo -root -tree | grep -i warning empty). Game window 0xc00009
640x480+80+100. Harness scripts/r1_t268_screen.py (t253 primitive, OUT ->
work/screens/t268/). Baseline shot: galaxy screen, ring turn 1236, in_game True.

NOTE: ring turn 1236 < t252/t253's 1255 — the relaunched production game
resumed t1086 and is AUTOPLAYING (turn advances between iterations). Turn
"drift" reported by the harness during this sweep is autoplay, not my clicks;
safety = I never click NEXTTURN (511,67) and never click war/propose rows.

SAFETY LAW (task): NEVER click PROPOSE/DECLARE/ABANDON/END-TURN. NEGSCREEN
option rows: only the Goodbye-equivalent row is clickable, and ONLY from a
per-sweep MEASURED band (posture may have changed since t252 — the option set
is posture-dependent, so the t252 band map is NOT trusted; re-read the actual
rendered rows via vision BEFORE any row click). Escape unwinds one level.

COORD LAW: xsend click coords are ROOT coords (window origin +80,+100); game
coord (gx,gy) -> root (gx+80, gy+100).

PLAN (screen -> dossier-level reads):
1. Species menu (RACES 553,301 root) -> race rows.
2. Race row -> NEGSCREEN: read alien dialogue line verbatim; read FULL option
   list verbatim; capture header/third-party region (y 40-206, t252 said
   "image content" — check for a control/intel readout).
3. Close via Goodbye-row (measured band) or Escape chain.
4. Intelligence screen -> click a race row -> does a detail view exist?
   (t252 only did the list). Measure columns/flags precisely.
5. RESWIN -> click tech nodes -> dossier panel content (name, days, Allows
   list); use pan arrows; measure what changes per node click (pixel-diff +
   read panel).

LEDGER TARGET: none expected to close (strict-close); annotate OQ-023
(negotiation flow = relation-posture driven UI) and OQ-005 (SHAPEFILE leads)
only with cited measurements.

## NEGSCREEN dossier (measured 05:2x, turn 1236 held)
- Species-menu race-row click law: rows are TEXT lines at game y ~73 (Orfa),
  ~140 (Ungooma), ~207 (Extinct); click at (553,173) BETWEEN rows did NOTHING
  (164 px blink); (553,73) on the Orfa text opened NEGSCREEN (197733 px).
  => race-row hit target is the text line, not a full-height band.
- NEGSCREEN Orfa at PEACE-ish posture rendered FIVE option rows (t252 saw
  THREE — posture/campaign-dependent list re-confirmed across campaigns).
  PLAYERDIP bright-text bands MEASURED: 329-339, 361-367, 390-396, 416-425,
  446-454 (~29 px pitch). ALIENDIP = single text band 252-261.
- DIALOGUE PROVENANCE EXACT: alien line "Uh oh.  What's wrong now?" ==
  race02.dip:172 (DR_NoDipResponse, Orfa; file header "Diplomacy text for
  Orfa"). Player rows verbatim player.dip DA_* strings: DA_NoDipAction
  (Goodbye, line 67), DA_DeclareWar (31), DA_ProposeAlliance (34),
  DA_TradeStarlanes (37), DA_TradeStars (40). NOT rendered this posture:
  DA_TradeResearch, DA_OfferPeace, DA_BreakAlliance, all %t third-party
  actions. Rendered order == player.dip ACTIONS file order MINUS filtered
  rows (Goodbye last in file but FIRST rendered — ordering law: Goodbye is
  hoisted to row 1).
- player.dip DIPVALUES block captured verbatim (DECLARE_WAR 70, ACCEPT_PEACE
  100, PROPOSE_PEACE 150, BREAK_ALLIANCE 170, ACCEPT_ALLIANCE 200,
  PROPOSE_ALLIANCE 250, START_ATTITUDE 100, SHIP_PATIENCE 100) — note
  ACCEPT_ALLIANCE 200 vs the LIVE-table 570 used in t189b: player.dip values
  are the base/default table, race files override (race02 Orfa 570 per
  diplomacy.md). Third-party region (y 40-206) = race art art (Orfa creature
  volcanic scene, 13NEGOT.SHP lead stands).

## Goodbye + INTELLIGENCE dossier (turn 1236 held)
- Goodbye row click (480,334 = measured band 329-339) CLOSED negotiation and
  returned DIRECTLY to the species menu (diff vs races_game = 202 px blink).
  DA_NoDipAction closes the flow without an alien reply screen.
- INTELSCREEN (this campaign, t1236): header "Chamachies Intelligence";
  columns Fleet/Colonies/Discoveries; rows Chamachies 10/12/4, Ungooma
  10/6/4, Orfa 8/6/4 [vision-read symbol counts, UNVERIFIED per R13 — the
  t252 campaign read 10/12/6, 8/8/4, 6/6/5: values differ per campaign,
  symbols are relative-magnitude per help intscr]. Self row present.
  Relation-flag icons at row right (colors noted, semantics unmapped).
- NEGATIVE (measured): clicking a race row on INTELSCREEN (230,370) changed
  204 px == blink floor -> NO intel detail view exists behind the rows;
  manifest-level IS the terminal intel depth. No buttons/tabs on the screen
  (vision). Escape unwinds intel -> species menu.

## RESWIN dossier-level detail (turn 1236 held; ONE state change, see SAFETY)
- OPEN STATE: panel EMPTY, no gold ring anywhere (this campaign had NO current
  project at t1236; contrast t252 which showed "Current Project: Accel Energy
  Replenishment (15 days)" immediately on open). 7 nodes visible: filled disks
  (pictures) + empty rings; one node red-ringed at (362,462).
- CLICK LAW MEASURED (help reswin verbatim: "click on an empty disk to make it
  your current topic of study"): clicked empty disk (72,327) -> panel
  "Repulsion Beam Tech / (33 days) / Allows: Fleet Disperser" + 900 px change
  CONFINED to the clicked disk bbox (41-100, 299-358; other nodes 0 px), no
  popup. => SET-TOPIC is one-click, no confirm dialog, and the selection
  highlight draws ON the disk. STATE CHANGE: this game now has Repulsion Beam
  Tech as study topic (was: none). Not revertible in-game (no cancel-research
  control); honest note, autoplay campaign only.
- DISCOVERED-DISK CLICK = dossier read, no state change: (213,88) -> panel
  "Energy Focusing / Allows Myrmidonic Carbonizer, Accutron" (no days line).
  Red-ringed filled node (362,462) -> "Megagraph Theory / Allows / Internet"
  (no days line). Days line appears ONLY for the current topic (in-progress).
- ALLOWS LAW PROVEN 3/3 AGAINST FILES [verified]: restree.txt row N -> tech
  index N-3 (rows 3..66 = idx 0..63). Energy^Focusing row 42 = idx 39; gizmos
  Myrmidonic^Carbonizer (gizmos.txt:230) 9th field 39 AND Accutron (:260) 9th
  field 39 -> exactly the two Allows rows rendered. Repulsion^Beam^Tech row 45
  = idx 42; gizmos Fleet^Disperser (:209) 9th field 42 -> rendered. Megagraph
  row 62 = idx 59; planitem Internet (planitem.txt:100) field 59 -> rendered.
  => RESWIN Allows list = REVERSE JOIN {gizmo/planitem records whose tech
  field == clicked tech idx}; restree's own trailing numbers are PREREQS
  (research.md), not Allows. Rewrite impact: campaign.cpp tech unlock display
  can derive Allows without new data.
- DAYS LAW DATA POINT (not a law): Repulsion cost 110 -> "(33 days)"; t252
  Accel cost 120 -> "(15 days)": days NOT a function of cost alone (rate
  dependent). Do not derive from n=2.
