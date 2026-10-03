# STATE — machine-readable working memory for the loop
# Update EVERY turn. A fresh session must be able to resume from THIS file alone.

phase: P1
milestone: 1  # 0..6 ; gate.sh keys build/test stages off milestone >= 3
updated: 2026-10-03T09:55
turn_log_recent:
  - "seed: environment installed, cob.py extracts 468 files, Ghidra+MCP wired, plan written"
  - "crash: 2026-10-03T01:49 session 20261003_003843 died on 'Session DB append_message
     failed: database or disk is full' (ENOSPC). Everything between the seed commit and
     the crash was UNCOMMITTED and therefore lost - the only surviving artifacts are the
     two .logs files. Resume from the seed state; do not go looking for partial work."
  - "cause: .logs/dosbox_probe.log grew to 12.39 GB (720M lines, uniform
     'Are you sure to quit anyway now? / y/n:' echo loop — a dosbox-x autoquit prompt
     being spammed, zero research value). Deleted; head salvaged to
     .logs/dosbox_probe_salvaged.log. Frees 12 GB."
  - "P1b: scripts/table_probe.py written; docs/re/tables.md generated (deterministic,
     sha256 stable across reruns). .bin layout SOLVED (16B hdr + N x 24B / 6 x u32,
     exact 7/7). Seed's '.tsv = text form of .bin' claim FALSIFIED. OQ-001 CLOSED:
     offset table is N not N+1; fixed cob.py which had silently dropped each
     archive's last file (468 -> 471 extracted, existing 468 byte-identical)."

## CURRENT FOCUS
P1 data formats. .bin tables are done (docs/re/tables.md). The .tsv container
grammar and "which file does the exe load" are NOT resolvable from data alone —
they need Ghidra xrefs, so they are carried into P2 as OQ-004 rather than guessed.

## NEXT ACTION (exactly one)
P1c: write scripts/shp_probe.py for extracted/ascend01/data/*.shp (plus
ascend02/data/dkship*.shp, lgrace*.shp): header fields, record/frame encoding,
palette handling; render sample shapes to PNG under docs/assets/ and document in
docs/re/shp.md. Closes OQ-005. OQ-004 and P2's Ghidra import are deliberately
deferred behind this because P1c needs no binary RE; see PLAN ordering rule.

## KNOWN-ISSUES / PARKING LOT
- P2 BLOCKER (do not retry the old way): the Watcom LE payload at
  game/ascend.exe + 0x2a50 is NOT an importable object file. Ghidra 12.1.4
  auto-import picks 'Old-style DOS Executable (MZ)' and loads only 0x2a4e
  bytes, reporting "File contains 0x8cc85 extra bytes starting at file
  offset 0x2a4e" -> function_count 0. Verified: MZ+0x3c -> 0x2a50, 'LE'
  magic there, payload = 576,643 B (0x8cc83).
  The retry that failed asked for language x86:LE:32:default with compiler
  'watcom': CompilerSpecNotFoundException. VERIFIED — Ghidra 12.1.4 ships NO
  watcom cspec (find ~/tools/ghidra -iname '*watcom*' = empty). Valid
  compiler ids for x86:LE:32:default are exactly: windows, clangwindows, gcc,
  borlandcpp, borlanddelphi, golang. Pick one of THOSE. [unverified prior
  knowledge] Watcom is said to pass the first args in EAX/EDX/ECX (unlike gcc
  cdecl), so no shipped cspec models it correctly - verify empirically in P2.
  Start with 'gcc' for a clean disassembly and correct calling
  conventions per-function during P2. Approach: load the payload
  as raw binary at a chosen imagebase with language x86:LE:32:default +
  compiler 'gcc' (NOT watcom), or import the whole MZ and then create the
  overlay block covering 0x2a50..EOF.
- Ghidra headless is DOWN right now (127.0.0.1:8089 not listening; server log
  ends "Server stopped" at 07:44). Restart via scripts/ghidra_headless_up.sh
  before any mcp ghidra call.
- DOSBOX RULE (caused the crash): never launch dosbox with stdout/stderr
  redirected to a log file unless you have FIRST confirmed it will not sit at
  an interactive prompt. dosbox-x re-prints "You are currently running a
  program or game. / Are you sure to quit anyway now? / y/n:" forever when
  kill-signalled or fed EOF at a prompt, with no rate limit. Bound the log
  (e.g. `timeout 60 dosbox-x ... 2>&1 | head -c 1M`) or drive it over a pty
  and answer the prompt. Salvaged head shows the last probe reached real DOS
  execution (XMS/EMS/COMMAND.COM, INT15 BFDE warnings, videomode 69) before
  being quit — so the launch recipe itself roughly worked.
- dosbox audio: no sound device in this box; run dosbox with
  nosound=true for captures (visual only).
- resume.gam may be from a different version than the shipped exe —
  verify version bytes before trusting it as golden data.
- radare2 unavailable on Debian 13; do not waste turns looking for it.

## DEFINITION-OF-DONE (from goal contract)
See docs/PLAN.md P6 + goal contract. All P0-P6 items checked below.

## CHECKLIST
[P0] env verified
[x] P1a .cob format spec (docs/FINDINGS.md)
[~] P1b .tsv/.bin tables — .bin SPEC COMPLETE (docs/re/tables.md, 7/7 exact);
        .tsv characterised as binary string blobs, container grammar OPEN (OQ-004,
        needs Ghidra). Seed claim that .tsv = text .bin is falsified in FINDINGS 1b.
[ ] P1c .shp sprites
[ ] P1d .gam saves
[ ] P1e FLIC/audio inventory
[ ] P1f text encodings
[ ] P2 Ghidra subsystem specs (9 subsystems, docs/re/*.md)
[ ] P3 engine skeleton builds, importer verified, headless smoke test
[ ] P4 all systems ported with tests
[ ] P5 UI+media parity pass
[ ] P6 full campaign playable to victory; README
