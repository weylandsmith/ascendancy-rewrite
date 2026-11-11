#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t283: OQ-021 WRITE-WATCHPOINT session — find the EIP that writes DAT_482fb.

Everything here is composed from MEASURED pieces (docs/re/dosbox-debugger.md
LIVE VERIFICATION, t282):
  * dosbox-x-dbg connects OUT to our listener (DIRECTION LAW) -> bind first.
  * EXEC works headless; BREAK needs a pty (debug.cpp:5410 isatty x3).
  * BREAK ~1 s after connect aborted the emulator 1/2 with a glibc heap error;
    BREAK after a long settle worked 2/2 -> settle first (default 40 s).
  * A BPLM fire prints seg 0000 (BPLM stores seg=0) so the printed address is
    USELESS -> arm EXACTLY ONE breakpoint and treat any fire line as ours.
  * First fire is the 0x00-baseline artifact (AddMemBreakpoint stores 0;
    fire test bp->GetValue()!=current, debug.cpp:870) -> reject '00 -> xx'.
  * ControlServer_Poll runs inside DEBUG_Loop (debug.cpp:5267) so the stopped
    debugger still answers EXEC over the same socket -> read registers there.

ADDRESS LAW (pointer law CLOSED, docs/re/r1-savestate.md): the payload image is
verbatim at guest-physical P0 = B - 0x88 and guest linear == physical, so the
score slot linear = B - 0x88 + 0x82bb0 + 0x482fb, with B SCANNED FROM THIS
SESSION'S OWN RING (never production's).

SAFETY: scratch copy work/r1/game-wp only (asserted); OWN captures dir; private
Xvfb (never :9); core=normal; -time-limit always; kill-by-recorded-PID in a
finally. The scratch copy's RESUME.GAM is replaced by the md5-verified Oct-29
backup so the title menu's "Return to Current Game" enters a REAL campaign
(t272 measured a title-screen boot has NO image resident -> nothing to watch).

usage: r1_t283_wp_session.py [--port 55997] [--disp 97] [--settle 40]
                             [--campaign-wait 300] [--fire-wait 480]
Exit 0 = non-artifact fire captured + register state banked.
     1 = ran with a negative (no real fire in budget / campaign not entered).
     2 = harness error.
