# t337 — STATE-TABLE READER WALK (zero capture)

Task (docs/STATE.md NEXT ACTION): enumerate who READS the winmgr per-id STATE
table (winmgr + 0x3066/0x3068/0x306a + 0x8e*id, global distinct-id counter
winmgr+0x4226), attribute each reader function by call chain, and answer the
residue-(1) question: is ANY reader battle-mode-1-reachable?

## S0 — Inputs and carried laws
- Disasm: work/r331_disasm.txt (objdump -D -M intel, restored payload image,
  imagebase 0 => addresses ARE payload-file offsets). 7,135,820 bytes.
- t336 geometry (VERBATIM, docs/re/_wip_t336.md S4): fn 0x57194 register,
  fn 0x57284 remover. edx = winmgr + id*0x8e; count = WORD [edx+0x3068]
  (dword read at +0x3066, sar 0x10); handles u32 [edx+0x306a .. +0x306a+4*31];
  global count WORD [winmgr+0x4226]; asserts id<0x20 (:0xb37), handle<0x400
  (:0xb38), slot<0x20 (:0xb5a).
- t336 census: table located W=0x2bc3e4 in 196/196 saves
  (scripts/r336d_state_census.py exit 0). => absolute table base
  0x2bc3e4+0x3068 = 0x2bf44c (for cross-checking absolute-address readers only;
  in-image code uses a base register).
- Sitting check this iteration: NEGATIVE (tail-seek, newest turn 1086 == corpus).
- REFUTED-ROUTES check: line 747 region re-read before starting (see S0b).

## S1 — READER CENSUS (scripts/r337_state_readers.py, exit 0; whole image
## 139,026 insns 0x14bb0..0x826a5; sites = displacements 0x3066/0x3068/0x306a/
## 0x4226 OR `imul *,0x8e`; function extents = next call-target start).
16 functions touch the STATE table. READ sites (non-writer) by function:
  fn 0x543fc (1 stride+store WORD[..+0x3066],0xffff)  callers: 0x5431f
  fn 0x54650 (3x read +0x4226)  callers: 0x217b3 0x555f9
  fn 0x54d18 (3x read +0x4226)  callers: 0x54951
  fn 0x5526c (4x read +0x4226)  callers(9): 0x1bf32 0x27c1e 0x548f7 0x54e09 0x5573b 0x55a0c 0x55b8a 0x56029 0x59a8d
  fn 0x55ae8 / fn 0x55df4 (1x each +0x4226)  callers: 0x54b74 / 0x54b4a
  fn 0x56890 (READS +0x4226, +0x3068, stride, +0x306a)  callers: 0x547f3 0x57014
  fn 0x56b5c (READS +0x4226 x2, +0x3068, stride, +0x306a)  callers(9): 0x53fa3 0x54976 0x54ac5 0x54b36 0x5531e 0x5548c 0x55f82 0x56f0f 0x57003
  fn 0x56ca4 (READ +0x4226)  callers(56) incl. 0x1615d 0x161d1 (the t331 0x1c01 posters)
  fn 0x56d8c (READ +0x4226, stride, +0x3068, +0x306a)  callers(10): 0x24fdc 0x2670b 0x27565 0x276f3 0x27ebb 0x28f00 0x363bd 0x3643e 0x36476 0x52742
  fn 0x56e10 (READS +0x4226 x4, +0x3066 x2 lea)  callers(5): 0x21733 0x54d92 0x54dba 0x55ea3 0x57089
  fn 0x57020 (mirrors remover; STORE dec +0x4226)  callers(3): 0x54a1c 0x54ebe 0x55eb4
  fn 0x57194 register (t336) callers(9): 0x5534a 0x55397 0x57c9c 0x58197 0x58435 0x587ea 0x58c5e 0x58df2 0x59081
  fn 0x57284 remover callers(2): 0x55430 0x5545e
  fn 0x575e4 (3 stride multiplies at 0x57cbb/0x58809/0x58e11 — parser sites t336 missed: THREE state-ish loops, not one)
  fn 0x5addc (1 stride)  callers: 0x5a64b 0x5a6c6
