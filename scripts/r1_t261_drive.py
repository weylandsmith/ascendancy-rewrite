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


def ring_in_game():
    """True iff the ring's CURRENT state is in-campaign. t273 LAW: the popup
    drain must NEVER run at the title menu — the white-band detector fires on
    title-menu text and clicked the Tutorial button (ring lineage flip 1086 ->
    645). Any row with in_game False in the tail window means title menu."""
    rows = ring_rows()
    if not rows:
        return False
    return all(r.get("in_game") for r in rows[-4:] if r.get("turn") is not None)


def grab(path):
    from PIL import Image
    r = sh(f"DISPLAY={DISPLAY} import -window root {path}")
    return Image.open(path).convert("RGB") if r.returncode == 0 else None


# ---- t289 RAM LIVENESS NEEDLE (docs/re/_wip_t288.md S3b) -------------------
# t288 CLOSED the dead-half question: softlock = the GAME-SIDE INPUT PUMP stops
# writing the pending-input globals WORD ds:0x484c4 (msg) / ds:0x484c6 (char),
# which the relay 0x54976 reads verbatim. They ride every ring slot's Memory
# member (no debugger): member-index law mem[B + 0x82bb0 + off], B by anchor
# vote (scripts/r288_input_census.py). SOP: inject 'c', expect the PAIR to
# CHANGE in a later slot. A pair frozen across the whole fresh ring is the
# t288 death signature.
# HONEST LIMIT (needle-char exhaustion): the globals hold the LAST-WRITTEN
# event and are not zeroed on consumption (witnessed: healthy production sat
# at (0x2e,0x63) after an old 'c'). So a 'c' injection is only DECISIVE when
# the pre-state char != 0x63; when pre is already (0x2e,0x63) the needle
# reports AMBIGUOUS and callers must fall back to the t288 conjunction
# (overlay pixel toggle + ring freeze + distinct-pair census).
import struct, zipfile
import r1_sav_scan as SS

PAYLOAD = os.path.join(ROOT, "work/ascend_payload.bin")
OBJ1_OFF = 0x82bb0
OFF_MSG, OFF_CHAR = 0x484c4, 0x484c6
NEEDLE_CHAR = 0x63                              # 'c': proven-safe, self-reverting
DEATH_SIG = (0x0001, 0x001b)                    # (msg, Escape) t288 census
_anchor_cache = None


def ring_slots():
    return sorted(glob.glob(os.path.join(SAVEDIR, "*.sav")), key=os.path.getmtime)


def input_globals(slot_path):
    """(msg, char) pending-input globals from one ring .sav, or None."""
    global _anchor_cache
    try:
        mem = zipfile.ZipFile(slot_path).read("Memory")
    except Exception:
        return None
    if _anchor_cache is None:
        with open(PAYLOAD, "rb") as f:
            _anchor_cache = SS.build_anchors(f.read())
    votes, _ = SS.find_base(mem, _anchor_cache)
    if not votes or votes.most_common(1)[0][1] < 5:
        return None
    base = votes.most_common(1)[0][0] + OBJ1_OFF
    return tuple(struct.unpack_from("<HH", mem, base + OFF_MSG))


def needle_census():
    """Distinct (msg,char) pairs across the current ring, newest last.
    >1 distinct = the pump wrote recently; 1 distinct over all slots = frozen."""
    seq = [p for p in ring_slots() if input_globals(p) is not None]
    pairs = [input_globals(p) for p in seq]
    return pairs


