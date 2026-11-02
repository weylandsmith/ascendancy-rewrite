#!/usr/bin/env python3
"""t261 turn-driver for the RESTORED-t1255 session on :8.

Inherits every t245/t250 law (ring-verified press, popup drain, OK hit-target
= label-row top minus 3, softlock = input-dead AND RAM-frozen, bank-before-kill)
with THREE t261 adaptations, each with a measured reason:

(a) DISPLAY=:8 and paths under work/r1/t261-drive. The production :9 t1086
    session keeps running untouched; per-session trust stays clean because the
    corpora are physically separate files.
(b) COORDINATE SHIFT. The GUI window (loadstate needs the menu bar) is
    640x497+80+100: game content starts at root y=117 (17 px menu bar), so the
    popup pixel band shifts +17 and NEXTTURN becomes window-rel (511, 84).
    xsend takes WINDOW-relative coords (t260: menu click (315,8) worked).
(c) RECOVERY = loadstate, NOT Return-to-Game. RESUME.GAM is the Oct-29 t1086
    save (md5 5b382afb), so the title-menu resume would drop us into a
    DIFFERENT campaign. Recovery: bank ring -> SIGKILL recorded pid -> relaunch
    via r1_t261_session.sh bringup with KEEP_SAVE=1 -> click Capture->Load
    state (reads slot 60 of the scratch ring, a same-session snapshot aged
    0..200 s; the turn loss is logged honestly).

usage: r1_t261_drive.py --target N [--max-presses M] [--max-softlocks K]
Exit 0 target reached; 2 press budget; 3 softlocks won; 1 ring/recovery failure.
"""
import glob, json, os, os.path, shutil, subprocess, sys, time, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_t250_turndrive as V4                      # pure pixel helpers only

# ENV-parameterized so ONE code path drives both sessions (periodic banking +
# final bank are the reason not to fork the driver):
#   T261_DISPLAY  :8 (restored scratch session) | :9 (production)
#   T261_BASE     evidence dir (timeline + save + run live under it)
#   T261_MENUBAR  17 for a GUI (no -nogui) window, 0 for -nogui production
#   T261_RECOVER  loadstate (scratch, loadsource slot 60) | resume (production,
#                 RESUME.GAM via title-menu Return to Current Game)
DISPLAY = os.environ.get("T261_DISPLAY", ":8")
BASE = os.environ.get("T261_BASE", os.path.join(ROOT, "work/r1/t261-drive"))
MENUBAR = int(os.environ.get("T261_MENUBAR", "17"))
RECOVER_MODE = os.environ.get("T261_RECOVER", "loadstate")
JSONL = os.path.join(BASE, "live-timeline.jsonl")
SAVEDIR = os.path.join(BASE, "save")
RUNDIR = os.path.join(BASE, "run")
XSEND = os.path.join(ROOT, "tools/xsend")
XOFF, YOFF = 80, 100            # window origin on root (measured xwininfo)
NEXTTURN = (511, 67 + MENUBAR)  # window-rel
LOAD_MENU = (315, 8)            # Capture menu (t260 measured)
LOAD_ROW = (350, 197)           # "Load state" row (t260 measured)
RETURN_TO_GAME = (318, 333)     # window-rel, production title menu top option
WALL_FIELDS = V4.WALL_FIELDS
PIXEL_ALIVE = 50

LOG = None


def log(msg):
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    print(line, flush=True)
    if LOG:
        with open(LOG, "a") as f:
            f.write(line + "\n")


def sh(cmd, timeout=90):
    env = dict(os.environ, DISPLAY=DISPLAY)
    return subprocess.run(cmd, shell=True, capture_output=True, timeout=timeout, env=env)


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
            continue
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
    r = sh(f"DISPLAY={DISPLAY} import -window root {path}")
    return Image.open(path).convert("RGB") if r.returncode == 0 else None


def popup_ok_center(im):
    """v4 detector with the +MENUBAR root-band shift for the GUI window."""
    px = im.load()
    rows = {}
    for y in range(330 + MENUBAR, 470 + MENUBAR):
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
    env = dict(os.environ, DISPLAY=DISPLAY)
    subprocess.run([XSEND, "DOSBox-X"] + args, capture_output=True, timeout=30, env=env)


