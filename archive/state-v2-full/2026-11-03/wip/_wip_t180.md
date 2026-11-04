# t180 WIP — OQ-023 STATE-3 WRITER SCAN (static)

Assignment source: docs/STATE.md NEXT ACTION (t180). Idle-gate Trigger B was
prompt-churn churn only: no LOOPSTEER.txt, no FORCE_RUN, no new capture
(playcap-20261014-224611 still newest, live-timeline.jsonl unchanged at
5691796463 bytes), empty tracked tree. So this session runs t180 as written.

## Question (ledger OQ-023 residual)
Which relation-state values can the ORIGINAL engine actually store into the
session-matrix state cell, and specifically: does ANY code path write 3?
Banked working adjudication (diplomacy.md §11/§12): 2 = AT WAR (measured from
a real player war-declaration, reciprocal, sustained 244 turns), 1 = peacetime
/ no active relationship (pre-war EVERY pair sat at 1), 0 = default/self.
3 has NEVER been observed in 28,843 trusted rows. §7 pairs state 3 with
DA_OfferPeace/DA_BreakAlliance in the chooser rows — so the enum question is
whether 3 is (a) a live engine state nobody reached, (b) a chooser-template
artefact, or (c) written by code outside the matrix cell.

## Method constraints (binding)
- R12: no u32 scans of string addresses / get_xrefs_to on these DATs. The
  route t85g named is an ENCODING census of memory-WRITING opcodes with the
  state-cell displacement, on work/ascend_restored.bin (t60 file-provenance
  law), boundary-verified per t106/t108 (instruction must START at the site;
  objdump long-instruction wrap merged).
- Displacement law (diplomacy.md §7/§10): row stride 0x1ee; attitude i16 at
  row+0x1b2+2t; state byte at row+0x1c0+t. Chooser gate at 0x447ba reads
  BYTE PTR [ebp+0x1c0] — so 0x1c0 appears as an ebp-relative disp.
- A plausible default never closes a row. If zero imm-3 writers exist, the
  honest output is a scoped negative: "no encoding of store-imm-3 to disp
  0x1c0 exists in code object 0 within coverage X", which BOUNDS the enum but
  does not close OQ-023 (capture-gated residual stands).

## P0 FINDING (objdump window 0x447a0..0x44800, ascend_restored.bin)
The chooser-gate region holds a WRITE PAIR, one to each of two different
address spaces:

    447a0: 66 89 93 c8 2f 01 00   mov  WORD PTR [ebx+0x12fc8],dx
    447a7: 31 d2                  xor  edx,edx
    447a9: 8a 16                  mov  dl,BYTE PTR [esi]
    447ab: b3 01                  mov  bl,0x1
    447ad: 88 9c 02 d6 2f 01 00   mov  BYTE PTR [edx+eax*1+0x12fd6],bl   <-- STORE imm-derived 1, base+index+disp32
    447b4: 88 9d c0 01 00 00      mov  BYTE PTR [ebp+0x1c0],bl            <-- STORE 1 to EBP+0x1c0
    447ba: 80 bd c0 01 00 00 00   cmp  BYTE PTR [ebp+0x1c0],0x0           <-- the S10 chooser gate
    447c1: 0f 84 4c ff ff ff      je   0x44713
    447cd: 89 f0                  mov  eax,esi
    447d0: e8 6f 02 00 00         call 0x44a44                              <-- S7 DA_ action chooser
    447d5: 88 c3                  mov  bl,al
    447d7: 3c 0e                  cmp  al,0xe

THREE things follow, all to be verified, none assumed:
 (a) the state cell the engine WRITES is [edx+eax+0x12fd6] form — base+index
     +disp32, NOT [rowbase+0x1c0]. So a census keyed on disp==0x1c0 alone
     MISSES matrix writers; the disp32 0x12fd6 family is the matrix form.
 (b) [ebp+0x1c0] is an EBP-relative disp32 (modrm 0xbd, mod=10, rm=5). In
     Watcom flat model EBP is conventionally the GLOBAL DATA base, which
     would make the S10 gate read DGROUP+0x1c0 — a scalar scratch state, not
     a matrix cell. If so, diplomacy.md S10's "state byte +0x1c0+t per row
     0x1ee" and the gate are two different objects that happen to share an
     offset. MUST verify by finding how EBP is set in this function.
 (c) value written here is bl=0x1 (set at 0x447ab) — consistent with the
     MEASURED 0->1 AI-contact transition (S11), i.e. this site is plausibly
     the state-1 writer. imm 3 does not appear in this window.


