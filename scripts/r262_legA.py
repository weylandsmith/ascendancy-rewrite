#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t262b — leg-A deep check: on turn boundaries where V changed but the ship
INVENTORY signature was identical, did ANY other banked field move
(systems_any, systems_full, planets_mine, ship target-word multiset)?
A boundary where NOTHING banked moved yet V moved is the strongest evidence
that V's inputs include something the watcher does not capture.
Same segmentation law as r262_census_disc.py. usage: r262_legA.py
"""
import json, os, struct as st, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
JSONL = os.path.join(ROOT, "work/r1/playcap/live-timeline.jsonl")


def decode(u16s):
    b = st.pack("<%dH" % len(u16s), *u16s)
    owner = st.unpack_from("<I", b, 0x54)[0] >> 16
    nslot = st.unpack_from("<I", b, 0x15a)[0]
    if nslot > 64:
        nslot = 0
    ring = [b[0xab + 7 * i] for i in range(nslot) if 0xab + 7 * i < len(b)]
    target = st.unpack_from("<I", b, 0x59)[0]
    kind = b[0x58]
    return owner, kind, st.unpack_from("<I", b, 0x10)[0], ring, target


def main():
    seen = set()
    segs = []
    seg = None
    pmt = None
    sid = 0
    with open(JSONL, "r", errors="replace") as f:
        while True:
            line = f.readline()
            if not line:
                break
            i = line.find('"file": "')
            if i < 0:
                continue
            j2 = line.rfind('"file_mtime_ns": ')
            if j2 < 0:
                continue
            try:
                mt = int(line[j2 + 17:].split(",")[0].split("}")[0])
            except Exception:
                continue
            fn = line[i + 9:line.find('"', i + 9)]
            if (fn, mt) in seen:
                continue
            seen.add((fn, mt))
            if pmt and (mt - pmt) / 1e9 > 600:
                if seg:
                    segs.append(seg)
                seg = None
                sid += 1
            pmt = mt
            try:
                j = json.loads(line)
            except Exception:
                continue
            t = j.get("turn", -1)
            V = j.get("score_stars")
            if seg is None:
                seg = dict(sid=sid, wm=-1, snaps=[])
            s = seg
            if s["wm"] >= 0:
                if (not V) and t <= s["wm"]:
                    segs.append(s)
                    seg = s = dict(sid=sid, wm=-1, snaps=[])
                elif V and t < s["wm"] - 2:
                    segs.append(s)
                    seg = s = dict(sid=sid, wm=-1, snaps=[])
            if not V:
                s["wm"] = max(s["wm"], t)
                continue
            s["wm"] = max(s["wm"], t)
            sr = j.get("ship_raw") or {}
            occ = Counter()
            dsig = Counter()
            ring = Counter()
            targets = []
            kinds = Counter()
            for k, v in sr.items():
                if isinstance(v, list) and len(v) >= 0x98:
                    try:
                        o, kind, d, rng, tg = decode(v)
                    except Exception:
                        continue
                    if o in (0xffff, 0xffffffff):
                        continue
                    occ[o] += 1
                    dsig[d] += 1
                    ring.update(rng)
                    kinds[kind] += 1
                    targets.append(tg)
            sig = (sum(occ.values()), tuple(sorted(occ.items())),
                   tuple(sorted(dsig.items())), tuple(sorted(ring.items())))
            rec = (t, V, j.get("systems_any"), j.get("systems_full"),
                   j.get("planets_mine"), sig, tuple(sorted(targets)),
                   tuple(sorted(kinds.items())))
            if s["snaps"] and s["snaps"][-1][0] == t:
                continue
            s["snaps"].append(rec)
    if seg:
        segs.append(seg)

    legA = 0
    chg = Counter()
    allstatic = []
    for s in segs:
        sn = s["snaps"]
        for a, b in zip(sn, sn[1:]):
            if b[1] == a[1]:
                continue                    # V static
            if b[5] != a[5]:
                continue                    # inventory changed (not leg A)
            legA += 1
            names = {2: "systems_any", 3: "systems_full", 4: "planets_mine",
                     6: "targets", 7: "kinds"}
            moved = [nm for idx, nm in names.items() if a[idx] != b[idx]]
            for nm in moved:
                chg[nm] += 1
            if not moved:
                allstatic.append((s["sid"], a[0], b[0], a[1], b[1], a[2], a[3], a[4]))
    print(f"legA boundaries (V changed, inventory sig identical): {legA}")
    print("of those, banked fields that moved:", dict(chg))
    print(f"NOTHING banked moved yet V moved: {len(allstatic)}")
    for e in allstatic:
        print(f"  seg{e[0]} t{e[1]}->{e[2]} V {e[3]}->{e[4]} "
              f"(any={e[5]} full={e[6]} planets={e[7]} both sides)")


if __name__ == "__main__":
    main()
