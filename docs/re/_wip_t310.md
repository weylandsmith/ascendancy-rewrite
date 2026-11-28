# _wip_t310 — DESTINATION-WIDGET WRITER WINDOWS (DAT_43508 family, ret_stack caller map)
# tCITE-AUDIT 2026-11-27 ANNOTATION: "calls 0x250bb (format)" (S1/S3) is a
# MIS-CITATION — zero rel32 call operands name 0x250bb in the code span; fn
# 0x51b68's real format chain is `call 0x21a20` @0x51c17 + `call 0x76c79`
# @0x51c23 (string-id select `mov eax,0x2b13` @0x51bc0). Corrected in
# ships.md:1833; this wip is kept as history.

## S0. Assignment + pre-flight
- STATE.md NEXT ACTION t310: fire the DAT_43508 family via a LIVE ORDER FLOW and
  name callers from ret_stack. CLOSE condition: a banked stop at any DAT_43508
  writer with a named ret0 caller on an ENTERED destination click = destination
  writer witnessed (OQ-019 residue narrows to per-ship select). Whole-log zero
  WITH btn_hdlr alive = fn 0x51b68/0x51834 need a different trigger (bank msg
  ids, keep row open).
- New sitting check: NO new sitting. live-timeline tail (400 KB, 16 recs)
  wall 17:04:34..17:07:04 ALL turn 1086 = same idle hold as t309; production
  :9 pid 1957 alive, autosaves 10 s. r1_t85g_sitting.py run anyway (output =
  historical sitting report, t>=1240 segments unchanged). Proceed with t310.
- REFUTED bindings honored: no 0x55ae8/0x55a60/0x56ad4 idle witness legs;
  bright-dot pip law dead; DAT addresses quoted only with +0x88 member rule.

## S1. STEP-1 offline disasm (file offsets, work/ascend_payload.bin)
- fn 0x51b68 entry 0x51b68: eax=record ptr saved [ebp-8]; dl=BYTE ds:0x7458e
  (star-table index k); eax = k*31*2 + 0x12e16 (star-record base, same law as
  t308 0x255be1 rebased -0x242000 = 0x12e16? verify: 0x255be1-0x242000=0x13be1,
  NOT 0x12e16 — DIFFERENT table, bank it); call 0x338 (relocation helper?);
  clamp to 0x64; then [rec+0xab]->[+0x8c7] word cmp 1 -> picks const 0x2b13 vs
  0x2b14 (string ids), pushes star-record addr [eax*2+0x12e17]-indexed name
  offset + 0x74590, calls 0x250bb (format) — fn 0x51b68 = a LABEL/TEXT builder
  over the star table for the record's system.
- 0x51fc2 (inside fn 0x51b68 tail): eax=[edx+0x59]; mov ds:0x43508,eax; then
  mov eax,0x7a35c; call 0x4b24 (ring post ebx=0x11); then [edi+0xab]+0x8cd.
  [edx+0x59] = ORDER TARGET field per t296 S24 candidate reading.
- fn 0x51834 entry: push esi/edi/ebp; eax->ebp; dx saved; dispatch on dx:
  <2 -> 0x51af2? (jb 0x2bf target = 0x51852+0x2bf... compute); >2 and <=? ;
  cmp dx,0x1c01 je 0x52067? ; default tail-calls 0x336b4 (btn_hdlr target!)
  with sar edx,0x10. THIS MATTERS: fn 0x51834 is a PRE-DISPATCHER in front of
  the type-0 button handler family — its gate word is dx.
## S1b. BLOCK MAP CORRECTION + msg-0x1c01 PATH (the STEP-1 datum)
- objdump-fallback branch targets are WINDOW-RELATIVE (base printed only in the
  address column). Resolved fn 0x51834 dispatch (dx = msg id, eax = window
  rec, [esp] u16 extra): cmp dx,2 -> jb 0x51AF3 (dx<2); jbe 0x51A2A (dx==2);
  cmp dx,0x1c01 je 0x51A67; DEFAULT path 0x51863 = TAIL-CALL btn_hdlr 0x336b4
  (e8 3c 1e fe ff at 0x51873, verified arithmetic 0x51878-0x1e1c4=0x336b4).
  => fn 0x51834 is a msg pre-dispatcher in front of the type-0 button handler.
