#!/usr/bin/env python3
"""t85g: adjudicate the t1253/1254 sitting (OQ-010/021/023 evidence).

Events this sitting must explain: alliance proposal #2 to Orfa, war
declaration on Ungooma, one Ungooma fleet destroyed with return fire.
Outputs (small, to stdout):
  1. full 4x4 relation diff across the t1253->t1254 boundary (states+atts)
  2. ship presence events t>=1240 (appear/vanish/owner-change per owner)
  3. DAMAGE HUNT: per-offset u16 diffs of ship_raw between consecutive
     rows *within* a turn (mid-turn autosaves) for t>=1240, vs baseline
     window t1100..1239. Offsets that move ONLY in the battle window are
     damage-application candidates for OQ-010.
"""
import sys
sys.path.insert(0, "/home/hrethric/projects/ascendancy/scripts")
import r1_stream

# t152: RUN was hard-coded to the SHARED accumulating dir (the one
# scripts/r1_playcap_vnc.sh writes). scripts/r1_playcap.sh instead writes a
# PER-RUN dir work/r1/playcap-<ts>/ with its own watcher and its own
# live-timeline.jsonl, so adjudicating a playcap.sh capture with the old
# constant silently replayed the stale shared sitting (t1253/1254) as if it
# were the user's new game — the same silent-wrong-input shape as the 0x88
# pointer-law trap. Default keeps back-compat; a sitting adjudication MUST
# pass the capture dir the trigger named.
DEFAULT_RUN = "/home/hrethric/projects/ascendancy/work/r1/playcap"
RUN = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_RUN

prev_rel = None          # first-row matrix of previous turn
first_at = {}            # turn -> (states, atts) first row
ship_events = []
present = {}
# offset-diff census: owner -> offset -> count  (battle window vs baseline)
battle_diffs = {}
base_diffs = {}
n_rows = 0
prev_raw = None          # (turn, {slot: [177 u16]})
prev_owner = None

for j in r1_stream.observations(RUN, trust=True, stats={}):
    t = j["turn"]
    rel = j.get("relation") or None
    raw = j.get("ship_raw") or None
    ships = j.get("ships") or []
    owners = {s["slot"]: s["owner"] for s in ships}

    # -- 1. turn-boundary matrix diff -------------------------------------
    if rel and t not in first_at:
        first_at[t] = (rel["states"], rel["atts"], rel["names"])
        if prev_rel is not None and t == prev_rel[0] + 1 and \
           rel["names"] == prev_rel[2]:
            ps, pa = prev_rel[1], prev_rel[2 - 1]   # states, atts of prev
            print(f"\n== FULL relation diff {t-1} -> {t} ==")
            nm = rel["names"]
            for i in range(len(nm)):
                for k in range(len(nm)):
                    if i == k:
                        continue
                    so, ok = ps[i][k], rel["states"][i][k]
                    ao, ak = pa[i][k], rel["atts"][i][k]
                    flag = ""
                    if so != ok:
                        flag += f"  STATE {so}->{ok}"
                    if abs(ak - ao) >= 10:
                        flag += f"  att {ao}->{ak}"
                    if flag:
                        print(f"  {nm[i]:>10s} -> {nm[k]:<10s}{flag}")
        prev_rel = (t, rel["states"], rel["atts"], rel["names"])

    # -- 2. ship presence events -------------------------------------------
    cur = {}
    for s in ships:
        has = (s["state"] != 0) or any(abs(c) > 1e-6 for c in s["xyz"])
        if has:
            cur[s["slot"]] = (s["owner"], s["state"])
    for sl, v in cur.items():
        old = present.get(sl)
        if old is None:
            if t >= 1240:
                ship_events.append((t, sl, "appear", f"owner={v[0]} state={v[1]}"))
        elif old[0] != v[0]:
            ship_events.append((t, sl, "owner-change", f"{old} -> owner={v[0]}"))
    for sl, old in present.items():
        if sl not in cur:
            if t >= 1240:
                ship_events.append((t, sl, "vanish", f"was owner={old[0]} state={old[1]}"))
    present = cur

    # -- 3. intra-turn ship_raw offset diffs --------------------------------
    if raw and t >= 1100:
        bucket = battle_diffs if t >= 1240 else base_diffs
        if prev_raw is not None and prev_raw[0] == t:   # SAME turn -> mid-turn frame
            for slot, w in raw.items():
                pw = prev_raw[1].get(slot)
                if pw is None or len(pw) != len(w):
                    continue
                own = owners.get(int(slot), prev_owner.get(int(slot)) if prev_owner else None)
                for k in range(len(w)):
                    if w[k] != pw[k]:
                        d = bucket.setdefault(own if own is not None else -1, {})
                        d[k] = d.get(k, 0) + 1
        prev_raw = (t, raw)
        prev_owner = owners
    n_rows += 1

print(f"\ntrusted turn-change rows: {n_rows} (from {RUN})")
print("\n== relation first-row snapshots t>=1250 ==")
for t in sorted(first_at):
    if t >= 1250:
        st, at, nm = first_at[t]
        print(f" t={t} states0={[st[0]]} states2={[st[2]]}")
        print(f"      att0={[at[0]]} att1={[at[1]]} att2={[at[2]]}")

print(f"\n== ship presence events t>=1240 ({len(ship_events)}) ==")
for e in ship_events[:80]:
    print("  t=%-5d slot=%-3d %-13s %s" % e)

def show(bucket, label):
    print(f"\n== mid-turn ship_raw offset diffs: {label} ==")
    for own in sorted(bucket):
        offs = sorted(bucket[own].items(), key=lambda x: -x[1])[:12]
        print(f"  owner={own}: " + ", ".join(f"+0x{2*off:x}(x{c})" for off, c in offs))
show(base_diffs, "baseline t1100..1239")
show(battle_diffs, "sitting t>=1240")
