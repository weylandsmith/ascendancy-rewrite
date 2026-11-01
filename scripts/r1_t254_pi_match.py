#!/usr/bin/env python3
"""t254: MAD-match the live PLBUILD current-project icon vs planitem.shp recs."""
import os
import subprocess
import importlib.util
from PIL import Image, ImageDraw

ROOT = "/home/hrethric/projects/ascendancy"
spec2 = importlib.util.spec_from_file_location(
    "t182", ROOT + "/scripts/r1_t182_pngdump.py")
t182 = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(t182)
pal = t182.load_palette()

live = Image.open(ROOT + "/work/r1/screens/t254/02_planet_detail.png").convert("RGB")
ic = live.crop((543 + 36, 108 + 22, 543 + 130, 108 + 75))

p = ROOT + "/extracted/ascend01/data/planitem.shp"
specf = ROOT + "/work/r1/shp_png/_spec_t254_pi_all.tsv"
with open(specf, "w") as f:
    for k in range(40):
        f.write(f"{p}\t{k}\n")
proc = subprocess.run([ROOT + "/tools/shp_pngdump", specf,
                       ROOT + "/work/r1/shp_png"],
                      capture_output=True, text=True, timeout=600)
out = {}
for line in proc.stdout.splitlines():
    c = line.split("\t")
    if len(c) >= 8 and c[2] == "ok":
        out[int(c[1])] = (int(c[3]), int(c[4]), c[6],
                          open(os.path.join(ROOT, "work/r1/shp_png", c[7]), "rb").read())


def recimg(k):
    W, H, sw, plane = out[k]
    w, h = (H, W) if sw == "1" else (W, H)
    img = Image.frombytes("P", (w, h), plane[:w * h])
    img.putpalette(pal)
    return img.convert("RGB")


scores = []
for k in sorted(out):
    W, H, sw, plane = out[k]
    a = list(ic.resize((W, H), Image.NEAREST).getdata())
    b = list(recimg(k).resize((W, H)).getdata())
    mad = sum(abs(x - y) for pa, pb in zip(a, b)
              for x, y in zip(pa, pb)) / (len(a) * 3)
    scores.append((mad, k))
scores.sort()
print("rendered", len(out), "recs")
print("top-10 MAD:", [(round(m, 1), k) for m, k in scores[:10]])

SC = 4
tiles = [("LIVE", ic)] + [(f"k{k}", recimg(k)) for m, k in scores[:6]]
big = [(lab, im.resize((im.width * SC, im.height * SC), Image.NEAREST))
       for lab, im in tiles]
Wtot = sum(b[1].width + 16 for b in big) + 16
Htot = max(b[1].height for b in big) + 40
cv = Image.new("RGB", (Wtot, Htot), (12, 12, 12))
dr = ImageDraw.Draw(cv)
x = 8
for lab, im in big:
    cv.paste(im, (x, 30))
    dr.text((x + 2, 6), lab, fill=(255, 255, 0))
    x += im.width + 16
cv.save("/tmp/t254_pi_mad_strip.png")
print("strip saved", cv.size)
