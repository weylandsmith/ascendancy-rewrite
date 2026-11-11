#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t262 — OQ-021 CENSUS/INVENTORY DISCRIMINATOR on the DRIVEN corpus.

Question (t256 MECHANICS note / t258 residue): V=DAT_000482fb moves only at
turn boundaries (t255/t258). t258's full-corpus candidicide killed every banked
feature on BOTH legs, but that corpus was mostly PARKED sessions (order churn
ubiquitous OR identical-state re-sampling; load artifacts polluted boundaries).
This instrument runs the TRIGGER question on the driven corpus (t261 drives:
End-Turn automation advancing the campaign, one turn per ~10 s), where every
turn boundary is a REAL end-turn.

Key design choice: in a moving drive, ORDER fields (kind/act) change at almost
every boundary (t258: A_k4/k5 33/38 with 277 false positives) — a binary
"did the census change" leg is powerless. The informative census is the
PIECEWISE-CONSTANT INVENTORY: live ship count per owner, design multiset,
gizmo-ring multiset. These change only on build/loss events, so a 2x2
(inventory-change x V-change) over turn boundaries is a real discriminator.
Plus the FUNCTIONALITY join: rows with IDENTICAL inventory signature that carry
DIFFERENT V => V is not a function of inventory within the lineage.

Corpus gate (t261 law): file_mtime_ns EPOCH window (x1e9! wall is HH:MM:SS and
collides across days). Dedup (file, file_mtime_ns) (orphan-watcher law t259).
Session = mtime-gap > 600 s. WITHIN a session split SEGMENTS at reload class
(V==0 at turn <= segment watermark) and foreign-lineage class (turn drops > 2
below watermark while V!=0 — the t261 softlock oscillation + the 23:05 re-drive
are exactly this; t255 per-session-trust pitfall generalized to per-SEGMENT).

ship_raw decode law (t256c, cited): per live slot a verbatim 177-u16 window of
the 0x162-byte record; bytes rebuilt via struct.pack; owner = u32@0x54 >> 16
(DEAD iff 0xffff/0xffffffff), kind = byte@0x58, design = u32@0x10, power =
u32@0x88, gizmo-slot count = u32@0x15a (clamp 64), ring types = byte@(0xab+7i).

