#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t273 — offline witness harvest over the EXISTING drive corpus (three legs).

Why offline: the t273 drive leg died at 11:35 EST when the :9 ring lineage
flipped 1086 -> 645 into a TUTORIAL campaign while a live VNC client was
connected (docs/re/_wip_t273.md S2). Advancing turns requires clicking; clicking
a screen a human may be driving is forbidden. Legs (a)/(b)/(c) are corpus
questions and are answerable from work/r1/playcap/live-timeline.jsonl + banks.

Selection law (t265, cited there): gate on file_mtime_ns EPOCH ns (wall strings
are HH:MM:SS and collide across days), dedup (file, file_mtime_ns) (orphan-watcher
law t259), in_game AND turn>0. OOM law: iterate the file object, json.loads ONE
row at a time, never read()/load the whole file, buffer nothing but the previous
row.

LEG A (OQ-016 / diplomacy row 13) — SHARPENED DAMAGE FILTER. t251's filter was
"any non-coordinate u16 changed", which t251 itself refuted (every live ship's
day byte +0x67 changes every turn -> streak counts were bookkeeping churn).
Here the filter is the cited HIT PATH of combat.md: apply-site 0x4b87a writes
[t+0x90] -= shield_absorb and [t+0x8c] -= hull_absorb, so a damage application
is u16[+0x8c] (idx 70) or u16[+0x90] (idx 72) DECREASING between consecutive
same-lineage rows while the slot stays alive with a stable owner. Destruction =
alive -> not alive. Owner flip = capture class, reported separately, never as
damage. For every hit the nearest other-owner ship and BOTH relation directions
are printed: the witness we want is damage with neither direction at WAR (2).
Second channel of leg A: attitude deltas (the 0x43a4c price) — any atts[i][j]
decrease between consecutive rows, its exact value, and whether a damage event
shares the row pair (the t251 t887 pattern: -40 + state 1->2).

LEG B (OQ-021) — V>=25 threshold watch + selector/rank census, per segment,
over the whole gated corpus INCLUDING the new tutorial-645 lineage rows (the
watcher reported selector_byte=2 / rank=1 there, which would be the FIRST
non-zero selector in a corpus whose prior census was {0: 71038}).

