# _wip_tPLD1 — HOME PLANET BY RACE (D26)

Task: STATE.md NEXT ACTION tPL-D1. D26 verbatim (docs/DECISIONS.md:693-694):
"I started a game with the Chamachies, and the home planet is wrong - wrong
art, wrong max population."

Assignment split (STATE.md 2026-11-24):
 - D1-a (cheap, FIRST): does the vendor home world carry a DIFFERENT seeded
   capBase than the corpus law nb/3+5 (income-law.md S10 t29/t33)? Measure on
   the save corpus before any debugger leg.
 - D1-b: fixed TABLE vs RNG-at-seed for the home-planet law -> debugger on a
   scratch new-game as Chamachies (scratch savedir law; protected saves
   01/02/03/04.SAV + RESUME.GAM untouchable). Cross-check Minions.

## P0 Context banked from disk (before probing)
- t270 [docs/re/mapgen.md S t270, KEEPER scripts/r270_homeplace.py RC=0]
  already MEASURED the home STAR law: race-row dword DWORD[data 0x12e1d +
  race*0x1ee] == phys of star base (NAME-0x1C, stride 0x60); home == k;
  RUN-LOCAL RANDOM not template (11 distinct home-star sets / 11 lineages);
  home planet ORBIT varies (I..V) = race's FIRST COLONISABLE planet per the
  t40/t42 picker law. So "fixed table for the star" is already REFUTED by
  measurement; what remains open is (i) the capBase on home worlds and
  (ii) what "wrong art" means concretely (home-planet disk art on the
  strategic map vs surface classes on the planet view).
- capBase law: +0x55 = NONBARRENCOUNT/3 + 5 @0x37f84..0x37f9e (verified
  38772/40318); modifiers: item37 Lush Growth +10 once @0x39212, ability-9
  SA_MoreMaxPop +2 every owned planet @0x4402a (dispatcher al=9 @0x41d8...
  cite: 0x441d8 table).
- REFUTED guards relevant: R-tNGS3c (dbg build input-deaf at fresh Xvfb —
  NEWGAME dynamic questions go to PRODUCTION binary + frames; debugger legs
  valid in-game state==3); R-t422c (only RNG = BCPP LCG 0x7824f; new-game
  init cluster 0x24f4b).
- Ring: production dosbox-x alive (sitting script exit 0, newest t=1335);
  ring TL expires 2026-11-24 14:53 — recovery pattern t439 if needed.

## P1 (in progress) corpus capBase-by-home measurement

## P1 MEASURED (scripts/tpld1_homecap_census.py, work/r1/tpld1_homecap.out)
- HOME capBase seed law is the SAME law: cap55 == nb/3+5 on 144/144 home
  worlds (26 fresh lineages, earliest save each). NO special home cap seed.
  The max-pop half of D1 does NOT fold into a different seeded capBase.
- Home worlds are LARGE-biased: home size-class hist spans 17..73 cells
  (mode 45/54/55; barren share 36.0%) vs non-home 47.2% barren and a full
  0..73 span. Homes never class-0 (0 cells) — but that census used the
  earliest save WITHOUT the turn>=1 trust-law filter, and per-race rows
  (owner-byte index) showed race0 homes cells=73 in 26/26.

## P2 SIGNAL (scripts/tpld1_race_join.py, work/r1/tpld1_racejoin.out)
owner-index -> specnum join via race rows (STATE+0x12e10 stride 0x1ee, +7
specnum) + raceNN.dip names. Per-SPEC home sizes look CONSTANT across
independent lineages: Minions always 73 (n~26 incl. template), Kambucha 73
x4, Arbryls 73 x4, Marmosians 45 x3, Chamachies 45 x3 (Syzygifer I,
Corncob I, Masticon I; Chloros III 45 at a turn=0 save), Orfa 45
(Corpuscle I + template Stavern I 45). Planet NAMES vary per run; SIZE
does not. HYPOTHESIS: the home SIZE CLASS is a per-race fixed table entry
(the race row itself), while star placement + terrain draw stay RNG (t270).
If true this explains BOTH D26 halves at once: the port draws home size
uniform rng%5 (campaign.cpp:166), so the player's home gets the wrong size
=> wrong art AND a different nb => different capBase/max-pop.
CAUTION: 125117's save is the static-init template (t270 names Xerxes I /
Stavern I / Hannibal III / Gasball V / Burphee III / Hurble I / Vishnu IV);
turn=0 saves need the trust-law filter before counting.

