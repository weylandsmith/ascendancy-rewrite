#!/usr/bin/env python3
"""t283 helper: map a stopped-debugger EIP back to a payload file offset and
disassemble the writing instruction locally.

LAW (pointer law CLOSED, docs/re/r1-savestate.md): image verbatim at guest
P0 = B - 0x88, linear == physical, so payload_file_offset = EIP - (B - 0x88).
The t106/t107 windowed-disasm recipe: decode a window AROUND the site and
locate the instruction whose span CONTAINS the target (x86 is variable-length;
decoding AT the offset can desync — t201 law: sanity-check the window contains
a plausible function prologue / the known operand bytes).

usage: r1_t283_disasm.py --base 0x1BF4D8 --eip 0x2A1B3C [--span 48]
Prints: file offset, raw bytes, objdump intel window with the target line
marked. Exit 0 on success, 2 harness error.
"""
import argparse
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PAYLOAD = os.path.join(ROOT, "work", "ascend_payload.bin")
H = 0x88


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, help="ring-scanned B (hex ok)")
    ap.add_argument("--eip", required=True, help="stopped CS:IP offset (linear)")
    ap.add_argument("--span", type=int, default=48)
    args = ap.parse_args()
    if not os.path.exists(PAYLOAD):
        print("harness error: missing payload")
        return 2
    B = int(args.base, 0)
    eip = int(args.eip, 0)
    foff = eip - (B - H)
    pay = open(PAYLOAD, "rb").read()
    if not (0 <= foff < len(pay) - args.span):
        print(f"EIP {eip:#x} -> file {foff:#x} OUTSIDE payload (len {len(pay):#x}) "
              "— EIP may be in a DOS/TSR segment, not the image")
        return 2
    lo = max(0, foff - args.span)
    hi = min(len(pay), foff + args.span)
    window = pay[lo:hi]
    tmp = "/tmp/_t283_disasm.bin"
    open(tmp, "wb").write(window)
    r = subprocess.run(
        ["objdump", "-D", "-b", "binary", "-m", "i386", "-M", "intel",
         f"--adjust-vma={lo}", tmp],
        capture_output=True, text=True)
    print(f"B={B:#x} P0={B-H:#x} EIP={eip:#x} -> payload file offset {foff:#x}")
    print(f"raw @target: {pay[foff:foff+16].hex(' ')}")
    print("--- windowed disasm (>> marks the instruction containing the target;"
          " x86 is variable-length so decode-alignment matters, t201 law) ---")
    lines = r.stdout.splitlines()
    addrs = []
    for line in lines:
        s = line.strip()
        a = None
        if ":" in s:
            head = s.split(":", 1)[0].strip()
            if head and all(c in "0123456789abcdef" for c in head.lower()):
                a = int(head, 16)
        addrs.append(a)
    # the instruction containing foff = greatest addr <= foff
    mark = -1
    for i, a in enumerate(addrs):
        if a is not None and a <= foff:
            mark = i
    for i, line in enumerate(lines):
        print((">> " if i == mark else "   ") + line)
    if mark == -1:
        print("WARNING: no decoded instruction at/preceding the target — the "
              "window did not decode (desync); widen --span")
    return 0


if __name__ == "__main__":
    sys.exit(main())
