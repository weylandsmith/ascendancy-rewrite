#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""r1_slot.py — shared slot-reading layer for the playcap analyzers (t85).

Laws this depends on (all cited, none invented here):
  * slot ZIP 'Memory' member == full guest RAM; image base B found by the
    unanimous high-entropy anchor vote (scripts/r1_sav_scan.py, OQ-011 CLOSED;
    member address = B + 0x82bb0 + X for every obj1 data offset X).
  * TURN COUNTER: DAT_00012e10 as a full u32 IS the turn number.
    [verified t85, two independent banked runs with documented turn ladders]
      - r1ad-20261006-131350 (mtimes chronological; click law turned 0->2):
        t=0 x17 slots, then 41.sav t=1, 42.sav t=1, 43.sav t=2.
      - r1deep-20261007-224831 (t24 law run, turns 35..42): mtime-ordered
        slots read 35,35,36,36,37,38,38,39,40,40,41,42,42,... monotone
        non-decreasing across the ring wrap (56..60 then 41..55).
    CAUTION: ring slot NUMBERS are cyclic (41..60), so ordering by filename
    is wrong across a wrap — order by mtime, and de-duplicate (the ring keeps
    stale copies whose contents match an earlier slot).
  * T (total stars) = u32 DAT_00016143 >> 16  (score.md S3; the playcap
    v1 readout read it as u16 first then >>16 => always 0; FIXED t85).
  * scored stars = u32 DAT_000482fb (score.md S3 "STARS CONTROLLED %d").
  * end-presenter selector byte = byte DAT_00043510 (score.md; BYTE not u16 —
    u16 reads pick up adjacent-pack noise e.g. 0xC500 on title slots),
    rank u16 DAT_0004350c.
  * TRUST LAW: a slot is in-game only if t>0 OR score>=1. Title-menu slots
    read t=0/score=0 and selector = uninitialized heap (docs/BLOCKED.md t82;
    re-measured t85: sel u16 0xC500 on title slots of BOTH banked runs).

