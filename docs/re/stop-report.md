# STOP-REPORT — Ascendancy RE + rewrite closeout (t110, 2026-10-27)

This is the loop's stop-report per GOAL.txt ("record one line and move
on") and docs/STATE.md's t110 assignment. It states outcome status, the
exact list of what only a new capture or a user decision can lift, and
the recommended capture protocol. No row was closed by this report
(strict-close: bookkeeping is not measurement).

## 1. Outcome status

Ledger (verified this session, fresh re-derivation, not inherited):
`python3 scripts/ledger_audit.py` ->
rows=18, closed=12,
open = OQ-003, OQ-005, OQ-016, OQ-019, OQ-021, OQ-023.
Gate green every iteration of t98..t110; the rewrite plays to victory
(PLAYTHROUGH.md, regenerated t89); all subsystem specs cited in docs/re/.

The t106-t109 epoch audited the census tooling that earlier closures rest
on: three verifier defects found and fixed (base==candidate
self-verification, objdump wrapped-tail coverage, non-mov write ops),
every census-cited claim re-verified under the authoritative function-
start decode, count columns purged, and NO banked law falsified
(docs/re/census-audit.md S1-S10). The static corpus is exhausted:
this session re-checked every open row's text against docs/REFUTED-ROUTES
(R1-R14) and found no offline static route that can move a row under
strict-close.

## 2. What only a NEW CAPTURE can lift

One user-run session of the ORIGINAL game lifts the three biggest rows
(t82 collapse, docs/BLOCKED.md "t82"):

- OQ-021 (victory threshold, >1/2 vs 2/3): needs the comparator to fire
  — colonize past 50% of stars with the autosave ring running. Fast
  declarative alternative in-session: press `C` on the starmap (debug
  State-of-Galaxy, docs/re/debugflags.md t85f) — it prints PERCENT
  CONTROLLED = 100*DAT_000482fb/T, the comparator's own formula output.
- OQ-023 (relation-state enum): needs one matrix cell actually holding
  3 (Alliance). State-3 is UNOBSERVED across 42k trusted rows
  (OPEN-QUESTIONS t85g). In-session route: raise Orfa attitude above
  ACCEPT_ALLIANCE=570 (gifts/trades — proposal alone gives +39 AI-side,
  487->526 measured t85g, not enough), then propose and see acceptance.
- OQ-010 (already CLOSED t89 at aggregate level): a battle in the same
  sitting additionally banks slot-diff damage-application evidence that
  strengthens the OQ-019 caveats, at zero extra protocol cost.

Separate capture-class residuals:
- OQ-016: the 0x4402a event-dispatch caller of the +0x55 word-writer,
  per-cell terrain/nuke wiring, home-placement verification, +2
  minutiae, live-UI-trace armer (OPEN-QUESTIONS OQ-016 t108/t109 tails).
- OQ-019: per-turn step CLAMP law (walk body 0x533e0 + callers) and the
  build/redesign inventory path; sugar-cube->hop scale is
  BLOCKED-USER-LEVEL — two measured zero-observation corpora (t49 idle:
  2260 slot-pair obs, 0 state-4; t58 scripted campaign to t52: 565 obs,
  0 flights) prove no save-observable route contains flight without
  real play.
- OQ-003: packed-entropy regions need play-mutation variants (mutate
  channel words +0x44..+0x4f before turns advance and watch production)
  or stay parked (docs/BLOCKED.md t49 step 1-2).

## 3. What only a USER DECISION can lift

- Accept-or-reject the remaining documented defaults, which strict-close
  forbids us to close ourselves: OQ-003 entropy regions, OQ-005 .shp
  dims-location (closure class = human-verifiable drawn frame; a 7th
  blind sweep is FORBIDDEN per GOAL/R2), OQ-019 sugar-cube
  [1,3]+immediate-arrival (not contradicted by either zero-corpus),
  OQ-023 threshold-only-branch AI behaviour (option C hybrid: build the
  TRADE/third-party engine only when the ownership model lands).
- Whether to authorize a capture sitting at all (sections above assume
  yes; if no, the loop has nothing left that can close a row and the
  honest end-state is "12 closed / 6 open, capture-gated").
- Whether to resume the t89a-interrupted follow-on code work
  (research leg closed; the interruption was session budget, NOT a
  research block — docs/BLOCKED.md t89a).

## 4. Recommended capture protocol (one sitting)

Script: scripts/r1_playcap.sh (banked READY t82; nothing scripted —
real play is the whole point).

    cd ~/projects/ascendancy && ./scripts/r1_playcap.sh
    # TL=1500 default (25 min); override: TL=3600 ./scripts/r1_playcap.sh
    # DISPLAY (t111): the old default ":0" does NOT exist on this host
    # (/tmp/.X11-unix has only socket X9) — a bare run died inside dosbox
    # with zero slots and no diagnostic. The script now auto-detects the
    # answering display (verified: resolves :9, self-test captured 9
    # slots). To play visually: VNC viewer -> localhost:5910 (x11vnc on
    # Xvfb :9; 800x600, viewer resize requests are refused by design),
    # then run the script; the game window appears on that screen.

Invariants (enforced by the script + gate 3n, docs/BLOCKED.md):
- runs ONLY against the scratch copy work/r1/game — game/ is NEVER
  mounted; dosbox-x killed via `pkill -x dosbox-x` only; output bounded
  to work/r1/playcap-<ts>/; autosave ring autosave=10 41-60.
- Turn advance is never automatic (cadence law: 14 idle runs held turn
  constant); each NEXTTURN click landed ON THE STRATEGIC MAP advances
  exactly +1 turn; modal screens swallow clicks — schedule by time,
  verify by turn.

Minimum play checklist, in order, one sitting:
1. build/expand; colonize past 50% of stars (OQ-021); press `C` on the
   starmap when you want the percent readout banked immediately.
2. raise an AI attitude (gifts/trades) and get an ACCEPTED alliance —
   a relation cell holding 3 (OQ-023); a proposal that is declined is
   still bankable but does not close the row.
3. let two fleets exchange fire once, end turn (OQ-010 slot-diff,
   feeds OQ-019 caveats).
4. quit normally (or let the time-limit end the run).

Afterwards: mtime of a new playcap dir (or an updated
work/r1/playcap/live-timeline.jsonl) is the trigger; the next loop
session runs scripts/r1_t85g_sitting.py-style adjudication on the new
turn-boundary sitting per docs/STATE.md NEXT ACTION, with the
T>0-only slot-adjudication law (title-menu slots read T=0 with
uninitialized selector).

## 5. Honest negatives banked this iteration

