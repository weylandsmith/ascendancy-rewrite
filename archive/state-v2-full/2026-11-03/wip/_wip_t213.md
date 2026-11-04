# _wip_t213 — al-form [ship+0x62] value-source trace (t211-fallback residue)

Task (STATE t212 NEXT item b): identify WHAT writes byte[ship+0x62] at
0x15c6d/0x15d98 and whether any path sets it outside {0,1}.
Trigger triage FIRST: timeline mtime 1793294532.100000000 / size 5,721,578,066
/ tail-64KiB md5 9054cc6c66802e6f80431d4ffa1416ee — ALL THREE == t213
baselines verbatim; no dosbox process. NO SITTING -> static work.

Interpreter: capstone is at /home/hrethric/tools/revenv (5.0.7); .venv and
system python3 do NOT have it. Use `/home/hrethric/tools/revenv/bin/python`.

## S1 — BOTH SITES ARE SOUND AND CONSTANT-FREE (r213_probe_a.py)

Entry-anchored decode of the CONTAINING function (functions_full.tsv
156d4 size 0x2551 -> 0x17c25; 2,673 insns, single gap at 0x17c23):
0x15c6d and 0x15d98 are both instruction starts (t108 law satisfied — unlike
0x42211/0x43188 which stay alignment-suspect). Both `mov byte [reg+0x62], al`.
SCANNER VALIDATED first (t211 law): E8 callers of 0x4b740 == t210's six
EXACTLY (0x1a146,0x39d9f,0x3a0b3,0x4bb56,0x4d191,0x4d2dd) -> zeros trustworthy.

## S2 — THE SITES ARE ORDER-COMMIT SITES, NOT UI WRITERS

Both sites sit in the SAME giant command dispatcher 0x156d4..0x17c25 (entry
`push esi/edi/ebp; sub esp,0x8c; mov ebp,eax (=ship struct); mov edi,edx`,
then command-code switch `cmp dx,0x327; jb 0x162ac; jbe 0x15998`).
docs/re/r1-savestate.md:393 already lists 0x156d4 among the **batmode/batcon
E1 functions** — battle-mode command code, not UI. Decisive structural proof:

  site 1: 0x15c63 mov edx,[ebp+0xac] ; 0x15c69 mov al,[esp+0x50]
          0x15c6d mov [edx+0x62],al
          0x15c70..0x15cba  packed write-through of the order record:
            [ship+0x63]=dword, [ship+0x67]=byte(day), [ship+0x68]=dword,
            +0x6c/0x70 via lea-chains, [ship+0x78]=dword, ... [ship+0x84]
          0x15cc5 xor edx,edx; call 0x49f28  ; t211 DISPATCHER, mode edx=0
          0x15cd0 test byte [eax+0x84],1 -> RET (0x15d25 ecx=-1 path)
  site 2: 0x15d8f/0x15d95 mov al,[esp] -> 0x15d98 mov [edx+0x62],al ->
          identical packed write-through -> 0x15df0 call 0x49f28 ->
          0x15dfb test byte [eax+0x84],8 -> 0x15e7c tail
          (0x15e7c: [ebp+0xb9]=1; call 0x16cf0; [ebp+0xb0]=0)

=> t211's "UI/setup family (0x15bd0-family)" label is SUPERSEDED: these are
the ORDER-SETTER sites that stamp phase+target+params into the ship record and
immediately run 0x49f28 in the same edx=0 dry-run shape as the t210 volley
loop. Consumer-side (t206..t211) and producer-side (this) now meet.

## S3 — VALUE DOMAIN (reaching defs, measured; answer: NO value >=2)

SITE 1 phase := [esp+0x50]. The only byte-def of that local in the whole
9,553-byte function is 0x15c34 `mov byte [esp+0x50], bl` with bl=1 (0x15c2c),
inside an init block 0x15c14..0x15c34 that zeroes the packed order buffer band
([esp+0x5a],[5e],[0x62],[0x66],[0x6a],[0x6e] dwords := ecx=0) and then stamps
phase=1. Entry to that block: 0x15bb8 `cmp bh,[ebp+0xab]` bh==3 AND
0x15bc1/0x15bc9 on the order arg [esp+0x84] (==0 -> skip order entirely via
0x15bcb->0x15cdb; !=0 -> 0x15c14 init). The value switch at 0x15c4f
(`cmp al,3 / jb 0x15c5b / jbe 0x15bdd / cmp al,4 / je 0x15c00 / else 0x15c63`)
lives AFTER the init block and its arms write ONLY the day byte
[esp+0x55] and [esp+0x56] (bl=1 at 0x15bd0; xor bl,bl -> 0 at 0x15be5/0x15bf4;
mov ah,2 -> 2 at 0x15c08) — never [esp+0x50].
=> PHASE AT SITE 1 == 1 on every path that reaches the store. No >=2.
   (Caveat banked, NOT claimed: paths entering 0x15c63 from the arms are
   downstream of the init block, so no stale-[esp+0x50] path was found; the
   predicate check preds(0x15c38/0x15c14) is in probe C.)

