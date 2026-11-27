# _wip_tPF7a — PER-MSG RELEASE-MASK SPLIT (0x38 vs 0x39), ebp ROLE (TPF7-A)

Working log; on landing distil into docs/re/research.md S10 seam note.
Assignment: STATE.md NEXT ACTION 2026-11-26T13:40 (post-tPF-1c). Steps:
(1) re-read 0x47d3b + press tail 0x47c48; (2) find the dispatcher that turns
the queued slot into the handler's ebp (0x56ca4 chain); (3) if ebp == queued
param verbatim, the mask law FOLLOWS -> ship + pins; else honest negative,
row stays open.

## P0 SITTING
- work/r1/playcap/live-timeline.jsonl mtime Nov 26 00:30 < HEAD (Nov 26
  17:35). No new sitting since the last iteration; assignment stands.
  (tPF-7's own sitting check tPF7_pre_sitting.out: trusted rows 45,227,
  newest t=1335.)
- Tree clean at session start (9472ac2).

## P1 RELEASE LEG + PRESS TAIL VERBATIM (fresh disasm, this session)
raw: /tmp/tPF7a_release_tail.asm /tmp/tPF7a_release_leg.asm (regenerate:
~/tools/revenv/bin/python scripts/t442_disasm.py 47c40 47e20)
- PRESS TAIL 0x47c48 (VERBATIM): `cmp ebp,4 / jne 0x47718` -> ONLY kind-4
  presses arm a release. Then `movsx edx,di / cmp edx,0x34 / je +1 /
  cmp edx,0x35 / jne keep / mov eax,1` where eax was initialised
  `mov eax,ebp` (0x47c54). Queue call 0x47c7a:
  eax=0x7a35c(screen), edx=[esi+0x41](target win), ecx=0x38, ebx=1,
  push eax, push 0. => THE PRESS ALWAYS ARMS MSG 0x38 (never 0x39); the
  PARAMETER carried is (pressmsg==0x34/0x35 ? 1 : ebp(=4 verbatim)).
  ANSWER to seam step (1): the 0x38-vs-0x39 split is NOT press-side —
  press->0x38 always; the split is in the PARAM (1 vs 4).
- RELEASE LEG 0x47d3b (VERBATIM, msg 0x38/0x39): `mov ebx,[0x764c4];
  not ebp; and ebx,ebp; mov [0x764c4],ebx` then `mov ebx,-1; call 0x56730`
  (cancel pending). ebp at handler entry = ebx of the dispatch call
  (entry 0x47614: `mov ebp,ebx`; esi=eax=window, edi=edx=msg id,
  [esp+8]=ecx). So mask = ~param: param 1 -> clears bit0; param 4 ->
  clears bit2.
- PUMP GATE SHAPE 0x47c88 (VERBATIM re-read): rot: `test ah,4 je skip`
  (bit2 = ROT GATE), `test ah,8` -> delta -3.0 else +3.0 (bit3 = DIR).
  move: `test dh,1 je skip` (bit0 = MOVE GATE), `test dh,2` -> +1.0 else
  -1.0 (bit1 = DIR). => latch is TWO (gate,dir) pairs: move=(bit0,bit1),
  rot=(bit2,bit3). Mask ~1 kills the MOVE gate; mask ~4 kills the ROT gate.
  CONSISTENT: move press arms param 1 (kills move gate), rot press arms
  param 4 (kills rot gate) — the per-msg split IS gate-of-the-pressed-pair,
  IF the queued param survives to the release handler's ebp.
- OPEN CRUX: does 0x5669c's pushed param become the handler's ebx at
  dispatch? Trace 0x5669c -> 0x59bf4 -> queue win+0x48c2 -> dispatcher
  0x56ca4 -> handler call regs. 0x56374 signature (P5 tPF7) is
  (eax screen, edx target, ecx PARAM, ebx MSGID, [esp+0x14] interval,
  [esp+0x18] flag2) — 0x5669c uses the SAME arg order shape but
  ecx=0x38(msgid?) ebx=1 push eax(param?) push 0: roles NOT yet verified,
  do not assume.

