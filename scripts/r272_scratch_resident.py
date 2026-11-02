#!/usr/bin/env python3
"""t272 probe: is the ascend.exe image resident in the SCRATCH session's RAM?

The scratch session (title screen, New Game never clicked) produced savestate
ZIPs whose Memory member has ZERO payload-chunk hits at 32B/64B windows, while
the production ring (campaign in play) anchors base 0x1bf4d8 with 7-10 unique
chunks. Hypothesis: Ascendancy loads its strategy image only when a campaign
starts (New Game / Return to Current Game), so a title-screen scratch session
has no [0x482fb] to watchpoint. This script confirms/refutes at 16B granularity
and reports page population + markers.

Exit 0 = image present (watchable session is just a title boot)
     1 = image absent at title screen (scratch session MUST enter a campaign)
"""
import zipfile, sys

pay = open('work/ascend_payload.bin', 'rb').read()
path = sys.argv[1] if len(sys.argv) > 1 else 'work/r1/wp-t272/save/60.sav'
m = zipfile.ZipFile(path).read('Memory')
print(f'file={path} Memory={len(m)} payload={len(pay)}')

hits = [o for o in range(0, len(pay) - 16, 4096) if m.count(pay[o:o+16]) > 0]
print('16B any-occurrence chunks in scratch:', len(hits), hits[:8])

nz = sum(1 for i in range(0, len(m), 0x100000)
         if m[i:i+0x100000].strip(b'\x00'))
print(f'non-zero 1MB pages: {nz} of {len(m)//0x100000}')

for s in (b'ASCEND.EXE', b'ascend.exe', b'LE', b'STARS CONTROLLED'):
    print(repr(s), m.count(s))
sys.exit(0 if hits else 1)
