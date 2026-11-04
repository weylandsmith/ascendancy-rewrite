# t282 WIP — debugger-build verification + live command capture

Started 2026-11-02 ~23:00. Source tree for all citations below:
work/r1/dbx-build/dosbox-x-master (upstream master, cloned 2026-11-02; the
build of THIS tree produced work/r1/bin/dosbox-x-dbg, md5 ebc6a785d95226d7997dd59b12dac55a).
Production binary /usr/bin/dosbox-x md5 15c49346539c155e4d0a7815f21e787c — DIFFERENT,
untouched.

## S1. BUILD GATES — VERIFIED PRESENT (assignment step 1)
config.h of the build tree:
  :43   `#define C_DEBUG 1`
  :115  `#define C_HEAVY_DEBUG 1`
  :172  `#define C_SDL2_NET 1`   <- required for the MCP control channel (see S3)
  :57   `/* #undef C_DOSBOX_AGENT */`  (agent path compiled out; irrelevant to us)
Binary: src/dosbox-x 130,962,440 B, `with debug_info, not stripped`.
strings -a -x exact-word counts on the copied binary (work/r1/bin/dosbox-x-dbg):
  BPLM 1   BPPM 1   RUNWATCH 1   mcp_server 1   (BPM 0 exact-word, 2 substring)
The STATE.md pairing note recorded "BPLM x3 / BPPM x3 / BPM x1 / RUNWATCH x4 /
mcp_server x2" — those are SUBSTRING counts on the build-dir binary; the
exact-word counts are lower because the help text and the ParseCommand literal
share words. Either way the point stands and is now re-measured: the dfsg
/usr/bin/dosbox-x has ZERO of every one of these (t272 + docs/re/dosbox-debugger.md).

## S2. THE HELP TEXT IS COMPILED, AND BPM/BPPM/BPLM ARE INSIDE THE HEAVY GUARD
src/debug/debug.cpp:4336 `if (command == "HELP" || command == "?")` prints the
live list via DEBUG_ShowMsg. The memory-change trio is emitted under
`#if C_HEAVY_DEBUG` (debug.cpp:4344-4348):
  BPM    [segment]:[offset] - Set memory breakpoint (memory change).
  BPPM   [selector]:[offset]- Set pmode-memory breakpoint (memory change).
  BPLM   [linear address]   - Set linear memory breakpoint (memory change).
So a live HELP capture proves heavy-debug commands are ACCEPTED, not just
present in .rodata. Note BPM's own help text says "[segment]:[offset]" — the
VOGONS "real vs protected mode" wording dispute resolves to the segmented form;
BPLM is the linear form we want (pointer law target is guest-linear).

## S3. MCP CONTROL CHANNEL — READ THE SOURCE BEFORE USING IT. IT IS A CLIENT.
THE SINGLE MOST IMPORTANT FINDING OF THIS ITERATION: dosbox-x does NOT listen
on the port. src/debug/debug_mcp.cpp:
  :30  `constexpr const char* CONTROL_HOST = "127.0.0.1";`
  :183 `SDLNet_ResolveHost(&address, CONTROL_HOST, g_port)` then
       `SDLNet_TCP_Open` — i.e. dosbox-x CONNECTS OUT to 127.0.0.1:<port> and
       RECONNECTS every 1000 ms while down (:32 RECONNECT_DELAY_MS, ThreadMain
       :371-386). WE must run the listener. (README.debugger's wording
       "connect OUT to 127.0.0.1:<port> where an external server listens" is
       correct and the companion project is the server.)
