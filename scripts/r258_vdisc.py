#!/usr/bin/env python3
"""r258_vdisc.py — t258 OQ-021: end-turn-recompute discriminator for
V = DAT_000482fb (the "STARS CONTROLLED" count, score.md S2).

TEST (STATE.md t258 task, verbatim): stream the corpus ONCE with PER-SESSION
trust (t255 law — the global watermark wrongly drops re-loaded lower-turn
campaigns), compute a candidate feature vector per row, and diff the vector
across every V-change turn-boundary vs V-stable turn-boundaries as control.

FEATURE VECTOR (banked fields only, no new capture):
  V, turn, T(total stars), systems_any, systems_full, planets_mine,
  alive_total, alive_player, alive_ai,
  player order-kind multiset kinds0..5, ai order-kind multiset kinds0..5
  (order kind = ship-record byte +0x58 rebuilt from the verbatim 177-u16
   window; decode() is r256c_shipstate.py's reference implementation)

STRICT BAR: a candidate discriminates iff it CHANGES at EVERY V-change
boundary and AT NO V-stable turn boundary (all sessions). Output is the
candidicide table either way. V==0 rows (load/title class) are excluded from
the fit; the first non-zero V row after each V==0 stretch is reported with its
full vector (consistency check for the reproduced-V=23@t1087 lineage pair).

STREAMING law (t251 OOM): readline + fixed slices + bracket-depth get_obj per
row; NOTHING is buffered except boundary records (O(#boundaries)).
PITFALLS: '"file": "' is 9 chars (i += 9); ship_raw sits mid-line (head/tail
miss); systems_*/wall at line END (tail -260); dedup key (file, mtime_ns).
"""
import json, struct, struct as st, sys, datetime
from collections import defaultdict

JSONL = sys.argv[1] if len(sys.argv) > 1 else "work/r1/playcap/live-timeline.jsonl"

FEAT_NAMES = ["V", "turn", "T", "rank", "sel", "systems_any", "systems_full",
              "planets_mine", "alive_total", "alive_player", "alive_ai",
              "P_k0", "P_k1", "P_k2", "P_k3", "P_k4", "P_k5",
              "A_k0", "A_k1", "A_k2", "A_k3", "A_k4", "A_k5"]


def _dedup_adjacent(seq):
    """Collapse consecutive duplicate (turn, V) pairs; keep first sighting."""
    out = []
    for x in seq:
        if not out or out[-1] != x:
            out.append(x)
    return out


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


def kind_of(u16s):
    """Order-kind byte (+0x58) of one ship slot from its 177-u16 window."""
    b = struct.pack("<%dH" % len(u16s), *u16s)
    owner = st.unpack_from("<I", b, 0x54)[0] >> 16
    return owner, b[0x58]


KEY_SHIP = '"ship_raw": {'          # 14 chars — t258 BUG C: i += 13 sliced
                                    # from the first KEY's quote, so json.loads
                                    # returned a scalar STRING (no exception)
                                    # and every ship feature silently died
def ship_raw_fast(line):
    """FAST extractor: the ship_raw object is a dict of int-lists (no nested
    braces), so the first '}' after its '{' closes it — the generic
    bracket-depth walk over a 25 KB line costs ~6x more. GUARD (t258): the
    result must be a dict, else treat as missing."""
    i = line.find(KEY_SHIP)
    if i < 0:
        return None
    i += len(KEY_SHIP)
    if line[i] == "}":
        return {}                       # empty dict == zero live slots
    j = line.find("}", i)
    if j < 0:
        return None
    try:
        # THE SLICE IS BRACE-DEFICIENT: i starts AFTER the opening '{' and j is
        # the closing '}', so the segment is `"0": [..], ...}` — json.loads on
        # it dies "Extra data: line 1 column 4". Re-add the leading brace
        # (t258 bug D; the isinstance guard is what kept it silent).
        v = json.loads("{" + line[i:j + 1])
    except Exception:
        return None
    return v if isinstance(v, dict) else None


