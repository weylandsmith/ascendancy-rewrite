#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t362 MIXED-FLEET DEPARTURE LAW — witness census on the banked t265 drive
corpus (docs/re/ships.md S24: regimes A 2026-11-01 21:24-21:37 and B
23:07-01:27 healthy, softlock window 21:38-23:06 EXCLUDED).

Question this answers (decides the sweep-count model of the command executor
FUN_00041260, hence the piecemeal-departure law t362 must pin):
  at each TURN-BOUNDARY pair (row turn t -> next row turn t+1, same slot) how
  many kind flips 4->5 / 5->4 happen, and can TWO DIFFERENT SLOTS of the SAME
  OWNER flip in the SAME boundary? One-pick-per-boundary (t361 model) forbids
  it only if flips are owner-serialized; multiple flips per boundary per owner
  falsifies one-pick and supports the REPEATS-sweeps reading.

Also measures (corroborations of banked laws, cited in the pin test):
  - same-turn consecutive-row kind flips (mid-turn movement class; S24 item 3
    says 0 outside the softlock window),
  - st4 rows off the 32-grid (S24 item 1 says 100% on-grid),
  - st5 same-turn x-deltas (S24 item 3: exactly 0).

Corpus law verbatim from r265_pass2.py: file_mtime_ns inside the epoch +
dedup (file, mtime_ns) + in_game + turn>0, BOUNDED tail seek (OOM law). The
timeline has grown ~7 days since the t265 capture, so the epoch window is
deeper: TAIL_BYTES default 4.2 GB (r265 used 420 MB on Nov 2).

