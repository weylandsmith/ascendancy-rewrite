#!/usr/bin/env python3
"""tPL-V1 lattice-law witness: vendor capture vs the two candidate pitch laws.

CANDIDATE A (the PORT law, planetview.cpp:129, t418 shorthand):
    centre = (110 + 34*col + 17*row, 410 + 17*col - 34*row)
    col step (34,17), row step (17,-34) -> |det| = 1445 > diamond area 1156
    => 80% coverage: GAPS (the D26 complaint).
CANDIDATE B (re-derived this iteration from the 24-byte vertex records at
    work/t198_planwin.asm 0x3c211..0x3c274: fields 0x260/0x264 carry
    (+-0x22, 0/+0x11/+0x22) offsets, colour slots 0x268/0x280/0x298/0x2b0
    all = 0x960000, stride 0x18):
    f0 = 410 + 34*(col-row)   f1 = 110 + 17*(col+row)
    vertices V0=(f0,f1) V1=(f0+34,f1+17) V2=(f0,f1+34) V3=(f0-34,f1+17)
    => centre (f0, f1+17); col step (34,17), row step (-34,17), |det| = 1156
    == the diamond area => EXACT tiling, ZERO gaps.

Measures the vendor tile-EDGE colours (class law 0x3bbd6..0x3bc52: game.pal
idx 0 black / 12 white / 117 red / 146 green / 255 blue, converted 6->8 bit)
in work/r1/screens/t254/02_planet_detail.png, then brute-forces a lattice
alignment for both candidates and reports edge-support. Exit 0 iff B beats A
by >= 10 points; 1 iff A wins; 2 inconclusive.
"""
import os, struct, struct as st, sys, zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PNG = os.path.join(ROOT, "work/r1/screens/t254/02_planet_detail.png")
ORIGIN = (80, 100)          # t428 F9 [verified]: png (80,100) == screen (0,0)