LEG C (OQ-019) — magnetron USE frames, r265's W2 signature verbatim: slot
state -> 5 with displacement > 300u (S21 big-mover bound) AND after-y in
[-200.0, 0.0) (0x21f58's exact -200.0 offset can never reach 0 or pass -200)
AND after-x/z NOT both on the 32-grid; lane-march st5 rows counted as control.

usage: r273_harvest.py [LO_EPOCH_S] [HI_EPOCH_S]   (default Nov 1 00:00 -> now)
Exit 0 always (honest negatives are findings).
"""
import json
import os
import struct
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSONL = os.path.join(ROOT, "work/r1", "playcap", "live-timeline.jsonl")

HULL_IDX = 0x8C // 2      # 70  -> ship +0x8c (apply 0x4b87a hull subtraction)
SHLD_IDX = 0x90 // 2      # 72  -> ship +0x90 (apply 0x4b87a shield subtraction)
OWNER_LO = 0x54 // 2
OWNER_HI = 0x54 // 2 + 1
STATE_IDX = 0x58 // 2
DAY_IDX = 0x67 // 2
COORD_U16 = {0x9E // 2, (0x9E + 2) // 2, (0x9E + 4) // 2, (0x9E + 6) // 2}
BIG = 300.0               # S21 big-mover bound (r265 W2)


def alive(w):
    return any(w) and not all(x == 0xFFFF for x in w)


def owner_of(w):
    return w[OWNER_LO] | (w[OWNER_HI] << 16)


def race_of(w):
    """RACE INDEX for relation lookups. MEASURED LAW (r265 header, ships.md
    S19 T3 cite): the owner INDEX byte is ship+0x56; the u32 at +0x54 is the
    owner HANDLE (0x10000/0x20000/0x30000 ... = idx<<16), and t251's pass
    printed handles (att=196608) which is why every relation lookup there
    returned None. 0xFF = unowned/garbage slot."""
    b = w[0x56 // 2] & 0xFF
    return -1 if b == 0xFF else b


def state_of(w):
    return struct.unpack_from("<H", struct.pack("<H", w[STATE_IDX]))[0] & 0xFF


def grid(v):
    q = v / 32.0
    return abs(q - round(q)) < 1e-4


def scalars(line):
    """Header scalars by string scan (cheap pre-filter before json.loads)."""
    i = line.find('"file_mtime_ns": ')
    if i < 0:
        return None
    j = line.find(",", i)
    if j < 0:
        j = line.find("}", i)
    mt = int(line[i + 17:j])
    i = line.find('"turn": ')
    j = line.find(",", i)
    turn = int(line[i + 8:j])
    return mt, turn


def snap_ships(ob):
    out = {}
    for k, w in (ob.get("ship_raw") or {}).items():
        if len(w) != 177:
            continue
        if not alive(w):
            continue
        out[int(k)] = w
    return out


def snap_st(ob):
    """state + xyz for the magnetron leg (needs floats, so from ship_raw bytes)."""
    out = {}
    for k, w in (ob.get("ship_raw") or {}).items():
        if len(w) != 177:
            continue
        b = struct.pack("<177H", *w)
        st = b[0x58]
        if st == 0:
            continue
        x, y, z = struct.unpack_from("<3f", b, 0x9E)
        out[int(k)] = (st, x, y, z, b[0x56])
    return out


def lineage(rel):
    if not rel:
        return None
    return (rel["n"], tuple(rel["names"]))


def nearest_other(sl, w, ships, own):
    b = struct.pack("<177H", *w)
    x, y, z = struct.unpack_from("<3f", b, 0x9E)
    best = None
    for k2, w2 in ships.items():
        if k2 == sl:
            continue
        o2 = race_of(w2)
        if o2 == own or o2 < 0:
            continue
        b2 = struct.pack("<177H", *w2)
        x2, y2, z2 = struct.unpack_from("<3f", b2, 0x9E)
        d2 = (x - x2) ** 2 + (y - y2) ** 2 + (z - z2) ** 2
        if best is None or d2 < best[2]:
            best = (k2, o2, d2)
    return best


def main():
    lo = int(sys.argv[1]) if len(sys.argv) > 1 else int(time.mktime(
        time.strptime("2026-11-01 00:00:00", "%Y-%m-%d %H:%M:%S")))
    hi = int(sys.argv[2]) if len(sys.argv) > 2 else int(time.time())
    lo_ns, hi_ns = lo * 10**9, hi * 10**9
    print(f"window {time.strftime('%m-%d %H:%M', time.localtime(lo))} .. "
          f"{time.strftime('%m-%d %H:%M', time.localtime(hi))} (local)")

    seen = set()
    prev = None            # (mt, turn, ships, st_snap, relation, lineage)
    n_rows = 0
    turn_hist = {}
    lin_hist = {}
    # leg A
    dmg = []               # damage applications
    destr = []             # destructions
    cap = []               # owner flips
    att_delta = []         # relation price events
    pairs = 0
    # leg B
    seg = None
    segs = []
    sel_census = {}
    rank_census = {}
    v_hist = {}
    # leg C
    w2 = []
    st5_control = 0
    st5_other = 0

    def close_seg(s):
        if s:
            segs.append(s)

    with open(JSONL, "r", errors="replace") as f:
        for line in f:
            sc = scalars(line)
            if sc is None:
                continue
            mt, turn = sc
            if not (lo_ns <= mt <= hi_ns):
                continue
            if '"in_game": true' not in line or turn <= 0:
                continue
            fi = line.find('"file": "')
            fn = line[fi + 8:line.find('"', fi + 8)] if fi >= 0 else "?"
            if (fn, mt) in seen:
                continue
            seen.add((fn, mt))
            try:
                ob = json.loads(line)
            except Exception:
                continue
            n_rows += 1
            turn_hist[turn] = turn_hist.get(turn, 0) + 1
            rel = ob.get("relation")
            lin = lineage(rel)
            lin_hist[lin] = lin_hist.get(lin, 0) + 1
            V = ob.get("score_stars")
            sel = ob.get("selector_byte")
            rk = ob.get("rank")
            sel_census[sel] = sel_census.get(sel, 0) + 1
            rank_census[rk] = rank_census.get(rk, 0) + 1
            if V is not None:
                v_hist[V] = v_hist.get(V, 0) + 1

            # ---- leg B segments: reload class = turn drop while V!=0, or
            # lineage switch, or mtime gap > 600 s (t262 per-segment trust).
            if (seg is None or (prev and (lin != seg["lin"]
                                          or mt - prev[0] > 600 * 10**9
                                          or (turn < seg["turn_max"] and V != 0)))):
                close_seg(seg)
                seg = dict(lin=lin, t0=mt, turn_min=turn, turn_max=turn,
                           v_max=-1, v_at=None, sel_nonzero=0, rank_nonzero=0)
            if seg is not None:
                seg["turn_max"] = max(seg["turn_max"], turn)
                seg["turn_min"] = min(seg["turn_min"], turn)
                if V is not None and V > seg["v_max"]:
                    seg["v_max"] = V
                    seg["v_at"] = (turn, fn, mt)
                if sel:
                    seg["sel_nonzero"] += 1
                if rk not in (None, 65535):
                    seg["rank_nonzero"] += 1

            ships = snap_ships(ob)
            sts = snap_st(ob)

            # ---- leg C census on this row
            for sl, v in sts.items():
                if v[0] == 5:
                    # v = (state, x, y, z, owner); lane-march control class per
                    # r265: y exactly 0 or 1 AND z on the 32-grid.
                    if (abs(v[2]) < 1e-4 or abs(v[2] - 1.0) < 1e-4) and grid(v[3]):
                        st5_control += 1
                    else:
                        st5_other += 1

            if prev is not None:
                pmt, pturn, pships, pst, prel, plin = prev
                gap = (mt - pmt) / 1e9
                # SESSION guard (t262 per-segment trust): a same-lineage pair is
                # only comparable within one running session. A LOAD boundary
                # shows as turn going BACKWARDS (new session restarted lower) or
                # an mtime gap (the ring stopped). Both make slot-array arithmetic
                # meaningless: slot k in row A and slot k in row B are different
                # ships. t251 banked the same trap for the streak proxy.
                # t273 EXTENSION: the row pair must also be ADJACENT IN GAME
                # TIME (prev_turn in {turn-1, turn}); stale-echo rows (an old
                # session's turn 692 row landing between 1037 and 1038) passed
                # the gap test and produced phantom -8/-20/-38 "deltas".
                same_session = (gap <= 120.0 and turn >= pturn
                                and pturn in (turn, turn - 1))
                if plin == lin and prel and rel and same_session:
                    pairs += 1
                    # ---- leg A: damage on slots alive in both, stable owner
                    for sl, w in ships.items():
                        pw = pships.get(sl)
                        if pw is None:
                            continue
                        if race_of(pw) != race_of(w):
                            cap.append((turn, sl, race_of(pw), race_of(w),
                                        ob.get("wall"), fn))
                            continue
                        own = race_of(w)
                        if own < 0:
                            continue
                        dh = w[HULL_IDX] - pw[HULL_IDX]
                        ds = w[SHLD_IDX] - pw[SHLD_IDX]
                        if dh < 0 or ds < 0:
                            tgt = nearest_other(sl, pw, pships, own)
                            vic = tgt[1] if tgt else None
                            s_dir = None
                            r_dir = None
                            if vic is not None and vic < len(rel["states"]):
                                if own < len(rel["states"]):
                                    s_dir = rel["states"][own][vic]
                                    r_dir = rel["states"][vic][own]
                            dmg.append(dict(turn=turn, prev_turn=pturn, slot=sl,
                                            own=own, dhull=dh, dshield=ds,
                                            near_slot=tgt[0] if tgt else None,
                                            near_own=vic, d2=round(tgt[2], 1) if tgt else None,
                                            st_own_vic=s_dir, st_vic_own=r_dir,
                                            wall=ob.get("wall"), file=fn))
                    # ---- leg A: destructions (present -> absent/dead)
                    for sl, pw in pships.items():
                        if sl not in ships:
                            own = race_of(pw)
                            if own < 0:
                                continue
                            tgt = nearest_other(sl, pw, pships, own)
                            destr.append((turn, sl, own,
                                          tgt[1] if tgt else None,
                                          round(tgt[2], 1) if tgt else None,
                                          ob.get("wall"), fn))
                    # ---- leg A: attitude price deltas
                    if rel and prel and rel["n"] == prel["n"]:
                        for i in range(rel["n"]):
                            for j in range(rel["n"]):
                                if i == j:
                                    continue
                                d = rel["atts"][i][j] - prel["atts"][i][j]
                                if d < 0:
                                    att_delta.append((turn, pturn,
                                                      rel["names"][i], rel["names"][j],
                                                      prel["atts"][i][j], rel["atts"][i][j],
                                                      d,
                                                      prel["states"][i][j],
                                                      rel["states"][i][j],
                                                      ob.get("wall")))
                    # ---- leg C: magnetron frame between consecutive rows
                    for sl, v in sts.items():
                        pv = pst.get(sl)
                        if pv is None:
                            continue
                        d = ((v[1] - pv[1]) ** 2 + (v[2] - pv[2]) ** 2
                             + (v[3] - pv[3]) ** 2) ** 0.5
                        if v[0] == 5 and pv[0] != 5 and d > BIG:
                            y_ok = -200.0 <= v[2] < 0.0
                            off = not (grid(v[1]) and grid(v[3]))
                            if y_ok and off:
                                w2.append((turn, sl, d,
                                           f"prev st{pv[0]} ({pv[1]:.1f},{pv[2]:.1f},{pv[3]:.0f})",
                                           f"now st5 ({v[1]:.3f},{v[2]:.3f},{v[3]:.1f}) own={v[4]}",
                                           ob.get("wall")))
            prev = (mt, turn, ships, sts, rel, lin)

    close_seg(seg)

    print(f"\nrows={n_rows}  same-lineage row-pairs={pairs}  "
          f"distinct turns={len(turn_hist)}")
    if turn_hist:
        print(f"turn range {min(turn_hist)}..{max(turn_hist)}")
    print("lineages (n, names) -> rows:")
    for k, v in sorted(lin_hist.items(), key=lambda x: -x[1]):
        print(f"   {k}: {v}")

    print("\n== LEG B: per-segment V / selector / rank ==")
    for s in segs:
        print(f"  {time.strftime('%m-%d %H:%M:%S', time.localtime(s['t0'] / 1e9))} "
              f"lin={s['lin']} turns {s['turn_min']}..{s['turn_max']} "
              f"Vmax={s['v_max']} at={s['v_at']} "
              f"sel_nonzero_rows={s['sel_nonzero']} rank_nonzero_rows={s['rank_nonzero']}")
    print(f"  V census: {dict(sorted(v_hist.items()))}")
    print(f"  selector census: {sel_census}")
    print(f"  rank census: {rank_census}")
    print(f"  V>=25 rows: {sum(c for v, c in v_hist.items() if v >= 25)}")

    print(f"\n== LEG A: damage applications (hull/shield DECREASE, stable owner): {len(dmg)} ==")
    with open(os.path.join(ROOT, "work", "r1", "t273_legA.json"), "w") as jf:
        json.dump(dict(damage=dmg, destructions=destr, owner_flips=cap,
                       att_deltas=att_delta), jf, indent=1)
    print("  full tables -> work/r1/t273_legA.json")
    for h in dmg[:40]:
        print("  ", h)
    print(f"  of which NEITHER direction at WAR: "
          f"{sum(1 for h in dmg if h['st_own_vic'] != 2 and h['st_vic_own'] != 2)}")
    print(f"  of which engagement-scale (d2<=3600): "
          f"{sum(1 for h in dmg if h['d2'] is not None and h['d2'] <= 3600)}")
    print(f"\n== LEG A: destructions (slot alive -> gone): {len(destr)} ==")
    for h in destr[:25]:
        print("  ", h)
    print(f"\n== LEG A: owner flips (capture class, NOT damage): {len(cap)} ==")
    for h in cap[:15]:
        print("  ", h)
    print(f"\n== LEG A: attitude DECREASES (0x43a4c price channel): {len(att_delta)} ==")
    hist = {}
    for h in att_delta:
        hist[h[6]] = hist.get(h[6], 0) + 1
    print(f"  delta-value histogram: {dict(sorted(hist.items()))}")
    big = [h for h in att_delta if h[6] <= -2]
    print(f"  every delta <= -2 (the -1 class is per-turn drift): {len(big)}")
    for h in big[:40]:
        print("  *", h)
    for h in att_delta[:4]:
        print("  ", h)
    print(f"  pairs where a decrease co-occurred with a WAR flip (state 1->2): "
          f"{sum(1 for h in att_delta if h[7] == 1 and h[8] == 2)}")

    print(f"\n== LEG C: magnetron USE-frame candidates: {len(w2)} ==")
    for h in w2[:25]:
        print("  ", h)
    print(f"  st5 control-class rows={st5_control} other={st5_other}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
