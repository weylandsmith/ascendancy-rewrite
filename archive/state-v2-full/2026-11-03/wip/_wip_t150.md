# t150 — IDLE re-check #37 (2026-10-28, session start 02:10:24 EDT) — WIP

Probe run 02:10:24, RC=0, VERDICT IDLE. Independent re-stats (outside probe):

- timeline mtime_ns 1793043841304000000 / size 5691796463 B — matches probe
  constants r1_idle_probe.py:55-56 (BASE_MTIME_NS/BASE_SIZE) and baseline
  (40th byte-identical reading t111..t150).
- git tree clean (diff HEAD empty, porcelain tracked empty), HEAD 61d32e2 ==
  journal row 71 sha (re-read independently). No STEERING.
- Prompt route re-checked by HAND (the t144/t145 burned route): numeric sort
  gives pair prompt-72 vs prompt-71 (58/58 lines), digit-stripped diff 0 lines,
  diff exit 0. Agrees with the tool leg.
- procs: Xvfb 1196, x11vnc 1207, watcher 27774 — zero dosbox. Watcher
  /proc/27774 wchan=hrtimer_nanosleep State S (5 s poll tick, not wedged);
  fds 1/2->watch.out, 3->live-timeline.jsonl, 4->watch.log.
- A5: none (save/*.sav = 20, all match watcher glob).
- Bank hygiene: grep -rln stop-report scripts/ -> only r1_idle_probe.py (+pyc);
  stop-report.md zero diff vs HEAD at 1416 lines before appending §43.
- Citation re-verification (t148 law applied to cited code sites, not only
  probe constants): r1_playcap_watch.py:161 IS the lowercase
  glob.glob(os.path.join(out,"save","*.sav")) line; r1_slot.py:49 IS
  cache = .../work/r1/.anch-cache.json inside anchors_cached(). Both alive.

No row closed (strict-close honest negative). No watch/census run. game/
untouched. NEXT stays IDLE.
