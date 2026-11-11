#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t287 diplomacy-corroboration step primitive (production :9, READ-ONLY).

Inherits the t268 primitive (click/key + screenshot + pixel-diff + ring turn
check) and PAIRS every step with the watcher's RAM relation row from the JSONL
tail (states matrix + i16 attitudes + th), printed COMPACT so context stays
cheap. Screens + band crops land in work/r1/t287-dip/.

t285/244/254 SAFETY LAWS (binding for this tool):
- This tool NEVER clicks NEXTTURN, NEVER clicks option rows 2+ of NEGSCREEN
  (only the driver passes explicit click coords; the SOP doc forbids
  PROPOSE/DECLARE/ABANDON), and NEVER sends Escape unless the operator has
  SCREENSHOT-VERIFIED a panel is open (bare-map Escape exits the campaign).
- Tail-scan <=200 KB of live-timeline.jsonl only (OOM law).

usage:
  r287_dipstep.py shot NAME
  r287_dipstep.py step NAME X Y
  r287_dipstep.py key  NAME KEY
  r287_dipstep.py rel              # newest relation row only, no click/shot
"""
import json, os, os.path as P, subprocess, sys, time

ROOT = P.dirname(P.dirname(P.abspath(__file__)))
JSONL = P.join(ROOT, "work/r1/playcap/live-timeline.jsonl")
XSEND = P.join(ROOT, "tools/xsend")
OUT = P.join(ROOT, "work/r1/t287-dip")
XOFF, YOFF = 80, 100
STATE = P.join(OUT, "_state.json")


def sh(cmd):
    env = dict(os.environ, DISPLAY=":9")
    return subprocess.run(cmd, shell=True, capture_output=True, timeout=90, env=env)


def rel_rows(n_bytes=200000):
    """Parse relation-bearing rows from the JSONL tail (t256b offsets law)."""
    out = sh(f"tail -c {n_bytes} {JSONL}").stdout.decode(errors="replace")
    rows = []
    for line in out.splitlines():
        if '"states": [[' not in line[600:]:
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            # truncated head line: salvage the relation object directly
            i = line.find('"states"')
            j = line.rfind('}')
            if i < 0 or j < 0:
                continue
            d = {}
            try:
                sub = line[i:j + 1]
                if not sub.rstrip().endswith("}"):
                    continue
                d = json.loads("{" + sub.rstrip().rstrip(",") + "}")
            except Exception:
                continue
        rel = d.get("relation") or (d if "states" in d else None)
        if not rel or "states" not in rel:
            continue
        rows.append({"slot": d.get("slot"), "wall": d.get("wall") or d.get("ts"),
                     "turn": d.get("turn"), "rel": rel})
    return rows


def compact(rel):
    st = rel["states"]
    n = len(st)
    out = {"n": n, "states": st}
    for k in ("atts", "atts_i16", "att", "th", "thresholds", "names", "races"):
        if k in rel:
            out[k] = rel[k]
    return out


def ring_state():
    out = sh(f"tail -c 120000 {JSONL}").stdout.decode(errors="replace")
    best = None
    ig = None
    for line in out.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
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


def main():
    os.makedirs(OUT, exist_ok=True)
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    mode = args[0]

    if mode == "rel":
        rows = rel_rows()
        if not rows:
            sys.exit("no relation rows in tail")
        r = rows[-1]
        print(f"slot={r['slot']} wall={r['wall']} turn={r['turn']}")
        print(json.dumps(compact(r["rel"])))
        return

    name = args[1]
    st = load_state()
    t0, ig0 = ring_state()
    if st["baseline_turn"] is None:
        st["baseline_turn"] = t0

    if mode == "step":
        x, y = int(args[2]), int(args[3])
        env = dict(os.environ, DISPLAY=":9")
        subprocess.run([XSEND, "DOSBox-X", "click", str(x), str(y)],
                       capture_output=True, timeout=20, env=env)
        time.sleep(1.2)
    elif mode == "key":
        env = dict(os.environ, DISPLAY=":9")
        subprocess.run([XSEND, "DOSBox-X", "key", args[2]],
                       capture_output=True, timeout=20, env=env)
        time.sleep(1.0)
    elif mode != "shot":
        sys.exit(f"unknown mode {mode}")

    wall = time.strftime("%H:%M:%S")
    tmp = P.join(OUT, "_grab.png")
    r = sh(f"DISPLAY=:9 import -window root {tmp}")
    if r.returncode != 0:
        sys.exit(f"import failed: {r.stderr.decode()[:200]}")
    from PIL import Image
    img = Image.open(tmp).convert("RGB")
    crop = img.crop((XOFF, YOFF, XOFF + 640, YOFF + 480))
    game_p = P.join(OUT, f"{name}.png")
    crop.save(game_p)
    # ALIENDIP text band + PLAYERDIP option band crops (windows.txt rects)
    crop.crop((336, 240, 633, 275)).save(P.join(OUT, f"{name}_alien.png"))
    crop.crop((336, 320, 633, 472)).save(P.join(OUT, f"{name}_player.png"))

    prev = None
    if st["prev"] and P.exists(st["prev"]):
        prev = Image.open(st["prev"]).convert("RGB")
    dpx = -1
    if prev is not None and prev.size == crop.size:
        from PIL import ImageChops, ImageStat
        d = ImageChops.difference(prev, crop)
        # numpy-free threshold count: point-wise max via darker/lighter trick
        import itertools
        pa, pb = d.convert("L").point(lambda v: 255 if v > 12 else 0), None
        dpx = sum(1 for v in pa.tobytes() if v)
    t1, ig = ring_state()
    rows = rel_rows()
    rr = rows[-1] if rows else None
    drift = (t1 is not None and st["baseline_turn"] is not None
             and t1 != st["baseline_turn"])
    st["prev"] = game_p
    st["steps"].append({"name": name, "mode": mode, "args": args[2:],
                        "wall": wall, "diff_vs_prev": dpx, "ring_turn": t1})
    with open(STATE, "w") as f:
        json.dump(st, f, indent=1)
    print(f"step={name} mode={mode} args={args[2:]} wall={wall} "
          f"diff_vs_prev={dpx} ring_turn={t1} baseline={st['baseline_turn']} "
          f"in_game={ig} TURN_DRIFT={'YES' if drift else 'no'}")
    if rr:
        print(f"RAM slot={rr['slot']} turn={rr['turn']}")
        print("RAM " + json.dumps(compact(rr["rel"])))
    print(f"saved {game_p}")


if __name__ == "__main__":
    main()
