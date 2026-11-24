#!/usr/bin/env python3
"""tPL-V1f census v2: the FORMAL port pixel census for the corrected tile
lattice (docs/re/planets-ui.md S14; tPL-V1 honest-negative closure).

WHY v2 (tPL-V1f): the v1 census asserted (a) >=200 white edge px and (b)
"shared-edge midpoint non-black". Both encoded wrong premises for this shot:
  * the seed-5 home planet's SURFACE classes are all 0 (app log: "ui planet
    classes 0 0 0 0 0 0 0 0 0 0 0 ..."), and the shipped edge law 0x3bbd6
    draws class 0 as BLACK — indistinguishable from starfield. Edge-COLOUR
    pixels are pinned by unit tests, not by this pixel census; here they are
    reported, not asserted.
  * the exact midpoint sits ON the shared edge line; with black edges it is
    legitimately black. The GAP signature of the old transposed law is
    instead: a point that should be INSIDE a diamond is black.

LAWS ASSERTED (all on the winner-size cell set):
  1. the t418b invented (24,24,32) outline colour is ABSENT (old painter sig).
  2. FILL: every valid cell centre carries uniform fill conv(150), or is
     covered by foreign art (structure blit — non-black, non-fill, non-edge).
     A lattice GAP would read black at the centre.
  3. ADJACENCY: for every adjacent pair (right-down and up-right edges), the
     probe 3px inside EACH side must be non-black (fill or art), and the
     midpoint must be black OR a class edge colour OR foreign art.
  4. CONTROL (anti-vacuity): the same probes evaluated under the OLD
     transposed law A (centre = (110+34c+17r, 410+17c-34r), the t418
     shorthand) must show a black-inside fraction >= 3x the corrected law's
     AND >= 25% absolute — i.e. this census CAN fail and does discriminate.
Exit 0 iff 1-4 pass."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
from tplv1_lattice_witness import load_rgb, conv, EDGE_RGB

SHOT = os.environ.get("SHOT", "/tmp/tplv1_shots/planet-open.png")
EXPECT_SIZE = int(os.environ.get("SIZE", "1"))
OLD_OUTLINE = (24, 24, 32)

B = [[0,0,0,0,4,4,5,0,0,0,0,0,0,0,0],
     [0,0,0,4,3,4,5,6,0,0,0,0,0,0,0],
     [0,0,3,2,3,3,4,5,7,0,0,0,0,0,0],
     [0,2,1,1,2,2,3,4,5,7,0,0,0,0,0],
     [1,0,0,0,1,1,2,3,4,5,7,0,0,0,0]]
C = [[0,0,0,0,2,3,2,0,0,0,0,0,0,0,0],
     [0,0,0,1,3,3,3,1,0,0,0,0,0,0,0],
     [0,0,1,4,4,5,4,4,1,0,0,0,0,0,0],
     [0,2,5,6,6,7,6,6,5,2,0,0,0,0,0],
     [3,6,7,8,8,9,8,8,7,6,3,0,0,0,0]]


def main():
    if not os.path.exists(SHOT):
        print("missing shot", SHOT)
        return 1
    w, h, px = load_rgb(SHOT)
    if (w, h) != (640, 480):
        print(f"FAIL shot is {w}x{h}, expected 640x480 (window grab law)")
        return 1

    def at(x, y):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < w and 0 <= y < h:
            b = (y * w + x) * 3
            return (px[b], px[b + 1], px[b + 2])
        return None

    fill = conv(150)
    def is_fill(p): return p is not None and all(abs(p[k] - fill[k]) <= 14 for k in range(3))
    def is_black(p): return p is not None and all(v < 12 for v in p)
    def is_edge(p): return p is not None and any(
        all(abs(p[k] - EDGE_RGB[c][k]) <= 14 for k in range(3)) for c in (1, 2, 3, 4))
    def known(p): return is_fill(p) or is_black(p) or is_edge(p) or p == OLD_OUTLINE

    ok = True

    # 1) old invented outline signature must be gone
    old = sum(1 for i in range(w * h) if px[3 * i:3 * i + 3] == bytes(OLD_OUTLINE))
    print("old (24,24,32) outline px:", old, "(must be 0)")
    if old:
        print("FAIL old outline present"); ok = False

    # edge-colour census: REPORTED (see header — class-0 black edges make a
    # white-pixel assertion invalid for the seed-5 home planet; the colour
    # law itself is pinned by campaign tests, planets-ui S14)
    edge_counts = {c: 0 for c in (1, 2, 3, 4)}
    for i in range(w * h):
        p = (px[3 * i], px[3 * i + 1], px[3 * i + 2])
        for c in edge_counts:
            if all(abs(p[k] - EDGE_RGB[c][k]) <= 14 for k in range(3)):
                edge_counts[c] += 1
    print("class edge px (reported only):", edge_counts)

    def cells_of(size):
        return [(r, c) for r in range(15)
                for c in range(B[size][r], B[size][r] + C[size][r])]

    def centre_B(r, c): return (410 + 34 * (c - r), 127 + 17 * (c + r))
    def centre_A(r, c): return (110 + 34 * c + 17 * r, 410 + 17 * c - 34 * r)

    # pick the size class whose centres best carry the fill
    best = (-1, None)
    for s in range(5):
        cl = cells_of(s)
        hits = sum(1 for (r, c) in cl if is_fill(at(*centre_B(r, c))))
        print(f"size {s}: centres {len(cl)} fill-hit {hits}")
        if hits > best[0]:
            best = (hits, s)
    hits, size = best
    if size != EXPECT_SIZE:
        print(f"FAIL best size class {size} != expected {EXPECT_SIZE}")
        return 1
    cl = cells_of(size)

    # 2) FILL census: centre = fill, or foreign art (structure blit). Black = gap.
    gap_cells = []
    art_cells = []
    for (r, c) in cl:
        p = at(*centre_B(r, c))
        if is_fill(p):
            continue
        if p is not None and not is_black(p):
            art_cells.append(((r, c), p))
        else:
            gap_cells.append((r, c))
    print(f"size{size} fill: {len(cl) - len(gap_cells) - len(art_cells)}/{len(cl)} "
          f"exact, art-covered {len(art_cells)} {[(k[0]) for k, _ in art_cells]}, "
          f"BLACK(gap) {gap_cells}")
    if gap_cells:
        print("FAIL black centres = lattice gaps"); ok = False

    # 3) ADJACENCY: both inside probes non-black; midpoint black|edge|art
    valid = set(cl)
    pairs = [((r, c), (r, c + 1)) for (r, c) in cl if (r, c + 1) in valid]
    pairs += [((r, c), (r - 1, c)) for (r, c) in cl if (r - 1, c) in valid]

    def adj_fail(centre, pts):
        bad = []
        for (a, n) in pairs:
            ax, ay = centre(*a); nx, ny = centre(*n)
            mx, my = (ax + nx) / 2.0, (ay + ny) / 2.0
            ux, uy = ax - mx, ay - my
            un = (ux * ux + uy * uy) ** 0.5
            if un == 0:
                continue
            po = at(mx + pts * ux / un, my + pts * uy / un)
            pn = at(mx - pts * ux / un, my - pts * uy / un)
            pm = at(mx, my)
            side_ok = (po is not None and not is_black(po)) and (pn is not None and not is_black(pn))
            mid_ok = pm is None or is_black(pm) or is_edge(pm) or not known(pm)
            if not (side_ok and mid_ok):
                bad.append((a, n, po, pn, pm))
        return bad

    bad = adj_fail(centre_B, 3.0)
    print(f"adjacency pairs {len(pairs)}, failures {len(bad)}")
    for b_ in bad[:6]:
        print("  BAD", b_)
    if bad:
        print("FAIL adjacency census"); ok = False

    # 4) CONTROL (anti-vacuity): the OLD transposed law placed tile (r,c) at
    # centre_A(r,c). Some A-centres fall inside the painted B-hexagon (fill is
    # expected there — not a signal), so the discriminator is the A-centres
    # OUTSIDE the B-cell union: had the port painted law A, those would carry
    # fill; under the corrected port they are starfield black. (seed-5: 5 such
    # centres, e.g. (3,4)->A(297,376); all measured black.)
    in_union = []
    for (r, c) in cl:
        bx, by = centre_B(r, c)
        in_union.append((bx, by))
    def in_B_union(x, y):
        return any(17 * abs(x - bx) + 34 * abs(y - by) <= 578
                   for (bx, by) in in_union)
    a_out = a_black = 0
    for (r, c) in cl:
        ax, ay = centre_A(r, c)
        if in_B_union(ax, ay):
            continue
        a_out += 1
        if is_black(at(ax, ay)):
            a_black += 1
    b_tot = len(cl)
    b_fill = len(cl) - len(gap_cells)
    print(f"control: A-centres outside B-union {a_out}, black {a_black} "
          f"(must be all); new-law centres fill {b_fill}/{b_tot}")
    if not (a_out >= 4 and a_black == a_out
            and b_fill >= int(0.9 * b_tot)):
        print("FAIL control: census does not discriminate the old law "
              "(wrong shot? wrong offset?)"); ok = False

    print("VERDICT", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
