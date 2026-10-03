# FINDINGS — verified reverse-engineering facts
Every entry cites its evidence. [verified] = observed directly in bytes/tools.

## 1. .cob resource archives [verified 2026-10-03, scripts/cob.py]
Layout (all LE):
  offset 0: u32 filecount N
  then N name records: ASCII filename, NUL-terminated, zero-padded so the
    next record starts on a 4-byte boundary (ascend00: 'batfx.txt' + 37 NULs
    -> next name at 0x36; padding pattern observed on all entries)
  then (N+1) u32 offsets: monotonic byte offsets into this file; entry i
    spans [off[i], off[i+1]). ascend00 N=54: dir ends 0xA90, first offsets
    2920, 6797, 6848 ... last == file size semantics TBD (extractor accepts
    best-fit N or N+1 tables; verified: extracted text is well-formed).
NO compression anywhere (extracted .txt files are plain CP437/ASCII;
entropy < 5.2 on text entries).
Contents:
  ascend00.cob (54 files): plaintext .txt/.dip — help.txt (44 KB),
    gizhelp.txt, gizmos.txt, history.txt, cosmos.txt ("STARS 50 /
    RACES 5 / SEED -1"), race00..race19.dip, music.txt, planitem.txt,
    subtitle.txt, tutindex.txt, ship.txt, static.txt, static? , beginnew.txt,
    galactic.txt, end-*.txt (ending texts).
  ascend01.cob (328 entries): data\NNname.shp shape sets (opening, status,
    negot, intel, ...), .tmp config blobs, misc.
  ascend02.cob (89 entries): PAIRED tables name.bin + name.tsv
    (battle, beginnew, galactic, planet, ship, species, tutintro) +
    data\ subdir (contents TBD).

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
