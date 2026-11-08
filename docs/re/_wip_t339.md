# t339 — BatControlWnd INTAKE DECODE (ZERO CAPTURE): who posts 0x1c01 (or any msg) to registry slot 61, and what do the state-16-family SENDMESSAGE values do? (working notes, streamed)

Assignment: docs/STATE.md NEXT t339 (2026-11-07/08). Predecessors: t337
(routing machinery, current-state word), t338 (state-16 live drive ZERO;
BatControlWnd TYPE-19 parent rect 0,0-0,0; entry needs a POSTER to registry
slot 61 — REFUTED-ROUTES t338 amendment clause (3) binding).

## S0 — SITTING CHECK (first action)
tail -c 200000 work/r1/playcap/live-timeline.jsonl -> newest turn 1086 ==
corpus max. NEGATIVE. r1_t85g_sitting.py NOT run.

## S1 — banked-law inventory for the SENDMESSAGE consumer (in progress)
t302 POSITIVE CONTROL verbatim (docs/re/_wip_t302.md S5): btn_hdlr file 0x336b4
(type-0 button table slot 2), click NEXTTURN -> eax=0xfd6190 name='NEXTTURN'
edx=0x7 == windows.txt SENDMESSAGE 7. So the FILE SENDMESSAGE value IS the msg
id delivered to the widget's OWN class handler. fn 0x336b4 = msg router on dx:
branches {<7, 7..8 via 0x30de2/0x30dbb, <0xe, <=0xe, 0xf, <0xc9, 0xc9..ca,
else 0}; 0x33708: dx==0xd -> call [[eax+0xa7]+0xc] dxor edx (self msg 0xd).

## S2 — STATIC INTAKE CENSUS (scripts/r339_intake_census.py exit 0,
## work/r339_intake.out; whole image 140,824 insns 0x14bb0..0x826a5)
(1) call 0x56ca4 (POST-TO-HANDLE): 56 sites. Target edx provenance classes:
    edx=[rec+0x41] (own slot) ~27 sites; edx=[w+0x63] (PARTNER slot) 13 sites
    {0x30ecb, 0x32266, 0x3339c (t316 STATSHIPLST emit), 0x3d83f..0x3daf9 x8,
    0x56d09 (=sar16 of +0x4226 — dispatch guard path)}; edx=[core+0x3002]
    (FOCUS window) 5 sites {0x54701,0x56955,0x56969,0x569ae,0x569c2}; misc reg.
(2) call 0x56ad4 (RING-A poster): 44 sites (t337 count reproduced). THE PAIR
    0x2f32c / 0x2f4f9 (in fn 0x2f280+ span): edx = [esi+0x43]>>16 = FILE
    SENDMESSAGE, ebx = [esi+0x47] = SENDPARAM1 — the generic
    "post-this-widget's-SENDMESSAGE" poster. Target = [w+0x63] law to test.
(3) Immediates 0x324..0x335 in CODE: ONLY branch-compares inside fn 0x156d4's
    own msg tree (0x156ec cmp dx,0x327 / 0x156fd 0x32b / 0x1570e 0x32d /
    0x16275 0x329 / 0x162bd 0x325 / 0x163e4 0x324) + `mov edx,0x326` posters
    {0x15aed, 0x1972a} + `mov ebx,0x326` {0x1b127,0x1b9c7,0x1ba71,0x1baef} +
    0x2d9f8 mov ebx,0x32e. NO site posts literal 804/805/807..813. => child
    SENDMESSAGE values can only reach fn 0x156d4 GENERICALLY (data-driven).
(4) Stores to [reg+0x63]: 34 sites; the window-parser ones are 0x57c27,
    0x5812d, 0x5877c, 0x58bf4, 0x59017, 0x5961d, 0x5972b (t336 S1c named
    0x5961d/0x5972b = "[parent-window+0x63] = found win +0x41"). 0x59017 is
    INSIDE the t336 STATE/PARENT block (0x58f67->0x59021) — decode pending.
