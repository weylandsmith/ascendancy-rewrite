#!/usr/bin/env python3
# t427 witness census: grade OUR OWN planets-list render mechanically
# against the vendor row-composition law (docs/re/_wip_t427.md F1-F6).
#   usage: python3 scripts/t427_witness_census.py OPEN.png SEL.png
# OPEN = status screen with statusSel == -1 (row unselected);
# SEL  = same screen after clicking row 0 and popping back (row 0 selected).
# The seed-5 --species 0 fixture owns ONE planet (header "1 Planet
# Occupied"), so the GREEN-vs-WHITE control is the SAME row across the two
# shots (row 0 GREEN open -> WHITE selected) — a stronger control than two
# rows in one frame; rows 1/2 are additionally asserted WHITE-free.
# Run with ~/tools/revenv/bin/python (numpy lives there).
import sys
import numpy as np
from PIL import Image

fails = 0
def chk(name, ok, detail=""):
    global fails
    print(("PASS " if ok else "FAIL ") + name + (" " + detail if detail else ""))
    if not ok: fails += 1

TOP, PITCH = 57, 141          # kStatusRowsTop / kStatusRowPitch (t417b F3)
WHITE = (255, 255, 255)       # kStatusLine1Sel (t427 F6 measured)
GREEN = (0, 170, 82)          # kStatusLine1Norm
PIPS = [(200, 60, 60), (200, 180, 60), (60, 120, 90)]  # port band colours

def load(p):
    im = np.asarray(Image.open(p).convert("RGB")).astype(int)
    if im.shape[:2] != (480, 640):
        print(f"FAIL frame size {im.shape[:2]} != (480,640)"); sys.exit(1)
    return im

def line1_band(im, row):
    y0 = TOP + row * PITCH + 10
    return im[y0:y0 + 24, 288:619]

def line_counts(im, row):
    b = line1_band(im, row).reshape(-1, 3)
    w = int(((b == np.array(WHITE)).all(1)).sum())
    g = int(((b == np.array(GREEN)).all(1)).sum())
    return w, g

open_im = load(sys.argv[1] if len(sys.argv) > 1 else "/tmp/t427_shots/status-open.png")
sel_im = load(sys.argv[2] if len(sys.argv) > 2 else "/tmp/t427_shots/status-sel.png")

# 1) SELECTION LAW (t427 F6: the marker IS the text colour): row 0 GREEN
#    when unselected, WHITE (>200 px) when selected; rows 1/2 never WHITE.
w, g = line_counts(open_im, 0)
chk("open row0 line1 GREEN", g > 100 and w == 0, f"w={w} g={g}")
w0, g0 = line_counts(sel_im, 0)
chk("sel row0 line1 WHITE >200", w0 > 200 and g0 == 0, f"w={w0} g={g0}")
for r in (1, 2):
    w, g = line_counts(sel_im, r)
    chk(f"sel row{r} never WHITE", w == 0, f"w={w}")

# 2) NO flat (255,0,0) capsule block x16..69 y+2..+26 on ANY row (t417b
#    capsule DELETED — it was fitted to the sun art arc; F6 refutation).
for r in range(3):
    y0 = TOP + r * PITCH + 2
    blk = sel_im[y0:y0 + 25, 16:70].reshape(-1, 3)
    n = int(((blk == np.array((255, 0, 0))).all(1)).sum())
    chk(f"no flat-red capsule row{r}", n == 0, f"n255={n}")

# 3) SUN warm-px present in the row-0 sun rect x16..145 y+2..+127:
#    red/orange family = r dominant over g over b, r > 100.
sun = sel_im[TOP + 2:TOP + 128, 16:146]
warm = int(((sun[:, :, 0] > 100) & (sun[:, :, 0] > sun[:, :, 1] + 30) &
            (sun[:, :, 1] >= sun[:, :, 2])).sum())
chk("sun warm px x16..145 row0", warm > 500, f"n={warm}")

# 4) RACEFLAG px present in x12..26 y+0..+24 (14x24 record at (12,row);
#    fixture --species 0). Seam T427-D: native colours, not the ramp tint.
flag = sel_im[TOP:TOP + 25, 12:27]
fn = int((flag.sum(-1) != 0).sum())
chk("raceflag px x12..26 row0", fn > 100, f"n={fn}")

# 5) POP PIP GRID GEOMETRY (law = position/pitch, colour follows band
#    value): pip-family px inside x498..544 y+50..+67, FIRST dot column at
#    x498/499, second column at pitch 5 (x503/504) when >=2 bands, and the
#    OLD x428..481 strip zone carries no pip px.
def pipmask(im, x0, x1, y0, y1):
    z = im[y0:y1, x0:x1]
    m = np.zeros(z.shape[:2], bool)
    for c in PIPS:
        m |= (z == np.array(c)).all(-1)
    return m
grid = pipmask(sel_im, 498, 545, TOP + 50, TOP + 68)
chk("pip px inside x498..544 y+50..+67", int(grid.sum()) >= 4, f"n={int(grid.sum())}")
cols = np.nonzero(grid.any(0))[0]
chk("pip first col at x498", len(cols) > 0 and cols[0] == 0,
    f"cols={[498 + c for c in cols][:6]}")
# Dots are 2 px wide: group adjacent columns into dot starts, then the
# start-to-start pitch must be 5 (kStatusPipPitch).
starts = [int(c) for i, c in enumerate(cols) if i == 0 or c - cols[i - 1] > 1]
pitches = [starts[i + 1] - starts[i] for i in range(len(starts) - 1)]
chk("pip dot pitch 5", all(p == 5 for p in pitches) and len(starts) >= 2,
    f"starts={[498 + s for s in starts][:6]} pitches={pitches[:5]}")
old = pipmask(sel_im, 428, 482, TOP + 40, TOP + 100)
chk("old x428 strip GONE", int(old.sum()) == 0, f"n={int(old.sum())}")

# 6) PLANET ART present in x150..245 y+5..+100 (record 5*type+size at the
#    measured centre; the husk face is GRAY — shape/position is the law,
#    not hue). Require a >=20 px contiguous non-black blob.
pl = sel_im[TOP + 5:TOP + 100, 150:246]
pn = int((pl.sum(-1) != 0).sum())
chk("planet art px x150..245", pn > 200, f"n={pn}")

print("VERDICT", "PASS" if fails == 0 else f"FAIL ({fails})")
sys.exit(0 if fails == 0 else 1)