def drain_popups(maxn=25):
    closed = 0
    for _ in range(maxn):
        im = grab("/tmp/_t261_popup.png")
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
    a = grab("/tmp/_t261_probe_a.png")
    send(["key", "Escape"])
    time.sleep(1.5)
    b = grab("/tmp/_t261_probe_b.png")
    n = V4.diff_pixels(a, b)
    if n > PIXEL_ALIVE:
        return True, n
    send(["key", "c"])
    time.sleep(1.5)
    c = grab("/tmp/_t261_probe_c.png")
    n2 = V4.diff_pixels(b, c)
    if n2 > PIXEL_ALIVE:
        send(["key", "c"])
        time.sleep(1.0)
        return True, n2
    return False, n


def ram_frozen(gap=20):
    s1 = ring_rows()
    time.sleep(gap)
    s2 = ring_rows()
    if not s1 or not s2:
        return False, "ring unreadable"
    def sig(rows):
        d = {}
        for r in rows:
            f = r.get("file")
            if f:
                d[f] = {k: v for k, v in r.items() if k not in WALL_FIELDS}
        return d
    a, b = sig(s1), sig(s2)
    changed = {f for f in set(a) & set(b) if a[f] != b[f]}
    new_slots = set(b) - set(a)
    if changed or new_slots:
        return False, f"RAM moved: {sorted(changed)[:4]} new={sorted(new_slots)[:4]}"
    return True, f"only wall/file moved in {gap}s ({len(b)} slots)"


def bank_ring(tag):
    dest = os.path.join(ROOT, f"work/r1/bank-{tag}")
    os.makedirs(dest, exist_ok=True)
    n = 0
    for p in sorted(glob.glob(os.path.join(SAVEDIR, "*.sav"))):
        shutil.copy2(p, dest)
        n += 1
    log(f"banked {n} ring slots -> work/r1/bank-{tag}")
    return dest


def click_load(expect_turn, timeout=150):
    """Capture->Load state; verify via a watcher row with turn>=expect_turn."""
    log0 = os.path.getsize(os.path.join(RUNDIR, "dosbox.log"))
    send(["key", "Escape"]); time.sleep(0.6)
    send(["315", "8"]);      time.sleep(1.2)
    send(["click", str(LOAD_ROW[0]), str(LOAD_ROW[1])])
    deadline = time.time() + timeout
    while time.time() < deadline:
        time.sleep(3)
        with open(os.path.join(RUNDIR, "dosbox.log"), errors="replace") as f:
            f.seek(log0)
            tail = f.read()
        if "Loaded. (Slot 60)" in tail:
            break
    else:
        log("load: no 'Loaded.' line in log window")
        return None
    deadline = time.time() + 120
    while time.time() < deadline:
        rs = ring_rows()
        hit = [r for r in rs if r.get("turn") and r.get("in_game")]
        if hit and max(r["turn"] for r in hit) >= expect_turn:
            return max(r["turn"] for r in hit)
        time.sleep(5)
    return None


