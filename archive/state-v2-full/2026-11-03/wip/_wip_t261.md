# _wip_t261 — LONG DRIVE + WITNESS HARVEST (in progress)

## S1. THE RESTORED-t1255 STATE IS SOFTLOCKED-ON-LOAD (MEASURED; kills the 1255 drive route)

Bring-up per t260 laws (scripts/r1_t261_session.sh, all green):
- bank md5 0024340d verified; scratch savedir held ONLY the copy; Xvfb :8;
  GUI dosbox-x (no -nogui, NO -time-limit); watcher up BEFORE launch.
- Load click (350,197) landed: log "Loading state from slot: 60" +
  "[21:02:27]: Loaded. (Slot 60)"; watcher row turn=1255 score_stars=14
  systems_any=36 == the frozen t1255 row. LOAD ITSELF REPRODUCES t260.

Input interrogation (scripts/r1_t261_drive.py, target 1405):
- presses 1-6 of NEXTTURN window-rel (511,84) [67+17 menu bar]: ring never
  advanced past 1255; drain_popups closed 0 (no popup on screen, vision
  confirmed: galaxy map, turn readout 01255, no dialog).
- input probe: Escape and 'c' changed_px = 0 (t250 law galaxy screen: healthy
  game toggles >50 px).
- screen md5 IDENTICAL across p0/p1/p2/p3 (minutes apart, 126933 B PNG,
  e403bbb5...) — work/r1/t261-softlock-evidence/screen_frozen.png.
- RAM CORE census over the ring tail: 1 distinct core state across slots
  59..41 (all fields except wall/file/mtime identical) — RAM-frozen while
  autosave keeps writing (t250 softlock signature = input-dead AND RAM-frozen:
  BOTH legs positive).
- CONTROL (proves the input path is healthy): xsend menu-bar click (315,8)
  OPENED the Capture dropdown (pixel-diff mean 0.043 vs frozen baseline), and
  autosave churn continued at 10 s cadence, dosbox at 90 % CPU. So SDL window
  events ARE delivered; it is the GAME that ignores them.
- ring banked first: work/r1/bank-t261-soft1255/ (20 slots), then session
  stopped (recorded pids only; production :9 524517 untouched, its timeline
  current 21:22 turn 1086).

INTERPRETATION [inferred from the measured legs]: the t1255 save captures the
game in the SAME softlock bug class that killed the live session at t1254
(planet-list-dead) / t1089 (popup-dead) / the 15:45 process death — the game
engine was already input-dead when the state was written; the autosave ring
kept banking the frozen frame. t260's verification (turn/V decode of a
round-trip re-save) is a STRUCTURAL check and cannot see input liveness —
new harness law: a restored state must pass an INPUT-LIVENESS PROBE
('c'-toggle delta > PIXEL_ALIVE) before any drive is planned on it.

CONSEQUENCE: the t1255 route to t261 is DEAD until the bug class is
understood (t266 material). Queue clause exercised: base = 1086 (production
:9, healthy, same campaign, already 169 turns ahead of the Oct-29 RESUME.GAM).

## S2. FALLBACK BASE = production :9 (healthy), drive toward 1405 IN PROGRESS

Liveness control on :9 BEFORE touching it: 'c'-toggle changed pixels both legs
(convert diff mean 0.00277 each way) => production input path alive; the :8
frozen-state result was NOT an xsend artifact.

scripts/r1_t261_drive.py parameterized by env (ONE code path for both
sessions; periodic bank-every-30 + final bank shared):
  T261_DISPLAY / T261_BASE / T261_MENUBAR (17 GUI, 0 -nogui) /
  T261_RECOVER=loadstate|resume. Production geometry: window 640x480+80+100,
  NEXTTURN window-rel (511,67). resume mode keeps the t250 Return-to-Game
  path but LOGS the RESUME.GAM regression honestly (Oct-29 save).

CHUNK 1 (foreground, target 1096): 1086 -> 1096, 10/10 presses moved,
popups drained 0-4 per press, final bank bank-t261-final-1096. rc=0.
CHUNK 2 (background proc_09d164ba35dc, target 1405, presses<=340,
softlocks<=3): started 21:31; press 16 at 21:35 = turn 1111. Log
work/r1/playcap/drive_t261.out.
CAVEAT (unexercised): with the gate-mandated `timeout -s KILL` wrapper the
pid file holds the timeout pid; killing it does NOT kill the child dosbox —
any future user of r1_t261_session.sh must kill by `pgrep -P` or exact name.
Moot for now: the :8 loadstate-drive route is REFUTED (S1).