- No ledger row moved (strict-close; no measurement this session).
- No new tool. No banked law falsified. Static routes: exhausted for
  every open row (this session's re-check, rows + REFUTED-ROUTES).

## 6. LOOP-END PROPOSAL (t113, 2026-10-27 21:35 EDT)

The t111 rule fires: three consecutive watches (t111, t112, t113) came
back empty. Final watch re-measured 2026-10-27 21:30 EDT —
live-timeline.jsonl mtime 2026-10-26 15:44:01.304 / 5691796463 B
byte-identical; newest playcap dir still 20261014-224611; no dosbox
process; watch infra alive (Xvfb :9, x11vnc :5910,
r1_playcap_watch.py --no-exit) so the negative is trustworthy; x11vnc.log
unchanged at 17:30:18 (still zero connect attempts against the
t111-FIXED launch path); git clean and no doc edited by the user since
t112 (no §3 answer arrived).

PROPOSAL: end the autonomous loop at 12 closed / 6 open. The six open
rows cannot be moved autonomously:
- capture-gated: OQ-016 (residual minutiae + live-UI-trace armer),
  OQ-019 (per-ship model), OQ-021 (end-ctrl threshold), OQ-023
  (state-enum value for war/allied) — each needs a real sitting per §2.
- user-decision-gated: OQ-003 (packed-entropy residue), OQ-005 (.shp
  dims; closure class = human-verifiable drawn frame) — plus the §3
  default accept/reject list.

Re-open path (either event, any time):
1. A capture: `bash scripts/r1_playcap.sh` (autodetects the :9 display;
   one-sitting checklist in §4). The new playcap dir or timeline growth
   is the trigger.
2. A §3 answer: answer the default/capture/code-work questions in §3;
   that answer becomes the next loop assignment verbatim.

Until one of those arrives, docs/STATE.md NEXT ACTION is IDLE and the
loop should not burn further iterations on watches.

## 7. IDLE re-check #1 (t114, 2026-10-27 21:45 EDT)

Per §6 the loop is event-driven: this turn did NOT run a watch or a
census, it only tested the two re-arm triggers once, fresh.

- (A) NEW CAPTURE — negative. Newest playcap dir still
  `work/r1/playcap-20261014-224611`; `live-timeline.jsonl` mtime
  2026-10-26 15:44:01.304 / 5691796463 B (4th consecutive byte-identical
  reading vs t111/t112/t113); no dosbox process (`pgrep -x dosbox-x`
  empty — an `pgrep -af dosbox` self-match on the probing command line
  is a false positive, re-verified via `ps -eo comm`).
  `scripts/r1_t85g_sitting.py` correctly not run.
- (B) USER DECISION — negative. Clean tree (`git status -uall` empty),
  no harness steering note, no STEERING file, nothing edited after
  commit fd49364.
- Infra alive (Xvfb :9 pid 1196, x11vnc :5910 pid 1207, watcher pid
  27772) so the negative is trustworthy; `x11vnc.log` mtime unchanged at
  2026-10-27 17:30:18.172 — still zero connects against the t111-fixed
  launch path.

Consequence: §6 stands unchanged (12 closed / 6 open). Honest negative
banked to docs/re/_wip_t114.md; no ledger row touched. Future idle turns
should repeat exactly this two-trigger probe and nothing else.

## 8. IDLE re-check #2 (t115, 2026-10-27 21:42 EDT)

Two-trigger probe only, per §7. Both measured NEGATIVE on fresh reads
(full measurements in docs/re/_wip_t115.md):

- (A) NEW CAPTURE — negative. Newest `work/r1/playcap-*` dir
  `20261014-224611`; `live-timeline.jsonl` mtime 2026-10-26 15:44:01.304 /
  5691796463 B (5th byte-identical reading t111..t115); no dosbox process
  (`ps -eo comm`, no `pgrep -af` self-match). Strengthened probe added this
  turn: `find work/r1 -type f -newermt <session start>` returns ONLY
  harness bookkeeping under `work/r1/loop/` — no capture-side file anywhere.
  `r1_t85g_sitting.py` correctly not run.
- (B) USER DECISION — negative. Clean tree at f1b1fde, no STEERING file, no
  harness note, no doc edited after the t114 commit. §3 answer outstanding.
- Infra alive so the negatives are trustworthy: Xvfb 1196, x11vnc 1207,
  watcher 27772/27774 (bash wrapper + python child — the pair is normal,
  not a duplicate watcher); `x11vnc.log` mtime unchanged at 17:30:18.172,
  still zero connects against the t111-fixed launch path.
- Bank-law pre-check: no script generates `stop-report.md` or `_wip_*.md`
  (grep hits are comment cross-refs only); PLAYTHROUGH.md untouched.

Consequence: §6 LOOP-END PROPOSAL unchanged, 12 closed / 6 open. NO row
closed this turn (strict-close honest negative). Future idle turns: run
exactly this probe — timeline/dir mtime + the `find -newermt` sweep + ps,
then gates, commit, stop.

## 9. IDLE re-check #3 (t116, 2026-10-27 21:52 EDT)

Three-probe probe, same result. Working notes `docs/re/_wip_t116.md`.

- (A) NEW CAPTURE: negative at 21:48:52. Newest playcap dir
  `20261014-224611`; `live-timeline.jsonl` mtime 2026-10-26 15:44:01.304 /
  5691796463 B — 6th consecutive byte-identical reading (t111..t116); zero
  dosbox processes (`ps -eo comm`); `find work/r1 -newermt <session start>`
  returned only `work/r1/loop/` harness bookkeeping.
- (B) USER DECISION: negative, plus a NEW PROBE PITFALL worth keeping.
  `find docs -newermt <HEAD commit time>` listed five docs
  (re/text, re/modules, re/economy, re/gizmos, re/fnt) with post-commit
  mtimes — yet `git diff HEAD` was EMPTY. Root cause: this iteration's
  preflight gate ran ~21:46, after the t115 commit and before the session
  started, and its verification stages touch those files (gate.sh checks
  gizmos/economy/fnt contents directly) with ZERO content delta. LAW: for
  trigger (B) trust `git diff HEAD` (content), never mtime — an mtime-only
  doc touch after the last commit is harness noise, not a user answer.
  Tree clean at a0d3c2a, no STEERING file, §3 answer still outstanding.
- Infra alive so the negatives are trustworthy: Xvfb 1196, x11vnc 1207,
  watcher 27772+27774 (wrapper+child, normal); `x11vnc.log` mtime
  17:30:18.172 / 30114 B unchanged since t112 — zero connects against the
  t111-FIXED launch path.

Consequence: §6 LOOP-END PROPOSAL unchanged, 12 closed / 6 open. NO row
closed (strict-close honest negative). Future idle turns: run the same
three probes with the CONTENT-diff rule for (B).


## 10. IDLE re-check #4 (t117, 2026-10-27 22:01 EDT) — probe TOOLIZED

Three-probe probe, same result, plus the iteration's one real deliverable: the
hand-run probe is now a script. Working notes `docs/re/_wip_t117.md`.

- **NEW `scripts/r1_idle_probe.py`** (RC=0 = both triggers negative, RC=1 = a
  trigger armed, RC=2 = probe failure). Idle turns should run this instead of
  re-implementing the probes, so the four hard-won probe laws cannot be
  "simplified" away by a fresh session: session-start cutoff for the find
  sweep; CONTENT-diff (never mtime) for (B); `ps -eo comm` matching (never
  `pgrep -af`); untracked files are informational, never a (B) trigger.
  Two defects were found and fixed by execution during authoring — worth
  keeping because they are the traps the NEXT session would hit blind:
  (1) the timeline lives at `work/r1/playcap/live-timeline.jsonl`, NOT
      `work/r1/live-timeline.jsonl` (wrong path printed "timeline missing"
      while a manual `stat` read it fine);
  (2) `git status --porcelain --untracked-files=all` ARMS (B) on this loop's
      own mid-iteration files (`_wip_*.md`, the probe itself) — so (B) keys on
      `git diff HEAD` + TRACKED porcelain lines only, untracked shown for
      information. Baseline mtime_ns re-derived with `stat %Y` =
      1793043841304000000 after a hand-typed value was wrong by 29536000000 ns.
  Accidental positive control: with the wrong baseline the tool correctly
  reported ARMED/"timeline grew past frozen baseline", so the growth-detect
  leg is live, not decorative.
  Two more refinements after the first green run: (3) the find sweep's
  session-start cutoff prefers the timestamp the harness bakes into the
  `iter-*.log` NAME (written at spawn; on t117 it equals the prompt-39 mtime
  21:54:50 exactly — no drift measured here, NAME is just the more direct
  source; prompt mtime remains the fallback). The manual manual sweep this
  turn ran with cutoff 21:47:01 (t116's start — looser), still negative, so
  the negative holds a fortiori at the true 21:54:50 cutoff.
  (4) a mid-iteration re-run armed (B) on the loop's OWN edits (STATE.md,
  stop-report.md). The fix is deliberately NOT silent: `docs/STATE.md` is the
  assignment carrier, so a delta OUTSIDE loop-owned paths arms (B), while a
  loop-owned-only delta prints a CAUTION naming the files and stays NEGATIVE.
  Idle turns run the probe at session start, before editing anything, where the
  distinction is moot.
- (A) NEW CAPTURE: negative at 21:56:50 (manual) re-confirmed by the tool at
  22:01:45 — newest playcap dir `20261014-224611`; `live-timeline.jsonl`
  mtime 2026-10-26 15:44:01.304 / 5691796463 B, 7th consecutive
  byte-identical reading (t111..t117); zero dosbox processes; session-start
  find sweep -> 4 files, all `work/r1/loop/`. `r1_t85g_sitting.py` not run.
  Sweep hygiene note: a LOOSER cutoff (~21:00) additionally lists
  `work/r1/selftest-t111-playcap/*` and `work/r1/.anch-cache.json` (mtime
  21:10:54, written by the t111 self-test analyzer via `scripts/r1_slot.py:49`)
  — attribute both to the t111 harness, they are not capture activity.
- (B) USER DECISION: negative. Clean tracked tree at 50f098e, no STEERING file,
  and the harness prompt for this iteration (`work/r1/loop/prompt-39.txt`) is
  the generic loop prompt — `grep -n -i steering` matches only the standing
  instruction line. §3 answer still outstanding.
- Infra alive so the negatives are trustworthy: Xvfb 1196, x11vnc 1207,
  watcher 27772+27774 (wrapper+child, normal); `x11vnc.log` 17:30:18.172 /
  30114 B unchanged since t112; all 138 `Client` lines predate the t111
  DISPLAY fix — zero connects against the fixed launch path.

Consequence: §6 LOOP-END PROPOSAL unchanged, 12 closed / 6 open. NO row closed
(strict-close honest negative — bookkeeping plus tooling, no measurement of
game behaviour). Future idle turns: `python3 scripts/r1_idle_probe.py`, read
the verdict, and do not re-derive the probes by hand.

## 11. IDLE re-check #5 (t118, 2026-10-27 22:12 EDT) — probe validated by a fresh reader

`python3 scripts/r1_idle_probe.py` at 22:12:21.769 EDT -> **RC=0**, both
triggers negative; `scripts/r1_t85g_sitting.py` correctly not run. (A) newest
playcap dir `playcap-20261014-224611`; live-timeline.jsonl mtime_ns
1793043841304000000 (2026-10-26 15:44:01.304) / 5691796463 B — 8th consecutive
byte-identical reading (t111..t118); zero dosbox procs; session-start find
sweep (cutoff 22:10:42) 4 files, all work/r1/loop/. (B) clean tracked tree at
35a9027, no STEERING file, prompt-40.txt byte-identical to prompt-39.txt modulo
digits, no delta outside loop-owned paths; the §3 answer is still outstanding
after five idle turns.

THE ITERATION'S FINDING: the t117 tool survives its first use by a session
that did not author it. Every leg prints its own evidence (mtime_ns, size, dir
name, pid table, diff output), so the verdict is reproducible WITHOUT hand
re-derivation — which was the whole point of toolizing. No defect found.

INFRA NOISE NOTE (do not chase, do not treat as a trigger): the probe's INFRA
leg lists two python3 rows beyond the watcher pair — pid 127729
`tools/mcp_death_supervisor.py` (ppid 127711, started 22:10:42 = this session's
own harness) and pid 127778, which was gone by the time `ps -p` re-checked it.
The probe shells out with `shell=True`, so its own git/find/stat children are
visible in a mid-run `ps -eo` snapshot. Harmless by construction: the load-
bearing (A) leg is the capture-file sweep (no non-loop file) and the dosbox leg
matches `comm`, not a full command line. LAW: trigger evidence is dosbox
processes and capture-side files ONLY — Hermes-own and probe-own processes are
noise. Infra alive: Xvfb :9 1196, x11vnc :5910 1207, watcher 27774;
x11vnc.log 2026-10-27 17:30:18 / 30114 B unchanged since t112 (zero connects
against the t111-FIXED launch path).

Consequence: §6 LOOP-END PROPOSAL unchanged, 12 closed / 6 open. NO row closed
(strict-close honest negative), no banked law falsified, no code change.
Future idle turns: run the tool, read the verdict, bank the reading — nothing else.

## 12. IDLE re-check #6 (t119, 2026-10-27 22:18 EDT) — steady-state negative, no new findings

Session start 22:18:56.820 EDT. `python3 scripts/r1_idle_probe.py` RC=0 at
22:18:56 (9th consecutive byte-identical timeline reading t111..t119):
newest playcap dir playcap-20261014-224611; live-timeline.jsonl
mtime_ns=1793043841304000000 / 5691796463 B; zero dosbox procs; find sweep
cutoff 22:18:03 -> 4 files, all work/r1/loop/. (B) negative: clean tracked
tree at 110ea35, no STEERING file, prompt-41.txt identical to prompt-40.txt
after digit-stripping (diff empty), no delta outside loop-owned paths.
r1_t85g_sitting.py correctly not run.

Infra unchanged since t112 (Xvfb 1196, x11vnc 1207, watcher 27774;
x11vnc.log 17:30:18/30114 — zero connects against the t111-FIXED launch
path). Two short-lived python3 128932/128996 in the INFRA leg are the
probe's own shell children — per the t118 noise law, trigger evidence is
dosbox procs + capture files only.

§3 answer (accept/reject documented defaults, authorize capture sittings,
resume t89a code work) still outstanding after six idle turns. No re-arm,
no row closed, no law falsified. NEXT stays IDLE.

## 13. IDLE re-check #7 (t120, 2026-10-27 22:24 EDT) — steady-state negative

Session start 22:22:27. `python3 scripts/r1_idle_probe.py` RC=0 at
22:24:09 (10th consecutive byte-identical timeline reading t111..t120):
newest playcap dir playcap-20261014-224611; live-timeline.jsonl
mtime_ns=1793043841304000000 / 5691796463 B; zero dosbox procs; find sweep
cutoff 22:22:27 -> 4 files, all work/r1/loop/. (B) negative: clean tracked
tree at 9b9c291, no STEERING file, prompt-42.txt identical to prompt-41.txt
after digit-stripping (diff empty), no delta outside loop-owned paths.
r1_t85g_sitting.py correctly not run.

Infra unchanged since t112 (Xvfb 1196, x11vnc 1207, watcher 27774;
x11vnc.log 17:30:18/30114 — zero connects against the t111-FIXED launch
path). INFRA-leg transients 130014 (started 22:22:27 = the harness loop
runner itself) and 130066 (probe child, gone on `ps -p` re-check) — per the
t118 noise law, correctly ignored.

§3 answer still outstanding after seven idle turns. Observation worth
noting for loop economics: idle turns t114..t120 are now near-zero-cost
reproductions of the same verdict (tool encodes every leg); each additional
idle turn adds bookkeeping but zero measurement. No re-arm, no row closed
(strict-close honest negative), no law falsified. NEXT stays IDLE.

## 14. IDLE re-check #8 (t121, 2026-10-27 22:29 EDT) — steady-state negative

Session start 22:28:18 (probe cutoff) / 22:29:23 (probe run).
`python3 scripts/r1_idle_probe.py` RC=0: newest playcap dir
playcap-20261014-224611; live-timeline.jsonl mtime_ns=1793043841304000000 /
5691796463 B (11th consecutive byte-identical reading t111..t121); zero
dosbox procs; find sweep -> 4 files, all work/r1/loop/. (B) negative: clean
tracked tree at e7d736c, no STEERING file, prompt-43.txt identical to
prompt-42.txt after digit-stripping (diff empty), no delta outside
loop-owned paths. r1_t85g_sitting.py correctly not run.

Infra unchanged since t112 (Xvfb 1196, x11vnc 1207, watcher 27774;
x11vnc.log 17:30:18/30114 — zero connects against the t111-FIXED launch
path). INFRA-leg transients 131136/131252 (this session's runner + probe
child) per the t118 noise law, correctly ignored.

Bank-hygiene check done fresh this turn (per the BLOCKED.md traps rule):
`grep -rln stop-report scripts/` matches only r1_idle_probe.py, and there
merely in its docstring line 3 — no script writes the file, so §14 here is
hand-authored and safe from regeneration.

§3 answer still outstanding after eight idle turns; the §6 t113 observation
holds and sharpens: idle turns are now pure bookkeeping. No re-arm, no row
closed (strict-close honest negative), no law falsified. NEXT stays IDLE.

## 15. IDLE re-check #9 (t122, 2026-10-27 22:35 EDT) — steady-state negative

Session start 22:33:22 (probe cutoff) / 22:35:06.625 (probe run).
`python3 scripts/r1_idle_probe.py` RC=0: newest playcap dir
playcap-20261014-224611; live-timeline.jsonl mtime_ns=1793043841304000000 /
5691796463 B (12th consecutive byte-identical reading t111..t122); zero
dosbox procs; find sweep -> 4 files, all work/r1/loop/. (B) negative: clean
tracked tree at 7c9a18f, no STEERING file, prompt-44.txt identical to
prompt-43.txt after digit-stripping (`sed -E 's/[0-9]+/N/g'` then diff:
empty), no delta outside loop-owned paths. r1_t85g_sitting.py correctly not
run; no watch/census executed per §6 discipline.

Infra unchanged since t112 (Xvfb 1196, x11vnc 1207, watcher 27774;
x11vnc.log 17:30:18/30114 — still zero connects against the t111-FIXED
launch path, so a user-side capture attempt remains possible but unobserved).
INFRA-leg transients 132359/132412 (this session's runner + probe child) per
the t118 noise law, correctly ignored.

Bank-hygiene check re-run fresh (BLOCKED.md traps rule):
`grep -rln stop-report scripts/` matches r1_idle_probe.py and its
`__pycache__` bytecode only — no script writes the file, so §15 here is
hand-authored and safe from regeneration.

§3 answer outstanding after nine idle turns. Ledger unchanged 12 closed /
6 open (OQ-003, 005, 016, 019, 021, 023); the t113 LOOP-END PROPOSAL (§6)
stands: re-arm ONLY on trigger (A) new capture dir / timeline growth or
trigger (B) a §3 answer. No row closed (strict-close honest negative), no
banked law falsified, no new tool. NEXT stays IDLE.

## 16. IDLE re-check #10 (t123, 2026-10-27 22:41 EDT) — steady-state negative

Session start 22:39:11 (probe cutoff) / 22:40:57 (probe run).
`python3 scripts/r1_idle_probe.py` RC=0, verdict IDLE from the tool's own
printed evidence — no hand re-derivation needed (third fresh-reader run
after t117 authored the tool, second clean steady-state reading).
(A) NEGATIVE: newest playcap dir playcap-20261014-224611; live-timeline.jsonl
mtime_ns=1793043841304000000 / 5691796463 B — 13th consecutive byte-identical
reading (t111..t123); zero dosbox procs; `find work/r1 -newermt <session
start>` -> 4 files, non-loop: none. r1_t85g_sitting.py correctly not run; no
watch/census executed per §6 discipline.
(B) NEGATIVE: clean tracked tree at 00728b4 (`git diff HEAD --name-only` empty,
`git status --porcelain` empty, no untracked), no STEERING file, no delta
outside loop-owned paths. Steering check via the t118 digit-strip law:
prompt-45.txt vs prompt-44.txt after `sed 's/[0-9]\+/N/g'` -> diff empty
(generic loop prompt, no prepended note).

Infra unchanged since t112 (Xvfb 1196, x11vnc 1207, watcher 27774; x11vnc.log
2026-10-27 17:30:18 / 30114 B — still zero connects against the t111-FIXED
launch path, so a user-side capture attempt remains possible but unobserved).
INFRA-leg transients 133462 / 133529 (this session's runner + probe child)
ignored per the t118 noise law.

Bank-hygiene re-run fresh: `grep -rln stop-report scripts/` -> only
r1_idle_probe.py and its `__pycache__` bytecode; no script regenerates the
bank, so §16 is hand-authored and safe.

§3 answer outstanding after TEN idle turns. Idle turns are now pure cost:
each yields one commit and zero measurement, and the two-trigger probe is
the cheapest possible form of that cost. Ledger unchanged 12 closed / 6 open
(OQ-003, 005, 016, 019, 021, 023). The t113 LOOP-END PROPOSAL (§6) stands and
is re-endorsed here: if no trigger arms, ending the loop at 12/6 is the honest
outcome, not a failure — every remaining row is capture-gated or user-decision-
gated and none can be closed by another idle session. No row closed
(strict-close honest negative), no banked law falsified, no new tool.
NEXT stays IDLE.

## 17. IDLE re-check #11 (t124, 2026-10-27 22:47 EDT) — steady-state negative

`python3 scripts/r1_idle_probe.py` RC=0 at 22:47:01 (session start 22:45:19).
(A) NEGATIVE: newest playcap dir playcap-20261014-224611; live-timeline.jsonl
mtime_ns 1793043841304000000 / 5691796463 B (14th consecutive byte-identical
reading t111..t124); zero dosbox procs; session-start find sweep 4 files, all
work/r1/loop/. r1_t85g_sitting.py correctly not run. (B) NEGATIVE: clean
tracked tree at 17846a7 (diff HEAD empty, status --porcelain empty), no
STEERING file, prompt-46.txt identical to prompt-45.txt after digit-stripping
(diff empty), no delta outside loop-owned paths. §3 answer outstanding after
eleven idle turns. Infra unchanged since t112 (Xvfb 1196 / x11vnc 1207 /
watcher 27774; x11vnc.log 17:30:18 / 30114 B); transient 134591 (this
session's runner) and its probe child 134644 (gone on re-check) ignored per
the t118 noise law. Bank-hygiene re-checked fresh: grep -rln stop-report
scripts/ hits only r1_idle_probe.py + its __pycache__ bytecode — no
regeneration trap. No row closed (strict-close honest negative), no banked
law falsified, no new tool. NEXT stays IDLE.

## 18. IDLE re-check #12 (t125, 2026-10-27 22:52 EDT) — steady-state negative

`python3 scripts/r1_idle_probe.py` RC=0 at 22:51:57 (session start 22:50:52).
(A) NEGATIVE: newest playcap dir playcap-20261014-224611; live-timeline.jsonl
mtime_ns 1793043841304000000 / 5691796463 B (15th consecutive byte-identical
reading t111..t125); zero dosbox procs; session-start find sweep 4 files, all
work/r1/loop/. r1_t85g_sitting.py correctly not run. (B) NEGATIVE: clean
tracked tree at 86900c5 (diff HEAD empty, status --porcelain empty, no
untracked), no STEERING file, prompt-47.txt identical to prompt-46.txt after
digit-stripping (`diff <(sed 's/[0-9]\+//g' 46) <(...47)` → 0 lines), no delta
outside loop-owned paths. §3 answer outstanding after twelve idle turns. Infra
unchanged since t112 (Xvfb 1196 / x11vnc 1207 / watcher 27774; x11vnc.log
17:30:18 / 30114 B — still zero connects against the t111-FIXED launch path);
transients 135661 / 135777 (this session's runner + probe child) ignored per
the t118 noise law. Bank-hygiene re-checked fresh: `grep -rln stop-report
scripts/` hits only r1_idle_probe.py plus its __pycache__ bytecode — no
regeneration trap, hand-authoring safe. No row closed (strict-close honest
negative), no banked law falsified, no new tool. The t113 LOOP-END PROPOSAL
stands unchanged: twelve consecutive idle turns have produced zero
measurement, and an idle session cannot close a capture-gated or
decision-gated ledger row. NEXT stays IDLE.

## 19. IDLE re-check #13 (t126, 2026-10-27 22:57 EDT) — steady-state negative

`python3 scripts/r1_idle_probe.py` RC=0 at 22:56:55 (session start cutoff
22:55:47). Trigger (A) negative: newest playcap dir playcap-20261014-224611;
live-timeline.jsonl mtime_ns 1793043841304000000 / 5691796463 B — the 16th
consecutive byte-identical reading (t111..t126); zero dosbox procs; session-start
find sweep 4 files, non-loop: none. r1_t85g_sitting.py correctly not run.
Trigger (B) negative: clean tracked tree at 9f1e2ab (`git diff HEAD --name-only`
empty, `git status --porcelain` tracked-empty, no untracked), no STEERING file,
prompt-48.txt identical to prompt-47.txt after digit-stripping
(`diff <(sed 's/[0-9]\+//g' 47) <(...48)` -> 0 lines), no delta outside
loop-owned paths. §3 answer outstanding after thirteen idle turns. Infra
unchanged since t112 (Xvfb 1196 / x11vnc 1207 / watcher 27774; x11vnc.log
17:30:18 / 30114 B — still zero connects against the t111-FIXED launch path);
transients 136797 / 136851 / 136888 (this session's runner + probe children)
ignored per the t118 noise law. Bank-hygiene holds: the file is hand-authored,
no script regenerates it (§15/§16 grep evidence stands; not re-run this turn to
save calls — probe surface unchanged). No row closed (strict-close honest
negative), no banked law falsified, no new tool. The t113 LOOP-END PROPOSAL
stands unchanged: thirteen consecutive idle turns, zero measurement; an idle
session cannot close a capture-gated or decision-gated ledger row. NEXT stays
IDLE.

## 20. IDLE re-check #14 (t127, 2026-10-27 23:02 EDT) — steady-state negative

`python3 scripts/r1_idle_probe.py` RC=0 at 23:01:55 (session start cutoff
23:00:51). Trigger (A) negative: newest playcap dir playcap-20261014-224611;
live-timeline.jsonl mtime_ns 1793043841304000000 / 5691796463 B — the 17th
consecutive byte-identical reading (t111..t127); zero dosbox procs; session-start
find sweep 4 files, non-loop: none. r1_t85g_sitting.py correctly not run.
Trigger (B) negative: HEAD 690a85d clean (`git diff HEAD --name-only` empty,
`git status --porcelain` tracked-empty, no untracked), no STEERING file,
prompt-49.txt identical to prompt-48.txt after digit-stripping
(`diff <(sed -E 's/[0-9]+//g' 49) <(...48)` -> 0 lines, both 58 lines), no delta
outside loop-owned paths. §3 answer outstanding after fourteen idle turns.
Infra unchanged since t112 (Xvfb 1196 / x11vnc 1207 / watcher 27774; x11vnc.log
17:30:18 / 30114 B — still zero connects against the t111-FIXED launch path);
transients 137997 / 138092 per the t118 noise law, correctly ignored.
Bank-hygiene RE-VERIFIED fresh this turn (t126 had skipped it to save calls):
`grep -rln stop-report scripts/` -> only r1_idle_probe.py + its pycache — the
probe detects the file, nothing regenerates it. No row closed (strict-close
honest negative), no banked law falsified, no new tool. The t113 LOOP-END
PROPOSAL stands unchanged: fourteen consecutive idle turns, zero measurement;
an idle session cannot close a capture-gated or decision-gated ledger row.
NEXT stays IDLE.

## 21. IDLE re-check #15 (t128, 2026-10-27 23:10 EDT) — steady-state negative

`python3 scripts/r1_idle_probe.py` RC=0 at 23:10:23 (session start cutoff
23:08:40). Trigger (A) negative: newest playcap dir playcap-20261014-224611;
live-timeline.jsonl mtime_ns 1793043841304000000 / 5691796463 B — the 18th
consecutive byte-identical reading (t111..t128); zero dosbox procs; session-start
find sweep 4 files, non-loop: none. r1_t85g_sitting.py correctly not run.
Trigger (B) negative: HEAD fa773c4 clean (`git diff HEAD --name-only` empty,
`git status --porcelain` tracked-empty, no untracked), no STEERING file,
prompt-50.txt identical to prompt-49.txt after digit-stripping (unified diff
0 lines, both 58 lines; keyword scan for steer/stop overrides hits only the
standing instruction lines), no delta outside loop-owned paths. §3 answer
outstanding after fifteen idle turns.
Infra unchanged since t112 (Xvfb 1196 / x11vnc 1207 / watcher 27774; x11vnc.log
17:30:18 / 30114 B — still zero connects against the t111-FIXED launch path);
transients 139526 / 139578 (this session's runner + probe child) per the t118
noise law, correctly ignored.
Bank-hygiene re-verified fresh: `grep -rln stop-report scripts/` -> only
r1_idle_probe.py + its __pycache__ bytecode — the probe detects the file,
nothing regenerates it; hand-authoring safe.
No row closed (strict-close honest negative), no banked law falsified, no new
tool. The t113 LOOP-END PROPOSAL stands unchanged: fifteen consecutive idle
turns, zero measurement; an idle session cannot close a capture-gated or
decision-gated ledger row. NEXT stays IDLE.

## 22. IDLE re-check #16 (t129, 2026-10-27 23:16 EDT) — steady-state negative

Ran the tool, did not re-derive the probes (t117 discipline):
`python3 scripts/r1_idle_probe.py` at 23:16:09 (session start cutoff
23:15:04), RC=0 before any doc edit.

Trigger (A) NEW CAPTURE — NEGATIVE. Newest playcap dir still
playcap-20261014-224611. `work/r1/playcap/live-timeline.jsonl`
mtime_ns=1793043841304000000 / size=5691796463 B — the 19th consecutive
byte-identical reading (t111..t129), i.e. the game has not been played since
2026-10-26 15:44:01.304. Zero dosbox procs (`ps -eo comm` law, not
`pgrep -af`). Session-start find sweep hit 4 files, all under
work/r1/loop/* — loop-owned, so negative by law.
`scripts/r1_t85g_sitting.py` correctly NOT run (no new turn-boundary sitting
to adjudicate).

Trigger (B) USER DECISION — NEGATIVE. HEAD at c933845 (t128) with a clean
tracked tree: `git diff HEAD --name-only` empty, `git status --porcelain`
empty, no untracked files at all. No STEERING file in work/r1/loop/. The
harness prompt advanced to prompt-51.txt; after digit-stripping
(`sed 's/[0-9]\+/N/g'`) it is byte-identical to prompt-50.txt — unified diff
0 lines, both 58 lines — so there is no prepended steering note, only the
standard iteration template. No delta outside loop-owned paths
(rewrite/, docs/PLAN.md, game docs all untouched since their last commits).
The §3 decision request (accept/reject the documented defaults for OQ-003
entropy, OQ-005 dims, OQ-019 sugar-cube [1,3]+immediate, OQ-023
threshold-only branch; authorize capture sittings; resume t89a code work) is
still outstanding after sixteen idle turns.

Infra — unchanged since t112: Xvfb 1196, x11vnc 1207, watcher 27774;
x11vnc.log mtime 2026-10-27 17:30:18 / 30114 B, i.e. zero VNC connects
against the t111-FIXED launch path. The two new python3 entries in the liveness
listing (140640 / 140735, ages 01:03 and <1s) are this iteration's own probe
and its parent shell — per the t118 noise law they are transients, not new
infrastructure, and correctly ignored.

Bank hygiene re-checked fresh this turn rather than assumed:
`grep -rln stop-report scripts/` hits only scripts/r1_idle_probe.py and its
__pycache__ entry — no script writes or regenerates this report, so
hand-authoring §22 is safe (BLOCKED.md trap re-verified, not inherited).

Verdict: NO ledger row closed (strict-close: an idle turn produces no cited
measurement, so nothing may close), no banked law falsified, no new tool.
The t113 LOOP-END PROPOSAL stands unchanged: sixteen consecutive idle turns,
zero measurement; an idle session cannot close a capture-gated or
decision-gated row. NEXT stays IDLE.


## 23. IDLE re-check #17 (t130, 2026-10-27 23:21 EDT) — steady-state negative

Trigger (A) NEGATIVE. `python3 scripts/r1_idle_probe.py` RC=0 at 23:21:02
(session start 23:20:07): newest playcap dir playcap-20261014-224611;
live-timeline.jsonl mtime_ns 1793043841304000000 / 5691796463 B — the 20th
consecutive byte-identical reading (t111..t130); zero dosbox procs;
session-start find sweep 4 files, non-loop: none. `scripts/r1_t85g_sitting.py`
correctly NOT run.

Trigger (B) NEGATIVE. Clean tracked tree at 69ed9b9 (diff HEAD empty, status
--porcelain empty, no untracked); no STEERING file in work/r1/loop/;
prompt-52.txt identical to prompt-51.txt after digit-stripping (unified diff
0 lines, both 58 lines). §3 answer outstanding after seventeen idle turns.

Infra unchanged since t112 (Xvfb 1196 / x11vnc 1207 / watcher 27774;
x11vnc.log 17:30:18/30114 — zero connects against the t111-FIXED launch path);
transients 141762/141834/141847 are this iteration's own probe and shells per
the t118 noise law, correctly ignored.

Bank hygiene re-checked fresh (probe output): `grep -rln stop-report scripts/`
hits only r1_idle_probe.py + its __pycache__ — no regeneration trap;
hand-authoring §23 is safe.

Verdict: NO ledger row closed (strict-close: an idle turn produces no cited
measurement), no banked law falsified. The t113 LOOP-END PROPOSAL stands:
seventeen consecutive idle turns, zero measurement; an idle session cannot
close a capture-gated or decision-gated row. NEXT stays IDLE.

---

## §24 — t131 IDLE re-check #18 (2026-10-27 23:25)

Both triggers probed with the sanctioned tool only (no watch, no census, per
§6 discipline). `python3 scripts/r1_idle_probe.py` RC=0 at 23:25:49 (session
start cutoff 23:24:51).

(A) NEW CAPTURE: NEGATIVE. Newest playcap dir playcap-20261014-224611;
live-timeline.jsonl mtime_ns 1793043841304000000 / 5691796463 B — the 21st
consecutive byte-identical reading (t111..t131); zero dosbox procs; session-
start find sweep over work/r1 = 4 files, non-loop: none.
r1_t85g_sitting.py correctly not run (no sitting to adjudicate).

(B) USER DECISION: NEGATIVE. Tracked tree clean at 555817b (diff HEAD empty,
status --porcelain empty, no untracked files at probe time, no delta outside
loop-owned paths, no STEERING file). Harness prompt-53.txt (58 lines) is
identical to prompt-52.txt after digit-stripping (unified diff 0 lines) — no
prepended steering note. The §3 answer remains outstanding after eighteen
idle turns.

Infra: unchanged since t112 — Xvfb 1196 / x11vnc 1207 / watcher 27774;
x11vnc.log mtime 2026-10-27 17:30:18 / 30114 B, i.e. zero connects against
the t111-FIXED launch path. Transient pids 142872/142952 are this iteration's
own probe and shell per the t118 noise law, correctly ignored.

Bank hygiene re-checked fresh (probe output): `grep -rln stop-report scripts/`
hits only r1_idle_probe.py + its __pycache__ — no regeneration trap;
hand-authoring §24 is safe.

Verdict: NO ledger row closed (strict-close: an idle turn produces no cited
measurement), no banked law falsified. The t113 LOOP-END PROPOSAL stands:
eighteen consecutive idle turns, zero measurement. NEXT stays IDLE.

## §25 — t132 IDLE re-check #19 (2026-10-27 23:30)

Both triggers probed with the sanctioned tool only (no watch, no census, per
§6 discipline). `python3 scripts/r1_idle_probe.py` RC=0 at 23:30:25 (session
start cutoff 23:29:29).

(A) NEW CAPTURE: NEGATIVE. Newest playcap dir playcap-20261014-224611;
live-timeline.jsonl mtime_ns 1793043841304000000 / 5691796463 B — the 22nd
consecutive byte-identical reading (t111..t132); zero dosbox procs; session-
start find sweep over work/r1 = 4 files, non-loop: none.
r1_t85g_sitting.py correctly not run (no sitting to adjudicate).

(B) USER DECISION: NEGATIVE. Tracked tree clean at 11c105d (diff HEAD empty,
status --porcelain empty, no untracked files at probe time, no delta outside
loop-owned paths, no STEERING file). Harness prompt-54.txt (58 lines) is
identical to prompt-53.txt after digit-stripping (unified diff 0 lines) — no
prepended steering note. The §3 answer remains outstanding after nineteen
idle turns.

Infra: unchanged since t112 — Xvfb 1196 / x11vnc 1207 / watcher 27774;
x11vnc.log mtime 2026-10-27 17:30:18 / 30114 B, i.e. zero connects against
the t111-FIXED launch path. Transient pids 143957/144039 are this iteration's
own probe and shell per the t118 noise law, correctly ignored.

Bank hygiene re-checked fresh: `grep -rln stop-report scripts/` hits only
r1_idle_probe.py + its __pycache__ — no regeneration trap; hand-authoring §25
is safe.

Verdict: NO ledger row closed (strict-close: an idle turn produces no cited
measurement), no banked law falsified. The t113 LOOP-END PROPOSAL stands:
nineteen consecutive idle turns, zero measurement. NEXT stays IDLE.

## §26 — t133 IDLE re-check #20 (2026-10-27 23:35)

Both triggers probed with the sanctioned tool only (no watch, no census, per
§6 discipline). `python3 scripts/r1_idle_probe.py` RC=0 at 23:35:10 (session
start cutoff 23:34:19).

(A) NEW CAPTURE: NEGATIVE. Newest playcap dir playcap-20261014-224611;
live-timeline.jsonl mtime_ns 1793043841304000000 / 5691796463 B — the 23rd
consecutive byte-identical reading (t111..t133); zero dosbox procs; session-
start find sweep over work/r1 = 4 files, non-loop: none.
r1_t85g_sitting.py correctly not run (no sitting to adjudicate).

(B) USER DECISION: NEGATIVE. Tracked tree clean at 1a1c448 (diff HEAD empty,
status --porcelain empty, no untracked files at probe time, no delta outside
loop-owned paths, no STEERING file). Harness prompt-55.txt (58 lines) is
identical to prompt-54.txt after digit-stripping (unified diff 0 lines) — no
prepended steering note. The §3 answer remains outstanding after twenty
idle turns.

Infra: unchanged since t112 — Xvfb 1196 / x11vnc 1207 / watcher 27774;
x11vnc.log mtime 2026-10-27 17:30:18 / 30114 B, i.e. zero connects against
the t111-FIXED launch path. Transient pids 145064/145154 are this iteration's
own probe and shell per the t118 noise law, correctly ignored.

Bank hygiene re-checked fresh: `grep -rln stop-report scripts/` hits only
r1_idle_probe.py + its __pycache__ — no regeneration trap; hand-authoring §26
is safe.

Verdict: NO ledger row closed (strict-close: an idle turn produces no cited
measurement), no banked law falsified. The t113 LOOP-END PROPOSAL stands:
twenty consecutive idle turns, zero measurement. NEXT stays IDLE.

## §27 — t134 IDLE re-check #21 (2026-10-27 23:39)

Both triggers probed with the sanctioned tool only (no watch, no census, per
§6 discipline). `python3 scripts/r1_idle_probe.py` RC=0 at 23:39:50 (session
start cutoff 23:39:00).

(A) NEW CAPTURE: NEGATIVE. Newest playcap dir playcap-20261014-224611;
live-timeline.jsonl mtime_ns 1793043841304000000 / 5691796463 B — the 24th
consecutive byte-identical reading (t111..t134); zero dosbox procs; session-
start find sweep over work/r1 = 4 files, non-loop: none.
r1_t85g_sitting.py correctly not run (no sitting to adjudicate).

(B) USER DECISION: NEGATIVE. Tracked tree clean at a40a7d8 (diff HEAD empty,
status --porcelain empty, no untracked files at probe time, no delta outside
loop-owned paths, no STEERING file). Harness prompt-56.txt (58 lines) is
identical to prompt-55.txt after digit-stripping (unified diff 0 lines) — no
prepended steering note. The §3 answer remains outstanding after twenty-one
idle turns.

Infra: unchanged since t112 — Xvfb 1196 / x11vnc 1207 / watcher 27774;
x11vnc.log mtime 2026-10-27 17:30:18 / 30114 B, i.e. zero connects against
the t111-FIXED launch path. Transient pids 146140/146217 are this iteration's
own probe and shell per the t118 noise law, correctly ignored.

Bank hygiene: §26 (t133) established `grep -rln stop-report scripts/` hits
only r1_idle_probe.py + its __pycache__ — no regeneration trap; file was
byte-stable at 746 lines with exactly one §26 verdict block since, so
hand-authoring §27 is safe.

Verdict: NO ledger row closed (strict-close: an idle turn produces no cited
measurement), no banked law falsified. The t113 LOOP-END PROPOSAL stands:
twenty-one consecutive idle turns, zero measurement. NEXT stays IDLE.

## §28 — t135 IDLE re-check #22 (2026-10-27 23:45)

Both triggers probed with the sanctioned tool only (no watch, no census, per
§6 discipline). `python3 scripts/r1_idle_probe.py` RC=0 at 23:45:53 (session
start cutoff 23:44:08).

(A) NEW CAPTURE: NEGATIVE. Newest playcap dir playcap-20261014-224611;
live-timeline.jsonl mtime_ns 1793043841304000000 / 5691796463 B — the 25th
consecutive byte-identical reading (t111..t135); zero dosbox procs; session-
start find sweep over work/r1 = 4 files, non-loop: none.
r1_t85g_sitting.py correctly not run (no sitting to adjudicate).

(B) USER DECISION: NEGATIVE. Tracked tree clean at 815a9fe (diff HEAD empty,
status --porcelain empty, no untracked files at probe time, no delta outside
loop-owned paths, no STEERING file). Harness prompt-57.txt (58 lines) is
identical to prompt-56.txt after digit-stripping (unified diff 0 lines) — no
prepended steering note. The §3 answer remains outstanding after twenty-two
idle turns.

Infra: unchanged since t112 — Xvfb 1196 / x11vnc 1207 / watcher 27774;
x11vnc.log mtime 2026-10-27 17:30:18 / 30114 B, i.e. zero connects against
the t111-FIXED launch path. Transient pids 147254/147306 are this iteration's
own probe and shell per the t118 noise law, correctly ignored.

Bank hygiene: re-checked fresh — `grep -rln stop-report scripts/` hits only
r1_idle_probe.py + its __pycache__ bytecode; no regeneration trap. File was
byte-stable at 779 lines (= §27's committed 746 + 33) with zero diff against
HEAD before this append, so hand-authoring §28 is safe.

Verdict: NO ledger row closed (strict-close: an idle turn produces no cited
measurement), no banked law falsified. The t113 LOOP-END PROPOSAL stands:
twenty-two consecutive idle turns, zero measurement. NEXT stays IDLE.

## §29 — t136 idle re-check #23 (2026-10-27 23:51)

Trigger (A) NEGATIVE. `python3 scripts/r1_idle_probe.py` RC=0 at 23:51:14
(session start 23:50:16): newest playcap dir playcap-20261014-224611;
live-timeline.jsonl mtime_ns 1793043841304000000 / 5691796463 B — the 26th
consecutive byte-identical reading (t111..t136); zero dosbox procs;
session-start find sweep 4 files, non-loop: none.
`scripts/r1_t85g_sitting.py` correctly not run.

Trigger (B) NEGATIVE. Clean tracked tree at 2c62078 (diff HEAD empty,
status --porcelain empty, no untracked), no STEERING file. Harness
prompt-58.txt (58 lines) is identical to prompt-57.txt after digit-stripping
(unified diff 0 lines) — no prepended steering note. The §3 answer remains
outstanding after twenty-three idle turns.

Infra: unchanged since t112 — Xvfb 1196 / x11vnc 1207 / watcher 27774;
x11vnc.log mtime 2026-10-27 17:30:18 / 30114 B, i.e. zero connects against the
t111-FIXED launch path. Transient pids 148438/148483/148498 are this
iteration's own probe and shells per the t118 noise law, correctly ignored.

Bank hygiene: re-checked fresh before appending — `grep -rln stop-report
scripts/` hits only r1_idle_probe.py + its __pycache__ bytecode; no
regeneration trap. File was byte-stable at 812 lines (= §28's committed
total) with zero diff against HEAD, so hand-authoring §29 is safe.

Verdict: NO ledger row closed (strict-close: an idle turn produces no cited
measurement), no banked law falsified. The t113 LOOP-END PROPOSAL stands:
twenty-three consecutive idle turns, zero measurement. NEXT stays IDLE.

## §30 — t137 idle re-check #24 (2026-10-27 23:56)

Trigger (A) NEGATIVE. `python3 scripts/r1_idle_probe.py` RC=0 at 23:56:01
(session start 23:55:04, same-second start/finish — the probe is a stat-only
pass): newest playcap dir playcap-20261014-224611; live-timeline.jsonl
mtime_ns 1793043841304000000 / 5691796463 B — the 27th consecutive
byte-identical reading (t111..t137); zero dosbox procs; session-start find
sweep 4 files, non-loop: none. `scripts/r1_t85g_sitting.py` correctly not run.

Trigger (B) NEGATIVE. Clean tracked tree at 295c0e3 (diff HEAD empty,
status --porcelain empty, no untracked), no STEERING file. Harness
prompt-59.txt is identical to prompt-58.txt after digit-stripping
(unified diff 0 lines) — no prepended steering note. The §3 answer remains
outstanding after twenty-four idle turns.

Infra: unchanged since t112 — Xvfb 1196 / x11vnc 1207 / watcher 27774;
x11vnc.log mtime 2026-10-27 17:30:18 / 30114 B, i.e. still zero connects
against the t111-FIXED launch path. Transient pids 149557/149638 are this
iteration's own probe and shells per the t118 noise law, correctly ignored.

Bank hygiene: re-checked fresh before appending — `grep -rln stop-report
scripts/` hits only r1_idle_probe.py + its __pycache__ bytecode; no
regeneration trap. File was byte-stable at 841 lines (= §29's committed
total) with zero diff against HEAD, so hand-authoring §30 is safe.

Verdict: NO ledger row closed (strict-close: an idle turn produces no cited
measurement), no banked law falsified. The t113 LOOP-END PROPOSAL stands:
twenty-four consecutive idle turns, zero measurement. NEXT stays IDLE.

## §31 — t138 idle re-check #25 (2026-10-28 00:01)

Trigger (A) NEGATIVE. `python3 scripts/r1_idle_probe.py` RC=0 at 00:01:59
(session start 00:00:16 — first idle turn after the calendar rollover to
2026-10-28): newest playcap dir playcap-20261014-224611; live-timeline.jsonl
mtime_ns 1793043841304000000 / 5691796463 B — the 28th consecutive
byte-identical reading (t111..t138); zero dosbox procs; session-start find
sweep 4 files, non-loop: none. `scripts/r1_t85g_sitting.py` correctly not run.
Note: the probe's session-start cutoff is computed from process start, not
from a hard-coded date, so the midnight rollover needed no adjustment —
`find work/r1 -newermt "2026-10-28 00:00:16"` is the leg that ran.

Trigger (B) NEGATIVE. Clean tracked tree at 9b75419 (diff HEAD empty,
status --porcelain empty, no untracked), no STEERING file. Harness
prompt-60.txt is identical to prompt-59.txt after digit-stripping
(unified diff 0 lines, both 58 lines) — no prepended steering note. The §3
answer remains outstanding after twenty-five idle turns.

Infra: unchanged since t112 — Xvfb 1196 / x11vnc 1207 / watcher 27774;
x11vnc.log mtime 2026-10-27 17:30:18 / 30114 B, i.e. still zero connects
against the t111-FIXED launch path. Transient pids 150738/150789 are this
iteration's own probe and shells per the t118 noise law — both verified gone
on a follow-up `ps -p` (exit 1), correctly ignored.

Bank hygiene: re-checked fresh before appending — `grep -rln stop-report
scripts/` hits only r1_idle_probe.py + its __pycache__ bytecode; no
regeneration trap. File was byte-stable at 870 lines (= §30's committed
total) with zero diff against HEAD, so hand-authoring §31 is safe.

Verdict: NO ledger row closed (strict-close: an idle turn produces no cited
measurement), no banked law falsified. The t113 LOOP-END PROPOSAL stands:
twenty-five consecutive idle turns, zero measurement. NEXT stays IDLE.

## 32. IDLE RE-CHECK #26 (t139, 2026-10-28 00:08 EDT) — negative

Tool run: `python3 scripts/r1_idle_probe.py` RC=0 at 00:08:29 (session start
00:06:44). Both legs negative, printed by the tool itself — no hand
re-derivation.

(A) NEW CAPTURE — negative. Newest playcap dir `playcap-20261014-224611`;
`work/r1/playcap/live-timeline.jsonl` mtime_ns 1793043841304000000 /
5691796463 B — the 29th consecutive byte-identical reading (t111..t139). Zero
dosbox processes. Session-start sweep `find work/r1 -newermt '2026-10-28
00:06:44'` -> 4 files, non-loop: none. `scripts/r1_t85g_sitting.py` correctly
NOT run (no turn-boundary sitting exists to adjudicate).

(B) USER DECISION — negative. Clean tracked tree at 7f3a589 (`git diff HEAD
--name-only` empty, `git status --porcelain` empty, no untracked). No STEERING
file. Harness prompt `work/r1/loop/prompt-61.txt` identical to
`prompt-60.txt` after digit-stripping (unified diff 0 lines). No delta outside
loop-owned paths. The §3 answer list remains outstanding after twenty-six idle
turns.

Infra liveness (so the negatives are trustworthy): Xvfb :9 pid 1196, x11vnc
:5910 pid 1207, capture watcher pid 27774 — all unchanged since t112.
`work/r1/vnc/x11vnc.log` mtime 2026-10-27 17:30:18 / size 30114 — zero connect
attempts against the t111-FIXED launch path. Transient pids 151887 (harness
loop runner, elapsed matches session start) and 151940 (probe child, gone on
the follow-up `ps -p`) are ignored per the t118 noise law: trigger evidence is
dosbox processes and capture-side files only.

Bank hygiene re-checked fresh before appending: `grep -rln stop-report
scripts/` hits only `r1_idle_probe.py` + its `__pycache__` bytecode; the file
was at 903 lines with zero diff against HEAD (§31's committed total), so
hand-authoring §32 is safe.

Verdict: NO ledger row closed (strict-close: an idle turn produces no cited
measurement), no banked law falsified. The t113 LOOP-END PROPOSAL stands:
twenty-six consecutive idle turns, zero measurement. NEXT stays IDLE.

## 33. IDLE RE-CHECK #27 (t140, 2026-10-28 00:14 EDT) — negative

`python3 scripts/r1_idle_probe.py` RC=0 at 00:14:34 (session start 00:12:50):
newest playcap dir `playcap-20261014-224611`; `work/r1/playcap/live-timeline.jsonl`
mtime_ns 1793043841304000000 / size 5691796463 — thirtieth consecutive
byte-identical reading (t111..t140); zero dosbox processes; session-start find
sweep 4 files, non-loop: none. `r1_t85g_sitting.py` correctly not run.

Trigger (B) NEGATIVE: clean tracked tree at 52d8b81 (`git diff HEAD --name-only`
empty, `git status --porcelain` empty, no untracked), no STEERING file, and
`prompt-62.txt` identical to `prompt-61.txt` after digit-stripping (unified diff
0 lines, both 58 lines) — the content-diff law from t116, not mtime. No delta
outside loop-owned paths. The §3 user-decision list (accept/reject documented
defaults OQ-003 entropy / OQ-005 dims / OQ-019 sugar-cube / OQ-023
threshold-only; authorize capture sittings; resume t89a code work) is
outstanding after twenty-seven idle turns.

Infra unchanged since t112: Xvfb :9 pid 1196, x11vnc :5910 pid 1207, watcher
pid 27774; `work/r1/vnc/x11vnc.log` mtime 2026-10-27 17:30:18 / size 30114 —
still zero connect attempts against the t111-FIXED launch path. Transient pids
153003 (harness loop runner, elapsed matches session start) and 153055 (probe
child, gone on the follow-up `ps -p`) ignored per the t118 noise law.

Bank hygiene re-checked fresh before appending: `grep -rln stop-report scripts/`
hits only `r1_idle_probe.py` + its `__pycache__` bytecode; the file was at 940
lines with zero diff against HEAD (§32's committed total), so hand-authoring
§33 is safe.

Verdict: NO ledger row closed (strict-close: an idle turn produces no cited
measurement), no banked law falsified. The t113 LOOP-END PROPOSAL stands:
twenty-seven consecutive idle turns, zero measurement. NEXT stays IDLE.

## 34. IDLE RE-CHECK #28 (t141, 2026-10-28 00:19 EDT) — negative

`python3 scripts/r1_idle_probe.py` RC=0 at 00:19:44 (session start 00:18:53):
newest playcap dir `playcap-20261014-224611`; `work/r1/playcap/live-timeline.jsonl`
mtime_ns 1793043841304000000 / size 5691796463 — thirty-first consecutive
byte-identical reading (t111..t141); zero dosbox processes; session-start find
sweep 4 files, non-loop: none. `r1_t85g_sitting.py` correctly not run.

Trigger (B) NEGATIVE: clean tracked tree at 17dfdd5 (`git diff HEAD --stat` empty,
`git status --porcelain` empty, `--untracked-files=all` empty), no STEERING file,
and `prompt-63.txt` identical to `prompt-62.txt` after digit-stripping
(`diff -q` clean) — the content-diff law from t116, not mtime. No delta outside
loop-owned paths. The §3 user-decision list (accept/reject documented defaults
OQ-003 entropy / OQ-005 dims / OQ-019 sugar-cube / OQ-023 threshold-only;
authorize capture sittings; resume t89a code work) is outstanding after
twenty-eight idle turns.

Infra unchanged since t112: Xvfb :9 pid 1196, x11vnc :5910 pid 1207, watcher
pid 27774; `work/r1/vnc/x11vnc.log` mtime 2026-10-27 17:30:18 / size 30114 —
still zero connect attempts against the t111-FIXED launch path. Transient pids
154161 (identified by `ps -o args=` as the harness's own
`mcp_death_supervisor.py --parent-pgid 154141`) and 154226 (gone on the
follow-up `ps -p`) ignored per the t118 noise law.

Bank hygiene re-checked fresh before appending: `grep -rln stop-report scripts/`
hits only `r1_idle_probe.py` + its `__pycache__` bytecode; the file was at 972
lines with zero diff against HEAD (§33's committed total), so hand-authoring
§34 is safe.

Verdict: NO ledger row closed (strict-close: an idle turn produces no cited
measurement), no banked law falsified. The t113 LOOP-END PROPOSAL stands:
twenty-eight consecutive idle turns, zero measurement. NEXT stays IDLE.

## 35. IDLE RE-CHECK #29 (t142, 2026-10-28 00:24 EDT) — negative

`python3 scripts/r1_idle_probe.py` RC=0 at 00:24:54 (session start 00:23:52):
newest playcap dir `playcap-20261014-224611`; `work/r1/playcap/live-timeline.jsonl`
mtime_ns 1793043841304000000 / size 5691796463 — thirty-second consecutive
byte-identical reading (t111..t142); zero dosbox processes; session-start find
sweep 4 files, non-loop: none. `r1_t85g_sitting.py` correctly not run.

Trigger (B) NEGATIVE: clean tracked tree at 6b68faa (`git diff HEAD --name-only`
empty, `git status --porcelain` empty, no untracked files), no STEERING file, and
`prompt-64.txt` identical to `prompt-63.txt` after digit-stripping (`diff -q`
clean) — the content-diff law from t116, not mtime. No delta outside loop-owned
paths. The §3 user-decision list (accept/reject documented defaults OQ-003
entropy / OQ-005 dims / OQ-019 sugar-cube / OQ-023 threshold-only; authorize
capture sittings; resume t89a code work) is outstanding after twenty-nine idle
turns.

Infra unchanged since t112: Xvfb :9 pid 1196, x11vnc :5910 pid 1207, watcher
pid 27774; `work/r1/vnc/x11vnc.log` mtime 2026-10-27 17:30:18 / size 30114 —
still zero connect attempts against the t111-FIXED launch path. Transient pids
155315 (`ps -o args=`: harness's own `mcp_death_supervisor.py --parent-pgid
155295`), 155367 (`hermes_kernel_runner.py` — this session's own code-execution
kernel), 155401 (this probe's child, gone on follow-up): harness/harness-adjacent
python, ignored per the t118 noise law.

Bank hygiene re-checked fresh before appending: `grep -rln stop-report scripts/`
hits only `r1_idle_probe.py` + its `__pycache__` bytecode; the file was at 1005
lines with zero diff against HEAD (§34's committed total), so hand-authoring §35
is safe.

Verdict: NO ledger row closed (strict-close: an idle turn produces no cited
measurement), no banked law falsified. The t113 LOOP-END PROPOSAL stands:
twenty-nine consecutive idle turns, zero measurement. NEXT stays IDLE.

## 36. IDLE RE-CHECK #30 (t143, 2026-10-28 00:30 EDT) — negative

`python3 scripts/r1_idle_probe.py` RC=0 at 00:30:54 (session start 00:29:08):
newest playcap dir `playcap-20261014-224611`; `work/r1/playcap/live-timeline.jsonl`
mtime_ns 1793043841304000000 / size 5691796463 — thirty-third consecutive
byte-identical reading (t111..t143); zero dosbox processes; session-start find
sweep 4 files, non-loop: none. `r1_t85g_sitting.py` correctly not run.

Trigger (B) NEGATIVE: clean tracked tree at 2c6c274 (`git diff HEAD --name-only`
empty, `git status --porcelain` empty, no untracked files), no STEERING file, and
`prompt-65.txt` identical to `prompt-64.txt` after digit-stripping (`diff -u`
0 lines, both 58 lines; `grep -in steering` hits only the standing instruction
line 14) — content-diff law from t116, not mtime. No delta outside loop-owned
paths. The §3 user-decision list (accept/reject documented defaults OQ-003
entropy / OQ-005 dims / OQ-019 sugar-cube / OQ-023 threshold-only; authorize
capture sittings; resume t89a code work) is outstanding after thirty idle turns.

Infra unchanged since t112: Xvfb :9 pid 1196, x11vnc :5910 pid 1207, watcher
pid 27774; `work/r1/vnc/x11vnc.log` mtime 2026-10-27 17:30:18 / size 30114 —
still zero connect attempts against the t111-FIXED launch path. Transient pids
156466 (`ps -o args=`: harness's own `mcp_death_supervisor.py --parent-pgid
156446`) and 156528 (this session's own kernel/probe child, gone on follow-up
`ps -p`) — harness/harness-adjacent python, ignored per the t118 noise law.

Bank hygiene re-checked fresh before appending: `grep -rln stop-report scripts/`
hits only `r1_idle_probe.py` + its `__pycache__` bytecode; the file was at 1039
lines with zero diff against HEAD (§35's committed total), so hand-authoring §36
is safe.

Verdict: NO ledger row closed (strict-close: an idle turn produces no cited
measurement), no banked law falsified. The t113 LOOP-END PROPOSAL stands:
thirty consecutive idle turns, zero measurement. NEXT stays IDLE.

## 37. IDLE RE-CHECK #31 (t144, 2026-10-28 00:37 EDT) — negative

`python3 scripts/r1_idle_probe.py` RC=0 at 00:37:04 (session start 00:35:19):
newest playcap dir `playcap-20261014-224611`; `work/r1/playcap/live-timeline.jsonl`
mtime_ns 1793043841304000000 / size 5691796463 — thirty-fourth consecutive
byte-identical reading (t111..t144); zero dosbox processes; session-start find
sweep 4 files, non-loop: none. `r1_t85g_sitting.py` correctly not run.

Trigger (B) NEGATIVE: clean tracked tree at ffd9e55 (`git diff HEAD --name-only`
empty, `git status --porcelain` empty, no untracked files), no STEERING file, and
`prompt-66.txt` identical to `prompt-65.txt` after digit-stripping (`diff -u`
0 lines, both 58 lines; `grep -in steering` hits only the standing instruction
line 14). No delta outside loop-owned paths. The §3 user-decision list is
outstanding after thirty-one idle turns.

NEW PROBE PITFALL banked (steering check): enumerate harness prompts with
`ls -1v`, NOT `ls -1`. `prompt-*.txt` is lexically ordered, so `tail -1` on the
lexical list returns `prompt-9.txt` — which exists alongside
`prompt-63..66.txt` — and compares the iteration's true prompt against a prompt
from ~57 turns ago. That comparison happens to come out empty (the loop prompt
text is stable), so the defect is SILENT: it yields the correct NEGATIVE verdict
while reading the wrong pair, and would only ever mislead by masking a steering
note added after single-digit numbering. Verified this session both ways:
lexical pair prompt-9/prompt-8 = 41 lines, 0 diff; version-sorted pair
prompt-66/prompt-65 = 58 lines, 0 diff. The TOOL is not affected:
`r1_idle_probe.py:82-84` selects the session-start prompt with
`sorted(glob(...), key=os.path.getmtime)[-1]` (mtime order), which is why the
tool's cutoff was correct while this hand check was wrong. Same class as the t117 tool-path defect:
trust the tool's enumeration, not a hand-globbed glob.

Infra unchanged since t112: Xvfb :9 pid 1196, x11vnc :5910 pid 1207, watcher
pid 27774; `work/r1/vnc/x11vnc.log` mtime 2026-10-27 17:30:18 / size 30114 —
still zero connect attempts against the t111-FIXED launch path. Transient pid
157622 (`ps -o args=`: harness's own `mcp_death_supervisor.py`) and 157674 (this
session's probe child) — ignored per the t118 noise law.

Bank hygiene re-checked fresh before appending: `grep -rln stop-report scripts/`
hits only `r1_idle_probe.py` + its `__pycache__` bytecode; the file was at 1072
lines with zero diff against HEAD (§36's committed total), so hand-authoring §37
is safe.

Verdict: NO ledger row closed (strict-close: an idle turn produces no cited
measurement), no banked law falsified. The t113 LOOP-END PROPOSAL stands:
thirty-one consecutive idle turns, zero measurement. NEXT stays IDLE.

## 38. IDLE RE-CHECK #32 (t145, 2026-10-28 00:44 EDT) — negative + probe coverage-hole FIX

`python3 scripts/r1_idle_probe.py` RC=0 (session start 00:43:18 per the
iter-*.log-name law; wall clock 00:44:23): newest playcap dir
`playcap-20261014-224611`; `work/r1/playcap/live-timeline.jsonl` mtime_ns
1793043841304000000 / size 5691796463 — thirty-fifth consecutive byte-identical
reading (t111..t145); zero dosbox processes; session-start find sweep 4 files,
non-loop: none. `r1_t85g_sitting.py` correctly not run. Trigger (B) NEGATIVE by
content: clean tracked tree at de16f04 before this iteration's edits, no STEERING
file, prompt-67 vs prompt-66 (58/58 lines) digit-stripped delta 0. §3 answer
outstanding after thirty-two idle turns.

FINDING — t144's "the TOOL is not affected" claim was WRONG, and the error is a
COVERAGE HOLE, not a wrong answer. `r1_idle_probe.py:82-84` (mtime prompt pick)
is real but is only the FALLBACK session-start cutoff (used when no `iter-*.log`
name parses) — it has nothing to do with steering. The tool's actual steering
check was `steer = sh("ls docs/STEERING* STEERING*")` (existence glob, two
paths). Grepping the whole file for `prompt|steer` before t145's edit hit only
lines 65/69/82/84 (cutoff) and 130-133 (glob): the tool NEVER diffs prompt
contents. But the loop's own contract ("the steering note, if the harness
prepended one", prompt line 14) and §(B) name the PREPENDED PROMPT NOTE as the
steering mechanism — so for every idle turn since the tool shipped, trigger (B)
was carried by a probe blind to one of its two documented inputs, while the only
procedure that covered it (the hand `ls -1v` diff) was actively discouraged by
the t144 NEXT ACTION text. Silent in the benign direction: "STEERING file: none"
reads identically whether or not a note was prepended. (t144 misattribution
mechanism: it saw `getmtime` on the prompt glob, pattern-matched "prompt handled",
and never asked what the tool DOES with prompts.)

FIX APPLIED (scripts/r1_idle_probe.py, loop-owned file, gate does not checksum
scripts/ contents — verified: gate.sh greps scripts/ only for stage existence and
r1_attempt.sh invariants): (1) new (B2) leg in `trigger_b()` — numeric sort of
`prompt-*.txt` (t144 law enforced in code, not prose), digit-stripped unified
diff of newest vs numeric predecessor, ARM on stripped delta > 0, print pair +
line counts + delta size; raw-vs-stripped annotation distinguishes
iteration-numbering drift from content change. (2) HEAD echo truncated to 130
chars: `trigger_b()` used to print `git log --oneline -1` whole, and idle-turn
subjects summarise the previous iteration (lengths over last 25 commits: 800 ->
1310, monotonically growing), so every re-check paid ~1.3k chars to re-read the
last LANDED summary; full text lives in STATE.md where successors actually read
it.

TEST MATRIX (real executions, all four branches; temp files created and deleted
inside the same command, prompt dir verified back to prompt-67 as newest):
  a. real state (prompt-67 vs 66): delta 0 -> NEGATIVE, RC=0.
  b. prepended note (temp prompt-99 = "STEERING: accept the OQ-019
     sugar-cube default..." + full 67 text): stripped delta > 0 -> verdict
     RE-ARM; RC=1 confirmed on the analogous stripped-delta case (c).
  c. word-level content edit ("READ FIRST" -> "READ 77 FIRST", raw 2,
     stripped 2): ARMED, RC=1 (captured before grepping).
  d. pure digit-only DIFF line ("1." -> "9.", raw 2 stripped 0): NEGATIVE, RC=0,
     prints "[raw delta 2 line(s) but digit-stripped delta 0 =
     iteration-numbering drift only]".
First control attempt was INVALID and is kept as a lesson: prompt-98 and
prompt-99 were both present when control 1 ran, so the numeric pair compared
99-vs-98 (note included) instead of drift-only 98-vs-67 — the probe reported the
truth about the state it saw; the tester's cleanup order was wrong. A control
must delete the positive fixture BEFORE running the negative leg, and `RC=$?`
after a pipe reads the LAST command (grep), not the probe — capture RC before
grepping.

Ledger untouched: `ledger_audit.py` -> rows=18 open=['OQ-003','OQ-005','OQ-016',
'OQ-019','OQ-021','OQ-023'] closed=12, LEDGER AUDIT OK. Infra unchanged since
t112 (Xvfb 1196 / x11vnc 1207 / watcher 27774; x11vnc.log 2026-10-27
17:30:18/30114 — zero connects). Transients 158952 (harness mcp_death_supervisor
--parent-pgid 158932, via `ps -o args=`) per the t118 noise law. Bank hygiene
checked before appending: `grep -rln stop-report scripts/` -> only
r1_idle_probe.py + pycache; file at 1117 lines with zero diff vs HEAD (§37's
committed total).

Verdict: NO ledger row closed (strict-close — an idle turn produces no cited
measurement). The t113 LOOP-END PROPOSAL stands: thirty-two consecutive idle
turns, zero measurement — but from t145 onward the IDLE verdict is backed by a
probe that actually covers both documented (B) inputs. NEXT stays IDLE.

## §39 — t146: IDLE RE-CHECK #33 + (B3) COVERAGE FIX — a COMMITTED user
## decision was invisible to every trigger-(B) leg

Probe: `python3 scripts/r1_idle_probe.py` RC=0 at 01:01:44 (session-start
cutoff 01:00:00). (A) NEGATIVE — newest playcap dir playcap-20261014-224611;
timeline mtime_ns 1793043841304000000 / 5691796463 B, 36th consecutive
byte-identical reading (t111..t146); zero dosbox procs; find sweep 4 files,
all work/r1/loop/. (B) NEGATIVE at run time — clean tracked tree at 7d2ccd7,
no STEERING, prompt-68 vs prompt-67 digit-stripped delta 0.

THE HOLE (found by the t145 method — ask what the tool DOES, not what it
reads): all four (B) legs adjudicate the WORKING TREE (git diff/status) or
UNCOMMITTED files (STEERING glob, prompt note). A user who answers §3 the way
work normally lands in this repo — edit rewrite/ or PLAN.md, COMMIT — moves
HEAD, leaves the tree clean, and every leg prints NEGATIVE. Thirty-two turns
adjudicated (B) under an unexamined assumption that a user answer is never
committed. Subject-convention is no backstop either: 123 commits repo-wide do
not match `^t<digits>:`.

THE LAW (measured): the harness writes work/r1/loop/journal.tsv AFTER each
iteration's commit and the LAST tab field starts with that iteration's sha
(row 67 `7d2ccd7` == git rev-parse HEAD, commit ct 00:58:12; re-check rows
carry an extra `(re-check` field before it, so LAST-FIELD-FIRST-TOKEN is the
invariant that holds for both row shapes). Therefore at session start,
HEAD != last-journal-sha <=> commits landed outside the loop. The leg
enumerates <journal-sha>..HEAD via `git log --format='C %h %s' --name-only`
('C ' prefix keeps file paths the only bare lines), ARMS only on a path
outside LOOP_OWNED, and downgrades loop-confined divergence to a CAUTION
(crashed iteration whose journal row never landed — t117 shape). Unreadable
journal = explicit NOT-adjudicated annotation, verdict unchanged. Env
R1_JOURNAL overrides the path for testing.

VALIDATION (real execution, fixtures deleted after): real state ->
"HEAD == journal sha 7d2ccd7", RC=0; truncated journal at row 66 (t144 sha)
-> CAUTION, not armed (t145 touched only loop-owned paths — correct); journal
at row 1 (t85g sha 2e50020) -> ARMED RC=1 listing rewrite/, gate.sh, t86..t145
scripts as foreign; garbage ancestor deadbeef -> diverged-history ARM RC=1;
missing file -> UNREADABLE annotation, RC=0. Two self-inflicted patch bugs
caught by post-patch reading before any run: `'C %h %s'` inside a Python
%-format (invalid conversion), then one-%s format with a 2-tuple (TypeError) —
the double-%% + two-%s form is what shipped.

Working notes docs/re/_wip_t146.md. NO ledger row closed (strict-close honest
negative), no law falsified. NEXT stays IDLE.

## 40. IDLE RE-CHECK #34 (t147, 2026-10-28 01:22 EDT) — negative + (A4) coverage FIX: a dead watcher made every trigger-(A) leg unfalsifiable

(1) Trigger (A) NEGATIVE — `python3 scripts/r1_idle_probe.py` RC=0 at
01:22:47 (session-start cutoff 01:21:48 from iter-*.log name): newest
playcap dir playcap-20261014-224611; live-timeline.jsonl mtime_ns
1793043841304000000 / 5691796463 B (37th consecutive byte-identical reading
t111..t147); zero dosbox procs; find sweep 4 files, non-loop: none;
r1_t85g_sitting.py correctly not run.
(2) Trigger (B) NEGATIVE — clean tracked tree at 4ad8a23, no STEERING, B3
HEAD == journal sha 4ad8a23 (journal row 68 re-verified by hand with
cat -A), prompt-69 vs prompt-68 (58/58 lines) digit-stripped delta 0.
§3 answer outstanding after thirty-four idle turns.

(3) THE HOLE (A4). Every (A) leg is an OBSERVATION of something
scripts/r1_playcap_watch.py WRITES: timeline growth, capture-side mtimes.
If the watcher dies while the box stays up (Xvfb/x11vnc persist as daemons;
dosbox is gone because the user FINISHED playing — the exact situation a
capture would produce), all legs print NEGATIVE over a real sitting, forever,
and the loop reports steady-state IDLE with total confidence. infra() could
not catch it: it greps `Xvfb|x11vnc|python3` and printed python3 pids
(163246 harness mcp_death_supervisor, 163362 probe child — t118 noise) while
asserting liveness in prose, without naming the watcher. Third instance of
the same meta-law: t114 (pgrep self-match), t145 ("touches X" !=
"adjudicates X"), t146 (all (B) legs read only the worktree) — a probe that
PRINTS a signal's neighborhood is not a probe that ADJUDICATES it.

(4) THE FIX (scripts/r1_idle_probe.py, trigger_a tail + main): match the
INTERPRETED script at argv[1] of a python process over `ps -eo pid=,args=`
in Python. Dead => CAUTION + header "NOT ADJUDICATED (watcher down)" +
VERDICT "IDLE on (B); (A) UNVERIFIED" + RC=2 (documented meaning: probe
could not run cleanly) — deliberately NOT RC=1: absence of signal is not
absence of event, arming would assert a user decision never made (t117).
R1_WATCH_SCRIPT env overrides the script name to test the dead branch.
First draft had an elif-substring fallback matching the whole cmdline — the
t114 trap in a new costume, caught by REAL EXECUTION: the test shell
`R1_WATCH_SCRIPT=<path> python3 probe.py` carries <path> in its OWN ps args
and false-matched the fallback. argv[1] cannot self-match (a shell's argv[1]
is its -c string; the probe's own argv[1] is r1_idle_probe.py). Validated
three ways by real execution: real box ALIVE pid 27774 RC=0;
R1_WATCH_SCRIPT=no_such_watcher.py => RC=2 + NOT ADJUDICATED; probe launched
via `bash -c` still resolves ALIVE exactly (pid 27772 bash wrapper correctly
no longer counted as a watcher — t115's pair law describes harnessing, not
matching).

(5) NEAR-MISS banked as a law. I accused the infra leg of FABRICATING the
x11vnc.log line after stat failed on work/r1/playcap/vnc/x11vnc.log — my
composed path was wrong: PLAYCAP=work/r1 (line 45), real path
work/r1/vnc/x11vnc.log exists with exactly the printed mtime 17:30:18.172 /
30114 B / 404 lines. LAW: before accusing a probe of inventing output,
resolve its constants from source (grep '^[A-Z_]* ='), don't compose paths
from variable NAMES. A false bug report costs more than a real one.

Working notes docs/re/_wip_t147.md. NO ledger row closed (strict-close honest
negative), no law falsified. NEXT stays IDLE.

## 41. IDLE RE-CHECK #35 (t148, 2026-10-28 01:41 EDT) — negative; no new hole; probe self-consistency re-verified

(1) TRIGGER (A) NEGATIVE — `python3 scripts/r1_idle_probe.py` RC=0 at
01:41:11 (cutoff 01:39:21 from iter-20261028-013921-70.log): newest playcap
dir playcap-20261014-224611; live-timeline.jsonl mtime_ns
1793043841304000000 / 5691796463 B (38th consecutive byte-identical reading
t111..t148); zero dosbox procs; find sweep 4 files, non-loop: none; A4
watcher ALIVE pid 27774, so (A) is fully adjudicated. r1_t85g_sitting.py
correctly not run.

(2) TRIGGER (B) NEGATIVE — clean tracked tree at 153a6f4 (diff HEAD empty,
status --porcelain empty), no STEERING file, prompt-70 vs prompt-69 (58/58
lines) digit-stripped delta 0, B3 HEAD == journal sha 153a6f4 (no commits
outside the loop since the last iteration). §3 answer outstanding after
thirty-five idle turns.

(3) THE ITERATION'S VALUE — the t147 NEAR-MISS law executed preemptively
instead of reactively: every load-bearing constant in the probe's verdict
was resolved from source and re-measured independently BEFORE banking
(`grep PLAYCAP|TIMELINE|BASELINE` -> r1_idle_probe.py:51-56,51 = work/r1 so
TIMELINE = work/r1/playcap/live-timeline.jsonl; os.stat returned exactly the
printed size 5691796463 / mtime_ns 1793043841304000000). Zero divergence
between the tool's numbers and a fresh-reader stat: the verdict is
reproducible without trusting the tool's prose.

(4) NO new coverage hole this turn. Reviewed the trigger surface against the
stop-report §3/§6 routes: (A) has dir/timeline/process/find/watcher-liveness
legs; (B) has worktree-delta, STEERING, prompt-content, and committed-decision
(B3) legs — every documented user-answer route now has an adjudicating leg.
The one asymmetry noted and deliberately NOT changed: the find sweep's cutoff
is session-start, so a capture-side file created BETWEEN iterations is missed
by that leg only — but a real capture necessarily also creates a playcap-<ts>
dir (leg 1) and grows the timeline (leg 2), and a stray file with neither is
not a capture. Tightening the cutoff would trade a provably redundant check
for new false-positive surface; declined.

(5) Infra unchanged since t112 (Xvfb 1196 / x11vnc 1207 / watcher 27774;
x11vnc.log 2026-10-27 17:30:18 / 30114 B — zero connects against the
t111-FIXED launch path); transients 165351 (harness) / 165418 (probe child)
per the t118 noise law. Bank hygiene checked fresh: grep -rln stop-report
scripts/ -> only r1_idle_probe.py + pycache; zero diff vs HEAD at 1292 lines
before appending §41. NO row closed (strict-close honest negative), no law
falsified. NEXT stays IDLE; the t113 LOOP-END PROPOSAL stands.

## 42. IDLE RE-CHECK #36 (t149, 2026-10-28 02:02 EDT) — negative + (A5) coverage FIX: a healthy watcher can still be blind to a save file it cannot name

(1) Trigger (A) NEGATIVE — probe RC=0 at 01:47:58 (cutoff 01:47:06 from the
iter-*.log name): newest playcap dir playcap-20261014-224611; timeline
mtime_ns 1793043841304000000 / 5691796463 B (39th byte-identical reading
t111..t149, independently re-statted outside the probe — exact match); zero
dosbox procs; find sweep non-loop none; A4 watcher ALIVE pid 27774. Deeper
liveness read outside the probe: /proc/27774 wchan=hrtimer_nanosleep, State S —
parked in the 5 s poll sleep, not wedged in I/O — with fd 1/2->watch.out,
3->live-timeline.jsonl, 4->watch.log open for append. r1_t85g_sitting.py
correctly not run.
(2) Trigger (B) NEGATIVE — clean tracked tree at 082866b, no STEERING,
prompt-71 vs prompt-70 (58/58 lines) digit-stripped delta 0, B3 HEAD == journal
sha 082866b (journal row 70 re-read independently). §3 answer outstanding after
thirty-six idle turns.

(3) THE (A) CLAIM, ONE LEVEL DEEPER (measured, scratch-only). t147's A4 leg
establishes the watcher PROCESS is up. "Process up" != "collector records a
sitting" — the t145 law applied to the layer below. Direct functional test
against a scratch dir (live timeline never touched, pristine game dir never
mounted):
    rm -rf /tmp/t149-watch && mkdir -p /tmp/t149-watch/save
    cp work/r1/playcap/save/41.sav work/r1/playcap/save/42.sav /tmp/t149-watch/save/
    python3 scripts/r1_playcap_watch.py /tmp/t149-watch --once        # cwd = repo root
Real execution 01:53:38, RC=0: two lines emitted —
`41.sav t=1254 SYSTEMS mine_any=36 full=32 planets=36 | DAT_482fb=14/50 sel=0
ships=38 rel_nonzero_cells=12` (42.sav identical) — and
/tmp/t149-watch/live-timeline.jsonl held 2 valid JSON rows with file/turn/T/
score_stars/in_game=true/systems_any/planets_mine/ships(38)/file_mtime_ns set.
Second `--once` pass: "(2 prior observations deduped)", 0 new rows — the t85b
jsonl-derived `seen` dedup law holds, no 73k-dup regression. Post-run stat of
the LIVE timeline: unchanged. So (A) is not merely falsifiable here, its
reporting path (payload -> anchor cache -> base vote -> slot parse -> JSONL
append) is demonstrated working end to end: a new sitting WOULD be recorded.

(4) THE COVERAGE HOLE THE FUNCTIONAL TEST EXPOSED, AND ITS FIX. The watcher
polls `save/*.sav` LOWERCASE (r1_playcap_watch.py:161). All 20 ring slots are
lowercase and all 20 are valid save-state ZIPs (`is_zipfile` 20/20), so the
game's own writes match today — no live blind spot [verified]. But a save file
the glob cannot match is invisible even to a healthy watcher: no new
playcap-<ts> dir, no timeline growth, no dosbox proc — every (A) leg reads
NEGATIVE over a real sitting. That shape is unreported, so `trigger_a()` now
has an (A5) leg: walk the capture dir (skipping caps/, loop/), compare every
save-looking file against what the watcher CAN read, and report strays as a
CAUTION — never a trigger (t117: only an observed user event arms). Two
false-positive guards earned by measurement, not taste: (i) only files that are
valid save-state ZIPs containing a "Memory" member count, because
work/r1/playcap/evidence_slot04_t1254.SAV is a raw 88 KB memory excerpt
(`is_zipfile` False, first bytes 346 004 00 00) read by r1_t87_gizmo_table.py,
not a slot — naming it every turn would be permanent noise; (ii) SEPARATELY, my
own scratch run refreshed work/r1/.anch-cache.json (r1_slot.anchors_cached,
r1_slot.py:49) and the find sweep armed the WHOLE of (A) on that one file — a
pre-existing self-inflicted false positive for any analyzer run, which STATE.md
had already declared an artifact but the code never encoded; now a
TOOL_ARTIFACTS exclusion, with the cache justified as a pure function of
work/ascend_payload.bin.
VALIDATION (real executions; fixtures under /tmp deleted after): all-lowercase
valid slot -> "none (save/*.sav = N, all match the watcher glob)"; uppercase
VALID-zip .SAV in save/ -> flagged; non-zip .SAV alongside it -> correctly NOT
listed (only the real blind spot shown); uppercase removed -> back to "none".
Real state after the patch: RC=0, "A5 un-ingestable save files: none
(save/*.sav = 20, all match the watcher glob)", VERDICT IDLE. One patch bug
self-inflicted and caught by running the tool: a dropped closing quote in the
find-sweep line (SyntaxError at line 112) — the pre-existing `%s` string was
rewritten, not left alone; py_compile before the fixture matrix confirmed the
repair. The live watcher was NOT restarted (its glob stays lowercase): making
the collector case-insensitive means killing pid 27774 and relaunching via
scripts/r1_playcap_vnc.sh, trading a provably-inert asymmetry for the t147
failure shape — declined; A5 makes the asymmetry visible instead.

(5) Infra unchanged since t112 (Xvfb 1196 / x11vnc 1207 / watcher 27774;
x11vnc.log 2026-10-27 17:30:18 / 30114 B — zero connects); transients 166484
(harness mcp_death_supervisor, via `ps -o args=`) / probe children, per the
t118 noise law. Scratch dirs /tmp/t149-watch, /tmp/t149-a5, /tmp/t149-a5b all
removed; game/ untouched; no watch/census run against the live capture. Bank
hygiene: grep -rln stop-report scripts/ -> only r1_idle_probe.py + pycache;
zero diff vs HEAD at 1336 lines before appending §42. NO row closed
(strict-close honest negative — an idle turn yields no cited measurement), no
law falsified. NEXT stays IDLE; the t113 LOOP-END PROPOSAL stands.

## 43. IDLE RE-CHECK #37 (t150, 2026-10-28 02:10 EDT) — negative; no new hole; t149's two guards and both cited code sites re-verified

(1) Trigger (A) NEGATIVE — probe RC=0 at 02:10:24 (session-start cutoff
02:09:27): newest playcap dir playcap-20261014-224611; live-timeline.jsonl
mtime_ns 1793043841304000000 / 5691796463 B — 40th consecutive byte-identical
reading t111..t150, re-statted independently with `stat -c '%Y %y %s'` (exact
match, incl. the .304000000 fractional part) and equal to the tool's own
BASE_MTIME_NS/BASE_SIZE (r1_idle_probe.py:55-56). Zero dosbox procs
(`ps -eo pid,comm` — t114 no-self-match form). Find sweep non-loop: none.
A4 watcher ALIVE pid 27774; /proc read outside the probe again shows
wchan=hrtimer_nanosleep, State S (the 5 s poll tick, not wedged in I/O), fds
1/2->watch.out, 3->live-timeline.jsonl, 4->watch.log. A5: none, 20/20 slots
match the watcher glob. r1_t85g_sitting.py correctly not run.

(2) Trigger (B) NEGATIVE — clean tracked tree at 61d32e2 (diff HEAD empty,
`git status --porcelain` tracked empty, no untracked), no STEERING file, B3
HEAD == journal row 71 sha 61d32e2 (journal re-read independently). The prompt
route — the one that cost t144/t145 — was additionally re-checked BY HAND as a
cross-check on the tool leg: numeric enumeration (`sed 's/prompt-//' | sort -n`)
pairs prompt-72.txt with prompt-71.txt, 58/58 lines each, digit-stripped
`diff` 0 lines and exit 0 — identical verdict to the tool. No new prompt
appeared since the last iteration.

(3) NO NEW COVERAGE HOLE SOUGHT OR FOUND, and t149's load-bearing pieces were
re-verified rather than trusted. Per the t113 loop-end rule this turn ran the
two-trigger probe and nothing else, so the only digging was the cheapest form
of the t148 law (re-check constants/citations before they mislead a later
turn): the two `grep -rn 'stop-report' scripts/` bank-hygiene hits are
r1_idle_probe.py (its own docstring, line 3) plus its .pyc — nothing
regenerates stop-report.md, so the hand-authored append below is safe; the
file was at 1416 lines with zero diff vs HEAD before appending. Both code
sites the IDLE block cites were re-read at the cited line, not from memory:
r1_playcap_watch.py:161 IS the lowercase `glob.glob(os.path.join(out, "save",
"*.sav"))` poll line, and r1_slot.py:49 IS
`cache = os.path.join(root, "work", "r1", ".anch-cache.json")` inside
anchors_cached() — so the TOOL_ARTIFACTS exclusion (r1_idle_probe.py:118) still
names the file that any analyzer run refreshes. Honest scope note on A5, not a
new task: A5 walks the capture dir only (`os.walk(os.path.dirname(TIMELINE))`,
r1_idle_probe.py:191), so a hypothetical slot written outside
work/r1/playcap would still be invisible to it. No such file exists and the
game writes its ring slots into the watched save dir (20/20 measured t149), so
this is an accepted boundary of the leg, recorded rather than fixed.

(4) Infra unchanged since t112 (Xvfb 1196 / x11vnc 1207 / watcher 27774;
x11vnc.log 2026-10-27 17:30:18 / 30114 B — zero connects against the
t111-FIXED launch path); probe children 169020/169107 per the t118 noise law.
Scratch: only /tmp/{a,b}.txt for the hand prompt diff, deleted. game/
untouched; no watch or census run against the live capture. NO row closed
(strict-close honest negative — an idle turn yields no cited measurement), no
law falsified. NEXT stays IDLE; the t113 LOOP-END PROPOSAL stands. §3 answer
outstanding after thirty-seven idle turns.

## 44. IDLE RE-CHECK #38 (t151, 2026-10-28 02:19 EDT) — negative; timeline CONTENT signature added to the (A) baseline

(1) Trigger (A) NEGATIVE — probe RC=0 at 02:19:44 (session-start cutoff
02:17:58): newest playcap dir playcap-20261014-224611; live-timeline.jsonl
mtime_ns 1793043841304000000 / 5691796463 B (41st consecutive byte-identical
reading t111..t151; re-statted independently, exact match, equal to the
probe's own BASE_MTIME_NS/BASE_SIZE at r1_idle_probe.py:55-56); zero dosbox
procs; find sweep non-loop: none; A4 watcher ALIVE pid 27774 (PPid 27772 =
the normal bash-wrapper pair, t115), wchan=hrtimer_nanosleep State S, fds
1/2->watch.out, 3->live-timeline.jsonl, 4->watch.log; A5 none (save/*.sav =
20, all match the watcher glob).

(2) THE ITERATION'S VALUE — the (A) baseline was mtime+size only, which
cannot distinguish a real ingest from a touch, and cannot be re-proved
content-stable without reading 5.7 GB. Recorded a CONTENT signature of the
frozen timeline as a second invariant (t116 content-over-mtime law pointed at
the baseline itself instead of at candidate deltas):
`head -c 65536 live-timeline.jsonl | md5sum` == 42a0bed0507f9052e2009ec94e9c27f1,
`tail -c 65536` == 1529ab1ad70ac360f441d819703f943f, last line
{"file":"60.sav","turn":1254,"T":50,"score_stars":14,...} (the t111 idle-boot
signature). Reading rule for future turns: if mtime/size move but the tail md5
matches, it is a touch not a sitting; if the tail md5 differs, a real ingest
happened regardless of what size says. NEVER md5 the whole file — head/tail
64 KiB only (stream-never-inhale). No probe change made: the md5s are a banked
baseline, and the growth leg already works (t117 positive control).

(3) Trigger (B) NEGATIVE — clean tracked tree at 39dcdc2, no STEERING file,
B3 HEAD == journal row 72 sha 39dcdc2 (re-read independently, ct 02:17:05);
prompt pair prompt-73 vs prompt-72 (58/58 lines) digit-stripped delta 0,
cross-checked by hand against the tool leg — identical verdict. §3 answer
outstanding after thirty-eight idle turns.

(4) Re-verification from source (t147 law), not trust: prompt enumeration
r1_idle_probe.py:335-341 IS the numeric _num sort; r1_playcap_watch.py:161 IS
the lowercase `glob.glob(os.path.join(out, "save", "*.sav"))` poll line;
r1_slot.py:49 IS the `.anch-cache.json` path inside anchors_cached(). Bank
hygiene: `grep -rln stop-report scripts/` -> only r1_idle_probe.py docstring
+ its .pyc; file 1468 lines zero diff vs HEAD before appending. Ledger audit
rows=18 open=[OQ-003,OQ-005,OQ-016,OQ-019,OQ-021,OQ-023] closed=12, OK.
Infra unchanged since t112 (Xvfb 1196 / x11vnc 1207 / watcher 27774;
x11vnc.log 2026-10-27 17:30:18/30114 — zero connects); probe children
170331/170382 per the t118 noise law. Housekeeping: removed the stale
/tmp/t149-watch fixture dir t149 left on disk. NO row closed (strict-close
honest negative), no law falsified. NEXT stays IDLE; the t113 LOOP-END
PROPOSAL stands.


## 45. IDLE RE-CHECK #39 (t152, 2026-10-28 02:28 EDT) — negative; (A) re-arm INSTRUCTION defect found and fixed: the sitting adjudicator could not address the capture dir the trigger names

(1) Trigger (A) NEGATIVE — `python3 scripts/r1_idle_probe.py` RC=0 at
02:28:41 (session-start cutoff 02:26:59): newest playcap dir
playcap-20261014-224611; live-timeline.jsonl mtime_ns 1793043841304000000 /
5691796463 B (42nd consecutive byte-identical reading t111..t152;
re-statted independently, exact match, equal to BASE_MTIME_NS/BASE_SIZE at
r1_idle_probe.py:55-56); zero dosbox procs; find sweep non-loop none; A4
watcher ALIVE pid 27774; A5 none (save/*.sav = 20, all match the glob).

(2) T151'S CONTENT BASELINE REPRODUCED — head 64 KiB md5
42a0bed0507f9052e2009ec94e9c27f1 / tail 1529ab1ad70ac360f441d819703f943f,
both byte-identical to the values banked at §44. The (A) timeline leg now has
a CONTENT baseline whose reproducibility is itself measured: tail-md5 match +
moved mtime == a touch, differing tail-md5 == real ingest.

(3) THE FINDING — defect in the (A) re-arm PATH, downstream of the trigger.
Every idle turn hands the next session the instruction "run
scripts/r1_t85g_sitting.py-style adjudication on the NEW sitting", but that
tool pinned `RUN = ".../work/r1/playcap"` (r1_t85g_sitting.py:18). There are
TWO capture harnesses writing TWO different evidence dirs [verified from
source]: r1_playcap_vnc.sh accumulates into work/r1/playcap (the shared 5.7 GB
timeline), while r1_playcap.sh — the user-facing one-shot that STATE/(A) and
§4 name as the launch path — creates work/r1/playcap-<ts>/ and at line 78
starts `r1_playcap_watch.py "$OUT"`, a PER-RUN watcher writing a PER-RUN
timeline. A playcap.sh sitting therefore writes evidence the named
adjudicator never opens. On disk: 4 of 5 playcap-* dirs hold their own
live-timeline.jsonl (4.8 KB..284 KB).

(4) HAZARD PROVEN BY EXECUTION (not review):
    `r1_t85g_sitting.py work/r1/playcap-20261014-224611`
      -> trusted turn-change rows: 0   (correct: that dir is 65 rows, ALL
         turn=0, a t82-law idle boot)
    `r1_t85g_sitting.py`  (legacy default, exactly what the bare instruction
         invites)
      -> trusted turn-change rows: 45050  (the OLD shared t1253/1254 sitting,
         printed WITH relation snapshots, ship events and damage deltas)
   So a future re-arm on a playcap.sh capture would have banked the STALE
   sitting's battle/alliance evidence as if it were the user's new game —
   silently, no error, no dir named. Same family as the 0x88 pointer-law trap:
   wrong input, plausible output.

(5) FIX — scripts/r1_t85g_sitting.py: `RUN = sys.argv[1] if len(sys.argv)>1
else DEFAULT_RUN` (default kept for t85g's own historical re-runs), and the
row-count header now echoes the source dir. py_compile clean; both branches
run above. LAW banked (generalising t145): when a procedure names a tool AND
an object, verify the tool can address THAT object — a pinned default that was
right for the last 30 turns proves nothing about the next. The trigger itself
was never blind: a new playcap-<ts> dir arms r1_idle_probe.py:74 regardless of
name.

(6) Trigger (B) NEGATIVE — clean tracked tree at 6ff9ded, no STEERING file,
B3 HEAD == journal row 73 sha 6ff9ded (re-read independently, ct 02:26:06);
prompt pair prompt-74 vs prompt-73 (58/58 lines) digit-stripped delta 0. §3
answer outstanding after thirty-nine idle turns.

(7) Re-verification from source (t147 law): r1_idle_probe.py:335-341 IS the
numeric _num sort; r1_playcap_watch.py:161 IS the lowercase save-glob poll
line; r1_slot.py:49 IS the .anch-cache.json path in anchors_cached(). Bank
hygiene: grep -rln stop-report scripts/ -> only r1_idle_probe.py + .pyc; file
1514 lines zero diff vs HEAD before appending. Infra unchanged since t112
(Xvfb 1196 / x11vnc 1207 / watcher 27774; x11vnc.log 2026-10-27
17:30:18/30114 — zero connects); probe children 171676/171728 per the t118
noise law. NO row closed (strict-close honest negative), no law falsified.
NEXT stays IDLE; the t113 LOOP-END PROPOSAL stands.

## 46. IDLE RE-CHECK #40 (t153, 2026-10-28 02:50 EDT) — negative; (B4) coverage FIX: a decision delivered as a NEW untracked file was invisible to every (B) leg

(1) Trigger (A) NEGATIVE — `python3 scripts/r1_idle_probe.py` RC=0 at 02:50:35
(session-start cutoff 02:48:55): newest playcap dir playcap-20261014-224611;
live-timeline.jsonl mtime_ns 1793043841304000000 / 5691796463 B (43rd
consecutive byte-identical reading t111..t153; re-statted independently, size
exact match, equal to BASE_MTIME_NS/BASE_SIZE at r1_idle_probe.py:55-56
re-read from source); zero dosbox procs; find sweep non-loop none; A4 watcher
ALIVE pid 27774; A5 none (save/*.sav = 20, all match the glob). r1_t85g_sitting.py
correctly NOT run; its t152 argv law re-verified from source (:26-27
DEFAULT_RUN / RUN = sys.argv[1]).

(2) T151 CONTENT BASELINE REPRODUCED a third time, byte-identical: head-64KiB
md5 42a0bed0507f9052e2009ec94e9c27f1, tail-64KiB md5
1529ab1ad70ac360f441d819703f943f.

(3) THE FINDING — a hole in trigger (B), found by asking what each leg DOES
with its input (t145 law), not whether it reads it. B1 diffs TRACKED files,
B3 compares commits, B2 diffs prompt text, and the STEERING leg globs the
literal names `docs/STEERING* STEERING*`. The one line that could see a brand
new file printed `??` entries as blanket "informational, NOT a trigger". t117's
law justified that against the LOOP'S OWN untracked files (docs/re/_wip_*.md,
probe scratch) but was applied to every path — so a user answer delivered as a
new file (docs/ANSWER.md, notes.md, a RESTORE-ME note, a re-added deleted doc)
read IDLE forever.

(4) FIX (B4): split untracked by OWNERSHIP instead of deleting the leg.
`git status --porcelain --untracked-files=all` `??` entries under LOOP_OWNED
stay informational (t117 preserved); foreign untracked paths ARM. Measured
safety first: porcelain never lists gitignored paths, and .gitignore covers the
loop's whole scratch surface (build/, build-*/, rewrite/build/, .logs/,
__pycache__/, *.pyc, .venv/, .cache/, .cache_check, *.log, work/) — verified by
creating a fixture in each and watching it stay unlisted — so a non-ignored
untracked file outside loop-owned has no loop-tool origin.
Validated by real execution on FOUR branches, fixtures deleted afterwards:
real state (only docs/re/_wip_t153.md untracked) -> none / RC=0; foreign
`t153_fixture_ANSWER.md` at repo root -> ARMS RC=1 naming the path and saying
why; gitignored scratch (.logs/*.log, work/r1/*) -> (B4) prints none (an
(A) find-sweep arm on the work/r1 fixture fired instead — correct division of
labour, the sweep owns work/r1); after fixture removal, control RC=0 with both
legs clean.

(5) Trigger (B) NEGATIVE — clean tracked tree at 1abf176, no STEERING file,
B3 HEAD == journal row sha 1abf176, prompt pair prompt-75 vs prompt-74 (58/58)
digit-stripped delta 0. §3 answer outstanding after forty idle turns.

(6) Bank hygiene fresh: grep -rln stop-report scripts/ -> only r1_idle_probe.py
+ its .pyc; file 1581 lines zero diff vs HEAD before appending. Infra unchanged
since t112 (Xvfb 1196 / x11vnc 1207 / watcher 27774; x11vnc.log 2026-10-27
17:30:18/30114 — zero connects); probe children per the t118 noise law. NO row
closed (strict-close honest negative), no law falsified. NEXT stays IDLE; the
t113 LOOP-END PROPOSAL stands. FUTURE TURNS: an (A) find-sweep arm at
work/r1/<file> you did not create is capture-side evidence; check it against
(A4)/(A5) before calling the turn idle. Gate 0.

## 47. IDLE RE-CHECK #41 (t154, 2026-10-28 03:06 EDT) — negative; no new hole; t153's (B4) split and the sweep/B4 division of labour verified IN SOURCE

Idle turn per the IDLE block: two-trigger probe and nothing else (t113
LOOP-END PROPOSAL still stands; no watch, no census against the live capture).

(1) Trigger (A) NEGATIVE — `python3 scripts/r1_idle_probe.py` RC=0 at
03:06:14 (cutoff 03:05:19 from the iter-log name stamp): newest playcap dir
playcap-20261014-224611; live-timeline.jsonl mtime_ns 1793043841304000000 /
5691796463 B — 44th consecutive byte-identical reading (t111..t154), and
re-statted independently (`stat -c`), EQUAL to BASE_MTIME_NS/BASE_SIZE as
re-read from source at r1_idle_probe.py:55-56, not from this doc. t151
CONTENT baseline reproduced byte-identical a THIRD time (head64K
42a0bed0507f9052e2009ec94e9c27f1 / tail64K 1529ab1ad70ac360f441d819703f943f);
last timeline line still the t1254 row (file 60.sav, wall 15:44:01). Zero
dosbox procs (`ps -eo comm`, t114 law); find sweep non-loop none; A4 watcher
ALIVE pid 27774; A5 none (save/*.sav = 20, all match the watcher glob).

(2) NO NEW HOLE — the t145 method (ask what each leg DOES with its input) was
applied to the surfaces t153 touched, and this time they hold. Verified in
source rather than by behaviour alone: LOOP_OWNED (r1_idle_probe.py:59-60) is
STATE/OPEN-QUESTIONS/BLOCKED/docs/re//r1_idle_probe.py/work/; the (A)
find-sweep filter excludes only the `work/r1/loop/` PREFIX plus TOOL_ARTIFACTS
— NOT LOOP_OWNED wholesale — so a foreign file anywhere under work/r1 still
arms (A) while (B4) (ownership split at :259/:277) owns the rest of the tree.
That is the t153 division of labour confirmed structurally: the two legs are
complementary by construction, not accidentally consistent at run time. B2's
numeric sort (int() key, :361-364) re-checked against the t144 trap.

(3) Trigger (B) NEGATIVE — clean tracked tree at d62b1f3; `git diff HEAD
--name-only` empty; porcelain tracked empty; untracked loop-owned none;
FOREIGN untracked none (the new (B4) leg clean on real state on its first
production turn); delta outside loop-owned none; STEERING none; B3 HEAD ==
journal last-tab-field sha d62b1f3 (re-checked independently with
`tail -1 journal.tsv | awk -F'\t' '{print $NF}'`, per the t146 invariant);
prompt pair prompt-76.txt vs prompt-75.txt (58/58 lines) digit-stripped
delta 0. §3 answers (OQ-003 entropy, OQ-005 dims, OQ-019 sugar-cube,
OQ-023 threshold-only branch, capture authorization, t89a follow-on) still
outstanding after forty-one idle turns.

(4) Bank hygiene fresh: grep -rln stop-report scripts/ -> only
r1_idle_probe.py (+ .pyc); gate.sh contains no touch/write of docs/re. File
was 1636 lines with zero diff vs HEAD before appending this section. Infra
unchanged since t112 (Xvfb 1196 / x11vnc 1207 / watcher 27774; x11vnc.log
2026-10-27 17:30:18/30114 — zero connects). NO row closed (strict-close honest
negative), no law falsified. NEXT stays IDLE; the t113 LOOP-END PROPOSAL
stands. Gate 0.

## 48. IDLE re-check #42 (t155, 2026-10-28 03:16 EDT) — verdict/CAUTION contradiction fixed (B5)

Trigger (A) NEGATIVE — probe RC=0 at 03:16:34 (cutoff 03:14:49): newest playcap
dir playcap-20261014-224611; live-timeline.jsonl mtime_ns 1793043841304000000 /
5691796463 B (45th consecutive byte-identical reading t111..t155; re-statted
independently, equal to BASE_MTIME_NS/BASE_SIZE at r1_idle_probe.py:55-56); t151
content baseline reproduced a FOURTH time (head 42a0bed0507f9052e2009ec94e9c27f1 /
tail 1529ab1ad70ac360f441d819703f943f; last row still t1254); zero dosbox procs;
find sweep non-loop none; A4 watcher ALIVE pid 27774; A5 none (save/*.sav = 20).
THE FINDING — hole (B5), found by running the t145 method against the last leg
whose OUTPUT shape had never been questioned. trigger_b() demoted every tracked
delta under LOOP_OWNED to a buried CAUTION line while the printed VERDICT asserted
"neither trigger" and RC=0. LOOP_OWNED (:59-60) contains docs/OPEN-QUESTIONS.md
and docs/BLOCKED.md — the two files stop-report §3 invites the user to answer
INTO. The loop quotes the RC line (STATE.md's (A)/(B) block says "RC=0 both
negative (stay IDLE)"), so the caution never reached the decision. FIX: trigger_b
returns a third value `decision_candidate`; main() prints "CANDIDATE — read the
CAUTION" as the (B) header and an "IDLE with CANDIDATE ... Read `git diff HEAD`
BEFORE keeping the IDLE block" VERDICT. Deliberately NOT armed (RC stays 0): t117
law says only an observed user event arms, and a crashed iteration that edited
the ledger pre-commit leaves byte-identical state — mtime cannot separate the
origins, so escalation-not-arming is the only sound choice. Validated by REAL
execution on five branches: real state CANDIDATE RC=0 (self-demonstrating — the
patched probe is itself loop-owned); clean tree + OLD code NEGATIVE RC=0
(regression control); clean tree + NEW code CANDIDATE RC=0; NEW code + foreign
untracked docs/ANSWER-t155test.md ARMED RC=1 (B4 precedence, fixture deleted);
fixture removed → CANDIDATE again RC=0. Also measured, not assumed: the prompt
corpus is 77 files with only 3 distinct digit-stripped bodies (41x15, 63x3,
58x59), so B2's newest-pair rule has no multi-shape drift exposure; and
LOOP_OWNED's "work/" entry is inert for B1/B3/B4 because git ls-files work/ is
empty and .gitignore ignores work/ wholesale — the blind surface that leaves
(new/modified files under work/ outside work/r1) is ACCEPTED: both capture
launch paths pin OUT under work/r1 (r1_playcap.sh:22, r1_playcap_vnc.sh:30) so
the (A) sweep owns every real capture, and broadening the sweep to all of work/
re-creates the t149 self-inflicted-arm shape. Trigger (B) NEGATIVE at session
start — clean tracked tree at f0e9527, no STEERING, B3 HEAD == journal sha
f0e9527 (re-extracted via rev/cut), prompt pair prompt-77 vs prompt-76
(58/58) digit-stripped delta 0 both by tool and by hand ls -1v. §3 answers
outstanding after forty-two idle turns. Bank hygiene fresh (grep -rln
stop-report scripts/ -> only r1_idle_probe.py + .pyc; stop-report.md 1683 lines
zero diff vs HEAD before appending §48). Infra unchanged since t112. NO row
closed (strict-close honest negative), no law falsified. NEXT stays IDLE; the
t113 LOOP-END PROPOSAL stands. Gate 0.

## 49. IDLE re-check #43 (t156, 2026-10-28 03:40 EDT) — both triggers negative; (A6) coverage FIX: the t151 content baseline was documented, not enacted

Trigger (A) NEGATIVE (probe RC=0 at 03:39:49, session-start cutoff 03:38:08):
newest playcap dir playcap-20261014-224611; live-timeline.jsonl mtime_ns
1793043841304000000 / 5691796463 B (46th consecutive byte-identical reading,
independently re-statted with stat -c '%Y %y %s' and equal to the probe's own
BASE_MTIME_NS/BASE_SIZE at r1_idle_probe.py:75-76); zero dosbox procs; find
sweep non-loop none; A4 watcher ALIVE pid 27774; A5 none (save/*.sav = 20, all
match the watcher glob). Trigger (B) NEGATIVE: clean tracked tree at 1767c28,
no STEERING file, untracked none inside/outside LOOP_OWNED, B3 HEAD == journal
sha 1767c28 (row 77 ct 03:37:15, last tab field re-extracted by hand outside
the probe), prompt pair prompt-78 vs prompt-77 (58/58) digit-stripped delta 0.
The VERDICT printed "IDLE — neither trigger", valid because the tree was clean
AT SESSION START (t155/B5 semantics).

THE FINDING — hole (A6), the t145 method ("ask what the leg DOES with its
input") aimed at the timeline growth leg. trigger_a compared ONLY st_mtime_ns
and st_size; `grep -c 'md5|hashlib' scripts/r1_idle_probe.py` returned 0. The
t151 rule — tail-md5 match + moved mtime = a touch, differing tail-md5 = real
ingest — lived ONLY in STATE.md prose, quoted forward ever since. So on the
loop's highest-stakes path, a fresh session that arms on (A) and does not
re-read the prose would run r1_t85g_sitting.py on the SHARED shared dir and
print the stale t1253/1254 sitting with alliance/ship/damage snapshots as if it
were the user's new game: the exact t152 hazard, with no error and (via the
default) no dir echo warning anyone.

FIX (scripts/r1_idle_probe.py): edge_md5() (first/last 64 KiB only, seek-based,
measured 0.019 s on the real 5.7 GB file; a file no larger than one window IS
its own head and tail) + the (A6) leg. Same size AND both md5s == baseline =>
"TOUCHED not grown", NOT armed; anything else => armed with the actual values;
OSError => armed without content check (cannot disprove growth). Demotion is
sound BECAUSE the watcher appends (r1_playcap_watch.py:146 jl=open(jlp,"a")):
an ingest strictly grows the file, so it can never be md5-and-size-neutral.
TIMELINE is now env-overridable (R1_TIMELINE) like R1_JOURNAL/R1_WATCH_SCRIPT,
so the leg is testable. Baseline constants pinned as BASE_HEAD_MD5 /
BASE_TAIL_MD5 next to the size baseline, with the re-freeze law inherited.

VALIDATION BY REAL EXECUTION (fixtures deleted): t1 growth arms "CONTENT
CHANGED"; t2 touch (new mtime, same size, same md5s) does NOT arm; t3 same-size
content-diff arms; t4 unreadable arms without content check; helper
cross-checked against the hand-measured dd/tail md5s on the REAL file (MATCH
True); t5 real-state control RC=0. One patch bug self-inflicted and caught by
running the tests: the first edge_md5 left the file position at EOF after the
head read, so files under one 64 KiB hashed an empty tail (d41d8cd9) while the
docstring promised otherwise — inert for the real file, a latent lie for any
future small fixture; rewritten with an explicit size<=window branch.

LAW GENERALISED (extends t145/t155): a rule recorded in STATE.md prose is NOT a
leg. If the adjudication depends on a human re-reading the doc at the moment of
the trigger, it will not happen — encode it in the tool or keep saying out loud
that the trigger is un-adjudicated.

## 50. IDLE re-check #44 (t157, 2026-10-28 03:55 EDT) — both triggers negative; ledger-index drift found and repaired

Trigger (A) NEGATIVE — probe RC=0 at 03:55:39 (cutoff 03:53:57): newest playcap
dir playcap-20261014-224611; live-timeline.jsonl mtime_ns 1793043841304000000 /
5691796463 B (47th consecutive byte-identical reading t111..t157; independently
re-statted, equal to BASE_MTIME_NS/BASE_SIZE); (A6) content baseline reproduced
a SIXTH time head 42a0bed0507f9052e2009ec94e9c27f1 / tail
1529ab1ad70ac360f441d819703f943f, last row still t1254; zero dosbox procs; find
sweep non-loop none; A4 watcher ALIVE pid 27774; A5 none (save/*.sav = 20).
Trigger (B) NEGATIVE — clean tracked tree at 1f62e45 at session start (so the
"IDLE — neither trigger" verdict wording is valid per t155/B5), no STEERING,
B3 HEAD == journal sha 1f62e45 (re-extracted by hand from journal.tsv last tab
field), prompt pair prompt-79 vs prompt-78 (58/58 lines) digit-stripped delta 0.

THE FINDING — a control-plane hole OUTSIDE the trigger surface: STATE.md's
"ledger:" fast index had silently diverged from the authoritative record
docs/OPEN-QUESTIONS.md by SIX rows, measured with ledger_audit.py's own status
classifier (imported, not eyeballed): OQ-006, OQ-012, OQ-015, OQ-020, OQ-025
were listed open while the record CLOSED them, and OQ-023 (genuinely open) was
absent from the index entirely. STATE.md's header says "Update BOTH or neither"
— the invariant existed in prose and had been violated for an unknown number of
turns. Why nothing caught it: gate.sh never runs ledger_audit.py (grep: no
match); loop_one_task.sh runs it post-flight but the audit only checks the
RECORD against its own hard-coded --expect list — it cannot see STATE.md, whose
index ledger_audit's docstring even describes in a format ("- > OQ-") STATE
never used. A fresh session that obeys "resume from STATE.md ALONE" reads a
10-row menu with 5 stale rows and misses the 1 missing open row. Idle turns
never acted on it because they don't pick tasks from the index — the day the
loop RE-ARMS, it picks from this menu.

REPAIR: index re-derived from the record (open = OQ-003/005/016/019/021/023,
closed = the 12 record rows + 7 v1 ids); and scripts/ledger_index_check.py
shipped — same classifier as ledger_audit (imported), diffs STATE's block
against the record, exit 1 naming each divergence. Validation by REAL
execution: HEAD's pre-repair STATE.md -> RC=1 naming all six drifts; repaired
STATE.md -> RC=0 "LEDGER INDEX OK"; fixtures deleted. The drift mechanism was
scope-narrowing narrative: each closed sub-leg stayed INLINE in the open-entry
text (e.g. OQ-012 "(a)...(d) all closed") while the row never moved to the
closed list — so a reader of the index sees "open" and a grepper of the body
sees all-closed. v1 ids (OQ-001/002/007/008/009/011/017) are exempt by design:
they close in the record's "- > OQ-" index block that ledger_audit skips.

LAW GENERALISED (extends t145/t146/t155/t156): a documented invariant between
two files is not enforced by anyone reading one of them. ledger_audit checked
file A against a constant; STATE's prose told humans to keep B equal to A; both
were satisfied in their own terms while A and B disagreed. If a fact must be
true across two artifacts, ship a checker that reads BOTH — and point the prose
at the checker, not at the manual discipline.

NO row closed (strict-close honest negative — the repair is bookkeeping, not
measurement); no law falsified. NEXT stays IDLE; the t113 LOOP-END PROPOSAL
stands (now 44 idle turns with zero user input).

## 51. IDLE re-check #45 (t158, 2026-10-28 04:17 EDT) — both triggers negative; t157's law recursed onto t157's own fix; strict-close evidence leg tightened

Trigger (A) NEGATIVE — probe RC=0 at 04:17:08: newest playcap dir
playcap-20261014-224611; live-timeline.jsonl mtime_ns 1793043841304000000 /
5691796463 B (48th consecutive byte-identical reading t111..t158; independently
re-statted with `stat -c`, equal to BASE_MTIME_NS/BASE_SIZE); (A6) content
baseline reproduced a SEVENTH time head 42a0bed0507f9052e2009ec94e9c27f1 / tail
1529ab1ad70ac360f441d819703f943f, last row still t1254; zero dosbox procs; find
sweep non-loop none; A4 watcher ALIVE pid 27774; A5 none (save/*.sav = 20).
Trigger (B) NEGATIVE — clean tracked tree at ec8a5ee at session start (verdict
wording "IDLE — neither trigger" valid per t155/B5), no STEERING, B3 HEAD ==
journal sha ec8a5ee (journal row 79 last tab field), prompt pair prompt-80 vs
prompt-79 (58/58 lines) digit-stripped delta 0. ledger_index_check at session
start: LEDGER INDEX OK.

HOLE 1 — t157's own fix was prose-enforced, which is what t157's generalised law
forbids. t157 shipped ledger_index_check.py and then pointed the NEXT ACTION
prose at a HUMAN RUNNING IT. Measured: `grep -c ledger_index_check` == 0 in
scripts/gate.sh AND 0 in scripts/loop_one_task.sh; the only automatic post-flight
checks are gate.sh + ledger_audit.py (loop_one_task.sh:119-124). Consequence: a
future session that edits STATE.md's ledger block and never runs the tool moves
HEAD green, and the 6-row drift shape returns within one careless turn. The loop
is alive (pids 78558/78559/78561), so this is the live enforcement surface.
FIX: gate.sh stage 3t runs BOTH ledger checks (/usr/bin/python3, matching every
other python stage in the file). gate.sh is the single command both the harness
post-flight and each iteration's finish sequence already run, so the invariant
becomes automatic. Cost measured: ~0.1 s. VALIDATED BY REAL EXECUTION, both
directions: (i) HEAD's clean tree -> GATE_EXIT=0 with the stage silent; (ii) the
pre-t157 drifted STATE.md restored from 1f62e45 via R1_STATE -> GATE_EXIT=1
naming all six drifts plus "re-derive the block from docs/OPEN-QUESTIONS.md (the
record wins)". Fixture deleted.

HOLE 2 — the strict-close auditor graded prose as citation. ledger_audit.py's
t84 EVIDENCE regex accepted the generic words \bmeasured\b, \bverified\b, law\b,
slots?\b, .sav/.gam/.cob/.dip as a satisfying evidence leg, so a CLOSED row
reading "verified and measured, the law holds" with NO address, offset, run dir,
digest or test name printed LEDGER AUDIT OK. That is GOAL.txt's forbidden state
(a plausible default grading itself as closed) wearing the auditor's own clothes.
The same regex had NO FUN_/DAT_ alternative, so Ghidra-style citations
(FUN_00044a44, DAT_00013bc5) did not match it at all — the leg was simultaneously
too weak and blind to the project's dominant citation form.
FIX: EVIDENCE now requires >=1 SPECIFIC handle: 0x-address | FUN_ | DAT_ | md5 |
capture run dir (r1xxx-NNNNNN) | N-of-M count | scripts/*.py probe path |
docs/re/*.md banked section. Old pattern kept as EVIDENCE_GENERIC for reference.
MEASURED before tightening (imported classifier over the 12 real closed rows):
every row carries >=1 handle — OQ-010 82 hex; OQ-022 13; OQ-020 9; OQ-006 7;
OQ-013 7; OQ-024 5; OQ-018 5; OQ-014 4; OQ-004 1 hex + md5; OQ-025 0 hex but
1 rundir + 15 ratios + probe path + docsec; OQ-012 2 rundirs + 2 ratios +
docsec; OQ-015 2 FUN_ + 5 ratios + docsec — so zero retroactive false positives.
VALIDATED: real record -> LEDGER AUDIT OK unchanged (rows=18 open=6 closed=12);
synthetic prose-only row -> "MISSING evidence: OQ-100" RC=1; synthetic
handle-bearing row -> passes. First fixture attempt was thrown (concatenation
without a trailing newline glued onto the last row and shifted the row count to
8/4 — a fixture bug, not an auditor bug; re-tested on a clean minimal ledger).

LAW (third instance of the t145 family, and the first where the hole was in the
PREVIOUS iteration's fix): shipping a checker is not enforcement. Enforcement is
the checker sitting in a path the loop cannot exit through. Audit every new
checker with `grep -l <name> scripts/gate.sh scripts/loop_one_task.sh` — zero
hits means you shipped a suggestion. Corollary for policy text: a strictness rule
written in a docstring ("only measurement closes a row") is not the policy; the
regex that grades the evidence IS the policy, so audit the grader whenever the
policy is restated.

NO row closed this iteration (no new measurement; strict-close honest negative);
no law falsified; game/ untouched; no watch or census run against the live
capture. NEXT stays IDLE; the t113 LOOP-END PROPOSAL stands (45 idle turns, zero
user input).

## 52. IDLE re-check #46 (t159, 2026-10-28 04:40 EDT) — both triggers negative; the audit grader could never pass the COMPLETION state; fixed

(1) TRIGGER A NEGATIVE — `python3 scripts/r1_idle_probe.py` RC=0 at 04:40:29:
newest playcap dir playcap-20261014-224611; live-timeline.jsonl mtime_ns
1793043841304000000 / 5691796463 B (49th consecutive byte-identical reading
t111..t159; independently re-statted via `stat -c '%Y %y %s'`, exact match to
the probe's BASE constants); (A6) content baseline reproduced an EIGHTH time
(head 64 KiB md5 42a0bed0507f9052e2009ec94e9c27f1 / tail
1529ab1ad70ac360f441d819703f943f, recomputed outside the probe, match True);
zero dosbox procs; find sweep 4 files, non-loop: none; A4 watcher ALIVE pid
27774; A5 none (save/*.sav = 20). r1_t85g_sitting.py correctly not run.
(2) TRIGGER B NEGATIVE — clean tracked tree at 0e8c8e9 at session start (verdict
wording valid per t155/B5), no STEERING, B3 HEAD == journal sha 0e8c8e9, prompt
pair prompt-81 vs prompt-80 (58/58) digit-stripped delta 0; ledger both legs OK
at session start. §3 answers outstanding after forty-six idle turns.
(3) THE FINDING — the t158 corollary ("audit the grader") aimed at the one case
the audit had NEVER seen in 158 iterations: a ledger with zero open rows, which
is GOAL.txt:2's own completion condition. Fixture (all 18 rows CLOSED, verified
via ledger_audit's own rows()/status_of) executed against both gate-3t legs:
`ledger_audit.py --ledger <all-closed> --expect ''` printed "OPEN-SET MISMATCH
vs expected ['']" RC=1 — because `"".split(",") == [""]`, want became {""} and
an empty open set can never equal it. `--expect ''` is the only CLI form of the
completion state, so the strict-close grader made the project's terminal green
unreachable by construction: a future session that legitimately closed the last
row would gate RED forever (or be tempted to delete the check). ledger_index_check
was already fine on the same fixture (RC=0 with an emptied STATE block — F7).
FIX, one line in scripts/ledger_audit.py main(): `want = {x.strip() for x in
a.expect.split(",") if x.strip()}`. Four branches validated by REAL execution,
fixtures deleted after: (a) real ledger + real default OK RC=0 (regression,
byte-identical verdict); (b) all-closed fixture + `--expect ''` OK RC=0;
(c) clone with the default string itself emptied (the completing session's
actual edit shape — history shows t89/t100 edited it per closure) + fixture
OK RC=0; (d) that clone vs the REAL open ledger FAILED RC=1 (an empty default
cannot silently bless open rows). py_compile clean. LAW (extends t158): when a
grader encodes a set as a literal, ask what its EMPTY case does — a checker that
cannot represent success converts "done" into "broken", the mirror image of the
t157 cannot-represent-drift bug.
(4) MEASURED BOUNDARIES, documented and deliberately NOT fixed: (a) status_of
is position-dependent (first pipe-wrapped status-shaped cell wins,
ledger_audit.py:52-61, t85 design); fixture F5 pasted "| CLOSED t40 note |" into
OQ-021's QUESTION field and the row flipped CLOSED — but BOTH gate-3t legs
caught it (audit RC=1 mismatch, index RC=1 naming the row), so the failure mode
is a lousy message, not silent green; a strict column-2 rule was rejected
because real rows legitimately put status words elsewhere (OQ-016 "| open
(sub-laws CLOSED: ...)"), so it would false-positive before the record is
reformatted. (b) `--expect` stays a hand-maintained duplicate of the open set
(deriving it from the record would be circular; the mismatch message names both
sets so repair is mechanical).
(5) RE-ARM MECHANISM MEASURED ALIVE, first explicit record anywhere: tmux
`ascendloop` pid 78558 (PPid 1) -> bash 78559 -> `bash scripts/loop_one_task.sh`
78561; this session is iteration 81 under `timeout -s KILL 12600 hermes chat
--query-file work/r1/loop/prompt-81.txt`; journal last row iter 80 OK 0e8c8e9;
fail_streak 0; no crontab. The supervisor is NOT inside gate.sh or the idle
probe (A4 adjudicates the watcher only), so its death is un-adjudicated by
design; repair = relaunch the exact 78558 command line after checking for
work/r1/loop/STOP. (6) Gate traversal: stage 3t is unavoidable — gate.sh uses
`set -u` (NOT `set -e`), err() only sets fail=1, the sole exit is `exit $fail`
at :464, and the harness post-flight runs the whole script
(loop_one_task.sh:119) — t158's enforcement question answered in the negative,
nothing to repair.
Bank hygiene fresh (grep -rln stop-report scripts/ -> r1_idle_probe.py +
ledger_audit.py docstrings only; 1901 lines zero diff vs HEAD before appending
§52). NO row closed (strict-close honest negative — harness hardening, not
measurement), no law falsified. NEXT stays IDLE; the t113 LOOP-END PROPOSAL
stands (46 idle turns). Gate 0.

## 53. IDLE re-check #47 (t160, 2026-10-28 05:05 EDT) — both triggers negative; the last hand-maintained duplicate in the ledger checks (V1_IDS) derived + reconciled

(1) TRIGGER (A) NEGATIVE — probe RC=0 at 05:01:53 (session start ~05:00):
newest playcap dir playcap-20261014-224611; live-timeline.jsonl mtime_ns
1793043841304000000 / 5691796463 B (50th consecutive byte-identical reading
t111..t160; independently re-statted via stat -c, exact match to
BASE_MTIME_NS/BASE_SIZE); (A6) content baseline reproduced a NINTH time head
42a0bed0507f9052e2009ec94e9c27f1 / tail 1529ab1ad70ac360f441d819703f943f, last
row still {"file":"60.sav","turn":1254,...}; zero dosbox procs; find sweep 4
files, non-loop: none; A4 watcher ALIVE pid 27774; A5 none (save/*.sav = 20).
r1_t85g_sitting.py correctly not run.

(2) TRIGGER (B) NEGATIVE — clean tracked tree at 87b41a4 at session start
(verdict wording valid per t155/B5), no STEERING, B3 HEAD == journal sha
87b41a4 (row 81, ct 04:59:16, re-read independently), prompt pair prompt-82 vs
prompt-81 (58/58) digit-stripped delta 0. §3 answers outstanding after
forty-seven idle turns.

(3) THE FINDING — the t145/t158 method (audit the grader's own inputs) run
against the one hand-maintained literal left in the ledger checks after t159:
ledger_index_check.py:38 `V1_IDS = {OQ-001,002,007,008,009,011,017}`. That set
is an EXEMPTION list: ids it names skip both "absent from record" divergence
legs, because the record closes them in the "- > OQ-" v1 block that
ledger_audit.rows() skips by design (t84 contract). Measured BEFORE patching:
the derived set from grep '^- > OQ-' over the real record == the literal
exactly (7/7), so no live drift existed — but nothing ever compared the two.
Drift shapes and their costs: (a) the record's v1 block deleted or reflowed ->
7 closed v1 rows silently stop being exempt, and the check would arm FALSE
divergence on a legitimate doc edit; (b) worse direction — the block gaining an
id (someone filing a v2 closure into the v1 region) silently EXEMPTS that row
from every cross-check, and worse still, with the block gone AND the literal
gone, both gate-3t legs print OK over vanished v1 closures. Fourth instance of
the t157/t158/t159 family: any fact restated as a literal inside a checker is a
duplicate that needs a leg.

FIX (scripts/ledger_index_check.py): V1_IDS is now DERIVED each run from the
record itself (v1_block_ids(): ^- > OQ-(\d+) lines; grep-verified the real
record's only 7 '^- > ' lines are all '^- > OQ-', so no non-id line pollutes
the set) and RECONCILED against a deliberately-kept code pin
V1_IDS_EXPECTED — disagreement fails RC=1 naming the exact delta in BOTH
directions. The literal became the leg rather than being deleted: deleting it
would recreate hazard (b) silently, keeping it unreconciled was hazard (a)+(b)
unwatched; the reconciliation makes the pair self-policing.

VALIDATION by REAL execution (fixtures /tmp/t160-f-*.md deleted after):
t1 real tree LEDGER INDEX OK RC=0 (byte-identical verdict to pre-patch);
t2 v1 block deleted -> RC=1, drift line names all 7 literal_only ids PLUS the
7 "id absent from record" divergences (double signal, no silent green);
t3 block gains spurious OQ-099 -> RC=1 naming block_only=['OQ-099'];
t4 pre-t157 drifted STATE (git 1f62e45, R1_STATE) -> RC=1 naming all six
original drifts (the t157 leg still works through the new code path). First t4
attempt printed RC=0 — that was MY test-harness bug (`env_extra + "; true"`
truncated before the python invocation, nothing ran), caught by checking the
fixture existed and re-running; py_compile clean after both patches.
Enforcement per t158 law: grep ledger_index_check scripts/gate.sh -> gate.sh:421
(stage 3t) already invokes it; nothing new to wire.

LAW (extends the family): when a checker holds a constant that names objects in
another artifact, ask which artifact is the contract and derive from it — but
KEEP the constant as a reconciliation pin so a silent edit of the contract
becomes a loud failure. Derive-and-reconcile, not copy-and-hope and not
delete-and-trust.

## 54. IDLE re-check #48 (t161, 2026-10-28 05:15 EDT) — both triggers negative; ledger_index_check had NO closed-side leg: two real CLOSED rows were missing from STATE.md and it printed OK

Triggers (A) and (B) both NEGATIVE at session start (clean tree at b9cf937,
probe RC=0, timeline byte-identical for the 50th consecutive reading, (A6)
content baseline reproduced a tenth time, watcher alive pid 27774, B3 HEAD ==
journal sha, prompt pair 83/82 delta 0). Full readings in docs/STATE.md's
T161 LANDED block.

THE FINDING — t160's audit-the-grader method applied one level deeper: instead
of asking whether each leg of ledger_index_check.py fires, ask which record ids
NO leg compares. Importing the tool's own sets (ledger_audit.rows/status_of,
v1_block_ids, state_index) on the real file pair gave:

    LEG A  rec_open - idx_open                = []
    LEG B  idx_open - rec_open                = []
    LEG C  idx_closed - rec_closed - V1_IDS   = []
    LEG D  idx_open & idx_closed              = []   (leg exists)
    UNCOVERED  rec_closed - idx_closed        = ['OQ-022','OQ-024']  <- LIVE DRIFT

Every t157 leg is indexed on the OPEN side or on entries the index ALREADY has
(ledger_index_check.py:111-124 pre-patch). "The record has a CLOSED row the
index never mentions" moved nothing and printed LEDGER INDEX OK. Not
hypothetical: the record closes OQ-022 (t8, music span check) and OQ-024 (t45,
governor law) and STATE.md's block listed neither — 19 closed ids in the record
(12 main-table + 7 v1-block) vs 17 in the index, while the header asserts
"statuses mirror ... Update BOTH or neither".

ORIGIN (git-archaeologied, not assumed): `git log -S'OQ-022' -- docs/STATE.md`
newest hit t57c; OQ-024 newest t44 — neither id has been touched in the ledger
block since t157 re-derived it. So this is residue of t157's own repair: it
re-derived the OPEN side (the side its legs could see) and hand-copied the
closed list, dropping 2 rows. Fourth recursion in the family: t158 found t157's
law unenforced, t159 found the grader couldn't represent done, t160 found the
exemption constant hand-duplicated, t161 finds t157's fix covered only one
direction. LAW (extends t159): when writing a bidirectional consistency check,
enumerate the directions as SET PAIRS (record-vs-index on open AND on closed);
a leg list derived from "what drifted last time" inherits last time's blind
side, because t157's drift was an open-side drift and every leg it shipped
fires on the open side.

WHY IT MATTERS even though the closed list is not the task menu: STATE.md is
what a fresh session reads ALONE. A session cannot learn OQ-022/OQ-024 exist,
so it can re-file closed work as novel, and t159's CLOSURE NOTE (terminal green
= empty open ledger) is graded off the same block that silently loses ids.

FIX (scripts/ledger_index_check.py, hard DIVERGENCE not CAUTION — t155 law: a
signal that only reaches a buried line is unenacted):
  leg E  record-CLOSED (main table OR v1 block) missing from STATE's closed
         list -> names the id and prints a pasteable `- "OQ-NNN ..."` stub.
  leg F  duplicate id in the RECORD (rows() can yield one twice; the status
         dict keeps the LAST body silently). Real record measured 18 rows /
         18 distinct today, so this is an early trip, not a live fix. The
         nost early-return previously skipped printing leg F's finding even
         when it had fired — fixed to print all problems on that path too.
  tightened leg B: the v1 exemption was scoped to "absent from record" but was
         applied to the OPEN side too, so STATE listing a v1 id as open (a
         dead route offered as a menu item) printed OK. It now diverges.

VALIDATION by real execution, fixtures deleted after (T-numbering per session):
T1 un-repaired real pair -> RC=1 naming OQ-022 AND OQ-024 with stubs (negative
control FIRST, before any repair); T2 v1 closed id removed from STATE -> RC=1
names it via leg E; T3 v1 id injected into STATE's open list -> RC=1 naming the
v1 block (pre-patch this printed OK); T4a duplicate CLOSED row appended -> RC=1
names the dupe; T4b duplicate WITHOUT status cell (the realistic wrap shape,
nost path) -> RC=1 and the dupe line still prints; T5 real repaired pair ->
LEDGER INDEX OK RC=0. STATE.md repaired with OQ-022/OQ-024 summaries copied
from the record; kept the file's YAML convention of exactly two quotes per
entry (first draft used raw '"' inside a double-quoted scalar — caught by
awk-counting quotes per line against HEAD's block, where every entry holds
exactly 2; reworded to item 33/34 instead of escaping).

TEST-HARNESS NOTE: one fixture silently failed to build because a heredoc-in-
execute_code swallowed its own quoting (the file never existed; the tool
correctly reported FileNotFoundError RC=1 for a MISSING file — do not read a
missing-fixture RC=1 as a passing divergence test). Rebuilt with a direct
pathlib one-liner and confirmed by grep before trusting the verdict.

BOUNDARY kept, not chased: ledger_audit's --expect stays a hand-maintained
duplicate (deriving it from the record is circular — t159). gate.sh stage 3t
runs BOTH ledger tools, so this fix is enforcement, not a suggestion (t158
grep law re-satisfied: gate.sh:421 invokes ledger_index_check.py).


## 55. t162 — the P0 grader (gate.sh stage 1) was one-directional: additions to game/ invisible, absent manifest silently re-blessed

t161's SET-PAIRS law applied to the grader protecting the project's top NEVER
("never modify game/"), which 161 iterations had never audited. Stage 1 in
source: sha256sum -c manifest, plus a regen-from-glob path when the manifest is
absent. Measured on a scratch copy under work/r1 (pristine game/ never touched):

- T0 control (23/23 match): silent.
- T1 DELETE a listed file: ARMED — sha256sum -c prints "FAILED open or read",
  grep finds the non-OK line. Covered direction.
- T2 ADD a foreign file (NOTES.TXT): ZERO signal. Nothing enumerates disk->set;
  the checksum loop only walks the manifest's own names.
- T3 ABSENT manifest: the gate ran `sha256sum * > MAN` itself, bless-ing the
  tampered tree (regenerated manifest held 24 entries incl. NOTES.TXT) — after
  one such run the tree passes forever. Self-healing grader = the tamper IS the
  baseline.
- Static: game/ is flat (0 dirs, 0 dotfiles, 0 nested, 0 unreadable); manifest
  set == disk set == 23 on the real tree (comm -3 empty); manifest git-tracked
  since seed 3792dc5 (revertable, but revertable != detected).

Fix (scripts/gate.sh stage 1): absence of docs/BASELINE.sha256 is now a hard
err with a restore-from-git instruction (never regen); added the second
direction — LC_ALL=C comm -3 of manifest names (awk substr($0,67), tolerant of
spaces) vs find game -maxdepth 1 -type f, any delta => err naming it. Five
branches validated by real execution on stage-1 code extracted verbatim from
the patched file (fixtures deleted): F0 silent flag 0; F1 ADD flags NOTES.TXT
only; F2 REMOVE fires BOTH legs; F3 absent-manifest errs with NO regen; F4
tampered manifest hash errs. Full gate green (exit 0, zero FAIL lines) with the
new leg running.

Fixture-harness traps banked (neither was a gate bug): (1) `err: command not
found` / RC=127 — sourcing extracted stage-1 code needs note()/err shims; my
first run's "RC_line_after=127" briefly read as a leg failure. (2) LC_ALL=C on
sort but NOT on comm: comm re-parses under the session collation, disagreed
with the C-sorted inputs, and dumped ALL 23 names as unpaired while the real
delta sat buried at the end — a grader whose own output is 23x noise is
functionally blind; the fix pins LC_ALL=C on comm itself.

LAW (fifth recursion t157/t158/t159/t160/t161 -> t162): audit the SAFETY
graders with the same SET-PAIRS question as the bookkeeping graders — for every
consistency check ask "which direction does it enumerate, and what happens to
the set members it cannot see". Modification-detection was tested for 161 turns
because it is the failure mode people imagine; ADDITION and baseline-destruction
were never imagined, so never tested.

## 56. t163 — IDLE re-check #50: the dosbox-launcher safety set was hand-listed (2 of 12)

Both triggers negative (probe RC=0, "IDLE — neither trigger", clean tree at
d806d3a at session start; ledger_index_check OK pre-edit). The iteration's
finding continues the t157..t162 grader-audit recursion, this time aimed at the
GOAL.txt:5 / BLOCKED.md:122-127 dosbox safety invariants — the graders for the
ONE rule the whole loop treats as top-critical ("never mount pristine game/",
"pkill -x only", "-time-limit always").

SET-PAIR MEASUREMENT (scripts/*.sh, comments stripped):
- {scripts that can launch dosbox} = 12 by the derived predicate "has a
  comment-stripped ^\s*I?MOUNT line": r1_adcapture, r1_attempt, r1_deepcapture,
  r1_mutation_run, r1_playcap, r1_playcap_vnc, r1_savestate, r1_t75_run,
  r1_t78b_panel, r1_t78c_cycle, r1_t78_size, ref_capture.
- {scripts gate.sh audits} = 2 by hand (gate.sh:208-215 r1_attempt.sh,
  :223-230 r1_savestate.sh). gate.sh:380's ref_capture.sh hit is a COMMENT
  (refcap provenance), not a leg. The ten unaudited launchers are exactly the
  ones earned later (t49..t85g) — the hand list was a copy of {the last file
  that broke}, never re-grown.
- The hand leg's FORM was also dead: `grep 'ascendancy/game'` cannot fire for
  10/12 launchers because the string appears nowhere in their code — they
  generate a dosbox conf whose only mount is `MOUNT C $SCRATCH` with
  SCRATCH="$ROOT/work/r1/game". The invariant was graded by the ABSENCE of a
  bad string instead of the PRESENCE of the good target. (Two .py files DO hold
  ascendancy/game — r1_t97c_le_debug.py:13, r1_t98_wlink.py:33 — both read-only
  'rb' reads of game/ascend.exe, which the rule never forbade; mounting does.)
- Current-state check: 11/12 launchers satisfy all three invariants on their
  own. r1_attempt.sh passes gate.sh:214's `grep 'time-limit'` ONLY because the
  word sits in a comment (its real bound is `timeout -s KILL 300` at
  r1_attempt.sh:56 and r1_tracer.py:94's -time-limit argv) — a comment word
  satisfying a bound check is exactly the t158 "regex IS the policy" shape.

FIX (gate.sh stage 3n2, static-only like 3n): derive the audit set each run
from the MOUNT predicate; err loudly if the predicate matches nothing (a leg
whose set is empty must scream, not pass — t159's empty-case law); per launcher
check pkill -f absence, EVERY MOUNT line targets $SCRATCH, SCRATCH= points under
work/, and a bound exists (-time-limit OR timeout -s KILL, accepting the tracer
route honestly instead of by comment). R1_SCRIPTS_DIR env-overridable for
fixtures. Belt-and-braces: the two hand legs stay (their messages are better);
3n2 is the superset.

VALIDATION by real execution on the leg code extracted VERBATIM from the patched
gate (sed -n '231,260p' -> /tmp/t163-leg.sh, sourced with note()/err shims per
the t162 trap), fixtures under /tmp/t163-fix, all deleted after: F1 clean
launcher RC=0; F2 MOUNT of pristine game/ ERR; F3 SCRATCH outside work/ ERR;
F4 pkill -f ERR; F5 no bound ERR; F6 empty dir ERR (inert-leg scream); F7
comment-only MOUNT correctly NOT counted as a launcher (inert-scream fires,
proving comment-stripping is load-bearing). Real gate: GATE_EXIT=0, zero FAIL
lines, "3n2: auditing 12 dosbox launcher(s)" at log line 7, ALL CHECKS PASS.
ledger_audit LEDGER AUDIT OK. One self-inflicted harness bug caught pre-run:
first draft of the fixture script DUPLICATED the leg code instead of sourcing it
(a copy drifts from the shipped leg — the exact failure family this section is
about); rewritten to source the extracted file.

LAW (sixth recursion t157->t163): {audited} must be DERIVED from the property
that makes a file dangerous, never hand-listed from memory of what broke — and
the check must assert the POSITIVE contract (mount target IS scratch under
work/) rather than the absence of one bad literal, because the literal's
presence was never what made a launcher safe. Enforcement per t158: 3n2 lives
inside gate.sh itself. NO ledger row closed (harness hardening, not
measurement).

## 57. t164 — IDLE re-check #51: both triggers negative (51st idle turn)

Session start 2026-10-28 06:16:47 EDT, clean tree at ac43aa4 (verdict wording
"IDLE — neither trigger" valid per t155/B5 — nothing edited before the probe
run).

TRIGGER A NEGATIVE — scripts/r1_idle_probe.py RC=0. Newest playcap dir
playcap-20261014-224611; live-timeline.jsonl mtime_ns 1793043841304000000 /
5691796463 B — byte-identical to the frozen baseline for the 53rd consecutive
reading (t111..t164); (A6) content-baseline leg satisfied; zero dosbox procs;
find sweep since 06:15:29 -> 4 files, non-loop none; A4 watcher ALIVE pid
27774; A5 none (save/*.sav = 20, all match the watcher glob).

TRIGGER B NEGATIVE — git diff HEAD empty; tracked porcelain empty; no
untracked paths at all (loop-owned or foreign); no STEERING file; B3 HEAD ==
journal sha ac43aa4 (no commits outside the loop); prompt pair prompt-86.txt
vs prompt-85.txt (58/58 lines) digit-stripped delta 0.

LEDGER — ledger_index_check.py LEDGER INDEX OK before any edit (record
rows=18 open=OQ-003/005/016/019/021/023 closed=12; STATE index mirrors it
exactly).

INFRA unchanged since t112 (Xvfb 1196 / x11vnc 1207 / watcher 27774;
x11vnc.log 2026-10-27 17:30:18 / 30114 B — zero connects).

HONEST NEGATIVE: no measurement, NO ledger row closed, no law falsified, no
harness change this turn (per the t113 idle law: an idle turn is the
two-trigger probe and nothing else — no watch, no census, no re-derivation of
probes). Bank hygiene: grep -rln stop-report scripts/ -> r1_idle_probe.py +
ledger_audit.py docstrings + gate.sh comment only (same set as t163); stop-report.md
was 2220 lines / 136735 B zero-diff vs HEAD before appending this section.
NEXT stays IDLE; the t113 LOOP-END PROPOSAL stands (51 idle turns).

## 58. t165 — IDLE re-check #52: both triggers negative (52nd idle turn)

Fresh session; ran scripts/r1_idle_probe.py BEFORE any edit per the t117 law.

TRIGGER A NEGATIVE — probe RC=0 at 06:22:36 on a clean tree at 2a53dd6
("IDLE — neither trigger" wording valid per t155/B5): newest playcap dir
playcap-20261014-224611; live-timeline.jsonl mtime_ns 1793043841304000000 /
5691796463 B — byte-identical to BASE_MTIME_NS/BASE_SIZE, (A6) content
baseline satisfied (54th consecutive identical reading t111..t165); zero
dosbox procs; find sweep since session start 06:21:37 -> 4 files, non-loop
none; A4 watcher ALIVE pid 27774; A5 none (save/*.sav = 20, all match the
watcher glob).

TRIGGER B NEGATIVE — git diff HEAD empty; tracked porcelain empty; no
untracked paths at all (loop-owned or foreign); no STEERING file; B3 HEAD ==
journal sha 2a53dd6 (no commits outside the loop); prompt pair prompt-87.txt
vs prompt-86.txt (58/58 lines) digit-stripped delta 0.

LEDGER — ledger_index_check.py LEDGER INDEX OK before any edit (record
rows=18 open=OQ-003/005/016/019/021/023 closed=12; STATE index mirrors it
exactly).

INFRA unchanged since t112 (Xvfb 1196 / x11vnc 1207 / watcher 27774;
x11vnc.log 2026-10-27 17:30:18 / 30114 B — zero connects).

HONEST NEGATIVE: no measurement, NO ledger row closed, no law falsified, no
harness change this turn (per the t113 idle law: an idle turn is the
two-trigger probe and nothing else — no watch, no census, no re-derivation of
probes). Bank hygiene: grep -rln stop-report scripts/ -> r1_idle_probe.py +
ledger_audit.py docstrings + gate.sh comment only (same set as t163/t164);
stop-report.md was 2253 lines / 138522 B zero-diff vs HEAD before appending
this section. NEXT stays IDLE; the t113 LOOP-END PROPOSAL stands (52 idle
turns).

## 59. t166 — IDLE re-check #53: both triggers negative (53rd idle turn)

Fresh session; ran scripts/r1_idle_probe.py BEFORE any edit per the t117 law.

TRIGGER A NEGATIVE — probe RC=0 at 06:30:16 on a clean tree at 488ea34
("IDLE — neither trigger" wording valid per t155/B5): newest playcap dir
playcap-20261014-224611; live-timeline.jsonl mtime_ns 1793043841304000000 /
5691796463 B — byte-identical to BASE_MTIME_NS/BASE_SIZE, (A6) content
baseline satisfied (55th consecutive identical reading t111..t166). Re-statted
INDEPENDENTLY of the probe this turn (`stat -c '%y %s'` -> 2026-10-26
15:44:01.304000000 -0400 / 5691796463) and the edge md5s re-derived by hand
(head 42a0bed0507f9052e2009ec94e9c27f1 / tail 1529ab1ad70ac360f441d819703f943f,
last row still {"file":"60.sav","turn":1254,...}) — 12th reproduction of the
t151 content baseline, matching edge_md5()'s own values exactly. Zero dosbox
procs; find sweep since session start 06:28:36 -> 4 files, non-loop none; A4
watcher ALIVE pid 27774; A5 none (save/*.sav = 20, all match the watcher glob).

TRIGGER B NEGATIVE — git diff HEAD --name-only empty; tracked porcelain empty;
no untracked paths at all (loop-owned or foreign); no STEERING file; B3 HEAD ==
journal sha 488ea34 (journal row 87, ct 06:27:43, OK, fail_streak 0 —
re-read independently from work/r1/loop/journal.tsv); prompt pair
prompt-88.txt vs prompt-87.txt (58/58 lines) digit-stripped delta 0.

LEDGER — ledger_index_check.py LEDGER INDEX OK before any edit (record
rows=18 open=OQ-003/005/016/019/021/023 closed=12; STATE index mirrors it
exactly). No OPEN-QUESTIONS row touched, so nothing to status-update this turn.

INFRA unchanged since t112 (Xvfb 1196 / x11vnc 1207 / watcher 27774;
x11vnc.log 2026-10-27 17:30:18 / 30114 B — zero connects). Transients 201171 /
201221 (harness supervisor + this session's probe child) per the t118 noise
law, correctly ignored.

HONEST NEGATIVE: no measurement, NO ledger row closed, no law falsified, no
harness change this turn (per the t113 idle law: an idle turn is the
two-trigger probe and nothing else — no watch, no census, no re-derivation of
probes). Bank hygiene re-checked fresh: grep -rln stop-report scripts/ ->
r1_idle_probe.py + ledger_audit.py docstrings + gate.sh:12 COMMENT only (same
set as t163/t164/t165 — no script writes this file); stop-report.md was 2287
lines / 140318 B zero-diff vs HEAD before appending this section. NEXT stays
IDLE; the t113 LOOP-END PROPOSAL stands (53 idle turns).