def features(fn, mt, turn, T, V, rank, sel, sany, sfull, pmine, ship_raw):
    pk = [0] * 7
    ak = [0] * 7
    if ship_raw:
        for k, v in ship_raw.items():
            if not (isinstance(v, list) and len(v) >= 0x98):
                continue
            try:
                owner, kind = kind_of(v)
            except Exception:
                continue
            oc = oc_of(owner)
            if oc == "PLAYER":
                pk[min(kind, 6)] += 1
            elif oc == "AI":
                ak[min(kind, 6)] += 1
    # alive counts = slots classified by OWNER (t256c law: kind 0 appears only
    # on dead slots, so owner classification alone is the live filter)
    # present-vs-missing is kept distinct from an EMPTY dict (zero live slots):
    # t258 saw title/menu-class rows with V nonzero and no ship array at all.
    alive_p, alive_a = sum(pk), sum(ak)
    has = ship_raw is not None
    return [V, turn, T, rank, sel, sany, sfull, pmine,
            (alive_p + alive_a) if has else None,
            alive_p if has else None,
            alive_a if has else None] + pk[:6] + ak[:6]


def main():
    seen = set()
    sessions = 1
    prev_mt = None
    watermark = 0
    prev = None            # (session, fn, mt, turn, vec, wall) trusted prev row
    zero_streak_open = False
    n_rows = n_v0 = n_dedup = n_stale = 0
    midturn = []
    vchg = []              # boundary records
    stable_cnt = [0] * len(FEAT_NAMES)   # V-stable TURN boundaries where feat changed
    stable_turnb = 0
    stable_samefile = 0
    first_after_zero = []  # (session, turn, wall, vec)
    v0_turns = []
    syserr = 0
    none_census = defaultdict(int)
    traj = defaultdict(list)     # session -> [(turn, V)] at every V change
    hi25 = []
    lineage_agg = {}       # (session, turn, V) -> rows (t1254 lineage cross-check)

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
            tail = line[-260:]
            mt = get_int(tail, '"file_mtime_ns": ')
            head = line[:200]
            turn = get_int(head, '"turn": ')
            if fn is None or mt is None or turn is None:
                continue
            key = (fn, mt)
            if key in seen:
                n_dedup += 1
                continue
            seen.add(key)
            if prev_mt is not None and (mt - prev_mt) / 1e9 > 600:
                sessions += 1
                watermark = 0
                prev = None
            prev_mt = mt
            if turn < watermark:
                n_stale += 1
                continue
            watermark = max(watermark, turn)
            V = get_int(head, '"score_stars": ')
            T = get_int(head, '"T": ')
            sany = get_int(tail, '"systems_any": ')
            sfull = get_int(tail, '"systems_full": ')
            pmine = get_int(tail, '"planets_mine": ')
            wall = get_int(tail, '"wall": "00"')  # unused placeholder
            wi = tail.find('"wall": "')
            wall = tail[wi + 9:wi + 17] if wi >= 0 else "?"
            if V is None or V == 0:
                n_v0 += 1
                zero_streak_open = True
                prev = None
                if turn > 0:
                    v0_turns.append((sessions, turn))
                continue
            n_rows += 1
            if V >= 25 and len(hi25) < 20:
                hi25.append((sessions, turn, V))
            rank = get_int(head, '"rank": ')
            sel = get_int(head, '"selector_byte": ')
            if '"systems_error"' in tail or '"systems_error"' in line[-400:]:
                syserr += 1
            for nm, val in (("systems_any", sany), ("systems_full", sfull),
                            ("planets_mine", pmine)):
                if val is None:
                    none_census[nm] += 1
            if get_obj(line, '"ship_raw"') is None and '"ship_raw": {}' not in line:
                none_census["ship_raw(missing)"] += 1
            vec = features(fn, mt, turn, T, V, rank, sel, sany, sfull, pmine,
                           ship_raw_fast(line))
            if zero_streak_open:
                first_after_zero.append((sessions, turn, wall, vec))
                traj[sessions].append((turn, V))
                zero_streak_open = False
            if turn in (1254, 1255, 1086, 1087):
                k = (sessions, turn, V)
                lineage_agg[k] = lineage_agg.get(k, 0) + 1
            if prev is not None:
                p_ses, p_fn, p_mt, p_turn, pvec, p_wall = prev
                turn_adv = p_turn != turn
                if vec[0] != pvec[0]:
                    rec = dict(ses=p_ses, pturn=p_turn, turn=turn,
                               pV=pvec[0], V=V, pfn=p_fn, fn=fn,
                               wall=wall,
                               d=[(FEAT_NAMES[i], pvec[i], vec[i])
                                  for i in range(1, len(FEAT_NAMES))
                                  if vec[i] != pvec[i]])
                    if turn_adv:
                        vchg.append(rec)
                        traj[p_ses].append((p_turn, pvec[0]))
                        traj[p_ses].append((turn, V))
                    else:
                        midturn.append(rec)
                elif turn_adv:
                    # V-stable TURN boundary = the control population
                    stable_turnb += 1
                    if p_fn == fn:
                        stable_samefile += 1
                    for i in range(1, len(FEAT_NAMES)):
                        if vec[i] != pvec[i]:
                            stable_cnt[i] += 1
            prev = (sessions, fn, mt, turn, vec, wall)

    print(f"trusted_V_rows={n_rows} v0_rows={n_v0} dedup={n_dedup} "
          f"stale={n_stale} sessions={sessions}")
    print(f"V-change MID-TURN boundaries={len(midturn)} "
          f"(t255 expectation: 0)")
    for r in midturn[:10]:
        print("  MID", r)
    print(f"V-change TURN boundaries={len(vchg)}   "
          f"V-stable turn boundaries (control)={stable_turnb} "
          f"(same-file pairs={stable_samefile})")
    print(f"V>=25 rows={hi25}")
    print(f"rows_with_systems_error={syserr}")
    print(f"none_census(trusted V rows)={dict(none_census)}")
    print("\n=== PER-SESSION V TRAJECTORY (every V change, same session) ===")
    for s in sorted(traj):
        seq = traj[s]
        print(f"S{s:02d}: " + " ".join(f"t{t}:V{v}" for t, v in
                                       _dedup_adjacent(seq)))
    print(f"V==0 rows with turn>0 (in-game class): "
          f"{sorted({(s, t) for s, t in v0_turns})[:40]}")

    print("\n=== ALL V-CHANGE BOUNDARIES ===")
    print("cols: ses pturn->turn pV->V wall | changed features (name: p->c)")
    for r in vchg:
        ds = " ".join(f"{n}:{a}->{b}" for n, a, b in r["d"])
        print(f"S{r['ses']:02d} t{r['pturn']}->{r['turn']} "
              f"V{r['pV']}->{r['V']} {r['wall']} "
              f"{'SAMEFILE' if r['pfn'] == r['fn'] else 'FILE ' + r['fn']} | {ds}")

    print("\n=== CANDIDICIDE TABLE ===")
    print("feat | vchg_boundaries_changed/%d | stable_turnb_changed/%d | "
          "DISCRIMINATES" % (len(vchg), stable_turnb))
    survivors = []
    for i, name in enumerate(FEAT_NAMES[1:], start=1):
        vchanged = sum(1 for r in vchg
                       if any(n == name for n, a, b in r["d"]))
        sch = stable_cnt[i]
        ok = (vchanged == len(vchg)) and (sch == 0) and len(vchg) > 0
        if ok:
            survivors.append(name)
        print(f"{name:14s} | {vchanged:3d} | {sch:5d} | {'YES' if ok else 'no'}")
    print("SURVIVORS:", survivors or "NONE")

    print("\n=== FIRST NON-ZERO V ROW AFTER EACH V==0 STRETCH ===")
    for s, t, w, vec in first_after_zero:
        print(f"S{s:02d} t{t} {w} " + " ".join(
            f"{n}={v}" for n, v in zip(FEAT_NAMES, vec)))

    print("\n=== LINEAGE ROWS (turns 1086/1087/1254/1255) ===")
    for (s, t, V), c in sorted(lineage_agg.items()):
        print(f"S{s:02d} t{t} V={V} rows={c}")


if __name__ == "__main__":
    main()
