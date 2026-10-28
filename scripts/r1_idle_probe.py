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
  (B3) a COMMITTED user decision is invisible to every tree-vs-HEAD leg
      (t146 hole: user edits rewrite//PLAN.md and commits -> `git diff HEAD`
      is empty, 32 turns adjudicated (B) on uncommitted state only). Law: the
      harness writes journal.tsv AFTER each iteration's commit and field 6's
      first token is that iteration's HEAD sha, so at session start HEAD must
      equal the journal sha; divergence = enumerate <journal-sha>..HEAD with
      files and ARM only on a path outside LOOP_OWNED (loop-own divergence,
      e.g. a crashed iteration whose row never landed, is a CAUTION like the
      t117 untracked-files law). Env R1_JOURNAL overrides the journal path.
  (A4) legs (a)-(c) are produced BY scripts/r1_playcap_watch.py: if it is dead,
      every (A) leg reads NEGATIVE over a real sitting (t147 hole). Adjudicate
      by matching the script name in `ps -eo pid=,args=` in Python — never
      shell grep (t114), never pgrep (comm truncates to 15 chars = "python3").
      Dead => (A) NOT ADJUDICATED: caution + exit 2, never arm (absence of
      signal is not absence of event). Env R1_WATCH_SCRIPT tests the leg.
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
# Paths the loop edits every iteration; a delta here is never the user's
# answer (t117). Shared by the tree leg and the (B3) committed-commit leg.
LOOP_OWNED = ("docs/STATE.md", "docs/OPEN-QUESTIONS.md", "docs/BLOCKED.md",
              "docs/re/", "scripts/r1_idle_probe.py", "work/")


def sh(cmd):
    return subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True,
                          text=True).stdout


