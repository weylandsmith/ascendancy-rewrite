# t116 — IDLE re-check #3 (working notes)

Session start 2026-10-27 21:47 EDT. Assignment: STATE.md IDLE block —
two-trigger probe only, no watch, no census (stop-report §6 discipline).

## P1 — trigger (A) NEW CAPTURE: NEGATIVE (measured 21:48:52 EDT)
- Newest playcap dir: work/r1/playcap-20261014-224611 (unchanged).
- work/r1/playcap/live-timeline.jsonl mtime 2026-10-26 15:44:01.304000000
  size 5691796463 B — 6th consecutive byte-identical reading (t111..t116).
- `ps -eo comm | grep -c '^dosbox'` = 0 (ps form, not pgrep — t114 trap).
- `find work/r1 -type f -newermt 21:47` sweep: ONLY harness bookkeeping
  under work/r1/loop/ (prompt-38.txt, loop.log, iter-20261027-214701-38.log,
  preflight_gate.log). No capture-side file anywhere.
- r1_t85g_sitting.py correctly NOT run.

## P2 — trigger (B) USER DECISION: NEGATIVE, with a NEW PROBE PITFALL
- HEAD a0d3c2a (t115), tree clean (`git status --porcelain` empty, incl.
  --untracked-files=all). No STEERING file.
- PITFALL FOUND: `find docs -newermt <HEAD commit time>` lists FIVE files
  (re/text.md, re/modules.md, re/economy.md, re/gizmos.md, re/fnt.md,
  mtimes 21:46:27–21:46:41) yet `git diff HEAD` is EMPTY. Cause: this
  iteration's harness ran `preflight_gate.log` (gate ALL CHECKS PASS) at
  ~21:46, AFTER the t115 commit (21:45:13) and BEFORE session start — the
  gate stages read/verify these docs (gate.sh:144-150, 281 check gizmos/
  economy/fnt directly) and the touching is mtime-only, zero content delta.
  LAW: for trigger (B), mtime is NOT decisive — `git diff HEAD` (content)
  is. An mtime-only doc touch after the last commit is harness noise, not
  a user answer.
- stop-report §3 answer still outstanding.

## P3 — infra alive, negatives trustworthy
- Xvfb :9 pid 1196 (11d), x11vnc pid 1207 (11d), watcher pid 27772 (bash
  wrapper) + 27774 (python child) 1d14h — the pair is normal (t115 note).
- work/r1/vnc/x11vnc.log mtime 2026-10-27 17:30:18.172 / 30114 B unchanged
  since t112 — still zero connects against the t111-FIXED launch path
  (last entries: 17:30:18 client resolution-change requests, all pre-fix).

## Verdict
No trigger. Honest negative; loop stays IDLE at 12 closed / 6 open. No
ledger row touched, no code changed, no watch/census run.
