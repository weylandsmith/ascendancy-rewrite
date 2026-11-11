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

## t370 TOOL PASS (scripts/r369_*, run 2026-11-11 ~01:15) — WINDOW FOUND
r369_playwindow.py exit 0: first turn!=1086 row = turn 1253 wall 00:02:09,
lo_ns=1794373326560000000. Ring banked to work/r1/bank-play-20261111/ (20
slots, ALL turn 1253 => the user's turn was still unended at bank time; the
bank covers only the last ~200 s of the session, so the 00:02-00:39 events
exist ONLY in live-timeline.jsonl).
r369_magnetron_hit.py --window lo -1: 385 deduped slot-samples; C1 carriage
cidx60 present on 10 slots (use-counter 1); C2 OFF-GRID st4 = 0 hits,
on-grid st4 = 8871; C3 W2 frames = 0; y-mod-32 histogram {0.0: 8871} (y is
ALWAYS a multiple of 32 in st4 rows).
r369_order_diff.py --window lo -1: 390 samples; kind histogram {4:8986,
3:2440, 5:3784, 1:780}; dest-change classes {'BOTH':2} (both slot 18);
TWO-CLICK (adjacent XY->Z) = 0; gizmo use-counter decrements = 4 (slot2 own2
cidx0 1->0; slot14 own0 cidx9 3->2; slot34 own0 cidx9 3->2 then 2->1);
off-32-grid z landings = 0.
r369_order_diff.py --dir bank-play-20261111: 1 deduped sample (all 20 slots
identical turn 1253 + identical diffed fields => turn never ended inside the
bank). Honest negative, instrument not at fault.

