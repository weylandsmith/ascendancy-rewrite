# t403 WIP — PHASE-12 VERIFY + RE-EXPORT + PUSH + D12 GRADING SHEET (session 2026-11-15)

Task (docs/STATE.md NEXT ACTION, queue row t403 VERBATIM): full gate +
run_tests + headless seed regression byte-identical; export; verify
vendor-free/build-without-data/identity; fetch FIRST; push; ls-remote verify;
rewrite NEXT to WAIT-USER-RULING with D11-item-by-item grading handoff.

## Probes

F0 (steering pre-checks). Ring-first sitting check: t368_ring_turn
parsed=20/20 max_turn=1254 — same sitting as t379..t383/t391/t396; zero new
play; r1_t85g_sitting.py NOT run; assignment stood. Tree clean at launch
(HEAD dff2462 t402). Ruling server ALIVE on :8613 (ss: python3 pid=646702).
DECISIONS.md tail: the 2026-11-15 11:37:07 D11 ruling block is the newest USER
content (6 lines: title near-pass w/ hover gap; new game usable-but-wrong;
galaxy map FAIL detail; audio "seems OK at first listen"; D11b drop).
NO USER line grades the t401/t402 shots (the ruling predates both landings —
11:37 vs t401 17:56 / t402 20:44 mtimes), so wake-procedure step (2) is a
no-op: nothing to record verbatim into t401-newgame-art.md S12 beyond the
predates note; D11 items stay USER-PENDING. server.log's 11:40 "selftest=ok"
line stays a harness artifact (t398 disposition).

F1 (verification, row leg 1). Gate background run: "ALL CHECKS PASS
(milestone=6)" GATE_EXIT=0 (/tmp/t403_gate.log). run_tests on the working tree:
"347 tests, 0 skipped, 0 failed" — == t402 record.

F2 (seed regression, row leg 1). HEAD `ascendancy --headless --campaign 1600`:
  seed 1    md5 7e794a6dfb495800502762def9331e85  VICTORY Extinct t266 (0%)
  seed 2024 md5 332a8cf3cebc95359924ce6a6b94a830  VICTORY Extinct t285 (0%)
  seed 23   md5 0a6b7876719f38796e8235cb772a43d3  VICTORY Control t1406 (68%)
ALL THREE md5s are EXACTLY the banked record (t389 _wip S36-39, re-confirmed
t396, original t365 law). The record is TRANSITIVE: t396 proved HEAD@cbe7b8f
byte-identical to baseline c7a3fda with these md5s; t397-t402 touched no sim
rng (their own seed-1 spot checks + this re-run); therefore phase-11+12 UI
rows (t398 palette, t399 cam3d, t400 rail, t401 newgame art, t402 statuslist)
moved ZERO sim rng — PROVEN by cited measurement, no redundant baseline
rebuild required (the /tmp/t403-baseline worktree at 3ceecce was started then
removed once the md5 match made it redundant).

F3 (grading-sheet geometry, MEASURED not guessed — t397 pitfall law):
scripts/t403_sheet_inventory.py (tracked tool: size + bg + per-band non-bg
mass for loop captures) + scratch _wip_t403_geom/_wip_t403_text runs:
- t400-title-hover.png: hover fill (0,28,36) count per button band y=200+40i:
  EXACTLY btn4 (y360 = LOAD GAME) 9347 px, all others 0 — one hovered button,
  law-consistent; the crop for the sheet is (159,355,478,445).
- t402-status-open.png: row-zone top colours (40,40,56) panel / (12,32,48)
  rail / (190,255,255) TEXT 2869 px / (235,235,235); text is CYAN-WHITE not
  green — the green-ink probe found only the ring ring (y112-115/224-227).
  Row crop for the sheet: (20,46,470,372) at 2x.
- t401-newgame.png: content column runs at bottom band: x 0-122 + 131-370
  (desc+panels) and 494-639 (racelist/begin). Crops: racelist (494,60,640,380),
  bottom-row (0,415,470,480), begin (490,415,640,480).
