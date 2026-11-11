#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t313 STEP 1h: msg-id dispatch chain inside fn 0x51cc4 (FLEETWND handler)
+ true indirect-dispatch census with SMALL displacements (the real law is
`ff 55 0c` call [ebp+0xc] / `ff 71 08` — 8-bit disp forms; the 1f3 probe used
disp32 and found nothing, which was a probe defect, not a negative).
"""
import re, subprocess, sys, tempfile, os

data = open("/home/hrethric/projects/ascendancy/work/ascend_payload.bin", "rb").read()

def disasm(start, end):
    with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as tf:
        tf.write(data[start:end]); path = tf.name
    try:
        out = subprocess.run(["objdump", "-D", "-b", "binary", "-m", "i386",
                              f"--adjust-vma={start}", path],
                             capture_output=True, text=True).stdout
    finally:
        os.unlink(path)
    pat = re.compile(r"^\s+([0-9a-f]+):\s+((?:[0-9a-f]{2} )+)\s*(\S+)\s*(.*)$")
    return [(int(m.group(1), 16), m.group(2).strip().replace(" ", ""), m.group(3), m.group(4).strip())
            for ln in out.splitlines() if (m := pat.match(ln))]

print("== fn 0x51cc4 (FLEETWND msg handler) full-ish map: cmp chain + calls + rets ==")
rows = disasm(0x51cc4, 0x51f3b)
for a, by, mnem, ops in rows:
    if (mnem == "cmp" and re.search(r"\b(dx|edx),", ops)) or mnem == "call" \
       or mnem == "ret" or (mnem.startswith("j") and re.search(r"0x51", ops)) \
       or "0x4350" in ops or re.search(r"\[e[a-z]+(\+0x[0-9a-f]+)?\]", ops) and mnem == "call":
        print(f"  {a:07x} {mnem} {ops}")

print("\n== whole-image indirect call census (8-bit disp forms ff 50-57 / ff 70-77) ==")
groups = {}
for m in re.finditer(rb"\xff([\x10-\x17\x48-\x4f\x90-\x97])(.)", data):
    modrm = m.group(1)[0]
    mode = (modrm >> 3) & 7          # FF sub-opcode lives in the REG field
    disp = m.group(2)[0]
    mod = modrm >> 6
    if mode == 2 and mod in (0, 1, 2):   # call r/m32
        key = disp if mod != 0 else 0x1000 + (modrm & 7)  # mod0 = [reg] no disp
        groups.setdefault(key, []).append(m.start())
for d in sorted(groups):
    hits = groups[d]
    if len(hits) >= 1:
        print(f"  call [reg+{d:#04x}]: {len(hits)} site(s) {[hex(h) for h in hits[:10]]}{'...' if len(hits)>10 else ''}")
