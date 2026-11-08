#!/usr/bin/env python3
"""r340_writer_site.py — locate the t340 BPLM-fire writer (file offset 0x39290)
in the restored image + Ghidra function table, and disassemble the window.

Fire: BPLM 0x25EAF4 (00->0F) at linear EIP 0x1f86e0, session base B=0x1bf4d8,
H=0x88  ->  file offset = eip - (B - H) = 0x1f86e0 - 0x1bf450 = 0x39290.
Build-queue acc/complete law sites are 0x39005 (acc += IND) / 0x390a3
(acc >= COST) per OQ-016 (t274). Print the containing function and a code
window around the writer. Exit 0 = located.
"""
import re
import sys

ROOT = "/home/hrethric/projects/ascendancy"
FIRE_FILE = 0x39290
B, H = 0x1BF4D8, 0x88


def containing_fn():
    best = None
    rows = []
    with open(f"{ROOT}/work/functions_full.tsv") as fh:
        hdr = fh.readline().rstrip("\n").split("\t")
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) < 2:
                continue
            try:
                addr = int(p[0], 16) if not p[0].startswith("0x") else int(p[0], 0)
            except ValueError:
                continue
            rows.append((addr, p))
            if addr <= FIRE_FILE:
                if best is None or addr > best[0]:
                    best = (addr, p)
    return best, rows, hdr


def window_from_disasm(path, lo, hi):
    """Pull lines from a text disassembly whose addresses fall in [lo, hi)."""
    out = []
    rx = re.compile(r"^\s*([0-9a-fA-F]{4,8})\b")
    with open(path, errors="replace") as fh:
        for line in fh:
            m = rx.match(line)
            if not m:
                continue
            a = int(m.group(1), 16)
            if lo <= a < hi:
                out.append(line.rstrip())
    return out


def main():
    print(f"fire linear=0x{0x1f86e0:08x}  B=0x{B:x} H={H} (0x{H:x}) "
          f"-> file=0x{0x1f86e0 - (B - H):x} (expect 0x{FIRE_FILE:x})")
    best, rows, hdr = containing_fn()
    print(f"functions_full.tsv header: {hdr}")
    print(f"nearest function at-or-below fire: "
          f"{' '.join(best[1][:4]) if best else 'NONE'}")
    below = [a for a, _ in rows if a <= FIRE_FILE]
    above = [a for a, _ in rows if a > FIRE_FILE]
    if below and above:
        nxt = min(above)
        print(f"enclosing function span: 0x{max(below):x} .. 0x{nxt:x} "
              f"(fire at +0x{FIRE_FILE - max(below):x})")
    for cand in ("work/r331_disasm.txt", "work/t73c_obj1slab_disasm.txt"):
        try:
            w = window_from_disasm(f"{ROOT}/{cand}", FIRE_FILE - 0x60,
                                   FIRE_FILE + 0x30)
        except OSError:
            continue
        if w:
            print(f"\n--- {cand} window 0x{FIRE_FILE-0x60:x}..0x{FIRE_FILE+0x30:x} "
                  f"({len(w)} lines)")
            for l in w:
                print("   " + l)
            return 0
    print("\nno text disassembly window found (static image check only)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
