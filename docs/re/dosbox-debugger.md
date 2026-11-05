# dosbox-x debugger: what it can do, what OUR build can do, and what it takes to unblock

Authored 2026-11-02 (pairing session) after the user supplied two references. This
exists so no future session re-derives the command set or re-concludes "no
watchpoints exist" from our Debian binary alone (t272 did exactly that, correctly
for our binary, but the conclusion does NOT generalize).

## SOURCES (fetched verbatim 2026-11-02)
- https://github.com/joncampbell123/dosbox-x/blob/master/README.debugger
  (master; last commit to this file 2026-10-14, 54602ee "Merge upstream STEPIN
  and retain standalone MEMREAD")
- https://www.vogons.org/viewtopic.php?t=3944 — "Guide to the DOSBox debugger"
  (Fizzban, 2004, edited 3x; reply 1 by jal 2015-12-26 pastes the 0.74 help set)

## THE INSTRUMENT WE WANT (OQ-021 DAT_482fb writer) — [verified from README]
| command | meaning |
|---|---|
| `BPPM <seg> <off>` | add memory-CHANGE breakpoint, protected mode |
| `BPLM <offset>` | memory-CHANGE breakpoint at a LINEAR/virtual address |
| `BPM <seg> <off>` | memory-change breakpoint (real mode per README; "protected mode" per VOGONS 0.74 paste — sources disagree on wording, same intent) |
| `BP <seg> <off>` | code breakpoint (real mode) |
| `BPLIST` / `BPDEL <n>` | list / delete (VOGONS: `BPDEL *` deletes all) |
| `RUN` / `RUNWATCH` | resume / resume while showing state while running |
| `MEMDUMPBIN <seg>:<off> <count> [file]` | dump RAM to a binary file |
| `LOG/LOGS/LOGL/LOGC <n>` | write a CPU log (n instructions) to LOGCPU.TXT |
| `HEAVYLOG` | keep a 20000-instruction ring; dump on crash or INT CD |
| `SR <reg> <value>` | set a register (also the answer to "set EIP") |
| `SM <seg> <off> <bytes>` / `SMV <off> <bytes>` | set memory (linear variant) |
| `IV <seg> <off> <name>` | name an address; disassembler annotates refs to it |
| `CPU`, `GDT`, `LDT`, `IDT`, `PAGING [page]`, `SELINFO <n>` | machine state dumps |

Our target address is guest-LINEAR (data-segment image base + 0x82bb0 + 0x482fb -
0x88 per the pointer law, score.md S9/S14), so **`BPLM` is the natural command**;
`BPPM` is the fallback if a selector:offset form is needed (GDT/SELINFO give the
data selector).

## BUILD GATING — this is the whole story for us [verified from both sources]
- The debugger exists only in builds configured `--enable-debug` (README: "In
  builds where it is enabled"; VOGONS §1: `./configure --enable-debug`).
- The MEMORY breakpoints are additionally `C_HEAVY_DEBUG`-only. VOGONS §1:
  `./configure --enable-debug=heavy` gives "Memory breakpoints that activates
  when the value of a memory location is changed", plus CPU log + heavylog.
  README command list lists `BPM/BPPM/BPLM/HEAVYLOG` in the same table whose
  intro warns "Commands behind build options, such as C_HEAVY_DEBUG-only
  commands, may be unavailable in some builds."
- VOGONS §1 also: heavydebug breakpoints do NOT use INT 3, so an in-game
  anti-debug cannot strip them ("if you want to use breakpoints, heavydebug is
  the better choice").
- VOGONS BPM pitfall: "The new breakpoint will assume that the given location
  currently has the value 0x00" -> expect ONE spurious "memory has changed from
  00 to ??" fire on the first resume. Do not treat that as the writer.
- VOGONS performance pitfall (Qbix, reply 14): with the recompiler core, single
  steps skip instructions (stepping a NOP landed 26 bytes later). Fix: **set the
  core to `normal`** for any stepping/watchpoint work. Same caveat applies to
  watchpoint fidelity and is the reason a watchpoint session will be SLOW.
- Debugger activation: mapper shortcut, normally **Alt+Pause** (Mac Alt+F12).
  On Linux the debugger needs dosbox-x **started from a terminal** (ncurses UI);
  Windows can pop a console. `-break-start` breaks in at startup.

## SCRIPTABLE CONTROL — master only, NOT in our binary [verified]
README.debugger "Debugger MCP control protocol": with the debugger enabled,
`[dosbox] mcp_server=<port>` makes DOSBox-X connect OUT to 127.0.0.1:<port>
where an external server listens (companion project
https://github.com/caiiiycuk/dosbox-x-mcp-server). Wire format is line text,
not JSON:
```
REQ <id> PING            -> BEGIN <id> OK / PONG / END <id>
REQ <id> BREAK           -> enter the debugger
REQ <id> EXEC <command>  -> run ONE debugger command through the same parser
```
`STEPIN` (one guest instruction, response AFTER the step, reports
`CS:IP/AX/BX/CX/DX`) and `MEMREAD <seg>:<off> <len>` (1-256 bytes, real-mode
conventional RAM only, refuses partial reads so a returned 00 is a real zero)
are the two standalone commands retained for external control. Resume commands
(RUN/RUNWATCH/VRT) are ACKed on ACCEPTANCE, not on post-resume state — a
watchpoint flow must BREAK again (or rely on the breakpoint's own stop) to read
registers. Paged commands (HELP/GDT/LDT/IDT) are captured without hanging on the
pager. Unknown commands return ERR with the "command not recognized" text.

WHY THIS MATTERS MORE THAN THE WATCHPOINT ALONE: our entire harness is
no-display (background shells, xsend, DISPLAY=:9). An ncurses debugger is
awkward there; a TCP control channel is native to it. That converts "watchpoint
session" from manual keystroke theatre into a scriptable capture: BREAK -> BPLM
-> RUNWATCH -> stop-on-write -> dump CS:IP + registers -> map to the t106/t107
windowed disasm.

MEASURED BY US: `strings /usr/bin/dosbox-x | grep -i mcp_server` -> **no hits**,
and t272 (commit 84ca40a) measured our build as debugger-free outright (zero
bpm/breakpoint strings at -n2, no DEBUGBOX shell, no GUI Debug menu). Installed
package is `dosbox-x 2025.02.01+dfsg-3` (Debian trixie). So MCP + watchpoints
require a build; NOTHING we have today can do them.

## BUILD — EXECUTED 2026-11-02 (route 2, upstream master; result: SUCCESS)
Route 1 (Debian source) was abandoned: sudo needs a password for build deps,
and 2025.02.01 predates the MCP protocol anyway. Route 2 executed sudo-free:
- clone: `git clone --depth 1 https://github.com/joncampbell123/dosbox-x.git`
  -> work/r1/dbx-build/dosbox-x-master (8 s, direct, no proxy vars needed)
- autotools staged from debs into work/r1/localprefix (autoconf 2.72, automake
  1.17, m4, libtool, libncurses-dev, libncurses6, libtinfo6). Debian bakes
  /usr/share paths into the scripts; our copies were repointed (aclocal line 68
  patched; M4/AUTOMAKE_LIBDIR/AUTOM4TE_CFG/PERL5LIB envs) — ALL captured in
  work/r1/localprefix/autotools.env.sh, `source` it. Also needed: real
  config.guess/config.sub copied into the repo root (the staged ones were
  dangling symlinks to /usr/share/misc).
- configure: `./configure --enable-debug=heavy --enable-sdl2` + CPPFLAGS/LDFLAGS
  pointing at the staged curses (system has only libncursesw.so.6 runtime; the
  probe wants -lcurses/-lncurses). config.h: `C_DEBUG 1` + `C_HEAVY_DEBUG 1`.
- `make -j3` RC=0 (~16 min, nice'd). Binary:
  work/r1/dbx-build/dosbox-x-master/src/dosbox-x (130 MB).
- STRINGS VERIFIED on the new binary: BPLM x3, BPPM x3, BPM x1, RUNWATCH x4,
  mcp_server x2 (the dfsg build: ZERO of every one). Copy to
  work/r1/bin/dosbox-x-dbg is queued (STATE t282); /usr/bin/dosbox-x untouched.
- NOT YET DONE at the time of that commit (t282/t283): live HELP capture via PTY
  (-break-start, ncurses console UI), scratch watchpoint session, live syntax
  confirmation. t282 CLOSED the first and third of those — see the two sections
  below; the scratch watchpoint session on OUR target address is t283.

## OPERATING RULES IF WE BUILD
- Install as a SEPARATE binary (e.g. work/r1/bin/dosbox-x-dbg). NEVER replace
  /usr/bin/dosbox-x: production :9 and the whole launch harness assume it.
- A watchpoint session runs on a SCRATCH game copy with its OWN ring dir
  (two-writer ring law, t266 — a second dosbox writing the same ring froze the
  game AND corrupted evidence).
- core=normal in the conf for watchpoint/stepping fidelity.
- Expect heavy slowdown; budget wall time accordingly, and never let the scratch
  session inherit production's TL or autosave slot range.
- First BPLM fire may be the 0x00-initialization artifact, not the writer.
- Production :9 stays untouched; the user's Oct-29 campaign save is the
  md5-verified backup (RESUME.GAM.user-oct29), never the live RESUME.GAM.

## LIVE VERIFICATION — t282, 2026-11-02 23:21-23:31 (the instrument WORKS)
Harness: `scripts/r1_t282_dbx_probe.py` (listener + pty + scratch mount, runbook
invariants in its docstring). Run dirs work/r1/t282-probe-20261102-{232113,
232519, 232655} with `mcp-transcript.txt` (raw protocol replies) + `pty.log`.
Scratch: work/r1/game-wp (`cp -a game/.` + extracted ascend00/ascend02 data),
OWN captures dir, private Xvfb (never :9), `core=normal`, `-time-limit`,
kill-by-recorded-PID in a `finally`.

### DIRECTION LAW — WE LISTEN, DOSBOX-X CONNECTS OUT
`mcp_server=<port>` does NOT make dosbox-x listen. debug_mcp.cpp
`CONTROL_HOST = "127.0.0.1"` + `SDLNet_ResolveHost`/`SDLNet_TCP_Open` = the
EMULATOR dials US and retries every 1000 ms while we are down. MEASURED: the
channel connected 0.2 s after spawn, before the game drew a frame (DEBUG_Init
runs in SDL's init list, sdlmain.cpp:9807; it is NOT gated on a tty, so the
socket works fully headless). The listener MUST be bound before the child starts.
Wire (line text, not JSON): `REQ <id> PING|BREAK|EXEC <cmd>` ->
`BEGIN <id> OK|ERR\n<lines>\nEND <id>`. The OK/ERR flag is ONLY in the BEGIN
header. `EXEC` output is captured from DEBUG_ShowMsg (debug_gui.cpp:786) and
paged content is suppressed while capturing (debug_gui.cpp:685/700), which is why
HELP returns all 79 lines instead of hanging on the pager.

### LIVE COMMAND LIST (captured from the running build, `EXEC HELP`, 79 lines,
### hdr=BEGIN 3 OK). Verbatim copy in the run's mcp-transcript.txt:
    BP     [segment]:[offset] - Set breakpoint.
    BPINT  [intNr] * / [ah] * / [ah] [al]  - Interrupt breakpoints.
    BPM    [segment]:[offset] - Set memory breakpoint (memory change).
    BPPM   [selector]:[offset]- Set pmode-memory breakpoint (memory change).
    BPLM   [linear address]   - Set linear memory breakpoint (memory change).
    BPLIST                    - List breakpoints.
    BPDEL  [bpNr] / *         - Delete breakpoint nr / all.
    C / D  [segment]:[offset] - Set code / data view address.
    DV [addr]                 - data view at linear (virtual) address
    DP [addr]                 - data view at physical address
    DOS MCBS / KERN / XMS / EMS / FNKEY ; BIOS MEM ; CALLBACKS
    INT [nr] / INTT [nr]      - Execute / trace into interrupt
    MEMREAD <seg>:<off> <len> - Read 1-256 conventional RAM bytes (external).
    STEPIN                    - Execute exactly one instruction, then stop.
    LOG [num] ; LOGS/LOGL/LOGC [num] ; HEAVYLOG ; ZEROPROTECT ; ADDLOG [msg]
    SR [reg] [value]          - Set register value(s).
    SM [seg]:[off] [val]..    - Set memory.        SMV [addr] [val].. (linear)
    FM [seg]:[off]            - Freeze memory value at address.
    EV [value...]             - Show register value(s).
    IV [seg]:[off] [name] ; SV/LV [filename]      - named addresses, var lists
    VRD                       - Redraw video.   VGA cmd ; PC98 cmd
    EMU MEM/MACHINE           - emulator memory or machine info
    MEMDUMP seg:off len [file] / MEMDUMPBIN seg:off len [file]
    MEMFIND [seg]:[off] [.].. ; MEMS [operator] [value]
    SELINFO [segName] ; INTVEC [filename] ; INTHAND [intNum]
    MMX / SSE [=t] [reg] [SET [val]]
    CPU ; FPU ; GDT ; LDT ; IDT ; PAGING [page] ; EXTEND
    TIMERIRQ ; TIME [time] ; DATE [date]
    VRT                       - Run, then enter debugger at next vertical retrace.
    IN[P|W|D] [port] ; OUT[P|W|D] [port] [data]
    HELP
KEYS (UI only, not over the wire): F5 run, F8 toggle printable, F9 breakpoint,
F10/F11 step over/into, ALT+D/E/S/X/B data view from DS:SI/ES:DI/SS:SP/DS:DX/ES:BX.
NOTE vs README.debugger: this master build's live list has NO separate
`RUN`/`RUNWATCH` HELP entry (they are accepted by the parser —
`EXEC RUN` returned `BEGIN 15 OK / OK` — and debug.cpp:5462 synthesises them
internally), yet `RUNWATCH` is present in the binary's strings. Do not conclude
either way from strings alone; the parser is the authority.

### MEMORY-BREAKPOINT ACCEPTANCE — ALL THREE FORMS, MEASURED
    EXEC BPLM 00FA0000 -> "DEBUG: Set linear memory breakpoint at 00FA0000"
                          BPLIST: "00. BPLM 00FA0000 (00)"
    EXEC BPPM 0040:0000 -> "Set prot-mode memory breakpoint at 0040:00000000"
                          BPLIST: "01. BPPM 0040:00000000 (00)"
    EXEC BPM  0040:0010 -> "Set memory breakpoint at 0040:0010"
                          BPLIST: "00. BPMEM 0040:0010 (00)"   <- list spells BPMEM
    EXEC BPDEL *        -> "DEBUG: Breakpoints deleted."  (BPLIST back to empty)
This SUPERSEDES t272's "no watchpoints on this box" with a live demonstration.
The `(00)` in BPLIST is the ARMED BASELINE (AddMemBreakpoint stores value 0;
BPLIST prints bp->GetValue(), debug.cpp:1048). The fire test is
`bp->GetValue() != current` (:870) -> a nonzero-valued location fires ONCE
spuriously the instant it is armed. THAT IS THE VOGONS 0x00 ARTIFACT, now traced
to its cause. t283 must read the `NN -> MM` pair and reject `00 -> xx`.

### FIRE PATH — MEASURED FIRED, 2.1 s (run -232655, --fire)
Chosen sanity target: guest PHYSICAL 0x46C, the BIOS 32-bit tick counter — the
cheapest guaranteed-changing address in the machine (~18.2 Hz). BPLM's operand is
used directly as a physical/linear Bitu (`address = bp->GetOffset()`,
debug.cpp:864) so no selector arithmetic is needed.
    EXEC BPLM 0000046C  -> armed "00. BPLM 0000046C (00)"
    EXEC RUN            -> "BEGIN 15 OK / OK"  (ACK on ACCEPTANCE, no state)
    +2.1 s, EXEC BPLIST -> "00. BPLM 0000046C (69)"   <- baseline re-armed to 0x69
    pty.log line: "DEBUG: Memory breakpoint : 0000:046C - 00 -> 69"
So: the watchpoint fires, the CPU stops, and the stopped debugger still answers
over TCP (ControlServer_Poll is pumped INSIDE DEBUG_Loop, debug.cpp:5267). That
is the whole t283 flow: BPLM -> RUN -> fire stops the CPU -> read registers /
MEMDUMP / disasm context over the SAME socket.
FIRE-LINE PITFALL: the format is
`"DEBUG: Memory breakpoint %s: %04X:%04X - %02X -> %02X"` where %s is "(Prot)"
ONLY for BPPM — a BPLM fire prints an EMPTY type tag and seg `0000` (BPLM stores
seg=0), so the printed address is USELESS for BPLM. Identify a fire by the value
pair and by having exactly one breakpoint armed. GRANULARITY: one byte
(`mem_readb_checked`), checked on every instruction in every core
(DEBUG_HeavyIsBreakpoint from core_normal.cpp:182, core_dyn_x86.cpp:466, ...) —
hence core=normal and the wall-clock cost.

### BREAK IS INTERMITTENTLY FATAL — 1 of 2 attempts ABORTED THE EMULATOR
Run -232519 (same conf, --fire added): PING answered PONG, then `REQ 2 BREAK`
and the process DIED with glibc **`corrupted double-linked list`** (last line of
that run's pty.log; the socket then EPIPE'd). Run -232113 sent BREAK at the same
+0.2 s and survived, so this is NOT a timing law. BREAK is the only path that
allocates the ncurses UI (`DEBUG_EnableDebugger` -> `DEBUG_Enable_Handler` ->
`DEBUG_SetupConsole` -> `DBGUI_StartUp` -> `initscr()` on our pty,
debug_gui.cpp:612). Mechanism NOT proven — do not cite one. MITIGATIONS, in
order tried: (a) `--settle 40` before BREAK (worked, runs -232655 and -232655's
successor); (b) skip BREAK and drive EXEC only — NOTE this is NOT sufficient for
t283, because without BREAK the CPU never stops and a fire has nowhere to land;
(c) keystroke-driven ncurses on the pty. t283 MUST confirm BREAK survived
(BPLIST answers, and the fire line appears) before trusting anything it reads.
tty GATE (why the pty exists at all): debug.cpp:5410
`if (!isatty(0)||!isatty(1)||!isatty(2)) { LOG_MSG("Debugger is not available
unless you start DOSBox-X from a terminal"); return; }`. A pty satisfies it;
`-nogui` does not remove it; the MCP EXEC parser is NOT gated by it.
GOAL.txt's "do not pilot -break-start" was RESPECTED — no -break-start anywhere.

REPRODUCIBILITY: the fire test run twice more with `--settle 40` and fired BOTH
times at +2.1 s (00 -> 69 in run -232655, 00 -> 94 in the --disp 93 rerun; the
value is the tick count, so it differs by wall-clock). BREAK survived both.
Status: ACCEPTED 3/3, FIRED 2/2 with settle, BREAK aborted 1/2 without settle.
The instrument is real. t283 is unblocked.

## t286 GENERAL INSTRUMENT — scripts/r1_wp_session.py (ACCEPTED, positive control rc=0)
Scripted hunt harness (targets data:OFF / lin:ADDR / heap-planets /
heap-planets-blind; phases quiet,c,turn,planets,reopen; --walk N per-fire
EIP; --expect-base determinism guard; blind target + --break-early).
Positive control run work/r1/wp-lin-0x46C-20261103-080919: title BREAK ->
arm BPLM 0000046C -> RUN -> boot fires drained -> campaign ENTER -> quiet
phase fire +2.0 s -> registers banked, rc=0. LAWS (all measured, 11 runs):
1. BPLM SURVIVES save-state restore + campaign load: a bp armed at the title
   screen fires post-load. t283's post-load re-arm was a workaround, not a
   law. Paging off at fire (cr0=10, cr3=0) => linear==physical.
2. BREAK survival is a per-attempt LOTTERY at any screen (title died run 9,
   lived 10/11; post-load lived 1,4 died 3,5,6,7 — all with 45 s settle).
   SOP = relaunch loop until 'armed:' in the session log. The tell of a
   lethal BREAK: REQ n BREAK echoed in pty, then stream ends, socket EPIPE.
3. --no-break is DEAD: EXEC BPLM arms and BPLIST lists it without BREAK, the
   watched event genuinely happens (ring-captured), ZERO fire lines. The
   fire path requires the BREAK-enabled debugger (t282 claim confirmed by
   negative arm).
4. Early-armed fires print with a '(Running)' prefix on the pty; FIRE_RE
   still matches. MEMDUMPBIN at title-arm returns hdr OK but NO file =>
   byte-at-arm unknown in break-early mode (artifact rejection off; drain
   boot fires instead).
5. Clicks are verified by ring/screen evidence, never xsend rc (a click 1 s
   after the ENTER reaction can be swallowed mid-load; retry loop until the
   target signature appears). Sidebar sidebar buttons DRILL IN (list ->
   planet detail), they are not open/close toggles; a 'reopen' must click a
   neutral starmap spot first.
6. Deterministic heap: the planet-list object's RING-MEMBER index lands at
   0xfda074 in EVERY session at base 0x1bf4d8 (4 independent sightings),
   i.e. guest-LINEAR 0xfd9fec (off-by-H: linear == member - 0x88; t286b
   correction — t286's "linear 0xfda074" mislabelled a member index and
   every t286 heap arm sat 0x88 too high); the loaded campaign carries NO
   sig object; ring slots 57/59 of run 10 captured the
   reset(count=0,stamp 0xe) -> refill(count=80,stamp 0x8d) transition live.
7. FIRE-TIMING: the store does NOT stop the CPU; the heavy check fires at the
   first LATER memory access to the watched byte and prints the post-store
   value (2 witnesses: t283 store 0x243a8/fire 0x243b3; t286b store
   0x32eb6/fire 0x32ecf). The reported EIP may be a READER — identify the
   writer as the last storing instruction BEFORE the reported EIP that
   touches the watched offset.
RESOLVED t286b (was the OPEN PUZZLE above): run 10's zero-fires were the
off-by-H bug of law 6 — it armed linear 0xfda93b = member 0xfda9c3, a byte
that is 0 in all 20 of run 10's own ring slots (dead). With the corrected
blind arm 0xfda8b3, attempt 1 of the re-probe FIRED '00 -> 01' 2 s after the
Planets-button click; writer = the list-add increment at file 0x32eb6
(FUN_00032d1c), matching t249's static census. BPLM blind-heap arms are
RELIABLE on this build. Full account: docs/re/_wip_t286b.md.

## t286b BLIND-HEAP WATCHPOINT POSITIVE — THE PLANET-LIST WRITER IS WITNESSED
work/r1/wp-heap-planets-blind-20261103-114454 rc=0, first armed attempt
(scripts/r286b_relaunch.sh wraps the BREAK lottery). Arm BPLM 00FDA8B3 at the
title screen (blind, --expect-base 0x1bf4d8), RUN, enter campaign, reopen
phase: fire 'Memory breakpoint : 0000:FDA8B3 - 00 -> 01'. Stopped frame:
EIP 1f231f (= file 0x32ecf, a READ of [ebp+0x8c7] per law 7), ESP 2e8b94,
EBX 1 (the incremented count), pty operand panel names the watched byte
('ss:[00FDA8B3]=0001') and EBP 00FD9FEC (the object linear — law 6
self-confirming). Writer site FILE 0x32eb6:
`mov bx,[ebp+0x8c7]; inc ebx; mov [ebp+0x8c7],bx` — the generic scrollable-
list ADD (FUN_00032d1c), the t249 S1 static prediction verbatim.
CALLER CHAIN [inferred, honestly graded — see _wip_t286b S4]: populator
FUN_00051834 -> FUN_00055df4 -> FUN_00056e10 -> FUN_00056890 -> FUN_00056ca4
(vtable-slot-8 call `mov esi,[eax+0xa7]; call [esi+0x8]` = the list-ADD
virtual) -> FUN_00032d1c. Evidence = stale-stack return-address-shaped words
(slot 54 predates the fire) + adjacent-call disasm; NOT a live unwind.
PRACTICAL LAWS: (1) ALWAYS convert member-index findings to linear (-0x88)
before BPLM — the silent-miss class this whole t286 thread was; (2) the ring
freezes at the LAST autosave before a fire (CPU stopped; no more saves), so
ring-based stack dumps around a fire are stale — bank registers via EV over
the socket instead; (3) a blind free-heap arm (byte 0 at arm) has no
baseline artifact and its first fire IS the first write.

## t302 CODE-BREAKPOINT MULTI-STOP PROTOCOL (MEASURED, run
## work/r1/t299-leg-20261105-004605 + failures 225819/230846/232859/002628)
Under C_HEAVY_DEBUG a code BP (BP cmd) is NON-once and NOT 0xCC-patched
(debug.cpp CBreakpoint::Activate PHYSICAL path is `#if !C_HEAVY_DEBUG`), and
the heavy check runs at the TOP of the core loop (core_normal.cpp:182).
CONSEQUENCE (measured): resuming with the FIRED bp still armed re-stops at the
same EIP on the very next dispatch — the guest FREEZES (autosave cadence dies;
pty shows '(Running)' ACK then debugger prompt `I-> _`).
PROTOCOL (only viable form): on stop -> bank regs/dumps -> `EXEC BPDEL <idx>`
(BPLIST order != arm order; parse the index from the address line; BPDEL's
operand is HEX) -> `EXEC RUN` -> PROVE liveness (new .sav mtime within 40 s;
NEVER trust the RUN ACK — resume cmds answer on ACCEPTANCE, debug_mcp.cpp
ProcessControlCommand) -> BREAK (stopped re-arm window; lottery risk) ->
re-arm ONLY legs not yet witnessed -> RUN. Re-arming a HOT leg (one a periodic
msg hits — e.g. msg 0x3b pumps COSMOS slot 2 every ~1 s) re-freezes the guest.
FIRE DETECTION: this build's stop line is the DrawCode render `1E5F84 56 push
esi...` — bare 6-hex EIP (no CS prefix, unpadded), opcode glued to mnemonic,
run-on lines. Pattern that works: `(?<![0-9A-Fa-f])<6hex> [0-9A-F]` (kills
'BREAKPOINT AT 0160:1F0158' echo false-hits). The full-form pattern
`0160:001E5F84` NEVER matches — it hid three iterations of zero-fires.
NEVER pty-drain right after a RUN that could stop immediately: the drain
SWALLOWS the first fire line.
