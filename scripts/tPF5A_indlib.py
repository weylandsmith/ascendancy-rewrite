#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""tPF5-A INDICATOR-POPUP FRAME-LIB READ (no capture, no debugger).

LAW (disasm FUN_0x3db80 prologue, raw 0x3dbb3..0x3dbca):
    mov eax, 0x9f10c          ; shape-cache struct (INLINE in DSEG)
    mov dx,  word [0x6fd8e]   ; frame-lib id for the msg-50 indicator popup
    call 0x1fc34              ; (ctx, id) -> shape record for the composer
0x1fc34 (raw 0x1fcd3/0x1fcd9) joins the registry at ctx + 0x7d0 + id*0x32
(shp.md S2: cp437 NUL-terminated name), bound-checked id < 0xc8 (0x1fc62)
and gated by the loaded-flag dword at ctx + id*0x32 + 0x7cd (0x1fc8d..0x1fc99).

Pointer law (CLOSED, docs/re/r1-savestate.md): ds-relative D -> guest LINEAR
0x242000 + D -> Memory-member offset + H. Base self-verifies per save via the
639/479/640/480 + 'DATA' signature at ds:0x48518.

EXIT 0 = id read in >=1 save; 1 = negative everywhere; 2 harness.
"""
import glob, os, struct, struct as st, sys, zipfile
from collections import Counter

D_BASE = 0x242000
SIG_DIMS = (639, 479, 640, 480)
CTX = 0x9f10c          # shape-cache struct base (ds)
ID_INDPOPUP = 0x6fd8e  # the builder's frame-lib id slot (0x3dbbc)
ID_ROWDEF = 0x6fd80    # tPF-4 default row lib (control leg)


def bda_h(mem):
    return [h for h in range(0, 0x2000)
            if struct.unpack_from("<H", mem, h + 0x413)[0] == 0x280
            and struct.unpack_from("<H", mem, h + 0x44A)[0] == 80]


def main():
    slots = []
    for d in sys.argv[1:]:
        slots += sorted(glob.glob(os.path.join(d, "*.sav")))
    if not slots:
        print("harness-error: no .sav under", sys.argv[1:])
        return 2
    ids = Counter()
    rows = Counter()
    names = Counter()
    ok = 0
    for slot in slots:
        try:
            mem = zipfile.ZipFile(slot).read("Memory")
        except Exception as e:
            print(f"{slot}: unreadable ({e})")
            continue
        hs = bda_h(mem)
        if len(hs) != 1:
            print(f"{slot}: H ambiguous {hs}")
            continue
        H = hs[0]
        dims = struct.unpack_from("<4I", mem, D_BASE + 0x48518 + H)
        tag = mem[D_BASE + 0x48528 + H: D_BASE + 0x48528 + H + 4]
        if tuple(dims) != SIG_DIMS or tag != b"DATA":
            print(f"{slot}: signature mismatch dims={dims} tag={tag!r}")
            continue
        ok += 1
        ind = st.unpack_from("<H", mem, D_BASE + ID_INDPOPUP + H)[0]
        row = st.unpack_from("<H", mem, D_BASE + ID_ROWDEF + H)[0]
        ids[ind] += 1
        rows[row] += 1
        if ind < 0xc8:
            reg = D_BASE + CTX + 0x7d0 + ind * 0x32 + H
            raw = mem[reg:reg + 0x20].split(b"\0")[0]
            flag = st.unpack_from("<I", mem, D_BASE + CTX + ind * 0x32 + 0x7cd + H)[0]
            names[(raw.decode("cp437", "replace"), (flag >> 24) & 0xff)] += 1
        else:
            names[("OUT-OF-BOUND", 0)] += 1
    print(f"saves ok={ok}/{len(slots)}")
    print(f"ds:0x6fd8e (indicator-popup frame id): {dict(ids)}")
    print(f"ds:0x6fd80 (tPF-4 row default, control): {dict(rows)}")
    for (name, flag_hi), n in names.most_common():
        print(f"  registry id -> '{name}'  flag>>24={flag_hi}  x{n}")
    return 0 if ok and any(k != "OUT-OF-BOUND" for k in names) else 1


if __name__ == "__main__":
    sys.exit(main())
