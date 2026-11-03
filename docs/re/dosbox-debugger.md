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

## TWO BUILD ROUTES (not yet executed — needs the user's nod)
1. **Debian source, rebuilt with debug** — `apt-get source dosbox-x` (deb-src IS
   configured for trixie + trixie-security) then configure with debug+heavy.
   Gives: BPLM/BPPM watchpoints. Does NOT give: the MCP control protocol
   (master-only; our 2025.02.01 binary has no mcp_server strings).
   Pros: distro toolchain, known-good deps, smallest failure surface.
2. **Upstream master clone** — gives watchpoints AND MCP control.
   Cons: dependency drift vs the distro build, and every debugger command must
   be re-verified against the live build anyway (README: "call HELP for the
   live command list from the running DOSBox-X build").
Recommendation: route 1 first (unblocks OQ-021 with the least risk); route 2
only if we want the scripted control channel for broader RE automation.

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
