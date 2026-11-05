# t307 WIP — SELECTION-WRITER WITNESS: arm the surviving t296 STORE-CENSUS sites + live cosmos star-click

## S0. PRE-FLIGHT (this session)
- No new sitting: live-timeline.jsonl tail (16 rows, 11:00:28..11:02:48) ALL
  turn=1086 T=50 in_game=True — production unchanged since the t306 commit
  (3e5d98b 10:54:35). r1_t85g_sitting.py NOT run (assignment t307 stands).
- STATE.md NEXT ACTION t307 read verbatim; REFUTED-ROUTES t306 amendment
  binding: do NOT re-arm {0x1aef8, 0x1b070, 0x1b71f, 0x1ba39}; writer hunt =
  the non-batmode census members ONLY.
- LEG BYTES ALL PAYLOAD-VERIFIED this session vs work/ascend_payload.bin AND
  work/t91_code_disasm.txt (store signature is the point — every site is a
  `mov ds:0x435XX,eax` = a3 04/08 35 04 00):
    w43504_28ec2 file 0x28ec2 a3 04 35 04 00 OK (preceded 0x28eb2 je; ebx=0x10)
    w43504_28ef6 file 0x28ef6 a3 04 35 04 00 OK (eax=[eax] at 0x28eed; ebx=0xfd8->deref path)
    w43504_36b01 file 0x36b01 a3 04 35 04 00 OK (eax=[ebx+0x13000]; ring 0x10 call 0x56ad4)
    w43504_52003 file 0x52003 a3 04 35 04 00 OK (eax=[esi+0x59]; ring 0x10)
    w43504_55d35 file 0x55d35 a3 04 35 04 00 OK (cmp [esp+8],1 gate 0x55d25)
    w43508_51a8e file 0x51a8e a3 08 35 04 00 OK (ring 0x11; turn gate ds:0x484ec>0x96 upstream)
    w43508_51fc2 file 0x51fc2 a3 08 35 04 00 OK (eax=[edx+0x59]; ring 0x11)
    w43508_55bbd file 0x55bbd a3 08 35 04 00 OK (edi=0x11 leg into 0x55d6f)
  -> ALL 8 are genuine stores of 43504/43508; NONE skipped under the
  "log and skip" clause.
- VIEW LAW (t306 run session.log): the t299 census flow open_fleet()->rowjump
  lands the click windows in the SYSTEM view (star='Icarus'). A COSMOS
  star-click must be measured from the GALAXY MAP (campaign-load view;
  r293 enter_system asserts map-then-click, and t244/t245: modal/system views
  swallow NEXTTURN -> escape ladder between star window and control).
- t285 law stands: never Escape at the bare map (escape_to_map checks
  orange-frac + diff-vs-map-baseline BEFORE each press).
- NEXTTURN control: keep btn_hdlr armed (t306 hit the 'Cancel' record via
  0x56c74 — but 0x56c74 is NOT armed this run, so the pty census cannot see
  that residue; btn_hdlr fire is still the msg-layer liveness control).
  If the Cancel pattern repeats (banked win name 'Cancel'), the honest reading
  is baseline+star = the two measured windows, control inconclusive.

## S1. INSTRUMENT CHANGES (this iteration, committed with the landing)
- scripts/r299_leg_session.py LEGS += the 8 writer legs (names w43504_*/
  w43508_*; addresses = FILE offsets like every leg; linear = P0+off printed
  by the LEG banner at start: 0x1e8312/0x1e8346/0x1f5f51/0x211453/0x215185/
  0x210ede/0x211412/0x21500d). FirePat last-4 audit over the FULL 46-leg
  table: NONE collide (new sigs 028EC2 028EF6 036B01 052003 055D35 051A8E
  051FC2 055BBD). FirePat regression re-run THIS session before launch:
  033648 cos_hdlr 41 / 052925 s2_56cda 3 / 061825 60+20+1 — 5/5 PASS.
  NOTE: fire_pats needs P0+LEGS[leg] (linear), not the raw file offset —
  a raw-offset regression harness reads 0 everywhere (false FAIL, caught
  same session).
- --star-click N (census mode): after the 15 s baseline, ON THE GALAXY MAP
  (campaign-load view IS the map; open_fleet is SKIPPED in star mode so
  nothing drags the session off it), pick N bright pips (r293 enter_system
  candidate law verbatim: sum(r+g,b)>380, x 40..455 y 60..440, nearest
  MAP_CENTER(236,240) first, dedupe >20px), run census_click per pip (arm ->
  close_eventwin -> click -> bank window -> disarm+liveness), classify
  screen-diff vs map baseline (>15000 = entered system view), escape_to_map
  ladder after every ENTERED click (t285 orange-checked). Oracle pairs
  star{i}_before/after around every pip click.
- sel_oracle MOVED above the baseline (shared by star + system phases); the
  t306 duplicate definition and its `oracles = {}` reset DELETED (the reset
  would have wiped the star pairs).