NOTE (record-vs-window base, t336 law): record base = win+0x20; rec+0x41 =
win+0x61, rec+0x43 = win+0x63 (SENDMESSAGE), rec+0x47 = win+0x67 (SENDPARAM1).
t316's "STATSHIPLST rec 0xfe7b48 +0x43=0x5f" and t336's "win+0x63=parent-slot"
are THE SAME FIELD — law to verify: [w+0x63] := PARENT window's slot-id at
parse time (then 0x2f32c posts the widget's SENDMESSAGE to its PARENT).
BLOCKED-BY-LAW: step (1) of the assignment (census [w+0x63] in saves) is DEAD
by t316 amendment clause (1) — registry NOT persisted in saves; the decode is
the static parent-link path + the 0x2f32c caller instead.


## S3 — THE ROAD EXISTS STATICALLY: [w+0x63] IS THE PARENT-SLOT, AND THE
## GENERIC BUTTON MSG-ROUTER POSTS THE FILE SENDMESSAGE TO IT VERBATIM
(1) PARSER LAW (verbatim, three identical sites 0x59012..0x59017,
    0x59618..0x5961d, 0x59726..0x5972b — inside the t336 PARENT-keyword
    blocks): after resolving the PARENT name via find-by-name fn 0x56d1c,
    `mov eax,[ecx+0x41]` (parent's registry slot-id) then
    `mov [ebp+0x63],eax` — CHILD.w+0x63 := PARENT's slot-id, plus call 0x30c20
    (link into parent's child list [w+0x67], cf. consumer fn 0x30c9c walks
    [esi+0x67] u32-array of child pointers). My^Items w+0x63 == 61 =
    BatControlWnd's slot-id BY CONSTRUCTION (t331 S4: parent BatControlWnd).
(2) CONSUMER LAW (fn at 0x30c9c span, the generic widget msg router; the
    0x336b4 branch chain lands HERE for msgs 2..0xca):
    - msg 4/5 (0x30e0e): rect-test click (ebx,ecx) vs widget [8/c/10/14];
      then if [esi+0x63]==0 -> RING-A post fn 0x56ad4(core, edx=cx msg,
      ebx=param) else 0x30ebd: `mov edx,[esi+0x63]; mov ebx,eax(SENDMESSAGE);
      ecx=param; call 0x56ca4` = POST-TO-HANDLE THE PARENT SLOT with msg =
      the FILE SENDMESSAGE VERBATIM.
    - msg 0xc (0x30f46->0x30edc = the t302-banked site): same rect-test then
      same parent-post 0x30ecb. THIS is the t302 "msg 0xc -> 0x30edc" law,
      now fully decoded: the rect test decides WHICH child gets clicked and
      the child's SENDMESSAGE goes to its PARENT.
    - msg 7/8 (0x30de2 press/release branch): NO parent post — only class
      self-msg 3 when [0x39]/[0x35]/[0x3d] all nonzero. => t338's clicks
      (all press/release 7/8 + 6) CANNOT propagate: consistent with t338.
(3) RECEIVER MATCH (data, verbatim): fn 0x156d4 BatControlWnd msg tree
    compares dx against 0x327/0x32b/0x32d/0x1c01/0x1c02 + sub-tree 0x162ac
    for <0x327 with 0x324 (My^Items SM) at 0x163e4 -> 0x158f3, 0x325
    (Other^Items SM) at 0x162bd. windows.txt state-16 family: My^Items SM
    804=0x324, Other^Items 805=0x325 (+807..813 for Pass/Auto/Repeat/W/S/Z/I;
    full table pending S3b). The parent's handler consumes EXACTLY the
    children's SENDMESSAGE values. The intake is DATA-DRIVEN through
    [w+0x63], not any hardcoded 804-immediate (S2(3)).
(4) WHAT t338'S ZERO DOES NOT COVER (arming-scope, t317 clause-3 class):
    t338 armed {chain legs, btn_hdlr, hit_test, focus, setstate, ringa}; the
    parent-post legs 0x30ebd/0x30ecb (msg 4/5/0xc intake) were NEVER ARMED.
    Hit-test fn 0x56890 posts msgs {8,6,7} (0x5694b..0x56988 verbatim) — no
    0xc/4/5 there. Banked t318: msg 4/0xc come via the BROADCAST PUMP road
    (posters 0x54aa9/0x54ab2 from click record ds:0x484ec/0x484f0).
    => t338's zero is NOT evidence the 0x324-to-parent road is dead; the
    delivery msg for propagation (0xc or 4) was never in any armed window.

## S3b — state-16 family SENDMESSAGE table (windows.txt verbatim, parsed)
BatControlWnd TYPE19 STATE '1 16' SM=0 rect 0,0-0,0; BatListWnd TYPE10 SM=0
rect 474,142-632,394; children (all STATE '1 16', MOUSEFOCUS 1):
My^Items 804 SP1=0 rect 479,103-548,133 | Other^Items 805 SP1=0 557,103-626,133
| Repeat 809 SP1=999 531,55-574,85 | Pass 807 479,55-522,85 | Auto 808
583,55-626,85 | W 810 479,103-509,133 | S 811 518,103-548,133 | Z 813
557,103-587,133 | I 812 596,103-626,133. (t338's clicked pixels map onto
Pass/Auto/Repeat/My^Items/Other^Items exactly.)

## S4 — THE FULL PROPAGATION CHAIN DECODED (all edges verbatim)
CLICK msg 8/6/7 arrives at the hit-tested window's OWN class entry (t317
measured law). The GENERIC per-widget msg router fn 0x30c9c (sole caller
0x30b57; arms reached via the 0x336b4 dx-compare chain) routes:
  msg 4/5 (0x30e0e): rect-test; [w+0x63]!=0 -> 0x30ebd POST [w+0x63] msg=SM.
  msg 0xc (0x30f46 -> 0x30edc): rect-test; same parent-post 0x30ecb.
  msg 7/8 (0x30de2/0x30dbb): NO parent-post EVER (only self msg 3 when
    [0x39]&&[0x35]&&[0x3d]). => t338's battery (all 7/8/6) COULD NOT
    propagate. Its zero is an ARMING-SCOPE fact for msg 4/0xc (t317 clause-3
    class), NOT a measurement of the parent road.
  msg 2/3 (0x30d37/0x30d63): focus/bookkeeping, no parent-post.
PARENT-SLOT LAW (parser, verbatim x3): 0x59012-0x59017 / 0x59618-0x5961d /
0x59726-0x5972b: parent found via fn 0x56d1c, then `mov eax,[parent+0x41];
mov [child+0x63],eax` + link fn 0x30c20 into parent child-list [w+0x67].
My^Items [w+0x63] == 61 BY CONSTRUCTION (parent BatControlWnd, live slot 61
t331 S50 measured 0xfdbe34 slot 61).
BROADCAST PUMP fn 0x56b5c (VERBATIM 0x56ba3 loop): walks state-table slots
31..0 of CURRENT state ([core+0x4226]>>16), per-window gate [rec+0x35], and
THE PARENT-PRIORITY LAW at 0x56c34: `if [w+0x63]!=0 && msg>2 -> edx=1` else
0; edx==0 -> DELIVER via call [[w+0xa7]+8] @0x56c74; edx==1 -> SKIP (bubbling
road). msg 0xc/4 posters 0x54aa9/0x54ab2 verbatim (click record
ds:0x484ec/0x484f0; 0xc iff edi==[esi+0x24da4] && [esi+0x489e]==0).
RECEIVER fn 0x156d4 (BatControlWnd, class 0x5850 slot 2): dx tree
{<0x327 -> 0x162ac sub-tree (0x324 My^Items @0x163e4, 0x325 Other^Items
@0x162bd); 0x327/0x32b/0x32d arms; 0x1c01 -> 0x15ebf; 0x1c02 -> 0x1625c}.
CFG (scripts/r339_cfg156d4.py, 941 insns 0x156d4..0x164ba): from ENTRY the
j-edge reachable set contains 0x15ebf, 0x162ac, 0x163e4, 0x162bd — the child
msgs DO reach their branches. The GATE/gate-post blocks {0x15fed, 0x16147,
0x16181} are reachable ONLY through the 0x15ef1 JUMP TABLE `jmp cs:[eax*4+
0xb04]` (RAM-rebased, t331 law: live members [0]=0x15ef9 [1]=0x15fed
[2]=0x16181 [3]=0x15ef9) — i.e. ONLY the 0x1c01 branch feeds arming. The
0x324/0x325 legs do NOT reach 0x16147 (t331's open question ANSWERED:
branch = 0x1c01 leg via table member; 0x16181's no-direct-j-edge = table-only,
confirmed).
SELF-POST: 0x16162..0x1616f (t331-banked) re-posts 0x1c01 to SELF via
[[ebp+0xa7]+0xc] — arming is 0x51->slot63->fn0x1aef8->0x1b7dd; the 0x1c01
self-post is a re-entry, not an external entry.

## S5 — b9 STATE MACHINE + THE SELF-POST IDENTITY (the intake question answered)
(1) windows.txt SENDMESSAGE FULL CENSUS (parsed 123 blocks verbatim): distinct
    values = {0,1,2,2,3,5,7,7,8,50..58,60,61,62,71,76,84,201,501,503,505,
    804,805,807..813,1002..1006}. NOTHING >= 7169 (0x1c01). No file value can
    produce a 0x1c01 post. Whole-image CODE literal census (0x1c01/0x1c02):
    18 sites = 14 compares (receiver branches) + 4 senders {0x16168 (self-post,
    fn 0x156d4 tail), 0x33374/0x3338e (STATSHIPLST emit, target [w+0x63]=95
    FLEETWND — t316 verbatim), 0x35696 (LOADSCREEN)}. t315 sender inventory
    REPRODUCED EXACTLY (its 5th site = 0x1642c receiver cmp). NO new poster.
(2) b9 LAW = SHAPE-FRAME/VIEW-MODE WORD [ebp+0xb9] (BatControlWnd):
    ctor fn 0x15630 zeroes b9=0 (0x15a0 store verbatim); msg 0x324 branch
    0x158c0: if b9!=1 {b9=1; call fn 0x16cf0; call [[ebp+0xa7]+0xc] edx=0};
    msg 0x325 branch 0x158f3: if b9!=4 {b9=4; call fn 0x16cf0; same edx=0
    self-post}. fn 0x16cf0 = child-list walk matching string-id 0x13e (shape
    lookup fn 0x76ce0) — a REDRAW/frame routine, NOT combat logic.
    0x15ebf (the 0x1c01 receiver branch): reject iff [BatModeWnd]+0xb7==4;
    al = b9-1; jmp cs:[eax*4+0xb04] REBASED (t331 live members [0]=0x15ef9
    [1]=0x15fed [2]=0x16181 [3]=0x15ef9). b9==0 -> al=0xffffffff >3 -> 0x15b39
    default exit.
(3) THE IDENTITY RESULT: the ONLY posts of 0x1c01 into slot 61 are the
    0x324/0x325-branch self-posts, and BOTH run with b9 JUST SET to 1/4 —
    al = 0 or 3 -> table member 0x15ef9 (or default 0x15b39), NEVER the
    arming members {0x15fed, 0x16181}. Those members need b9 IN {2,3} AT
    ARRIVAL. The writers of b9 2/3 (0x15f1e/0x15f25/0x15f35) are INSIDE the
    gate block itself (self-bootstrapping: gate sets b9, tail 0x16168 re-posts
    0x1c01, second arrival takes member [1]/[2]) — plus banked msg-0x320
    param arms (S5d below).
(4) CFG PROOF (scripts/r339_cfg156d4.py + whole-image j-edge index): the ONLY
    in-edges to the gate block in the ENTIRE image are 0x1608e je 0x16147 and
    fallthrough 0x15fed-chain; 0x15fed/0x16181 have NO direct j-edge anywhere
    (t331's open question CLOSED: reachable ONLY via the rebased 0x15ef1
    table). The `mov eax,0x16147` sites {0x273b6,0x29143,0x46299,0x463be,
    0x4b16c...} are arithmetic coincidences in other code (sub/eax imm), not
    code pointers; no u32 in any table equals 0x15fed/0x16181.

## S6 — VERDICT: THE INTAKE IS FULLY DECODED; THE MODE-1 ARMING FEED HAS NO
## POSTER ANYWHERE (EIGHTH CITED-DEAD LEG); CHILD SM VALUES DECODED
(1) WHO POSTS 0x1c01 TO SLOT 61: ONLY fn 0x156d4's OWN tail 0x16162..0x1616f
    (`mov ebx,[ebp+0xa7]; mov edx,0x1c01; mov eax,ebp; call [ebx+0xc]`), and
    that tail sits INSIDE the gate block: its only in-edges in the WHOLE image
    are 0x16071 jmp and 0x16145 jmp (both inside 0x15fed..0x16181, verified by
    whole-image j-edge index) — which are reachable ONLY through the 0x15ef1
    rebased jump table from the 0x1c01 branch itself. The tail is a RE-POST
    (self-bootstrap: gate sets b9 2/3 at 0x15f1e/0x15f25/0x15f35 then re-posts;
    second arrival takes table member [1]/[2]). An EXTERNAL first arrival with
    b9==0 (ctor zeroes b9 verbatim 0x15a0-store) computes al=0-1=0xffffffff >3
    -> default exit 0x15b39. NO file SENDMESSAGE value >= 7169 exists (full
    windows.txt census: max 1006). Whole-image 0x1c01 literal: 4 senders, all
    accounted dead-or-self (t315 inventory reproduced exactly).
    => BatControlWnd msg-tree entry fn 0x156d4 is UNREACHABLE from any
    observable in-game traffic — eighth cited-dead leg of OQ-016 residue-(1).
(2) WHAT THE STATE-16-FAMILY SENDMESSAGE VALUES DO (assignment part 2, closed
    by static measurement): they are msg ids posted TO THE PARENT (slot 61) via
    the generic router msg-4/5 (0x30e0e->0x30ebd) and msg-0xc (0x30f46->
    0x30edc->0x30ecb) roads, gated by the t338 hit rect + the pump parent-
    priority law (fn 0x56b5c 0x56c34: [w+0x63]!=0 && msg>2 -> child skipped,
    msg bubbles to parent). Receiver branches (data-matched): 0x324 My^Items
    -> 0x158c0 {if b9!=1: b9=1, fn 0x16cf0 shape-redraw, self-post msg 0 via
    class slot 3}; 0x325 Other^Items -> 0x158f3 {same with b9=4}. 807..813
    (Pass/Auto/Repeat/W/S/Z/I) have NO branch in fn 0x156d4 (tree: <0x322 ->
    0x16410/0x163f4 arms only 1/0xd/0x320; 0x322/0x323 -> 0x15baa; default
    0x1573b -> call fn 0x336b4 generic) — they fall through to the generic
    router (no-ops at the parent). The 804/805 legs CANNOT arm mode-1: they
    never reach 0x16147 (CFG S4) and never post 0x1c01 (their self-posts carry
    edx=0).
(3) b9 STATE MACHINE (verbatim): ctor b9=0; 0x320 arms {param 0->1 @0x15b51,
    2->3 @0x15b48, 3->2 @0x15b1e each + fn 0x16cf0 + self-post 0}; 0x324->1,
    0x325->4; gate legs set 2/3 (0x15f1e/0x15f25/0x15f35). The 0x320 msg's ONLY
    posters are BatModeWnd back-posts {0x1b164, 0x1b202, 0x1bb5e, 0x1bf80}
    with target edx=[[BatModeWnd]+0xab]+0x41 — the STATE-TABLE slot, and
    BatModeWnd's state table is NULL at t=1086 (t331: [+0xab]=NULL 20/20 saves,
    setter asserts for count=0) => those posts never executed (consistent:
    BatModeWnd b7==1 ZERO in t332+t338; the posts sit on b7-clearing paths).
    0x326 posters: 0x15aed (BatControlWnd internal, fn 0x15baa-region),
    0x1b127/0x1b9c7/0x1ba71/0x1baef (BatModeWnd, same NULL-table target).
