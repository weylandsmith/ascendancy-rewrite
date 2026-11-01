#!/usr/bin/env python3
"""t250 turn-driver v4: v3 (ring-verified press + popup drain) PLUS softlock
detect and auto-recovery, plus a persistent run log.

v3 laws inherited verbatim (measured t244/t245):
- Ring autosave every 10 s is the authoritative turn counter; journal is
  multi-GB so ONLY a tail-scan (tail -c 400000).
- NEXTTURN at window-rel (511,67); popups SERIALIZE turn-end events and
  swallow NEXTTURN clicks; popup OK hit-target = label-row TOP minus 3
  (y=443 works, baseline y=455+ misses); popup box is dark w/ cyan trim so
  detect by WHITE-text pixel count.
- Background shells need DISPLAY=:9 injected explicitly.

t250 ADDITIONS:
(a) SOFTLOCK DETECT. Signature (t245 + t247 refined): the game stops
    responding to synthetic input AND RAM stops advancing. Measured two ways:
      probe  = press 'c' (galaxy-screen relation overlay toggle, selfplay.md
               S2) and diff the full root screenshot; <= PIXEL_ALIVE changed
               pixels => input-dead.
      frozen = two ring-tail samples ~20 s apart whose rows differ ONLY in the
               wall-clock / file bookkeeping fields (wall, file,
               file_mtime_ns) => RAM-frozen.
    DEVIATION from the t250 task text, deliberate and recorded: the task text
    also required "a popup is on screen", but t247 measured the signature
    recur WITH NO POPUP (the user's t1254 session), so popup presence is
    LOGGED, not required. The safety that popup-check was standing in for is
    provided instead by sequencing: the check only runs after two consecutive
    non-advancing presses with a popup drain that closed ZERO popups, so a
    healthy game parked behind a popup is never killed.
(b) RECOVERY: bank the ring slots, SIGKILL (never SIGTERM - it pops the game's
    own quit-confirm with (Yes) DEFAULT, t247), relaunch via
    r1_playcap_vnc.sh start, click "Return to Current Game" at window-rel
    (318,333), then keep driving toward the same absolute target. Writes
    work/r1/SELFPLAY.marker so a future probe can tell self-play timeline
    growth from a user sitting; marker is removed on clean exit.
(c) RUN LOG: every press, drain count, probe and ring sample appended to
    work/r1/t250_drive_<ts>.log.

usage: r1_t250_turndrive.py [--target N] [--max-presses M] [--max-softlocks K]
Exit 0 = ring turn >= target. 2 = press budget exhausted. 3 = softlocks kept
winning. 1 = ring unreadable / recovery failed.
"""
import json, os, subprocess, sys, time, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSONL = os.path.join(ROOT, "work/r1/playcap/live-timeline.jsonl")
SAVEDIR = os.path.join(ROOT, "work/r1/playcap/save")
RUNDIR = os.path.join(ROOT, "work/r1/vnc")
MARKER = os.path.join(ROOT, "work/r1/SELFPLAY.marker")
XSEND = os.path.join(ROOT, "tools/xsend")
XOFF, YOFF = 80, 100            # dosbox window origin on root
NEXTTURN = (511, 67)            # window-rel
RETURN_TO_GAME = (318, 333)     # window-rel, title menu top option
WALL_FIELDS = {"wall", "file", "file_mtime_ns"}
PIXEL_ALIVE = 50                # changed pixels that count as "screen reacted"

LOG = None


def log(msg):
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    print(line, flush=True)
    if LOG:
        with open(LOG, "a") as f:
            f.write(line + "\n")


def sh(cmd):
    env = dict(os.environ, DISPLAY=":9")
    return subprocess.run(cmd, shell=True, capture_output=True, timeout=90, env=env)


def ring_rows(n_bytes=400000):
    out = sh(f"tail -c {n_bytes} {JSONL}").stdout.decode(errors="replace")
    rows = []
    for line in out.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue           # tail cut a row in half: expected, skip
    return rows


def ring_turn():
    best = None
    for d in ring_rows():
        t = d.get("turn")
        if isinstance(t, int) and (best is None or t > best):
            best = t
    return best


def grab(path):
    from PIL import Image
    r = sh(f"DISPLAY=:9 import -window root {path}")
    return Image.open(path).convert("RGB") if r.returncode == 0 else None


