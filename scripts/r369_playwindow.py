#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t369 — PLAY-WINDOW LOCATOR (phase 8, playtest 2026-11-10 evening).

Finds the bounds of the USER'S play session over the production capture:
  Signal A (disk): work/r1/game/RESUME.GAM or any work/r1/game/*.SAV with
    mtime after its recorded baseline (baselines below mirror
    docs/re/_wip_playtest_t369.md 'SESSION FACTS'; the day-1300 save is
    expected to arrive as a NEW .SAV file and/or touch RESUME.GAM).
  Signal B (capture): first live-timeline row whose turn != 1086
    (pre-play ring = t1086, banked work/r1/bank-t1086-preplay/).

OOM LAW: the timeline is ~9 GB — bounded tail-SEEK (start 64 MB, double to
--max-seek cap), one record parsed at a time, turn extracted by string scan
(r265 selector style), never a whole-file iteration.

Output: machine-readable WINDOW block (first/last wall, first/last
file_mtime_ns, row count, turn range) consumable by r369_magnetron_hit.py
and r369_order_diff.py via --window LO_NS HI_NS.

Exit 0 = window found. 1 = NO WINDOW YET (honest negative: user has not
played; re-run tomorrow — per the t369 queue row this KEEPS NEXT=t369).
2 = harness error.  usage: r369_playwindow.py [--max-seek BYTES]
"""
import os, sys, time, time as T

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GAME = os.path.join(ROOT, "work", "r1", "game")
JSONL = os.path.join(ROOT, "work", "r1", "playcap", "live-timeline.jsonl")

BASE_TURN = 1086  # pre-play ring turn (banked t1086, t368 check green)


def _ep(s):
    return time.mktime(time.strptime(s, "%Y-%m-%d %H:%M:%S"))


# baselines (mtime, seconds) at tool-authoring 2026-11-10; docs mirror above.
BASELINES = {
    "RESUME.GAM": _ep("2026-11-02 21:46:09") + 0.004,
    "01.SAV": _ep("2026-10-21 01:09:38"),
    "02.SAV": _ep("2026-10-26 00:03:36"),
    "03.SAV": _ep("2026-10-19 14:52:42"),
    "04.SAV": _ep("2026-10-26 08:37:12"),
}


def signal_disk():
    """Return list of (name, mtime_iso) changed vs baseline; [] = no play."""
    out = []
    if not os.path.isdir(GAME):
        return out
    for f in sorted(os.listdir(GAME)):
        if not (f == "RESUME.GAM" or (f.endswith(".SAV") and len(f) == 6)):
            continue
        mt = os.path.getmtime(os.path.join(GAME, f))
        base = BASELINES.get(f)
        if base is None or mt > base + 1.0:  # 1 s slack for fs granularity
            out.append((f, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mt))))
    return out


def scan_timeline(mtime_floor_ns, max_seek=64 * 1024 * 1024,
                  cap=2 * 1024 * 1024 * 1024):
    """Bounded tail scan. Return (first_row_with_turn!=BASE, rows_scanned,
    seek_used) or (None, rows, seek) if the whole scanned tail is BASE_TURN.
    Row fields extracted by string find (no json.loads needed for the turn).
    MTIME FLOOR MANDATORY: file_mtime_ns < floor rows are OLD DRIVE EPOCHS
    (the Nov-3 drive banked turns 1086->1236 into the same file; wall clock
    collides across days — t251/t265 selector law)."""
    if not os.path.isfile(JSONL):
        return None, -1, 0
    size = os.path.getsize(JSONL)
    seek = min(max_seek, size)
    while True:
        first = None
        rows = 0
        last = None
        with open(JSONL, "r", errors="replace") as fh:
            fpos = max(0, size - seek)
            fh.seek(fpos)
            if fpos:
                fh.readline()  # partial
            for line in fh:
                if not line.endswith("\n"):
                    continue
                i = line.find('"file_mtime_ns": ')
                if i < 0:
                    continue
                mt = int(line[i + 17:line.find(",", i)])
                if mt < mtime_floor_ns:
                    continue
                i = line.find('"turn": ')
                if i < 0:
                    continue
                j = line.find(",", i)
                try:
                    turn = int(line[i + 8:j])
                except ValueError:
                    continue
                rows += 1
                rec = (turn, line)
                last = rec
                if turn != BASE_TURN and first is None:
                    first = rec
                    break
        if first is not None:
            return first, rows, seek
        if seek >= min(cap, size):
            return None, rows, seek
        seek = min(seek * 4, cap, size)


def _field(line, key):
    i = line.find('"%s": ' % key)
    if i < 0:
        return "?"
    j = line.find(",", i)
    if key in ("wall", "file"):
        q1 = line.find('"', i + len(key) + 4)
        return line[q1 + 1:line.find('"', q1 + 1)]
    return line[i + len(key) + 4:j].strip()


def find_window(root=ROOT):
    """Importable: returns dict or None (no window). Disk signal alone (no
    capture rows yet) yields a window with lo_ns=None."""
    disk = signal_disk()
    # mtime floor = the pre-play bank time (2026-11-10 11:18), so rows from
    # the Nov-3 drive epoch (turns 1086->1236, stale echoes in the same file)
    # can never masquerade as the play window (t251 rewind caveat).
    floor = time.mktime(time.strptime("2026-11-10 11:18:00",
                                      "%Y-%m-%d %H:%M:%S")) * 1e9
    first, rows, seek = scan_timeline(int(floor))
    if first is None and not disk:
        return None
    w = {"disk_changed": disk, "rows_scanned": rows, "seek_bytes": seek}
    if first is not None:
        turn, line = first
        w.update({
            "first_turn": turn,
            "first_wall": _field(line, "wall"),
            "first_mtime_ns": int(_field(line, "file_mtime_ns")),
            "first_file": _field(line, "file"),
        })
    return w


def main():
    argv = sys.argv[1:]
    ms = 64 * 1024 * 1024
    if "--max-seek" in argv:
        ms = int(argv[argv.index("--max-seek") + 1])
    w = find_window()
    if w is None:
        print("NO WINDOW: no .SAV/RESUME.GAM mtime change and every scanned "
              f"timeline row (seek {ms} B tail) reads turn {BASE_TURN}.")
        print("VERDICT: user has not played yet. Honest negative — re-run "
              "after the playtest session; NEXT stays t369 (queue law).")
        return 1
    print("PLAY WINDOW (t369)")
    for name, iso in w["disk_changed"]:
        print(f"  disk: {name} mtime {iso} (post-baseline)")
    if w.get("first_turn") is not None:
        print(f"  capture: first turn!={BASE_TURN} row: turn={w['first_turn']} "
              f"wall={w['first_wall']} file={w['first_file']} "
              f"mtime_ns={w['first_mtime_ns']}")
        print(f"  window lo_ns={w['first_mtime_ns']} hi_ns=<EOF; pass "
              f"-1 for open end>")
    else:
        print("  capture: no non-1086 row in scanned tail "
              f"({w['rows_scanned']} rows, {w['seek_bytes']} B) — save "
              "dropped but session not yet banked mid-play?")
    print("  baselines: RESUME.GAM 2026-11-02 21:46:09.004 | ring t1086 "
          "banked work/r1/bank-t1086-preplay/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
