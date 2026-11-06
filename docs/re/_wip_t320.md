# t320 WIP — THE MOUSE-ACTIVE POSTER-PASS RUN (capture, one scratch run)

## S0. Assignment (docs/STATE.md NEXT ACTION t320; REFUTED-ROUTES t319
## amendment (1)-(4) binding). Goal: witness a pump_entry_56b5c stop with
## edx==0xc (msg 0xc) — the destination-road candidate t319 left open. Datum =
## a BANKED leg stop (the save corpus is save-blind to the transient flags,
## t319 S5.1). Legs: {pump_entry_56b5c} ONLY (bytes in LEGS, payload-verified
## t319). Choreography: proven --shipclick gutter phase MODIFIED so input
## activity stays alive through the poster pass.

## S1. INPUT-SHAPE GROUND TRUTH (static, this session, verbatim)
### S1.1 xsend capability (tools/xsend.c read in full):
- VERBS: `key KEYSYM [ch]` (press+release), `keyup KEYSYM` (PRESS ONLY — hold
  semantics), `click x y` / `click3 x y` (Button1/Button3 press+release,
  50 ms gap), legacy `x y`. THERE IS NO MOTION VERB. Header law (measured
  2026-10-04): SDL2 REJECTS synthetic MotionNotify — a built "mousemove"
  would be dropped; XWarpPointer is only re-read by SDL for Button events.
- xdotool is NOT INSTALLED on this host (`command not found`).
- => STATE.md's PRIMARY lever (xdotool mousemove) is DEAD ON THIS HOST; the
  sanctioned substitute (input that re-sets ds:0x484ac via real event verbs)
  is the click train. t320 uses `click` pulses (+ optional `keyup` hold).
### S1.2 ds:0x484ac WRITER/READER census (work/t91_code_disasm.txt, verbatim):
- fn 0x2a5f0 (BIOS int 0x16 AH=2 poll; 0x2a605-0x2a635): ebx/edx isolation of
  AL bits: set -1 @0x2a629 iff (al&1)||(al&2); ELSE store ebx @0x2a635. With
  int16 AH=2 semantics (AL=0, shift flags in AH) the set-path is UNREACHABLE
  and the clear-path writes 0 EVERY pass — i.e. this fn is the PER-PASS
  CLEADER of 484ac [inferred from verbatim bytes; DOSBox int16 AL=0 is the
  assumption].
- fn at 0x2a8a2 (mouse user-event record; t310 law [rec+0xc]=X, +0x10=Y):
  0x2a8a8 sub-branch sets 484d0=Y, 484dc=-1 (THE block-entry conjunction
  members) and 484ac=-1 @0x2a8ce iff word[rec+0xa]!=0 AND 484d0!=0, else
  484ac=0 @0x2a8db.
- fn at 0x2a8fe (the recorder family t319 called fn 0x2a7a4's kin; writes
  484a0=-1 @0x2a92d EVERY call + 484c4/484c6/484c8 = mouse x/y/word):
  484ac = -1 @0x2a94d iff v&1 or v&2 (v = word[rec+0xc] = X low word), else
  484ac = v (=X) @0x2a959. NOTE x=620: 620&3==0 -> 484ac=620 (!=0) at this
  site — yet t319 measured m24da4=0, i.e. fn 0x2a5f0's per-pass clear wins
  unless fn 0x54650 runs BETWEEN a mouse-record write and the next int16 poll.
- fn 0x3ad84 also reads 484ac (0x3ad84 cmp,0).
### S1.3 OPERATIONAL MODEL (why t319 got msg 4 and what t320 bets):
484ac is a RACE value: mouse-record recorders set it on event-consumption,
fn 0x2a5f0 zeroes it every keyboard-poll pass. msg 0xc needs fn 0x54650's
0x54673 read to land while 484ac!=0 (then 24da4=-1 @0x546a5, poster cmp
0x54a88 equal -> 0xc). A single click 6 s pre-poster (t319 shape) loses the
race. t320 SHAPE: sustained input pulse train INSIDE the armed window —
extra gutter clicks every ~1.5 s for the whole bank window, so (a) mouse
records keep being consumed (484ac re-set), (b) 484dc=-1/484d0!=0 stay
re-armed, (c) the poster pass, whenever it runs, lands in active traffic.

## S6. REFINED MODEL (mid-run, static, verbatim t91_code_disasm):
ds:0x484ac is the BIOS mouse/BUTTON STATUS WORD (fn 0x2a5f0 = int 0x16 AH=2
poll; bit0 left, bit1 right, bit3 no-middle). The set-paths (0x2a629/0x2a94d)
are REACHABLE only with AL bit0/1 set = a button HELD; with DOSBox int16
semantics (AL=0, flags in AH) fn 0x2a5f0 writes 0 EVERY pass -> 484ac!=0 only
in the interval between a mouse-record consumption (0x2a8ce/0x2a94d) and the
NEXT int16-poll pass. So msg 0xc is a ONE-PASS RACE per mouse event.
- Pulse-click duty cycle ~50 ms pressed / 1.5 s = weak; each consumed click
  record still gives one candidate pass.
- STRONGER LEVER (t321 candidate if t320 is negative): xsend press-ONLY
  Button1 = `click` mode with the release loop skipped (xsend.c press loop
  `for (press=1; press>=(press_only?1:0); press--)` — keyup does this for
  KEYS; a clickhold verb does it for Button1). A held button keeps the BIOS
  bit0 set -> 484ac=-1 CONTINUOUSLY across poll passes -> 24da4=-1 at the
  next fn 0x54650 -> poster pass cmp EQUAL -> msg 0xc. tools/ is NOT
  game/ (gate checksums game/ only); xsend.c rebuild is sanctioned but MUST
  release the button (paired keydown-release) before the run tail or the
  scratch game drags. STATE.md's "sanctioned substitute = any input that
  re-sets ds:0x484ac" covers this.

