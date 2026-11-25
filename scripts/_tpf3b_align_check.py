import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tplv1_lattice_witness as W

w, h, px = W.load_rgb(W.PNG)
ox, oy = W.ORIGIN
mask = bytearray(w * h)
for i in range(w * h):
    r, g, b = px[3*i], px[3*i+1], px[3*i+2]
    for c, rgb in W.EDGE_RGB.items():
        if abs(r-rgb[0]) <= W.TOL and abs(g-rgb[1]) <= W.TOL and abs(b-rgb[2]) <= W.TOL:
            if c != 0:
                mask[i] = 1 + c
            break

# monkeypatch the module's mask by re-implementing score EXACTLY as in-file
def centre(law, row, col):
    if law == "A":
        return (110 + 34*col + 17*row, 410 + 17*col - 34*row)
    return (410 + 34*(col-row), 127 + 17*(col+row))

B, C = W.B, W.C
cells = {s: [(row, col) for row in range(15)
             for col in range(B[s][row], B[s][row]+C[s][row])] for s in range(5)}
print("cell counts per size:", {s: len(cells[s]) for s in cells})

def score(law, s, dx, dy, subset=None):
    hit = tot = 0
    cl = subset if subset is not None else cells[s]
    for (row, col) in cl:
        cx, cy = centre(law, row, col)
        cx += dx; cy += dy
        for (x0, y0, x1, y1) in ((cx-34, cy, cx, cy-17), (cx, cy-17, cx+34, cy),
                                 (cx+34, cy, cx, cy+17), (cx, cy+17, cx-34, cy)):
            for t in range(8):
                sx = ox + x0 + (x1-x0)*t//7
                sy = oy + y0 + (y1-y0)*t//7
                if 0 <= sx < w and 0 <= sy < h:
                    tot += 1
                    if mask[sy*w+sx]:
                        hit += 1
                        break
    return (100.0*hit/tot) if tot else 0.0

print("replay law B s0 dx-23 dy48 :", round(score("B", 0, -23, 48), 1))
best = (-1, None)
for s in range(5):
    for dx in range(-80, 40):
        for dy in range(20, 90):
            sc = score("B", s, dx, dy, cells[s][::2])
            if sc > best[0]:
                best = (sc, (s, dx, dy))
print("coarse re-search best:", round(best[0], 1), best[1])
s, dx0, dy0 = best[1]
fine = (-1, None)
for dx in range(dx0-3, dx0+4):
    for dy in range(dy0-3, dy0+4):
        sc = score("B", s, dx, dy)
        if sc > fine[0]:
            fine = (sc, (s, dx, dy))
print("fine best:", round(fine[0], 1), fine[1])
open("/tmp/tpf3b_align.txt", "w").write(repr(fine))