## S3. PRODUCTION :9 ANOMALY AT 21:38 — RAM FLIPPED HEALTHY-t1111 -> t1255-PROFILE -> TITLE MENU, ALL INPUT-DEAD; RECOVERED PER SOP (mechanism [unverified])

MEASURED, in order:
- Drive chunk 2 ran clean 1086->1111 (presses 1-16, popups drained 0-5/press).
- Presses 17-20: ring stuck at 1111, drains closed 0-2, input probe ALIVE
  (changed_px ~306k — that probe TOGGLES the overlay, so ALIVE was genuine).
- Press 20 at 21:38:41: ring turn JUMPS 1111 -> 1255 (V 23->14, systems_any
  26->36 — the exact frozen-t1255 profile; same campaign, +144 turns of
  history, NOT a re-load of my bank: prod ring 60.sav Memory md5 8bd6dd0f !=
  bank-t251-live1255 3a0a36c8, != :8-session slots 2513d0ae).
- dosbox.log for :9 contains ZERO "Loading state"/"Loaded." lines (count 0) —
  NOT a dosbox loadstate.
- work/r1/game/{01..04}.SAV atimes ALL 21:38:14.768 (same instant; mtimes
  unchanged Oct 19-26) — the GAME process scanned its in-game save-dialog
  directory mid-window. RESUME.GAM untouched (5b382afb, atime 07:39).
- NOW (22:05-22:16): screen md5-frozen (three consecutive 1.5 s grabs
  identical; Escape x2 and 'c' legs ALL zero-pixel); ENDTURN click no advance;
  ring decodes t=1255 V=14 at 22:16:04; ring rows OSCILLATE t1254<->t1255
  between consecutive slots (NEW bug-class tell for t266 — turn site toggling
  while game is input-dead).
- ss: an ESTABLISHED VNC connection exists on :5910 ([::1]:53822) — BUT the
  x11vnc log logs exactly ONE connection ever (Oct 16 15:39:20, never closed)
  and bytes_acked FROZE across 20 s. => stale zombie client, NO evidence of a
  human at the display during the window. Human-sitting hypothesis WEAKENED.
- Arrow keys (Down, Up) on the title menu changed 0 px — a healthy title menu
  moves its highlight; the process is input-dead even on the menu, while
  dosbox burns 89.7% CPU. Fourth incident of the bug class; ring banked to
  work/r1/bank-t261-prod-titlesoft/ (20 slots incl. the oscillating rows).

[unverified] MECHANISM candidates: (1) a human at the VNC client opened the
in-game Load dialog (atime fits) and loaded a state — but no on-disk in-game
SAV decodes to t1255 (01-04.SAV are Oct 19-26 vintage), so the load SOURCE is
unexplained; (2) driver drain-popups misclicks on the bare galaxy screen hit
the game's own menu (t244 precedent: misclicks DO trigger game actions) —
cannot be excluded, the OK-target band (root y~340-460, x~170-486) overlaps
the game's lower screen; a slot-load would still need a source file (same
unexplained-source problem). Driver was killed on discovery (ps|awk pattern,
NOT pgrep -f — that footgun fired once more this session, killing only my own
shell).

DECISION (final, after the zombie-VNC finding): the human-sitting premise
evaporated (single Oct-16 connection, bytes_acked frozen), so the standing
recovery SOP was executed: bank bank-t261-prod-titlesoft -> SIGKILL recorded
pid 524517 -> r1_playcap_vnc.sh start -> Return-to-Game click -> resumed
t1086 V=0 at 23:05:11; re-drive to 1236 launched 23:07. HONEST LOSS: the live
t1111 RAM image (dosbox.log has zero loadstate lines and RESUME.GAM never
advanced past t1086, so the kill discarded it); banked slots survive.

## S4. HARVEST (full tables in docs/re/score.md S12 + docs/re/combat.md §5)
Witness(b) LANDED: +0x15 star-set grows 1087->1111 ([4,24,36,44] ->
[4,14,24,32,36,44]) while V=23 stays constant — S6 non-join re-corroborated
on a driven corpus. Witness(a) honest negative: 20 non-war change-hits, zero
destructions, zero strict engagement-scale (min dist2 39441) — churn, not
volleys. OQ-016/OQ-021 STAY OPEN. KEEPER scripts/r261_harvest.py; window_rows
off-by-one bugfix in r1_t251_mine.py (earlier trust=False passes were vacuous).
