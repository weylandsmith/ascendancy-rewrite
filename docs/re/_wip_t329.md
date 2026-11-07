# _wip_t329 — OQ-019 DISPOSITION PACKET (drafts only; row closes on USER ruling)

Session: fresh 2026-11-06 ~22:50 EST. Assignment: STATE.md NEXT t329, whose
condition ("only if t324 landed NEGATIVE-ABSOLUTE") is met (LANDED t324).
Sitting check FIRST: playcap/live-timeline.jsonl tail-seek newest turn 1086 ==
corpus -> no new play, r1_t85g_sitting.py NOT run. Production :9 (pid 1957)
untouched. Zero capture, zero guest boot this iteration.

## S1. MAGNETRON CARRIAGE CENSUS (measured this iteration)

scripts/r329_magnetron_census.py (NEW, exit 0; laws imported from t101/t184/
t185, NOT re-derived; bounded named-dir inputs per OOM law):

  PRODUCTION corpus work/r1/playcap/save (the t=1086 sitting):
    saves=20 ship_rows=600 cidx60 (Lane Magnetron) slots = 0.
  SCRATCH drive epochs that DID carry magnetrons (owner 0):
    t261-drive/save                    saves=20 cidx60=360
    t288-probe-dbg-a0-...104330/save   saves= 5 cidx60= 18
    t288-probe-rel-a0-...104942/save   saves=16 cidx60=216
    t288-probe-rel-a0-...110123/save   saves=16 cidx60= 18

Reading: the production residue is ABSENCE (no carrier exists at t=1086), but
carriage alone never produced a witness — across the t261/t288 epochs the
use-frame mines t265 (off-grid instrument, P(false neg)<0.1%), t273 (K3
st->5 transition hunt: 0) and t285 still returned ZERO magnetron uses.
=> the residue is WITNESS-CLASS, not absence-only: presence + drive sessions
+ zero uses is already measured. (r1_t185_magnetron_census.py re-run green
this session: loaded table == file order, cidx60 total 630 across all saves.)

## S2. THE ARMING ROAD — WHY THE SCRIPTED MAGNETRON IDEA IS CITED-DEAD

