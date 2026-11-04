# t155 WIP — IDLE re-check #42

Session start 2026-10-28 03:16:34 EDT. Task: STATE.md IDLE block = run
`python3 scripts/r1_idle_probe.py` and nothing else (no watch, no census).

## 1. Trigger measurements (real tool output)

`python3 scripts/r1_idle_probe.py` RC=0 at 03:16:34 (cutoff 03:14:49):
- (A) NEGATIVE — newest playcap dir playcap-20261014-224611; live-timeline.jsonl
  mtime_ns 1793043841304000000 / 5691796463 B; zero dosbox procs; find sweep 4
  files, non-loop none; A4 watcher ALIVE pid 27774; A5 none (save/*.sav = 20).
- (B) NEGATIVE — clean tracked tree at f0e9527, no STEERING, B3 HEAD == journal
  sha f0e9527, prompt pair prompt-77 vs prompt-76 (58/58) digit-stripped delta 0.

Independent re-verification (t147/t148 law — resolve constants from source,
re-stat outside the probe):
- `stat -c '%Y %y %s'` = 1793043841 / 2026-10-26 15:44:01.304000000 -0400 /
  5691796463 == BASE_MTIME_NS/BASE_SIZE at r1_idle_probe.py:55-56. 45th
  consecutive byte-identical reading t111..t155.
- t151 content baseline reproduced a FOURTH time: head 64 KiB md5
  42a0bed0507f9052e2009ec94e9c27f1, tail 1529ab1ad70ac360f441d819703f943f; last
  row still the t1254 row (file_mtime_ns 1793043836296000000, wall 15:44:01).
- journal last row's last tab field first token = f0e9527 == HEAD (re-extracted
  by `rev | cut -f1 | rev`, not via the probe).
- Prompt enumeration done BY HAND with `ls -1v` (t144 law): pair prompt-76 /
  prompt-77, digit-stripped diff 0 lines.
- r1_playcap_watch.py:161 is still the lowercase `save/*.sav` glob;
  r1_idle_probe.py:191 A5 still walks `os.path.dirname(TIMELINE)`.
- Bank hygiene fresh: `grep -rln stop-report scripts/` -> only
  scripts/r1_idle_probe.py + its .pyc; gate.sh has no stop-report write.

## 2. THE FINDING — the most likely §3 answer route is demoted by design

t145 method = ask what a leg DOES with its input, not whether it reads it.

`trigger_b()` (r1_idle_probe.py:276-290) demotes EVERY tracked delta under
LOOP_OWNED to "CAUTION" and keeps the verdict NEGATIVE / RC=0. LOOP_OWNED
(:59-60) contains `docs/OPEN-QUESTIONS.md` and `docs/BLOCKED.md`.

Consequence: a user answering §3 by editing the ledger itself — typing
"OQ-005 accepted" into docs/OPEN-QUESTIONS.md, which is the most natural place
for that answer and the file stop-report §3 names — moves no leg to ARMED. The
RC=0 verdict line and the buried CAUTION line contradict each other, and the
NEXT ACTION block quotes RC ("RC=0 both negative (stay IDLE)"), so the verdict
dominates the caution.

Measured context for the fix (real, this session):
- Prompt corpus: 77 files, only 3 distinct digit-stripped bodies
  (41 lines x15, 63 lines x3, 58 lines x59). So B2's newest-pair comparison is
  not exposed to multi-shape drift; the prompt route is genuinely covered.
- A5's scope (shared dir only) is NOT a new hole: a per-run capture always
  creates work/r1/playcap-<ts>/, which arms (A) leg 1 (r1_idle_probe.py:74)
  regardless of A5. Confirmed in source: r1_playcap.sh:22 pins
  OUT=$ROOT/work/r1/playcap-<ts>; r1_playcap_vnc.sh:30 pins
  OUT=$ROOT/work/r1/playcap. Both launch paths are inside the (A) find sweep.

Fix decision (NOT yet applied): make the uncommitted-decision-file case change
the printed VERDICT line (escalate its visibility) without arming — arming with
RC=1 would violate t117 ("only an observed user event arms"), because
crash-residue (an iteration that edited STATE/ledger and died before committing)
produces the identical file state and cannot be distinguished from a user edit
by mtime: a user answer typed after the last commit is NEWER than HEAD, and so
is crash residue. Time cannot separate them; that whole discriminator was
considered and rejected.

## 3. SECOND MEASUREMENT — a real blind surface, banked as an accepted boundary

`work/` is listed in LOOP_OWNED, but:
- `git ls-files work/` is EMPTY (nothing under work/ has ever been tracked);
- `.gitignore` contains `work/`, so `git status --porcelain` (any -u setting)
  never lists a path under work/.
Therefore LOOP_OWNED's `work/` entry contributes NOTHING to B1 (tracked diff),
B3 (committed diff — same reason) or B4 (untracked). The only leg that sees
anything under work/ is the (A) find sweep, and it is scoped to `work/r1`.

Net blind surface = **modified or new files under work/ OUTSIDE work/r1** (e.g.
work/t52_s15_append.md, work/attribution.tsv): no leg moves. Judgement: accept,
do not chase. Rationale — (1) the loop's documented answer routes are docs/
(stop-report §3), the repo root and rewrite/ (B1/B3/B4 all cover them; verified
.gitignore has no catch-all that would hide a root-level ANSWER.md); (2)
r1_playcap.sh:95 points the user at $OUT == work/r1/playcap-<ts>, which the
sweep covers; (3) extending the sweep to all of work/ would arm trigger (A) on
analyzer scratch, which is the t149 self-inflicted-false-positive shape.
`t52_s15_append.md`-style files are loop scratch the user has no reason to edit;
if they ever do, the answer is also useless to the loop unless it lands in docs/.