Lifecycle: config key `[dosbox] mcp_server=<port>` (dosbox.cpp:1773,
`OnlyAtStart`, min 0 max 65535, 0=disabled) -> DEBUG_Init() reads it
(debug.cpp:6240-6243) and does `ControlServer_Start(port)` +
`TIMER_AddTickHandler(ControlServer_Poll)`. DEBUG_Init is called from
SDLMAIN's init list (sdlmain.cpp:9807) — NOT gated on a tty, so the TCP channel
works headless even though the ncurses UI does not (see S4). ControlServer_Poll
is ALSO pumped inside DEBUG_Loop (debug.cpp:5267), so commands are serviced
whether the debugger UI is up or not.
Wire protocol (debug_mcp.cpp ParseControlRequest :442-513, SendResponse :515):
  request  `REQ <id> PING` / `REQ <id> BREAK` / `REQ <id> EXEC <command>`
           (only these three verbs; unknown -> ERR)
  response `BEGIN <id> OK|ERR\n<line>\n<line>...\nEND <id>`
  event    `BEGIN event OK\n<event> <data>\nEND event` (ControlServer_SendEvent)
  Output capture: EXEC runs under BeginCapture(); every DEBUG_ShowMsg line is
  routed to the capture ring (debug_gui.cpp:786 `DEBUG_MCP_CaptureMessage(buf)`)
  and flushed into the response. Paged content is SUPPRESSED while capturing
  (debug_gui.cpp:685/:700 early-return in DEBUG_Begin/EndPagedContent) — that is
  how HELP avoids hanging on the pager, so HELP comes back in full.
  Resume asymmetry (:126 IsResumeDebuggerCommand): RUN/RUNWATCH/VRT are answered
  `OK` on ACCEPTANCE and then executed (the emulation resumes) — the response
  carries NO post-resume state. A watchpoint flow must therefore BREAK again
  after the fire to read registers, or read the fire from the debug output.
  SanitizeProtocolLine (:100) replaces CR/LF inside payload/lines, so the
  framing cannot be corrupted by command text.
  MAX_CAPTURE_LINES 16384 (:36) with a "[N debug output lines discarded]" tail.

## S4. WHY THE PTY PATH IS THE WORSE INSTRUMENT (assignment suggested it; source says otherwise)
DEBUG_Enable_Handler (debug.cpp:5410-5425): on MACOSX/LINUX,
`if (!isatty(0) || !isatty(1) || !isatty(2)) { LOG_MSG("Debugger is not
available unless you start DOSBox-X from a terminal"); return; }` — so the
ncurses debugger needs a real tty, and the same isatty() gate disables the
mapper's debugger item (sdlmain.cpp:9806-9813). A PTY supplies a tty, so the
ncurses route is POSSIBLE, but it means driving a curses UI by keystrokes over a
pseudo-terminal while the game runs, and DEBUG_SetupConsole calls initscr() on
the same console (debug_gui.cpp:612) that our shell reads — screen-scrape
parsing of curses redraws. The MCP channel needs none of that and is
headless-native: one TCP accept loop, plain text in, plain text out.
DECISION: capture HELP live over MCP, not the PTY. The PTY stays as the fallback
if MCP fails. This is a deliberate deviation from the assignment's suggested
mechanism, on cited source grounds.
GOAL.txt standing decision "do not pilot dosbox-x -break-start" is RESPECTED —
no -break-start anywhere; BREAK is issued over the wire after boot. (R5's
reasons — EOF-spam from a piped stdin pilot — do not apply to the MCP BREAK,
which enters the same DEBUG_Enable_Handler from a tick handler.)

## S5. WATCHPOINT SEMANTICS READ FROM SOURCE (pre-loads t283, cheap to state now)
- BPLM handler debug.cpp:2835-2841: `CBreakpoint::AddMemBreakpoint(0,ofs)` then
  `SetType(BKPNT_MEMORY_LINEAR)`; prints "DEBUG: Set linear memory breakpoint at
  %08X". Always returns true (even if bp is null) — so a successful-looking
  response is NOT proof the breakpoint exists; BPLIST is the check.
- The check runs EVERY INSTRUCTION in the core loop:
  DEBUG_HeavyIsBreakpoint() (debug.cpp:6665) is called from core_normal.cpp:182,
  core_dyn_x86.cpp:466/541/558, core_dynrec.cpp:269..., core_prefetch, core_simple,
  core_full — confirming the heavy-debug slowdown warning and the reason
  `[cpu] core=normal` is mandatory (the dyn cores cache blocks and the VOGONS
  skip-instruction artifact).
