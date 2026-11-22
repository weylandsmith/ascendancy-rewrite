# _wip_tNGB — tNG-B PHASE-17 G3 (BEHAVIOR) opening cycle [in progress]
Trigger check: ring turn 1086 on tail saves (watch.log 18:12, pid 1182156
alive) = NO new sitting; assignment = STATE.md NEXT ACTION tNG-B B1.
## B1 SCOPE READING (from cited laws, pre-probe)
Vendor density click (disasm work/tNGC_paint526b4.asm 0x52db9..0x52e57):
inc word[win+0xb7]; cmp hiword(word[+0xb5]),5 -> wrap +0xb7=0;
edx = hiword(dword[esp + rank*4 - 2]) where esp[0..4] = COPY of the
0x895c8 table {15,25,50,75,100} (movsd x5 at 0x52903..0x5290c, dispatcher
head) -> call FUN_000226e4(0x12e10, ebx=word[+0xb7]?, edx=starcount)
= FULL REGENERATE {0x22878 file parse, 0x22728 star POSITIONS (LCG),
0x234a4 lanes, 0x22ce4 reset} -> 0x28fc0 -> window repaint -> child[0]
+0x72 = word[+0xb5] -> child repaint.
=> B1 defect: the port's density click changes label+word+wheel record
   only; the preview cosmos set is splitmix-per-index STABLE across
   clicks (only N changes), and the Begin starfield follows the BUILT
   50-star campaign, not the wheel. Vendor: every click REBUILDS the
   star set (FUN_00022728 is a rand() consumer) with N = ladder rung.
## OPEN SUB-QUESTIONS (probe list)
Q1: which field is the density RANK (+0xb5 vs +0xb7) — the arm increments
    +0xb7 but compares/stack-indexes +0xb5hi; child +0x72 gets +0xb5.
    [F6 says +0xb5hi = density 0..4; F15 disasm shows inc on +0xb7 —
    reconcile: the vendor may keep rank in +0xb5hi set elsewhere, or the
    0x52db9 arm is NOT the density arm.]
Q2: does the port's wheel k-index already match the vendor sorted-rank
    law (t423 S2 F3-correction says EQUIVALENT) — verify by law fn.
Q3: vendor refcap density states: any captured at rung != Average?
## B1-DISASM CONFIRMATION (this session, capstone dump re-read)
DENSITY ARM 0x52db9..0x52e57 (msgs 0x1f5/0x1f6 via dispatch 0x5290d/0x52918):
  inc word[win+0xb7]                       ; DENSITY RANK++ (F6 pairing:
                                           ; dword[+0xb5] sar16 == word[+0xb7])
  hiword(dword[win+0xb5]) == 5 -> word[+0xb7] = 0    ; WRAP AT 5 (0x52dc9)
  ecx = hiword(dword[win+0xb1]) = word[+0xb3] = SELECTED RACE ROW
  edx = hiword(dword[esp + rank*4 - 2])    ; 0x52df4/0x52dfb STRADDLE READ:
      esp[0..19] = COPY of table 0x895c8 {15,25,50,75,100} (5x movsd
      0x52903..0x5290c at dispatcher head). rank 0 straddles word[esp+0x30]
      = pushed msg (0x1f5/1f6); hiword = ladder rung EXACTLY rank 0..4.
  ebx = hiword(dword[win+0xb7]) = word[+0xb9] = SPECIES COUNT 3..7
  call 0x226e4(eax=0x12e10 = CAMPAIGN STATE)  ; FULL REGENERATE (t295 S2:
      0x22878 parse + 0x22728 STAR POSITIONS rand-consumer + 0x234a4 lanes
      + 0x22ce4 reset) -> 0x28fc0(0x7a360-law) -> win repaint -> child[0]
      +0x72 = word[+0xb5] (0x52e39) -> child repaint.
=> VENDOR BEHAVIOR LAW: the density wheel click REGENERATES THE CAMPAIGN
   GALAXY ITSELF (state 0x12e10 is the play state, t295 base confirmation)
   with N = ladder[rank]; the preview cosmos AND the Begin-panel starfield
   (count word[obj+0x572]) are consequences, redrawn per click; each regen
   CONSUMES the LCG (t423 F4: "the preview IS a rand() consumer") so the
   visible set CHANGES every click, it is not a stable set with N clipped.
PARAM-SLOT CAVEAT (banked, do not re-litigate): t295 read the new-game call
   as ebx=50(T) edx=7; the wheel arm loads edx=ladder rung, ebx=word[+0xb9].
   The port models OBSERVABLE behaviour (N + set-change + wrap), not the
   internal slot order; 0x226e4's ebx/edx semantics stay a named seam.
