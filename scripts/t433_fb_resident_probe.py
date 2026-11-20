#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t433 PROBE 4: IS THE FRAMEBUFFER/SURFACE IN THE SAVE AT ALL? (vacuity gate)

F2 proved no CONTIGUOUS copy of the vendor chrome rows exists in the Memory or
Vga members of the playcap saves. Before treating that as "the surface isn't
resident", two vacuity holes must be closed:

  (1) Does the save even STORE the displayed pixels? If the Vga member holds
      only registers/palette (no framebuffer), the Vga half of F2 is vacuous.
      Test: search Vga for (a) the loaded game.pal, (b) many long signatures
      taken from DISTINCTIVE screen content (text rows, star-field runs) —
      anything the game certainly painted. Hits => pixels ARE stored, so F2's
      Vga negative is a real negative about chrome.
  (2) Planar storage. A horizontal run of N px crosses all 4 VGA planes, so a
      packed-byte search cannot see it. A VERTICAL run of k px in one column is
      contiguous-within-plane at pitch W/4. Test vertical runs of chrome at the
      candidate pitches for 320x200 mode-X (80), 640x480 planar (160), and
      packed 320/640, in BOTH members.

Exit 0 = verdict printed (pixels stored y/n + chrome resident y/n).
"""
import os, sys, glob, zipfile, numpy as np
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW = open(os.path.join(ROOT, "extracted/ascend01/data/game.pal"), "rb").read()[:768]
SIX = np.frombuffer(RAW, dtype=np.uint8).reshape(256, 3).astype(np.int32)
PAL = np.clip(SIX * 4 + SIX // 16, 0, 255)


def idx_plane():
    a = np.asarray(Image.open(f"{ROOT}/docs/assets/refcap/original-strategic-map.png").convert("RGB")).astype(np.int32)[40:]
    d = np.abs(a[:, :, None, :] - PAL[None, None, :, :]).sum(axis=3)
    assert (d.min(axis=2) == 0).all()
    return d.argmin(axis=2).astype(np.uint8)


def main():
    idx = idx_plane()
    sdirs = sorted(glob.glob(f"{ROOT}/work/r1/bank-play-20261111"))
    if not sdirs:
        print("no save dir"); return 2
    savs = sorted(glob.glob(os.path.join(sdirs[0], "*.sav")))[:3]

    # ---- signature set: long runs from distinctive content
    sigs = []
    for y in range(0, 436, 7):
        for x0 in (0, 64, 160, 256, 384, 466):
            s = idx[y:y+2, x0:x0+32].tobytes()
            if len(s) == 64 and len(set(s)) >= 12:
                sigs.append((f"y{y}x{x0}", s))
    print(f"64B distinctive-content signatures: {len(sigs)}")

    for sv in savs:
        z = zipfile.ZipFile(sv)
        mem = z.read("Memory"); vga = z.read("Vga"); z.close()
        pal_in_vga = vga.find(RAW)
        pal_in_mem = mem.find(RAW)
        hv = sum(1 for _, s in sigs if vga.find(s) >= 0)
        hm = sum(1 for _, s in sigs if mem.find(s) >= 0)
        print(f"\n{os.path.basename(sv)}")
        print(f"  game.pal in Vga: {hex(pal_in_vga) if pal_in_vga>=0 else 'no'} | in Memory: {hex(pal_in_mem) if pal_in_mem>=0 else 'no'}")
        print(f"  screen-content 64B sigs found: Vga {hv}/{len(sigs)}  Memory {hm}/{len(sigs)}")

        # ---- planar vertical-run test for chrome
        colruns = []
        for x in range(7):
            y = 0
            while y < 420:
                seg = idx[y:y+8, x]
                if len(set(seg)) == 1 and seg[0] != 0:
                    colruns.append((x, y, int(seg[0])))
                y += 1
        print(f"  chrome vertical runs >=8 px (same colour): {len(colruns)}")
        found = {}
        for pitch in (80, 160, 320, 640):
            for nm, buf in (("Memory", mem), ("Vga", vga)):
                arr = np.frombuffer(buf, dtype=np.uint8)
                n = 0
                for (x, y, v) in colruns:
                    # need base offset: search for v followed by v at +pitch ... x8
                    cand = np.flatnonzero(arr == v)
                    if cand.size == 0 or cand.size > 400000:
                        continue
                    ok = np.ones(cand.size, dtype=bool)
                    for k in range(1, 8):
                        vals = np.full(cand.size, 255, dtype=np.int64)
                        tgt = cand + k * pitch
                        good = tgt < arr.size
                        vals[good] = arr[tgt[good]]
                        ok &= (vals == v)
                    n += int(ok.sum())
                found[(pitch, nm)] = n
        print("  vertical-run support (sum of run-start hits):",
              {f"{p}/{nm}": v for (p, nm), v in found.items()})
    return 0


if __name__ == "__main__":
    sys.exit(main())
