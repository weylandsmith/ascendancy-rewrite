#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""tPF12_tick_census.py — MEASURE the framework tick rate DAT_000a2044 from
banked save states (zero new capture), and read the FPS-DUDE meter state.

LAW (cited):
  * POINTER LAW (OQ-011 CLOSED, docs/re/r1-savestate.md): ds-relative static D
    lives at guest LINEAR 0x242000 + D; guest linear L at Memory-member offset
    L + H (H per-run, BDA-signature derived). member(D) = 0x242000 + D + H.
  * DAT_000a2044: sole increment fn 0x53d84 (`inc [0xa2044]; ret`), sole
    u32 pointer in the image at 0x8b35c (callback table at 0x8b358), zeroed
    at run init 0x545af — monotonic WITHIN a run (docs/re/_wip_tPF12.md P2).
  * Fire-loop 0x56608 compares DAT vs [slot+0x12] (0x56666); interval-0 slots
    fire EVERY main-loop pass => the pump cadence is the loop rate, and the
    tick's job is first-fire arming + nonzero-interval slots.
  * FPS-DUDE: fn 0x55020 sprintfs 1000/(ticks per 10 calls) into the string
    buffer at ds:0x895ec ("FPS DUDE" verbatim); meter counter ds:0x7a34c,
    samples ds:0x7a350 / ds:0x7a354; counter resets to 0 after each sample
    (0x55068), so snapshot 0 is the EXPECTED resting state.

METHOD: per .sav, decode H via BDA; read tick + meter words; group saves by
directory, order by tick (ring rotation wraps), and report consecutive deltas
against file-mtime steps. EXIT 0 always (census prints).
"""
import os, struct, sys, zipfile
from collections import Counter, defaultdict

D_BASE = 0x242000
ADDrs = {"tick": 0xa2044, "meter_cnt": 0x7a34c, "meter_now": 0x7a350,
         "meter_prev": 0x7a354, "fps_str": 0x895ec}


def bda_h(mem):
    return [h for h in range(0, 0x2000)
            if struct.unpack_from("<H", mem, h + 0x413)[0] == 0x280
            and struct.unpack_from("<H", mem, h + 0x44A)[0] == 80]


def read_u32(mem, h, d):
    off = D_BASE + d + h
    return struct.unpack_from("<I", mem, off)[0] if off + 4 <= len(mem) else None


def main():
    dirs = sys.argv[1:] or ["work/r1"]
    per_dir = defaultdict(list)
    fps_hist = Counter()
    total = 0
    for d in dirs:
        for root, _, files in os.walk(d):
            for fn in sorted(files):
                if not fn.endswith(".sav"):
                    continue
                p = os.path.join(root, fn)
                try:
                    with zipfile.ZipFile(p) as z:
                        if "Memory" not in z.namelist():
                            continue
                        mem = z.read("Memory")
                except Exception:
                    continue
                hs = bda_h(mem)
                if len(hs) != 1:
                    continue
                h = hs[0]
                total += 1
                tick = read_u32(mem, h, ADDrs["tick"])
                fps_off = D_BASE + ADDrs["fps_str"] + h
                s = mem[fps_off:fps_off + 16].split(b"\x00")[0] if fps_off + 16 <= len(mem) else b""
                fps_hist[s.decode("latin1", "replace")] += 1
                per_dir[root].append((tick, os.path.getmtime(p), p))
    print("saves decoded:", total)
    for root, rows in sorted(per_dir.items()):
        if len(rows) < 4:
            continue
        deltas = []
        for i in range(1, len(rows)):
            t0, m0, _ = rows[i - 1]
            t1, m1, _ = rows[i]
            if t0 is None or t1 is None:
                continue
            dt = t1 - t0
            if dt < 0:
                continue  # ring wrap
            dtm = m1 - m0
            if 5 < dtm < 20:  # consecutive autosave slots (cadence ~10 s)
                deltas.append((dt, dtm))
        if not deltas:
            print(root, ": no consecutive-pair windows")
            continue
        n = len(deltas)
        rate = sum(dt / dtm for dt, dtm in deltas) / n
        print(f"{root}: n={n} mean {sum(dt for dt,_ in deltas)/n:.1f} ticks/"
              f"{sum(dtm for _,dtm in deltas)/n:.3f}s => {rate:.1f} ticks/s")
        print("   delta histogram:", dict(Counter(dt for dt, _ in deltas).most_common(8)))
    print("FPS-DUDE buffer contents histogram:", dict(fps_hist.most_common(6)))


main()
