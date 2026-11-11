#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t290: tiny file-offset disassembler over work/ascend_payload.bin.

Why it exists: `objdump -b binary --start-address` prints NOTHING (t283 trap),
and the dd+objdump one-liners need -d every time. This is the same windowing
law with the trap designed out: extract N bytes at a FILE offset, disassemble
with capstone if available else objdump -b binary -d, print with FILE offsets
(never a virtual base — every consumer here converts file -> linear itself via
linear = B - 0x88 + file_off).

usage: r290_disasm.py FILE_OFF [NBYTES] [--end FILE_OFF_END]
       r290_disasm.py --pat eb540300        (census: every hit, then window)
Exit 0 always unless the payload is missing (2).
"""
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PAYLOAD = os.path.join(ROOT, "work", "ascend_payload.bin")


def disasm(data, base):
    try:
        from capstone import Cs, CS_ARCH_X86, CS_MODE_32
        md = Cs(CS_ARCH_X86, CS_MODE_32)
        out = []
        for ins in md.disasm(data, base):
            out.append(f"  {ins.address:07x}  {ins.bytes.hex():<20} "
                       f"{ins.mnemonic} {ins.op_str}")
        return out
    except ImportError:
        pass
    with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as tf:
        tf.write(data)
        path = tf.name
    try:
        # -D (NOT -d): a raw binary has no symbols, so -d disassembles
        # NOTHING and every window printed empty (t309 trap: the fallback
        # silently returned zero instructions whenever capstone was absent).
        r = subprocess.run(["objdump", "-b", "binary", "-m", "i386", "-M",
                            "intel", "-D", path],
                           capture_output=True, text=True)
        out = []
        for line in r.stdout.splitlines():
            m = re.match(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2} )+)"
                         r"\s*(.*)$", line)
            if not m:
                continue
            off = int(m.group(1), 16)
            raw = m.group(2).replace(" ", "")
            out.append(f"  {base + off:07x}  {raw:<20} {m.group(3)}")
        return out
    finally:
        os.unlink(path)


def window(pay, start, nbytes):
    data = pay[start:min(len(pay), start + nbytes)]
    print(f"--- file window {start:#x} .. {start + len(data):#x} "
          f"({len(data)} B)")
    for l in disasm(data, start):
        print(l)


def main():
    if not os.path.exists(PAYLOAD):
        print("missing payload", PAYLOAD)
        return 2
    pay = open(PAYLOAD, "rb").read()
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        return 0
    if a[0] == "--pat":
        pat = bytes.fromhex(a[1])
        hits = [m.start() for m in re.finditer(re.escape(pat), pay)]
        print(f"pattern {a[1]} : {len(hits)} hits {[hex(h) for h in hits]}")
        w = int(a[2], 0) if len(a) > 2 else 0x40
        for h in hits:
            window(pay, h - 0x10, w + 0x10)
        return 0
    if a[0] == "--end":
        print(__doc__)
        return 0
    start = int(a[0], 0)
    n = int(a[1], 0) if len(a) > 1 else 0x40
    if "--end" in a:
        e = int(a[a.index("--end") + 1], 0)
        n = e - start
    window(pay, start, n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
