#!/usr/bin/env python3
"""t414: decode 3cfgnew.shp k0..k12 with the port's own decoder path (via a
small C++ driver would be heavy; reuse the unified-law Python walk + game.pal)
and emit a labelled montage for native-vision classification."""
import struct
from PIL import Image

PATH = '/tmp/uishow/extracted/ascend01/data/3cfgnew.shp'
PAL = '/tmp/uishow/extracted/ascend01/data/game.pal'

data = open(PATH, 'rb').read()
raw = open(PAL, 'rb').read()
pal = []  # gamepal.cpp law: 768 bytes, 3B/entry, DOSBox 6->8 bit
for i in range(256):
    r, g, b = raw[i * 3], raw[i * 3 + 1], raw[i * 3 + 2]
    conv = lambda v: (v << 2) | (v >> 4)
    pal.append((conv(r), conv(g), conv(b)))

count, tsz = struct.unpack_from('<II', data, 4)
starts = [struct.unpack_from('<Q', data, 0x10 + 8 * i)[0] for i in range(count - 1)]


def decode(stream, W, H):
    out = [None] * (W * H)
    pos = 0
    for row in range(H):
        px = 0
        while True:
            if stream + pos >= len(data):
                return None
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
                        out[row * W + px] = v; px += 1
                pos += n
            else:
                v = data[stream + pos]; pos += 1
                n = c >> 1
                for j in range(n):
                    if px < W:
                        out[row * W + px] = v; px += 1
            if px > W + 400:
                return None
    return out


imgs = []
for k in range(count):
    rec = (0x10 + tsz) if k == 0 else starts[k - 1]
    off = rec if k == 0 else rec + 0x10
    w, h = struct.unpack_from('<II', data, off)
    stream = rec if k == 0 else rec + 0x18
    pix = decode(stream, w, h)
    if pix is None:
        pix = decode(stream, h, w)
        w, h = h, w
    if pix is None:
        print(f'k{k}: decode FAIL')
        imgs.append((k, None, 0, 0))
        continue
    im = Image.new('RGB', (w, h), (0, 0, 0))
    px = im.load()
    for y in range(h):
        for x in range(w):
            v = pix[y * w + x]
            px[x, y] = pal[v] if v is not None else (0, 0, 0)
    imgs.append((k, im, w, h))

# montage 5 per row
cols = 5
cw = max((w for _, _, w, _ in imgs if w), default=84)
ch = max((h for _, _, _, h in imgs if h), default=80)
M = Image.new('RGB', (cols * (cw + 6), ((len(imgs) + cols - 1) // cols) * (ch + 6)), (30, 30, 30))
for i, (k, im, w, h) in enumerate(imgs):
    if im is None:
        continue
    M.paste(im, ((i % cols) * (cw + 6), (i // cols) * (ch + 6)))
M.save('/tmp/t414-3cfgnew-montage.png')
print('saved /tmp/t414-3cfgnew-montage.png', M.size)
for k, im, w, h in imgs:
    if im is None:
        continue
    im.resize((w * 2, h * 2), Image.NEAREST).save(f'/tmp/t414-k{k:02d}.png')
