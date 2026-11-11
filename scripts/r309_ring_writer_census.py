#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t309: whole-image byte census of RING counter writers.

Question (docs/re/_wip_t309.md S3): both ring counters read 0 in EVERY oracle
snapshot incl. hold_post_star AFTER a witnessed ring-A post (the star ENTER
click fired w43504_28ec2 whose follow-on 0x28ed8 calls 0x56ad4) — yet the
post-fn gates on those counters let the post proceed. Who clears them, and is
the counter the LOW half (my rdc() read the HIGH half)?

usage: r309_ring_writer_census.py  (exit 0 always)
"""
import re

d = open("work/ascend_payload.bin", "rb").read()

def scan(pfx, disp, label, modrm_ok=lambda m: True):
    hits = []
    n = len(d)
    w = len(pfx)
    for i in range(n - w - 7):
        if d[i:i + w] == pfx:
            m = d[i + w]
            if (m >> 6) == 2 and d[i + w + 1:i + w + 5] == disp and modrm_ok(m):
                hits.append((hex(i), f"reg={(m >> 3) & 7} rm={m & 7}"))
    print(f"{label}: {len(hits)} {hits[:18]}")
    return hits

print("== ring counter writers (mod=10 disp32 form only) ==")
# RING-B: count dword [core+0x4758], widx word [core+0x475a]
scan(b"\x89", b"\x58\x47\x00\x00", "mov DWORD [r+0x4758] (ringB count)")
scan(b"\xc7\x80", b"\x58\x47\x00\x00", "mov DWORD [eax+0x4758],imm")
scan(b"\x66\x89", b"\x5a\x47\x00\x00", "mov WORD [r+0x475a] (ringB widx)")
scan(b"\x66\xc7", b"\x5a\x47\x00\x00", "mov WORD [r+0x475a],imm",
     lambda m: (m >> 3) & 7 == 0)
scan(b"\x66\xff", b"\x5a\x47\x00\x00", "inc/dec WORD [r+0x475a]",
     lambda m: (m >> 3) & 7 in (0, 1))
# RING-A: count dword [core+0x44aa], idx word [core+0x44ac]
scan(b"\x89", b"\xaa\x44\x00\x00", "mov DWORD [r+0x44aa] (ringA count)")
scan(b"\xc7\x80", b"\xaa\x44\x00\x00", "mov DWORD [eax+0x44aa],imm")
scan(b"\x66\x89", b"\xac\x44\x00\x00", "mov WORD [r+0x44ac] (ringA idx)")
scan(b"\x66\xc7", b"\xac\x44\x00\x00", "mov WORD [r+0x44ac],imm",
     lambda m: (m >> 3) & 7 == 0)
scan(b"\x66\xff", b"\xac\x44\x00\x00", "inc/dec WORD [r+0x44ac]",
     lambda m: (m >> 3) & 7 in (0, 1))
print("\n== sanity: the three sites disasm already proved ==")
print("0x55acc (ringB post inc widx):", d[0x55acc:0x55ae0].hex(" "))
print("0x56b4e (ringA post inc idx) :", d[0x56b4e:0x56b55].hex(" "))
print("0x55e3b (resolver zero idx)  :", d[0x55e3b:0x55e44].hex(" "))
print("\n== dword-wide stores that could zero the counter PAIRS ==")
# 0x4758 (count) and 0x475a (widx) share a dword: a mov [r+0x4758] writes both.
# likewise 0x44aa/0x44ac. The consumer/pump READS are sar>>16 = high half =
# 0x475a/0x44ac words. Print every dword store + imm store into either pair.
for pat, lbl in ((re.compile(rb"\x89[\x80-\xbf][\x00-\xff]{4}"), None),):
    pass
import struct
def dword_pair_stores(off, label):
    lo = struct.pack("<I", off)
    out = []
    for i in range(len(d) - 10):
        # mod=10 disp32 stores of any general reg: opcode 89 /r (r32->rm32)
        if d[i] == 0x89 and (d[i + 1] >> 6) == 2 and d[i + 2:i + 6] == lo:
            out.append((hex(i), "mov r32->"))
        if d[i:i + 2] == b"\xc7\x80" and d[i + 2:i + 6] == lo:
            imm = struct.unpack_from("<I", d, i + 6)[0]
            out.append((hex(i), f"imm={hex(imm)}"))
    print(f"{label} @+{hex(off)}: {len(out)} {out[:16]}")
dword_pair_stores(0x4758, "ringB count+widx dword")
dword_pair_stores(0x44aa, "ringA count+idx dword")