## P2 DISPATCH CHAIN DECODED — ebp IS THE QUEUED PARAM VERBATIM
(fresh disasm 0x5669c full, 0x56ca4, 0x56608 tail, 0x56730 full, 0x56798
one-shot queue walker; regenerate: t442_disasm 5669c 56730 / 56ca4 56ce2 /
565f0 5669c / 56730 567e2 / 567e0 568b0)
- QUEUE WRITER 0x5669c(eax=screen, edx=target, ecx=MSGID, ebx=filter,
  [esp+0x10]=param1, [esp+0x14]=param2). Slot stride 0x12 at win+0x4610:
  +0 target, +4 filter (u32), +8 msgid (u16), +0xa PARAM1 (u32),
  +0xe param2. Press tail stores param1 = eax where eax = ebp(=4) default,
  OVERRIDDEN to 1 iff msg==0x34/0x35 (0x47c54..0x47c60). CORRECTION to the
  earlier "push (msg==0x34/0x35 ? 1 : 0)" note: the else-value is ebp=4
  VERBATIM, not 0.
- ONE-SHOT DISPATCHER = leg-1 of the queue walker 0x56798 (0x56813..0x56848):
  `mov ecx,[slot+0xa]` (0x5683d — PARAM VERBATIM), msgid via dword[+6]
  sar 0x10, then `call 0x56ca4`. LEG-2 (0x56864, passes global 0x484ec as
  ecx) is DEAD for our slots: its gate is `[slot+4] & [esp]` and [esp] only
  ever gets |=4 (bit2, 0x567e2), never bit0; our slot filter is 1.
- FRAMEWORK DISPATCH 0x56ca4: `mov ebx,ecx` (0x56ca6/56caa) — ebx is the
  CALLER's ecx verbatim — widget ptr from [screen+edx*5*4+4], vtable
  `[widget+0xa7]+8` called with edx=msgid, ebx=param. Handler entry
  0x47614: `mov ebp,ebx` (0x4761e). CHAIN CLOSED:
  press param (1|4) -> slot+0xa -> 0x5683d ecx -> 0x56ca4 ebx -> 0x47614 ebp.
- MASK LAW (FOLLOWS): 0x47d3b `latch &= ~ebp`:
    release armed by UP(0x34)/DOWN(0x35) press: ebp=1 -> clears bit0 =
      the MOVE GATE bit (dir bit1 survives);
    release armed by LEFT(0x32)/RIGHT(0x33) press: ebp=4 -> clears bit2 =
      the ROT GATE bit (dir bit3 survives).
  i.e. per-press release mask == the pressed pair's GATE bit; DIRECTION
  BITS ARE NOT CLEARED. Pump gates on the gate bit first (0x47c8e test ah,4
  / 0x47cd6 test dh,1 je skip), and the press table re-normalises dir on
  every start leg ((0,x)->(1,0) / (0,x)->(1,1)), so gate-only vs
  pair-clear is BEHAVIOURALLY EQUIVALENT through the press/pump paths —
  proof: enumerate all 4 start legs per pair, post-release state (0,dir)
  reaches the same next-press state as (0,0).
- FIRE LOOP 0x56608 tail re-confirmed: repeating slots dispatch via the
  SAME 0x56ca4 (0x56839? no — 0x56689) with ecx=[slot+6] param, ebx=msgid;
  msg 0x29a special-cased 0x56677.
- CENSUS (imm32 scan of obj0 code): 0x38 appears as an immediate at exactly
  12 sites incl 0x47c68 (the reswin press tail — the ONLY 0x38 producer in
  the reswin module); 0x39 has 14 imm32 sites, NONE in [0x47614,0x47e20]
  (reswin handler range) -> the 0x39 dispatch arm of 0x47d3b has NO
  producer inside reswin; 0x39 is another window's release id that merely
  shares the handler shape. reswin's own second 0x5669c caller 0x477ad:
  msg id read next.

## P3 ebp ROLE ANSWERED — LAW CLOSED STATICALLY (steps 1-2 of the
## assignment are DONE; ebp == queued param verbatim, chain cited above)
- PRESS-KIND: ebp at the latch block is the framework press-kind arg (the
  windows.txt SENDPARAM1=999 is NOT ebp — dispatch entry takes ebx). The
  arm-gate `cmp ebp,4` fires on ordinary mouse presses; param pushed =
  (msg 0x34/0x35 ? 1 : ebp) and ebp==4 on that path => param in {1,4}
  exactly. THE EARLIER SEAM NOTE "push (msg==0x34/0x35 ? 1 : 0)" is
  CORRECTED: else-value is 4 (0x47c54 `mov eax,ebp` precedes the cmps).
