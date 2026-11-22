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


## B2 PLAN (decided after probes; 3 findings so far)
F-A SPECIES ARM [verified 0x52e58..0x52ecc]: NOT a regen. rank word[+0xb9]
   ++, wrap 8->3, setter 0x22ce4, repaint, child[1] art = count+2. The STAR
   SET IS PRESERVED (0x22ce4 zeroes only owner/OR bytes +0x14..+0x17 of the
   stride-0x60 star records, never the +0x30/+0x34 position floats [t441
   record law]). => the species click's law is the OPPOSITE of B1's:
   positions INVARIANT, roster re-rolled.
F-B 0x22ce4 [verified decompile]: word[state+0xd88]=N (PLAYER COUNT), clears
   all star-owner bits, re-rolls HOME WORLDS per player k<N: star =
   state+0xdb5 + (FUN_0007824f()%starcount)*0x60 retry-until-free (rand
   consumers), then FUN_0003e6bc per player (species pick rand%0x15 distinct),
   then FUN_000232ec (COLOUR assignment — the chip-click law fn runs on the
   SPECIES CLICK TOO via this tail call).
F-C PORT DEFECT: title.cpp speciesSetting default = 7 (wheel k9 'Seven');
   VENDOR DEFAULT = 5 (window-init 0x52c55: word[+0xb9]=5, child art +0x72=7
   = k7 'Five' — matches t401 anchor 'k7 @ Five measured'). The B3 species
   anchor 'content confound ours k9 vs vendor k7' IS this defect. Fix default
   -> 5: species panel becomes a REAL pixel-verdict vs refcap (no longer
   informational). The 'word = campaign player count Seven' coupling comment
   (title.cpp ~176) decouples; live-campaign apply stays the t393 named seam.
## B2 WITNESS GREEN (first run, post-code)
- Law lines: roster n 6,7,3,4 wheelgen 0 h15 827d710cd0409ed0 CONSTANT all
  four clicks (positions preserved; wheelgen 0 == no regen). h15 == the B1
  rung0 hash — same galaxy, independent confirmation.
- tNGB_b3_anchor.py on spec0.png: species 88.8% @(0,0) (was 80.0% @(1,0)
  with the k9 default) — THE DEFAULT FIX IS PIXEL-VISIBLE. Species UPGRADED
  informational->verdict: best shift must sit at ORIGIN and agreement must
  stay >= 87.0 (a default-7 mutant sits ~80 = RED; margin to 88.8 = 1.8pt,
  the row-7 knife-edge class caution applies — canonical shot only).
## B2 PLAN (decided after probes; 3 findings so far)
DO: (1) menulaw.h pure speciesRankNext (wrap 8->3, cited); (2) title.cpp
default 5 + click uses speciesRankNext + re-runs assignRaceColours (cited
0x22ce4 tail 0x232ec) + law line 'ui raceconfig roster n N h15 H' (h15 from
wheelGal — INVARIANT across species clicks, the log-side counterpart of the
positions-preserved law; a mutant that bumps wheelGen on species click turns
it RED); (3) pins speciesRankNext wrap/visited-from-5 + default-frame k7;
(4) witness tNGB_species_shot.sh + tNGB_species_witness.py (words Six,Seven,
Three,Four; roster 6,7,3,4; h15 constant) + tNGB_b3_anchor.py species panel
UPGRADED informational->verdict (best shift at origin + agreement jump);
(5) mutation tNGB2_mutate.py S1-S4 (wrap term, wrap value, species-click
regen mutant via h15, default 7 via words+anchor).

## B2 SPECIES ARM FULL DECODE (this session, capstone work/tNGC_paint526b4.asm + Ghidra decompile FUN_00022ce4)
ARM 0x52e58 (msg 0x1f7 = 503 SPECIES_MORE; dispatched 0x5291e->0x52f49->je 0x52e58):
  inc word[win+0xb9]                       ; species-count counter
  cmp hiword(dword[win+0xb7]), 8           ; F7 pairing: hiword(dword[+0xb7]) == word[+0xb9]
                                           ; == SAME word just incremented (not a shadow)
  je -> word[ebp+0xb9] = 3                 ; WRAP 8->3 (0x52e6b..0x52e6d): domain 3..7,
                                           ; visited from DEFAULT 5: 6,7,3,4,5 cycle
