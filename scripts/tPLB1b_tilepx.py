#!/usr/bin/env python3
# tPL-B1b witness helper: parse the app's "home-cb cell C size S surf N" log
# line and print FOUR integers: adjacent-tile px, non-adjacent-tile px (lattice
# law F1/F2: cell = cum+C walk, px = 110+c*34+r*17 / 410+c*17-r*34 — the SAME
# tables as scripts/t418b_witness_census.py, never eyeballed). If every
# surface cell is adjacent (tiny grids), prints "ADJ px px NOADJ" with NOADJ
# replaced by -1 -1 (the refuse leg is then vacuous — the witness says so).
import re, sys

B = [[0,0,0,0,4,4,5,0,0,0,0,0,0,0,0],
     [0,0,0,4,3,4,5,6,0,0,0,0,0,0,0],
     [0,0,3,2,3,3,4,5,7,0,0,0,0,0,0],
     [0,2,1,1,2,2,3,4,5,7,0,0,0,0,0],
     [1,0,0,0,1,1,2,3,4,5,7,0,0,0,0]]
C = [[0,0,0,0,2,3,2,0,0,0,0,0,0,0,0],
     [0,0,0,1,3,3,3,1,0,0,0,0,0,0,0],
     [0,0,1,4,4,5,4,4,1,0,0,0,0,0,0],
     [0,2,5,6,6,7,6,6,5,2,0,0,0,0],
     [3,6,7,8,8,9,8,8,7,6,3,0,0,0,0]]

log = open(sys.argv[1]).read()
m = re.search(r"home-cb cell (\d+) size (\d+) surf (\d+)", log)
if not m:
    sys.exit(1)
cb, size, surf = map(int, m.groups())

def rowcol(cell):
    cum = 0
    for r in range(15):
        if cum + C[size][r] > cell:
            return r, cell - cum + B[size][r]
        cum += C[size][r]
    sys.exit(1)

def cellat(r, c):
    if r < 0 or r >= 15 or c < B[size][r] or c >= B[size][r] + C[size][r]:
        return -1
    return sum(C[size][:r]) + c - B[size][r]

def px(r, c):
    return 110 + c * 34 + r * 17, 410 + c * 17 - r * 34

r0, c0 = rowcol(cb)
nbrs = {cellat(r0 + 1, c0), cellat(r0 - 1, c0),
        cellat(r0, c0 - 1), cellat(r0, c0 + 1)}
nbrs = {n for n in nbrs if n >= 0 and n != cb}
if not nbrs:
    sys.exit(1)
adj = sorted(nbrs)[0]
mis = next((x for x in range(surf) if x not in nbrs and x != cb), -1)
ax, ay = px(*rowcol(adj))
if mis < 0:
    print(ax, ay, -1, -1)
else:
    mx, my = px(*rowcol(mis))
    print(ax, ay, mx, my)