- WHO ELSE QUEUES 0x38 INTO RESWIN: nobody. `mov ecx,0x38` occurs at
  exactly 1 site in the whole image (0x47c67, the reswin press tail); the
  imm32 census agrees (12 sites, reswin's is the only one in
  [0x47614,0x47e20]). reswin's OTHER 0x5669c caller 0x477ad queues msgid
  8 (0x8) filter 4 param 0 — a DIFFERENT msg (0x8 arm -> 0x47b33, not the
  release leg). msg 0x39/0x3a as SENDMESSAGE ids belong to COSMOSWnd
  (windows.txt:336/354/390 CENTERHOLO/TOGLANES/TOGSHIPS send 56/57/58) —
  per-window msg id spaces; those targets are COSMOSWnd's own handler, so
  the 0x39 arm of reswin's dispatch is UNREACHABLE for reswin. THE
  0x38-vs-0x39 SPLIT IS NOT A RESWIN CONCERN AT ALL: reswin has ONE
  release msg (0x38); its per-control selection rides the PARAM.
- MASK LAW FINAL (all legs cited): release dispatch ebp=1 (after an
  UP/DOWN press) -> latch &= ~1 clears the MOVE GATE bit; ebp=4 (after a
  LEFT/RIGHT press) -> latch &= ~4 clears the ROT GATE bit. DIRECTION bit
  survives the release.
