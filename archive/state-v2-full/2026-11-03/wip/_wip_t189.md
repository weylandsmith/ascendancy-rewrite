# WIP t189 — static hunt for the lane-step word (OQ-019 residue)

Intake (this session):
- Pre-checks all negative as STATE predicted: tail 4MB has 0 rows turn>1335
  (new-game ring), sel never armed, DAT_482fb=2[5-9] count 0, dosbox down.
- Adopted+committed prior-session residue 87dcab9 (game.pal 6-bit fix —
  independently re-measured: max byte 0x3f, 0/256 entries any ch>0x3f;
  plus r1_t187_session.py, r1_t188_state3_arbiter.py, gitignore
  tools/shp_pngdump binary).
- Ghidra bridge ALIVE: tcp 127.0.0.1:8089, current program
  ascend_restored.bin (list_instances verified).

P1 [verified disasm 0x4a74c..0x4a968, decompile agree]: FUN_0004a74c IS
THE STATE-5 LANE MARCH BODY. Structure:
  - prologue: [ship+0x9c]=0; [ship+0x88] := FUN_0004a99c() (REFILLS POW
    each call — S21's "POW frozen" was first-row-per-turn aliasing: POW
    burns mid-call then refills to same value at end); slot-refresh loop
    ([+0xab+i*7] cidx -> design word 0x7654e+cidx*0x6a into slot+1).
  - guard CMP byte [ESI+0x58],5 @0x4a7a6 (JNZ skips to tail).
  - LANE VECTOR: H = dword[ship+0x59]; A = ptr[H+0], Bk = ptr[H+4];
    vec = (A[+8]-Bk[+8], A[+c]-Bk[+c], A[+10]-Bk[+10]) f32 (0x4a7cd..
    0x4a7e9); len = FUN_00076da0(dot) (0x4a81f) — SAME star-rec f32
    layout as walk law/magnetron (+8/+c/+10).
  - BASE STEP: local_20 = float(int32[ship+0x8] + int32[ship+0xc])
    (0x4a824..0x4a83a FILD) — NOT MOVES+0x94, NOT POW+0x88.
  - MULTIPLIER 1: if byte[handle+0x23] & 1 (0x4a837 TEST BL,0x1):
    step *= float moffs [0x263b] (FMUL moffs 0x4a84b).
  - MULTIPLIER 2 (species): idx = (ship+0x54 dword)>>16; if species-table
    row idx (stride 0x1ee, base DAT_00012fb3) col == 0x12 (0x4a867):
    step = max(step,1.0); step *= float moffs [0x263f] (0x4a888).
  - ADVANCE+CLAMP (0x4a892..0x4a8af): x += step; if x > len: x := len.
  - LANE-END ARRIVAL (0x4a8b5..0x4a954): if x == len: endpoint = ptr[H]
    if [ship+0xa2]==0 else ptr[H+4]; if ship-owner-race(DAT_0007458e)==
    that-star race -> FUN_00045e48; elif star byte +0x14|+0x15 owns-bit
    -> FUN_00046144; then ALWAYS FUN_00021f58 (the kind-5 PLACEMENT
    handler — sets state 4); assert state==4 else ship.cpp:0xfc.
  - tail: FUN_0004a658 (the MOVES-refill routine from T4 sweep) @0x4a95b.
  => S21 residue ANSWERED STRUCTURALLY: step = (ship+8 + ship+0xc) [x
     handle+0x23-bit0 const] [x 1/3 if species-row==0x12]; lane-local
     frame == distance along (endA-endB) chord; the 14/3 case must be one
     of the two multipliers. UNVERIFIED: live values of moffs 0x263b/
     0x263f, what ship+0x8/+0xc mean (design vs runtime), species table
     identity, row==0x12 semantics.

Probe log:
P2 (running): corpus check step == ship[+8]+ship[+0xc] for st5 rows;
   ratio 13 vs 17; read +0x54/+0x59.
P3 (pending): moffs 0x263b/0x263f live values from a playcap save.
P4 (pending): callers of FUN_0004a74c (dispatch site).

P5 [MEASURED 58-60.sav]: relocated operands decoded from the st5-copy:
  M1 moffs VA 0x24463b (payload_off 0x85163) LIVE 0.0; M2 VA 0x24463f
  (0x85167) LIVE 0.0 in all three (these are NEW-GAME saves saved after
  the ring rotated — the old campaign values are gone; runtime-init words
  per t43). Species tbl relocated VA 0x254fb3 (DAT_00012fb3+0x42000):
  stride-0x1ee rows, col 0x12 ALL ZERO rows 0..23 in these saves.
P6 [MEASURED corpus, r1_t189_lawcheck.py RC=0]: base law
  step0 = float(ship[+8] + ship[+0xc]) holds for EVERY st5 slot: values
  (14,0) or (0,28) — S21's 14/28 ARE THESE WORDS. Consecutive-turn deltas
  are step0 (tag BASE-LAW-EXACT, species 0/2 slots) or step0/3
  (ratio 0.333333-4, species-1 slots 13/17/20/29 AND occasional
  species-0 phases: slot16 t1250 4.6667 h=0x2589cf-ish, slot30 t1301
  x reset to 18.6667 under h=0x2589cf, slot34 t1250-51 slow under
  h=0x2589f6 then FAST after handle changed to 0x25831b). Handle values
  are LINEAR POINTERS in the 0x258000..0x258FFF data-seg window (seg
  relocated +0x42000 => payload_off window 0x2160000.. check) — handle
  byte +0x23 (bit0 => *M1) is a LANE-RECORD flag: lane-scoped 1/3 vs
  species-scoped 1/3 NOT yet fully separated (owner-1 always slow,
  species-1 slots sometimes FAST at 14.0 — slot13 t1252+ steps 14).
  KEY CORPUS FACT: identical words, ratio exactly 1/3 (x48) => a runtime
  const 1/3 (M2) exists during the old campaign; saves can't show it.
