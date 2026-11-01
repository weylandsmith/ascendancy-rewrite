#!/usr/bin/env python3
"""t253 live screen-sweep primitive: click (optional) + screenshot + pixel-diff
+ ring turn check, one atomic step per screen.

Laws inherited (selfplay.md S4/S6, r1_t250_turndrive.py):
- windows.txt rects are EXACT and their coords == WINDOW-relative coords
  (NEXTTURN 474,52-548,82 center 511,67 fires turn advance, ring-verified).
- Background shells need DISPLAY=:9 injected explicitly.
- Popups swallow all input; Escape closes research/building popups (S4) but
  NOT construction popups (S6: OK click at label-row TOP minus ~3).
- Ring autosave every 10 s is the authoritative turn counter; tail-scan only
  (timeline is multi-GB; OOM law).
Safety: this script NEVER clicks NEXTTURN and never saves. Turn drift is
MEASURED after every step (ring max-turn vs baseline) and reported loudly.

usage:
  r1_t252_screen.py step NAME [X Y]   # optional window-rel click, then shot
  r1_t252_screen.py key NAME KEY      # send one key (e.g. Escape), then shot
  r1_t252_screen.py shot NAME         # screenshot only
Screens land in work/screens/t253/NAME.png (root, 1920-wide?) plus NAME_game.png
cropped to the 640x480 game area. Prints diff-pixel count vs previous shot of
the same session and current ring max turn.
"""
import json, os, os.path as P, subprocess, sys, time

ROOT = P.dirname(P.dirname(P.abspath(__file__)))
JSONL = P.join(ROOT, "work/r1/playcap/live-timeline.jsonl")
XSEND = P.join(ROOT, "tools/xsend")
OUT = P.join(ROOT, "work/screens/t253")
XOFF, YOFF = 80, 100            # dosbox window origin on root (t250 law)
STATE = P.join(OUT, "_state.json")


def sh(cmd):
    env = dict(os.environ, DISPLAY=":9")
    return subprocess.run(cmd, shell=True, capture_output=True, timeout=90, env=env)


def ring_rows(n_bytes=200000):
    out = sh(f"tail -c {n_bytes} {JSONL}").stdout.decode(errors="replace")
    rows = []
    for line in out.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def ring_state():
    best = None
    ig = None
    for d in ring_rows():
        t = d.get("turn")
        if isinstance(t, int) and (best is None or t > best):
            best = t
        ig = d.get("in_game")
    return best, ig


def load_state():
    if P.exists(STATE):
        with open(STATE) as f:
            return json.load(f)
    return {"baseline_turn": None, "prev": None, "steps": []}


def save_state(s):
    with open(STATE, "w") as f:
        json.dump(s, f, indent=1)


def grab(path):
    r = sh(f"DISPLAY=:9 import -window root {path}")
    if r.returncode != 0:
        sys.exit(f"import failed: {r.stderr.decode()[:200]}")
    from PIL import Image
    return Image.open(path).convert("RGB")


def click(x, y):
    env = dict(os.environ, DISPLAY=":9")
    subprocess.run([XSEND, "DOSBox-X", "click", str(x), str(y)],
                   capture_output=True, timeout=20, env=env)


def key(k):
    env = dict(os.environ, DISPLAY=":9")
    subprocess.run([XSEND, "DOSBox-X", "key", k],
                   capture_output=True, timeout=20, env=env)


def diff_pixels(a, b):
    if a is None or b is None or a.size != b.size:
        return -1
    from PIL import ImageChops
    import numpy as np
    d = np.asarray(ImageChops.difference(a, b))
    return int((d.max(axis=2) > 12).sum())


def main():
    os.makedirs(OUT, exist_ok=True)
    if not P.exists(XSEND):
        sys.exit("tools/xsend missing")
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    mode, name = args[0], args[1]
    st = load_state()
    t0, ig0 = ring_state()
    if st["baseline_turn"] is None:
        st["baseline_turn"] = t0

    if mode == "shot":
        pass
    elif mode == "step":
        x, y = int(args[2]), int(args[3])
        click(x, y)
        time.sleep(1.2)
    elif mode == "key":
        key(args[2])
        time.sleep(1.0)
    else:
        sys.exit(f"unknown mode {mode}")

    tmp = P.join(OUT, "_grab.png")
    img = grab(tmp)
    from PIL import Image
    crop = img.crop((XOFF, YOFF, XOFF + 640, YOFF + 480))
    root_p = P.join(OUT, f"{name}.png")
    game_p = P.join(OUT, f"{name}_game.png")
    img.save(root_p)
    crop.save(game_p)

    prev = None
    if st["prev"] and P.exists(st["prev"]):
        prev = Image.open(st["prev"]).convert("RGB")
    dpx = diff_pixels(prev, crop)
    t1, ig = ring_state()
    drift = (t1 is not None and st["baseline_turn"] is not None
             and t1 != st["baseline_turn"])
    st["prev"] = game_p
    st["steps"].append({"name": name, "mode": mode,
                        "args": args[2:], "diff_vs_prev": dpx,
                        "ring_turn": t1, "in_game": ig})
    save_state(st)
    print(f"step={name} mode={mode} args={args[2:]} diff_vs_prev={dpx} "
          f"ring_turn={t1} baseline={st['baseline_turn']} in_game={ig} "
          f"TURN_DRIFT={'YES' if drift else 'no'}")
    print(f"saved {root_p} + {game_p}")


if __name__ == "__main__":
    main()
