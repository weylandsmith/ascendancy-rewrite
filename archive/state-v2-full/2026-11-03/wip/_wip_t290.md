# _wip_t290 — THE END-CTRL COMPARATOR IS READ VERBATIM: V >= floor(2T/3)+1, T=DAT_16143, sel/rank written at 0x24d9f/0x24dab

Session 2026-11-03. Task: t290 poke-past-threshold experiment. The live poke
session is S5 (running); S1-S4 are the STATIC result that superseded part of
the assignment's premise (the comparator no longer needs to be inferred from a
poked V — it is READ, and it says two-thirds, not half).

## S1. THE COMPARATOR (file 0x24b9c..0x24bbe, inside evaluator FUN_00024a34)

Disasm (capstone via /home/hrethric/tools/revenv/bin/python, tool
scripts/r290_disasm.py — NEW KEEPER: file-offset windowed disassembler,
designed around the t283 objdump `-b binary --start-address` dead-output trap):

    0024b9c  mov edx, dword ptr [esi + 0x3333]   ; T<<16 (u32 at state+0x3333)
    0024ba2  sar edx, 0x10                        ; T = hi16  == DAT_00016143>>16
    0024ba5  add edx, edx                         ; 2T
    0024ba7  mov ebx, 3
    0024bae  sar edx, 0x1f                        ; sign ext (idiv pair)
    0024bb1  idiv ebx                             ; eax = floor(2T/3)
    0024bb3  mov edi, dword ptr [esi + 0x354eb]   ; V = DAT_000482fb (t283/t284 law)
    0024bb9  inc eax                              ; floor(2T/3)+1
    0024bba  cmp eax, edi
    0024bbc  jg  0x24bc3                          ; skip iff floor(2T/3)+1 > V
    0024bbe  mov byte ptr [esp+0x10], 5           ; *** CONTROL VICTORY ***

LAW: Control victory iff V >= floor(2T/3)+1  <=>  V > 2T/3 (integer).
T=50 (the ONLY T in the whole corpus, score.md S14) -> threshold V >= 34.
The corpus max V=23 = 46% was NEVER one step away from arming — it was 11
steps away. The t85c..t289 "boundary is 4 units away" framing (based on >1/2)
was WRONG. The OQ-021 text dispute resolves: the CODE implements the prose
("two-thirds"); the file-header comment "over half" (end-ctrl.txt line 2) is
decoration — end-ctrl.txt enddesc says "spans over two-thirds of the galaxy"
and congrat says "more than two-thirds of the stars", matching the code.

