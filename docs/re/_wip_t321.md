# t321 — OFFLINE DECODE: fn 0x51cc4 (FLEETWND msg entry). What do msg 4 / msg 0xc do; is 0x1c01 reachable here?

Fresh session 30, 2026-11-06. Source: work/t91_code_disasm.txt (objdump of
work/ascend_restored.bin). Sitting check FIRST: 200MB tail max turn 1086 ==
t319/t320's newest — NO new play, r1_t85g_sitting.py not run.

## S0 — fn 0x51cc4 dispatch map (VERBATIM, disasm lines 73623-73839)

Prologue 0x51cc4 (56 57 55 81 ec bc 01 00 00): eax=edi=window, dx=msg saved
[esp+0x1b4], ebx [esp+0x1b0], ecx [esp+0x1ac], later-pushed edx [esp+0x1b2].

Dispatch on msg (dx, 16-bit):
- cmp dx,2 @0x51ce5; jb 0x5206f; jbe 0x51f0c  (unsigned)
  -> msg<2 -> 0x5206f: cmp dx,1; je 0x51d29 (msg-1 gate chain, t315's);
     else (msg 0) -> jmp 0x51d00 (default)
  -> msg==2 -> 0x51f0c: eax=[[eax+0xab]+0x8cd]; [edi+0xaf]=ax (set batmode
     word from rec); call fn 0x336b4 (default tail); ret. NO DAT store.
- msg>2: cmp dx,0x1c01 @0x51cf5; je 0x51f3b (THE 0x1c01 HANDLER);
  -> ELSE (msg 3,4,5,... 0xc,...) FALL THROUGH 0x51d00 = DEFAULT:
     reload args, sar edx,0x10, call fn 0x336b4, ret.
     *** msg 4 AND msg 0xc have NO dedicated branch in fn 0x51cc4. ***
     *** They hit generic fn 0x336b4 with ZERO stores on the path. ***

0x1c01 HANDLER 0x51f3b-0x52058 (the ONLY in-window road to the DAT writers):
- 0x51f3d eax=[[orig eax]+0xab] (accessor record), dx=u16 [esp+0x1b0] (ebx arg)
- 0x51f4b call fn 0x32fa4 -> eax=rec (esi), ecx=?? (index out)
- 0x51f54 cmp ecx,5; jne 0x52059
- ecx==5 path 0x51f57: call fn 0x56d1c(0x7a35c, 0x2b6b, ecx=-1) -> [edi+0xab]
  ; call fn 0x4da1c(esi); call fn 0x56ad4(0x7a35c, ebx=8, edx=1) pub code 8;
  [edi+0.af]=[[edi+0xab]+0x8cd]; ret -1
- 0x52059 (ecx!=5): al=[[rec]+0x58]-1; cmp al,4; ja 0x5207e (ret 0);
  jmp [eax*4+0x3d100] jump table @0x52067 — modes 0..4 (u8 [rec+0x58])
- TABLE TARGETS SEEN: mode1 0x51fb5: eax=[rec+0x59]; *** mov ds:0x43508,eax
  @0x51fc2 ***; pub fn 0x56ad4(code 0x11); [edi+0xaf]=rec+0x8cd word; ret -1
  mode2 0x51ff6: eax=[rec+0x59]; *** mov ds:0x43504,eax @0x52003 ***; pub
  code 0x11; ret -1.  mode3 0x52037: pub fn 0x56ad4(0x7a35c, edx=3, ecx=0,
  ebx=0); ret -1 (no store). modes 0,4 at 0x3d100 table (TBD).

## S1 — HEADLINE (static, verbatim): THE DAT_43508/43504 STORE ROAD IS
## MSG-0x1c01-ONLY INSIDE fn 0x51cc4. msg 4 and msg 0xc are default-handled
## (fn 0x336b4) and touch NOTHING. Therefore the t319/t320 poster family
## (which posts msg 4, and would post 0xc) can NEVER reach the destination
## writers — independent of whether the poster ever fires active-pass.
## Corollary: t312's whole-log writer-zero is fully explained by 0x1c01
## never firing (t312 S2 s2_356a5=0), not by the writers being dead code.
## S2 — fn 0x336b4 (default msg handler, ALL non-2/non-1c01 msgs incl. 4 and
## 0xc) FULL DISPATCH TREE VERBATIM (disasm lines 36507-36540, 32947-33120):
- tree: dx<7 -> 0x30f55 | dx==7 -> 0x30de2 | 8..0xd -> 0x30f46 | dx==0xe ->
  0x30dbb | dx==0xf -> 0x30dd2 | 0x10..0xc8 -> 0x30fa9 (RET 0, DEAD) |
  dx==0xca -> 0x30f26 | dx>0xca -> ret 0.
- 0x30f55 (dx<7): dx<2 -> 0x30f9f (dx==1 -> 0x30d37; else ret 0); dx==2 ->
  0x30d63; dx==3 -> 0x30fa9 ret 0; **dx==4 OR 5 -> 0x30e0e**; dx==6 ->
  gate [win+0x39]/[+0x35]/[+0x3d] all !=0 -> call [win+0xa7 -> +0xc] edx=2.
- **msg 4 path 0x30e0e**: rect hit-test ebx/ecx in [win+8/0xc/0x10/0x14], out
  -> 0x30fa9 ret 0. In-rect: reads [win+0x45/0x47/0x4b] (0x3e7 sentinel
  swap with di), [win+0x57] sar16 != -1 -> fn 0x4fb30(0x78638); then
  [win+0x63]==0 -> ring post fn 0x56ad4(0x7a35c, edx=movsx[win+0x45],
  ecx=ebx_win, ebx=[esp]); else [win+0x63]!=0: movsx cx==0x3e6 -> ring post
  (edx=[esp-2] sar16, ecx=0); else 0x30ebd REGISTRY DISPATCH fn
  0x56ca4(0x7a35c, edx=[win+0x63], ebx=win) -> target [obj+edx*12+4] cp+8
  member (t316 law). NO DAT store anywhere in fn 0x336b4.
- **msg 0xc path 0x30edc**: rect hit-test (ebx vs [eax+8]/[eax+0x10], ecx vs
  [eax+0xc]/[eax+0x14]); out -> 0x30fa9 ret 0; in-rect: [esi+0x4f]!=0x30 ->
  ring post fn 0x56ad4(0x7a35c, edx=5, ecx=0, ebx=&[esi+0x4f]); ret -1.
  NO DAT store, NO registry forward.
- dx==7 -> 0x30de2: triple gate [+0x39]/[+0x35]/[+0x3d] -> call [cp+0xc]
  edx=3. dx==0xe -> [+0x35]=-1,[+0x39]=-1. dx==0xf -> [+0x35]=0.
  dx==0xca -> ring post code 6. msg 0xd -> call [ebx+0xc] edx=0 (0x336b0
  block, shares fn body).
- CONCLUSION S2: msg 4 -> rect-gated ring-post OR registry dispatch fn
  0x56ca4; msg 0xc -> rect-gated ring post code 5 ONLY. NEITHER reaches
  DAT_43508/43504 or ring code 0x11/0x10 through fn 0x336b4 itself.

## S3 — DAT WRITER CENSUS (whole disasm, literal a3 stores; 5+5 sites):
DAT_43508: 0x1b5e6 (fn 0x1aef8), 0x1baa7 (**fn 0x1b91c = BATCON click
handler — t297 law: [win+0xaf]!=0 routes EVERY click here**), 0x51a8e (fn
0x51834 STATUSWND), 0x51fc2 (fn 0x51cc4 FLEETWND 0x1c01 leg1), 0x55bbd (TBD).
DAT_43504: 0x28ec2, 0x28ef6 (TBD), 0x36b01 (TBD), 0x52003 (fn 0x51cc4
0x1c01 leg2 state-4), 0x55d35 (TBD).
=> t321 HEADLINE REFINED: the ONLY msg-driven roads to the destination store
are (a) msg 0x1c01 into a STATUSWND/FLEETWND handler (needs the 0x1c01
sender — t314/t315: keyboard sender is LOADSCREEN-menu-only, dead in-game),
and (b) the BATCON family fn 0x1b91c/fn 0x1aef8 which is the CLICK route
when [win+0xaf]!=0 (batmode active). The broadcast pump (msg 4/0xc) is a
DEAD END for the store road — closure confirmed independent of the poster
gate. THIS SELECTS THE t322 FORK: batmode/mouse capture, NOT Button1 HOLD
for the pump.
## S4 — BATCON CLICK FAMILY FULLY DECODED (fn 0x1b91c verbatim, disasm
## 8148-8229; callers 0x1b0cc + 0x1b1de BOTH inside fn 0x1aef8 = class-table
## 0x88498 SLOT-2 msg handler {1abfc,30d08,1aef8,1d858,311b8,1e9dc}):
fn 0x1b91c state machine (esi=batcon window; NO click coords read — state is
[win+0xaf] pending-object ptr, [win+0xb3] stored-object ptr, [win+0xb7] u8
sequence state):
- entry 0x1b921 assert [win+0xaf]!=0 (fail -> fn 0x2a428 0x82ffe/0x3d7).
- ecx==0 -> fn 0x1ca38(win, [win+0xaf]) -> tail 0x1bb1f.
- [win+0xb7]==1 branch 0x1b962: kind dispatch via REGISTRY fn 0x56ca4
  (codes 0x322/0x326), no DAT store.
- 0x1b9ee: dl = BYTE [[win+0xaf]] (object kind):
  * dl==2 (0x1b9f9): first-click arm — iff [win+0xb7]==0: [win+0xb3]=obj;
    gate [[[obj]+0x54] sar16 == ds:0x7458e (CURRENT TURN)] and [[obj+1]+0x88]
    >0 -> [win+0xb7]=2. NO store.
  * dl==1 (0x1ba45): ch=[win+0xb7]; ch==2|3 -> 0x1ba5e clear state + registry
    dispatch 0x56ca4 code 0x326 ecx=2; ELSE (ch==0) 0x1ba8c: cmp clicked-obj
    eax == [win+0xb3] stored; jne 0x1bac0 (re-store, no DAT); test ch,ch jne;
    -> ecx=1, eax=[[stored]+1], ebx=0x11, *** mov ds:0x43508,eax @0x1baa7 ***,
    [win+0xaf]=-1, ring post fn 0x56ad4(0x7a35c, edx=1, ecx=1, ebx=0x11).
    *** THIS IS THE PER-SHIP DESTINATION STORE t308-t312 hunted. ***
  * dl==3 (0x1bad3): registry dispatch code 0x326 ecx=4 (bh gates), no store.
- tail 0x1bb1f: if ebp==-1: registry post code 0x320 on [win+0xb3]; fn
  0x1be10(win).
fn 0x1aef8 ALSO holds a DAT_43508 store @0x1b5e6 (S3 census; context TBD).

## S5 — THE DECISIVE HARNESS FACT: THE LEG SET NEVER COVERED THE BATCON
## WRITERS. scripts/r299_leg_session.py dict (lines 224-231, verbatim):
## w43504_{28ec2,28ef6,36b01,52003,55d35} + w43508_{51a8e,51fc2,55bbd} = 8
## legs. 0x1b5e6 and 0x1baa7 (the fn 0x1aef8/fn 0x1b91c stores — the CLICK
## road) were NEVER ARMED in any capture t307..t320. Every "writer zero
## whole-log" negative t307-t312 measured only the STATUSWND/FLEETWND-0x1c01/
## cosmos-fallback/diplomacy/0x55bxx sites. t307 proved the leg instrument
## CATCHES stores (w43504_28ec2 fired live), so arming 1baa7/1b5e6 is the
## highest-value live probe that exists for OQ-019.
## Attribution of the 8 armed sites (leg comments + t307/t308 landings):
## 28ec2/28ef6 = cosmos star-fallback fn 0x28e70 (28ec2 FIRED LIVE t307,
## EAX=0x256825 Icarus); 36b01 = diplomacy row eax=[ebx+0x13000]; 52003 =
## FLEETWND 0x1c01 state-4 leg; 55d35 + 55bbd/51a8e/51fc2 = 0x55bxx dispatcher
## fn (cmp-tree on ecx codes -> edi=0x10/0x11 store+post; 0x55bbd edi=0x11
## store eax; 0x55bcc store edx; turn-gate 0x484ec>0x96 on 51a8e per comment).

## S6 — t322 FORK RESOLVED BY S1+S2+S4+S5: batmode/batcon TWO-CLICK capture
## with NEW legs {w43508_1b5e6, w43508_1baa7} (+ entry legs fn 0x1aef8,
## fn 0x1b91c for attribution). The Button1-HOLD-for-pump branch is DEAD:
## per S1/S2 the pump's msg 4/0xc cannot reach any DAT store from FLEETWND
## regardless of which id the poster posts, so making ds:0x484ac!=0 buys
## nothing for OQ-019. Premises to verify in-run: (P1) BATCON window class =
## table 0x88498 -> RAM cp; clicks on the galaxy while [win+0xaf]!=0 arrive at
## fn 0x1aef8 slot 2 (entry leg); (P2) the arm gate [[obj]+0x54]sar16 ==
## ds:0x7458e means owner-turn — pick a CURRENT-turn ship; (P3) two-click
## semantics: kind-2 arm then kind-1 confirm on SAME stored object (read
## [win+0xaf]/[win+0xb3]/[win+0xb7] live at a fn 0x1b91c stop to learn the
## real choreography BEFORE scripting clicks — recorder-first law t318).

## S7 — RECONCILIATION WITH t296/t297 BANKINGS (no re-derivation; deltas only)
- t296 S4/S5 ALREADY banked fn 0x1aef8's msg-0x50 publish block (0x1b5ba gate
  -> 0x1b5e6 store + ring 0x11) and the [win+0xb7] mode enum. t321 CONFIRMS
  independently: the only branch into [0x1b5ba,0x1b600) whole-image is jbe
  0x1b7d7, and 0x1b7cd is `cmp dx,0x50` — msg 0x50 is the publish trigger,
  BatModeWnd-internal. fn 0x1b91c decode (S4) matches t296 S5's reading
  (0x1ba8c order-issue leg, 0x1bad3 planet leg, kind dispatch 2->3/1->2/3->4).
