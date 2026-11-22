#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""tNG-F F2: pin the exact black-box rect of the Player Species header."""
import numpy as np
from PIL import Image

im = np.array(Image.open("scratchpad/newgame-original.png").convert("RGB")).astype(int)
r, g, b = im[:, :, 0], im[:, :, 1], im[:, :, 2]
fam = (r <= 16) * (g <= 40) * (b <= 50) * (abs(r - g) < 8) * (abs(g - b) < 12)
for row in (8, 20, 30, 36):
    xs = np.nonzero(fam[row, 490:640])[0] + 490
    if len(xs):
        gaps = [x for x in range(int(xs.min()), int(xs.max()) + 1)
                if not fam[row, x]]
        print(f"row{row}: fam {xs.min()}..{xs.max()} n={len(xs)} gaps={gaps[:8]}")
    else:
        print(f"row{row}: none")
for col in (500, 530, 560, 600, 628, 632, 633):
    ys = np.nonzero(fam[0:50, col])[0]
    print(f"col{col}: rows {ys.tolist()[:6]}...{ys.tolist()[-4:] if len(ys) else []} n={len(ys)}")
print("row36 px:", [tuple(im[36, x]) for x in range(506, 522)])