## P1 RESULT — THE ENUM IS LIVE CODE: imm-3 writers EXIST (t180)
Source: one linear objdump of code object 0 [0x14bb0,0x82bb0) over
work/ascend_restored.bin -> work/r1/t180/code0.txt (140,902 lines), grepped
for store-to-disp forms at the mnemonic level. (The t107 full-encoding sweep
was launched too and is still running; the mnemonic pass is faster AND shows
the source operand, so it is the primary here.)

Census of `mov BYTE PTR [...+0x1c0], imm8` in code object 0 (26 total hits
for disp 0x1c0; frame-local ones KEPT VISIBLE because they are the trap):

    0x19eef  mov BYTE [esp+0x1c0],dl      <-- FRAME LOCAL, not the matrix
    0x25b06  mov BYTE [esp+0x1c0],al      <-- FRAME LOCAL
    0x274f8  mov BYTE [eax+ebp*1+0x1c0],cl
    0x3e69c  mov BYTE [edx+0x1c0],0x0
    0x3e98c  mov BYTE [eax+0x1c0],0x1
    0x447b4  mov BYTE [ebp+0x1c0],bl      (bl=1; immediately followed by the
                                          S10 chooser gate cmp [ebp+0x1c0],0)
    0x45572  mov BYTE [edi+eax*1+0x1c0],0x1   cluster A: value 1
    0x455d6  mov BYTE [edi+eax*1+0x1c0],0x2   cluster B: value 2
    0x4562f  mov BYTE [edi+eax*1+0x1c0],0x3   cluster C: value 3  <<<
    0x456c8  mov BYTE [edi+0x1c0],0x1
    0x4570c  mov BYTE [edi+eax*1+0x1c0],0x1
    0x45961 0x4596f  mov BYTE [eax+0x1c0],0x1
    0x459d3 0x459e1  mov BYTE [eax+0x1c0],0x2
    0x45a45 0x45a53  mov BYTE [eax+0x1c0],0x1
    0x45af1 0x45aff  mov BYTE [eax+0x1c0],0x3   cluster D: value 3 <<<
    0x45f13  mov BYTE [ebx+0x1c0],0x1
    0x461a8  mov BYTE [eax+0x1c0],0x1

ANSWER TO THE t180 QUESTION (first half, cited): YES. imm 3 is stored to a
+0x1c0 displacement at THREE sites — 0x4562f, 0x45af1, 0x45aff — all inside
FUN_000454a4 (0x454a4, size 0x1944, per work/functions3.tsv). State 3 is
emitted by the original engine; it is not a DA_ template artefact.

## P1b — CLUSTER A/B/C IS A THREE-WAY CASE BLOCK WITH RECIPROCAL MIRRORING
code0.txt lines 58715..58800 verbatim. Dispatch reaches the block through
`jmp DWORD PTR cs:[ebp+0x308b8]` at 0x45560. The base constant is
materialised at 0x45520 `mov eax,0x12e16` — the S10 window base is a real
code-baked immediate, and 0x12e16 + 0x1c0 == 0x12fd6, which is exactly the
disp32 family the rest of the image uses (see P2).

  CASE (cell := 1)  0x45567..0x455c8
     al = BYTE[esi]                            ; the OTHER empire index
     BYTE[edi + al + 0x1c0] = 1
     al = BYTE[edi + al + 0x1c0]               ; re-read (== 1)
     BYTE[edx + esi + 0x1c0] = al              ; MIRROR to reciprocal cell
     WORD[edx + 0x1b2]          = WORD[esi + 0x1d5]   ; attitude COPY
     WORD[edi + al*2 + 0x1b2]   = WORD[edi + 0x1d5]
  CASE (cell := 2)  0x455cb..0x45605
     BYTE[edi + al + 0x1c0] = 2 ; mirror ; WORD[edi + al*2 + 0x1b2] -= 0x28 (-40)
  CASE (cell := 3)  0x45608..0x45668
     bh = BYTE ds:0x7458e ; if bh == BYTE[esi]: WORD[edi + al*2 + 0x1b2] += 3
     cmp cl,0x4 / jne 0x45674                  ; <<< STATE-3 BRANCH GUARDED ON cl==4
     BYTE[edi + al + 0x1c0] = 3 ; mirror
     WORD[esi + edx*2 + 0x1b2] += 0xa ; WORD[edi + al*2 + 0x1b2] += 0xa  (+10 BOTH sides)

