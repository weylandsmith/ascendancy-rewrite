#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t261 load-click: click Capture->Load state on the :8 restored session and
VERIFY structurally (watcher row turn==1255), not by vision.

Laws (t260, docs/re/selfplay.md t260 block):
- menu clicks via tools/xsend (synthetic BUTTON events drive the SDL2 menu);
  keys carry state=0 so the F12+L chord is NOT deliverable — clicks only.
- menu bar Capture at window-rel (315, 8); dropdown "Load state" row was
  (350, 197) on the identical layout (t260 _wip attempt 1/2).
- window IDs change per launch -> resolve by name; xsend matches by title
  substring anyway.
- verification authority = the watcher timeline row for the slot read AFTER
  the load (turn==1255), plus the dosbox.log lines "Loading state from slot:
  60" / "Loaded. (Slot 60)".

usage: r1_t261_load.py [--x X --y Y] [--expect-turn 1255]
Exit 0 verified; 1 not verified (screen+log paths printed for triage).
"""
import os, subprocess, subprocess as sp, sys, time, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "work/r1/t261-drive")
ENV = dict(os.environ, DISPLAY=":8")
XSEND = os.path.join(ROOT, "tools/xsend")

def arg(flag, default):
    a = sys.argv[1:]
    return int(a[a.index(flag) + 1]) if flag in a else default

def rows_tail(n_bytes=200000):
    out = sp.run(f"tail -c {n_bytes} {BASE}/live-timeline.jsonl",
                 shell=True, capture_output=True).stdout.decode(errors="replace")
    rows = []
    for l in out.splitlines():
        l = l.strip()
        if l.startswith("{"):
            try:
                rows.append(json.loads(l))
            except Exception:
                pass
    return rows

def main():
    x, y, expect = arg("--x", 350), arg("--y", 197), arg("--expect-turn", 1255)
    log0 = os.path.getsize(os.path.join(BASE, "run/dosbox.log")) \
        if os.path.exists(os.path.join(BASE, "run/dosbox.log")) else 0
    # open Capture menu, click the Load-state row
    sp.run([XSEND, "DOSBox-X", "key", "Escape"], env=ENV, capture_output=True)
    time.sleep(0.6)
    sp.run([XSEND, "DOSBox-X", "315", "8"], env=ENV, capture_output=True)
    time.sleep(1.2)
    sp.run([XSEND, "DOSBox-X", "click", str(x), str(y)], env=ENV, capture_output=True)
    print(f"clicked Load state at ({x},{y}); watching log + ring", flush=True)
    # poll log for the two lines (up to 90 s; a load of a ~1 MB state is fast,
    # but dosbox may re-init devices)
    loaded = False
    deadline = time.time() + 90
    while time.time() < deadline and not loaded:
        time.sleep(3)
        with open(os.path.join(BASE, "run/dosbox.log"), errors="replace") as f:
            f.seek(log0)
            tail = f.read()
        if "Loaded. (Slot 60)" in tail:
            loaded = True
            print("LOG:", [l for l in tail.splitlines() if "slot" in l.lower()][:6], flush=True)
    if not loaded:
        sp.run(["import", "-window", "root", f"{BASE}/load-fail.png"], env=ENV)
        print("NOT LOADED within 90 s; screen at work/r1/t261-drive/load-fail.png", flush=True)
        return 1
    # structural verification: a watcher row with turn==expect lands within
    # ~20 s of the load (autosave cadence 10 s, watcher 1 s scan)
    deadline = time.time() + 120
    while time.time() < deadline:
        rs = rows_tail()
        hit = [r for r in rs if r.get("turn") == expect and r.get("in_game")]
        if hit:
            r = hit[-1]
            print(f"VERIFIED row: wall={r['wall']} file={r['file']} turn={r['turn']} "
                  f"score_stars={r.get('score_stars')} systems_any={r.get('systems_any')}",
                  flush=True)
            return 0
        time.sleep(5)
    sp.run(["import", "-window", "root", f"{BASE}/load-verify-miss.png"], env=ENV)
    last = rows_tail()[-3:]
    print("loaded per log but NO turn==%d row; last rows: %s" %
          (expect, [{k: r.get(k) for k in ('wall', 'file', 'turn', 'in_game')} for r in last]),
          flush=True)
    return 1

if __name__ == "__main__":
    sys.exit(main())
