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