Claim under test (from DECISIONS.md D3 line "magnetron -> needs one witnessed
use; scriptable via the t289 drive class"): that a scripted drive session can
witness a magnetron USE. Measured/verified this session (work/
t91_code_disasm.txt verbatim; Ghidra MCP reachable but no program loaded —
offline method per t323):

1. COMMIT LAW (t88a, re-read this session at 0x2550c..0x2559d): gizmo effects
   commit ONLY via fn 0x2547c edges 0x25560 (ah==3 -> call 0x49f28) and
   0x25570 (ah==2 -> call 0x39c10), after resolver 0x41260 returns command
   byte ah. All AI/volley/batmode paths are mode-0 dry runs (t88a census).
2. The commit edges fire during TURN RESOLUTION with no window traffic — but
   they only reach the magnetron case (0x4ca50 case 0x3c, t185 §19 T3) when
   the ship ALREADY carries the armed order: BYTE [ship+0x62]=1, DWORD
   [ship+0x63]=slot ptr, BYTE [ship+0x67]=kind, [ship+0x68]=target.
3. ARMING TAIL re-verified verbatim this session at 0x15c63..0x15c85:
   `mov edx,[ebp+0xac]` (ship) then `mov BYTE [edx+0x62],al / mov DWORD
   [edx+0x63],eax / mov BYTE [edx+0x67],al` — fed from the window's STATE
   dispatch at 0x15c38 `mov eax,[ebp+0xb1]` (state WORD -> al compared 0x2/
   0x3/0x4 selecting the order shape; second identical tail at 0x15da6,
   probe call sites 0x15cc5/0x15df0 labelled "batmode" by the t88 caller
   census; 0x16ee1 likewise).
   [ebp+0xb1] is EXACTLY the field t323 proved has NO in-session writer for
   BatModeWnd (14-site census; only runtime switcher fn 0x31f30 <- fn 0x32100
   NOT in the cited class table), and t324 measured fn 0x32100 ABSENT from
   the live RAM class table 10/10 saves. t322 additionally measured
   BatModeWnd receiving ZERO msgs in-view (batmode legs armed live-first-time,
   control alive).
4. SCOPE CAVEAT (honest, do not overstate): no census t296..t324 NAMES the
   specific window record [ebp] owning the 0x15xxx arming block — the
   "same widget path" identity is [inferred] from (i) the t88 "batmode"
   family labels, (ii) the [ebp+0xb1] state-WORD gate shape being the t323
   pinned-field, (iii) the mode-0 probe law covering every batmode path.
   t322's armed-zero covers BatModeWnd's own legs specifically, not the whole
   0x15xxx family. The retirement is therefore cited-but-indirect — the same
   closure class t323 accepted for the activation law.

VERDICT on the scripted idea: RETIRED. The only road that arms a gizmo-use
order runs through the batmode family's pinned state WORD; the production
sitting has no carrier at all (S1); and in the epochs that DID carry, zero
uses occurred across three independent mines (S1). A debugger leg at
0x25560/0x25570 in a magnetron-carrying scratch session is the one residual
instrument shape — its expected result is confirming absence the saves
already show (t265 K3 st->5 hunt was exactly that test at save cadence).
This retires the last scripted-capture idea in DECISIONS.md D3 honestly.

## S3. DEAD-ROUTE CLOSURE TABLE (every OQ-019 capture route, cited)

| residue | route | status | citation |
|---|---|---|---|
| select/destination (msg 0x50 widget, DAT_43508/0x43504 stores via fn 0x1b5e6/0x1baa7) | broadcast pump poster | DEAD | t319: poster fired 1x msg-4 only; t320: 27/27 msg-4, zero 0xc; ds:0x484ac = BIOS int16h button word (50-ms pulse cannot cover ~20 s poster period) |
| " | batcon mouse road | DEAD | t322: batmode legs armed live-first-time, whole-log zeros, control alive, instrument census MATCH=True |
| " | activation decode | DEAD (census-complete) | t323: [win+0xb1] writer census 14 sites; sole runtime switcher fn 0x31f30 <- fn 0x32100 NOT in cited BATMODE table; law is STATIC (sitting-independent) |
| " | RAM class-table re-open check | DEAD ABSOLUTE | t324: scripts/r324_census.py — live RAM table == cited BATMODE 6/6 slots, fn 0x32100/0x31f30/0x339a4 ABSENT, 10/10 saves identical |
| " | scripted order capture (t293 shape) | DEAD (budget spent + explained) | t293 negative (dots are kind-3 planet clips); t296 closed selection statically (4 cited gates); t312 sprite-pixel select refuted; t315 digit->0x1c01 is a LOADSCREEN menu mechanism |
| sugar-cube arrival granularity | corpus mining | CLOSED class | t49/t58/t265 corpus-mining class CLOSED; st4 in-system march resolves inside one turn boundary (t265, 21 runs d=0.00) |
| per-ship build/redesign path | (not an RE unknown) | DECISION | t256c census 62,762 rows; AI dossier GAP->BOUNDARY; = D2 |
| magnetron witnessed use | corpus x3 | ZERO x3 | t265 (P(false neg)<0.1%), t273, t285; carriage proven S1 this session |
| magnetron witnessed use | scripted (t289 drive class) | DEAD (cited-indirect) | S2 above: batmode-family pinned-state arming road; production carrier count 0 |

## S4. DRAFT FINAL OQ-019 ROW TEXT — DO NOT APPLY (USER ruling required)

DRAFT (replaces the row's RESIDUE block + status line ONLY on USER ruling;
apply = edit docs/OPEN-QUESTIONS.md verbatim from this block):

  OQ-019 | ships | per-ship design model (hull+gizmo inventory), sugar-cube->
  hop scale, vendor cost hack, Orbital Docks effect
  | USER-RULING-REQUIRED (loop-side work complete t329; NOT closed — strict-
  close) | CLOSED PORTION unchanged [existing text stands verbatim: gizmo
  record law, cost hack t16, inventory law t46, Orbital Docks §12-13, BUDGETS
  t101, SCALE t183, LANE-STEP + TURN-ATOMICITY, st4 DWELL, magnetron use-site
  static law t185 §19].
  RESIDUES — FINAL DISPOSITION (all capture routes cited-dead; packet
  docs/re/_wip_t329.md S3):
  (1) sugar-cube per-turn clamp/arrival granularity + per-ship select +
      msg-0x50 destination widget = UNREACHABLE-BY-CAPTURE. Static law stands
      (t296 S5 four gates; t321 S1-S4). Dead-route chain: t319/t320 pump
      (poster never posts 0xc), t322 mouse (zero msgs in-view, instrument
      verified), t323 activation (census-complete, static, sitting-
      independent), t324 RAM class table (fn 0x32100 ABSENT 10/10 saves,
      scripts/r324_census.py). Re-open condition discharged NEGATIVE
      ABSOLUTE — no capture instrument remains.
  (2) per-ship build/redesign path = BUILD DECISION, not RE unknown (t256c
      census 62,762 rows; ai-dossier = spec). Closure = D2 ruling:
      (a) boundary accepted [row closes as boundary-documented], or
      (b)/(c) commission (row closes at delivery).
  (3) magnetron witnessed use = WITNESS-CLASS LIMITED: carriage measured
      (scripts/r329_magnetron_census.py: 0 carriers at t=1086; 360+252
      owner-0 slots in t261/t288 epochs), zero uses across t265/t273/t285;
      scripted road cited-dead (_wip_t329 S2, batmode-family pinned-state
      arming). Use-site LAW stands static-cited (gizhelp.txt:1173-1181 +
      0x4ca50 case 0x3c t185). Row-level: accept static citation (R13 class)
      or name the instrument.
  REWRITE IMPACT: none pending — rewrite models cited laws only; residues
  are boundary-documented, silently-stubbed nowhere (GOAL constraint holds).

## S5. DECISIONS.md D3 UPDATE (applied this iteration; text below is what D3 becomes)

D3 currently claims closures still have routes ("OQ-019 -> sugar-cube scale:
t293 scripted move-order capture (queued NOW)"; "magnetron -> scriptable via
the t289 drive class"). Both are now cited-dead. Actual state after t329:
- OQ-019: loop-side work COMPLETE; closure requires USER ruling (D2
  commission, or accept boundary + cited-dead notes; packet = this file S4).
- OQ-005: adjudicable subset requires USER ruling (D1); t328 (queued) will
  convert the no-witness-possible records (cos_star k40..k51, 25 ladder
  slots, explosions, 3cfgnew) to CITED-NO-WITNESS and may design a
  draw-capture for mouse/1starmap if statically reachable.
- OQ-016: loop-runnable captures REMAIN (t325 shield-byte witness, t326
  phase-bomb forced-capture) — the ONLY row with live loop-side closure
  potential left; residue (5) build-order minutiae stays a diminishing
  corpus tail.
So: rows closeable by the loop WITHOUT user input = NONE end-to-end
(OQ-016 needs t325+t326 positive AND residue (5) dispositioned); the queue
t325-t328 can still MOVE rows, it cannot close the ledger. D1 + D2 remain
the user's two asks; D4 unchanged.
