# t369 census-tool bank — USER PLAY-TEST 2026-11-10 evening (scribe: assistant)

## USER TESTIMONY (verbatim, 2026-11-10) — PLAYER TESTIMONY = HYPOTHESIS
"I'll try to do a test tonight on that if you want to observe it. My day
1300-somethign save has ships with that gizmo."
"There are kind of two paradigms that govern ship movement - you select a
ship, and if you click on an actionable object (planet, star link, or another
ship if you've got a targetable gizmo selection), it will move or do the
action of the gizmo. If you just click on empty space, it takes two clicks to
select a destination in 3d space - the first click sets x/y coordinates, and
the second click selects z coordinates."

## WHY THIS MATTERS (re-open, do NOT re-litigate the old routes)
The two-click empty-space destination = the msg-0x50 destination-widget
mechanism classed UNREACHABLE-BY-CAPTURE (t319-t324 chain, OQ-019 residue
(1)). Player testimony says a HUMAN uses it routinely. The cited-dead chain
covers synthetic-pump, synthetic-in-view-mouse, static activation census, and
RAM class table — it does NOT cover a real hand on a banking game. Testimony
does not override the citations; a WITNESS from tonight does: if the ring
diffs show a ship order with an off-lane z component set by two clicks, the
residue re-opens measurement-wise (R13-clean: RAM evidence, not pixels).

## EXPECTED SIGNATURES (tools to build, in priority order)
1. MAGNETRON LANDING: use-site law ships.md S19 T3 — placement via
   FUN_000220a8 + kind-5 handler FUN_00021f58: star coords + (0,-200,0) +
   rng%200 on x/z (jitter const -200.0 live @B+0x82bb0+0xaee). Census K3b
   (scripts/r265_*): any st4 row off-grid in x OR z = hit (P(false neg) <
   0.1%). Extend over the NEW session window only (fast). Also ring-diff:
   gizmo charges byte decrement (upkeep law FUN_0004a658, bit0) + kind 5->4
   transition on one ship row.
2. DESTINATION ORDERS: per-turn ring diff of ship-record order fields
   (pership-spec.md S2 enum); testimony predicts a NEW order kind (or
   existing kind with arbitrary z) appears for empty-space targets, set in
   TWO steps across clicks. Diff consecutive .sav slots in the play window;
   attribute by ship index (t273 owner law).
3. GIZMO-ON-TARGET actions: kind-2 target path into FUN_0004ca50 (case per
   gizmo id, ships.md S19 table). Decrement + effect witnesses.

## SESSION FACTS
- Production relaunched 2026-11-10 ~11:24 pid 107664, TL=604800 (expiry
  2026-11-17 11:24) so the user's night session cannot be guard-killed.
- Ring banked pre-play: work/r1/bank-t1086-preplay/ (20 slots, t1086).
- User drops day-1300 .SAV into work/r1/game/ and loads in-game; VNC from
  main PC via ssh -L 5910:127.0.0.1:5910 -> localhost:5910.
- Watcher banking continuously (single writer). Witness window = first mtime
  change of work/r1/game/*.SAV / RESUME.GAM, or first timeline turn != 1086.
- Baselines at authoring: RESUME.GAM mtime 2026-11-02 21:46:09.004; timeline
  8,931,163,683 B; game dir has 01/02/04.SAV.
- OQ-016/OQ-019 acceptance + D3: user explicitly DEFERRED pending test
  results. Do NOT apply _wip_t329 S4 yet.