Address identities (pointer/state law, all arithmetic exact):
  state base = DAT_00012e10 (the turn counter's game-state object, t284);
  state+0x354eb = 0x482fb = V (t283 witnessed store operand, same base);
  state+0x3333  = 0x16143 = T (score.md S3 presenter source — SAME field);
  state+0x30700 = 0x43510 = presenter selector byte (r1_slot.py:93);
  state+0x306fc = 0x4350c = presenter rank u16    (r1_slot.py:94).
The evaluator writes EXACTLY the presenter's two fields, 12 bytes apart
(`mov byte [esi+0x30700], al` @0x24d9f; `mov dword [esi+0x306fc], eax`
@0x24dab), then fires event 0x56ad4 arg 0x7a35c (game object, t206 law) @0x24dbf.

WHY t212's census missed it (the predicted shape, positively witnessed): the
comparator reads V via base+disp32 `[esi+0x354eb]` — no static disp32==0x482fb
encoding exists; t212's disp32+imm pass over 0x482fb could not see it. The
t284 state-object resolution is what unlocked it (same unlock as the t283
writer). t212's "runtime-computed-address class" claim stands for the WRITER
(it is the same store t283 witnessed) — the COMPARATOR was simply never in the
search window because nobody had the state base.

## S2. CALLER + GATE LAW (the evaluator runs EVERY end-turn pass)

Evaluator = FUN_00024a34 (prologue 53 51 52 56 57 55 83ec14 @0x24a34), register
arg eax = state ptr. E8 census: EXACTLY ONE caller, 0x252e9, inside the
end-turn pass right after the V producer (t284 protocol):

    00252aa  mov dword ptr [ebp+0x354eb], 1   ; seed V=1 (home-bit branch)
    00252bc  call 0x24274                     ; the t284 flood
    00252c3  mov dword ptr [ebp+0x354eb], 0   ; seed V=0 (else branch)
    00252cd  mov esi,[ebp]; inc esi; mov [ebp],esi     ; TURN++ (DAT_12e10)
    00252d1  mov ch, byte [ebp+0x30700]       ; selector
    00252da  test ch,ch; jne 0x252ee          ; GAME-OVER LATCH: sel!=0 -> never re-evaluated
    00252de  cmp dword [0x10ba4], 0
    00252e5  jne 0x252ee                      ; gate global
    00252e9  call 0x24a34                     ; *** THE COMPARATOR PASS ***

MEASURED on banked banks (this session): [0x10ba4] == 0 in bank-t261-final-1150
AND bank-t273-tutorial645 -> the gate is OPEN in captured play; the evaluator
ran every turn of every captured game and simply never found a winner.
The sel!=0 latch explains why no bank shows sel != 0 except the tutorial
(a game that ended keeps its sel forever, evaluations skipped).

## S3. RESULT-CODE MAP + PRESENTER IDENTITY (closes the t273 selector-mapping residue)

Presenter 0x2c01d `mov al,[0x43510]` -> `cmp al,5; ja default; jmp [eax*4+tbl]`.
t273 could not locate the jmp table; RESOLVED: the cs-relative operand is
disp32 at file 0x2c035 (`2e ff 24 85 e0 b3 1e 00` witnessed live in
bank-t261-final-1150: relocated imm = P0+0x173e0, linear 0x1eb3e0), and the
table CONTENT is relocated code addresses — content-scan found it at member
0x1eb468 (linear 0x1eb3e0), entries EXACTLY:
    sel 0 -> file 0x2c03a (default: assert 0x34e/0x12fc eventwnd.cpp = no-ending bug)
    sel 1 -> 0x2c04d push 0x130c = "end-xtnc.txt"
    sel 2 -> 0x2c064 push 0x1319 = "end-dest.txt"
    sel 3 -> 0x2c07b push 0x2c07b push 0x1326 = "end-capt.txt"
    sel 4 -> 0x2c092 push 0x1333 = "end-unit.txt"
    sel 5 -> 0x2c0a9 push 0x1340 = "end-ctrl.txt"   <-- CONTROL VICTORY PRESENTER
Each arm loads the ending file and calls 0x76c79; 0x2c0c7 then 0x206c0 and on
failure "Couldn't open %s" (0x134d). String pool offsets verified readable in
the payload at obj1 pool (0x82bb0+imm) this session.

Evaluator result-byte ladder (file offsets; semantics graded honestly):
  result=1 @0x24a66  iff dword[state+6+0x1ee*race+3] == -1        [class: xtnc?]
  result=2 @0x24a78  iff for ALL other races dword[race+9] != 0   [class UNVERIFIED]
  result=3 @0x24ab7  iff for ALL other races byte[[race+0xd]+0x14]&0x7f != (1<<me)
  result=4 @0x24b05  (survives a race-bitmask + planet-bit loop over [esi+0xdcc])
  result=5 @0x24bbe  iff V >= floor(2T/3)+1   (the S1 comparator; runs ONLY when
                     results 1-4 all cleared, i.e. nobody eliminated yet)
Flow law: result != 0 -> ladder @0x24c35 -> sel/rank/event written; result==0
after the V check -> return 0x24dc4 WITHOUT touching sel (why healthy games
read sel=0 — the field is written ONLY at game end).
The rank ladder @0x24c35..0x24dbf: accumulate [esp+8] (per-race +0xf ALLIANCE /
-0xa WAR @0x24c87..0x24cc8, +50 if result==4 @0x24cd1, call 0x40ec0, +own-planet
count over [esi+0x3333] via byte[eax+0xdcc]&(1<<race)), scaled by a clamp
100-share of a /0xfa0 quotient (clamped 25..100 @0x24cfd..0x24d13), difficulty
byte [esi+0xdb4] float-multiplier table 0xcec/0xce4 (@0x24d26..0x24d5b), floored
at 0, then /600 -> rank INDEX @0x24d8d..0x24d92. RANK semantics [unverified]
beyond the arithmetic (the 10 rank names live in end-*.txt 'ranks' blocks).
The tutorial witness (sel=2, rank=1, V=0 — t273) reads consistently with
result=2 firing in a 3-power game; exact check-2 semantics stay a residue.

## S4. CONSEQUENCES (honest)

- OQ-021's named dispute (comment "over half" vs prose "two-thirds") is
  ANSWERED BY CITED CODE: two-thirds, strictly greater (V>=floor(2T/3)+1).
  Operands are V=DAT_482fb and T=DAT_16143 — the SAME pair the disproducer
  prints (score.md S3), so the 'c' overlay percent IS the comparator's input
  ratio (t85g's "prints the comparator's own formula output" now confirmed
  structurally).
- The rewrite default >1/2 (campaign.cpp:2093) is WRONG and upgradeable to the
  cited law. (Code change + pin = this session or the next, per scope.)
- The vendor's natural victory-screen appearance (the row's last residue under
  the old framing) is now: presenter = end-ctrl.txt arm @0x2c0a9, gated by
  sel==5 written ONLY by 0x24d9f. A live poked-V witness (S5) would additionally
  demonstrate the whole chain end-to-end.
- RESIDUES banked: result 1-4 class semantics (elimination ladder) not fully
  decoded; rank name mapping unverified; [0x10ba4] identity (what sets it —
  presumably a scenario/debug flag; 0 in all captured play); check-2/check-4
  field semantics (race+9, state+0xdcc bitmask).

