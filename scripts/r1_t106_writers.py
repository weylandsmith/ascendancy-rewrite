#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""r1_t106_writers.py — boundary-correct [reg+DISP] write census (offset, img).

Same encoding families as r1_t86_write_census.py, but fixes its
DIS_CACHE desync bug (P6 in docs/re/_wip_t106.md): instead of disassembling
one window at addr & ~0xF, tries EVERY 16-byte-aligned base in
[addr-15, addr] (each disassembling through addr), parses instruction
lengths from the byte column, and accepts a site only if some alignment
yields an instruction that STARTS exactly at addr.

Usage: r1_t106_writers.py 0x55 [0x4a ...]
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
    ops = [(0x89, None, "mov32"), (0x88, None, "mov8"),
           (0x29, None, "sub32"), (0x28, None, "sub8"),
           (0x01, None, "add32"), (0x00, None, "add8"),
           (0xC7, 0, "mov_imm"), (0xC6, 0, "mov8_imm"),
           (0x81, 5, "sub_imm32"), (0x83, 5, "sub_imm8"),
           (0x81, 0, "add_imm32"), (0x83, 0, "add_imm8"),
           (0x66, None, "NOPFX")]  # placeholder dropped below
    ops = ops[:-1]
    for op, ext, kind in ops:
        for pfx in (b"", b"\x66"):
            k = kind + ("16" if pfx and kind.endswith("32") else "")
            for mod, disp in mods:
                regs = (ext,) if ext is not None else range(8)
                for reg in regs:
                    for rm in BASE_REGS:
                        out.add((pfx + bytes([op, mod | (reg << 3) | rm]) + disp, k))
                    for sb in BASE_REGS:
                        sib = (0 << 6) | (4 << 3) | sb
                        out.add((pfx + bytes([op, mod | (reg << 3) | 4, sib]) + disp, k))
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
    """{addr: (nbytes, text)} via one objdump run [lo,hi).
    t108: objdump WRAPS long instructions: the tail appears as an address
    line with bytes but no mnemonic (e.g. '544ff: 00 ff ff' = tail of the
    insn at 0x544f8). Those tails are merged into the previous instruction's
    length so mid-inspection coverage is accurate; without merging, the
    gap left open lets fallback bases re-accept phantom boundaries."""
    r = subprocess.run(["objdump", "-b", "binary", "-D", "-m", "i386",
                        "-M", "intel", f"--start-address={lo}",
                        f"--stop-address={hi}", IMG],
                       capture_output=True, text=True)
    ins = {}
    last = None
    for ln in r.stdout.splitlines():
        m = ln.split(":", 1)
        if len(m) != 2 or not m[0].strip() or \
           not all(c in "0123456789abcdef" for c in m[0].strip()):
            continue
        a = int(m[0].strip(), 16)
        parts = m[1].split("\t")
        if len(parts) < 3:
            # t108: wrapped tail — bytes live in parts[1] (normal field);
            # merge into the previous instruction's length
            bs = parts[1].replace(" ", "") if len(parts) > 1 else ""
            if last is not None and bs and len(bs) % 2 == 0:
                n, t = ins[last]
                ins[last] = (n + len(bs) // 2, t)
            continue
        bytestr = parts[1].replace(" ", "")
        if len(bytestr) % 2:
            continue
        ins[a] = (len(bytestr) // 2, parts[2].strip())
        last = a
    return ins


def boundary_ok(addr, tok, fstart):
    """t108 AUTHORITATIVE RULE: decode from the containing FUNCTION START
    (objdump is sequential, so the chain covers [fstart, addr]); accept iff
    an insn starts exactly at addr and names tok; if the chain puts addr
    mid-instruction, REJECT. A fallback whose base equals addr (16-aligned
    candidate) self-verifies every pattern (R7 recurrence) — bases must be
    strictly below addr and are used only when the fn-start chain does not
    cover addr (dark zone)."""
    if fstart is not None and fstart <= addr:
        ins = ins_window(fstart, addr + 32)
        if addr in ins and tok in ins[addr][1]:
            return ins[addr][1]
        if any(a <= addr < a + ln for a, (ln, _) in ins.items()):
            return None
    for base in [a for a in ((addr & ~0xF) - 16, (addr & ~0xF)) if a < addr]:
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
        print(f"candidates={len(cand)} verified={len(verified)} "
              f"rejected={rejected}")
        for i, kind, d in verified:
            k = bisect.bisect_right(addrs, i) - 1
            fn = names[addrs[k]] if k >= 0 else "?"
            print(f"  0x{i:x}  [{fn}]  {kind:12s}  {d}")


if __name__ == "__main__":
    main()