Static-side adjudication [inferred from the shape, NOT closure]:
  1 -> entered with an ATTITUDE COPY from [+0x1d5]; matches the MEASURED
       AI-contact 0->1 both-ways event (S11).
  2 -> entered with attitude -40 and the reciprocal set; matches the MEASURED
       player war-declaration 1->2 reciprocal (S11).
  3 -> entered with +10 attitude to BOTH cells; alliance-shaped in DIRECTION
       but the +10 is far too small to be the +280/+39 proposal bonus, so
       this reads as the ACCEPT/FORGE act rather than the offer.
OPEN: (i) what is `cl` / who sets it, (ii) [x+0x1d5] vs +0x1b2+2t,
(iii) whether (edi, edx) is the stride-0x1ee row pair the capture measures
(edx = sar DWORD[esp+0x1c2], 0x10 — a PACKED u16 PAIR, so the caller passes
both empire indices in one u32).

## P2 — THE MATRIX CELL'S REAL DISPLACEMENT IS 0x12fd6 (= 0x12e16 + 0x1c0)
26 sites reference disp32 0x12fd6 in code object 0. Readers compare against
0x0, 0x1, 0x2 and 0x3 — i.e. THE FULL FOUR-VALUE ENUM IS CONSUMED:
    0x19ff3 cmp [edx+ebx+0x12fd6],2      0x242b5 cmp [ecx+eax+0x12fd6],3
    0x22407 cmp [esi+eax+0x12fd6],2      0x24384 cmp [ecx+eax+0x12fd6],3
    0x24ede cmp [edx+ebx+0x12fd6],2      0x27295 cmp [ecx+ebx+0x12fd6],0
    0x276c0 cmp [edx+ebx+0x12fd6],0      0x282ff cmp [edx+esi+0x12fd6],0
    0x29f13 cmp [ecx+edx+0x12fd6],0      0x2a00f mov dl,[ecx+edx*2+0x12fd6]
    0x2a0ae cmp [edx+ebx+0x12fd6],0      0x2a32d cmp [edx+0x12fd6],0
    0x36966/0x36976 cmp [...,0]          0x37a13 cmp [esi+eax+0x12fd6],0
    0x3b13d cmp [ebx+eax+0x12fd6],0      0x3e9b5 mov BYTE [ebx+eax+0x12fd6],1
    0x41861 cmp [ecx+ebx+0x12fd6],2      0x447ad mov BYTE [edx+eax+0x12fd6],bl
    0x44c1a cmp [edx+ebx+0x12fd6],3      0x44c89 cmp [edx+ebx+0x12fd6],2
    0x44cf8 cmp [edx+ebx+0x12fd6],1      0x45f3c mov BYTE [ebx+edx*2+0x12fd6],1
    0x461d9 mov BYTE [ebx+eax+0x12fd6],1  0x4d2ca cmp [edx+0x12fd6],2
NOTE the index forms: [base + idx*1] and [base + idx*2] both appear. idx*1 is
the BYTE state cell; idx*2 is the i16 attitude cell (S10 law: att at
+0x1b2+2t). The S10 stride-0x1ee row law is therefore NOT how these sites
address the cell — they index empire-to-empire directly off one global base,
row-major over a n*n matrix, n from the campaign race count.

## P3 — ROW/CELL ADDRESSING LAW MEASURED FROM CODE (corroborates S10)
Three sites in FUN_00044848 (0x44848, size 0x507) show the cell arithmetic
verbatim, e.g. 0x44c02..0x44c22:

    imul   ebx, edx, 0x1ee                      ; row stride 0x1ee  <<< S10 CONFIRMED
    cmp    DWORD PTR [ebx+0x12e19], 0xffffffff  ; row owner != -1 (free-record guard, S12)
    cmp    BYTE  PTR [ecx+edx*1+0x1c0], 0x2     ; rec[SELF][edx] == 2
    mov    bl, BYTE PTR ds:0x7458e              ; bl = PLAYER empire index
    imul   ebx, ebx, 0x1ee
    cmp    BYTE  PTR [edx+ebx*1+0x12fd6], 0x3   ; rec[PLAYER][edx] == 3
    mov    DWORD PTR [eax], edx ; mov al, 0xa   ; emit DA 10 about empire edx

