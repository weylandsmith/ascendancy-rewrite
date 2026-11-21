# t295 WIP — OQ-016 residue 2: setup-time HOME-DRAW law (debugger session)

Assigned: docs/STATE.md NEXT ACTION t295. Question: WHICH rng draw (stream
position + modulus) picks each race's home star, i.e. the consumer path from
CALL 0x7824f to the home-star store. Known join (t270): DWORD[0x12e1d+race*0x1ee]
== star base NAME-0x1C. t30c: run-local uniform over candidate stars (11
distinct sets / 11 lineages). Gap = the draw law.

## Plan (probe budget ~35)
1. STATIC FIRST (cheap, no launch): disassemble the scenario-init loop
   0x23a20..0x23d22 from work/ascend_payload.bin (payload offset == Ghidra
   addr, imagebase 0; file is 0x8cc83 = obj1 end, verified by size) with
   capstone 5.0.7 (/home/hrethric/tools/revenv/bin/python). Find every
   `call 0x7824f` in the range and what the quotient feeds.
2. If the static chain names the store -> one debugger session to witness the
   live values (BPLM sentinel + stop at the store), OR close statically if the
   cited addresses + a corpus check suffice.
3. Session only if needed: scratch work/r1/game-wp, NO resume.gam, own ring,
   Xvfb :96, core=normal, background=true notify=true.

## S1 STATIC — scenario-init loop disasm
(tool output below as I go)

## S1 STATIC — FUN_000238e8 = WORLD GENERATOR (full body disassembled, work/t295_loop_disasm.txt + work/t295_238e8_head.txt)

STATE BASE IS STATIC: call sites 0x214a3/0x214b5 do `mov eax,0x12e10` then
call 0x226e4/0x238e8 — the campaign-state base == DS image 0x12e10 (image
offset; runtime +P0). Cross-checks: state+0x3333 dword >>16 = 0x16143 = T
(star count, score.md S14 census T=50); state+0xd86 >>16 = 0x13b96 race
count; state+0xdb5 = 0x13bc5 = the 0x60-stride star-owner table (aicode P7);
race row k = state + 0xd + 0x1ee*k = 0x12e1d + 0x1ee*k == THE t270 HOME JOIN
(read at 0x23970, NOT written in this function).

FUN_000238e8(eax=state) structure (verified instruction-by-instruction):
 OUTER loop j = 0..T-1 over the star-owner table (tail 0x23d58: i++, ptr+=0x60):
  1. call 0x7824f; IDIV 5; +1; clamp<=5 -> [esp+0xf4] = NPLANETS(star) in 1..5
     (draw @0x23da4, mod5 @0x23db3) — NEW LAW: planets-per-star = rng%5+1.
  2. race scan 0x23955..0x23975: find FIRST race row k with
     DWORD[row+0xd] (home star ptr) == &cand[j] -> [esp+0x108]=k else -1.
     (walker 0x23946 `add eax,0x1ee` from base state.)
  3. 0x2399b: if matched (ecx>=0): call 0x7824f; IDIV NPLANETS ->
     [esp+0xf8] = HOME-PLANET-INDEX k0 = rng % nplanets. No match -> 0, no draw.
  INNER loop k = 0..NPLANETS-1 (0x23a7c head, tail 0x23d1a cmp ebx,[esp+0xf4]):
   per planet: ebp += 0x7b (123B planet stride);
   call 0x7824f; IDIV 5 -> SIZE (edx param); call 0x7824f; IDIV 11 -> ROW;
   (0x23a86/0x23a97; param mapping via 0x23b38 mov ax,dx -> ebx=ROW, 0x23b40
   mov dx,bx -> edx=SIZE, call 0x37d80 @0x23b49 — T36 confirmed.)
   SPECIAL-FIRE gate 0x23aaa: [esp+0x108]>=0 && [esp+0xf8]==k  ==  THIS IS THE
   HOME PLANET (k-th planet of a host star when k == draw k0). REINTERPRETS
   T30's "special scenario mode": NOT scenario mode — per-race home build.
   Then tables: mov dl, byte[ MATCHED-RACE-ROW + 7 ] (eax=[esp+0xe4]=
   state+[esp+0x108]*0x1ee — a race row, NOT a star; T30's "byte[STAR+7]"
   mislabel corrected); tableA@payload 0x63e0 -> esp[0..20] -> EBX = ROW;
   tableB@payload 0x6434 -> esp[0x54..] -> EDX = SIZE (0x23ac9/adb rep movsd).
   (T30's 0x88f90/0x88fe4 pair = same two tables seen in the restored image;
   payload offsets verified THIS pass by capstone on ascend_payload.bin.)
  Home-planet extra block 0x23c7c..0x23cb2 (same gate): byte[planet+0x57] :=
  [esp+0x108] (owner race), word[planet+0x42] := 2 (pop==2 law!), then
  EBX=0xffffffff EDX=5 CALL 0x38818 = the CB picker (t42 law) — CORROBORATES
  t42 item 1 "home seed @0x23ca2" and ties pop:=2 to the same store.
  Also per planet: [state+0x1c + 4*m] := planet-pool ptr (0x23a83 mov
  [eax+0x46] is race row+0x46 := pool head ebp; [esp+0xfc] array),
  0x5a/0xc/0xe header inits, 0x39a84 call, 0x5324c (x87 float rand? — the
  fild/fmul block 0x23bb5..0x23c70 feeds 0x5324c, star POSITION jitter).
  After outer loop 0x23d22: add word[state+0x27283], ax (planet total).

