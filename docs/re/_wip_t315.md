# t315 — DIGIT-HANDLER WINDOW HUNT (OFFLINE, ZERO capture; hand-authored)

Task (docs/STATE.md NEXT ACTION 2026-11-05T22:05): name the window/class whose
msg handler contains the digit sender at payload 0x35696 (t314 S6: it sends
edx=0x1c01 ecx=0 via call [esi+8] on ITS OWN window [ebp]). Steps: (1) fn
boundary + E8 census; (2) RAM grid scan of run 212402 save for entry+P0 ->
magic rec name; (3) resolve the STATSHIPLST lead by span walk. NO capture.

## S0 Pre-flight
- Sitting check: live-timeline mtime 22:33 (writer alive); 1.5GB tail window
  60740 turn-lines, max turn 1255 == t313's value, newest lines 50/51/52.sav
  t=1086 (restored state) -> NO new sitting; r1_t85g_sitting.py NOT run.
  Assignment stands.
- Binding negatives honoured (t311/t312/t313/t314 amendments): no capture, no
  fn51cc4_entry re-arm for keys, no STATUSWND legs, no bare-map senders, no
  fn 0x51b68 offline census. NEW target 0x354f8 is explicitly authorized by
  the assignment ("extend r313 pattern to a NEW target").

## S1 STEP 1 DONE — fn BOUNDARY + DISPATCH MAP (objdump -b binary -m i386, verbatim)
- ENTRY = 0x354f8. Prologue `56 57 55 81 ec 44 01 00 00` (push esi/edi/ebp;
  sub esp,0x144) occurs at exactly TWO payload sites: 0x1cf23 and 0x354f8 —
  boundary is unique. Frame law: eax->ebp (window), dx saved +0x140, ebx saved
  +0x13c, ecx saved +0x138. Epilogue `81 c4 44 01` at 0x35557/0x35666/0x356af/
  0x35880; fn span [0x354f8, 0x35899) (next prologue `53 51 56 57 55` at
  0x3589c after 0x35899 lea-pad).
- E8 CENSUS of 0x354f8: ZERO callers (whole-payload rel32 check) —
  table-dispatched, exactly like STATUSWND/FLEETWND handlers. (0x1cf23 also
  zero — sibling window of the same frame shape, not our target.)
- DISPATCH MAP (raw-verified at 0x35519..0x3554e):
  - `cmp $0x3,%dx; jb 0x3588a; jbe 0x35670` -> dx==3 EXACTLY -> 0x35670 THE
    DIGIT BRANCH (t314 S6 shape verbatim: gate ebx in 0x31..0x39, digit-max
    [ebp+0xaf]==1?10:9; fire: mov edx,0x1c01; esi=[ebp+0xa7]; eax=ebp;
    ecx=0; call [esi+8] at 0x356a5). Non-digit msg 3 -> 0x35662 return 0
    (NOT forwarded to 0x336b4!).
  - `cmp $0x1c01,%dx; je 0x356b9` -> THE 0x1c01 RECEIVER IS FN 0x354f8 ITSELF:
    0x356b9: eax=win; eax=[win+0xab] (the 8-stride table set at 0x355b2 by
    fn 0x56d1c); dx=ebx (the digit char, saved at entry +0x13c); call fn
    0x32fa4 (t314's 8-stride accessor) -> rec; reads [rec+0x6c], formats via
    fn 0x76c79 + string 0x1b4a, displays via fn 0x20728; then branches on
    [ebp+0xaf]: ==1 -> fn 0x53fe8 + fn 0x56ad4(0x7a35c,3); ==0 ->
    `cmpl $0xffffffff,[esi+8]` guard loop via fn 0x53f50 + globals
    0x7eab4/0x7ea92/0x7eab2; both roads end fn 0x598fc/fn 0x56ad4 + fn 0x20778.
    => THE SENDER AND RECEIVER ARE THE SAME FN = SELF-SEND 0x1c01.
  - dx<3 other (dx!=1): jmp 0x35534 generic: edx>>=16 then call 0x336b4
    (btn_hdlr). dx>3 && !=0x1c01: same 0x35534 path.
  - dx==1 -> 0x35561: MODE HANDLER — `mov 0x7e582,%eax; sar $0x10,%eax`:
    hw==2 -> [ebp+0xaf]=1; hw==4 -> [ebp+0xaf]=0; else -> [ebp+0xaf]=2; then
    fn 0x56d1c(0x7a35c, str 0x1b2a/0x1b32/0x1b3a, 0x1b41) whose result is
    stored [ebp+0xab] (the 8-stride table fn 0x32fa4 indexes). bl==2 branch
    writes word 0x3c @ [[ebp+0xab]+0x8c9] + fn 0x33458(0x20838) + fn 0x35a60;
    else word 0x55 + fn 0x33458(0x20170) + fn 0x35938. => digit-max byte is
    GLOBAL-DRIVEN: DAT_7e582 >> 16, never per-ship.
- STEP 3 RESOLVED ALONG THE WAY (span walk): STATSHIPLST slot-2 fn 0x32664
  ends at the ret group 0x32943..0x3294c (ret0 0x32943 = run-2 witnessed stop,
  t314 S5) with lea-pad at 0x3294d and next fn at 0x32950. Span ~[0x32664,
  0x3294d) does NOT contain 0x354f8. The digit handler fn is NOT
  STATSHIPLST's slot-2 fn. (t314's run-2 msg-3 stop stays a btn-family
  forward; the digit branch never ran in run 2 — consistent with fn51cc4=0 and
  s2_356a5 t312-zero.)