SITE 2 phase := [esp+0x00] (byte 0 of a packed 0x22-byte order buffer at
[esp+0x00]). External in-edges into the cluster (probe B, whole function):
0x16329 jne 0x15e43 | 0x16378 jne 0x15e23 | 0x16391 jne 0x15d36 |
0x163df jmp 0x15d8f. The defs of [esp] byte and their fates:
  0x16361 `mov byte [esp], dl` with dl=2 (0x16359) — followed by
    0x1636a [ship+0x5d]=0; 0x1636e dh=[ebp+0xb0]; 0x16376 test dh,dh;
    0x16378 jne 0x15e23 ; FALLTHROUGH (dh==0) 0x16385 `mov byte [esp], dh`
    == 0 OVERWRITES the 2 before any path to the site. => the literal 2 never
    survives to 0x15d98 on this chain.
  0x15e23 `mov byte [esp],1` (dh!=0 branch) — then fills [esp+1]=[ebp+0xb1],
    [esp+5]=bh=0, [esp+6]=eax and `jmp 0x15e7c` = the TAIL, which does NOT
    contain the 0x62 store; so phase=1 via this def never reaches site 2.
  0x16385 dh==0 -> [esp]=0 -> 0x1638f cmp al,5 -> (al==5: 0x16397..0x163df
    jmp 0x15d8f writes [ship+0x5d]=7,[ship+0x5e]=0, fills params from ESI,
    NO [esp] byte write) | (al!=5: 0x15d36 `cmp al,dl` cluster: al==4 arm
    0x15d5d writes [ship+0x5d]=1 / else no [ship+0x5d] write) -> 0x15d8f.
=> PHASE AT SITE 2 == 0 on every measured path (the ORDER-CLEAR case:
   dh==[ebp+0xb0]==0). No >=2, and the site-2 chain is a cancel/clear commit
   ([ship+0x5d] cleared/set, day byte from dl/dh, then 0x49f28 dry-run).

## S4 — ENTRY MECHANISM OF 0x156d4 (indirect; table dword at file 0x88408 = RAM 0x488408)

ZERO E8 callers AND zero direct jmp/rel8 into 0x156d4..0x156f4 anywhere in
0x14bb0..0x82bb0 (scanner validated above). The ONLY image dword == 0x156d4 is
file 0x88408, inside a table of code addresses:
  0x88400: 0x15630 | 0x88404: 0x30d08 | 0x88408: 0x156d4 | 0x8840c: 0x16420
preceded by the magic pair 0x3c8efa35/0x42652ee1 (recurs at 0x88424/0x88438 —
entry-array shape) and just after the assert string tail `ted" function!`.
docs/re/r1-savestate.md:393 (OQ-010 batch 1) had already Ghidra-classified
0x156d4 as a batmode/batcon E1 function (battle-mode UI / window-message
dispatch) — consistent. The al-form commits are therefore RUNTIME-DISPATCHED
handlers [inferred: registration present, dispatcher-read not measured]; the
VALUE verdict below is caller-independent (intra-function), so it does not
depend on resolving the dispatcher.

## S5 — SOUNDNESS CLOSURE (probes C/D/E: every value claim now dominance-checked)

(C2) EXHAUSTIVE byte-defs of the two phase locals over the whole
2,673-insn region: [esp+0x50] has exactly ONE byte-def 0x15c34; [esp] byte has
defs 0x15e23 (const 1), 0x16361 (dl=2 from 0x16359), 0x16385 (dh=[ebp+0xb0]),
0x16e8b (xor ah,ah — inside SEPARATE function 0x16e4c, own frame; probe B
edge-census shows zero branches from the 0x16e40s into the site-2 cluster, so
irrelevant to 0x15d98).

