#!/usr/bin/env python3
"""t94 (W6-A5): ship order-kind +0x58 imm-store and cmp-reader census.

Complements scripts/r1_t86_write_census.py (whose op set lacks mov r/m8,imm8).
Scans work/ascend_restored.bin (R12 amendment file law — NEVER the payload
file for immediates) for:

  (S) store forms of literal imm into [base+DISP]:
      C6 /0 ib            mov byte [..], imm8   (imm8 == V)
      83 /0 ib            mov dword [..], imm8  (sign-ext, V in 0..7 or FF)
      66 83 /0 ib         mov word [..], imm8
  (C) compare forms (readers naming each kind):
      80 /7 ib            cmp byte [..], imm8
      83 /7 ib            cmp dword [..], imm8
      80 /0../3           test byte variants skipped (no imm)
  (R) plain register reads feeding dispatch:
      8A /r               mov r8, [base+DISP]
      0F B6 /r            movzx r32, byte [base+DISP]

Boundary verification: decode from the 16-byte-aligned window base and only
report the site if the disassembly stream lists it AND the text contains the
disp token (t86 pattern; t90 lesson: objdump --start-address needs 0x).

Scope filter: report sites in the obj0 code range [0x14bb0, 0x82bb0) as
CODE; anything else is flagged OUTSIDE-OBJ0 (the restored image covers all
objects; R12 says presence is a lead, not proof).

Usage: r1_t94_order_census.py [DISP_HEX ...]   (default 0x58)
"""
import subprocess, sys, os, bisect

ROOT = "/home/hrethric/projects/ascendancy"
IMG = os.path.join(ROOT, "work/ascend_restored.bin")
FUNCS = os.path.join(ROOT, "work/functions_full.tsv")
BASE_REGS = (0, 1, 1, 3, 4, 5, 6, 7)  # eax ecx ecx ebx esp ebp esi edi
OBJ0 = (0x14bb0, 0x82bb0)

def encodings(off, vals):
    """(pattern, kind) store-imm / cmp-imm / read forms at [base+off]."""
    out = set()
    mods = []
    if off < 0x80:
        mods.append((0x40, bytes([off])))
    mods.append((0x80, off.to_bytes(4, "little")))
    for mod, disp in mods:
        for v in vals:
            for rm in BASE_REGS:
                out.add((bytes([0xC6, mod | rm]) + disp + bytes([v]), f"st8imm{v}"))
                out.add((bytes([0x83, 0x00 | (rm & 7) | mod]) + disp + (v & 0xFF).to_bytes(1, "little"), f"st32imm{v}"))
                out.add((bytes([0x80, 0x38 | (rm & 7) | mod]) + disp + bytes([v]), f"cmp8imm{v}"))
        # word 16-bit operand form
        for v in vals:
            for rm in BASE_REGS:
                out.add((b"\x66" + bytes([0x83, 0x00 | (rm & 7) | mod]) + disp + (v & 0xFF).to_bytes(1, "little"), f"st16imm{v}"))
    # reads: independent of imm values; disp-only patterns
    if off < 0x80:
        mods_r = [(0x40, bytes([off]))]
    else:
        mods_r = []
    mods_r.append((0x80, off.to_bytes(4, "little")))
    for mod, disp in mods_r:
        for reg in range(8):
            for rm in BASE_REGS:
                out.add((bytes([0x8A, mod | (reg << 3) | rm]) + disp, "mov8r"))
                out.add((bytes([0x0F, 0xB6, mod | (reg << 3) | rm]) + disp, "movzx8"))
                out.add((bytes([0x38, mod | (reg << 3) | rm]) + disp, "cmp8rr"))
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
            addrs.append(a); names[a] = p[1] if len(p) > 1 else "?"
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
        res.append(i); start = i + 1

DIS_CACHE = {}
def dis_at(addr):
    lo = addr & ~0xF
    if lo not in DIS_CACHE:
        r = subprocess.run(
            ["objdump", "-b", "binary", "-D", "-m", "i386", "-M", "intel",
             f"--start-address=0x{lo:x}", f"--stop-address=0x{lo+64:x}", IMG],
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
        DIS_CACHE[lo] = ins
    return DIS_CACHE[lo].get(addr)

def main():
    offs = [int(x, 16) if not x.startswith("0x") else int(x, 16) for x in sys.argv[1:]] or [0x58]
    data = open(IMG, "rb").read()
    addrs, names = load_funcs()
    vals = [1, 2, 3, 4, 5, 5, 0xFF]
    for off in offs:
        print(f"\n######## [base+0x{off:x}] ########")
        tok = f"+0x{off:x}"
        cand = {}
        for pat, kind in encodings(off, vals):
            for i in find_all(data, pat):
                cand.setdefault(i, kind)
        rows = []
        for i in sorted(cand):
            d = dis_at(i)
            if d is None or tok not in d:
                continue
            rows.append((i, cand[i], d))
        inn = [r for r in rows if OBJ0[0] <= r[0] < OBJ0[1]]
        out = [r for r in rows if r not in inn]
        print(f"verified={len(rows)}  in-obj0={len(inn)}  outside={len(out)}")
        for i, kind, d in inn:
            print(f"  0x{i:x}  [{containing(i, addrs, names) or 'no-function'}]  {kind:10s}  {d}")
        if out:
            print("  --- outside obj0 code range (leads only) ---")
            for i, kind, d in out[:40]:
                print(f"  0x{i:x}  {kind:10s}  {d}")

if __name__ == "__main__":
    main()
