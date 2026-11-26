#!/usr/bin/env python3
"""tPF-10 hover pixel census (D28 items 19/20).

Args: <shot-dir> <cx> <cy>  (node centre from the app's own log line).
Ring box = centre +-30, clamped to x>=16 (tPF-9 RESWIN border law) and
rows 47..455 (tPF-8 crop law: y46 header, y>=456 panel).

Checks:
 A hover-vs-idle: >60 changed px in the box (blue frame k2 replaced k1);
 B blue-family px (B>R+40, B>=120) in the box: hover >= idle+40;
 C off-idle frame returns near idle render (changed <= 30 — the word
   cleared, ring back to default);
 D studied frame (post-click, word cleared by then? NO — the cursor sat on
   the node during the click; frame 2 then too. So D measures studied-vs-
   idle OUTSIDE the hover: re-entry shot is hovered again; the studied-law
   leg is the LOG (study line printed), not pixels. D instead checks the
   re-entry hover render matches the first hover render (same blue, +-
   tolerant) — the word+frame law is deterministic across screens.
"""
import sys
from PIL import Image

def px(im):
    return im.load()

def main():
    d, cx, cy = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    x0 = max(16, cx - 30); x1 = min(475, cx + 30)
    y0 = max(47, cy - 30); y1 = min(455, cy + 30)
    idle = px(Image.open(f"{d}/research_idle.png").convert("RGB"))
    hov = px(Image.open(f"{d}/research_hover.png").convert("RGB"))
    off = px(Image.open(f"{d}/research_off.png").convert("RGB"))
    ree = px(Image.open(f"{d}/research_reentry.png").convert("RGB"))

    def changed(a, b):
        return sum(1 for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)
                   if a[x, y] != b[x, y])

    def blue(a):
        n = 0
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                r, g, b = a[x, y]
                if b > r + 40 and b >= 120:
                    n += 1
        return n

    ch_ho = changed(idle, hov)
    ch_oo = changed(idle, off)
    ch_hr = changed(hov, ree)
    b_idle, b_hov, b_off = blue(idle), blue(hov), blue(off)
    print(f"box=({x0},{y0})-({x1},{y1}) changed idle->hover={ch_ho} "
          f"idle->off={ch_oo} hover->reentry={ch_hr}")
    print(f"blue-family idle={b_idle} hover={b_hov} off={b_off}")
    ok = True
    def chk(cond, msg):
        nonlocal ok
        print(("  OK  " if cond else "  FAIL") + " " + msg)
        ok = ok and cond
    chk(ch_ho > 60, f"A hover repaints the ring box ({ch_ho} > 60)")
    chk(b_hov >= b_idle + 40,
        f"B hover adds strong-blue px ({b_hov} >= {b_idle}+40)")
    chk(ch_oo <= 30, f"C off-disk frame clears to idle render ({ch_oo} <= 30)")
    chk(b_off <= b_idle + 10, f"C2 off-disk blue back to idle ({b_off})")
    chk(ch_hr <= 60, f"D re-entry hover matches first hover ({ch_hr} <= 60)")
    print("VERDICT PASS" if ok else "VERDICT FAIL")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