SITE 1 (r213_probe_e.py reachability): cutting 0x15c14 (the bl=1 init block)
from the CFG makes 0x15c6d UNREACHABLE from the entry (reachable blocks
641 -> 564; 0x15c6d is in the lost set). In-edges confirm single-entry:
0x15c14 <- {0x15bc9} (bh==[ebp+0xab]==3 AND byte [esp+0x84]!=0), block
0x15c14..0x15c34 is straight-line with bl=1 at 0x15c2c, and the store
0x15c34 has a single pred 0x15c31. All seven in-edges of the rejoin 0x15c63
originate downstream of the init block.
=> PHASE AT 0x15c6d == 1 ON EVERY EXECUTION. [verified, dominance-checked]
   The day/stamp companion byte [esp+0x55] -> [ship+0x67] carries the order
   arg al=[esp+0x84] code: 5 (bh default, 0x15c3e/0x15c4b), 1 (al==2 arm
   0x15bd0), 0 (al==3 cancel, matched 0x15be5 or mismatch 0x15bf4), 2 (al==4
   match 0x15c08); target [ship+0x63] = [ebp+0xb1] via [esp+0x51] (0x15c40).

SITE 2 (probes B+D): in-edges of the whole cluster [0x15d36,0x15e7c) are
EXACTLY {0x16329->0x15e43, 0x16378->0x15e23, 0x16391->0x15d36, 0x163df->0x15d8f}.
0x15e43 block is dead-ended (0x15e46 jne 0x15e7c tail; 0x15e61 arm also to
tail) — never reaches the store. 0x15e23 sets [esp]=1 but `jmp 0x15e7c` TAIL
(0x15e7c: [ebp+0xb9]=1; call 0x16cf0; [ebp+0xb0]=0; call [ebx+0xc] vtable;
ret) — never reaches 0x15d98. The two live chains into 0x15d8f
({0x15d57,0x15d5b,0x15d8c} via 0x15d36<-0x16391, and 0x163df straight-line)
are BOTH downstream of 0x16385 `mov byte [esp], dh` where dh = [ebp+0xb0] AND
the gate 0x16376 `test dh,dh` took the ZERO side (jne went to 0x15e23/tail).
The dl=2 def at 0x16361 is straight-line-overwritten by 0x16385 on that side.
=> PHASE AT 0x15d98 == 0 ON EVERY EXECUTION. [verified, dominance-checked]

## S6 — VERDICT ON THE t211 RESIDUE (THE TASK (b) ANSWER)

CLOSED AS A MEASURED NEGATIVE: the al-form family 0x15c6d/0x15d98 is NOT a
source of phase values >= 2, and t211's "UI/setup family" label is SUPERSEDED
by "batcon order-commit sites": site 1 (order arg != 0, [ebp+0xab]==3) stamps
phase=1 + target + day-code into the ship record and runs 0x49f28 edx=0;
site 2 ([ebp+0xb0]==0 clear branch) stamps phase=0 and runs 0x49f28 edx=0.
Combined with t211 S4 (constant writers {0,1}: 9 ==1 + 6 ==0 sites) this is
the complete static writer population of [ship+0x62], every member producing 0
or 1 — matching the observed never-firing cl>=2 arm at 0x49f28 (t211 S2) and
requiring NO >=2 model in the rewrite. The al==2 order arg's day-code 1 is the
value t211 mis-saw as phase-reachable: it lives in [ship+0x67], not +0x62.
0x42211/0x43188 remain alignment-suspect (t108), excluded not refuted.

## S7 — TASK (a): STATIC EXHAUSTION, HONEST STATEMENT

t212 closed the OQ-021 write-site static route (score.md S9: three controlled
instruments, zero writer; aicode P7 refuted). t213 closes the last residue
explicitly named by a prior STATE block (t211 fallback al-form). Remaining
open-row residues are ALL play-gated (OQ-021 comparator firing + mid-campaign
V/[star+0x15] witness; OQ-016 multi-volley clamp witnesses) or BLOCKED-USER
(OQ-019 per-ship model conversion; OQ-005 player index.txt ruling) or
watchpoint-class (OQ-021 writer via dosbox-x). The static corpus is formally
EXHAUSTED: any further static pass re-runs a censused instrument without new
inputs, which t212's pitfalls (re-hit at 8,961 insns) show is net-negative.