## P3 NEXT (decisive): aggregate turn>=1 homes per spec; scan race-row byte
offsets for a field == home size class / cells; cross-check the static
template in the payload data segment.

## P4 TABLE FOUND (payload scan, decisive)
work/ascend_payload.bin @0x88f90 21 u32 = (4,4,3,4,3,4,3,3,4,3,3,3,4,4,4,3,4,3,2,3,3)
  == per-SPEC HOME SIZE-CLASS INDEX into surfaceBySize {7,11,23,45,73}.
  Matches ALL 85 measured homes (20 specs): spec0 Minions 4->73 (17/17),
  spec19 Chamachies 3->45 (6/6), spec18 Chronomyst 2->23 (2/2), ...
  Predicts Hanshaks (spec4, absent from corpus) = 3 -> 45.
@0x88fe4 21 u32 = (5,1,1,6,3,2,8,6,4,4,10,2,7,8,9,7,3,5,3,7,9)
  == the SECOND 21-dword table of t30 (restored file 0x88fe4 -> esp[0x54..],
  indexed together with 0x88f90 by `MOV DL,[EAX+7]` @0x23aeb). Values 1..10
  fit the terrain weight-row domain; VERIFY == home planet +0x16.
t30 read [EAX+7] as "byte[STAR+7] cluster" — star record +4..+7 is the idx
u32 (t270), so byte+7 is always 0 for stars; race row +7 == specnum (t441
verified). EAX is the RACE ROW; the tables are SPECNUM-keyed. [inferred from
two verified field laws]
Law (D1): vendor home planet SIZE CLASS and TERRAIN ROW come from these
static per-spec tables, not the rng%5 / rng%11 feeds (t30: the r2%11 EDX is
destroyed @0x23ae7). Constancy 85/85 per spec across independent lineages.

## P5 LAWS CLOSED (cited measurement, 26 independent fresh lineages, 85 homes)
D1-A HOME SIZE + TERRAIN TABLE (fixed TABLE, not RNG-at-seed):
 - payload 0x88f90 21 u32 T1=(4,4,3,4,3,4,3,3,4,3,3,3,4,4,4,3,4,3,2,3,3)
   home SIZE-CLASS index into surfaceBySize {7,11,23,45,73}:
   T1[spec]==home size idx 85/85 (incl. Chamachies spec19 -> 3 -> 45 cells,
   6/6 lineages; Minions 4->73 17/17; Chronomyst 2->23 2/2).
 - payload 0x88fe4 21 u32 T2=(5,1,1,6,3,2,8,6,4,4,10,2,7,8,9,7,3,5,3,7,9)
   home TERRAIN weight row: T2[spec]==home +0x16 85/85.
 - KEY is the RACE specnum (row+7, t441), NOT a star cluster: the row byte
   functional scan found ONLY row+0x07/0x1a3/0x1cd size-functional, and
   0x1a3==specnum, 0x1cd==NEG_PLAYER_TURNS (dip values) — no home-size field
   lives in the race row itself; the tables are read at scenario init.
 - Non-home planets span the full rng distribution (barren 47.2%, sizes
   0..73) — the table path is HOME-ONLY. Home nb/barren/CB-cell stay RNG
   (nb varies per run within the row's shares).
 - t30 INTERPRETATION CORRECTION CANDIDATE: t30 read `MOV DL,[EAX+7]`
   @0x23aeb as byte[STAR+7] cluster (star idx u32 @base+4 -> byte+7 always 0
   for stars per t270, so a star reading would be constant 0; the per-spec
   constancy proves the EAX operand is the race row / specnum). The t30
   "special mode" gate note stays banked unresolved; the shipped-scenario
   measurement IS the table path in 26/26 fresh games.
D1-B HOME MAX POP: NO special seed. cap55==nb/3+5 on 144/144 home worlds
  (P1). The D26 "wrong max population" is a CONSEQUENCE of the wrong home
  size class (port drew rng%5; Chamachies must be 45 cells -> nb ~33-37 ->
  capBase 16-17, while an rng size-0/1 home yields 5-9).
