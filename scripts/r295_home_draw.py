#!/usr/bin/env python3
"""t295: HOME-DRAW LAW CENSUS (OQ-016 residue 2 closure evidence). KEEPER.

Static law (docs/re/_wip_t295.md S3-S4, disasm FUN_00022ce4 + FUN_000238e8):
  * HOME STAR: per race r = 0..word[state+0xd88]-1 IN RACE ORDER,
    loop { call 0x7824f; idx = r % T } until byte[entry(idx)+0x14]==0
    (0x22eba/0x22ec7/0x22ee0), then
      dword[row_r+0xd] = entry(idx)              (0x22edd; row_r=state+0x1ee*r)
      byte[entry+0x14] = 0x80 | (1<<r)           (pre-colonisation old==0)
      byte[entry+0x17] |= 1<<r
    entry(j) = state+0xdb5+0x60j == base(j) == NAME(j)-0x1C (t270 join).
  * HOME PLANET: nplanets = rng%5+1 (0x23da4); k = rng % nplanets (0x239af)
    -> orbit index uniform 1..nplanets.
  * Pump law: whole block repeats until lane count word[state+0x32dd3] >=
    600 (0x22e06/0x22f57 call 0x2635c, zero rng) — final pass wins.

Predictions tested on EARLY trusted saves (turn>=1 per t270 trust law;
turn<=2 preferred so the owner byte still equals the draw-time value):
  P1 home indices distinct within a lineage
  P2 byte[home+0x14] == 0x80|(1<<r) exactly (turn<=2) / bit r + bit7 set
     (later saves; colonisation ORs extra bits, never clears)
  P3 home-index histogram ~uniform over 0..T-1 (chi-square, pooled races)
  P4 home-planet orbit index ~uniform over 1..nplanets (pooled)
  P5 nplanets (live live-prefixed planets at turn<=2) in 1..5

Laws reused verbatim from scripts/r270_homeplace.py (keeper): pointer law
member = phys + H, H = B - 0x1BF450; data X at member B+0x82bb0+X; star
chain anchor; live_planets prefix law; race count word[state+0xd88]==0x13b98.
Exit 0 = census ran (verdict printed); 2 = harness error.
"""
import glob
import math
import os
import struct
import struct as ST
import sys
import sysconfig
import zipfile
import collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_sav_scan as SS
import r1_slot as S
import r270_homeplace as HP

OFF = 0x82bb0


def analyze(path, label):
    try:
        mem = zipfile.ZipFile(path).read("Memory")
    except Exception as e:
        return {"label": label, "err": str(e)}
    pay = S.load_payload(".")
    anch = S.anchors_cached(".", pay)
    B = S.base_of(mem, anch)
    if B is None:
        return {"label": label, "err": "no-base"}
    H = B - 0x1BF450
    turn = struct.unpack_from("<I", mem, B + OFF + 0x12e10)[0]
    T = struct.unpack_from("<H", mem, B + OFF + 0x16145)[0]
    races = struct.unpack_from("<H", mem, B + OFF + 0x13b98)[0]
    if turn == 0:
        return {"label": label, "err": "turn0"}
    k0, names = HP.chain(mem, H)
    if len(names) < 45 or k0 is None:
        return {"label": label, "err": "no-chain"}

    def base(k):
        return k0 + k * HP.STRIDE_S - 0x1C

    rows = []
    for r in range(min(races, 8)):
        ptr = struct.unpack_from("<I", mem, B + OFF + 0x12e1d + r * 0x1ee)[0]
        rel = ptr - (k0 - 0x1C)
        if ptr == 0 or rel < 0 or rel % HP.STRIDE_S:
            rows.append({"race": r, "k": None})
            continue
        k = rel // HP.STRIDE_S
        if k >= min(T, len(names)):
            rows.append({"race": r, "k": None})
            continue
        own = mem[base(k) + 0x14 + H]
        sel = mem[base(k) + 0x17 + H]
        live = []
        sn = names[k]
        for i in range(5):
            v = struct.unpack_from("<I", mem, base(k) + 0x46 + 4 * i + H)[0]
            oo = v - ((HP.PLANET_HINT - 0x24) & 0xFFFFFFFF)
            if not (0 <= oo < 400 * HP.STRIDE_P) or oo % HP.STRIDE_P:
                continue
            j = oo // HP.STRIDE_P
            p = HP.PLANET_HINT + j * HP.STRIDE_P + H
            z = mem[p:p + 30].find(b"\x00")
            if not (0 <= z <= 25):
                continue
            pn = mem[p:p + z].decode("ascii", "replace")
            if pn.rsplit(" ", 1)[0] != sn:
                continue
            live.append((pn, mem[p + 0x33]))
        mine = [p for p in live if p[1] == r]
        orbit = None
        ROM = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5}
        if mine and " " in mine[0][0]:
            orbit = ROM.get(mine[0][0].rsplit(" ", 1)[1])
        rows.append({"race": r, "k": k, "own": own, "sel": sel,
                     "nlive": len(live), "orbit": orbit})
    ks = [x["k"] for x in rows if x["k"] is not None]
    return {"label": label, "turn": turn, "T": T, "races": races,
            "rows": rows, "distinct": len(set(ks)) == len(ks)}