GAP REMAINING: the STORE into race row+0xd (home star ptr). 0x12e1d-immediate
census = 10 sites, ALL loads/cmps (16622,21ea8,2528a,252b4,29a83,43d02,4d051,
5061c,516d7,516f6) — the writer must use the state-base+0x1ee*k pattern.
NEXT probe: census `mov [reg+0xd]` 32-bit stores + dump new-game caller head
0x21300..0x21560 + 0x226e4 subcalls (0x22878/0x22728/0x234a4).

## S2 — setup chain structure (new-game path, all [verified disasm])

New-game caller (FUN_00021300? entry ~0x21284, has 0x92d/0x937 assert strings):
 0x2142e call 0x226e4(eax=0x12e10, ebx=0x32(T=50), edx=7, ecx=0)  [new game]
 0x21438 call 0x238e8(eax=0x12e10)
Scenario path: 0x21442.. reads file via 0x77fe1(0x998,...) then 0x214b0 call
 0x226e4 + 0x214ba call 0x238e8. Third caller 0x52a67 (scenario-mode loader,
 near 0x52678) — NOT the stock new-game path.

0x226e4(eax=state,edx=7,ecx param,[esp+0x26]=count): four subs:
  0x22878: FILE PARSE (0x206c0 open, 0x776dd read-record loop x<=100 stride
    0x14, sprintf 0x76c79 fmt 0xb42, fclose 0x773be). ZERO rng calls.
  0x22728: STAR POSITION GENERATOR — per star: rng%[esp+0x1c] (0x227d7) and
    rng%600-300 (0x22804); writes x/y floats at state+0x3067e stride 0xd,
    flag byte state+0x3067d; constants 1000.0f/300.0f. NEW LAW candidate.
  0x234a4: memset state+0x3337 (0x168c), word[state+0x49c3]:=0, call 0x23e00
    (LANE GENERATOR: nearest-star via sqrt 0x76da0, add lane via 0x21ad8
    which writes dword[star+0x2c+4*n] + inc word[star+0x44]), word
    [state+0x32dd1]:=2, word[state+0xdbb+0x60j]:=0xffff all stars, then
    0x24018, 0x2446c (NOT YET DUMPED).
  0x22ce4: RESET — word[state+0x306fc]:=-1, byte[state+0x30700]:=0 (the
    t290/t292 selector pair!), word[state+0xd88]:=race count, zeroes
    byte[state+0xdc9..0xdcc+0x60j] (star owner bytes) for all stars, zeroes
    byte[state+0x3357+0x27j], loads research tree 0x46870, clears 0x76492/
    0x764a0, and CRITICALLY: per race row (imul 0x1ee) `mov edx,[esi+eax+0xd];
    mov byte [edx+0x14],0` — READS home ptr row+0xd and zeroes star+0x14.
    => HOME POINTERS row+0xd ARE ALREADY SET BEFORE 0x22ce4 RUNS. The
    0x32dd3 threshold word = 600 (T>=25) / 300 (T<25) — banked bonus.
STATE BASE CONFIRMED STATIC 0x12e10 image offset (race rows state+0x6 stride
0x1ee; home ptr at row+0xd == 0x12e1d+0x1ee*k == t270 join verbatim).

