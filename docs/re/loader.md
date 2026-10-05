# RE spec — ascend.exe load model (P2 foundation)

Target: `game/ascend.exe` (587,475 B), an OS/2 LE (Watcom-locked) flat image
behind an MZ stub. Nothing here is guessed; every claim names the script that
measures it. Reproduce with the commands at the bottom.

## 1. Layout [verified]

- MZ stub 0..0x2a4f; `MZ+0x3c = 0x2a50` -> LE magic `LE` there.
  Payload = 0x2a50..EOF = 576,643 B (`work/ascend_payload.bin`).
- LE header dwords (payload-relative from 0x2a50, hex dump in
  `scripts/le_header_dump.py`): +0x10=512, +0x14=121, +0x18=1, +0x1c=0x63774
  (407 KB — debug/line-info size), +0x24=0xa7710 (0.68 MB image size),
  +0x28=0x1000 (page size), +0x2c=211.
- A run of exactly **121 dwords stepping +0x100 at file 0x2b40** (first
  values `0x0, 0x10000, 0x20000, ...`): consistent with an LE page table of
  121 pages of 0x1000 where each dword's **low byte is the page-flags byte**
  (all flags 0x00 here, so the step is exact). The earlier "no page table
  exists" conclusion was wrong in both directions: the table exists, and its
  page values are *memory* page numbers, not file offsets — which is why every
  "value must be a file offset in the data area" test returned 0/N.
  CORRECTION 2026-10-05i: scripts/le_tables_anchored.py could not tie ANY
  object-table parse to this run (no offset/entry-size combination from the
  header values has sum(cbObject)==cbImage), and the longest stride run in the
  file (256 at 0x789c4, first value 0x90c300cd = repeated `int3` code pattern)
  shows flag-free stride runs occur in CODE too. The page-table reading of the
  0x2b40 run is therefore PLAUSIBLE-BUT-UNTIED [inferred]; nothing downstream
  depends on it — §2 stands on le_contiguity_test.py, and the runtime base now
  comes from the capture (docs/re/r1-savestate.md POINTER LAW, CLOSED).

## 2. The image is stored in file order [verified]

`scripts/le_contiguity_test.py`: rel32 CALL targets resolve inside their own
page at 76:1 versus a page-shuffled control, and inter-page targets resolve
135:1 better than the control. Therefore disassembling at
`VA = file_offset − 0x2a50` is **correct for control flow**.

## 3. Bootstrap: 269 real functions without a loader [verified]

Ghidra 12.1.4 cannot import LE (`LinearExecutable.java` is a
NotYetImplementedException stub). `scripts/ghidra/Seed2.java` performs the
loader job headless: seed every `0xE8` rel32 CALL whose target starts with a
Watcom prologue, disassemble with flow, createFunction, iterate. Result
(`work/seed3.out`): pass1 seeds 1,555 of 8,856 call sites -> 269 functions,
82,033 code bytes covered (14.2%), median function 164 B, exported to
`work/functions.tsv`. These 269 are true positives (prologue + call-referenced);
the remaining ~86% needs indirect-edge recovery (jumptables via EBX-based
`jmp [tbl,ebx]`, which is why C matters — see §5).

## 4. No absolute base C exists in the static image [verified, four ways]

Candidate hypothesis `VA = payload_offset + C` was tested and **refuted**:

1. `scripts/vtable_base_test.py`: 10 pointer tables (>=8 in-image 4-aligned
   u32), 169 entries, with slot-1 value `0x1c158` repeated across 7
   independent tables (a destructor-slot signature — the runs are real
   vtables). Best C scores 25/169 prologue hits with a flat plateau; expected
   random = 0.4 and any real C would give ~169/169. No spike exists.
2. `scripts/ebx_relative_test.py`: EBX-relative displacements voting on a data
   base K reaches 71 — **below** the spacing control's 82 (anchor strings are
   15–31 B apart; multiples of 4 produce arithmetic collisions). REFUTED.
   (Also: 2,384 EBX-memory instructions exist, but the vote does not identify K.)
3. C=0 test: disassembled operands equal to an anchor's own payload offset —
   **zero** hits across 604k instructions (`/tmp/c0test.py` this session;
   logic to be re-added as a script if re-verification is wanted). Memory
   disp32 with no base equal to an anchor: zero.
4. High-coverage immediates (52 imm32 used by >=40 distinct functions, e.g.
   0x76e30 in 120 functions) — no C in [0,0x80000) maps more than 4/52 of them
   onto ASCII runs (control 1.0/52). They are **not** string addresses.

