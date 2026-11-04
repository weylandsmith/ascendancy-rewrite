# t186 WIP — trigger-B adjudication: the idle gate arms ITSELF every iteration

Session launched from prompt-108.txt (armed report r1_idle_probe @ 2026-10-28
21:25:04). Assignment per assignment-override rule: act on the armed trigger
(Trigger B, "user decision"), do not re-run the idle protocol.

## Trigger A (new capture): NEGATIVE, re-confirmed from the report only
live-timeline.jsonl mtime_ns/size identical to baseline baseline
(1793043841304000000 / 5691796463); no dosbox procs; newest playcap dir still
playcap-20261014-224611. Not re-probed (t178 IDLE RULE: never re-check for
new work). Nothing to ingest.

## Trigger B: the arm is a self-echo, MEASURED

Delta between the pair the probe compared (prompt-107 vs prompt-106), digit-
stripped, reproduced independently with difflib (2 content lines, both loop
prose):

  -  "  - HEAD: 46dd6ea t183: OQ-019 SCALE MEASURED ..."
  +  "  - HEAD: a239b27 t184: OQ-019 build/redesign inventory path CLOSED ..."
  -  "  - B3 HEAD == journal sha 46dd6ea: ..."
  +  "  - B3 HEAD == journal sha a239b27: ..."

Tree facts that make this decisive (measured this session, not inferred):
  - `git diff HEAD --name-only` EMPTY, `git status --porcelain` EMPTY, no
    untracked outside loop-owned paths, no docs/STEERING*, no LOOPSTEER.txt
    (report B1/B2 lines + re-verified).
  - Report line B3 verbatim: "B3 HEAD == journal sha 5aed299: no commits
    outside the loop since last iteration" — the probe's OWN cross-check says
    there is no user commit.
  - prompt file mtimes are one-per-loop-iteration
    (104 17:40:28, 105 18:14:04, 106 19:31:43, 107 20:24:39, 108 21:25:42).

## Root cause (code-cited)

1. scripts/loop_one_task.sh:135-143 builds each iteration prompt as
   CONTRACT + `cat $LOOPDIR/probe-last.log` + STEERING + INTERRUPTED note.
   So iteration N's prompt EMBEDS iteration N-1's probe report.
2. scripts/r1_idle_probe.py writes into that report:
   - :351 `git log --oneline -1` (HEAD subject = the loop's own last commit
     message prose),
   - :446-455 the "B3 HEAD == journal sha ..." line,
   - :511-519 the "prompt pair ... digit-stripped delta N line(s)" line.
3. :498 neutralises NUMBERS only (`re.sub(r"\d+","N")`). Commit subjects and
   the delta line are PROSE, so they survive digit-stripping.
4. :515-519 `if stripped: armed = True` — no filter for report-echo lines.

=> Every loop iteration commits, so HEAD's subject changes every iteration, so
the embedded report differs in prose every iteration, so B2 arms every
iteration FOREVER. The idle gate cannot idle: it is a feedback loop that
converts the loop's own commit message into a fake "user decision". Consistent
with the observed run: idle polls 100→108 all launched sessions.
Same class of noise arms on the loop-generated INTERRUPTED note (present/absent
between pairs — measured in the 107-pair scan).

## Fix shape (in progress)
Diff ONLY the human-authored regions of a prompt file: the CONTRACT segment
(before the IDLE-GATE marker) and the STEERING segment (from
"STEERING FOR THIS ITERATION" to before "INTERRUPTED PRIOR WORK DETECTED").
Report-echo region is loop noise and is excluded from the arm decision (still
printed as a count for visibility). Arm on steering-delta (the real route) and
on contract-delta (human-edited harness), never on report echo.
Regression requirement: replay all 107 historical prompt pairs; old-vs-new arm
decisions must show pairs 100-108 flipping ARMED -> IDLE, and must not lose
any pair that historically carried a real LOOPSTEER section.

## Next-task note (for STATE.md)
The decision surface the user owes is already on disk and needs no new build:
work/r1/shp_png/index.txt (OQ-005 eyeball packet, 15 RENDERED/VALIDATED PNGs +
65 DECODE-FAIL rows, law snapshot V197/A1289/FAIL71) and docs/re/stop-report.md
§3 (accept/reject documented defaults OQ-003/OQ-005/OQ-019/OQ-023; authorize a
capture sitting; resume t89a code work). Ledger as measured by
scripts/ledger_index_check.py this session: 18 rows, open = OQ-005, OQ-016,
OQ-019, OQ-021, OQ-023; LEDGER INDEX OK.