## S5. LIVE SESSION — THE THRESHOLD-FREEZE INSTRUMENT (scripts/r290_poke_session.py)

Design (supersedes the assignment's V:=25 arms — 25 is NOT the threshold; the
static law says 34, strict boundary 33):
  scratch game-wp + OWN ring + Xvfb :96 + dosbox-x-dbg, RESUME.GAM = Oct-29
  t1086 point (V=0 at load per t255; first End Turn recomputes); BREAK at
  title (t286 lottery -> scripts/r290_relaunch.sh loops until 'armed:');
  sentinel BPLM on V linear 0x28A2FB (= B-0x88+0x82bb0+0x482fb at
  expect-base 0x1bf4d8, t283's own target; survives campaign load, t286
  law 1); enter campaign; press END TURN (511,67); FIRST FIRE = a producer
  store mid-flood -> CPU stopped INSIDE the pass, BEFORE the evaluator
  (caller order 0x252bc flood -> 0x252e9 evaluator).

DESIGN CORRECTION made during build (why FREEZE, not plain poke): the flood
re-reads and re-stores V per admit, so a poked value only sticks UPWARD and a
mid-flood poke of 34 could be partially overwritten by the seed/loop order.
The debugger's FM breakpoint (BKPNT_MEMORY_FREEZE, debug.cpp:2875; check loop
:870-874 writes the frozen byte back on EVERY instruction-loop-top heavy check,
core_normal.cpp:182) OVERRULES the flood deterministically: freeze at the stop
(BPDEL * ; SMV V:=N ; FM <live ds>:28A2FB — FM resolves via GetAddress, and at
flat-model bases seg 0000 == linear, same witness class as BPLM fire lines) ->
RUN -> the evaluator's read at 0x24bb3 sees exactly N. One-byte granularity is
enough: V values 0..50 fit the low byte (upper bytes always 0).
  PRIMARY ARM: freeze N=34 -> expect sel=5 + rank + end event (latch law S2).
  BOUNDARY CONTROL: freeze N=33 -> expect sel STAYS 0 (pins strict >2T/3 live).
Evidence: ring rows (r1_slot readout) + screenshots (victory presenter screen
text = end-ctrl.txt enddesc "Congratulations! Your massive empire spans over
two-thirds of the galaxy"). READ-PRIMITIVE NOTES banked: MEMREAD is
real-mode-only (debug.cpp:2983 'supports real mode only'); MEMDUMPBIN-with-
filename over EXEC stays dead (t283) — verification rides on ring + BPLIST.
Safety: production :9 untouched (HEALTHY at session start, pid 660167, t1150
V23); scratch asserted; kill-by-recorded-PID finally; TL 1500; no Escape ever.

## S6. LIVE RESULT (honest) — INSTRUMENT REACHED THE FIRE WINDOW; EMULATOR DIED AT THE DECISIVE RUN

Loop scripts/r290_relaunch.sh freeze 34, 5 attempts. Attempt 2
(work/r1/t290-freeze-a34-20261103-155038) got furthest and is the witness:
- BREAK lottery ~1/5 this session (attempts 1,3,3-lost... died at BREAK with
  channel EPIPE — consistent with t286 law 2, no regression).
- ARMED attempt: sentinel BPLM 0028A2FB armed at title (BPLIST confirmed),
  campaign entered, End Turn pressed, MID-PASS STOP caught at the producer
  store, EV ds = 0168 read, `SMV 28A2FB d:34` + `FM 0168:0028A2FB` ANSWERED
  'Set memory freeze ... with value: 34' — the freeze operand resolved and
  armed (first live use of FM on this build).
- DECISIVE RUN: channel dead (EPIPE) seconds later; ring froze at t1086/V=0
  (10 slots, none armed; no t1087 row ever written, no victory screen).
  VERDICT: the post-FM RUN killed the emulator (mechanism NOT proven —
  candidates: freeze writeback storm vs dyn-core interaction, or the same
  BREAK-family instability; do not cite a cause). NO live arming witnessed;
  the static S1 law stands uncontradicted (nothing completed a pass to
  disagree), and the row's live-witness residue SURVIVES (S5 arms for a
  future session: poke mode N>=threshold avoids the freeze path entirely;
  consider core=dyn default conf or --no-break-free variant).

NEW PITFALLS BANKED (this session, cheap to avoid next time):
1. tools/xsend arg1 is the WINDOW TITLE ("DOSBox-X"), DISPLAY via env
   (r1_wp_session.py:147 law) — passing ':96' as arg1 parses as a title,
   every click rc=1 NO-OPS SILENTLY (first-loop burn, caught by watching rc).
2. objdump `-b binary --start-address` prints NOTHING (t283 trap re-hit once);
   KEEPER tool scripts/r290_disasm.py wraps the working dd/-d form and a
   --pat census mode.
3. MEMREAD over MCP is real-mode-only (debug.cpp:2983 refuse 'supports real
   mode only') — pmode value reads must ride fire lines / BPLIST baselines /
   the ring.
