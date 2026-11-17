#!/usr/bin/env python3
# t417b witness census: our OWN render graded MECHANICALLY against the vendor
# law (docs/re/_wip_t417.md F1-F5 + F8). Run with ~/tools/revenv/bin/python.
#   python3 scripts/t417b_witness_census.py /tmp/t417b_shots/status-open.png
import sys, sys as _s
import numpy as np
from PIL import Image

path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/t417b_shots/status-open.png"
im = np.asarray(Image.open(path).convert("RGB")).astype(int)
if im.shape[:2] != (480, 640):
    print(f"FAIL frame size {im.shape[:2]} != (480,640)"); sys.exit(1)

fails = 0
def chk(name, ok, detail=""):
    global fails
    print(("PASS " if ok else "FAIL ") + name + (" " + detail if detail else ""))
    if not ok: fails += 1

eq = lambda c: (im[:,:,0]==c[0]) & (im[:,:,1]==c[1]) & (im[:,:,2]==c[2])

# 1) NO k0 fingerprint: the never-painted backdrop's navy idx242 (12,32,48)
n242 = int(eq((12,32,48)).sum())
chk("no k0 navy (12,32,48) block", n242 < 1000, f"count={n242}")

# 2) Interior black: a text-free strip x200..280 y60..470 must be >=0.95 black
strip = im[60:471, 200:281].reshape(-1,3)
pblk = float(((strip.sum(1))==0).mean())
chk("interior strip black", pblk >= 0.95, f"p_black={pblk:.3f}")

# 3) Perimeter texture: each edge band >=0.85 non-black (texfrac family)
for name, sl in [("top y0..6", (slice(0,7), slice(0,640))),
                 ("bottom y472..479", (slice(472,480), slice(0,640))),
                 ("left x0..6", (slice(0,480), slice(0,7))),
                 ("right x633..639", (slice(0,480), slice(633,640)))]:
    band = im[sl].reshape(-1,3)
    frac = float((band.sum(1) != 0).mean())
    chk(f"perimeter {name} textured", frac >= 0.85, f"texfrac={frac:.3f}")

# 4) Header speckle: the census colours present in y8..36 x8..630
hdr = im[8:37, 8:631].reshape(-1,3)
for c in [(0,0,0), (8,12,16), (8,12,8), (8,28,49)]:
    m = (hdr == np.array(c)).all(1).sum()
    chk(f"speckle {c} present", m > 100, f"n={m}")
# green title (0,170,82) present (the port draws the header string in it)
g = int((hdr == np.array((0,170,82))).all(1).sum())
chk("header title green (0,170,82) present", g > 50, f"n={g}")

# 5) Divider: y46 solid (33,56,57) across x7..631; y47 black
row46 = im[46, 7:632]
solid46 = float((row46 == np.array((33,56,57))).all(1).mean())
chk("divider y46 solid (33,56,57)", solid46 >= 0.90, f"share={solid46:.3f}")
row47 = im[47, 8:630]
blk47 = float((row47.sum(1)==0).mean())
chk("y47 black below divider", blk47 >= 0.90, f"share={blk47:.3f}")

# 6) Left border x7 (33,56,57) over y48..470
col7 = im[48:471, 7]
b7 = float((col7 == np.array((33,56,57))).all(1).mean())
chk("left border x7 (33,56,57)", b7 >= 0.90, f"share={b7:.3f}")

# 7) NO row separators: no row y in 100..470 with >300 identical non-black px
seps = 0
for y in range(100, 471):
    r = im[y, 8:619]
    nz = r[r.sum(1) != 0]
    if len(nz) > 300:
        vals, cnts = np.unique(nz, axis=0, return_counts=True)
        if cnts.max() > 300: seps += 1
chk("no row separator lines", seps == 0, f"sep_rows={seps}")

print("VERDICT", "PASS" if fails == 0 else f"FAIL ({fails})")
sys.exit(0 if fails == 0 else 1)