def needle_probe(tag=""):
    """Full liveness needle. Returns (verdict, detail) with verdict in
    ALIVE / DEAD / AMBIGUOUS / UNKNOWN.

    t289 LIVE MEASUREMENTS (running drive, pump demonstrably alive):
    (a) char GLOBAL == the injected key verbatim ('z' mid-drive flipped the
        pair (0x50,0x0) -> (0x2c,0x7a) in the next slots);
    (b) a needle whose char EQUALS the pre char is unobservable — pre
        (0x2e,0x63) + one 'c' + mouse re-stamping reads (0x2e,0x63) again,
        and a DEAD pump frozen at (0x2e,0x63) reads identically. So the
        needle char must differ from the pre char: 'c' normally, 'z' when
        pre char is already 0x63 (the parked/idle baseline t288 left).
        'z' map behaviour is UNVERIFIED (observed benign once: turns kept
        advancing, campaign unchanged); it fires ONLY in-campaign (callers
        run assert_on_map first) and only in the exhausted-pre case.
    Decisiveness: dead pump => globals frozen => post char != injected char
    => DEAD (no false-ALIVE path); live pump => char stamped => ALIVE."""
    slots = ring_slots()
    if not slots:
        return "UNKNOWN", "ring empty"
    pre = input_globals(slots[-1])
    pre_mt = os.path.getmtime(slots[-1])
    if pre is None:
        return "UNKNOWN", "base vote failed on newest slot"
    needle = NEEDLE_CHAR if pre[1] != NEEDLE_CHAR else 0x7A   # 'c', else 'z'
    send(["key", chr(needle)])
    if needle == NEEDLE_CHAR:
        time.sleep(1.2)
        send(["key", "c"])          # revert the overlay toggle (self-reverting)
    post, newer = None, []
    for _ in range(8):                       # 10 s cadence; 2 fresh slots max 40 s
        time.sleep(5)
        s = ring_slots()
        newer = [p for p in s if os.path.getmtime(p) > pre_mt + 0.5]
        if len(newer) >= 2:
            post = input_globals(newer[-1])
            break
    if post is None:
        return "UNKNOWN", f"no fresh slot pair after injection ({len(newer)} new)"
    if post[1] == needle:
        return "ALIVE", f"needle char {needle:#x} stamped: {pre} -> {post}"
    if pre == DEATH_SIG:
        return "DEAD", f"death signature {pre} survived needle {needle:#x}"
    pairs = needle_census()
    distinct = len(set(pairs))
    if pairs and distinct == 1:
        return "DEAD", f"pair {pre} constant across {len(pairs)} slots post-needle"
    return "DEAD", f"needle {needle:#x} absent from post {post}; {distinct} distinct in ring"


# ---- t285 DRIVE-CLASS PRECONDITION: title menu detected FROM THE SCREEN ----
# (fixture work/r1/bank-t285-flip1255/probe_b_043813.png: the orange title
# background dominates the game area above the white menu box). The ring is
# BLIND here (it keeps autosaving off-campaign), so no RAM-side guard substitutes.
def title_menu_on_screen(im):
    if im is None:
        return False, None
    px = im.load()
    w, h = im.size
    y0, y1 = 0, max(0, min(h, 330 + MENUBAR))
    tot = orange = 0
    for y in range(y0, y1, 3):
        for x in range(0, w, 4):
            r, g, b = px[x, y]
            tot += 1
            if r > 140 and g > 50 and b < 110 and r - b > 70:
                orange += 1
    frac = orange / max(1, tot)
    return frac > 0.20, round(frac, 4)


