# t317 — SHIP-LIST-CLICK -> FLEETWND 0x1c01 LIVE WITNESS (hand-authored)

Task (docs/STATE.md NEXT ACTION 2026-11-06T00:55): ONE scratch capture —
open FLEET (rails=188 reguard, NO rowjump), legs {fn56ca4_entry,
fn51cc4_entry, w43508_51fc2, w43504_52003, btn_hdlr}, click inside the
STATSHIPLST rect on the correct strip. Oracle: whole-log leg census +
DAT_43504/43508 + sel43510 + mode4226 + 0x600058 datum at exit.

## S0 Pre-flight
- Sitting check: live-timeline.jsonl mtime Nov 6 00:38 (writer alive), tail
  max turn 1086 == t316's value. NO new sitting -> r1_t85g_sitting.py NOT run.
- Binding negatives honoured: t316 amendment (no save-scan witness on
  registry/mode4226/slot tables; emit owner fn 0x33320 named, no re-hunt;
  rec+0x41=slot-id), t315 (LOADSCREEN dead; key-driven shapes dead), t314
  (rowjump CLOSES FLEET; FLEETWND gets no keyboard msg), t312 (sprite-pixel
  select dead). This is the t316-sanctioned live shape.
- fn56ca4 ENTRY BYTES VERIFIED against payload before shipping:
  payload[0x56ca4:0x56cb8] = `56 57 89 c6 89 df 89 cb 8b 4c 24 0c 8b 80 26 42
  00 00 c1 f8` — prologue push esi/edi + the [[obj+0x4226]>>16] bail read.
  Matches the assignment spec `56 57 89 c6 89 df`.

## S1 DESIGN-TIME READ (1) DONE — THE GUARD IS AN X-COORDINATE TEST, NOT A
## MSG-ARG TEST (objdump -D -b binary -m i386, payload file bytes, verbatim)
The t316 S4 note ("guard [w+0xbf]=28 means the msg arg must exceed 28") is a
MISREAD — corrected here, verbatim path fn 0x33320 0x33331..0x33342:
```
33331: mov 0x10(%eax),%edx      ; edx = widget rect x1 (632)
33334: mov 0xbf(%eax),%ebx      ; ebx = 28  (STRIP WIDTH)
3333a: mov 0x4(%esp),%ecx       ; ecx = INCOMING edx = click X coord
3333e: sub %ebx,%edx            ; edx = x1 - 28 = 604
33340: cmp %ecx,%edx
33342: jbe 0x333b4              ; X <= 604 -> NOT the emit road
```
Register law at fn 0x32664 entry (0x32667..0x3266d): eax=widget, edx=msg,
ecx->ebx, ebx->ebp... cross-checked against the in-rect gate 0x32730..0x3274e:
ebp tested against [+0x8=7 .. +0x10=632] => ebp = X; ebx tested against
[+0xc=46 .. +0x14=472] => ebx = Y. fn 0x33320 is called at 0x32778 with
eax=widget, edx=ebp=X, ecx=msg(di sign-ext), ebx=Y inherited.
=> THE EMIT ROAD FIRES FOR A CLICK WITH X IN (x1-28, x1] = (604, 632] AND Y IN
   [46, 472]: THE RIGHT-HAND 28-PIXEL STRIP OF THE SHIP LIST (the scroll
   gutter), NOT the row body. t316's "prev/next page arrows" inference is
   CONSISTENT (arrows live in the gutter); the paired 0x1c01/0x1c02 road
   picks by global 0x9f100 (runtime abs 0x2e1100) == 0 -> 0x1c01.
- MSG-ARG GATE on the in-rect road (fn 0x32664 verbatim): in-rect branch
  0x32730 is entered from msg 0xc (0x328be je) AND msg 4/5 (0x328e0 jbe).
  At 0x32754: if msg==0xc AND [w+0x4f] != 0x30 -> btn_hdlr fn 0x336b4
  (call 0x32768, stop-file 0x3276d); if msg!=0xc OR [w+0x4f]==0x30 -> emit
  road fn 0x33320 (call 0x32778, stop-file 0x3277d). THE TWO ROADS HAVE
  DISTINCT STOP-FILES, so the btn_hdlr leg census names which road a click
  took — the census is self-diagnosing.
