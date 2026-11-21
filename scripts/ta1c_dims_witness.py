#!/usr/bin/env python3
"""tA1-CONT: drawn-dims witness, port render vs vendor, per region.
Detector is VENDOR-INDEPENDENT: opaque-content bbox (nonblack minus the
row navy/panel base colour), so the SAME numbers apply to both sides.
Usage: ta1c_dims_witness.py OURS_VENDORSHOT VENDORSHOT [--sun k ...]
"""
import sys, struct
import numpy as np
from PIL import Image

def load640(p):
    im = np.array(Image.open(p).convert('RGB'))
    if im.shape[:2] != (480, 640):
        if im.shape[0] == 481 and im.shape[1] == 643:
            im = im[1:481, 1:641]
        elif im.shape == (600, 800, 3):
            im = im[100:580, 80:720]
        else:
            raise SystemExit(f'{p}: unrecognised size {im.shape}')
    return im

def bbox_of(mask, x0, y0):
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return None
    return (x0 + int(xs.min()), y0 + int(ys.min()), x0 + int(xs.max()), y0 + int(ys.max()), int(mask.sum()))

def content_mask(reg, base):
    """opaque art px = differs from the flat panel base by > tol."""
    d = np.abs(reg.astype(int) - np.array(base)).sum(axis=2)
    return d > 60

def ring_bbox(im, cx, cy, half=56):
    reg = im[cy - half:cy + half + 1, cx - half:cx + half + 1]
    # ring greys: low-chroma mid-luminance
    mx = reg.max(axis=2).astype(int); mn = reg.min(axis=2).astype(int)
    grey = (mx - mn < 25) & (mx >= 35) & (mx <= 200)
    bb = bbox_of(grey, cx - half, cy - half)
    return bb, (None if bb is None else (bb[2] - bb[0] + 1, bb[3] - bb[1] + 1))

def disc_bbox(im, cx, cy, half, base):
    reg = im[cy - half:cy + half + 1, cx - half:cx + half + 1]
    bb = bbox_of(content_mask(reg, base), cx - half, cy - half)
    return bb, (None if bb is None else (bb[2] - bb[0] + 1, bb[3] - bb[1] + 1))

def report(title, ours, vendor, regions):
    print(f'== {title}')
    ok = True
    for (name, cx, cy, half, base, cited) in regions:
        bo, do = disc_bbox(ours, cx, cy, half, base)
        bv, dv = disc_bbox(vendor, cx, cy, half, base)
        match = do is not None and dv is not None and abs(do[0] - dv[0]) <= 2 and abs(do[1] - dv[1]) <= 2
        ok &= match
        print(f'  {name:<18} ours {do} (n={bo[4] if bo else 0})  vendor {dv} (n={bv[4] if bv else 0})  cited {cited}  {"MATCH" if match else "DIFF"}')
    return ok

if __name__ == '__main__':
    ours = load640(sys.argv[1])
    vendor = load640(sys.argv[2])
    navy = (12, 32, 48)
    black = (0, 0, 0)
    ok = True
    # NEWGAME regions (D19 family)
    ok &= report('newgame race-column portraits (smrace 100 + racering 109)', ours, vendor,
                 [(f'RACELIST row{i}', 559, 107 + i * 108, 60, navy, '100x100 disc / 109 ring') for i in range(3)])
    ok &= report('newgame DESC portrait+ring', ours, vendor,
                 [('DESC portrait', 409, 97, 60, black, '100x100 disc / 109 ring')])
    ok &= report('newgame DESC planet (planets ladder)', ours, vendor,
                 [('DESC planet', 401, 218, 26, black, 'ladder 24/38/52/71/95')])
    # PLANETS-LIST regions
    ok &= report('planets-list sun (suns ladder)', ours, vendor,
                 [('row0 sun', 80, 121, 72, black, 'row0 suns k<type>')])
    ok &= report('planets-list planet (planets ladder)', ours, vendor,
                 [('row0 planet', 215, 110, 50, black, '5*type+size')])
    print('DIMS VERDICT', 'PASS' if ok else 'FAIL')
    sys.exit(0 if ok else 1)
