# t424 WIP — PHASE-16 VERIFY + RE-EXPORT + PUSH + D17 SHEET (2026-11-18)

Scope (STATE.md NEXT ACTION): (1) gate + run_tests + seed regression seeds
1/2024/23; (2) export /tmp/pubpush-t424 vendor-free + data-less build/tests
+ gate --portable; (3) push fast-forward; (4) D17 sheet from the t423 shots
+ t422 chrome field. No measurement task; ledger expected to close NOTHING.

## F0 — pre-flight
- SITTING CHECK: live-timeline.jsonl mtime Nov 12 06:45 (unchanged since
  t396-era audits) -> no new play; assignment stands.
- WAKE step 0: :8613 LISTEN python3 pid 646702 — page server LIVE.
- Tree clean at 01b02f4 (t423c3). Remote expected tip 9692126 (t420 push).
- CHIP-CLICK RNG AUDIT (the assignment's VERIFY item): assignRaceColours
  (rewrite/src/ui/menulaw.cpp:47) consumes its OWN local `colourLcg`
  (title.cpp:173 `unsigned int colourLcg = 0x12e10u`), NOT the campaign
  rng_. It runs only inside the title/RaceConfig loop — buildCampaign is
  never re-entered from the click path (title.cpp:963 mutates only local
  raceColours[] + prints). The sim binary path (--headless) never touches
  title.cpp state. => chip click CANNOT move sim md5s; seed regression
  below is the mechanical confirmation.

## F1 — verification battery
- GATE_EXIT=0 ("[gate] ALL CHECKS PASS (milestone=6)"), /tmp/t424-gate.log;
  run_tests inside gate: 423/0/0 (t423c3 record).
- SEED REGRESSION (`rewrite/build/ascendancy --headless --campaign 1600
  --seed S`, HEAD 01b02f4):
    seed 1    md5 7e794a6dfb495800502762def9331e85  VICTORY Extinct t266
    seed 2024 md5 332a8cf3cebc95359924ce6a6b94a830  VICTORY Extinct t285
    seed 23   md5 0a6b7876719f38796e8235cb772a43d3  VICTORY Control t1406 (68%)
  ALL THREE EXACTLY the banked record (_wip_t420 F1) — phase 16
  (t422..t423c3) moved ZERO sim rng. The F0 chip-click audit stands:
  assignRaceColours consumes only the local colourLcg, never the sim rng.
  Logs /tmp/t424-seed-{1,2024,23}.log.

## F2 — export + data-optional battery
- `rm -rf /tmp/pubpush-t424 && GITHUB_USER=weylandsmith bash
  scripts/publish_public.sh /tmp/pubpush-t424` exit 0: vendor-free history
  7202 objects, 6.6M .git, tree intact (/tmp/t424-export.log).
- Fresh cmake build WITHOUT data (empty CMAKE_BUILD_TYPE): exit 0, ZERO
  warnings (grep -ci warning = 0).
- run_tests WITHOUT data: 423 / 245 skipped / 0 failed (data-optional law
  HOLDS). `gate.sh --portable` exit 0.

## F3 — push
- REMOTE NAME PITFALL RE-HIT IN-FLIGHT: first fetch used
  github.com/weylandsmith/ascendancy.git -> "Repository not found"; the
  canonical remote is ascendancy-rewrite.git (working repo `git remote -v`).
- set-url BEFORE the deciding fetch (t389 law). Fetched tip
  96921269e9267d601711a9591834e2ffa2e075ed == the t420 record; HEAD..origin
  empty (zero foreign commits); origin..HEAD = 11 commits (94ffcae..01b02f4);
  FAST_FORWARD_OK.
- `push --force-with-lease=main:96921269...` landed 9692126..8525086.
  POST-PUSH `ls-remote origin main` VERIFIED 8525086bc31bea4d458dbe8d6b28222
  59b16c322. Throwaway askpass /tmp/t424_askpass.sh built from
  ~/.config/gh-pub-token, used, DELETED, verified absent.

## F4 — D17-round sheet (fallback channel; web sheet PAUSED per D17)
- scripts/t424_grading_page.py (tracked). 10 crops from MEASURED inventory
  (t403_sheet_inventory bands + PIL before/after DIFF-CLUSTER scan: chip
  diff cells cluster (352..448,32..160) = DESC ring + header; hostile diff
  clusters (288..352,384..480) = atmosphere wheel) — crop-by-measurement law.
- All shots md5-distinct; the t412/t423 /tmp shots banked into
  work/r1/loop/ (t423c3-* already there from cycle 3; t412-newgame refreshed,
  t412-raceintro-current.png added — the old banked raceintro shot was
  pre-t415, md5 4a2dc7f3 vs current 64b88ce2).
- NATIVE-VISION verified crops live: hostile-wheel shows the red spiked orb +
  "Atmosphere" + the 7-chip Player Color row (live content); chip-after shows
  the PINK ring around the portrait (green->pink reassign visible).
- Questions: q0 chrome grain (t422), q1 newgame wheels/preview/portrait,
  q2 hostile orb, q3 chip click. NO re-ask of anything D16/D17 covered; no
  audio row (OQ-027 closes only on the hearing verdict).
- SCRATCH SELF-TEST PASS: port 8699, scratch root /tmp/t424_scratch_page,
  scratch DECISIONS — GET index/crop 200, POST -> "USER: D17r2 q0 = ok |
  notes: scratch" in the SCRATCH file, traversal 403; scratch server killed
  by pid from ss (pitfall: server.py forks — kill the LISTEN pid, 1044412,
  not just the shell pid). LIVE :8613 serves the new sheet without restart
  (index title + crop 200).

## F5 — ledger disposition
- CLOSES NOTHING (strict-close honest negative): a verify+push+sheet
  iteration ships no measurement about the vendor (t420/t413/t403 precedent).
  17 closed / 3 open unchanged. OQ-027 still awaits the final hearing
  verdict; OQ-016/OQ-019 DEFERRED — do not re-ask.
