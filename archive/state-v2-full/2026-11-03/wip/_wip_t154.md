# t154 WIP — IDLE re-check #41 (session started 2026-10-28 03:05 EDT)

STATUS: in progress. Both triggers measured NEGATIVE at probe run.

## Measurements (raw, this iteration)
- session start cutoff: iter log name stamp -> probe used 2026-10-28 03:05:19
- probe run 2026-10-28 03:06:14, RC=0, verdict IDLE.
- (A) newest playcap dir playcap-20261014-224611 (unchanged).
- (A) timeline stat independent re-stat: mtime 2026-10-26 15:44:01.304000000
  -0400 (=1793043841304000000 ns), size 5691796463 B — EQUAL to
  BASE_MTIME_NS/BASE_SIZE re-read from source r1_idle_probe.py:55-56.
  44th consecutive byte-identical reading (t111..t154).
- (A) content signature: head64K md5 42a0bed0507f9052e2009ec94e9c27f1,
  tail64K md5 1529ab1ad70ac360f441d819703f943f — 3rd byte-identical
  reproduction of the t151 baseline. Last line still the t1254 row
  ("file":"60.sav","turn":1254...,"wall":"15:44:01").
- (A) dosbox procs: 0 (ps -eo comm | grep -c '^dosbox').
- (A) find sweep non-loop: none. A4 watcher ALIVE pid 27774.
  A5 none (save/*.sav = 20, all match watcher glob).
- (B) HEAD d62b1f3; git diff HEAD --name-only empty; porcelain tracked empty;
  untracked loop-owned none; foreign untracked none (B4 leg clean on real
  state); delta outside loop-owned none; STEERING none;
  B3 HEAD == journal last-field sha d62b1f3 (independently re-checked via
  tail -1 work/r1/loop/journal.tsv | awk -F'\t' '{print $NF}');
  prompt pair prompt-76.txt vs prompt-75.txt (58/58) digit-stripped delta 0.
- Infra: Xvfb 1196 / x11vnc 1207 / watcher 27774 unchanged since t112;
  x11vnc.log 2026-10-27 17:30:18 / 30114 — zero connects.

## Probe-source re-verification (t145 method: what the leg DOES, not whether it reads)
- LOOP_OWNED (r1_idle_probe.py:59-60) = docs/STATE.md, OPEN-QUESTIONS,
  BLOCKED, docs/re/, scripts/r1_idle_probe.py, work/.
- (A) find-sweep filter (lines ~118-124): excludes work/r1/loop/ prefix and
  TOOL_ARTIFACTS only — NOT LOOP_OWNED wholesale, so a foreign file under
  work/r1 still arms (A) while (B4) owns the rest of the tree: the t153
  division of labour holds in source, not just in behaviour.
- B4 ownership split at lines 259/277 (own_untracked vs foreign).
- B2 numeric sort at lines 361-364 (int() key) per t144 law.
- Regeneration check for the bank file: grep -rln stop-report scripts/ ->
  only r1_idle_probe.py (+ .pyc); gate.sh has no touch/write of docs/re.

## Ledger
- No row touched this iteration. Strict-close: honest negative, §3 answers
  (OQ-003 entropy, OQ-005 dims, OQ-019 sugar-cube, OQ-023 threshold branch,
  capture authorization, t89a follow-on) still outstanding after 41 idle turns.
