# t322 — BATCON TWO-CLICK ORDER-WITNESS: first-ever live arming of 0x1b5e6/0x1baa7

Fresh session 31, 2026-11-06. Task = STATE.md NEXT ACTION t322.

## S0 — PRE-FLIGHT
- Sitting check FIRST: 200MB tail of work/r1/playcap/live-timeline.jsonl max
  turn 1086 == t319/t320/t321's — NO new play, r1_t85g_sitting.py not run.
- Production :9 (pid 1957) untouched; only Xvfb :9 + its timeout wrapper in
  `ps`; capture runs on Xvfb :97 scratch game-wp.
- Binding negatives honoured (REFUTED-ROUTES t321 amendment (1)-(4) binding,
  which SUPERSEDES the t306 amendment's "do not re-arm" clause for exactly
  these legs — t321(3) proved they were never armed, so t306's zero is about
  the click layer not dispatching into BatModeWnd, not about the legs being
  invalid instruments). t320 (1)-(4); t319 (1)-(4); msg-0x50 no external
  sender; fn 0x1b91c decode VERBATIM stands (t296 S5 + t321 S4).

## S1 — LEG INSTRUMENT (scripts/r299_leg_session.py patched this session)
Three legs ADDED to LEGS (bytes payload-verified vs work/ascend_payload.bin):
  w43508_1b5e6  file 0x1B5E6  a3 08 35 04 00   mov ds:0x43508,eax  (fn 0x1aef8
                                              msg-0x50 publish leg, t296 S4)
  w43508_1baa7  file 0x1BAA7  a3 08 35 04 00   mov ds:0x43508,eax  (fn 0x1b91c
                                              per-ship destination store,
                                              t296 S5 / t321 S4)
  fn1b91c_entry file 0x1B91C  56 57 55 89 c6 83 b8 af 00 00 00 00
                                              entry; at stop eax=esi=BatModeWnd
                                              rec (bank_stop magic grid dumps
                                              +0xaf/+0xb3/+0xb7 = the
                                              recorder-first reads); edx=clip
                                              ptr (bank_stop clip block reads
                                              kind+obj+ship_slot).
Legset = batmode_dead (0x1AEF8, ctl-anchoring code-entry leg[0] + entry
witness), fn1b91c_entry, w43508_1b5e6, w43508_1baa7, btn_hdlr (positive
control). NO cos_hdlr/s2_* (0x3b pump storm floods the 6-stop bank cap, t306
launch-note law).

## S2 — CHOREOGRAPHY (scripts/r322_relaunch.sh NEW)
Census mode: --pre-turn 1 (slot-8 kind-4 gate, t298 law) -> close_eventwin ->
open_fleet -> rowjump (200,93) -> sprite/planet clicks (t312 census values
48,151 / 439,331; finder bounds x 8..465 client rect) -> control_nextturn ->
hold. Each click inside its own armed window (t303 census unit); recorder-first
law satisfied structurally: every fn 0x1aef8/fn 0x1b91c stop banks the
[win+0x90..0xcf] grid + clip kind/obj BEFORE the window disarms and the next
click fires.

## S3 — RUN RESULT (MEASURED, run work/r1/t299-leg-20261106-055549 rc=0
## attempt-1, BREAK lottery won first try, census-ctl MATCH=True, teardown
## clean, scripts/r322_relaunch.sh + scripts/r322_analyze.py NEW)
Battery: baseline -> hold -> pre-turn 1086->1087 -> fleet open (rails=188) ->
rowjump -> sprite (48,151) -> planet (439,331) -> control_nextturn -> hold.
WHOLE-LOG pty census: {batmode_dead: 0, fn1b91c_entry: 0, w43508_1b5e6: 0,
w43508_1baa7: 0, btn_hdlr: 3}. Banked stops (all btn_hdlr):
  sprite  -> win 'PLIND'  edx=0x8 (msg 8 repaint, t312 law re-observed)
  planet  -> win 'Cancel' edx=0x4 (post-turn EVENTWIN popup ate the click —
            census_click's close_eventwin ran BEFORE the arm, popup re-opened
            or persisted into the window; harness defect, see S5)
  nextturn-> win 'PLSQUARE' edx=0x8
Oracles: sel43510 = 0 in EVERY snapshot (9/9); DAT_43504 'Icarus' constant;
DAT_43508 0x26fe77 -> 0x26f00d across the turn with ZERO armed-writer fires
(writer-less churn re-observed, t298-C/t311 law — NOT a witnessed store).

## S4 — VERDICT: DECISION-TREE BRANCH (b). The FIRST-EVER live arming of the
batcon click-road legs measured ZERO whole-log executions while the positive
control btn_hdlr fired 3x and the instrument verified (MATCH=True). fn 0x1aef8
(BatModeWnd msg handler entry) never received a single msg during the entire
session — including while FLEET was open, the rowjump navigated, and turn
advanced. Combined with t306 (same entry zero under a sprite-only battery) this
is now TWO independent rc=0 runs with the entry leg armed: BatModeWnd is
COMPOSITION-SHIELDED at the campaign/system map — no mouse event in any
captured in-view state dispatches into it. The t321(3) blind spot is CLOSED as
a blind spot: the mouse road was tested (t322) and it is dead IN-CAPTURE. The
unnamed blocker is precise: windows.txt BatModeWnd block (line 1178: TYPE 4,
PARENT NONE, STATE 1 16, rect 7,7-465,472) — the window exists but is never
STATE-active in captured sessions; no click can hit-test into an inactive
window. Per the STATE.md decision tree: NO third mouse battery before the
offline activation decode (who writes STATE / what shows BatModeWnd).

## S5 — HARNESS DEFECT BANKED (not fixed this iteration): census_click's
close_eventwin + assert_on_map run BEFORE arm_census; a popup that is open at
reguard-time bails the window (digit/fleet-keys phases) but the sprite/planet
path banked a 'Cancel'-window stop instead of the map click — the planet datum
was spent on the popup. Fix options for the next capture-bearing iteration:
re-run close_eventwin AFTER arm and before EXEC RUN in census_click, or make
assert_on_map reject when the banked stop's win-name is EVENTWIN-class.

## S6 — NEXT (t323, offline, zero capture): WHO ACTIVATES BatModeWnd.
Probe surface: (1) whole-image census of writers to the window-record STATE
field (windows.txt STATE 1 16 -> runtime window record; the t313 fleetwnd_map
+ t316 registry tools locate the BatModeWnd INSTANCE cp, handler-ptr member
0x247978 known since t298-E); (2) fn 0x1d7dc / fn 0x1be10 (called at every
fn 0x1aef8 exit, disasm 7508/7510) are activation-adjacent candidates;
(3) the msg-0x53/0x50 senders (t296: no widget imm census hit outside the
batmode family) — if activation is itself a msg from a MENU (e.g. a batmode
toggle button), the sender lives in a class the captures never opened. Route:
offline decode only; a capture is justified ONLY after the decode names a
concrete activator widget/keypress.