MYSTERY: image-wide store census for dest '+ 0xd]' dword = ZERO hits; lea
[reg+0xd]->store window = zero. The row+0xd writer is NOT statically
displacement-addressable (register-computed base or memcpy/rep movsd class) —
same writer-census-blind class as score.md S9. Candidates left: 0x24018,
0x2446c (dump next), 0x22878's parse (no rng — can't be the DRAW, could be
the template), or a data-driven clone. NOTE 0x22878 has ZERO rng: if homes
came from that file parse, t30c run-locality would be REFUTED — it is not,
so a DRAW-writer exists in 0x24018/0x2446c or the setup chain is deeper.

## S3 — THE STORE FOUND: FUN_00022ce4 0x22eb4..0x22f55 = HOME-STAR DRAW + STORE
(linear sweeps MISSED it — capstone desync at 0x22e49 junk; function-aligned
disasm from functions_full.tsv FOUND it. Lesson: census per-function, not raw
linear. The score.md S9 'zero statically-encodable writers' class may partly be
THIS desync bug — note for future hunts, do NOT re-open S9 itself.)

HOME-STAR DRAW LAW [verified disasm, work/t295_22ce4 region dump]:
FUN_00022ce4(state) — called 0x2271e inside setup 0x226e4, BEFORE world-gen
0x238e8 (order at 0x2142e/0x21438). Pre-clear loop 0x22d25..0x22d5f zeroes
byte[entry+0x14..0x17] for ALL T stars (0xdc9-0xdb5=0x14).
Draw loop 0x22e82 head per race k = 0..word[state+0xd88]-1:
  0x22eb4 mov ebx,[state+0x3333]; sar 0x10      ; T = star count (50)
  0x22eba call 0x7824f                           ; ONE rng draw (0..32767)
  0x22ec7 idiv ebx                               ; edx = r % T
  0x22ec9 imul edx,0x60; add edx,ebp             ; ebp = state+0xdb5 -> entry
  0x22ed3 imul eax,0x1ee; add eax,esi            ; race row = state+0x1ee*k
  0x22edd mov [eax+0xd],edx                      ; *** HOME STAR PTR STORE ***
  0x22ee0 bl = byte[entry+0x14]; if != 0: 0x22ee7 dec [esp+0x14] (retry SAME k)
  accept 0x22eee: entry+0x14 := (old|0x80); |= (1<<k)  ; bit7 HOME MARKER
                  entry+0x17 |= (1<<k)
                  row+6 := k                     ; 0x22f08
  0x22f3a..0x22f37: per lane i of home star (bound word[home+0x44]=lane count):
                  lane=[home+i*4+0x2c]; byte[lane+0x20] |= 1<<k;
                  byte[lane+0x16] |= 1<<k; byte[lane[+4]+0x16] |= 1<<k
                  (home LANES visible to race k at setup — corroborates t195.)
LAW = uniform rejection sampling over ALL T stars in race order, distinct by
construction (owner-byte gate). rng%50 over 0..32767 -> indices 0..17 have
656/32768, 18..49 have 655/32768 (idiv remainder semantics, slight real bias).
PUMP CAVEAT: head 0x22e06 re-enters the whole pre-clear+draw block until
word[state+0x32dd3] (lane count) >= 600 (300 if T<25) via 0x22f57 call 0x2635c
pump; the LAST pass wins, distribution law unaffected. [first pass skips
pre-clear: [esp+8]==0 gate at 0x22e17]
SECOND HALF (home PLANET within star) = S1 0x239af draw rng % nplanets.
t270 join row+0xd == star base NAME-0x1C: entry = state+0x13bc5+0x60*j, entry
dword+0 = star record ptr; consistent (t270 resolved via name join).

CLOSURE EVIDENCE PLAN: static chain UNAMBIGUOUS (one store site image-wide,
function-aligned census of all 1144 funcs = only fn@22ce4 writes [reg+0xd]
dword in the campaign-state window class). Live values via CORPUS census
(pointer law, same class as t270/t294): per trusted save verify (a) distinct
home indices (b) bit7 marker on home entry +0x14 (c) owner bit == race (d)
index uniform over 0..T-1. Debugger session NOT needed; task's caveat allowed
stopping at an unambiguous chain + banked trace.

## S4 — FULL LAW PINNED (corrections + sub-laws)

