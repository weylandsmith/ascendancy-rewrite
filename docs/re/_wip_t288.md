# _wip_t288 — softlock-class follow-up WITH THE DEBUGGER

S0 TASK (STATE.md NEXT ACTION, 2026-11-03): bring up a SOFTLOCKED scratch
session per t260/t261 laws (GUI, loadstate from scratch copy of
bank-t251-live1255 slot 60, own ring dir, never :9), BREAK in, dump the
input-callback path / the game's own input flag instead of guessing.
Target question (t266 §5): which part of the input chain is dead in the
save-carried softlock — the event PUMP (writes the pending-input globals)
or the DISPATCH downstream of them?

S0.1 STATIC LEAD (t103 P13, docs/re/_wip_t103.md:138-155, cited): the game's
pending-input globals are WORD ds:0x484c4 (msg code), ds:0x484c6 (char/ebx),
plus a second pair ds:0x484ec/0x484f0 — written by the INPUT layer, read
verbatim by the input relay 0x54976 (msg := [ds:484c4], ebx := [ds:484c6]);
event record readers at 0x2a875/0x2a8fe. So the game-visible INPUT FLAG does
exist and has addresses. Census route: ring-slot Memory member contains the
full linear image (pointer law CLOSED), so these words are readable OFFLINE
from any banked slot — zero debugger risk.

S0.2 DESIGN DECISIONS (measured-law driven):
- dosbox-x-dbg (2026.10.01 master build) GUI mode: NO -nogui (loadstate is
  Capture-menu-only, t260 law) and pty stdin (tty gate debug.cpp:5410).
  Release binary /usr/bin/dosbox-x has ZERO "BPLM" strings -> debugger-less,
  cannot host the watch; dbg binary must carry the session.
- NO -time-limit on the loading process (TL-BOUNCE law, t260: the deadline
  expels a loaded state within seconds). Bounded externally by `timeout -s
  KILL` (not an emulator flag). This is why r1_wp_session.py (always passes
  -tl) is NOT reused verbatim — t288 gets its own script r288_softlock_probe.
  py borrowing its socket/scan/dump code.
- BREAK lottery per t286 law 2: relaunch loop until 'armed:'; arm at the
  TITLE screen (t282 3/3 class, t286 title 2/3) BEFORE the load, because
  BPLM survives save-restore (t286 law 1) and post-load BREAK died 4/6.
- Base at title: ASCEND.EXE is resident at the game title screen (it IS the
  game process), and autosave=10 arms at launch (AUTOSAVE-FROM-START law),
  so ring_mem() base vote works pre-load. Verify B == 0x1bf4d8 (t286
  deterministic base) before trusting data-derived linears.
- Watch byte: data:0x484c6 low byte (the char). Injected 'c' key char=0x63
  nonzero; msg word low byte also fine, but char is the semantically
  injected value. Artifact law: nonzero-at-arm byte fires once '00 -> xx' —
  reject exactly one.
- Load with bp armed fires the watch during state restore (restore writes
  every byte) — DRAIN those (log eip + RUN), same loop as t286 break-early
  entry. A fire that stops the CPU mid-restore is recoverable by RUN.
- MENU LAYOUT RISK [unverified]: dbg build is 2026.10.01, t260's menu coords
  are 2025.02.01 (Capture at 315,8; Load-state row 350,197). Mitigation:
  screenshot the open dropdown and locate rows by the t260 neutral-dark
  pixel census BEFORE clicking; verify load by dosbox.log "Loaded. (Slot
  60)" + ring row turn==1255, never by xsend rc.