"""
import argparse
import glob
import os
import pty
import re
import signal
import shutil
import socket
import struct
import subprocess
import sys
import threading
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_sav_scan as SS                                   # noqa: E402

DBG_BIN = os.path.join(ROOT, "work/r1/bin/dosbox-x-dbg")
SCRATCH = os.path.join(ROOT, "work/r1/game-wp")
PAYLOAD = os.path.join(ROOT, "work/ascend_payload.bin")
OCT29 = os.path.join(ROOT, "work/r1/game/RESUME.GAM.user-oct29")
OCT29_MD5 = "5b382afbb789186c3654f3cec085b2e2"
OBJ1_OFF = 0x82bb0
SCORE_OFF = 0x482fb
H = 0x88                                    # member offset -> image base
RETURN_TO_GAME = (318, 333)                 # window-rel, -nogui layout (t250)
NEXTTURN = (511, 67)                        # window-rel, -nogui (t245 law)
XSEND = os.path.join(ROOT, "tools/xsend")

EVENTS = []
FIRE_RE = re.compile(r"Memory breakpoint.*?([0-9A-Fa-f]{2})\s*->\s*([0-9A-Fa-f]{2})")


def read_until_end(f, end_marker, budget):
    lines, header = [], None
    t0 = time.time()
    while time.time() - t0 < budget:
        try:
            raw = f.readline()
        except (socket.timeout, OSError):
            continue
        if not raw:
            return lines, False, header
        line = raw.decode("utf-8", "replace").rstrip("\r\n")
        if line == end_marker:
            return lines, True, header
        if line.startswith("BEGIN event"):
            ev, _, _ = read_until_end(f, "END event", 2.0)
            EVENTS.extend(ev)
            continue
        if line.startswith("BEGIN "):
            header = line
            continue
        if line:
            lines.append(line)
    return lines, True, header


def drain(master_fd, path):
    with open(path, "wb") as fh:
        while True:
            try:
                data = os.read(master_fd, 65536)
            except OSError:
                return
            if not data:
                return
            fh.write(data)
            fh.flush()


def kill_rec(pid, name):
    try:
        os.kill(pid, signal.SIGKILL)
        print(f"[teardown] SIGKILL {name} pid={pid}", flush=True)
    except ProcessLookupError:
        print(f"[teardown] {name} pid={pid} already gone", flush=True)


def xsend(disp, args, log):
    env = dict(os.environ, DISPLAY=dspec(disp))
    for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"):
        env.pop(k, None)
    r = subprocess.run([XSEND, "DOSBox-X"] + args, capture_output=True,
                       timeout=30, env=env)
    log(f"xsend {args} rc={r.returncode} {r.stderr.decode(errors='replace').strip()}")
    return r.returncode == 0


def ring_base(savedir, anch, log, budget=180.0):
    """Scan this session's own ring slots for the payload base B.

    Returns (B, slot_path) or (None, None). A slot being written while we read
    it raises (partial zip) -> skip and retry until the budget.
    """
    t0 = time.time()
    while time.time() - t0 < budget:
        for p in sorted(glob.glob(os.path.join(savedir, "*.sav")),
                        key=os.path.getmtime, reverse=True):
            try:
                import zipfile
                mem = zipfile.ZipFile(p).read("Memory")
            except Exception as e:
                log(f"ring {os.path.basename(p)} unreadable ({e})")
                continue
            votes, _ = SS.find_base(mem, anch)
            if votes and votes.most_common(1)[0][1] >= 5:
                B, n = votes.most_common(1)[0]
                u32 = struct.unpack("<I", mem[B + OBJ1_OFF + SCORE_OFF:
                                             B + OBJ1_OFF + SCORE_OFF + 4])[0]
                turn = struct.unpack("<I", mem[B + OBJ1_OFF + 0x16143:
                                               B + OBJ1_OFF + 0x16143 + 4])[0]
                log(f"ring {os.path.basename(p)}: B={B:#x} ({n} votes) "
                    f"score_stars={u32}")
                return B, p, u32
        time.sleep(5)
    return None, None, None


def fire_lines(path):
    if not os.path.exists(path):
        return []
    txt = open(path, "rb").read().decode("utf-8", "replace")
    return [l for l in txt.splitlines() if "Memory breakpoint" in l]


def dump_stopped(req, out, B, log, eip=None, esp=None):
    """Read the stopped debugger's state over the SAME socket (t282 measured).

    Memory reads: MEMDUMPBIN with seg=0000. ADDRESSING IS SELF-VERIFIED, not
    assumed: the code window at EIP must equal the payload bytes at
    EIP-(B-0x88) (positive control — if they differ, the seg:0 form is NOT
    linear and the stack read is meaningless, which we then say). [esp] u32 is
    the `call` return address -> caller site (t283).
    """
    bank = os.path.join(out, "stopped-state.txt")
    with open(bank, "w") as tf:
        for cmd in ["BPLIST", "CPU", "EV eip", "EV cs", "EV ds", "EV es",
                    "EV ss", "EV esp", "EV eax", "EV ebx", "EV ecx", "EV edx",
                    "EV esi", "EV edi", "EV flags",
                    f"DV {B - H + OBJ1_OFF + SCORE_OFF - 0x20:08X}"]:
            lines, ok, hdr = req(f"EXEC {cmd}", 12.0)
            tf.write(f"\n=== EXEC {cmd} hdr={hdr} ok={ok}\n")
            for l in lines:
                tf.write(l + "\n")
            tf.flush()
            log(f"EXEC {cmd!r} -> hdr={hdr} {len(lines)} lines")
        if eip is not None:
            f = os.path.join(out, "code_at_eip.bin")
            lines, ok, hdr = req(f"EXEC MEMDUMPBIN 0000:{eip:08X} 40 {f}", 15.0)
            tf.write(f"\n=== MEMDUMPBIN code hdr={hdr} lines={lines}\n")
            if os.path.exists(f):
                got = open(f, "rb").read()
                want = open(PAYLOAD, "rb").read()[eip - (B - H):
                                                  eip - (B - H) + len(got)]
                ctl = got == want
                tf.write(f"code control vs payload: MATCH={ctl} "
                         f"({len(got)} B)\n")
                log(f"MEMDUMPBIN code control MATCH={ctl}")
            else:
                tf.write("code dump file absent\n")
                log("MEMDUMPBIN code: no file produced")
        if esp is not None:
            f = os.path.join(out, "stack_at_esp.bin")
            lines, ok, hdr = req(f"EXEC MEMDUMPBIN 0000:{esp:08X} 64 {f}", 15.0)
            tf.write(f"\n=== MEMDUMPBIN stack hdr={hdr} lines={lines}\n")
            if os.path.exists(f):
                data = open(f, "rb").read()
                tf.write("stack hex: " + data.hex(" ") + "\n")
                if len(data) >= 4:
                    ra, = struct.unpack("<I", data[:4])
                    tf.write(f"[esp] u32 = {ra:#08x} "
                             f"-> payload file off {ra - (B - H):#x}\n")
                    log(f"[esp] return address = {ra:#08x} "
                        f"(file {ra - (B - H):#x})")
            else:
                tf.write("stack dump file absent\n")
    return bank


def dspec(disp):
    """t283 RUN-3 BUG: argparse --disp is '98' WITHOUT the colon; passing it
    raw as DISPLAY makes X treat it as a hostname -> empty output -> the
    window check false-negatives while the emulator is provably alive."""
    return f":{str(disp).lstrip(':')}"


def grab(disp, path):
    r = subprocess.run(["import", "-window", "root", path],
                       capture_output=True, timeout=30,
                       env=dict(os.environ, DISPLAY=dspec(disp)))
    return r.returncode == 0


def diff_px(a, b, stride=2):
    """Changed pixels; -1 if unreadable. t283 RUN-4 TRAP: system python3 has
    NO PIL (the venv does) — a PIL-based helper silently returned -1 and the
    entry loop read 'no reaction' forever. ImageMagick `compare` is installed
    system-wide and gives an exact AE count."""
    r = subprocess.run(["compare", "-metric", "AE", a, b, "null:"],
                       capture_output=True, timeout=60, text=True)
    tok = r.stdout.strip() or r.stderr.strip()
    try:
        return int(float(float(tok.split(" ")[0])))
    except Exception:
        return -1


def window_alive(disp):
    r = subprocess.run(["xwininfo", "-root", "-tree"], capture_output=True,
                       timeout=15, env=dict(os.environ, DISPLAY=dspec(disp)),
                       text=True)
    return "DOSBox-X" in r.stdout


def enter_campaign(out, disp, log, max_clicks=25):
    """Click 'Return to Current Game' until the screen RESPONDS (t283 lesson:
    an xsend rc=0 proves the event was SENT, not delivered; the t244/t245
    blocker-window class is why we verify by screen diff, not by log)."""
    a = os.path.join(out, "screen_pre_click.png")
    b = os.path.join(out, "screen_post_click.png")
    for k in range(5):                      # tolerate a transient recreate
        if window_alive(disp):
            break
        log(f"ENTER: window tree has no DOSBox-X yet (try {k})")
        time.sleep(3.0)
    else:
        log("ENTER: X window gone — Xvfb died?")
        return False
    grab(disp, a)
    for i in range(max_clicks):
        xsend(disp, ["click", str(RETURN_TO_GAME[0]),
                     str(RETURN_TO_GAME[1])], log)
        # poll for reaction up to 24 s BEFORE clicking again: the campaign
        # load takes several seconds (t261 allows 150), and a second click
        # landing on the loaded starmap would hit the bottom control grid.
        reacted = False
        n = -1
        for k in range(6):
            time.sleep(4.0)
            if not grab(disp, b):
                log(f"ENTER attempt {i}: grab failed (X dead?)")
                return False
            n = diff_px(a, b)
            if n > 2000:
                log(f"ENTER attempt {i} poll {k}: diff {n} px -> reacted")
                reacted = True
                break
        if reacted:
            shutil.copy2(b, os.path.join(out, f"screen_entered_{i}.png"))
            log("ENTER: screen reacted — campaign load presumed")
            return True
        shutil.copy2(b, a)
        log(f"ENTER attempt {i}: 24 s, no reaction (diff {n} px)")
    log("ENTER: %d clicks, screen never reacted" % max_clicks)
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=55997)
    ap.add_argument("--disp", default="97")
    ap.add_argument("--tl", type=int, default=1500)
    ap.add_argument("--settle", type=int, default=40)
    ap.add_argument("--boot", type=int, default=60)
    ap.add_argument("--campaign-wait", type=int, default=300)
    ap.add_argument("--fire-wait", type=int, default=480)
    ap.add_argument("--walk", type=int, default=0,
                    help="after the first fire, keep EXEC RUNning and record "
                         "every subsequent fire line for N seconds (the value "
                         "WALK: 01 -> 02 -> ... proves a per-turn accumulator "
                         "loop and gives the cadence). 0 disables.")
    ap.add_argument("--phases", default="",
                    help="comma list of ATTRIBUTION phases, each run in order "
                         "with its own fire budget, e.g. 'quiet,c,turn'. "
                         "quiet = no injected input at all; c = starmap overlay "
                         "toggle only; turn = NEXTTURN click only. Empty (the "
                         "default) keeps the old mixed-probe behaviour. A fire "
                         "in a named phase attributes the writer to that input "
                         "(run 6 fired with BOTH probes live - ambiguous).")
    ap.add_argument("--phase-wait", type=int, default=90,
                    help="per-phase fire budget (seconds) when --phases is set")
    ap.add_argument("--turn-probe", type=int, default=60,
                    help="seconds between NEXTTURN clicks while armed "
                         "(t258 recompute-on-end-turn candidate); 0 off")
    ap.add_argument("--overlay-probe", type=int, default=45,
                    help="seconds between 'c' starmap-overlay presses while "
                         "armed (t189b candidate: value recomputes when the "
                         "overlay opens); 0 disables")
    args = ap.parse_args()

    for p, why in [(DBG_BIN, "debugger binary"), (SCRATCH, "scratch copy"),
                   (PAYLOAD, "payload"), (OCT29, "Oct-29 campaign backup")]:
        if not os.path.exists(p):
            print(f"HARNESS ERROR: missing {why} {p}")
            return 2
    if os.path.abspath(SCRATCH).startswith(os.path.join(ROOT, "game") + os.sep):
        print("HARNESS ERROR: refusing to mount game/")
        return 2
    import hashlib
    if hashlib.md5(open(OCT29, "rb").read()).hexdigest() != OCT29_MD5:
        print("HARNESS ERROR: Oct-29 backup md5 mismatch")
        return 2

    out = os.path.join(ROOT, "work/r1",
                       f"t283-wp-{time.strftime('%Y%m%d-%H%M%S')}")
    os.makedirs(out, exist_ok=True)
    # t283 RUN-2 MEASURED: `-savedir` does NOT mkdir (autosave at +10 s
    # logged 'Failed to save the current state.' and the SDL window
    # then vanished from the X tree). The dir MUST pre-exist.
    os.makedirs(os.path.join(out, "save"), exist_ok=True)
    runlog_path = os.path.join(out, "session.log")
    transcript = os.path.join(out, "mcp-transcript.txt")
    ptylog = os.path.join(out, "pty.log")
    conf = os.path.join(out, "wp.conf")
    # t282 MEASURED: autosave slots land in the dosbox CWD (/save),
    # NOT under captures= (run dirs show save/ siblings of wp.conf).
    savedir = os.path.join(out, "save")

    def log(msg):
        line = f"{time.strftime('%H:%M:%S')} {msg}"
        print(line, flush=True)
        with open(runlog_path, "a") as fh:
            fh.write(line + "\n")

    # --- scratch campaign seed (SCRATCH ONLY; game/ untouched) --------------
    shutil.copy2(OCT29, os.path.join(SCRATCH, "RESUME.GAM"))
    low = os.path.join(SCRATCH, "resume.gam")
    if os.path.exists(low):
        os.rename(low, low + ".vendor-t283")
        log("scratch vendor resume.gam renamed out of the way")

    with open(conf, "w") as fh:
        fh.write(f"""[dosbox]
