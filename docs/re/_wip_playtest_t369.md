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


## WITNESSES CAPTURED (assistant manual pass 2026-11-11 ~00:45; t370 MUST
## re-run the t369 tools over this window and land the MEASURED blocks)
Window: turn 1253, wall 00:02:09 -> 00:39:11 (frames per file_mtime_ns,
dedup by (file,mtime_ns); 225 frames). Session = USER day-1253 save,
turn NOT yet ended at capture time — orders are PLACED, effects pending.
Slot attribution via ship_raw words[26:] (record +0x34 name law, spec S1):
- slot 28 GUANDAGNINI (owner 0, design 12): frame-to-frame SINGLE delta
  (-1184,1344,-1184) -> (1280,-1760,1344) at wall 00:13:50; d=(+2464,
  -3104,+2528) = 77/97/79 x grid-32. INSTANT multi-thousand-unit jump =
  MAGNETRON USE WITNESSED (first runtime witness ever; corpus zero-census
  ships.md S24 item 4). Record diff across the jump (00:05:31->00:46:21
  bracket, 11 words): +0x88 90->80 (POWER burn 10 — matches gizmos.txt
  Lane^Magnetron power field), +0x8c 40->39 (CHARGES -1 — NumUses law),
  +0x58 kind byte LOW stays 4, high byte 0x45->0x85; +0x5c 256->0;
  +0xa0/a4/a8 pointer churn; +0x10c 15360->65280, +0x10e 1->0.
  PUZZLE for t370: landing (1280,-1760,1344) is ON the 32-grid, but the
  use-site law S19 T3 predicts rng%200 jitter (not a multiple of 32).
  Resolve: watcher xyz field quantized? placement quantized after jitter?
  or this delta includes a later march step? K3b off-grid test returned
  zero hits tonight BY CONSTRUCTION if the field is quantized — amend the
  instrument if so.
- slot 38 ILMARINEN (owner 0, design 12): st4 -> st5 at 00:21:21 to
  (0,0,-2144) = star-plane x/y==0 + deep z = LANE-ENTRY witness (user:
  Icarus -> Pulveran star link). Corroborates kind-5 march state.
- slot 22 IGNATZ (owner 0): st4 -> st3 at 00:28:22 at (-480,0,-736),
  y=0 = ORBIT state (user: orbit Vernunft I then invade — invasion
  effect lands at END TURN, pending).
- slot 16 ERCHAMION (owner 0): st4->st4 d=(-192,-864,+384) 00:15:29 =
  empty-space move (Vernunft). slot 25 IPSHITZ: st3->st4 00:22:19 then
  d=(-224,+544,-768) 00:22:29 = empty-space move (Atropos).
- slot 18 SPARROWHAWK (owner 0, design 6): FOUR stepwise moves
  00:24:39/49/49/59/25:10 (~10 s cadence, deltas 2240/448/896/800 units)
  — NOT in the user action list. Investigate: dwell-march residue, AI, or
  a ship the user moved and forgot to mention. 10-s cadence inside one
  unended turn suggests real-time glide animation, NOT end-turn march —
  CHECK whether watcher xyz updates during animation vs order commit.
- slots 1,6,19 (owners 1/2, design 2/4): single-frame position deltas at
  00:22:29/00:24:08 — AI ships? owner!=0; attribute and explain or note.
- slot 14 STAINER / slot 34 GOFRILLER: NO position change (expected —
  fire orders pending end-turn; their power/charge deltas land at end turn).

## WHAT t370 SHOULD PRIORITIZE
1. Re-run r369_* tools over the window (they are control-verified per t369
   journal a6f9b1a); land MEASURED blocks in ships.md new S-section.
2. Magnetron: reconcile instant-jump + on-grid landing vs S19 T3 rng%200;
   diff ONLY the 00:13:4x-00:13:5x bracket frames (my bracket above is
   wide); identify which word is the placement source the watcher reads.
3. Two-click destination: the moved ships' +0x58/+0x59 order words at
   order-PLACEMENT time (pre-end-turn) are the msg-0x50 witness class —
   extract kind + target encoding for empty-space moves (Erchamion,
   Ipshitz) vs object moves (Ignatz->planet orbit).
4. IF the user ends the turn tonight: re-scan post-end-turn frames for
   combat resolution (Stainer vs Ungooma ship; Gofriller vs planet),
   invasion effect, and the per-ship loss bookkeeping t364 predicts.
