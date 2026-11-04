# WIP t201 — AI gap rows 3+4: threat-byte INPUT + emergency chain

Trigger triage (measured this session): timeline size 5,721,578,066 ==
frozen baseline, mtime 2026-10-29 13:22:12.10, dosbox-x not running, tree
clean at 8ac9dd8. No sitting -> proceed with STATE NEXT t201.

## S0. In-hand citations (do not re-derive)
- Evaluator FUN_0003fc4c (forced-emergency items) inside AI build selector
  region 0x3f130..0x3f757 (income-law.md S9): item 18 Surface Shield chain
  `IND>=4 && PROS>0 && (+0x1c)-(+0x20)>=3 && threat byte[planet+0x59] < 6`;
  item 19 Surface Mega Shield `(DAT_00012e10 - [planet+0x67]) / period >
  threat`, period {200,225,300,400} by threat class 0/1/>=4 "@0x45beb stride
  law". Full body banked work/ai_selector_disasm.txt (per income-law S9).
- Planet record stride 123; known fields pop+0x42 RES+0x46 IND+0x44 PROS+0x48
  cap+0x4a used+0x4c owner+0x57 buildprog+0x50 target+0x52 pending+0x54
  (income-law S6/S9, planets-ui S2/S4).
- DAT_00012e10 = day counter (t183: no autonomous obj0 tick).
- DAT_00045beb folds data+0x32ddb = 100-linear hop matrix (t190 e) — SAME
  base the S9 note cites for the period lookup: must verify whether the
  threat-period read really uses this base or a nearby table.
- Gap map: ai-dossier.md S8 row 3 (threat input) + row 4 (demolish channel —
  t202 half, NOT this iteration).

## S1. Findings

