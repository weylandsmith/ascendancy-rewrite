#!/usr/bin/env python3
"""t105b — characterise the 0x74782 region + locate restree runtime rows.

Legs:
  1. Hexdump live region 0x74760..0x748a0 as u16/u32 streams (both phases).
  2. Stride hypotheses vs the CITED runtime cost law (OQ-013: runtime =
     file_cost * (2*row-20) for row>10, clamp 65000; rows<=10: runtime ==
     file cost — from docs/re/research.md 6 / restree law tool). Test strides
     75 (0x4b) and 45, base candidates 0x74782/0x74784/0x7478b-2.
  3. Find restree.txt row names in live RAM (all byte phases) -> runtime
     record base + stride.
  4. Planet census (locator law: +0x18 in {7,11,23,45,73} && +0x1a==+0x18+10):
     dump (own-planet) +0x42 vs +0x55 pairs across saves 59+60.sav.
"""
import os, re, struct, zipfile, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load(path):
    with zipfile.ZipFile(path) as z:
        m = z.read("Memory")
    hits = [mo.start() - (0x82bb0 + 0x73e40 + 8)
            for mo in re.finditer(rb"\x1e\x00Factory", m)]
    if len(set(hits)) != 1:
        raise SystemExit("harness-error: anchor not unique")
    return m, hits[0]

def file_rows():
    with open(os.path.join(ROOT, "extracted/ascend00/restree.txt"), errors="replace") as f:
        lines = f.read().splitlines()
    rows = []
    for ln in lines:
        t = ln.replace("^", " ").split()
        if len(t) >= 2 and not t[0].isdigit():
            name = "_".join(t[:2]) if not t[0][0].isupper() or len(t) > 1 else t[0]
            nums = []
            for tok in t:
                try: nums.append(int(tok))
                except ValueError: pass
            # cost column: file law used cost = second numeric? restree law
            # tool r1_restree_law knows; here capture all numerics
            rows.append((t[0] + (" " + t[1] if len(t) > 1 and t[1].isalpha() else ""), nums))
    return rows[:66]

def runtime_cost(fcost, row):
    if row > 10:
        return min(65000, fcost * (2 * row - 20))
    return fcost

def main():
    m, B = load(os.path.join(ROOT, "work/r1/playcap/save/60.sav"))
    idx = lambda X, n: m[B + 0x82BB0 + X: B + 0x82BB0 + X + n]
    rows = file_rows()
    print(f"file rows {len(rows)}; row0 {rows[0]}; row1 {rows[1]}; row11 {rows[11]}")

    print("\n-- region 0x74760..0x748a0 u16 (base-rel to 0x74782):")
    blob = idx(0x74760, 0x140)
    for k in range(0, 0x140, 2):
        a = 0x74760 + k
        v = struct.unpack("<H", blob[k:k+2])[0]
        print(f"  0x{a:x} ({a-0x74782:+d}): {v}")

    print("\n-- u32 phase 0:")
    for k in range(0, 0x140, 4):
        a = 0x74760 + k
        v = struct.unpack("<I", blob[k:k+4])[0]
        if v > 0x10000:
            print(f"  0x{a:x} ({a-0x74782:+d}): u32=0x{v:08x}")

    # stride hypotheses vs cost law
    fcosts = []
    for name, nums in rows:
        # OQ-013 file cost = u16 at restree file record +62? that is runtime
        # cost; file_cost column: restree.txt 2nd numeric is cost per t71 law
        # (row = name... 0 cost children 255). Take nums[1] as candidate.
        fcosts.append(nums[1] if len(nums) > 1 else None)
    for base in (0x74782, 0x74784, 0x74789, 0x7478b, 0x74739, 0x7473b):
        for stride in (45, 75):
            hit = miss = 0
            for i in range(66):
                if fcosts[i] is None: continue
                want = runtime_cost(fcosts[i], i)
                got = struct.unpack("<H", idx(base + stride * i, 2))[0]
                if got == want: hit += 1
                else: miss += 1
            print(f"base 0x{base:x} stride {stride}: cost-law {hit}/{hit+miss}")

    # restree names in live RAM
    print("\n-- restree runtime row search (row0/row2/row5 names):")
    for nm in (b"Orbital Structures", b"Interplanetary Exploration",
               b"Orbital^Structures", b"Tonklin Diary", b"Superconductivity"):
        occ = []
        pat = nm.replace(b" ", b"[\\x00-\\xff]?")  # '^' may be 0x1e or space
        for mo in re.finditer(re.escape(nm), m):
            occ.append(mo.start() - B)
        if nm == b"Superconductivity":
            print(f"  {nm!r}: raw hits at member-B rel {[hex(o) for o in occ[:12]]}")
        else:
            print(f"  {nm!r}: hits(rel B) {[hex(o) for o in occ[:8]]} (space form)")

    # planet census: find heap planets (locator law) in 60.sav
    print("\n-- planet census +0x42 vs +0x55 (owner0 planets):")
    for sav in ("59.sav", "60.sav"):
        mm, BB = load(os.path.join(ROOT, f"work/r1/playcap/save/{sav}"))
        # planet records live heap-side; scan member for stride-123-ish?
        # locator: +0x18 u16 in set, +0x1a == +0x18+10, +0x10 ptr sane,
        # owner at name+0x57? per STATE: slot arrays. Use known heap base law:
        # scan candidate bases by stepping 4 over member? too slow. Use the
        # t101 approach: find via restree? Simpler: planets are reached from
        # star table planet ptrs (name-anchored STAR table law) -- reuse
        # scripts/r1_record_census.py? For now: scan u16==cells pattern with
        # 123 stride from any base where +0x18==7.
        found = 0
        shown = 0
        for pos in range(0, len(mm) - 0x80, 4):
            try:
                c = struct.unpack("<H", mm[pos + 0x18:pos + 0x1a])[0]
                cap = struct.unpack("<H", mm[pos + 0x1a:pos + 0x1c])[0]
            except struct.error:
                continue
            if c in (7, 11, 23, 45, 73) and cap == c + 10:
                p0x42 = struct.unpack("<H", mm[pos + 0x42:pos + 0x44])[0]
                p0x55 = mm[pos + 0x55]
                owner = struct.unpack("<H", mm[pos + 0x54:pos + 0x56])[0] & 0xff
                if owner == 0 and p0x42 and found < 400:
                    found += 1
                    if shown < 12:
                        print(f"  {sav} member 0x{pos:x}: cells={c} +0x42={p0x42} +0x55={p0x55}")
                        shown += 1
        print(f"  {sav}: owner0 candidates with +0x42 nonzero: {found}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
