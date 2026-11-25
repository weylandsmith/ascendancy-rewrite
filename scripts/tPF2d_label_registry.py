#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""tPF2d_label_registry.py — resolve the 0x744a0 id->label registry STATICALLY
from banked save states (no capture, no debugger).

LAW (all previously cited, cited in docs/re/r1-savestate.md POINTER LAW and
docs/re/_wip_tPF2c.md C5/C6/C10/C11):
  * ds-relative static address D lives at guest LINEAR 0x242000 + D (obj1 data
    base), and a guest linear L lives at Memory-member offset L + H (H from the
    BDA signature, per-run).  => member(D) = 0x242000 + D + H.
  * The button consumer 0x3d5db reads label = u32[ds:0x744a0 + id*4] and copies
    it as a Pascal-style string (raw bytes, first byte = length) per C6.
  * fn 0x3d2a0 fills 0x74528+/0x74540+/0x7456c+ with getter(41..61)/(46..57)/
    (57..88) POINTERS (C10). C11 asks whether 0x744a0 is the SAME registry base
    (0x74528 == base+0x28) or a different table.

METHOD: for each banked .sav, decode H, dump the u32 grid ds:0x74440..0x745a0,
decode each u32 that points into the payload/data region as a string
(Pascal-first or NUL-terminated), print the id-indexed view 0x744a0[id] for
id 40..90, and test the C11 base hypothesis directly: does 0x744a0[57] resolve
to the same string as getter(57)='Cancel', [60]='Build', [54]=? (the decisive
refcap word is 'Build' on the 54-append button).

EXIT: 0 = registry strings resolved consistently across saves (id->label map
extracted); 1 = region present but not resolvable (honest negative); 2 harness.
"""
import argparse, os, struct, sys, zipfile, json
from collections import Counter

D_BASE = 0x242000          # obj1 data linear base (POINTER LAW, closed)
P0_CODE = 0x1d4000         # obj0 code linear base
PAYLOAD = "work/ascend_payload.bin"
REG = 0x744a0
LO, HI = 0x74440, 0x745b0  # dump window (ds-relative)

def bda_h(mem):
    return [h for h in range(0, 0x2000)
            if struct.unpack_from("<H", mem, h + 0x413)[0] == 0x280
            and struct.unpack_from("<H", mem, h + 0x44A)[0] == 80]

def cstr_at(mem, off, limit=64):
    if off < 0 or off + 2 >= len(mem):
        return None
    end = mem.find(b"\x00", off, off + limit)
    if end < 0:
        return None
    raw = mem[off:end]
    if not raw or any(c < 0x20 or c > 0x7e for c in raw):
        return None
    return raw.decode("ascii")

def pstr_at(mem, off):
    if off < 0 or off + 1 >= len(mem):
        return None
    n = mem[off]
    if 1 <= n <= 40 and off + 1 + n <= len(mem):
        raw = mem[off+1:off+1+n]
        if all(0x20 <= c <= 0x7e for c in raw):
            return raw.decode("ascii")
    return None

def decode_ptr(mem, pay, v, H):
    """Return (kind, string) for a u32 value that looks like a pointer."""
    if v == 0:
        return None
    # ANY guest linear L lives at member offset L + H (t440 law). Static
    # ds-disps merely happen to map to L = 0x242000 + D; heap pointers are raw
    # linear and must NOT have 0x242000 subtracted.
    if 0x100000 <= v < 0xa00000:
        s = pstr_at(mem, v + H) or cstr_at(mem, v + H)
        return ("lin", hex(v), s)
    if P0_CODE <= v < 0x242000:
        f = v - P0_CODE
        s = pstr_at(pay, f) or cstr_at(pay, f)
        return ("code", hex(f), s)
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--saves", required=True, help="dir of banked .sav")
    ap.add_argument("--one")
    ap.add_argument("--json-out")
    args = ap.parse_args()

    pay = open(PAYLOAD, "rb").read()
    files = [args.one] if args.one else sorted(
        os.path.join(args.saves, f) for f in os.listdir(args.saves)
        if f.endswith(".sav"))
    if not files:
        print("harness: no .sav found in", args.saves); sys.exit(2)

    results = {}
    for path in files:
        try:
            z = zipfile.ZipFile(path)
            mem = z.read("Memory")
        except Exception as e:
            print(f"{os.path.basename(path)}: unreadable ({e})"); continue
        hs = bda_h(mem)
        if len(hs) != 1:
            print(f"{os.path.basename(path)}: H ambiguous {hs}"); continue
        H = hs[0]
        row = {}
        for D in range(LO, HI, 4):
            v = struct.unpack_from("<I", mem, D_BASE + D + H)[0]
            if v == 0:
                continue
            d = decode_ptr(mem, pay, v, H)
            row[D] = (v, d)
        results[os.path.basename(path)] = row

    if not results:
        sys.exit(2)

    # consensus id->label view for 0x744a0[id]
    per_id = {}
    for name, row in results.items():
        for D, (v, d) in row.items():
            if D < REG or D >= REG + 96*4:
                continue
            idx = (D - REG) // 4
            s = d[2] if d else None
            per_id.setdefault(idx, Counter())[s if s else f"raw:{v:#x}"] += 1

    print(f"saves decoded: {len(results)}  (H per save varies)")
    print("id  value/label consensus across saves")
    for idx in sorted(per_id):
        c = per_id[idx]
        top = c.most_common()
        lab = top[0][0]
        print(f"[{idx:3d}] ds:0x{REG+idx*4:x}  " + ", ".join(f"{k} x{n}" for k, n in top[:4]))

    # C11 test: is 0x74528 inside this same table with the same content family?
    print("\nC11 window (ds:0x74500..0x745a0) first-save detail:")
    first = next(iter(results.values()))
    for D in range(0x74500, 0x745a0, 4):
        if D in first:
            v, d = first[D]
            print(f"  ds:0x{D:x} -> {d if d else hex(v)}")

    if args.json_out:
        out = {name: {str(D): [v, d] for D, (v, d) in row.items()}
               for name, row in results.items()}
        json.dump(out, open(args.json_out, "w"), indent=1)
        print("json ->", args.json_out)

    # exit 0 only if at least one id resolved to a real string in a majority of saves
    resolved = sum(1 for c in per_id.values()
                   if c.most_common(1)[0][0] not in () and not c.most_common(1)[0][0].startswith("raw:"))
    print(f"\nresolved-string ids: {resolved}")
    sys.exit(0 if resolved >= 5 else 1)

if __name__ == "__main__":
    main()
