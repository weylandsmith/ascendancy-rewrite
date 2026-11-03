#!/usr/bin/env python3
"""t282: bring up the debugger build on a SCRATCH copy and capture the LIVE
debugger command list + prove BPLM/BPPM/BPM are accepted.

WHY BOTH A PTY AND THE MCP SOCKET (source-cited, do not "simplify" one away):
  * mcp_server=<port> makes dosbox-x CONNECT OUT to us (debug_mcp.cpp
    CONTROL_HOST + SDLNet_TCP_Open). Command injection + output capture are
    headless-clean: every DEBUG_ShowMsg line during an EXEC is routed to the
    response (debug_gui.cpp:786) and paged content is suppressed so HELP does
    not hang on the pager (debug_gui.cpp:685/700).
  * BUT entering the debugger is tty-gated on Linux: DEBUG_EnableDebugger ->
    DEBUG_Enable_Handler, debug.cpp:5410 `if (!isatty(0)||!isatty(1)||!isatty(2))
    { LOG_MSG("Debugger is not available unless you start DOSBox-X from a
    terminal"); return; }`. So without a pty the CPU never stops and a
    watchpoint fire has nowhere to land.
  => pty for the tty gate, socket for the words. The pty's curses redraw spam
     is drained to a file and never parsed.

SAFETY (inherits the R1 runbook, docs/BLOCKED.md):
  * mounts work/r1/game-wp (SCRATCH). NEVER game/. Checked at startup, hard exit.
  * OWN ring/captures dir under the run dir (two-writer law, t266).
  * own Xvfb on a private display number; never :9 (production).
  * -time-limit always; kill by RECORDED PID (os.kill), never pkill -f.
  * core=normal (VOGONS: dyn cores skip instructions under stepping/watchpoints).
  * teardown runs in a finally block: an exception mid-session must not leave a
    stray dosbox-x or Xvfb running (a stray second dosbox on a shared ring is
    the t266 corruption shape).

Usage: scripts/r1_t282_dbx_probe.py [--port 55991] [--boot 60] [--disp 97]
Exit: 0 = HELP captured AND BPLM accepted; 1 = ran with a negative; 2 = harness.
"""
import argparse
import os
import pty
import signal
import socket
import subprocess
import sys
import threading
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DBG_BIN = os.path.join(ROOT, "work/r1/bin/dosbox-x-dbg")
SCRATCH = os.path.join(ROOT, "work/r1/game-wp")

# Unsolicited 'BEGIN event OK ... END event' frames land here.
EVENTS = []


def read_until_end(f, end_marker, budget):
    """Return (lines, got_end, header). OK/ERR lives ONLY in the BEGIN header.

    NOTE: conn.makefile() gives a BufferedRWPair with NO settimeout() — the
    timeout belongs on the SOCKET (set it once after accept); the file object
    inherits it and raises socket.timeout on a short read.
    """
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
    """Keep the pty master empty so curses writes never block the child."""
    with open(path, "wb") as fh:
        while True:
            try:
                data = os.read(master_fd, 65536)
            except OSError:
                return
            if not data:
                return
            fh.write(data)
            fh.flush()   # the fire test tails this file while we run
            fh.flush()   # the fire test tails this file while we run


def kill_rec(pid, name):
    try:
        os.kill(pid, signal.SIGKILL)
        print(f"[teardown] SIGKILL {name} pid={pid}", flush=True)
    except ProcessLookupError:
        print(f"[teardown] {name} pid={pid} already gone", flush=True)


