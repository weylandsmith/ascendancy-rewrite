#!/usr/bin/env python3
"""r1_mutation_inject.py — t53 capture STEP 1 injection side (OQ-003).

SCRATCH ONLY (game/ untouched). Target layout MEASURED this turn on the
scratch resume file (75,603 B): planet-name chain at 0xaae2, stride 123,
NAMES AT RECORD START (+0x00), 78 named records then empty ones. This file
convention differs from t50's game/resume.gam (base 0x9af8, name +0x24) —
the injection is NAME-RELATIVE so it needs no cross-file law.

  rec0 name := b'HERMESSEN'           (the load-path proof: if Resume reads
                                       this file, the string MUST appear in RAM)
  rec0/rec1: u16 0xBEEF/0xCAFE at name+0x0e, +0x20, +0x4a, +0x55
Prints injected record names + whole-file sentinel census.
Usage: r1_mutation_inject.py <resume-file> [--restore]
"""
import struct, sys, shutil, os, re

NBASE = 0xAAE2
REC = 123
NAMELEN = 30
OFFS = (0x0e, 0x20, 0x4a, 0x55)

def main():
    path = sys.argv[1]
    bak = path + ".pret53"
    if "--restore" in sys.argv:
        if os.path.exists(bak):
            shutil.copy2(bak, path)
            print("restored", path, "from", bak)
        else:
            print("no backup at", bak)
        return
    data = bytearray(open(path, "rb").read())
    # layout self-check before touching anything
    probe = [bytes(data[NBASE + REC * i:NBASE + REC * i + 30]).split(b"\x00")[0]
             for i in range(3)]
    if not all(nm and all(32 <= c < 127 for c in nm) for nm in probe):
        print("ABORT: name chain not at", hex(NBASE), "probe", probe)
        sys.exit(2)
    print("layout OK:", [nm.decode("cp437", "replace") for nm in probe])
    if not os.path.exists(bak):
        shutil.copy2(path, bak)
    for i, tag in ((1, 0xBEEF), (2, 0xCAFE)):
        for off in OFFS:
            struct.pack_into("<H", data, NBASE + REC * i + off, tag)
        print(f"rec{i} '{probe[i].decode('cp437','replace')}' sentinel {hex(tag)}")
    nm = NBASE
    old = bytes(data[nm:nm + NAMELEN])
    data[nm:nm + NAMELEN] = b"HERMESSEN" + b"\x00" * 21
    print("rec0 name", old.split(b"\x00")[0].decode("cp437", "replace"), "-> HERMESSEN")
    for v in (0xBEEF, 0xCAFE):
        b = struct.pack("<H", v)
        c = data.count(b)
        print(f"u16 {hex(v)} whole-file count after injection: {c}")
    open(path, "wb").write(bytes(data))
    print("wrote", path, len(data), "B")

if __name__ == "__main__":
    main()
