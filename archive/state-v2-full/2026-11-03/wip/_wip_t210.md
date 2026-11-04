# t210 — PER-SHOT STACKING vs PER-ENGAGEMENT AGGREGATE at the 0x4b875 call

Question (residue carried t204..t209): the original's 0x43a4c attack-dip cost
= 10*(MOVSX([0x13bc4])+1) PER CALL (t204 law). If the 0x4b875 call site sits
inside a per-shot / per-gizmo / per-attacker loop, the original stacks -20 per
battle multiple times and the rewrite's per-engagement `applyAttackDipCost`
under-fires. Assignment: STATE.md t210 legs (1) nesting of 0x4b875 inside
0x4b740, (2) six-caller census with the t89 mode==1 correlation, (3) bank a
LAW either way, no combatPhase semantic change.

Tooling: `scripts/r205d_windows.py work/ascend_restored.bin <start>:<end>` via
/home/hrethric/tools/revenv/bin/python (project .venv lacks capstone — re-hit,
t207/t205 pitfalls).

## S1 — 0x4b740 END-TO-END: the 0x4b875 call is LOOP-FREE and once-per-invocation

Full body 0x4b740..0x4b8e2 (`ret` at 0x4b8e2) decodes contiguously with
capstone x86-32 (zero undecodable bytes — no seed-restart needed this time).
Control-flow inventory of the whole function:

- Entry regs: eax=damaged-ship ptr (->esi 0x4b746), edx=mode (->[esp+8]),
  ebx=raw damage (->[esp]), cx=?(->[esp+0x10]), stack arg [esp+0xe] high word.
- Two vendor identity asserts 0x4b77a / 0x4b7a2 (call 0x2a428 pattern).
- 0x4b7a7..0x4b7d6: shield absorb (edi = applied dmg clamped to [esi+0x90],
  ebp = hull spill [esp]-ebx-... , flags byte [esp+0xc] |= 2 / |= 4).
- 0x4b7f1 GATE: `cmp dword [esp+8],1 ; jne 0x4b8d8` — the ENTIRE
  0x4b7fc..0x4b875 region (attacker-row lookup + the 0x43a4c call) runs ONLY
  when mode==1. Independent re-confirmation of the t89 commit law at this site.
- 0x4b7fc..0x4b834: attacker gizmo/row select on [esi+0x58] (dh):
  dh==4 -> ecx=[esi+0x59]; dh==3 or 1 -> ecx=[[esi+0x59]+0xa] scaled
  (0x13bc5 + 96*row via 32*row-row then shl 5 == 96*row ... arithmetic:
  eax=4*r; eax-=r -> 3r; eax<<5 -> 96r; ecx=0x13bc5+96r); dh==2 falls through
  to the test with ecx=0; dh other -> ecx=0.
- 0x4b836..0x4b846: `test ecx,ecx; jne 0x4b84b` else assert 0x2a428(id 0x53)
  and CONTINUE with ecx unchanged (assert reporter never returns — t209).
- 0x4b84b..0x4b875: ebx = ecx (attacker-row base), eax = 0x12e16 + 39*owner
  ([esi+0x54] sar 16; 39 = ((x<<5)-x)<<3-x pattern), [esp+4]=high arg,
  `call 0x43a4c`. One call instruction, statically.
- 0x4b87a.. tail: shield/hull subtraction, death path 0x49d2c, all outcome-
  independent of the call's return (EAX clobbered at 0x4b8ad by `xor eax,eax`).

JUMP-GRAPH FACT (the decisive one): every conditional branch in the body jumps
FORWARD — targets {0x4b76e,0x4b77f,0x4b796,0x4b7a7,0x4b7be,0x4b7da,0x4b7f1,
0x4b80b,0x4b81a,0x4b836,0x4b84b,0x4b8d8} all > their site; there is NO
back-edge anywhere in 0x4b740..0x4b8e2, hence the function contains no loop
and the 0x4b875 call executes AT MOST ONCE PER INVOCATION of 0x4b740.
Stacking, if real, must come from the callers.