def chi2(obs, exp_each):
    return sum((o - exp_each) ** 2 / exp_each for o in obs.values())


def main():
    targets = []
    for run in sorted(glob.glob("work/r1/r1deep-*") + glob.glob("work/r1/r1ad-*")):
        sd = os.path.join(run, "save")
        if not os.path.isdir(sd):
            continue
        files = sorted(glob.glob(sd + "/*.sav"), key=lambda f: os.stat(f).st_mtime)
        pick = None
        for f in files:
            try:
                mem = zipfile.ZipFile(f).read("Memory")
                Bv = S.base_of(mem, S.anchors_cached(".", S.load_payload(".")))
                if Bv is None:
                    continue
                if struct.unpack_from("<I", mem, Bv + OFF + 0x12e10)[0] >= 1:
                    pick = f
                    break
            except Exception:
                continue
        if pick:
            targets.append((os.path.basename(run), pick))
    # production lineages: banked saves, one per bank at the LOWEST turn>=1
    pay = S.load_payload(".")
    anch = S.anchors_cached(".", pay)
    for bank in sorted(glob.glob("work/r1/bank-*")):
        best = None
        for f in glob.glob(bank + "/*.sav"):
            try:
                mem = zipfile.ZipFile(f).read("Memory")
                Bv = S.base_of(mem, anch)
                if Bv is None:
                    continue
                tv = struct.unpack_from("<I", mem, Bv + OFF + 0x12e10)[0]
                if tv >= 1 and (best is None or tv < best[0]):
                    best = (tv, f)
            except Exception:
                continue
        if best:
            targets.append((os.path.basename(bank), best[1]))

    results = []
    for label, path in targets:
        a = analyze(path, label)
        results.append(a)
        if "err" in a:
            print(f"[{label}] skip: {a['err']}")
            continue
        p2 = all((x["own"] == (0x80 | (1 << x["race"]))) if a["turn"] <= 2
                 else ((x["own"] >> x["race"]) & 1 and x["own"] & 0x80)
                 for x in a["rows"] if x["k"] is not None)
        sel_ok = all((x["sel"] >> x["race"]) & 1 for x in a["rows"]
                     if x["k"] is not None)
        print(f"[{label}] t={a['turn']} T={a['T']} races={a['races']} "
              f"P1-distinct={a['distinct']} P2-ownbyte={p2} selbits={sel_ok} "
              f"ks={[x['k'] for x in a['rows']]} "
              f"orbits={[x['orbit'] for x in a['rows']]} "
              f"nlive={[x['nlive'] for x in a['rows']]}")

    ok = [a for a in results if "err" not in a]
    # LINEAGE DE-DUPE: banks share the production campaign (same ks set); pool
    # fresh runs (r1deep/r1ad) + each distinct ks-set once.
    fresh = [a for a in ok if a["label"].startswith(("r1deep", "r1ad"))]
    seen_sets, uniq = set(), []
    for a in ok:
        sig = tuple(sorted(x["k"] for x in a["rows"] if x["k"] is not None))
        if sig not in seen_sets:
            seen_sets.add(sig)
            uniq.append(a)
    print("\n== POOLED (lineage-deduped) ==")
    print(f"fresh={len(fresh)} distinct-ks-sets={len(uniq)} "
          f"(raw rows={len(ok)})")
    late_bad = [x for a in ok if a["turn"] > 2 for x in a["rows"]
                if x["k"] is not None
                and not (((x["own"] >> x["race"]) & 1) and (x["own"] & 0x80))]
    print("late-turn subset violations:",
          [(a["label"][:18], x["race"], hex(x["own"]))
           for a in ok for x in a["rows"]
           if x["k"] is not None and a["turn"] > 2
           and not (((x["own"] >> x["race"]) & 1) and (x["own"] & 0x80))][:8])
    print("P1 distinct:", all(a["distinct"] for a in ok),
          f"({len(ok)} rows-sets)")
    early = [a for a in ok if a["turn"] <= 2]
    print("P2 exact-equal (turn<=2):",
          all((x["own"] == (0x80 | (1 << x["race"])))
              for a in early for x in a["rows"] if x["k"] is not None),
          f"(n={sum(1 for a in early for x in a['rows'] if x['k'] is not None)})")
    idx = collections.Counter(x["k"] for a in uniq for x in a["rows"] if x["k"] is not None)
    n_tot = sum(idx.values())
    T0 = ok[0]["T"]
    c = chi2(idx, n_tot / T0)
    print(f"P3 index hist n={n_tot} over {T0} slots chi2={c:.1f} "
          f"(df={T0-1}, crit@.01=74.92)")
    print("   hist:", dict(sorted(idx.items())))
    orb = collections.Counter()
    for a in ok:
        for x in a["rows"]:
            if x["k"] is not None and x["orbit"]:
                orb[x["orbit"]] += 1
    print("P4 orbit hist:", dict(sorted(orb.items())))
    nl = collections.Counter(x["nlive"] for a in ok for x in a["rows"] if x["k"] is not None)
    print("P5 nlive hist (early only):",
          dict(sorted(collections.Counter(
              x["nlive"] for a in early for x in a["rows"] if x["k"] is not None).items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