Two notations for the SAME cell, now tied together:
  row-relative : [row_base + other*1 + 0x1c0]         (ecx form)
  absolute     : [other + (owner*0x1ee) + 0x12fd6]    (0x12e16 + 0x1c0 baked)
=> the S10 window law (state byte +0x1c0+t per 0x1ee row, base 0x12e16) is
   now CODE-CONFIRMED, not merely RAM-inferred. The t77b retraction's hazard
   (a) about the static base is answered for the STRUCTURE (per-run
   re-location is still a capture question, untouched).

## P4 — THE THREE FOURTH-STATE CONSUMERS ARE THE THIRD-PARTY MESSAGE SELECTOR
All three inside FUN_00044848, identical shape, differing only in the state
pair tested and the DA emitted:
    0x44c02/0x44c1a  rec[SELF][x]==2 AND rec[PLAYER][x]==3  -> al=0xa (DA 10)
    0x44c71/0x44c89  rec[SELF][x]==3 AND rec[PLAYER][x]==2  -> al=0x7 (DA  7)
    0x44ce0/0x44cf8  rec[SELF][x]==2 AND rec[PLAYER][x]==1  -> al=0x9 (DA  9)
This is exactly the THIRD-PARTY rung §9 measured behaviourally. SEMANTIC
FORCE: value 3 is being tested as a relation the PLAYER can hold with a third
empire while SELF is at war with that empire — i.e. 3 is ALLIANCE-shaped, and
the enum ordering 0 < 1 < 2 < 3 = none / peace / war / alliance-with-third
is consistent with all banked transitions. [inferred from cited comparators;
still needs the writer's trigger to be closure-grade.]

## P5 — WRITER DISPATCH IS A 15-CASE TABLE, FULLY RESOLVED
FUN_000454a4 (0x454a4..0x45c30) header:
    454dd  cmp bl,0xe / ja 0x45c30               ; bl = event code, 15 cases
    454ea  lea ebp,[eax*4]                        ; EBP reused as index, NOT frame
    45560  jmp DWORD PTR cs:[ebp+0x308b8]
cs-relative base per R13 law (+0x14bb0) -> table at image 0x45468. Tool
scripts/r1_t180_switchtbl.py prints 15/15 targets inside [0x454a4,0x45c30):
  bl=0 ->0x45567(state1)  bl=5 ->0x457e9   bl=10->0x45a31(writes 1,1)
  bl=1 ->0x45bfb          bl=6 ->0x45883   bl=11->0x45aa3(writes 3,3) <<<
  bl=2 ->0x455cb(state2)  bl=7 ->0x4591d   bl=12->0x45b4f
  bl=3 ->0x45608(state3)  bl=8 ->0x45708(writes 1) bl=13->0x45699
  bl=4 ->0x45742          bl=9 ->0x459bf(writes 2,2) bl=14->0x45c1f
Exactly THREE callers of FUN_000454a4 exist in code object 0: 0x36b2f,
0x36c47, 0x4470e. The event-code census for the cell is therefore closed at
static level: state written per case = {1: 0,8,10; 2: 2,9; 3: 3,11; ...}.

## P6 — CROSS-METHOD AGREEMENT (independent censuses)
scripts/r1_t107_writers_full.py 0x1c0 (encoding-enumeration + function-start
boundary verification) and the mnemonic-level grep of the linear objdump
produce the SAME site list for disp 0x1c0 (t107 additionally surfaces
0x6bc7c / 0x6ecc0 `mov DWORD [..+0x1c0]` and the [esp+0x1c0] frame locals).
Two methods, one site set — the imm-3 sites 0x4562f, 0x45af1, 0x45aff are
not decoding artefacts.

## P7 — THE STATE-3 WRITERS AND THEIR GUARDS (decisive result)

### Case bl=3 (0x45608) — writes 3 only when cl == 4
    45608  mov bh, BYTE ds:0x7458e          ; player empire index
    4560e  cmp bh, BYTE [esi] / jne         ; (attitude +3 side-effect if self==player)
    4561f  cmp cl,0x4 / jne 0x45674         ; <<< GATE
    4562f  mov BYTE PTR [edi+eax*1+0x1c0],0x3      ; SELF row, other column
    45637  sar edx,0x10
    4563a  mov al, BYTE [edi+eax*1+0x1c0]
    45641  mov BYTE PTR [edx+esi*1+0x1c0],al       ; MIRROR row, reciprocal
    45648..0x45666  attitude += 10 on BOTH cells

### Case bl=11 (0x45aa3) — writes 3 to both cells under an attitude test
    45aa3  cmp cl,0x13 / jne 0x45a8f        ; <<< GATE: cl == 19
    45aa8  add WORD [eax+0x1b2], 5
    45ab7  mov ecx, DWORD [ecx+0x12fe5]     ; packed pair; >>16 = other's attitude
    45ad4  sub ebp, 0xa                     ; threshold minus 10
    45ada  cmp ecx, ebp / jle 0x45c30       ; <<< requires att > (other_att - 10)
    45af1  mov BYTE PTR [eax+0x1c0],0x3     ; cell A
    45aff  mov BYTE PTR [eax+0x1c0],0x3     ; cell B (reciprocal)
    45b06..0x45b42  attitude += 5, +5, +0xf, +10, +10 across the pair
=> EVERY state-3 store in the image is CONDITIONAL on an ATTITUDE test, never
   unconditional. State 3 is earned, not default — which is exactly why 28,843
   trusted rows of banked play never produced one (Orfa att 485->451 vs
   ACCEPT_ALLIANCE 570, S12).

### The `cl` dimension is FUN_00044fc0's return value = §6 offer-state setter
FUN_00044fc0 (0x44fc0, called at 0x36c22 and 0x446f3 with the chooser's DA
index in bl):
    44fd3  mov al,bl ; sub al,2 ; cmp al,0xc / ja 0x45448     ; bl in 2..14
    44fe6  jmp DWORD PTR cs:[eax*4+0x303dc]
Acceptance ladder case body (0x44fff..0x45029) verbatim:
    mov ax, WORD [esi + other*2 + 0x1b2]       ; att[self][other]
    cmp ax, WORD [esi+0x1d1]                   ; <<< row ACCEPT threshold
    jle -> mov al,5                            ; REJECT code
          mov al,4                             ; ACCEPT code
So `cl == 4` (the case-bl=3 gate) IS the accept verdict of that ladder, and
`cl == 5` is its reject. This is the FIRST static account of how an alliance
would form: chooser emits DA_ProposeAlliance -> FUN_00044fc0 compares the
ATTITUDE against [row+0x1d1] -> verdict 4 -> FUN_000454a4 case 3 writes
state 3 to both cells and bumps both attitudes by +10.
[Status: cited instruction-level chain, n=0 observations. Strong enough to
name the mechanism and to make the capture test PRECISE; not yet closure
without either (a) an observed cell==3, or (b) verification that [row+0x1d1]
IS the per-race ACCEPT_ALLIANCE value read from raceNN.dip.]

## P8 — A THIRD STATE WRITER, OUTSIDE FUN_000454a4 (scenario setup, value 1)
0x27476..0x27511 is a loop over races (`mov dx, WORD ds:0x13b98` = race count,
`add eax,0x1ee` row walk) that copies attitude WORD[+0x12feb] into both cells
and then writes state **1** unconditionally to the pair:
    274f0  mov cl,1
    274f2  mov BYTE PTR [edi+0x12fd6],cl        ; absolute form
    274f8  mov BYTE PTR [eax+ebp*1+0x1c0],cl    ; row form (same cell, 2 notations)
It SKIPS the player's own row (`cmp eax,edx / je` against
0x12e16 + player*0x1ee) and is gated by `cmp DWORD ds:0x10ba0,0 / je`.
This is the START-OF-SCENARIO relationship seeding — the static origin of the
"pre-war EVERY pair sat at 1" observation in S11, and of the 0->1 pattern the
capture calls AI contact (candidates for the two explanations are now both
documented; disambiguating them is a capture question, unchanged).

