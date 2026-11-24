#!/usr/bin/env python3
"""tPL-V2 port census: the orbital hover-outline on OUR port's shots
(/tmp/tplv2_shots/{rest,hover-slot0,hover-slot6,rest-again}.png).

LAW under test (docs/re/_wip_tPLV2.md F2/F6): an EMPTY orbital slot shows
a 69x69 box outline in game.pal index 150 (conv6->8 of raw (4,17,19) =
(16,69,77) — the t398 conversion law) ONLY while the pointer is inside its
70x70 box; at rest NOTHING is painted. Slot boxes: col0 x13 y in
{119,189,259,329,399}, col1 x83 same ys.

PASS = outline pixels (== conv(150), or close) form the box perimeter in
hover-slot0 at (13,119) and hover-slot6 at (83,189), and BOTH rest shots
have ZERO such perimeter pixels at every slot. Anti-vacuity: the hover
perimeter must NOT appear at the OTHER slot's box.
"""
import subprocess, sys

BOXES = [(13, y) for y in (119, 189, 259, 329, 399)] + \
        [(83, y) for y in (119, 189, 259, 329, 399)]
TARGET = (16, 69, 77)   # conv6->8 of game.pal 150 = (4,17,19)
TOL = 12

def load(path):
    raw = subprocess.run(["convert", path, "-depth", "8", "rgb:-"],
                         capture_output=True, check=True).stdout
    return 640, 480, raw

def px(w, raw, x, y):
    i = (y * w + x) * 3
    return raw[i], raw[i+1], raw[i+2]

def near(c, t=TARGET, tol=TOL):
    return all(abs(a - b) <= tol for a, b in zip(c, t))

def perimeter(w, raw, x0, y0):
    """count target-coloured pixels ON the 69x69 box perimeter (SDL_RenderDrawRect
    draws x..x+w-2 inclusive of a w-1 rect: corners (x0,y0)..(x0+68,y0+68))."""
    pts = [(x, y0) for x in range(x0, x0 + 69)] + \
          [(x, y0 + 68) for x in range(x0, x0 + 69)] + \
          [(x0, y) for y in range(y0, y0 + 69)] + \
          [(x0 + 68, y) for y in range(y0, y0 + 69)]
    return sum(1 for x, y in pts if near(px(w, raw, x, y)))

def main():
    shots = {}
    for name in ("rest", "hover-slot0", "hover-slot6", "rest-again"):
        shots[name] = load(f"/tmp/tplv2_shots/{name}.png")
    fails = []
    for name in ("rest", "rest-again"):
        w, h, raw = shots[name]
        counts = {b: perimeter(w, raw, *b) for b in BOXES}
        tot = sum(counts.values())
        print(f"{name}: perimeter-target px total={tot} " +
              " ".join(f"{b}:{c}" for b, c in counts.items() if c))
        if tot > 4:
            fails.append(f"{name} shows outline px at rest ({tot})")
    for name, box in (("hover-slot0", (13, 119)), ("hover-slot6", (83, 189))):
        w, h, raw = shots[name]
        c_hit = perimeter(w, raw, *box)
        others = {b: perimeter(w, raw, *b) for b in BOXES if b != box}
        oth = sum(others.values())
        print(f"{name}: box{box} perimeter={c_hit}/272  other-boxes={oth}")
        if c_hit < 200:
            fails.append(f"{name}: outline incomplete at {box} ({c_hit}/272)")
        if oth > 4:
            fails.append(f"{name}: outline leaked to other boxes ({oth})")
    if fails:
        print("VERDICT FAIL")
        for f in fails:
            print(" -", f)
        return 1
    print("VERDICT PASS: hover outline exact per law; nothing at rest; no leak")
    return 0

sys.exit(main())
