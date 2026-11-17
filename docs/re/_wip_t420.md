# t420 — PHASE-15 VERIFY + PUSH + HANDOFF (working log, 2026-11-17)

Scope (STATE.md NEXT ACTION + queue row :1575): full gate + run_tests + seed
regression byte-identical; export; fetch FIRST; push; ls-verify ONLY; then
rewrite NEXT ACTION to WAIT-USER-RULING + the D16 sheet on :8613.

## F0 Pre-flight
- HEAD at start: 08adbe1 (t419). Tree clean. No new sitting:
  work/r1/playcap/live-timeline.jsonl mtime Nov 12 06:45 (unchanged since
  t397's audit) -> r1_t85g_sitting.py correctly NOT re-run.
- Remote tip per record: c178a43c1f71 (t413 push). t414..t419 are LOCAL-only
  commits -> this iteration owns closing a 6-commit gap.
- Page server :8613 LISTENING (python3 pid 646702) — health check per WAKE
  PROCEDURE passed, no restart needed.
- publish_public.sh exists and is the canonical history-rewriting exporter
  (REFUSES an existing OUT dir; clone-then-filter-branch; game/ extracted/
  work/ archive/user-saves docs/assets scratchpad + the two vendor-EXE
  derivatives removed per commit; ISP scrub passes P1/P2 + fail-closed scan).

## F1 Verification
- GATE_EXIT=0 ("ALL CHECKS PASS (milestone=6)"), /tmp/t420-gate.log.
- run_tests inside gate: 421/0/0 (t419 record).
- SEED REGRESSION (`rewrite/build/ascendancy --headless --campaign 1600
  --seed S`, HEAD 08adbe1):
    seed 1    md5 7e794a6dfb495800502762def9331e85  VICTORY Extinct t266
    seed 2024 md5 332a8cf3cebc95359924ce6a6b94a830  VICTORY Extinct t285
    seed 23   md5 0a6b7876719f38796e8235cb772a43d3  VICTORY Control t1406 (68%)
  ALL THREE EXACTLY the banked record (_wip_t413 F2) — phase 15
  (t414..t419b) moved ZERO sim rng. Logs /tmp/t420-seed-{1,2024,23}.log.

## F2 — export + data-optional battery
- `rm -rf /tmp/pubpush-t420 && GITHUB_USER=weylandsmith bash
  scripts/publish_public.sh /tmp/pubpush-t420` exit 0: vendor-free history
  7080 objects, 6.5M .git, tree intact.
- Fresh cmake build WITHOUT data: exit 0, ZERO warnings (grep -ci warning
  over the full build log = 0) — the t413 carried hygiene note is CLOSED
  (8877e8c fixed the sign-compare pair).
- run_tests WITHOUT data: 421 tests / 245 skipped / 0 failed (data-optional
  law HOLDS). gate --portable exit 0.

## F3 — push [VERIFIED]
- Working repo has NO origin (law): remote add from
  docs/re/packaging.md:253 URL, set-url-style BEFORE the deciding fetch.
- Fetch: tip c178a43c1f7186c87d2c542afc6bd17720867a60 (== t413 record; zero
  foreign commits — `git log c178a43..main` is exactly the t413..t419b run,
  17 commits incl. the two t419b-withdrawal commits ae76a1b/a38b9f8).
- merge-base --is-ancestor c178a43 main -> FAST_FORWARD_OK.
- Askpass: t413's helper was deleted per policy; ~/.config/gh-pub-token
  (93 B) persists. Recreated /tmp/t420-askpass.sh (chmod 700, reads the
  token file, never embeds it), pushed
  `--force-with-lease=main:c178a43c...` -> c178a43..9692126 landed.
- POST-PUSH ls-remote refs/heads/main == 96921269e9267d601711a9591834e2ffa2e075ed.
- Askpass DELETED, verified absent (ls: No such file).

## F4 — D16 sheet
- shots: t419 witness frames banked /tmp/t419_shots/*.png -> work/r1/loop/
  (research-open/spin1/spin2/scrolldn/stopped/corner-topleft).
- Inventory run (scripts/t403_sheet_inventory.py, PIL python): 8 frames
  graded, all bg/mass/bands recorded in the generator docstring; md5 check
  proves the 9 sheet sources DISTINCT (t418b open vs tile differ;
  research-stopped == research-spin2 md5, so the sheet uses open/spin1/
  scrolldn — three distinct frames).
- scripts/t420_grading_page.py authored (t413 pattern): 18 crops, 9 ask
  rows q0..q8 covering EVERY D15 item + carried audio q8 with a "skip
  audio" off-ramp. POST shape re-keyed to the server's REAL contract
  (/ruling, JSON {title,fields:[[label,value]]}) after reading
  work/r1/d1page/server.py do_POST — NOT guessed.
- Self-test on SCRATCH port 8699 + SCRATCH decisions file: GET / 200, GET
  crop 200, POST -> "Ruling recorded", scratch file holds
  `USER: D16 q0 = ok | notes: selftest`. Scratch server killed by pid from
  ss (pkill -f pattern matched nothing — banked).
- Live :8613 (untouched pid 646702): GET / contains D16 x4, crop 200 — the
  server serves ROOT/index.html so no restart (t403 fact re-verified).

## F5 — ledger
- OPEN-QUESTIONS untouched: verify+push+sheet ships no measurement —
  LEDGER AUDIT OK, index check OK, 17 closed / 3 open.
- NEXT re-parked as WAIT-USER-RULING t374 with the live re-check list +
  the honest-negative audit that the machine-closable queue is EMPTY (all
  remaining seams need live-vendor witnesses).