## P9 — CALLER CENSUS OF THE STATE MUTATOR (bounded)
FUN_000454a4 has EXACTLY THREE call sites in code object 0: 0x36b2f, 0x36c47,
0x4470e. The 0x4470e caller is inside the per-race loop whose iterator is
visible at 0x4471b..0x44720 (`inc ebp; inc edi; add ecx,2; add eax,0x1ee`) —
attitude cells walked by 2, rows by 0x1ee, i.e. the chooser sweep.

## P10 — CALLER-ARGUMENT LAW FOR THE MUTATOR (closes the `cl`/`bl` question)
The sweep caller 0x446d9..0x4470e verbatim:

    446ca  mov BYTE PTR [esi+0x1e9], 0xe          ; init slot to DA_NoDipAction
    446d9  lea  eax,[esp+8]                        ; OUT-PARAM slot
    446f3  call 0x44fc0                            ; §6 offer-state setter
    44701  movsx ecx, al                           ; cl := VERDICT CODE
    4470a  mov  ebx, DWORD [esp+8]                 ; bl := DA INDEX (out-param)
    4470e  call 0x454a4                            ; apply the transition

So FUN_00044fc0 returns a verdict code and writes the chosen DA index;
FUN_000454a4's 15-case bound (cmp bl,0xe) is EXACTLY the DA index space
(0..14). State transition = f(DA index bl, verdict code cl). This is cited
for the 0x4470e caller; the other two callers (0x36b2f, 0x36c47) load ecx
from different sources (0x36b17 movsx ecx,dl / 0x36c27 movsx ecx,al after an
intervening call) and their cl provenance is NOT claimed.