ADDRESS ARITHMETIC RECONCILED: state base = image 0x12e10 (phys 0x254e10 =
the banked TURN-counter phys — self-confirming). Star-owner records ARE the
star records: entry(j) = state+0xdb5+0x60j; NAME0 = state+0xdd1 = entry(0)+
0x1C, so base(k)=NAME(k)-0x1C == entry(k) EXACTLY (t270 join, now derived).
[t441 CORRECTION: the record BASE is state+0xd8d+0x60j — the stored row+0xd
home pointer lands there; state+0xdb5 is the record's +0x28 field, so every
disp8 above must be re-based by -0x28 when read from +0xdb5 (marker +0x14 ->
base+0x3c, bitset +0x17 -> base+0x3e, name +0x1c -> base+0x44). Verified
50/50 star records + all four homeptrs in bank-t251-live1255/45.sav;
scripts/t441_race_table_census.py. The DRAW LAW itself is unaffected.]
word[state+0xd88] = RACE COUNT (0x13b98, diplomacy loop bound);
dword[state+0x3333] hi word = T.

CALL ARGTRACE CORRECTION (0x2141d..0x2142e): ebx=7 (races), edx=0x32 (T=50),
ecx=0 -> 0x226e4(state, ebx=races, edx=T). Inside: 0x22719 movsx edx,di gives
0x22ce4 edx = 7 -> `mov word [state+0xd88],dx` = 7. Consistent with corpus +
diplomacy. (Earlier reading 50 was MY misread of the mov ebx,7 / mov edx,0x32
pair; corrected here before landing.)

HOME-STAR DRAW LAW (FUN_00022ce4, cited):
  head 0x22d1e..0x22d5f: byte[base(j)+0x14..0x17] := 0 for ALL T stars.
  pump loop 0x22e06..0x22f67 (repeats until word[state+0x32dd3] lane-count
  >= 600, T>=25; 300 if T<25; 0x2635c lane pump has ZERO rng — pass count is
  lane-geometry driven, homes RE-DRAWN every pass, LAST pass wins):
    for r = 0..word[state+0xd88]-1:
      loop: call 0x7824f; edx = r_draw % T (idiv @0x22ec7);
            entry = state+0xdb5+0x60*edx
      gate 0x22ee0: if byte[entry+0x14] != 0 -> retry SAME r (dec/inc 0x14 slot)
      accept: byte[entry+0x14] |= 0x80; |= (1<<r)   ; bit7 home marker + owner
              byte[entry+0x17] |= (1<<r)
              row_r+6 := r   (0x22f08; row_r = state+0x1ee*r, home ptr at +0xd)
              per lane i of home star (bound word[home+0x44]):
                byte[lane+0x20] |= 1<<r; byte[lane+0x16] |= 1<<r;
                byte[lane[+4]+0x16] |= 1<<r   (0x22f1a..0x22f37)
  => UNIFORM rejection sampling over all T stars in RACE ORDER; distinct by
  construction. idiv bias: indices 0..(32768 mod 50 = 17) get 656/32768,
  others 655/32768 — 0.15% real bias, undetectable corpus-wide, noted honestly.

HOME-PLANET SUB-LAW (FUN_000238e8): nplanets(star) = rng%5 + 1 (0x23da4/
0x23db3, clamp 1..5); home planet = k-th planet where k = rng % nplanets
(0x239af/0x23c0 draw gated on star-owner match) -> orbit index uniform over
1..nplanets. Testable prediction: home-planet orbit distribution.

CENSUS PREDICTIONS (early trusted saves, turn>=1):
 P1 distinct home indices per lineage (known t30c, re-verify at index level)
 P2 byte[home(k)+0x14] == 0x80|(1<<r) EXACTLY pre-colonisation (old=0 path)
 P3 home indices ~uniform over 0..49 (chi-square)
 P4 home-planet orbit ~uniform over 1..nplanets

## S5 — CENSUS VERDICT (scripts/r295_home_draw.py, corpus run 2026-11-04)

