#!/usr/bin/env python3
"""r1_t85_combat.py RUN_DIR [--no-trust] — OQ-010 combat application evidence
extractor (t85; streaming rewrite t85b).

Question: hit probability, shield subtract-vs-absorb, overkill, firing
order — the APPLICATION laws (device constants are already data-verified:
gizmos damage 1..13, shields 1..5).

HONEST SCOPE: a 10 s autosave ring cannot resolve intra-battle ordering.
This tool BANKS the evidence a battle leaves in the slot stream and frames
the four sub-questions; the laws are then reasoned offline (this loop),
cross-checked against ships.md §6 design-record laws.

Ship record law [verified verbatim, FUN_00022304; r1_trajectory_regression.py
header + ships.md S10/S11]: array base runtime(B + 0x82bb0 + 0x3a095),
stride 0x162 (=177 u16), live count u32(B + 0x82bb0 + 0x43489) >> 16,
owner dword[+0x54]>>16, state byte +0x58 (3 = docked/landing success,
4 = airborne; ships.md S11 landing branches), design aggregates
(shield -> +0x4, scanner -> +0x20, drive -> +0x10, power -> +0x18 per
gizmo-sum @0x49b67), coords f32 +0x9e/+0xa2/+0xa6.

WHAT COUNTS AS BATTLE EVIDENCE in the slot stream:
  * a ship DISAPPEARS (was live, later slot's slot window all-zero or
    count shrank / owner becomes 0xFFFF)  -> destruction (overkill question);
  * a ship's u16 window CHANGES anywhere other than coords/state between
    consecutive slots while two enemy-owned ships are within a few units ->
    damage application candidates (report offset-by-offset);
  * owner flips on planet records or item-23 ring landings (capture chain,
    S10) -> battle resolution;
  * state 4 -> 3 with enemy nearby = combat ended via landing.

STREAMING (t85b): the jsonl grows past 4 GB across sittings; loading it all
was MEASURED at ~65 MB/1000 points = projected 12 GB (16 GB VM; the t85 run
was OOM-killed mid-analysis). This version keeps only the previous point in
RAM via scripts/r1_stream.py (order + dedup + stale-echo laws there).
--no-trust disables the stale-echo law (see r1_stream docstring caveat).

Input: live-timeline.jsonl (watcher; primary — the ring rolls off in ~200 s)
or the ring itself (fallback). Exit 0 = battle-class events found.
Exit 1 = ran, zero ship events (no combat happened in the capture). 2 = 2
harness error.
"""
import argparse, json, os, os.path, struct, sys, zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_slot as S
import r1_stream as ST

