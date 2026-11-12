# WIP t383 — RE-EXPORT + VERIFY + PARK FOR PUSH

## S0. Trigger + sitting check (09:07 EST 2026-11-12)
- Assignment: STATE.md NEXT ACTION = queue row t383 (last row), verbatim:
  re-run scripts/publish_public.sh into a FRESH dir (tree moved since
  /tmp/pubpush), verify on clone shapes: vendor-free history (script gate),
  build + run_tests (expect 270 tests, 187+ skipped, 0 failed WITHOUT data —
  recount from a fresh run_tests output line), author identity single
  (weylandsmith@users.noreply.github.com, zero [ISP-DOMAIN] emails),
  GITHUB_USER=weylandsmith set. Then rewrite NEXT to sentinel
  'NEXT WAIT-PUSH-USER t383 — ...' (TAG LAW: field 2 WAIT*, never renumber).
- Sitting check RING-FIRST: scripts/t368_ring_turn.py parsed=20/20
  max_turn=1254 == same sitting as t380..t382. NO new play. timeline
  9,385,663,364 B mtime Nov 12 06:45; ring mtimes 09:05-09:07 all turn=1254
  = rotation. Production dosbox-x pid 107664 up 1d21h. Assignment stands.
- Tree at start: git status --porcelain EMPTY, HEAD 1218e3c (t382 LANDED).
- Prior export /tmp/pubpush EXISTS (2026-11-11 vintage) — script REFUSES
  existing dirs by design (line 21). Fresh dir this iteration:
  /tmp/pubpush-t383.

## S1. Export run (EXECUTED, exit 0)
- `GITHUB_USER=weylandsmith bash scripts/publish_public.sh /tmp/pubpush-t383`
  -> "OK: vendor-free history, 6143 objects, 11M .git, tree intact."
  (script's own gate: zero objects under game/ extracted/ work/
  artifacts/ascend_restored.bin; keep-checks campaign.cpp, docs/re, LICENSE,
  NOTICE, README.md all present.)

## S2. Verification on the clone (ALL PASS)
- HISTORY: 567 commits, author/committer name+email UNIFORM:
  567x "Weyland Smith <weylandsmith@users.noreply.github.com>"; zero [ISP-DOMAIN]
  strings in any commit identity; refs/original count 0 (strip not cosmetic).
- VENDOR OBJECTS: independent re-check `git rev-list --objects --all |
  grep -cE ' (game/|extracted/|work/|artifacts/ascend_restored\.bin|
  artifacts/functions_full\.tsv|archive/user-saves/)'` = 0.
- BUILD (no vendor data in tree): cmake Debug configure + build -j4 exit 0,
  run_tests linked.
- TESTS: `./build/run_tests` exit 0, fresh output line:
  "270 tests, 192 skipped, 0 failed" — matches the queue's expectation
  (270 total, 187+ skipped). Observer pins present: 5 SKIP (no vendor data),
  observer_synthetic_terminator_laws_t382 + observer_render_map_t382 ok.
- NOTICE: "Copyright (C) Weyland Smith" (t376 landed; no TBD placeholder
  remains in the copyright line).
- REMOTE: origin set on the verified tree to
  https://github.com/weylandsmith/ascendancy-rewrite.git (set-url; push NOT
  run — USER-gated).
- WORKING-TREE PRIVACY SWEEP (beyond the row's history gate): full-tree grep
  for email patterns excluding noreply/example -> ONE hit:
  docs/re/_license_draft_t372.md:110 quoted the personal git identity
  ([ISP-DOMAIN]-domain address, withheld verbatim here AND from all shipped docs —
  the bare domain string is the history-gate pattern, so no blob may hold it) — 7 grep hits = same
  line + STATE.md task text). t383 REDACTED it in the source repo (S7
  rewritten; published identity named) AND banked the t383b history-scrub
  route below, because the email survives in 25 historical blobs of that file
  (git grep over rev-list, counted) — a tip-only redaction would still push
  the address inside old blobs. NOTE: 160 files carry the plain username
  "hrethric" in /home/hrethric paths — username, not an email; disposition
  left open (user's call whether that ships; it is not a credential).

## S4. HISTORY SCRUB (EXECUTED — same session, follow-on commit)
- MEASURED LEAK: `git grep -c [ISP-DOMAIN] $(git rev-list --all)` -> the
  address lived in 25 historical blobs of docs/re/_license_draft_t372.md
  (tip redaction alone would still have pushed it). Full-rev-list git grep
  timed out at 300 s; the count above is from the bounded run before timeout.
- publish_public.sh 1b: --tree-filter sed scoped to that ONE path, pattern
  [A-Za-z0-9._%+-]*[ISP-DOMAIN][A-Za-z0-9.-]* -> [REDACTED-EMAIL]. PITFALLS
  hit and banked in the script comments: no --blob-filter on this git
  (git-filter-repo only, exit 1 first try); the earlier [[:punct:]] class
  stopped at '@' and would have leaked the local part.
- NEW FAIL-CLOSED GATE (exit 5): batch `rev-list --objects --all | cat-file
  --batch | grep -a $SCRUB_PATTERN` over every blob.
- Re-export /tmp/pubpush-t383b exit 0 (20.5 s): "vendor-free history, 6149
  objects, 11M .git, tree intact." INDEPENDENT re-scan: 0 hits
  "[ISP-DOMAIN]", 0 hits "hrethric@". 568 commits uniform Weyland Smith
  noreply (the +1 vs S2's 567 = this session's redact/wip commit). refs/
  original 0.
- Re-verified ALL S2 bars on the NEW tree: cmake+build exit 0; run_tests exit
  0 "270 tests, 192 skipped, 0 failed"; observer pins 7 present (5 SKIP
  no-vendor + 2 ok); keep-checks pass; NOTICE copyright line intact. origin =
  https://github.com/weylandsmith/ascendancy-rewrite.git (set-url; push NOT
  run — USER-gated). Stale exports /tmp/pubpush + /tmp/pubpush-t383 deleted;
  /tmp/pubpush-t383b is THE verified tree.
- Laws banked docs/re/packaging.md §12 (hand-appended; no generator writes
  that file — scripts/ grep = comment citations only).

## S5. Ledger
- NO OQ row touched (queue mandate). 17 closed / 2 open unchanged.
