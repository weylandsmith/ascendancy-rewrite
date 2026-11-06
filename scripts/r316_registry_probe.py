#!/usr/bin/env python3
"""t316: registry probe — can fn 0x56ca4's window table EVER name FLEETWND?

Laws (docs/re/_wip_t316.md S1, objdump-verbatim):
- fn 0x56ca4: esi=obj; bails ret0 if [[obj+0x4226]>>16] < 0; win=[obj+edx*12+4];
  call [win+0xa7 +0x8] with msg. edx = caller-supplied (STATSHIPLST passes
  [w+0x63]). fn 0x56d1c: same 12-stride table, count=[obj+0x3000] (<=0x400),
  entry valid iff [e+4]!=0, NAME at [e+4]+0x20 => table entry +4 = magic rec.
- Segment law (t315): code bytes at B+off; DATA absolutes = patched immediates
  read from code (obj1 base DB=0x242000 this run: imm 0x7a35c -> 0x2bc35c).
- Magic rec: u32 0x12345678 at rec+0, NAME rec+0x20 (RAW guest addresses).

Checks per save: (1) B/DB re-derive; (2) patched obj imm + count + mode4226;
(3) whole-RAM count of u32 values equal to any magic-rec address (a populated
registry must hold >=1 such pointer, fn 0x56d1c semantics); (4) FLEETWND rec
pointer presence; (5) base-free registry-shape scan (count in 1..0x400 at
A+0x3000 AND >=2 rec-pointers at A+4+i*12).

Usage: r316_registry_probe.py <sav> [<sav> ...]
"""
import re, struct, sys, zipfile

PAYLOAD = "/home/hrethric/projects/ascendancy/work/ascend_payload.bin"
pl = open(PAYLOAD, "rb").read()
MAGIC = struct.pack("<I", 0x12345678)

def probe(path):
    mem = zipfile.ZipFile(path).read("Memory")
    def u32(a):
        return struct.unpack_from("<I", mem, a)[0] if 0 <= a <= len(mem) - 4 else None

    hits = [m.start() for m in re.finditer(re.escape(pl[0x51834:0x51834 + 48]), mem)]
    Bs = sorted({h - 0x51834 for h in hits})
    B = Bs[0]
    obj = u32(B + 0x33398)          # patched imm of `mov $0x7a35c,%eax` @0x33397
    DB = obj - 0x7a35c
    count = u32(obj + 0x3000)
    mode = u32(obj + 0x4226)
    # magic recs (raw)
    recs = [m.start() for m in re.finditer(re.escape(MAGIC), mem)]
    recset = set(recs)
    # whole-RAM u32-aligned pointer-to-rec census
    ptr = 0
    fleet = 0
    for m in re.finditer(re.escape(struct.pack("<I", 0xfe7a90)), mem):
        fleet += 1
    # generic: scan aligned dwords in code-free zones is slow; regex per-rec is
    # bounded by rec count (126): sum of finditer passes
    for r in recset:
        for _ in re.finditer(re.escape(struct.pack("<I", r)), mem):
            ptr += 1
    # base-free shape scan
    shape = 0
    n = len(mem)
    for A in range(0, n - 0x3010, 4):
        c = u32(A + 0x3000)
        if c and 1 <= c <= 0x400:
            h = sum(1 for i in range(min(c, 6)) if u32(A + 4 + i * 12) in recset)
            if h >= 2:
                shape += 1
    loadscr = b"LOADSCREEN" in mem
    print(f"{path}\n  B={B:#x} Bs={[hex(b) for b in Bs]} obj={obj:#x} DB={DB:#x} "
          f"count={count} mode4226={mode and hex(mode)}")
    print(f"  magic-recs={len(recs)} ptr-to-rec(u32,whole-RAM)={ptr} "
          f"FLEETWND-rec-ptr={fleet} registry-shape-sites={shape} LOADSCREEN-bytes={loadscr}")

for p in sys.argv[1:]:
    probe(p)
