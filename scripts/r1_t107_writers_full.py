#!/usr/bin/env python3
"""r1_t107_writers_full.py — FULL memory-write encoding census [reg+DISP].

t107 audit tool. r1_t86/r1_t106 covered only mov/sub/add(+imm) store forms.
This variant adds every other memory-WRITING opcode family for the same
[base+disp] shapes (mod=01 disp8 and mod=10 disp32, plain + SIB scale00),
with and without the 0x66 operand-size prefix where legal:

  AND 20/21, OR 08/09, XOR 30/31, ADC 10/11, SBB 18/19, XCHG 86/87
  group 80 /0../5 imm8 ; 81/83 /0../5 imm (+66 imm16)   (/6 CMP excluded)
  INC/DEC FE /0,/1  byte ; FF /0,/1 (+66 word, no-prefix dword)
  NEG/NOT F6 /2,/3 byte ; F7 /2,/3 (+66 word)
  shifts/rotates C0 /0../5, C1 /0../5 (+66), D0..D3 /0../5 (all write)
  MOV C6 /0 imm8, C7 /0 imm32 (+66 imm16)

Boundary verification identical to r1_t106_writers.boundary_ok (function-start
decode preferred). Usage: r1_t107_writers_full.py 0x88 0x5d ...
"""
import bisect, subprocess, sys, os

ROOT = "/home/hrethric/projects/ascendancy"
IMG = os.path.join(ROOT, "work/ascend_restored.bin")
FUNCS = os.path.join(ROOT, "work/functions_full.tsv")
BASE_REGS = (0, 1, 2, 3, 5, 6, 7)


def encodings(off):
    out = set()
    mods = []
    if off < 0x80:
        mods.append((0x40, bytes([off])))
    mods.append((0x80, off.to_bytes(4, "little")))
    # (opcode, None-or-iter-of-ext, kind-base, allow66)
    ops = [(0x88, (None,), "mov8", False), (0x89, (None,), "mov", True),
           (0x00, (None,), "add8", False), (0x01, (None,), "add", True),
           (0x28, (None,), "sub8", False), (0x29, (None,), "sub", True),
           (0x20, (None,), "and8", False), (0x21, (None,), "and", True),
           (0x08, (None,), "or8", False), (0x09, (None,), "or", True),
           (0x30, (None,), "xor8", False), (0x31, (None,), "xor", True),
           (0x10, (None,), "adc8", False), (0x11, (None,), "adc", True),
           (0x18, (None,), "sbb8", False), (0x19, (None,), "sbb", True),
           (0x86, (None,), "xchg8", False), (0x87, (None,), "xchg", True),
           (0xC6, (0,), "mov8_imm", False), (0xC7, (0,), "mov_imm", True)]
    for op in (0x80, 0xFE, 0xF6):  # byte groups (no 66 variant)
        for g in (0, 1, 2, 3, 4, 4, 5):
            if op == 0x80 and g in (4,):
                continue  # placeholder dedupe
            ops.append((op, (g,) if op == 0x80 or op == 0xFE or op == 0xF6 else (g,),
                        f"g{op:x}_{g}", False))
    for op in (0x81, 0xFF, 0xF7):  # groups with legal 66
        gs = (0, 1, 2, 3, 4, 5) if op == 0x81 else (0, 1, 2, 3)
        for g in gs:
            ops.append((op, (g,), f"g{op:x}_{g}", True))
    for op in (0xC0, 0xD0, 0xD2):  # byte shifts (imm8/cl/dl)
        for g in range(6):
            ops.append((op, (g,), f"sh{op:x}_{g}", False))
    for op in (0xC1, 0xD1, 0xD3):  # word/dword shifts
        for g in range(6):
            ops.append((op, (g,), f"sh{op:x}_{g}", True))
    for op, exts, kind, allow66 in ops:
        for pfx in ((b"", b"\x66") if allow66 else (b"",)):
            k = kind + ("16" if pfx else "")
            for mod, disp in mods:
                for reg in (range(8) if exts == (None,) else exts):
                    r = reg
                    for rm in BASE_REGS:
                        out.add((pfx + bytes([op, mod | (r << 3) | rm]) + disp, k))
                    for sb in BASE_REGS:
                        sib = (0 << 6) | (4 << 3) | sb
                        out.add((pfx + bytes([op, mod | (r << 3) | 4, sib]) + disp, k))
    return out


def find_all(data, pat):
    res, start = [], 0
    while True:
        i = data.find(pat, start)
        if i < 0:
            return res
        res.append(i)
        start = i + 1


def ins_window(lo, hi):
    r = subprocess.run(["objdump", "-b", "binary", "-D", "-m", "i386",
                        "-M", "intel", f"--start-address={lo}",
                        f"--stop-address={hi}", IMG],
                       capture_output=True, text=True)
    ins = {}
    for ln in r.stdout.splitlines():
        m = ln.split(":", 1)
        if len(m) != 2 or not m[0].strip() or \
           not all(c in "0123456789abcdef" for c in m[0].strip()):
            continue
        a = int(m[0].strip(), 16)
        parts = m[1].split("\t")
        if len(parts) < 3:
            continue
        bytestr = parts[1].replace(" ", "")
        if len(bytestr) % 2:
            continue
        ins[a] = (len(bytestr) // 2, parts[2].strip())
    return ins


def boundary_ok(addr, tok, fstart):
    bases = [a for a in (fstart, addr & ~0xF, (addr & ~0xF) - 16)
             if a is not None and a <= addr]
    for base in bases:
        ins = ins_window(base, addr + 32)
        if addr in ins and tok in ins[addr][1]:
            return ins[addr][1]
    return None


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


def main():
    offs = [int(x, 0) for x in sys.argv[1:]] or [0x55]
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
            k = bisect.bisect_right(addrs, i) - 1
            fstart = addrs[k] if k >= 0 else None
            d = boundary_ok(i, tok, fstart)
            if d is None:
                rejected += 1
                continue
            verified.append((i, cand[i], d))
        print(f"candidates={len(cand)} verified={len(verified)} rejected={rejected}")
        for i, kind, d in verified:
            k = bisect.bisect_right(addrs, i) - 1
            fn = names[addrs[k]] if k >= 0 else "?"
            print(f"  0x{i:x}  [{fn}]  {kind:14s}  {d}")


if __name__ == "__main__":
    main()
