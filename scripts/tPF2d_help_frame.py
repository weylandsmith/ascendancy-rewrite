#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""tPF2d_help_frame.py — help.shp k0 popup-frame identity check (C7 owed).

Decode help.shp record 0 with the VERBATIM codec law (r1_shp_decode_law.py,
FUN_0005caac grammar), build the OPAQUE mask (pixels the stream writes), and
pixel-diff its BORDER RING against the refcap popup frame measured from
scratchpad/original-planet-screen-*.png (scale 512/640). The comparison is
mask-vs-frame-structure (no palette assumption — the question is WHICH
rectangle is the frame, not its colour).

VERDICT rule: the refcap popup outer frame rect (detected by the teal border
runs) must equal the k0 dims 336x256 in LOGICAL coords (dim-parity already
exact per C7), AND the k0 ring's opaque/thin profile must match the refcap
frame's (a solid 1-2px ring vs vendor frame ART can only be compared at the
"frame occupies exactly dims x dims" level without the palette — so this
script CONFIRMS placement/extent identity and reports the mask's border
profile; a mismatch of extents REFUTES the identity).
"""
import struct, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_shp_decode_law import parse, rows_from  # grammar-validated container walk

HELP = "extracted/ascend01/data/help.shp"

def decode_record(d, start, end, W, H):
    """decode row streams -> mask (list of rows of 0/1 written)."""
    mask = [[0] * W for _ in range(H)]
    i = start
    for r in range(H):
        x = 0
        while True:
            if i >= end: return None
            c = d[i]; i += 1
            if c == 0:
                break
            if c == 1:                     # transparent skip L (shp.md S9)
                x += d[i]; i += 1
                continue
            n = c >> 1
            if c & 1:                      # literal copy of n bytes
                for k in range(n):
                    if x < W: mask[r][x] = 1
                    x += 1
                i += n
            else:                          # run: next byte repeated n times
                x2 = min(x + n, W)
                for xx in range(x, x2): mask[r][xx] = 1
                i += 1
                x += n
        # rows outside clip are stream-skipped; here W-clamped
    return mask

def main():
    d, count, table_end, starts, spans = parse(HELP)
    w0, h0 = struct.unpack_from("<II", d, starts[0])
    W, H = w0 + 1, h0 + 1
    print(f"help.shp k0 dims {W}x{H} (fields {w0},{h0} = W-1,H-1 law)")
    mask = decode_record(d, starts[0] + 8, starts[0] + spans[0], W, H)
    if mask is None:
        print("DECODE FAILED (stream overrun)"); sys.exit(1)
    # border profile: opaque fraction of each of the 4 rings, and of the
    # interior (2px inset) — a FRAME has ring >> interior.
    def frac(px):
        return sum(px) / max(1, len(px))
    top = mask[0]; bot = mask[-1]
    left = [row[0] for row in mask]; right = [row[-1] for row in mask]
    ring = frac(top) + frac(bot) + frac(left) + frac(right)
    inner = [mask[r][c] for r in (2, H - 3) for c in range(2, W - 2)]
    inner += [mask[r][c] for r in range(2, H - 2) for c in (2, W - 3)]
    print(f"ring opacity  top {frac(top):.2f} bottom {frac(bot):.2f} "
          f"left {frac(left):.2f} right {frac(right):.2f}")
    print(f"interior(2px inset ring) opacity {frac(inner):.3f} "
          f"centre {mask[H//2][W//2]}")
    # row 1 / col 1 too (frames are often 2px)
    print(f"row1 {frac(mask[1]):.2f} row-2 {frac(mask[-2]):.2f} "
          f"col1 {frac([r[1] for r in mask]):.2f} col-2 {frac([r[-2] for r in mask]):.2f}")
    # refcap extents: logical popup per the t394 dims-parity claim is the
    # PLSQUARE widget 152,120..487,375 (336x256 EXACTLY). The visible refcap
    # popup frame in scratchpad PNGs (scale 0.8): detect the wide teal rows.
    try:
        from PIL import Image
    except ImportError:
        print("PIL missing — extents only"); sys.exit(0)
    im = Image.open("scratchpad/original-planet-screen-click-on-square-adjacent-to-structure.png").convert("RGB")
    px = im.load(); Wc, Hc = im.size
    s = Wc / 640.0
    def teal(p): return abs(p[0]-70)<45 and abs(p[1]-140)<50 and abs(p[2]-140)<50
    rows = [y for y in range(int(90*s), int(120*s)) if
            sum(1 for x in range(Wc) if teal(px[x, y])) > 0.55 * (336*s)]
    cols = [x for x in range(int(140*s), int(170*s)) if
            sum(1 for y in range(int(90*s), int(390*s)) if teal(px[x, y])) > 0.55 * (256*s)]
    print(f"refcap full-width frame rows (logical y): {[round(y/s) for y in rows]}")
    print(f"refcap full-height frame cols (logical x): {[round(x/s) for x in cols]}")
    if len(rows) >= 2 and len(cols) >= 2:
        h_log = round(rows[-1]/s) - round(rows[0]/s) + 1
        w_log = round(cols[-1]/s) - round(cols[0]/s) + 1
        print(f"refcap frame logical extent {w_log}x{h_log} vs k0 {W}x{H}")
        print("MATCH" if (w_log, h_log) == (W, H) else "MISMATCH")

if __name__ == "__main__":
    main()
