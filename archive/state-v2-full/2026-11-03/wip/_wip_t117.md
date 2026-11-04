# T117 — IDLE RE-CHECK #4 (two-trigger probe only, per stop-report §6)

Session start 2026-10-27 21:54:50 EDT — this iteration is harness iter-39
(`work/r1/loop/iter-20261027-215450-39.log`; iter-38/21:47:01 was t116). P1's
manual sweep used cutoff 21:47:01 — looser than the true start, so its negative
stands a fortiori; the tool's sweep at the true 21:54:50 cutoff is also
negative (4 files, all work/r1/loop/).
Assignment = docs/STATE.md "## NEXT ACTION": the IDLE two-trigger probe and
nothing else. No watch, no census, no capture, no sitting adjudication.

## P1 — trigger (A) NEW CAPTURE: NEGATIVE (measured 21:56:50.133 EDT)
- Newest `work/r1/playcap-*` dir: `playcap-20261014-224611` (unchanged since
  t111; `ls -1dt` order verified, next newest 20261014-214407).
- `work/r1/playcap/live-timeline.jsonl`: mtime **2026-10-26 15:44:01.304** /
  size **5691796463 B** — 7th consecutive byte-identical reading (t111..t117).
- Zero dosbox processes: `ps -eo pid,comm | grep -c '[d]osbox'` -> `0`
  (bracket-class form; avoids the t114 pgrep self-match false-positive trap).
- Session-cutoff sweep `find work/r1 -type f -newermt '2026-10-27 21:47:01'`
  -> **11 files, all in work/r1/loop/** (harness bookkeeping). Directory-level
  roll-up (`| sed 's|/[^/]*$||' | sort | uniq -c`) confirms one single dir
  carrier = no capture-side file exists anywhere under work/r1.
- `scripts/r1_t85g_sitting.py` correctly NOT run (no sitting to adjudicate).
- NEW SWEEP HYGIENE NOTE: with a LOOSER cutoff (~21:00) the sweep also lists
  `work/r1/selftest-t111-playcap/*` (mtimes 21:10:42-50, the t111 self-test
  run) and `work/r1/.anch-cache.json` (21:10:54, the r1_slot.py:49 anchor
  cache written by that same self-test analyzer). Neither is capture activity;
  cut the sweep at SESSION START, and if a looser window is used, attribute
  selftest-* + .anch-cache.json to the t111 harness before alarming.

## P2 — trigger (B) USER DECISION: NEGATIVE (content-adjudicated per t116 law)
- `git diff HEAD --name-only` -> 0 lines; `git status --porcelain
  --untracked-files=all` -> empty. HEAD = 50f098e (t116).
- No `docs/STEERING*` / `STEERING*` file anywhere (grep over docs/*.md hits
  only STATE.md prose describing the trigger).
- No harness steering note prepended: `head -3` + `grep -n -i steering
  work/r1/loop/prompt-39.txt` -> only the standing instruction line 14, i.e.
  this iteration's prompt is the generic loop prompt.
- The stop-report §3 answer (defaults accept/reject, capture authorization,
  t89a code-work resumption) is still outstanding.

## P3 — infra liveness (makes the negatives trustworthy)
- Xvfb pid 1196 (11d uptime), x11vnc pid 1207 (11d), watcher pair 27772
  (bash wrapper) + 27774 (python3 child, 1d14h) — the PAIR is normal.
- `work/r1/vnc/x11vnc.log` mtime **2026-10-27 17:30:18.172** / 30114 B —
  unchanged since t112. 138 `Client` lines total, last two are the 17:30
  resolution-change/resize-prohibited pair; every connect predates the t111
  DISPLAY-autodetect fix (21:09), so still ZERO connects against the fixed
  launch path.

## P4 — bank-law pre-check
- `ls docs/re/_wip_t11*.md` shows t110..t116 hand-authored; grep of scripts/
  (t115/t116) found no generator for stop-report.md or _wip_*.md. Files this
  iteration touches (stop-report.md, _wip_t117.md, OPEN-QUESTIONS.md,
  STATE.md) are hand-authored — safe to hand-edit.

## P5 — NEW TOOL scripts/r1_idle_probe.py (the iteration's deliverable)
Idle turns 111-116 each re-derived the same probes by hand. The tool now runs
them in one shot (RC=0 both negative / RC=1 armed / RC=2 probe error) and
encodes the probe laws. Defects found by EXECUTION while authoring — kept
because they are exactly the traps a fresh session hits blind:
  D1 wrong path `work/r1/live-timeline.jsonl` -> printed "timeline missing"
     while a manual `stat` on the real path (work/r1/playcap/...) succeeded.
  D2 `git status --porcelain --untracked-files=all` ARMED (B) on this loop's
     own files (_wip_t117.md, the probe). (B) now keys on `git diff HEAD` +
     TRACKED porcelain lines; untracked is printed for information only.
  D3 hand-typed baseline mtime_ns was wrong (correct `stat %Y` =
     1793043841304000000). Accidental POSITIVE CONTROL: with D3 in place the
     tool reported ARMED + "timeline grew past frozen baseline", so the
     growth-detect leg is live rather than decorative.
  D4 session-start cutoff: prefer the timestamp baked into the iter-*.log
     NAME (spawn-time; on t117 == prompt-39 mtime 21:54:50 exactly), prompt
     mtime as fallback. Using "now" is too tight — a capture earlier in the
     same session would be missed. (An earlier draft of this note claimed an
     ~8-min prompt drift; that was MY misattribution — t116 ran iter-38 at
     21:47, t117 is iter-39 at 21:54:50, no drift measured. Retracted here
     same-turn per no-fabrication law.)
  D5 (design, not a bug) mid-iteration re-runs armed (B) on the loop's OWN
     doc edits (STATE.md, stop-report.md). Fix is NOT a silent suppression:
     `docs/STATE.md` is itself the assignment carrier, so suppressing it could
     hide a real user answer. Delta outside loop-owned paths => ARMED;
     loop-owned-only => NEGATIVE with a printed CAUTION naming the files.
Final run 22:01:45: TRIGGER A NEGATIVE, TRIGGER B NEGATIVE, VERDICT IDLE,
RC=0 — agrees with every manual reading in P1/P2/P3 signal-for-signal.

## Verdict
No trigger fired. NO ledger row touched, NO row closed (strict-close honest
negative), no banked law falsified, no new tool, no code change.
NEXT = same two-trigger probe (stop-report §10 wording), loop stays IDLE.
