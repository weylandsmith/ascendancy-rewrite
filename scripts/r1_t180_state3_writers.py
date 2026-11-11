#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""r1_t180_state3_writers.py — relation-state cell writer census (t180).

Question (ledger OQ-023 residual): which values can the ORIGINAL engine store
into the session-matrix relation-state cell, and does ANY code write 3?

Method (the fast one — a mnemonic-level census over a single linear objdump
pass, NOT a per-candidate boundary-verification sweep; the independent
encoder sweep scripts/r1_t107_writers_full.py 0x1c0 agrees site-for-site,
which is what makes this safe):

  1. objdump -b binary -D -m i386 -M intel over code object 0 [0x14bb0,
     0x82bb0) of work/ascend_restored.bin (t60 file-provenance law: the
     restored image carries the reconstructed VA immediates). objdump decodes
     sequentially, so boundaries are authoritative for a straight-line pass.
  2. Grep the disassembly for stores whose effective address carries the cell
     displacement, in BOTH banked notations for the same cell:
        row-relative  [rowbase + other*1 + 0x1c0]
        absolute      [other + owner*0x1ee + 0x12fd6]   (0x12e16 + 0x1c0)
  3. Report each store with its immediate (or source register), and every
     reader's compared constant, so the value set is derived from cited
     comparators rather than assumed.

Frame locals [esp+0x1c0] are KEPT in the output and flagged, because they are
the trap that made an earlier reading (docs/re/diplomacy.md S10 draft) wrong.

Usage: r1_t180_state3_writers.py [--cache work/r1/t180/code0.txt]
Exit 0 always. Output is a census, not a verdict.
"""
import os, re, re as _re, subprocess, subprocess as _sp, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "work", "ascend_restored.bin")
CODE_LO, CODE_HI = 0x14BB0, 0x82BB0
CACHE = os.path.join(ROOT, "work", "r1", "t180", "code0.txt")

ROW_DISP = 0x1C0
ABS_DISP = 0x12FD6
INSN = _re.compile(r"^\s*([0-9a-f]+):\t((?:[0-9a-f]{2} )+)\t(.*)$")

WRITE_MO = ("mov", "and", "or", "xor", "adc", "sbb", "add", "sub", "xchg")


def disasm():
    if os.path.exists(CACHE):
        return open(CACHE, errors="replace").read()
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    r = _sp.run(["objdump", "-b", "binary", "-D", "-m", "i386", "-M", "intel",
                 f"--start-address={CODE_LO}", f"--stop-address={CODE_HI}", IMG],
                capture_output=True, text=True)
    open(CACHE, "w").write(r.stdout)
    return r.stdout


def parse(text):
    """[(addr, bytes, mnem, operands)] ignoring objdump's wrapped-byte tails."""
    out, pend = [], None
    for ln in text.splitlines():
        m = INSN.match(ln)
        if not m:
            continue
        addr, bs, rest = m.group(1), m.group(2).strip(), m.group(3)
        if not rest:
            if pend is not None:
                out[pend] = (out[pend][0] + " " + bs, out[pend][1])
            continue
        out.append((int(addr, 16), bs, rest))
        pend = len(out) - 1
    return out


def main():
    text = disasm()
    ins = parse(text)
    print(f"code object 0 [{CODE_LO:#x},{CODE_HI:#x}) -> {len(ins)} decoded insns"
          f" (cache {os.path.relpath(CACHE, ROOT)})")

    stores, reads = [], []
    for addr, bs, rest in ins:
        if "+0x1c0]" not in rest and "+0x12fd6]" not in rest:
            continue
        parts = rest.split(None, 1)
        if len(parts) < 2:
            continue
        mnem, ops = parts[0], parts[1]
        mem = ops
        if mnem in WRITE_MO or mnem.startswith(("mov", "add", "sub", "sub")):
            # store form: destination is the first operand
            dst = ops.split(",")[0]
            if "+0x1c0]" in dst or "+0x12fd6]" in dst:
                kind = "FRAME-LOCAL" if "[esp+0x1c0]" in dst or "[sp+0x1c0]" in dst else "CELL"
                stores.append((addr, kind, mnem, ops))
                continue
        reads.append((addr, mnem, ops))

    print(f"\n== STORES to the state-cell displacement ({len(stores)}) ==")
    for addr, kind, mnem, ops in stores:
        imm = _re.search(r",\s*(0x[0-9a-f]+)\s*$", ops)
        tag = f"imm={imm.group(1)}" if imm else "src=reg"
        print(f"  {addr:#07x} {kind:11s} {mnem:6s} {ops:38s} {tag}")

    print(f"\n== READERS: constants compared against the cell ({len(reads)}) ==")
    consts = {}
    for addr, mnem, ops in reads:
        imm = _re.search(r",\s*(0x[0-9a-f]+)\s*$", ops)
        if imm:
            consts.setdefault(imm.group(1), []).append(f"{addr:#x}")
        else:
            consts.setdefault("(no imm)", []).append(f"{addr:#x}")
    for k in sorted(consts, key=lambda s: (s == "(no imm)", s)):
        print(f"  {k:9s} x{len(consts[k]):2d}  {', '.join(consts[k])}")

    print("\n== VALUE SET (derived from cited writers+comparators, not assumed) ==")
    wv = sorted({m.group(1) for a, k, mn, o in stores if k == "CELL"
                 for m in [_re.search(r",\s*(0x[0-9a-f]+)$", o.strip())] if m})
    rv = sorted(k for k in consts if k.startswith("0x"))
    print(f"  stores imm to CELL: {wv}")
    print(f"  readers compare:    {rv}")
    w3 = [f"{a:#x}" for a, k, m, o in stores if k == "CELL" and o.rstrip().endswith(",0x3")]
    print(f"  IMM-3 WRITER SITES: {w3 if w3 else 'NONE'}")


if __name__ == "__main__":
    main()