Verdict codes emitted by the bl=3 (DA_ProposeAlliance) rung 0x44ffc..0x45029:
    att[self][other] > WORD[esi+0x1d1]  -> al = 4  (accept)
    otherwise                            -> al = 5  (reject)
and FUN_000454a4 case bl=3 stores state 3 ONLY when cl == 4. +0x1d1 is
ACCEPT_ALLIANCE per the MEASURED §8 field map (loader FUN_00044290 positional
parse, 22/22 .dip key-order proof). VERIFIED ALLIANCE-FORMATION LAW:
    state 3 is written to BOTH cells iff att > race.ACCEPT_ALLIANCE.
Case bl=11 (0x45aa3) is a second alliance-shaped channel requiring cl==19
(the code emitted at 0x45420, rung 0x4536a) plus att > (other-10); its cl
provenance is unresolved and NOT claimed.

## P11 — ENUM ADJUDICATION (each value backed by a cited comparator AND/OR a
## banked live transition)
  0 = NO ACTIVE RELATIONSHIP. Chooser entry 0x447ba skips the whole dialogue
      rung when the cell is 0. Scenario seeding 0x274f2 writes 1, never 0.
  1 = PEACETIME / CONTACTED, not allied. (a) live: pre-war EVERY pair sat at 1
      (S11) and AI contact fires 0->1 both ways on one boundary; (b) static:
      case bl=0 (0x45567) sets 1 while COPYING attitude from [row+0x1d5] =
      START_ATTITUDE (§8); (c) semantic lock: consumer 0x44ce0 requires
      self==2 AND third==1 to emit DA 9 = DA_DeclareWarOnOtherRace (§7) — the
      target of a war declaration must NOT be allied.
  2 = AT WAR. (a) live: player war-declaration 1->2 reciprocal, sustained 244
      turns (S11); (b) static: case bl=2 (0x455cb) sets 2 both ways with
      attitude -40; (c) semantic lock: 0x44c71 requires self==3 AND third==2
      to emit DA 7 = DA_OfferPeaceToOtherRace — the recipient must be at war.
  3 = ALLIED. (a) static formation law P10 (att > ACCEPT_ALLIANCE writes 3
      both ways + attitude bumps); (b) semantic lock: 0x44c1a requires
      self==2 AND third==3 to emit DA 10 = DA_BreakAllianceWithOtherRace —
      the third party must hold an ALLIANCE with the player; (c) consumers
      exhaust the value: readers test {0,1,2,3} and nothing else (P2).
  NOT OBSERVED live in 28,843 trusted rows — the campaign never crossed
  Orfa ACCEPT_ALLIANCE (485 peak / 570, S12), which P10 now explains
  causally rather than as an absence.

## P12 — REWRITE IMPACT (honest scope)
rewrite/src/game/diplomacy.cpp:227 `if (!st->atWar && !st->allied)` is
CONSISTENT with value 1 (single neither-state), and DipAction::AcceptAlliance
exists but is never returned: the original's acceptance test lives in the
RECEIVER's rung (0x44ffc against the receiver's own +0x1d1), and
decideDipAction's signature carries no incoming-offer parameter. Upgrading
it requires the ownership/offer plumbing already tracked as the W-B engine
gate — so NO rewrite behaviour claim is contradicted and NO code change is
justified this iteration. The comment at diplomacy.cpp:244 ("state changes
only on accept") is now CITED rather than assumed, and the accept condition
is named: att > acceptAlliance, then allied=1 with attitude +10 (case bl=3
tail, 0x45648..0x45666).
