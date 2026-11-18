#!/usr/bin/env python3
"""t422 CONT cycle 2: census of call targets in the obj0 code range.
Linear capstone sweep with skipdata; dumps {target: [call sites]} JSON.
Usage: python3 t422c_callgraph.py [LO HI] > /tmp/calls.json"""
import sys, json
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

data = open("work/ascend_restored.bin", "rb").read()
md = Cs(CS_ARCH_X86, CS_MODE_32)
lo, hi = (int(sys.argv[1], 16), int(sys.argv[2], 16)) if len(sys.argv) > 2 else (0x10000, 0x82bb0)
calls = {}
n = 0
i = lo
while i < hi:
    ins = next(md.disasm(data[i:hi], i), None)
    if ins is None:
        i += 1
        continue
    n += 1
    if ins.mnemonic == "call" and ins.op_str.startswith("0x"):
        calls.setdefault(ins.op_str, []).append(ins.address)
    i += ins.size
print(f"# insns {n} sites {sum(len(v) for v in calls.values())} targets {len(calls)}",
      file=sys.stderr)
json.dump({k: [hex(a) for a in v] for k, v in calls.items()}, sys.stdout)