=> t336's "who reads it is unknown" is now FALSE: 11 reader functions, and the
   readers are the WINDOW ROUTING machinery (see S2), not just the remover.

## S2 — FUNCTION SEMANTICS (bodies dumped work/r337_fnbodies.txt,
## work/r337_fnb2.txt; VERBATIM operands)
KEY GEOMETRY CORRECTION: dword [winmgr+0x4226] is TWO u16s.
  u16 @ +0x4226 = state-group COUNT (t336 measured 18) — written ONLY by
    0x57194 (`inc WORD PTR [ecx+0x4226]`) and 0x57020 (`dec WORD`).
  u16 @ +0x4228 = CURRENT STATE ID. Evidence verbatim:
    0x56e20 `cmp di, WORD PTR [eax+0x4228]` (bail if new==current)
    0x56f66 `mov WORD PTR [esi+0x4228], di` (STORE new state)
  Every `mov eax/eax..[X+0x4226]; sar eax,0x10` site (17 of them) is therefore a
  read of the CURRENT STATE word, not of the count.
fn 0x56e10 = SET-STATE (screen switch), verbatim behaviour:
  bail if di==current(+0x4228); assert di in [0,0x20) (winmgr.cpp:0xa90);
  if current-state slot [winmgr+0x3064+0x8e*cur] != -1 -> call 0x4f3fc(0x78638);
  same test on NEW state -> call 0x4f2cc(0x4f2cc body at 0x56ea5);
  if [winmgr+0x30f0+0x8e*cur] != 0 -> call it(ecx=slot base, edx=winmgr+0x3066+
  0x8e*cur, eax=cur) = PER-STATE LEAVE CALLBACK;
  post msg 6 to focused handle [winmgr+0x3002] via 0x56ca4; broadcast msg
  (edx=2,ebx=0) to state via 0x56b5c; push old state into a 16-deep HISTORY RING
  at winmgr+0x4736 (u16 x16) with counter +0x4756 / index +0x4758;
  store [winmgr+0x4228]=di; if count==0 and ds:0x89614==-1 and 0x78283(0x85ac4)
  ==0 -> call 0x53f50(0x85acf); call 0x5b68c([winmgr+0x3006]) and 0x551a8(703,
  639); if [winmgr+0x30ec+0x8e*new] != 0 -> call it = PER-STATE ENTER CALLBACK;
  broadcast msg (edx=1) via 0x56b5c; [winmgr+0x3002]=0xffffffff; tail-call
  0x56890 (hit-test).
fn 0x57020 = POP-STATE: reads [winmgr+0x4754] (enabled) and [winmgr+0x4756]
  (count), pops ring entry, decrements count, calls 0x56e10 with it (0x57089).
fn 0x56b5c = BROADCAST-TO-STATE: walks slots 0x1f..0 of
  [winmgr+0x306a+0x8e*state], resolves handle -> window [winmgr+0x4+12*h],
  re-entrancy guard BYTE [0xa2024 + state], calls window vtable [win+0xa7]+8.
