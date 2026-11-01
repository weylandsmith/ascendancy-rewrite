#!/usr/bin/env python3
"""t249 S9: (1) entries-as-OLD-records test: owner at entry+0x33, set-equality
of {entry+0xac} vs race-owned NEW records; (2) writer census for u16@dsx
0x131b4: scan code range of ascend_restored.bin for writes to absolute
0x131b4 (66 C7 05 / 66 89 0x05 modrm r16 / C7 05 / 89 05 / FF 0F inc /
0F C8-ish dec) — print every site with context. Also reads."""
import struct, sys, zipfile, re, collections, subprocess
sys.path.insert(0, "scripts")
import r1_slot as S
pay = S.load_payload("."); anch = S.anchors_cached(".", pay)
NAME_RE = rb"[A-Z][A-Za-z]{2,}(?: [IVX]+)?\x00"
STRIDE = 123

mem = zipfile.ZipFile("work/r1/bank-t1254/48.sav").read("Memory")
B = S.base_of(mem, anch); OFF = 0x82bb0
race = mem[B + OFF + 0x7458e]
hits = set(m.start() for m in re.finditer(NAME_RE, mem))
cands = [h for h in hits if all(h + i*STRIDE in hits for i in range(15))]
def runlen(c):
    n = 0; p = c
    while p in hits: n += 1; p += STRIDE
    return n
c = max(cands, key=runlen); rbase = c
while rbase - STRIDE in hits: rbase -= STRIDE
recs = {}
for k in range(200):
    j = rbase + k*STRIDE
    raw = mem[j:j+NAMEW] if False else mem[j:j+19]
    if raw.strip(b"\x00") == b"": continue
    recs[j] = (raw.split(b"\x00")[0].decode(errors="replace"), mem[j+0x33], k)
OBJ = 0xfda074
cnt = struct.unpack_from("<H", mem, OBJ + 0x8c7)[0]
ents = [struct.unpack_from("<I", mem, OBJ + 0xc7 + 8*k)[0] for k in range(cnt)]
own_ent = collections.Counter(mem[e + 0x33] for e in ents)
print(f"(1) owner byte at entry+0x33 hist: {dict(own_ent)}  (race={race})")
names = [mem[e:e+19].split(b"\x00")[0].decode(errors='replace') for e in ents[:6]]
print(f"    names at entry+0 (first 6): {names}")
race_recs = sorted(j for j, v in recs.items() if v[1] == race)
shifted = sorted(e + 0xac for e in ents)
print(f"    set {{entry+0xac}} == race-owned NEW recs: {shifted == race_recs}")
miss = set(race_recs) - set(shifted); extra = set(shifted) - set(race_recs)
print(f"    missing {len(miss)} extra {len(extra)}"
      + (f" e.g. miss {[hex(x) for x in list(miss)[:4]]}" if miss else ""))
# also plain set-equality entry==rec
print(f"    set {{entry}} == race-owned recs: {sorted(ents) == race_recs}")

# (2) writer census for absolute data addr 0x131b4 in code
print("(2) code scan for disp32==0x131b4 (any instruction referencing it):")
code = open("work/ascend_restored.bin", "rb").read()
pat = struct.pack("<I", 0x131b4)
sites = [m.start() for m in re.finditer(re.escape(pat), code)]
# keep only sites inside code range 0x14bb0..0x82bb0 (payload offsets == base-0 vaddr)
sites = [s for s in sites if 0x14bb0 <= s < 0x82bb0]
print(f"    disp32 sites in code: {len(sites)} -> {[hex(s) for s in sites]}")
if sites:
    lo = max(0, min(sites) - 16); hi = min(len(code), max(sites) + 16)
    out = subprocess.run(["objdump", "-b", "binary", "-D", "-m", "i386", "-M", "intel",
                          "--start-address", hex(lo), "--stop-address", hex(hi),
                          "work/ascend_restored.bin"], capture_output=True, text=True).stdout
    for line in out.splitlines():
        if any(hex(s)[2:] in line for s in sites) or "131b4" in line:
            print("   ", line)
# also scan for disp16 forms? i386 flat uses abs32; check byte-level 0xb4 0x13 0x00 0x00 done.
# quick semantic: what reads/writes: disasm each site ±6 insns
for s in sites[:8]:
    out = subprocess.run(["objdump", "-b", "binary", "-D", "-m", "i386", "-M", "intel",
                          "--start-address", hex(max(0, s-24)), "--stop-address", hex(s+24),
                          "work/ascend_restored.bin"], capture_output=True, text=True).stdout
    print(f"  --- site {s:#x} ---")
    for line in out.splitlines()[-14:]:
        print("   ", line)
