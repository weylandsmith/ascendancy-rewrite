#!/usr/bin/env python3
"""t187: adjudicate the LIVE sitting delta (turns >= T0) for the three
capture-gated rows, in one streaming pass with small output.

  OQ-023: any relation cell holding 3 (Alliance) -> CLOSING measurement
  OQ-021: DAT_482fb/T trajectory (percent control) + selector_byte arming
  OQ-010/019: ship state census + mid-turn raw diffs in the new window
Usage: r1_t187_delta.py <run_dir> <T0>
"""
import sys, collections
sys.path.insert(0, "/home/hrethric/projects/ascendancy/scripts")
import r1_stream

RUN = sys.argv[1]
T0 = int(sys.argv[2])
st3 = []                     # (turn, i, j, names)
sel_armed = []
star_series = collections.OrderedDict()   # turn -> (stars, T)
state_census = collections.Counter()
owner_state = collections.defaultdict(collections.Counter)
offgrid = collections.Counter()
pos_track = {}               # (slot) -> list of (turn, xyz) sampled
big_move = []                # (turn, slot, owner, dxy) per-turn displacement
prev_pos = {}
n = 0
prev_raw = None
raw_diffs = collections.defaultdict(collections.Counter)
stat = {}

for j in r1_stream.observations(RUN, trust=True, stats=stat):
    t = j["turn"]
    if t < T0:
        prev_raw = None
        prev_pos = {}
        continue
    n += 1
    rel = j.get("relation")
    if rel:
        nm = rel["names"]
        for i, row in enumerate(rel["states"]):
            for k, v in enumerate(row):
                if i != k and v == 3:
                    st3.append((t, nm[i], nm[k]))
    sel = j.get("selector_byte")
    if sel:
        sel_armed.append((t, sel))
    sc, T = j.get("score_stars"), j.get("T")
    if sc is not None and T:
        star_series[t] = (sc, T)
    owners = {int(s["slot"]): s["owner"] for s in (j.get("ships") or [])}
    cur_pos = {}
    for s in (j.get("ships") or []):
        sl = int(s["slot"])
        state_census[s["state"]] += 1
        owner_state[s["owner"]][s["state"]] += 1
        x, y, z = (list(s["xyz"]) + [0, 0, 0])[:3]
        cur_pos[sl] = (x, y, z)
        if abs(x - round(x / 32.0) * 32.0) > 1e-3 or abs(y - round(y/32.0)*32.0) > 1e-3:
            offgrid[sl] += 1
    for sl, p in cur_pos.items():
        pp = prev_pos.get(sl)
        if pp is not None:
            dx = p[0]-pp[0]; dy = p[1]-pp[1]
            if abs(dx) > 1e-3 or abs(dy) > 1e-3:
                big_move.append((t, sl, owners.get(sl), round(dx,2), round(dy,2), round(p[2],2)))
    prev_pos = cur_pos
    raw = j.get("ship_raw")
    if raw:
        if prev_raw is not None and prev_raw[0] == t:
            for slot, w in raw.items():
                pw = prev_raw[1].get(slot)
                if pw is None or len(pw) != len(w):
                    continue
                own = owners.get(int(slot), -1)
                for k in range(len(w)):
                    if w[k] != pw[k]:
                        raw_diffs[own][k] += 1
        prev_raw = (t, raw)

print(f"new-window trusted rows: {n} (t>={T0}) from {RUN}")
print("stream:", r1_stream.echo_note(stat))
print(f"\n== OQ-023 relation cells holding 3: {len(st3)} ==")
for e in st3[:20]:
    print("   t=%s %s -> %s = 3" % e)
print(f"\n== OQ-021 selector_byte armed rows: {len(sel_armed)} ==")
for e in sel_armed[:10]:
    print("   ", e)
print("   star series (turn: stars/T): " + ", ".join(f"{t}:{v[0]}/{v[1]}" for t, v in list(star_series.items())[-40:]))
print("   max stars seen:", max((v[0] for v in star_series.values()), default=None))
print("\n== ship state census (new window) ==")
for s, c in sorted(state_census.items()):
    print(f"   state={s}: x{c}")
print("   per-owner: " + "; ".join(f"o{o}={dict(sorted(c.items()))}" for o, c in sorted(owner_state.items())))
print(f"\n== off-32-grid slots (mid-transit candidates): {len(offgrid)} ==")
print("   " + ", ".join(f"{s}x{c}" for s, c in sorted(offgrid.items())[:30]))
print(f"\n== per-row position displacements: {len(big_move)} ==")
for e in big_move[:40]:
    print("   t=%s slot=%s owner=%s d=(%s,%s) z=%s" % e)
print("\n== mid-turn ship_raw u16 offsets that moved (new window) ==")
for own in sorted(raw_diffs):
    top = sorted(raw_diffs[own].items(), key=lambda x: -x[1])[:14]
    print(f"   owner={own}: " + ", ".join(f"+0x{2*k:x}(x{c})" for k, c in top))