def fire_test(req, ptylog_path):
    """End-to-end sanity: does a BPLM actually STOP the CPU?

    Target = guest PHYSICAL 0x46C, the BIOS 32-bit timer tick counter (ticks at
    ~55 ms). It is the cheapest guaranteed-changing address in the machine, so a
    build whose watchpoint path is broken shows up as ZERO fires in the budget.
    BPLM is checked with mem_readb_checked(address) directly (debug.cpp:864-869),
    i.e. the operand is used as a physical/linear Bitu.
    Returns (fired: bool, detail: str).
    """
    lines, ok, hdr = req("EXEC BPLM 0000046C")
    print(f"[fire] arm BPLM 0x46C -> {lines}", flush=True)
    lines, ok, hdr = req("EXEC BPLIST")
    armed = [l for l in lines if "BPLM" in l]
    print(f"[fire] armed as: {armed}", flush=True)
    if not armed:
        return False, "BPLM not armed"

    # RUN is a resume command: ACKed on ACCEPTANCE (debug_mcp.cpp:126), so this
    # reply carries no post-resume state. The fire line goes to the pty.
    lines, ok, hdr = req("EXEC RUN", 10.0)
    print(f"[fire] RUN -> hdr={hdr} lines={lines}", flush=True)

    t0 = time.time()
    budget = 40.0
    while time.time() - t0 < budget:
        time.sleep(2.0)
        lines, ok, hdr = req("EXEC BPLIST", 8.0)
        cur = [l for l in lines if "BPLM" in l]
        txt = open(ptylog_path, "rb").read().decode("utf-8", "replace") \
            if os.path.exists(ptylog_path) else ""
        nfires = txt.count("Memory breakpoint")
        print(f"[fire] t+{time.time()-t0:4.1f}s bplm={cur} "
              f"fire_lines_in_pty={nfires}", flush=True)
        if nfires:
            tail = [l for l in txt.splitlines() if "Memory breakpoint" in l][-3:]
            return True, "; ".join(tail)
        if not cur and "BPLM" not in " ".join(lines):
            # BPLIST came back empty/absent -> either BPDEL ran or the child died
            pass
    return False, f"no fire within {budget:.0f}s"