INIT BLOCK 0x52c3d..0x52c77 (window open, cited verbatim):
  word[+0xb7]=2 child[0]+0x72=2   ; density rank 2 = Average(50)
  word[+0xb9]=5 child[1]+0x72=7   ; *** SPECIES DEFAULT = 5 (Five) -> WHEEL ART k7 ***
  word[+0xbb]=1 child[2]+0x72=0xb ; atmosphere 1 = Neutral
  then 0x52caa straddle read over rank 2 -> edx=50 -> call 0x226e4 (initial regen N=50)
=> PORT DEFECT FOUND: title.cpp speciesSetting default = 7 (k9 'Seven') where the
   VENDOR DEFAULT IS 5 (k7 'Five'). The B3 'content confound ours k9 vs vendor
   k7' is EXACTLY THIS — not a confound, a wrong default. Chip-row hypothesis
   REFUTED: painter-head chip loop 0x525eb..0x5264c binds to LITERAL 7
   (cmp eax,7 at 0x525f1) — all seven chips ALWAYS draw; only the white frame
   moves (cmp si, word[+0xb5] = player colour idx). Chip count does NOT follow
   the species wheel.
  call 0x22ce4(0x12e10, ebx=word[win+0xb1]hi=word[+0xb3] SELECTED RACE ROW,
               edx=word[win+0xb7]hi=word[+0xb9] SPECIES COUNT)   ; *** RACE ASSIGNMENT, NOT REGEN ***
  call 0x28fc0(0x7a360-law repaint)
  repaint self
  child[0]=[[win+0x67]+4]: child->obj+0x72 = count + 2 (0x52ec9) ; wheel art idx law
  child repaint
=> ANSWERS THE ASSIGNMENT'S FIRST QUESTION: PLAYERS_MORE does NOT re-run
   FUN_000226e4 (no star POSITION regen). It runs FUN_00022ce4 ONLY.
FUN_00022ce4 [verified decompile 2026-11-21, Ghidra :8089]:
  word[state+0xd88] = param_2 (= species count N)  ; *** THE PLAYER-COUNT FIELD (t441: n = word[STATE+0xd88])
  zero star-owner bits: loop i<NSTARS(state+0x3333): state+0xdc9+i*0x60..+0xdcc = 0 (star rec +0x14..+0x17 owner+OR words, t441 stride-0x60 law)
  zero anomaly bits: loop state+0x3357 stride 0x27 (anomaly table)
  clear 7 race-slot words (0x76490-family = 0xffff, 0x764a0+ = 0) + per-race visibility
  HOME-WORLD ASSIGNMENT: loop attempts local_24<=600 (or 0x1c2=450 if starcount<25):
    per player k<word[+0xd88]: star = state+0xdb5 + (FUN_0007824f() % starcount)*0x60  ; LCG rand
      if star+0x14==0: set +0x14 |= 0x80 | (1<<k); OR bit into +0x17 + every system rec (+0x2c array)
      else: sVar10-- (RETRY same player)
    then FUN_0002635c() per attempt
  post: FUN_0003e6bc per player (species pick, rand%0x15 distinct-check), FUN_000232ec,
    ability/homeworld tweaks by byte[state+0xdb4], relations reset (0x1b8 matrix, type 3/4/0xf arms).
=> VENDOR BEHAVIOR LAW (B2): species-wheel click KEEPS the star set (positions
   UNTOUCHED — 0x22ce4 never writes star x/y) and RE-ROLLS HOME-WORLD
   ASSIGNMENT: N = species count players each get a random distinct home star
   + OR visibility, species ids re-drawn distinct (rand%0x15 = 21 species),
   relation matrix reset. word[STATE+0xd88] = N is the player-count field.