machine=svga_s3
memsize=16
core=normal
mcp_server={args.port}
captures={out}/caps
autosave=10 41-60
saveremark=false
[sdl]
output=x11
fullscreen=false
autolock=false
[mixer]
nosound=true
[autoexec]
MOUNT C {SCRATCH}
C:
ASCEND.EXE
""")

    xv = subprocess.Popen(["Xvfb", f":{args.disp}", "-screen", "0", "800x600x24"],
                          stdout=open(os.path.join(out, "xvfb.out"), "wb"),
                          stderr=subprocess.STDOUT)
    time.sleep(1.5)
    ls = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ls.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ls.bind(("127.0.0.1", args.port))
    ls.listen(1)
    ls.settimeout(2.0)

    master, slave = pty.openpty()
    threading.Thread(target=drain, args=(master, ptylog), daemon=True).start()
    env = dict(os.environ, DISPLAY=f":{args.disp}", TERM="xterm")
    for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"):
        env.pop(k, None)
    child = subprocess.Popen(
        [DBG_BIN, "-conf", conf, "-nogui", "-savedir", savedir,
         "-time-limit", str(args.tl)],
        stdin=slave, stdout=slave, stderr=slave, cwd=out, env=env,
        close_fds=True)
    os.close(slave)
    log(f"spawned dosbox-x-dbg pid={child.pid} display=:{args.disp} out={out}")

    rc = 1
    conn = None
    try:
        t0 = time.time()
        while time.time() - t0 < args.boot:
            try:
                conn, addr = ls.accept()
                log(f"connected OUT from {addr} after {time.time()-t0:.1f}s")
                break
            except socket.timeout:
                if child.poll() is not None:
                    log(f"child exited early rc={child.returncode}")
                    break
        if conn is None:
            log("NEGATIVE: no MCP connection")
            return 1

        conn.settimeout(0.5)
        f = conn.makefile("rwb")
        seq = [0]

        def req(verb, budget=30.0):
            seq[0] += 1
            rid = str(seq[0])
            try:
                f.write(f"REQ {rid} {verb}\n".encode())
                f.flush()
            except OSError as e:
                log(f"channel dead ({e}) at {verb!r}")
                return [], False, None
            return read_until_end(f, f"END {rid}", budget)

        lines, ok, hdr = req("PING", 10.0)
        log(f"PING hdr={hdr} lines={lines}")
        if "PONG" not in " ".join(lines):
            log("NEGATIVE: no PONG")
            return 1

        # ---- enter a campaign (t272: title boot has no image resident) ----
        log(f"settling {args.settle}s before the resume click")
        time.sleep(args.settle)
        if not enter_campaign(out, args.disp, log):
            log("NEGATIVE: campaign entry click never moved the screen")
            return 1
        pay = open(PAYLOAD, "rb").read()
        anch = SS.build_anchors(pay)
        B, slot, score_at_scan = ring_base(savedir, anch, log,
                                            budget=args.campaign_wait)
        if B is None:
            log("NEGATIVE: campaign never entered (payload image not resident "
                "in this session's ring) — no address to watch")
            shutil.copytree(savedir, os.path.join(out, "ring-negative"),
                            dirs_exist_ok=True)
            return 1
        lin = B - H + OBJ1_OFF + SCORE_OFF
        log(f"TARGET: B={B:#x} P0={B-H:#x} score linear={lin:#08x} "
            f"(payload file off {lin - (B - H):#x})")

        # ---- BREAK. t283 RUN-5 MEASURED: BREAK issued seconds after the
        # campaign-load click got RECEIVED ([ControlClient] mcp command REQ 2
        # BREAK in pty.log) but no BEGIN header came back in 25 s, while t282's
        # BREAKs at a quiescent title screen answered BEGIN-OK. The settle law
        # therefore applies AFTER the load, not only before it. Retry with
        # PING liveness between attempts; last resort VRT (enters the debugger
        # at the next vertical retrace, live HELP list).
        lines, ok, hdr = req("PING", 10.0)
        if "PONG" not in " ".join(lines):
            log("NEGATIVE: dead after campaign load (no PONG)")
            return 1
        log(f"post-load settle {args.settle}s before BREAK")
        time.sleep(args.settle)
        hdr = None
        for attempt in range(3):
            lines, ok, hdr = req("BREAK", 60.0)
            log(f"BREAK#{attempt} hdr={hdr} frame_ok={ok} lines={lines[:5]}")
            if hdr is not None and not hdr.rstrip().endswith("ERR"):
                break
            hdr = None
            lines, ok, _ = req("PING", 15.0)
            if "PONG" not in " ".join(lines):
                log(f"BREAK#{attempt}: channel dead (no PONG)")
                break
            time.sleep(10.0)
        if hdr is None:
            log("trying VRT (run-then-stop at next retrace) instead of BREAK")
            lines, ok, hdr2 = req("EXEC VRT", 45.0)
            log(f"VRT hdr={hdr2} lines={lines[:5]}")
            time.sleep(3.0)
            lines, ok, hdr = req("EXEC BPLIST", 20.0)
            if hdr is None:
                log("NEGATIVE: neither BREAK nor VRT stopped the debugger")
                return 1
            log("VRT stopped the debugger (BPLIST answers)")
        lines, ok, hdr = req("EXEC BPLIST", 10.0)
        log(f"BPLIST after BREAK hdr={hdr} lines={lines}")

        # ---- arm EXACTLY ONE watchpoint -----------------------------------
        lines, ok, hdr = req(f"EXEC BPLM {lin:08X}", 15.0)
        log(f"arm BPLM {lin:08X} hdr={hdr} lines={lines}")
        lines, ok, hdr = req("EXEC BPLIST", 10.0)
        armed = [l for l in lines if "BPLM" in l]
        log(f"armed: {armed}")
        if len(armed) != 1:
            log(f"NEGATIVE: expected exactly 1 armed BPLM, got {armed}")
            return 1

        tf = open(transcript, "w")
        tf.write(f"t283 watchpoint session {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        tf.write(f"B={B:#x} score linear={lin:#08x} slot={slot} "
                 f"score_at_scan={score_at_scan}\n")

        # ---- ARTIFACT LAW, DERIVED (t283): AddMemBreakpoint stores baseline 0
        # (debug.cpp:1048) and the fire test is bp->GetValue() != current
        # (:870), so the spurious first fire happens IFF the byte != 0 at arm
        # time. score_stars read 0 from this session's own ring at scan time
        # (measured run t283-wp-20261103-003143: score_stars=0 post-load) =>
        # NO artifact is possible here and the FIRST fire IS the writer.
        # If the byte was nonzero, reject exactly one '00 -> xx' fire, and
        # remember: after ANY fire the CPU is STOPPED, so a rejected fire must
        # be followed by EXEC RUN before anything else can happen.
        expect_artifact = (score_at_scan & 0xFF) != 0

        def inject(phase):
            """One input poke for the named attribution phase (no-op 'quiet')."""
            if child.poll() is not None:
                return
            if phase == "c":
                xsend(args.disp, ["key", "c"], log)
            elif phase == "turn":
                xsend(args.disp, ["click", str(NEXTTURN[0]),
                                  str(NEXTTURN[1])], log)
            elif phase == "mixed":
                xsend(args.disp, ["key", "c"], log)
                xsend(args.disp, ["click", str(NEXTTURN[0]),
                                  str(NEXTTURN[1])], log)

        phases = [p.strip() for p in args.phases.split(",") if p.strip()] \
            or ["mixed"]
        fires = []          # (phase, fire_line)
        seen = []
        for phase in phases:
            budget = args.phase_wait if args.phases else args.fire_wait
            log(f"PHASE {phase!r}: budget {budget}s")
            lines, ok, hdr = req("EXEC RUN", 10.0)
            if hdr is None:
                log("NEGATIVE: channel dead at RUN")
                break
            t0 = time.time()
            last_inject = 0.0
            iv = 15 if phase in ("c", "turn") else max(
                args.overlay_probe, args.turn_probe)
            while time.time() - t0 < budget:
                cur = fire_lines(ptylog)
                new = [l for l in cur if l not in seen]
                if new:
                    for l in new:
                        log(f"FIRE LINE [{phase}] +{time.time()-t0:.1f}s: {l}")
                    seen = cur
                    last_new = new[-1]
                    mm = FIRE_RE.search(last_new)
                    art = bool(mm) and mm.group(1).upper() == "00"
                    if art and expect_artifact:
                        log("baseline-artifact fire - rejecting, RUN again")
                        expect_artifact = False
                        lines, ok, hdr = req("EXEC RUN", 10.0)
                        continue
                    fires.append((phase, last_new))
                    break
                if time.time() - last_inject > iv:
                    inject(phase)
                    last_inject = time.time()
                time.sleep(3.0)
            if fires:
                break
        tf.write("\n=== fires: " + repr(fires) + "\n")
        tf.flush()

        if not fires:
            log("NEGATIVE: no non-artifact fire in any phase — OQ-021 "
                "producer still unwitnessed (phase budgets banked)")
            tf.close()
            shutil.copytree(savedir, os.path.join(out, "ring-final"),
                            dirs_exist_ok=True)
            return 1

        phase, real = fires[0]
        log(f"REAL FIRE in phase {phase!r}: {real}")

        # ---- optional WALK: keep resuming, record every fire --------------
        walk = []
        if args.walk:
            log(f"WALK: {args.walk}s of RUN/fire cycles")
            tw = time.time()
            while time.time() - tw < args.walk:
                lines, ok, hdr = req("EXEC RUN", 10.0)
                if hdr is None:
                    log("WALK: channel dead")
                    break
                tw0 = time.time()
                while time.time() - tw0 < 25:
                    cur = fire_lines(ptylog)
                    new = [l for l in cur if l not in seen]
                    if new:
                        seen = cur
                        for l in new:
                            # EIP AT EVERY FIRE: the heavy-debug check runs
                            # once per instruction at the interpreter loop top
                            # (core_normal.h:181), so the reported EIP is the
                            # instruction AFTER the store. A walk whose fires
                            # sit at DIFFERENT EIPs is a loop body; identical
                            # EIPs = the same instruction re-executed.
                            le, _, _ = req("EXEC EV eip", 8.0)
                            nums = [x.strip() for x in le if x.strip()]
                            eip_s = nums[-1] if nums else "?"
                            walk.append((eip_s, l))
                            log(f"WALK FIRE eip={eip_s}: {l}")
                        break
                    time.sleep(2.0)
                if args.turn_probe and child.poll() is None:
                    xsend(args.disp, ["click", str(NEXTTURN[0]),
                                      str(NEXTTURN[1])], log)
            tf.write("\n=== walk fires (%d):\n" % len(walk))
            for w_ in walk:
                tf.write("  " + (w_[0] + " " if isinstance(w_, tuple)
                                 else "") +
                         (w_[1] if isinstance(w_, tuple) else w_) + "\n")
            tf.flush()
        # registers FIRST (needed to size the dumps), then code + stack
        regs = {}
        for r_ in ["eip", "esp"]:
            lines, ok, hdr = req(f"EXEC EV {r_}", 10.0)
            nums = [l.strip() for l in lines if l.strip()]
            if nums:
                try:
                    regs[r_] = int(nums[-1], 16)
                except ValueError:
                    pass
        log(f"regs: {regs}")
        bank = dump_stopped(req, out, B, log, eip=regs.get("eip"),
                            esp=regs.get("esp"))
        tf.write(f"\n=== stopped state banked to {bank}\n")
        lines, ok, hdr = req("EXEC BPLIST", 10.0)
        tf.write("=== BPLIST at stop: " + " | ".join(lines) + "\n")
        tf.close()
        log(f"transcript={transcript} state={bank}")
        shutil.copytree(savedir, os.path.join(out, "ring-final"),
                        dirs_exist_ok=True)
        rc = 0
    finally:
        kill_rec(child.pid, "dosbox-x-dbg")
        kill_rec(xv.pid, "Xvfb")
        ls.close()
        try:
            os.close(master)
        except OSError:
            pass
    log(f"DONE rc={rc} out={out}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
