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
