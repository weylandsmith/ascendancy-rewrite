#!/usr/bin/env python3
"""r1_game_health.py — production :9 liveness + TL-expiry + watcher census (t267).

WHY (t266 measured): the 15:45 game death was dosbox-x -time-limit EXPIRY
(launch 07:46 + 28800 s), and it went unnoticed ~1.5 h because production
runs the loop with IDLE_GATE=0 — r1_idle_probe.py never fires between
iterations, and nothing polls the recorded dosbox.pid. This tool is the
cheap check the loop CAN run every wake: stdlib-only, sub-second, and it
NEVER touches live-timeline.jsonl (OOM law t251: one json.load of the 6.4 GB
file OOM-killed the whole tmux scope). Ring-slot mtimes are the feed-arrival
signal instead.

Checks (all independent; report every failure, never short-circuit):
  G  game process: work/r1/vnc/dosbox.pid recorded + kill -0 + /proc comm
     == dosbox-x. Missing pidfile alone is NOT a death (adopt by comm? NO —
     kill model is recorded-PIDs only; report DEATH-AMBIGUOUS instead).
  T  time-limit: parse '-time-limit N' from /proc/PID/cmdline, compute
     expiry = process_start(/proc/PID ctime) + N. Warn at WARN_AHEAD (env,
     default 14400 s — t277 raised it from t267's 600 s: 600 s is far smaller
     than the loop's own ~25 min..4 h health-sampling interval, so it could
     never fire; see the WARN_AHEAD comment) BEFORE expiry; FAIL once expired
     (the t266 failure mode: the game dies mid-sitting with nobody watching).
  W  watcher census: count /proc procs comm python* whose cmdline has
     r1_playcap_watch.py AND the OUT dir. 0 => feed dead; >1 => MULTI-WRITER
     (t266/t267 collision class: each watcher keeps its own `seen`, so every
     slot lands N times — point at scripts/r1_watch_reaper.py).
  F  feed freshness: newest OUT/save/*.sav mtime age. Cadence law 10 s;
     FAIL past FEED_MAX_AGE (env, default 60 s = 6x margin). While the game
     is alive at the TITLE menu autosave still churns, so staleness here
     means watcher-or-ring trouble, not play state.
  B  bring-up: same as F but against VERIFY_WINDOW (env, default 30 s) —
     only meaningful immediately after a start; reported as info otherwise.

Exit codes: 0 HEALTHY, 1 UNHEALTHY (reasons on stdout), 2 instrument broken
(bad paths — mirrors r1_idle_probe.py's contract so the loop can grade it).

Side effects (bounded, atomic): rewrites work/r1/loop/GAME_HEALTH_LIVE.txt
(latest snapshot, tmp+rename) and appends one row to
work/r1/loop/game_health.tsv (time, verdict, reasons). Writes GAME_DEAD.txt
when G fails — the queue asked for exactly that artifact.
"""
import glob, os, shutil, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Env overrides exist for FIXTURE TESTS of the failure branches (t267) — the
# real dirs below are the production defaults; never point them at game/.
RUNDIR = os.environ.get("R1_VNC_DIR", os.path.join(ROOT, "work/r1/vnc"))
OUT = os.environ.get("R1_PLAYCAP_DIR", os.path.join(ROOT, "work/r1/playcap"))
LOOPDIR = os.environ.get("R1_LOOP_DIR", os.path.join(ROOT, "work/r1/loop"))

# t277 MEASURED (F3): the loop samples health ONCE PER ITERATION
# (loop_one_task.sh:185) and iteration gaps run p50 1502 s / p90 6206 s / p95
# 8682 s / max 15156 s (journal.tsv, n=198). A 600 s warn window inside a
# ~25 min-4 h sampling interval is ~7-17% likely to ever be sampled — the
# t267 warn could NOT fire in practice (Nov-2 death caught 35 min AFTER the
# fact, loop.log G:DEATH). 14400 s (4 h) covers p95; the SOP (BLOCKED.md
# t277) is to relaunch before the warn window opens, not inside it.
WARN_AHEAD = int(os.environ.get("WARN_AHEAD", "14400"))
FEED_MAX_AGE = int(os.environ.get("FEED_MAX_AGE", "60"))
VERIFY_WINDOW = int(os.environ.get("VERIFY_WINDOW", "30"))
BRINGUP = os.environ.get("BRINGUP") == "1"     # 'start' sets this


def proc(pid):
    try:
        st0 = open(f"/proc/{pid}/stat").read()
        if st0.rsplit(")", 1)[1].split()[0] == "Z":
            return None, None, None   # zombie: comm still reads; not alive
        comm = open(f"/proc/{pid}/comm").read().strip()
        cmd = open(f"/proc/{pid}/cmdline", "rb").read().replace(b"\0", b" ").decode("latin-1")
        ctime = os.stat(f"/proc/{pid}").st_ctime   # /proc inode ctime == start time
        return comm, cmd, ctime
    except OSError:
        return None, None, None


