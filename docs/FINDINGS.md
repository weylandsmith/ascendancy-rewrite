# FINDINGS — verified reverse-engineering facts
Every entry cites its evidence. [verified] = observed directly in bytes/tools.

## 1. .cob resource archives [verified 2026-10-03, scripts/cob.py; OQ-001 CLOSED]
Layout (all LE):
  offset 0: u32 filecount N
  then N FIXED-50-BYTE name records: ASCII filename NUL-padded to exactly 50 B.
    Proof: dir_end == 4 + 50*N for all three archives (ascend00 4+50*54=0xA90,
    ascend01 4+50*328=0x4014, ascend02 4+50*89=0x1166) and an offset-table u32
    starts at each of those. Name lengths cover all residues mod 4, so the
    padding is fixed-50, NOT align-to-4.
  then N u32 offsets (NOT N+1 — see below); entry i spans [off[i], off[i+1]),
    last entry spans [off[N-1], EOF].
  Verified per archive: table strictly increasing; off[0] == 4+50*N+4*N exactly
    (data area starts immediately after the table); blob sizes sum exactly to
    filesize - (4 + 50N + 4N). OQ-001 CLOSED.
  BUG FIXED 2026-10-03: the seed extractor tried N-then-N+1 and used o[i+1] per
    entry, so it silently dropped each archive's LAST file (ascend00/static.txt
    5,685 B; ascend01/data/intro01.raw 479,670 B; ascend02/data/intro65a.flc
    19,054,614 B). Extraction now yields 471 files (was 468); the other 468 are
    byte-identical to before (0 mismatches in a full re-extract diff).
