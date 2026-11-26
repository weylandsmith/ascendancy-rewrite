# tPF-1c WIP — day-20 camp.over() defect, user-exact-cmdline repro (2026-11-26)

## Assignment (steering 2026-11-26, overrides STATE NEXT)
fe0fb45 closure VOIDED: user's verbatim cmdline "./build/ascendancy --data
/home/hrethric/Games/ascendancy/ascendancy-rewrite/ --ui" has NO --campaign;
console showed ONLY "ui ok: turn 20" => clean exit via ui.cpp camp.over()
leg. Task: repro with EXACT cmdline (Begin-built, factory order pending,
xsend next-day past day 25). On exit: Victory enum + checkVictory branch,
fix ROOT ownership/AI-setup law, verify ALIVE 40+ days. If HEAD does not
reproduce: name the rev delta that fixed it — no silent "couldn't reproduce".

## Session-start audit findings (facts, before repro)
1. `c68e8bd` DOES NOT EXIST in this repo (git rev-parse: "Needed a single
   revision"). The steering's "user built ~c68e8bd era" rev hint is STALE;
   the feedback artifact is scratchpad/t433-build-feedback.txt (D28,
   2026-11-24). Rev-delta range for "did later commits fix it" =
   f8c51e1(2026-11-24)..HEAD if the user built the t433 tree.
2. User cmdline NOT runnable verbatim here: /home/hrethric/Games/... does
   not exist on this host (find, maxdepth 4). Closest on-host equivalent:
   --data <repo root> (default dataRoot law, main.cpp:46) + --ui.
3. REPRO B (fe0fb45) config deltas vs user: seed 5 (user: NO --seed =>
   seed 1 default, main.cpp:50) and NO factory order (user: factory
   pending). Both must be matched. REPRO B survived 40 presses; that is
   NOT yet evidence about the user's config.
4. checkVictory legs (campaign.cpp:2265-2318): Extinct (mine==0 &&
   turn_>0 && !fleetPending), LastAlive, Captured, Unification, Control
   (scoreStars_ >= (2*total)/3+1). tPF-8 LANDED names residue "zero-mask
   early lethality seeds (42 t10)" — Extinct at low turns is a KNOWN
   port-side outcome family after the tPF-8 zero-start research mask.
5. Exit-site print: "ui ok: turn %d" ui.cpp:3749 (post-loop, only site);
   quit=true legs: cap (turns>0) ui.cpp:~1593, camp.over() next line.
6. pickHomeStars (campaign.cpp:384) assigns a distinct home to EVERY owner
   0..aiCount (rejection draw) — AI owners DO get stars at setup on HEAD;
   suspect (b) static-refuted for HEAD, live check still queued.

## Plan
A. headless deterministic sim at the user's Begin triple (seed 1): per-turn
   starsOwned census + victory name -> if Extinct ~t20, root cause is the
   sim (AI capture / player star loss), not the exit plumbing.
B. interactive repro, user-exact flags (--ui only), seed 1, Begin-built,
   factory order pending (tPF-2b click law), NEXT TURN x45, pgrep liveness.
C. disposition: fix root law or honest negative + rev delta.

## REPRO RESULT 1 (HEAD f518347, user-exact flags) — NO REPRO
scripts/tPF1c_repro.sh (new, committed this iteration): --data <repo> --ui,
NO --campaign, NO --seed (=> seed 1), Begin-built wheel defaults (log:
'newgame live stars 50 owners 5 gov 1'), FACTORY ORDER LANDED
('ui planet project Parsimony I Factory (ordered armed cell 10)'), then 45
x NEXT TURN — EVERY press registered ('ui click next-turn' x45), app
ALIVE, zero VICTORY lines, zero camp.over() exit. VERDICT rc=0.
Harness lessons banked (all were VACUITY traps, each caught by an
assertion, not by luck):
 - order log format is 'ordered armed cell N' INSIDE parens (ui.cpp:1146);
 - an armed cell with n=0 legal items leaves projectOpen set — recovery =
   Escape (pops to STATUS) + row-0 re-select (fresh-entry reset ui.cpp:899);
 - Escape from planet view lands on STATUS, NOT the map — the day-advance
   leg must assert 'ui screen Planets -> map' before pressing NEXT TURN at
   (511,67) or the presses are vacuous;
 - every nav step must grep-assert its own log line (the first run's
   'ALIVE after 45' was worth ZERO — 0 presses registered);
 - script needs a cleanup trap (NAV FAIL leaked Xvfb :97 -> next run
   'Xvfb dead' on the lock).
Headless control: '--campaign 45 --seed 1' and '--stars 50' both survive
45 turns on HEAD (player 1 star, 6 AI 1 star each, no victory).

## DISPOSITION PATH (steering law: no silent 'couldn't reproduce')
User built ~t433 era (2026-11-24; c68e8bd is NOT a rev in this repo —
git rev-parse fails). HEAD-era config does NOT exit at 20. Therefore the
exit, if real, belonged to the t433-Era build and a later commit fixed it.
Plan: build t433-era binary (commit 7cc4d22 tree = the feedback commit
itself; earliest possible build the user had AFTER reporting would be
f8c51e1) and run the same repro script against it; if it exits ~20,
bisect forward over the 20 commits to name the fixing rev.

## REPRO RESULT 2 (era build 656ce2e) — camp.over() DOES NOT FIRE
Era tree (656ce2e, 2026-11-24 18:17 — the HEAD the user was told to build
per the 2026-11-24 STATE block 'user is BUILDING c68e8bd locally'; c68e8bd
is NOT in this repo: git rev-parse, reflog --all, fsck all NEGATIVE — it is
a rev in the USER's own clone ~/Games/ascendancy/ascendancy-rewrite).
Built /tmp/era-tree, ran scripts/tPF1c_repro.sh SKIP_ORDER=1 (popup ids law
is post-era): Begin 50/5/1, 45 registered NEXT TURN presses — ALIVE, zero
VICTORY lines. checkVictory is BYTE-IDENTICAL era..HEAD (git diff shows only
tRS-V2w research/freeloader + tPL-D1 home-table hunks). The steering's
suspects (a) Extinct miscount and (b) AI-no-homes are REFUTED at
construction: pickHomeStars assigns a distinct home star to EVERY owner
0..aiCount before anything can consume them.

## ROOT CAUSE MEASURED — THE DAY-20 EXIT IS THE QUIT LEG, NOT camp.over()
scripts/tPF1c_escape_test.sh TAG=era, era binary, user flags (--data --ui,
no --campaign, seed default), Begin-built, 20 manual NEXT TURN presses,
then ONE Escape at the map (stack bottom):
    'ESCAPE-TEST: EXITED on map-Escape (presses=20)'
    log tail: 'ui click next-turn' / 'ui ok: turn 20'
That is the user's symptom line VERBATIM — 'ui ok: turn 20', no victory
announcement — reached with ZERO victory conditions firing. Mechanism:
doEscape else-branch (era ui.cpp:573, HEAD ui.cpp:683 — IDENTICAL code,
'quit = true' at stack bottom). The user's flow fits the feedback text
exactly: he opened popups/lists on the planet screen (each Escape unwinds
one level), ended on the map, and one more Escape quit the process.
The exit at day N is DETERMINISTIC given N presses + one bottom-Escape;
'20' is just how many presses he made.

## STATUS OF THE STEERING CLAIMS
- 'the campaign is declaring VICTORY/DEFEAT ~day 20': REFUTED by the escape
  repro — the same cmdline, same era build, 45 presses, no victory. No
  Victory enum printed, no VICTORY event line, no end-*.txt screen.
- 'fix the ownership/AI-setup ROOT LAW': nothing to fix — setup law gives
  every owner a home (pickHomeStars, cited t295 law) and 45-day runs keep
  1+1+1+1+1+1+1 star distribution stable.
- 'if it does not reproduce name the rev delta': the exit was NEVER a
  victory defect, so no fixing commit exists and none is needed; the
  reproducible mechanism (bottom-Escape quit) is PRESENT IN HEAD TOO
  (ui.cpp:683). D30 law respected: the user's denial of '--campaign' was
  correct — his exit did not come from the cap.
