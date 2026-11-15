#!/usr/bin/env python3
# t390 debug: stream-level events (clears, table-full) of the reference decode.
from PIL import Image
im = Image.open('/home/hrethric/projects/ascendancy/extracted/ascend01/data/0opening.gif')
im.load()
ref = im.tobytes()
d = open('/home/hrethric/projects/ascendancy/extracted/ascend01/data/0opening.gif', 'rb').read()
i = 781 + 10
mcs = d[i]; i += 1
comp = bytearray()
while d[i]:
    comp += d[i + 1:i + 1 + d[i]]
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
nclear = 0
events = []
while pos < len(comp):
    while nbits < width and pos < len(comp):
        acc |= comp[pos] << nbits
        pos += 1
        nbits += 8
    code = acc & ((1 << width) - 1)
    acc >>= width
    nbits -= width
    if code == eoi:
        events.append(('eoi', out, next_code))
        break
    if code == clear:
        nclear += 1
        events.append(('clear', out, next_code))
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
        events.append(('bad', code, next_code, out))
        break
    out += len(entry)
    if prev is not None:
        table[next_code] = prev + entry[:1]
        next_code += 1
        if width < 12 and next_code >= (1 << width):
            width += 1
        if next_code == 4096:
            events.append(('full', out))
    prev = entry
print("nclear", nclear)
print("events", events[:20])
print("end out", out, "next", next_code)
