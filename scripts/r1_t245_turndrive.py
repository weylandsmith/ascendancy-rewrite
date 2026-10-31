#!/usr/bin/env python3
"""t245 turn-driver v3: advance turns on the live headless game, verified
against the watcher ring (authoritative).

Laws encoded (all measured t244/t245):
- Ring autosave every 10 s is the authoritative turn counter; the journal is
  multi-GB so ONLY a tail-scan is allowed.
- windows.txt is exact: NEXTTURN rect 474,52-548,82 (game coords == window
  coords here; the dosbox window is 640x480 at root +80+100, so window-rel =
  game coords; xsend takes WINDOW-relative).
- Turn-end event popups SERIALIZE: while ANY popup is open, NEXTTURN clicks
  are swallowed (verified: 6 presses, zero advancement).
- Construction popups: Escape does NOT close them (research/building popups
  do); they need their OK button clicked.
- The popup box is DARK with cyan trim; detect by WHITE-TEXT pixel count in
  the popup band, not grey runs. OK button center = rightmost white-text
  label cluster of the lowest text row, +~6px below baseline (clicking the
  text baseline itself MISSES — t245 incident: y=455 failed, y=443 worked...
  detector uses ybot+6 which sits inside the button for both layouts).
- After a successful press, AI processing takes ~10-20 s before the ring
  banks the new turn AND before queued popups appear: drain again after.

usage: r1_t245_turndrive.py [--target N] [--max-presses M]
Exit 0 when ring turn >= target.
"""
import subprocess, sys, time
from PIL import Image

JSONL = "work/r1/playcap/live-timeline.jsonl"
XOFF, YOFF = 80, 100   # dosbox window origin on root
NEXTTURN = (511, 67)   # windows.txt rect center, window-relative

def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, timeout=40)

def ring_turn():
    out = sh(f"tail -c 400000 {JSONL}").stdout.decode(errors="replace")
    best = None
    for line in out.splitlines():
        i = line.find('"turn": ')
        if i < 0: continue
        try: t = int(line[i+8:].split(",")[0])
        except ValueError: continue
        if best is None or t > best: best = t
    return best

def grab(path="/tmp/_drv.png"):
    r = sh(f"DISPLAY=:9 import -window root {path}")
    return Image.open(path).convert("RGB") if r.returncode == 0 else None

def popup_ok_center(im):
    """None if no popup; else root (x,y) of the OK hit-target.

    t245 MEASURED LAW: the drawn button art spans y 430..470 (navy edge runs)
    but the engine's HIT RECT hugs the top of the label row: y=443 works,
    y=455 and y=460 (baseline / baseline+6) MISS. Aim: label-row top minus 3.
    """
    px = im.load()
    rows = {}
    for y in range(330, 470):
        xs = [x for x in range(170, 486)
              if px[x, y][0] > 190 and px[x, y][1] > 190 and px[x, y][2] > 190]
        if len(xs) > 8: rows[y] = xs
    if sum(len(v) for v in rows.values()) < 120:
        return None
    ybot = max(rows)
    groups = []
    for x in sorted(set(rows[ybot])):
        if groups and x - groups[-1][-1] <= 8: groups[-1].append(x)
        else: groups.append([x])
    ok = groups[-1]
    # top of the bottom label row (labels are ~10px tall)
    ytop = min(y for y in rows if y >= ybot - 12)
    return (sum(ok)//len(ok), ytop - 3)

def send(args):
    subprocess.run(["./tools/xsend", "DOSBox-X"] + args, capture_output=True, timeout=20)

def drain_popups(maxn=25):
    closed = 0
    for _ in range(maxn):
        im = grab()
        if im is None: break
        c = popup_ok_center(im)
        if c is None: return closed
        send(["click", str(c[0] - XOFF), str(c[1] - YOFF)])
        closed += 1
        time.sleep(2.5)
    return closed

def main():
    target, presses = 1092, 10
    a = sys.argv[1:]
    for i, x in enumerate(a):
        if x == "--target": target = int(a[i+1])
        if x == "--max-presses": presses = int(a[i+1])
    drain_popups()
    start = ring_turn()
    print(f"ring turn at start: {start}; target {target}", flush=True)
    if start is None:
        print("RING UNREADABLE - abort", flush=True); return 1
    cur = start
    n = 0
    while n < presses and cur < target:
        n += 1
        send(["click", str(NEXTTURN[0]), str(NEXTTURN[1])])
        # poll ring up to 60 s for advancement (AI processing ~10-20 s)
        moved = False
        for _ in range(12):
            time.sleep(5)
            t = ring_turn()
            if t is not None and t > cur:
                cur = t; moved = True; break
        print(f"press {n}: ring turn {cur}{' (moved)' if moved else ' (STUCK)'}", flush=True)
        c2 = drain_popups()
        if c2: print(f"  drained {c2} popup(s)", flush=True)
    ok = cur >= target
    grab("work/screens/t2/drive_final.png")
    print(("TARGET REACHED" if ok else "BUDGET EXHAUSTED") + f" at ring turn {cur}", flush=True)
    return 0 if ok else 2

if __name__ == "__main__":
    sys.exit(main())