- fn 0x33058 (post-emit + msg-8 sibling) decoded head: hit-tests click
  against row table [w+0x8d1] (fn 0x5e940 binary search), calls [w+0x8fa]
  row callback, then fn 0x55240(0x7a35c) — repaint. It is NOT the msg
  deliverer into fn 0x32664; the deliverer is the class dispatcher
  (call [cp+0xc] law, t313). Design-time read (1) CLOSED.
- MEASURE-AT-RUN-TIME (cheap, from the save the leg session boots): STATSHIPLST
  widget fields +0x4f (0x30 gate byte), +0x63 (target slot, t316 says 95),
  +0x10 (x1), +0xbf (28) — confirms the click strip per-run before arming.

## S2 DESIGN-TIME READ (2) DONE — MEASURED WIDGET FIELDS + THE MSG-ID ROAD
## TABLE (scripts/r317_gate_probe.py NEW, run on t299-leg-20261105-212402/41.sav)
- GATE[guest 0x600058] = 0, datum 0x600059..c = 00000000 (t315 law re-confirmed).
- FLEETWND rec 0xfe7a90 magic ok name='FLEETWND' slot41=95 inst 0xfe7ac0
  rect 7,7,632,472 (rect fields are u32).
- STATSHIPLST rec 0xfe7b48 magic ok: slot41=96, rect 7,46,632,472, x1(+0x10)=632,
  +0xbf=28, TARGET(+0x63)=95 -> EMIT TARGET = FLEETWND (t316 reproduced live-shape).
