#!/usr/bin/env python3
"""t247: locate the "Planets Occupied" producer (header showed 102 at
t=1254 while u16@0x131b4 sat at 60 -> t246 attribution was wrong)."""
import zipfile, struct, sys
sys.path.insert(0, "scripts")
import r1_sav_scan as SS, r1_slot as S

OFF = 0x82bb0
pay = S.load_payload("."); anch = S.anchors_cached(".", pay)
mem = zipfile.ZipFile("work/r1/playcap/save/48.sav").read("Memory")
B = S.base_of(mem, anch)
race = mem[B + OFF + 0x7458e]
print("race", race, "turn", struct.unpack_from("<I", mem, B + OFF + 0x12e10)[0])

cands = [off for off in range(0, 0x160000, 2)
         if struct.unpack_from("<H", mem, B + OFF + off)[0] == 102]
print("u16==102 count:", len(cands))

blk0, blk1 = 0x12e1a, 0x12e1a + 0x1ee
print("in race-0 block:", [hex(o) for o in cands if blk0 <= o < blk1])
print("u8==102 in race-0 block:",
      [hex(blk0 + i) for i in range(0x1ee) if mem[B + OFF + blk0 + i] == 102])

n = struct.unpack_from("<I", mem, B + OFF + 0x13b96)[0] >> 16
print("u32@0x13b96>>16 =", n)

# adjacency: header shows (102 planets, 36 systems) together -> maybe stored together
for off in cands:
    nxt = struct.unpack_from("<H", mem, B + OFF + off + 2)[0]
    prv = struct.unpack_from("<H", mem, B + OFF + off - 2)[0] if off >= 2 else -1
    if 34 <= nxt <= 36 or 34 <= prv <= 36:
        print(f"ADJACENT u16@{hex(off)}=102 prev={prv} next={nxt}")

# star-table planet tally: maybe each star record holds a planet-count byte
base = B + OFF + 0x13bc5
bitset_idx = [i for i in range(50) if (mem[base + i * 0x60 + 0x14] >> race) & 1]
for o in range(0x60):
    s = sum(mem[base + i * 0x60 + o] for i in bitset_idx)
    if 95 <= s <= 110:
        print(f"star byte +0x{o:02x} sums {s} over bit-set stars")