def session(conn, out, transcript, do_fire=False, settle=45):
    """Drive the MCP channel. Returns rc."""
    conn.settimeout(0.5)
    f = conn.makefile("rwb")
    seq = [0]

    def req(verb, budget=30.0):
        seq[0] += 1
        rid = str(seq[0])
        try:
            f.write(f"REQ {rid} {verb}\n".encode())
            f.flush()
        except OSError as e:            # emulator crashed mid-session
            print(f"[req] channel dead ({e}) at {verb!r}", flush=True)
            return [], False, None
        return read_until_end(f, f"END {rid}", budget)

    lines, ok, hdr = req("PING", 10.0)
    print(f"[PING] hdr={hdr} frame_ok={ok} lines={lines}", flush=True)
    if "PONG" not in " ".join(lines):
        print("NEGATIVE: no PONG")
        return 1

    # BREAK TIMING LAW (MEASURED 2026-11-02, run t282-probe-20261102-232519):
    # issuing BREAK ~1 s after the channel comes up ABORTS the emulator with
    # glibc "corrupted double-linked list" (see pty.log tail). Issued after the
    # machine has settled it works (run -232113, +9 s). So: settle first.
    print(f"[probe] settling {settle}s before BREAK", flush=True)
    time.sleep(settle)
    lines, ok, hdr = req("BREAK", 25.0)
    print(f"\n[BREAK] hdr={hdr} frame_ok={ok} {len(lines)} lines", flush=True)
    for l in lines[:20]:
        print("   ", l)
    if hdr is None:
        print("NEGATIVE: channel died at BREAK (see the BREAK TIMING LAW above)")
        return 1

    cmds = ["HELP", "BPLIST", "BPLM 00FA0000", "BPLIST",
            "BPPM 0040:0000", "BPLIST", "BPM 0040:0010", "BPLIST",
            "BPDEL *", "BPLIST"]
    results = {}
    with open(transcript, "w") as tf:
        tf.write(f"t282 live MCP transcript  {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        tf.write(f"BREAK hdr={hdr} lines={lines}\n")
        for c in cmds:
            lines, ok, hdr = req(f"EXEC {c}")
            err = bool(hdr) and hdr.rstrip().endswith("ERR")
            nr = any("not recognized" in l.lower() for l in lines)
            results[c] = dict(err=err, unrecognized=nr, n=len(lines), hdr=hdr)
            tf.write(f"\n=== EXEC {c} hdr={hdr} frame_ok={ok} err={err} "
                     f"unrecognized={nr} lines={len(lines)}\n")
            for l in lines:
                tf.write(l + "\n")
            tf.flush()
            print(f"\n=== EXEC {c!r} hdr={hdr} err={err} unrecognized={nr} "
                  f"lines={len(lines)}", flush=True)
            for l in lines[:10]:
                print("   ", l)

    h = results.get("HELP", {})
    help_ok = h.get("n", 0) > 20 and not h.get("unrecognized", True)
    def acc(c):
        r = results.get(c)
        return bool(r) and not r["unrecognized"]
    print(f"\nVERDICT: HELP live={help_ok} ({h.get('n')} lines)  "
          f"BPLM accepted={acc('BPLM 00FA0000')}  "
          f"BPPM accepted={acc('BPPM 0040:0000')}  "
          f"BPM accepted={acc('BPM 0040:0010')}", flush=True)
    print(f"VERDICT: BPLIST line counts before/after BPLM: "
          f"{[results[c]['n'] for c in cmds if c == 'BPLIST']}", flush=True)
    rc = 0 if (help_ok and acc("BPLM 00FA0000")) else 1
    if do_fire:
        fired, detail = fire_test(req, os.path.join(out, "pty.log"))
        print(f"VERDICT: WATCHPOINT FIRED={fired}  detail: {detail}", flush=True)
        if not fired:
            rc = 1
    return rc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=55991)
    ap.add_argument("--boot", type=int, default=60,
                    help="seconds to give dosbox-x to connect OUT")
    ap.add_argument("--disp", default="97", help="private Xvfb display number")
    ap.add_argument("--tl", type=int, default=240, help="-time-limit seconds")
    ap.add_argument("--settle", type=int, default=45,
                    help="seconds after connect before BREAK (see BREAK TIMING LAW)")
    ap.add_argument("--fire", action="store_true",
                    help="after the command sweep, arm BPLM on guest phys 0x46C "
                         "(BIOS tick counter) and prove the CPU actually stops")
    args = ap.parse_args()

    if not os.path.exists(DBG_BIN):
        print(f"HARNESS ERROR: missing {DBG_BIN}")
        return 2
    if not os.path.exists(os.path.join(SCRATCH, "ascend.exe")):
        print(f"HARNESS ERROR: scratch copy missing at {SCRATCH}")
        return 2

    out = os.path.join(ROOT, "work/r1",
                       f"t282-probe-{time.strftime('%Y%m%d-%H%M%S')}")
    os.makedirs(out, exist_ok=True)
    transcript = os.path.join(out, "mcp-transcript.txt")
    ptylog = os.path.join(out, "pty.log")
    conf = os.path.join(out, "wp.conf")

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
        [DBG_BIN, "-conf", conf, "-nogui", "-time-limit", str(args.tl)],
        stdin=slave, stdout=slave, stderr=slave, cwd=out, env=env,
        close_fds=True)
    os.close(slave)
    print(f"[probe] dosbox-x-dbg pid={child.pid} display=:{args.disp} "
          f"mcp={args.port} out={out}", flush=True)

    rc = 1
    conn = None
    try:
        t0 = time.time()
        while time.time() - t0 < args.boot:
            try:
                conn, addr = ls.accept()
                print(f"[probe] connected OUT from {addr} "
                      f"after {time.time()-t0:.1f}s", flush=True)
                break
            except socket.timeout:
                if child.poll() is not None:
                    print(f"[probe] child exited early rc={child.returncode}")
                    break
        if conn is None:
            print("NEGATIVE: dosbox-x never connected to the MCP port")
        else:
            try:
                rc = session(conn, out, transcript, do_fire=args.fire, settle=args.settle)
            finally:
                conn.close()
    finally:
        kill_rec(child.pid, "dosbox-x-dbg")
        kill_rec(xv.pid, "Xvfb")
        ls.close()
        try:
            os.close(master)
        except OSError:
            pass
    if os.path.exists(ptylog):
        print(f"[probe] pty.log={os.path.getsize(ptylog)} B transcript={transcript}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
