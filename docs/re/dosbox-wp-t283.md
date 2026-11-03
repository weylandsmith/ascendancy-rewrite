# t283 — THE DAT_482fb PRODUCER, WITNESSED LIVE BY A WRITE WATCHPOINT

Hand-authored 2026-11-03 (t283 iteration). Nothing regenerates this file
(gate.sh regenerates only PLAYTHROUGH.md-type artifacts; see docs/BLOCKED.md).
Raw evidence: work/r1/t283-wp-20261103-{005402,010221,013603,014543}/
(session.log, pty.log, mcp-transcript.txt, stopped-state.txt, ring-final/).
Harness: scripts/r1_t283_wp_session.py (phase protocol + walk),
scripts/r1_t283_disasm.py (EIP -> payload-file disasm),
scripts/r1_t283_tailturn.py (no-sitting adjudication helper).

## 1. THE FIRES [verified]

Target address law (pointer law CLOSED, docs/re/r1-savestate.md): score slot
guest-linear = B - 0x88 + 0x82bb0 + 0x482fb, B scanned from the SESSION'S OWN
ring (r1_sav_scan anchors, 6 unanimous votes): B=0x1bf4d8 -> **0x28A2FB**
(== 0x242000 + 0x482fb, the law's own anchor arithmetic).

Run 6 (t283-wp-20261103-005402), armed `00. BPLM 0028A2FB (00)`, first fire
+3.3 s after the NEXTTURN press:

    LOG: DEBUG: Memory breakpoint : 0000:28A2FB - 00 -> 01

Run 7 (…-010221) phase protocol reproduced it EXCLUSIVELY in the `turn` phase:

| phase | input | 90 s | fire |
|---|---|---|---|
| quiet | none | yes | NO |
| c     | 'c' overlay x6 | yes | NO |
| turn  | NEXTTURN (511,67) | +3.1 s | YES `00 -> 01` |

Run 8 (…-013603) WALK (EXEC RUN after each fire, NEXTTURN between rounds):

    00->01  01->03  03->06  06->0B  0B->0C  0C->0F  0F->10  10->12  12->16  16->17
    = 0,1,3,6,11,12,15,16,16,18,22,23   (monotone INCREASING, terminal 23)

Run 9 (…-014700-region, same dir naming) repeated the walk WITH EIP AT EVERY
FIRE: fire EIPs 1e3803 (x7), 1e3844, 1e37c2 — all in ONE function body.

Non-artifact status: AddMemBreakpoint stores baseline 0 (debug.cpp:1048) and
the fire test is `bp->GetValue() != value` (:870), so a spurious first fire
needs the byte NONZERO at arm time. Ring read at scan time: score_stars=0
(runs 6,7,8,9 all) => the 00->xx first fire CANNOT be the artifact here.
Production corroboration (read-only): work/r1/playcap/save/51.sav also reads
score_stars=0 — the value is 0 at load/resume EVERYWHERE observed, and the
end-of-turn pass repopulates it. The displayed count is DERIVED state, not
saved state.

## 2. THE WRITER SITE [verified fire-anchored + static corroboration]

Fire EIP 1e3803 -> payload file 0x243B3 (EIP - (B-0x88)); the heavy-debug check
runs at the interpreter loop top (core_normal.h:181), so the fire EIP is the
instruction AFTER the store. The preceding instructions (objdump -b binary
-m i386 -M intel, work/ascend_payload.bin):

    2438e: 66 3b 15 8b 34 04 00   cmp    dx, WORD PTR ds:0x4348b   ; vs live ship count (r1_slot law)
    24395: 7c 1c                  jl     0x243b3
    24397: 66 c7 46 21 01 00      mov    WORD PTR [esi+0x21], 1
    2439d: 8b 8d eb 54 03 00      mov    ecx, DWORD PTR [ebp+0x354eb]   ; load counter
    243a3: 89 e8                  mov    eax, ebp                       ; EAX = base (254e10!)
    243a5: 41                     inc    ecx                            ; counter += 1
    243a6: 89 fa                  mov    edx, edi
    243a8: 89 8d eb 54 03 00      mov    DWORD PTR [ebp+0x354eb], ecx   ; store counter
    243ae: e8 c1 fe ff ff         call   0x24274                        ; -> FUN_00024274
    243b3: 8b 5c 24 04            mov    ebx, [esp+0x4]                 ; <<< FIRE EIP (x7)

ARITHMETIC ANCHOR [verified]: captured EAX=0x254e10 == 0x28A2FB - 0x354EB
exactly. So the counter variable at [base+0x354eb] IS the dword that the
watchpoint watched (ebp = the object base whose linear is 0x254e10;
0x28a2fb = ebp + 0x354eb). t212's census missed this because the store is
BASE-REGISTER+DISP — no static disp32/imm form exists for it, exactly the
"address COMPUTED at runtime" residue score.md S9 predicted.

Loop body (same function, file ~0x24340-0x243b3): `imul ecx,eax,0x162` +
`[ecx+0x3a0e9]` = ship-array stride 0x162 with the live count gate
`cmp dx, ds:0x4348b` (r1_slot.py law: live count = u32@0x43489>>16);
`imul ecx,ecx,0x1ee` + `cmp BYTE PTR [ecx+eax+0x12fd6], 3` = race-stride 0x1ee
(aicode.md §2) test for value 3; on match: mark `[esi+0x21]=1`, INC the
[ebp+0x354eb] counter, `call 0x24274`. Ghidra label: this region is aicode.md
P8's "FUN_00024274 / 0x24a34 events" tail of the 0x25xxx per-race command
chain; 0x24274 itself is `push ebx/ecx/esi/edi/ebp; sub esp,0xc` (a small
helper, first bytes verified 53 51 56 57 55 83 ec 0c).

WHAT THE WALK SEMANTICS SAY [verified shape, [inferred] mapping]: the value
walks monotonically UP within one end-of-turn pass and lands at 23 — the exact
banked corpus max (S6: max 23/50). Increments are 1,2,3,1,3,1,2,4,1 (mostly +1,
occasionally several): consistent with ONE increment per qualifying entity and
the monitor coalescing several stores per RUN slice (the debugger stops at the
FIRST instruction after a change, so a fire shows net old->new across a burst).
The predicate (what "qualifying" means: race-3-linked, ship-counted systems) is
NOT yet decoded — that is the next measurement, not this one.

## 3. CADENCE [verified]

Write happens ONLY in the end-of-turn path (NEXTTURN press -> fire +3.1-3.3 s;
quiet 90 s clean; 'c' overlay 90 s clean x6 presses). The t189b hypothesis
"recomputes when the overlay opens" is REFUTED. Production consequence: idle
sessions display 0 because no end-turn pass ever runs after load — which also
explains why watcher rows sampled between turns read the value mid-recompute
(the S6 oscillation is consistent with sampling a per-entity accumulation that
restarts every turn; full oscillation accounting stays OPEN, this is a shape,
not a formula).

## 4. OPERATIONAL LAWS BANKED (harness class)

1. BREAK after a campaign LOAD needs its OWN ~45 s settle: run 5's BREAK at
   load+0 s was RECEIVED (pty.log `[ControlClient] mcp command REQ 2 BREAK`)
   but never answered (no glibc error — a silent stall, distinct from t282's
   crash shape). 45 s post-load settle: BEGIN-OK first try, runs 6,7,8,9.
2. `-savedir` does NOT mkdir; autosave then logs "Failed to save the current
   state." and the SDL window VANISHES from the X tree while the emulator is
   alive. Pre-create the dir.
3. `--disp 97` (no colon) as DISPLAY makes X treat "97" as a HOSTNAME: empty
   xwininfo -> false "window gone". Always `:97`.
4. System python3 has NO PIL (the Hermes venv does). Pixel-diff via
   ImageMagick `compare -metric AE` (verified: landed click 306716, identical 0).
5. MEMDUMPBIN with a filename tail over the MCP EXEC channel returns
   "Invalid memory dump arguments" (both code+stack attempts, run 7). Do not
   re-guess syntax; the code/stack bytes are already on disk in the ring saves.
6. The BREAK reply's "Dynamic core" warning is printed UNCONDITIONALLY
   (DEBUG_WarnDynamic, debug.cpp:5350) — NOT evidence of the active core.
7. xsend's "(window died before release)" trailer is a cosmetic artifact of its
   own loop counter; verify delivery by screen diff, not by xsend output.
8. Fire EIP = instruction AFTER the store (loop-top check, core_normal.h:181);
   disassembly windows decode from the payload copy, never from a live dump.

## 5. LEDGER EFFECT

OQ-021 PRODUCER residue: CLOSED (witness x2 reproducible + walk + fire-anchored
store site + EAX arithmetic anchor). THRESHOLD residue: OPEN (this campaign
never reaches V>=25 at a sampled row; selector never armed in campaign lineage).
OQ-021 row overall: stays OPEN pending the threshold residue.
t284 (rewrite the V semantic in rewrite/src/game/score.cpp) is now unblocked:
mirror the cadence — value 0 at load, accumulate +1 per qualifying entity in
the end-of-turn pass, display the accumulator (0x482fb).