- THE DESTINATION PATH 0x51A67 (msg 0x1c01): eax=[eax+0xab] (system rec);
  call 0x32FBC; gate cmp ds:0x484ec,0x96 jle skip;
  IF ds:0x484ec > 0x96 (turn-ish counter, 1086=0x43E passes): DAT_43508=eax,
  RING-A post code 0x11 (0x7a35c, ecx=1, via 0x5074) at 0x51A8E;
  ELSE 0x51AA1: k=[eax+0xa]>>16 (system index), edx=0x13bc5+k*3*32 ->
  star-record addr (0x13bc5+0x242000=0x255bc5 == t308 WITNESS value EXACTLY),
  DAT_43504=edx at 0x51AC9, RING-A post code 0x10 (via 0x5034).
  Both stores + both ring posts live on ONE msg: 0x1c01.
- SPAN CORRECTION vs t309: stores 0x51a8e AND 0x51ac9 sit in fn 0x51834's span
  (0x51834..~0x51af0), NOT fn 0x51b68 (starts 0x51b68; epilogue add esp,0x58
  class; 0x51FAB's add esp,0x1bc belongs to a DIFFERENT fn). fn 0x51b68 =
  star LABEL/text builder: k=ds:0x7458e, base k*31*2+0x12e16, string ids
  0x2b13/0x2b14 on [rec+0xab]->[+0x8c7]==1, format call 0x250bb.
- Orphan blocks AFTER rets (jump-target fragments): 0x51FB5: DAT_43508=
  [edx+0x59] + ring-A 0x11 (call 0x4b24); 0x51FF6: DAT_43504=[esi+0x59] +
  ring-A 0x10 (call 0x4aec). [+0x59] = order-destination field read; these are
  the widget-paint-style direct stores (render-direct law consistent).
- u32 refs to fn entries 0x51b68 / 0x51834 in FILE image: 0 and 0 (re-measured
  this session) = relocated class tables; ret_stack remains the only caller map.
- Leg byte verification (payload): w51ac9 0x51AC9 = 89 15 04 35 04 00 OK;
  w43508_51fc2 a3 08 35 04 00 OK; w43508_51a8e a3 08 35 04 00 OK;
  w43504_52003 a3 04 35 04 00 OK; btn_hdlr entry 56 57 55 83 ec 04 OK.

## S3. MSG-0x1c01 SENDER CENSUS (whole-image byte census, this session)
- cmp dx,0x1c01 (66 81 fa 01 1c): 8 sites {0x1571f, 0x35529, 0x36393, 0x3aa6c,
  0x4dd96, 0x51858 (fn 0x51834 = consumer), 0x51cf5, 0x5293a}; cmp ax form
  0x5a5b7 x1. mov edx,0x1c01 (ba 01 1c 00 00): EXACTLY 2 senders:
  0x16168 (fn 0x160xx; after ring-A post code 0x51 of [ebp+0xbb]->[+0x41],
  then call [ebx+0xc] where ebx=[ebp+0xa7] CLASS TABLE -> slot-4 relay, NOT a
  direct call into 0x51834) and 0x35696 (DIGIT-KEY handler: gate cmp ebx,0x31
  / cmp ebx,0x39 = ASCII '1'..'9', dh=[ebp+0xaf] layer byte, then call
  [esi+8] slot-2 with eax=ebp ecx=-1). push/mov ecx|eax/cmp eax|ecx forms: 0.
- CONSEQUENCE: if fn 0x51834 receives 0x1c01 at all, it is via a class-table
  slot whose SLOT OWNER is the window under the key/click; the digit-key phase
  is the cheapest live trigger the image offers. s2_1616f armed as the relay
  witness (stop there = 0x1c01 was sent by the fn-0x160xx path).
- t304 legacy census data (runs 033648/061825): s2_356a5 fired 0x whole-log
  with btn_hdlr alive 4/2 — digit keys NEVER PRESSED in any prior session
  (battery never included a key phase), so the 0x35696 sender is UNTESTED,
  not refuted.

## S4. RUN t299-leg-20261105-173627 (attempt 2 of r310; attempt 1 = BREAK
## lottery loss at boot, teardown clean). Battery: preturn -> fleet -> sprite
## (48,151) -> planet (439,331) -> digit 1..9 -> control_nextturn -> holds.
- LEGS armed 6/6 (BPLIST verbatim, rebase P0=0x1BF450 consistent at every
  site: 210EDE/211412/210F19/211453/1D55BF/1F2B04).
- PRE-TURN WORKED: turn 1086 -> 1087 (oracle pair; sav granularity caveat
  stands but pair bracketed the click).
- **ds:0x484ec IS NOT A TURN COUNTER — IT IS MOUSE/CURSOR X** (measured 2/2):
  value 0x30(48) in the window after the x=48 sprite click, 0x1b7(439) after
  the x=439 planet click — exactly the last-clicked X both times. The t296
  reading 'turn gate ds:0x484ec>0x96 = turn number' is REFUTED; the fn-0x51834
  msg-0x1c01 branch select is: last-mouse-X > 150 -> DAT_43508=system-ptr +
  ring-A 0x11; X <= 150 -> DAT_43504=star-addr + ring-A 0x10. (Explains the
  t308/t307 star case AND makes 'turn-gated' a misnomer — a click at screen
  x<=150 takes the star branch.)
- Oracle constant across sprite/planet/digit phases: DAT_43504 0x256825
  'Icarus', DAT_43508 0x26f00d, sel43510 0, mode4226 0x11 (system view),
  ringB/A counters 0, gate_7e5aa 0, gate_7e89e 0 — NO destination write.
- Stops banked (all btn_hdlr, control alive): sprite window hit name='PLIND'
  ret0=?; planet click hit name='Cancel' (the EVENTWIN/popup) ret0 file
  0x56c77; digit keys hit name='Cancel' (edx=3, ecx=2) ret0 0x56c77;
  control_nextturn name='PLSQUARE' ret0 file 0x3d391. ZERO stops at
  w43508_51a8e / w43508_51fc2 / w51ac9 / w43504_52003 / s2_1616f (pty
  whole-log census pending confirmation).
- DIGIT KEYS DID ROUTE (btn_hdlr fired on the key window 'Cancel') but the
  FOCUSED window's slot-2 is btn_hdlr — class 0x247cb8 (type-0 button), NOT
  the class owning fn 0x51834. The 0x35696 sender fires call [esi+8] on the
  KEY-FOCUSED window; to route 0x1c01 INTO fn 0x51834 its class must hold
  focus. Class owner UNKNOWN (file-image u32 scan blind per t309 relocation
  law) -> needs a RAM scan or an entry-leg.
- INSTRUMENT GAP (honest): this run armed only the STORE sites, never
  fn 0x51834's ENTRY 0x51834. An entry leg fires for EVERY msg of its class
  with dx = msg id and ret0 = the dispatch site — it is the direct witness
  for "does this class receive anything on this battery".
## S5. CLASS TABLE FOUND (RAM scan of run 173627's own sav — the t309 route)
- Scan sav Memory member (17,055,880 B) for REBASED entry value 0x51834 +
  P0(0x1BF450) = 0x210c84: EXACTLY 1 hit at RAM 0x248050. Controls: btn_hdlr
  +P0 -> 4 hits (4 button classes), cos_hdlr +P0 -> 1 hit 0x247adc. THE FILE
  scan finds ZERO for all of them (t309 relocation blindness CONFIRMED; the
  +0x242000 rebased-value scan of the FILE is also zero — only RAM works).
- Slot grid banked VERBATIM (RAM u32s): 0x248040 {311b8, 316f0, 51630, 30d08,
  51834, 51680} (fn file offsets; 0x248058 = garbage 3c8efa35 = grid ends).
  fn 0x51630 (grid member) = constructor: sets [win+0xa7]=0x5fc0 (RELOCATED
  class ptr -> RAM 0x247FC0) and [win+0xab]=0. fn 0x51680 = star-table walker
  (stride 0x60 over n=ds:0x16145, visibility byte [rec+0x14] vs 1<<ds:0x7458e).
- WINDOW OWNER: RAM scan for refs to 0x247FC0: 3 hits, ONE with window magic
  0x12345678 at rec-0xa7: rec 0xfd9fbc NAME 'STATUSWND'. Other two refs = code
  bytes inside fn 0x51630 (constructor imm). => THE CLASS OWNING fn 0x51834 IS
  THE STATUS WINDOW — exactly the destination-widget semantics.
- DIGIT SENDER + STATUSWND COMPOSE: 0x35696 handler calls [esi+8] edx=0x1c01 on
  the KEY-FOCUSED window's class. If STATUSWND holds focus -> fn 0x51834 ->
  msg-0x1c01 destination path. t310 RUN pressed keys while the 'Cancel' popup
  held focus (stop ret0 0x56c77 dispatcher, ret1=0x31 = ASCII '1' — keys DID
  enter the dispatcher, WRONG WINDOW owned it). DEFECT (mine): no
  close_eventwin immediately before the digit phase (digit block ran after the
  planet window whose bank ended with the popup open).
- RUN-STATE FACT: gate ds:0x484ec = LAST MOUSE X (2/2: 0x30 after x=48 click,
  0x1b7 after x=439 click) — 'turn counter' reading REFUTED. msg-0x1c01 branch
  select = last-mouse-X > 150 -> DAT_43508+ring0x11; <=150 -> DAT_43504+ring0x10.
- CENSUS-CTL MATCH=False on the digit-phase arm is EXPECTED, not a defect:
  the ctl compares RAM bytes at the first leg (w43508_51a8e) against FILE
  bytes, and the leg IS a data-immediate store (a3 08 35 04 00 -> RAM
  a3 08 55 28 00 per the t307 self-relocation law). A store-imm leg must
  never be leg[0] when the ctl probe matters (use btn_hdlr/router as leg[0]).
- PTY WHOLE-LOG CENSUS (run 173627, rc=0): {w43508_51a8e:0, w43508_51fc2:0,
  w51ac9:0, w43504_52003:0, s2_1616f:0, btn_hdlr:4}. Control alive -> zeros are
  context: the STATUSWND class received NO msg on the order battery, and the
  fn-0x160xx relay never fired. Oracle DAT_43504/43508 constant
  (0x256825 Icarus / 0x26f00d) across sprite/planet/digit pairs.

- LEGSET = w43508_51a8e,w43508_51fc2,w51ac9,w43504_52003,btn_hdlr (w51ac9 NEW).
- Battery = census mode --target-kinds sprite,planet (fleet view -> rowjump ->
  sprite select -> planet destination click) INSIDE armed windows; star-click 0;
  --pre-turn 1 (t298 gate: owner-0 fleet has no kind-4 at t=1086; End Turn ONCE
  before picking). control_nextturn + hot holds kept (t309 shape).
- Oracle ADDS rd(0x7e5aa), rd(0x7e89e) (task-mandated) + rd(0x484ec) (the gate).
- CLOSE: banked stop at any DAT_43508 writer with named ret0 on ENTERED dest
  click. Whole-log zero with btn_hdlr alive = msg-0x1c01 never sent by map
  clicks -> bank msg ids seen, row stays open.
