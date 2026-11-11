#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t319: offline poster-gate operand read from a save.

The poster block (fn containing 0x54a3f, in main-loop fn 0x54650) decides the
pump msg id from core-object members + patched ds: globals:
  msg 0xc  iff  edi == [obj+0x24da4]  AND  [obj+0x489e] == 0   (0x54a88 road)
  equal road    iff  edi == ds:0x484a4-rebased                  (0x54a47 road)
  equal road posts ONLY if [[obj+0x21d92]+0x39] != 0            (0x54a72 gate)
Laws (VERBATIM this session, work/t91_code_disasm.txt 77080-77250 + t316/t308):
- Addressing law EXACTLY as the session oracle (r299_leg_session sel_oracle):
  sav offset of raw/ds address X = B + SL.OFF + X (SL.OFF=0x82bb0, B = anchor);
  core member of offset D = same with X = 0x7a35c + D. (The patched code imm
  0x2bc35c is the GUEST-LINEAR core addr; the sav member is 0x88 lower — the
  t308 law. Do NOT index the sav by guest linear.)
- Patched ds: storage = raw address read via the law above (no DB arithmetic).
- obj = patched imm of `mov $0x7a35c,%eax` @0x33397 (r316 law, guest-linear).
Prints per-save: obj, [obj+0x24da4], [obj+0x489e], [obj+0x24da8],
[obj+0x48a6], [obj+0x21d92] (+ its +0x39 deref via the law if plausible),
ds:0x484a4/0x484ec/0x484ac/0x484d0/0x484dc/0x484c4/0x484c6, mode4226>>16.
Usage: r319_gate_read.py <sav> [<sav> ...]
"""
import re, struct, sys, zipfile

PAYLOAD = "/home/hrethric/projects/ascendancy/work/ascend_payload.bin"
pl = open(PAYLOAD, "rb").read()
ANCHOR = pl[0x51834:0x51834 + 48]
OFF = 0x82bb0   # r1_slot.OFF (same constant the session oracle uses)

def read(path):
    mem = zipfile.ZipFile(path).read("Memory")
    def u32(a):
        return struct.unpack_from("<I", mem, a)[0] if 0 <= a <= len(mem) - 4 else None
    hits = [m.start() for m in re.finditer(re.escape(ANCHOR), mem)]
    if not hits:
        print(f"{path}: NO ANCHOR"); return
    B = hits[0] - 0x51834
    rd = lambda X: u32(B + OFF + X)          # raw/ds address X
    rdc = lambda D: rd(0x7a35c + D)          # core member offset D
    obj = u32(B + 0x33398)                   # guest-linear core addr (code imm)
    out = {"sav": path.split("/")[-1], "B": hex(B), "obj": hex(obj)}
    for name, d in [("m24da4", 0x24da4), ("m489e", 0x489e), ("m24da8", 0x24da8),
                    ("m48a6", 0x48a6), ("m21d92", 0x21d92)]:
        out[name] = hex(rdc(d))
    out["mode4226_hi"] = hex(rdc(0x4226) >> 16)
    p21 = rdc(0x21d92)
    # deref [[obj+0x21d92]+0x39]: p21 is GUEST-LINEAR (t308 law: linear =
    # DB + raw, DB = obj - 0x7a35c = 0x242000), so its sav member is
    # B + OFF + (p21 - DB).
    DB = obj - 0x7a35c if obj else None
    v39 = (u32(B + OFF + (p21 - DB) + 0x39)
           if (p21 is not None and DB and DB <= p21 < DB + 0x800000) else None)
    out["m21d92_p39"] = hex(v39) if v39 is not None else "implausible"
    for name, raw in [("ds484a4", 0x484a4), ("ds484ec", 0x484ec),
                      ("ds484ac", 0x484ac), ("ds484d0", 0x484d0),
                      ("ds484dc", 0x484dc), ("ds484c4", 0x484c4),
                      ("ds484c6", 0x484c6)]:
        out[name] = hex(rd(raw))
    print(" ".join(f"{k}={v}" for k, v in out.items()))

for p in sys.argv[1:]:
    read(p)
