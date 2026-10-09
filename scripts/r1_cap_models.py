#!/usr/bin/env python3
"""r1_cap_models.py — POP-CAP model matrix on the byte-verified item table
(OQ-016 residual, S10 T33).

Recalc law as READ from the restored image (FUN_00038ba4, store tail
0x38ee3 MOV EAX,[ESP+0x1c] / MOV [EBX+0x4a],AX @0x38ee7, clamp 0..100
@0x38f01..0x38f18): accumulator starts at word[rec+0x55] (@0x38bd4), and per
slot in the array (loop head 0x38c7d/0x38c8b):

  if item byte == 0xFF:  (no accumulator change; terrain tallies only)
  word = flags slot+2 ;
  if (flags & 1) == 0:  goto 0x38c07   <- BYPASSES the IND term, but the
                          path 0x38c07..0x38c3b is itself guarded (item!=23,
                          !(slot flags&2), !(item flags&0x40)) and then adds
                          item byte +0x1 (=RES) into [ESP+0x18] (-> +0x4c),
                          NEVER the +0x1c accumulator.
  active path: 0x38cbe MOV CH,[EAX] -> IND byte +0 adds [ESP+0x28](+0x44);
               0x38d36 INC [ESP+0x24] and 0x38d3a JMP 0x38bf8; at 0x38bf8
               MOV ESI,[EAX]; SAR ESI,0x18; ADD EDI(=[ESP+0x1c]); -> the
               cap accumulator adds the item record's BYTE 4 = MPOP.

=> MODEL DIS (disassembly-exact): clamp(+0x55 + sum MPOP(active slots)),
   no flags&4 exclusion, Colony Base INCLUDED.
Models A/B (flags&4 skip, CB skip) kept from t31/t32 ledgers for comparison;
model E = no-active-filter; F = DIS + flags&4 skip.

Exit 0 if a model >= 99% on the WORLD-IDENTITY-DEDUPED corpus (one slot per
distinct first-record set — the 20 slots of a run are the same game), 1
otherwise, 2 harness error.
"""
import os, struct as st, sys, zipfile, collections, glob

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_income_law as IL
from r1_sav_scan import build_anchors, find_base

CB = 5


def models(m, rec, items):
    base, cells, cap, arr = rec
    r55 = st.unpack_from("<H", m, base + 0x55)[0]
    sDIS = sF = sA = sC = sE = r55
    for i in range(cap):
        it = m[arr + i * 4 + 1]
        if it == 0xFF or it >= IL.N_ITEMS:
            continue
        fl = st.unpack_from("<H", m, arr + i * 4 + 2)[0]
        mp = items[it]["mpop"]
        sE += mp
        if fl & 1:
            sDIS += mp                       # disassembly-exact
            if not (items[it]["flags"] & 4):
                sF += mp
            if it != CB:
                sC += mp
        else:
            if not (items[it]["flags"] & 4):
                sA += mp                     # old model A: INACTIVE add
    cl = lambda x: min(100, max(0, x))
    return cl(sDIS), cl(sF), cl(sA), cl(sC), cl(sE)


def main():
    anch = build_anchors(open(IL.PAY, "rb").read())
    root = sys.argv[1] if len(sys.argv) > 1 else "work/r1"
    tot = 0
    hits = collections.Counter()
    diffr = collections.defaultdict(collections.Counter)
    worlds = set()
    for run in sorted(glob.glob(os.path.join(root, "*"))):
        src = run if os.path.isdir(os.path.join(run, "save")) is False and \
            os.path.isdir(os.path.join(run, "ck")) else os.path.join(run, "save")
        if not os.path.isdir(src):
            continue
        seen_world = set()
        for f in sorted(glob.glob(os.path.join(src, "*.sav"))):
            try:
                m = zipfile.ZipFile(f).read("Memory")
            except Exception:
                continue
            v, _ = find_base(m, anch)
            if not v:
                continue
            B = v.most_common(1)[0][0]
            recs = IL.find_records(m)
            if len(recs) < 30:
                continue
            names = tuple(sorted(m[b + IL.NAME_AT:b + IL.NAME_AT + 24].split(b"\x00")[0]
                                 for (b, c_, cp, a) in recs))
            if names in seen_world:
                continue
            seen_world.add(names)
            items = IL.item_table(m, B)
            if items is None or not IL.names_ok(items):
                continue
            worlds.add((os.path.basename(run), len(recs)))
            for rec in recs:
                act = st.unpack_from("<H", m, rec[0] + 0x4a)[0]
                pDIS, pF, pA, pC, pE = models(m, rec, items)
                tot += 1
                for nm, p in (("DIS", pDIS), ("F", pF), ("A", pA), ("C", pC), ("E", pE)):
                    if p == act:
                        hits[nm] += 1
                    else:
                        diffr[nm][act - p] += 1
    print(f"samples {tot} over {len(worlds)} (run,nrec) keys: {sorted(worlds)}")
    for nm in ("DIS", "F", "A", "C", "E"):
        print(f"model {nm:3s}: {hits[nm]:6d} ({100.0*hits[nm]/max(1,tot):6.2f}%)  "
              f"fail diffs {dict(sorted(diffr[nm].items())) if diffr[nm] else '{}'}")
    best = max(hits.values()) if hits else 0
    return 0 if tot and best >= 0.99 * tot else (1 if tot else 2)


if __name__ == "__main__":
    sys.exit(main())
