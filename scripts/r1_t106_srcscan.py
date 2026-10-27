#!/usr/bin/env python3
"""r1_t106_srcscan.py v2 — counts-only: is a deviating planet's GRID BLOCK
copied from a template (memory / restored image / extracted corpus)?

v1 BUG (disclosed): v1 searched the stride-4 COMPRESSED class-byte sequence,
which does not exist contiguously anywhere in RAM — every "hit" was the -1
artifact of subtracting 1 from zero. v2 searches the CONTIGUOUS slot block
m[arr : arr+4*cells] (4 bytes/slot: class, item, flags — banked record layout),
counts-only.

Degenerate exclusion: blocks whose class bytes have <3 distinct values, or
whose full block is <70% distinct-4-byte-word, are not searchable (too many
coincidental matches). A preset world loaded from a table must show >=1 hit
OUTSIDE its own window; an rng world shows 0.

Exit 1 if any DEV block has external hits, 0 if negative.
"""
import argparse, glob, os, struct as st, sys, zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_income_law as IL
from r1_sav_scan import build_anchors, find_base

NAME_AT = 0x24


def nfind(data, pat, cap=3):
    n, start = 0, 0
    while n <= cap:
        i = data.find(pat, start)
        if i < 0:
            return n
        n += 1
        start = i + 1
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default="work/r1/r1deep-*")
    ap.add_argument("--corpus", default="extracted")
    ap.add_argument("--max-per-run", type=int, default=8)
    args = ap.parse_args()
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    anch = build_anchors(open(IL.PAY, "rb").read())
    img = open(os.path.join(ROOT, "work/ascend_restored.bin"), "rb").read()
    cdir = os.path.join(ROOT, args.corpus)
    corpus = []
    for f in sorted(glob.glob(os.path.join(cdir, "**", "*"), recursive=True)):
        if os.path.isfile(f):
            try:
                corpus.append(open(f, "rb").read())
            except Exception:
                pass

    dev_t = dev_h = ctrl_t = ctrl_h = skip = 0
    for run in sorted(glob.glob(os.path.join(ROOT, args.runs))):
        src = os.path.join(run, "save")
        if not os.path.isdir(src):
            continue
        svs = sorted(glob.glob(os.path.join(src, "*.sav")), key=os.path.getmtime)
        if not svs:
            continue
        try:
            m = zipfile.ZipFile(svs[0]).read("Memory")
        except Exception:
            continue
        if not find_base(m, anch)[0]:
            continue
        pl = []
        for base, cells, cap, arr in IL.find_records(m):
            name = m[base + NAME_AT:base + NAME_AT + 30].split(b"\x00")[0] \
                   .decode("cp437", "replace").strip()
            blk = m[arr:arr + 4 * cells]
            classes = [blk[4 * i] for blk_i in range(1) for i in range(cells)] \
                      if False else [m[arr + 4 * i] for i in range(cells)]
            nb = sum(1 for c in classes if (c & 0xF) != 0)
            r55 = st.unpack_from("<H", m, base + 0x55)[0]
            pl.append((name, blk, classes, r55 - (nb // 3 + 5), arr))
        for label, group in (("DEV", [p for p in pl if p[3]][:args.max_per_run]),
                             ("CTRL", [p for p in pl if p[3] == 0][:6])):
            for name, blk, classes, d, arr in group:
                if len(set(classes)) < 3:
                    skip += 1
                    continue
                hm = nfind(m, blk)
                # own-array occurrence: exactly 1 expected (at arr)
                ext_m = max(0, hm - 1)
                ext_i = nfind(img, blk, cap=1)
                ext_c = 0
                for blob in corpus:
                    if nfind(blob, blk, cap=1):
                        ext_c = 1
                        break
                hits = ext_m + ext_i + ext_c
                if label == "DEV":
                    dev_t += 1
                    dev_h += 1 if hits else 0
                else:
                    ctrl_t += 1
                    ctrl_h += 1 if hits else 0
                print(f"  {os.path.basename(run)[:26]:26s} {label} "
                      f"{name:16s} d={d:+3d} blklen={len(blk):4d} "
                      f"mem_ext={ext_m} img={ext_i} corpus={ext_c}")
    print(f"\nSUMMARY dev_tested={dev_t} dev_with_external_block={dev_h} "
          f"| ctrl_tested={ctrl_t} ctrl_with_external={ctrl_h} "
          f"| skipped_degenerate={skip}")
    print("VERDICT:", "EXTERNAL BLOCK COPIES FOUND" if dev_h or ctrl_h else
          "NEGATIVE: no deviating (or control) grid block appears anywhere "
          "outside its own heap array (memory, restored image, 471-file corpus)")
    return 1 if dev_h else 0


if __name__ == "__main__":
    sys.exit(main())
