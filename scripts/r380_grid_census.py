#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t380 — QUANTIZER REST-ON-GRID CENSUS (zero capture; banks + timeline).

Law under test (docs/re/_wip_t380.md S1c/S1d, instruction-level static):
EVERY COMMITTED galactic position store passes the triple through the
quantizer FUN_000533e0 (g = ds:0x895dc = 32): the walk body calls it
UNCONDITIONALLY and copies back only in commit mode (0x4a2d9 gate
cmp edi,1); placement 0x2202a and scatter 0x399df store via the quantizing
helper FUN_00049aa8. The lane march NEVER stores galactic +0x9e (lane-local
laneX is a different field; S22 L4 frame law).

READ-OUTS:
 1. RING/BANK REST CENSUS: every LIVE record's pos (+0x9e f32[3]) in the
    playtest banks + production ring -> fraction on the 32-grid.
    (Rest rows are by definition post-commit => law predicts 100%.)
 2. TIMELINE KIND CENSUS (bounded tail, OOM law): deduped frames classified
    by kind byte (+0x58 low byte) -> for kind-4 rows: pos on/off grid;
    for kind-5 rows: is the off-grid axis ONLY x (lane-local progress),
    with y,z galactic-ish on grid? This adjudicates the t370 reading of the
    (14,1,-224) / (28,0,-2144) / (144.7->149.3) rows.
Exit 0 always (report tool); the C++ pin asserts the laws.
"""
import json
import os
import struct
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

JSONL = os.path.join(ROOT, "work", "r1", "playcap", "live-timeline.jsonl")
GRID = 32.0


def on_grid(v):
    return v % GRID == 0.0


def bank_census(paths, label):
    import r1_slot as S
    pay = S.load_payload(ROOT)
    anch = S.anchors_cached(ROOT, pay)
    tot = 0
    off = 0
    kinds = {}
    off_kinds = {}
    on_kind5 = 0
    non_lane = []
    for f in sorted(paths):
        try:
            mem = zipfile.ZipFile(f).read("Memory")
        except Exception as e:
            print(f"{os.path.basename(f)} unzip {repr(e)[:60]}")
            continue
        B = S.base_of(mem, anch)
        if B is None or len(mem) < 0x90000:
            continue
        # ship array member index law (ships.md S59): B + 0x82bb0 + 0x3a095,
        # stride 0x162, count window separate; LIVE = owner word +0x56 != 0xffff
        arr = B + 0x82bb0 + 0x3a095
        for i in range(0x6b):
            o = arr + i * 0x162
            if o + 0xa6 > len(mem):
                break
            owner = struct.unpack_from("<H", mem, o + 0x56)[0]
            if owner == 0xFFFF:
                continue
            kind = mem[o + 0x58]
            x, y, z = struct.unpack_from("<3f", mem, o + 0x9e)
            tot += 1
            kinds[kind] = kinds.get(kind, 0) + 1
            if not (on_grid(x) and on_grid(y) and on_grid(z)):
                off += 1
                off_kinds[kind] = off_kinds.get(kind, 0) + 1
                # S22 L4 lane-local frame: y EXACTLY 0 or 1, z exact x32.
                lane_local = (y in (0.0, 1.0)) and on_grid(z)
                if not lane_local:
                    non_lane.append((os.path.basename(f), i, kind, x, y, z))
            elif kind == 5:
                on_kind5 += 1
    print(f"{label}: live rest rows {tot}, off-grid {off}"
          + (f" ({100.0*off/max(tot,1):.2f}%)" if tot else ""))
    print(f"   kinds={dict(sorted(kinds.items()))} "
          f"off-by-kind={dict(sorted(off_kinds.items()))} "
          f"on-grid-kind5={on_kind5}")
    print(f"   off-grid rows that are NOT the S22-L4 lane-local frame "
          f"(y in {{0,1}}, z on grid): {len(non_lane)}")
    for r in non_lane[:12]:
        print(f"   NON-LANE OFF {r[0]} slot{r[1]} kind{r[2]} pos=({r[3]},{r[4]},{r[5]})")
    return tot, off, non_lane


def timeline_tail(lo_ns=None, max_bytes=200_000_000):
    """Bounded tail stream of deduped frames: (kind, pos) events only.
    Trust law per r370_slot_events.stream: field file_mtime_ns, dedup on it,
    ship_raw = dict slot -> 177 u16."""
    if not os.path.exists(JSONL):
        return []
    sz = os.path.getsize(JSONL)
    out = {}
    seen = set()
    with open(JSONL, "r", errors="replace") as fh:
        fh.seek(max(0, sz - max_bytes))
        fh.readline()
        for line in fh:
            if not line.endswith("\n"):
                continue
            i = line.find('"file_mtime_ns": ')
            if i < 0:
                continue
            mt = int(line[i + 17:line.find(",", i)])
            if lo_ns is not None and mt < lo_ns:
                continue
            if mt in seen:
                continue
            seen.add(mt)
            if '"in_game": true' not in line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            raw = rec.get("ship_raw")
            if not raw:
                continue
            for k, words in raw.items():
                if not isinstance(words, list) or len(words) < 0xa6 // 2 + 1:
                    continue
                b58 = words[0x58 // 2] & 0xFF
                x, y, z = struct.unpack_from("<3f", struct.pack(
                    "<%dH" % len(words), *words), 0x9e)
                out[(int(k), b58, x, y, z)] = True
    return sorted(out.keys())


def main():
    import glob
    banks = []
    for d in ("work/r1/bank-play-20261111", "work/r1/bank-play-20261111-late",
              "work/r1/bank-play-20261111-t371", "work/r1/bank-play-20261111-t372",
              "work/r1/bank-play-20261111-t377"):
        p = os.path.join(ROOT, d)
        if os.path.isdir(p):
            banks += glob.glob(p + "/*.sav")
    if banks:
        bank_census(banks, f"BANKS ({len(banks)} saves)")
    else:
        print("BANKS: absent (public clone shape)")
    ring = glob.glob(os.path.join(ROOT, "work/r1/playcap/save/*.sav"))
    if ring:
        bank_census(ring[:20], f"PRODUCTION RING ({min(20,len(ring))} saves)")
    frames = timeline_tail()
    k4 = [f for f in frames if f[1] == 4]
    k5 = [f for f in frames if f[1] == 5]
    print(f"TIMELINE TAIL: frames {len(frames)} kind4={len(k4)} kind5={len(k5)}")
    for name, rows in (("kind4", k4), ("kind5", k5)):
        off_any = [r for r in rows if not (on_grid(r[2]) and on_grid(r[3]) and on_grid(r[4]))]
        off_x_only = [r for r in off_any if on_grid(r[3]) and on_grid(r[4])]
        print(f"  {name}: off-grid {len(off_any)}/{len(rows)}; "
              f"off ONLY in x (lane-local signature): {len(off_x_only)}")
        for r in off_any[:8]:
            print(f"    OFF slot{r[0]} kind{r[1]} pos=({r[2]},{r[3]},{r[4]})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