def assert_on_map(why):
    """Screen-based gate BEFORE any click (t285 law). Returns True iff safe."""
    im = grab("/tmp/_t261_precheck.png")
    title, frac = title_menu_on_screen(im)
    if title:
        log(f"TITLE MENU ON SCREEN ({frac} orange) at {why} - STOP, no clicks "
            f"(t285 precondition); evidence /tmp/_t261_precheck.png")
        return False
    return True


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
    # t273 LAW GUARD: never drain at the title menu (the white-band detector
    # misfires on menu text; t273 clicked Tutorial and lost the campaign).
    # t289 UPGRADE: the guard is the SCREEN, not the ring — t285 law says the
    # ring keeps autosaving in_game rows even off-campaign (blind).
    im0 = grab("/tmp/_t261_drain_gate.png")
    if title_menu_on_screen(im0)[0]:
        log("popup drain SKIPPED — title menu on screen (t289 screen guard)")
        return 0
    if not ring_in_game():
        log("popup drain SKIPPED — ring not in_game (t273 law)")
        return 0
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
    """True if the game reacts to synthetic input (PIXEL channel).
    t285 LAW: NEVER probe with Escape. Witnessed 04:38:11-13 (screenshots
    banked in work/r1/bank-t285-flip1255/): one Escape at the bare galaxy map
    ejected the campaign to the TITLE MENU (probe_a=campaign t1092, probe_b=
    title menu). The title-menu popup-drain misfire that followed swapped the
    campaign in RAM (t1086/fp3a189896 -> t1255/fp39614c7c). The old Escape
    last-resort branch is DELETED (t289): its guard was ring_in_game, and the
    t285 law established the ring is BLIND off-campaign (it keeps autosaving),
    so the branch could fire exactly where it is fatal. The 'c' overlay toggle
    is the only pixel probe: no-op at the title menu, big pixel delta in-game,
    self-reverting."""
    a = grab("/tmp/_t261_probe_a.png")
    send(["key", "c"])
    time.sleep(1.5)
    b = grab("/tmp/_t261_probe_b.png")
    n = V4.diff_pixels(a, b)
    if n > PIXEL_ALIVE:
        send(["key", "c"])          # revert the overlay
        time.sleep(1.0)
        return True, n
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
        # t289 / t287 LAW: the title-menu row highlight is HOVER state and SDL
        # rejects synthetic MotionNotify — an xsend click fires the STALE
        # hovered row (witnessed: opened Tutorial Select). Enter ONLY when the
        # cyan highlight is measured on R4 via scripts/r287_title_nav.py.
        import r287_title_nav as NAV
        for i in range(12):
            time.sleep(10)
            row = NAV.status("nav_t289_recover")
            for _ in range(8):          # walk highlight to R4 (index 3)
                if row == 3:
                    break
                NAV.key("Down"); time.sleep(0.8)
                row = NAV.status("nav_t289_walk")
            if row != 3:
                log(f"recover attempt {i+1}: highlight {NAV.NAMES[row] if row is not None else 'NONE'} "
                    f"not R4 - no Enter")
                continue
            NAV.key("Return")
            time.sleep(8)
            rs = ring_rows()
            if rs and any(x.get("in_game") for x in rs[-6:]) and assert_on_map("post-recover-enter"):
                got = ring_turn()
                log(f"resumed into game (attempt {i+1}) at turn {got} "
                    f"(pre-crash {prev_turn}) - RESUME.GAM regression logged")
                return True
        log("recovery FAILED: still not in_game after 12 highlight-verified resume attempts")
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


def ring_v():
    """(score_stars, selector_byte, turn) from the newest trusted ring row.
    t284 caveat: slots captured mid-recompute (~3 s window) legitimately read
    low, so this watch only fires on score_stars >= V_TARGET, never on deltas."""
    rows = ring_rows()
    inplay = [r for r in rows if r.get("in_game") and r.get("turn")]
    if not inplay:
        return None
    r = inplay[-1]
    return (r.get("score_stars"), r.get("selector_byte"), r.get("turn"))


