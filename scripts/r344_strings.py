#!/usr/bin/env python3
"""t344: name the immediate string operands of the cursor-shape dispatcher
fn 0x5a292..0x5a3ed (work/r331_disasm.txt). Per the pool-relative-immediate
law (docs/re/datafiles.md), an imm in the code may be a pool-relative offset
(str_off) that the loader relocates to P0+str_off, OR a direct linear/data
offset. Print BOTH readings for every imm seen in the dispatcher arms."""
import sys

PATHS = ["artifacts/ascend_restored.bin", "work/ascend_restored.bin"]
data = None
for p in PATHS:
    try:
        data = open(p, "rb").read()
        print("image:", p, len(data), "bytes")
        break
    except OSError:
        continue
if data is None:
    sys.exit(1)

def cstr(off):
    if off is None or off < 0 or off >= len(data):
        return None
    e = data.find(b"\0", off)
    if e < 0 or e - off > 64 or e == off:
        return None
    b = data[off:e]
    try:
        t = b.decode("cp437")
    except Exception:
        return None
    # printable-ish only
    if any(ord(c) < 9 or (13 < ord(c) < 32) for c in t):
        return None
    return t

IMMS = {
    0x863a2: "arm1 (default-ish, after cmp ax,0x13 ja)",
    0x3804: "case?", 0x3815: "case?", 0x3827: "case?",
    0x863e9: "arm?", 0x384b: "case?", 0x385c: "case?",
    0x386d: "case?", 0x387f: "case?", 0x388e: "case?",
    0x38a0: "assert-fallback (before call 0x2a428 assert reporter)",
    0x484f8: "fn 0x5a1e4 argument (call 0x30a60)",
    0x4850c: "blit arg (push before call 0x5caac at 0x5a3e3)",
}
for i, note in IMMS.items():
    rel = i + 0x82bb0
    print("%-8s DIRECT=%-28r REL(+0x82bb0)=%-28r  %s"
          % (hex(i), cstr(i), cstr(rel), note))

print()
print("raw string run 0x86390..0x86440:")
run = data[0x86390:0x86440]
parts = [p.decode("cp437", "replace") for p in run.split(b"\0") if p]
print(parts)
