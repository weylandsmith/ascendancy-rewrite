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
