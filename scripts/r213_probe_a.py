#!/usr/bin/env python3
"""t213 probe A — al-form [ship+0x62] value source (0x15c6d / 0x15d98).

Three questions, in the order the t210/t211 pitfalls demand:
  1. ALIGNMENT (t108 law): are 0x15c6d and 0x15d98 instruction starts when the
     decode is anchored at the CONTAINING function entry 0x156d4
     (functions_full.tsv: 156d4 size 0x2551 -> 0x17c25)?  Report the gap bytes.
  2. FRAME STABILITY: any add/sub esp, or push/pop, between the prologue and
     each site?  (The two sites read esp+0x50 and esp+0 respectively, so the
     esp-offset semantics must be checked, not assumed.)
  3. VALUE DOMAIN: every write to the two source locals
     ([esp+0x50] byte for 0x15c6d; packed [esp+0] byte for 0x15d98) inside the
     function, with the value operand, plus the branch structure that reaches
     each site, plus whether bl==1 is forced before 0x15c34.
  4. SCANNER VALIDATION (t211 law): reproduce t210's six known E8 callers of
     0x4b740 BEFORE trusting any zero result, then census E8 callers of 0x156d4.
Usage: r213_probe_a.py [IMG]
"""
import sys
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

IMG = sys.argv[1] if len(sys.argv) > 1 else "work/ascend_restored.bin"
img = open(IMG, "rb").read()
FUNC_LO, FUNC_HI = 0x156d4, 0x17C25
CODE_LO, CODE_HI = 0x14BB0, 0x82BB0


def decode(lo, hi):
    out, gaps = {}, []
    off = lo
    while off < hi:
        md = Cs(CS_ARCH_X86, CS_MODE_32)
        md.detail = True
        got = False
        for ins in md.disasm(img[off:hi], off):
            out[ins.address] = ins
            off = ins.address + ins.size
            got = True
        if not got:
            gaps.append(off)
            off += 1
    return out, gaps


fn, gaps = decode(FUNC_LO, FUNC_HI)
print(f"== (1) ALIGNMENT: function {FUNC_LO:#x}..{FUNC_HI:#x} decoded {len(fn)} insns, {len(gaps)} gap bytes ==")
for s in (0x15C6D, 0x15D98, 0x15C34, 0x15E23, 0x15C63, 0x15DF0, 0x15CC5):
    print(f"   {s:#07x} is an insn start (entry-anchored): {s in fn}"
          + (f"  [{fn[s].mnemonic} {fn[s].op_str}]" if s in fn else ""))
print("   gap bytes:", [hex(g) for g in gaps][:40])
for s in (0x15C6D, 0x15D98):
    near = [g for g in gaps if s - 4 <= g <= s + 4]
    print(f"   gaps within +/-4 of {s:#x}: {[hex(g) for g in near]}")

print("\n== (2) FRAME OPS prologue -> site (esp must be stable for both offset families) ==")
for site in (0x15C6D, 0x15D98):
    ops = [(a, fn[a].mnemonic, fn[a].op_str) for a in sorted(fn)
           if FUNC_LO <= a < site and (fn[a].mnemonic in ("add", "sub") and fn[a].op_str.startswith("esp")
                                       or fn[a].mnemonic in ("push", "pop"))]
    print(f"   -> {site:#x}: {len(ops)} frame ops; last 8: {[f'{hex(a)} {m} {o}' for a, m, o in ops[-8:]]}")
print("   prologue:")
for a in sorted(fn)[:12]:
    print(f"     {a:#07x} {fn[a].mnemonic} {fn[a].op_str}")

print("\n== (3) VALUE DOMAIN ==")
print("   writes/reads of the [esp+0x50] byte family (0x15c6d source):")
for a in sorted(fn):
    o = fn[a].op_str
    if "esp + 0x50]" in o:
        print(f"     {a:#07x} {fn[a].mnemonic} {o}")
print("   writes of bl before/at 0x15c34 (0x15b00..0x15c60 window):")
for a in sorted(fn):
    if 0x15B00 <= a <= 0x15C60 and fn[a].mnemonic == "mov" and fn[a].op_str.startswith("bl"):
        print(f"     {a:#07x} mov {fn[a].op_str}")
print("   writes/reads of the packed [esp] byte family (0x15d98 source):")
for a in sorted(fn):
    o = fn[a].op_str
    m = fn[a].mnemonic
    if o in ("byte ptr [esp], al",) or o.startswith("byte ptr [esp], ") or o == "al, byte ptr [esp]":
        print(f"     {a:#07x} {m} {o}")

print("\n== (4) E8 CALLER CENSUS (validated first) ==")


def callers_of(tgt):
    return [a for a in range(CODE_LO, CODE_HI - 5)
            if img[a] == 0xE8 and a + 5 + int.from_bytes(img[a + 1:a + 5], "little", signed=True) == tgt]


T210_KNOWN = {0x1A146, 0x39D9F, 0x3A0B3, 0x4BB56, 0x4D191, 0x4D2DD}
got = set(callers_of(0x4B740))
print(f"   positive control 0x4b740: got {sorted(hex(x) for x in got)}")
print(f"   control == t210's six EXACTLY: {got == T210_KNOWN}")
c = callers_of(0x156D4)
print(f"   E8 callers of 0x156d4: {[hex(x) for x in c]}  (n={len(c)})")
for a in c[:10]:
    print("     context:")
    for ins in Cs(CS_ARCH_X86, CS_MODE_32).disasm(img[a - 24:a + 5], a - 24):
        print(f"       {ins.address:#07x} {ins.mnemonic} {ins.op_str}")
