# t314 — FLEETWND-FOCUS msg-0x1c01 LIVE CAPTURE (WIP, hand-authored)

Task (docs/STATE.md NEXT ACTION 2026-11-05T20:35): ONE capture run testing
whether msg 0x1c01 reaches FLEETWND when the FLEET window holds focus, and
whether the t313 state-table continuation blocks (the t312 writer pair
{0x52003 DAT_43504, 0x51fc2 DAT_43508}) finally stop.

## S0 Pre-flight
- Sitting check: live-timeline.jsonl mtime 20:47 (ring writer alive), newest
  lines turn 1086; 400MB-window max turn 1150 < t313's 1255 -> NO new sitting,
  r1_t85g_sitting.py NOT run. Assignment stands.
- Binding negatives honoured (docs/REFUTED-ROUTES.md t311/t312/t313
  amendments): no STATUSWND legs re-armed, no bare-map digit sender as the
  hypothesis, no offline census on these targets (spent), sprite-pixel select
  DEAD, batmode legs DEAD.

## S1 Legset (planned)
- fn51cc4_entry = 0x51CC4 NEW (FLEETWND msg-handler ENTRY; per t311 entry-leg
  law it fires for ANY msg delivered to FLEETWND; dx = msg id, ret0 = dispatch
  site, magic window rec names the window). Census leg[0].
- w43508_51fc2 (DAT_43508 store, states 1/2/3 of the 0x211188 table)
- w43504_52003 (DAT_43504 store, state 4)
- btn_hdlr 0x336B4 positive control.
Entry bytes of fn 0x51cc4 to be verified vs work/ascend_payload.bin BEFORE the
run (do not arm an unverified address).

## S2 Choreography (planned)
assert_on_map -> open_fleet -> click fleet ROW (FLEET_ROWS[0]) -> digit keys
1..9 WITH THE FLEET WINDOW OPEN (this is the whole point: FLEETWND focus, not
the btn class) -> popup reguard -> NEXTTURN control -> hold. Oracle pair
(DAT_43504/43508 + sel43510 + mode4226 + last-mouse-X 0x484ec) around each
phase.

## S4 RUN 1 (run dir work/r1/t299-leg-20261105-210255, attempt 2 rc=0,
## 21:02-21:13) — MEASURED, BUT THE PHASE HAD A FOCUS DEFECT (caught, fixed)
- Whole-log census: {fn51cc4_entry: 0, w43508_51fc2: 0, w43504_52003: 0,
  btn_hdlr: 3}; census-ctl MATCH=True x6; all disarms liveness=True.
- Banked stops: fleet_keys#0 btn_hdlr win='PLBUILD' edx=0x3 ret0 file 0x3cb8d;
  planet#0 btn_hdlr 'PLBUILD' edx=0x4; control_nextturn#0 btn_hdlr 'Cancel'
  edx=0x4 ret0 file 0x56c77.
- DEFECT (measured, banked as a law): the rowjump click (200,93) CLOSES the
  FLEET window — rails detector (t253 law) 188 at grab 20_fleet.png vs 0 at
  22_fleetkeys_reguard.png. Run-1 order was open_fleet -> rowjump -> keys, so
  the digit keys went to 'PLBUILD' (btn class), NOT FLEETWND. Run 1 therefore
  does NOT test (and does not refute) the FLEETWND hypothesis; it re-banks
  that system-view keys route to the btn class (t311 family).