PORT GAP: species click sets label+wheel art+chip frame only; no roster/ownership consequence modelled.

## MUTATION ROUND 2: 8/8 CAUGHT, ALL WITH NAMED VERDICTS (bug-1 fixed)
M1 wrap term (straddle pin :81); M2 count-table (:82); M3 guard-fallback
(wrap pin :92); M4 seed-no-gen wITNESS: h15 repeated 827d710cd0409ed0 x4
(the gen1/gen6 wrap pair + all frozen-seed rungs collide — exactly the
designed discriminator); M5 anchor-dy: density best shift (0,-1)!=origin;
M6 anchor-dx: atmos (-2,0)!=origin; M7 hash-no-gen: pure pin :132; M8
n-frozen: cosmos-n ['100'] != full sequence. AFTER-RESTORE rc=0, md5-ok x3.
Round-1 lesson banked: an agreement-at-best-shift metric is anchor-INVARIANT
(mutants just move the shift) — pin the SHIFT POSITION, not the agreement.

## B2 MUTATION 4/4 CAUGHT (scripts/tNGB2_mutate.py, round-1 clean)
S1 wrap term -> pin tngb_species_rank_cycle :137 (n 3..7 domain);
S2 wrap value -> :138 (visited sequence); S3 species-click-regen -> witness
'wheelgen [1,2,3,4]' (positions-preserved law, LOG-side); S4 default-seven
-> witness 'roster [3,4,5,6] != [6,7,3,4]' (word-sequence shift catches the
default WITHOUT needing pixels). AFTER-RESTORE rc=0 build=0, md5-ok x2.
HONEST NOTE: S4 was caught by the log leg before its anchor leg ran; the
anchor floor 87.0 (clean 88.8 vs old-k9 80.0) remains the designed pixel
backstop, unexercised by this run.
## B2 CLOSE-OUT

## B4 BEGIN-PRESS SCOPE (cycle 3, this session)
Assignment: tNG-B cycle 3 B4 begin-press -> settings-apply seam (last B seed).
Playcap unchanged (turn 1086 == floor, pid 1182156 alive) -> no re-sitting.
Re-read of the cited blocks (work/tNGC_paint526b4.asm):
- BEGIN PRESS 0x52a44..0x52b75: 0x52a60 mov eax,0x12e10; 0x52a65 xor ebx,ebx;
  0x52a67 call 0x238e8 WORLDGEN (ebx=0 CONFIRMED at call site — the wheel
  words are NOT args); 0x52a76 call 0x2351c(0x12e10, 0x2bf7); 0x52a80..0x52b16
  camera/matrix block on 0x7a35c; 0x52b3c/0x52b44 byte[win+0xbb] low byte ->
  byte[0x13bc4]; 0x52b50 call 0x23388(0x12e10); script arms 0x52b55..0x52b65;
  returns 0xffffffff.
- WINDOW-INIT BLOCK 0x52c3d..0x52c86 (NEW FINDING this session): init sets
  word[+0xb7]=2 / word[+0xb9]=5 / word[+0xbb]=1 (0x52c40/52c55/52c6b — the
  known defaults) AND THEN IMMEDIATELY RUNS THE DENSITY ARM + COLOURS:
  0x52c80 mov ebx,[ebp+0xb7]; 0x52c95 sar ebx,0x10 (ladder word); 0x52caa mov
  edx,[esp+eax*4-2] (chip-word -> T via ladder table); 0x52cb6 call 0x226e4
  (eax=0x12e10) = REGEN; 0x52ce4 call 0x232ec(0x12e10, edx=word[+0xb3]>>16)
  = COLOURS. => the vendor new-game state is ALREADY density/species-configured
  at window open; Begin does NOT apply window words — it re-runs WORLDGEN on
  the current state. HYPOTHESIS (b): the wheel settings reach play ONLY via
  the per-click 0x226e4/0x22ce4 arms; Begin's worldgen adds PLANETS to the
  existing star field (t295 S1: planets-per-star rng%5+1, home worlds, pop=2)
  and does NOT write star positions.
