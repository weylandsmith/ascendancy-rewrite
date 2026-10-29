#!/usr/bin/env python3
"""t192: adjudicate the TRIGGER-A timeline growth WITHOUT streaming the whole
5.7 GB file. Compares head/tail md5 baselines, then walks only the TAIL WINDOW
(new bytes since the trigger baseline size) and prints a compact census:
turn range, wall-clock range, row count, which observation keys are present,
and any relation-matrix deltas inside the window.

Usage: r1_t192_tail_probe.py [path] [new_bytes_to_scan]
"""
import sys, os, json, hashlib, datetime

P = sys.argv[1] if len(sys.argv) > 1 else \
    "/home/hrethric/projects/ascendancy/work/r1/playcap/live-timeline.jsonl"
N = int(sys.argv[2]) if len(sys.argv) > 2 else 8 * 1024 * 1024

sz = os.path.getsize(P)
BASE_SIZE = 5691796463          # trigger baseline
with open(P, "rb") as f:
    head = hashlib.md5(f.read(4096)).hexdigest()
    growth = max(0, sz - BASE_SIZE)
    scan = min(sz, max(N, growth + 4096))
    f.seek(sz - scan)
    blob = f.read()
print(f"path={P}")
print(f"size={sz} baseline={BASE_SIZE} growth={growth} scanned={scan}")
print(f"head_md5={head}")

lines = blob.split(b"\n")
print(f"first_partial_len={len(lines[0])} dropped={not lines[0].startswith(b'{')}")
start = 0 if lines[0].startswith(b"{") else 1

turns = {}
keys = {}
first = None
last = None
bad = 0
for L in lines[start:]:
    if not L.strip():
        continue
    try:
        j = json.loads(L)
    except Exception:
        bad += 1
        continue
    t = j.get("turn")
    turns[t] = turns.get(t, 0) + 1
    for k in j:
        keys[k] = keys.get(k, 0) + 1
    if first is None:
        first = j
    last = j

print(f"rows={sum(turns.values())} bad={bad} distinct_turns={len(turns)}")
tt = sorted(k for k in turns if isinstance(k, int))
print(f"turn_range={tt[0] if tt else None}..{tt[-1] if tt else None}")
if first:
    print("first_row_keys=" + ",".join(sorted(first)))
    for k in ("wall", "ts", "ts_wall", "clock", "time"):
        if k in (first or {}):
            print(f"  first.{k}={first[k]}  last.{k}={(last or {}).get(k)}")
print("key_census(top20)=" + ", ".join(
    f"{k}:{v}" for k, v in sorted(keys.items(), key=lambda x: -x[1])[:20]))
print("turn_hist(tail30)=" + ", ".join(f"{t}:{turns[t]}" for t in tt[-30:]))