- EQUIVALENCE PROOF (gate-only vs the port's pair-clear): vendor latch
  byte = (moveGate,moveDir,rotGate,rotDir); port encodes each pair
  2-bit 0=(0,0) 1=(1,0) 2=(1,1) 3=(0,1). Consumers: (i) pump gates on the
  GATE bit first (0x47c8e/0x47cd6) — state (0,dir) pumps NOTHING; (ii)
  every press leg with gate clear STARTS with dir normalised
  (0x47b73/0x47bf5 force (1,0); 0x47bc6/0x47c3d force (1,1)) — so
  (0,0) and (0,1) are indistinguishable to every subsequent press and
  pump. Enumerated all 4 start legs x 2 residual states: identical
  next-state and identical pump output. => port releaseRot/Move = 0 is
  BEHAVIOURALLY EXACT; keep, upgrade comments + pin the equivalence.
- FRAMEWORK GUARD banked: one-shot dispatch leg-1 gate `([esp]&1)!=0`
  (0x567c3) where bit0 = (global 0x484dc != -1); mask bits bit1/bit2 from
  0x484e0/0x484e8; leg-2 (0x484ec-carrier) is gated by mask bit2 and can
  never fire for filter=1 slots (filter&mask==0). Slot dispatch param =
  dword [slot+0xa] VERBATIM (0x5683d).

## P4 RAW-BYTE MASK BYTES + PRESS-TABLE AUDIT (0x47b44..0x47c42 hexdump)
- AND/OR immediates verbatim from the image: f7 (0x47b5b), fb (0x47b68),
  f7 (0x47b80), fb (0x47ba3), or 08 (0x47bb0), fd (0x47bdd), fe (0x47bea),
  fe (0x47c25), or 02 (0x47c32), or 03 (0x47c3f). Pair-A legs (msg 0x32
  rot-left / 0x34 move-up) clear/keep bits {4,8}/{1,2} EXACTLY as the port
  pressPair models; pair-B legs OR in 0xc/0x2/0x3 likewise. pressPair is
  byte-faithful — no port delta needed anywhere in the press path.
- STATE/seam-note CORRECTION restated for the landing docs: the press tail
  pushes `(msg==0x34/0x35 ? 1 : ebp)` with ebp==4 on the arm path — the
  earlier "(? 1 : 0)" phrasing mis-stated the else value (0x47c54
  `mov eax,ebp` executes BEFORE the cmps; eax=1 only on the je legs).
- MASK SEMANTICS AT THE BYTE LEVEL: ebp=1 -> ~1 = 0xfe clears bit0 (MOVE
  GATE); ebp=4 -> ~4 = 0xfb clears bit2 (ROT GATE). The vendor release
  clears the GATE bit of the pressed pair and PRESERVES the dir bit; the
  port's 2-bit pair-clear maps {1,3} (gate-clear states) to 0.
  EQUIVALENCE (exhaustive, pinned in test_releaseparam_tpf7a): for every
  raw latch byte b in [0,256) and every press sequence of length <=4 over
  the 4 controls, vendor(gate-clear release) and port(pair-clear release)
  produce identical pump outputs and identical post-release press
  transitions — because (i) the pump tests the gate bit FIRST
  (0x47c8e/0x47cd6 je-skip: gate-clear pumps NOTHING regardless of dir),
  and (ii) every press leg with gate clear re-normalises dir
  ((0,x)->(1,0) at 0x47b73/0x47bf5; (0,x)->(1,1) at 0x47bbd/0x47c3f).
- FRAMEWORK GRAB GUARD (new leg found in the walker prologue 0x567a3..
  0x567e2): dispatch mask bit0 = (global 0x484dc == -1) (0x567be sets it,
  0x567d4/0x567e2 set bits1/2 from 0x484e0/0x484e8); slot leg-1 requires
  (filter&mask)!=0, filter=1 => the queued release dispatches ONLY while
  no widget holds the mouse grab (0x484dc is the grab word: writers
  0x2a7bb/0x2a802/0x2a844 set, 0x55626/0x59b06 clear). Matches the port's
  "release applies wherever the pointer drifted" reading.

## P5 DISPOSITION — SHIP (comments + pins), no behavioural delta
- Assignment step (3) first branch CONFIRMED: ebp IS the queued param
  verbatim (chain 0x5669c slot+0xa -> 0x5683d ecx -> 0x56ca4 ebx ->
  0x47614 mov ebp,ebx), so the mask law FOLLOWS and is SHIPPED SAFE:
  per-control release = clear the pressed pair's GATE bit; the port's
  pair-clear is byte-equivalent (P4) -> keep releaseRot/releaseMove,
  upgrade the .h comment to the cited split, add equivalence pins.
- The "0x38 vs 0x39" framing was itself a mis-framing: reswin's ONLY
  release producer is msg 0x38 at 0x47c67 (sole `mov ecx,0x38` in the
  image); msg 56/57/58 (0x38/0x39/0x3a) in windows.txt belong to
  COSMOSWnd buttons (CENTERHOLO/TOGLANES/TOGSHIPS, ln336/354/390) —
  per-window msg-id spaces. The per-msg split that matters is the queued
  PARAM (1=move-gate, 4=rot-gate), not the id.

## P6 *** PRESS-TABLE DEFECT FOUND BY THE EQUIVALENCE TEST ***
The exhaustive vendor-model pin FAILED at state (1,1) on all four
controls. RAW BYTES (own dump, authoritative):
- msg 0x32/0x34 (pair A LEFT/UP): both-set leg = `and 0xf7`/`and 0xfd`
  -> clears the DIR bit, KEEPS gate: (1,1)->(1,0) FLIP (left/up revives
  or keeps its own direction).
- msg 0x33/0x35 (pair B RIGHT/DOWN): both-set leg = `and 0xfb`/`and 0xfe`
  -> clears the GATE: (1,1)->(0,1) DEAD (second RIGHT press KILLS motion).
Vendor table: A: 0->1,1->0,2->1,3->1; B: 0->2,1->2,2->3,3->2.
Port pressPair SHIPPED table: A: 0->1,1->0,2->3,3->1; B: 0->2,1->2,2->1,
3->2 — the case-2 results are SWAPPED between the pairs. _wip_tPF7 P2
line 76 "pressPair CORRECT, no port bug in the table" was a MISREAD of
P2's own raw line (line 72 correctly says msg50 (1,1)->(1,0) flip);
test_researchgeom_trsvc ln 244-247 pinned the wrong DEAD reading.
=> SHIP the vendor table (fix pressPair case 2), re-pin
test_researchgeom, mutation at the .cpp DEFINITION site. This also
refines user-item-17 colour: vendor RIGHT = start / kill / restart;
vendor LEFT = start / stop / revive-left — the port's flipped table is
part of the 'buttons feel wrong' family.