- t297 law RE-READ PRECISELY (fixes a misreading floating in t310-t320
  NEXT-ACTION prose): "msg-4 router 0x1b070 dispatches on [win+0xaf] NON-NULL
  -> batcon 0x1b91c(ecx=1)" is INTERNAL to fn 0x1aef8 (BatModeWnd's OWN slot-2
  handler, disasm 7418/7493 callers at 0x1b0cc/0x1b1de). It is NOT a global
  router: a msg 4 reaches 0x1b91c ONLY IF BatModeWnd ITSELF received the msg 4.
- SCOPE HONESTY on S2: msg 4 in-rect at 0x30ebd DOES forward via registry
  dispatch fn 0x56ca4(edx=[win+0x63]) to ANOTHER window's handler (t316 slot-id
  law) — so "msg 4 reaches no store" is proven for FLEETWND's own code and for
  fn 0x336b4, [inferred] not for whatever window the registry forward selects.
  t318's census (msg 4 never even reached FLEETWND live) keeps this theoretical.
- LIVE NEGATIVES THAT FRAME t322 (from LANDED t297-t312, binding): sprite-pixel
  click (48,151) lands at 0x3cb8d in the type-0 class 0x247cb8 btn_hdlr, NOT in
  fn 0x1aef8 (t312); t299 sprite/planet/empty clicks = ZERO stops at six
  downstream legs; batmode_dead (0x1AEF8 entry leg) EXISTS in
  r299_leg_session.py line 163 but was NEVER the primary leg of a galaxy-click
  battery (only cos_hdlr companion, line 1048); sel43510=0 every snapshot;
  handler ptr 0x1aef8 has exactly ONE RAM hit (static image member 0x247978) —
  z-order/window-composition is the unnamed blocker, NOT the code path.
- FINAL t322 SPEC (supersedes S6's sketch): legs {batmode_dead 0x1aef8,
  fn51b91c_entry=0x1b91c, w43508_1b5e6, w43508_1baa7} + btn_hdlr control +
  Icarus-view click battery (sprite 48,151 / planet 439,331 / empty 236,200 —
  census values t312) with recorder-first reads of [win+0xaf]/[+0xb3]/[+0xb7]
  at every fn 0x1aef8 stop. DECISION TREE: (a) fn 0x1aef8 stops>0 -> learn
  choreography from live state bytes, script the two-click, close the OQ-019
  select leg on a witnessed 1baa7/1b5e6 store; (b) fn 0x1aef8 stops=0 while
  btn_hdlr>0 -> BatModeWnd is z-order-shielded at the campaign map: the named
  blocker moves to window composition (STATE 1 16 activation), offline probe =
  who writes the STATE bytes / what shows the window; Button1 HOLD stays dead.

