#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t326b: extract fn(0x17c54) and fn(0x16147) from work/t91_code_disasm.txt.

Function segmentation law (t91 disasm): functions are separated by int3-pad
blocks (runs of `cc` / `nop`). A function starts at the first non-pad
instruction after a pad run >= 4 bytes, and ends at the pad run that follows
its ret/jmp tail. This script finds pad-run boundaries and reports the
function range containing a target address, then dumps it.
"""
import re, sys, bisect

PATH = "work/t91_code_disasm.txt"
LINE = re.compile(r"^\s+([0-9a-f]{4,6}):\t(.*)$")

addrs = []      # sorted addresses of every instruction line
lines = []      # (addr, text)
pads = []       # indices where a pad run starts (int3/nop after gap or consecutive pad)

with open(PATH, "r", errors="replace") as f:
    prev_addr = None
    pad_open = False
    for raw in f:
        m = LINE.match(raw)
        if not m:
            continue
        a = int(m.group(1), 16)
        txt = m.group(2).rstrip()
        # objdump format: "bytes<TAB>mnemonic" — strip the bytes column
        parts = txt.split("\t")
        mnem = parts[-1].strip() if len(parts) > 1 else txt
        is_pad = mnem.startswith("int3") or mnem.startswith("nop")
        gap = prev_addr is not None and a != prev_addr  # sequential file anyway
        if is_pad and not pad_open:
            pads.append(len(addrs))  # index of first pad insn of a run
            pad_open = True
        elif not is_pad:
            pad_open = False
        addrs.append(a)
        lines.append((a, mnem))
        prev_addr = a

print(f"total insns {len(addrs)}  range {hex(addrs[0])}..{hex(addrs[-1])}  padruns {len(pads)}")

def fn_bounds(target):
    """function = last pad-run start at/below target  ..  next pad-run start after target"""
    i = bisect.bisect_right(addrs, target) - 1
    if i < 0 or addrs[i] != target and False:
        pass
    # find pad-run start index <= i
    p = bisect.bisect_right(pads, i) - 1
    start = pads[p] if p >= 0 else 0
    # skip leading pads of this block
    while start < len(addrs) and lines[start][1].startswith(("int3", "nop")):
        start += 1
    q = bisect.bisect_right(pads, i)
    end = pads[q] if q < len(pads) else len(addrs)
    return start, end

for name, tgt in (("fn(0x17c54)", 0x17c54), ("fn(0x16147)", 0x16147)):
    s, e = fn_bounds(tgt)
    out = f"work/r326b_{name.split('(')[1].rstrip(')')}.txt"
    with open(out, "w") as g:
        for a, t in lines[s:e]:
            g.write(f"{a:06x}\t{t}\n")
    print(f"{name}: {hex(addrs[s])}..{hex(addrs[e-1])} ({e-s} insns) -> {out}")
