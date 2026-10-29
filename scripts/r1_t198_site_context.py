#!/usr/bin/env python3
"""t198 — context dump around each blit (FUN_0005caac) call site.

Prints a linear capstone disassembly of [site-SPAN, site+8] for every E8 call
to --target, restricted to --only address ranges (prefix match on hex).
Image: work/ascend_restored.bin, base-0 (image addr == file offset).
Restored-image caveat: string immediates are pool-relative (imm = off-0x82BB0).
"""
import sys, re
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

IMG = "work/ascend_restored.bin"
POOL = 0x82BB0
code = open(IMG, "rb").read()


def str_at(v):
    """resolve an immediate to a pool string if plausible (both encodings)."""
    for cand in (v, v + POOL):
        if 0x82bb0 <= cand < len(code):
            m = re.match(rb"[\x20-\x7e]{3,40}", code[cand:cand + 40])
            if m:
                return m.group(0).decode("latin1")
    return None


def main():
    target = 0x5CAAC
    span = 0x60
    prefixes = []
    i = 0
    while i < len(sys.argv):
        a = sys.argv[i]
        if a == "--target":
            target = int(sys.argv[i + 1], 16); i += 2
        elif a == "--span":
            span = int(sys.argv[i + 1], 16); i += 2
        elif a == "--only":
            prefixes = sys.argv[i + 1].split(","); i += 2
        else:
            i += 1

    md = Cs(CS_ARCH_X86, CS_MODE_32)
    md.detail = True
    lo, hi = 0x14BB0, 0x82BB0
    sites = []
    i = lo
    while i < hi - 5:
        if code[i] == 0xE8:
            rel = int.from_bytes(code[i + 1:i + 5], "little", signed=True)
            if i + 5 + rel == target:
                sites.append(i)
            i += 5
        else:
            i += 1
    if prefixes:
        sites = [s for s in sites if any(hex(s)[2:].startswith(p) for p in prefixes)]
    print(f"# target={hex(target)} sites_shown={len(sites)} span={hex(span)}")
    for s in sites:
        print(f"\n=== SITE {hex(s)} ===")
        start = s - span
        # re-sync: linear decode from start is approximate; note it
        for ins in md.disasm(code[start:s + 8], start):
            extra = ""
            for op in ins.operands:
                if op.type == 2:  # imm
                    sv = str_at(op.imm & 0xFFFFFFFF)
                    if sv:
                        extra += f"   ;; {sv}"
            mark = "  <<< CALL" if ins.address == s else ""
            print(f"{ins.address:#x}  {ins.mnemonic} {ins.op_str}{extra}{mark}")


if __name__ == "__main__":
    main()
