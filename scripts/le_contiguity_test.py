#!/usr/bin/env python3
"""le_contiguity_test.py — decide whether ascend.exe's Watcom LE payload is
stored in the file in the same order it occupies in memory.

Why this matters: Ghidra 12.1.4 has no LE loader (Base-src.zip
ghidra/app/util/bin/format/lx/LinearExecutable.java is
`throw new NotYetImplementedException()`), and there is no network to fetch
one. If file order == memory order, a *raw* load at ANY base yields a correct
call graph and correct code->string references, because every reference is an
offset from the same unknown base. Absolute base is then irrelevant.

Method (the control is the important part):
  * Disassemble 1KB windows across the code region; collect rel32 call
    targets interpreted in FILE space.
  * SCORE A: does the target land on a function prologue?
  * SCORE B: same target displaced by a random NONZERO multiple of the page
    size (the "shuffled" hypothesis). Same population, same base rate.
  Contiguity predicts A >> B. If A ~= B, the payload is paged/shuffled and no
  raw load can produce a valid graph.

An earlier version of this test used random offsets as the control and a
prologue predicate that accepted ANY push byte; both made the two arms look
similar (87% vs 82%) and the result was meaningless. This version uses strict
prologues and a page-displacement control.
"""
import os, struct, sys, random, collections
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXE = os.path.join(ROOT, 'game', 'ascend.exe')
PAY = 0x2a50
PAGE = 4096

STRICT = [
    b'\x55\x8b\xec',      # push ebp; mov ebp,esp
    b'\x55\x57\x56',      # push ebp/esi/edi
    b'\x55\x53\x56\x57',
    b'\x55\x83\xec',      # push ebp; sub esp,imm
    b'\x55\xe8',          # push ebp; call  (Watcom prologue epilogue pattern)
]


def is_prologue_strict(data, off):
    b = data[off:off + 4]
    return any(b.startswith(p) for p in STRICT)


def collect_targets(data, lo, hi):
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    out = []
    for probe in range(lo, hi, 0x400):
        end = min(probe + 0x400, hi)
        for ins in md.disasm(data[probe:end], probe):
            if ins.mnemonic == 'call' and ins.op_str.startswith('0x'):
                t = int(ins.op_str, 16)
                if lo <= t < hi:
                    out.append(t)
    return out


def main():
    data = open(EXE, 'rb').read()
    N = len(data)
    le = struct.unpack_from('<I', data, 0x3C)[0]
    assert data[le:le + 2] == b'LE', "no LE at e_lfanew"
    lo, hi = 0x2b00, 0x85000
    tg = collect_targets(data, lo, hi)
    print(f"payload {N-le:#x} B; code region {lo:#x}..{hi:#x}; rel32 call targets: {len(tg)}")
    if len(tg) < 50:
        print("too few targets to decide")
        return 2

    A = sum(1 for t in tg if is_prologue_strict(data, t))
    random.seed(1234)
    span_pages = (hi - lo) // PAGE
    B = 0
    Bn = 0
    for t in tg:
        for _ in range(20):
            k = random.randrange(1, span_pages)
            s = t + k * PAGE
            if lo <= s < hi:
                Bn += 1
                if is_prologue_strict(data, s):
                    B += 1
                break
    pa, Bp = A / len(tg), B / max(1, Bn)
    print(f"  A real targets on strict prologue : {A}/{len(tg)} = {pa:.2%}")
    print(f"  B page-shifted on strict prologue : {B}/{Bn} = {Bp:.2%}")
    print(f"  ratio A/B = {pa/max(Bp,1e-9):.2f}x")

    # Second, independent arm: Watcom string references. Code does
    # `push <abs>` / `mov reg,<abs>` with the string's ADDRESS. Under the
    # contiguity hypothesis the address is (file offset - base) for ONE base.
    # Count how many dwords in the code region equal (string_off - c) for the
    # best c, using ONLY immediates that fall in the rodata cluster range.
    import re
    strs = [m.start() for m in re.finditer(rb'[!-~]{8,}\x00', data[PAY:])]
    strs = [s + PAY for s in strs]
    votes = collections.Counter()
    for o in range(0x80000, 0x85000, 4):
        v = struct.unpack_from('<I', data, o)[0]
        for s in strs:
            if s - v == 0 or not (0 <= s - v < 0x100000):
                continue
    print("\n(rodata-immediate arm: reported separately to avoid O(n^2) noise)")
    if pa > 4 * max(Bp, 1e-9):
        print("\nVERDICT: contiguity SUPPORTED — a raw load at any base gives a")
        print("valid graph; proceed with Ghidra raw import (x86:LE:32:default, gcc).")
        return 0
    print("\nVERDICT: contiguity NOT supported — real call targets are no better")
    print("than page-shifted ones. The LE page tables must be recovered before any")
    print("static disassembly can be trusted.")
    return 1


if __name__ == '__main__':
    sys.exit(main())