## S2 — six-caller census (E8 byte-pass, whole image, zero packed-u32 sites)

Literal u32 0x0004b740 search: EMPTY (no thunk/vtable indirection). Direct E8
edges to 0x4b740, EXACTLY SIX:

  0x1a146, 0x39d9f, 0x3a0b3, 0x4bb56, 0x4d191, 0x4d2dd

(per-caller loop-nesting + mode-arg analysis follows in S3)

## S2b — PITFALL: capstone operand-type constant (SELF-CAUGHT, detector validated)

First CFG pass reported ZERO loops everywhere. Cause: capstone operand types
are INVALID=0, REG=1, IMM=2, MEM=3 — `operands[0].type == 3` means MEM, so
every branch edge was silently dropped from the CFG (no SCC, no back-edge).
Second bug same family: a back-edge is NOT `target <= site` — the 0x3a174
defense loop's back-edges are `jne 0x3a2c9` @0x3a30e / `je 0x3a2c9` @0x3a31f
with target NUMERICALLY ABOVE the site (loop head mid-range). Sound test =
SCC size>1 over the call's containing function. Fixed in
scripts/r210_loop_nesting.py (CS_OP_IMM + Tarjan SCC + entry = nearest
ret+nop-padding boundary validated by `insns[caller].mnemonic=='call'`
alignment). VALIDATION: the script finds the known 0x3a2c9..0x3a325 defense
loop when run on 0x3a30e — positive control.

## S3 — CALLER NESTING RESULT (the answer's core)

scripts/r210_loop_nesting.py, all six callers, aligned=True each:

  0x1a146 (fn 0x19e93..)  NOT in any loop        edx at call: `xor edx,edx` -> mode 0
  0x39d9f (fn 0x3980f..)  NOT in any loop        edx = ebp (mode from context; 0x39f00 gun-bombardment family, t207)
  0x3a0b3 (fn 0x39eff..)  NOT in any loop        edx = 1 (`mov edx,1` @0x3a0a9)  mode 1 ACTIVE
  0x4bb56 (fn 0x4b8e3..)  NOT in any loop        edx = [esp+0x4d0]
  0x4d191 (fn 0x4cd8f..)  ENCLOSING SCC 0x4d0a5..0x4d1a4 (back-edge 0x4d1a4 `jmp 0x4d0a5`)   edx = [esp+0x73c]
  0x4d2dd (fn 0x4cd8f..)  ENCLOSING SCC 0x4d2ab..0x4d2fd (back-edge 0x4d2fd `jl 0x4d2ab`)    edx = [esp+0x73c]

t89 correlation (mode==1 only fires the 0x43a4c leg — re-verified statically
at the gate `cmp [esp+8],1; jne 0x4b8d8` @0x4b7f1 inside 0x4b740 itself, S1):
- 0x1a146 passes mode=0 -> DEAD leg (no cost possible, loop or not).
- 0x3a0b3 passes mode=1 once per invocation, acyclic -> once per item-0x17
  event (t204: ship-cost path via 0x396cc).
- 0x4d191/0x4d2dd pass the SAME variable [esp+0x73c]; both sit in loops
  inside one big combat function 0x4cd8f — THESE are the stacking candidates.
  Induction variable + bound + mode value = S4.

## S4 — combat dispatcher fn 0x4cd8f (the 0x4d191/0x4d2dd host) FULL-LOOP CENSUS

