# t389 WIP — PHASE-10 VERIFY + RE-EXPORT + PUSH (session 2026-11-14)

Task (docs/STATE.md NEXT ACTION, queue row t389 VERBATIM):
  1. Full gate + run_tests (expect prior 293, 0 failed)
  2. headless --campaign seed regression: seeds 1/2024/23 headless logs stay
     byte-identical (engine untouched rule; UI rows must not move sim rng)
  3. Fresh export via scripts/publish_public.sh GITHUB_USER=weylandsmith;
     verify vendor-free + build + tests WITHOUT data + identity
  4. Push (fast-forward expected; FETCH FIRST per law; lease-pin if force needed)
  5. Rewrite NEXT to WAIT-USER-RULING t374 verbatim (TAG LAW: field 2 WAIT*,
     never renumber) with pointer that phase-10 landed + what user screenshots
     would grade (title art candidates t386; SOUND check per t388b).

## Probes

F0 (steering pre-check). work/r1/playcap/live-timeline.jsonl mtime
   2026-11-14? NO: `ls -la` = 9385663364 bytes, mtime **Nov 12 06:45**; today is
   2026-11-14 17:28 EST and the last LANDED block is t388b (2026-11-14T19:40
   header stamp). No new sitting since the last iteration -> the assigned
   assignment stands; scripts/r1_t85g_sitting.py NOT run.
   Tree at session start: `git status --short` EMPTY (clean), HEAD c877e40.

F1 (suite). `cmake --build rewrite/build -j4` clean (ascend_core, ascend_ui,
   ascendancy, run_tests all Built); `./run_tests` -> "293 tests, 0 skipped,
   0 failed" — matches the t389 key-fact (289 prior + 4 audio pins).

F2 (SEED REGRESSION — the row's engine-untouched proof). No golden seed logs
   existed on disk (searched work/, scripts/, docs: only the t365 narrative in
   docs/re/engine-flip-t365.md L28-30 names the law: seeds 1/2024/23
   headless-1600 byte-identical, Extinct t266 / Extinct t285 / Control t1406).
   Built a REAL baseline: `git worktree add /tmp/t389-baseline c7a3fda` (the
   last commit BEFORE phase 10 — 7e6507c t385 is the first UI row), cmake with
   CMAKE_BUILD_TYPE EMPTY to match the working repo's cache (first attempt used
   Release — rebuild required for a fair byte-compare). Runs
   `ascendancy --headless --campaign 1600 --seed S` both sides:
     seed 1    base md5 7e794a6dfb495800502762def9331e85 == head (VICTORY
               Extinct via end-xtnc.txt t266)
     seed 2024 base md5 332a8cf3cebc95359924ce6a6b94a830 == head (Extinct t285)
     seed 23   base md5 0a6b7876719f38796e8235cb772a43d3 == head (Control t1406,
               score 68%)
   `diff -q` clean all three. Phase-10 UI/audio rows moved ZERO sim rng; the
   victories also independently reproduce the t365 banked record. Baseline
   worktree REMOVED at end of session (git worktree remove).
   NOTE for future rows: the working repo's rewrite/build cache has
   CMAKE_BUILD_TYPE=STRING= (empty); any byte-compare harness must match it.

F3 (export). GITHUB_USER=weylandsmith publish_public.sh /tmp/pubpush-t389
   exit 0: 6298 objects, 5.6M .git, tree intact; vendor dirs absent; identity
   uniform (single noreply email across --all). No-data clone build: cmake
   (empty build type) + build -j4 exit 0 ZERO warnings, ascend_ui built
   (key-fact 1 confirmed on the export); run_tests "293 tests, 196 skipped,
   0 failed"; ASCENDANCY_DATA=<repo> gate --portable exit 0.

F4 (push). FETCH-FIRST: first fetch revealed the export's origin == the LOCAL
   SRC path (clone default) — set-url to the GitHub URL first (TRAP banked
   packaging.md). Remote tip b2539b3; merge-base --is-ancestor => FF OK;
   push b2539b3..36bf92d; ls-remote main == 36bf92dbb4bdf12d. Helper deleted.

F5 (landing). packaging.md t389 block appended; STATE NEXT re-parked
   WAIT-USER-RULING t374 (tag law) with grading pointer; LANDED t389 block
   written. No OQ row moved (strict-close honest negative: verify+push is not
   a measurement). Gate + audits below.