- rc law extended: in --star-click mode a bank-window that RAN with zero
  stops counts as measured (zero-fires-at-all-8 is the assigned datum);
  non-star mode keeps t303 semantics exactly.
- scripts/r307_relaunch.sh: --census --legs <8 writers + btn_hdlr>
  --star-click 3 --target-kinds none --window 60 --disp 97 --port 55999
  --tl 7200, attempts 1 2 2 (same BREAK-lottery absorption as r305/r306).
- DRY RUN 11:27:55 (run dir t299-leg-20261105-112755, killed at settling):
  all 9 LEG banners print store signature a3 04/08 35 04 00 verbatim; no
  stray dosbox-x-dbg/Xvfb after kill; production :9 verified t=1086.

## S2. RUN
- Loop launched 11:31 via scripts/r307_relaunch.sh (console
  work/r1/t307-loop.out). (pending results)
## S3. RUN t299-leg-20261105-112859 (attempt 1, rc=0, census-measured=
### ['star0','star1','star2','control_nextturn']) — ONE FIRE AT A WRITER:
### w43504_28ec2, EAX = 0x256825 (THE STAR POINTER). THE WRITER IS NAMED.
Instrument healthy: ring base B=0x1bf4d8, 9 BPs armed att=0 every cycle,
disarm liveness True every window, teardown SIGKILL pid 66617, production :9
untouched. FirePat regression 5/5 PASS same session pre-arm.

PTY WHOLE-LOG CENSUS (9 armed legs):
  {w43504_28ec2: 1, w43504_28ef6: 0, w43504_36b01: 0, w43504_52003: 0,
   w43504_55d35: 0, w43508_51a8e: 0, w43508_51fc2: 0, w43508_55bbd: 0,
   btn_hdlr: 5}
STAR WINDOWS (map view, r293 candidate law, nearest-first):
  star0 (226,238) diff=488 entered=False stops=1 (btn_hdlr NEXTTURNCONT msg 4)
  star1 (238,282) diff=94504 entered=True  stops=1 (btn_hdlr NEXTTURNCONT)
  star2 (218,308) diff=? entered=False stops=1 (btn_hdlr NEXTTURNCONT)
  control_nextturn: btn_hdlr msg 0x7 (NEXTTURN, esi=0x247cb8 class table) —
  CLEAN control this run (no 'Cancel' residue: 0x56c74 not armed).
ORACLES: DAT_43504 = 0x256825 CONSTANT across every before/after pair (it is
the idle Icarus-star value per t297-A — a SAME-VALUE store is invisible to
the oracle; see S4). DAT_43508 = 0x26fe77 constant this run (t297 churn did
not reproduce in these windows).

THE FIRE (mcp-pty.log byte ~34151, raw ANSI decoded verbatim):
  HL stop render: "E8312 A304552800 mov [00285504],eax" then
  "E8317 B85CC32B00 mov eax,002BC35C", "E831C 89CA mov edx,ecx",
  "E831E C786BB0... mov dword [esi+000000BB],0",
  "E8328 E8F7DB0200 call 00215F24", "E832D 5D pop ebp"
  Register panel: EAX=0256825, ESI=2BC35C, CS=0160, IP=E8312.
  => STORED VALUE EAX=0x256825 = THE Icarus STAR RECORD POINTER (T298-A:
  member 0x256825+0x88+0x1c reads "Icarus"). Follow-on sequence matches
  disasm 0x28ec7..0x28ed8 verbatim (mov eax,0x7a35c; mov edx,ecx;
  [esi+0xbb]:=0; call 0x56ad4) = RING POST CODE 0x10 (ebx=0x10 set at
  0x28ebd). The following instruction bytes pop ebp/edi/esi/ecx/ret = the
  0x28edd..0x28ee1 tail EXACTLY. ENCLOSING FUNCTION (static, disasm
  23071-23130): entry 0x28e70 `push ecx; push esi; push edi; push ebp;
  mov esi,eax; mov eax,[eax+0xbb]` — eax arg = a WINDOW RECORD; gate chain:
  cmp BYTE [[win+0xbb]+0x4],0 (clip kind byte must be 0) -> jne 0x28fb9;
  cmp [esi+0x582],0 (clip list EMPTY — only when NO clips exist);
  GATE: (ds:0x7e582>>0x10)==1 -> 0x28ea1: eax=[[win+0xbb]] (the clip's
  OBJECT = star record), bl=[eax+0x17], test bl, dl=BYTE ds:0x6774,
  je skip -> STORE ds:0x43504=eax + ring 0x10. Sibling at (>>0x10)==0xd ->
  0x28ef6 store + call 0x56d8c + call 0x36cac + [esi+0xa7] call [ebx+0xc].