Function body 0x4cd90 (nop 0x4cd8f = padding) .. 0x4d692 (`ret` 0x4d693-1);
prologue `push ebx/ecx/esi/edi/ebp; sub esp,0x75c` @0x4cd90..0x4cd9b;
mode arg edx -> [esp+0x73c] @0x4cd9d; ZERO other writes to [esp+0x73c] in the
whole function (operand census) — the mode is INVARIANT inside this function,
so both looped call sites fire with the caller's mode, never a locally-forced
mode. Reads: 0x4ce2b `cmp [esp+0x73c],1`, 0x4d17a, 0x4d2d3 (the two call prep
sites).
Census (Tarjan, this script): loops in 0x4cd8f..0x4d693 =
  0x4cf25..0x4cff6, 0x4d0a5..0x4d1a4 (hosts 0x4d191), 0x4d23a..0x4d272,
  0x4d2ab..0x4d2fd (hosts 0x4d2dd), 0x4d35d..0x4d509.
  0x4d0a5 loop: induction EBP += 4 (0x4d19d), bound [esp+0x730] (0x4d196),
  back-edge `jmp 0x4d0a5` @0x4d1a4; skips self (`cmp esi,edx; je 0x4d196`
  @0x4d0ac, esi = own ship) — a per-OTHER-ENTITY loop reading a position array
  ([edx+0x9e] xyz delta vs [esp+0x74c]) => SELF-DESTRUCT/AREA splash over the
  other combat entities (t87 row: 0x48 Self Destructotron = 0x4d075 loop).
  0x4d2ab loop: induction EBP += 4, bound [esp+0x734] (0x4d2e9), back-edge
  `jl 0x4d2ab` @0x4d2fd; per-entity gate `edx.owner != esi.owner`
  (0x4d2be je skip) AND race-alive table check byte[0x12fd6+494*owner]==2
  (0x4d2ca) — i.e. per HOSTILE ALIVE-POWER entity.
