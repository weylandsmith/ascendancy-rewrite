# t209 WIP — 0x3a174 invasion-leg residues: out-param caller law + clamp-vs-repel position

Trigger triage: timeline mtime 1793294532 / size 5,721,578,066 == frozen
baselines, dosbox down, tree clean at 1b00c13 -> no sitting; STATE t209 stood.

Assignment (STATE.md t209):
(1) OUT-PARAM LAW: enumerate callers of 0x3a174 (E8 full-image byte-pass),
    disasm call sites 0x42c8e + 0x3d951; what is the 3rd arg address; does any
    caller pre-init it; is the callee's ability==0 -> store-1 arm the only
    writer before the read?
(2) CLAMP-vs-REPEL POSITION: disasm 0x42c8e..func-end; what branches on the
    0x3a174 return; does the clamp at 0x3a25a run before the repel decision.
No semantic code change without the cited tail.

## S1 — caller census + function spans [verified this session]
E8 full-image byte-pass (rel32-correct scan over work/ascend_restored.bin):
callers of 0x3a174 EXACTLY {0x3d951, 0x42c8e} — matches t207's census.
Spans (functions_full.tsv file_off,size): 0x3d951 in 0x3d2fe+2134; 0x42c8e in
0x41e34+6087 (named FUN_00041e34, size 6602 in functions.tsv — overlap,
tightest-full wins per t206 pitfall).
Callee arg convention (0x3a174 prologue, verified): EAX=ESI planet obj,
EDX=EDI slot idx, EBX=ECX OUT-PARAM POINTER (3rd arg). Body:
`mov ecx,ebx` @0x3a17f; writes `[esp],0` @0x3a208 (witness slot) / `0xffffffff`
@0x3a215 (ability-gate -1 arm — witness, NOT the out param); out param written
at 0x3a35e `mov [ecx],eax` where eax = [esp+8] = defense result, forced 1 iff
witness==-1 (0x3a349..0x3a34e).

## S2 — caller B = 0x42c8e (order resolver, invasion leg) [verified]
0x42c26..0x42cd7 (windows work/t209 via r205d_windows): slot-scan validates
item type 0x17 twice via 0x396cc + owner compares (asserts 0xbc0). Call site:
`lea ebx,[esp+0x30c]` (0x42c7d) -> out param = stack local [esp+0x30c];
EAX=esi obj, EDX=ecx&0xffff slot (0x42c84/8a). AFTER THE CALL:
- 0x42c93 `mov edx,ecx` + 0x42c97 `call 0x396cc` — EAX return CLOBBERED,
  ZERO branches on 0x3a174's return value.
- out-param slot [esp+0x30c] never read: 0x42cba `mov [esp+0x30c],eax`
  OVERWRITES it with the 0x39894 (targetability) return; 0x42cc1 branches on
  THAT (-1 -> 0x42cd7 -> eax=-1 `ret 0x1c`).
=> In the engine invasion path the out param is a DEAD STORE and the return is
discarded; caller B consumes NOTHING from 0x3a174 except side effects.

## S3 — caller A = 0x3d951 (UI/cheat family) [verified]
Prologue block 0x3d8f9..0x3d930: two 0x56ca4 calls (ecx=0,ebx=0x32 /
ecx=word[obj+0xab] slot, ebx=0x34) on [ebp-0x10] obj. Call site:
`lea ebx,[ebp-0x24]` (0x3d942) -> out param = stack local; EAX = dword[0x43508]
(global), EDX = word [obj+0xab]. AFTER: esi=eax return, `cmp esi,-1` picks
message 0x1fc5 vs 0x1fd3 (0x56d1c); OUT PARAM READ: 0x3d9c1
`mov edx,[ebp-0x24]; cmp edx,1` -> message-id 0x1c vs 0x1d (0x21a20), value
also pushed as format arg to 0x76c79 @0x3d9e4; tail writes words 0x1c/0x49/0x1d
to [ecx+0xcb1/0xcb3/0xccc] (UI state; 0x49 = invasion gizmo byte).
=> CALLERS DISAGREE (the assigned fork): A consumes out param (==1 test +
message), B discards it. Law to bank: callee always writes exactly one value
(defense-result or forced 1) at 0x3a35e; engine-relevant path ignores it.