Probes: (1) Ghidra census byte[0x13bc4] consumers; (2) Ghidra census
state+0x27283 (the worldgen planet-total += site) writers/readers — does
0x226e4 also touch it / does double-worldgen double it; (3) confirm 0x238e8
never writes star position fields; (4) port delta: Begin builds the PLAY
campaign from wheel settings (vendor: play galaxy = worldgen(current state),
NOT the preview cosmos).

## B4 FULL ARM DECODE (this session, work/tNGC_paint526b4.asm lines 488-599)
- DENSITY arm 0x52db9: inc word[+0xb7]; if word[+0xb5]==5 -> word[+0xb7]=0
  (the noted odd cross-read, B1-banked); call 0x226e4(eax=0x12e10,
  ebx=word[+0xb7]>>16, edx=ladder[word[+0xb5]>>16]>>16, ecx=word[+0xb1]>>16).
- SPECIES arm 0x52e58: inc word[+0xb9]; if word[+0xb7]>>16==8 -> word[+0xb9]=3
  (the B2 wrap; NOTE the tested reg is the DENSITY word read via eax-after-
  inc quirk — B2 bank stands); call 0x22ce4(0x12e10, ebx=+0xb1>>16,
  edx=+0xb7>>16). NO state call for atmosphere.
- ATMOSPHERE arm 0x52eec: inc word[+0xbb]; if word[+0xb9]>>16==3 ->
  word[+0xbb]=0; refresh widgets ONLY — NO state-fn call. => atmosphere
  reaches campaign state ONLY via the BEGIN block 0x52b3c/0x52b44
  (byte[win+0xbb] low byte -> byte[0x13bc4]). THE B4 FINDING (i).
- WINDOW-INIT 0x52c3d..0x52ce4: defaults 2/5/1 THEN density arm inline
  (0x52cb6 call 0x226e4) THEN colours (0x52ce4 call 0x232ec) => state is
  density-configured at WINDOW OPEN, before any click.
- DISPATCH 0x52f49: cmp dx,0x1f7 -> species arm.

## B4 ATMOSPHERE CONSUMER CENSUS (offline, DONE — finding (ii))
byte[0x13bc4] is a LIVE OBSERVABLE GLOBAL, not decorative:
- diplomacy.md §17.1 [verified 0x43a99]: dip-on-attack subtrahend
  d = 10*(MOVSX(byte[0x13bc4])+1), doubled iff victim state==3; the port
  ALREADY consumes it (diplomacy.h:98 govByte param, campaign.cpp:2125).
- aicode.md:242/315: gov-type gate byte[0x13bc4]==2 arms AI behaviours.
- raceintro.h:16: the intro's gated section is on DAT_00013bc4 == 0/1/2.
- IDENTITY ID = 1: window-init default word[+0xbb]=1 (0x52c6b) AND
  byte[0x13bc4]==1 in 20/20 playcap saves (diplomacy.md §17.3). The wheel
  domain 0..2 (arm wrap 0x52efc) == the gate domain 0/1/2.
=> Begin press 0x52b3c/0x52b44 stores the ATMOSPHERE WHEEL into the gameplay
   global. The port's Begin currently drops it into the intro ONLY
   (beginAtmosphere -> runRaceIntro); the vendor ALSO sets the campaign
   subtrahend key. PORT DELTA: plumb atmosphere 0..2 into the govByte the
   campaign passes to applyAttackDipCost (vendor: wheel value verbatim).

