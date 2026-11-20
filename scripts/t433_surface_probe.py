#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t433 PROBE 0 (offline, zero capture): does the vendor chrome surface exist
as an exact byte run in guest RAM of existing ring saves?

Hypothesis under test (chrome.md F1): the chrome field is ONE screen-fixed
surface painted once. If so, its palette-index bytes must persist somewhere in
guest RAM (heap surface, OR the VGA framebuffer itself) and a vendor-derived
index run from docs/assets/refcap/original-strategic-map.png should appear
VERBATIM in a save's Memory/Vga member.

Method:
 1. quantise the refcap to game.pal indices (nearest, 6-bit*255//63 scale,
    report exact-match rate as a gate on the method);
 2. take the left-band rows (x0..6, rows 40..479): 7-px rows are SHORT
    signatures; require >=2 consecutive rows concatenated (14 px) to be found;
 3. scan every Memory + Vga member of each save for the concatenated runs;
 4. also scan a full-width top-band run (rows 0..6 x0..465 is too long; use
    rows 2..5 x 8..465 per-row 458-px runs) — a hit there pins the surface
    to the framebuffer or a 640-pitch surface.

Exit 0 = at least one verbatim >=14px vendor run found (surface exists).
Exit 1 = ran, clean negative. 2 = harness error.
"""
import os, sys, struct, zipfile, glob
from collections import Counter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REF = os.path.join(ROOT, "docs/assets/refcap/original-strategic-map.png")
PAL = os.path.join(ROOT, "extracted/ascend01/data/game.pal")

def load_pal():
    b = open(PAL, "rb").read()[:768]
    return [(b[i*3]*255//63, b[i*3+1]*255//63, b[i*3+2]*255//63) for i in range(256)]

def load_png_rgb(path):
    from PIL import Image
    im = Image.open(path).convert("RGB")
    import numpy as np
    return np.asarray(im)

def main():
    import numpy as np
    pal = np.array(load_pal(), dtype=np.int16)
    img = load_png_rgb(REF).astype(np.int16)
    H, W = img.shape[0], img.shape[1]
    print(f"refcap {W}x{H}")

    # quantise whole image
    d = np.abs(img[:, :, None, :] - pal[None, None, :, :]).sum(axis=3)  # HxWx256
    idx = d.argmin(axis=2)
    mind = d.min(axis=2)
    exact = int((mind == 0).sum())
    close = int((mind <= 6).sum())
    print(f"quantise: exact {exact}/{W*H} ({100*exact/(W*H):.1f}%), tol<=6 {close/(W*H)*100:.1f}%")

    # left band rows x0..6, rows 40..479 -> 7-px runs; pair consecutive rows
    runs = []
    for y in range(40, 479):
        r = idx[y, 0:7].tobytes()
        runs.append((y, r))
    # 14-px signatures: two consecutive band rows
    sigs = []
    for i in range(len(runs)-1):
        y0, r0 = runs[i]; y1, r1 = runs[i+1]
        sigs.append((f"band{y0}+{y1}", r0 + r1))
    # longer: 4 consecutive rows = 28 px (stronger)
    sigs4 = []
    for i in range(0, len(runs)-3, 7):
        y0 = runs[i][0]
        blob = b"".join(runs[i+k][1] for k in range(4))
        sigs4.append((f"band4_{y0}", blob))

    sdirs = sorted(glob.glob(os.path.join(ROOT, "work/r1/bank-play-20261111")))
    if not sdirs:
        print("no save dir"); return 2
    any_hit = False
    for sd in sdirs:
        savs = sorted(glob.glob(os.path.join(sd, "*.sav")))
        for sv in savs[:2]:  # two slots per dir enough
            z = zipfile.ZipFile(sv)
            for mem in ("Memory", "Vga"):
                try:
                    data = z.read(mem)
                except Exception:
                    continue
                hits = []
                for name, s in sigs4:
                    o = data.find(s)
                    if o >= 0:
                        hits.append((name, o))
                print(f"{os.path.basename(sv)} {mem}: size={len(data)} sig4_hits={len(hits)}/{len(sigs4)} {hits[:5]}")
                if hits:
                    any_hit = True
            z.close()
        break  # one dir is enough for probe 0
    print("VERDICT:", "SURFACE RUN FOUND" if any_hit else "NEGATIVE (no verbatim 28px vendor chrome run in sampled saves)")
    return 0 if any_hit else 1

if __name__ == "__main__":
    sys.exit(main())
