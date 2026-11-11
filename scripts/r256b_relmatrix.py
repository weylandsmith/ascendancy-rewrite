#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""r256b_relmatrix.py — AI-AI relation-state census over the live timeline.

t256b (gap row 12): the rewrite carries ONE attitude vector (AI->player); the
original carries a full n x n matrix — state byte row*0x1ee+col+0x1c0 and
attitude i16 row*0x1ee+col*0x1b2+2col (diplomacy.md §13.4a row law, code-
confirmed). The watcher banks the FULL matrix per row under "relation"
(scripts/r1_playcap_watch.py relation()). Question: do AI-vs-AI cells (i,j
both != the player row) ever leave 1, and what transitions fire without the
player as a party?

STREAMING law (t251 OOM): never json.loads the whole file. PITFALL (t256b,
measured): the relation object sits at LINE OFFSET ~28800 (after the ~28 KB
ship_raw window) — r255d's head[:600]/tail[-260] slices MISS it entirely.
Rows are compact JSON (no spaces except ': ' after keys), so the
'"states": [[' ... ']]' and '"atts": [[' ... ']]' arrays are unambiguous
(bracket-depth match). Per-session trust per the t255 law: dedup
(file, mtime_ns), split sessions on mtime gap > 600 s, stale-echo watermark
PER SESSION (the global watermark wrongly drops re-loaded lower-turn
campaigns).
"""
import json, sys, datetime
from collections import defaultdict

JSONL = sys.argv[1] if len(sys.argv) > 1 else "work/r1/playcap/live-timeline.jsonl"
PLAYER = sys.argv[2] if len(sys.argv) > 2 else "Chamachies"


def get_int(s, key, frm=0):
    i = s.find(key, frm)
    if i < 0:
        return None
    i += len(key)
    # t256b: skip ':' and spaces — the watcher writes compact-ish JSON where
    # ':' may or may not be followed by a space depending on the key path.
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


def get_file(head):
    i = head.find('"file": "')
    if i < 0:
        return None
    i += 9
    j = head.find('"', i)
    return head[i:j]


def get_str(s, key):
    i = s.find(key)
    if i < 0:
        return None
    i += len(key)
    j = s.find('"', i)
    k = s.find('"', j + 1)
    try:
        return json.loads("[" + s[j:k + 1] + "]")[0]
    except Exception:
        return None


def get_matrix(s, key):
    """Bracket-depth match a [[..],[..]] array following key."""
    i = s.find(key)
    if i < 0:
        return None
    i = s.find("[", i)
    if i < 0:
        return None
    depth = 0
    for k in range(i, len(s)):
        c = s[k]
        if c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(s[i:k + 1])
                except Exception:
                    return None
    return None


def main():
    seen = set()
    rows = []
    with open(JSONL, "r", errors="replace") as f:
        while True:
            line = f.readline()
            if not line:
                break
            fn = get_file(line[:200])
            if fn is None:
                continue
            mt = get_int(line[-260:], '"file_mtime_ns": ')
            turn = get_int(line[:200], '"turn": ')
            if mt is None or turn is None:
                continue
            key = (fn, mt)
            if key in seen:
                continue
            # relation only if present (cheap probe before the deep parse)
            ri = line.find('"states": [[', 600)
            if ri < 0:
                seen.add(key)
                continue
            rel = line[ri:]
            # PITFALL (t256b): rows are COMPACT JSON — no space after ':'.
            # Search the key without the trailing space, then match brackets.
            states = get_matrix(rel, '"states"')
            if states is None:
                seen.add(key)
                continue
            seen.add(key)
            atts = get_matrix(rel, '"atts"')
            # PITFALL: "n" precedes "states" in the object, so it is NOT in
            # the rel slice; n = len(states) IS the same value (the watcher's
            # relation() returns None unless names validate at that n).
            n = len(states)
            rows.append((mt, fn, turn, n, states, atts,
                         get_str(line, '"wall": ')))
    rows.sort()
    print(f"unique_rows_with_relation={len(rows)}")
    if not rows:
        return

    # sessions: mtime gap > 600 s
    sessions = []
    prev = None
    for r in rows:
        if prev is not None and (r[0] - prev[0]) / 1e9 > 600:
            sessions.append([])
        if not sessions:
            sessions.append([])
        sessions[-1].append(r)
        prev = r
    print(f"sessions={len(sessions)}")

    value_census = defaultdict(int)          # state value -> cell-observations
    ai_transitions = []                      # (turn, i, j, old, j2, wall, fn)
    all_transitions = 0
    n_seen = set()
    entry_states = defaultdict(lambda: defaultdict(int))  # (i,j) -> {v: count of sessions entering at v}
    ever_held = defaultdict(set)             # (i,j) -> set of values ever seen (trusted)
    max_att = {}                             # (i,j) -> max attitude i toward j
    for si, sess in enumerate(sessions):
        watermark = 0
        prev_row = None
        first_logged = False
        for (mt, fn, turn, n, states, atts, wall) in sess:
            if turn < watermark:
                continue                     # per-session stale echo
            watermark = max(watermark, turn)
            if n is None or not (2 <= n <= 40) or len(states) != n:
                continue
            n_seen.add(n)
            if not first_logged:
                first_logged = True
                for i in range(n):
                    for j in range(n):
                        if i != j:
                            entry_states[(i, j)][states[i][j]] += 1
            for i in range(n):
                for j in range(n):
                    if i != j:
                        value_census[states[i][j]] += 1
            if prev_row is not None:
                pn, pstates, patts = prev_row
                if pn == n:
                    for i in range(n):
                        for j in range(n):
                            if i != j and states[i][j] != pstates[i][j]:
                                all_transitions += 1
                                ai_transitions.append(
                                    (turn, i, j, pstates[i][j], states[i][j],
                                     wall, fn, si,
                                     atts[i][j] if atts else None))
            prev_row = (n, states, atts)

    print(f"n_values_seen={sorted(n_seen)}")
    print(f"state_value_census={dict(sorted(value_census.items()))}")
    print(f"total_transitions={all_transitions}")
    # t256b: per-pair ENTRY census (first trusted row of each session) —
    # distinguishes "value never leaves 1 mid-session" from "value can be
    # non-1 at load". Cross-session echoes of the SAME campaign re-load
    # inflate counts, so report as session-counts not cell-observations.
    names4 = ["Chamachies", "Orfa", "Ungooma", "Minions"]
    print("\nper-pair ENTRY state census (sessions entering at value):")
    for (i, j), d in sorted(entry_states.items()):
        nm = lambda k: names4[k] if k < 4 else str(k)
        party = "PLAYER" if (i == 0 or j == 0) else "AI-AI"
        print(f"  {nm(i)}->{nm(j)} [{party}] {dict(sorted(d.items()))}")
    pname = PLAYER
    # name resolution: sessions carry no names here; n=4 campaign is
    # [Chamachies, Orfa, Ungooma, Minions] (diplomacy.md §12 validated).
    names4 = ["Chamachies", "Orfa", "Ungooma", "Minions"]
    print("\n--- transitions (turn, i->name, j->name, old>new, wall, file, session) ---")
    for (turn, i, j, old, new, wall, fn, si, att) in ai_transitions:
        nm = lambda k: names4[k] if len(names4) > k else str(k)
        party = "PLAYER-PARTY" if (i == 0 or j == 0) else "AI-AI"
        print(f"t{turn} {nm(i)}->{nm(j)} {old}->{new} {party} wall={wall} {fn} sess={si} att={att}")
    ai_only = [t for t in ai_transitions if t[1] != 0 and t[2] != 0]
    print(f"\nAI-AI transitions: {len(ai_only)} of {len(ai_transitions)}")


if __name__ == "__main__":
    main()
