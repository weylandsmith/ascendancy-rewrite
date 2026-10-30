#!/usr/bin/env python3
"""t202d — final +0x4c model comparison over the 20-save corpus.
Per record compute candidate models and histogram EXACT-EXACT agreement:
  M1 inactU           (S6 verbatim: UPOP over INACTIVE non-23 non-0x40 non-slotflag2)
  M2 actU             (same but ACTIVE)
  M3 actU+1
  M4 actU+inactU
  M5 actU+UPOP(pending)      (pending item idx at sys+0x54, 0xff none)
  M6 actU+inactU+UPOP(pending)
  M7 clamp(pop, actU+inactU+UPOP(pending))
Also census governor byte sys+0x54 values and (owner,ab) pairs. RC=0.
"""
import os, sys, re, struct, zipfile, collections
sys.path.insert(0, "/home/hrethric/projects/ascendancy/scripts")
from r1_sav_scan import build_anchors, find_base
ROOT = "/home/hrethric/projects/ascendancy"
P0 = 0x26D07B
RUN = sys.argv[1] if len(sys.argv) > 1 else f"{ROOT}/work/r1/playcap"
agree = collections.Counter()
gov_c = collections.Counter()
pend_c = collections.Counter()
fail_rows = []
tot = 0
anch = build_anchors(open(f"{ROOT}/work/ascend_payload.bin", "rb").read())
for f in sorted(os.listdir(os.path.join(RUN, "save"))):
    if not f.endswith(".sav"):
        continue
    mem = zipfile.ZipFile(os.path.join(RUN, "save", f)).read("Memory")
    votes, _ = find_base(mem, anch)
    H = votes.most_common(1)[0][0] - 0x1BF450
    B = H + 0x1BF450
    IT = lambda i: B + 0x82bb0 + 0x73e40 + 0x28 * i
    n = 0
    while mem[P0 + n * 123 + H] and re.match(
            rb"[A-Z][A-Za-z]{2,}(?: [IVX]+)?\x00",
            mem[P0 + n * 123 + H:P0 + n * 123 + H + 40]):
        n += 1
    for k in range(n):
        j = P0 + k * 123 + H
        rec = j - 0x24
        cells = struct.unpack_from("<H", mem, rec + 0x18)[0]
        capw = struct.unpack_from("<H", mem, rec + 0x1a)[0]
        if cells not in (7, 11, 23, 45, 73) or capw != cells + 10:
            continue
        pop = struct.unpack_from("<H", mem, rec + 0x42)[0]
        cap = struct.unpack_from("<H", mem, rec + 0x4a)[0]
        used = struct.unpack_from("<H", mem, rec + 0x4c)[0]
        pend = struct.unpack_from("<H", mem, rec + 0x54)[0]
        gov_c[pend] += 1
        own = mem[rec + 0x57]
        ptr = struct.unpack_from("<I", mem, rec + 0x10)[0]
        if not (0x100000 < ptr < 0x800000):
            continue
        act = inact = 0
        for si in range(capw):
            s = ptr + 0x88 + 4 * si
            it = mem[s + 1]
            fl = struct.unpack_from("<H", mem, s + 2)[0]
            if it == 0xff or it == 23:
                continue
            ia = IT(it)
            if mem[ia + 6] & 0x40 or fl & 2:
                continue
            if fl & 1:
                act += mem[ia + 4]
            else:
                inact += mem[ia + 4]
        pu = mem[IT(pend) + 4] if pend != 0xFFFF and pend < 39 else 0
        pend_c[(pend != 0xFFFF, pu)] += 1
        models = {"M1": inact, "M2": act, "M3": act + 1, "M4": act + inact,
                  "M5": act + pu, "M6": act + inact + pu,
                  "M7": min(pop, act + inact + pu)}
        hits = [m for m, v in models.items() if v == used]
        agree[tuple(hits)] += 1
        if not hits and len(fail_rows) < 10:
            fail_rows.append((f, k, own, cap, pop, used, act, inact, pend, pu))
        tot += 1
print("tot", tot)
print("gov(+0x54) census:", dict(sorted(gov_c.items())))
print("pending(non-ff, upop):", dict(pend_c))
for pat, c in agree.most_common():
    print(f"pattern {','.join(pat) or 'NONE'}: {c}")
print("fails:", fail_rows)