- +0x4f = 0x66 (NOT 0x30) at this save state. ROAD TABLE from fn 0x32664 verbatim:
  * msg 0xc in-rect -> [w+0x4f]==0x30 ? emit road : btn_hdlr road (0x3275c je).
    With 0x4f=0x66, a msg-0xc gutter click takes the BTN_HDLR road.
  * msg 4/5 in-rect -> 0x32730 UNCONDITIONALLY, NO +0x4f test -> emit road if X
    passes the strip guard. => THE CLICK MUST ARRIVE AS MSG 4 OR 5 (t301's
    "msg 5 = click" family), NOT msg 0xc.
  * msg 0x191/0x192 (fn 0x33320's OWN arrow re-sends to itself, 0x333e5/0x33402)
    -> fn 0x5649c/fn 0x564d8 row-scroller roads, never the emit.
  * msg 8 -> fn 0x33058; msg 0x193 -> 0x32786; msg<4/6/else -> btn_hdlr/0x326d6.
- Strip law (fn 0x33320 0x33331..0x33342, verbatim): emit iff X > [w+0x10]-[w+0xbf]
  = 632-28 = 604, and Y in [46,472] (gate at 0x32730). THE RIGHT 28-px GUTTER.
- Post-emit road note (fn 0x333b4 branch = the OTHER half, NOT the emit):
  row-body clicks (X<=604, [w+0xb3]==-1) self-send msg 0x191/0x192 by row half
  (arrow keys), then fn 0x56374 + msg 0x193 — the row-select/paging mechanism.
- fn 0x56ca4 verbatim: bail ret@0x56cbf iff [[obj+0x4226]>>16] < 0 (save-time
  mode=0 passes); win=[obj+edx*12+4]; cp=[win+0xa7]; call [cp+8] @0x56cda.
  LEG CHOICE: arm the CALL SITE s2_56cda (it is ALREADY in LEGS — t304 census
  set) INSTEAD of fn56ca4_entry: a call-site hit proves mode-gate PASS +
  registry deref, and eax at the stop = the registry win rec (names the target
  window); an entry-only leg cannot distinguish bail from deliver.

## S3 CAPTURE DESIGN (locked) — WITNESS DISCRIMINATOR = edi AT THE CALL SITE
- fn 0x56ca4 register law at the s2_56cda stop (stop BEFORE the call executes):
  eax = win = [obj+edx*12+4] (registry winner — RAW guest rec addr per t316),
  esi = cp = [win+0xa7] (FLEETWND => 0x247fa8, t313), edi = MSG (the emit road
  sets ebx=0x1c01 -> fn 0x56ca4 moves ebx->edi at 0x56ca8), edx = 95 (slot).
  => A STOP AT s2_56cda WITH edi=0x1c01 IS THE ENTIRE CHAIN WITNESSED IN ONE
     REG SET: gutter-click -> slot95 -> FLEETWND rec -> dispatch msg 0x1c01.
  edi=0x1c01 also discriminates OUR dispatch from the ~20/session unrelated
  ones (t304 census: s2_56cda fired 20x in run 061825 — HOT but attributable).
- fn51cc4_entry is COLD (t314 whole session: 0 fires, FLEETWND received no msg)
  — any fire is news; edx at the stop = msg id (t314 law).
- Legs: fn51cc4_entry (first, entry-leg law), s2_56cda, w43508_51fc2,
  w43504_52003, btn_hdlr (road diagnosis + NEXTTURN positive control).
- Click shape: FLEET open (rails reguard, NO rowjump before the phase), one ARM
  WINDOW PER CLICK at X=620 (strip 604<X<=632, inside rail band x606-635),
  Ys [250,120,453,300] (all in [46,472]); popup reguard post-arm (modal law);
  click via send(); census_window(args.window); disarm_run; oracle pair +
  RAW gate read mm[0x600058] + datum 59..c after each window (member coord ==
  raw guest addr for the magic-rec region, t316 S2 law — NOT P0-relative).
- EXPECTED OUTCOMES: (a) stop s2_56cda edi=0x1c01 + fn51cc4_entry edx=0x1c01
  -> destination-fire residue CLOSES at the gate (writers stay dark iff gate
  datum 0: state rec +0x58 = 0 in every save = nobody set a destination — the
  GATE, not the chain, is then the residue); (b) fn51cc4 fires no 0x1c01 =
  bank msg ids; (c) s2_56cda fires with other edi only = click road never
  emits (bank btn_hdlr args; watchpoint 0x600058 route t318).
- RISK (stated): if the live registry entry slot95 were null, fn 0x56ca4
  derefs [0+0xa7] -> call [garbage+8] = game crash. Mitigation: scratch copy
  only, kill-by-recorded-PID, production :9 untouched; and [inferred] the
  registry MUST be live-populated (fn 0x56ca4 has 56 callers — a null table
  would crash the game constantly).

## S4 LIVE OBSERVATION (run t299-leg-20261106-012002, in-flight, session 26
## adopting the killed session's capture; attempt loop pid 108004 GUARDED —
## if attempt-1 yields a measured census the loop must NOT start attempt 2)
- FLEET open rails=188 diff=175532 (01:27:43). shipclick_baseline (60s, no
  click): 0 stops banked. Clicks at x=620 banked ONE s2_56cda stop each:
  * 620x250: edi=0x8 edx=0x8 eax=0xfe7ac0 wrec_eax NAME='STATSHIPLST'
    ebx=0x26c(=620) ecx=ebp=0xfa(=250) esi=0x247c70 esp=0x2e9108 ret0=0x60
  * 620x120: edi=0x8 edx=0x8 eax=0xfe7ac0 ebx=0x26c ecx=ebp=0x78(=120)
  => THE CLICK ARRIVES AT fn 0x56ca4 AS MSG 8 DISPATCHED ON THE STATSHIPLST
     REGISTRY ENTRY ITSELF (slot 8, NOT slot 95) — NOT msg 4/5, NOT msg 0xc.
     Click coords verbatim in ebx/ecx/ebp prove it is OUR click.
  => msg 8 fired ONLY in click windows (baseline 0) — attributable, not noise.
  => fn51cc4_entry ZERO, w43508/w43504 ZERO, btn_hdlr ZERO through click 2.
     THE EMIT ROAD NEVER FIRED: STATE.md BRANCH (c) in effect
     ("click road never emits"). The t316 S1 strip law (X>604) is NOT the
     blocker — the MSG-ID road is: msg 8 -> fn 0x33058 (S2 table), which
     never reaches call site 0x32778.
- OPEN DECODE (S5): fn 0x32664 head msg-census verbatim — which branch msg 8
  takes and WHY msg 0xc/4/5 never arrived; and fn 0x33058's role at the msg-8
  road (row hit-test + repaint per S1; gutter is not a row => inert).

## S5 VERBATIM ROAD DECODE (objdump payload bytes; run still live)
- fn 0x32664 head (0x3266f..): msg u16 switch — <8 -> 0x328da sub-switch
  (4/5 -> 0x32730 emit-road gate; 6 -> 0x326d6; <4 -> 0x3292b); 8 -> 0x32720
  = fn 0x33058 + ret -1; 9..0x190 -> 0x328be (msg-0xc test -> 0x32730
  in-rect); 0x191/0x192 -> 0x327b3/0x32827; 0x193 -> 0x32786; else btn_hdlr.
  LIVE WITNESS CONFIRMS: our click entered as msg 8 => fn 0x33058. The
  0x32778 emit call (fn 0x33320) sits ONLY on the msg-0xc branch AND needs
  [w+0x4f]==0x30 (MEASURED 0x66) => THE t316 0x1c01 CHAIN IS GATED DEAD AT
  [w+0x4f] IN THIS GAME STATE — msg 0xc alone never reaches fn 0x33320.
- fn 0x56ca4 verbatim (0x56ca4..0x56cdf): eax=obj(0x7a35c) edx=slot ->
  win=[obj+slot*12+4]; esi=[win+0xa7]=CP; movswl %di,%edx (msg sign-ext);
  0x56cda call *[cp+8]. So the RUNTIME DISPATCH of EVERY registry msg is
  slot-table SLOT 2 ([cp+8]); msg lands in edx of the slot-2 fn.
- fn 0x33058 (msg-8 road) FULL DECODE — IT HAS ITS OWN GUTTER BRANCH:
  0x3313b: edi=[w+0xb3]; 0x33141: eax=[w+0x10]=632; if edi==-1 (no
  scrollbar) eax -= [w+0xbf]=28 -> 604; 0x3314f cmp msgX(eax spill) vs eax;
  X<=604 -> 0x332ad row-half road (self-send msg 0x191/0x192 via fn 0x32af8,
  the S1 note); X>604 GUTTER -> 0x33158: if [w+0x8e5]>1: ebx=0x193,
  fn 0x32af8 self-send, THEN **fn 0x56730(0x7a35c, edx=[w+0x41]=96)** and
  **fn 0x56434(0x7a35c, edx=96)**; else row-index bookkeeping 0x3319c..
  => THE MSG-8 GUTTER ROAD CALLS fn 0x56730 AND fn 0x56434 — SIBLINGS OF
  fn 0x56ca4 IN THE SAME REGISTRY FAMILY (obj 0x7a35c, edx=slot-id law).
  NEW PRIME SUSPECTS for the FLEETWND 0x1c01 emit (t316 only censused
  fn 0x5712c registration + fn 0x56ca4 dispatch).
- fn 0x56730/fn 0x56434 DECODED (0x56730..0x56794 / 0x56434..0x56498): TABLE
  ENTRY CLEARERS — loop slots <0x10, stride 0x12 (resp 0x16) at obj+0x4610
  (resp +0x44ae), match entry-by-id edi==[e+0x4610] (+parent cx==[e+0x4618]
  when ecx!=-1), clear entry to 0 + decw count (+0x4730/+0x460e); not-found
  tail -> fn 0x59bf4(obj, edx=id, ebx=7/5). NOT msg dispatchers, NOT 0x1c01
  emitters. THE MSG-8 GUTTER ROAD IS ROW-SCROLLER BOOKKEEPING ONLY (self-send
  0x193 + row-table clear). PRIME-SUSPECT STATUS: CLOSED NEGATIVE.
- SAVE CORROBORATION (this run's saves 58/59/60.sav): STATSHIPLST b3=-1
  (no scrollbar) => strip law uses 632-28=604 — our x=620 clicks WERE in the
  gutter (consistent with the 0x33158 branch bookkeeping observed); [w+0x4f]
  = 0x66 stable.

## S6 FINAL RUN RESULT (run t299-leg-20261106-012002, rc=0, SESSION END
## 01:46:57, census-measured 9 windows, hits=96; relaunch loop exited after
## attempt 1 — no attempt 2; teardown SIGKILL dosbox pid=108013; production
## :9 (pid 1957) untouched)
- PTY WHOLE-LOG CENSUS: fn51cc4_entry 0, s2_56cda 96, w43508_51fc2 0,
  w43504_52003 0, btn_hdlr 0.
- 96-stop attribution by (window, edi): COSMOSWnd edi=0x3b x74 (background
  pump); STATSHIPLST edi=0x8 x4 — EXACTLY our four gutter clicks (250/120/
  453/300; ebx=0x26c=620, ecx=ebp=Y verbatim). Baseline window: 0 STATSHIPLST
  stops. msg 8 clicks are attributable, click-specific, and REPRODUCED 4/4.
- gate600058 probe after every click window: gate=0 datum59c=00000000 x4.
  Oracles sel43510=0, DAT_43504='Icarus' star-rec, DAT_43508=0x26fe77
  (churn constant, t297-A delta law), mode4226=0x12 all windows — NO oracle
  moved.
- VERDICT (STATE.md branch (c), honest negative for the emit chain): THE
  VENDOR MOUSE CLICK ARRIVES AT THE REGISTRY DISPATCHER fn 0x56ca4 AS MSG 8
  TARGETING STATSHIPLST'S OWN ENTRY (slot 8), NOT msg 0xc and NOT an emit to
  slot 95. fn 0x32664's msg-8 arm (0x32679 jbe 0x32720) routes to fn 0x33058
  (row bookkeeping; gutter sub-branch 0x33158 -> self-send 0x193 + row-table
  clearers fn 0x56730/fn 0x56434). THE t316 CHAIN'S INTAKE PREMISE
  ("in-rect msg-0xc click") IS LIVE-REFUTED: no user click posts msg 0xc to
  STATSHIPLST, and the emit road additionally needs [w+0x4f]==0x30 (0x66 in
  every save incl. this run's 58/59/60). fn51cc4_entry ZERO whole-log = the
  FLEETWND 0x1c01 delivery NEVER happened; the 0x600058 gate was never
  evaluated live. NO LEDGER ROW CLOSES (strict-close).

## S7 msg-0xc PRODUCER CENSUS (offline seed for t318; payload imm census
`ba 0c 00` = mov $0xc,%edx — 7 hits, decoded with ±context):
- 0x21638: msg 0xa/0xc/0/d sequence via fn 0x57464(0x7a35c) ebx=0x456e4
  (string operand) — NOTIFICATION/TEXT road, not a click.
- 0x38d3f, 0x3ffba: fn 0x3958c(win, edx=0xc, ...) — two sites, ecx/esi from
  [w+0x44]/[w+0x46] (0x3ffba) — LOOKUP road (returns u16, 0xffff = miss).
- 0x4b8c9: fn 0x55a60(0x7a35c, edx=0xc) GUARDED BY `mov 0x7e582,%eax;
  sar $0x16? (sar 0x10); cmp $0x10; je skip` — fires ONLY when
  [DAT_7e582(runtime 0x2c0582, t315 law)]>>16 != 0x10. THE ONLY
  MODE-CONDITIONAL msg-0xc poster.
- 0x54aa9: msg 0xc (ebx=ds:0x484ec pump word) / msg 4 (ecx=ds:0x484f0) via
  fn 0x56b5c — the per-turn PUMP road.
- 0x7ba77: arithmetic false positive (sub/cmc/sbb align idiom).
=> t318 QUESTION: does fn 0x55a60 (or fn 0x3958c) ever post msg 0xc INTO
fn 0x32664 (STATSHIPLST), and does ANY writer set [w+0x4f]=0x30 (byte-store
census `c6 8x 4f 00 00 00` and `88 8x 4f 00 00 00` = ZERO direct stores —
0x4f must be written by a struct/template copy; find it via the ctor fn
0x3264c region or a memcpy). If NO writer can make 0x4f==0x30, the
STATSHIPLST emit road is DEAD BY CONSTRUCTION (t315 LOADSCREEN pattern) and
the destination-entry widget hunt re-opens elsewhere (OQ-019 residue (2)
msg-0x50 family).

## S8 THE msg-0xc/4 INTAKE IS A BROADCAST PUMP (fn 0x56b5c, verbatim
## 0x56b5c..0x56c93) — THE t317 LEG SET MISSED IT; t318 SEED
- fn 0x54aa9 site context re-read: the per-turn pump posts msg 0xc (ebx=
  ds:0x484ec) OR msg 4 (ecx=ds:0x484f0, ebx=ds:0x484ec, push 0) into
  fn 0x56b5c(esi=0x7a35c). ORACLE NOTE: our saves' gate_484ec read 0x26c —
  the LAST-CLICK X law (620 = our gutter clicks), so the pump runs off the
  click record.
- fn 0x56b5c verbatim shape: mode gate [[obj+0x4226]>>16] >= 0; loop over a
  MASK TABLE stride 0x8e at obj+0x3068+mode*0x8e (t316's "count 0x3000"
  region = THIS table family), word [esp+0xc]=count from [obj+0x3068+mode*
  0x8e], per-entry: test mask byte (0xa2024+key), read target rec ptr
  [e+0x4], guard [tgt+0x35]/flags, THEN **0x56c74: call *[tgt+0xa7+8]** —
  SLOT-2 DISPATCH ON ARBITRARY REGISTERED WINDOWS with msg = [esp+8] (0xc
  or 4). ds:0xa2024 = per-msg suppression flags (set/cleared at 0x56c59/
  0x56c87).
- => THE REAL DELIVERY ROAD for msg 0xc/4 into fn 0x32664 is s2_56c74 (a
  t304 leg ALREADY IN THE REGISTRY, fired 1x in run 061825), NOT fn 0x56ca4.
  t317 armed s2_56cda only — msg-0xc/4 deliveries were INVISIBLE this run.
  fn51cc4_entry still zero = no 0x1c01 EVER reached FLEETWND regardless.
- t318 LIVE SHAPE (one run): legs {s2_56c74, s2_56cda, fn51cc4_entry,
  w43508_51fc2, w43504_52003} + the t317 click choreography VERBATIM (proven
  good: rails 188, msg-8 stops 4/4 attributable). Watch s2_56c74 stops:
  eax=target rec, msg [esp+8]. A msg-4 stop with eax=STATSHIPLST rec +
  s2_56cda edi=0x1c01 + fn51cc4_entry edx=0x1c01 CLOSES the destination-fire
  residue. If msg 4 hits STATSHIPLST but no emit: the in-rect gate at
  0x32730 is the blocker (pump msg carries NO click X? — ebx=msg arg,
  ebp=[w+?]; decode the pump arg law from banked regs).
- [w+0x4f] DIRECT-STORE CENSUS CLOSED (payload-wide, disp32 AND disp8
  encodings, movb/movw/movl imm+reg forms, offsets 0x4c..0x4f): EXACTLY ONE
  direct store — movb $0x0,[r+0x4f] @0x30bdb. The measured 0x66 is
  template/record-copy written (no byte-addressed writer). msg 4 does NOT
  test [w+0x4f] (S2 table), so t318 does not depend on it.