def trigger_a(now_wall):
    reasons, armed, adjudicated = [], False, True
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
    # Loop-owned artifacts under work/r1 that are NOT captures. .anch-cache.json
    # is written by r1_slot.anchors_cached (r1_slot.py:49) on ANY analyzer run
    # -- proven t149: a scratch-dir `r1_playcap_watch.py --once` refreshed it and
    # armed this leg by itself, a pure self-inflicted false positive. It is a
    # pure function of work/ascend_payload.bin, so it can never carry a sitting.
    TOOL_ARTIFACTS = ("work/r1/.anch-cache.json",)
    foreign = [p for p in sweep
               if not p.startswith("work/r1/loop/")
               and p not in TOOL_ARTIFACTS]
    reasons.append("find work/r1 -newermt %s (session start) -> %d files, "
                   "non-loop: %s" % (cutoff, len(sweep), foreign or "none"))
    if foreign:
        armed = True
        reasons.append("capture-side file newer than session start")
    # (A4) t147: legs (a)/(b)/(c) above are only observable if the watcher that
    # WRITES them is alive. scripts/r1_playcap_watch.py appends the timeline and
    # the capture-side files, so a dead watcher on an otherwise-healthy box
    # (Xvfb/x11vnc up, dosbox exited because the user finished playing) makes
    # every (A) leg print NEGATIVE over a real sitting, indefinitely. infra()
    # cannot cover this: it pattern-matches `Xvfb|x11vnc|python3` and prints
    # python3 pids without naming the watcher ("touches X" != "adjudicates X",
    # t145 law). Match the cmdline in Python, never shell grep (t114 self-match)
    # and never pgrep -x (comm truncates to 15 chars, so it can only ever see
    # "python3"). Dead => CANNOT ADJUDICATE, do NOT arm: arming asserts a user
    # decision that was never made (t117 law).
    wscript = os.environ.get("R1_WATCH_SCRIPT", "scripts/r1_playcap_watch.py")
    procs = []
    for line in sh("ps -eo pid=,args=").splitlines():
        parts = line.strip().split(None, 1)
        if len(parts) == 2:
            procs.append((parts[0], parts[1]))
    watchers = []
    wbase = os.path.basename(wscript)
    for pid, args in procs:
        argv = args.split()
        # Match the INTERPRETED script at argv[1] ("python3 watch.py dir").
        # argv[0] is always "python3" (never matches); whole-cmdline substring
        # matching is the t114 trap in a new costume: measured — my test shell
        # `R1_WATCH_SCRIPT=<path> python3 probe.py | ...` had the path in its
        # OWN ps args, so the elif-substring fallback false-matched (and a
        # `bash -c`-launched probe self-matches the same way). argv[1] of a
        # shell is its -c string or another script, so neither can hit it.
        if len(argv) > 1 and os.path.basename(argv[0]).startswith("python") \
                and os.path.basename(argv[1]) == wbase:
            watchers.append((pid, args))
    if watchers:
        reasons.append("A4 watcher: ALIVE %s" % ", ".join(
            "pid %s (%s)" % (pid, args[:90]) for pid, args in watchers))
    else:
        reasons.append(
            "A4 watcher: NOT RUNNING (%s absent from ps) — TRIGGER (A) IS "
            "NOT ADJUDICATED this run: timeline growth and capture-side files "
            "are produced by that process, so its absence cannot PROVE no "
            "sitting happened, it only means the loop is blind to one. Do NOT "
            "treat the (A) NEGATIVE above as a steady-state result; repair via "
            "`bash scripts/r1_playcap_vnc.sh` then re-run this probe. Reported "
            "as a caution, not a trigger (t117: only an observed user event "
            "arms)." % wscript)
        adjudicated = False
    # (A5) t149: t147 proved the watcher PROCESS is up, which is a different
    # claim than the collector WORKING (t145 law, one level deeper). t149
    # measured function directly: scratch-dir `--once` over two ring slots
    # emitted 2 valid JSONL rows (t=1254, 38 ships) and re-deduped to 0 new
    # rows on a second pass. That run also exposed an ingestion asymmetry:
    # scripts/r1_playcap_watch.py:161 globs save/*.sav LOWERCASE, so a save file
    # the glob cannot match is never read even with a healthy watcher, and the
    # timeline stays flat. An un-ingested played slot is precisely a sitting no
    # other (A) leg reports (no new playcap-<ts> dir, no timeline growth), so
    # surface it. CAUTION, never a trigger (t117 law: only an observed user
    # event arms). Env R1_SAVE_DIR overrides the save dir for testing.
    savedir = os.environ.get("R1_SAVE_DIR",
                             os.path.join(os.path.dirname(TIMELINE), "save"))
    try:
        save_root = os.path.abspath(savedir)
        ingestable = (set(n for n in os.listdir(save_root)
                          if n.endswith(".sav"))
                      if os.path.isdir(save_root) else set())
        stray = []
        for dirpath, subdirs, fnames in os.walk(os.path.dirname(TIMELINE)):
            subdirs[:] = [d for d in subdirs if d not in ("caps", "loop")]
            for f in fnames:
                if not f.lower().endswith(".sav"):
                    continue
                full = os.path.abspath(os.path.join(dirpath, f))
                # A file that is not a valid dosbox save-state ZIP cannot hold a
                # sitting, so it is not an ingestion blind spot:
                # work/r1/playcap/evidence_slot04_t1254.SAV is a raw 88 KB memory
                # excerpt (is_zipfile False, measured t149) used by
                # r1_gizmo_table, not a ring slot. Naming it every turn would be
                # a permanent false positive.
                try:
                    with __import__("zipfile").ZipFile(full) as zf:
                        if "Memory" not in zf.namelist():
                            continue
                except Exception:
                    continue
                in_save = (os.path.dirname(full) == save_root)
                if in_save and f.endswith(".sav"):
                    continue          # matches the watcher glob exactly
                stray.append((os.path.relpath(full, ROOT), f))
        if stray:
            reasons.append(
                "A5 un-ingestable save files under playcap (watcher reads only "
                "save/*.sav, r1_playcap_watch.py:161): %s - if any is a COPY OF "
                "A PLAYED SLOT the loop is blind to that sitting: adjudicate it "
                "directly. CAUTION, not a trigger (t117)." % ", ".join(
                    "%s (%s)" % (p, time.strftime("%Y-%m-%d %H:%M", time.localtime(
                        os.stat(os.path.join(ROOT, p)).st_mtime)))
                    for p, _ in stray[:6]))
        else:
            reasons.append("A5 un-ingestable save files: none (save/*.sav = %d, "
                           "all match the watcher glob)" % len(ingestable))
    except Exception as e:
        reasons.append("A5 leg ERROR (%s) - ingestion asymmetry NOT adjudicated"
                       % repr(e)[:100])
    return armed, reasons, adjudicated


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
    # (B4) t153: the untracked line used to be blanket-"informational". t117's
    # law was earned against the LOOP'S OWN untracked files (docs/re/_wip_*.md,
    # probe scratch) but it was applied to every path, so a user decision
    # delivered as a NEW FILE (docs/ANSWER.md, notes.txt, a restored doc) is
    # invisible to every (B) leg: B1 diffs the working tree of TRACKED files,
    # B3 compares commits, B2 reads prompt text, and the STEERING leg globs the
    # literal names only. Split by OWNERSHIP instead of deleting the leg:
    # untracked under LOOP_OWNED stays informational (t117 preserved), foreign
    # untracked ARMS. Measured safety: `.gitignore` covers the loop's whole
    # scratch surface (build/, build-*/, .logs/, __pycache__/, *.pyc, .venv/,
    # .cache/, *.log, work/) and porcelain never lists ignored files, so a
    # non-ignored untracked path outside LOOP_OWNED has no loop-tool origin.
    untracked = sh("git status --porcelain --untracked-files=all").splitlines()
    untracked = [l[3:].strip() for l in untracked if l.startswith("??")]
    own_untracked = [p for p in untracked if p.startswith(LOOP_OWNED)]
    foreign_untracked = [p for p in untracked if p not in own_untracked]
    reasons.append("untracked loop-owned (informational — this loop writes"
                   " _wip_*.md here): %s" % (own_untracked or "none"))
    reasons.append("untracked OUTSIDE loop-owned: %s" % (foreign_untracked or "none"))
    if foreign_untracked:
        armed = True
        reasons.append("UNTRACKED USER FILE: %d path(s) outside loop-owned paths"
                       " appeared since the last iteration — a decision left as a"
                       " new file (answer/notes/RESTORE-ME) is the §3 answer; read"
                       " it before treating the turn as idle (it may also be the"
                       " user re-adding a file the loop deleted, which is a"
                       " decision about that file either way)"
                       % len(foreign_untracked))
    # The loop itself owns these paths and edits them every iteration, so a
    # tracked delta there is NOT a user answer. A change OUTSIDE this set
    # (e.g. rewrite/, game/ docs, PLAN.md) is what a real decision looks like.
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
    # (B3) t146: every leg above adjudicates the WORKING TREE vs HEAD, so a
    # user decision delivered as a COMMIT (the normal way work lands here) is
    # invisible: HEAD moves, tree clean, diff empty. The harness appends a
    # journal row AFTER each iteration's commit whose field 6 starts with that
    # iteration's sha, so HEAD != last-journal-sha at session start means
    # commits landed outside the loop. ARM only on a foreign path.
    jpath = os.environ.get("R1_JOURNAL", os.path.join(PLAYCAP, "loop", "journal.tsv"))
    jsha = None
    try:
        rows = [l for l in open(jpath, encoding="utf-8", errors="replace")
                if l.strip()]
        if rows:
            # sha is the FIRST token of the LAST tab field (measured on the real
            # journal: normal rows "date\titer\tOK\t0\t<sha> subj", re-check rows
            # carry an extra '(re-check' field before it — last-field-first-token
            # is the invariant that holds for both shapes).
            last_field = rows[-1].rstrip("\n").split("\t")[-1]
            m = re.match(r"^([0-9a-f]{7,40})\b", last_field)
            jsha = m.group(1) if m else None
            if jsha is None:
                reasons.append("B3 journal leg: last row has no leading sha "
                               "(%r) — committed-decision route NOT adjudicated"
                               % last_field[:40])
    except OSError as exc:
        reasons.append("B3 journal leg: UNREADABLE (%s) — committed-decision "
                       "route NOT adjudicated this run" % exc)
    if jsha:
        head_full = sh("git rev-parse HEAD").strip()
        if head_full.startswith(jsha):
            reasons.append("B3 HEAD == journal sha %s: no commits outside the "
                           "loop since last iteration" % jsha)
        else:
            # 'C ' prefixes each commit line so file paths are the only bare
            # lines (subject text can contain spaces but never starts a line).
            # %% escapes: the git format must survive Python %-interpolation.
            log = sh("git log --format='C %%h %%s' --name-only %s..%s"
                     % (jsha, head_full)).strip()
            if not log or "fatal:" in log:
                reasons.append("B3 journal sha %s NOT an ancestor of HEAD %s "
                               "(diverged/unknown history) — read `git log` "
                               "before treating as idle" % (jsha, head_full[:12]))
                armed = True
            else:
                commits = [l for l in log.splitlines() if l.startswith("C ")]
                files = [l.strip() for l in log.splitlines()
                         if not l.startswith("C ") and l.strip()]
                foreign = [f for f in files if not f.startswith(LOOP_OWNED)]
                reasons.append("B3 commits since journal sha %s: %d commit(s), "
                               "foreign paths: %s\n%s" %
                               (jsha, len(commits), foreign or "none",
                                log[:1500]))
                if foreign:
                    armed = True
                    reasons.append("COMMITTED USER DECISION: %d commit(s) touch "
                                   "paths outside loop-owned since the last "
                                   "iteration — read them, they are the §3 "
                                   "answer" % len(commits))
                else:
                    reasons.append("CAUTION: divergence confined to loop-owned "
                                   "paths (crashed iteration whose journal row "
                                   "never landed?) — NOT a trigger (t117 law)")
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
    a_a, r_a, adj_a = trigger_a(now_wall)
    print("\n== TRIGGER A (new capture): %s" % ("ARMED" if a_a else
          ("NOT ADJUDICATED (watcher down)" if not adj_a else "NEGATIVE")))
    for r in r_a:
        print("  - " + r)
    b_b, r_b = trigger_b()
    print("\n== TRIGGER B (user decision): %s" % ("ARMED" if b_b else "NEGATIVE"))
    for r in r_b:
        print("  - " + r)
    print("\n== INFRA (liveness of the watch path)")
    for r in infra():
        print("  " + r)
    verdict = ("RE-ARM — a trigger fired, do NOT treat this as idle"
               if (a_a or b_b) else
               ("IDLE on (B); (A) UNVERIFIED — watcher down, re-check after "
                "repair" if not adj_a else
                "IDLE — neither trigger; honest negative, keep the IDLE block"))
    print("\nVERDICT: %s" % verdict)
    if a_a or b_b:
        return 1
    # rc=2 documented as probe failure: with the watcher down the (A) legs are
    # blind, so "both negative" cannot be honestly asserted (t117 law cuts the
    # other way too — don't print a clean verdict you didn't measure).
    return 0 if adj_a else 2


if __name__ == "__main__":
    sys.exit(main())
