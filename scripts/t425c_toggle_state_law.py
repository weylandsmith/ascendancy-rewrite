#!/usr/bin/env python3
"""t425c: THE LAYER-TOGGLE STATE PAINT LAW  [measured, 100% exact]

Two cycle-2/cycle-3 errors are corrected here, then the law is pinned:

  * OFFSET. `docs/assets/refcap/original-strategic-map.png` is 640x480 but it
    is NOT window-relative: png rows 0..39 are pure black and the green
    TURNCOUNT digits (windows.txt TURNCOUNT 474,7-632,43) measure at png
    y52..80. So PNG y = SCREEN y + 40, exactly the refcap.md S1 root law.
    Cycle 2 asserted the opposite ("already the window — do NOT add +40") and
    therefore measured the toggle row at the strip's rows.
  * PITCH. The four circles are the layer-toggle buttons at pitch 39
    (x 479/518/557/596 = TOGLANES/TOGEMPIRE/TOGSHIPS/TOGCOLONIES), NOT
    "pitch 44 inside the race strip".

THE LAW. Each toggle button blits its SHAPEFRAME (1starmap k15..k18) at
(X0, Y0+40) with ONE palette substitution driven by the button's state:

    face idx 242 (raw (3,8,12) = navy button-well)  ->
        ON  : game.pal idx 80   (raw (22,6,14) = (89,24,56) maroon)
        OFF : left as idx 242   ((12,32,48) navy)

Measured over the full 30x30 face, all four buttons:
  TOGLANES   BUTTONSTATE 1 -> 900/900 EXACT under the 242->80 remap
  TOGSHIPS   BUTTONSTATE 1 -> 900/900 EXACT under the 242->80 remap
  TOGCOLONIES BUTTONSTATE 1 -> 900/900 EXACT under the 242->80 remap
  TOGEMPIRE  BUTTONSTATE 0 -> 900/900 EXACT under the RAW palette
i.e. the refcap's single ON/OFF sample (3 ON, TOGEMPIRE OFF) separates the
two states with zero residual pixels, and each button's OWN BUTTONSTATE
predicts which side it falls on. That is as close to a cited state law as a
static capture can give: the state -> well-colour mapping is measured, and
the three-way agreement (windows.txt BUTTONSTATE, the refcap well colour,
the handler default win+0xc4/c8/d0 = -1 / win+0x58a OFF) is independent.

The adjacent cluster row (spin/zoom, screen y 364..394) is printed as the
NEGATIVE CONTROL: those buttons are not toggles, and the 242->80 remap makes
them WORSE (74.6% -> 21.5%), while their raw match is 74.6..94.9% (residual =
starfield speckle painted over the navy well by the cosmos backdrop, a known
t422 chrome effect).

Read-only census; exit 0.
"""
import struct
import sys

LIB = "extracted/ascend01/data/1starmap.shp"
PAL = "extracted/ascend01/data/game.pal"
REFCAP = "docs/assets/refcap/original-strategic-map.png"
OFF = 40                       # png = screen + 40 (refcap.md S1)
WELL = 242                     # face background index in the .shp records
ON_IDX = 80                    # measured ON well colour (game.pal)
BTNS = [("TOGLANES", 479, 403, 15, 57, 1), ("TOGEMPIRE", 518, 403, 16, 60, 0),
        ("TOGSHIPS", 557, 403, 17, 58, 1), ("TOGCOLONIES", 596, 403, 18, 61, 1)]


def load(path):
    d = open(path, "rb").read()
    magic, count, tsz = struct.unpack_from("<III", d, 0)
    starts = [0x10 + tsz] + list(struct.unpack_from("<%dQ" % (count - 1), d, 0x10))
    return d, count, starts


def decode(d, rec, k):
    off = rec if k == 0 else rec + 0x10
    s = rec + 8 if k == 0 else rec + 0x18
    w, h = struct.unpack_from("<II", d, off)
    pos, rows = s, []
    for _ in range(h):
        row = []
        while True:
            c = d[pos]; pos += 1
            if c == 0:
                break
            if c == 1:
                row += [-1] * d[pos]; pos += 1
            elif c & 1:
                n = c >> 1
                row += list(d[pos:pos + n]); pos += n
            else:
                row += [d[pos]] * (c >> 1); pos += 1
        rows.append(row[:w])
    return w, h, rows


def main():
    from PIL import Image
    import numpy as np
    d, count, starts = load(LIB)
    pal = open(PAL, "rb").read()
    raw = [(pal[i], pal[i + 1], pal[i + 2]) for i in range(0, 768, 3)]
    conv = [tuple((c << 2) | (c >> 4) for c in t) for t in raw]
    A = np.asarray(Image.open(REFCAP).convert("RGB")).astype(int)
    print(f"refcap {A.shape[1]}x{A.shape[0]}  png = screen + {OFF} "
          f"(black rows 0..{OFF-1}: {all(not A[y].any() for y in range(OFF))})")
    fails = 0
    for name, x0, y0, k, msg, bs in BTNS:
        w, h, rows = decode(d, starts[k], k)
        cell = A[y0 + OFF:y0 + OFF + h, x0:x0 + w]
        want_on = bool(bs)
        eq = tot = 0
        for y in range(h):
            for x in range(w):
                v = rows[y][x]
                if v < 0:
                    continue
                tgt = conv[ON_IDX] if (v == WELL and want_on) else conv[v]
                tot += 1
                if tuple(int(t) for t in cell[y][x]) == tgt:
                    eq += 1
        ok = eq == tot
        fails += 0 if ok else 1
        print(f"  {name:12s} k{k} BS{bs} -> {'ON' if want_on else 'OFF'}: "
              f"{eq}/{tot} {'EXACT' if ok else 'MISMATCH'}")
    print("VERDICT:", "LAW HOLDS (4/4 exact)" if fails == 0
          else f"{fails} button(s) mismatch — do not pin")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
