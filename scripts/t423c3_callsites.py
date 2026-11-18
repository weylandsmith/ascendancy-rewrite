#!/usr/bin/env python3
"""t423c3: find all rel32 CALL/JMP sites to a target address in the restored
image (imagebase 0; file offset == address)."""
import sys, struct

PATH = "/home/hrethric/projects/ascendancy/work/ascend_restored.bin"
data = open(PATH, "rb").read()
targets = [int(t, 16) for t in sys.argv[1:]]
for T in targets:
    sites = []
    for i in range(0x14bb0, 0x82bb0 - 5):
        if data[i] == 0xE8 or data[i] == 0xE9:
            rel = struct.unpack_from("<i", data, i + 1)[0]
            if i + 5 + rel == T:
                sites.append(hex(i))
    print(hex(T), "->", len(sites), "sites")
    for s in sites:
        print("   ", s)