def recover(prev_turn):
    """recover per RECOVER_MODE. loadstate = scratch session (slot 60).
    resume = production: bank, SIGKILL recorded pid, r1_playcap_vnc.sh start,
    Return-to-Game. HONEST CAVEAT (t259): RESUME.GAM is the Oct-29 save, so a
    production resume REGRESSES to that campaign point; it is a last resort,
    logged with the turn delta."""
    log(f"SOFTLOCK DECLARED - recovery mode={RECOVER_MODE}")
    grab(os.path.join(BASE, f"softlock_evidence_{int(time.time())}.png"))
    bank_ring(f"t261-recovery-{int(time.time())}")
    pidf = os.path.join(RUNDIR, "dosbox.pid")
    pids = []
    if os.path.exists(pidf):
        p = open(pidf).read().strip()
        if p:
            pids.append(p)
    else:                                   # production pid file naming
        alt = os.path.join(ROOT, "work/r1/vnc/dosbox.pid")
        if os.path.exists(alt):
            pids.append(open(alt).read().strip())
    for p in pids:
        sh(f"kill -9 {p} 2>/dev/null || true")
    log(f"SIGKILLed recorded dosbox pid(s) {pids}")
    time.sleep(4)
    if RECOVER_MODE == "resume":
        r = subprocess.run(["bash", os.path.join(ROOT, "scripts/r1_playcap_vnc.sh"), "start"],
                           capture_output=True, timeout=400, cwd=ROOT)
        log("relaunch rc=%d %s" % (r.returncode,
            r.stdout.decode(errors="replace").strip()[-200:]))
        if r.returncode != 0:
            return False
        for i in range(12):
            time.sleep(10)
            send(["click", str(RETURN_TO_GAME[0]), str(RETURN_TO_GAME[1])])
            time.sleep(8)
            rs = ring_rows()
            if rs and any(x.get("in_game") for x in rs[-6:]):
                got = ring_turn()
                log(f"resumed into game (attempt {i+1}) at turn {got} "
                    f"(pre-crash {prev_turn}) - RESUME.GAM regression logged")
                return True
        log("recovery FAILED: still not in_game after 12 resume clicks")
        return False
    env = dict(os.environ, KEEP_SAVE="1")
    r = subprocess.run(["bash", os.path.join(ROOT, "scripts/r1_t261_session.sh"), "bringup"],
                       capture_output=True, timeout=400, cwd=ROOT, env=env)
    log("relaunch rc=%d %s" % (r.returncode,
        r.stdout.decode(errors="replace").strip()[-200:]))
    if r.returncode != 0:
        return False
    time.sleep(25)                       # boot to title menu
    got = click_load(prev_turn)          # never regress below the pre-crash turn
    if got is None:
        # slot 60 may predate prev_turn; accept any same-session in-game state
        rs = ring_rows()
        hit = [r for r in rs if r.get("turn") and r.get("in_game")]
        if hit:
            got = max(r["turn"] for r in hit)
            log(f"recovery loaded turn {got} (< pre-crash {prev_turn}) - loss logged")
            return True
        log("recovery FAILED: no in-game row after loadstate")
        return False
    log(f"recovery OK: loaded turn {got}")
    return True


def main():
    global LOG
    target, presses, max_soft = 1405, 200, 3
    a = sys.argv[1:]
    for i, x in enumerate(a):
        if x == "--target": target = int(a[i + 1])
        if x == "--max-presses": presses = int(a[i + 1])
        if x == "--max-softlocks": max_soft = int(a[i + 1])
    LOG = os.path.join(BASE, f"drive_{time.strftime('%Y%m%d-%H%M%S')}.log")
    log(f"t261 drive start target={target} presses<={presses} softlocks<={max_soft}")
    log(f"dosbox pids alive: {sh('pgrep -x dosbox-x || echo none').stdout.decode().split()}")
    drain = drain_popups()
    log(f"pre-drive popup drain closed {drain}")
    cur = ring_turn()
    log(f"ring turn at start: {cur}")
    if cur is None:
        log("RING UNREADABLE - abort")
        return 1
    n = stall = softlocks = 0
    last_bank = cur
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
        log(f"press {n}: ring turn {cur}{' (moved)' if moved else ' (no advance)'} drained={drained}")
        if moved:
            stall = 0
            if cur - last_bank >= 30:
                bank_ring(f"t261-t{cur}")
                last_bank = cur
            continue
        stall += 1
        if stall < 2:
            continue
        alive, npix = input_alive()
        log(f"probe: input {'ALIVE' if alive else 'DEAD'} (changed_px={npix})")
        if alive:
            stall = 0
            continue
        frozen, why = ram_frozen()
        im = grab("/tmp/_t261_softlock_screen.png")
        log(f"probe: ram {'FROZEN' if frozen else 'MOVING'} ({why}) "
            f"popup_on_screen={popup_ok_center(im) is not None}")
        if not frozen:
            stall = 0
            continue
        softlocks += 1
        if softlocks > max_soft:
            log(f"softlock {softlocks} > max - giving up at ring turn {cur}")
            return 3
        if not recover(cur):
            return 1
        cur = ring_turn() or cur
        last_bank = cur
        stall = 0
    ok = cur >= target
    grab(os.path.join(BASE, "drive_final.png"))
    log(("TARGET REACHED" if ok else "BUDGET EXHAUSTED") + f" at ring turn {cur}")
    bank_ring(f"t261-final-{cur}")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