def main():
    now = time.time()
    reasons, info = [], []

    # ---- G: game process (recorded-PID kill model; never pattern-signal) ----
    # t267 adoption rule: a missing/stale pidfile is NOT a death if /proc shows
    # EXACTLY ONE dosbox-x LAUNCHED BY THIS HARNESS (cmdline carries $RUNDIR —
    # our session.conf path; measured on production 535172). Foreign strays
    # (t261 class) are NOT adoptable but are reported as info so they stay
    # visible. Adoption RECORDS the pid (record-never-signal); zero harness
    # dosbox-x is the honest DEATH.
    pid = None
    pf = os.path.join(RUNDIR, "dosbox.pid")
    sole, foreign = [], []
    for p in os.listdir("/proc"):
        if not p.isdigit():
            continue
        c, cmdline, _ = proc(p)
        if c != "dosbox-x":
            continue
        if RUNDIR in (cmdline or ""):
            sole.append(p)
        else:
            foreign.append(p)
    if os.path.isfile(pf):
        pid = open(pf).read().strip()
    comm, cmd, pstart = proc(pid) if pid else (None, None, None)
    if pid and comm is not None and comm != "dosbox-x":
        reasons.append(f"G:PIDSTALE(pid {pid} comm={comm})")
        pid = None
    # MULTI check runs EVEN with a valid pidfile: t261's class is production +
    # a stray BOTH harness-launched on one ring; the pidfile names only one.
    if len(sole) > 1:
        reasons.append(f"G:MULTI-DOSBOX({','.join(sole)} — t261 stray class; sort out before trusting the ring)")
    if pid is None or comm is None or pstart is None:
        if len(sole) == 1:
            pid = sole[0]
            comm, cmd, pstart = proc(pid)
            os.makedirs(RUNDIR, exist_ok=True)
            with open(pf + ".tmp", "w") as f:
                f.write(pid + "\n")
            os.replace(pf + ".tmp", pf)
            info.append(f"game pid {pid} ADOPTED into dosbox.pid")
        elif len(sole) > 1:
            reasons.append(f"G:MULTI-DOSBOX({','.join(sole)} — t261 stray class; sort out before trusting the ring)")
            pid = None
        else:
            reasons.append(f"G:DEATH(pid {pid or '?'} gone, zero harness dosbox-x in /proc)")
            pid = None
    if foreign:
        info.append(f"NOTE foreign dosbox-x (not harness-launched): {','.join(foreign)}")
    if pid is not None and cmd and pstart:
        if not any(i == f"game pid {pid}" for i in info):
            info.append(f"game pid {pid}")
        # ---- T: -time-limit expiry, measured from the process itself ----
        toks = cmd.split()
        tl = None
        if "-time-limit" in toks:
            try:
                tl = int(toks[toks.index("-time-limit") + 1])
            except (ValueError, IndexError):
                reasons.append("T:TLUNPARSEABLE")
        if tl is not None:
            left = (pstart + tl) - now
            exp = time.strftime("%F %T", time.localtime(pstart + tl))
            info.append(f"TL expiry {exp} ({int(left)} s left)")
            if left <= 0:
                reasons.append(f"T:EXPIRED(expired {int(-left)} s ago @ {exp})")
            elif left <= WARN_AHEAD:
                reasons.append(f"T:WARN(expiry {exp} in {int(left)} s)")

    # ---- W: watcher census on OUT (t266 multi-writer collision class) ----
    watchers = []
    for p in os.listdir("/proc"):
        if not p.isdigit():
            continue
        comm, cmd, _ = proc(p)
        if comm and cmd and comm.startswith("python") and "r1_playcap_watch.py" in cmd and OUT in cmd:
            watchers.append(p)
    if len(watchers) == 0:
        reasons.append("W:NOWATCHER(feed not banking)")
    elif len(watchers) > 1:
        reasons.append(f"W:MULTI-WRITER({len(watchers)}: {','.join(watchers)}; run scripts/r1_watch_reaper.py {OUT})")
    else:
        info.append(f"watcher {watchers[0]}")

    # ---- F/B: ring freshness (never reads the timeline jsonl) ----
    newest, newest_m = 0.0, None
    for sp in glob.glob(os.path.join(OUT, "save", "*.sav")):
        try:
            m = os.stat(sp).st_mtime
        except OSError:
            continue
        if m > newest:
            newest, newest_m = m, os.path.basename(sp)
    if newest_m is None:
        reasons.append("F:NORING(no save/*.sav)")
    else:
        age = now - newest
        info.append(f"ring {newest_m} age {age:.0f}s")
        if age > FEED_MAX_AGE:
            reasons.append(f"F:FEED-STALE(newest slot {newest_m} {age:.0f}s old > {FEED_MAX_AGE}s)")
        if BRINGUP:
            if age <= VERIFY_WINDOW:
                info.append(f"BRINGUP OK(row landed {age:.0f}s <= {VERIFY_WINDOW}s)")
            else:
                reasons.append(f"B:BRINGUP-FAIL(no ring row within {VERIFY_WINDOW}s)")

    # ---- report + durable artifacts ----
    verdict = "HEALTHY" if not reasons else "UNHEALTHY"
    stamp = time.strftime("%F %T")
    line = f"{verdict} | {'; '.join(reasons) if reasons else '; '.join(info)}"
    print(f"game-health {stamp}: {line}")
    for i in info:
        print(f"  info: {i}")
    os.makedirs(LOOPDIR, exist_ok=True)
    live = os.path.join(LOOPDIR, "GAME_HEALTH_LIVE.txt")
    with open(live + ".tmp", "w") as f:
        f.write(line + "\n" + "".join(f"  info: {i}\n" for i in info))
    os.replace(live + ".tmp", live)
    with open(os.path.join(LOOPDIR, "game_health.tsv"), "a") as f:
        f.write(f"{stamp}\t{verdict}\t{'; '.join(reasons) if reasons else 'ok'}\n")
    if any(r.startswith("G:DEATH") for r in reasons):
        with open(os.path.join(LOOPDIR, "GAME_DEAD.txt"), "w") as f:
            f.write(f"game death detected {stamp} (pid {pid}); reasons: {'; '.join(reasons)}\n"
                    "bank the ring NOW (cp save/ bank-tNNN-*), then relaunch per SOP.\n")
    return 0 if verdict == "HEALTHY" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:                       # instrument broken != unhealthy
        print(f"game-health INSTRUMENT-BROKEN: {e!r}")
        sys.exit(2)