NO compression anywhere (extracted .txt files are plain CP437/ASCII;
entropy < 5.2 on text entries).
Contents:
  ascend00.cob (54 files): plaintext .txt/.dip — help.txt (44 KB),
    gizhelp.txt, gizmos.txt, history.txt, cosmos.txt ("STARS 50 /
    RACES 5 / SEED -1"), race00..race19.dip, music.txt, planitem.txt,
    subtitle.txt, tutindex.txt, ship.txt, static.txt, beginnew.txt,
    galactic.txt, restree.txt, starstat.txt, end-*.txt (ending texts).
    The same-stem .txt (battle/beginnew/galactic/planet/ship/species) are
    HELP/SCREEN TEXT with `text`/`endtext`/`pos`/`help`/`button` keywords —
    they are NOT data tables despite matching the ascend02 stems.
  ascend01.cob (328 entries): data\NNname.shp shape sets (opening, status,
    negot, intel, ...), .tmp config blobs, .voc audio, misc.
  ascend02.cob (89 entries): PAIRED tables name.bin + name.tsv
    (battle, beginnew, galactic, planet, ship, species, tutintro) +
    data\ subdir (.shp dkship00..20/lgrace00..20/9endgame, .raw theme00..04/
    race00..08/victory, intro65a.flc, intro.fnt, logo.gif, .tmp).

## 1b. ascend02 table pair [verified 2026-10-03, scripts/table_probe.py]
`name.bin` = 16-byte header (u32 constant 60; u32[3] zero — identical in all
7) + N x 24-byte records of 6 x u32 LE. Stride 24 is exact (body%24==0 on
7/7; autocorrelation ranks 24 above 48/72/96). Record counts: battle 2084,
beginnew 767, galactic 1028, planet 3463, ship 2169, species 1198,
tutintro 384. Full column inventory in docs/re/tables.md. cols 0/1/3/4 fit
u16 (high half always zero); col 2 contains recurring 0xFFFF and col 5
sometimes 0xFFFFFFFF -> keep as u32 pending Ghidra.
`name.tsv` = NOT TEXT despite the extension and NOT a text form of the .bin
(SEED CLAIM FALSIFIED). Evidence: 56-59% NUL bytes; entropy 2.55-3.00 (rules
out compression); lcp(x.tsv, x.bin)==0 for all 7; no .bin is a substring of
its .tsv; a 40-byte tech-name run at species.tsv+182 ("Orbital Structures...")
appears in ALL SEVEN .tsv and in NO .bin. They are sparse binary blobs of
NUL-delimited strings (tech names / UI labels). Container grammar + which file
the exe loads remain OQ-004.

## 1c. .shp shape libraries [verified container 2026-10-03, scripts/shp_probe.py; OQ-005 container CLOSED, codec OPEN]
208 libraries (ascend01 165, ascend02 43), 1557 shape records, all parsed.
Container (LE): magic "1.10" @0; u32 N @4; u32 table_size==8*(N+1) @8; u32 0
@12; then N+1 u64 slots @16. Record 0 sits at table_end (no slot); slots
0..N-2 are strictly-increasing record pointers for records 1..N-1; the last
record runs to EOF. Slots N-1 and N are library-level metadata, NEVER inside
the data area (verified 208/208; e.g. bullet04: (39,39,20,20) then signed
-10,-6). Record prefixes: rec0 packs dims u32 w + u32 h (198/208 — the other
10 are opaque in 2 byte-identical patterns, first word 0x7FFFFFBB x9, or
u32 18 + signed -5 x1); rec1+ pack dims u16 w + u16 h (163/163 observed).
Raw w*h does not size a record (bullet04 rec0: 10x11 spans 331 B).
CODEC UNRESOLVED: 5 RLE grammars x header 4/8/12 x u16/u32 dims searched
with an exact-span discriminator on the 12 smallest libraries — 0 survivors.
Per-record entropy 3.4-3.9 bits/byte over 20-31 distinct byte values: light
RLE over palette indices, not LZ. Do not render until the exe's shape loader
settles it (xrefs to 'DATA\DKSHIP%02d.SHP' @ascend.exe+0x86190). gate stage
3c asserts container parseability of all 208. game.pal = 768 B = 256xRGB888.
Aside: vesa480.dll is a Miles Design display shim, not game content.

## 2. Executables [verified]
ascend.exe 587,475 B: MZ DOS header; strings show "WATCOM C Run-Time
  system code ... 1988-1993", DOS4GPATH/dos4gw.exe stub messages ->
  32-bit LE Watcom FLAT binary under DOS4GW extender.
setsound.exe, uvconfig.exe: same family (setup tools).
dos4gw.exe 265,420 B: DOS4GW extender (do not RE; standard).
sndscape/ultra/rap10/sb*/proaudio .dig + dig.ini: Miles Design Audio
  Interface Library V3.02 of 18-Jan-95 (string in dig.ini) — driver shims,
  NOT game assets. AILDRV.RST present = driver listing.

## 3. Savegame resume.gam [verified header sample]
81,647 B; first bytes are plausible small u32 LE values
(0, 7, 0, 2, 4, 3, 12, 13, 19, ...) — structure TBD (P1d).

## 4. logic.flc [partially verified]
3,835,618 B. First u32 = 3,835,618 == file size (FLIC-style: header size
field == whole file for a single-fli container). Magic at +4 = 0xE1AF12??
NOTE: raw bytes e2 86 3a 00 | 12 af e1 00 -> magic field reads 0x00E1AF12
across the word boundary; per FLIC spec magic u16 @4 = 0xAF12 (FLC).
[unverified] treat as Autodesk FLC until a parser confirms frame count.

## 5. Toolchain notes [verified]
Ghidra 12.1.4 unpacked ~/tools/ghidra (sha256 ddac49f9... d2d4db, matches
release body). GhidraMCP (bethington v7-dev @d66702c) built via maven;
headless server entry com.xebyte.headless.GhidraMCPHeadlessServer,
HTTP 127.0.0.1:8089; stdio bridge module bridge_mcp_ghidra registered in
Hermes config mcp_servers.ghidra (PYTHONPATH=~/tools/ghidra-mcp/python,
~/tools/revenv/bin/python, --transport stdio --no-lazy).
Bridge DEFAULT_TCP_URL = http://127.0.0.1:8089 (config.py:55) — matches.
No network access at runtime for the headless server.
