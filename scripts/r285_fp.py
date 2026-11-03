#!/usr/bin/env python3
"""r285_fp.py — campaign fingerprint for slots (t285 flip forensics).

Identity law adapted from selfplay.md t266 (md5 over the ownership table). The
t266 fp joined star->owner-multiset; this variant hashes sorted (planet-name,
owner-byte) pairs from the SAME name-anchor locator (r1_income_law.find_records)
so it is comparable BETWEEN slots here but NOT to the banked t266 strings —
stated honestly. Equality of this fp across a turn jump => same campaign grew;
inequality => a different campaign entered RAM.

usage: r285_fp.py DIR_OR_SAV [DIR_OR_SAV...]
Exit 0 ran.
"""
import glob, os, struct, sys, zipfile, hashlib

ROOT = "/home/hrethric/projects/ascendancy"
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import r1_sav_scan as SS
import r1_slot as SL
import r1_income_law as IL

PAY = SL.load_payload(ROOT)
ANCH = SL.anchors_cached(ROOT, PAY)


def mem_of(path):
    with zipfile.ZipFile(path) as z:
        mem = z.read("Memory")          # FIXED: member is literally "Memory",
    B = SL.base_of(mem, ANCH)           # not namelist()[0] (CMOS sorts first)
    return mem, B


def report(path):
    try:
        mem, B = mem_of(path)
    except Exception as e:
        return f"{path:64s} UNREADABLE {type(e).__name__}"
    if B is None:
        return f"{path:64s} BASE UNRESOLVED"
    scal = SL.read_slot(path, mem, B)
    recs = IL.find_records(mem)
    pairs = sorted(
        (mem[b + IL.NAME_AT:b + IL.NAME_AT + 30].split(b"\x00")[0], mem[b + 0x57])
        for (b, cells, cap, ptr) in recs)
    fp = hashlib.md5(repr(pairs).encode()).hexdigest()[:8]
    owned = sum(1 for _, o in pairs if o != 0xFF)
    return (f"{os.path.basename(path):12s} turn={scal['turn']:5d} "
            f"V={scal['score_stars']:3d} recs={len(pairs):3d} owned={owned:3d} fp={fp}")


def main():
    for a in sys.argv[1:]:
        if os.path.isdir(a):
            for p in sorted(glob.glob(os.path.join(a, "*.sav"))):
                print(report(p))
        else:
            print(report(a))
    return 0


if __name__ == "__main__":
    sys.exit(main())
