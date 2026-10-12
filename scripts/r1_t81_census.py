#!/usr/bin/env python3
"""r1_t81_census.py — OQ-003 planet-record field census (t81).

Cohort: 20-slot r1deep timeline (real turns, idle+boundary phases).
BASE CONVENTION (declared): income-law banked base = planet-NAME - 0x24,
records enumerated ONLY via r1_income_law.find_records (name-anchored,
cells/cap gated; 151/151 on r1deep). Offsets in output are banked.

For each offset 0..0x7a emit: records_changed / 151, and per-record
trajectory shape over the timeline:
  mono  = value never decreases
  updown= value both rises and falls
  flat  = never changes
Cross-aids printed for interpretation on owned records: banked closed
words +0x44 IND, +0x46 RES, +0x48 PROS, +0x1c/+0x1e/+0x20 counters,
+0x4a/+0x4c pop counters, +0x54 queue-byte, +0x57 owner.
"""
import os, struct as st, sys, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_sav_scan import build_anchors, find_base
from r1_income_law import find_records

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN = os.path.join(ROOT, "work", "r1", "r1deep-20261005-230146", "save")


def slots():
    pay = open(os.path.join(ROOT, "work", "ascend_payload.bin"), "rb").read()
    anch = build_anchors(pay)
    out = []
    for f in sorted(os.listdir(RUN), key=lambda x: int(x.split(".")[0])):
        if not f.endswith(".sav"):
            continue
        m = zipfile.ZipFile(os.path.join(RUN, f)).read("Memory")
        v, _ = find_base(m, anch)
        if not v:
            print(f"{f}: NO BASE", file=sys.stderr)
            continue
        out.append((f, m, v.most_common(1)[0][0]))
    return out


def main():
    S = slots()
    if not S:
        return 2
    # enumerate records on first slot, then verify identical name-set on all
    base_recs = find_records(S[0][1])
    names = [S[0][1][r[0] + 0x24:r[0] + 0x24 + 20].split(b"\x00")[0] for r in base_recs]
    bases_by_name = {n: r[0] for n, r in zip(names, base_recs)}
    T = {}  # name -> {off: [u16 per slot]}
    ok_slots = 0
    for f, m, P0 in S:
        recs = find_records(m)
        bn = {m[r[0] + 0x24:r[0] + 0x24 + 20].split(b"\x00")[0]: r[0] for r in recs}
        if set(bn) != set(names):
            print(f"{f}: name-set drift ({len(set(bn))} vs {len(names)}) — skipped", file=sys.stderr)
            continue
        ok_slots += 1
        for n in names:
            b = bn[n]
            d = T.setdefault(n, {})
            for off in range(0x7b):
                d.setdefault(off, []).append(m[b + off])
    print(f"slots used: {ok_slots}/{len(S)}  records: {len(names)}")

    # per-offset census
    print("off  chg  mono updn flat  owned-chg  sample_owned(name:seq)")
    for off in range(0x7b):
        chg = mono = updn = flat = ochg = 0
        sample = ""
        for n in names:
            v = T[n][off]
            changed = any(x != v[0] for x in v)
            chg += changed
            dec = any(v[i + 1] < v[i] for i in range(len(v) - 1))
            inc = any(v[i + 1] > v[i] for i in range(len(v) - 1))
            mono += inc and not dec
            updn += inc and dec
            flat += not changed
        # owned-only change: owner at banked +0x57
        for n in names:
            if T[n][0x57][-1] != 0xFF and any(x != T[n][off][0] for x in T[n][off]):
                ochg += 1
                if len(sample) < 90:
                    seq = T[n][off]
                    sample = f"{sample} {n.decode(errors='replace')[:10]}:{','.join(map(str, seq[:8]))}"
        if chg:
            print(f"0x{off:02x} {chg:4d} {mono:4d} {updn:4d} {flat:4d} {ochg:9d} {sample[:110]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
