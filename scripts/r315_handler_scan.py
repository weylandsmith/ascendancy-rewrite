#!/usr/bin/env python3
"""t315 STEP 2: offline class-grid RAM scan for the digit-handler fn 0x354f8.

Target fn (docs/re/_wip_t315.md S1): payload 0x354f8, prologue 56 57 55 81 ec
44 01 (unique 2-site shape incl. sibling 0x1cf23), ZERO E8 callers ->
table-dispatched. Route (t313 laws, binding): class tables exist ONLY in guest
RAM; scan sav 'Memory' for u32 == 0x354f8 + P0; grid stride 6; cp =
grid_base - 0x88; window rec magic 0x12345678 at rec+0x00, NAME rec+0x20,
class ptr rec+0xa7.

P0 IS RE-DERIVED PER RUN (STATE warning): scan Memory for b'STATSHIPLST'
(payload string 0x856c6 per t314) -> P0 = hit - 0x856c6. Control: u32
0x51834+P0 must hit exactly 1 (t313, 4-reproduction law).

Usage: r315_handler_scan.py <sav> [--p0 HEX]
"""
import re, struct, sys, zipfile
from collections import Counter

SAV = sys.argv[1]
mem = zipfile.ZipFile(SAV).read("Memory")

def u32(a):
    return struct.unpack_from("<I", mem, a)[0]

def scan(val):
    n = struct.pack("<I", val)
    return [m.start() for m in re.finditer(re.escape(n), mem)]

# ---- P0 re-derivation -------------------------------------------------
# LAW (t315, measured on 212402 58.sav): payload BYTES map to RAM at B+off
# (B=0x1bf4d8 this run; STATSHIPLST string 0x856c6 -> 0x244b9e), but u32 CODE
# POINTERS carry P0 = B - 0x88 (vtable 0x248050 holds 0x210c84 =
# 0x51834+0x1bf450, NOT +B). So derive B from a payload code-byte pattern, then
# scan pointer values against P0 = B-0x88.
PAYLOAD = "/home/hrethric/projects/ascendancy/work/ascend_payload.bin"
if "--p0" in sys.argv:
    P0 = int(sys.argv[sys.argv.index("--p0") + 1], 16)
else:
    pl = open(PAYLOAD, "rb").read()
    hits = [m.start() for m in re.finditer(re.escape(pl[0x51834:0x51834 + 48]), mem)]
    Bs = sorted({h - 0x51834 for h in hits})
    print(f"code-pattern hits {[hex(h) for h in hits]} -> B candidates "
          f"{[hex(b) for b in Bs]}")
    P0 = Bs[0] - 0x88
CODE_END = P0 + 0x8CC83
print(f"sav={SAV} mem={len(mem)} P0={P0:#x} code=[{P0:#x},{CODE_END:#x})")

def is_code(v):
    return P0 <= v < CODE_END and (v & 1) == 0

def grid_of(addr):
    lo = addr
    while lo - 4 >= 0 and is_code(u32(lo - 4)):
        lo -= 4
    hi = addr
    while hi + 4 + 4 <= len(mem) and is_code(u32(hi + 4)):
        hi += 4
    return lo, hi

def name_rec(r, cp):
    rec = r - 0xa7
    if rec >= 0 and u32(rec) == 0x12345678:
        nm = mem[rec + 0x20:rec + 0x20 + 32].split(b"\0")[0].decode("cp437", "replace")
        b_af = mem[rec + 0xaf] if rec + 0xb0 <= len(mem) else None
        tbl = u32(rec + 0xab)
        return f"WINDOW rec {rec:#08x} NAME={nm!r} [+0xaf]={b_af} [+0xab]={tbl:#x}"
    return None

def report(val, label):
    hits = scan(val)
    print(f"\n== {label}: value {val:#x} -> {len(hits)} hit(s) {[hex(h) for h in hits]}")
    for h in hits:
        lo, hi = grid_of(h)
        nslots = (hi - lo) // 4 + 1
        slot = (h - lo) // 4
        print(f"  hit {h:#08x}: grid base {lo:#08x} nslots={nslots} slot_index={slot}")
        print("    slots: " + ", ".join(f"{u32(lo+4*i)-P0:#x}" for i in range(nslots)))
        # LAW (t313 name_b, STATUSWND-verified): class ptr ADDRESS cp =
        # grid_base - 0x88 (cp's vtable tail at cp+0x88 = the grid); window
        # recs hold cp at rec+0xa7. DO NOT deref grid_base-0x88 (lands on a
        # shifted slot value, the t310 trap).
        cp = lo - 0x88 if lo >= 0x88 else None
        print(f"    cp = grid_base-0x88 = {cp:#x}" if cp is not None else "    cp: n/a")
        if cp is not None:
            for r in scan(cp):
                named = name_rec(r, cp)
                print(f"    ref {r:#08x} -> {named if named else 'no magic at ref-0xa7'}")
    return hits

# controls first
report(0x51834 + P0, "CONTROL fn 0x51834 STATUSWND handler (expect 1)")
report(0x51cc4 + P0, "CONTROL fn 0x51cc4 FLEETWND handler (t313: grid B slot 2)")
# target + sibling
tgt = report(0x354f8 + P0, "TARGET digit-handler fn 0x354f8")
sib = report(0x1cf23 + P0, "SIBLING fn 0x1cf23 (same frame shape)")

# ---- DAT_7e582 (drives [win+0xaf] digit-max via dx==1 handler) --------
print("\n== DAT_7e582 census (high word selects digit-max) ==")
addr = P0 + 0x7e582
vals = Counter(u32(addr) for _ in [0])
print(f"  this sav: [{P0+0x7e582:#08x}] = {u32(addr):#08x} (high word "
      f"{u32(addr) >> 16})")
