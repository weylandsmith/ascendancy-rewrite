#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""r1_income_channels.py — per-channel income-law battery (OQ-016 income
half; docs landing docs/re/economy.md S6 t20). Exit 0 iff IND and PROS
each fit >=95% under the banked model.

MODEL (disassembly-faithful; FUN_00038ba4 0x38e2d/0x38e31 JZ-skip):
  stored IND = accI == 0 ? G_I : trunc((dbl(accI,f12)+1)^0.85)
  stored PROS= accP == 0 ? G_P : max(0, trunc((dbl(accP,f13)+1)^0.85) - (|up|>>2))
  stored RES = accR (raw, never compressed)
  t35 CORRECTION: every channel accumulator adds the class-cell +1 bonus
  ONLY when the item's own channel field is non-zero (disasm nests the
  bonus inside the field test; RES proof: 49 cls-4-on-res-0 slots in
  exactly 49 distinct owned records == the 49 pre-fix failures). Battery
  with corrected array + gating: IND 173/173 PROS 173/173 RES 173/173
  (old banked 138/139 + 136/139 were raw-array runs; the RES misses were
  the gating bug, not grants).
  dbl(v,f) = v + (v>>1 if f); f12/f13 = ACTIVE flag of the FIRST slot whose
  itemIdx==12/13 (FUN_0003958c + caller bit-test @0x38d4b..0x38dd9).
  G_I, G_P per-record grants: colonization +1 to both linked home records
  (FUN_00025d30), ship-completion INC [ESI+0x44] @0x21b85, scenario
  template copy into 0x42..0x55 (FUN_0003a558 @0x3a611..0x3a64d). The JZ
  skip at 0x38e31 (acc==0) is what lets post-store grants survive: recalc
  NEVER overwrites income fields of a facility-free planet. Governor
  0x21/0x22/0x23 (P/R += IND>>2, O += byte@0x743b9) tried both raw and
  compressed IND: 134/139 either way; misses are the grant rows below.
  G_* here are INFERRED per record as (stored when acc==0) — that is
  exactly the banked grant definition, not a free parameter fit for acc>0.
"""
import os, struct as st, sys, sys as _s, zipfile
_s.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_income_fit as F


def dbl(v, f):
    return v + ((v >> 1) if f else 0)


def main():
    pay = open(F.PAY, "rb").read()
    anch = F.build_anchors(pay)
    rows = []
    grants = {}
    for run in F.RUNS:
        src = os.path.join(run, "save")
        for f in sorted(f for f in os.listdir(src) if f.endswith(".sav"))[:1]:
            m = zipfile.ZipFile(os.path.join(src, f)).read("Memory")
            v, _ = F.find_base(m, anch)
            if not v:
                continue
            B = v.most_common(1)[0][0]
            items = F.item_table(m, B)
            if items is None or not F.names_ok(items):
                continue
            for base in F.find_records(m):
                if m[base + 0x57] == 0xFF:
                    continue
                cap = st.unpack_from("<H", m, base + 0x1a)[0]
                # +0x10 = heap OBJECT address; member array at object+0x88
                # (pointer law; see r1_income_law.find_records, t33).
                arr = st.unpack_from("<I", m, base + 0x10)[0] + 0x88
                if not (0 <= arr and arr + cap * 4 <= len(m)):
                    continue
                ai = ap = ar = 0
                f12 = f13 = None
                gov = m[base + 0x54]
                up = st.unpack_from("<h", m, base + 0x42)[0]
                si = st.unpack_from("<H", m, base + 0x44)[0]
                sp = st.unpack_from("<H", m, base + 0x48)[0]
                sr = st.unpack_from("<H", m, base + 0x46)[0]
                for i in range(cap):
                    cls = m[arr + i * 4]
                    it = m[arr + i * 4 + 1]
                    act = bool(st.unpack_from("<H", m, arr + i * 4 + 2)[0] & 1)
                    if f12 is None and it == 12:
                        f12 = act
                    if f13 is None and it == 13:
                        f13 = act
                    if it != 0xFF and act:
                        # t35 GATING [verified two ways]: each channel's +1
                        # class bonus is nested INSIDE the item's own
                        # channel-field non-zero test (FUN_00038ba4: `if
                        # (*(char*)(&DAT_00073e41+uVar3*10) != 0) { acc +=
                        # field; if (cls == 4) acc += 1; }` — Ghidra shows
                        # the comma-joined side effects on BOTH legs). An
                        # item with res==0 sitting on a class-4 cell grants
                        # NOTHING: 49 such slots in exactly 49 distinct
                        # owned records == the battery's 49 pre-fix RES
                        # failures, one-for-one. cls2-ind==0 / cls3-pros==0
                        # never occur in this corpus (0 samples), so the
                        # IND/PROS legs are instruction-level-verified only.
                        d = items[it]
                        if d["ind"]:
                            ai += d["ind"] + (1 if cls == 2 else 0)
                        if d["pros"]:
                            ap += d["pros"] + (1 if cls == 3 else 0)
                        if d["res"]:
                            ar += d["res"] + (1 if cls == 4 else 0)
                key = (os.path.basename(run), base)
                gi0, gp0 = grants.get(key, (0, 0))
                if ai == 0:
                    gi0 = max(gi0, si)
                if ap == 0:
                    gp0 = max(gp0, sp)
                grants[key] = (gi0, gp0)
                rows.append((key, ai, ap, ar, f12, f13, gov, up, si, sp, sr))

    nI = np_ = nR = 0
    misses = []
    for (key, ai, ap, ar, f12, f13, gov, up, si, sp, sr) in rows:
        gi, gp = grants.get(key, (0, 0))
        vi = gi if ai == 0 else int((dbl(ai, f12) + 1) ** 0.85)
        vp = gp if ap == 0 else max(0, int((dbl(ap, f13) + 1) ** 0.85) - (abs(up) >> 2))
        nI += vi == si
        np_ += vp == sp
        nR += ar == sr
        if (vi, vp) != (si, sp):
            misses.append((key, ai, ap, f12, f13, up, (si, sp), (vi, vp)))
    n = len(rows)
    print(f"records {n}:  IND {nI}/{n}  PROS {np_}/{n}  RES {nR}/{n}")
    for mm in misses:
        print("  MISS", mm)
    return 0 if n and nI >= 0.95 * n and np_ >= 0.95 * n else 1


if __name__ == "__main__":
    sys.exit(main())
