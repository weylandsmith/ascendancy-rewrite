# t318 WIP — BROADCAST-PUMP LEG s2_56c74 LIVE CAPTURE

## S0 Assignment (from docs/STATE.md NEXT ACTION, 2026-11-06 session 27)
Arm the msg-0xc/4 intake leg the t317 run never armed: s2_56c74 (the
dispatch call site `call *[tgt+0xa7+8]` inside broadcast pump fn 0x56b5c),
together with s2_56cda, fn51cc4_entry, w43508_51fc2, w43504_52003
(btn_hdlr only if leg budget free — positive control). Choreography = the
PROVEN --shipclick 4 phase VERBATIM (run t299-leg-20261106-012002 rc=0) PLUS
the standard tail (rowjump/sprite/planet/NEXTTURN), since the pump posters
0x54aa9/0x54ab2 fire off the click record ds:0x484ec/0x484f0.
Branches per REFUTED-ROUTES t317 amendment (5) + STATE.md:
(a) s2_56c74 msg 4/0xc on STATSHIPLST rec AND s2_56cda edi=0x1c01 AND
    fn51cc4_entry edx=0x1c01 -> destination-fire residue CLOSES OQ-019,
    law into ships.md S44.
(b) s2_56c74 fires on STATSHIPLST but no 0x1c01 -> bank msg id + args;
    in-rect gate 0x32730 or the 0x4f road is the named blocker (S2 road
    table); t319 = decode pump-arg X law.
(c) s2_56c74 never fires whole-log -> pump is turn-gated; t319 arms same
    legs across a NEXTTURN window.

## S2 THE RUN (attempt-2 measured; attempt-1 lost the BREAK lottery)
run = work/r1/t299-leg-20261106-021602 (SESSION END 02:33:42 rc=0,
census-measured 9 phases: hold_post_star, shipclick250/120/453/300, sprite,
planet, control_nextturn, hold_post_turn; 26 stops; pty-whole-log-census
probe present => relaunch loop short-circuited, NO attempt 3).
Legs armed: s2_56c74, s2_56cda, fn51cc4_entry, w43508_51fc2, w43504_52003,
btn_hdlr (6/6 ARM OK every cycle; census mode re-arms the FULL set every
stop, so s2_56c74 was armed in all 9 windows — DISARM only between phases).
HARNESS CHANGE this run (scripts/r299_leg_session.py bank_stop): esp dump
8 -> 16 bytes, banking esp_p8/esp_p12 (the pump dispatch s2_56c74 carries
msg=[esp+8] AT the call, before the return addr is pushed, so an 8-byte
window could never read it). No stop reached that field (s2_56c74 silent),
so the extension is unexercised-but-harmless (ret0/ret1 semantics unchanged;
26/26 stops banked normally).

## S3 MEASUREMENT — THE BROADCAST PUMP DISPATCH s2_56c74 IS COLD
pty-whole-log-census counts (whole session, 9 armed windows, 540 s armed):
  s2_56c74 0 | s2_56cda 26 | fn51cc4_entry 0 | w43508_51fc2 0 |
  w43504_52003 0 | btn_hdlr 1
s2_56cda 26 stops decompose (scripts/r318_analyze.py, NEW):
  - 18x msg 0x3b (periodic pump) -> eax='COSMOSWnd' (baseline/post-rearm
    background, matches the t304/t317 positive-control law)
  - 4x msg 8 -> eax=0xfe7ac0 NAME='STATSHIPLST' at the four gutter clicks
    x=620 y 250/120/453/300 (t317 REPRODUCED VERBATIM: edi=edx=0x8,
    ebx=ecx=ebp=Y, baseline window 0 click-attributable stops)
  - 1x msg 8 -> 'PLIND' (sprite click 48x151), 1x msg 6 -> 'PLIND',
    2x msg 8 -> 'PLANETALLOC' (planet click + NEXTTURN window)