## S4 — out-param law CLOSED (leg 1 answer) [verified]
Exhaustive operand pass over the disassembled callee body 0x3a174..0x3a4dd
(seed-restart capstone, 284 insns): the ONLY write through the out-param
register is 0x3a35e `mov dword [ecx],eax` (ecx := ebx at 0x3a17f, never
rewritten before it — reg-write census: push ecx/mov ecx,ebx, then first
reuse `mov ecx,1` @0x3a3dc AFTER the store; pop ecx @0x3a4dd restores). NO
`ret` exists anywhere in [0x3a174,0x3a35e) (explicit ret-scan) and NO jump
from below 0x3a35e lands at/after it other than in-loop edges — so every
non-assert path reaches 0x3a35e exactly once. Assert arms (bad slot idx
vs count 0x3a199, non-0x17 type 0x3a1b9, self-owned gate 0x3a1ef) call
0x2a428 which is the vendor assert reporter (0x2a428: test eax; push ebx;
push edx; push LINE; jmp 0x2a4cc — never returns to the caller stream).
VALUE LAW: eax = [esp+8]; [esp+8] := [esp+0x14] (defense result) @0x3a345,
FORCED 1 iff witness [esp]==-1 @0x3a349/0x3a34e; witness := 0 @0x3a208,
:= -1 @0x3a215 iff ability byte (diplo-row0+0x19d, scale-2 form 0x12fb3)
== 0 — the t207 reading is now VERIFIED end-to-end, and the forced-1 value
is ALSO the strip-loop bound ([esp+8] gates 0x3a36e/0x3a3b5) i.e. semantically
"defense items consumed, minimum 1 when the attacker lacks the species
ability". CALLER PRE-INIT: NEITHER call site writes its slot before the call
(B: lea ebx,[esp+0x30c] @0x42c7d is first touch; A: lea ebx,[ebp-0x24]
@0x3d942 is first touch) — callee 0x3a35e is the sole writer before A's read
@0x3d9c1. LAW CLOSED; both callers' consumption banked in S2/S3.

## S5 — clamp-vs-repel position CLOSED (leg 2 answer) [verified]
The answer needed the CALLER tail per assignment; it is decisive:
(1) Inside 0x3a174 the clamp (0x3a25a handler==-1 -> 0x3a28c/0x3a291 attitude
    cell := DECLARE_WAR-10 while cell < DECL line) executes BEFORE the
    defense-law loop even starts counting (0x3a29e..0x3a2f5 init,
    0x3a2c9..0x3a325 shield score, 0x3a327..0x3a33e result select) — the
    outcome of the defense is not merely unbranched at the clamp, it is not
    yet COMPUTED there. REPEL IS REAL but determined strictly after the clamp:
    success/repel branches ONLY at 0x3a45c `cmp invmod, shieldscore; jg
    0x3a46c` (success tail: event 0xd announce path, planet+0x67 :=
    [0x12e10] @0x3a4c9, [esp+0xc] := -1 return sentinel @0x3a4c5; else
    0x3a466 witness check -> activator tail with return 0).
(2) At the caller 0x42c8e the return is DISCARDED: 0x42c93/0x42c97 re-call
    0x396cc which clobbers EAX; the following `cmp edi,eax` @0x42c9c is the
    ship-record identity ASSERT (0xbc4), not an outcome branch. The out-param
    slot is likewise never read (overwritten @0x42cba with 0x39894's return).
    => no order-survival or ship-survival branch anywhere keys on the
    invasion outcome at this call site; control flow is outcome-INDEPENDENT.
CONCLUSION (bank per assignment, no semantic change): the original pays the
guarantee-war clamp AT ATTEMPT TIME, unconditionally once the diplo handler
returns -1 (i.e. on ANY invasion resolution against a non-at-war owner, repelled
OR successful). The rewrite's capture-branch wiring (clamp only when the
aggregate volley exceeds hull) is therefore a DOCUMENTED UNDER-MODEL of an
attempt-time law; rebuilding combatPhase to fire per attempt is a projection
NOT authorised this iteration (aggregate model conflates gunnery+invasion,
OQ-019 boundary). campaign.cpp divergence comment amended with these cites.

## S6 — rewrite/doc deltas this session
(1) campaign.cpp capture-branch comment block: "undetermined statically" ->
    cited attempt-time law (this file S5).
(2) _wip_t207.md S7e: (b) CLOSED via S4; divergence note CLOSED via S5;
    (c) 0x3d951 context now MEASURED (UI message family S3, no longer
    [unverified]); (a)(d)(e) unchanged (e2e pin stands; defense law = OQ-019
    family; zero in-corpus clamp witnesses unchanged).
(3) diplomacy.md S19: clamp position + out-param caller law appended.
NO semantic code change; blast radius trivially unchanged (comment-only).