Exit 0 always. usage: r362_departure_witness.py [tail_bytes]
"""
import json, os, struct, sys, time
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSONL = os.path.join(ROOT, "work/r1/playcap/live-timeline.jsonl")

# Regime windows by file_mtime_ns (the r265 corpus law; the `wall` field has
# no date component — measured on a mid-file record). A and B healthy, the
# softlock window falls in the gap between them (excluded by construction).
_A_LO = time.mktime(time.strptime("2026-11-01 21:24:00", "%Y-%m-%d %H:%M:%S"))
_A_HI = time.mktime(time.strptime("2026-11-01 21:37:59", "%Y-%m-%d %H:%M:%S"))
_B_LO = time.mktime(time.strptime("2026-11-02 00:07:00", "%Y-%m-%d %H:%M:%S"))
_B_HI = time.mktime(time.strptime("2026-11-02 01:27:59", "%Y-%m-%d %H:%M:%S"))


def regime(ns):
    if _A_LO <= ns <= _A_HI:
        return "A"
    if _B_LO <= ns <= _B_HI:
        return "B"
    return None


def parse_ships(j):
    """slot -> (kind, owner, x, y, z) from the 177-u16 raw window."""
    out = {}
    for k, w in (j.get("ship_raw") or {}).items():
        if len(w) != 177:
            continue
        b = struct.pack("<177H", *w)
        st = b[0x58]
        if st == 0:
            continue
        x, y, z = struct.unpack_from("<3f", b, 0x9e)
        out[int(k)] = (st, b[0x56], x, y, z)
    return out


yield_counter = Counter()
flip_events = []


def main():
    tail = int(sys.argv[1]) if len(sys.argv) > 1 else 4_200_000_000
    size = os.path.getsize(JSONL)
    tail = min(tail, size)
    rows = []
    seen = set()
    total_lines = 0
    with open(JSONL, "rb") as f:
        f.seek(size - tail)
        if size > tail:
            f.readline()  # partial first line
        for line in f:
            total_lines += 1
            # OOM-law prefilter (r265 shape): byte-grep cheap fields before
            # json.loads; only in-window rows pay the parse cost.
            if b'"in_game": true' not in line:
                continue
            i = line.find(b'"file_mtime_ns": ')
            if i < 0:
                continue
            j0 = i + len(b'"file_mtime_ns": ')
            j1 = line.find(b",", j0)
            try:
                ns = int(line[j0:j1])
            except Exception:
                continue
            reg = regime(ns / 1e9)
            if reg is None:
                continue
            try:
                jj = json.loads(line)
            except Exception:
                continue
            t = jj.get("turn", 0)
            if not t or t <= 0:
                continue
            fn = jj.get("file", "")
            key = (fn, ns)
            if key in seen:
                continue
            seen.add(key)
            rows.append((ns, fn, t, reg, parse_ships(jj)))
    rows.sort(key=lambda r: r[0])
    print(f"lines scanned: {total_lines}; in-regime rows kept: {len(rows)}")
    if len(rows) < 50:
        print("HONEST NEGATIVE: epoch window not present in this tail (or "
              "timeline rotated). Try a bigger tail_bytes arg.")
        return 0

    # --- same-turn consecutive-row flips (mid-turn class) ---
    mid_flips = Counter()
    st5_same_turn_x = Counter()
    i = 0
    while i < len(rows) - 1:
        ns0, f0, t0, r0, s0 = rows[i]
        ns1, f1, t1, r1, s1 = rows[i + 1]
        if t0 == t1:
            for slot in set(s0) & set(s1):
                k0, o0, x0, y0, z0 = s0[slot]
                k1, o1, x1, y1, z1 = s1[slot]
                if k0 != k1:
                    mid_flips[(r0, k0, k1)] += 1
                if k0 == 5 and k1 == 5:
                    st5_same_turn_x[round(x1 - x0, 4)] += 1
            i += 1
        else:
            # boundary pair: THIS row vs the FIRST row of the next turn
            j = i + 1
            while j < len(rows) and rows[j][2] == t1:
                j += 1
            # rows[i+1..j-1] all turn t1; use rows[i+1] (first row of next turn)
            nsx, f1, t1, r1, s1 = rows[i + 1]
            flips = defaultdict(list)   # owner -> [slot,...] for 4->5
            rflips = defaultdict(list)  # 5->4
            for slot in set(s0) & set(s1):
                k0, o0, *_ = s0[slot]
                k1, o1, *_ = s1[slot]
                if k0 == 4 and k1 == 5:
                    flips[o0].append(slot)
                if k0 == 5 and k1 == 4:
                    rflips[o0].append(slot)
            for o, sl in flips.items():
                yield_counter[("4->5", r1, len(sl))] += 1
                if len(sl) > 1:
                    flip_events.append((r1, t0, "4->5", o, sorted(sl)))
            for o, sl in rflips.items():
                yield_counter[("5->4", r1, len(sl))] += 1
                if len(sl) > 1:
                    flip_events.append((r1, t0, "5->4", o, sorted(sl)))
            i += 1

    print("\n== A. mid-turn (same-turn consecutive rows) kind flips, by regime ==")
    if mid_flips:
        for k, v in sorted(mid_flips.items()):
            print("  ", k, v)
    else:
        print("   ZERO (S24 item 3 corroborated: one step per boundary)")
    print("   st5 same-turn x-deltas:", dict(st5_same_turn_x.most_common(6)))

    print("\n== B. per-boundary flip YIELDS (slots flipping per owner per "
          "boundary pair) ==")
    by_kind = defaultdict(Counter)
    for (kind, reg, n), v in yield_counter.items():
        by_kind[kind][n] += v
    for kind in by_kind:
        tot = sum(by_kind[kind].values())
        print(f"   {kind}: boundaries with yield n: "
              f"{dict(sorted(by_kind[kind].items()))}  (total events {tot})")

    print("\n== B2. multi-flip boundary EVENTS (regime, t->t+1, class, owner, "
          "slots) ==")
    for e in flip_events:
        print("  ", e)

    # --- st4 on-grid census ---
    off = Counter()
    st4 = 0
    for _, _, t, r, s in rows:
        for slot, (k, o, x, y, z) in s.items():
            if k == 4:
                st4 += 1
                if abs(x % 32) > 1e-3 or abs(z % 32) > 1e-3:
                    off[r] += 1
    print(f"\n== C. st4 rows: {st4}, off-32-grid by regime: {dict(off)} "
          f"(S24 item 1: 100% on-grid expected)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
