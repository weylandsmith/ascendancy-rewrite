#!/usr/bin/env python3
"""r1_terrain_authored.py — OQ-016 residue: scenario-AUTHORED vs rng-GENERATED
terrain (income-law.md S10 t29b, t30).

Call-site law [verified t30, restored disasm]:
  0x23ad2  MOV ECX,0x15 ; MOV EDI,[ESP+0x54] ; MOV ESI,0x88fe4 ; REP MOVSD
  -> a 21-dword scenario table (restored file 0x88fe4, one preset-row index
     per dword: 5,1,1,6,3,2,8,6,4,4,10,2,7,8,9,7,3,5,3,7,9) is copied to a
     stack buffer; 0x23b45 passes [ESP+0xc]=buffer+index into 0x37d80, where
     the index is byte[planet+7]-relocated. 0x37d80 stores it to word[+0x16]
     (@0x37e33, clamp->2 @0x37e39) and draws classes from 0x744f4+4*row.

Hypotheses:
  AUTHORED: first-save terrain per planet NAME is IDENTICAL across all
    capture runs (they resume one scenario file whose grids were built once)
    -> our captures never exercised 0x37d80; histogram mismatch vs +0x16
    rows is explained, S10 t29b residue closes for captures.
  GENERATED: terrain differs run-to-run.

Usage: python3 scripts/r1_terrain_authored.py [--runs 'work/r1/r1deep-*']
"""
import argparse, glob, os, os, struct as st, sys, zipfile, hashlib
import re, collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_sav_scan import build_anchors, find_base  # noqa: E402

REC, NAME_AT = 123, 0x24
NAME_RE = re.compile(rb"[A-Z][A-Za-z]{2,}(?: [IVX]+)?\x00")
N_ITEMS = 39
TABLE = [5,1,1,6,3,2,8,6,4,4,10,2,7,8,9,7,3,5,3,7,9]


def first_sav(run_dir):
    svs = glob.glob(os.path.join(run_dir, "save", "*.sav"))
    return min(svs, key=os.path.getmtime) if svs else None


def find_records(m):
    """Same mod-class name-anchor walk as r1_income_law.py (proven)."""
    starts = collections.defaultdict(list)
    pos = 0
    while True:
        mm = NAME_RE.search(m, pos)
        if not mm:
            break
        starts[mm.start() % REC].append(mm.start())
        pos = mm.start() + 1

    def good(base):
        cells = st.unpack_from("<H", m, base + 0x18)[0]
        cap = st.unpack_from("<H", m, base + 0x1a)[0]
        if not (7 <= cells <= 73) or cap != cells + 10:
            return False
        ptr = st.unpack_from("<I", m, base + 0x10)[0]
        if not (0 <= ptr and ptr + cap * 4 <= len(m)):
            return False
        return all(m[ptr + i * 4 + 1] == 0xFF or m[ptr + i * 4 + 1] < N_ITEMS
                   for i in range(cap))

    best = []
    for mod, s in starts.items():
        s = sorted(s)
        chain, cur = [], [s[0]]
        for a, b in zip(s, s[1:]):
            if b - a == REC:
                cur.append(b)
            else:
                if len(cur) > len(chain):
                    chain = cur
                cur = [b]
        if len(cur) > len(chain):
            chain = cur
        ok = sum(1 for n in chain if good(n - NAME_AT))
        if ok > sum(1 for n in best if good(n - NAME_AT)):
            best = chain
    return [n - NAME_AT for n in best if good(n - NAME_AT)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default="work/r1/r1deep-*")
    args = ap.parse_args()
    runs = sorted(d for d in glob.glob(args.runs) if os.path.isdir(d))
    per_planet = collections.defaultdict(dict)   # name -> run -> (hash,row,nb)
    for r in runs:
        s = first_sav(r)
        if not s:
            print(f"skip {r}: no sav")
            continue
        zf = zipfile.ZipFile(s)
        got = False
        for n in zf.namelist():
            raw = zf.read(n)
            if len(raw) < 0x100000:
                continue
            base = find_base(raw, build_anchors(raw))
            if base is None:
                continue
            recs = find_records(raw)
            if len(recs) < 40:
                continue
            for rb in recs:
                name_end = raw.index(b"\x00", rb + NAME_AT)
                name = raw[rb + NAME_AT:name_end].decode("cp437", "replace")
                row = st.unpack_from("<H", raw, rb + 0x16)[0]
                ncells = st.unpack_from("<H", raw, rb + 0x18)[0]
                capc = st.unpack_from("<H", raw, rb + 0x1a)[0]
                ptr = st.unpack_from("<I", raw, rb + 0x10)[0]
                cls = bytes(raw[ptr + i * 4] for i in range(ncells))
                nb = sum(1 for c in cls if c & 7)
                per_planet[name][os.path.basename(r)] = (
                    hashlib.md5(cls).hexdigest()[:10], row, nb, ncells)
            got = True
            break
        if not got:
            print(f"skip {r}: no base/records")
    same = diff = 0
    print(f"{'planet':18s} rows seen          hash variants")
    for name, d in sorted(per_planet.items()):
        hashes = {v[0] for v in d.values()}
        rows = {v[1] for v in d.values()}
        if len(d) < 2:
            continue
        if len(hashes) == 1:
            same += 1
        else:
            diff += 1
            print(f"{name:18s} {sorted(rows)}          {len(hashes)} VARIANTS")
    print(f"identical across runs: {same}   differing: {diff}")
    # barren battery by row using the +0x16 the SAVE records
    by_row = collections.defaultdict(lambda: [0, 0])
    for name, d in per_planet.items():
        for h, row, nb, ncells in d.values():
            by_row[row][0] += ncells - nb
            by_row[row][1] += ncells
    print("row  ncells   barren%  (w0 table {100,50,20,0,40,20,40,20,40,20,0})")
    for row in sorted(by_row):
        b, t = by_row[row]
        w0 = [100,50,20,0,40,20,40,20,40,20,0][row] if row < 11 else -1
        print(f"{row:3d} {t:7d}  {100*b/t:6.1f}  w0={w0}")


if __name__ == "__main__":
    main()
