# Data-file reference census + .cob container grammar (OQ-004)

Measured 2026-10-06s. Primary artifacts: `work/ascend_payload.bin`,
`game/ascend0{0,1,2}.cob`, live captures `work/r1/r1deep-20261006-123049`
(slot 41.sav; names-table identity additionally checked in
`r1deep-20261005-230146` and `r1ad-20261006-144225`). Tool:
`scripts/r1_datafile_strings.py` (per-run base via anchors; never hard-coded).

Address conventions used below: Ghidra/image address `d` (= payload file
offset at load, per the pointer law; H = 0x88 is only the zip member-header
constant, docs/re/r1-savestate.md). Image base P0 this build = 0x1BF450
guest-physical; string pool base = payload 0x82BB0.

## 1. THE POOL-RELATIVE IMMEDIATE LAW [verified byte-exact, 337 sites]

The obj stores data-file references as immediates RELATIVE TO THE STRING POOL,
not as image-absolute pointers. The file holds `imm = str_off - 0x82BB0`;
at load, relocation rewrites every such imm32 to the absolute runtime value
`P0 + str_off`. Verified pairs (payload file offset -> RAM u32 at the same
address, slot 41):

| site    | file imm  | RAM imm     | decodes to           |
|---------|-----------|-------------|----------------------|
| 0x468d3 | 0x02464   | 0x0244464   | `restree.txt`        |
| 0x2c0aa | 0x01340   | 0x0243340   | `end-ctrl.txt`       |
| 0x51921 | 0x02AD8   | 0x0244AD8   | `DATA\planets.shp`   |
| 0x1d071 | 0x00540   | 0x0242540   | `DATA\BLACK%.2d.HAZ` |

Consequences:
- A RAM scan for `u32 == P0 + name_offset` DOES find every code referrer of a
  pool string (that is how the census below was produced).
- The restored image shows the UNRELOCATED immediate (Ghidra prints
  `MOV EAX,0x2464` at 0x468d3); referrer addresses must come from the RAM
  scan, never from reading image immediates.
- REFINES/REFUTES the earlier STATE.md claim "shape libs are not opened via an
  image-absolute string pointer" (06r): the false zero was produced by a name
  regex that (a) excluded backslash paths and (b) matched extensions case
  sensively. All .shp/.HAZ/.DIP names DO have referrers (below).

## 2. CENSUS — names referenced by exe code (slot 41; 1 referrer unless noted)

`.txt` (23/23 in ascend00 TOC): batfx 0x1ad97, cosmos 0x2140e, end-dest
0x2c065, end-capt 0x2c07c, end-unit 0x2c093, end-ctrl 0x2c0aa (end-xtnc
0x2c04e also present), history 0x2b4d5, help 0x1bee2(+3 more), names
0x22894+0x571c2, newgame 0x5212c, planhelp 0x561f0, planitem 0x37fcd,
restree 0x468d3 (== independently-found loader FUN_00046870; self-validates
the law), reswin 0x4712b+0x47579, gizmos 0x49081, gizhelp 0x56105, soundfx
0x4ff42, static 0x218c1(+1), gwshare 0x31562, tutindex 0x35a7b, windows
0x575c3, music 0x212d4, SUBTITLE.TXT 0x2d15e+0x4fab0.
NOTE: the "23/23" census population is ascend00's TOC (54 entries; .txt
subset); every one has >=1 code referrer. The 10 data-dir .txt files with no
exe-literal name (batfx/battle/beginnew/galactic/planet/ship/species/starstat/
tutintro/tutorial .txt) DO appear in the .cob TOCs (all 10 confirmed present;
they are loaded via TOC lookup, not via a code literal).

