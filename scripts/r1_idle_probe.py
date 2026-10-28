#!/usr/bin/env python3
"""r1_idle_probe.py — one-shot adjudication of the two IDLE re-arm triggers
(docs/STATE.md NEXT ACTION / docs/re/stop-report.md §6). Read-only: touches
no game state, launches nothing. Exit 0 = both triggers NEGATIVE (loop stays
IDLE); exit 1 = at least one trigger ARMED (print which); exit 2 = probe
could not run cleanly.

Laws encoded here (each earned the hard way, do not "simplify" them away):
  (A) mtimes+score MOVEMENT prove a sitting, in_game does not (t111 hygiene
      law); the find-sweep cutoff MUST be session start — a looser window
      also lists work/r1/selftest-t111-playcap/* and work/r1/.anch-cache.json
      (t111 self-test artifacts, not captures).
  (B) trigger (B) is adjudicated by CONTENT (`git diff HEAD`), never mtime:
      the preflight gate runs after each commit and mtime-touches
      docs/re/{text,modules,economy,gizmos,fnt}.md with zero content delta
      (t116 pitfall).
  (B2) the steering NOTE route (harness prepends text to
      work/r1/loop/prompt-<n>.txt) is NOT covered by the STEERING-file glob:
      only a CONTENT diff of the newest prompt vs its numeric predecessor arms
      it (t145 coverage hole). Enumerate with NUMERIC sort, never `ls -1`
      lexical order (t144 law: `tail -1` returns prompt-9.txt).
  Process check uses `ps -eo comm` matching, NOT `pgrep -af` (self-match
  false-positive trap, t114).
  Watcher pids 27772+27774 are bash-wrapper + python-child — the PAIR is
  normal, not a duplicate (t115).
"""
import difflib
import glob
import os
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAYCAP = os.path.join(ROOT, "work", "r1")
TIMELINE = os.path.join(PLAYCAP, "playcap", "live-timeline.jsonl")
# Frozen baseline per STATE.md t116; re-freeze only when a sitting legitimately
# lands (the sitting-adjudication task), never to silence a real trigger.
BASE_MTIME_NS = 1793043841_304_000_000  # 2026-10-26 15:44:01.304 -0400 (stat %Y verified t117)
BASE_SIZE = 5691796463


def sh(cmd):
    return subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True,
                          text=True).stdout


def trigger_a(now_wall):
    reasons, armed = [], False
    dirs = sorted([d for d in os.listdir(PLAYCAP)
                   if d.startswith("playcap-")], reverse=True)
    newest = dirs[0] if dirs else None
    reasons.append("newest playcap dir: %s" % newest)
    if newest and newest != "playcap-20261014-224611":
        armed = True
        reasons.append("NEW playcap dir present")
    if os.path.exists(TIMELINE):
        st = os.stat(TIMELINE)
        reasons.append("live-timeline.jsonl mtime_ns=%d size=%d (baseline %d/%d)"
                       % (st.st_mtime_ns, st.st_size, BASE_MTIME_NS, BASE_SIZE))
        if st.st_mtime_ns > BASE_MTIME_NS or st.st_size > BASE_SIZE:
            armed = True
            reasons.append("timeline grew past frozen baseline")
    else:
        reasons.append("WARNING: timeline missing")
    dosbox = sh("ps -eo pid,comm | awk '$2 ~ /dosbox/ {print}'").strip()
    reasons.append("dosbox procs: %r" % (dosbox or "none"))
    if dosbox:
        armed = True
        reasons.append("dosbox running")
    # Session start = the harness prompt file for THIS iteration (written when
    # the loop spawned the session). Using "now" would be too tight and could
    # miss a capture that landed earlier in the same session.
    # Best source is the timestamp the harness bakes into the iteration log
    # NAME (prompt mtimes drift later than the real spawn: measured 21:54:50 vs
    # true 21:47:01 on t117, a ~8 min blind spot).
    names = sorted(os.path.basename(x) for x in
                   glob.glob(os.path.join(PLAYCAP, "loop", "iter-*.log")))
    start = None
    for n in reversed(names):
        stamp = n[len("iter-"):len("iter-") + 15]
        try:
            start = time.mktime(time.strptime(stamp, "%Y%m%d-%H%M%S"))
            break
        except ValueError:
            continue
    if start is None:
        prompts = sorted(glob.glob(os.path.join(PLAYCAP, "loop", "prompt-*.txt")),
                         key=os.path.getmtime)
        start = os.path.getmtime(prompts[-1]) if prompts else now_wall
    cutoff = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start))
    sweep = sh("find work/r1 -type f -newermt '%s'" % cutoff).split()
    foreign = [p for p in sweep if not p.startswith("work/r1/loop/")]
    reasons.append("find work/r1 -newermt %s (session start) -> %d files, "
                   "non-loop: %s" % (cutoff, len(sweep), foreign or "none"))
    if foreign:
        armed = True
        reasons.append("capture-side file newer than session start")
    return armed, reasons


