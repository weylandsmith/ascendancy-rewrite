# t163 WIP — IDLE re-check #50

Session start 2026-10-28 05:53:28. HEAD d806d3a (t162), clean tracked tree.

## Trigger adjudication (run BEFORE any edit)
`python3 scripts/r1_idle_probe.py` RC=0 => VERDICT "IDLE — neither trigger".
 (A) NEGATIVE: newest playcap dir playcap-20261014-224611; live-timeline.jsonl
 mtime_ns 1793043841304000000 / 5691796463 B (baseline-equal); zero dosbox procs;
 find sweep since 05:51:47 -> 4 files, non-loop none; A4 watcher ALIVE pid 27774;
 A5 none (save/*.sav = 20, all match the watcher glob).
 (A6) content baseline: printed as equal by the probe (leg inside trigger_a).
 (B) NEGATIVE: diff HEAD --name-only empty; status --porcelain empty; untracked
 none (loop-owned and foreign); STEERING none; B3 HEAD == journal sha d806d3a;
 prompt pair prompt-85 vs prompt-84 (58/58) digit-stripped delta 0.
`python3 scripts/ledger_index_check.py` -> LEDGER INDEX OK before any edit
 (record rows=18 open=OQ-003/005/016/019/021/023 closed=12; index identical).

## Iteration target (chosen per the t157..t162 recursion, static-only, live
capture untouched): the dosbox launch SAFETY invariants in docs/GOAL.txt:5 /
docs/BLOCKED.md:122-127 are graded by gate.sh legs that name scripts by hand.
Set-pair question: {scripts that can launch dosbox} vs {scripts gate.sh audits}.

## RESULT (complete — full write-up docs/re/stop-report.md §56)
Derived set = 12 scripts/*.sh with a comment-stripped `I?MOUNT` line; hand-audited
set = 2 (gate.sh:208-215 r1_attempt.sh, :223-230 r1_savestate.sh; the :380
ref_capture.sh hit is a comment). Ten launchers earned after the hand list were
frozen are unaudited, and the leg's FORM was dead anyway: `grep ascendancy/game`
cannot fire for 10/12 (the string is absent; they mount `MOUNT C $SCRATCH` from a
generated conf). r1_attempt.sh passes its bound check only via a COMMENT word.
FIX: gate.sh stage 3n2 derives the set each run from the MOUNT predicate and
asserts the POSITIVE contract per launcher (pkill -f absent; every MOUNT line
targets $SCRATCH; SCRATCH under work/; a bound = -time-limit or timeout -s KILL),
erroring loudly if the predicate matches nothing.
Validation: 7 fixture branches on the VERBATIM-extracted leg (F1 clean RC=0,
F2 pristine mount, F3 scratch-outside-work, F4 pkill -f, F5 no bound, F6 empty set
inert-scream, F7 comment-only MOUNT not a launcher), fixtures deleted; real gate
GATE_EXIT=0 zero FAIL lines, "3n2: auditing 12 dosbox launcher(s)"; ledger_audit
LEDGER AUDIT OK. No ledger row closed (harness hardening, not measurement).