def load_rgb(path):
    """Minimal PNG -> (w, h, bytearray rgb24). Supports depth 8, colortype 2/3/6."""
    data = open(path, "rb").read()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "not a png"
    pos, idat = 8, b""
    w = h = 0
    depth = color = 0
    pal = b""
    while pos + 8 <= len(data):
        ln, typ = st.unpack_from(">I4s", data, pos)
        body = data[pos + 8:pos + 8 + ln]
        if typ == b"IHDR":
            w, h, depth, color = st.unpack_from(">IIBB", body, 0)
        elif typ == b"PLTE":
            pal = body
        elif typ == b"IDAT":
            idat += body
        elif typ == b"IEND":
            break
        pos += 12 + ln
    assert (depth == 8 and color in (2, 3, 6)) or (depth == 16 and color == 2), \
        f"depth {depth} color {color}"
    raw = zlib.decompress(idat)
    nch = 3 if color == 2 else (1 if color == 3 else 4)
    if depth == 16:
        nch = 6
    stride = w * nch
    out = bytearray(w * h * 3)
    prev = bytearray(stride)
    p = 0
    for y in range(h):
        f = raw[p]; p += 1
        line = bytearray(raw[p:p + stride]); p += stride
        if f == 1:
            for i in range(nch, stride):
                line[i] = (line[i] + line[i - nch]) & 0xFF
        elif f == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 0xFF
        elif f == 3:
            for i in range(stride):
                a = line[i - nch] if i >= nch else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 0xFF
        elif f == 4:
            for i in range(stride):
                a = line[i - nch] if i >= nch else 0
                b = prev[i]
                c = prev[i - nch] if i >= nch else 0
                pp = a + b - c
                pa, pb, pc = abs(pp - a), abs(pp - b), abs(pp - c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 0xFF
        base = y * w * 3
        if color == 3:
            for x in range(w):
                j = 3 * line[x]
                out[base + 3 * x:base + 3 * x + 3] = pal[j:j + 3]
        elif color == 2 and depth == 8:
            out[base:base + stride] = line
        elif color == 2 and depth == 16:
            for x in range(w):
                out[base + 3 * x:base + 3 * x + 3] = bytes(
                    (line[6 * x], line[6 * x + 2], line[6 * x + 4]))
        else:
            for x in range(w):
                out[base + 3 * x:base + 3 * x + 3] = line[4 * x:4 * x + 3]
        prev = line
    return w, h, out


def palconv():
    raw = open(os.path.join(ROOT, "extracted/ascend01/data/game.pal"), "rb").read()
    assert len(raw) == 768, len(raw)
    return bytes(((v << 2) | (v >> 4)) for v in raw)


PC = palconv()
def conv(i):
    return (PC[3 * i], PC[3 * i + 1], PC[3 * i + 2])

EDGE_IDX = {0: 0, 1: 12, 2: 117, 3: 146, 4: 255}   # tile class -> game.pal index
FILL_IDX = {0: 7, 2: 8, 3: 9, 4: 10, 1: 13}
EDGE_RGB = {c: conv(i) for c, i in EDGE_IDX.items()}
FILL_RGB = {c: conv(i) for c, i in FILL_IDX.items()}

# grid B / C (planitem.txt tokens 45..119 / 120..194, t418 F1 verbatim)
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

TOL = 12


def main():
    w, h, px = load_rgb(PNG)
    ox, oy = ORIGIN
    # edge-hit mask over the whole png (1 = within TOL of a NON-BLACK vendor
    # edge colour; class-0 tiles draw black edges which are indistinguishable
    # from the starfield, so black is deliberately excluded from scoring)
    mask = bytearray(w * h)
    counts = {c: 0 for c in EDGE_RGB}
    for i in range(w * h):
        r, g, b = px[3 * i], px[3 * i + 1], px[3 * i + 2]
        for c, rgb in EDGE_RGB.items():
            if abs(r - rgb[0]) <= TOL and abs(g - rgb[1]) <= TOL and abs(b - rgb[2]) <= TOL:
                counts[c] += 1
                if c != 0:
                    mask[i] = 1 + c
                break
    print("vendor edge-colour px (class: count):", counts, f"total {sum(counts.values())}")
    if sum(counts.values()) < 200:
        print("VERDICT INCONCLUSIVE: no vendor edge colours present")
        return 2

    def centre(law, row, col):
        if law == "A":
            return (110 + 34 * col + 17 * row, 410 + 17 * col - 34 * row)
        return (410 + 34 * (col - row), 127 + 17 * (col + row))

    cells = {s: [(row, col) for row in range(15)
                 for col in range(B[s][row], B[s][row] + C[s][row])] for s in range(5)}

    def score(law, s, dx, dy, subset=None):
        hit = tot = 0
        cl = subset if subset is not None else cells[s]
        for (row, col) in cl:
            cx, cy = centre(law, row, col)
            cx += dx; cy += dy
            for (x0, y0, x1, y1) in ((cx - 34, cy, cx, cy - 17),
                                     (cx, cy - 17, cx + 34, cy),
                                     (cx + 34, cy, cx, cy + 17),
                                     (cx, cy + 17, cx - 34, cy)):
                for t in range(8):
                    sx = ox + x0 + (x1 - x0) * t // 7
                    sy = oy + y0 + (y1 - y0) * t // 7
                    if 0 <= sx < w and 0 <= sy < h:
                        tot += 1
                        if mask[sy * w + sx]:
                            hit += 1
                            break
        return (100.0 * hit / tot) if tot else 0.0

    # centroid of non-black edge pixels in the FIELD region (below the strip)
    field = [i for i in range(w * h) if mask[i] and (i // w) >= oy + 106]
    if len(field) < 50:
        print("VERDICT INCONCLUSIVE: <50 non-black edge px in the field")
        return 2
    exs = [i % w for i in field]
    eys = [i // w for i in field]
    ecx, ecy = sum(exs) / len(exs), sum(eys) / len(eys)
    print(f"field edge px n={len(exs)} centroid png=({ecx:.0f},{ecy:.0f}) "
          f"screen=({ecx-ox:.0f},{ecy-oy:.0f})")

    best = {}
    for law in ("A", "B"):
        bb = (-1.0, (0, 0, 0, "none"))
        for s in range(5):
            # lattice centroid at dx=dy=0
            cs = [centre(law, r, c) for (r, c) in cells[s]]
            lcx = sum(p[0] for p in cs) / len(cs)
            lcy = sum(p[1] for p in cs) / len(cs)
            gx0, gy0 = int(ecx - ox - lcx), int(ecy - oy - lcy)
            sub = cells[s][::2]
            for dx in range(gx0 - 34, gx0 + 35, 2):
                for dy in range(gy0 - 34, gy0 + 35, 2):
                    sc = score(law, s, dx, dy, sub)
                    if sc > bb[0]:
                        bb = (sc, (s, dx, dy, "coarse"))
            # refine the winner's neighbourhood at 1px on the full cell set
            _, (s2, dx2, dy2, _ph) = bb
            for dx in range(dx2 - 3, dx2 + 4):
                for dy in range(dy2 - 3, dy2 + 4):
                    sc = score(law, s2, dx, dy)
                    if sc > bb[0]:
                        bb = (sc, (s2, dx, dy, "fine"))
        best[law] = bb
        print(f"law {law}: best edge support {bb[0]:.1f}% at (size,dx,dy,phase)={bb[1]}")
    a, b = best["A"][0], best["B"][0]
    print("det test: law A |det|=1445 (80% coverage -> gaps), law B |det|=1156 == diamond area (exact tiling)")
    if b >= a + 10:
        print("VERDICT PASS: vendor lattice == candidate B")
        return 0
    if a >= b + 10:
        print("VERDICT FAIL: vendor lattice matches law A; candidate B refuted")
        return 1
    print("VERDICT INCONCLUSIVE: within 10 points")
    return 2


if __name__ == "__main__":
    sys.exit(main())
