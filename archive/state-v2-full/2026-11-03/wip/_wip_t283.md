# WIP t283 — OQ-021 write-watchpoint session (started 2026-11-03 04:39Z)

## Pre-flight [measured this session]
- No new sitting: `scripts/r1_t283_tailturn.py` (new, tail-window parser) —
  playcap tail max turn **1086** == the t216..t242/t282 baseline turn; file
  growth 7,733,849,975 -> 7,734,015,882 B is idle watcher rows, not play.
  Sitting script correctly NOT run (t152 law).
- Production :9 HEALTHY pid 636955, TL expiry 2026-11-04 22:33, watcher 636970,
  ring 52.sav age 1s. Untouched all session.
- Instrument present: work/r1/bin/dosbox-x-dbg (t282); scratch work/r1/game-wp
  148M with ascend.exe. t282 harness scripts/r1_t282_dbx_probe.py reusable
  pieces (read_until_end/drain/kill_rec) imported, not forked.
- capstone is NOT installed in any python (system, /usr/bin, hermes venv) —
  post-fire disassembly uses `objdump -D -b i386 -M intel` against a slice of
  work/ascend_payload.bin (available: /usr/bin/objdump).

## Target address arithmetic [derived from CLOSED pointer law]
Law (docs/re/r1-savestate.md POINTER LAW, CLOSED 2026-10-05i): payload image
verbatim at guest-physical P0 = B - 0x88 (H=136), guest linear == physical;
obj1 (data) mem base = P0 + 0x82bb0.
  score slot linear = B - 0x88 + 0x82bb0 + 0x482fb
Production cross-check: B=0x1bf4d8 -> 0x28a2fb == 0x242000+0x482fb (law's own
anchors) — arithmetic self-consistent. THE RUN'S OWN B IS SCANNED FROM THE
SCRATCH RING (scripts/r1_sav_scan.py anchors, >=5 unanimous votes); production
B is NEVER used as the operand.

## Run 1 (t283-wp-20261103-001644) — harness negatives, TWO bugs, both fixed
1. SAVEDIR LAW (mine, violated): dosbox autosave slots land in the process CWD
   (`<run>/save`), NOT under `captures=` — the t282 run dirs show `save/` as a
   SIBLING of wp.conf. My `caps/save` scan path never existed -> campaign-wait
   could never see a slot. Fix: `-savedir <out>/save` (flag exists in
   dosbox-x-dbg --help, verified verbatim) + savedir = out/save.
2. CLICK-VERIFICATION LAW (re-learnt, t244/t245 class): xsend rc=0 + "sent
   button1" only proves SENT. Run 1 clicked (318,333) once at +40 s; screenshot
   40 s later STILL showed the title menu (vision-checked: Play Introduction /
   Tutorial / New Game / Return to Current Game / Load / Save / Exit — RTOGame
   HIGHLIGHTED, so the pointer position was right; the click just didn't land —
   dosbox may need focus, or the SDL2 event needed a warp+press gap). Fix:
   enter_campaign() loop: click -> grab -> PIL screen-diff (>2000 px = reacted),
   up to 25 attempts, re-baseline each round.
3. pty.log fire-line grep works (t282 file: line 259
   'DEBUG: Memory breakpoint : 0000:046C - 00 -> 69').
4. Local disasm recipe CONFIRMED on the known presenter read 0x28074:
   `objdump -D -b binary -m i386 -M intel --adjust-vma=<lo>` on a payload slice;
   --start/stop-address SILENTLY print nothing with -b binary (trap banked in
   scripts/r1_t283_disasm.py which marks the instruction CONTAINING the target).
   Test: eip=0x1e74c4 (production-B arithmetic) -> file 0x28074 ->
   `mov eax,ds:0x482fb` exact.
5. No stray processes after run 1 (kill-by-recorded-PID + Xvfb teardown held;
   only production Xvfb :9 remains).