(4) t338 ZERO RE-READ (honest scope): fn156d4_entry ZERO in state 16 IS
    meaningful for the 0x324/0x325 road (entry leg sees ANY msg) — but the
    parent-post legs {0x30ecb, 0x30e0e, 0x30f46} and pump legs were never
    armed, so whether msg 4/0xc EVER bubbles from the battle children to slot
    61 remains unmeasured (UI-law question, not arming). Even if 0x324/0x325
    delivered, S6(1)+(2) prove mode-1 arming still cannot happen (no 0x1c01
    feed). The arming residue is now CLOSED-BY-CONSTRUCTION as a negative:
    unreachable from ALL identifiable feeds; only user ruling D2-c moves the
    row. LEDGER: nothing closed strict-close; residue-(1) REWRITTEN with the
    EIGHTH leg named + intake decode cited.
INSTRUMENTS: scripts/r339_intake_census.py (exit 0, work/r339_intake.out),
scripts/r339_cfg156d4.py, scripts/r339_xreach.py (work/r339_xreach.out),
scripts/r339_dump.py (range dumper). Zero capture; production :9 untouched;
game/ read-only.

## S7 — SAVE-AXIS CENSUS ATTEMPTED AND DIED ON THE t316 LAW (honest negative)
scripts/r339_rec_census.py over t299-leg-20261105-112859/save/41..49.sav
(incl. the five state-16 saves): ZERO hits — raw byte counts prove WHY:
`My^Items`, `BatControlWnd`, `STATSHIPLST`, `FLEETWND`, `COSMOSWnd` occur
0 times and magic 0x12345678 occurs 0 times in 43.sav. The window records and
their NAME strings are NOT in the save image AT ALL (t316 amendment clause (1)
corroborated directly for the whole family, not just the registry table).
Assignment step (1) ("census [w+0x63] in the state-16 saves") is therefore
DEAD-BY-LAW, not by instrument bug: [w+0x63] is runtime-only; the parent-link
law stands on the PARSER sites (S4, three verbatim sites) + t316's live
measurement (STATSHIPLST +0x63==95 via debugger). Script exit 1 = instrument
negative, kept in tree as the reproduction.

