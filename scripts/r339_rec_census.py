#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t339 — magic-rec census of the state-16 family in the five state-16 saves
(work/r1/t299-leg-20261105-112859/save/43..47.sav) + two state-1 neighbours.
Law (banked): magic u32 0x12345678 at rec+0x00 (t316 fn 0x5712c file 0x57173);
NAME raw ASCII at rec+0x20 (t331 S50); rec+0x41 = registry slot-id (t316);
rec+0x63 = PARENT slot-id (t339 parser law 0x59012/0x5961d/0x5972b; t316
measured STATSHIPLST rec+0x63==95==FLEETWND slot 685/685).
Prints per-save per-record {name, +0x41, +0x43 (SENDMESSAGE), +0x63}.
Exit 0 always; exit 1 only if NO family record found in ANY save (instrument
failure, not a negative)."""
import struct, glob, sys, os

MAGIC = 0x12345678
FAMILY = ["My^Items", "Other^Items", "Pass", "Auto", "Repeat", "W", "S", "Z",
          "I", "BatControlWnd", "BatModeWnd", "BatListWnd"]
SAVES = sorted(glob.glob("work/r1/t299-leg-20261105-112859/save/4*.sav"))
print("saves:", [os.path.basename(s) for s in SAVES])

def name_at(data, a):
    end = data.find(b"\x00", a, a + 64)
    if end < 0:
        return ""
    try:
        return data[a:end].decode("ascii")
    except Exception:
        return ""

found_any = False
for path in SAVES:
    data = open(path, "rb").read()
    rows = []
    for name in FAMILY:
        pat = name.encode()
        off = 0
        while True:
            i = data.find(pat, off)
            if i < 0:
                break
            off = i + 1
            rec = None
            # t331 S50 law: NAME raw ASCII at rec+0x20, magic u32 at rec+0x00
            if i >= 0x24 and struct.unpack_from("<I", data, i - 0x20)[0] == MAGIC \
               and name_at(data, i) == name:
                rec = i - 0x20
            if rec is None:
                continue
            f41 = struct.unpack_from("<I", data, rec + 0x41)[0]
            f43 = struct.unpack_from("<I", data, rec + 0x43)[0]
            f63 = struct.unpack_from("<I", data, rec + 0x63)[0]
            rows.append((name, hex(rec), hex(f41), f43, hex(f63)))
            found_any = True
    print(f"\n{os.path.basename(path)} ({len(data)} bytes):")
    for r in rows:
        print(f"  {r[0]:16s} rec={r[1]} +0x41={r[2]} SM(+0x43)={r[3]:>5} +0x63={r[4]}")
    if not rows:
        print("  (no magic-verified family records)")

if not found_any:
    print("\nINSTRUMENT FAILURE: zero magic recs anywhere")
    sys.exit(1)
print("\nDONE exit 0")
sys.exit(0)