usage: r262_census_disc.py [LO_EPOCH_S] [HI_EPOCH_S]  (defaults: today 13:00+)
output -> stdout
"""
import json, os, struct as st, sys, time
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
JSONL = os.path.join(ROOT, "work/r1/playcap/live-timeline.jsonl")
TAIL_BYTES = 8_000_000_000        # whole-file single pass (rows never buffered; t256c law)


def ep(s):
    return int(time.mktime(time.strptime(s, "%Y-%m-%d %H:%M:%S")))


LO = ep("2026-10-29 00:00:00") * 1_000_000_000
HI = None


def decode(u16s):
    b = st.pack("<%dH" % len(u16s), *u16s)

    def u32(off):
        return st.unpack_from("<I", b, off)[0] if off + 4 <= len(b) else None
    owner = (u32(0x54) or 0) >> 16
    nslot = u32(0x15a)
    if nslot is None or nslot > 64:
        nslot = 0
    ring = []
    for i in range(int(nslot)):
        o = 0xab + 7 * i
        if o < len(b):
            ring.append(b[o])
    return dict(owner=owner, kind=b[0x58], design=u32(0x10),
                power=u32(0x88), ring=ring)


DEAD = (0xffff, 0xffffffff)


def invent(recs):
    live = [r for r in recs.values() if r["owner"] not in DEAD]
    by_owner = Counter(r["owner"] for r in live)
    designs = Counter(r["design"] for r in live)
    ring = Counter(t for r in live for t in r["ring"])
    sig = (len(live), tuple(sorted(by_owner.items())),
           tuple(sorted(designs.items())), tuple(sorted(ring.items())))
    kind_by = Counter((r["owner"], r["kind"]) for r in live)
    return sig, dict(n_live=len(live), by_owner=dict(by_owner),
                     n_design=len(designs), n_ring=len(ring),
                     kind_by=dict(kind_by))


def main():
    global LO, HI
    if len(sys.argv) > 2:
        LO, HI = int(sys.argv[1]) * 10**9, int(sys.argv[2]) * 10**9

    size = os.path.getsize(JSONL)
    seen = set()
    n_gate_out = n_dedup = n_bad = 0
    # segment state
    sessions = []          # list of dicts: rows meta + snaps [(turn,V,wall,sig,detail)]
    seg = None
    prev_mt = None
    session_id = 0

    def close_seg():
        nonlocal seg
        if seg:
            if seg["cur"] is not None:
                seg["snaps"].append(seg["cur"])
                seg["cur"] = None
            if seg["snaps"]:
                sessions.append(seg)
        seg = None

    def new_seg(mt):
        nonlocal seg
        close_seg()
        seg = dict(sid=session_id, start=mt, wm=-1, snaps=[], cur_turn=None,
                   cur=None, n_v0=0, n_rows=0)
        return seg

    with open(JSONL, "r", errors="replace") as f:
        f.seek(max(0, size - TAIL_BYTES))
        f.readline()                       # partial line
        while True:
            line = f.readline()
            if not line:
                break
            i = line.find('"file": "')
            if i < 0:
                continue
            i += 9
            fn = line[i:line.find('"', i)]
            j2 = line.rfind('"file_mtime_ns": ')
            if j2 < 0:
                continue
            try:
                mt = int(line[j2 + 17:].split(",")[0].split("}")[0])
            except Exception:
                continue
            if mt < LO or (HI is not None and mt > HI):
                n_gate_out += 1
                continue
            key = (fn, mt)
            if key in seen:
                n_dedup += 1
                continue
            seen.add(key)
            try:
                j = json.loads(line)
            except Exception:
                n_bad += 1
                continue
            # session split
            if prev_mt is not None and (mt - prev_mt) / 1e9 > 600:
                close_seg()
                session_id += 1
            prev_mt = mt
            t = j.get("turn", -1)
            V = j.get("score_stars")
            if seg is None:
                seg = new_seg(mt)
            seg["n_rows"] += 1
            # segment split conditions (per-SEGMENT trust, t255 pitfall generalized)
            if seg["wm"] >= 0:
                if (V is None or V == 0) and t <= seg["wm"]:
                    seg = new_seg(mt)          # load/reload class
                    seg["n_v0"] += 1
                    continue
                if V and t < seg["wm"] - 2:
                    seg = new_seg(mt)          # foreign lineage (softlock oscillation / re-drive)
            if V is None or V == 0:
                seg["wm"] = max(seg["wm"], t)
                seg["n_v0"] += 1
                continue
            seg["wm"] = max(seg["wm"], t)
            sr = j.get("ship_raw") or {}
            recs = {}
            for k, v in sr.items():
                if isinstance(v, list) and len(v) >= 0x98:
                    try:
                        recs[int(k)] = decode(v)
                    except Exception:
                        continue
            sig, det = invent(recs)
            row = (t, V, j.get("wall", "?"), sig, det)
            if seg["cur_turn"] == t:
                # same-turn re-sample: keep FIRST (deterministic state within turn)
                continue
            if seg["cur"] is not None:
                seg["snaps"].append(seg["cur"])
            seg["cur_turn"] = t
            seg["cur"] = row
        f.close()
    close_seg()

    print(f"file {size/1e9:.2f} GB tail {min(size,TAIL_BYTES)/1e6:.0f} MB "
          f"window {time.strftime('%m-%d %H:%M', time.localtime(LO/1e9))}..")
    print(f"dedup-dropped={n_dedup} out-of-window={n_gate_out} bad_json={n_bad} "
          f"segments_with_snaps={len(sessions)}")

    agg = Counter()
    for s in sessions:
        snaps = s["snaps"]
        t0, t1 = snaps[0][0], snaps[-1][0]
        wall0, wall1 = snaps[0][2], snaps[-1][2]
        print(f"\nSEG s{s['sid']} rows={s['n_rows']} V0={s['n_v0']} "
              f"turns {t0}..{t1} wall {wall0}..{wall1}")
        if len(snaps) < 2:
            print("  single-snapshot segment (parked/short) — no boundaries")
            continue
        # trajectory
        parts = [f"{snaps[0][0]}:{snaps[0][1]}"]
        prevV = snaps[0][1]
        for (t, V, w, sig, det) in snaps[1:]:
            if V != prevV:
                parts.append(f"{t}:{V}")
                prevV = V
        print("  V trajectory: " + " ".join(parts))
        print(f"  inventory: n_live {snaps[0][4]['n_live']} -> {snaps[-1][4]['n_live']}"
              f" by_owner {snaps[0][4]['by_owner']} -> {snaps[-1][4]['by_owner']}")
        # 2x2 over consecutive-snapshot boundaries
        both = vonly = ichg_only = neither = 0
        order_chg = 0
        vchg_rows = []
        for a, b in zip(snaps, snaps[1:]):
            dV = a[1] != b[1]
            dI = a[3] != b[3]
            dO = a[4]["kind_by"] != b[4]["kind_by"]
            if dO:
                order_chg += 1
            if dV and dI:
                both += 1
                ta, Va, wa, si_a, da = a
                tb, Vb, wb, si_b, db = b
                what = []
                if tb - ta > 1:
                    what.append(f"turn-JUMP {ta}->{tb} (load class)")
                if da["n_live"] != db["n_live"]:
                    what.append(f"nlive {da['n_live']}->{db['n_live']}")
                if da["by_owner"] != db["by_owner"]:
                    what.append(f"owner {da['by_owner']}->{db['by_owner']}")
                print(f"    V&inv boundary: t{ta}->{tb} V {Va}->{Vb} wall {wa}->{wb}"
                      + (" [" + "; ".join(what) + "]" if what else ""))
            elif dV:
                vonly += 1
                vchg_rows.append((a, b))
            elif dI:
                ichg_only += 1
            else:
                neither += 1
        n = both + vonly + ichg_only + neither
        agg["n"] += n
        agg["both"] += both
        agg["vonly"] += vonly
        agg["ionly"] += ichg_only
        agg["neither"] += neither
        agg["order_chg"] += order_chg
        print(f"  boundaries n={n}: V&inv {both} | V&inv-static {vonly} | "
              f"inv-only {ichg_only} | neither {neither} | order-churn {order_chg}")
        for (a, b) in vchg_rows[:12]:
            ta, Va, _, si_a, da = a
            tb, Vb, _, si_b, db = b
            what = []
            if da["n_live"] != db["n_live"]:
                what.append(f"nlive {da['n_live']}->{db['n_live']}")
            if da["by_owner"] != db["by_owner"]:
                what.append(f"owner {da['by_owner']}->{db['by_owner']}")
            if si_a != si_b:
                what.append("design/ring sig")
            print(f"    V-change with STATIC inventory: t{ta}->{tb} V {Va}->{Vb} "
                  f"[{'; '.join(what) or 'inventory byte-identical'}]")
        # functionality join: identical inventory sig, different V
        bysig = defaultdict(set)
        for (t, V, w, sig, det) in snaps:
            bysig[sig].add(V)
        multi = {k: sorted(vv) for k, vv in bysig.items() if len(vv) > 1}
        print(f"  functionality: {len(bysig)} distinct inventory sigs; "
              f"{len(multi)} sigs carry MULTIPLE V values")
        for k, vv in list(multi.items())[:5]:
            print(f"    sig n_live={k[0]} by_owner={dict(k[1])} -> V values {vv}")
        agg["multi_sig"] += len(multi)
        agg["sigs"] += len(bysig)

    print("\n=== AGGREGATE over driven segments ===")
    print(f"  boundaries={agg['n']}  V&inv={agg['both']}  V&inv-static={agg['vonly']} "
          f"(leg-A failures)  inv-only={agg['ionly']} (leg-B failures)  "
          f"neither={agg['neither']}  order-churn={agg['order_chg']}")
    print(f"  inventory sigs={agg['sigs']} multi-V sigs={agg['multi_sig']}")


if __name__ == "__main__":
    sys.exit(main())
