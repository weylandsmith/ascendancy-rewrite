#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t282/t286: DOSBox-X debugger MCP control channel — LISTENER side.

DIRECTION LAW (read the source before trusting the README's phrasing):
dosbox-x does NOT listen on `mcp_server=<port>`. src/debug/debug_mcp.cpp
CONTROL_HOST="127.0.0.1" + SDLNet_TCP_Open means the EMULATOR connects OUT to
us and retries every 1000 ms while we are down. So this tool must be
LISTENING BEFORE dosbox-x starts, or the first commands are simply never sent.

Protocol (line text, not JSON; debug_mcp.cpp ParseControlRequest/SendResponse):
    REQ <id> PING                -> BEGIN <id> OK / PONG / END <id>
    REQ <id> BREAK               -> enter the debugger (tty-gated UI! see below)
    REQ <id> EXEC <debugger cmd> -> runs one command, response carries every
                                    DEBUG_ShowMsg line the command printed
    response framing: BEGIN <id> OK|ERR\\n<lines>\\nEND <id>
    events:           BEGIN event OK\\n<event> <data>\\nEND event

Resume asymmetry (IsResumeDebuggerCommand): RUN/RUNWATCH/VRT are answered OK on
ACCEPTANCE (emulation resumes), so the reply has NO post-resume state — read
registers with a later EXEC after the watchpoint fires.

BREAK caveat: DEBUG_Enable_Handler() (debug.cpp:5410) refuses on Linux unless
stdin/stdout/stderr are ALL ttys. Headless runs therefore drive the debugger
through EXEC only (the command parser itself is not tty-gated) — which is what
this tool defaults to.

Usage:
    scripts/r1_mcp_dbg.py --port 55999 --cmd HELP [--cmd BPLIST ...]
    scripts/r1_mcp_dbg.py --port 55999 --cmd-file cmds.txt --out out.txt
    scripts/r1_mcp_dbg.py --port 55999 --wait-only     # just accept + PING loop

Exit: 0 all requested commands returned OK-ish; 1 a command returned ERR or no
connection within the budget; 2 usage/harness error.
"""
import argparse
import socket
import sys
import time

MAX_RECV = 4 << 20

# Unsolicited 'BEGIN event OK ... END event' frames land here.
EVENTS = []


def read_until_end(f, end_marker, budget, t_start):
    """Read lines until `end_marker` line seen or budget exhausted.

    Returns (lines, got_end, header) where header is the 'BEGIN <id> OK|ERR'
    line — the OK/ERR flag lives ONLY there, so callers must look at it rather
    than assuming a well-framed reply means success.
    """
    lines = []
    header = None
    f.settimeout(0.5)
    while time.time() - t_start < budget:
        try:
            raw = f.readline()
        except socket.timeout:
            continue
        except OSError:
            continue
        if not raw:                      # peer closed
            return lines, False, header
        line = raw.decode("utf-8", "replace").rstrip("\r\n")
        if line == end_marker:
            return lines, True, header
        if line.startswith("BEGIN event"):
            # unsolicited event frame: "BEGIN event OK\n<event> <data>\nEND event"
            ev, _, _ = read_until_end(f, "END event", 2.0, time.time())
            EVENTS.extend(ev)
            continue
        if line.startswith("BEGIN "):
            header = line
            continue
        if line:
            lines.append(line)
    return lines, True, header


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, required=True)
    ap.add_argument("--cmd", action="append", default=[],
                    help="debugger command to EXEC (repeatable)")
    ap.add_argument("--cmd-file", help="file of debugger commands, one per line")
    ap.add_argument("--wait-only", action="store_true",
                    help="accept, PING once, dump anything that arrives, exit")
    ap.add_argument("--listen-timeout", type=float, default=120.0,
                    help="seconds to wait for dosbox-x to connect OUT to us")
    ap.add_argument("--resp-budget", type=float, default=20.0)
    ap.add_argument("--out", help="also write transcript here")
    args = ap.parse_args()

    cmds = list(args.cmd)
    if args.cmd_file:
        with open(args.cmd_file) as fh:
            cmds += [l.strip() for l in fh if l.strip() and not l.startswith("#")]

    out = open(args.out, "w") if args.out else None

    def say(s):
        print(s)
        if out:
            out.write(s + "\n")
            out.flush()

    ls = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ls.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        ls.bind(("127.0.0.1", args.port))
    except OSError as e:
        say(f"HARNESS ERROR: bind 127.0.0.1:{args.port}: {e}")
        return 2
    ls.listen(1)
    say(f"[listener] bound 127.0.0.1:{args.port} waiting for dosbox-x to connect OUT "
        f"(budget {args.listen_timeout:.0f}s)")

    ls.settimeout(min(5.0, args.listen_timeout))
    conn = None
    addr = None
    t0 = time.time()
    while time.time() - t0 < args.listen_timeout:
        try:
            conn, addr = ls.accept()
            break
        except socket.timeout:
            continue
    if conn is None:
        say(f"NEGATIVE: no connection from dosbox-x within {args.listen_timeout:.0f}s")
        return 1
    say(f"[listener] connected from {addr}")

    f = conn.makefile("rwb")
    rc = 0
    seq = 0

    def request(verb, budget=None):
        """Send `REQ <id> <verb...>`; verb is PING|BREAK|EXEC <cmd>."""
        nonlocal seq
        seq += 1
        rid = f"{seq}"
        line = f"REQ {rid} {verb}"
        f.write((line.replace("\n", " ") + "\n").encode())
        f.flush()
        lines, ok, hdr = read_until_end(f, f"END {rid}",
                                        budget or args.resp_budget, time.time())
        return rid, lines, ok, hdr

    rid, lines, ok, hdr = request("PING")
    say(f"[PING] rid={rid} frame_ok={ok} header={hdr!r} lines={lines}")
    if not lines or "PONG" not in " ".join(lines):
        say("NEGATIVE: PING did not return PONG")
        return 1

    if args.wait_only:
        # dump whatever the emulator emits unprompted (startup chatter)
        read_until_end(f, "<<none>>", 3.0, time.time())
        for l in EVENTS[-200:]:
            say(f"[event] {l}")
        conn.close()
        ls.close()
        if out:
            out.close()
        return 0

    for c in cmds:
        t1 = time.time()
        rid, lines, ok, hdr = request(f"EXEC {c}")
        err_flag = bool(hdr) and hdr.rstrip().endswith("ERR")
        head = [l for l in lines if "not recognized" in l.lower()]
        say(f"\n=== EXEC {c!r} -> header={hdr!r} frame_ok={ok} "
            f"({time.time()-t1:.1f}s, {len(lines)} lines) "
            f"{'*** NOT RECOGNIZED ***' if head else ''}")
        if head or err_flag or not ok:
            rc = 1
        for l in lines:
            say(f"  {l}")

    conn.close()
    ls.close()
    if out:
        out.close()
    return rc


if __name__ == "__main__":
    sys.exit(main())