### S1a. Emergency chain body re-read from the BANKED DISASM
(work/ai_selector_disasm.txt lines 600-870; FUN_0003fc4c spans
0x3f758..0x3fc4a? no — 0x3f758 = special-project gate FUN_A, 0x3fc4c
region; the "evaluator" t28 banked is the sequence below.)
SUPERSEDES income-law.md S9's parenthetical "period 200/225/300/400 by
threat class 0/1/>=4 lookup @0x45beb stride law" — the disasm shows NO
literal 200/225/300/400 anywhere in the region (grep over the whole banked
listing: zero hits). Measured structure [verified from banked disasm]:

 CHAIN-2 (Surface Mega Shield, item 0x13=19) @0x3f9aa..0x3fa68:
  gate: word[planet+0x1e] >= 2  (0x3f9ac; NOTE chain-3 gate is ALSO >=2 at
    0x3f890 chain-1-style idiv-2, while income-law S9 said jl for one —
    re-read below)
  hop = byte DAT_00045beb[ hopIdx(starOf(planet)) *15? ][...] — 0x3f9cf..
    0x3fa14: edx = f([planet+0xa]>>16) with *5<<5 (=*160)  -> star idx*0x60?
    (0x13bc7 table => star OBJECT ptr), then g(idx)*5*8<<2? -> hop-matrix
    row stride; [0x45beb + row + col] = hop count (t190: stride-100 linear
    matrix folded DAT_00045beb).
  period := (hop < 3) ? (3-hop)*2 : 0     [0x3fa19..0x3fa28]
  threat := byte[planet+0x59]; if 0 -> STORE 1 (0x3fa36) then reread
  ratio  = (IND(+0x44) + RES(+0x46)) / threat   [signed idiv 0x3fa52]
  days   = ([ctx+0x1a8]>>16) - [esp]   ([esp] = ? — set 0 at 0x3fa0a? NO:
    0x3fa28 overwrote [esp] with period! so days = (ctx+0x1a8>>16) - period?
    RE-READ CAREFULLY: 0x3fa0a mov [esp],ecx(=0); 0x3fa28 mov [esp],eax
    (=period). 0x3fa5e mov esi,[esp]; 0x3fa64 sub edx,esi -> days =
    (ctx+0x1a8>>16) - period. NOT (day - stamp)! [ctx+0x1a8>>16] is some
    accumulated counter (race ctx dword) — ID OPEN.
  fire iff ratio > days. Then candidate loop 0x3fa73: template list
    byte[esp+eax+0x10], eax<2 -> RUNTIME 5-entry list @0x89360
    (0x3f9c3 mov esi,0x89360; 3 movsw+movsb copies 5 bytes) — the REAL
    emergency template list. Legality = research mask bit(owner) on restree
    row (0x3fa84..0x3faa6 pattern: item*0x28 -> [0x73e45] -> *0x4b ->
    [0x7478b]>>24 & (1<<owner)).
  Buy path: first template item ABSENT from slots (0x3958c==0xffff) -> buy
    @0x3faeb; if all present, rng%bx pick one @0x3fb03..0x3fb20 (buy even
    if occupied? 0x38818 dl=item).
 CHAIN-3 twin @0x3fb33..0x3fc40: identical shape with byte[planet+0x58]
    clamp-store 1, threshold hop<3->period*2, ctx dword +0x1aa, template
    list at [esp+0xc] (copied earlier? locate), fires buying via 0x38818.
 CHAIN-1 (Surface Shield item 0x12=18? — 0x3f88e block uses edx=0x19=25!)
    @0x3f88e: gate word[+0x1e]>2, owner%2==0, IND>0x14 (20), rng%100<3,
    FUN_0003830c(0x19) legal, slot 0x3958c(0x19)==0xffff -> buy 25.
    This is item 25 (Orbital Cloaker? per income-law chain names) NOT 18!
    @0x3f91c block: owner%3==0 (idiv 3, je when remainder==0), IND<=0x19
    (25) jle skip?? (cmp eax,0x19; jle 0x3f9aa -> skip when IND<=25)
    rng%100<2, item 0x18=24 legality+absent -> buy 24.
  => income-law S9's summary mapped these chains sloppily; the RAW disasm
     is the authority. Threat bytes +0x58/+0x59 clamp-store 1 and divide
     IND+RES: they are DIVISORS, higher threat -> smaller ratio -> HARDER
     to fire? or ratio > days means LOW threat fires easily.

 STILL OPEN before writing anything: [esp] semantics at the sub-blocks,
 what [ctx+0x1a8]/[ctx+0x1aa] are (race context stride? the ctx passed by
 caller 0x3eade = EAX at 0x3f13b stored esp+0xc4), and the identity of the
 RUNTIME list 0x89360 + the [esp+0xc] template for chain-3.

### S1e. THREAT-BYTE INPUT LAW MEASURED (gap row 3 ANSWERED)
Writer census (scripts/r201_threat_writers.py RC=0, obj0 byte-wide
disp32∈{0x58,0x59}, capstone-resume pass — t201 PITFALL: sequential
capstone stops at first data gap, coverage ended 0x1ca34 of 0x82bb0;
resume-by-1-byte fixes it; 325 sites found vs 36 blind):
  planet-record writers EXACTLY: FUN_00038ba4 recalc exits 0x38ef7 (+0x58
  from local [esp+0x24]) and 0x38efe (+0x59 from local [esp+4]); evaluator
  self-inits 0x3fa36 (+0x59:=1 if 0) and 0x3fb3e (+0x58:=1 if 0); save
  materialiser FUN_0003a558 copies stack args (round-trip only).
  RECALC RE-ZEROES BOTH EVERY RUN (xored @0x38baf stored to BOTH locals
  0x38bd0/0x38bd8) — the bytes are PURE DERIVED COUNTERS, not accumulated.
LAW (read from recalc disasm work/t201_recalc_scan.txt; slot loop
0x38c7d..0x38c85 over word[sys+0x1a], item byte1, ACTIVE = word[slot+2]
bit0 @0x38cab):
  +0x58 = #{ACTIVE slots whose ITEM FILE FLAGS word (item*0x28+0x73e46,
          OQ-014 field map u16@+6) has bit 0x4} — inc @0x38d36
  +0x59 = #{ACTIVE slots whose item FLAGS bit 0x8} (je-path @0x38be5 inc
          @0x38bf4; corpus cannot distinguish the !bit4 refinement — no
          shipped item holds both bits active)