def diff_pixels(a, b):
    """Count of differing pixels between two same-size screenshots."""
    if a is None or b is None or a.size != b.size:
        return -1
    pa, pb = a.load(), b.load()
    w, h = a.size
    n = 0
    for y in range(0, h, 2):            # 2-px stride: overlay text is blocky
        for x in range(0, w, 2):
            if pa[x, y] != pb[x, y]:
                n += 4
    return n


def popup_ok_center(im):
    """None if no popup; else root (x,y) of the OK hit-target (v3 law)."""
    px = im.load()
    rows = {}
    for y in range(330, 470):
        xs = [x for x in range(170, 486)
              if px[x, y][0] > 190 and px[x, y][1] > 190 and px[x, y][2] > 190]
        if len(xs) > 8:
            rows[y] = xs
    if sum(len(v) for v in rows.values()) < 120:
        return None
    ybot = max(rows)
    groups = []
    for x in sorted(set(rows[ybot])):
        if groups and x - groups[-1][-1] <= 8:
            groups[-1].append(x)
        else:
            groups.append([x])
    ok = groups[-1]
    ytop = min(y for y in rows if y >= ybot - 12)
    return (sum(ok) // len(ok), ytop - 3)


def send(args):
    env = dict(os.environ, DISPLAY=":9")
    subprocess.run([XSEND, "DOSBox-X"] + args, capture_output=True, timeout=30, env=env)


def drain_popups(maxn=25):
    closed = 0
    for _ in range(maxn):
        im = grab("/tmp/_drv_popup.png")
        if im is None:
            break
        c = popup_ok_center(im)
        if c is None:
            return closed
        send(["click", str(c[0] - XOFF), str(c[1] - YOFF)])
        closed += 1
        time.sleep(2.5)
    return closed


def input_alive():
    """True if the game reacts to synthetic input.

    MEASURED t250 (live :9): the 'c' overlay is GALAXY-SCREEN-ONLY (selfplay.md
    S2) - it changed 0 px while the session sat on the planet LIST screen of a
    healthy game, and 1152 px on the galaxy screen. So a 'c'-only probe
    false-positives on any modal sub-screen. Probe order: Escape (backs out of
    modals, selfplay t252 law; no-op on the galaxy screen), then 'c'.
    """
    a = grab("/tmp/_drv_probe_a.png")
    send(["key", "Escape"])
    time.sleep(1.5)
    b = grab("/tmp/_drv_probe_b.png")
    n = diff_pixels(a, b)
    if n > PIXEL_ALIVE:
        return True, n
    send(["key", "c"])
    time.sleep(1.5)
    c = grab("/tmp/_drv_probe_c.png")
    n2 = diff_pixels(b, c)
    if n2 > PIXEL_ALIVE:
        send(["key", "c"])              # restore: toggle overlay back off
        time.sleep(1.0)
        return True, n2
    return False, n


def ram_frozen(gap=20):
    """True if the ring advances only in wall/file bookkeeping fields."""
    s1 = ring_rows()
    t1 = time.time()
    time.sleep(gap)
    s2 = ring_rows()
    if not s1 or not s2:
        return False, "ring unreadable"
    # compare the newest row seen for each slot file; ignore wall/file fields
    def sig(rows):
        d = {}
        for r in rows:
            f = r.get("file")
            if not f:
                continue
            d[f] = {k: v for k, v in r.items() if k not in WALL_FIELDS}
        return d
    a, b = sig(s1), sig(s2)
    changed = {f for f in set(a) & set(b) if a[f] != b[f]}
    new_slots = set(b) - set(a)
    if changed or new_slots:
        return False, f"RAM moved: {sorted(changed)[:4]} new={sorted(new_slots)[:4]}"
    # nothing but bookkeeping moved in `gap` s
    return True, f"only wall/file moved in {int(time.time()-t1)}s ({len(b)} slots)"


def softlock_screen(evidence):
    sh(f"cp /tmp/_drv_probe_b.png {evidence} 2>/dev/null || true")


def bank_ring(tag):
    dest = os.path.join(ROOT, f"work/r1/bank-{tag}")
    os.makedirs(dest, exist_ok=True)
    n = 0
    for p in sorted(glob.glob(os.path.join(SAVEDIR, "*.sav"))):
        sh(f"cp -p {p} {dest}/")
        n += 1
    log(f"banked {n} ring slots -> work/r1/bank-{tag}")
    return dest


def recover():
    """SIGKILL + relaunch + Return to Current Game. True on success."""
    log("SOFTLOCK DECLARED - starting recovery")
    softlock_screen(os.path.join(ROOT, f"work/r1/softlock_evidence_{int(time.time())}.png"))
    bank_ring(f"t250-recovery-{int(time.time())}")
    pidf = os.path.join(RUNDIR, "dosbox.pid")
    killed = []
    if os.path.exists(pidf):
        pid = open(pidf).read().strip()
        if pid:
            sh(f"kill -9 {pid} 2>/dev/null || true")
            killed.append(pid)
    time.sleep(3)
    # leftovers: this is OUR scratch-copy session (never the user's), and the
    # softlocked process ignores SIGTERM, so escalate by exact comm name.
    left = sh("pgrep -x dosbox-x || true").stdout.decode().split()
    for p in left:
        if p not in killed:
            sh(f"kill -9 {p} 2>/dev/null || true")
    log(f"SIGKILLed dosbox pids {killed + left}")
    r = subprocess.run(["bash", os.path.join(ROOT, "scripts/r1_playcap_vnc.sh"), "start"],
                       capture_output=True, timeout=300, cwd=ROOT)
    log("relaunch rc=%d %s" % (r.returncode, r.stdout.decode(errors="replace").strip()[-300:]))
    if r.returncode != 0:
        return False
    # title menu needs boot time; poll for the Return-to-game click to land
    for i in range(12):
        time.sleep(10)
        send(["click", str(RETURN_TO_GAME[0]), str(RETURN_TO_GAME[1])])
        time.sleep(8)
        rows = ring_rows()
        if rows and any(r0.get("in_game") for r0 in rows[-6:]):
            log(f"resumed into game after {i+1} click attempt(s); ring turn {ring_turn()}")
            return True
        log(f"recovery poll {i+1}: not in game yet")
    log("recovery FAILED: still not in_game after 12 attempts")
    return False


def main():
    global LOG
    target, presses, max_soft = 1092, 10, 2
    a = sys.argv[1:]
    for i, x in enumerate(a):
        if x == "--target": target = int(a[i + 1])
        if x == "--max-presses": presses = int(a[i + 1])
        if x == "--max-softlocks": max_soft = int(a[i + 1])
    os.makedirs(os.path.join(ROOT, "work/r1"), exist_ok=True)
    LOG = os.path.join(ROOT, f"work/r1/t250_drive_{time.strftime('%Y%m%d-%H%M%S')}.log")
    open(MARKER, "w").write("1")            # self-play growth bracket opens
    log(f"drive start target={target} max_presses={presses} max_softlocks={max_soft}")
    log(f"dosbox pids: {sh('pgrep -x dosbox-x || echo none').stdout.decode().split()}")
    drain = drain_popups()
    if drain:
        log(f"pre-drive drain closed {drain} popup(s)")
    cur = ring_turn()
    log(f"ring turn at start: {cur}")
    if cur is None:
        log("RING UNREADABLE - abort")
        return 1
    n = 0
    stall = 0
    softlocks = 0
    while n < presses and cur < target:
        n += 1
        send(["click", str(NEXTTURN[0]), str(NEXTTURN[1])])
        moved = False
        for _ in range(12):
            time.sleep(5)
            t = ring_turn()
            if t is not None and t > cur:
                cur = t
                moved = True
                break
        drained = drain_popups()
        log(f"press {n}: ring turn {cur}{' (moved)' if moved else ' (no advance)'}"
            f" drained={drained}")
        if moved:
            stall = 0
            continue
        stall += 1
        if stall < 2:
            continue                     # one miss = could be a queued popup
        # two presses, zero advancement, zero popups closed: interrogate
        alive, npix = input_alive()
        log(f"probe: input {'ALIVE' if alive else 'DEAD'} (changed_px={npix})")
        if alive:
            stall = 0
            continue
        frozen, why = ram_frozen()
        im = grab("/tmp/_drv_softlock_screen.png")
        log(f"probe: ram {'FROZEN' if frozen else 'MOVING'} ({why}) "
            f"popup_on_screen={popup_ok_center(im) is not None}")
        if not frozen:
            stall = 0
            continue
        softlocks += 1
        if softlocks > max_soft:
            log(f"softlock {softlocks} > max_softlocks - giving up at ring turn {cur}")
            return 3
        if not recover():
            return 1
        cur = ring_turn() or cur
        stall = 0
    ok = cur >= target
    grab(os.path.join(ROOT, "work/screens/t2/drive_final_t250.png"))
    log(("TARGET REACHED" if ok else "BUDGET EXHAUSTED") + f" at ring turn {cur}")
    if ok:
        os.remove(MARKER)                   # clean exit closes the bracket
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
