#!/usr/bin/env python3
"""t202b helper: dump the 39-row planitem table (name, IND/RES/PROS/MPOP/
UPOP/COST/REQ/FLAGS) exactly as loadPlanItems indexes it, so the demolish
picker pins can name real items. Rows start after the '39 22 9' count triple
(docs/re/income-law.md; economy.cpp loadPlanItems)."""
import sys

PATH = sys.argv[1] if len(sys.argv) > 1 else "extracted/ascend00/planitem.txt"
lines = open(PATH, encoding="cp437", errors="replace").read().splitlines()
triple = next(i for i, l in enumerate(lines) if l.strip() == "39 22 9")
recs = []
pending = None
for l in lines[triple + 1:]:
    t = l.strip()
    if not t:
        continue
    toks = t.split()
    try:
        v = [int(x) for x in toks]
    except ValueError:
        pending = t.replace("^", " ")  # NAME line (full line, not first token)
        continue
    if pending is None:
        continue  # numeric row with no preceding name
    # Mirror loadPlanItems (economy.cpp:203-227): v = [IND RES PROS MPOP
    # UPOP COST REQ flagbitpos...], last == 255 terminator, flags = OR of
    # 1<<pos over v[7:-1].
    assert v[-1] == 255, (pending, v)
    flags = 0
    for pos in v[7:-1]:
        flags |= 1 << pos
    recs.append((pending, v[:7], flags))
    pending = None
    if len(recs) == 39:
        break

print(f"rows={len(recs)}")
for k, (n, v, fl) in enumerate(recs):
    ind, res, pros, mpop, upop, cost, req = v
    marks = []
    if fl & 0x40:
        marks.append("flags&0x40")
    if fl == 4:
        marks.append("orbitalclass4")
    print(f"{k:2d} {n:22s} ind={ind:2d} res={res:2d} pros={pros:2d} "
          f"mpop={mpop} upop={upop} cost={cost:3d} req={req:3d} fl={fl}"
          + (" [" + ",".join(marks) + "]" if marks else ""))
print("MPOP>0 items:", [k for k, (_, v, _) in enumerate(recs) if v[3] > 0])
print("UPOP==0 items:", [k for k, (_, v, _) in enumerate(recs) if v[4] == 0])
print("flags&0x40:", [k for k, (_, _, f) in enumerate(recs) if f & 0x40])
print("req==255:", [k for k, (_, v, _) in enumerate(recs) if v[6] == 255])