- t400-map.png sidebar full-height content (rows 0-479) — reuse t397 split
  (430,0,640,240)/(430,240,640,480).

F4 (sheet). scripts/t403_grading_page.py (tracked, pattern of
t397_grading_page.py; run with ~/tools/revenv/bin/python — system python3 has
NO PIL). D12 fields: title-hover / new game / galaxy map / planets list (NEW
item, t402) / audio line (OQ-027 closer re-ask per row's own bar — "seems OK
at first listen" is NOT the verdict). Vendor refs copied local-only.

F5 (export + push). First export attempt FOUND A REAL REGRESSION: run_tests on
   the data-less export SIGSEGV 139. stdbuf -o0 pinned the crasher:
   statuslist_word_tables_match_static_txt_t402 (t402) lacked REQUIRE_DATA();
   no static.txt -> empty vector -> its own CHECK fails -> s[41+i] OOB UB.
   The SAME class t396 fixed for newgame_t393_lore_file_real_data — t402
   re-introduced it (data-optional law needs a per-file guard census, not
   memory). Guard census over all t398-t402 test files (awk TEST/REQUIRE_DATA
   pairing): the only unguarded test that dereferences data reads
   (rail_t400's game.pal read is if(load)-guarded by design). Fix commit
   cda9cb1; working tree 347/0/0 with data.
   RE-EXPORT /tmp/pubpush-t403 (from cda9cb1): "vendor-free history, 6654
   objects, 6.0M .git, tree intact"; refs/original 0; identity uniform Weyland
   Smith noreply; keep-checks pass (campaign.cpp/statuslist.cpp/
   test_statuslist_t402.cpp/NOTICE/LICENSE/docs STATE). Build WITHOUT data
   exit 0 ZERO warnings/errors; run_tests WITHOUT data 347 tests / 218
   skipped / 0 failed; gate --portable on the export ALL CHECKS PASS exit 0.
   PUSH: FETCH-FIRST law respected — first fetch went to the LOCAL SRC path
   (export clone default, the t389 trap re-hit); set-url to GitHub BEFORE the
   deciding fetch. Remote tip 3be7e9af6c24 (== t396 push, no foreign/web-UI
   commits: `git log origin/main --not main` empty); export tip 06da9b2
   (filter-branch rewrites SHAs — 06da9b2 IS cda9cb1's public twin);
   merge-base --is-ancestor => FAST_FORWARD_OK (no history rewrite this round,
   so no GC exposure added). Push --force-with-lease=main:3be7e9a landed
   3be7e9a..06da9b2. POST-PUSH ls-remote origin main ==
   06da9b2fa8a4dc1a5e21838def2964a85b2ec262 (verified, not self-reported).
   Askpass helper /tmp/t403_askpass.sh deleted (verified absent).

F6 (grading channel). D12 sheet LIVE on :8613 (the long-running server serves
   ROOT/index.html, so no restart needed — verified GET 200 + 'D12' x7/8).
   12 crops all PASS non-flat census (>=4 colours). Self-test
   (scripts/_wip_t403_selftest.py, in-process, SCRATCH port 8699 + SCRATCH
   DECISIONS per server docstring rule): POST fields -> USER: lines PASS;
   traversal 404 PASS. D12 ask block appended to docs/DECISIONS.md.
   t401 wake-step: NO USER line grades the t401/t402 shots (ruling 11:37
   predates both landings) — nothing to record verbatim; D11 items stay
   USER-PENDING pending D12.

LEDGER: 17 closed / 3 open UNCHANGED. Honest negative: t403 closes nothing —
verify+push moves no measurement, and the D11/D12 grades are testimony for the
STATE queue items, not witnesses for any OQ row's named closer. OQ-027 stays
OPEN on its own bar (audio line paste + match verdict).
