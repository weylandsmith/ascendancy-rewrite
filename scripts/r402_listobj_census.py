#!/usr/bin/env python3
"""t402: locate the PLANETALLOC list object (t249 sig law) in a banked save
and census the PAINT-VISIBLE planet records it references (+0x14 size word,
+0x16 type word). Sig: [o+0xab]==0 && byte[o+0xc5]==0 && [o+0xbb]==0xffffffff
&& u16[o+0x8c9]==0x8d ; entries inline obj+0xc7 stride 8; record = entry+0xac;
pointer values are guest-PHYSICAL (member = value+0x88)."""
import struct, sys, sys, zipfile
from collections import Counter

def main(path, want_count=None):
    mem = zipfile.ZipFile(path).read("Memory")
    objs = []
    for base in range(0x8000, len(mem) - 0x900, 4):
        m = base + 0x88
        if struct.unpack_from("<I", mem, m + 0xab)[0] != 0: continue
        if mem[m + 0xc5] != 0: continue
        if struct.unpack_from("<I", mem, m + 0xbb)[0] != 0xFFFFFFFF: continue
        if struct.unpack_from("<H", mem, m + 0x8c9)[0] != 0x8D: continue
        cnt = struct.unpack_from("<H", mem, m + 0x8c7)[0]
        if cnt == 0: continue
        objs.append((base, cnt))
    print("sig-objs:", [(hex(b), c) for b, c in objs])
    if not objs:
        return 1
    base, cnt = objs[0]
    if want_count:
        cand = [(b, c) for b, c in objs if c == want_count]
        if cand: base, cnt = cand[0]
    m = base + 0x88
    w14 = Counter(); w16 = Counter(); cells = Counter(); bad = 0
    samples = []
    for k in range(cnt):
        e = struct.unpack_from("<I", mem, m + 0xc7 + 8 * k)[0]
        rec = e + 0xac + 0x88
        if rec + 0x60 >= len(mem):
            bad += 1; continue
        a = struct.unpack_from("<H", mem, rec + 0x14)[0]
        b = struct.unpack_from("<H", mem, rec + 0x16)[0]
        c18 = struct.unpack_from("<H", mem, rec + 0x18)[0]
        w14[a] += 1; w16[b] += 1; cells[c18] += 1
        if len(samples) < 10:
            nm = mem[rec:rec + 19].split(b"\x00")[0].decode("cp437", "replace")
            samples.append((nm, a, b, c18, mem[rec + 0x33]))
    print(f"obj {base:#x} count {cnt} bad {bad}")
    print("w14(+0x14 size):", dict(sorted(w14.items())))
    print("w16(+0x16 type):", dict(sorted(w16.items())))
    print("cells(+0x18):", dict(sorted(cells.items())))
    for s in samples:
        print("  ", s)
    ok = all(v <= 4 for v in w14) and all(v <= 10 for v in w16) and not bad
    print("VERDICT", "PASS" if ok else "FAIL")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1
                  else "work/r1/bank-t249-live-open/60.sav"))
