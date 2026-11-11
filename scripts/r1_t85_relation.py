#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""r1_t85_relation.py RUN_DIR [--no-trust] — OQ-023 relation-state ENUM
adjudication (t85; streaming rewrite t85b).

Question (docs/re/diplomacy.md §10): which nonzero value is war and which is
allied?

Field laws (verbatim §7; offsets relative to race DIPLOMA record base =
DAT_00012e16 + 0x1ee*race):
  state byte   record +0x1c0 + TARGET idx  <-- A MATRIX (rows = acting race,
               cols = target). The first watcher pass stored only the
               target-0 column; that, not the corpus, is why earlier censuses
               "saw only value 1" (5 cells of n*(n-1)).
  attitude i16 record +0x1b2 + 2*target
  THIRD-PARTY matrix: separate window (&DAT_00012fd6)[me*0x1ee + other]
Chooser semantics (§7, code-confirmed) — a value ALONE never distinguishes
war from alliance:
  0 no relationship | 1 declare-war iff att<DECLARE_WAR(+0x1c9) else
    propose-alliance iff PROPOSE_ALLIANCE(+0x1d3)<att
  2 third-party-eligible, no direct action, cadence skipped
  3 offer-peace iff PROPOSE_PEACE(+0x1cd)<att else break-alliance iff
    att<BREAK_ALLIANCE(+0x1cf)
So the closing evidence = value + player's stated action + attitude vs that
race's resolved thresholds, all banked side by side here.

BASE VALIDATION independent of the anchor vote (t77b retraction rule): %m
name law (§5) — byte(DAT_00012e17+0x1ee*i) indexes 20-byte names at
DAT_00074590; every row must resolve printable or the slot is dropped.

STREAMING (t85b): points are yielded one at a time via scripts/r1_stream.py
(order + dedup + stale-echo laws there). This matters for OQ-023 beyond
memory: the banked 4.3 GB stream contains 12k+ rows from a STALE second
instance parked at turn 692, and interleaved duplicate watchers; naive
file-order diffing invented ~half the fake transitions (e.g. a whole
782->692->782 bounce per 10 s). What remains is the real event list:
each transition is printed with its banked wall-clock so it can be paired
with what the player actually did.

Primary source = watcher live-timeline.jsonl (durable across ring rollover);
fallback = surviving ring slots. v1-schema jsonl lines (states as vector) are
skipped with a count.