## S2 STEP 2 DONE — RAM GRID SCAN (scripts/r315_handler_scan.py, runs 212402 + 192246)
- P0 RE-DERIVATION LAW (new, measured): payload BYTES map to RAM at B+off
  (string/code-pattern hit gives B=0x1bf4d8 both runs), but u32 CODE POINTERS
  carry P0 = B-0x88 = 0x1bf450 (vtable slot 0x248050 holds 0x210c84 =
  0x51834+0x1bf450). A string-offset P0 (hit-0x856c6) returns 0x1bf4d8 and
  makes every pointer scan blind — first-run trap, fixed in the script.
- TARGET fn 0x354f8+P0 = 0x1f4948: EXACTLY 1 RAM hit @0x247db0, grid base
  0x247da8 stride-6, SLOT 2 (msg-handler slot, same shape as every named
  class). Slots: {0x354ac, 0x30d08, 0x354f8, 0x3589c, 0x311b8, 0x316f0}.
- cp = grid_base-0x88 = 0x247d20 (ADDRESS, not deref — deref = t310 trap, hit
  in-script). Refs named by magic rec at ref-0xa7: rec 0xfd7103-0xa7... =
  0xfd705c NAME='LOADSCREEN'. Reproduced 212402/41.sav, 212402/58.sav,
  192246/58.sav (3/3). LOADSCREEN rec fields: magic 0x12345678, +0xa7=cp,
  +0xaf=0 (digit-max MODE byte), +0xab=0 (8-stride table never allocated).
- CONTROLS: fn 0x51834+P0 exactly 1 hit @0x248050 (5th reproduction); fn
  0x51cc4+P0 exactly 1 hit @0x248038; sibling fn 0x1cf23 ZERO hits (menu-time
  only class).
- RUNTIME PATCHING PROVEN ON THIS CLASS: fn 0x31710 (cp+0x08) file imm
  0x5ca0 -> runtime imm 0x247ca0 (cp-region RAM, +0x82bb0 relocation); code
  bytes of the sender site 0x35696 UNPATCHED (ff 56 08 direct); DAT_7e582's
  runtime absolute read FROM CODE BYTES at B+0x35561 = 0x2c0582 (do not guess
  P0+off for data — read the patched immediate).