def trigger_b():
    reasons, armed = [], False
    diff = sh("git diff HEAD --name-only").strip()
    # Tracked modifications only: this script and _wip_*.md are legitimately
    # untracked mid-iteration and must not read as a user answer (t117).
    status = sh("git status --porcelain").strip()
    head = sh("git log --oneline -1").strip()
    # t145: idle-turn subjects summarise the previous iteration, so printing the
    # whole thing taxes every re-check (~1.3k chars, growing monotonically). The
    # full text lives in docs/STATE.md's LANDED block, where it is actually read.
    reasons.append("HEAD: %.130s%s" % (head, "..." if len(head) > 130 else ""))
    reasons.append("git diff HEAD --name-only: %s" % (diff.splitlines() or "empty"))
    tracked = [l for l in status.splitlines() if not l.startswith("??")]
    reasons.append("git status --porcelain (tracked): %s" % (tracked or "empty"))
    reasons.append("untracked (informational, NOT a trigger — mid-iteration"
                   " _wip_/probe files): %s"
                   % ([l for l in status.splitlines() if l.startswith("??")] or "none"))
    # The loop itself owns these paths and edits them every iteration, so a
    # tracked delta there is NOT a user answer. A change OUTSIDE this set
    # (e.g. rewrite/, game/ docs, PLAN.md) is what a real decision looks like.
    LOOP_OWNED = ("docs/STATE.md", "docs/OPEN-QUESTIONS.md", "docs/BLOCKED.md",
                  "docs/re/", "scripts/r1_idle_probe.py", "work/")
    foreign_delta = [f for f in diff.splitlines()
                     if not f.startswith(LOOP_OWNED)]
    reasons.append("delta outside loop-owned paths: %s"
                   % (foreign_delta or "none"))
    if foreign_delta:
        armed = True
    own = [f for f in diff.splitlines() if f.startswith(LOOP_OWNED)]
    if own and not armed:
        reasons.append("CAUTION: loop-owned file(s) modified since HEAD: %s. "
                       "Run this probe at SESSION START and these are the "
                       "loop's own edits; if you have edited nothing this "
                       "session, they ARE the user decision — read `git diff "
                       "HEAD` before treating the turn as idle." % own)
        reasons.append("content delta after last commit = candidate user answer"
                       " (read the diff before assigning work)")
    steer = sh("ls docs/STEERING* STEERING* 2>/dev/null").strip()
    reasons.append("STEERING file: %s" % (steer or "none"))
    if steer:
        armed = True
    # (B2) t145: the STEERING glob above is file-EXISTENCE only. The other
    # documented steering route -- the harness PREPENDING a note to this
    # iteration's prompt file -- is invisible to it, so adjudicate it by
    # content here. NUMERIC sort (t144: `ls -1 | tail -1` -> prompt-9.txt).
    def _num(path):
        m = re.search(r"(\d+)", os.path.basename(path))
        return int(m.group(1)) if m else -1

    prompts = sorted(glob.glob(os.path.join(PLAYCAP, "loop", "prompt-*.txt")),
                     key=_num)
    if len(prompts) < 2:
        reasons.append("prompt content delta: UNKNOWN (<2 prompt files)")
    else:
        newest, prev = prompts[-1], prompts[-2]
        with open(newest, encoding="utf-8", errors="replace") as fh:
            n_txt = fh.read()
        with open(prev, encoding="utf-8", errors="replace") as fh:
            p_txt = fh.read()
        strip = lambda t: re.sub(r"\d+", "N", t)  # noqa: E731
        n_lines, p_lines = len(n_txt.splitlines()), len(p_txt.splitlines())
        raw = [l for l in difflib.unified_diff(p_txt.splitlines(),
                                               n_txt.splitlines(), lineterm="")
               if l[:1] in "+-" and l[:3] not in ("+++", "---")]
        stripped = [l for l in difflib.unified_diff(strip(p_txt).splitlines(),
                                                    strip(n_txt).splitlines(),
                                                    lineterm="")
                    if l[:1] in "+-" and l[:3] not in ("+++", "---")]
        note = ""
        if raw and not stripped:
            note = (" [raw delta %d line(s) but digit-stripped delta 0 ="
                    " iteration-numbering drift only]" % len(raw))
        reasons.append("prompt pair %s vs %s (%d/%d lines): digit-stripped delta"
                       " %d line(s)%s" % (os.path.basename(newest),
                                          os.path.basename(prev),
                                          n_lines, p_lines, len(stripped), note))
        if stripped:
            armed = True
            reasons.append("PROMPT CONTENT CHANGED: %d line(s) -- read %s, a"
                           " prepended steering note is the loop's assignment"
                           % (len(stripped), newest))
    return armed, reasons


def infra():
    lines = []
    out = sh("ps -eo pid,etime,comm | awk '$3 ~ /Xvfb|x11vnc|python3/'").strip()
    lines.append(out or "NO Xvfb/x11vnc/python3 — negatives UNTRUSTWORTHY")
    log = os.path.join(PLAYCAP, "vnc", "x11vnc.log")
    if os.path.exists(log):
        st = os.stat(log)
        lines.append("x11vnc.log mtime=%s size=%d"
                     % (time.strftime("%Y-%m-%d %H:%M:%S",
                                      time.localtime(st.st_mtime)), st.st_size))
        lines.append("  (unchanged 2026-10-27 17:30:18/30114 since t112 => zero"
                     " connects against the t111-FIXED launch path)")
    return lines


def main():
    now_wall = time.time()
    print("r1_idle_probe @ %s" % time.strftime("%Y-%m-%d %H:%M:%S",
                                               time.localtime(now_wall)))
    a_a, r_a = trigger_a(now_wall)
    print("\n== TRIGGER A (new capture): %s" % ("ARMED" if a_a else "NEGATIVE"))
    for r in r_a:
        print("  - " + r)
    b_b, r_b = trigger_b()
    print("\n== TRIGGER B (user decision): %s" % ("ARMED" if b_b else "NEGATIVE"))
    for r in r_b:
        print("  - " + r)
    print("\n== INFRA (liveness of the watch path)")
    for r in infra():
        print("  " + r)
    print("\nVERDICT: %s" % ("RE-ARM — a trigger fired, do NOT treat this as idle"
                             if (a_a or b_b) else
                             "IDLE — neither trigger; honest negative, keep the IDLE block"))
    return 1 if (a_a or b_b) else 0


if __name__ == "__main__":
    sys.exit(main())
