#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t97: live-RAM read of the pool region the restored image truncates
(image ends FILE 0x8cc83; pool-rel 0xa0e0 -> F 0x8cc90 is PAST the end).
Law: pool string at payload-file offset F -> save member index B + F
(B = find_base vote on payload anchors; STATE POINTER-INDEX COROLLARY).
Self-validate first: F 0x88e60 (SONothing block) must read as names.
RC=0 iff at least one slot self-checked and the region printed."""
import sys, zipfile
sys.path.insert(0, '/home/hrethric/projects/ascendancy/scripts')
from r1_sav_scan import build_anchors, find_base

PAY = '/home/hrethric/projects/ascendancy/work/ascend_payload.bin'
SAVS = ['/home/hrethric/projects/ascendancy/work/r1/playcap/save/60.sav',
        '/home/hrethric/projects/ascendancy/work/r1/playcap/save/41.sav']
pay = open(PAY, 'rb').read()
anch = build_anchors(pay)
ok = False
for p in SAVS:
    try:
        mem = zipfile.ZipFile(p).read('Memory')
    except Exception as e:
        print('slot', p, 'ERR', e); continue
    votes, _ = find_base(mem, anch)
    if not votes:
        print('slot', p, 'base unresolved'); continue
    B = votes.most_common(1)[0][0]
    blk = mem[B+0x88e60: B+0x88f28]
    names_blk = [blk[i:i+20].split(b'\0')[0].decode(errors='replace') for i in range(0, 0xc8, 20)]
    print('slot', p, 'B=', hex(B))
    print('self-check SO block:', names_blk[:10])
    if names_blk[0] != 'SONothing':
        print('SELF-CHECK FAIL'); continue
    print('region F 0x8cc40..0x8cd40 repr:')
    print(repr(mem[B+0x8cc40: B+0x8cd40]))
    print('string at F 0x8cc90:', repr(mem[B+0x8cc90: B+0x8cd10].split(b'\0')[0]))
    # neighbours: what is at F 0x7a35c (second arg to call 0x55240 = likely file/name string)
    print('at F 0x7a35c:', repr(mem[B+0x7a35c: B+0x7a35c+48]))
    # pool-rel strings staged in the same tail zone
    for po in (0x613, 0x638, 0xa0e0, 0xa100, 0xa120):
        F = 0x82bb0 + po
        print('pool-rel %#x -> F %#x:' % (po, F), repr(mem[B+F: B+F+48].split(b'\0')[0]))
    ok = True
    break
print('RC', 0 if ok else 1)
sys.exit(0 if ok else 1)
