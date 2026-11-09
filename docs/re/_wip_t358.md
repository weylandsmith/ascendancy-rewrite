# _wip t358 — D1-RULING APPLICATION (CONDITIONAL): CONDITION NOT MET, honest negative, proceed to t359

## S0 Condition check (the assignment's gate), cited
- Sitting check NEGATIVE: work/r1/playcap/live-timeline.jsonl 8,868,782,651 B
  (mtime 2026-11-09 11:51:35), 400 KB tail-seek, 16 records parsed, turn 1086
  on 16/16 == corpus floor; newest tail files 42/43/44.sav (ring rotation).
  r1_t85g_sitting.py correctly NOT run.
- D1 gate: `grep -c "^USER: D1 mouse" docs/DECISIONS.md` = 0 (exit 1). The only
  USER: lines are the 2026-11-09 chat-scribe block L151-157: D2=(b) commissioned,
  "D1 = ruling page live (work/r1/d1page); D1 answer to follow via page submit",
  D3 DEFERRED. No D1 verdict exists on any path (no *ruling*/*reply* files).
- DECISIONS.md mtime 2026-11-09 11:39:08 = the committed USER RULING block
  (commit 09d3ccd 11:46:18); git status --porcelain EMPTY. decision-sheet.md
  mtime unchanged 03:40:49.800 (t347 generator output).
- Production :9 HEALTHY: pid 1555 up 11:54:48, watcher 1575, ring 58.sav age 2s,
  TL expiry 2026-11-11 01:07:10 (work/r1/loop/GAME_HEALTH_LIVE.txt).

## S1 HARNESS FACT LANDED (the one new measurement this iteration)
- The d1page ruling server IS LIVE: pid 43067 listening 0.0.0.0:8613, but
  /proc/43067/cwd = work/r1/d1page while `python3 server.py` resolved to the OLD
  /tmp/d1page/server.py copy (diff: /tmp copy has ROOT=/tmp/d1page and the
  UNPATCHED path handler `p = os.path.join(ROOT, self.path)` — no traversal
  guard; the patched copy in work/r1/d1page/server.py restricts to ROOT/img and
  appends the USER block to REPO/docs/DECISIONS.md identically).
  Both copies share REPO=/home/hrethric/projects/ascendancy, so a page SUBMIT
  still appends the USER block to docs/DECISIONS.md (the trigger works); but the
  served page is the /tmp copy's (same index.html bytes, 7803 B, both mtimes
  10:56/11:35) and image requests go through the UNPATCHED handler.
  ACTION FOR USER/next session: kill 43067 and relaunch
  `python3 server.py` from work/r1/d1page to get the path-traversal-safe handler.
  (Do not kill from this loop unilaterally — it is the user's ruling channel.)

## S2 Disposition
- Condition not met => assignment's own exit ramp: honest negative banked here,
  NEXT rewritten to t359 VERBATIM (no parking; the sentinel is retired while the
  phase-7 queue has work). No OQ row touched; no DECISIONS/OQ edits (nothing to
  apply). Ledger stays 16/3.
