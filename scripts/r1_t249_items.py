#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t249 S8: item-run semantics + widget anchor.
Findings so far: bank-t1254 has ONE sig-hit obj at 0xfda074 with count 102,
entries forming a 0x7b-stride item run (base ~0x26d057 = recbase-0xac).
Here: (1) dump the 102 raw entries: are they item_base+0x7b*k exactly (sorted
by k) for some base? (2) owner byte test item+0x87 (== rec+0x33) count.
(3) pointer sites of (0xfda074-0xab) = widget, and of the item base.
(4) windows: obj+0xa0..0x100, item0 window."""
import struct, sys, zipfile, re, collections
sys.path.insert(0, "scripts")
import r1_slot as S
STRIDE = 123
pay = S.load_payload("."); anch = S.anchors_cached(".", pay)
mem = zipfile.ZipFile("work/r1/bank-t1254/48.sav").read("Memory")
B = S.base_of(mem, anch); OFF = 0x82bb0
race = mem[B + OFF + 0x7458e]
OBJ = 0xfda074
cnt = struct.unpack_from("<H", mem, OBJ + 0x8c7)[0]
ents = [struct.unpack_from("<I", mem, OBJ + 0xc7 + 8*k)[0] for k in range(cnt)]
comp = [struct.unpack_from("<I", mem, OBJ + 0xcb + 8*k)[0] for k in range(cnt)]
print(f"race {race} count {cnt}")
print("ents[:8] ", [hex(e) for e in ents[:8]])
print("comp[:8] ", [hex(c) for c in comp[:8]])
base = min(ents)
print(f"min ent {base:#x} max {max(ents):#x} span {max(ents)-base:#x} "
      f"span/0x7b {(max(ents)-base)/STRIDE:.3f}")
offs = [(e - base) for e in ents]
kset = [o/STRIDE for o in offs]
aligned = all(o % STRIDE == 0 for o in offs)
print(f"all (ent-min)%0x7b==0: {aligned}")
if aligned:
    ks = sorted(int(o/STRIDE) for o in offs)
    print(f"k range {ks[0]}..{ks[-1]} distinct {len(set(ks))} dup {len(ks)-len(set(ks))}")
    # owner byte at item+0x87
    own = collections.Counter(mem[e + 0x87] for e in ents)
    print(f"owner(item+0x87) hist over entries: {dict(own)}")
    # global count of items with +0x87==race and item-name sanity
    name0 = mem[ents[0]:ents[0]+19]
    print(f"item0 name-window raw: {name0!r}")
    print(f"item0+0x33 window: {mem[ents[0]+0x33:ents[0]+0x40]!r}")
    print(f"item0+0x80..0x95: {mem[ents[0]+0x80:ents[0]+0x95]!r}")
# (3) sites
for label, tgt in (("widget(OBJ-0xab)", OBJ - 0xab), ("OBJ", OBJ), ("item-min", base)):
    pat = struct.pack("<I", tgt)
    sites = [m.start() for m in re.finditer(re.escape(pat), mem)]
    d = [(s, m.start()-B-OFF) for m in re.finditer(re.escape(pat), mem)]
    tag = [(s, hex(s-B-OFF), "DATA" if 0 <= s-B-OFF < 0x20000 else "heap") for s, _ in d]
    print(f"sites of {label} {tgt:#x}: {len(sites)} -> {tag[:12]}")
# (4) obj window
print("obj+0xa0..0xf0:", mem[OBJ+0xa0:OBJ+0xf0].hex())