## t370 TOOL PASS 2 (scripts/r370_slot_events.py + r370_bank_deref.py, ~01:30-02:20)
WINDOW EXTENDS: session still live at probe time (timeline mtime 02:19, rows
to wall 02:18). Full event stream banked work/r1/t370_slot_events_all.txt
(window lo..EOF at ~01:26 run; 29 lines, events=10). SECOND BANK
work/r1/bank-play-20261111-late/ taken 02:19: TURN=1254 => the user ENDED THE
TURN between 01:26 and 02:19. Late bank n=40 ships (was 41).
STAR COORD SCALE: star-table triples (name-0x14) are 50/50 OFF the 32-grid
(Vega (359.5,246.4,-60.2)) while SHIP pos records are 32-multiples in st4 —
different unit scales confirmed (open mapping question; ship-grid law T3
DAT_000895dc=32 stands for ship space).
GUANDAGNINI 00:13:50 EVENT (full decode): pos (-1184,1344,-1184)->(1280,-1760,
1344); kind 4/0x45->4/0x85; tgt 0x256045->0x255c85; type 1->2; pay swap;
POWER +0x88 90->80 (= Lane Magnetron gizmos.txt idx 60 'Power 10' EXACT);
RING SLOT REMOVED: slot14 (cidx 60, use 1) GONE post-jump = single-use gizmo
consumed (NumUses=1 column); +0x8c 40->39 happened LATER (00:24:08, separate
10-s frame) = 1 dmg point, NOT a charge decrement (spec: +0x8c = INTEGRITY
hull, combat `sub [esi+0x8c],eax`) — the manual-pass note calling +0x8c
'charges' is CORRECTED.
+0x59 DECODE (this session, r370_bank_deref): value 0x255c85 = star-record
NAME SLOT address (Vega chain base 0x255c69 + 0x1c; chain0 Vega @H+0x255be1
pattern, k=7 name 0x255f09... NOTE: 0x255c85-0x255c69=0x1c = name-0x1c? the
hit is INSIDE Vega record 0's name field region (name 60B? star name field).
Deref of FUN_00021f58's target[+8]/[+0x14] at that addr reads zeros/garbage =>
target object is NOT at the guest-linear addr read naively OR the ptr points
at an embedded sub-record; the handler's 'target' is the star OBJECT ptr and
[+0x14] = its triple — at 0x255c85 the bytes AFTER +0x1c ARE the triple slot?
UNRESOLVED: landing (1280,-1760,1344) is >200 units from EVERY star triple at
scale 1/5/160 => placement source is NOT star-table xyz at those scales.
=> magnetron landing-vs-star-xyz mapping UNRESOLVED; on-grid landing is
CONSISTENT with T3 quantizer applied at commit (FUN_00049aa8 path + walk
quantizer FUN_000533e0 g=32) — jitter survives only mid-transit (t101: 12/12
off-grid ships were kind-2 mid-transit). C2 census off-grid test is
BLIND AT REST by construction; instrument law, not a game law.
ILMARINEN: 00:20:19 type 0->3 trip:=(-672,32,-2112) (OFF-32? no: all x32) +
act:=7 + power -2; 00:21:21 kind 4->5 pos:=(0,0,-2144) = lane-entry. LATE
BANK (post end-turn): pos (28,0,-2144) — x=28 OFF the 32-grid, still kind 5
= MID-TRANSIT off-grid corroborates T3 'arrival-time-only' quantization.
SPARROWHAWK s18: 00:24:39 kind 3->4 pos jump d=2240; then 00:24:49/59,
00:25:10 type=3 trip==pos EXACTLY each frame + pay ptr churns 0x1030000/
0x14f0000/0x1aa0000 (garbage-looking, NOT deref'd in tl mode) + power
19->16->11->8 = real-time march steps consumed at 10-s cadence (watcher
samples the GLIDE, not order commits — answers the manual-pass CHECK item).
AI ships s2/s11/s12/s23 own2 at 00:24:08: power burns + ring slot u16 arg
0xFFFFFFFF churn = AI order issue at the same wall frame as player's Stainer
power burn — end-of-sub-turn batch.
RING DECREMENT STORY (census r369 4 decrements + slot_events): s14 Stainer
cidx9 slot13 use 3->2 @00:24:08 (power 90->84 = gizmos.txt idx 9
Nanomanipulator 'Power 6' EXACT); s34 Gofriller cidx9 slot13 3->2 @00:26:59
(power -6) then 2->1 @00:27:51 (power -6) = 2 uses. cidx==gizmos.txt ENTRY
INDEX confirmed for 9 (Nanomanipulator), 60 (Lane Magnetron), 73 (Invasion
Module — s22 Ignatz LOST 2 slots (73,0,0) @00:28:48 = invasion launched,
user: 'invade Vernunft I'; effect pending end-turn, check post-1254 bank).


## END-TURN RESOLUTION CAPTURED (assistant, 2026-11-11 02:07-02:12; user asleep,
## blanket grant "do whatever you want / mess with the running game" 23:5x)
Route notes: NEXTTURN clicks STUCK twice while screen sat in SYSTEM VIEW
(button exists only on star map; NEW LAW candidate: system-view must Escape
first — Escape unwinds one level, corroborated). First Escape attempt hit the
ORPHANED t1555 quit-blocker (xmessage pid 107540, spawned 11:23:30 by the
SIGTERM'd old dosbox; killed process, window unmapped, game unharmed —
xsend blocker-refusal worked exactly as designed). Then driver t245 pressed
turn: 1253 -> 1254, drained 5 popups. ON-DISK USER SAVE UNTOUCHED (no game
save performed; RAM state 1254, disk stays 1253).
RESOLUTION WITNESSES (pre=bank-t1253-preresolve/60.sav frame 02:07:27 vs
post=playcap 60.sav 02:11:36; ship slots via watcher):
- SLOT 40 DESTROYED: owner 0, design 12, xyz (0,0,0) state 1 pre -> slot gone
  post (41->40 ships). WHO + WHY UNKNOWN: at star-plane origin in st1; check
  raw record + AI-attack plausibility; Ungooma att 190->189 same boundary.
- SLOT 12 (owner 2) state 4->0 owner byte 2->0xFFFF = DEATH-CLEANING law
  (death handler 0x49d2c class): position FROZEN at last xyz, owner becomes
  sentinel. AI ship died too (combat or dwell? design 4).
- POWER RECOVERY at turn boundary: Stainer +0x88 84->90, Gofriller 78->90 =
  CAP (recharge law trunc([+0x18]*(1+...)) cap hit; both fired orders
  resolved with charges word +0x8c UNCHANGED 40 -> their shots were NOT
  gizmo charges; charges law untouched).
- USER-ORDERED MOVES RESOLVED: Erchamion (-416,-2048,+864), Ipshitz
  (-416,+896,-1312), Sparrowhawk (0,+256,+384) [user: several Pulveran moves,
  confirmed], Guandagnini arrived st5->st4 d=(-1504,-1952,+736) continues
  post-jump travel; 7 AI ships st4->st5 (lane entries) + 5 st5 st5 +14/+28
  px = transit crawl steps.
- INVASION: Vernunft I owner byte 255->255 NO CHANGE (planet table 151 recs,
  base-normalized diff: ZERO owner changes turn 1253->1254). Hypotheses:
  ground-control is a different field/law, or effect next turn, or invade-
  own-planet no-op (Vernunft I owner=0 ALREADY player-owned in planet table —
  CHECK what the user saw on screen; possible the planet is UNOWNED in table
  sense vs player sense... 255 at +0x24+0x33 vs owner-count dict says
  Vernunft I owner 0. RE-VERIFY offsets before banking any law).
- relation.atts Ungooma 190->189 (-1); matrix states unchanged (no war).
PLANETS: planets_mine 35->35; score_stars 0->14 (watcher field, meaning TBD
- first non-zero ever? check field law).

## t370 TARGET-DEREF RESOLUTION (execute_code probes on bank-play-20261111-late)
+0x59 VALUE ANATOMY: runtime u32 whose LOW 16 bits are a guest offset into the
star-name table region (0x255c85 = Vega-rec0 name 0x255c69 + 0x1c; chain base
H+0x255be1 law). The +0x1c site is ZEROS (star record: name@-0x1c..-0x01,
triple@-0x14, idx@-0x18; at name+0x1c sits the NEXT record's spare/zero word)
— reading FUN_00021f58's target[+8]/[+0x14] there gives zeros/garbage. So the
naive 'target = star object at that linear addr' read FAILS; the handler's
EDI-based branch (target[0]/target[4] id match) never matches garbage => the
placement triple must come from a record whose base = +0x59 value MINUS the
high-byte-tagged stride, or the low16+H rebase law for this field differs.
UNRESOLVED, banked as instrument question (needs the disasm of 0x220a8's
target-store leg, not more RAM pokes).
STAR TRIPLE vs SHIP POS SCALE: Vega table triple (359.5,246.4,-60.2); no
scale 1/5/160 puts the magnetron landing (1280,-1760,1344) within 200 units.
type=2 pay ptr deref (0x2589f6) = (-654.8,2055.2,-556.8) = some object triple,
NOT the landing. => landing source UNIDENTIFIED this session; honest negative.


## S-T376 save-slot map + protection (2026-11-11, user directive)

User directive: existing saved games (day 887, 1086, 1253) must NOT be
overwritten; other save-state mutation is granted.

MEASURED LAW (new, cheap): a raw `.SAV`/`RESUME.GAM` byte 0..3 is a u32
LE = the game-day (turn) at save time. Verified 6/6 files in the mounted
game dir (work/r1/game): 01.SAV=1086, 02.SAV=1253, 03.SAV=887, 04.SAV=1254,
RESUME.GAM=1086, RESUME.GAM.user-oct29=1086. (The in-game menu shows these
as day numbers; slot order is NOT chronological.) mtimes are USELESS here —
the whole game dir was copied at VM setup (Oct 26 08:59) and the in-game
save writes preserve them.

PROTECTION EXECUTED 2026-11-11: all six files copied read-only (chmod 444)
into ~/ascendancy-saves-protected/ (dir 0500), md5-verified identical:
01 a5816431d5afc9940cbfa75e790ef943 / 02 35b29d9c8fa8aff7b903796eb37cd349 /
03 e3e9e220cb4e0804f44854ea03305453 / 04 5b8662d9bb5567cd4efdb65122e450ab /
RESUME(+user-oct29) 5b382afbb789186c3654f3cec085b2e2.
NOTE: in-game SAVE writes to slot NN replace work/r1/game/NN.SAV wholesale
(dosbox C: mount) — the protected copies are the restore point, not a lock.
Ring saves (NNN.sav in playcap/save/) are a different container (raw, ~2 MB,
watcher-made) and never collide with the user's 4 slots.

Consequence for the tutorial plan: running the tutorial mutates RESUME.GAM
(=day 1086 slot content) and may clobber slot files if saved; RESTORE
POINT = cp ~/ascendancy-saves-protected/RESUME.GAM work/r1/game/RESUME.GAM.