## RUN 6 — t283-wp-20261103-005402 — **THE WATCHPOINT FIRED WITH A REAL VALUE**

Full flow GREEN end to end: connect OUT 0.2 s -> settle 45 -> resume click
(screen diff 306716 px = reacted) -> ring scan `B=0x1bf4d8` (6 votes,
score_stars=0) -> post-load settle 45 -> `BREAK` hdr=BEGIN 3 OK -> `EXEC BPLM
0028A2FB` accepted -> `00. BPLM 0028A2FB (00)` armed -> +3.3 s:

    (Running)LOG: DEBUG: Memory breakpoint : 0000:28A2FB - 00 -> 01

Non-artifact by the DERIVED artifact law (byte was 0 at arm time, so no
spurious fire is possible) — this is the first witnessed write of the displayed
count in the whole project. Stopped debugger answered EVERY read over the same
socket (BPLIST/CPU/EV x12/DV, all BEGIN..OK) -> stopped-state.txt banked:

    EIP=1e36c4  CS=160 DS=ES=SS=168  ESP=2e8a24
    EAX=254e10 EBX=1 ECX=0 EDX=256525 ESI=2555ce EDI=2c06c8 flags=202

EIP -> payload file offset (EIP - (B-0x88)) = **0x24274**, which scripts/
r1_t283_disasm.py resolves to `push ebx` — a FUNCTION PROLOGUE (`53 51 56 57 55
83 ec 0c`), preceded in file order by an unrelated loop + `nop` alignment pad.
So dosbox reported EIP as the NEXT instruction to execute (we are at a function
ENTRY, just after a `call`), and the writing store is therefore either in the
CALLER or the first store of this function. EBX=1 == the new byte value.

WHAT RUN 6 DOESN'T SETTLE (do not over-claim): which input caused the write
(run 6 fired the `c` overlay press AND the NEXTTURN click in the same poll
iteration, then fired at +3.3 s), and the caller identity. ESP=2e8a24 holds the
return address — unread, because run 6 predates the stack dump.

## Run-5/BREAK law (banked): BREAK after a campaign LOAD needs its OWN settle
Run 5 (t283-wp-20261103-005134): BREAK ~0 s after the load click was RECEIVED
(`[ControlClient] mcp command REQ 2 BREAK` in pty.log) but NO BEGIN header came
back in 25 s and no glibc error (grep 0) — a silent stall, NOT the t282 crash.
Run 6 with a 45 s POST-LOAD settle answered BEGIN-OK first try. Harness now:
PING liveness -> settle -> BREAK x3 (PING between) -> VRT fallback.

## Harness traps hit this iteration (all fixed in r1_t283_wp_session.py)
1. `-savedir` does not mkdir; autosave then logs "Failed to save the current
   state." and the SDL window vanishes from the X tree. Pre-create it.
2. `--disp 97` has NO colon; passing it raw as DISPLAY makes X treat "97" as a
   hostname -> empty xwininfo -> false "window gone" while the emulator is
   provably alive and saving. Helper `dspec()`.
3. System python3 has NO PIL (the Hermes venv does) -> a PIL pixel diff
   returned -1 forever. Use ImageMagick `compare -metric AE` (installed).
   Verified: landed click = 306716 px, identical = 0.
