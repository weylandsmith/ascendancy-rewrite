#!/usr/bin/env python3
"""r258_probe.py — format/format-only probe for the t258 OQ-021 discriminator.

Answers, cheaply and BEFORE the main single-pass pass:
  1. where "score_stars" sits in a line (head-window safety for V!=0 rows);
  2. whether V==0 rows exist and whether their header fits a head window
     (the fit-exclusion set must not be silently under-counted);
  3. line-length stats (cost model for the main pass);
  4. whether the live session has advanced (new turns past t1255) and whether
     any V>=25 row / selector arm appeared (would change the task).
STREAMING ONLY (t251 OOM law): readline + fixed slices, never json.loads of
the file, never buffering rows.
"""
import sys, os
JSONL = sys.argv[1] if len(sys.argv) > 1 else "work/r1/playcap/live-timeline.jsonl"

def gi(s, key, frm=0):
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

n = 0
npos = {}
zero_rows = 0
zero_lens = []
zero_pos = {}
lenmin, lenmax = 10**9, 0
lensum = 0
max_turn = 0
hi_v = []
sel_pos = None
first_zero_example = None
with open(JSONL, "r", errors="replace") as f:
    while True:
        line = f.readline()
        if not line:
            break
        n += 1
        L = len(line)
        lenmin = min(lenmin, L)
        lenmax = max(lenmax, L)
        lensum += L
        i = line.find('"score_stars"')
        if i >= 0:
            bucket = i // 100 * 100
            npos[bucket] = npos.get(bucket, 0) + 1
            v = gi(line, '"score_stars": ')
            if v == 0:
                zero_rows += 1
                zero_lens.append(L)
                zb = i // 100 * 100
                zero_pos[zb] = zero_pos.get(zb, 0) + 1
                if first_zero_example is None:
                    first_zero_example = line
            elif v and v >= 25 and len(hi_v) < 20:
                hi_v.append((n, gi(line[:600], '"turn": '), v))
        if sel_pos is None:
            k = line.find('"selector_byte"')
            if k >= 0:
                sel_pos = k
        t = gi(line[:600], '"turn": ')
        if t:
            max_turn = max(max_turn, t)

print(f"lines={n} bytes={lensum} lenmin={lenmin} lenmax={lenmax} len_avg={lensum//max(n,1)}")
print("score_stars offset buckets (100B):", sorted(npos.items()))
print(f"V==0 rows={zero_rows} offset buckets={sorted(zero_pos.items())}")
if zero_lens:
    print(f"V==0 line lens: min={min(zero_lens)} max={max(zero_lens)} n={len(zero_lens)}")
print("selector_byte first offset:", sel_pos)
print("max turn seen:", max_turn)
print("V>=25 rows:", hi_v)
if first_zero_example:
    print("--- first V==0 row head 400 ---")
    print(first_zero_example[:400])
    print("--- first V==0 row tail 300 ---")
    print(first_zero_example[-300:])
