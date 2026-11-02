# _wip_t267 — HARNESS SELF-HEAL (in-flight scratch; findings banked here as measured)

## PRE-FLIGHT STATE (measured 2026-11-02 ~04:25 EST, this session)
- git tree CLEAN at babbc17 (t266 landed). No steering file. No STOP flag.
- Game ALIVE: dosbox-x PID 535172, started Sun Nov 1 23:03:57, conf
  work/r1/vnc/session.conf, -nogui -time-limit 28800.
  TL EXPIRY WALL = 23:03:57 + 28800 s = 07:03:57 (Nov 2). ~2.6 h from this
  pre-flight. The t266 I3 root cause (TL expiry kills the game silently at
  launch+TL) means the NEXT death of :9 is PREDICTABLE, not random.
- Watchers on work/r1/playcap: THREE live python instances — 524207 (start
  Nov 1 18:40:11), 524532 (start Nov 1 18:49:13), 535187 (start Nov 1
  23:03:58, the current session's; work/r1/vnc/watch.pid records its parent
  535185). Confirmed via /proc/PID/cmdline + ps lstart.
- WRITERHOOD (t215 law: writer = open fd, not process presence): ALL THREE
  hold an open fd on live-timeline.jsonl (per-fd census /proc/PID/fd). This
  is the t266 two-writer collision class, now THREE writers.
- COLLISION MEASURED LIVE (this session, last 400 KB tail, rows wall 04:25:59
  .. 04:26:41): 16 rows = only 6 distinct (file, file_mtime_ns) slot-keys;
  reps histogram {3x5, 1x1} — every ring write lands as THREE timeline rows
  because each watcher keeps its OWN in-memory `seen` set and none can see
  the others' appends. The dedup law in r1_playcap_watch.py (jsonl-derived
  `seen` at start) only dedups within a watcher's lifetime, never across
  concurrent watchers. t266's oscillation forensics read data with this
  3x amplification factor live in it.
- Ring is CURRENT right now: save/49.sav mtime 04:25:45.952, 10 s cadence
  holds (45..49 at exactly 10 s spacing), turn frozen at 1236 (idle title /
  in-game no-turn-advance — NOT a softlock signature per t266: needle check
  required for liveness, full-frame diff is always-alive on the starfield).

## WHY THE t266 FAILURE MODE NEEDS A DETECTOR (scope, verbatim from queue)
15:45 game death (TL expiry of the 07:46 launch) went unnoticed ~1.5 h.
loop_one_task.sh (scripts/loop_one_task.sh:179-183) only runs
r1_idle_probe.py when IDLE_GATE=1; production runs use IDLE_GATE=0
(tmux ascendloop: MAX_ITERS=14 IDLE_GATE=0), so NOTHING checks game liveness
between iterations. dosbox.pid records 535172 but nothing polls kill -0.

## DESIGN (decided before writing code)
- New scripts/r1_game_health.py: stdlib-only, exit codes 0 HEALTHY / 1
  UNHEALTHY (with machine-readable reason list) / 2 instrument broken;
  ALWAYS prints one summary line + writes/updates
  work/r1/loop/GAME_HEALTH_LIVE.txt (atomic tmp+rename) and appends
  work/r1/loop/game_health.tsv history. NEVER opens live-timeline.jsonl
  (OOM law) — ring mtime is the feed-arrival signal.
  Checks: (a) game process alive by RECORDED pid in work/r1/vnc/dosbox.pid
  (verify /proc comm == dosbox-x, never pattern-signal); (b) TL expiry from
  /proc/PID starttime + -time-limit arg parsed from its own cmdline ->
  warn_at = expiry - WARN_AHEAD (default 600 s); (c) watcher liveness:
  count python procs whose cmdline is r1_playcap_watch.py on OUT_DIR,
  >1 => UNHEALTHY multi-writer; (d) feed freshness: newest save/*.sav mtime
  age > 60 s (10 s cadence law, 6x margin) => feed stalled;
  (e) bring-up-verify: newest slot mtime landed within VERIFY_WINDOW (30 s).
- scripts/r1_playcap_vnc.sh: 'status' calls the health tool; 'start' runs
  bring-up-verify after launching (poll ring mtime up to 30 s, print
  BRINGUP OK/FAIL); reaper extended to catch the multi-writer class.
- scripts/r1_watch_reaper.py: targeted kill ONLY — every r1_playcap_watch.py
  process on OUT_DIR except the newest-started one; each victim verified via
  /proc/PID/comm == python* AND cmdline contains the script path AND the
  OUT_DIR path; refuses pattern-kills (pkill -f self-match footgun).
- loop_one_task.sh: cheap health check logged between iterations (non-fatal,
  advisory), so a death is stamped in loop.log with wall time even under
  IDLE_GATE=0. Keep it one line + no new deps.

## SHIPPED + VERIFIED (this session)
1. scripts/r1_watch_reaper.py — targeted /proc-verified reaper (comm python*
   AND cmdline holds script name AND OUT dir; keeps newest-started; SIGTERM
   only; no pattern-kills). DRY-RUN first, matched t266's recorded stale pair
   exactly; REAL RUN: REAPED 524532 + 524207, KEPT 535187; post-census 1
   watcher; /proc confirms both victims GONE, keeper holds the single
   timeline fd. Multi-writer duplication (3x) stops at the source from
   04:29 onward.
2. scripts/r1_game_health.py — exit 0 HEALTHY / 1 UNHEALTHY / 2 broken.
   Checks G (recorded pid + comm), T (TL expiry from /proc ctime + cmdline
   arg — MEASURED on live game: expiry 2026-11-02 07:03:58, 9147 s left at
   04:31, matches hand-computation launch 23:03:57+28800 exactly), W
   (watcher census, >1 => MULTI-WRITER with reaper pointer), F (ring-slot
   mtime age > 60 s => FEED-STALE; NEVER opens the timeline jsonl — OOM law),
   B (bring-up verify: ring row within 30 s, env BRINGUP=1).
   Artifacts: work/r1/loop/GAME_HEALTH_LIVE.txt (atomic), game_health.tsv
   (append history), GAME_DEAD.txt written ONLY on G:DEATH.
   First live run 04:31:30: HEALTHY (pid 535172; watcher 535187; ring age 5s).
3. r1_playcap_vnc.sh wiring: 'status' now runs the health check; 'start'
   runs BRINGUP=1 verify after launch; reaper loop at start calls
   r1_watch_reaper.py in addition to the pid-file sweep (kills the class the
   pid files miss).

## FINAL (task complete)
- Full lifecycle E2E proven in isolated sandbox (:10, copied scratch, TL=120):
  BRINGUP OK -> T:WARN 100 s pre-expiry -> TL kill -> G:DEATH + GAME_DEAD.txt.
  Adoption guard proven (rm pidfile + live game -> ADOPTED, one dosbox).
  Sandbox fully torn down; production :9 never touched (foreign census
  logged it correctly from the sandbox's point of view).
- Production post-reap timeline tail: reps all 1 (duplication gone).
- Full findings + honest negatives: docs/re/selfplay.md t267 block.
- NEXT = t268 VERBATIM (queue order; research resumes; t268 pre-flight must
  run r1_game_health.py — production TL expires 07:03:58 today).
