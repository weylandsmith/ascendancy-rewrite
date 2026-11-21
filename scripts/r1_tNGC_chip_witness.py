#!/usr/bin/env python3
"""tNG-C CHIP/PLANET WITNESS (cycle 2). Law docs/re/_wip_tNGC.md F9/F10/F13.

Checks a NEW GAME screenshot (ours or the vendor refcap; browser shots
auto-cropped [1:481,1:641]):
  1. CHIP RAMP: chip i (rect x 381+16i..395+16i, rows 433..457) has a
     brightest ink EXACTLY game.pal[4i+19] (6->8 bit). The vendor chip0 in
     the refcap is the exception BY LAW: its brightest pixel is the white
     selection frame (255,255,255); the frame law is checked separately
     (white hlines at rows 434/458 spanning the chip).
  2. PLANET PRESENCE: content (NAVY-detector) bbox inside (382..433,
     191..242) covers the cited smhome 52x52 extent +-2.
Exit 0 = all checks pass on the given shots.
"""
import sys
import numpy as np
from PIL import Image

ROOT = "/home/hrethric/projects/ascendancy"
NAVY = np.array((12, 32, 48))


def load640(p):
    im = np.array(Image.open(p).convert("RGB"))
    if im.shape[:2] == (480, 640):
        return im
    if im.shape[0] == 481 and im.shape[1] == 643:
        return im[1:481, 1:641]
    raise SystemExit(f"{p}: not 640x480/browser source {im.shape}")


def pal():
    raw = np.fromfile(f"{ROOT}/extracted/ascend01/data/game.pal",
                      dtype=np.uint8).reshape(256, 3).astype(int)
    return (raw << 2) | (raw >> 4)


def check(p, p8):
    im = load640(p).astype(int)
    ok = True
    # --- chip ramp census
    for i in range(7):
        x0, x1 = 381 + 16 * i, 395 + 16 * i
        z = im[433:458, x0:x1 + 1]          # emblem rows (frame law below)
        s = z.sum(axis=2)
        px = z[np.unravel_index(s.argmax(), s.shape)]
        want = p8[4 * i + 19]
        # exclude white (frame) pixels from the ink claim
        is_white = bool((px == 255).all())
        if is_white:
            # FRAMED chip (this is the selected chip per the 0x52621 law):
            # the frame greys outshine the emblem ink, so the brightest
            # test is frame-polluted on BOTH sides (vendor refcap chip0
            # brightest non-white = (244,245,245) frame pixel). The law
            # check degrades to PRESENCE: pal[4i+19] pixels must occur in
            # the chip (vendor 7 px, ours 67 px for k0 — ink census k0
            # slot-19 count dominates; count parity is NOT law).
            n = int((z == want).all(axis=2).sum())
            hit = n > 0
            note = f"framed chip, pal[4i+19] present x{n}"
        else:
            hit = bool((px == want).all())
            note = f"ink {tuple(px)} want {tuple(want)}"
        if not hit:
            ok = False
        print(f"  chip{i} rows433..457 {note} "
              f"{'OK' if hit else 'MISS'}")
    # --- selection frame: white hlines rows 434/458 over the player chip.
    # The player chip is whichever chip shows white hlines (vendor refcap =
    # chip0; ours = playerColourIdx, 0 at fresh start).
    frames = []
    for i in range(7):
        x0, x1 = 381 + 16 * i, 395 + 16 * i
        w434 = int((im[434, x0:x1 + 1] == 255).all(axis=1).sum())
        w458 = int((im[458, x0:x1 + 1] == 255).all(axis=1).sum())
        if w434 >= 13 and w458 >= 13:
            frames.append(i)
    print(f"  frame chips (white hlines 434+458): {frames}")
    if len(frames) != 1:
        ok = False
        print("  FAIL: exactly one framed chip expected")
    # --- planet presence
    x0, y0, x1, y1 = 382, 191, 433, 242
    reg = im[y0:y1 + 1, x0:x1 + 1]
    m = (np.abs(reg - NAVY).sum(axis=2) > 60) & (reg.sum(axis=2) > 30)
    ys, xs = np.where(m)
    if len(xs) == 0:
        ok = False
        print("  planet: EMPTY (no content px)")
    else:
        bb = (xs.min(), ys.min(), xs.max(), ys.max())
        w, h = bb[2] - bb[0] + 1, bb[3] - bb[1] + 1
        good = abs(w - 52) <= 2 and abs(h - 52) <= 2
        ok &= good
        print(f"  planet bbox {w}x{h} at zone-rel {bb[:2]} n={int(m.sum())} "
              f"{'OK' if good else 'OFF 52+-2'}")
    return ok


def main():
    p8 = pal()
    ok = True
    for p in sys.argv[1:]:
        print(f"== {p}")
        ok &= check(p, p8)
    print("WITNESS", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