Conclusion: the Watcom image resolves data through mechanisms that are not
recoverable as a single static offset shift — per-object relocation applied at
load time (LE runtime fixups / Watcom self-relocation), EBX-based addressing
whose base register is set at runtime. **Static Ghidra analysis of the raw load
can recover control flow and function structure, but NOT data identity.**
Any claim of a recovered C must survive tests 1–4; several were proposed this
session and all died.

## 5. What the file DOES tell us statically [verified]

- 34 source module names embedded in the payload (`docs/re/text.md`,
  gate 3g): cosmos.c, race.c, ranceneg.c, ship.c, batmode.c, research.c,
  winmgr.c etc. — the subsystem spine for P2 specs.
- 26 `DATA\...` path templates (`work/ascend_payload.bin`, offsets in
  `scripts/media_probe.py` inventory): shape libs `SMRACE/LGRACE/SMSHIP/DKSHIP
  %02d.SHP`, `MOUSE.SHP`, `planets.shp`, `suns.shp`, `smhome.shp`, UI shape
  libs `1starmap.tmp`, `3cfgnew.tmp`, `7racesel.tmp`, `8shipdes.tmp`,
  `9ENDGAME.tmp`, `12start.tmp`, `13negot.tmp`, `16battle.tmp`, `20res.tmp`,
  `10status.tmp`, hazards `BLACK%.2d.HAZ`, `SLANE03.HAZ`, `RACEA03.HAZ`,
  palette `game.pal`, `0OPENING.GIF`.
- String search: the exe contains **no `.COB`/`.cob` string and no
  `.BIN`/`.bin` load templates** except `WINEVENT.BIN`. The CD ships
  `ascend00..02.cob`; the exe loads loose `DATA\*` files. Strong inference
  [inferred]: the installer unpacked the archives into `DATA\` at install
  time, and our `extracted/` tree reproduces that layout. The table-loader
  question (OQ-004) narrows to *which extracted files* the game names, and
  those names are not in the exe as plain strings.

## 6. Consequences for the rewrite [decision recorded]

Rule constants (combat, economy, AI thresholds) live in code whose
data side cannot be statically addressed. Two viable extraction routes remain:

- **R1 runtime dump** (dosbox-x): run the original, dump memory after data
  load, correlate dumped data pointers with extracted-file contents to derive
  the live base, then re-run Ghidra with the fixed base. Highest information,
  moderate risk (see DOSBOX RULE in STATE.md — the 12 GB log incident; must
  bound all logs and drive via pty). NOT YET ATTEMPTED this session.
  NB: §4 refuted a *constant static* base, not a runtime base; R1 remains
  viable.
- **R2 data-first rules** : implement systems from the extracted plaintext
  tables (`race*.dip` DIPVALUES, `restree.txt`, `items.txt`, ship tables),
  the manual (23-page rules prose, rasterised to `docs/assets/manual-jpg/`),
  and targeted dosbox observation; every constant cites an extracted-file
  offset per the goal contract. Formulas that remain ambiguous go to
  OPEN-QUESTIONS with the range of admissible behaviour.

Default under which work proceeds: **R2 first, R1 opportunistically** — see
docs/BLOCKED.md.

## Reproduce

```
# payload
~/tools/revenv/bin/python - <<'EOF'
import struct; d=open('game/ascend.exe','rb').read()
le=struct.unpack_from('<I',d,0x3c)[0]; open('work/ascend_payload.bin','wb').write(d[le:])
EOF
# contiguity
~/tools/revenv/bin/python scripts/le_contiguity_test.py
# seed functions (needs ~/tools/ghidra)
rm -rf work/ghp3 && mkdir -p work/ghp3
~/tools/ghidra/support/analyzeHeadless work/ghp3 ascend3 \
  -import work/ascend_payload.bin -processor x86:LE:32:default -cspec gcc \
  -noanalysis -scriptPath scripts/ghidra -postScript Seed2.java
# base refutation
~/tools/revenv/bin/python scripts/vtable_base_test.py
~/tools/revenv/bin/python scripts/ebx_relative_test.py
~/tools/revenv/bin/python scripts/le_header_dump.py
```

Ghidra API facts (12.1.4, verified via javap against shipped jars):
`currentProgram`/`monitor` are protected FIELDS on FlatProgramAPI, not methods;
no `disassembleAll`; `Listing` has no `getFunctionCount` (use
`Program#getFunctionManager()`); headless flag is `-cspec` not `-compiler`;
`Memory.getBytes(addr, buf)` vs `(addr, buf, arrayOffset, length)` — arg 3 is
an array offset (misusing it silently produced an all-zero image once).
