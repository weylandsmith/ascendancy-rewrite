# _wip_t272 — V-PRODUCER WRITE WATCHPOINT on scratch (user-granted)

Target: guest-phys = B + 0x82bb0 + 0x482fb - 0x88 (pointer law, score.md S9/S14)
for DAT_000482fb = the displayed score V. Instrument = dosbox-x debugger
memory-write breakpoint. Instrument facts are S1 below (measured this session,
do not re-derive).

## S1 — INSTRUMENT FACTS, dosbox-x 2025.02.01 SDL2 (/usr/bin/dosbox-x, stripped) [measured 2026-11-02]

1. THE PAIRING SESSION'S CENSUS WAS ON THE WRONG ARTIFACT, but its conclusion
   survives on better grounds. `strings -n 3/-n 4` finds ZERO occurrences of
   "breakpoint", "bpm", "bph", "bplist", "clrbp*", "dbgcon", "watchpoint",
   "Add breakpoint", "Break on write". Re-run at `-n 2` (the length that would
   actually catch a 3-char command name): `grep -Fx bpm|bph|clrbpm|bplist` =
   0 hits; `bp` = 6 hits, all inside .text/code byte noise, none in the
   .rodata string region (0x8b0000..0x901000 where every UI literal lives).
2. The debugger IS compiled in — the binary carries the DEBUGBOX shell command
   and the debugger prompt: `.rodata` 0x8ff819 "Enter Debugger Command";
   en_US.lng:53-54 `:DEBUGCMD` / "Enter Debugger Command";
   en_US.lng:2375-2382 `:SHELL_CMD_DEBUGBOX_HELP[_LONG]` ("Runs program and
   breaks into debugger at entry point", "DEBUGBOX [command] [options]",
   "Type DEBUGBOX without a parameter to start the debugger");
   `-break-start  Break into debugger at startup` at .rodata 0x8ccdf8 (the CLI
   usage block) + 0x8f5dfe (the switch-name table).
3. NEW KEY FOUND (the pairing session did not report this one):
   `[log] debuggerrun` — "The run mode when the DOSBox-X Debugger starts.
   Possible values: debugger, normal, watch." VERBATIM in the shipped
   /usr/share/dosbox-x/dosbox-x.reference.conf:109-116 (default
   `debuggerrun = debugger`), and the three modes are menu items in
   en_US.lng:3206-3213 (`debugger_rundebug` / `_runnormal` / `_runwatch`).
   So this build has a first-class "Run watch" debugger mode, selectable from
   the config file — i.e. NO keystrokes needed to enter the debugger, and the
   mode name "watch" is a candidate memory-watch facility.
4. No `language.txt`-style debug string table for debugger commands exists in
   the .lng files either (`grep -iE 'breakpoint|watchpoint' en_US.lng` = 0).
   Conclusion: debugger command HELP TEXT is not localised and the command
   verbs are not plaintext literals at the offsets searched — the only way to
   enumerate the command set is EMPIRICAL (task-sanctioned).

## S2 — DRIVE/READ TOOLING for a debugger session [measured]
(to fill: how to send keystrokes to the scratch window; how to read debugger
 output back — logfile vs screenshot+vision)

## S3 — RESOLUTION (this session completed; authoritative text is
docs/re/score.md S15 and docs/REFUTED-ROUTES.md "t272"). The debugger does not
exist in the installed build (no command set; DEBUGBOX shell internal absent;
no GUI Debug menu; -break-start ignored), so S2 was never needed. Keeper facts
that came out of the S2 work: xsend `key KEYSYM [ch]` (tools/xsend.c t244
modes) is the keyboard path if a debugger ever arrives; `import -window
0xWINID` beats root capture when the SDL window is offset; a title-screen boot
does NOT have the game image resident (scripts/r272_scratch_resident.py).
