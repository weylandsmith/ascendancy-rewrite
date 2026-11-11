#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""r256c_shipstate.py — per-ship ORDER-STATE census over the live timeline.

t256c (AI gap row 16): the dossier's cited ship-order laws (§5 stickiness,
0x220f2 retreat-downgrade, t179 P1 power tie-break, t179 P3 invasion-module
carrier) are all functions of per-ship fields the watcher ALREADY banks every
row: "ship_raw" = per live slot the verbatim 177-u16 window of the 0x162-byte
ship record (scripts/r1_playcap_watch.py:93; array law scripts/r1_slot.py:133
base = B+0x82bb0+0x3a095, count = u32[0x43489]>>16 cap 0x6b).

Cited field map (docs/re/ai-dossier.md §5/§6, combat.md S2g/t101, t179 P3):
  +0x10 design handle (u32)        +0x54 owner (u32>>16)
  +0x58 ORDER KIND (byte, 0..5)    +0x59 ORDER TARGET ptr (u32)
  +0x5d ACT enum (byte)            +0x88 POWER (u32)   +0x94 MOVES (u32)
  +0xab gizmo ring, stride 7 BYTES, count dword at +0x15a (ships.md 632)
  slot type byte = ring+0; 0xff empty; 0x49 == Invasion Module (gizmos row 73)
  (u16 index = byte/2; the ring is BYTE-aligned odd, so bytes are rebuilt from
   the u16 window with struct.pack before indexing.)

