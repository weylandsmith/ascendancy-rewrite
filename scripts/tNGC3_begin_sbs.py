#!/usr/bin/env python3
"""tNG-C3: Begin-panel side-by-side builder + green-mass census."""
import sys
import numpy as np
from PIL import Image

ours_p = sys.argv[1]
vend_p = '/home/hrethric/projects/ascendancy/scratchpad/newgame-original.png'
out_p = sys.argv[2]
ours = np.asarray(Image.open(ours_p).convert('RGB')).astype(int)
vend = np.asarray(Image.open(vend_p).convert('RGB'))[1:481, 1:641].astype(int)
def gm(im):
    return (im[:, :, 0] < im[:, :, 1] - 30) & (im[:, :, 2] < im[:, :, 1] - 10) & (im[:, :, 1] > 60)
print('ours begin-panel green n=', int(gm(ours)[373:473, 494:641].sum()),
      'vendor', int(gm(vend)[373:473, 494:641].sum()))
o = Image.open(ours_p).convert('RGB').crop((502, 381, 633, 473))
v = Image.open(vend_p).convert('RGB').crop((503, 382, 634, 474))
m = Image.new('RGB', (131 * 2 + 6, 92), (255, 0, 255))
m.paste(o, (0, 0)); m.paste(v, (137, 0))
m = m.resize((m.width * 3, m.height * 3), Image.NEAREST)
m.save(out_p)
print('saved', out_p)
