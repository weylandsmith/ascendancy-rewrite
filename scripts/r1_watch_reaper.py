#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""r1_watch_reaper.py OUT_DIR [--keep N] [--dry-run] — targeted watcher reaper (t267).

WHY: three r1_playcap_watch.py instances were MEASURED alive on playcap at
t267 pre-flight (524207, 524532, 535187), each holding an open fd on
live-timeline.jsonl and each keeping its OWN in-memory `seen` set — so every
ring write lands as N duplicate rows (MEASURED 3x in the last-400KB tail:
16 rows / 6 distinct slot-keys). The vnc harness reaper only reads
$RUNDIR/watch*.pid files, which misses watchers whose session ended without
recording (or whose pid file was overwritten by the next start). pkill -f is
FORBIDDEN here: it matches its own shell's cmdline and kills your session
(known footgun, banked repeatedly).

Kill model (inherited from r1_playcap_vnc.sh t85b, tightened):
  * discover victims via /proc enumeration ONLY (comm == python* AND cmdline
    contains 'r1_playcap_watch.py' AND cmdline contains OUT_DIR);
  * keep the NEWEST-started KEEPN (default 1) — that is the one the current
    session launched;
  * SIGTERM only (the watcher's loop exits cleanly on death; it holds no
    lock, dedup is jsonl-derived at start, so a kill mid-row costs at most
    one unflushed line);
  * never signals anything that failed verification; never pattern-kills.

Exit: 0 = done (prints REAPED/KEPT lines); 2 = bad args.
"""
import os, sys, time

def proc_info(pid):
    try:
        comm = open(f"/proc/{pid}/comm").read().strip()
        cmd = open(f"/proc/{pid}/cmdline","rb").read().replace(b"\0", b" ").decode("latin-1").strip()
        st = os.stat(f"/proc/{pid}")
        return comm, cmd, st.st_ctime   # /proc ctime == process start time
    except OSError:
        return None, None, None

def main():
    args = [a for a in sys.argv[1:]]
    dry = "--dry-run" in args
    keep = 1
    if "--keep" in args:
        i = args.index("--keep")
        keep = int(args[i + 1]); del args[i:i + 2]
    if not args:
        print(__doc__); return 2
    out = os.path.abspath(args[0])

    victims = []
    for p in os.listdir("/proc"):
        if not p.isdigit():
            continue
        comm, cmd, start = proc_info(p)
        if not comm or not cmd:
            continue
        if not comm.startswith("python"):
            continue
        if "r1_playcap_watch.py" not in cmd or out not in cmd:
            continue
        victims.append((int(p), start, cmd))
    # NOTE: bash -c wrappers are deliberately NOT victims (comm is bash); the
    # python child is what holds the timeline fd. When the python dies the
    # wrapper's `&& ... >>` pipeline ends by itself.

    victims.sort(key=lambda t: -t[1])  # newest-started first
    keep_pids = {v[0] for v in victims[:keep]}
    print(f"reaper: {len(victims)} watcher(s) on {out} (keep newest {keep})")
    rc = 0
    for pid, start, cmd in victims:
        stamp = time.strftime("%F %T", time.localtime(start))
        if pid in keep_pids:
            print(f"KEPT  pid {pid} started {stamp}")
            continue
        if dry:
            print(f"WOULD-REAP pid {pid} started {stamp}")
            continue
        try:
            os.kill(pid, 15)   # verified cmdline above; targeted, never pattern
            print(f"REAPED pid {pid} started {stamp}")
        except OSError as e:
            print(f"FAILED pid {pid}: {e}")
            rc = 1
    return rc

v1_start_desc = None
if __name__ == "__main__":
    sys.exit(main())
