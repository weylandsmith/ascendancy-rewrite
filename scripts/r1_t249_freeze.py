#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t249 S10: (a) E8 direct-caller census for 0x51684 / 0x51834 / 0x51b68;
(b) every site writing dword 0 to [reg+0xab] (freeze-vs-refresh question:
    does anything clear the widget's list handle?);
(c) sites writing word 0x8d to [reg+0x8c9] (class constructor census)."""
import re, struct, subprocess
code = open("work/ascend_restored.bin", "rb").read()
CODE = (0x14bb0, 0x82bb0)

def disasm(lo, hi):
    return subprocess.run(["objdump", "-b", "binary", "-D", "-m", "i386", "-M", "intel",
                           "--start-address", hex(lo), "--stop-address", hex(hi),
                           "work/ascend_restored.bin"], capture_output=True, text=True).stdout

print("(a) E8 callers:")
for tgt in (0x51684, 0x51834, 0x51b68):
    callers = []
    for m in re.finditer(rb"\xe8", code):
        i = m.start()
        if not (CODE[0] <= i < CODE[1]):
            continue
        rel = struct.unpack_from("<i", code, i+1)[0]
        if CODE[0] <= i+5+rel < CODE[1] and i+5+rel == tgt:
            callers.append(i)
    # also pointer-table refs (disp/imm32 == tgt) outside code? whole-file:
    ptrs = [m.start() for m in re.finditer(re.escape(struct.pack("<I", tgt)), code)]
    print(f"  {tgt:#x}: E8 callers {len(callers)} {[hex(c) for c in callers]} "
          f"| u32 refs {len(ptrs)} {[hex(p) for p in ptrs[:8]]}")

print("(b) sites writing DWORD 0 to [reg+0xab] (66? no: C7 80 ab000000 / 83 80 ab000000 0 / 89 xx modrm disp8=0xab):")
hits = [CODE[0] + m.start() for m in re.finditer(rb"\xc7[\x80-\x87]\xab\x00\x00\x00\x00\x00\x00\x00", code) if CODE[0] <= m.start() < CODE[1]]
hits2 = [CODE[0] + m.start() for m in re.finditer(rb"\x83[\x80-\x87]\xab\x00\x00\x00\x00", code) if CODE[0] <= m.start() < CODE[1]]
# 89 8x (mov [reg+disp8],reg) can write 0 via xor'd reg; catch in disasm pass instead
print(f"  C7 form {len(hits)} {[hex(h) for h in hits]}")
print(f"  83 form {len(hits2)} {[hex(h) for h in hits2]}")
for h in (hits + hits2)[:12]:
    out = disasm(max(0, h-20), h+12)
    lines = [l for l in out.splitlines() if l.strip() and "<" in l or re.match(r"^\s+[0-9a-f]{6}:", l)]
    print(f"  --- {h:#x} ---")
    for l in lines[-6:]:
        print("   ", l)

print("(c) word 0x8d writes to [reg+0x8c9] (66 C7 8x c7080000 8d00):")
h3 = [m.start() for m in re.finditer(rb"\x66\xc7[\x80-\x87]\xc7\x08\x00\x00", code) if CODE[0] <= m.start() < CODE[1]]
print(f"  sites {len(h3)} {[hex(h) for h in h3]}")
for h in h3[:6]:
    out = disasm(max(0, h-16), h+16)
    print(f"  --- {h:#x} ---")
    for l in out.splitlines()[-8:]:
        print("   ", l)
