#!/usr/bin/env python3
"""t260 helper: locate the dropdown panel rows in the experiment window shot.
Opens the Capture menu via xsend, screenshots window 0x600009, finds the dark
dropdown panel bbox, and prints candidate item-row centers (~16 px pitch)."""
import re, subprocess, subprocess as sp, os, sys
ROOT = "/home/hrethric/projects/ascendancy"
env = dict(os.environ, DISPLAY=":9" if len(sys.argv) > 1 and sys.argv[1] == ":9" else ":8")
shot = os.path.join(ROOT, "work/r1/t260-loadstate/cap-check.png")

sp.run(["./tools/xsend", "DOSBox-X 2025.02.01: ASCEND", "key", "Escape"],
       cwd=ROOT, env=env, capture_output=True)
import time; time.sleep(0.6)
sp.run(["./tools/xsend", "DOSBox-X 2025.02.01: ASCEND", "315", "8"],
       cwd=ROOT, env=env, capture_output=True)
time.sleep(1.2)
WID = os.environ.get("T260_WID", "")
if not WID:
    out = sp.run(["bash", "-c", "DISPLAY=:8 xwininfo -root -tree | grep -m1 -i 'DOSBox-X.*ASCEND' | awk '{print $1}'"],
                 capture_output=True, text=True).stdout.strip()
    WID = out
sp.run(["import", "-window", WID, shot], env=env, capture_output=True, timeout=30)

# full-window pixel enumeration
p = sp.run(["convert", shot, "txt:-"], capture_output=True, text=True).stdout
pts = {}
for m in re.finditer(r"(\d+),(\d+):\s*\((\d+),(\d+),(\d+)", p):
    x, y, r_, g_, b_ = map(int, m.groups())
    pts[(x, y)] = (r_, g_, b_)
W = max(x for x, _ in pts) + 1
H = max(y for _, y in pts) + 1
print("image", W, "x", H, "pts", len(pts))
if len(pts) < W * H * 0.9:
    print("WARNING truncated txt dump; rerun with smaller crop")
# NOTE ImageMagick txt:- yields 16-bit channel values (0..65535) here.
# The dropdown panel is NEUTRAL dark grey; the Ascendancy title art behind it
# is saturated orange. Detect neutral-dark: max(r,g,b) < 0.55*65535 and
# (max-min) < 0.15*65535.
def neutral_dark(px):
    r_, g_, b_ = pts.get(px, (65535, 65535, 65535))
    mx = max(r_, g_, b_); mn = min(r_, g_, b_)
    return mx < 36000 and (mx - mn) < 10000
def neutral_lit(px):
    r_, g_, b_ = pts.get(px, (0, 0, 0))
    mx = max(r_, g_, b_); mn = min(r_, g_, b_)
    return mx > 40000 and (mx - mn) < 12000

# dark panel detection per row within x 290..640
rows = []
for y in range(17, H):
    n = sum(1 for x in range(290, min(640, W)) if neutral_dark((x, y)))
    rows.append((y, n))
band = None
bands = []
for y, n in rows:
    dark = n > 120
    if dark and band is None:
        band = [y, y]
    elif dark:
        band[1] = y
    elif band:
        bands.append(tuple(band)); band = None
if band: bands.append(tuple(band))
print("panel bands:", bands)
if not bands:
    sys.exit(1)

# within the biggest band, find text rows: rows with several bright pixels
y0, y1 = max(bands, key=lambda b: b[1] - b[0])
lit = []
for y in range(y0, y1 + 1):
    c = sum(1 for x in range(295, min(635, W)) if neutral_lit((x, y)))
    lit.append((y, c))
# group consecutive lit rows into item bands
seg = None
items = []
for y, c in lit:
    on = c >= 3
    if on and seg is None:
        seg = [y, y]
    elif on:
        seg[1] = y
    elif seg:
        items.append(tuple(seg)); seg = None
if seg: items.append(tuple(seg))
print("text segments in panel:")
for i, (a, b_) in enumerate(items):
    print("  seg %2d: y %d..%d center %d" % (i, a, b_, (a + b_) // 2))
