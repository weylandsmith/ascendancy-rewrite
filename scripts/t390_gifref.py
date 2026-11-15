#!/usr/bin/env python3
# t390: emit the reference hashes for the C++ GIF decoder pins (PIL plane =
# reference rasterizer law, t386 S6.3). Run under the venv python.
import hashlib
from PIL import Image

im = Image.open('/home/hrethric/projects/ascendancy/extracted/ascend01/data/0opening.gif')
im.load()
pl = im.tobytes()


def fnv(b):
    h = 0xcbf29ce484222325
    for v in b:
        h ^= v
        h = (h * 0x100000001b3) & 0xFFFFFFFFFFFFFFFF
    return h


print("fnv full  ", hex(fnv(pl)))
print("fnv 4096  ", hex(fnv(pl[:4096])))
print("fnv 6144  ", hex(fnv(pl[:6144])))
print("fnv row0  ", hex(fnv(pl[:640])))
print("sha full  ", hashlib.sha256(pl).hexdigest())
print("sha 4096  ", hashlib.sha256(pl[:4096]).hexdigest())
print("sha row0  ", hashlib.sha256(pl[:640]).hexdigest())
print("distinct", len(set(pl)), "key255", pl.count(255))
print("row0 first16", pl[:16].hex())