VERIFIED (scripts/r201_threat_law_verify.py RC=0, 2900 recs x 20 saves):
  H58 agreement 2880/2900; H59 (active&!4&8) 2900/2900; H59b (active&8)
  2900/2900. All 20 H58 misses are ONE record (41..60.sav rec44 "Shlupp
  II", AI-owned, stored 1 computed 0, stored59 correct) — exactly the
  evaluator self-init signature 0x3fb3e (+0x58:=1 when recalc hasn't fired
  since the clamp). Corpus census r201_threat_census.py: +0x58
  {0:2400,1:240,2:260}, +0x59 {0:2120,1:320,2:300,3:120,4:20,5:20},
  owner{0:1600,1:220,2:260,255:820}; self-check IND/RES/PROS maxima match
  t198 exactly (77/52/16).
SEMANTICS: the "threat" the AI reads is NOT an enemy-scan quantity — it is
the count of FLAG-marked items the planet ITSELF hosts (bit0x8 witnesses
include item 26 Orbital Shield; bit0x4 set census pending). Enemy proximity
enters ONLY through the chain-C hop-tier term (DAT_00045beb row/col, S1d).
Gap map row 3 "no threat input at all" -> INPUT LAW FOUND; rewrite upgrade
follows (S2).

### S1f. LIVE WITNESSES (60.sav, all cited addresses re-read this session)
- CHAIN E template MEASURED: member B+0x82bb0+0x67b8 = bytes
  [0x0c,0x0d,0x0e,0x0f,0x25] = items {12 Hyperpower Plant, 13
  Fertilization Plant, 14 Internet, 15 Cloning Plant, 37 Lush Growth Bomb}
  — the fallback template is the slot-comparison pair set + growth bomb,
  NOT shields. [verified]
- f758-tail template RESOLVED [verified]: imm 0x89360 is an OBJ1-DATA
  address (in [0x82bb0,0x8cc83)), and 0x89360 == 0x82bb0+0x67b0 — the
  SAME live member as the pool window at pool offset 0x67b0:
  live bytes (28,29,30,0,26,27,0,0,12,13,14,15,37,0,2,0). 5-byte copy =
  {28 Orbital Missile Base, 29 SR Orbital Whopper, 30 LR Orbital Whopper,
  0 Factory, 26 Orbital Shield} — the ORBITAL DEFENCE template. Chain E
  (in FUN_0003fc4c, imm 0x67b8 pool-relative law) = {12,13,14,15,37}.
- ITEM FLAG BITS IDENTIFIED [verified via live item table
  member B+0x82bb0+0x73e40, field FLAGS u16@+6, OQ-014 map]:
  bit0x4 set EXACTLY on {17 Tractor Beam, 28 Orbital Missile Base,
  29 Short Range Orbital Whopper, 30 Long Range Orbital Whopper};
  bit0x8 set EXACTLY on {18 Surface Shield, 19 Surface Mega Shield,
  26 Orbital Shield, 27 Orbital Mega Shield}.
  => +0x58 = count of ACTIVE ORBITAL-DEFENCE items; +0x59 = count of
  ACTIVE SHIELD items. Threat is SELF-ASSESSED infrastructure, not enemy
  scan. Chain B gate reads +0x59<6: planet buys Surface Shield only while
  it holds <6 shield items. Chain C ratio/(day-stamp law) DELAYS mega
  shield as shield count rises.
- CHAIN C hop byte [rec+0xa]->star law matches t200's identical chain
  (display-node+0 -> stride-0x60 star record via [0x13bc5/7]). DAT base
  0x45beb READS AS RELOCATED BYTES at member B+0x45beb (payload image
  bytes are the UNRELOCATED table — t200 pitfall (1) again); corpus hop-
  value witness NOT completed this session (stride 120 x col-law over the
  relocated window produced junk; t190's folded 100-linear matrix at
  data+0x32ddb is the authoritative table, and chain C's index law reads
  it with STAR row-stride 120(*0x78 after <<2) — the stride-100 vs
  stride-120 tension is BANKED OPEN, does not block the rewrite: rewrite
  computes hop via its own lane graph).
- +0x67 dword writers over obj0: NO planet-record-scoped writer found in
  normal play besides save round-trip 0x3a69d + zero at 0x30be6; the
  41xxx/42xxx byte-writes are ship/UI structs (order-field adjacency). =>
  the mega-shield day stamp is WRITTEN NOWHERE STATICALLY that we found:
  either the buy-complete path through an indirect call or a UI handler
  (live-capture class). CENSUSED, HONEST NEGATIVE. Corpus witness: 60.sav
  dword[rec+0x67] values — NOT yet dumped; cheap add next iteration.

### S1d. CORRECTION OF S1a + THE REAL EMERGENCY CHAIN (FUN_0003fc4c,
631 bytes per functions_full.tsv == 0x3fc4c..0x3fec3; fresh capstone dump
work/t201_fc4c.txt). S1a's block-by-block mapping was WRONG: it walked the
tail of FUN_0003f758 (0x3f9aa..0x3fc4a belongs to 0x3f758, size 0x1267).
The t28 doc summary was RIGHT about which law lives where; the fresh dump
now CITES it fully:

  CHAIN A @0x3fc57: byte[rec+0x66] bit1 set -> BUY item 38 (0x26); on
    success CLEAR bit1 (@0x3fc78) and RETURN -1 (0xffffffff). [verified]
  CHAIN B (Surface Shield) @0x3fc86: IND(word+0x44)>=4 && PROS(+0x48)!=0 &&
    item22(Orbital Shield) ABSENT (0x3958c!=0xffff check inverted: je out)
    && (u16[+0x1c]-u16[+0x20])>=3 && byte[+0x59] < 6 -> if 0x3830c(18) legal
    && slot-absent -> BUY 18; -> ret -1. [verified; matches income-law S9]
  CHAIN C (Surface Mega Shield) @0x3fd30 — THE PERIOD TIERS ARE REAL, at
    0x3fd73/0x3fd7f/0x3fd8b/0x3fd92 as immediates 0xc8=200, 0xe1=225,
    0x12c=300, 0x190=400 [verified verbatim]. Selection law:
      hop = byte DAT_00045beb[ col_star(rec) *4 + row ] where
        col via [rec+0xa]>>16 -> *0x14 -> *0x20 -> [0x13bc7] (star obj) ->
        >>16 -> *0x3c -> <<2 => star_idx*120 (0x78);
        row = [ctx+7]->[+2]>>16  (ctx dword — the [0x7458e] CURRENT PLAYER
        idx [inferred from t191 writer census; NOT re-proved here])
      period = hop==0 -> 200 | hop==1 -> 225 | hop<4 -> 300 | else 400
      FIRE iff UNSIGNED (DAT_00012e10 - dword[rec+0x67]) / period > threat
        byte[rec+0x59]   (div @0x3fda1 — u32, NOT idiv)
      -> 0x3830c(19) legal -> BUY 19; ret -1.
    => dword[rec+0x67] = per-planet LAST-MEGA-SHIELD DAY STAMP [inferred
       from the formula shape; writer census pending S1e]. Higher threat
       DELAYS the buy (ratio must EXCEED threat); hop-to-CURRENT-PLAYER's
       star accelerates it (nearer = smaller period = more urgent).
  CHAIN D (Surface Cloaker item 11) @0x3fde0: owner(+0x57) ODD &&
    IND>20? NO: (word+0x44)>0x14 is jle-out so IND>=21... recheck: cmp
    eax,0x14; jle 0x3fe5e => IND>20 -> hmm income-law said >=20; MEASURED
    LAW: IND strictly >20. Wait — 0x3fdfb loads +0x44 then cmp 0x14 jle out
    -> IND must be >=21. [verified disasm; income-law's >=20 was sloppy]
    && rng%100 < 4 (cmp edx,4) && legal && absent -> BUY 11; ret -1.
  CHAIN E @0x3fe5e: static 5-byte template list @IMAGE 0x67b8 (mov esi,
    0x67b8; movsd+movsb copies 5 bytes to esp) — loop i<5, first LEGAL
    (0x3830c) and ABSENT (0x3958c==0xffff) item -> buy; ret -1. This is
    income-law's "5-entry template list" (NOT runtime 0x89360 — that const
    belongs to FUN_0003f758's shipyard tail, a DIFFERENT function).
  RETURN CONVENTION: forced-buy -> -1; no-forced-item -> 0 (@0x3feb9).
  CALLER 0x3f4d3 region inside FUN_0x3f130: MUST verify the -1/0 result is
  actually CONSUMED (else the whole chain is dead code). PENDING S1f.

### S1b. (SUPERSEDED by S1d for chain mapping; items 3-4 on writers stand)
(this session, capstone re-disasm + esp-map logic)

1. THE FUNCTION BOUNDARY IS FUN_0003f758 (size 0x1267 per functions_full.tsv
   HEX sizes), spanning 0x3f758..0x3fc4a — t28's "FUN_0003fc4c evaluator"
   is an entry *inside* FUN_0003f758 (the 0x3f80b FUN_00039a9c tail falls
   into it), not a separate function. [verified]
2. CHAIN ORDER (all inside FUN_0003f758, first-ret-win):
   A. 0x3f766..0x3f801 Shipyard/ship-production gate (t28 banked, unchanged).
   B. 0x3f88e..0x3f91b: word[planet+0x1e]>2 && owner(+0x57)%2==0 &&
      IND(+0x44)>20 && rng%100<3 && FUN_0003830c(0x19) legal && slot-absent
      (0x3958c(0x19)==0xffff) -> BUY item 25. [verified disasm]
   C. 0x3f91c..0x3f9a9: word[+0x1e]>2 && owner%3==0 && IND>25 (jle skips!)
      && rng%100<2 && legal+absent -> BUY item 24 (0x18). [verified]
   D. 0x3f9aa..0x3fb32 THREAT CHAIN 1 (byte[+0x59]):
      gate word[+0x1e]>=2 (0x3f9b3 jl->out);
      copies 5-byte template from RUNTIME 0x89360 (0x3f9c3 mov esi,0x89360;
      3x movsw + movsb — NOT the static 0x67b8 list income-law conflated);
      p = byte[0x45beb + ((race([ebp+0xa]>>16)*5)*8)] with race :=
      [planet+0x0a]>>16 (0x3f9cf..0x3fa14); p>=3 -> period=0 else
      period=(3-p)*2 (0x3fa19..0x3fa28 [esp]=period);
      threat=byte[+0x59], 0->store 1 (0x3fa36, SELF-INITIALISING);
      ratio = (IND+RES)/threat signed idiv (0x3fa48..0x3fa52);
      days = ([ctx+0x1a8]>>16) - period (0x3fa58..0x3fa64);
      FIRE iff ratio > days. Then loop i<2 over [esp+0x10+i] template bytes
      filtered by research-mask legality (restree [0x7478b + 75*row] byte3
      bit owner), count bx of LEGAL ones; if some legal item ABSENT from
      slots -> buy first absent (0x3faeb); else rng%bx -> buy that (0x3fb03,
      buy even if present). [verified disasm]
   E. 0x3fb33..0x3fc40 THREAT CHAIN 2 twin: byte[+0x58] self-init 1,
      ratio=(IND+RES)/+0x58, ctx dword +0x1aa, SAME template buffer
      ([esp+0x10+i], no second copy), loop i<3 — wait: 0x3fb7e cmp eax,3 is
      the LEGAL-COUNT build bound over the same 2-entry buffer? NO: loop
      bound i<3 reads [esp+0x10+2] — third template byte from the copied
      5-byte buffer at 0x89360+2. Fire buys via 0x38818 (absent-first at
      0x3fbf8, rng-pick fallback 0x3fc1f). [verified disasm; NOTE no period
      term in chain E — days = ([ctx+0x1aa]>>16) directly, 0x3fb60..6c]
   => THE "period tiers 200/225/300/400" IN income-law S9 ARE NOT IN THE
   CODE: zero literals 200/225/300/400 in 0x3f130..0x3fc4a (grep of banked
   listing). The real period law is PER-OWNER: period = f(DAT_00045beb[
   40*race]) = {p: 0,1,2 -> (3-p)*2 in {6,4,2}; p>=3 -> 0} [verified].
   SMALLER period -> fires EARLIER. DAT_00045beb is the SAME base t190
   folded as the hop matrix (data+0x32ddb) — alias check: the hop matrix is
   stride-100; index 40*race collides with the matrix interior, so ONE of
   the two readings is misfolded — t190's identity was tied to
   scenario-authored lanes (verified then), so treat 40*race here as a
   stride-5-per-empire(8B) sub-view UNLESS the corpus says otherwise. OPEN.
3. THREAT-BYTE INPUT (gap row 3) — WRITER CENSUS MEASURED
   (scripts/r201_threat_writers.py RC=0, obj0 [0x14bb0,0x82bb0), byte-wide
   disp32==0x58/0x59 any base): 325 sites total, 93 W. PLANET-RELEVANT
   WRITERS are EXACTLY:
     0x3fa36 / 0x3fb3e  the two evaluator self-inits (value 1)
     0x38ef7/0x38efe    inside FUN_00038ba4 (the t45/t18 planet-recalc fn):
                        [ebx+0x58]=arg@esp+0x24, [ebx+0x59]=arg@esp+4
     0x3a673/0x3a67a    inside FUN_0003a558 (rec-like copy, args esp+0x58/59
                        -> [ebp+0x58/59])
   (All other byte writers 2202f..4db04 are SHIP order-kind stores —
   aicode.md S2f law: ship+0x58=order kind, +0x59=order target ptr; the
   cmp ...,4 pattern everywhere is order-kind==RETREAT idiom.)
   => NEITHER +0x58 NOR +0x59 IS COMPUTED IN obj0: both arrive via STACK
   ARGUMENTS of the two rec-painting functions (recalc FUN_00038ba4 and
   FUN_0003a558). The producer is whoever passes those args — candidate:
   obj1 data segment (the AI threat scan may live there — obj1
   [0x82bb0,0x8cc83) was NEVER code-scanned; attribution says gsystem/
   cosmos modules) OR an upstream caller doing a ship-proximity scan.
   NEXT: E8 callers of 0x38ba4 + 0x3a558, then scan obj1 for disp 0x58/59.
4. CALLER CONTEXT (0x3eab8..0x3eade): per-planet loop (EDX=rec, ECX=ctx,
   owner==ctx[0] byte; skip when owner==player([0x7458e]) && [rec+0x5a]!=0
   && [0x10ba4]==0; skip when byte[rec+0x54]!=0 = queue-in-progress).
   The SAME ctx dword +0x1a8/+0x1aa semantics: [verified read sites only
   0x3fa58/0x3fb60 inside obj0? — grep of the 325-site census for 0x1a8/
   0x1aa returned NOTHING (exit 1) because the census only matched disp
   0x58/0x59; need targeted ctx-field scan. The (>>16) form matches the
   day-counter convention (DAT_00012e10 == day, low-word-shifted packs);
   ID [unverified]: per-race last-fire day counters would make
   ratio > (lastday - period) a re-fire latch. CORPUS TEST PLANNED.
5. ITEM NAMES: items 24/24/25/26? — planitem.txt rows to check: 24,25
   (extracted/ascend00/planitem.txt). Chain B/C buy 25 and 24; chains D/E
   buy from the 0x89360 template (RUNTIME — measure in 60.sav).

### S1c. CORPUS CENSUS MEASURED (scripts/r201_threat_census.py RC=0)
Window = PLANET_P0 name-anchored stride-123 walk (r1_record_census law),
sys field X at window j+(X-0x24). SELF-CHECK PASSED EXACT: IND max 77,
RES max 52, PROS max 16 == t198 measured (2900 recs / 20 saves).
  sys+0x58 census {0:2400, 1:240, 2:260}   (per save: 120/12/13 of 145)
  sys+0x59 census {0:2120, 1:320, 2:300, 3:120, 4:20, 5:20}
  joint top: (0,0) 2120, (2,2) 220, (0,1) 180, (1,1) 140, (1,2) 40,
             (1,3) 40, (0,2) 40, (0,3) 40, (2,3) 40, (1,4) 20, (0,5) 20
=> THREAT VALUES ARE REAL AND NON-TRIVIAL in the NEW-GAME corpus (values
2..5 cannot come from the self-init-1 stores). The static writers are only
recalc FUN_00038ba4 (stack args: [esp+0x24]->+0x58 byte, [esp+4]->+0x59
byte), loader-copy FUN_0003a558 (args esp+0x58/0x59), evaluator self-inits.
=> THE INPUT PRODUCER LIVES UPSTREAM OF FUN_00038ba4's CALL ARGS.
Corroboration +0x57==owner: 0x3a548 writes byte[ecx+0x57]=0xff (clear
owner) immediately before calling the recalc in the demolish-all helper
FUN_0003a4e0; owner census {0:1600,1:220,2:260,255:820}.
CALLERS of 0x38ba4 (E8 byte-pass, 12): 0x37fa8(FUN_00037d80), 0x388d4/
0x389b0/0x38a2a/0x38b7c/0x38b94 (FUN_00038840 cmd-exec), 0x39401
(FUN_00038f68), 0x3a165 (FUN_00039f00), 0x3a4ce (FUN_0003a174), 0x3a54c
(FUN_0003a4e0 demolish-all), 0x3ada3 (FUN_0003aa0a big event fn), 0x44058
(GAP). CALLERS of 0x3a558 (2): 0x258dd (FUN_00025604 = t190 game-state
SNAPSHOT deserialiser!) and 0x26044 (FUN_00025d30). => FUN_0003a558 is the
SAVE/LOAD record materialiser — threat bytes ROUND-TRIP through saves; the
live generator is among the 0x38ba4 callers' arg computations.