## S2. Harness wiring (this session)
- scripts/r299_leg_session.py: +--pulse-clicks N (+ pulse x/y reuse the
  click coord): census_window sends a pulse click every PULSE_S seconds
  BETWEEN pty polls (never during a bank cascade — the t302 freeze law needs
  polling interleaved, which the loop provides).
- scripts/r320_relaunch.sh NEW (r319 pattern: attempt-1 short-circuit, rc=2
  never retry). LEGSET=pump_entry_56b5c. --shipclick 4 --pulse-clicks.
- Oracle pair per window via scripts/r319_gate_read.py (save-blind; banked
  stop is the datum).

## S8. RESULT (run complete, SESSION END rc=0 04:33:41 attempt-1, loop
## short-circuited; census windows: shipclick_baseline + 4 gutter clicks +
## sprite x2 + planet + control_nextturn; 28 pulse clicks logged)
pty-whole-log-census: pump_entry_56b5c=27. BANKED 27/27: EVERY stop
edx=0x4 (MSG 4), esi=eax=0x2bc35c, edi=0xffffffff, ret0=0x213f1a file
0x54aca = POSTER 0x54ac5, esp_p8=0x0. caller histogram 27/27 POSTER.
0x1c01/0x1c02 literal absent every stop. DAT oracles unmoved (nextturn_after
gate_484ec=0x1ff, DAT_43508=0x26d339 unchanged; turn advanced only via
NEXTTURN control 1086->1088).
- THE PULSE LEVER FAILED: msg 0xc ZERO despite pulses landing inside the
  armed windows (e.g. PULSE shipclick_620x120#4 at 04:22:25, poster stop
  04:22:27 same window). Verdict: a 50-ms press every 1.5 s never wins the
  one-pass race of S6.
- NEW MEASUREMENT (corrects t319 S4.2's rarity reading): baseline windows
  banked 0 (idle law holds), but under click traffic the poster block ran
  27x in 18 min (t319: 1x in 28 min unpulsed) — the entry conjunction
  (484dc=-1 AND 484d0!=0) is CLICK-TRAFFIC-DRIVEN and PERSISTS (the
  control_nextturn windows had NO pulses yet still fired 3x: 484dc stayed
  -1 after traffic stopped).
- STATIC RE-READ (t91_code_disasm 24853-24866 verbatim): fn 0x2a5f0 IS a
  BIOS int 0x16 AH=2 mouse poll; ebx/edx isolate AL (xor bh/dh,ah zeroes the
  high byte): 484ac=-1 @0x2a629 iff (AL&1)||(AL&2) = LEFT OR RIGHT BUTTON
  HELD at poll time; else store (AL&1) -> 0 @0x2a635. So 484ac is the raw
  BUTTON-HELD state word, and DOSBox int16 AH=2 reports the held state —
  HELD button keeps 484ac=-1 across EVERY poll pass (not a one-event race).
  50-ms pulse presses lose because the next ms-scale poll clears the word
  long before the ~20 s-period poster pass.
- t321 LEVER (static-backed, deterministic): PRESS-AND-HOLD Button1 across
  the armed window (xsend press-only Button1 verb does not exist yet —
  xsend.c press loop `for (press=1; press>=(press_only?1:0); press--)`
  already has the press_only machinery for KEYS; add `clickhold x y` +
  `clickrelease` (release at same coord, send_event=True)). Premise to
  verify live: SDL->DOSBox-X ButtonPress-without-release parks the emulated
  button; MUST release before the run tail (drag law) and MUST NOT hold
  across bank_stop cascades that click the debugger side (they don't — MCP
  is a separate socket).
- xdotool ABSENT on this host; SDL2 rejects synthetic MotionNotify (xsend.c
  header, measured 2026-10-04): any mousemove-shaped lever is dead here.

## S9. Strict-close verdict
No ledger row closed: the datum would be a live 0x1c01/DAT_43508 store or a
msg-0xc poster stop; neither witnessed. OQ-019 stays open. Honest negative:
"click-pulse mouse-active shape" joins the refuted shapes; the gate itself
(24da4==-1 iff button held at poll) is now statically law [verified bytes]
pending the held-button live witness.

## S10. SAVE CENSUS (r319_gate_read.py over all 20 saves of this run):
19/20 = (ac,d0,dc,24da4,24da8) = (0,0,0,0,-1); 1/20 caught the ENTRY
conjunction live-frozen (d0=1, dc=-1, ac=0, 24da4=0). Confirms t319 S5.1:
saves miss the transient 484ac/24da4 states; the banked stop remains the
only witness class. The one conjunction-save is the strongest independent
corroboration yet that click traffic sets 484dc=-1 + 484d0!=0.

## S11. WINDOW LEDGER (per-window bank counts, this run):
baseline 0 | hold_post_star 0 | shipclick_baseline 0 | 620x250 4 | 620x120 4
| 620x453 4 | 620x300 4 | sprite_47x360 2 | sprite_48x291 3 | planet 3 |
control_nextturn 3 | hold_post_turn 0. 28 pulses fired (per-run cap 30;
observed cadence ~20 s apart, NOT the 1.5 s design: bank_stop cascades eat
~14 s each, and with the poster firing every ~20 s under traffic the loop
spends most wall-time banking — pulses landed in the quiet gaps BETWEEN
poster fires, e.g. PULSE 04:21:25 -> poster stop 04:21:26 still msg 4).
ALL 27 stops msg 4.
