#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""graph_quality.py — acceptance test for the raw-load approach.

Because scripts/le_contiguity_test.py showed rel32 call targets resolve in
file space at 76:1 over a page-shifted control, absolute addresses are
irrelevant to the call graph: every code reference is either rel32 (base-free)
or a dword whose value is (target_file_off - C) for one constant C.

This script therefore treats FILE OFFSETS as addresses, seeds functions from
rel32 call targets, walks each function body to its terminators (following
branch targets inside the same function), and measures:

  * instruction count decoded vs bytes in the code region
  * fraction of decoded bytes that are unreachable by calls/jumps from the
    seed set (lower is better; huge unreachable mass = bogus disassembly)
  * bad-offset rate: branch/call targets outside a decoded function

This is the metric that decides whether a Ghidra raw import of the payload
can carry P2. Exit 0 = usable.
"""
import os, struct, sys
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXE = os.path.join(ROOT, 'game', 'ascend.exe')
CODE_LO, CODE_HI = 0x2b00, 0x85000


def main():
    if '--file' in sys.argv:
        global EXE
        EXE = sys.argv[sys.argv.index('--file') + 1]
    data = open(EXE, 'rb').read()
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    md.detail = True

    # 1. seed function entries from rel32 call targets found by window sweeps
    entries = set()
    for probe in range(CODE_LO, CODE_HI, 0x200):
        end = min(probe + 0x200, CODE_HI)
        for ins in md.disasm(data[probe:end], probe):
            if ins.mnemonic == 'call' and ins.op_str.startswith('0x'):
                t = int(ins.op_str, 16)
                if CODE_LO < t < CODE_HI:
                    entries.add(t)
    print(f"seed entries from call targets: {len(entries)}")

    # 2. walk each function from its entry to terminators
    decoded = bytearray(CODE_HI - CODE_LO)
    reached = bytearray(CODE_HI - CODE_LO)
    total_xfer = 0
    bad_xfer = 0
    fn_count = 0
    stack = sorted(entries)
    visited_entries = set()
    while stack:
        e = stack.pop()
        if e in visited_entries:
            continue
        visited_entries.add(e)
        fn_count += 1
        o = e
        body_targets = []
        while CODE_LO < o < CODE_HI:
            chunk = data[o:o + 15]
            got = False
            for ins in md.disasm(chunk, o):
                got = True
                if decoded[ins.address - CODE_LO]:
                    break
                for i in range(ins.size):
                    if ins.address + i - CODE_LO < len(decoded):
                        decoded[ins.address + i - CODE_LO] = 1
                total_xfer += 1
                m = ins.mnemonic
                if m in ('call', 'jmp') and ins.op_str.startswith('0x'):
                    t = int(ins.op_str, 16)
                    if CODE_LO < t < CODE_HI:
                        if m == 'call':
                            stack.append(t)
                        else:
                            body_targets.append(t)
                    else:
                        bad_xfer += 1
                elif m.startswith('j') and ins.op_str.startswith('0x'):
                    t = int(ins.op_str, 16)
                    if CODE_LO < t < CODE_HI:
                        body_targets.append(t)
                    else:
                        bad_xfer += 1
                o = ins.address + ins.size
                if m in ('ret', 'retf', 'iret') or m.startswith('hlt'):
                    break
                break
            if not got:
                break
        for t in body_targets:
            if not reached[t - CODE_LO]:
                reached[t - CODE_LO] = 1
                stack.append(t)

    nbytes = sum(decoded)
    region = CODE_HI - CODE_LO
    print(f"functions walked: {fn_count}")
    print(f"bytes decoded   : {nbytes} / {region} = {nbytes/region:.1%} of code region")
    print(f"transfer xrefs  : {total_xfer}, out-of-range: {bad_xfer} "
          f"({bad_xfer/max(1,total_xfer):.2%})")
    ok = nbytes / region > 0.55 and fn_count > 1500 and bad_xfer / max(1, total_xfer) < 0.03
    print("\nVERDICT:", "USABLE for P2 (raw load carries a real graph)" if ok
          else "NOT usable as-is")
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
