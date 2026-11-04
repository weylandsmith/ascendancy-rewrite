# t151 WIP — IDLE re-check #38 (2026-10-28, session start 02:19:44 EDT)

Task: IDLE two-trigger probe only (t113 loop-end rule; STATE.md NEXT ACTION).
Deliverables: stop-report.md §44 appended, this file. No ledger row touched,
no scripts/ change, no game/ touch, no watch/census run against live capture.

## Measurements (all from real execution this session)

(1) TRIGGER A NEGATIVE — `python3 scripts/r1_idle_probe.py` RC=0 at 02:19:44
    (session-start cutoff 02:17:58):
  - newest playcap dir playcap-20261014-224611
  - live-timeline.jsonl mtime_ns 1793043841304000000 / 5691796463 B
    (41st consecutive byte-identical reading t111..t151); independently
    re-statted via `stat -c '%Y %y %s'` — exact match, equal to
    BASE_MTIME_NS/BASE_SIZE at r1_idle_probe.py:55-56.
  - NEW this turn: CONTENT signature of the frozen timeline recorded as a
    second, stronger invariant than mtime/size (t116 content-over-mtime law
    applied to the (A) baseline itself):
      head -c 65536 md5 = 42a0bed0507f9052e2009ec94e9c27f1
      tail -c 65536 md5 = 1529ab1ad70ac360f441d819703f943f
      last line = {"file": "60.sav", "turn": 1254, "T": 50, "score_stars": 14,
                   ...}  (idle-boot signature, t111 hygiene law)
    Future turns: if mtime/size ever move but these md5s match, it is an
    mtime touch, not a sitting; if the tail md5 differs, a real ingest
    happened regardless of size. Do NOT re-md5 the whole 5.7 GB file — head
    and tail 64 KiB only, per the stream-never-inhale law.
  - zero dosbox procs; find sweep non-loop: none
  - A4 watcher ALIVE pid 27774 (PPid 27772 wrapper pair = normal, t115 law),
    wchan=hrtimer_nanosleep State S (5 s poll tick), fds verified fresh:
    1/2->watch.out, 3->live-timeline.jsonl, 4->watch.log
  - A5 none (save/*.sav = 20, all match the watcher glob)

(2) TRIGGER B NEGATIVE — clean tracked tree at 39dcdc2, no STEERING file,
    B3 HEAD == journal row 72 sha 39dcdc2 (journal re-read independently:
    row 72 ct 02:17:05). Prompt route cross-checked BY HAND (numeric sort ->
    prompt-73 vs prompt-72, 58/58 lines, digit-stripped delta 0 exit 0) —
    identical verdict to the tool leg. §3 answer outstanding after 38 idle
    turns.

(3) RE-VERIFICATION LAW RUN (t147/t150 law — resolve from source, do not
    trust): prompt enumeration r1_idle_probe.py:335-341 IS the numeric _num
    sort (t144 trap cannot recur); r1_playcap_watch.py:161 IS the lowercase
    glob.glob(save/*.sav) poll line; r1_slot.py:49 IS the .anch-cache.json
    path inside anchors_cached(); bank hygiene `grep -rln stop-report
    scripts/` -> only r1_idle_probe.py docstring + its .pyc, so nothing
    regenerates stop-report.md (file 1468 lines, zero diff vs HEAD pre-
    append). Ledger audit fresh: rows=18 open=[OQ-003,OQ-005,OQ-016,OQ-019,
    OQ-021,OQ-023] closed=12, LEDGER AUDIT OK.

(4) Infra unchanged since t112 (Xvfb 1196 / x11vnc 1207 / watcher 27774;
    x11vnc.log 2026-10-27 17:30:18 / 30114 B — zero connects). Transients
    170331/170382 (probe children) per the t118 noise law. Scratch cleanup:
    /tmp/t149-watch (t149 fixture dir, left on disk by t149) removed; /tmp
    a/b.txt already gone. NO row closed (strict-close honest negative), no
    law falsified.