Exit 0 = transitions banked. 1 = ran, none. 2 = harness error.
"""
import argparse, json, os, os.path, re, struct, sys, zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_slot as S
import r1_stream as ST

NAME_RE = re.compile(rb"[A-Za-z][A-Za-z '^_.\-]{2,19}")
KEYS = {0x1c9: "DECLARE_WAR", 0x1cb: "ACCEPT_PEACE", 0x1cd: "PROPOSE_PEACE",
        0x1cf: "BREAK_ALLIANCE", 0x1d1: "ACCEPT_ALLIANCE",
        0x1d3: "PROPOSE_ALLIANCE", 0x1d5: "START_ATTITUDE"}


def diplo_rows(mem, M, n):
    names, states, atts, th = [], [], [], []
    for i in range(n):
        nb = mem[M + 0x12e17 + 0x1ee * i]
        nm = mem[M + 0x74590 + nb * 0x14: M + 0x74590 + nb * 0x14 + 20
                 ].split(b"\x00")[0]
        if not NAME_RE.fullmatch(nm):
            return None
        names.append(nm.decode("latin-1"))
        rb = M + 0x12e16 + 0x1ee * i
        states.append([mem[rb + 0x1c0 + j] for j in range(n)])
        atts.append([struct.unpack_from("<h", mem, rb + 0x1b2 + 2 * j)[0]
                     for j in range(n)])
        th.append({v: struct.unpack_from("<h", mem, rb + k)[0]
                   for k, v in KEYS.items()})
    return names, states, atts, th


def third_party(mem, M, n):
    return [[mem[M + 0x12fd6 + i * 0x1ee + j] for j in range(n)]
            for i in range(n)]


def point_from_json(j):
    r = j.get("relation") or {}
    if not (r and isinstance(r.get("states", [[]])[0], list)):
        return None
    return dict(file=j["file"], turn=j["turn"], wall=j.get("wall", "?"),
                n=r["n"], names=r["names"], states=r["states"],
                atts=r["atts"], th=r["th"], tp=r["matrix"])


def watcher_points(run_dir, trust, stats):
    """Generator (streaming); stats dict (passed in) is filled by r1_stream."""
    stale = 0
    for j in ST.observations(run_dir, trust=trust, stats=stats):
        p = point_from_json(j)
        if p is None:
            stale += 1
            continue
        yield p
    stats["v1_schema_skipped"] = stale


def ring_points(run_dir, root, pay, anch):
    out = []
    for d in S.timeline(run_dir, pay, root, anch=anch, verbose=False):
        if not d["in_game"]:
            continue
        mem = zipfile.ZipFile(d["path"]).read("Memory")
        M = d["base"] + S.OFF
        n = struct.unpack_from("<I", mem, M + 0x13b96)[0] >> 16
        if n < 2 or n > 40:
            continue
        rows = diplo_rows(mem, M, n)
        if rows is None:
            continue
        names, states, atts, th = rows
        out.append(dict(file=d["file"], turn=d["turn"], wall="?", n=n,
                        names=names, states=states, atts=atts, th=th,
                        tp=third_party(mem, M, n)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--no-trust", action="store_true",
                    help="disable the stale-echo law (see r1_stream)")
    a = ap.parse_args()
    if not os.path.isdir(a.run_dir):
        print("harness-error: no run dir")
        return 2
    root = os.getcwd()

    # PASS 1 (streaming, cheap): census values + collect TRANSITIONS only.
    # Matrices for transition turns are re-read in PASS 2 (ring may be gone;
    # then we rely on the banked atts/th in the jsonl rows we stream twice).
    stats = {}
    vals = set()
    tpvals = set()
    race_names = None
    n_pts = 0
    transitions = []
    prev = None
    for p in watcher_points(a.run_dir, trust=not a.no_trust, stats=stats):
        n_pts += 1
        race_names = p["names"]
        for i in range(p["n"]):
            for j in range(p["n"]):
                if i != j:
                    vals.add(p["states"][i][j])
                    tpvals.add(p["tp"][i][j])
        if prev and prev["turn"] != p["turn"]:
            if prev["n"] != p["n"]:
                transitions.append(("racen", prev, p))
            elif len(prev["names"]) == len(p["names"]):
                for i in range(p["n"]):
                    for j in range(p["n"]):
                        if prev["states"][i][j] != p["states"][i][j]:
                            transitions.append(("rec", prev, p, i, j))
                        if prev["tp"][i][j] != p["tp"][i][j]:
                            transitions.append(("tp", prev, p, i, j))
        prev = p
    src = "watcher jsonl (streamed)"
    if n_pts == 0:
        pay = S.load_payload(root)
        anch = S.anchors_cached(root, pay)
        pts = ring_points(a.run_dir, root, pay, anch)
        src = "ring (what survived)"
        n_pts = len(pts)
        vals = {pts[k]["states"][r][m] for k in range(len(pts))
                for r in range(len(pts[k]["states"]))
                for m in range(len(pts[k]["states"])) if r != m}
        race_names = pts[-1]["names"] if pts else None
        transitions = []
        for prev, cur in zip(pts, pts[1:]):
            for i in range(cur["n"]):
                for j in range(cur["n"]):
                    if prev["states"][i][j] != cur["states"][i][j]:
                        transitions.append(("rec", prev, cur, i, j))
                    if prev["tp"][i][j] != cur["tp"][i][j]:
                        transitions.append(("tp", prev, cur, i, j))

    print(f"validated relation points: {n_pts} (source: {src})")
    print(ST.echo_note(stats))
    if stats.get("v1_schema_skipped"):
        print(f"note: {stats['v1_schema_skipped']} v1-schema jsonl rows skipped")
    if not race_names:
        print("No in-game slot passed base+name validation (title-only "
              "capture?). If a real campaign ran and this still fails, it IS "
              "a harness bug — report it.")
        return 1
    print("races: " + ", ".join(f"{i}:{n}" for i, n in enumerate(race_names)))

    # transitions: collapse repeats of the SAME (pair, value-change) into one
    # line with a count + first/last wall-clock (duplicate watchers banked the
    # same boundary change many times before the dedup fix).
    collapsed = {}
    order = []
    for tr in transitions:
        kind = tr[0]
        if kind == "racen":
            key = ("racen", tr[1]["n"], tr[2]["n"])
        else:
            _, prev, cur, i, j = tr
            key = (kind, tuple(cur["names"]), i, j,
                   prev["states"][i][j] if kind == "rec" else prev["tp"][i][j],
                   cur["states"][i][j] if kind == "rec" else cur["tp"][i][j])
        if key not in collapsed:
            collapsed[key] = [tr, tr, 1]
            order.append(key)
        else:
            collapsed[key][1] = tr
            collapsed[key][2] += 1

    print(f"\nTRANSITIONS (the closing evidence — pair with what YOU did): "
          f"{len(order)} distinct, {sum(c for *_, c in collapsed.values())} raw")
    for key in order:
        first_tr, last_tr, cnt = collapsed[key]
        if first_tr[0] == "racen":
            print(f"  t{first_tr[1]['turn']}->{first_tr[2]['turn']} "
                  f"(x{cnt}, {first_tr[1]['wall']}..{last_tr[2]['wall']}): "
                  f"race count {first_tr[1]['n']}->{first_tr[2]['n']} "
                  f"(elimination or new contact)")
            continue
        kind, names, i, j, v1, v2 = key
        _, prev, cur, _, _ = first_tr
        nm = cur["names"]
        th = cur["th"][i]
        label = f"rec[{nm[i]}->{nm[j]}]" if kind == "rec" else f"3P[{nm[i]}->{nm[j]}]"
        span = first_tr[1]["wall"] if cnt == 1 else f"{first_tr[1]['wall']}..{last_tr[1]['wall']}"
        print(f"  t{prev['turn']}->{cur['turn']} ({label} {v1}->{v2} "
              f"att={cur['atts'][i][j]}, DW={th['DECLARE_WAR']} "
              f"PP={th['PROPOSE_PEACE']} BA={th['BREAK_ALLIANCE']} "
              f"PA={th['PROPOSE_ALLIANCE']}) x{cnt} @{span}")
    if not order:
        print("  (none)")

    nz = sorted(v for v in (vals | tpvals) if v)
    print(f"\ndistinct nonzero values observed across trusted stream: {nz or '[]'}")
    if nz and nz == [1]:
        print("=> value 1 alone: consistent with BOTH war and alliance per "
              "§7 (same state feeds both branches, split is on attitude). "
              "Adjudication needs the attitude pairing above plus what you "
              "actually did.")
    print("ADJUDICATION: tell the assistant, in order, which race you "
          "declared war on and which you allied with (and roughly when — the "
          "wall-clock spans above anchor 'when'). The transitions pin the enum.")
    return 0 if order else 1


if __name__ == "__main__":
    sys.exit(main())