- Code breakpoints are checked in the same function (:6713
  `CBreakpoint::CheckBreakpoint(SegValue(cs),reg_eip)`) — no INT 3 anywhere, so
  the game cannot strip our breakpoints (VOGONS claim, now source-corroborated).

## S6. LIVE CAPTURE — EXECUTED 2026-11-02 23:21, SUCCESS (assignment steps 1-3)
Harness: scripts/r1_t282_dbx_probe.py (new). Run dir
work/r1/t282-probe-20261102-232113/ (mcp-transcript.txt, pty.log 12 KB, wp.conf).
Scratch mount work/r1/game-wp (fresh `cp -a game/.` + extracted ascend00/ascend02
data — 148 MB), OWN captures dir, private Xvfb :96, core=normal,
mcp_server=55992, -time-limit 300, kill-by-recorded-PID in a finally block.
dosbox-x-dbg connected OUT to our listener 0.2 s after spawn (before the game
even drew a frame — the channel comes up in SDL init, debug.cpp:6240).

MEASURED, live from the running build (RC=0):
  PING   -> BEGIN 1 OK / PONG
  BREAK  -> BEGIN 2 OK, 1 line: "***| TYPE HELP (+ENTER) ..." (the debugger
            really entered — that banner is printed only by DEBUG_Enable_Handler)
  HELP   -> BEGIN 3 OK, 79 lines, NOT paged (the capture-suppresses-pager path
            debug_gui.cpp:685 works as read). First lines verbatim:
              BP     [segment]:[offset] - Set breakpoint.
              BPINT  [intNr] *          - Set interrupt breakpoint.
              BPM    [segment]:[offset] - Set memory breakpoint (memory change).
              BPPM   [selector]:[offset]- Set pmode-memory breakpoint (memory change).
              BPLM   [linear address]   - Set linear memory breakpoint (memory change).
              BPLIST                    - List breakpoints.
  BPLM 00FA0000 -> "DEBUG: Set linear memory breakpoint at 00FA0000";
            BPLIST then shows "00. BPLM 00FA0000 (00)"
  BPPM 0040:0000 -> "Set prot-mode memory breakpoint at 0040:00000000";
            BPLIST "01. BPPM 0040:00000000 (00)"
  BPM 0040:0010 -> "Set memory breakpoint at 0040:0010";
            BPLIST "00. BPMEM 0040:0010 (00)"   <- NOTE the list spells it BPMEM
  BPDEL * -> "DEBUG: Breakpoints deleted."; BPLIST back to header-only.
So t272's "no watchpoints on this box" is now SUPERSEDED WITH A LIVE DEMONSTRATION:
this binary accepts all three memory-CHANGE breakpoint forms over TCP.

THE "(00)" IS THE ARMED BASELINE, AND THAT IS THE VOGONS 0x00 ARTIFACT:
CBreakpoint::AddMemBreakpoint stores value 0 and BPLIST prints bp->GetValue()
(debug.cpp:1048-1049). The fire test is `bp->GetValue() != current` (:870), so a
location whose real value is nonzero fires spurious-once the instant it is armed
— exactly the VOGONS BPM note, now traced to its cause. t283 MUST read the fire
line's "NN -> MM" pair and reject `00 -> xx` as the artifact.

## S6b. INTERMITTENT CRASH AT BREAK — MEASURED, NOT YET EXPLAINED
Run work/r1/t282-probe-20261102-232519 (identical conf to the successful run
-232113 except port/display/--fire): the channel connected at +0.2 s, `REQ 1
PING` was answered PONG, then `REQ 2 BREAK` printed to the pty and the process
DIED with glibc **`corrupted double-linked list`** (last line of pty.log; socket
then EPIPE). The successful run -232113 ALSO sent BREAK ~0.2 s after connect and
survived. So this is NOT a timing law — it is an INTERMITTENT heap abort on the
MCP BREAK path, observed 1 of 2 attempts.
What the code does on BREAK (debug_mcp.cpp:560-575 -> DEBUG_EnableDebugger ->
DEBUG_Enable_Handler): sets exitLoop, enables the handler, and — because the pty
satisfies the isatty gate — calls DEBUG_SetupConsole -> DBGUI_StartUp ->
`initscr()` (debug_gui.cpp:612) on our pty, then allocates ncurses windows.
Heap corruption in that path plausibly involves ncurses' own terminal init
racing our drain thread or the capture ring, but I have NOT proven the mechanism
and will not claim one. MITIGATIONS TO TRY, in order: (a) settle before BREAK;
(b) if BREAK keeps aborting, keep the game RUNNING and drive the debugger purely
by EXEC (the parser itself is NOT tty-gated — BPLM/BPLIST worked in run 1 without
needing the CPU stopped) and accept that the CPU cannot stop, which would make
t283 impossible; (c) drive the ncurses UI by keystrokes on the pty instead of the
wire. Record which one worked before t283 commits to a design.