Exit codes follow the runbook: 0 ran with findings, 1 ran negative,
2 harness error.
"""
import os, struct, sys, zipfile, json, glob

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_sav_scan as SS

OFF = 0x82bb0


def load_payload(root):
    p = os.path.join(root, "work", "ascend_payload.bin")
    if not os.path.isfile(p):
        raise SystemExit(2)
    return open(p, "rb").read()


def anchors_cached(root, pay):
    """Anchor list is a pure function of the payload; cache it (find_base
    over 17 MB is ~1.5 s/slot and playcap re-scans every slot per tick)."""
    cache = os.path.join(root, "work", "r1", ".anch-cache.json")
    key = f"{len(pay)}:{pay[:64].hex()}"
    try:
        j = json.load(open(cache))
        if j.get("key") == key:
            return [tuple(x) for x in j["anchors"]]
    except Exception:
        pass
    a = SS.build_anchors(pay)
    try:
        os.makedirs(os.path.dirname(cache), exist_ok=True)
        json.dump({"key": key, "anchors": [list(x) for x in a]}, open(cache, "w"))
    except Exception:
        pass
    return a


def base_of(mem, anch, min_votes=5):
    v, _ = SS.find_base(mem, anch)
    if v and v.most_common(1)[0][1] >= min_votes:
        return v.most_common(1)[0][0]
    return None


def slots_by_mtime(run_dir):
    save = os.path.join(run_dir, "save")
    if not os.path.isdir(save):
        return []
    return sorted(glob.glob(os.path.join(save, "*.sav")), key=os.path.getmtime)


def read_slot(path, mem, B):
    """Scalar readout for one slot (B known)."""
    def u32(X):
        return struct.unpack_from("<I", mem, B + OFF + X)[0]
    def u16(X):
        return struct.unpack_from("<H", mem, B + OFF + X)[0]
    def u8(X):
        return mem[B + OFF + X]
    d = {
        "file": os.path.basename(path),
        "turn": u32(0x12e10),
        "T": u32(0x16143) >> 16,
        "score_stars": u32(0x482fb),
        "selector_byte": u8(0x43510),
        "rank": u16(0x4350c),
    }
    d["in_game"] = d["turn"] > 0 or d["score_stars"] >= 1
    return d


def timeline(run_dir, pay, root, anch=None, dedupe=True, verbose=True):
    """mtime-ordered, content-deduped, in-game-only slot timeline.
    root = project root (for the anchor cache)."""
    anch = anch or anchors_cached(root, pay)
    out, seen = [], set()
    for sp in slots_by_mtime(run_dir):
        try:
            mem = zipfile.ZipFile(sp).read("Memory")
        except Exception:
            if verbose:
                print(f"  {os.path.basename(sp)}: unreadable", file=sys.stderr)
            continue
        if len(mem) < 0x90000:
            continue
        B = base_of(mem, anch)
        if B is None:
            if verbose:
                print(f"  {os.path.basename(sp)}: no base vote", file=sys.stderr)
            continue
        d = read_slot(sp, mem, B)
        d["path"] = sp
        d["base"] = B
        sig = (d["turn"], d["score_stars"], d["selector_byte"])
        if dedupe and sig in seen:
            continue
        seen.add(sig)
        out.append(d)
    return out


SHIP = dict(stride=0x162, x=0x3a095, count=0x43489)


def ship_array_law(mem, B):
    """runtime ship array base = B+0x82bb0+0x3a095, stride 0x162,
    live count = u32 at B+0x82bb0+0x43489 >> 16 (r1_trajectory_regression.py
    header law, 'verified verbatim, FUN_00022304')."""
    base = B + OFF + SHIP["x"]
    n = struct.unpack_from("<I", mem, B + OFF + SHIP["count"])[0] >> 16
    return base, min(n, 0x6b)


def ship_records(mem, B):
    base, n = ship_array_law(mem, B)
    recs = []
    for k in range(n):
        r = base + k * SHIP["stride"]
        if r + SHIP["stride"] > len(mem):
            break
        recs.append(dict(
            slot=k,
            owner=struct.unpack_from("<I", mem, r + 0x54)[0] >> 16,
            state=mem[r + 0x58],
            design=struct.unpack_from("<I", mem, r + 0x10)[0],
            # FULL 3-tuple: a truncated xyz here once crashed the live
            # watcher at the first slot containing ships (t85).
            xyz=struct.unpack_from("<3f", mem, r + 0x9e),
        ))
    return recs


def owned_systems(mem):
    """Control-victory progress census, t85 revision.

    Returns dict(owner -> (systems_any, systems_full, planets)) where
      systems_any  = distinct star indices with >=1 owned planet
      systems_full = star indices where the owner holds EVERY planet record
      planets      = owned planet-record count
    Laws: owner byte name+0x33 == RAM +0x57 (t80 mirrored); owning star index
    byte name-0x18 == base+0x0c (savegame.md, 116/116 file-side UPGRADED t80;
    t85 confirms it is populated in LIVE RAM — a captured slot resolves all
    5 of its colonies to sensible star indices).

    t85 CALIBRATION (captured campaign, rescued ring — origin UNCONFIRMED;
    %m race law resolves its player to Ungooma, but owner 0 (5 planets, 4
    systems) sits at diplo row 0 = Chamachies; user played as Comaches and
    denies this campaign, so treat attribution as OPEN and player-row id via
    DAT_00006775 as UNTRUSTED). Player side: 5 planets / 4 systems-any / 1
    systems-full while DAT_000482fb == 1. So the score.md '[inferred]
    DAT_482fb = player-owned star count' is FALSE as stated: planets !=
    stars. 'systems_full' matches at this ONE point — leading hypothesis,
    one data point, from a campaign of contested provenance.
    """
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from r1_income_law import find_records
    star = {}
    for rec in find_records(mem):
        rb = rec[0]
        star.setdefault(mem[rb + 0x0c], []).append(mem[rb + 0x57])
    out = {}
    for s, owners in star.items():
        for o in set(owners):
            if o == 0xFF:
                continue
            any_n, full_n, pl = out.get(o, (set(), set(), 0))
            any_n.add(s)
            if all(x == o for x in owners):
                full_n.add(s)
            out[o] = (any_n, full_n, pl + sum(1 for x in owners if x == o))
    return {o: (len(v[0]), len(v[1]), v[2]) for o, v in out.items()}


if __name__ == "__main__":
    # CLI: r1_slot.py RUN_DIR [RUN_DIR...] -> per-slot timeline table
    root = os.getcwd()
    pay = load_payload(root)
    anch = anchors_cached(root, pay)
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    based = False
    ingame = 0
    for run in sys.argv[1:]:
        tl = timeline(run, pay, root, anch=anch)
        n_in = sum(1 for d in tl if d["in_game"])
        based = based or bool(tl)
        ingame += n_in
        print(f"== {run}: {len(tl)} validated slots, {n_in} in-game")
        for d in tl:
            if not d["in_game"]:
                continue
            print(f"  {d['file']:9} t={d['turn']:<4} T={d['T']:<4} "
                  f"score={d['score_stars']:<3} sel={d['selector_byte']:#04x} "
                  f"rank={d['rank']}")
    if based and not ingame:
        print("NOTE: base found but NO in-game slot — the session never "
              "entered a campaign (title screen only).")
    raise SystemExit(0 if based else 1)
