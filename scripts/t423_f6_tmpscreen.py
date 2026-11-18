#!/usr/bin/env python3
"""t423 F6: decode the *_tmp screen-state containers (3cfgnew.tmp et al).

Header: magic '1.10', count=1, tsz=16; record at 0x20: dims pair (479,639)
(S16 swapped => 639x479). Walk the RLE at rec+0x18 (k0 law: stream rec+0x08?
try both). Save PNG via game.pal (fallback titlepalette). Prints geometry
only.
"""
import struct, os
from PIL import Image

D = '/home/hrethric/projects/ascendancy/extracted/ascend01/data'
raw = open(os.path.join(D, 'game.pal'), 'rb').read()
pal = []
for i in range(256):
    r, g, b = raw[i*3], raw[i*3+1], raw[i*3+2]
    conv = lambda v: (v << 2) | (v >> 4)
    pal.append((conv(r), conv(g), conv(b)))


def walk(data, stream, W, H):
    out = [None] * (W * H)
    pos = 0
    for row in range(H):
        px = 0
        while True:
            if stream + pos >= len(data):
                return out, row, 'EOF'
            c = data[stream + pos]; pos += 1
            if c == 0:
                break
            if c == 1:
                L = data[stream + pos]; pos += 1; px += L; continue
            if c & 1:
                n = c >> 1
                for j in range(n):
                    v = data[stream + pos + j]
                    if px < W:
                        out[row * W + px] = v
                    px += 1
                pos += n
            else:
                v = data[stream + pos]; pos += 1
                n = c >> 1
                for j in range(n):
                    if px < W:
                        out[row * W + px] = v
                    px += 1
            if px > W + 400:
                return out, row, 'ROW-OVERRUN'
    return out, H, 'OK'


for name in ('3cfgnew.tmp',):
    data = open(os.path.join(D, name), 'rb').read()
    count, tsz = struct.unpack_from('<II', data, 4)
    rec = 0x10 + tsz
    w, h = struct.unpack_from('<II', data, rec)
    print(f'{name}: count={count} tsz={tsz} rec={rec:#x} dims=({w},{h}) len={len(data)}')
    for (W, H, soff, tag) in ((639, 479, rec + 0x08, 'k0-law'),
                              (639, 479, rec + 0x18, 'k1-law'),
                              (479, 639, rec + 0x08, 'swap-k0'),
                              (479, 639, rec + 0x18, 'swap-k1')):
        pix, rows, st = walk(data, soff, W, H)
        nonnull = sum(1 for v in pix if v is not None)
        print(f'  {tag}: W={W} H={H} stream={soff:#x} -> {st} rows={rows} px={nonnull}')
        if st == 'OK' and nonnull > W * H * 0.5:
            im = Image.new('RGB', (W, H), (0, 0, 0))
            pxl = im.load()
            for y in range(H):
                for x in range(W):
                    v = pix[y * W + x]
                    if v is not None:
                        pxl[x, y] = pal[v]
            outp = f'/home/hrethric/projects/ascendancy/work/r1/t423-{name}.png'
            im.save(outp)
            print(f'  SAVED {outp}')
            break
