#!/usr/bin/env python3
"""t259 sav-pair census: which banked/ring savstates exist, and do any two
share a TURN but differ in V (DAT_482fb)? Bounded RSS: one Memory member at a
time. Prints one line per sav + a PAIRS summary. NEVER loads the timeline."""
import glob, os, sys, struct, zipfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import r1_slot as S

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(root)
pay = S.load_payload(root)
anch = S.anchors_cached(root, pay)

dirs = sorted(glob.glob("work/r1/bank-*")) + ["work/r1/playcap/save"]
rows = []
for d in dirs:
    for sp in sorted(glob.glob(os.path.join(d, "*.sav"))):
        try:
            mem = zipfile.ZipFile(sp).read("Memory")
        except Exception as e:
            print(f"{sp}: UNZIP FAIL {repr(e)[:60]}")
            continue
        if len(mem) < 0x90000:
            print(f"{sp}: mem too small {len(mem)}")
            del mem
            continue
        B = S.base_of(mem, anch)
        if B is None:
            print(f"{sp}: no base vote")
            del mem
            continue
        t = struct.unpack_from("<I", mem, B + S.OFF + 0x12e10)[0]
        v = struct.unpack_from("<I", mem, B + S.OFF + 0x482fb)[0]
        T = struct.unpack_from("<I", mem, B + S.OFF + 0x16143)[0] >> 16
        mt = os.path.getmtime(sp)
        rows.append((sp, t, v, T, mt))
        del mem

print(f"census: {len(rows)} savs")
# group by turn
by_turn = {}
for sp, t, v, T, mt in rows:
    by_turn.setdefault(t, []).append((v, sp))
pairs = []
for t, lst in sorted(by_turn.items()):
    vs = sorted({v for v, _ in lst})
    if len(vs) > 1:
        pairs.append((t, vs, [sp for _, sp in lst]))
        print(f"SAME-TURN-DIFF-V t={t} V={vs}")
        for v, sp in sorted(lst):
            print(f"    V={v:<3} {sp}")
if not pairs:
    print("PAIRS: NONE — no two banked/ring savs share a turn with different V")
# also print full table compactly
print("--- full table ---")
for sp, t, v, T, mt in sorted(rows, key=lambda r: (r[1], r[2])):
    print(f"t={t:<5} V={v:<3} T={T} {sp}")