## S6b — AMENDMENT: FOR THE BATTLE FAMILY THE PARENT-POST ROAD IS ITSELF
## STRUCTURALLY BLOCKED (two verbatim edges; strengthens S6(2))
The generic router arms 4/5 (0x30e0e) and 0xc (0x30f46->0x30edc) post the
child's SENDMESSAGE (WORD [w+0x45] = high half of the +0x43 dword; verbatim
0x30e35 `mov cx,[esi+0x45]`, 0x30ec4 `mov ebx,eax`) + SENDPARAM1 ([w+0x47])
to [w+0x63] — BUT to take those arms the CHILD must first RECEIVE msg 4/5/0xc,
and for state-16 children that can't happen:
(a) PUMP PARENT-PRIORITY (fn 0x56b5c verbatim 0x56c34): `if [w+0x63]!=0 and
    msg>2 -> edx=1` -> NOT dispatched (0x56c7b path). The msg-4/0xc posters
    (0x54aa9/0x54ab2) go THROUGH the pump, so parented children (My^Items
    +0x63=61) are never delivered 4/0xc; the pump hands them to the
    PARENTLESS windows of the state instead.
(b) PARENT RECT EMPTY: BatControlWnd rect 0,0-0,0 (windows.txt verbatim + t338
    clause (3)); the pump DOES deliver msg 4/0xc to IT ([+0x63]==0), but
    fn 0x156d4's msg 4/5/0xc arms fall through the dx-tree (all <0x327 ->
    0x162ac -> 1/0xd/0x320 arms only) to default 0x1573b `call 0x336b4`, whose
    rect-test (0x30edc: x in [0,0], y in [0,0]) fails for every real click.
(c) CHILDREN HAVE NO CUSTOM CODE (type 0/32 generic; class-table slot 2 =
    fn 0x336b4 — t302 banked for type-0; table dumps show 0x336b4 installed
    across the widget class tables), so no child-side poster of their own SM
    to slot 61 exists outside the blocked router arms.
=> The 804..813 values are DORMANT data for the battle family: consumed only
if some future poster posts 4/5/0xc-with-coords directly to a child slot.
t338's fn156d4_entry ZERO (state 16, family clicks) is now EXPLAINED
statically, closing the "was it just arming scope?" worry for the arming
question: no msg road into fn 0x156d4 exists for ANY of {0x1c01, 0x324, 0x325,
807..813} from observable traffic. EIGHTH cited-dead leg stands.
