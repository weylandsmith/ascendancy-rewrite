#!/usr/bin/env python3
# t390 debug: print code trace of the python decoder around output 27205.
from PIL import Image

im = Image.open('/home/hrethric/projects/ascendancy/extracted/ascend01/data/0opening.gif')
im.load()
ref = im.tobytes()
d = open('/home/hrethric/projects/ascendancy/extracted/ascend01/data/0opening.gif', 'rb').read()
i = 781 + 10
mcs = d[i]; i += 1
comp = bytearray()
while d[i]:
    comp += d[i+1:i+1+d[i]]
    i += d[i] + 1

width = mcs + 1
clear, eoi = 256, 257
next_code = 258
table = {}
prev = None
out = 0
acc = 0
nbits = 0
pos = 0
trace = []
while pos < len(comp):
    while nbits < width and pos < len(comp):
        acc |= comp[pos] << nbits
        pos += 1
        nbits += 8
    code = acc & ((1 << width) - 1)
    acc >>= width
    nbits -= width
    if code == eoi:
        break
    if 27190 <= out <= 27215:
        trace.append((out, width, code, next_code))
    if code == clear:
        width = mcs + 1; next_code = 258; table = {}; prev = None
        continue
    if code < 256:
        entry = bytes([code])
    elif code in table:
        entry = table[code]
    elif code == next_code and prev is not None:
        entry = prev + prev[:1]
    else:
        raise RuntimeError('bad code %d next %d at %d' % (code, next_code, out))
    out += len(entry)
    if prev is not None:
        table[next_code] = prev + entry[:1]
        next_code += 1
        if width < 12 and next_code >= (1 << width):
            width += 1
    prev = entry
for t in trace:
    print("out=%d width=%d code=%d next=%d" % t)
print("ref[27200:27215]", list(ref[27200:27215]))