ZERO whole-log: fn51cc4_entry (no msg of ANY id reached FLEETWND — second
independent confirmation after t317), the writer pair, and the literal
0x1c01/0x1c02 anywhere in any banked reg/stack field (0 hits).
Oracles: gate guest 0x600058=0 datum 00000000 (save 60.sav,
r317_gate_probe), FLEETWND rec ok slot41=95 rect 7,7,632,472; STATSHIPLST
rec 0xfe7b48 slot41=96 rect 7,46,632,472 bf_28=28 4f=0x66 target63=95
(t316/t317 widget law re-confirmed on this run's saves). DAT_43508/43504
unmoved across every phase pair (0x26fe77/0x256825 then 0x26f00d after the
sprite phase — a phase-boundary write, not click-attributable: identical
before AND after each of the 4 gutter clicks). mode4226 = 0x12 during the
shipclick phase, 0x11 sprite/planet, 0x1 after NEXTTURN. gate_484ec
(last-click X law) 0x1ff at nextturn_after.

## S4 READING THE s2_56c74 ZERO (what it does and does not license)
DOES license: in a live in-game session that contained a witnessed turn
boundary (--pre-turn 1 crossed 1086->1087; the NEXTTURN after-oracle still
read turn 1087, so its advance is UNWITNESSED — hold_post_turn window had 0
stops either way), 4 vendor gutter clicks, sprite/planet clicks and the
periodic msg-0x3b pump,
fn 0x56b5c's slot-2 dispatch 0x56c74 DELIVERED NOTHING — so the msg-0xc/4
road t317 nominated as "the real intake into fn 0x32664" is NOT the road a
vendor-gutter click takes either. Combined with t317 (1) and (2): NO msg
id ever reaches FLEETWND by any of the three candidate roads witnessed so
far (fn 0x56ca4 direct, digit-key LOADSCREEN, broadcast pump).
DOES NOT license: "fn 0x56b5c is never CALLED". arming-scope caveat — legs
are DELETED between census windows (DISARM/BPLIST left=0) and during the
BPDEL->re-arm gap of each fired cycle, so a pump dispatch landing in a gap
is invisible; and the run has NO leg at the pump ENTRY (fn 0x56b5c) or at
the posters (0x54aa9/0x54ab2) that would separate "pump never called" from
"pump called, per-entry mask/count selected nobody". That separation is the
t319 question and it is CHEAP (see S5).

## S6 STATIC RE-READ OF THE POSTER BLOCK (t91_code_disasm.txt 77195-77245,
## verbatim; shapes t319 WITHOUT spending a capture)
- 0x54a3f: `cmp edi,ds:0x484a4; jne 0x54a88` — THE GATE deciding the msg-0xc
  road. Equal branch 0x54a47: pushes (ds:0x484f0, ds:0x484ec, 0x4850c),
  `call 0x5be9b` -> ds:0xa1ffc, then loads [esi+0x21d92], edi=[[..]+0x39];
  if edi==0 -> jmp 0x54aca (NO PUMP AT ALL); else dispatch msg **0x3f1** via
  `call [[eax+0xa7]+8]` at 0x54a83 (a DIFFERENT dispatch site, already in the
  t304 registry as s2_54a83).
- 0x54a88 (jne road): `cmp edi,[esi+0x24da4]; jne 0x54ab0`. Fall-through
  0x54a90: if [esi+0x489e]!=0 -> 0x54ab0; else POST msg **0xc** (ecx=ds:
  0x484f0, ebx=ds:0x484ec, push 0) at 0x54ac5. The jne target 0x54ab0 POSTs
  msg **4** (same ecx/ebx from ds:0x484f0/0x484ec, push 0) at the SAME call
  0x56b5c. So msg 4 vs 0xc is decided by TWO u32 equalities on edi vs
  ds:0x484a4 / [esi+0x24da4] — NOT by the click geometry alone.
- fn 0x56b5c has NINE callers total (E8 census): 0x53fa3 (msg 0xd),
  0x54976 (msg 3, args ds:0x484c4/c6), 0x54ac5 (4/0xc — the click road),
  0x54b36 (msg 5), 0x5531e (0xf), 0x5548c (0xe), 0x55f82 (0xd), 0x56f0f
  (msg 2, call site of fn 0x56ca4 immediately BEFORE it at 0x56efd),
  0x57003 (msg 1).
- MASK LAW COROLLARY (fn 0x56b5c verbatim, t317 S8; NOTE: the mask byte key
  law is `0xa2024+key` with key semantics UNVERIFIED — do not assume it is
  the msg id): the t318 census proves msg 0x3b dispatches THROUGH fn
  0x56ca4 (18 COSMOSWnd stops at s2_56cda), while the 0x56b5c pump delivered
  nothing. A t319 leg at the fn 0x56b5c ENTRY (ret0 names the caller
  verbatim, edx=the msg id it carries) plus legs at 0x54a47 and 0x54a88
  (bank ebx/ecx = the click record the pump WOULD carry) separates all
  remaining hypotheses in ONE run: caller-never / gate-never-equal /
  gate-equal-but-mask-empty.
- t319 LEG BUDGET (5): pump_entry_56b5c (0x56B5C bytes 56 57 55 83 ec 10
  89 c7 66 89 54 24 08 payload-verified), p54a47 (0x54A47 `mov ebx,ds:
  0x484f0` first byte of the equal road), p54a88 (0x54A88 `3b be a4 4d 02
  00` verbatim), s2_56c74, s2_56cda. DROP fn51cc4_entry (zero twice; any
  msg reaching it must pass a witnessed site first) and the writer pair
  (downstream of it; no 0x1c01 twice).

## S1 Pre-run checks (this session)
- Sitting check: live-timeline.jsonl writer alive (pid 1979), newest lines
  turn=1086 wall 02:08 (same turn as t316/t317 checked; threshold play past
  t1255) -> NO new sitting, r1_t85g_sitting.py not run, t318 proceeds.
- Production :9 (pid 1957 under timeout 1955) running, untouched.
- Binding amendments honoured: t317 (1)-(5), t316 (1)-(4), t315, t314.
- relaunch loop per scripts/r317_relaunch.sh pattern (attempt-1
  short-circuit: rc=0 + pty-whole-log-census probe => no attempt 2).