## S4. TWO INSTRUMENT/STATIC CORRECTIONS FROM THE FIRE (BINDING)
1. SELF-RELOCATION LAW (MEASURED, MEMDUMPBIN ctl file MEM_CTL_CENSUS_
   001E8312.BIN): guest RAM bytes at P0+0x28ec2 = a3 04 55 28 00 (imm
   0x285504) vs payload-file a3 04 35 04 00 (imm 0x43504); delta 0x242000
   (= obj1 data base; second imm 0x7a35c -> 0x2bc35c same delta). The game
   REBASES data-segment immediates IN CODE at load time. Consequences:
   (a) the census-ctl byte compare vs PAYLOAD reads False at rebase-carrying
   legs while BPLIST proves the arm — NOT an arming failure (t306's legs
   carried no rebased imms, which is why it read MATCH);
   (b) the debugger decodes [00285504] = DS(5404)+0x43504 = the SAME DAT
   scalar (panel DS=5404 verbatim) — attribution holds, FirePat matches on
   the address token so detection is unaffected;
   (c) t91_code_disasm immediates are PRE-REBASE — add 0x242000 to read
   runtime DAT addresses in code (and runtime linear = P0 + file_off where
   P0 is the CODE base; data DAT at B+0x82bb0+X as always).
2. THE ORACLE CANNOT SEE A SAME-VALUE STORE (43504 was already 0x256825
   while idle). Witnessing requires the debugger leg, not RAM deltas —
   consistent with t305's conclusion that msg-layer/RAM readings alone left
   the writer unnamed.

## S5. READING (banked; ledger interaction in S6)
THE DAT_00043504 STORE CENSUS MEMBER 0x28ec2 IS A LIVE, CLICK-TRIGGERED
WRITER: the cosmos-window fallback star-select publisher (function 0x28e70,
Sole caller 0x27332 in the COSMOS msg chain), storing the clicked clip's
star-record pointer + posting ring code 0x10. The t296 "SELECTED OBJECT"
semantics is CONFIRMED live for the star case. The t306 conclusion "map
clicks never dispatch into any selection layer" is REFINED: BatModeWnd was
never reached (t306 datum stands), but the COSMOS family selection writer DID
fire on the entered star click.

FIRE ATTRIBUTION (REQ correlation, mcp-pty.log): HL render at byte 34151 sits
between 'REQ 111 EXEC RUN' (resume after the star1 btn_hdlr msg-4 stop) and
'REQ 112 BREAK' = inside the star1 armed window, seconds after the click at
(238,282) which ENTERED the system view (screen diff 94504; vision-verified
'Icarus / Red Dwarf' system panel in 14_star1_screen.png). The fire was NOT
banked by bank_stop (it landed during resume_and_rearm's liveness peek) — the
pty whole-log census is what caught it (count 1). Panel verbatim:
EAX=0256825, CS=0160, IP=E8312 (= P0 0x1bf450 + 0x28ec2).
GATE CHAIN (static, all verbatim t91_code_disasm 23071-23130): entry 0x28e70
eax=window record; [[win+0xbb]+4]==0 (clip kind 0); [win+0x582]==0 (clip list
EMPTY — the fallback branch); (ds:0x7e582>>16)==1 (MEASURED =1 in the run's
sav @DB+0x7e582 u16); dl=BYTE ds:0x6774 (viewer mask, DB+0x6774 read 0x01);
bl=[clip_obj+0x17]; test bl,dl must pass (post-hoc sav byte mem[0x256825+0x17]
==0x00 — the flag is transient/transitional around entry; the FIRE is the
evidence, not the byte); then STORE + ecx=1, ebx=0x10, [esi+0xbb]:=0,
call 0x56ad4 (ring post code 0x10). Follow-on bytes in the render
(B85CC32B00 / 89CA / C786BB0..0 / E8F7DB0200 call 00215F24 / 5D pop) match
0x28ec7..0x28edd EXACTLY including the rebase of 0x7a35c -> 2BC35C.

## S6. LEDGER (see OPEN-QUESTIONS t307 note)
CLOSE CONDITION (task-assigned) = banked stop with win/reg evidence AND an
ORACLE DELTA. First half MET (regs name the stored value: EAX=0x256825 = the
Icarus star record; win context = COSMOS msg chain, entered-system click).
ORACLE DELTA NOT MET: DAT_43504 read 0x256825 before AND after (same-value
store — invisible to RAM deltas, S4-2). The OQ-019 RESIDUE (per-SHIP
selection + destination widget) is untouched by this fire (star clip, kind 0,
fallback branch; no kind-2 ship exists at t=1086). ROW STAYS OPEN
(strict-close). What moved: the census is now LIVE-VALIDATED — the leg
instrument CAN and DOES catch these writers, so the remaining zeros
(w43508_51a8e/51fc2/55bbd, w43504_28ef6/36b01/52003/55d35) are CONTEXT
statements, not instrument statements. Ring codes 0x10/0x11 were POSTED
(0x28ec2 witness) but the ring CONSUMER family (0x55a60 incl. 0x55bbd/55d35)
never ran inside any armed window — the turn never advanced during the run
(last sav t=1086).
