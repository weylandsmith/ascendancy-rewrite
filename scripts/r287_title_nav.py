#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t287 title-menu keyboard navigator: arrow-key highlight tracker.

Why keyboard: the title-menu row highlight is HOVER state updated by motion
events; SDL rejects synthetic MotionNotify, so a warped synthetic click fires
the STALE hovered row (MEASURED 08:40:48: click (318,333) 'Return to Current
Game' from title menu opened the TUTORIAL SELECT instead — the row the VNC
user last hovered; esc1/backgame/esc2 pixel diffs prove the transition).
Keys ARE accepted (Escape 248874 px). This tool tracks the highlight band by
luminance (separator-anchored slots), so Enter is only pressed with the screen
EVIDENCE that the highlight is on the intended row.

Slots (separators MEASURED y=233/273/313/353/393/393..473, pitch 40):
  R1 Play Introduction [~193-233]  R2 Tutorial [233-273]
  R3 New Game [273-313]            R4 Return to Current Game [313-353]
  R5 Load Game [353-393]           R6 Save Game [393-433]
  R7 Exit to DOS [433-473]

usage: nav.py status | nav.py down N | nav.py enter
'enter' REFUSES unless the highlight is on R4 (unless --force, unused here).
"""
import os, os.path as P, subprocess, sys, time

ROOT = P.dirname(P.dirname(P.abspath(__file__)))
OUT = P.join(ROOT, "work/r1/t287-dip")
XSEND = P.join(ROOT, "tools/xsend")
XOFF, YOFF = 80, 100
SEPS = [233, 273, 313, 353, 393, 433, 473]
NAMES = ["R1 PlayIntroduction", "R2 Tutorial", "R3 NewGame",
         "R4 ReturnToCurrentGame", "R5 LoadGame", "R6 SaveGame",
         "R7 ExitToDOS"]


def sh(cmd):
    env = dict(os.environ, DISPLAY=":9")
    return subprocess.run(cmd, shell=True, capture_output=True, timeout=90, env=env)


def grab(name):
    tmp = P.join(OUT, "_navgrab.png")
    r = sh(f"DISPLAY=:9 import -window root {tmp}")
    if r.returncode != 0:
        sys.exit("import failed")
    from PIL import Image
    img = Image.open(tmp).convert("RGB")
    crop = img.crop((XOFF, YOFF, XOFF + 640, YOFF + 480))
    path = P.join(OUT, f"{name}.png")
    crop.save(path)
    return crop, path


def highlight_row(img):
    """Row whose interior carries the CYAN highlight bg (16,69,74) vs dark
    (8,32,48). MEASURED nav_status.png: box interior x 160-470; the earlier
    (b>120) detector was wrong (it fired on separator rules)."""
    px = img.load()
    bands = []
    slots = [(193, 233), (233, 273), (273, 313), (313, 353),
             (353, 393), (393, 433), (433, 473)]
    for (lo, hi) in slots:
        hits = tot = 0
        for y in range(lo + 6, hi - 6, 2):
            for x in range(165, 470, 4):
                r_, g_, b_ = px[x, y]
                tot += 1
                if 10 <= r_ <= 24 and 58 <= g_ <= 80 and 62 <= b_ <= 84:
                    hits += 1
        bands.append(hits / max(tot, 1))
    best = max(range(len(bands)), key=lambda i: bands[i] or 0)
    if not bands[best] or bands[best] < 0.5:
        return None, bands
    return best, bands


def key(k):
    env = dict(os.environ, DISPLAY=":9")
    subprocess.run([XSEND, "DOSBox-X", "key", k],
                   capture_output=True, timeout=20, env=env)


def key_rfb(k):
    # keys via the RFB channel too (XTEST path; avoids xsend keysym quirks)
    subprocess.run([P.join(ROOT, "scripts", "r287_vncinput.py"), "key", k],
                   capture_output=True, timeout=20)


def status(tag):
    img, path = grab(tag)
    row, bands = highlight_row(img)
    rname = NAMES[row] if row is not None else "NONE"
    print(f"{tag} highlight={rname} bands=" +
          " ".join(f"{i}:{(b or 0):.2f}" for i, b in enumerate(bands)) +
          f" shot={path}")
    return row


def main():
    args = sys.argv[1:]
    mode = args[0] if args else "status"
    if mode == "status":
        status("nav_status")
    elif mode == "down":
        n = int(args[1]) if len(args) > 1 else 1
        for i in range(n):
            key("Down")
            time.sleep(0.8)
        status(f"nav_down{n}")
    elif mode == "enter":
        row = status("nav_pre_enter")
        if row != 3:
            sys.exit(f"REFUSED enter: highlight is {NAMES[row] if row is not None else 'NONE'}, not R4")
        key("Return")
        time.sleep(1.5)
        status("nav_post_enter")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