4. Autosave slots land in the dosbox CWD `save/`, NOT under `captures=`.
5. Poll 24 s before re-clicking the title menu (load takes seconds; a second
   click lands on the starmap's control grid).
6. Turn field is NOT u32 at 0x16143 (that read gave 0x320000 garbage);
   r1_slot.py is the authority for slot fields.

## RUN 7 — t283-wp-20261103-010221 — ATTRIBUTED: THE WRITE HAPPENS ON TURN ADVANCE

Phase protocol (`--phases quiet,c,turn --phase-wait 90`, one input kind per
phase, one armed BPLM, `EXEC RUN` between phases):

| phase | injected input | 90 s budget | fire? |
|---|---|---|---|
| quiet | none | 01:03:58->01:05:28 | NO |
| c     | `key c` x6 (State-of-Galaxy overlay) | 01:05:28->01:06:59 | NO |
| turn  | NEXTTURN click (511,67) | 01:06:59->01:07:02 | **YES +3.1 s** `0000:28A2FB - 00 -> 01` |

Same EIP as run 6: `EIP=1e36c4` (= payload file **0x24274**, a function
prologue `53 51 56 57 55 83 ec 0c`, Ghidra's `FUN_00024274` per aicode.md P8),
CS=0160 DS=ES=SS=0168 ESP=2e8a24, EBX=1, ECX=0, EAX=254e10 EDX=256525
ESI=2555ce EDI=2c06c8. Two INDEPENDENT FIRES, same address, same EIP, same
value 00 -> 01 => reproducible, not a one-off.

CONSEQUENCES (evidence-bounded):
1. The t189b "recomputes when the overlay opens" hypothesis is REFUTED for this
   build/campaign: 6 overlay toggles, zero writes.
2. The write is NOT spontaneous (quiet phase clean) — it is driven by the
   end-of-turn path, i.e. the t258 recompute-on-end-turn SHAPE.
3. `score_stars` at load is 0 in BOTH the scratch session (run 6/7 ring scan)
   and production (work/r1/playcap/save/51.sav, B=0x1bf4d8, score_stars=0 at
   turn 1086 — read-only). So the value is RECOMPUTED during a turn rather than
   being restored from the save: a resume starts at 0 and the writer repopulates.
   That is itself a finding (the displayed count is derived state, not saved state).
   CAVEAT: production's 51.sav is the newest slot of a session that has been
   idle since Nov-02; whether it is mid-turn or post-turn is NOT established.
4. Fire-to-fire is 3.1-3.3 s after the NEXTTURN press in both runs, and the
   value went 00 -> 01 (not to the campaign's ~21). So the first write of the
   turn is an INITIALISE/ACCUMULATE-START, consistent with a per-turn recompute
   loop that then walks up over subsequent writes. NOT YET MEASURED: the walk.

## MEMDUMPBIN over the wire is DEAD — read from the source, do not retry
`EXEC MEMDUMPBIN 0000:001E36C4 40 /abs/path` -> `DEBUG: Invalid memory dump
arguments.` Both attempts (code + stack) in run 7. Cause read in the build tree
(work/r1/dbx-build/dosbox-x-master, the exact tree the binary came from):
`ParseMemoryDumpArguments` (debug.cpp:2176) requires seg<=0xffff, a ':', an off
followed by a space, then a hex num — our string satisfies that shape, so the
failure is upstream in how EXEC hands the payload to `ParseCommand`
(debug_mcp.cpp:575 -> DEBUG_ExecuteCommand debug.cpp:4434 -> ParseCommand, which
`trim`s then re-splits; the filename tail is where it diverges). DO NOT burn
iterations re-guessing the syntax: the code+stack bytes are ALREADY ON DISK in
the ring saves (pointer law), so read them from `save/NN.sav` instead.

## BREAK warning text is NOT core evidence
The BREAK reply always carries "Warning: Single-stepping may not work correctly
with Dynamic core" — `DEBUG_WarnDynamic()` (debug.cpp:5350) prints it
unconditionally, so it does NOT prove the dyn core is in use. `core=normal` IS
in wp.conf (verified in the run dir).

## NEXT (run 8, same harness): the value WALK + the caller from the ring
After a fire, `EXEC RUN` repeatedly and log every fire line: 01 -> 02 -> 02 ->
03... would prove an accumulator loop and pin the cadence for t284. For the
caller, read the ring slot that covers the stop (autosave lands every 10 s;
newest post-fire slot) and pull the stack at ESP from the Memory member — no
MEMDUMPBIN needed.