E8 census: exactly ONE caller, 0x4a3c4 — the cat5 arm of the category
dispatcher 0x4a360 (`cmp cl,5` @0x4a3bf, t88 category law). No literal-u32
(thunk) sites. (t210 self-correction: an earlier S4 draft said "reached only
indirectly" from a literal-only search — wrong, the E8 pass finds 0x4a3c4.)

=> MODE-1 REACHABILITY is what decides stacking. Inside 0x4b740 the 0x43a4c
leg is gated `cmp [esp+8],1` @0x4b7f1, so the cost fires once per mode-1
INVOCATION of 0x4b740. Looped sites 0x4d191/0x4d2dd multiply invocations per
splash event; the volley path multiplies them per weapon. The commit law
(t88a, [verified] by re-disasm this session @0x25560/0x25575: both `mov edx,1`
then `call 0x49f28` / `call 0x39c10`, each followed by `jmp 0x2551b` — i.e.
BOTH mode-1 sites sit in the SAME loop whose head is 0x2551b) is the last
quantifier. Loop head + induction + bound = S5.

## S5 — command-exec fn 0x2547c: the commit loop and BOTH mode-1 arms

Whole function 0x2547c..0x25530 decoded. Structure:
- Loop A 0x254ad..0x254fc (induction EAX, bound word [ebp+0xd88]): builds a
  list of MATCHED gizmos (ship-order slot flags [esi+0x14]|[esi+0x15] bit
  (1<<player) @0x254ca..0x254e5) into a stack array, count -> word [esp+0x18].
- Loop B 0x2550c..0x25527 (induction ECX, bound word [esp+0x18] — THE MATCHED
  GIZMO COUNT): per entry: call 0x41260 (movement/resolve probe, flag out
  byte [esp+0x10]), then branch on flag ah ([esp+0x10] high-of-byte read
  @0x25556 `mov ah,[esp+0x10]`; note the flag is the SECOND byte of the
  0x41260 out-param dword, gun operand [esp+0x11] @0x25565):
    ah==0 -> next gizmo (`jmp 0x2551b` @0x2555e)
    ah==3 -> 0x25560 arm: `mov edx,1; call 0x49f28` (GUN commit)
    ah==2 -> 0x25570 arm: `mov edx,1; call 0x39c10` (ABILITY commit)
    ah==1 or ah>=4 -> assert trap 0x2a438 @0x25598 (ids 0x8f5/0xd92).
    [t210 correction to t88a's "ah>=4 = assert trap": ah==1 ALSO traps —
    `cmp ah,2; jb 0x2558c` @0x25583 routes it there; the trap never returns.]
  Both arms `jmp 0x2551b` (loop-B continue). So ONE mode-1 activation PER
  MATCHED GIZMO PER ORDER COMMIT — the loop-B bound is the multiplier.

## S6 — THE LAW (banked, both legs cited)

STACKING IS REAL. The original's attack-dip cost fires ONCE PER mode-1
INVOCATION of 0x4b740 (gate `cmp [esp+8],1; jne 0x4b8d8` @0x4b7f1, S1), and
the mode-1 invocations per player order are:
(a) GUNS: per committed cat-0 weapon. Chain: 0x25560(m=1)->0x49f28 ->
    [ship+0x62]==1 -> 0x4a360 dispatcher (@0x4a3a0 when [ship+0x67]==0) ->
    cat0 0x4b8e4 (dec NumUses @0x4a390, mode passthrough @0x4b8f1
    [esp+0x4d0]) -> its ONLY 0x4b740 call 0x4bb56 (E8 census inside
    [0x4b8e4,0x4cd90): exactly one). The generic volley loop 0x4a5c1 is a
    DRY-RUN: `xor edx,edx; call 0x49f28` @0x4a5ec/0x4a5f1 -> mode 0 -> NOT a
    cost site (consistent with the t88a commit law). Per-order gun-cost
    multiplier = committed cat-0 gizmo count (loop-B bound, S5).
(b) ABILITIES: per committed gizmo of any kind via 0x25570(m=1)->0x39c10;
    the cat-5 dispatcher 0x4cd90 (E8 call from 0x4a3c2, t88 category law)
    stacks the cost over its splash loops: per-OTHER-ENTITY loop
    0x4d0a5..0x4d1a4 call 0x4d191, per-HOSTILE-ALIVE-POWER loop
    0x4d2ab..0x4d2fd call 0x4d2dd (gated owner!=victim @0x4d2be and
    race-alive byte[0x12fd6+494*owner]==2 @0x4d2ca), mode = entry edx
    ([esp+0x73c] written ONLY @0x4cd9d — invariant, S4). Upper bound per
    activation = loop bound [esp+0x730]/[esp+0x734] (entity-array size;
    runtime values play-gated).
(c) DIRECT mode-1 acyclic sites: 0x3a0b3 (item-0x17 ship-cost hit, `mov
    edx,1` @0x3a0a9 — t204 family), each once per invocation of its host fn.
(d) DEAD arms: 0x1a146 (`xor edx,edx` @0x1a13f — mode 0), 0x39d9f host fn
    0x39810 passes edi-derived edx derived from [eax+0x57] with mode NOT 1 on
    the measured path (t207 gun-bombardment family), 0x4bb56 only via mode-0
    unless S6(a) chain carries mode 1.

REWRITE DELTA (DOCUMENTED UNDER-MODEL, NO SEMANTIC CHANGE per leg-3 rule):
combatPhase charges applyAttackDipCost once per (attacker,victim) engagement
(campaign.cpp:1935, first-pair-per-phase); the original charges once per
committed weapon/victim — a multi-gun ship ordering N cat-0 gizmos at the
same victim pays N x 20 (t204 census subtrahend), and a cat-5 splash pays
per hostile victim. Converting to per-commit charges crosses the OQ-019
per-ship boundary (BLOCKED-USER design projection) — same rule t209 applied
to the clamp position and t204 applied to the volley mapping. The t204 S2
line "Fires PER SHOT/PER-HIT ... volley can stack -30 repeatedly" is now
QUANTIFIED: per COMMITTED WEAPON (not per shot — volley is mode 0), and the
-30 figure is superseded by the t204-measured 20 (govByte==1, 20/20 saves).
Static residue CLOSED; what remains play-gated: clamp witnesses (OQ-016),
runtime entity-loop bounds.

