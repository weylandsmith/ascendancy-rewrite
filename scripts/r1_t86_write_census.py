#!/usr/bin/env python3
"""t86 (W6-A1): [reg+DISP] write-encoding census over work/ascend_restored.bin.

Finds every MEMORY-WRITE encoding that touches a fixed byte offset from a
base register, then verifies every candidate is an instruction boundary with
the right operand via objdump (R12: raw byte hits can be mid-instruction).

Encodings covered (32-bit mode, base regs eax..edi, SIB scale=1 index-free
disp8 forms included):
  mov  r/m32, r32   89 /r             mov r/m8, r8   88 /r
  mov  r/m16,r16    66 89 /r
  mov  r/m32,imm32  c7 /0             66 c7 /0 (imm16)
  sub  r/m32,r32    29 /r   sub8 28   66 29
  sub  r/m,imm      81 /5, 83 /5      66 81 /5
  add  r/m32,r32    01 /r   add8 00   66 01
  add  r/m,imm      81 /0, 83 /0
mod bits (32-bit addressing): mod=01 -> [reg+disp8], mod=10 -> [reg+disp32],
rm=4 is SIB (scale 00, no index encoded as 100 -> [base+disp]).

Usage: r1_t86_write_census.py 0x90 0x4a 0x3a ...
Output per offset: verified sites  addr, disasm, containing function
(work/functions_full.tsv offsets are HEX -- t83 trap).
"""
import subprocess, sys, os, bisect

ROOT = "/home/hrethric/projects/ascendancy"
IMG = os.path.join(ROOT, "work/ascend_restored.bin")
FUNCS = os.path.join(ROOT, "work/functions_full.tsv")
REGS = (0, 1, 2, 2, 3, 5, 6, 6)  # placeholder unused

BASE_REGS = (0, 1, 2, 3, 5, 6, 7)  # eax ecx edx ebx ebp esi edi


def encodings(off):
    """(pattern, kind) for writes to [base+off]."""
    out = set()
    mods = []
    if off < 0x80:
        mods.append((0x40, bytes([off])))                 # mod=01 disp8
    mods.append((0x80, off.to_bytes(4, "little")))        # mod=10 disp32
    # (opcode, ext-or-None, kind)
    ops = [(0x89, None, "mov32"), (0x88, None, "mov8"),
           (0x29, None, "sub32"), (0x28, None, "sub8"),
           (0x01, None, "add32"), (0x00, None, "add8"),
           (0xC7, 0, "mov_imm"),
           (0x81, 5, "sub_imm32"), (0x83, 5, "sub_imm8"),
           (0x81, 0, "add_imm32"), (0x83, 0, "add_imm8")]
    for op, ext, kind in ops:
        for pfx in (b"", b"\x66"):
            k = kind + ("16" if pfx and kind.endswith("32") else "")
            for mod, disp in mods:
                regs = (ext,) if ext is not None else range(8)
                for reg in regs:
                    # plain [reg+disp]
                    for rm in BASE_REGS:
                        modrm = mod | (reg << 3) | rm
                        out.add((pfx + bytes([op, modrm]) + disp, k))
                    # SIB scale=00 index=none(100): [base+disp]
                    for sb in BASE_REGS:
                        modrm = mod | (reg << 3) | 4
                        sib = (0 << 6) | (4 << 3) | sb
                        out.add((pfx + bytes([op, modrm, sib]) + disp, k))
    return out


def load_funcs():
    addrs, names = [], {}
    with open(FUNCS) as f:
        f.readline()
        for ln in f:
            p = ln.rstrip("\n").split("\t")
            try:
                a = int(p[0], 16)
            except Exception:
                continue
            addrs.append(a)
            names[a] = p[1] if len(p) > 1 else "?"
    addrs.sort()
    return addrs, names


def containing(a, addrs, names):
    i = bisect.bisect_right(addrs, a) - 1
    return names[addrs[i]] if i >= 0 else None


def find_all(data, pat):
    res, start = [], 0
    while True:
        i = data.find(pat, start)
        if i < 0:
            return res
        res.append(i)
        start = i + 1


DIS_CACHE = {}


def dis_at(addr):
    """First instruction disassembly at addr, via objdump windows.

    t106 FIX: the original decoded only the window at addr & ~0xF; objdump
    starts at the WINDOW BASE, so a base mid-instruction desyncures the stream
    and real sites were rejected as false negatives (the banked +0x55 seed
    store 0x37f9a was one of them). Try the aligned base and the two previous
    16-byte bases; accept only an instruction that STARTS at addr.
    """
    out = None
    for base in (addr & ~0xF, (addr & ~0xF) - 16, (addr & ~0xF) - 32):
        if base < 0:
            continue
        if base not in DIS_CACHE:
            r = subprocess.run(
                ["objdump", "-b", "binary", "-D", "-m", "i386", "-M", "intel",
                 f"--start-address={base}", f"--stop-address={base + 64}", IMG],
                capture_output=True, text=True)
            ins = {}
            for ln in r.stdout.splitlines():
                if ":" in ln and ln[:8].strip() and all(c in "0123456789abcdef" for c in ln[:8].strip()):
                    hexpart, rest = ln.split(":", 1)
                    try:
                        a = int(hexpart.strip(), 16)
                    except Exception:
                        continue
                    parts = rest.split("\t")
                    if len(parts) >= 2:
                        ins[a] = parts[-1].strip()
                    else:
                        toks = rest.split(None, 2)
                        if len(toks) == 3:
                            ins[a] = toks[2].strip()
            DIS_CACHE[base] = ins
        d = DIS_CACHE[base].get(addr)
        if d is not None:
            out = d
    return out


def main():
    offs = [int(x, 0) for x in sys.argv[1:]] or [0x90]
    data = open(IMG, "rb").read()
    addrs, names = load_funcs()
    for off in offs:
        print(f"\n######## offset +0x{off:x} ########")
        cand = {}
        for pat, kind in encodings(off):
            for i in find_all(data, pat):
                cand.setdefault(i, kind)
        tok = f"+0x{off:x}"
        verified, rejected = [], 0
        for i in sorted(cand):
            d = dis_at(i)
            if d is None or tok not in d:
                rejected += 1
                continue
            verified.append((i, cand[i], d))
        print(f"candidates={len(cand)} verified={len(verified)} rejected={rejected}")
        for i, kind, d in verified:
            fn = containing(i, addrs, names)
            print(f"  0x{i:x}  [{fn or 'no-function'}]  {kind:12s}  {d}")


if __name__ == "__main__":
    main()