fn 0x56ca4 = POST-TO-HANDLE: guard `sar eax,0x10` on [eax+0x4226], resolve
  handle [winmgr+0x4+12*h], `call [win+0xa7]+8`. (t331's msg-emit path.)
fn 0x56d8c = FIND-WINDOW-BY-NAME-IN-STATE: walks the state's slots, compares
  window name via 0x7892a(len 0xa) against edx, outputs handle to [ecx], returns
  window pointer.
fn 0x56890 = HIT-TEST / MOUSE ROUTER: reads mouse globals ds:0x484ec/ds:0x484f0,
  rect-containment on windows + their item arrays [win+0x67]/count [win+0x69] +
  item rects (+0x4..+0x10), posts msgs 8/6/7 via 0x56ca4, updates focused handle
  [winmgr+0x3002]; on the no-focus fallthrough 0x569d9 it walks the CURRENT
  STATE's slot list looking for a window with [+0xa3]==-1 containing the point,
  then posts msg 7 and sets focus (0x56aa4..0x56ac2).
=> THE STATE TABLE IS THE LIVE SCREEN-ROUTING TABLE: it decides which windows
   receive msgs 1/2/6/6/7/8 and which get the per-state ENTER/LEAVE callbacks,
   keyed by the CURRENT STATE word winmgr+0x4228. The "global active-screen-state
   datum" t333 declared nonexistent DOES EXIST in-image: u16 winmgr+0x4228 with
   writer 0x56f66 inside fn 0x56e10.

## S3 — SET-STATE CALLERS AND THE PUMP (arg-trace + caller walk, verbatim)
+0x4228 WRITERS ARE EXACTLY THREE (whole-image displacement census):
  0x56f66 `mov WORD PTR [esi+0x4228],di`   (fn 0x56e10 SET-STATE)
  0x570c2 `mov WORD PTR [ecx+0x4228],0xffff` (fn 0x57094 CLEAR-STATE-GROUP:
        zeroes group +0x3066/+0x3068, frees handles via 0x574a4 per slot,
        `dec WORD [ecx+0x4226]`)
  (reads: 0x56e20 bail-if-same, 0x56f39 ring-push, 0x570b9 same-check)
fn 0x56e10 SET-STATE(core=eax, edx=NEW STATE, ebx, ecx) — 4 in-image callers +
the pop path:
  0x21733 in fn 0x20fd4 (INIT; sole caller 0x7b817 in program-entry trampoline
    0x7b7d7): edx=0 -> BOOT STATE = 0. Same fn 0x20fd4 calls 0x57464(core,edx=k)
    for k in {0,1,2,3,4,7,8,9,9,0xa,0xc,0xd,0xe,0xf,0x10,0x12,0x14} =
    per-state-group init (fn 0x57464 sets winmgr+0x30ec ENTER cb per t336).
  0x54d92 in fn 0x54d18 (input/hotkey dispatcher, keyed on WORD ds:0x484c4):
    branch 0x21..0x26 -> if current!=8: SET-STATE(edx=2, ebx=-1).
  0x54dba in fn 0x54d18: branch 0x27..0x2b -> if current!=8: SET-STATE(edx=4).
  0x55ea3 in fn 0x55df4 (RING-A resolver; jmp-table 0x55e86 code<=8, table
    RAM-relocated): case arm -> SET-STATE(edx = sx: ring-record u16 at
    [core+0x436e+code*10] shadow copy) = THE GENERAL RUNTIME STATE SWITCH:
    a ring-A record's param IS the new state id.
  0x57089 = fn 0x57020 POP-STATE (pops 16-deep history ring core+0x4736,
    callers 0x54a1c, 0x54ebe in fn 0x54650 pump, 0x55eb4 in RING-A resolver).
fn 0x54650 = the pump (banked law ships.md:1778: called ONLY from 0x217b3 in
  main-loop fn 0x20fd4 and 0x555f9) calls fn 0x54d18 at 0x54951 (gated mouse/
  input), calls 0x55df4 at 0x54b4a, broadcasts msg 3 via 0x56b5c at 0x54976,
  hit-tests via 0x56890 at 0x547f3. NOTE ships.md's "fn 0x54650 size 0x1734"
  (t309) vs my call-target boundary 0x6c8 — boundary method differs; the CALL
  SITES are what matter and both docs agree on them.
fn 0x56d8c (FIND-WINDOW-BY-NAME-IN-STATE) callers(10) = the window-lookup
  consumers: 0x24fdc 0x2670b 0x27565 0x276f3 0x27ebb 0x28f00 0x363bd 0x3643e
  0x36476 0x52742 (0x27401/0x27513 family = the debugflags.md batmode rows).
fn 0x56b5c BROADCAST callers include the pump (0x54976 msg3, 0x54b36 msg5),
  fn 0x56e10 (msg 1 = ENTER broadcast, msg 2 = LEAVE broadcast), 0x55f82,
  0x53fa3, 0x5531e, 0x5548c, 0x56f0f (msg 6-adjacent), 0x57003 (msg 1).

## S4 — THE CURRENT-STATE WORD AND WHAT THE READERS DO WITH IT
+0x4226 is TWO u16s (t336 read it as one word — correction): LOW = distinct-group
COUNT (0x57194 inc / 0x57020... verbatim 0x5711e dec), HIGH = CURRENT STATE ID.
Proof: 0x56e20 `cmp di,[eax+0x4228]` + 0x56f66 store + 0x56e4a/0x56f6d read
`[+0x4226]; sar 0x10` inside the same fn 0x56e10 whose edx arg IS the new state;
0x54d74 `cmp eax,0x8` on the sar'd value = "if current screen==8".
Broadcast fn 0x56b5c call sites (edx = STATE GROUP, verbatim immediates):
  0x53fa3 edx=0xd (fn 0x53f50)   0x54976 edx=0x3 (pump)
  0x54ac5 edx=0x4 ebx=ds:0x484ec 0x54b36 edx=0x5 ebx=ds:0x484ec (pump mouse)
  0x5531e edx=0xf / 0x5548c edx=0xe (fn 0x5526c)  0x55f82 edx=0xd (resolver)
  0x56f0f edx=2 / 0x57003 edx=1 (SET-STATE leave/enter broadcasts)
  => NO caller ever passes the current-state value; every broadcast names a
  FIXED group. Group 16 (the battle family) is NEVER a broadcast target.
fn 0x56890 HIT-TEST reads the CURRENT state word (0x569d9 fallthrough walks
  [winmgr+0x306a+0x8e*cur]) and fn 0x56d8c FIND-BY-NAME walks the CURRENT
  state's slots (0x56e20-keyed). THESE are the two live current-state consumers.
STATE-GROUP ENTER CALLBACK slots winmgr+0x30ec+0x8e*g (called by 0x56e10 at
  0x56ff0) are installed ONCE at boot by fn 0x20fd4 via 0x57464(core, group k,
  cb=ebx) for k in {0,1,2,3,4,7,8,9,0xa,0xc,0xd,0xe,0xf,0x10,0x12,0x14} —
  16 groups, NO group-16 callback. fn 0x57464 verbatim: [ecx+k*0x8e*2? no:
  eax=k*9*2 -> +0x30ec] `mov DWORD PTR [ecx+eax*2+0x30ec],ebx`.
  fn 0x57400 sets per-group word +0x30ea (skip if !=0xffff).
fn 0x574a4 = window-record free (refcount, vtable[0], zeroes [esi+h*12],
  `dec WORD [esi+0x3000]` = resident-window count — t316's "+0x3000" law home).

## S5 — MEASURED CURRENT-STATE WORD (scripts/r337_state_word.py exit 0)
537 saves (playcap/save + dbg-t332 + t299-leg + dbg-t331 dirs, 12/dir cap),
core base located by the t336 exact-membership fingerprint: B = 0x2bc3e4 in
537/537 (same base t336 found). u16 [B+0x4226] = 18 everywhere (group count).
CURRENT STATE u16 [B+0x4228] histogram: {0: 122, 1: 236, 16: 5, 17: 174}.
State-group residency: for every save, group[state] count>0 and every handle
resolves to a resident magic+NAME window: 537/537.
THE 5 STATE-16 SAVES (the game DOES enter the battle state at runtime):
  work/r1/t299-leg-20261105-112859/save/{43,44,44,45,46}.sav  (dir listing
  double-hits; distinct files 43,44,45 + dupes of 44/46 in the walk).
Cross-check in those same saves (raw record bytes at magic recs):
  BatControlWnd rec 0xfdbebc BYTE+0xb7=253 BYTE+0xb9=1 (state-16 saves AND the
  state-0/1/17 saves — identical); BatModeWnd rec 0xfdc924 +0xb7=0/+0xb9=0
  everywhere (consistent with t332's never-armed). NOTE the byte-read base
  question: t332's "BatControlWnd[+0xb7]=0" vs this 253 — different field base
  (accessor rec vs magic-record byte, OFF-BY-H family). The STATE word is
  base-unambiguous (dual fingerprint: t336 table + resident counts).

## S6 — WHO SWITCHES STATE (RING-A param law, verbatim call sites)
RING-A poster fn 0x56ad4(core, edx=CODE u16, ebx=PARAM u32, ecx) writes
{code@+0x422c+10i, param@+0x422e, ecx@+0x4232}, index WORD +0x44ac (assert
0x9aa at 32). Resolver fn 0x55df4 (ships.md banked) shadows 0x140B to +0x436c,
jmp-table on code<=8; ONE table arm (0x55e8e..0x55ea8) = SET-STATE with
edx = sx(record u16 param at +0x436e) — THE PARAM IS THE NEW STATE ID.
Static-param posters of code 1 (edx=1/ecx=1) with param 0x10 (=state 16):
  0x28ed8 (fn 0x28e70 <- 0x27332; t309 law: star-select, sets ds:0x43504 first)
  0x51ad1 (fn 0x51674 <- 0x51626/0x51b16; primes ds:0x43504 from 0x13bc5 family)
  0x5200f (fn 0x51b04 <- 0x57932; ds:0x43504 <- [esi+0x59])
  0x36b0b (fn 0x36a90 <- 0x36661; ds:0x43504 <- [ebx+0x13000])
Other static params seen: 0x8 (0x51f8d ship-design family), 0x11=17
(0x1b5f2/0x51fce rowjump->planet), 0xd/0xe/0xf via broadcast not ring.
=> ENTERING STATE 16 IS CLICK-DRIVEN VIA RING-A CODE-1 PARAM-16 RECORDS, and
the 5 measured state-16 saves prove those posters fire in real play.

## S7 — VERDICT (residue-(1) arming question)
(1) THE STATE TABLE'S READERS ARE THE SCREEN ROUTING MACHINERY: fn 0x56e10
SET-STATE / 0x57020 POP-STATE / 0x57094 clear-group read +0x4226/+0x4228;
fn 0x56b5c broadcast and fn 0x56ca4 post-to-handle resolve targets THROUGH the
table's per-group slot arrays; fn 0x56890 hit-test and fn 0x56d8c find-by-name
read the CURRENT STATE word. t333's "there is NO global active-screen-state
datum" is RETRACTED-BY-SUPERSESSION: the datum is u16 core+0x4228, sole writer
0x56f66 (fn 0x56e10), MEASURED 537 saves {0,1,16,17}.
(2) IS ANY READER BATTLE-MODE-1-REACHABLE: yes trivially (the router/hit-test
run in state 16 — 5 saves witness state 16 itself), but the ARMING edge (msg
0x51 -> BatModeWnd slot 61, t331 chain) is NOT gated on any state-table reader:
fn 0x156d4's posters fire on BatControlWnd msgs, and no broadcast site ever
targets group 16 (all 9 0x56b5c call sites name fixed groups {1,2,3,3,4,5,0xd,
0xe,0xf}). The reason t332's forced capture saw zero chain legs now has a
MEASURED candidate explanation: the capture's save axis sat in states
{0,1,17} — clicks never landed while core+0x4228==16, so state-16 hit-testing
of BatControlWnd never ran. Route forward = LIVE drive on a state-16 save
(t299-leg-20261105-112859 has one resident) with the debugger chain BPs, NOT
another static walk.
(3) KEYWORD->STORE MAP ADDENDUM (t336 S4 table): STATE ids -> global per-group
table core+0x3068/0x306a+0x8e*id (writer 0x57194) AND the runtime semantics of
that table are now pinned: per-group message routing + ENTER callback slot
+0x30ec (boot-wired by fn 0x20fd4 for 16 groups, NO group-16 callback) + LEAVE
callback +0x30f0 + group flag word +0x30ea (fn 0x57400).