## S3 THE ANSWER — THE DIGIT-HANDLER WINDOW IS LOADSCREEN (loadwin.cpp family)
- Payload name pool corroborates: 0x846da 'savescr', 0x846e2 'loadscr',
  0x846f1 'LOADLIST', 0x846fa '%02d.sav', 0x84716 'tutindex.txt',
  0x84726 '..\loadwin.cpp' (strings verified in work/ascend_payload.bin).
  fn 0x354f8's dx==0x1c01 receiver formats via fn 0x76c79 + string 0x1b4a and
  displays via fn 0x20728; the dx==1 mode handler builds its [win+0xab] table
  via fn 0x56d1c(0x7a35c, strings 0x1b2a/0x1b32/0x1b3a) — a save/load/tutorial
  list screen, NOT any in-game map/fleet surface.
- => THE 0x1c01 KEY ROUTE IS DEAD BY CONSTRUCTION for in-game selection:
  digit keys talk to the LOADSCREEN window family. FLEETWND can NEVER receive
  0x1c01 from keys (t314's zero is now EXPLAINED, not just measured).
  REFUTED-ROUTES t315 amendment filed.
- SENDER INVENTORY (whole-payload literal 0x1c01 census = exactly 5 sites):
  0x16169 (relay, call [ebx+0xc] on own window; owner fn entry 0x156d7 —
  t311-dead shape), 0x1642c (owner fn 0x16420: `cmp $0x1c01,%edx; je 0x16437`
  = a RECEIVER that copies [ebp+4..] 0x1d2x0x27f block when 0x1c01, else
  tail-calls fn 0x16754), 0x33375 (mov $0x1c01,%ebx msg builder via fn
  0x56ca4(0x7a35c) — an internal msg-emit helper, not a window call),
  0x35697 (the LOADSCREEN digit sender), 0x1756b FALSE POSITIVE (E8 rel32
  bytes `e8 01 1c 00 00` = call 0x19170 — census must exclude instruction
  operands). No in-game-window sender of 0x1c01 exists in the image.

## S4 SECONDARY MEASUREMENTS
- DAT_7e582 (runtime 0x2c0582) == 0x00000000 in 433/433 saves across ALL
  t299-leg run dirs. High word 0 -> [win+0xaf] would take the 'else' arm (=2)
  if the dx==1 handler ever ran; LOADSCREEN[+0xaf]==0 observed. Consistent:
  the LOADSCREEN window is alive only at the load/menu screen; in-play saves
  hold the mode global at zero.
- t313's RAM table 0x211188 re-verified in 212402/58.sav: pattern
  {0x51fb5 x3, 0x51ff6, 0x52037} whole-RAM unique (1 hit). CAUTION: the byte
  at 0x211188+0x58 is 140 — that address is the JUMP-TABLE data, NOT the
  state-record; the 0x52059 gate byte lives at [accessor-result]+0x58 where
  accessor = fn 0x32fa4 on [[win]+0xc7+idx*8] — do not conflate (t314
  table-selected caution stands).
- DISPATCH SEMANTICS RAW (fn 0x30d08 = grid slot 1 of every class): a
  MOVE/RESIZE fn (adds dx to [win+8], bx to [win+0xc], also +0x10/+0x14).
  The class vtable cp[+0x8] = fn 0x31710 = set-class-string fn (movl
  $0x5ca0,[eax+0xa7] runtime-patched + flag-bit dispatch to fn 0x30ad8/
  fn 0x76cd4). So the sender's `call [esi+8]` (esi=cp) is NOT the msg path —
  the msg path is `call [esi+0xc]` (0x30d37 law). The 0x35696 sender calls
  [esi+8]: banked verbatim, semantics [unverified] whether that is a vendor
  bug masked by [win+8]==7 no-op-ish reads or a different dispatch contract;
  live behavior unmeasurable for LOADSCREEN in-play.

## S5 VERDICT (strict-close: NO row closed)
- THE t315 QUESTION IS ANSWERED WITH CITED MEASUREMENT: the digit-handler
  window = LOADSCREEN (grid base RAM 0x247da8, cp 0x247d20, magic rec
  0xfd705c, 3/3 saves, both runs; controls 1-hit exact). The digit->0x1c01
  route is a MENU-SCREEN mechanism (save-slot pick '%02d.sav'); NO in-game
  window class contains a 0x1c01 digit handler and NO in-game-window sender
  of 0x1c01 exists (5-site literal census, one false positive excluded).
- OQ-019 CONSEQUENCE (row STAYS OPEN — no live store witnessed): the
  destination-writer chain {0x52003, 0x51fc2} of FLEETWND cannot be reached
  via ANY key path; the remaining live hypothesis is the FLEETWND msg intake
  via a click INSIDE the FLEET rect (t314 S7 residue (a)) and/or the state-
  byte watchpoint route (t314 S7 residue (b)). Key-driven shapes are now
  dead-by-mechanism, not just dead-by-measurement.
- Honest negatives banked: sibling fn 0x1cf23 zero RAM hits; LOADSCREEN
  +0xab=0 (table never allocated in-play); DAT_7e582 zero 433/433.

## S6 ACCESSOR RESOLVED EXACT + THE GATE RECORD IS MEASURED (late session)
- fn 0x32fa4 body verbatim: `mov 0xc7(%esi,%eax,8),%eax` — an INDEXED LOAD
  from the window at 0xc7 + idx*8 (NOT a hop through [[win+0xab]] as t314
  phrased; the value law holds, the addressing is now exact).
- CALLER 0x51f3b (FLEETWND 0x1c01 path head) verbatim: eax=[win+0xab];
  dx=msg char (frame +0x1b0); call fn 0x32fa4 -> esi=GATE RECORD; if ecx==5
  confirm-leg branch (string 0x2b6b); else jne 0x52059 GATE:
  `mov 0x58(%eax),%al; dec %al; cmp 4; ja ret0; jmp *cs:0x3d100(,%eax,4)`.
  Table arms READ THE RECORD: state1/2/3 `mov 0x59(%edx),%eax ->
  DAT_00043508` (0x51fc2), state4 `mov 0x59(%esi),%eax -> DAT_00043504`
  (0x52003) — the destination datum is record field +0x59..0x5c.
- CHAIN MEASURED (correct base = the magic rec itself, 0xfe7a90; an earlier
  probe this session used 0xfe7ac0 as the window and hit the name-string area
  '...SHIP' at +0xab — WRONG base, corrected): win=[0xfe7a90+0xab]=0xfe7ac0
  (the FLEETWND instance block, name 'fleetwin' at +0x48); slot0 =
  [0xfe7ac0+0xc7] = 0x600000. GATE RECORD = guest-physical 0x600000:
  gate byte [rec+0x58] = 0x600058 == 0 and datum 0x600059..0x60005c == 0 in
  212/212 saves with a valid chain; the other 221 saves hold
  [win+0xab]==0x0 -> the accessor would take its error path (fn 0x2a428).
  Record block 0x600000..0x600078 all-zero (212402/58 raw dump).
  => THE WATCHPOINT TARGET FOR THE NEXT ITERATION IS GUEST 0x600058 (the
  state byte in front of every writer arm) — file census blind (t314 law).
- fn 0x56ca4 = the msg-emit helper: reads [[obj]+0x4226] (mode4226 law,
  view id), bails if high word < 0, indexes [obj + edx*12 + 4] -> window ->
  [win+0xa7] cp. Its 56 E8 callers include 0x3339c (the 0x1c01/0x1c02 builder
  site 0x33374) — an INTERNAL emit path, owner class of fn 0x33xxx family;
  not a key path. (Banked for the watchpoint iteration; no census spent on
  it — it is a NEW target.)
- SECOND 0x1c01 RECEIVER NAMED (grid scan, NEW target, 212402/58): fn 0x16420
  (receives 0x1c01 -> copies [ebp+4] block 0x1d2 x 0x27f; else tail-calls fn
  0x16754) is slot 3 of grid 0x2478d8, cp 0x247850, magic-named
  'BatControlWnd'. fn 0x16754 and fn 0x156d7 (relay 0x1616f owner) are NOT
  grid slots (0 hits) — mid-body or helper shapes.