## S7. THE FIRE PATH — WHAT t283 WILL SEE (source, debug.cpp:850-882)
CheckMemoryBreakpoint for the three change-types: reads 1 BYTE at
  BPLM: address = bp->GetOffset()  (treated as a Guest PHYSICAL/LINEAR Bitu)
  BPPM: requires cpu.pmode + a valid GDT descriptor with limit != 0, then
        address = GetAddress(seg,off)
  BPM : address = GetAddress(seg,off)
On change: prints
  "DEBUG: Memory breakpoint %s: %04X:%04X - %02X -> %02X"
  (the %s is "(Prot)" ONLY for BPPM; for BPLM it prints EMPTY and the seg field
  prints 0000 because BPLM stored seg=0 — so A BPLM FIRE LOOKS LIKE
  "DEBUG: Memory breakpoint : 0000:000000 - 12 -> 13" and carries NO address!
  Identify the fire by the value pair + the fact you only have one breakpoint
  armed, not by the printed address.)
then bp->SetValue(value) and returns true -> the core returns debugCallback ->
DEBUG_EnableDebugger -> the CPU stops in DEBUG_Loop.
GRANULARITY LAW: the check is ONE BYTE (mem_readb_checked). Our target DAT_482fb
is read by the game as a u16 elsewhere; a write that changes only the HIGH byte
still fires (byte-level), which is what we want, but a fire tells us only that
THIS byte changed — a 16-bit store hitting both bytes fires once per instruction
check, not twice.
WHERE THE FIRE TEXT GOES: DEBUG_ShowMsg always writes the pty (and the MCP
capture ring ONLY while an EXEC is in flight). A fire during RUN therefore lands
in pty.log, NOT in an MCP response. But ControlServer_Poll is pumped INSIDE
DEBUG_Loop (debug.cpp:5267), so after the fire the channel is still live: send
EXEC BPLIST / EXEC "D ..." / EXEC CPU-style commands and read the stopped state.
That is the t283 flow: EXEC BPLM -> EXEC RUN -> (fire stops the CPU; pty.log
catches the fire line) -> EXEC BPLIST + register/data reads over the same socket.

## S8. FINAL VERDICT (t282 complete)
ACCEPTED 3/3 runs (HELP 79 lines live; BPLM/BPPM/BPM all armed, BPLIST confirms,
BPDEL * clears). FIRED 2/2 with --settle 40 (0x46C BIOS tick, +2.1 s,
"00 -> 69" / "00 -> 94"; CPU stopped; stopped debugger still answers EXEC).
BREAK aborted the emulator 1/2 without settle (glibc heap abort, mechanism NOT
proven). Permanent record: docs/re/dosbox-debugger.md (LIVE VERIFICATION +
verbatim HELP list); OQ-021 annotated (NOT closed — producer witness still zero);
REFUTED-ROUTES t272 + score.md S15 marked SUPERSEDED-as-to-the-general-claim
(dfsg-only now). New tools: scripts/r1_mcp_dbg.py (listener lib),
scripts/r1_t282_dbx_probe.py (bring-up + sweep + fire test). Scratch copy
work/r1/game-wp persists for t283. Production :9 untouched and HEALTHY
(pid 636955) after every run; no stray dosbox/Xvfb left.
