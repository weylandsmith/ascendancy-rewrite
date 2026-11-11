#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t181 correction probe: the earlier probe had an empty-slice bug
(mem.find(b'') == 0). RESUME-014 is 75,603 B (EOF 0x12753), so every
"verbatim chunk" hit past that offset was an artifact. Re-run with
in-bounds, content-bearing needles only."""
import zipfile, sys, os, time, struct
sys.path.insert(0, '/home/hrethric/projects/ascendancy/scripts')
R = '/home/hrethric/projects/ascendancy'
A14 = open(f'{R}/work/r1/SAVINGS-backup-20261014/RESUME.GAM', 'rb').read()
A21 = open(f'{R}/work/r1/game/RESUME.GAM', 'rb').read()
print("len14", hex(len(A14)), "len21", hex(len(A21)))

memT = zipfile.ZipFile(f'{R}/work/r1/playcap-20261014-224611/save/41.sav').read('Memory')
memS = zipfile.ZipFile(f'{R}/work/r1/selftest-t111-playcap/save/41.sav').read('Memory')

def find_in(data, off, mem, ln=0x30):
    seg = data[off:off+ln]
    if len(seg) < ln or seg.count(0) >= ln - 4:
        return None, None
    return mem.find(seg), seg

print("--- class-(i) correction: R14 tables located in oct14 title slots (t=0) ---")
for off in (0x200, 0x3200, 0x4000, 0xa000, 0xa200, 0xd000, 0x11200, 0x11400, 0x12000, 0x12400):
    j, seg = find_in(A14, off, memT)
    print(f"R14 {off:#07x} -> oct14slot41 {j and hex(j) or 'NONE'}  delta {j and hex(j-off) or '-'}")
print("--- same needles against selftest slot (different world: R21) ---")
for off in (0x200, 0x3200, 0xa000, 0x11200):
    j, seg = find_in(A14, off, memS)
    print(f"R14 {off:#07x} -> selftest41 {j and hex(j) or 'NONE'}")

print("--- R14 tail past 0x11200 ---")
tail = A14[0x11200:]
print("tail len", len(tail), "zeros", tail.count(0), "nonzero bytes", sum(1 for b in tail if b))

print("--- R21-vs-R14: does 01.SAV world == oct14 world? name token overlap ---")
def names(data):
    out = set(); cur = bytearray()
    for i in range(0x1000, len(data)-1):
        c = data[i]
        if 32 <= c < 127: cur.append(c)
        else:
            if len(cur) >= 6 and b' ' not in cur[:2]: out.add(bytes(cur).decode('cp437', 'replace'))
            cur = bytearray()
    return out
n14 = names(A14); n1 = names(A21)
print("tokens14", len(n14), "tokens21", len(n1), "shared", len(n14 & n1))

print("--- earliest slots: class labels ---")
import r1_slot as SL
pay = open(f'{R}/work/ascend_payload.bin', 'rb').read(); anch = SL.anchors_cached(R, pay)
for lbl, rd in [('oct14', 'playcap-20261014-224611'), ('selftest', 'selftest-t111-playcap'), ('playcap', 'playcap')]:
    for p in SL.slots_by_mtime(f'{R}/work/r1/{rd}')[:2]:
        mem = zipfile.ZipFile(p).read('Memory'); B = SL.base_of(mem, anch); d = SL.read_slot(p, mem, B)
        print(lbl, os.path.basename(p), time.strftime('%m-%d %H:%M:%S', time.localtime(os.path.getmtime(p))),
              f"t={d['turn']} score={d['score_stars']} sel={d['selector_byte']:#04x}")
