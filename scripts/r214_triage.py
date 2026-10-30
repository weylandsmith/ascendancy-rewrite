#!/usr/bin/env python3
"""t214: capture-health triage on the SHARED playcap dir.

Two questions, both answered from the tail window only (never the whole file):

  1. TRIGGER-A re-verification: full-ns mtime / size / tail-64KiB md5 of
     live-timeline.jsonl against the frozen baselines banked in docs/STATE.md.
     Any delta => a new sitting exists and the sitting script must run.

  2. WATCHER MULTIPLICITY: ps shows FOUR r1_playcap_watch.py processes with the
     same capture dir open (t115 law says one bash wrapper + one child is a
     PAIR, not a duplicate). If the extra instances are live, the timeline grows
     faster than play does and per-event counts mined from it are inflated.
     Measure it honestly: distinct-line fraction in the tail window plus the
     key-shape census, so a future witness mining run knows what it is reading.

Prints only small summaries. RC=0 always (triage, not an assertion).
"""
import hashlib
import json
import os
import subprocess
import collections

ROOT = "/home/hrethric/projects/ascendancy"
RUN = os.path.join(ROOT, "work/r1/playcap")
JSONL = os.path.join(RUN, "live-timeline.jsonl")

BASE_NS_MTIME = 1793294532100000000
BASE_SIZE = 5_721_578_066
BASE_TAIL_MD5 = "9054cc6c66802e6f80431d4ffa1416ee"


def trigger_a():
    st = os.stat(JSONL)
    with open(JSONL, "rb") as f:
        f.seek(-65536, os.SEEK_END)
        tail_md5 = hashlib.md5(f.read()).hexdigest()
    ok = (st.st_mtime_ns == BASE_NS_MTIME and st.st_size == BASE_SIZE
          and tail_md5 == BASE_TAIL_MD5)
    print("== TRIGGER-A ==")
    print(f"  ns_mtime {st.st_mtime_ns} == {BASE_NS_MTIME}: "
          f"{st.st_mtime_ns == BASE_NS_MTIME}")
    print(f"  size     {st.st_size} == {BASE_SIZE}: {st.st_size == BASE_SIZE}")
    print(f"  tail md5 {tail_md5} == {BASE_TAIL_MD5}: "
          f"{tail_md5 == BASE_TAIL_MD5}")
    print(f"  => sitting delta: {not ok}")
    return not ok


def game_procs():
    """dosbox/game processes, matched so this script's own cmdline can't match."""
    out = subprocess.run(["ps", "-eo", "pid,comm,etime,args"],
                         capture_output=True, text=True).stdout
    hits = []
    for ln in out.splitlines()[1:]:
        parts = ln.split(None, 3)
        if len(parts) < 4:
            continue
        pid, comm, et, args = parts
        if "r214_triage" in args:
            continue
        if comm.startswith("dosbox") or "ascend.exe" in args.lower():
            hits.append((pid, comm, et, args[:70]))
    print("== GAME PROCESS ==")
    print(f"  dosbox/ascend.exe processes: {len(hits)}")
    for h in hits:
        print("   ", h)
    return len(hits)


def watchers():
    out = subprocess.run(["ps", "-eo", "pid,ppid,comm,etime,args"],
                         capture_output=True, text=True).stdout
    rows = []
    for ln in out.splitlines()[1:]:
        parts = ln.split(None, 4)
        if len(parts) < 5 or "r1_playcap_watch.py" not in ln:
            continue
        pid, ppid, comm, et, args = parts
        rows.append((int(pid), int(ppid), et, "bash" if comm == "bash" else comm))
    print("== WATCHER INSTANCES (shared dir) ==")
    parents = {p for p, pp, _, _ in rows}
    orphans = [(p, pp, et, c) for p, pp, et, c in rows if pp not in parents]
    for p, pp, et, c in sorted(rows):
        print(f"  pid {p} ppid {pp} [{c}] up {et}"
              + ("   <- orphaned (ppid not a watcher proc)" if pp not in parents else ""))
    print(f"  total processes: {len(rows)}  orphaned: {len(orphans)}")
    return len(rows), len(orphans)


def tail_shape(n=400):
    out = subprocess.run(["tail", "-n", str(n), JSONL],
                         capture_output=True, text=True, errors="replace").stdout
    keysets = collections.Counter()
    per_turn = collections.Counter()
    distinct = collections.defaultdict(set)
    bad = 0
    kept = 0
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        kept += 1
        try:
            j = json.loads(line)
        except Exception:
            bad += 1
            continue
        keysets[tuple(sorted(j.keys()))] += 1
        t = j.get("turn")
        per_turn[t] += 1
        distinct[t].add(hashlib.md5(line.encode()).hexdigest())
    print(f"== TAIL SHAPE (last {kept} rows) ==")
    print(f"  bad json lines: {bad}")
    for t in sorted(k for k in per_turn if k is not None):
        print(f"  turn {t}: rows={per_turn[t]} distinct={len(distinct[t])}")
    print("  key shapes (top 4):")
    for ks, c in keysets.most_common(4):
        print(f"    n={c}: {','.join(ks)}")
    return keysets


if __name__ == "__main__":
    sitting = trigger_a()
    game_procs()
    watchers()
    tail_shape()
    print("\nNOTE: r1_stream.observations(trust=True) dedupes per the t85b "
          "jsonl `seen` law, so per-EVENT mining is safe; per-ROW counting of "
          "the raw file is not.")