36 analyseable save-rows (10 fresh fresh-game lineages r1deep/r1ad + banks;
12 distinct ks-sets — banks all share the production campaign ks {2,18,25,27}).
  P1 distinct home indices: TRUE 36/36 (rejection gate holds corpus-wide).
  P2 EXACT-EQUAL byte[home+0x14] == 0x80|(1<<race) at turn<=2: TRUE 30/30.
     Late-turn exceptions (production race3 home own=0x1) = conquest: the +0x14
     byte is the LIVE-planet OR (t246/t248/t270 law) — race3 lost its home
     world in the production campaign; draw-time law untouched. Honest note:
     bit7 clearing on conquest is a consumer behaviour, NOT the draw.
  P3 index uniformity (lineage-deduped n=57 over T=50): chi2=31.0, df=49,
     crit@.01=74.92 -> UNIFORM NOT REJECTED (raw pooled chi2 755 was pure
     production-bank duplication — de-dupe law re-confirmed, t42 §6 lesson).
  P4 home-planet orbit uniform over 1..nplanets: obs {1:24,2:11,3:11,4:7,5:1}
     vs exp {24.6,12.6,9.6,5.2,2.0}, chi2=1.5 (df~4, crit 13.3) CONFIRMED.
     (Raw pooled {72,35,11,7,1} was bank duplication again.)
  P5 nlive in 1..5 everywhere: consistent with nplanets=rng%5+1.
CLOSURE BAR MET: cited addresses (0x22eba draw, 0x22ec7 mod T, 0x22ee0 gate,
0x22edd store, 0x22eee marker, 0x239af planet draw) + live-RAM measurement via
pointer law. No debugger session was needed (static chain unambiguous:
function-aligned census shows FUN_00022ce4 is the ONLY writer of [reg+0xd]
dword into the race-row window image-wide).
HARNESS LESSON (worth keeping): raw-linear capstone sweeps DESYNC on junk
bytes and MISS instructions (0x22e49 desync hid the home store all session;
the score.md S9 'zero writers' class may be partly this bug — future writer
censuses MUST iterate per-function from functions_full.tsv).

## S6 — REWRITE UPGRADE + FIXTURE RE-DERIVATION (in flight)

campaign.cpp pickHomeStars REPLACED (was max-min BFS MISMATCH) with the cited
draw: race-ordered loop { homeNext()%n } until unclaimed; new isolated stream
homeLcg_ = cfg.seed^0x295 (t195 visLcg_ precedent — provably cannot perturb
worldLcg_/rng_). run_tests now takes an optional name-substring arg.

FAILURES 23 CHECKS in 5 TESTS, all re-trajectory/re-class:
 1 campaign_total_owned_grows (seed 42 Extinct t20 now — lethal layout; pick
   surviving seed).
 2 campaign_colonised_plan_gets_colony_base_t41 (seed 2024: AI home s29 CB
   DEMOLISHED by cited t202b law — global "every owned star has CB" was an
   old-trajectory artefact; REWRITE TEST to pin the cited event-time law:
   colonise => exactly one CB AT THAT MOMENT).
 3 campaign_build_queue_law_oq016 (seed 42 dead at t20 < Factory t31; seed 7
   verified alive, completion cadence unchanged t16 per passing t274 pin).
 4 campaign_visibility_law_oq026_t195 (hand-built 5-star chain, cfg.seed
   4242 -> homes no longer {0,4}; scan says salt-0x295 seeds {1,23,45,63,77,
   102,112,150,165,182,225,242} give [o0=0,o1=4]; use 23).
 5 species_cornucopia_repaints_min_pop_colony_t281 seed-8 leg (home no longer
   on terrainRow 10; SCAN for a row-10-home seed with no eligible alternative
   at t150).
HOME LAYOUTS NEW LAW: seed 7 o0=21 o1=4 o2=37 o3=33 o4=39 o5=8 o6=27;
seed 42 o0=31 o1=28 o2=27 o3=42 o4=17 o5=24 o6=36; seed 2024 o0=42 o1=29
o2=8 o3=0 o4=2 o5=21 o6=44.

## S7 — FINAL (session 2026-11-04, t295 COMPLETE)
pickHomeStars() replaced with cited law; homeLcg_ isolated stream. Fixtures
re-derived by MEASUREMENT (seed scans, diagnostics then deleted):
t41 CB test (structural per-colonise CB), campaign_total_owned_grows seed
42->7 (42 now Extinct t20 — lethal layouts are real under uniform draws),
build-queue seed 42->7, visibility chain seed 4242->23 (homes {0,4}),
cornucopia seed-8 leg -> seed 10 (row-10 home; MUTATION: deleting skip leg
fires event), t274 pin t16->t31 (MUTATION: >= -> > slips exactly to t32).
run_tests 175/0. PLAYTHROUGH regenerated: A seed2024 Extinct t285, B seed23
CONTROL t1406 (new exemplar; seed 1 re-drew Extinct t266), C seed13 Extinct
t485; record_playthrough.sh seeds updated. OQ-016 residue 2 CLOSED in ledger.
