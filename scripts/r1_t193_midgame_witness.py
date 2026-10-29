#!/usr/bin/env python3
"""t193: mid-game witness probe for the lane/star visibility share law.

The t192 corpus (new-game saves) produced the honest negative "share path
ZERO witnesses: pool +0x20 census all single-bit". The user has now played a
MID-GAME sitting (Oct-29 12:30..13:03, t=1086, war Chamachies<->Minions,
peace elsewhere, alliances absent from the first-row matrix). Re-measure
against the SAME addressing law as r1_t192_share_mask_scan.py (mem[B+D+X],
blob_offset = guest_phys + 0x88):

  1. pool +0x20 census over nlanes records, per save AND aggregate --
     MULTI-BIT values = share-path witnesses (0x463eb/0x46421 OR a second
     empire's bit onto a lane the first already revealed).
  2. race r's sub-list == EXACTLY {lanes rec+0x20 == 1<<r}? (t192 law
     re-check on mid-game state).
  3. rec+0x21 census (MAP byte -- t192 found all-zero, writer unknown).
  4. star-obj +0x16/+0x17 census (star twin FUN_00046524).
Prints small aggregates only. RC=0 always.
"""
import os, sys, struct, zipfile, collections
sys.path.insert(0, "/home/hrethric/projects/ascendancy/scripts")
from r1_sav_scan import build_anchors, find_base

ROOT = "/home/hrethric/projects/ascendancy"
RUN = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "work/r1/playcap")
PAY = os.path.join(ROOT, "work/ascend_payload.bin")
D = 0x82BB0
PHYS = 0x88
X_CUR = 0x7458E
X_ROW, STRIDE_ROW = 0x12E16, 0x1EE
X_SUBPTR = 0x12E1D
X_POOL, S_POOL = 0x16147, 0x27
X_NLANES, X_NSTAR, X_NRACES = 0x177D3, 0x16145, 0x13B98
STAR_BASE, S_STAR = 0x13BC5, 0x60


def saves():
    sd = os.path.join(RUN, "save")
    for f in sorted(os.listdir(sd)):
        if f.endswith(".sav"):
            yield os.path.join(sd, f)


def main():
    pay = open(PAY, "rb").read()
    anch = build_anchors(pay)
    agg_lane20 = collections.Counter()
    agg_lane21 = collections.Counter()
    agg_star16 = collections.Counter()
    agg_star17 = collections.Counter()
    multi_witness = []
    eq_ok = eq_bad = 0
    eq_detail = []
    nsave = 0
    for p in saves():
        try:
            mem = zipfile.ZipFile(p).read("Memory")
        except Exception:
            continue
        votes, _ = find_base(mem, anch)
        if not votes:
            continue
        B = votes.most_common(1)[0][0]
        M = B + D
        nsave += 1
        idx = mem[M + X_CUR]
        nr = struct.unpack_from("<H", mem, M + X_NRACES)[0]
        nlane = struct.unpack_from("<H", mem, M + X_NLANES)[0]
        nstar = struct.unpack_from("<H", mem, M + X_NSTAR)[0]
        pool = M + X_POOL
        # 1+3: lane mask census
        lane_mask = {}
        for k in range(nlane):
            rec = pool + S_POOL * k
            b20 = mem[rec + 0x20]
            b21 = mem[rec + 0x21]
            lane_mask[rec] = b20
            agg_lane20[b20] += 1
            agg_lane21[b21] += 1
            if b20 and (b20 & (b20 - 1)):
                multi_witness.append((os.path.basename(p), k, hex(b20)))
        # 2: per-race list equality vs {rec+0x20 == 1<<r}
        for r in range(min(nr, 8)):
            sub_phys = struct.unpack_from("<I", mem, M + X_SUBPTR + STRIDE_ROW * r)[0]
            sub = sub_phys + PHYS
            if not (0x1000 < sub < len(mem) - 0x900):
                continue
            cnt = struct.unpack_from("<H", mem, sub + 0x44)[0]
            lst = set()
            for i in range(min(cnt, 400)):
                rp = struct.unpack_from("<I", mem, sub + 0x2C + 4 * i)[0]
                rec = rp + PHYS
                if rp and 0x1000 < rec < len(mem) - 8 and rec >= pool:
                    d = rec - pool
                    if d % S_POOL == 0 and d // S_POOL < nlane:
                        lst.add(rec)
            want = {rec for rec, m_ in lane_mask.items() if m_ == (1 << r)}
            if lst == want:
                eq_ok += 1
            else:
                eq_bad += 1
                if len(eq_detail) < 12:
                    eq_detail.append(
                        f"{os.path.basename(p)} r={r} cnt={cnt} "
                        f"list={sorted((x-pool)//39 for x in lst)} "
                        f"want={sorted((x-pool)//39 for x in want)} "
                        f"extra={sorted((x-pool)//39 for x in lst-want)} "
                        f"missing={sorted((x-pool)//39 for x in want-lst)}")
        # 4: star twin
        for k in range(nstar):
            so = M + STAR_BASE + S_STAR * k
            agg_star16[so] = agg_star16.get(so, 0)
            s16 = struct.unpack_from("<H", mem, so + 0x16)[0]
            s17 = struct.unpack_from("<H", mem, so + 0x17)[0]
            agg_star16[s16 & 0xFF] += 1
            agg_star17[s17 & 0xFF] += 1
    print(f"saves={nsave} cur_idx_census_note=see per-save lines below")
    print("== lane rec+0x20 census (aggregate) ==")
    print("  " + ", ".join(f"{v}:{n}" for v, n in sorted(agg_lane20.items())))
    print("  MULTI-BIT witnesses (share path fired): " +
          (str(multi_witness[:20]) if multi_witness else "NONE"))
    print("== lane rec+0x21 census (aggregate) ==")
    print("  " + ", ".join(f"{v}:{n}" for v, n in sorted(agg_lane21.items())))
    print(f"== per-race list == mask-law: ok={eq_ok} bad={eq_bad} ==")
    for d in eq_detail:
        print("  " + d)
    print("== star obj +0x16 byte census ==")
    print("  " + ", ".join(f"{v}:{n}" for v, n in sorted(agg_star16.items())))
    print("== star obj +0x17 byte census ==")
    print("  " + ", ".join(f"{v}:{n}" for v, n in sorted(agg_star17.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
