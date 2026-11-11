#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""R1 tracer probe + capture (option C cadence; docs/BLOCKED.md Resolution).

Attempts to seize/attach a running dosbox-x to dump guest RAM and locate the
ascend.exe payload (work/ascend_payload.bin head). If tracing is possible,
optionally dumps the large writable regions into --dump-dir.

Design rules (the 12 GB incident, STATE.md DOSBOX RULE):
  - the child is ALWAYS killed by its tracked PID (never pkill -f),
  - all waits are WNOHANG polls with hard deadlines, never blocking,
  - dosbox runs headless: output=dummy, nosound, stdin=/dev/null, -time-limit.

Exit 0 = attempt ran (outcome in stdout: TRACABLE=yes|no). Exit 2 = harness
error (the probe itself is broken — that needs a human, not a retry).
"""
import argparse, os, signal, subprocess, sys, time

PTRACE_ATTACH, PTRACE_DETACH, PTRACE_SEIZE = 16, 17, 0x4206

import ctypes
libc = ctypes.CDLL("libc.so.6", use_errno=True)
def estr(): return os.strerror(ctypes.get_errno())

def seize_or_attach(pid, deadline):
    """Return ('seized'|'attached', None) or (None, reason). Non-blocking wait."""
    for req, name in ((PTRACE_ATTACH, "attached"), (PTRACE_SEIZE, "seized")):
        ctypes.set_errno(0)
        r = libc.ptrace(req, pid, 0, 0)
        if r == 0:
            # reap the stop without ever blocking forever
            while time.time() < deadline:
                wpid, wst = os.waitpid(pid, os.WNOHANG)
                if wpid == pid:
                    return name, wst
                time.sleep(0.1)
            return name, None  # traced but never reported stopped
    return None, f"ATTACH and SEIZE both failed: {estr()}"

def scan_regions(pid, needle, dump_dir=None, min_mb=4):
    """Scan writable regions >= min_mb for needle. Returns hit list."""
    hits = []
    data = open(f"/proc/{pid}/maps").read()
    regions = []
    for line in data.splitlines():
        f = line.split()
        lo, hi = (int(x, 16) for x in f[0].split("-"))
        if "w" in f[1] and hi - lo >= min_mb * 1024 * 1024:
            regions.append((lo, hi))
    mem = open(f"/proc/{pid}/mem", "rb", buffering=0)
    for lo, hi in regions:
        try:
            mem.seek(lo)
            blob = mem.read(hi - lo)
        except Exception as e:
            print(f"  region {lo:#x}: read failed {e!r}")
            continue
        off = blob.find(needle)
        if off >= 0:
            hits.append((lo, off, len(blob)))
            print(f"  PAYLOAD HIT region {lo:#x} +{off:#x} ({len(blob)/1048576:.1f} MB region)")
            if dump_dir:
                os.makedirs(dump_dir, exist_ok=True)
                path = os.path.join(dump_dir, f"region-{lo:016x}.bin")
                with open(path, "wb") as fh:
                    fh.write(blob)
                print(f"  dumped -> {path}")
    return hits

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--conf", required=True, help="dosbox-x conf file (attempt.sh generates it)")
    ap.add_argument("--needle", help="payload file whose first 64 bytes locate the image")
    ap.add_argument("--dump-dir", help="if traceable, dump rw regions here")
    ap.add_argument("--boot-seconds", type=int, default=20, help="time to let the game load before tracing")
    args = ap.parse_args()

    needle = open(args.needle, "rb").read(64) if args.needle else b""

    # Harness self-check: if we cannot trace even a plain child, exit 2.
    ctl = subprocess.Popen(["sleep", "30"], stdin=subprocess.DEVNULL)
    time.sleep(0.3)
    ctypes.set_errno(0)
    r = libc.ptrace(PTRACE_SEIZE, ctl.pid, 0, 0)
    if r != 0:
        print(f"TRACABLE=harness-error: cannot seize a plain child ({estr()})")
        ctl.kill(); ctl.wait()
        return 2
    os.waitpid(ctl.pid, 0)
    libc.ptrace(PTRACE_DETACH, ctl.pid, 0, 0)
    ctl.kill(); ctl.wait()
    print("self-check: plain-child seize OK")

    child = subprocess.Popen(
        ["dosbox-x", "-nogui", "-conf", args.conf, "-time-limit",
         str(args.boot_seconds + 30), "-c", "c:"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT,
        start_new_session=True)
    pid = child.pid
    print(f"dosbox-x pid {pid} launched (headless, time-limited)")
    try:
        time.sleep(args.boot_seconds)
        if child.poll() is not None:
            print(f"TRACABLE=no: dosbox exited early rc={child.returncode}")
            return 0
        deadline = time.time() + 5
        how, info = seize_or_attach(pid, deadline)
        if how is None:
            print(f"TRACABLE=no: {info}")
            return 0
        wst = info
        print(f"TRACABLE=yes ({how}, stop-status {wst if isinstance(wst,int) else 'none-reported'})")
        try:
            # /proc/mem access requires the tracer stop to be held
            hits = scan_regions(pid, needle, args.dump_dir) if needle else []
            print(f"payload scan: {len(hits)} hit(s)" + ("" if hits else " (game may not have loaded data yet; rerun with --boot-seconds higher)"))
        except Exception as e:
            print(f"TRACABLE=yes but /proc read failed: {e!r}")
        finally:
            libc.ptrace(PTRACE_DETACH, pid, 0, 0)
        return 0
    finally:
        try:
            os.kill(pid, signal.SIGKILL)
            child.wait()
        except Exception:
            pass

if __name__ == "__main__":
    sys.exit(main())
