#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t261 witness harvest on the DRIVE corpus (production session 2026-11-01
21:24-21:38, turns 1086->1111), with the two bugs that poisoned earlier passes
fixed:
  (1) r1_t251_mine.window_rows wall-slice off-by-one (quote char included) —
      silently returned ZERO rows since t251 (fixed at source, this script
      re-implements the same law explicitly).
  (2) wall-clock windows collide across DAYS (wall is HH:MM:SS only, corpus
      spans Oct 29->Nov 1): this script seeks by byte offset to the tail
      region instead of trusting a global wall filter, and dedups by
      (file, file_mtime_ns) (orphan-watcher law t259).

Witness (a) [OQ-016 clamp]: multi-volley change vs NON-at-war owner via
r1_t251_mine.mine_stream. The session-boundary pair (t1111 -> t1255 jump when
the campaign exited to the title menu) is DROPPED — cross-campaign pairs are
artifacts, not witnesses.
Witness (b) [OQ-021 S6/P7]: V>1 AND byte[star+0x15]!=0 per banked slot, with
the per-turn star-membership table.

usage: r261_harvest.py  (paths hardcoded to this corpus; output -> stdout)
"""
import glob, json, os, struct, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r1_t251_mine as M
import r1_slot as S

ROOT = os.path.dirname(HERE)
JSONL = os.path.join(ROOT, "work/r1/playcap/live-timeline.jsonl")
BANKS = ["work/r1/bank-t261-final-1096", "work/r1/bank-t261-t1255"]
TAIL_BYTES = 12_000_000          # bounded tail region (OOM law)
LO_WALL, HI_WALL = "21:24:00", "21:38:10"   # HI ends BEFORE the title-exit jump


def drive_rows():
    """Full-file BUFFERED scan (memory-bounded per line; the 400KB/12MB tail
    covers only minutes at ~180 MB/day write rate). Cross-day wall collisions
    are removed by the (file, mtime_ns) dedup + the turn-range gate: the only
    session whose slots carry turns 1086-1111 AT walls 21:24-21:38 is today's
    drive (yesterday's same-clock rows carry turns <=1255 AND different
    mtimes; dedup keeps first-seen, so we gate on wall AND require the row's
    own mtime_ns to fall inside today's drive epoch)."""
    seen, rows = set(), []
    import time as _T
    drive_lo_ns = int(_T.mktime(_T.strptime("2026-11-01 21:24:00", "%Y-%m-%d %H:%M:%S")) * 1e9)
    with open(JSONL, "r", errors="replace") as f:
        for line in f:
            i = line.find('"wall": "')
            if i < 0:
                continue
            w = line[i + 9:i + 17]         # +9: skip the opening quote (bugfix)
            if not (LO_WALL <= w <= HI_WALL):
                continue
            try:
                j = json.loads(line)
            except Exception:
                continue
            mt = j.get("file_mtime_ns") or 0
            if mt < drive_lo_ns:
                continue                   # yesterday's same-clock rows
            key = (j.get("file"), mt)
            if key in seen:
                continue
            seen.add(key)
            if j.get("in_game") and 1086 <= j.get("turn", 0) <= 1111:
                rows.append(j)
    rows.sort(key=lambda r: (r.get("file_mtime_ns"), r.get("wall")))
    return rows


def witness_b():
    pay = S.load_payload(ROOT)
    anch = S.anchors_cached(ROOT, pay)
    out = []
    for d in BANKS:
        for sp in sorted(glob.glob(os.path.join(ROOT, d, "*.sav"))):
            try:
                mem = zipfile.ZipFile(sp).read("Memory")
            except Exception:
                continue
            B = S.base_of(mem, anch)
            if B is None:
                del mem
                continue
            t = struct.unpack_from("<I", mem, B + S.OFF + 0x12e10)[0]
            v = struct.unpack_from("<I", mem, B + S.OFF + 0x482fb)[0]
            stars = []
            for k in range(50):
                p = B + S.OFF + 0x13BC5 + k * 0x30 + 0x15
                if p + 1 <= len(mem) and mem[p]:
                    stars.append(k)
            out.append(dict(file=os.path.relpath(sp, ROOT), turn=t, V=v,
                            stars15=stars))
            del mem
    return out


def main():
    rows = drive_rows()
    print(f"drive corpus: {len(rows)} deduped rows, "
          f"turns {rows[0]['turn']}->{rows[-1]['turn']}, "
          f"wall {rows[0]['wall']}..{rows[-1]['wall']}")
    n, hits, shits = M.mine_stream(iter(rows), "drive1086-1111", strict=True)
    print(f"witness(a): stream points={n} non-war change-hits={len(hits)} "
          f"strict(engagement-scale)={len(shits)}")
    by = {}
    for h in hits:
        k = (h["att_name"], h["vic_name"], h["rel"])
        e = by.setdefault(k, dict(n=0, max_streak=0, dead=0, walls=[]))
        e["n"] += 1
        e["max_streak"] = max(e["max_streak"], h["streak"])
        e["dead"] += 1 if h["dead"] else 0
        e["walls"] = (e["walls"] + [h["wall"]])[-3:]
    for k, e in sorted(by.items(), key=lambda x: -x[1]["max_streak"]):
        print(f"  {k[0]} vs {k[1]} rel={k[2]}: hits={e['n']} "
              f"max_streak={e['max_streak']} destruction={e['dead']} last={e['walls']}")
    json.dump(hits, open(os.path.join(ROOT, "work/r1/t261_witness_a_hits.json"), "w"),
              indent=1)

    print("witness(b): per-slot V and +0x15 star set (banks at 1090-1096, 1111)")
    tab = {}
    for r in witness_b():
        tab.setdefault(r["turn"], []).append(r)
        print(f"  {r['file']} t={r['turn']} V={r['V']} stars15={r['stars15']}")
    print("per-turn star-set changes:")
    prev = None
    for t in sorted(tab):
        s = sorted(set(tab[t][0]["stars15"]))
        if s != prev:
            print(f"  t={t}: stars15={s}")
            prev = s


if __name__ == "__main__":
    sys.exit(main())