AGG = {0x4: "shield-agg", 0x10: "drive-agg", 0x18: "power-agg", 0x20: "scanner-agg"}
COORD_U16 = {0x9e // 2, (0x9e + 2) // 2, (0x9e + 4) // 2, (0x9e + 6) // 2}


def iter_watcher(run_dir, trust):
    stats = {}
    yield ("stats", stats)
    for j in ST.observations(run_dir, trust=trust, stats=stats):
        if j.get("ship_raw") is not None:
            yield j


def ring_points(run_dir, root, pay, anch):
    pts = []
    for d in S.timeline(run_dir, pay, root, anch=anch, verbose=False):
        if not d["in_game"]:
            continue
        mem = zipfile.ZipFile(d["path"]).read("Memory")
        base, n = S.ship_array_law(mem, d["base"])
        raw = {str(k): list(struct.unpack_from("<177H", mem, base + k * 0x162))
               for k in range(min(n, 0x6b))}
        ships = []
        for k in range(min(n, 0x6b)):
            r = base + k * 0x162
            ships.append(dict(slot=k,
                              owner=struct.unpack_from("<I", mem, r + 0x54)[0] >> 16,
                              state=struct.unpack_from("<B", mem, r + 0x58)[0],
                              xyz=list(struct.unpack_from("<3f", mem, r + 0x9e))))
        pts.append(dict(file=d["file"], turn=d["turn"], ship_raw=raw,
                        ships=ships))
    return pts


def alive(w):
    return any(w) and not all(x == 0xFFFF for x in w)


def diff_pair(p, q, emit):
    """Battle-class events between two consecutive trusted points."""
    events = 0
    rw, rw2 = p["ship_raw"], q["ship_raw"]
    if rw == rw2:
        return 0
    touched = False
    for k in sorted(set(rw) | set(rw2), key=int):
        w1, w2 = rw.get(k), rw2.get(k)
        if w1 is None or w2 is None:
            events += 1
            emit(f"  t{p['turn']}->{q['turn']}: ship {k} slot "
                 f"{'appeared' if w1 is None else 'VANISHED'} "
                 f"({q['file']})")
            continue
        if alive(w1) != alive(w2):
            events += 1
            emit(f"  t{p['turn']}->{q['turn']}: ship {k} ALIVE->"
                 f"{'ALIVE' if alive(w2) else 'DEAD-or-purged'} "
                 f"({q['file']}) — OVERKILL question evidence")
        o1 = w1[0x54 // 2] | (w1[0x54 // 2 + 1] << 16)
        o2 = w2[0x54 // 2] | (w2[0x54 // 2 + 1] << 16)
        if o1 != o2:
            events += 1
            emit(f"  t{p['turn']}->{q['turn']}: ship {k} owner "
                 f"{o1:#06x}->{o2:#06x} ({q['file']})")
        diffs = [(i, w1[i], w2[i]) for i in range(177)
                 if w1[i] != w2[i] and i not in COORD_U16]
        if not diffs:
            continue
        touched = True
        off_rows = []
        for i, v1, v2 in diffs:
            bo = i * 2
            tag = AGG.get(bo, "")
            off_rows.append(f"+0x{bo:x}:{v1}->{v2}" + (f" [{tag}]" if tag else ""))
        if alive(w1):
            events += 1
            emit(f"  t{p['turn']}->{q['turn']}: ship {k} state="
                 f"{w1[0x58 // 2]} u16 window changed ({len(diffs)} fields):")
            for r_ in off_rows[:24]:
                emit(f"      {r_}")
    if touched:
        emit(f"  --- {q['file']}: ships now: "
             + ", ".join(f"{s['slot']}:o{s['owner']:#x}s{s['state']}"
                         f"{[round(c, 1) for c in s['xyz']]}"
                         for s in q.get("ships", []) if s["owner"] != 0xFFFF)
             or "(none owned)")
    return events


MAX_PRINT = 400          # bounded stdout: after this, count-only


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

    n_printed = [0]
    def emit(msg):
        if n_printed[0] < MAX_PRINT:
            print(msg)
            if n_printed[0] == MAX_PRINT - 1:
                print(f"  ... (stdout capped at {MAX_PRINT} lines; event "
                      f"COUNTING continues)")
        n_printed[0] += 1

    pay = S.load_payload(root)
    anch = S.anchors_cached(root, pay)
    gen = iter_watcher(a.run_dir, trust=not a.no_trust)
    stats = next(gen)[1]
    prev = None
    n_pts = 0
    events = 0
    quiet_turns = 0
    for p in gen:
        n_pts += 1
        if prev is None:
            prev = p
            continue
        e = diff_pair(prev, p, emit)
        if e == 0 and n_printed[0] >= MAX_PRINT:
            quiet_turns += 1
        events += e
        prev = p
    src = "watcher (streamed)"
    if n_pts == 0:
        pts = ring_points(a.run_dir, root, pay, anch)
        src = "ring (what survived)"
        for p, q in zip(pts, pts[1:]):
            events += diff_pair(p, q, emit)
        n_pts = len(pts)
    print(f"points: {n_pts} (source: {src}) — {ST.echo_note(stats)}")
    if n_pts == 0:
        print("No trusted (turn>0) points: the session never entered a "
              "campaign (title-only capture). Not a harness bug — play in, "
              "then rerun.")
        return 1
    if n_pts < 2:
        print("Only one trusted point banked — need >=2 to diff. Play "
              "through at least one End Turn AFTER the battle.")
        return 1

    print()
    if events:
        print(f"{events} battle-class observations banked above.")
        print("SUB-QUESTION FRAMING (to be decided offline from these rows):")
        print("  hit prob   : count engaged turns vs observed damage events")
        print("  shield     : does target damage == attacker_power - shield_agg"
              " (subtract) or == max(1, ...) masked by shield (absorb)?")
        print("  overkill   : DEAD slots whose last window still shows"
              " nonzero aggregates?")
        print("  firing order: 10 s AUTOSAVE GRANULARITY CANNOT RESOLVE this;")
        print("                close class = in-battle UI recording or static"
              " code site, NOT the ring.")
        return 0
    print("Zero ship-activity events: NO BATTLE OCCURRED in this capture "
          "(same null class as T49/T58). Build/launch a fleet, get two"
          " enemy-owned ships touching, End Turn, wait 15+ s, then rerun.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
