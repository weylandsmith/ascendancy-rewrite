# t145 WIP — IDLE re-check #32 + probe coverage-hole fix

Session start 2026-10-28 00:44:23 EDT (cutoff the probe used: 00:43:18, from the
iter-*.log name per the t117 law). HEAD at session start: de16f04 (t144).

## 1. Trigger (A) NEGATIVE
`python3 scripts/r1_idle_probe.py` RC=0 at 00:44:23:
- newest playcap dir `playcap-20261014-224611`
- `work/r1/playcap/live-timeline.jsonl` mtime_ns 1793043841304000000 /
  size 5691796463 — thirty-fifth consecutive byte-identical reading
  (t111..t145)
- zero dosbox processes
- `find work/r1 -newermt 00:43:18` -> 4 files, non-loop: none
`r1_t85g_sitting.py` correctly NOT run.

## 2. Trigger (B) NEGATIVE (measured by content)
- `git diff HEAD --name-only` empty; `git status --porcelain` empty (no untracked)
- no STEERING file (`ls docs/STEERING* STEERING*` -> none)
- natural-sorted prompt pair prompt-67.txt vs prompt-66.txt, both 58 lines,
  digit-stripped `diff -u` = 0 lines; `grep -in steering` hits only standing
  instruction line 14.
- no delta outside loop-owned paths.

## 3. FINDING: t144's "the tool is immune" claim is FALSE — coverage hole in (B)
t144 banked: "`r1_idle_probe.py:82-84` picks the prompt by mtime so the tool was
never exposed [to the lexical-ordering trap]" and NEXT ACTION tells future turns
"RUN THE TOOL, DO NOT RE-DERIVE THE PROBES." The citation is right, the
conclusion is wrong, and the reason matters:

`grep -n prompt scripts/r1_idle_probe.py` -> 65, 69, 82, 84 only. Lines 82-84 are
the FALLBACK session-start cutoff (used only when no `iter-*.log` name is
parseable). The tool's actual steering check is

    scripts/r1_idle_probe.py:130-133
        steer = sh("ls docs/STEERING* STEERING* 2>/dev/null").strip()
        reasons.append("STEERING file: %s" % (steer or "none"))
        if steer: armed = True

i.e. a file-EXISTENCE glob on two paths. The tool NEVER diffs prompt contents.
Consequence: the steering mechanism this loop actually uses — the harness
prepending a note to `work/r1/loop/prompt-<n>.txt`, which is what both the loop
contract ("or the steering note, if the harness prepended one") and STATE.md
NEXT ACTION §(B) name as the signal — CANNOT arm trigger (B). Only the hand
procedure (natural-sorted digit-stripped prompt diff) covers that route, and the
NEXT ACTION block actively discourages running it. So for thirty-one idle turns
the (B) verdict has been carried by a probe that is blind to one of the two
documented (B) inputs, while the hand check that does cover it has been
discouraged. Silent in both directions: the tool reports "STEERING file: none"
(which reads as a clean verdict) whether or not the prompt changed.

FIX (this iteration, minimal): add a prompt-content-delta leg to `trigger_b()` —
natural/numeric sort of `prompt-*.txt`, compare newest vs previous with digits
stripped, arm on non-empty delta, print the pair and delta size so the verdict is
auditable. No change to trigger (A) or to the frozen baseline.

## 4. FINDING: commit-subject bloat is an idle-turn tax
Subject lengths, newest last, over the last 25 commits:
806 913 916 994 920 919 800 921 920 938 944 940 941 940 933 983 991 1011 1134
1049 1046 1097 1113 1065 1310
`trigger_b()` prints `"HEAD: %s" % git log --oneline -1`, so every idle turn pays
~1.3k chars of context to read the previous iteration's full subject, and the
figure grows monotonically because each subject summarises the last. FIX: print
the short SHA + first 120 chars of the subject only (the full text is already in
STATE.md's LANDED block, which is where a successor actually reads it).

## 5. Ledger state (untouched by this iteration)
`python3 scripts/ledger_audit.py` -> `rows=18 open=['OQ-003','OQ-005','OQ-016',
'OQ-019','OQ-021','OQ-023'] closed=12 / LEDGER AUDIT OK`. No row closed: an idle
turn produces no cited measurement, and strict-close forbids otherwise.

## 6. Infra
Xvfb :9 pid 1196, x11vnc :5910 pid 1207, watcher pid 27774 — unchanged since
t112; `work/r1/vnc/x11vnc.log` mtime 2026-10-27 17:30:18 / size 30114 (zero
connects). Transients 158952 (harness `mcp_death_supervisor.py --parent-pgid
158932`, via `ps -o args=`) per the t118 noise law — ignored.

## 7. Bank hygiene (checked before appending §38)
`grep -rln stop-report scripts/` -> only `r1_idle_probe.py` + its `__pycache__`
bytecode; `git diff HEAD --stat -- docs/re/stop-report.md` empty at 1117 lines
(= §37's committed total). Hand-authoring safe, no regeneration trap.
