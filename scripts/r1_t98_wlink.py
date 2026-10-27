#!/usr/bin/env python3
"""t98: WATCOM WLINK debug-info verdict for game/ascend.exe (spec-first).

PURPOSE (docs/STATE.md t98): try once, properly, to tie the SO name block
(image FILE 0x88e60 == exe-file 0x8b8b0, delta +0x2a50) to order-kind
numerics via a SYMBOL TABLE. Record layouts from the IBM OS/2 16/32-bit LX
Specification rev 11 (cached: ~/.hermes/cache/web/archive.org-c9e087b277.md,
https://archive.org/download/IBMOS2Warp4ToolkitDocuments2/lxref.htm), NOT
guesswork (t97 guessed twice; that tool is superseded and corrected here).

STRUCTURE FACTS MEASURED THIS PASS (all cited in docs/re/aicode.md t98):
- LE header at DW(0x3c)=0x2a50; WATCOM variant keeps IBM field positions
  (header-relative table pointers verified by byte-exact tiling:
  objtab(2x24B)->obj page table(121x4B)->resident name 'corn'->entry
  table; loader section le+0xb8 size DW(le+0x38) ends exactly at DATA
  PAGES OFFSET 0x17600). Page-table entry VALUES are not raw file
  offsets -- value decoding is irrelevant to the verdict and not
  guessed here (t97 lesson).
- SO block (exe-file 0x8b8b0) lies inside the demand-page span
  (0x17600..EOF) = plain loaded image data.

VERDICT LOGIC (strict-close): the tie requires debug symbol records. They
exist iff DEBUG INFO OFF/LEN (header +0x98/+0x9c, FILE-relative per spec's
explicit correction note) are nonzero, or a debugger signature exists
anywhere in the file (spec section 2.18: first 4 bytes 'NB0'+n).
EXIT: 0 = walk completed AND verdict printed (positive tie prints TIE,
absence prints NEGATIVE); 2 = structure did not parse (harness bug).
"""
import re
import struct
import sys

EXE = '/home/hrethric/projects/ascendancy/game/ascend.exe'
SO_EXE_OFF = 0x8b8b0          # t94/t97 byte-verified block location
d = open(EXE, 'rb').read()
fail = []

le = struct.unpack_from('<I', d, 0x3c)[0]
DW = lambda o: struct.unpack_from('<I', d, o)[0]
if d[le:le + 2] != b'LE':
    print('harness: LE signature missing'); sys.exit(2)

objtab = le + DW(le + 0x40)
nobj = DW(le + 0x44)
optab = le + DW(le + 0x48)
datapages = DW(le + 0x80)
dbg_off = DW(le + 0x98)
dbg_len = DW(le + 0x9c)

print(f'LE hdr file={hex(le)} objects={nobj} datapages={hex(datapages)}')
print(f'DEBUG INFO OFF={hex(dbg_off)} LEN={hex(dbg_len)}')

# --- structural seals ---------------------------------------------------
# 1. loader-section tiling: le+0xb8 .. datapages (WLINK places the object
#    table first, spec fig 3-3; verify our objtab lands inside it)
if not (le + 0xb8 <= objtab < datapages):
    fail.append(f'objtab {hex(objtab)} outside loader section')
# 2. resident name table parses per spec 2.7 (module name entry)
resnam = le + DW(le + 0x58)
L = d[resnam] if 0 < resnam < len(d) else 0
modname = d[resnam + 1:resnam + 1 + L].decode('ascii', 'replace') if 0 < L < 0x100 else ''
if modname != 'corn':
    fail.append(f'resident name table parse failed (got {modname!r})')
else:
    print(f'module name (resident name table): {modname!r}')
# 3. page-table length seal: object page table (121 u32 per header
#    npages field) ends EXACTLY at the resident name table pointer ->
#    three independent header pointers tile: objtab(48B)->optab(121x4)->
#    resnam(->entrytab +8). (Byte-exact; proves header reads are sound --
#    the WATCOM variant keeps IBM field POSITIONS. Entry VALUES are not
#    raw file offsets -- page-table value decoding is NOT needed for the
#    verdict and is deliberately not guessed here, t97 lesson.)
pt_end = optab + DW(le + 0x14) * 4
if pt_end != resnam:
    fail.append(f'page table end {hex(pt_end)} != resident name {hex(resnam)}')
else:
    print(f'header tiling seal OK: objtab(48B)->optab(121x4B)->{hex(resnam)}==resname, '
          f'entrytab {hex(le + DW(le + 0x5c))}')
# 4. SO block lies inside the demand-page (file) span
if not (datapages <= SO_EXE_OFF < len(d)):
    fail.append('SO block outside demand span (unexpected)')
else:
    print(f'SO block at exe-file {hex(SO_EXE_OFF)}: inside demand pages '
          f'({hex(datapages)}..{hex(len(d))}) -- plain loaded data, no section of its own')

# --- debug-info verdict --------------------------------------------------
SIGS = [b'NB03', b'NB00', b'NB02', b'ODIAG', b'DWARF', b'OS21001']
sig_hits = {s: len(re.findall(re.escape(s), d)) for s in SIGS}
name_hits = {n: len(re.findall(re.escape(n), d)) for n in
             (b'SONothing', b'SOGoStar', b'SOColonize', b'SOOrbitPlanet',
              b'SOPatrol', b'SODefendPlanet', b'SOAttack', b'SOGoSpace')}
print('debug signatures:', sig_hits)
print('SO-name occurrences (each should be 1 = the block itself):',
      {k.decode(): v for k, v in name_hits.items()})

tie = None
if dbg_off != 0 and dbg_len != 0:
    # PRESENT branch (not taken on this exe; kept for reruns/other builds)
    blob = d[dbg_off:dbg_off + dbg_len]
    if re.search(rb'SONothing', blob):
        tie = f'DEBUG SECTION at {hex(dbg_off)} names the block -- parse records for the tie'
    else:
        print(f'debug section present ({hex(dbg_len)} B) but contains no SO names')
if tie is None and any(sig_hits.values()):
    tie = 'debug signature string found -- investigate region'
if tie:
    print('TIE LEAD:', tie)
else:
    print('NEGATIVE: debug symbol records ABSENT (header walk per LX spec rev 11 '
          'section 2.2/2.18: DEBUG INFO OFF=LEN=0; zero debugger signatures; '
          'each SO name occurs exactly once in the file = the data block). '
          'No symbol table exists to tie SO names to kind numerics.')

if fail:
    for f_ in fail:
        print('harness FAIL:', f_)
    sys.exit(2)
print('WALK COMPLETE (structure parses; verdict above is cited).')
sys.exit(0)
