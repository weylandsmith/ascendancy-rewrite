#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t265 KEEPER — st5 lane-march law check on the t261 DRIVE corpus.

Checks in ONE bounded-tail pass (corpus law: mtime_ns inside
2026-11-01 21:20 .. 2026-11-02 01:59, dedup (file, mtime_ns), in_game, turn>0):

K1 (t189 law re-test, new corpus): for consecutive TURN rows where both
   endpoints are st5 (same slot), delta_x must equal step0 or step0/3 where
   step0 = float(u16[+0x8] + u16[0xc]) read from the SAME raw window, the /3
   branch iff the route handle carries the bridge bit (handle identity via
   S22: the gate lives on the lane record; from the ship window we can only
   key by handle value at +0x52, so the check asserts delta in
   {step0, step0/3} and reports which handle values took which branch).
K2 same-turn st5 delta == 0 census (turn-atomicity at ring granularity).
K3 magnetron W2 counter (st->5 + d>300 + y in [-200,0) + off-grid x/z).
K3b MAGNETRON LANDING CENSUS via the jitter law: 0x21f58 adds rng%200 to TWO
   axes of the chosen star triple (and exactly -200.0 to the third). st=5 is
   a same-CALL transient for the magnetron (0x4cd16 sets 5, placement resets
   4), so a landing row IS an st4 row. P(both jittered axes land on the
   32-grid) ~= (6/200)^2 < 0.1%, so an st4 population that is 100% on-grid in
   x AND z (plus a descriptive y-mod-32 histogram) is a strong zero-census of
   magnetron landings. Star-record grid alignment is NOT assumed (uncited).
(K4 st4 dwell was measured in r265_pass3.py; not re-run here.)

Exit 0 ran with findings, 1 harness error. usage: r265_keeper.py
"""
import json, os, struct, sys, time
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
JSONL = os.path.join(ROOT, "work/r1/playcap/live-timeline.jsonl")
LO_NS = int(time.mktime(time.strptime("2026-11-01 21:20:00", "%Y-%m-%d %H:%M:%S")) * 1e9)
HI_NS = int(time.mktime(time.strptime("2026-11-02 01:59:00", "%Y-%m-%d %H:%M:%S")) * 1e9)
TAIL_SEEK = 420_000_000
# drive regimes only (softlock windows excluded; mtime clock, see _wip_t265)
import datetime as _dt
A0 = _dt.datetime(2026, 11, 1, 21, 24, 0)
S0 = _dt.datetime(2026, 11, 1, 21, 38, 0)
B0 = _dt.datetime(2026, 11, 1, 23, 7, 0)


def drive(mt):
    d = _dt.datetime.fromtimestamp(mt / 1e9)
    return (A0 <= d < S0) or (d >= B0)


def grid32(v):
    q = v / 32.0
    return abs(q - round(q)) < 1e-4


def snap(j):
    out = {}
    for k, w in (j.get("ship_raw") or {}).items():
        if len(w) != 177:
            continue
        b = struct.pack("<177H", *w)
        st = b[0x58]
        if st == 0:
            continue
        x, y, z = struct.unpack_from("<3f", b, 0x9e)
        step0 = float(struct.unpack_from("<H", b, 0x8)[0]
                      + struct.unpack_from("<H", b, 0xc)[0])
        out[int(k)] = (st, b[0x59], x, y, z, step0,
                       struct.unpack_from("<I", b, 0x52)[0])
    return out


def main():
    size = os.path.getsize(JSONL)
    seen = set()
    rows = []
    with open(JSONL, "r", errors="replace") as f:
        f.seek(max(0, size - TAIL_SEEK))
        f.readline()
        for line in f:
            i = line.find('"file_mtime_ns": ')
            if i < 0:
                continue
            j = line.find(",", i)
            mt = int(line[i + 17:j])
            if not (LO_NS <= mt <= HI_NS) or not drive(mt):
                continue
            i = line.find('"turn": ')
            j = line.find(",", i)
            turn = int(line[i + 8:j])
            if '"in_game": true' not in line or turn <= 0:
                continue
            fi = line.find('"file": "')
            fn = line[fi + 8:line.find('"', fi + 8)] if fi >= 0 else "?"
            key = (fn, mt)
            if key in seen:
                continue
            seen.add(key)
            try:
                ob = json.loads(line)
            except Exception:
                continue
            rows.append((mt, turn, snap(ob)))
    rows.sort(key=lambda r: r[0])

    k1 = Counter()                # (handle, branch) counts
    k1_bad = []
    k2_same = 0
    k3 = 0
    k3b = Counter()               # st4 row y mod 32
    k3b_bad = []
    prev = None
    for mt, t, s in rows:
        if prev is not None:
            pturn, ps = prev
            for sl, v in s.items():
                pv = ps.get(sl)
                if pv is None:
                    continue
                dx = v[2] - pv[2]
                d = (dx * dx + (v[3] - pv[3]) ** 2 + (v[4] - pv[4]) ** 2) ** 0.5
                if t == pturn:
                    if v[0] == 5 and pv[0] == 5:
                        k2_same += 1
                        if abs(dx) > 1e-4:
                            k1_bad.append(("SAME", t, sl, dx))
                else:
                    # t189 law is a CONSECUTIVE-TURN law; the corpus contains
                    # re-drive rewinds (23:05 relaunch: t1111 -> t1086, and the
                    # 1111->1255 softlock jump). A boundary pair that is not
                    # t == pturn+1 spans a rewind/jump and would read as
                    # N-turns-of-march (measured: 25 x 14/3 = 116.6667). Drop.
                    if v[0] == 5 and pv[0] == 5 and t == pturn + 1:
                        step0 = pv[5]
                        if step0 > 0 and abs(abs(dx) - step0) < 1e-3:
                            k1[(pv[6], "x1")] += 1
                        elif step0 > 0 and abs(abs(dx) - step0 / 3.0) < 1e-3:
                            k1[(pv[6], "/3")] += 1
                        else:
                            k1_bad.append(("STEP", t, sl, abs(dx), step0))
                if v[0] == 5 and pv[0] != 5 and d > 300.0 \
                        and -200.0 <= v[3] < 0.0 \
                        and not (grid32(v[2]) and grid32(v[4])):
                    k3 += 1
        # K3b: y-mod-32 census over ALL st4 rows (both regimes; st=5 is a
        # same-CALL transient for the magnetron — 0x4cd16 sets 5, 0x21f58
        # commits and resets to 4 — so the landing row is an st4 row).
        for sl, v in s.items():
            if v[0] == 4:
                yq = round((v[3] % 32.0), 3)
                k3b[yq] += 1
                if yq != 0.0 or not (grid32(v[2]) and grid32(v[4])):
                    k3b_bad.append((t, sl, v[2], v[3], v[4]))
        prev = (t, s)
    print(f"rows={len(rows)} drive-regime")
    print(f"K1 st5 boundary delta vs step0 (+0x8/+0xc sum):")
    for (hnd, br), c in sorted(k1.items()):
        print(f"  handle=0x{hnd:x} {br}: x{c}")
    print(f"  violations: {len(k1_bad)} {k1_bad[:8]}")
    print(f"K2 same-turn st5 pairs: {k2_same} (all delta==0 unless listed above)")
    print(f"K3 magnetron W2 frames: {k3}")
    print(f"K3b st4 rows y-mod-32 histogram: {dict(k3b.most_common(8))}; "
          f"off-grid-x-or-z st4 rows: {len(k3b_bad)} {k3b_bad[:6]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