## B4 VERDICT: DISPLAY==PLAY STATE-IDENTITY LAW (this session, cited)
- Click arms pass eax=0x12e10 — THE PLAY STATE BASE (0x52dd7 density,
  0x52e76 species; t295 S2 "state base is static"). Begin's worldgen
  0x52a67 reads that SAME base. => the wheel writes the PLAY state directly
  at CLICK time; there is no "apply at Begin" step for density/species
  (Begin passes ebx=0, reads no wheel words for them — honest negative
  scope (2) SATISFIED as state-identity, not as absence).
- 0x226e4 = STARFIELD regen (positions/owners) WITHOUT planets; 0x238e8 =
  WORLD (planet) gen over the current starfield (t295 S1: planet-total +=
  word[state+0x27283] after outer loop). New-game init 0x2142e+0x21438 is
  the same pair. Vendor play galaxy = state starfield (last click regen) +
  Begin's planets.
- PORT DEFECT NAMED: the port's Begin enters play on the PRE-BUILT campaign
  (buildCampaign ran with o.stars/6-AI before the screen) — the vendor's
  play galaxy/species count IS the wheel state. Fix = rebuild the campaign
  from the wheel settings on the Begin handoff (state-identity law).
- ATMOSPHERE POSITIVE LAW: Begin 0x52b3c/0x52b44 is the SOLE WHEEL->GLOBAL
  writer byte[0x13bc4] = byte[win+0xbb] (window-init 0x52c86 hardcodes 1
  independent of the wheel). Consumers cited: dip-on-attack subtrahend
  10*(gov+1) (diplomacy §17.1 — port kAttackDipGovByte=1 constant),
  aicode gov==2 gates, raceintro section gate. Port delta: govByte becomes
  a Campaign value (default 1 == shipped-scenario census 20/20), set from
  the wheel at Begin.

## B4 VERDICT ROUND 2 — BYTE-LEVEL ARM ARGS (this session, supersedes the
## sloppy arg notes above; work/tNGC_paint526b4.asm 488-599 re-read)
WINDOW WORD MAP (word slots; the dwords straddle pairs): dword[+0xb1]=
[word+0xb1|word+0xb3(chip idx)], dword[+0xb5]=[pad|word+0xb7 DENSITY RANK],
dword[+0xb7]=[rank|word+0xb9 SPECIES COUNT], dword[+0xb9]=[count|word+0xbb
ATMOSPHERE]. Each arm's wrap test reads its OWN word via the straddle dword
(B1's "the OTHER field" phrasing was the straddle, behaviourally wrap-ON-OWN;
t423c's "chip stores word[+0xb5]" is mislabelled — the store at 0x52d83 is
word[+0xb3], and the colours call 0x52ce4 reads word[+0xb3]).
- DENSITY 0x52db9: word[+0xb7]++; if word[+0xb7]==5 ->0 (wrap 5, own word);
  call 0x226e4(eax=0x12e10, ebx=rank, edx=hiword(dword[esp+rank*4-2])=rung,
  ecx=word[+0xb3] chip) — B1 STRADDLE LAW CONFIRMED ARGS.
- SPECIES 0x52e58: word[+0xb9]++; if word[+0xb9]==8 ->3 (wrap 8->3, own word
  via dword[+0xb7] sar16); call 0x22ce4(eax=0x12e10, ebx=word[+0xb3],
  edx=word[+0xb9] via dword[+0xb7] sar16). B2 LAW CONFIRMED ARGS.
- ATMOSPHERE 0x52eec: word[+0xbb]++; if word[+0xbb]==3 ->0 (wrap 3, own word
  via dword[+0xb9] sar16); NO state call; widget refresh only.
