# t413 WIP — PHASE-14 VERIFY + PUSH + HANDOFF (started 2026-11-16)

## Assignment (STATE.md:233 + queue row STATE.md:1284)
Full gate + run_tests + seed regression (seeds 1/2024/23 byte-identical);
export via scripts/publish_public.sh GITHUB_USER=weylandsmith; verify
vendor-free + build WITHOUT data + tests WITHOUT data; fetch FIRST; push;
ls-remote verify; rewrite NEXT to WAIT-USER-RULING t374 verbatim with a
WALKTHROUGH TABLE (per screen, own-grade before/after, what user re-checks
live); rebuild :8613 sheet to the D14 asks (scripts/t403_grading_page.py
pattern; t397b server hardening stays).

## Pre-flight facts (measured this session)
- live-timeline.jsonl mtime 2026-11-12 06:45:50 — NO new sitting since last
  iteration -> r1_t85g_sitting.py correctly NOT re-run.
- HEAD at session start: 39a6546 (t412), tree clean.
- `git remote -v` in the WORKING repo: EMPTY (t389 trap family — the canonical
  remote URL must come from docs; export clone's origin defaults to the local
  SRC path — set-url BEFORE deciding fetch, per t403 note).
- Last pushed remote tip (t403): 06da9b2fa8a4dc1a5e21838def2964a85b2ec262.
  Push-gap law: every phase MUST push; gap since t403 push = t404..t412
  commits unpushed -> this row is load-bearing.
- Seed md5 record (t411/t403): 7e794a6d / 332a8cf3 / 0a6b7876 (seeds 1/2024/23,
  `--headless --campaign 1600`).

## F1 — canonical remote URL [VERIFIED]
https://github.com/weylandsmith/ascendancy-rewrite.git
(cited docs/re/packaging.md:253,276 + STATE.md:899,1469; working repo has NO
remote configured — push runs FROM THE EXPORT CLONE per t403 flow: set-url
origin BEFORE fetch, fetch-first law, force-with-lease against fetched tip.)

## F2 — verification battery [MEASURED 2026-11-16]
- Build: cmake --build rewrite/build -j4 clean (targets up to date).
- run_tests: **401 tests, 0 skipped, 0 failed** (== t412 record).
- SEED REGRESSION (`ascendancy --headless --campaign 1600 --seed S`, HEAD
  39a6546):
    seed 1    md5 7e794a6dfb495800502762def9331e85  VICTORY Extinct t266
    seed 2024 md5 332a8cf3cebc95359924ce6a6b94a830  VICTORY Extinct t285
    seed 23   md5 0a6b7876719f38796e8235cb772a43d3  VICTORY Control t1406 (68%)
  ALL THREE EXACTLY the banked record (t389 full md5s, docs/re/_wip_t389.md
  F2) — phases 13/14 (t404-t412) moved ZERO sim rng. Full md5s re-pinned here
  so future rows don't need the 8-char reconstruction.

## F3 — export + data-optional battery [MEASURED]
- `rm -rf /tmp/pubpush-t413 && GITHUB_USER=weylandsmith bash
  scripts/publish_public.sh /tmp/pubpush-t413` exit 0: "OK: vendor-free
  history, 6889 objects, 6.1M .git, tree intact." Export tip c178a43 (== t412
  39a6546's public twin). Identity uniform: single
  weylandsmith@users.noreply.github.com across --all.
- Build WITHOUT data (empty CMAKE_BUILD_TYPE per t389 law): exit 0, but TWO
  -Wsign-compare warnings in rewrite/tests/test_statuslist_t402.cpp:201,226
  (vector<size_type> vs int). t403 recorded ZERO warnings -> small regression
  introduced t404-t412 era. NOT fixed mid-verify (export tree must equal
  verified tree); carried as a t414 hygiene item. Harmless (tests pass) but
  the 0-warning law needs the fix.
- run_tests WITHOUT data: 401 tests / 241 skipped / 0 failed, exit 0
  (data-optional law HOLDS — no REQUIRE_DATA crash class this round).
- gate --portable on the export: ALL CHECKS PASS exit 0.

## F4 — push + ls-remote [MEASURED]
- Credential route: ~/.config/gh-pub-token (PAT, mode 600) via throwaway
  GIT_ASKPASS /tmp/t413_askpass.sh (t389/t396 pattern).
- FETCH-FIRST law honoured: `set-url origin <github>` was run BEFORE the
  first fetch, so the deciding fetch went straight to GitHub (t389 trap
  AVOIDED, not re-hit). The fetch's "+ c178a43...06da9b2 (forced update)"
  line is the clone-inherited origin/main (local-SRC tip) being replaced by
  the REAL remote tip — expected, since the clone defaulted origin to SRC.
- Remote tip 06da9b2fa8a4 (== t403 push; `git log origin/main --not main`
  empty => zero foreign commits); merge-base --is-ancestor => FAST_FORWARD_OK.
- `git push --force-with-lease=main:06da9b2...` landed **06da9b2..c178a43**.
- POST-PUSH `git ls-remote origin main` == **c178a43c1f7186c87d2c542afc6bd177
  20867a60** (verified, not self-reported). Gap closed: t404..t412 (9 commits)
  now public.
- Askpass helper deleted (verified absent: ls /tmp/*askpass* -> no match).

## F5 — handoff / sheet [MEASURED]
- Witness shots promoted /tmp/t40{6,7,9}_shots + t410 -> work/r1/loop/
  (planet-view, project-list, fleet-rows, species-menu, ability-open,
  sys-open, planet-open).
- scripts/t413_grading_page.py (tracked, t403 pattern): builds index.html +
  20 crops d11/t414-*.png; crop boxes from a t403_sheet_inventory run
  (crop-by-measurement law). Non-flat census: 17/20 OK; 3 flagged (intro
  crops 2-colour, sys-orbits 3-colour) — NATIVE VISION verified the flagged
  ones are LIVE content ("Supreme Planet Invaders" heading + red Minion body
  legible; orbit rings + spokes visible), not dead frames. JS bug found+fixed
  pre-ship (notes-id split index 2->1).
- Self-test on SCRATCH port 8699 + SCRATCH DECISIONS (real file never a test
  target): GET 200, POST -> "USER: D14 q3 system-view = ok | notes: ..." +
  q8 audio lines land correctly, traversal 404. Scratch server killed.
- :8613 LIVE immediately without restart (serves ROOT/index.html — t403
  fact): GET 200 with 'D14' x10, crop GET 200.
- D14 ask block appended to docs/DECISIONS.md (pointer to sheet + STATE
  walkthrough table).

## Ledger
NOTHING closed (strict-close: verify+push+sheet ships no measurement; OQ-016/
019/027 unchanged — 17 closed / 3 open).
