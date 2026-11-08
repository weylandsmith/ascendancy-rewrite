#!/usr/bin/env python3
"""t344 DECISIVE OFFLINE TEST of the vendor dims law.

Static law just derived (work/r331_disasm.txt verbatim):
  fn 0x61058(lib, idx):  rec = lib + 8 + 8*idx; rec = lib + [rec]
      W = u32[rec+0x10] - u32[rec+0x8]  + 1
      H = u32[rec+0x14] - u32[rec+0xc]  + 1
      return (W << 16) | H          (0x64f17..0x64f36 consume it that way:
      ds:0xa2090=H? no: sar16->0xa2090, &0xffff->0xa20cc, area=prod @0xa20a0)
  fn 0x6108c(lib, idx): return (u32[rec+0x8] << 16) | u16[rec+0xc]
  The cursor chain fn 0x1be10 -> fn 0x5a1e4 -> fn 0x30a60 -> fn 0x64ea9
  calls BOTH on (lib=[core+0x733] = the MOUSE.SHP object, idx=shape id).
  lib layout = .shp pool: [lib+8+8*idx] = u32 file offset of record (TOC).

If the .shp FILE bytes satisfy fn 0x61058's formula for the records t330
witnessed live (mouse k0 -> (11,15), k2), then the file IS the runtime
record and the formula predicts k5/k6/k7 dims with ZERO capture.
"""
import struct, os

P = "extracted/ascend01/data/mouse.shp"
if not os.path.exists(P):
    # fall back to the verbatim copy t330 banked from the save
    P = None
    print("extracted mouse.shp missing; searching banked copies...")
    import glob
    for c in glob.glob("work/r1/**/*mouse*", recursive=True):
        print("  candidate:", c)
    raise SystemExit(1)

d = open(P, "rb").read()
print("mouse.shp size:", len(d), hex(len(d)))

u32 = lambda off: struct.unpack_from("<I", d, off)[0]
u16 = lambda off: struct.unpack_from("<H", d, off)[0]

# header: t328 law -- count + TOC? print first 0x70 bytes as u32 grid
print("header u32s @0..0x68:", [hex(u32(i)) for i in range(0, 0x6c, 4)])
print("count u16@0:", u16(0))

# The TOC law from fn 0x61058: rec_off = [lib+8+8*idx]. lib base = image
# load of the pool; in the FILE, the TOC should sit at file offset 8 with
# stride 8 (u32 off + u32 aux). Verify against t330's witnessed record file
# offsets: k0 @0x68, k2 @0x257.
print("\nTOC probe (u32 @8+8*i, aux @12+8*i):")
n = u16(0) if u16(0) < 64 else 12
for i in range(0, 12):
    off = 8 + 8 * i
    if off + 8 > len(d):
        break
    print("  idx %2d: rec_off=%s aux=%s" % (i, hex(u32(off)), hex(u32(off + 4))))