STREAMING law (t251 OOM): never json.loads the whole file — per-row slices
only. PITFALL (t256b/t256c): the big per-row windows sit at line offset
~3200..~28800; head/tail slices MISS them, so the ship_raw object is located
by find() and closed by bracket-depth match. Per-session trust per the t255
law: dedup (file, mtime_ns), split sessions on mtime gap > 600 s, per-session
turn watermark (the global watermark wrongly drops re-loaded campaigns).
PITFALL (t251): ship SLOTS can be remapped mid-campaign, so transition stats
condition on owner equality and are reported as slot-pair observations.
"""
import json, struct, struct as st, sys
from collections import defaultdict

JSONL = sys.argv[1] if len(sys.argv) > 1 else "work/r1/playcap/live-timeline.jsonl"


def oc_of(o):
    if o is None or o in (0xffff, 0xffffffff):
        return "DEAD"
    return "PLAYER" if o == 0 else "AI"


def get_int(s, key, frm=0):
    i = s.find(key, frm)
    if i < 0:
        return None
    i += len(key)
    while i < len(s) and s[i] in ": ":
        i += 1
    j = s.find(",", i)
    j2 = s.find("}", i)
    if j < 0 or (0 <= j2 < j):
        j = j2
    try:
        return int(s[i:j].strip())
    except Exception:
        return None


def get_obj(s, key):
    """Bracket-depth match the object {..} following key."""
    i = s.find(key)
    if i < 0:
        return None
    i = s.find("{", i)
    if i < 0:
        return None
    depth = 0
    for k in range(i, len(s)):
        c = s[k]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(s[i:k + 1])
                except Exception:
                    return None
    return None


def decode(u16s):
    """u16 window -> dict of cited fields (bytes rebuilt for odd offsets)."""
    b = struct.pack("<%dH" % len(u16s), *u16s)

    def u32(off):
        return st.unpack_from("<I", b, off)[0] if off + 4 <= len(b) else None
    kind = b[0x58]
    owner = u32(0x54) >> 16
    act = b[0x5d]
    nslot = u32(0x15a)
    if nslot is None or nslot > 64:
        nslot = 0
    ring_types = []
    for i in range(int(nslot)):
        o = 0xab + 7 * i
        if o >= len(b):
            break
        ring_types.append(b[o])
    return dict(owner=owner, kind=kind, act=act,
                target=u32(0x59), design=u32(0x10),
                power=u32(0x88), moves=u32(0x94),
                nslot=int(nslot), ring=ring_types)


def main():
    """SINGLE-PASS stream (t256c): the timeline is append-ordered by save
    mtime, so session splits (gap > 600 s) and the per-session turn
    watermark need no buffering. Storing all decoded rows would cost >1.5 GB
    RSS on a 7.3 GB corpus — the t251 OOM class."""
    seen = set()
    no_shipraw = 0
    n_rows = 0
    kind_census = defaultdict(int)              # (owner_class, kind) -> obs
    act_census = defaultdict(int)
    live_obs = 0
    power_nonzero = 0
    moves_nonzero = 0
    invmod_slots = 0
    invmod_rows = 0
    invmod_ships = set()                        # (fn,mt,slot) holding 0x49
    ring_type_census = defaultdict(int)
    kind_trans = defaultdict(int)               # (owner_class, old, new)
    retreat = defaultdict(int)                  # (owner_class, old) -> 4
    retreat_first = []
    target_changes = 0
    kind_changes_total = 0
    sticky_kept = 0
    sessions = 0
    prev_mt = None
    watermark = 0
    prev_recs = None
    turn_min, turn_max = None, None

    with open(JSONL, "r", errors="replace") as f:
        while True:
            line = f.readline()
            if not line:
                break
            i = line.find('"file": "')
            if i < 0:
                continue
            i += 9
            j = line.find('"', i)
            fn = line[i:j]
            mt = get_int(line[-260:], '"file_mtime_ns": ')
            turn = get_int(line[:200], '"turn": ')
            if fn is None or mt is None or turn is None:
                continue
            key = (fn, mt)
            if key in seen:
                continue
            seen.add(key)
            if prev_mt is not None and (mt - prev_mt) / 1e9 > 600:
                sessions += 1
                watermark = 0
                prev_recs = None
            if prev_mt is None:
                sessions = 1
            prev_mt = mt
            if turn < watermark:
                continue                        # per-session stale echo
            watermark = max(watermark, turn)
            sr = get_obj(line, '"ship_raw"')
            if not sr:
                no_shipraw += 1
                continue
            n_rows += 1
            turn_min = turn if turn_min is None else min(turn_min, turn)
            turn_max = turn if turn_max is None else max(turn_max, turn)
            recs = {}
            for k, v in sr.items():
                if isinstance(v, list) and len(v) >= 0x98:
                    try:
                        recs[int(k)] = decode(v)
                    except Exception:
                        pass
            for k, fr in recs.items():
                oc = oc_of(fr["owner"])
                kind_census[(oc, fr["kind"])] += 1
                act_census[(oc, fr["act"])] += 1
                if oc != "DEAD":
                    live_obs += 1
                    if fr["power"]:
                        power_nonzero += 1
                    if fr["moves"]:
                        moves_nonzero += 1
                    for t in fr["ring"]:
                        ring_type_census[t] += 1
                        if t == 0x49:
                            invmod_slots += 1
                            invmod_rows += 1
                            invmod_ships.add((fn, k, fr["owner"]))
            if prev_recs is not None:
                for k, fr in prev_recs.items():
                    nf = recs.get(k)
                    if nf is None or nf["owner"] != fr["owner"]:
                        continue                # slot remap (t251 law)
                    oc = oc_of(fr["owner"])
                    if nf["kind"] != fr["kind"]:
                        kind_changes_total += 1
                        kind_trans[(oc, fr["kind"], nf["kind"])] += 1
                        if fr["kind"] in (1, 2, 3) and nf["kind"] == 4:
                            retreat[(oc, fr["kind"])] += 1
                            if len(retreat_first) < 20:
                                retreat_first.append(
                                    (turn, k, fr["owner"], fr["kind"]))
                    if nf["target"] != fr["target"]:
                        target_changes += 1
                    if fr["kind"] in (1, 2, 5) and nf["kind"] == fr["kind"]:
                        sticky_kept += 1
            prev_recs = recs

    print(f"unique_rows_with_ship_raw={n_rows}  rows_without={no_shipraw}")
    print(f"sessions={sessions}  turn_range={turn_min}..{turn_max}")
    print("\n=== KIND CENSUS (owner_class, kind) -> slot observations ===")
    for (oc, k), c in sorted(kind_census.items()):
        print(f"  {oc:6s} kind={k}: {c}")
    print("\n=== ACT CENSUS (owner_class, act) ===")
    for (oc, a), c in sorted(act_census.items()):
        print(f"  {oc:6s} act={a}: {c}")
    print(f"\nlive_slot_obs={live_obs} power_nonzero={power_nonzero} "
          f"moves_nonzero={moves_nonzero}")
    print(f"invasion_module(0x49): slot-obs={invmod_slots} "
          f"distinct_ships={len(invmod_ships)}")
    top = sorted(ring_type_census.items(), key=lambda x: -x[1])[:15]
    print(f"ring_type_census(top15)={ {hex(t): c for t, c in top} }")
    print(f"\nkind_changes_total={kind_changes_total} "
          f"retreat_downgrade(1|2|3->4)={sum(retreat.values())} "
          f"target_changes={target_changes} sticky_kept={sticky_kept}")
    print("--- kind transitions (owner_class, old, new) -> count ---")
    for (oc, o, n), c in sorted(kind_trans.items()):
        print(f"  {oc} {o}->{n}: {c}")
    if retreat_first:
        print("--- first 20 retreat-downgrades (turn slot owner old->4) ---")
        for t in retreat_first:
            print(f"  t{t[0]} slot{t[1]} owner{t[2]} {t[3]}->4")


if __name__ == "__main__":
    main()
