#!/usr/bin/env python3
# t390: python mirror of the intended C++ chain decoder, tested against the
# PIL reference plane BEFORE the C++ is trusted. Two growth variants:
#   A: grow when next+1 >= 2**width  (my C++ law)
#   B: grow when next >= 2**width    (textbook)
# Prints which variant reproduces PIL's plane exactly.
import sys
from PIL import Image

im = Image.open('/home/hrethric/projects/ascendancy/extracted/ascend01/data/0opening.gif')
im.load()
ref = im.tobytes()

d = open('/home/hrethric/projects/ascendancy/extracted/ascend01/data/0opening.gif', 'rb').read()
# locate LZW data: image descriptor at 781, packed 0, mcs at 792
i = 781 + 10
mcs = d[i]; i += 1
comp = bytearray()
while d[i]:
    comp += d[i+1:i+1+d[i]]
    i += d[i] + 1


def decode(variant):
    width = mcs + 1
    clear, eoi = 256, 257
    next_code = 258
    table = {}
    prev = None
    out = bytearray()
    acc = 0
    nbits = 0
    pos = 0
    while pos < len(comp):
        while nbits < width and pos < len(comp):
            acc |= comp[pos] << nbits
            pos += 1
            nbits += 8
        if nbits < width:
            break
        code = acc & ((1 << width) - 1)
        acc >>= width
        nbits -= width
        if code == eoi:
            break
        if code == clear:
            width = mcs + 1
            next_code = 258
            table = {}
            prev = None
            continue
        if code < 256:
            entry = bytes([code])
        elif code in table:
            entry = table[code]
        elif code == next_code and prev is not None:
            entry = prev + prev[:1]
        else:
            raise RuntimeError('bad code %d next %d at %d' % (code, next_code, len(out)))
        out += entry
        if prev is not None:
            table[next_code] = prev + entry[:1]
            next_code += 1
            if variant == 'A':
                if width < 12 and next_code + 1 >= (1 << width):
                    width += 1
            else:
                if width < 12 and next_code >= (1 << width):
                    width += 1
        prev = entry
    return bytes(out)


for v in ('A', 'B'):
    try:
        got = decode(v)
        print(v, 'len', len(got), 'match' if got == ref else 'MISMATCH',
              'first-diff', next((k for k in range(min(len(got), len(ref))) if got[k] != ref[k]), None))
    except RuntimeError as e:
        print(v, 'ERROR', e)
