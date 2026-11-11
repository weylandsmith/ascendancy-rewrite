#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t313 STEP 1f: block map of the FLEETWND vtable region 0x51b64..0x52060.

capstone is NOT installed (t313 trap: r290_disasm imports it but falls back to
objdump -D; this script reuses that fallback law directly). Prints only the
anchor instructions: msg-id cmp chain, DAT_43504/43508 references, calls, rets.
"""
import re, re, subprocess, subprocess, sys, tempfile, os

data = open("/home/hrethric/projects/ascendancy/work/ascend_payload.bin", "rb").read()
START, END = 0x51b64, 0x52060
with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as tf:
    tf.write(data[START:END]); path = tf.name
try:
    out = subprocess.run(["objdump", "-D", "-b", "binary", "-m", "i386",
                          f"--adjust-vma={START}", path],
                         capture_output=True, text=True).stdout
finally:
    os.unlink(path)

pat = re.compile(r"^\s+([0-9a-f]+):\s+((?:[0-9a-f]{2} )+)\s*(\S+)\s*(.*)$")
rows = []
for ln in out.splitlines():
    m = pat.match(ln)
    if m:
        rows.append((int(m.group(1), 16), m.group(3), m.group(4).strip()))
print(f"{len(rows)} insns {START:#x}..{END:#x}")

groups = {"MSGCMP": [], "DAT": [], "ICALL": [], "DCALL": [], "RET": []}
for a, mnem, ops in rows:
    line = f"{a:07x} {mnem} {ops}"
    if mnem == "ret":
        groups["RET"].append(line)
    elif mnem == "cmp" and re.search(r"\b(dx|edx),0x[0-9a-f]+", ops):
        groups["MSGCMP"].append(line)
    elif re.search(r"0x(43504|43508)\b", ops):
        groups["DAT"].append(line)
    elif mnem == "call" and ops.startswith("["):
        groups["ICALL"].append(line)
    elif mnem == "call":
        groups["DCALL"].append(line)
for k, sel in groups.items():
    print(f"\n== {k} ({len(sel)}) ==")
    for l in sel:
        print("  " + l)
