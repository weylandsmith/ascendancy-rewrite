#!/usr/bin/env python3
"""le_layout_test.py — decide, statistically, whether ascend.exe's Watcom LE
payload is stored in memory order in the file.

Why: Ghidra 12.1.4 has no LE loader (its LinearExecutable class is a
NotYetImplementedException stub) and there is no network access to fetch one.
If the payload's bytes appear in the file in the same order they occupy in
memory, a raw load at any base gives a correct call/jump graph and correct
string cross-references, which unblocks P2 without needing the LE page tables.

Two independent tests, both base-independent or base-voting:

 T1 call-graph locality: disassemble the code region; collect rel32 call
    targets computed AS IF file order == memory order, then score whether
    each target lands on a recognisable Watcom prologue. Compare against a
    control sample of random offsets in the same range. Contiguity predicts
    the real sample beats the control by a wide margin.

 T2 immediate/string voting: for dword immediates inside the code region
    only, vote on C = string_file_offset - immediate. A real base produces a
    sharp peak; noise produces a flat tail.

Exit 0 if contiguity is supported, 1 if refuted, 2 if inconclusive.
"""
import os, re, re as RE, struct, sys, random, collections
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXE = os.path.join(ROOT, 'game', 'ascend.exe')
PAY = 0x2a50

PROLOGUES = [b'\x55\x8b\xec', b'\x55\x57', b'\x55\x56', b'\x55\x53', b'\x55\x83',
             b'\x53\x56\x57', b'\x56\x57', b'\xe8']


def is_prologue(b):
    return any(b.startswith(p) for p in PROLOGUES) or (len(b) and b[0] in (0x50, 0x51, 0x52, 0x52, 0x55, 0x56, 0x57, 0x53))


def t1(data, start, end, label):
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    code = data[start:end]
    tgts = []
    insns = 0
    for ins in md.disasm(code, start):
        insns += 1
        if ins.mnemonic == 'call' and ins.op_str.startswith('0x'):
            t = int(ins.op_str, 16)
            if start < t < end:
                tgts.append(t)
    if not tgts:
        print(f"  [{label}] no in-range rel32 call targets")
        return 0.0, 0
    hit = sum(1 for t in tgts if is_prologue(data[t:t + 3]))
    rate = hit / len(tgts)
    print(f"  [{label}] insns={insns} targets={len(tgts)} land-on-prologue={hit} ({rate:.1%})")
    return rate, len(tgts)


def main():
    data = open(EXE, 'rb').read()
    N = len(data)
    le = struct.unpack_from('<I', data, 0x3C)[0]
    assert data[le:le + 2] == b'LE'
    print(f"file={EXE} size={N:#x} LE header at {le:#x} payload={N-le:#x}")

    # Code region heuristic: from just past the LE header+stub to the rodata
    # cluster (the .SHP path strings live near 0x86000).
    CODE_LO, CODE_HI = 0x2b00, 0x85000
    print(f"\nT1 — call-graph locality, region {CODE_LO:#x}..{CODE_HI:#x}")
    # chunked sweep: linear sweep desyncs, so restart at every call target
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    seeds = []
    for probe in range(CODE_LO, CODE_HI, 0x1000):
        r, n = None, None
    # per-1K linear sweeps and keep only the plausible ones
    real_rate_tot, real_tgt_tot = 0, 0
    for probe in range(CODE_LO, CODE_HI, 0x400):
        r, n = t1_chunk(data, probe, min(probe + 0x400, CODE_HI))
        real_rate_tot += r * n
        real_tgt_tot += n
    real_rate = real_rate_tot / max(1, real_tgt_tot)
    random.seed(11)
    ctl_rate_tot, ctl_tgt_tot = 0, 0
    for _ in range(80):
        probe = random.randrange(CODE_LO, CODE_HI - 0x400)
        r, n = t1_chunk(data, probe, probe + 0x400)
        ctl_rate_tot += r * n
        ctl_tgt_tot += n
    ctl_rate = ctl_rate_tot / max(1, ctl_tgt_tot)
    print(f"  REAL region prologue-hit rate: {real_rate:.1%} over {real_tgt_tot} targets")
    print(f"  CONTROL (random phases)      : {ctl_rate:.1%} over {ctl_tgt_tot} targets")

    print("\nT2 — immediate/string base voting (code region only)")
    strs = [m.start() for m in re.finditer(rb'[!-~]{8,}\x00', data[PAY:])]
    strs = [s + PAY for s in strs]
    strset = set(strs)
    votes = collections.Counter()
    for o in range(CODE_LO, CODE_HI - 3, 4):
        v = struct.unpack_from('<I', data, o)[0]
        if v == 0 or v > 0x1000000:
            continue
        # candidate base so that some string lands at this immediate
        for s in strs[::37]:
            c = s - v
            if 0 <= c < 0x200000:
                votes[c] += 1
    top = votes.most_common(5)
    print(f"  strings={len(strs)}; top base candidates:")
    for c, k in top:
        print(f"    C={c:#08x} votes={k} ({k/max(1,len(strs)):.0%} of strings)")
    peak = top[0][1] if top else 0
    median = sorted(votes.values())[len(votes)//2] if votes else 0
    print(f"  peak={peak} median={median} peak/median={peak/max(1,median):.1f}x")

    print("\nVERDICT")
    if real_rate > 3 * max(ctl_rate, 1e-9) and real_tgt_tot > 50:
        print("  T1 SUPPORTS file-order == memory-order")
        v1 = 1
    elif real_tgt_tot > 50:
        print("  T1 REFUTES contiguity (real sample no better than random)")
        v1 = -1
    else:
        print("  T1 inconclusive (too few call targets)")
        v1 = 0
    if peak >= 10 * max(1, median):
        print("  T2 SUPPORTS a single constant base")
        v2 = 1
    else:
        print("  T2 does not support a single constant base")
        v2 = 0
    if v1 == 1 and v2 == 1:
        print("  => raw-load the payload at the voted base (Ghidra raw import).")
        return 0
    if v1 == -1 or (v1 == 0 and v2 == 0):
        print("  => cannot raw-load; LE page tables must be recovered first.")
        return 1
    print("  => partial support; needs a third test.")
    return 2


def t1_chunk(data, start, end):
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    tgts = []
    for ins in md.disasm(data[start:end], start):
        if ins.mnemonic == 'call' and ins.op_str.startswith('0x'):
            t = int(ins.op_str, 16)
            if start - 0x2000 < t < end + 0x2000:
                tgts.append(t)
    if not tgts:
        return 0.0, 0
    hit = sum(1 for t in tgts if is_prologue(data[t:t + 3]))
    return hit / len(tgts), len(tgts)


if __name__ == '__main__':
    sys.exit(main())
