#!/usr/bin/env python3
"""t188: FRAME + SCALE adjudication for the flight corpus (OQ-019).

Q1 (frame): are ship xyz [+0x9e] and star-table f32 [name-0x14] the SAME
    world frame? For each trusted save, find each live ship's nearest star
    and the distance; a lane-transit arrival should land the ship AT (or
    walk-target-toward) a STAR RECORD position, and the 1100-2500u
    'discontinuities' should equal star-to-star distances if real transit.
Q2 (scale): per-turn lane step magnitudes 14/28/56 vs MOVES=4/6/12, and
    owner-1 4.67=14/3. If walk law is per-day walk=min(d,MOVES) sugar and
    1 sugar=160 world units, then 14 u/day => 0.0875 sugar/day — REFUTED
    unless a second divisor exists. Measure the divisor candidates against
    the drive stat (design table) and the species law.

Reads: .sav Memory zips via anchor law (r1_sav_scan), star grid
(r1_star_table law), ship grid stride 0x162 (t101 locator law).
"""
import sys, os, zipfile, struct, math, collections, re
sys.path.insert(0, "/home/hrethric/projects/ascendancy/scripts")
from r1_sav_scan import build_anchors, find_base

PAY = "/home/hrethric/projects/ascendancy/work/ascend_payload.bin"
STRIDE_S, S_XYZ = 96, -0x14
SNAME_RE = rb"[A-Z][a-z]{2,15}\x00"
NAME_ANCHOR_HINT = 0x255be1
SHIP_STRIDE = 0x162

def load(f):
    mem = zipfile.ZipFile(f).read("Memory")
    v, _ = find_base(mem, build_anchors(open(PAY, "rb").read()))
    H = v.most_common(1)[0][0] - 0x1BF450
    # star names
    best = []
    for delta in range(0, 0x21):
        for sign in (-1, 1):
            cand = NAME_ANCHOR_HINT + sign * delta
            names, k = [], 0
            while True:
                p = cand + k * STRIDE_S + H
                m = re.match(SNAME_RE, mem[p:p+18])
                if not m: break
                names.append((m.group()[:-1].decode(), struct.unpack_from("<3f", mem, p + S_XYZ)))
                k += 1
                if k > 60: break
            if len(names) > len(best): best = names
    return mem, H, best

def ships(mem, H):
    # t101 locator law: find ship array by scanning for records whose +0x58 in
    # {1..5} and +0x9e f32 triple sane; anchor on the known ship-array hint
    # from the watcher raw window base. Watcher window == record start.
    pass

def main():
    sdir = "/home/hrethric/projects/ascendancy/work/r1/playcap/save"
    files = sorted(os.listdir(sdir), key=lambda f: os.stat(os.path.join(sdir, f)).st_mtime)
    mem, H, stars = load(os.path.join(sdir, files[-1]))
    print("save", files[-1], "H", H, "stars", len(stars))
    xs = [s[1][0] for s in stars]; ys = [s[1][1] for s in stars]; zs = [s[1][2] for s in stars]
    print("star coord extent x[%.0f,%.0f] y[%.0f,%.0f] z[%.0f,%.0f]" % (min(xs),max(xs),min(ys),max(ys),min(zs),max(zs)))
    dd = []
    for i in range(len(stars)):
        for j in range(i+1, len(stars)):
            a, b = stars[i][1], stars[j][1]
            dd.append(math.dist(a, b))
    dd.sort()
    print("star-star dist: min %.0f p25 %.0f med %.0f p75 %.0f max %.0f" %
          (dd[0], dd[len(dd)//4], dd[len(dd)//2], dd[3*len(dd)//4], dd[-1]))
    # bucket around the observed 'jump' magnitudes 1100-2500
    jumps = [1372, 1379, 1268, 1300, 1236, 1554, 1224, 1256, 1384, 1076, 1512, 1374, 1172, 1905, 1969, 1108, 1122, 1732, 1796, 1038, 1764, 448, 480, 496, 346, 196]
    for jm in jumps:
        near = min(dd, key=lambda d: abs(d-jm))
        # count star pairs within +-2u of jm
        cnt = sum(1 for d in dd if abs(d-jm) < 2)
        print(f"  observed {jm:5d}u: nearest star-star {near:7.1f} (|d|={abs(near-jm):6.1f}), pairs within 2u: {cnt}")

main()
