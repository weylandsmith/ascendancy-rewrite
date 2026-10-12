#!/usr/bin/env python3
"""r1_t79_pos.py RUN... — OQ-025: the shell law at NON-default density.

Laws used (all r1_star_table.py / docs/re/r1-savestate.md, pointer law):
  - star records stride 96, name-anchored near HINT; slot idx at name-0x18
    must equal k; position f32[x,y,z] at name-0x14 — THE LAW IS ON THE 3D
    RADIUS r3 = hypot(x,y,z). (A 2D hypot(x,y) reading is a PROJECTION and
    is disc-scattered by geometry — an earlier t79 revision made exactly
    this mistake and drew a spurious "uniform-disc" conclusion from it.)
  - the LIVE in-play set is the HEAD of the chain, cut at the slot's own
    DAT_00016143>>16. Records past the cut may stay allocated on low-T
    campaigns (their names still match the pool; OQ-025 ledger caveat).

Check per run: an in-ladder-T slot whose gated head(T) radii form
NON-INCREASING runs at the shell radii (440,365,290,215,140,65,50) with
run populations equal to the measured halving law:
    shell0 pop = T//2 + 1; each next shell halves the remainder
    (rem==1 -> 1); shell6 (r=50) keeps the final remainder.
Exit 0 = law confirmed for EVERY analyzed arm; 1 = any FAIL.
"""
import os, sys, re, math, struct, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_sav_scan import build_anchors, find_base

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAY = open(os.path.join(ROOT, "work", "ascend_payload.bin"), "rb").read()
ANCH = build_anchors(PAY)
SNAME_RE = rb"[A-Z][a-z]{2,15}\x00"
PNAME_RE = rb"[A-Z][A-Za-z]{2,}(?: [IVX]+)?\x00"
HINT = 0x255be1
PLANET_N = 0x26d07b
STRIDE_P = 123
RADII = (440, 365, 290, 215, 140, 65, 50)
LADDER = {15, 25, 50, 75, 100}   # measured OQ-012(a) density totals


def nplanets(mem, H):
    n = 0
    while re.match(PNAME_RE, mem[PLANET_N + H + n * STRIDE_P:][:40]):
        n += 1
        if n > 400:
            break
    return n


def walk_gated(mem, H):
    """Stride-96 name-chain walk gated on: idx==k AND first planet-pointer
    slot targets the live planet grid (r1_star_table.py law)."""
    npg = nplanets(mem, H)
    best = []
    for delta in range(0x21):
        for sign in (-1, 1):
            cand = HINT + sign * delta
            recs, k = [], 0
            while k < 200:
                p = cand + k * 96 + H
                m = re.match(SNAME_RE, mem[p:p + 18])
                if not m:
                    break
                idx, = struct.unpack_from("<i", mem, p - 0x18)
                ok = False
                for i in range(5):
                    pv, = struct.unpack_from("<I", mem, p + 0x2A + 4 * i)
                    if pv == 0:
                        continue
                    off = pv - (PLANET_N - 0x24)
                    if off < 0 or off >= npg * STRIDE_P or off % STRIDE_P:
                        continue
                    ok = True
                    break
                if ok and idx == k:
                    x, y, z = struct.unpack_from("<fff", mem, p - 0x14)
                    recs.append((k, round(math.sqrt(x * x + y * y + z * z), 1)))
                k += 1
            if len(recs) > len(best):
                best = recs
    return best


def halving_pops(T):
    rem, pops = T, []
    for j in range(7):
        if rem <= 0:
            pops.append(0)
            continue
        if j == 0:
            c = rem // 2 + 1
        elif j == 6:
            c = rem
        else:
            c = rem // 2 if rem >= 2 else rem
        pops.append(c)
        rem -= c
    return pops


def analyze(run):
    sd = os.path.join(run, "save")
    loaded = []
    for f in sorted(os.listdir(sd)):
        if not f.endswith(".sav"):
            continue
        try:
            mem = zipfile.ZipFile(os.path.join(sd, f)).read("Memory")
        except Exception:
            continue
        if len(mem) < 0x90000:
            continue
        v, _ = find_base(mem, ANCH)
        if not v or v.most_common(1)[0][1] < 5:
            continue
        H = v.most_common(1)[0][0] - 0x1BF450
        T = struct.unpack_from("<I", mem, H + 0x1BF450 + 0x82bb0 + 0x16143)[0] >> 16
        loaded.append((f, mem, H, T))
    cands = [s for s in loaded if s[3] in LADDER]
    if not cands:
        print(f"{run}: no in-ladder-T slot")
        return False
    # autosave cycles over 41-60; take the ladder-T slot with the longest
    # gated chain (the fullest allocation state observed).
    f, mem, H, T = max(cands, key=lambda s: len(walk_gated(s[1], s[2])))
    recs = walk_gated(mem, H)
    if T > len(recs):
        print(f"FAIL {run} {f}: gated chain {len(recs)} < DAT T {T}")
        return False
    rs = [r for _, r in recs[:T]]
    viol = sum(1 for i in range(len(rs) - 1) if rs[i] < rs[i + 1] - 0.001)
    runs_list = []
    for r in rs:
        if runs_list and abs(runs_list[-1][0] - r) < 0.001:
            runs_list[-1][1] += 1
        else:
            runs_list.append([r, 1])
    got = [p for _, p in runs_list]
    exp = [p for p in halving_pops(T) if p]
    shell_ok = all(abs(r - RADII[i]) < 0.05 for i, (r, _) in enumerate(runs_list))
    ok = viol == 0 and shell_ok and got == exp
    print(f"{'OK ' if ok else 'FAIL'} {run} {f}: T={T} viol={viol} "
          f"runs={[(int(r), p) for r, p in runs_list]} expected={exp}")
    return ok


allok = True
n = 0
for run in sys.argv[1:]:
    try:
        if not analyze(run):
            allok = False
        else:
            n += 1
    except Exception as e:
        print(f"{run}: ERROR {type(e).__name__} {e}")
        allok = False
sys.exit(0 if (n and allok) else 1)
