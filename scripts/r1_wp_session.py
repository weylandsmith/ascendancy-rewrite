#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t286: GENERAL write-watchpoint session (the t283 instrument, scripted).

Everything runtime-behavioural here is MEASURED, not assumed — see
docs/re/dosbox-debugger.md "LIVE VERIFICATION" (t282) and docs/re/*.md t283:
  * dosbox-x-dbg connects OUT (DIRECTION LAW) -> bind the listener first.
  * EXEC works headless; BREAK needs a pty (debug.cpp:5410 isatty x3) and a
    LONG SETTLE both before it and after a campaign load (t283 run-5).
  * A BPLM fire prints seg 0000 (BPLM stores seg=0) -> printed address is
    USELESS; arm EXACTLY ONE breakpoint, treat any fire line as ours.
  * ARTIFACT LAW (debug.cpp:1048 stores baseline 0; :870 fires iff
    value != baseline): a byte that is NONZERO at arm time fires once
    spuriously ('00 -> xx') on its next ACCESS (read counts) -> reject once.
  * After any fire the CPU is STOPPED; ControlServer_Poll runs inside
    DEBUG_Loop (debug.cpp:5267) so registers/MEMDUMPBIN answer over the SAME
    socket. MEMDUMPBIN addressing is SELF-VERIFIED against the payload file.

TARGETS (resolved AFTER the ring scan, because every derived address needs
this session's own base B; pointer law CLOSED: linear == physical, payload at
P0 = B - 0x88, data segment at obj1 file offset 0x82bb0):

  data:OFF      byte at data-seg offset OFF (linear = B-0x88+0x82bb0+OFF).
                e.g. data:0x482fb = score_stars (t283 closed producer),
                     data:0x13bc5+0x5a form NOT supported — pre-add it.
  lin:ADDR      absolute guest-linear address (no derivation).
  heap-planets  the planet-list OBJECT discovered by its t249 OPEN-TIME
                signature ([o+0xab]==0 && byte[o+0xc5]==0 &&
                [o+0xbb]==0xffffffff && u16[o+0x8c9]==0x8d,
                docs/re/_wip_t249.md S2/S8) and watched at +0x8c7 (the u16
                item-count that IS the header "N Planets Occupied"). The
                object only exists AFTER the Planets screen has been opened
                once (t249: zero sig-hits in 20 never-opened slots), so this
                target mode clicks the sidebar button FIRST (window-rel
                (553,145), windows.txt NAME PLANETS rect 474,130-632,160 —
                the identical read-only click t249 ran on production), then
                re-scans the ring for the signature.

PHASES (--phases, comma list, run in order until one produces a fire):
  quiet   no injected input            c       'c' starmap overlay key
  turn    NEXTTURN click (511,67)      planets Planets-button click (553,145)
A fire in a named phase attributes the writer to that input.

--walk N after the first fire keeps EXEC RUNning and records (EIP, fire-line)
for N seconds: the heavy-debug check runs at the instruction-loop top
(core_normal.h:181), so the reported EIP is the instruction AFTER the store;
EIPs == one site = same instruction re-executed (a loop body).

SAFETY: scratch copy work/r1/game-wp only (asserted); OWN ring dir (TWO-WRITER
RING LAW); private Xvfb (never :9); core=normal; -time-limit always;
kill-by-recorded-PID in a finally. RESUME.GAM = md5-verified Oct-29 backup so
"Return to Current Game" enters a REAL campaign (t272: a title boot has no
image resident).

usage: r1_wp_session.py [--target data:0x482fb] [--port 55997] [--disp 97]
                        [--settle 45] [--phases quiet,c,turn] [--walk 0]
Exit 0 = non-artifact fire captured + register state banked.
     1 = ran with a negative (no fire in budget / campaign or object absent).
     2 = harness error.
"""
import argparse
import glob
import hashlib
import os
import pty
import re
import shutil
import signal
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
H = 0x88                                    # member offset -> image base
RETURN_TO_GAME = (318, 333)                 # window-rel, -nogui layout (t250)
NEXTTURN = (511, 67)                        # window-rel, -nogui (t245 law)
PLANETS_BTN = (553, 145)                    # window-rel (t249 live experiment)
RESEARCH_BTN = (553, 223)                   # window-rel (windows.txt RESEARCH rect)
XSEND = os.path.join(ROOT, "tools/xsend")

EVENTS = []
FIRE_RE = re.compile(r"Memory breakpoint.*?([0-9A-Fa-f]{2})\s*->\s*([0-9A-Fa-f]{2})")


def dspec(disp):
    """DISPLAY needs the colon ('97' reads as a hostname — t283 run-3 bug)."""
    return f":{str(disp).lstrip(':')}"


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


def grab(disp, path):
    r = subprocess.run(["import", "-window", "root", path],
                       capture_output=True, timeout=30,
                       env=dict(os.environ, DISPLAY=dspec(disp)))
    return r.returncode == 0


def diff_px(a, b):
    """ImageMagick `compare` AE count (no PIL system-wide — t283 run-4 trap)."""
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
    """Click 'Return to Current Game' until the screen RESPONDS (xsend rc=0
    proves SENT, not delivered — verify by screen diff, t244/t245 class)."""
    a = os.path.join(out, "screen_pre_click.png")
    b = os.path.join(out, "screen_post_click.png")
    for k in range(5):
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


def ring_mem(savedir, anch, log, budget=180.0):
    """Yield (B, mem, slot_path) for each readable ring slot until the budget
    produces one with a confident base vote (>=5)."""
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
                return votes.most_common(1)[0][0], mem, p
        time.sleep(5)
    return None, None, None


def sig_hits(mem):
    """t249 OPEN-TIME signature of the planet-list object:
    [o+0xab]==0 && byte[o+0xc5]==0 && [o+0xbb]==0xffffffff && u16[o+0x8c9]==0x8d."""
    hits = []
    for o in range(0, len(mem) - 0x8cf, 4):
        if struct.unpack_from("<H", mem, o + 0x8c9)[0] != 0x8d:
            continue
        if struct.unpack_from("<I", mem, o + 0xab)[0] != 0:
            continue
        if struct.unpack_from("<I", mem, o + 0xbb)[0] != 0xffffffff:
            continue
        if mem[o + 0xc5] != 0:
            continue
        hits.append(o)
    return hits


def resolve_target(spec, B, mem, out, log):
    """-> (linear, note, value_at_scan) or (None, reason, None)."""
    if spec.startswith("data:"):
        off = int(spec[5:], 16)
        lin = B - H + OBJ1_OFF + off
        val = mem[B + OBJ1_OFF + off]
        return lin, f"data offset {hex(off)}", val
    if spec.startswith("lin:"):
        lin = int(spec[4:], 16)
        val = mem[lin] if mem is not None and lin < len(mem) else None
        return lin, "absolute linear", val
    if spec == "heap-planets":
        hits = sig_hits(mem)
        log(f"heap-planets sig scan: {len(hits)} hits "
            f"{[hex(h) for h in hits]}")
        if len(hits) != 1:
            return None, f"expected exactly 1 planet-list object, got {hits}", None
        o = hits[0]
        cnt = struct.unpack_from("<H", mem, o + 0x8c7)[0]
        # OFF-BY-H FIX LAW (t286b MEASURED): sig_hits returns a RING-MEMBER
        # index; BPLM wants guest-LINEAR. linear == physical == member - 0x88
        # (pointer law CLOSED; self-proof: the widget's own +0xab slot holds
        # u32 0xfd9fec == 0xfda067-0x88 pointing at the object). The old
        # member-index form armed 0x88 too high and missed silently.
        return o - H + 0x8c7, f"planet-list OBJ={o:#x} count={cnt}", cnt & 0xFF
    if spec == "heap-planets-blind":
        # BLIND-ARM LAW (runs 1-6 MEASURED, CORRECTED t286b): the planet-list
        # object's RING-MEMBER index lands at 0xfda074 EVERY session at this
        # base (3/3 sig hits + t249's production and t1254's bank), i.e.
        # guest-LINEAR 0xfda074-0x88 = 0xfd9fec (off-by-H law; self-proof:
        # RAM u32 0xfd9fec stored at member 0xfda067 == 0xfd9fec+0x88, the
        # widget's list pointer). t286 run 10 armed the MEMBER index
        # 0xfda93b as a linear — 0x88 too high, silently missing every
        # refill write; that, not BPLM unreliability, is the run-10 zero.
        # The loaded campaign carries NO sig object (runs 2/3/4/5/6 PRE-ARM
        # 0 hits), so the slot byte is free-heap at arm time: baseline 0, no
        # '00 -> xx' artifact possible, and the FIRST fire IS the first
        # write — the open-click's alloc/zero/add path. Arming after the
        # object exists (runs 1/4) watches an orphan the UI never re-reads
        # (zero fires incl. reads — ALSO suspect the off-by-H now). GUARD:
        # only valid at --expect-base.
        o = 0xfda074 - H          # guest-linear base of the object
        # value read stays MEMBER-indexed (mem is the raw Memory member):
        val = mem[0xfda074 + 0x8c7] if mem is not None else None
        return (o + 0x8c7,
                "blind deterministic planet-list slot, linear = member-0x88 "
                "(valid only at expect-base)", val)
    return None, f"unknown target spec {spec!r}", None


def dump_stopped(req, out, B, log, eip=None, esp=None):
    """Read the stopped debugger's state over the SAME socket (t282 measured).
    Addressing self-verified: code window at EIP must equal payload bytes."""
    bank = os.path.join(out, "stopped-state.txt")
    with open(bank, "w") as tf:
        for cmd in ["BPLIST", "CPU", "EV eip", "EV cs", "EV ds", "EV es",
                    "EV ss", "EV esp", "EV eax", "EV ebx", "EV ecx", "EV edx",
                    "EV esi", "EV edi", "EV flags"]:
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
                         f"({len(got)} B) file off {eip - (B - H):#x}\n")
                log(f"MEMDUMPBIN code control MATCH={ctl} "
                    f"eip={eip:#x} file={eip - (B - H):#x}")
            else:
                tf.write("code dump file absent\n")
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


def fire_lines(path):
    if not os.path.exists(path):
        return []
    txt = open(path, "rb").read().decode("utf-8", "replace")
    return [l for l in txt.splitlines() if "Memory breakpoint" in l]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="data:0x482fb")
    ap.add_argument("--port", type=int, default=55997)
    ap.add_argument("--disp", default="97")
    ap.add_argument("--tl", type=int, default=1500)
    ap.add_argument("--settle", type=int, default=45)
    ap.add_argument("--boot", type=int, default=60)
    ap.add_argument("--campaign-wait", type=int, default=300)
    ap.add_argument("--fire-wait", type=int, default=480)
    ap.add_argument("--phase-wait", type=int, default=90)
    ap.add_argument("--turn-probe", type=int, default=60)
    ap.add_argument("--walk", type=int, default=0)
    ap.add_argument("--phases", default="")
    ap.add_argument("--pre-open-planets", action="store_true",
                    help="click the sidebar Planets button once after the "
                         "campaign load (read-only nav, t249 law). NOT used "
                         "by heap-planets any more: run-1 measured the sig "
                         "object present at first scan, so opening BEFORE "
                         "arming watches nothing — the planets PHASE click "
                         "is the instrumented open")
    ap.add_argument("--expect-base", default="",
                    help="hex B that the ring scan MUST report (determinism "
                         "guard for lin: targets — heap addrs are only "
                         "meaningful at the expected base); mismatch = abort")
    ap.add_argument("--no-break", action="store_true",
                    help="DEAD (run-8 MEASURED): arms fine, event happens, "
                         "zero fire lines — the fire path needs BREAK. Kept "
                         "for provenance; do not use.")
    ap.add_argument("--break-early", action="store_true",
                    help="BREAK at the QUIESCENT TITLE SCREEN right after "
                         "boot (t282's best-measured survival class: 3/3 "
                         "with settle, vs post-load 2/6 in t286), arm the "
                         "FIXED-address target there, EXEC RUN, then enter "
                         "the campaign and run phases. Requires a target "
                         "that needs no base: heap-planets-blind or lin:.")
    args = ap.parse_args()

    for p, why in [(DBG_BIN, "debugger binary"), (SCRATCH, "scratch copy"),
                   (PAYLOAD, "payload"), (OCT29, "Oct-29 campaign backup")]:
        if not os.path.exists(p):
            print(f"HARNESS ERROR: missing {why} {p}")
            return 2
    if os.path.abspath(SCRATCH).startswith(os.path.join(ROOT, "game") + os.sep):
        print("HARNESS ERROR: refusing to mount game/")
        return 2
    if hashlib.md5(open(OCT29, "rb").read()).hexdigest() != OCT29_MD5:
        print("HARNESS ERROR: Oct-29 backup md5 mismatch")
        return 2
    if args.target == "heap-planets-blind" and not args.expect_base:
        print("HARNESS ERROR: heap-planets-blind REQUIRES --expect-base "
              "(the address is only valid at the base it was measured at)")
        return 2

    tag = args.target.replace(":", "-").replace("/", "-")
    out = os.path.join(ROOT, "work/r1",
                       f"wp-{tag}-{time.strftime('%Y%m%d-%H%M%S')}")
    os.makedirs(out, exist_ok=True)
    # `-savedir` does NOT mkdir and the autosave failure kills the window
    # (t283 run-2) — the dir MUST pre-exist. OWN dir = TWO-WRITER RING LAW.
    savedir = os.path.join(out, "save")
    os.makedirs(savedir, exist_ok=True)
    runlog_path = os.path.join(out, "session.log")
    transcript = os.path.join(out, "mcp-transcript.txt")
    ptylog = os.path.join(out, "mcp-pty.log")
    conf = os.path.join(out, "wp.conf")

    def log(msg):
        line = f"{time.strftime('%H:%M:%S')} {msg}"
        print(line, flush=True)
        with open(runlog_path, "a") as fh:
            fh.write(line + "\n")

    shutil.copy2(OCT29, os.path.join(SCRATCH, "RESUME.GAM"))
    low = os.path.join(SCRATCH, "resume.gam")
    if os.path.exists(low):
        os.rename(low, low + ".vendor-wp")
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

        log(f"settling {args.settle}s before the resume click")
        time.sleep(args.settle)

        def do_break():
            """BREAK with the t283 retry law; returns True if the debugger
            stopped (BPLIST answers)."""
            hdr = None
            for attempt in range(3):
                lines, ok, hdr = req("BREAK", 60.0)
                log(f"BREAK#{attempt} hdr={hdr} frame_ok={ok} lines={lines[:5]}")
                if hdr is not None and not hdr.rstrip().endswith("ERR"):
                    return True
                hdr = None
                lines, ok, _ = req("PING", 15.0)
                if "PONG" not in " ".join(lines):
                    log(f"BREAK#{attempt}: channel dead (no PONG)")
                    break
                time.sleep(10.0)
            log("trying VRT (run-then-stop at next retrace) instead of BREAK")
            lines, ok, hdr2 = req("EXEC VRT", 45.0)
            log(f"VRT hdr={hdr2} lines={lines[:5]}")
            time.sleep(3.0)
            lines, ok, hdr = req("EXEC BPLIST", 20.0)
            if hdr is None:
                log("NEGATIVE: neither BREAK nor VRT stopped the debugger")
                return False
            log("VRT stopped the debugger (BPLIST answers)")
            return True

        def arm_bp():
            """Arm EXACTLY ONE BPLM at `lin`; returns True on success."""
            lines, ok, hdr = req(f"EXEC BPLM {lin:08X}", 15.0)
            log(f"arm BPLM {lin:08X} hdr={hdr} lines={lines}")
            lines, ok, hdr = req("EXEC BPLIST", 10.0)
            armed = [l for l in lines if "BPLM" in l]
            log(f"armed: {armed}")
            if len(armed) != 1:
                log(f"NEGATIVE: expected exactly 1 armed BPLM, got {armed}")
                return False
            return True

        lin = None
        seen = []
        if args.break_early:
            # t286 law: post-load BREAK died 4/6 even with settle; the title
            # screen is t282's 3/3 class. Arm the FIXED target before the
            # campaign exists, RUN, then enter + phases.
            if args.target not in ("heap-planets-blind",) \
                    and not args.target.startswith("lin:"):
                log("NEGATIVE: --break-early needs a base-free target "
                    "(heap-planets-blind or lin:ADDR)")
                return 1
            lin, note, val = resolve_target(args.target, 0, None, out, log)
            if lin is None:
                log(f"NEGATIVE: target unresolved — {note}")
                return 1
            log(f"EARLY TARGET {args.target}: linear={lin:#08x} ({note})")
            if not do_break():
                return 1
            # artifact logic needs the byte value at arm time; the debugger
            # is STOPPED here, so MEMDUMPBIN (seg 0000 = linear, t283
            # self-verified) answers. Failure => val None => no artifact
            # rejection (a '00 -> xx' first fire would then be kept — the
            # entry loop drains boot-stage fires separately).
            f0 = os.path.join(out, "byte_at_arm.bin")
            lines, ok, hdr = req(f"EXEC MEMDUMPBIN 0000:{lin:08X} 1 {f0}", 15.0)
            if os.path.exists(f0) and os.path.getsize(f0) == 1:
                val = open(f0, "rb").read()[0]
                log(f"EARLY byte at arm = {val} ({val:#x})")
            else:
                val = None
                log(f"EARLY byte at arm: MEMDUMPBIN failed (hdr={hdr}) — "
                    "no artifact rejection this run")
            if not arm_bp():
                return 1
            seen = fire_lines(ptylog)
            lines, ok, hdr = req("EXEC RUN", 10.0)
            log(f"EARLY RUN hdr={hdr} — entering campaign with bp armed")
            # entry with FIRE WATCH: a boot-time write to the watched slot
            # stops the CPU mid-entry, the screen would never react, and the
            # plain enter_campaign would burn 10 minutes false-negativ-ing.
            # Drain fires inside the loop: log (with eip), RUN, keep waiting.
            a = os.path.join(out, "screen_pre_click.png")
            b = os.path.join(out, "screen_post_click.png")
            grab(args.disp, a)
            entered = False
            t0 = time.time()
            last_click = 0.0
            while time.time() - t0 < 240 and not entered:
                cur = fire_lines(ptylog)
                new = [l for l in cur if l not in seen]
                if new:
                    seen = cur
                    for l in new:
                        le, _, _ = req("EXEC EV eip", 8.0)
                        nums = [x.strip() for x in le if x.strip()]
                        log(f"BOOT/LOAD FIRE eip={nums[-1] if nums else '?'}: {l}")
                        with open(os.path.join(out, "boot-fires.txt"), "a") as bf:
                            for l2 in new:
                                bf.write((nums[-1] if nums else "?") + " " + l2 + "\n")
                    lines, ok, hdr = req("EXEC RUN", 10.0)
                    if hdr is None:
                        log("NEGATIVE: channel dead after boot fire")
                        return 1
                    continue
                if time.time() - last_click > 20:
                    xsend(args.disp, ["click", str(RETURN_TO_GAME[0]),
                                 str(RETURN_TO_GAME[1])], log)
                    last_click = time.time()
                time.sleep(2.0)
                if grab(args.disp, b) and diff_px(a, b) > 2000:
                    entered = True
                    shutil.copy2(b, os.path.join(out, "screen_entered_early.png"))
                    log("ENTER(early): screen reacted — campaign load presumed")
            if not entered:
                log("NEGATIVE: early-armed entry never showed a screen change")
                return 1

        if not args.break_early:
            if not enter_campaign(out, args.disp, log):
                log("NEGATIVE: campaign entry click never moved the screen")
                return 1

        pay = open(PAYLOAD, "rb").read()
        anch = SS.build_anchors(pay)
        B, mem, slot = ring_mem(savedir, anch, log, budget=args.campaign_wait)
        if B is None:
            log("NEGATIVE: campaign never entered (payload image not resident "
                "in this session's ring)")
            shutil.copytree(savedir, os.path.join(out, "ring-negative"),
                            dirs_exist_ok=True)
            return 1
        log(f"ring {os.path.basename(slot or '?')}: B={B:#x} P0={B-H:#x}")
        if args.expect_base and B != int(args.expect_base, 16):
            log(f"NEGATIVE: --expect-base {args.expect_base} != scanned "
                f"B={B:#x} — heap-derived addresses invalid, aborting")
            return 1
        # control scan: does the planet-list sig object ALREADY exist before
        # any planets click? (runs 2-6: the loaded campaign carries NO sig
        # object — a hit here means THIS session already opened the screen.)
        pre = sig_hits(mem)
        log(f"PRE-ARM sig-object count: {len(pre)} {[hex(h) for h in pre]}")

        if args.pre_open_planets or (args.target == "heap-planets"
                                     and not pre):
            # run-2 MEASURED: the loaded campaign has NO sig object (PRE-ARM
            # 0 hits — run-1's object was created by run-1's click), and a
            # single click ~1 s after the ENTER reaction can land mid-load and
            # be SWALLOWED (12 s later: still 0 hits). Retry until the
            # signature appears — verify by evidence, not by xsend rc.
            obj = []
            a = os.path.join(out, "screen_pre_planetsclick.png")
            grab(args.disp, a)
            for i in range(10):
                xsend(args.disp, ["click", str(PLANETS_BTN[0]),
                                  str(PLANETS_BTN[1])], log)
                for k in range(4):
                    time.sleep(5.0)
                    B2, mem, slot = ring_mem(savedir, anch, log, budget=20.0)
                    if B2 is None:
                        continue
                    if B2 != B:
                        log(f"NEGATIVE: base moved {B:#x} -> {B2:#x} "
                            "(campaign swap? t285 class) — aborting")
                        return 1
                    obj = sig_hits(mem)
                    if obj:
                        break
                if obj:
                    log(f"sig object appeared after click {i}: {[hex(h) for h in obj]}")
                    break
                b = os.path.join(out, f"screen_planetsclick_{i}.png")
                if grab(args.disp, b):
                    log(f"creation click {i}: no sig object yet "
                        f"(panel diff {diff_px(a, b)} px)")
            if not obj:
                log("NEGATIVE: 10 planets clicks, sig object never appeared")
                return 1

        if not args.break_early:
            lin, note, val = resolve_target(args.target, B, mem, out, log)
            if lin is None:
                log(f"NEGATIVE: target unresolved — {note}")
                return 1
            log(f"TARGET {args.target}: linear={lin:#08x} ({note}) "
                f"value_at_scan={val}")

            # ---- BREAK (settle law AFTER the load too — t283 run-5) -------
            lines, ok, hdr = req("PING", 10.0)
            if "PONG" not in " ".join(lines):
                log("NEGATIVE: dead after campaign load (no PONG)")
                return 1
            if args.no_break:
                log("--no-break: skipping BREAK entirely (EXEC-only mode)")
            else:
                log(f"post-load settle {args.settle}s before BREAK")
                time.sleep(args.settle)
                if not do_break():
                    return 1
            if not arm_bp():
                return 1

        tf = open(transcript, "w")
        tf.write(f"t286 watchpoint session {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        tf.write(f"target={args.target} B={B:#x} linear={lin:#08x} "
                 f"({note}) value_at_scan={val} slot={slot} "
                 f"break_early={args.break_early}\n")

        # ARTIFACT LAW (debug.cpp:1048 stores baseline 0; :870 fires iff
        # value != baseline): if the byte is NONZERO at arm time, its very
        # next ACCESS — read OR write — fires once as '00 -> <current>'
        # (t283's run-6 comment claims a first fire was a baseline artifact
        # with value 00 at scan; that shape can only mean the byte was
        # nonzero between scan and arm, or the fire was real — do not reuse
        # that reasoning). Reject exactly ONE '00 -> xx'; 'xx -> 00' and
        # 'xx -> yy' are real stores.
        expect_artifact = (val is not None and (val & 0xFF) != 0)

        def inject(phase):
            if child.poll() is not None:
                return
            if phase == "c":
                xsend(args.disp, ["key", "c"], log)
            elif phase == "turn":
                xsend(args.disp, ["click", str(NEXTTURN[0]),
                                  str(NEXTTURN[1])], log)
            elif phase == "planets":
                # run-4 MEASURED: consecutive sidebar clicks DRILL IN (list
                # -> planet detail view), they are not open/close toggles.
                xsend(args.disp, ["click", str(PLANETS_BTN[0]),
                                  str(PLANETS_BTN[1])], log)
                inject.n += 1
            elif phase == "reopen":
                # neutral starmap spot first (exit whatever mode is showing),
                # THEN the Planets button: every planets click comes from a
                # known non-planets panel state (run-4 lesson).
                xsend(args.disp, ["click", "200", "300"], log)
                time.sleep(6.0)
                xsend(args.disp, ["click", str(PLANETS_BTN[0]),
                                  str(PLANETS_BTN[1])], log)
                inject.n += 1
            elif phase == "mixed":
                xsend(args.disp, ["key", "c"], log)
                xsend(args.disp, ["click", str(NEXTTURN[0]),
                                  str(NEXTTURN[1])], log)
        inject.n = 0

        phases = [p.strip() for p in args.phases.split(",") if p.strip()] \
            or ["mixed"]
        fires = []
        seen = fire_lines(ptylog)          # anything before arming is not ours
        for phase in phases:
            budget = args.phase_wait if args.phases else args.fire_wait
            log(f"PHASE {phase!r}: budget {budget}s")
            lines, ok, hdr = req("PING", 10.0)
            if "PONG" in " ".join(lines):
                # running: EXEC RUN is a harmless no-op ack (t282: parser
                # accepts RUN while running)
                pass
            lines, ok, hdr = req("EXEC RUN", 10.0)
            if hdr is None:
                log("NEGATIVE: channel dead at RUN")
                break
            t0 = time.time()
            last_inject = 0.0
            iv = 15 if phase in ("c", "turn", "planets") else 45
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
                time.sleep(2.0)
            if fires:
                break
        tf.write("\n=== fires: " + repr(fires) + "\n")
        tf.flush()

        if not fires:
            log("NEGATIVE: no non-artifact fire in any phase (phase budgets "
                "banked) — writer still unwitnessed for this target")
            grab(args.disp, os.path.join(out, "screen_after_phases.png"))
            postB, post_mem, _ = ring_mem(savedir, anch, log, budget=30.0)
            if post_mem is not None:
                post = sig_hits(post_mem)
                log(f"POST-PHASES sig-object count: {len(post)} "
                    f"{[hex(h) for h in post]}")
                with open(transcript, "a") as _tf:
                    _tf.write(f"post sig hits: {[hex(h) for h in post]}\n")
            tf.close()
            shutil.copytree(savedir, os.path.join(out, "ring-final"),
                            dirs_exist_ok=True)
            return 1

        phase, real = fires[0]
        log(f"REAL FIRE in phase {phase!r}: {real}")
        if args.no_break:
            # did the fire STOP the CPU (heavy-check path) or only print?
            lines, ok, hdr = req("PING", 10.0)
            pong = "PONG" in " ".join(lines)
            log(f"no-break post-fire PING -> {hdr} pong={pong}")
            with open(transcript, "a") as _tf:
                _tf.write(f"post-fire PONG={pong} hdr={hdr}\n")
            if pong:
                lines, ok, hdr = req("EXEC EV eip", 10.0)
                log(f"no-break EXEC EV eip -> hdr={hdr} {lines}")
                with open(transcript, "a") as _tf:
                    _tf.write(f"post-fire EV eip hdr={hdr}: {lines}\n")

        walk = []
        if args.walk:
            log(f"WALK: {args.walk}s of RUN/fire cycles (EIP = insn AFTER "
                "the store, core_normal.h:181)")
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
                            le, _, _ = req("EXEC EV eip", 8.0)
                            nums = [x.strip() for x in le if x.strip()]
                            eip_s = nums[-1] if nums else "?"
                            walk.append((eip_s, l))
                            log(f"WALK FIRE eip={eip_s}: {l}")
                        break
                    time.sleep(1.0)
                if args.turn_probe and child.poll() is None:
                    # after a planets/reopen fire, the useful NEXT event is
                    # ANOTHER open (walk the refill cadence), not end-turn
                    if phase in ("planets", "reopen"):
                        inject("reopen")
                    else:
                        xsend(args.disp, ["click", str(NEXTTURN[0]),
                                          str(NEXTTURN[1])], log)
            tf.write("\n=== walk fires (%d):\n" % len(walk))
            for w_ in walk:
                tf.write("  " + (w_[0] + " " if isinstance(w_, tuple)
                                 else "") +
                         (w_[1] if isinstance(w_, tuple) else w_) + "\n")
            tf.flush()

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
