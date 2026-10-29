#!/usr/bin/env python3
"""t185: OQ-019 magnetron identity — LOADED gizmo table + ship slot census.

Question (STATE.md t185): immediate 0x24 at image 0x4159a feeds
FUN_00049768(ship, edx) = first gizmo slot with cidx==edx, then order kind
is set to 5 (placement). WHICH loaded design-table row is index 36, and do
ships actually carry it?

Laws used (all previously cited):
  - loaded design table: member B + 0x82bb0 + 0x7650c, stride 0x6a, 76 rows,
    name ASCIIZ rec+0, category BYTE rec+0x32  (t87 loader FUN_00049074
    store sites; t101 correction 0x7653c-0x30).
  - base B: unique 'Factory' needle hit at +0x82bb0+0x73e40+8 (t101/t184).
  - ship rows: base B+0x82bb0+0x3a095 stride 0x162, count u32@0x43489>>16
    clamped 0x6b, owner = hi16 dword[+0x54] < 20 (t101 locator, t184).
  - gizmo ring: ship+0xab + 7*i, cidx u8 at +0 (0xFF empty), 25 slots (t184).

Exit 0 = loaded table names match file rows on every save AND census done;
1 = mismatch/census anomaly; 2 = harness broken.
"""
import struct, os, sys, zipfile, re, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "work", "r1")
TABLE = 0x7650C
NROWS = 76
STRIDE = 0x6A


def parse_file(path):
    lines = []
    for ln in open(path, "rb"):
        s = ln.decode("cp437", "replace").strip()
        if not s or s.startswith("#"):
            continue
        lines.append(s)
    out, i = [], 0
    while i < len(lines) - 1:
        nums = []
        try:
            nums = [int(x) for x in lines[i + 1].split()]
        except ValueError:
            nums = []
        ok = len(nums) >= 9
        if ok:
            out.append((lines[i].replace("^", " "), nums))
            i += 2
        else:
            i += 1
    return out


def saves():
    out = []
    for dp, dn, fn in os.walk(BASE):
        if os.path.basename(dp) in ("save", "ck"):
            for f in sorted(fn):
                if f.endswith(".sav"):
                    out.append(os.path.join(dp, f))
    return sorted(out)


def main():
    frows = parse_file(os.path.join(ROOT, "extracted", "ascend00", "gizmos.txt"))
    if len(frows) != NROWS:
        print("FATAL: file rows", len(frows)); return 2
    fname = [n for n, _ in frows]

    n_saved = 0
    name_mismatch = 0
    # per-save: does live row idx match file name; census accumulators
    carry_hist = collections.Counter()      # cidx -> #ships carrying (any save)
    ship_count = 0
    idx36_ships = 0
    idx60_ships = 0
    cat5_idx_named = None
    per_save = []

    for p in saves():
        try:
            m = zipfile.ZipFile(p).read("Memory")
        except Exception:
            continue
        hits = {mo.start() - (0x82bb0 + 0x73e40 + 8)
                for mo in re.finditer(rb"\x1e\x00Factory", m)}
        if len(hits) != 1:
            continue
        B = hits.pop()
        g = lambda X: B + 0x82bb0 + X
        n = struct.unpack_from("<I", m, g(0x43489))[0] >> 16
        n = min(n, 0x6b)

        # LEG 1: loaded table names vs file order
        bad = 0
        names = []
        for k in range(NROWS):
            a = g(TABLE + STRIDE * k)
            nm = m[a:a + 0x40].split(b"\0")[0].decode("cp437", "replace").replace("^", " ")
            names.append(nm)
            if nm.strip() != fname[k].strip():
                bad += 1
        name_mismatch += bad
        n_saved += 1
        if cat5_idx_named is None:
            cat5_idx_named = [(k, names[k]) for k in range(NROWS)
                              if m[g(TABLE + STRIDE*k + 0x32)] == 5]

        # LEG 2: slot census over owned ship rows
        s36 = s60 = 0
        seen_this_save = set()
        for k in range(n):
            r = g(0x3a095) + k * 0x162
            own = struct.unpack_from("<I", m, r + 0x54)[0] >> 16
            if own >= 20:
                continue
            ship_count += 1
            for i in range(25):
                c = m[r + 0xab + 7*i]
                if c != 0xFF:
                    if c not in seen_this_save:
                        seen_this_save.add(c)
                    carry_hist[c] += 1
                    if c == 36: s36 += 1
                    elif c == 60: s60 += 1
        idx36_ships += s36
        idx60_ships += s60
        per_save.append((os.path.relpath(p, BASE), n, bad, s36, s60))

    print(f"saves analysed: {n_saved}; total loaded-vs-file name mismatches: {name_mismatch}")
    print("\nCATEGORY-5 rows in the LOADED table (60.sav law, idx = live row = table order):")
    for k, nm in (cat5_idx_named or []):
        print(f"  idx {k:2d}  {nm}")
    print("\nper-save (relpath, ship_rows, name_mismatch, slots_with_cidx36, slots_with_cidx60):")
    for row in per_save:
        print("  %-46s n=%2d bad=%d c36=%d c60=%d" % row)
    print(f"\nSHIP-slot occurrences across saves: cidx36 total={idx36_ships}  cidx60 total={idx60_ships}")
    print("\ncensus of occupied cidx values (cidx -> slot-occurrences), sorted:")
    for c in sorted(carry_hist):
        nm = fname[c] if c < NROWS else "?"
        print(f"  {c:3d} {carry_hist[c]:5d}  {nm}")
    ok = name_mismatch == 0 and n_saved >= 10
    print("\nVERDICT:", "LOADED TABLE == FILE ORDER; CENSUS COMPLETE" if ok else "ANOMALY")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