S1 OFFLINE CENSUS OF THE GAME'S INPUT GLOBALS — LANDED, DISCRIMINATOR FOUND
Tool: scripts/r288_input_census.py RC=0 (member-index law: mem[B+OBJ1_OFF+off];
first attempt used B-H+OBJ1_OFF and read the string table 'White Dwarf/Red
Dwarf' — off-by-H, fixed and documented in the script). Linear of data:0x484c4
== 0x28a4c4 at the deterministic base B=0x1bf4d8 (same base in every bank).

MEASURED (u16 readings, one slot per bank):
  SOFT t251-live1255/60.sav : 484c4=0x0001 484c6=0x001b  484ec=0x014e 484f0=0x0156
  SOFT t261-soft1255/52.sav : 484c4=0x0001 484c6=0x001b  484ec=0x014e 484f0=0x0156
      (the :8 restored session's own bank mid-input-dead — BYTE-IDENTICAL to
       the save it was loaded from: nothing in the pair ever changed again)
  HEALTHY t261-final-1096/43: 484c4=0x002e 484c6=0x0063  484ec=0x0144 484f0=0x0156
      (char 0x63 == 'c', the overlay key the driver pressed — proves the pair
       holds the LAST DELIVERED EVENT, and that healthy play rewrites it)
  HEALTHY t285-predrive/48   : 484c4=0x0000 484c6=0x0000  484ec=0x01dc 484f0=0x0000
  TITLESOFT t261-prod-titlesoft/48: 484c4=0x0048 484c6=0x0000 484f0=0x0043
CONSTANTS across every bank (healthy AND soft): 484c8=0x0200, 484cc=0x0001 —
structural, not input state.

READING [inferred from the cited static law + these values]: 0x484c4/c6 is the
pending-input PAIR (msg code, char) the input layer writes and relay 0x54976
consumes verbatim (t103 P13). In the softlock class the pair is STUCK at
(msg=1, char=0x1b=Escape) across slots; healthy idle zeroes it; healthy play
overwrites it. So the softlocked save carries a pending event that is NEVER
CONSUMED — the consumer/dispatch side is the dead half, OR the pump is dead and
1/0x1b is merely the last thing written before the pump died. THE LIVE WATCH
DISTINGUISHES THESE: inject 'c' into a restored soft session with a BPLM on
data:0x484c6 — a fire = the pump still writes (dead downstream of the globals);
silence = the pump itself is dead (event never lands in the game).
S1b FULL-BANK CENSUS (execute_code over 10 banks, 20 slots each) — REFINES S1
Second pair decoded [inferred, strongly]: 0x48ec/0x484f0 == LAST MOUSE X/Y.
  healthy t261-t1116 p2=(0x1ff,0x043)=(511,67)=NEXTTURN button; t250-predrive
  p2c/p2=(553,145)=Planets sidebar; t285-restored + t273-predrive
  p2=(320,240)=screen centre; t285-loaded1255 p2=(318,333)=Return-to-Game.
Per-bank (msg,char) histograms:
  HEALTHY idle: (0,0) 20/20 slots. HEALTHY after driver 'c': (0x2e,0x63) 18-19/20.
  SOFT t285-loaded1255 (the input-dead restored session): (1,0x1b) 20/20 AND
     mouse pair FROZEN at (318,333) 20/20 — no pump write after the load click.
  SOFT t261-t1255 (restored campaign churning): (1,0x1b) 9/20 slots but the
     MOUSE PAIR CHANGES (511,67)->(326,342) while (msg,char) stays 1/0x1b.
  SOFT t1254 bank (softlock #2, t247): (0x2e,0x63) 19/20 + one (1,0x1b) slot,
     mouse pair constant (639,171).
CONSEQUENCE (honest): a frozen nonzero (msg,char) is NOT by itself proof of
pump death — t261-t1255 proves the pump still wrote mouse coords while the pair
sat at 1/0x1b. The clean discriminator is therefore a LIVE KEY INJECTION:
xsend keys are a proven-delivered channel (t260/t287 laws), so if an injected
'c' does NOT move 0x484c4/0x484c6 in the ring of a restored soft session, the
game-side input PUMP is dead; if it does move, the pump is alive and the dead
half is downstream (relay/dispatch). t285/t261 injected input and measured
pixels only — never the globals. That measurement is THIS iteration's product.




S2 LIVE PROBE ATTEMPT 0 (dbg binary) — NEW REFUTED ROUTE: THE DEBUGGER BUILD
CANNOT RESTORE THE BANK. scripts/r288_softlock_probe.py run
work/r1/t288-probe-dbg-a0-20261103-104330: BREAK lottery WON at title
('00. BPLM 0028A4C6 (00)' armed; base vote B=0x1bf4d8 works at TITLE too),
EXEC RUN, Capture-menu click + Load-row click delivered (xsend rc=0), pty:
  LOG: Loading state from slot: 60 (...)        <- restore STARTED
  LOG: pixratio 1.000 ... menuScale=1
  corrupted size vs. prev_size                  <- glibc abort, process DIED
"Loaded. (Slot 60)" NEVER printed. Mechanism [unverified] — same glibc-heap
abort family as t282's BREAK 'corrupted double-linked list', fired mid-restore;
the untested combination was master(2026.10.01)-restoring-a-2025.02.01-ZIP
(t286's campaign entries were RESUME.GAM game-loads, never emulator states).
=> The dbg binary is OUT for restored-bank sessions. The RELEASE 2025.02.01
binary (same version as the bank, zero BPLM strings) hosts the session; the
RING-LEVEL census answers the pump question with no debugger. Writer-EIP leg
stays open (honest negative).
NOTE title census reads garbage (mx=0x6168 ASCII): base vote works at title
(code resident) but the DATA segment is not meaningful pre-campaign — census
labels valid only after campaign entry.

S3 LIVE PAIR (dbg route closed by S2) — THE ANSWER
Release-2025.02.01 host, ring census through injections (full slot tables in
selfplay.md t288): SOFT run 104942 restored t1255 (LOG+turn+vision all confirm)
— (msg,char) stuck (1,0x1b) 11 slots across click + 2 'c' keys, screen md5
frozen 23492a86. CONTROL run 110123 (same scratch mount, --no-load, RESUME
t1086) — pair moved to (46,99) after ONE 'c', overlay visibly toggled.
=> DEAD HALF = THE GAME-SIDE PUMP. Downstream dispatch never got a chance.
S3b SOP: liveness needle = inject 'c', expect data:0x484c6==0x63 in next ring
slot(s). Replaces pixel-diff for drive softlock detection (t266 §4 request).
S4 LEDGER: no OQ row matches the softlock class (grep '^OQ-0' shows no engine-
hang row) -> nothing closed, nothing opened; honest negatives stand (writer EIP
unwitnessed; mouse-pair sub-variant; control turn-dword 0 anomaly flagged).
S5 FILES THIS ITERATION: scripts/r288_input_census.py (RC=0),
scripts/r288_softlock_probe.py (rc=0 both modes), docs/re/selfplay.md t288
block, docs/REFUTED-ROUTES.md t288 block, banks: work/r1/t288-probe-{dbg-a0,
rel-a0 x2}-*, work/r1/game-t288 scratch (149M, keep for t289), production :9
UNTOUCHED (pid 660167 alive, t1086).