def main():
    global LOG
    target, presses, max_soft = 1405, 200, 3
    V_TARGET, max_secs = 25, 3300
    a = sys.argv[1:]
    for i, x in enumerate(a):
        if x == "--target": target = int(a[i + 1])
        if x == "--max-presses": presses = int(a[i + 1])
        if x == "--max-softlocks": max_soft = int(a[i + 1])
        if x == "--v-target": V_TARGET = int(a[i + 1])
        if x == "--max-secs": max_secs = int(a[i + 1])
    deadline = time.time() + max_secs
    LOG = os.path.join(BASE, f"drive_{time.strftime('%Y%m%d-%H%M%S')}.log")
    log(f"t289 drive start target={target} presses<={presses} softlocks<={max_soft} "
        f"v_target={V_TARGET} needle=RAM(0x484c4/6)")
    log(f"dosbox pids alive: {sh('pgrep -x dosbox-x || echo none').stdout.decode().split()}")
    # t285 PRECONDITION 1: screen, not ring, decides whether we may click at all.
    if not assert_on_map("session start"):
        return 4
    drain = drain_popups()
    log(f"pre-drive popup drain closed {drain}")
    cur = ring_turn()
    log(f"ring turn at start: {cur}")
    if cur is None:
        log("RING UNREADABLE - abort")
        return 1
    n = stall = softlocks = alive_stalls = 0
    last_bank = cur
    while n < presses and cur < target and time.time() < deadline:
        v = ring_v()
        if v and ((v[0] is not None and v[0] >= V_TARGET) or (v[1] not in (0, None))):
            log(f"*** THRESHOLD WITNESS score_stars={v[0]} selector={v[1]} "
                f"turn={v[2]} - BANKING AND STOPPING (OQ-021 feed)")
            grab(os.path.join(BASE, f"witness_v_{v[2]}_{int(time.time())}.png"))
            bank_ring(f"t289-witness-t{v[2]}")
            return 0
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
            alive_stalls = 0
            if cur - last_bank >= 30:
                bank_ring(f"t261-t{cur}")
                last_bank = cur
            continue
        stall += 1
        if stall < 2:
            continue
        # t285 PRECONDITION 2: 2 consecutive no-advances = STOP-AND-LOOK.
        grab(os.path.join(BASE, f"stall2_{cur}_{int(time.time())}.png"))
        bank_ring(f"t289-stall2-t{cur}-press{n}")
        if not assert_on_map(f"stall2 press {n}"):
            return 4
        # t289 PRIMARY CHANNEL: RAM liveness needle (t288 S3b SOP) replaces
        # the pixel-diff as the softlock discriminator.
        verdict, why = needle_probe()
        log(f"NEEDLE {verdict}: {why}")
        if verdict == "DEAD":
            softlocks += 1
            frozen, why2 = ram_frozen(gap=12)
            log(f"softlock {softlocks} (needle DEAD, ring "
                f"{'FROZEN' if frozen else 'MOVING'}: {why2}) at turn {cur}")
            if softlocks > max_soft:
                log(f"softlock {softlocks} > max - STOP, no retry spiral at turn {cur}")
                return 3
            if not recover(cur):
                return 1
            if not assert_on_map("post-recover"):
                return 4
            cur = ring_turn() or cur
            last_bank = cur
            stall = 0
            continue
        if verdict == "ALIVE":
            alive_stalls += 1
            if alive_stalls >= 4:
                log(f"pump ALIVE but 4 stalled presses - STOP-AND-LOOK for a human "
                    f"at turn {cur} (engine stuck downstream of the pump)")
                return 3
            stall = 0
            continue
        # AMBIGUOUS / UNKNOWN -> t288 conjunction fallback:
        # pixel-toggle dead AND ring frozen -> treat as softlock-class but do
        # NOT kill blindly: bank already done above; one recovery attempt max.
        alive, npix = input_alive()
        frozen, why2 = ram_frozen(gap=12)
        log(f"fallback: pixel {'ALIVE' if alive else 'DEAD'}({npix}px) "
            f"ring {'FROZEN' if frozen else 'MOVING'} ({why2})")
        if (not alive) and frozen:
            softlocks += 1
            if softlocks > max_soft:
                log(f"softlock {softlocks} > max (conjunction) - STOP at turn {cur}")
                return 3
            if not recover(cur):
                return 1
            if not assert_on_map("post-recover-conj"):
                return 4
            cur = ring_turn() or cur
            last_bank = cur
        stall = 0
        alive_stalls += 1
    ok = cur >= target
    grab(os.path.join(BASE, "drive_final.png"))
    log(("TARGET REACHED" if ok else "BUDGET EXHAUSTED") + f" at ring turn {cur}")
    bank_ring(f"t261-final-{cur}")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
