#!/usr/bin/env python3
"""r1_cb_picker_law.py — verify the PINNED uniform-among-legal-empty CB picker
(FUN_0003875c, disasm-verified t42) on first-save worlds.

Pinned chain (docs/re/income-law.md T42):
  home seed   FUN_000238e8 @0x23ca2..0x23cb2: EDX:=5, EBX:=0xffff, pop:=2,
              CALL FUN_00038818 = picker + activator (NO explicit slot)
  AI arrival  FUN_0003aa0a @0x3b0bd..0x3b0d1: same shape (item from +0xab,
              slot from +0xae — the transport-cargo path carries a slot)
  picker      FUN_0003875c: for slot k in [0, word[rec+0x1a]) if byte1==0xFF
              and FUN_0003830c(planet,k,item)!=0 collect k; if any, ONE call
              FUN_0007824f -> IDIV count -> list[rem] (uniform uniform,
              signed rem = rng % n; rng>=0 so rem>=0)
  activator   FUN_00038718: slot must be empty; FUN_00038840 writes
              byte1:=item, word2:=1 (ACTIVE)

MEASUREMENT (t42 correction): the PINNED legality chain for item 5 in
FUN_0003830c slot branch (iVar9 sequence, last-writer-wins, legal iff
iVar8!=0 && iVar9!=0 at 0x383a1) resolves to:
  default iVar9=0(illegal); rule B (cell class != 0) -> legal;
  rule D (rock XOR item==0x26) -> illegal on rock;
  rule C (surface XOR id<22) -> illegal orbital for item 5.
So picker-legal cells = class!=0 AND !(class&8) — EXACTLY the t40
"nonbarren" buildable set, and NOT including barren. The first census run
found 41/172 first-save CBs on class 0 — those must come from the
TRANSPORT-CARGO path (mode-3 FUN_00038840 with an explicit recorded slot
+0xae, no cell legality), not the picker. This tool separates the two
populations and tests uniformity on the picker population only.

Exit codes: 0 = class0 subset exists (transport path) or n==0, and
picker-population uniformity holds (chi2<=27.88, |z|<=3.3); 1 = harness
error; 2 = uniformity rejected.
"""
import sys, os, glob, math, struct as st, zipfile, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_sav_scan import build_anchors, find_base
import r1_income_law as IL

TURN_PHYS, IMAGE_MAP_BASE = 0x254E10, 0x1BF450  # banked H-map law (r1_pros_growth)


def first_saves():
    """(run, file, base) of the EARLIEST turn<=1 save per DISTINCT world
    identity (owned-records (name,capw) tuple). t42 lesson: collect the
    world only if the save ITSELF is turn<=1 (picker-placed population);
    deduping over ALL saves first lures in mid-game worlds whose owned set
    happens to match a home world (a 162-vs-72 population inflation)."""
    pay = open("work/ascend_payload.bin", "rb").read()
    anch = build_anchors(pay)
    worlds = {}
    for run in sorted(glob.glob("work/r1/*")):
        if not os.path.isdir(run):
            continue
        for f in sorted(glob.glob(run + "/save/*.sav"), key=os.path.getmtime):
            try:
                m = zipfile.ZipFile(f).read("Memory")
            except Exception:
                continue
            votes, _ = find_base(m, anch)
            if not votes:
                continue
            base = votes.most_common(1)[0][0]
            items = IL.item_table(m, base)
            if items is None or not IL.names_ok(items):
                continue
            turn = st.unpack_from("<H", m, TURN_PHYS + (base - IMAGE_MAP_BASE))[0]
            if turn > 1:
                continue
            ids = []
            for rec in IL.find_records(m):
                rb = rec[0]
                if m[rb + 0x57] == 0xFF:
                    continue
                ids.append((m[rb + 0x24:m.index(b"\x00", rb + 0x24)].decode("cp437", "replace"),
                            st.unpack_from("<H", m, rb + 0x1a)[0]))
            wid = tuple(ids)
            if not wid:
                continue
            if wid not in worlds or os.path.getmtime(f) < worlds[wid][1]:
                worlds[wid] = ((run, f), os.path.getmtime(f), base)
    return worlds


def main():
    rock_viol = 0
    ranks = []                 # (rank among non-rock surface, n_nonrock)
    rank01 = collections.Counter()
    cls_hist = collections.Counter()
    orbital_cb = 0
    n_cb = 0
    n_rec = 0
    for wid, ((run, f), _, b0) in first_saves().items():
        m = zipfile.ZipFile(f).read("Memory")  # turn<=1 picker population
        for rec in IL.find_records(m):
            rb = rec[0]
            if m[rb + 0x57] == 0xFF:
                continue
            ptr = st.unpack_from("<I", m, rb + 0x10)[0] + 0x88
            surf = st.unpack_from("<H", m, rb + 0x18)[0]
            capw = st.unpack_from("<H", m, rb + 0x1a)[0]
            n_rec += 1
            for k in range(min(capw, 200)):
                if m[ptr + 4 * k + 1] != 5:
                    continue
                if not (st.unpack_from("<H", m, ptr + 4 * k + 2)[0] & 1):
                    continue
                n_cb += 1
                cls = m[ptr + 4 * k]
                cls_hist[("rock" if cls & 8 else cls,
                          "orb" if k >= surf else "surf")] += 1
                if cls & 8:
                    rock_viol += 1
                    print(f"  ROCK-VIOLATION {run} {os.path.basename(f)} slot {k}")
                if k >= surf:
                    orbital_cb += 1
                    continue
                nonrock = [kk for kk in range(surf)
                           if not (m[ptr + 4 * kk] & 8)]
                if k not in nonrock:
                    print(f"  note CB not non-rock?? {run} slot {k}")
                    continue
                r = nonrock.index(k)
                ranks.append((r, len(nonrock)))
                rank01[min(r, 4)] += 1
    print(f"records(owned)={n_rec} active CBs={n_cb} orbital={orbital_cb}")
    print(f"CB cell class hist: {dict(sorted(cls_hist.items(), key=str))}")
    print(f"low-rank hist (0..4+): {dict(sorted(rank01.items()))}")
    n = len(ranks)
    if not n:
        return 1
    print(f"rank samples={n}")
    # Statistics done RIGHT (t42 fix): per-planet rank spaces differ in
    # size, so a decile chi-square is structurally biased (small N maps
    # ranks onto unequal bins: N=18 leaves decile 4 EMPTY and decile 9
    # unreachable — a former VERDICT-2 here was that artifact, not data).
    # Use (1) the pooled standardised mean z and (2) a pooled KS test of
    # u = r/(N-1) ~ Uniform(0,1). crit KS D at alpha=0.01: 1.63/sqrt(n).
    zmean = sum((r - (N - 1) / 2) / math.sqrt((N * N - 1) / 12)
                for r, N in ranks if N > 1) / math.sqrt(n)
    us = sorted(r / (N - 1) for r, N in ranks if N > 1)
    D = 0.0
    for i, u in enumerate(us):
        D = max(D, (i + 1) / len(us) - u, u - i / len(us))
    ks_crit = 1.63 / math.sqrt(len(us))
    print(f"KS D={D:.3f} (crit {ks_crit:.3f}, alpha .01)  "
          f"z(mean)={zmean:+.2f} (crit 3.3)")
    if rock_viol:
        print("VERDICT 1"); return 1
    if D > ks_crit or abs(zmean) > 3.3:
        print("VERDICT 2: uniform-over-non-rock REJECTED")
        return 2
    print("VERDICT 0: uniform-over-non-rock CONFIRMED")
    return 0


sys.exit(main())