## PORT DELTA PLAN (B1 + B3 same-file)
1. menulaw.h PURE LAWS: densityRankNext (wrap 5), densityStarCount =
   ladder[rank] (the straddle-read equivalence pinned in C), and
   previewStarMapPos(i, gen) -> 1024-grid map coords (splitmix keyed on
   gen: new SET per click, deterministic per gen — gate 3l safe, NEVER the
   sim rng); beginStarPanel keeps beginStarPos/beginStarClass but its
   COUNT becomes N = densityStarCount(rank) (word[obj+0x572] law).
2. title.cpp: preview cosmos seed rides gen; Begin starfield iterates the
   wheel-galaxy N set (not previewCamp's fixed 50); density click bumps
   gen; printf law line records gen + N.
3. B3 ANCHOR POLISH: per-control wheel blit delta measured refcap (F15-1c):
   atmos (+2.5,+1.5) ours-vs-vendor -> shift (-2,-1)... DECIDE from
   re-measure, not stale numbers; density (-1,+1) -> (+1? ) SEE F15-1c
   SIGN: ours = vendor + delta => blit shift = -delta.
4. PINS test_newgame_behavior_tNGB.cpp; WITNESS shot: 3 density rungs,
   cosmos-rect pixel set changes + Begin-panel star-content census grows
   with rung.
## STRADDLE-READ FULL DECODE (this session, byte-level)
Dispatcher head copies 0x895c8 -> esp[0..19] = {15,25,50,75,100} (5x movsd).
Arm: edx = hiword(dword[win+0xb5]) = word[+0xb7] = the rank JUST incremented
(F7 pairing: dword[+0xb5] sar16 == word[+0xb7] — SAME word, self-consistent).
edx = hiword(dword[esp + rank*4 - 2]): rank r reads bytes esp+4r..esp+4r+1 =
LOW WORD of table[r] (r=0 straddles the pushed msg word 0x1f5/1f6 which
supplies the low half of dword[esp-2]; its HIGH half = table[0] = 15). =>
edx = {15,25,50,75,100}[rank] EXACTLY — the vendor star-count law is the
SORTED ladder indexed by rank; port ring {50,75,100,15,25} = same set,
bijection-equiv (t423 S2 F3). ebx = word[+0xb9] = species count; t295 read
the NEW-GAME call as ebx=50 edx=7 — slot semantics of 0x226e4 ebx/edx stay
NAMED SEAM (port models observable N + set-change + wrap only).
## IMPLEMENTATION DECISIONS (B1)
- menulaw.h pure laws: densityRankNext (wrap 5, 0x52dc9); densityStarCount
  (rung law). Test-side emulator vendorStraddleStarCount in the pin file.
- title.cpp: wheelGen counter + local rebuild of a PREVIEW galaxy via
  MapGenerator(starCount = rung, seed = f(campaign seed, wheelGen)) —
  vendor FUN_00022728 is a rand() consumer: EVERY regen draws a NEW set,
  never a stable set clipped to N (the D17-class defect here: our cosmos
  points were per-index stable across clicks). Live-campaign apply stays
  the t393 named seam (Begin enters play on the built galaxy).
- Preview cosmos seeds its per-star hash with (baseSeed, wheelGen) -> set
  changes per density click; N = wheel galaxy size. Begin starfield field =
  wheelGal stars when present (count law word[obj+0x572] consequence),
  else previewCamp (initial screen = built galaxy, matches vendor init).
- B3 anchor polish: per-control blit deltas from F15-1c (ours-vendor):
  density (-1,+1) -> correction (+1,-1); species (-1,0) -> (+1,0);
  atmos (+2.5,+1.5) -> (-2,-1) [STATE B3 quotes (+2,+2) -> (-2,-2)].
  VERIFY post-change pixel agreement vs refcap; REVERT if not improved.
- WITNESS scripts/tNGB_density_shot.sh: 4 clicks 50->75->100->15->25;
  assertions (1) app.log 'galaxy regen gen G stars N' x4; (2) cosmos-rect
  non-black pixel SET differs every click (md5 of masked png); (3) mass
  VeryDense(100) > Vacuous(15); (4) Begin-panel star-family px tracks N.
## RANK/CYCLE FULL DECODE (byte-level, supersedes ambiguity above)
hiword(dword[A]) = word at A+2. Dispatcher copies 0x895c8 -> esp[0..19].
r=0: hiword(dword[esp-2]) = word at esp+0 = low half table[0] = 15.
r>=1: hiword(dword[esp+4r-2]) = word at esp+4r = low half table[r].
=> VENDOR LAW: star count = SORTED {15,25,50,75,100}[rank]; wheel art
   child+0x72 = rank VERBATIM (k0 = rank0 = 15 = Vacuous). Default screen
   Average => initial rank 2; click sequence of ranks 3,4,0,1,2,... (wrap
   cmp==5 -> 0 at 0x52dc9) => counts 75,100,15,25,50,... == t78 MEASURED
   cycle Average->Dense->VeryDense->Vacuous->Sparse->wrap. The port's
   kDensityStarCounts {50,75,100,15,25} is that same VISITED sequence from
   the Average default — cycle-index == visited-order, EQUIVALENT (t423 S2
   F3 stands). PIN: byte-buffer emulation of the straddle read + visited
   sequence 50,75,100,15,25,50 (mutation target: wrap 5, table values).
## B1 CODE DELTA (decided)
- menulaw.h/cpp: densityRankNext (wrap 5); densityStarCount(rank-cycle).
- title.cpp: WHEEL GALAXY = display-only Galaxy rebuilt via MapGenerator
  (starCount = rung, seed = base + wheelGen) on EVERY density click (vendor
  0x526e4 rand-consumer: new SET per click — port models set-change by
  gen-keyed seed, placement laws UNTOUCHED: preview stays t423 cylinder,
  Begin stays shrunk-map /5+5). Begin starfield iterates wheelGal (count
  law word[obj+0x572] consequence), falls back previewCamp when wheelGal
  null (no starstat/names = honest). Preview cosmos hash keys (i, wheelGen).
- NO live-campaign mutation (t393 named seam: Begin enters play built).
## B1 IMPLEMENTED + PINS GREEN (build verified)
- menulaw.h/cpp densityRankNext + densityStarCount (defined in cpp; the
  first attempt at an inline array definition broke the extern — fixed).
- title.cpp: wheelGal (std::optional<Galaxy>) + rebuildWheelGalaxy lambda
  (MapGenerator starCount=rung, seed=base+gen; honest keep-previous on load
  failure); preview cosmos N = wheelGal size, hash += wheelGen*0x100000001;
  Begin starfield iterates wheelGal (fallback previewCamp); density click =
  densityRankNext + rebuild + printf 'ui raceconfig galaxy regen gen G
  stars N'.
- PIN test_newgame_behavior_tNGB.cpp x4: straddle byte-emulator == sorted
  ladder; visited sequence 75,100,15,25,50,75 from Average (NOTE: port
  cycle index j == vendor sorted-rank (j+2)%5 — Average is vendor rank 2;
  newgameWheelFrame already keys art off the SORTED rank, consistent);
  wrap term; rebuild determinism per (seed,gen) + new set per gen.
  run_tests: 483 tests, 0 skipped, 0 FAILED.
## BEGIN-PRESS BLOCK FOUND (0x52a44..0x52b75, seed for a LATER row)
Click OUTSIDE the chip zone (0x529d2 zone test fails) + 0x52678 passes ->
0x52a54: call 0x238e8(0x12e10, ebx=0) = WORLD GEN (t295 "new game" pair),
0x2351c(0x12e10, 0x2bf7), camera/matrix init, byte[win+0xbb] ATMOSPHERE ->
byte[0x13bc4] (0x52b3c/0x52b44 — THE atmosphere global store, first writer
census site banked), 0x23388(0x12e10), script arms. => the vendor BEGIN
press re-runs WORLD GEN with the wheel settings (t393 "settings apply"
named seam has a cited call site now — B2/B4 candidate, NOT this cycle).
## B1 WITNESS GREEN + B3 VERIFIED (this session, adoption of killed run)
- Build incremental-green; ctest 0 failed (unit_tests Passed 26.25s).
- scripts/tNGB_density_shot.sh ran clean (Xvfb :97, /tmp/uishow): app.log
  regen lines EXACT gen1..4 stars 75,100,15,25 alongside the pre-existing
  'click GALAXY_MORE msg 501 -> Dense/Very Dense/Vacuous/Sparse' words.
- scripts/tNGB_density_witness.py GREEN: star mass rung0..4 {326,671,727,
  86,210} tracks N monotone-consistently (100>75>50>25>15 ordering within
  reachable comparisons); EQUAL-N set-change rung0(gen0,50) vs rung4(gen4,
  50) jaccard 0.158 (inter 73 union 463) => the click DRAWS A NEW SET, the
  pre-tNG-B per-index-stable defect is dead.
- B3 VERIFY scripts/tNGB_b3_anchor.py (F15-1 best-shift method, +-4, delta
  <=12, interior rows 408..466, refcap scratchpad/newgame-original.png):
  density 94.3% @(0,0) (base 93.6 @(1,-1) IMPROVED), atmos 91.2% @(0,0)
  (base 91.4 @(-2,-1), hold, shift->origin), species 76.0% @(0,0) (base
  80 @(1,0); CONTENT confound ours k9 vs vendor k7 — informational, shift
  moved to origin). Verdict: kWheelBlitDx/Dy {1,1,-2}x{-1,0,-1} KEPT.
  NOTE method caveat: agree() overlap-window shift of ours over vend (the
  F15-1 wording didn't pin crop-edge handling; results reproduce baseline
  baselines to +-0.2% at the same shifts, so the comparison is sound).
## t441 RUN + chrome-recess-row7 KNIFE-EDGE (harness observation, not a
## B1 defect): t441_screen_diff newgame on the B3 build:
- t412-newgame.png (canonical shot): 18/18 PASS, exit 0.
- rung0.png (tNGB density shot, initial Average state): 17/17 + row7 FAIL
  'ours fam share 0.90 < 0.9'. Pixel autopsy: row 7 differs from the t412
  render at EXACTLY 3 px x304..306 (the preview-cosmos region boundary
  zone; delta max 191). run-to-run probe scripts/tNGB_var_shot.sh (same
  binary, SAME state, three grabs a/b/c): the spin animation flips row-7
  fam share between 0.8994 and 0.9035 across grabs 1s apart — the region
  fam_min=0.90 threshold (t441_screen_diff.py:175) sits INSIDE the
  animation dither band. => row7 is a harness knife-edge on an ANIMATED
  cosmos column, NOT the B1 delta (B1 touches rows 381..472 + cosmos hash;
  the flip sites x304..306 are cosmos stars at the row-7 chrome edge).
  Options (tNG-U harness polish, NOT this cycle): fam_min 0.89, or freeze
  seed animation for chrome regions. Canonical t412 shot stays green.
## MUTATION CAMPAIGN round 1 + TWO harness bugs found (skill rule 7 triage)
- scripts/tNGB_mutate.py (copy-snapshot revert, md5-verified, launch guard):
  8 mutants M1-M8. Verdicts printed 'MUTATION 8/8 CAUGHT' BUT:
  (a) BUG-1 inverted catcher: witness_catch() returned (rc==0) as CAUGHT —
      tests-class M1/M2/M3 verdicts are SOUND (rc!=0 == caught, names:
      tngb_density_straddle_star_count_law:81/:82, tngb_density_rank_wrap_
      term:92). Witness-class recheck standalone: M4-seed-no-gen is MISSED
      (witness GREEN rc=0 under mutant) — the equal-N pixel-jaccard is
      ANIMATION-CONFOUNDED (see below). M5/M6 rechecked with the fixed
      anchor law: both RED = genuinely CAUGHT (M5 density best shift
      (0,-1)!=origin; M6 atmos (-2,0)!=origin).
  (b) BUG-2 witness aim: the equal-N test used chroma-PIXEL jaccard in the
      Begin band: clean rung0-vs-rung4 0.158, M4 0.233 — weak separation,
      because the FOUR-WAY CLASS law flickers star colours with beginYaw
      between shots (positions are STATIC per the beginStarPos law, so the
      right discriminator is star CENTROID sets, not chroma pixels). And
      the PREVIEW cosmos band is backdrop-dominated (chroma mass ~6000,
      jaccard 0.73..0.92 everywhere — clean vs M7 0.864 vs 0.874: no
      signal): a count-observable is needed, not pixels.
## FIX PLAN (in flight)
1. witness: Begin-band star CENTROID clustering for the equal-N set test
   (static-position law makes centroids animation-robust; same seed =>
   same centroid set => M4 RED). Mass test kept.
2. title.cpp observability law line 'ui raceconfig cosmos n N' printed on
   CHANGE of the rendered cosmos n (once per click) — the port's law-line
   pattern; witness asserts 75,100,15,25. Under M8 (frozen n) absent => RED.
3. campaign rerun M4-M8 with corrected catcher logic (CAUGHT = rc!=0).
## FIX LANDED (observability + pure-law extraction)
- menulaw.h cosmosHash(i, gen) PURE LAW (splitmix seed key, gen * 0x100000001
  term) — title.cpp draw loop calls it (avalanche unchanged, verified build).
- title.cpp law line 'ui raceconfig cosmos n N' printed on CHANGE of the
  rendered cosmos n: clean sequence [50,75,100,15,25] (initial + 4 clicks);
  M8 (frozen n) emits only [50] -> witness RED.
- Centroid probe (brightness mask mx>100/min>4, 8-conn clusters >=4px, Begin
  band): CLEAN rung0->rung4 containment 0.316 (th100) / 0.450 (th120) —
  different galaxies, random coincidence floor; under M4 (same seed => same
  50-star set, static positions) containment ~1.0. Witness threshold 0.70.
  n0=19 n4=14 n2=31 centroids (mask catches the bright subset only — fine,
  containment is over DETECTED centroids either way).
- WITNESS rewrite: equal-N chroma-jaccard REPLACED by centroid containment
  (animation-invariant: class flicker moves brightness not position); mass
  test kept; cosmos-n law-line assertion added.
- CAMPAIGN bug-1 fixed: CAUGHT = rc!=0 for witness/anchor catchers too.
## SET-CHANGE DISCRIMINATOR ANALYSIS (flicker confound, resolved LOG-side)
Chroma-centroid containment CLEAN rung0<->rung4 0.25-0.39 and M4 0.47 — NO
separation: the four-way class law (beginYaw) makes each shot detect only a
~30% RANDOM SUBSET of the static star set, so cross-shot overlap is
flicker-sampled either way. Pixel-space equal-N tests are DEAD for M4.
KEY OBSERVATION (M4 pair census): M4 jaccard(3,4)=0.368 vs clean 0.046 —
MapGenerator at a FIXED seed is PREFIX-STRUCTURED (same rng stream, count
k => stars[0..k-1]; rung3's 15 stars are rung4's first 15). => FIX: the
regen law line gains 'h15 <hex>' = hash of the first 15 star positions
(min cycle count). CLEAN: h15 DIFFERS every click (seed rides gen). M4:
h15 CONSTANT (prefix of one stream) -> witness RED on log alone, no pixels.
M8 CAUGHT by the 'cosmos n' law line (frozen n emits [50] only).
M7 CAUGHT by unit pin on the NEW pure cosmosHash(i,gen) gen-key term.
WITNESS ASSERTS (all log-based + mass): regen lines exact; cosmos-n
sequence [50,75,100,15,25]; h15 four distinct values; mass monotone-
consistent. Centroid containment printed INFORMATIONAL only.
## ROUND-2 CAMPAIGN DESIGN (prefix hypothesis REFUTED by pin, re-aimed)
- tngb_mapgen_prefix_structure FAILED: positions are NOT prefix-structured
  across counts (shell radii allocate from n, mapgen.cpp:114) — the pin was
  replaced by tngb_mapgen_same_seed_same_count_identical (pure fn of
  (seed,count); different seed differs) which PASSES, and that property is
  what the witness now uses: SIX clicks so the rung cycle wraps (counts
  75,100,15,25,50,75) — gen1 vs gen6 share RUNG 75; seed riding gen =>
  h15 DIFFERS (clean: feb28588.. vs d257d497..), frozen seed => IDENTICAL
  h15 -> M4 RED on the log alone.
- CLEAN 6-click witness GREEN: regen lines exact, cosmos-n
  [50,75,100,15,25,50,75], h15 six distinct values, mass monotone-consistent
  (rung5=326==rung0 mass — same rung same field, an independent consistency
  signal).
- M7 re-aimed at the PURE cosmosHash gen-key term (menulaw.h) -> tests
  catcher. M8 catcher = the cosmos-n law line (frozen n prints [50] only).
- Campaign round 2 launched with bug-1 fixed (CAUGHT = rc!=0, all catchers).
## MUTATION ROUND 2: 8/8 CAUGHT, ALL WITH NAMED VERDICTS (bug-1 fixed)
M1 wrap term (straddle pin :81); M2 count-table (:82); M3 guard-fallback
(wrap pin :92); M4 seed-no-gen wITNESS: h15 repeated 827d710cd0409ed0 x4
(the gen1/gen6 wrap pair + all frozen-seed rungs collide — exactly the
designed discriminator); M5 anchor-dy: density best shift (0,-1)!=origin;
M6 anchor-dx: atmos (-2,0)!=origin; M7 hash-no-gen: pure pin :132; M8
n-frozen: cosmos-n ['100'] != full sequence. AFTER-RESTORE rc=0, md5-ok x3.
Round-1 lesson banked: an agreement-at-best-shift metric is anchor-INVARIANT
(mutants just move the shift) — pin the SHIFT POSITION, not the agreement.
