# STATE — machine-readable working memory for the loop
# Update EVERY turn. A fresh session must be able to resume from THIS file alone.

phase: P3
milestone: 3  # 0..6 ; gate.sh keys build/test stages off milestone >= 3
updated: 2026-10-04T03:20
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
  - "P1c: scripts/shp_probe.py + docs/re/shp.md + gate stage 3c. .shp CONTAINER
     SOLVED 208/208 (magic 1.10; u32 N; table_size==8*(N+1); N+1 u64 slots where
     slots 0..N-2 are strictly-increasing record pointers, rec0 sits at table_end,
     last rec -> EOF; slots N-1/N are library metadata, never inside the data
     area). CODEC NOT SOLVED: 5 RLE grammars x hdr 4/8/12 x u16/u32 dims,
     exact-span discriminator, 12 smallest libs = 0 survivors (OQ-005 stays open).
     NO PNG renders - rendering with an unknown codec fabricates pixels.
     rec0 packs dims u32+u32 (198/208, 10 opaque); rec1+ packs u16+u16 (163/163)."
  - "LESSON (this turn, three caught-in-review errors): do not write an
     interpretation into docs/ without computing it. Wrong: 'cos_ship-style
     variant' (rec0/rec1 differ only in dim PACKING, not a third header);
     '0x7FFFFFBB = signed -4103' (it is positive as i32, 2147483579);
     'h lands on byte 4' (u16 h is at byte 2). Verify the number, then write
     the sentence. Also: read_file output carries LINE_NUM| prefixes - never
     write it back into source (that corrupted and deleted shp_probe.py earlier;
     it was untracked, git had no copy).

  - "P2 loader model (turn 2026-10-04b): Seed2.java bootstraps 269 functions
     (work/functions.tsv, gate stage 3h runs the probes). ABSOLUTE BASE C IS
     REFUTED STATICALLY by four scripted tests (vtable_base_test,
     ebx_relative_test — whose own first verdict I reversed with its spacing
     control, c0_anchor_test, high-imm->ASCII) — full story docs/re/loader.md.
     Data identities resolve at load time; only a RUNTIME base (R1 dosbox dump)
     can restore them. docs/BLOCKED.md poses the R1/R2 methodology question;
     working default = C hybrid, R2-priority. Gate 3h added; OQ-004/005/008/
     011 updated. Two self-caught API bugs recorded in loader.md footer
     (currentProgram is a FIELD; getBytes arg3 is an array offset -> silently
     zero-filled images). Ghidra java sources now tracked in scripts/ghidra/. (a) PROVED the LE payload is stored in file =
     memory order (scripts/le_contiguity_test.py: rel32 call targets resolve
     76:1 in-page and 135:1 inter-page vs a page-shuffled control), so a raw
     load at imagebase 0 is valid for control flow; absolute base C is STILL
     open (OQ-011) because the string-anchor vote is a density artefact.
     (b) Ghidra facts, all measured here: no LE loader (LinearExecutable.java
     = NotYetImplementedException stub); NO 'watcom' cspec; headless flag is
     -cspec, NOT -compiler (the earlier run died with 'Bad argument:
     -compiler'); MCP run_script_inline is NOT a GhidraScript context, so
     batch analysis must go through analyzeHeadless + a -postScript.
     (c) rewrite/ built and booted; gate stage 4b added (headless + Xvfb).
     (d) OQ-002/006/007/009 closed or narrowed from measurements; the earlier
     savegame note mis-cited OQ-010 (that is combat) — corrected to OQ-003.
P1 data formats. .bin tables (docs/re/tables.md) and the .shp container
(docs/re/shp.md) are done and gate-asserted (stages 3b, 3c). Three open items
all terminate at the same place — the exe's loaders: OQ-004 (.tsv grammar /
which file is loaded), OQ-005 (.shp pixel codec), OQ-008 (Ghidra import). That
is one Ghidra session, so P2 is the critical path; P1d/P1f are independent and
can be done any time but do not unblock P2.

## NEXT ACTION (exactly one)
Begin P4 map-gen from extracted files: inventory which files in
extracted/ascend02/data hold map/galaxy parameters (gen*.tmp, mapdata,
*.haz hazard tables — 26 DATA\ templates in docs/re/loader.md §5 name the
canonical set), write docs/re/mapgen.md citing file offsets, then implement
src/game/mapgen.{h,cpp} + unit tests. Constants MUST cite docs/re/mapgen.md;
anything ambiguous goes to OPEN-QUESTIONS (never invent). Do NOT chase the
static base again — read docs/re/loader.md §4 first.

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
[~] P1c .shp sprites — CONTAINER SPEC COMPLETE + gate-asserted (docs/re/shp.md,
        scripts/shp_probe.py, gate 3c; 208 libs / 1557 records). Pixel codec OPEN
        (OQ-005, needs the P2 shape loader); no PNGs until the codec is known.
[~] P1d .gam saves — CORRELATION ONLY (docs/re/savegame.md, scripts/gam_probe.py,
        gate 3f). resume.gam = sparse u32-LE; stride-75 tech-name chain resolves
        against restree.txt. Full record map OPEN (OQ-003): needs the exe's save
        writer. PLAN P4 requires save/load, which is NOT satisfiable until
        OQ-003 closes — tracked as a real dependency, not worked around.
[~] P1e FLIC/audio inventory — INVENTORY COMPLETE (docs/re/media.md, gate 3e).
        2 FLICs exact-tiled; 15 real Creative VOC + 77 headerless raw PCM
        (extension lies); sample rate unknown (OQ-006).
[~] P1f text encodings — COMPLETE (docs/re/text.md, gate 3g). ascend00 is
        CP437-clean; the shipped exe exposes 34 source module names, which is
        the P2 subsystem spine.
[ ] P2 Ghidra subsystem specs (9 subsystems, docs/re/*.md)
[~] P3 engine skeleton — BUILDS + BOOTS (gate 4/4b). rewrite/ C++17 + SDL2
        2.32.4 / SDL2_mixer 2.8.1 via pkg-config; libascend_core holds the
        verified readers (formats/cob.cpp, formats/bin_table.cpp) ported 1:1
        from the gate-asserted Python probes. 8 unit tests pass, including
        byte-for-byte equality between the C++ .cob reader and the extracted/
        tree. Binary boots headless (dummy driver) AND under Xvfb (x11).
        Remaining for P3: an actual render surface + input event pump.
[ ] P4 all systems ported with tests
[ ] P5 UI+media parity pass
[ ] P6 full campaign playable to victory; README
