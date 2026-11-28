#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""tCITE pass 5 (call-target precision): for every `call 0xADDR` citation in
durable docs/re/*.md, verify ADDR is named by at least one E8 rel32 call
operand in the code span (or is an indirect-call idiom the doc itself names).
A `call 0xX` whose X no call instruction targets = mis-cited site (the
ships.md 0x250bb shape found by hand). Prints per-doc counts + offenders.
"""
import os, re, json

ROOT = "/home/hrethric/projects/ascendancy"
data = open(f"{ROOT}/work/ascend_restored.bin", "rb").read()
CODE_LO, CODE_HI = 0x14bb0, 0x82bb0

targets = set()
for i in range(CODE_LO, CODE_HI - 5):
    if data[i] == 0xE8:
        t = i + 5 + int.from_bytes(data[i + 1:i + 5], "little")
        targets.add(t & 0xFFFFFFFF)
print(f"rel32_call_targets={len(targets)}")

tok = re.compile(r"call(?:s|ed)?\s+(?:to\s+)?0x([0-9a-fA-F]{3,8})")
skip = {"_wip_", "_draft_", "_license_", "_notice_", "_readme_"}
docs = sorted(d for d in os.listdir(f"{ROOT}/docs/re")
              if d.endswith(".md") and not any(k in d for k in skip))
n = 0
off = []
for d in docs:
    for i, line in enumerate(open(f"{ROOT}/docs/re/{d}", encoding="utf-8", errors="replace"), 1):
        for m in tok.finditer(line):
            v = int(m.group(1), 16)
            n += 1
            if v not in targets:
                off.append((d, i, hex(v), line.strip()[:170]))
print(f"call_citations={n} offenders={len(off)}")
for d, i, a, ctx in off:
    print(f"OFFENDER {d}:{i} {a} | {ctx}")