- Oracle pair fleetkeys_before/after (43.sav -> 50.sav, turn 1087):
  DAT_43504 'Icarus' 0x256825 constant, DAT_43508 0x26f00d constant,
  sel43510 0, mode4226 0x11 (system view), gate_484ec 0xc8 both snapshots
  (>0x96 — the destination-path gate would PASS from the pre-turn click;
  t310's last-mouse-X reading unchanged).
- FIX (scripts/r299_leg_session.py, py_compile OK): fleet-keys phase MOVED
  BEFORE rowjump0; entry gate now `im is None or not fleet_open(im)` -> skip;
  post-arm reguard now ALSO asserts fleet_open(rails)>0 (fail = RUN resumed,
  keys NOT pressed) and logs rails. RUN 2 relaunched 21:2x (loop2 log
  work/r1/t314-loop2.log).

## S5 RUN 2 (run dir work/r1/t299-leg-20261105-212402, attempt 1 rc=0,
## 21:24-21:34) — THE VALID TEST: FLEETWND RECEIVES NO MSG AT ALL
- Focus verified THIS TIME: "FLEET-KEYS: armed RUN ... rails=188" (FLEET
  window open at arm; reguard passed popup AND rails gates). Keys 1..9
  pressed; popup open after keys = False.
- Whole-log census: {fn51cc4_entry: 0, w43508_51fc2: 0, w43504_52003: 0,
  btn_hdlr: 4}; census-ctl MATCH=True; all windows measured
  [fleet_keys, sprite, planet, control_nextturn]; liveness True.
- fn51cc4_entry armed 10x across all windows, FIRED ZERO the whole session —
  the honest-negative branch (2) of the assignment: FLEETWND receives no key
  msgs (and no msg of any kind witnessed) with the window OPEN.
- ONE stop inside the fleet_keys window: btn_hdlr eip 0x1f2b04, win[esi]
  name='STATSHIPLST' (rec member 0xfe7b48), eax=0xfe7ac0, edx=0x3, ecx=0x2,
  ret0 file 0x32943 — call site `ff 56 08` form = call [esi+8] INSIDE
  STATSHIPLST's own slot-2 fn (cp 0x247c70 grid tail {0x324f4, 0x30d08,
  0x32664} read from RAM this session). HONEST CAVEAT: s2_356a5 (the digit
  sender's own call site) was NOT armed in run 2, so attributing THIS msg-3
  stop to the keypresses is inference, not witness; t312 measured the sender
  zero with keys alive in the bare-map shape. What IS witnessed: with the
  FLEET window open, the only msg traffic in the keys window is STATSHIPLST-
  family, and FLEETWND gets none.

## S6 OFFLINE READS (this session, objdump -b binary -m i386 verbatim)
- SENDER FN 0x35696 BRANCH FULLY DECODED (the t310/t312 shape, exact):
  `0x35675 cmp 0x39,ebx / jg bail; mov eax,9; mov dh,[ebp+0xaf];
  sub ebx,0x30; cmp dh,1; jne +5; mov eax,0xa; cmp eax,ebx; jge bail;
  0x35696 mov edx,0x1c01; mov esi,[ebp+0xa7]; mov eax,ebp; xor ecx,ecx;
  call [esi+8]`. THE SENDER'S OWN WINDOW is [ebp] — the KEY handler's window;
  its +0xaf byte (max digit 9, or 10 when ==1) gates the branch. Run 2
  measured s2_356a5 NOT armed (gap named below), but fn51cc4_entry zero
  means: even when the branch DID fire historically, the handler window's
  class was never FLEETWND. The handler window's identity = the next offline
  question (which fn contains 0x35696, which class grid holds it — t313
  grid-scan route applies to a NEW target, cheap).
- fn 0x32fa4 (called at 0x51f4b): `mov [esp+4],edx; mov ecx,edx; ax=dx;
  if (eax<0 || eax>=0x100) error fn 0x2a428; return [[win]+0xc7 + eax*8]` —
  an 8-stride table hung off [[win+0xab]] indexed by the msg arg. So the
  writer-block state byte [eax+0x58] at 0x52059 (`mov 0x58(%eax),%al;
  dec %al; cmp 4; ja -> ret 0; jmp cs:0x3d100(,eax,4)`) reads a TABLE-SELECTED
  record, semantics [unverified]. t313's "system-record" label is not proven
  either way; 9 E8 callers of fn 0x32fa4 {0x15f5a..0x16239, 0x356c9,
  0x51a73, 0x51f4b} — a shared accessor family (the STATUSWND 0x1c01 path
  0x51a73 uses the same call, t310-consistent).
- STATSHIPLST[+0x58] == 0 in 20/20 saves of run 212402 AND 20/20 saves of
  run 192246 (histograms; rec member 0xfe7b48 magic-verified). Datum about
  the rec only — the runtime gate byte was never evaluated (msg never
  arrived).
- Whole-payload store census for the gate byte: `c6/88 [r+0x58],r8/imm8` and
  `89/c7 [r+0x58],r32/imm32` (disp32 forms) = ZERO sites — writers use
  computed offsets (t313 file-blindness law); only a live watchpoint names
  them.
- STATSHIPLST string exists in payload at 0x856c6 (obj1 name pool); FLEETWND
  has no payload string (RAM-named only, consistent t313).
- RUN-2 GAP (name it before it becomes a route): s2_356a5 was not in the run-2
  legset, so "the sender never fires under FLEET focus" is t312-extrapolation,
  not measurement. Any t315 legset MUST include s2_356a5 beside
  fn51cc4_entry.

## S7 VERDICT (strict-close: NO row closed)
- The t313 hypothesis "digit key under FLEET-window focus reaches FLEETWND's
  0x1c01 path" is REFUTED by run 2 (valid focus, entry leg leg[0] zero). The
  key focus while the FLEET window is open belongs to STATSHIPLST (btn-family
  class 0x247c70), and msg 0x1c01 is only sent past the ASCII+shift gates
  which the synthetic keys did not pass (digit branch not taken; msg 3
  delivered instead).
- OQ-019 residue RE-SCOPES to two concrete, measured things:
  (a) FLEETWND msg intake: never witnessed at all — the one untested shape is
      a click INSIDE the FLEET rect while armed (rowjump0 has always run
      leg-free; sidebar (553,184) opens the window but its click goes to the
      underlying window).
  (b) THE STATE BYTE STATSHIPLST[+0x58] (const 0 x 40 saves): the hard gate
      in front of every writer block. Someone must make it 1..5; offline
      writers are unfindable (computed offsets) -> live watchpoint route.
- Honest negatives banked: fn51cc4_entry 0 with FLEET open; writers 0; the
  destination-widget hunt has now been validly attempted from the key side
  and failed — it is NOT one digit key away.

- 20:5x LAUNCH: scripts/r314_relaunch.sh (NEW, cloned from r312) backgrounded,
  loop log work/r1/t314-loop.log, attempt console work/r1/t314/attempt-N-
  console.log. LEGSET fn51cc4_entry,w43508_51fc2,w43504_52003,btn_hdlr.
  Flags: --census --star-click 0 --target-kinds sprite,planet --pre-turn 1
  --digit-keys 0 --fleet-keys 9 --window 60 --disp 97 --port 55999 --tl 7200.
- Script delta (scripts/r299_leg_session.py, py_compile OK):
  1. NEW LEG fn51cc4_entry = 0x51CC4. Entry bytes payload-verified this
     session: `56 57 55 81 ec bc 01 00 00 89 c7 66 89 94 24` (push esi/edi/
     ebp; sub esp,0x1bc; mov edi,eax; mov [esp+0x1b4],dx) — edx AT THE STOP is
     the msg id (same prologue law as the t311 fn51834_entry leg).
  2. NEW PHASE --fleet-keys N: runs AFTER open_fleet + rowjump0 (im != None
     required, else skipped); oracle fleetkeys_before -> arm_census -> post-arm
     popup reguard (t311 law) -> EXEC RUN -> keys '1'..'N' @1.2 s -> grab
     popup state -> census_window(60 s) -> disarm_run -> close_eventwin if a
     popup opened -> oracle fleetkeys_after. census key = "fleet_keys".
  3. r312's digit-block ordering stands (digit-keys 0 = phase skipped).
- Pre-launch hygiene: port 55999 free; production dosbox pid 1957 (:9) alive
  and untouched; scratch dirs per session script (R293.SCRATCH, never game/).

