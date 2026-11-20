# t439 WIP — GAME-RING RECOVERY (relaunch vs park)

## F0 Assignment (from docs/STATE.md t438 handoff)
Task: recover the production playcap game. Steps: (1) bank ring [DONE at t438],
(2) decide relaunch vs park per BLOCKED.md SOP and relaunch, record pid,
verify a NEW ring slot banks within ~30 s, (3) if the relaunch softlocks or the
title resume path fails: do NOT open a crash investigation (t277 law) — bank,
record under the sentinel park log, land parked.

## F1 Pre-flight census (all measured this session, 2026-11-20)
- work/r1/loop/GAME_DEAD.txt 2026-11-20 11:54:50: `G:DEATH(pid 107664 gone,
  zero harness dosbox-x in /proc); W:NOWATCHER(feed not banking);
  F:FEED-STALE(newest slot 60.sav 516078s old > 60s)`.
- Structured /proc census (basename(argv[0])=='dosbox-x', kill-law compliant):
  ZERO dosbox-x processes. Xvfb :9 alive (pid 444917); no x11vnc pidfile match,
  no live TCP clients on :5910 (ss -tn empty) => no human VNC client attached.
- DEATH CAUSE = TL EXPIRY, not a crash. Witness: last lines of
  work/r1/vnc/dosbox.log = `LOG: Active save slot: 1 [Empty]` then
  `X connection to :9 broken` — the t277 golden farewell signature; TL expiry
  was 2026-11-11 01:07 and the ring froze Nov 14 12:33. Per t277 law: NO crash
  investigation.
- Ring bank verified present, NOT re-copied: work/r1/bank-t438-ring-2200 =
  20 slots / 43M.
- LIVE RING STATE (scripts/t368_ring_turn.py, read-only, 20/20 parsed):
  ALL 20 slots 41..60 turn=1254. So the last live campaign state was turn 1254.
- VENDOR SAVE STATE: work/r1/game/RESUME.GAM md5
  5b382afbb789186c3654f3cec085b2e2 == the documented UNTOUCHED witness
  (docs/re/driver-selfharm-t285.md:80, docs/re/diplomacy.md:836). RESUME.GAM
  mtime Nov 2 21:46; it is the Oct-29 t1086 world.
  => t259 LAW RESTATED WITH NUMBERS: the 168 turns played since Oct-29
  (1086 -> 1254) live ONLY in dosbox Memory ring slots (evidence), never in
  RESUME.GAM. Title resume therefore returns the Oct-29 world, NOT turn 1254.
  No in-game Save was ever issued by the drivers (drive scripts click NEXTTURN,
  they never save).

## F2 Decision: RELAUNCH (not park)
Reasons, each tied to a fact above:
1. Bank is verified on disk, so recovery cannot destroy evidence.
2. No human VNC client attached (ss -tn empty) — the SOP's pre-relaunch gate.
3. Death is a scheduled TL expiry, so the environment is known-good; a relaunch
   is a restart, not a gamble.
4. Every remaining machine-closable capture route (OQ-016 Phase-Bomb nuke law,
   OQ-019 sugar-cube session via scripts/r297_order_session.py, OQ-027(a) heap
   tune-table) requires a live process; the corpus route is refuted x3
   (t49/t58/t265). Parking buys nothing.
Launch used verbatim: `bash scripts/r1_playcap_vnc.sh start` (defaults
TL=172800, output=x11 under Xvfb :9, scratch work/r1/game, ring 41-60, single
writer). Harness output: `harness: reusing display :9`, `reaper: 0 watcher(s)`,
`harness: BRINGUP OK (ring row landed within 30 s: 41.sav)`.

## F3-F7 (concluded; full text banked to the durable docs)
- F3 bring-up verification (pid 1182156, TL 2026-11-22 12:02:26, ring age 1 s)
  and F5 resume to the map at turn 1086: docs/re/selfplay.md
  "GAME-RING RECOVERY LAW (t439)".
- F4 window-origin drift (measured `640x480+192+184`; r287_title_nav.py's
  hard-coded +80/+100 crop misread the highlight as NONE/0.49 while the real
  row was Tutorial): docs/re/selfplay.md "WINDOW-ORIGIN DRIFT".
- F6 keys vs pointers over RFB (both key channels failed on the focus-less
  restart; positional XTEST click worked): docs/re/selfplay.md.
- F7 GATE RED -> ROOT FIX: relaunch rotated the live ring, invalidating
  rewrite/tests/test_observer_t382.cpp's scalar witness (5 fails, day
  1254->1086). Repointed at the frozen bank via kWitnessSave; 466/0.
  docs/re/r1-savestate.md "PIN A BANK, NEVER THE LIVE RING".
- F8 R-t439 written to docs/REFUTED-ROUTES.md: the pre-death turn-1254 state is
  unrecoverable; do not spend an iteration trying.
- LEDGER: no row closed (recovery measures nothing). OQ-027(a) is t440's target.
