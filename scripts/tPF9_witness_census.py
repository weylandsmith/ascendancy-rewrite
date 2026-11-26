#!/usr/bin/env python3
# tPF-9 stray-text pixel census. Boxes (640x480 logical == native here):
#   UR hint box   : PLBUILD panel bottom strip (463,88)-(632,106) — where
#                   "click: set project" painted (rect.x0+6, rect.y1-14).
#   BL hint box   : (7,448)-(240,472) — where "Esc: return to galaxy"
#                   painted (interior.x0+8, interior.y1-16).
#   UR CONTROL box: same UR box on the list-open frame (the transient
#                   "list open: pick one" string MUST be found there).
#   BL CONTROL box: bottom-left of the RESEARCH frame pre-fix was the Esc
#                   label; post-fix it must be empty too (checked as BL).
# Text ink signature: kDim = (150,130,110) +- tol, OR kText=(235,235,235)
# +- tol. Panel ART text is excluded by box placement (art 'No Project'
# sits centred near y<=60; boxes start y>=88).
import sys
from PIL import Image

TOL = 40
def near(p, c): return all(abs(p[i]-c[i]) <= TOL for i in range(3))
KDIM = (150,130,110); KTEXT = (235,235,235)

def ink(img, box):
    x0,y0,x1,y1 = box
    n = 0
    for y in range(y0, y1):
        for x in range(x0, x1):
            p = img.getpixel((x,y))
            if near(p, KDIM) or near(p, KTEXT): n += 1
    return n

def main():
    # argv: rest_planet.png listopen_planet.png research.png
    rest = Image.open(sys.argv[1]).convert("RGB")
    listo = Image.open(sys.argv[2]).convert("RGB")
    resch = Image.open(sys.argv[3]).convert("RGB")
    UR = (463, 88, 632, 106)
    # BL box starts x=16: the RESWIN frame border is neutral gray
    # (120,120,120) at x=7, which sits inside the kText tolerance; the
    # deleted label painted at interior.x0+8 = x15 and spans right, so a
    # box at x16 still covers every glyph column.
    BL = (16, 448, 240, 472)
    ur0, bl0 = ink(rest, UR), ink(rest, BL)
    urL = ink(listo, UR)
    blR = ink(resch, BL)
    print(f"planet-idle  UR ink={ur0}  BL ink={bl0}")
    print(f"list-open    UR ink={urL}  (control: transient text present)")
    print(f"research     BL ink={blR}")
    ok = True
    # Thresholds: a rendered hint label is ~150+ ink px (8pt-ish text at
    # kDim over navy). The planet-screen starfield is TRUE WHITE and can
    # scatter a handful of kText-near pixels into a box, so empty boxes
    # tolerate <=8 ink px; the control requires >=30 (label presence).
    if ur0 > 8: print(f"FAIL: idle planet UR box has {ur0} ink px (hint not deleted)"); ok = False
    if bl0 > 8: print(f"FAIL: planet BL box has {bl0} ink px (Esc label not deleted)"); ok = False
    if blR > 8: print(f"FAIL: research BL box has {blR} ink px (Esc label not deleted)"); ok = False
    if urL < 30: print(f"FAIL: list-open UR control ink={urL} < 30 (census blind or feedback deleted)"); ok = False
    print("VERDICT PASS" if ok else "VERDICT FAIL")

main()