STATE-IDENTITY LAW [verified: every arm passes eax=0x12e10 == THE PLAY STATE
BASE (t295 S2)]: the wheel writes the play state AT CLICK TIME. Begin
0x52a44..0x52b75 passes ebx=0 to worldgen and reads ONLY byte[win+0xbb] ->
byte[0x13bc4] (0x52b3c/0x52b44; window-init 0x52c86 stores 1 unconditionally,
wheel-independent). => "Begin applies density/species" is FALSE (honest
negative, scope (2)); Begin's delta = the WORLD layer (0x238e8 planets over
the CURRENT starfield — the click-regen'd one) + THE ATMOSPHERE GLOBAL.
RACE-COUNT IDENTITY [verified t295 S1 + B2]: word[state+0xd88] (=0x13b98,
the census'd race count, ==4 in 20/20 shipped saves) = the species wheel
value N = TOTAL races INCLUDING the player. => owners = speciesSetting,
aiCount = speciesSetting-1 (NUMCONTROLS 7 caps at Seven).
PORT DELTA (decided):
 D1 menulaw.h pure atmosphereRankNext (wrap 3, domain 0..2; default 1 ->
    visited 2,0,1,...); title.cpp atmosphere click uses it (behaviour-
    identical to the old %3 — pure-law home for the pin).
 D2 ui.h NewGameApply out-param on runTitleScreen; Begin press fills
    {stars=rung, owners=species, govByte=atmosphere} + prints law line
    "ui newgame apply stars S owners O gov G".
 D3 main.cpp: on Campaign exit with apply set, REBUILD the campaign
    (starCount=apply.stars, cfg.aiCount=owners-1, cfg.govByte=apply.govByte)
    — closes the t393 named seam via the state-identity law; --resume / no-
    Begin paths keep the built campaign (defaults unchanged).
 D4 CampaignConfig.govByte (default kAttackDipGovByte==1 == shipped census
    20/20); campaign.cpp:2126 passes cfg_.govByte (was the constant).
 BEHAVIOUR CHANGE NOTED: default Begin now enters play with owners 5 (vendor
 default word 2/5/1) instead of the port's 7 — that IS the seam closing.

## B4 CODE LANDED + WITNESS GREEN (this session)
- menulaw.h: atmosphereRankNext (wrap 3) + NewGameSettings/newGameSettings
  pure law (identity map: stars=cycle rung, owners=species VERBATIM,
  gov=atmosphere VERBATIM). title.cpp: atmosphere arm uses the pure law +
  law line 'ui raceconfig atmos wheel G'; Begin fills newGameOut + prints
  'ui newgame apply stars S owners O gov G'. main.cpp buildCampaign takes
  an optional apply (aiWant=owners-1 cap 6 via NUMCONTROLS; cfg.starCount/
  govByte + mc.starCount from the triple); --ui rebuilds the campaign on
  Begin exit ('newgame live stars S owners O' line = LIVE terms) with an
  honest-degrade branch (apply FAILED -> play on the built campaign).
  campaign.h CampaignConfig.govByte (default kAttackDipGovByte); campaign
  .cpp:2126 passes cfg_.govByte. --resume / no-Begin: untouched defaults.
- PINS tngb_atmosphere_rank_cycle (wrap term, visited 2,0,1 from default 1,
  orb art k10..k12, off-domain refuse) + tngb_newgame_settings_identity
  (identity terms + UNSET default struct). run_tests 488/488, ctest exit 0.
- WITNESS scripts/tNGB4_begin_shot.sh + tNGB4_begin_witness.py GREEN first
  run: atmos 1->2; apply (75,6,2) == one click each wheel from the vendor
  defaults 2/5/1; live (75,6) == apply (pre-built was 50/7 — the rebuild
  provably took); intro atmosphere 2 rides the same wheel.

## B4 MUTATION 4/4 CAUGHT (scripts/tNGB4_mutate.py, round-1 clean)
T1 atmos wrap term -> pin tngb_atmosphere_rank_cycle :201 (domain 0..2);
T2 owners-minus-one -> pin tngb_newgame_settings_identity :234 (identity);
T3 apply-never-runs -> witness log leg (no 'newgame live' line);
T4 gov-not-plumbed -> witness live gov term (live (75,6,1) != apply
(75,6,2)). AFTER-RESTORE rc=0, md5-ok both files. LIVE-terms line extended
with Campaign::govByte() (campaign.h accessor added this cycle) so T4 is a
LIVE catch, not an intent catch.