`.shp`: data\planets.shp 0x2b224, data\planal%02d.shp 0x3a7e8, data\resring.shp
0x48476+0x487ad, DATA\planets.shp 0x51921+0x51dcd, DATA\suns.shp 0x51964+
0x51e10, DATA\smhome.shp 0x5231e, DATA\MOUSE.SHP 0x309f9, DATA\DKSHIP%02d.SHP
0x2344d(+LGRACE/SMSHIP siblings 0x233ff/0x23427, one loader at 0x23388).

`.HAZ`: DATA\BLACK%.2d.HAZ 0x1d071, DATA\SLANE03.HAZ 0x1d0b7, DATA\RACEA03.HAZ
0x1d0ea (all inside FUN_0001cf20 region).

`.DIP`: RACE%02d.DIP 0x37181+0x442a9, PLAYER.DIP 0x37193.

`.tmp` UI layouts (10): single table function ~0x5a2b3..0x5a39b
(1starmap 0x5a2b3, 3cfgnew 0x5a2ce, 7racesel 0x5a2e9, 8shipdes 0x5a305,
9ENDGAME 0x5a320, 12start 0x5a33b, 13negot 0x5a353, 16battle 0x5a36b,
20res 0x5a383, 10status 0x5a39a).

Media: data\logo.pal 0x211ea, DATA\game.pal 0x21704+0x2f435, data\logo.gif
0x2122b, scr%03d.gif 0x3605a, data\%s.voc 0x50230, data\theme00.raw 0x210f3,
DATA\0OPENING.GIF (referrers in the 0x2183x startup cluster).

## 3. .cob CONTAINER GRAMMAR [exact; ascend00 round-trips 54/54 MD5]

    +0x000  u32            N (entry count)          ascend00/01/02: 54/328/89
    +0x004  N x 50 bytes   NUL-padded CP437 names   (paths like 'data\10status.tmp')
    +0x004+50N  N x u32    absolute BLOB offsets into the same file
    blobs: entry i's bytes = [off_i, next_off) (sorted-ascending neighbours);
    ascend00: first off 0xb68 = toc_end(0xa90) + 216; final blob runs to EOF.

Verification: for ascend00, blob_md5 == md5(extracted/ascend00/<name>) for
ALL 54 entries (0 mismatches). ascend02: 14 md5-exact; the remaining 75 names
have no on-disk extracted twin (they belong to ascend01/02 paths the v1
extractor flattened differently or did not unpack), so per-entry md5 is
undefined for them — no mismatch was observed, only absence of a comparator.
ascend01: all 328 names are `data\...` UI/shape paths with no extracted twin.

## 4. WHICH TABLES THE EXE LOADS — ANSWERED

(a) Exe code literals (section 2) open the ascend00 text set + media + .DIP/
.HAZ/.SHP shapes — every pool name has a referrer.
(b) The ascend02 pair `battle.bin … tutintro.bin` + `.tsv` mirrors: ZERO exe
string literals anywhere in the payload (all case variants), and the bare
pool strings '.bin' (0x84708) / '.tsv' (0x84703) have zero referrers. BUT the
14 names sit in a resident RUNTIME NAME TABLE in guest RAM at 0x250c1c,
fixed address across 3/3 captures, inside a copied name-TOC block anchored in
`game/ascend01.cob:0x3f98` (i.e. the engine loads .cob TOC data into RAM and
opens files by TOC lookup). The RAM table interleaves media names
(`data\trust02.voc`, `data\intro00.raw`) with `battle.bin`…`tutintro.tsv`.
(c) The `.tsv` files are binary containers, not text (tables.md §3 stands);
the container grammar question is closed by section 3.
Field SEMANTICS of the .bin tables remain OQ-010 (open) — this item only
covered "which files load + container grammar".

## 5. Rewrite status

No rewrite behaviour change this item: the rewrite is a fresh-start model that
reads the extracted data dir directly; there is no .cob-loading or
TOC-lookup behaviour to upgrade. Evidence is documentary (this file) plus the
tool `scripts/r1_datafile_strings.py`. Gate coverage: RE static probe section
already asserts payload attribution health.
