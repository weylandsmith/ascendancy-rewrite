# diplomacy — `.dip` files [verified; extends OQ-009]
Sources: `extracted/ascend00/player.dip` (human species) and the 21 `raceNN.dip`. Vendor comment in each: everything above `DIPVALUES` is commentary. Produced by `scripts/ui_probe.py`; gate 3k.

## 1. Weight schema [verified 2026-10-04, all 21 race files]
- all 21 `raceNN.dip` share **one 15-key** DIPVALUES set (asserted). `player.dip` (the human species) carries a strict **8-key subset** — asserted. The 6 race-only keys are the mood-oscillation model: BIO_MAXNEGATIVE, BIO_MAXPOSITVE, BIO_PERIOD, BIO_SIN_HALF_X, BIO_SIN_TWICE_X, BIO_SIN_X, NEG_PLAYER_TURNS.
- PARSE TRAP: values can be NEGATIVE (`BIO_MAXNEGATIVE` is negative in all 21 files; `BIO_SIN_*` in several). An `isdigit()`-style numeric filter SILENTLY drops those keys — this probe's own first revision did exactly that (assertion `set(player) < set(race)` caught it: the race set came up missing BIO_MAXNEGATIVE). Correct parser: `-?[0-9]+`. (scripts/dip_probe.py has always parsed them correctly; 15 keys, docs/re/ai-data.md.)
- envelope per key (min, max, distinct across 21 races):
  - ACCEPT_ALLIANCE         500 .. 800      (11 distinct)  player=200
  - ACCEPT_PEACE            200 .. 530      (12 distinct)  player=100
  - BIO_MAXNEGATIVE          -5 .. -1       ( 5 distinct)
  - BIO_MAXPOSITVE            1 .. 5        ( 5 distinct)
  - BIO_PERIOD              180 .. 800      (14 distinct)
  - BIO_SIN_HALF_X           -5 .. 3        ( 8 distinct)
  - BIO_SIN_TWICE_X          -2 .. 2        ( 5 distinct)
  - BIO_SIN_X                -3 .. 4        ( 7 distinct)
  - BREAK_ALLIANCE          420 .. 750      (15 distinct)  player=170
  - DECLARE_WAR             130 .. 450      (12 distinct)  player=70
  - NEG_PLAYER_TURNS         43 .. 319      (18 distinct)
  - PROPOSE_ALLIANCE        680 .. 900      (10 distinct)  player=250
  - PROPOSE_PEACE           300 .. 670      (11 distinct)  player=150
  - SHIP_PATIENCE            35 .. 145      (13 distinct)  player=100
  - START_ATTITUDE          310 .. 620      (15 distinct)  player=100
- [inferred, clearly labelled] `BIO_PERIOD`/`BIO_SIN_*` + `BIO_MAXPOSITVE`/`BIO_MAXNEGATIVE` describe a per-species sinusoidal mood cycle (period in turns, amplitude split pos/neg); `NEG_PLAYER_TURNS` gates how long a negative state sticks. The rewrite implements exactly that documented model; exact phase arithmetic is runtime-blocked (R1).

## 2. DA_* dialogue templates [verified]
- template counts: {'race00.dip': 15, 'player.dip': 15} (race00 vs player)
- substitution tokens across bodies: {'y': 12, 'm': 2, 's': 4, 't': 9} — semantics per token are inferred from context (%m = my species, %y = your species, %s = star system name, %t = third-party species), but the full token table is runtime-blocked -> OQ-015. The rewrite implements exactly the tokens observed in data and leaves unknown ones literal.
- the AI evaluation ORDER that picks which DA_ message fires remains in the exe (R1); the rewrite ships a documented behaviour-plausible order (discover > propose > accept/break > trade > declare-war) and will re-check against R1.

## 4. Loader law banked (OQ-015 probe t10, 2026-10-07) [verified static]
- Name-table census (ck005, pointer law member B+0x82BB0+X, table image 0xa0f8,
  stride 50, count 471 @0x10a70): exactly 22 .dip entries — player.dip idx25,
  raceNN.dip idx26..46 (indices contiguous).
- Section-key strings (restored image): `RACE%02d.DIP` @0x847d9/0x84da0,
  `PLAYER.DIP` @0x847e6, `ACTIONS` @0x8480d, `RESPONSES` @0x84815,
  `END DIPLO` @0x8481f (owner strings `..\negwnd.cpp`, `..\race.cpp`,
  `..\raceneg.cpp`). Only `RESPONSES` (0x84815) has a direct u32 code ref:
  0x372b0 inside FUN_00037268 — other keys are referenced indirectly
  (pool-relative imm law did not apply here; do NOT re-scan).
- FUN_00037114 (v1-named .dip loader): guards race indices <= 0x14 (21 races,
  DAT_00006775 / DAT_0007458e pair = (me, other) or (other, me)); loads each
  party's dialogue only when the cached id at [obj+0xb9]/[obj+0xbb] (u16 high
  half test >>0x10) mismatches — on-demand per-pair caching.
- FUN_00037268: reads three sections (keys 0x1c5d, 0x1c65=`RESPONSES`-adjacent,
  0x1c6f) via line-helper 0x7892a into pools, stride **128** (loader
  `SHL EAX,0x7`; renderer FUN_00036ed8 independently uses `param_2*0x80` —
  earlier "112" in this section was my arithmetic slip, corrected 2026-10-07
  t11), cap 0x7f (127 entries), selecting AI-vs-player pool base by EDI:
  ACTIONS AI 0x705e8 / player 0x71c78; RESPONSES-pair 0x70d68 / 0x723f8;
  helper 0x776f0 stores each line.
- Capture corroboration (ck005 + ck010, byte-identical region): heap text at
  phys 0x39e267 holds the parsed DA_ templates in FILE ORDER
  (DA_Discover, DA_DiscoverAskHelp, DA_DeclareWar, DA_ProposeAlliance,
  DA_TradeStarlanes, DA_TradeStars, ...) == load order == pool index order.
- NOT found (clean negatives, do not re-run image scans for these):
  zero `DA_` bytes in the static image (templates are data-file-only); the
  selection/priority logic does NOT live in the loader — the loader only
  populates pools. Weighted choice lives in the negwnd/raceneg AI paths fed
  by the 15 DIPVALUES weights (docs/re/ai-data.md).

## 5. Renderer + queue + dispatch laws (t11, 2026-10-07) [verified static]
- Renderer FUN_00036ed8 (regparm3: EAX=param_1 negotiation ctx, EDX=param_2
  template idx, EBX=perspective): pool selection CONFIRMS stride 0x80 —
  param_3==0 (response): EBX==0 -> 0x723f8, else 0x70d68; else (action):
  EBX==0 -> 0x71c78, else 0x705e8. Entry = base + idx*0x80.
- %token substitution law (measured byte-dispatch on template byte after
  '%'): 0x6d 'm' -> own-species name: DAT_00074590 + nameIdx*0x14 where
  nameIdx = byte(&DAT_00012e17 + DAT_00006775*0x1ee) (player side) resp.
  DAT_00007458e variant (other side); 0x79 'y' -> swapped pair;
  0x73<=b<0x74 's' -> star-system name field *(int)(&DAT_00013000 +
  idx*0x1ee) + 0x1c; 0x74<=b<0x75 't' -> third party name, via negotiation
  pair table DAT_000066d8 + ([param_1+0xbd]>>0x10)*2 when (EBX==-1 &&
  param_3==-1), else DAT_00013000 chain. Species name records stride 0x1ee,
  names are 20 bytes (stride 0x14) at DAT_00074590. Exactly {m,y,s,t} —
  v1's data-side token census is now corroborated by CODE.
- Message queue (negotiation obj): count u16 +0x8c7, entries at +0xc7 stride
  8, capacity init u16 0x1d (29) @0x363f1; reset FUN_00032fdc: count=0,
  +0xcb=0, +0xcd=0, +0xcf=0xffff, +0x8dd=[obj+0x10]-1.
- Event dispatch FUN_0003634a(ctx, event u16, param_3): event 0/1 dialogue
  open -> build/alloc negotiation objs (+0xab,+0xaf,+0xb3), cap 0x1d, load
  .dip via FUN_00037114, then AI-vs-human branch on species byte
  (&DAT_00012fff)[playerIdx*0x1ee] == 0x0e: AI path FUN_00044848 ->
  FUN_00036cd8 (render queue, max loop DAT_000701f4 entries at 0x701e0+1,
  u32 packed type = >>0x18 indexes ACTIONS-pool base 0x71c68... note
  0x71c68 vs 0x71c78: render base is 16 lower — header word per pool, no
  claim) -> FUN_00036ea4; human path FUN_00044e20 -> FUN_00036dd4 ->
  FUN_00036e6c. event 4..5 gated 0xAD<EBX<0x148 && 0x144<param_3<0x1D9 ->
  FUN_0004fb30 + FUN_000369a4. event 0x1c01 -> FUN_00032f34 + FUN_00036a90.
- CHOOSER (AI message pick) = FUN_00044848: switch on byte
  [param_1+0x1c0+param_2] — Ghidra truncates its jumptable (bad-data).
  NEXT: raw jumptable recovery (disassemble_bytes past 0x44848, manual
  table decode), NOT re-deriving the loader.

## 6. FUN_00044848 decoded = offer-state setter, NOT the DA_ chooser (t11)
- Entry shuffle (regparm3): ESI=ctx, EBP=sx(param_2), race-record base
  EDI = 0x12e16 + 494*EBP (0x1ee stride law again); always writes 0xe byte
  to out-param [EBX] (human-species marker).
- Switch var: byte [ctx + 0x1c0 + idx]; guard JA>3 -> 0x44a29; jump-mode
  `JMP [EBP_disp + disp32]` with encoded disp32 0x2fc88 (EH-prologue bytes
  live there in-file; the ACTUAL case dwords sit at RESTORED 0x44838:
  {0x448a2, 0x448cd, 0x448bc, 0x44959} — the encoded-vs-materialised
  mismatch is the known 143-not-simple-fixups class; do NOT re-scan for a
  second table).
- Case bodies (read through 0x448e4): case0 = vendor error 0x2a438
  (EBX=0x126 line 294, msg 0x22ca); case1 writes bytes 2 then 3 into the
  race record and reads [0x12e10]-[0x74734]; case2 writes byte 0xd,
  returns 2; case3 @0x44959 not yet read.
- Conclusion so far: this is the treaty/offer state machine on the race
  record (marker bytes 2/3/0xd), keyed by per-(ctx,idx) state byte. The DA_
  MESSAGE CHOOSER is elsewhere; candidates queued: FUN_00044a44 (callee of
  the 0xe-gate just above), and the packed type writer for queue entries
  ([obj+0xc7] stride 8, type u32 >>0x18 indexes the ACTIONS pool @0x71c68+16
  per FUN_00036cd8).

## 7. DA_ action chooser FUN_00044a44 — MEASURED selection law (t12)
CALLER LOCATED t12: Ghidra's caller list is empty but the raw CALL exists —
`E8 6F 02 00 00 @0x447d0` (relative target 0x44a44, verified byte row
0x447d0..0x447e9: CALL / MOV BL,AL / CMP AL,0xe / JZ 0x44713). Post-call
caller law: AL==0xe -> JZ epilogue 0x44713 (NO message queued); otherwise
DL=player idx ([0x7458e]), EDI==DL required to continue, action byte stored
[ESI+0x1e9] @0x44801 (negotiation obj), then msg box 0x7a35c via 0x55a60
with EDX=2. Ghidra never formed the owning function (0x446d9-ish head, ep
0x4482d..0x44836) — another caller-attribution gap, raw bytes authoritative.
Call site: `CALL 0x44a44 @0x447d0` (inside the AI branch; Ghidra
get_function_callers returns [] here — caller attribution gap at 0x447d0,
raw bytes are the authority). Gate after return: AL==0xe -> JZ 0x44713
(no message); other values flow into the queue as the entry type.
Record layout (race-diplo record ptr param_1, per-target idx param_2):
state byte [+0x1c0+idx]; per-target attitude i16 [+0x1b2+2*idx]; power-ish
u32 [+0x1b0+?] (hi-byte compared); cadence divisor u32 hi [+0x1c5];
thresholds i16 [+0x1c9], [+0x1cd], [+0x1cf], [+0x1d3]. [unverified] which
DIPVALUES key each threshold comes from — next leg.
Return value == DA_ ACTIONS pool index (file order, §4 census):
- state==1: att < [rec+0x1c9] AND tech-word DAT_00013b9c[idx*6] hi > 2
  -> 2 (DA_DeclareWar); elif [rec+0x1d3] < att -> 3 (DA_ProposeAlliance).
- state==2: (no direct return; falls to cadence block; state==2 also means
  eligible as third party in loop 3 -> caller gets 9).
- state==3: [rec+0x1cd] < att -> 0xd (13 DA_OfferPeace); elif att <
  [rec+0x1cf] -> 8 (DA_BreakAlliance).
- Cadence block (gated DAT_00012e10 % (rec+0x1c5 hi) == 0 AND idx ==
  DAT_0007458e AND state != 2): roll = RNG FUN_0007824f() % 100.
  - roll < 0x50 (80), three third-party loops in ORDER over races
    (count DAT_00013b96 hi-word), rel matrix (&DAT_00012fd6)[me*0x1ee+other]:
    loop1: other.state==2 && rel==3 -> 10 (DA_BreakAllianceWithOtherRace),
    loop2: other.state==3 && rel==2 -> 7  (DA_OfferPeaceToOtherRace),
    loop3: other.state==2 && rel==1 -> 9  (DA_DeclareWarOnOtherRace),
    each also requires other alive (DAT_00012e19 chain != -1) and
    other != me, other != target. [unverified] rel enum semantics (1/2/3).
  - then if [rec+0x1c9] <= att: bonus +0xf when state==3;
    trade ladder in ORDER, each needing its FUN predicate nonzero:
    (rec+0x1cd hi)+10 < power hi && roll > 0x5c (92) && FUN_000465fc ->
    6 (DA_TradeResearch); [rec+0x1cf] < att && roll > 0x57 (87) &&
    FUN_00046428 -> 5 (DA_TradeStars); (rec+0x1d3 hi)+0x14 < power hi &&
    roll > 0x4f (79) && FUN_00046258 -> 4 (DA_TradeStarlanes).
- else -> 0xe (14 DA_NoDipAction).
State-byte semantics {1,2,3} NOT yet mapped (writers next leg; do not guess
in code). Rewrite decideDipAction stays the documented default until the
state/threshold mapping lands; its order (alliance@hi vs war@lo) matches
state==1's dual-threshold shape but NOT the cadence/roll/trade machinery.

## 8. Field map: DIPVALUES -> record offsets (OQ-015 t13, MEASURED)
- Loader FUN_00044290 (raceneg.cpp owner): opens `RACE%02d.DIP` (pool imm
  0x21f0 -> decoded from banked RAM pool base P=0x242088 via soundfx.txt
  anchor 0x2a08; `%s %d` format strings at pool 0x2216..0x22b5, 6-byte
  pitch, verified verbatim in ck005 RAM), sequentially scan-parses the
  DIPVALUES lines POSITIONALLY into fixed record offsets:
  +0x1c9,+0x1cb,+0x1cd,+0x1cf,+0x1d1,+0x1d3,+0x1d5 (i16), +0x1b0 (i16),
  +0x1d7,+0x1d9,+0x1db (i16), +0x1dd,+0x1e1,+0x1e5 (float), +0x1c7 (i16).
  After each of the first six it enforces strictly ascending, else vendor
  error 0x2a428.
- Positional mapping == canonical key order (proved two ways: loader is
  positional + every one of the 22 .dip files lists its keys as an IN-ORDER
  SUBSEQUENCE of DECLARE_WAR, ACCEPT_PEACE, PROPOSE_PEACE, BREAK_ALLIANCE,
  ACCEPT_ALLIANCE, PROPOSE_ALLIANCE, START_ATTITUDE, SHIP_PATIENCE,
  BIO_PERIOD, BIO_MAXPOSITVE, BIO_MAXNEGATIVE, BIO_SIN_X, BIO_SIN_HALF_X,
  BIO_SIN_TWICE_X, NEG_PLAYER_TURNS [verified regex over all 22 files]).
  => +0x1c9=DECLARE_WAR, +0x1cb=ACCEPT_PEACE, +0x1cd=PROPOSE_PEACE,
  +0x1cf=BREAK_ALLIANCE, +0x1d1=ACCEPT_ALLIANCE, +0x1d3=PROPOSE_ALLIANCE,
  +0x1d5=START_ATTITUDE, +0x1b0=SHIP_PATIENCE, +0x1d7=BIO_PERIOD,
  +0x1d9=BIO_MAXPOSITVE, +0x1db=BIO_MAXNEGATIVE, +0x1dd/0x1e1/0x1e5 =
  BIO_SIN_X/HALF/TWICE (floats), +0x1c7=NEG_PLAYER_TURNS.
- Chained-ascending check: first six values strictly ascending in 21/21
  race files (matches the loader's six enforced comparisons).
- Chooser §7 thresholds REKEYED: state1 declare-war iff att < DECLARE_WAR
  (and tech-word DAT_00013b9c[race*6] hi > 2); state1 propose-alliance iff
  PROPOSE_ALLIANCE < att; state3 offer-peace iff PROPOSE_PEACE < att;
  state3 break-alliance iff att < BREAK_ALLIANCE. Cadence divisor reads
  byte [rec+0x1c5] hi-half — NOT a DIPVALUES field (packs with an adjacent
  runtime u32; unmapped, non-blocking for the selection ORDER).
- Cross-check vs rewrite decideDipAction (v1): thresholds and directions
  MATCH the original for all four primary branches; original comparison is
  STRICT (PROPOSE_ALLIANCE < att, PROPOSE_PEACE < att) where the rewrite
  used >= at the two propose sites -> upgrade to strict (t13 code site).
  Original declare-war additionally gates on per-race tech level; rewrite
  DipPolicyState carries no tech field — documented extension, not copied.
- STATE-BYTE +0x1c0 writers: disp-scan sees only stack-slot writes
  (0x19eef, 0x1d71e are [ESP+0x1c0]); record writes go through computed
  pointers (FUN_00044848 family) — relationship-state semantics belong to
  the negotiation-state family (OQ-012(a)), NOT to selection order.

## 9. Trade predicates + cadence REKEY — MEASURED (t14, 2026-10-08)
Same-shape gates behind the §7 trade rungs; state byte == 3 short-circuits
PAST all checks (predicate returns true when allied posture). PASS <=> ALL:
- DA_TradeStarlanes gate FUN_00046258: starlane table 0x16147 stride 0x27
  (count u16 [0x177d3]), owner byte [+0x20] per-race bits; mine = records
  with my bit, theirs = with target bit.
  PASS <=> mine >= 5 (@0x462e2 `CMP EAX,5`; bytes 83 F8 05)
       AND mine/total <= 0.9  (FCOMP qword pool 0x2432 @0x4630f DC 1D 32 24
          00 00; JBE pass direction -> FAILS iff ratio EXCEEDS floor)
       AND mine/theirs <= 2.0 (FCOMP pool 0x243a @0x4632e DC 1D 3A 24 00 00;
          theirs clamped >=1 first).
- DA_TradeStars gate FUN_00046428: star table 0x13bc5 stride 0x60 (the
  OQ-012(a) star table), owner byte [+0x17].
  PASS <=> mine >= 3 AND mine/total <= 0.9 (pool 0x2442)
       AND mine/theirs <= 1.6 (pool 0x244a).
- DA_TradeResearch gate FUN_000465fc: tech table 0x74746 stride 0x4b,
  owner byte [+0x45].
  PASS <=> mine >= 5 AND mine/total <= 0.85 (pool 0x2452)
       AND mine/theirs <= 1.7 (pool 0x245a).
  Pool doubles read verbatim from banked ck005 RAM at P=0x242088 (§8
  anchor law). Semantics [inferred]: the AI offers an exchange only when it
  holds a real stake (min count) without dominating the commodity — a
  >floor share or a big multiple of the partner's holdings kills the offer.
- CADENCE REKEY (u32>>0x10 aliasing correction to §7): the "divisor
  [rec+0x1c5 hi]" IS the u16 at +0x1c7 == NEG_PLAYER_TURNS (§8 map): the
  block fires iff `turn % NEG_PLAYER_TURNS == 0`
  (DAT_00012e10 % (dword[0x1c5] >> 0x10) == 0). §8's "packs with adjacent
  runtime u32; unmapped" note RESOLVED — +0x1c5/0x1c6 are the low half of
  the dword load.
- "power hi" in §7 likewise aliases the target's ATTITUDE word:
  dword[0x1b0 + 2*idx] >> 16 == word[0x1b2 + 2*idx]. RUNGS REKEYED:
  research rung = BREAK_ALLIANCE + 10 < att (dword[0x1cd]>>16 = word[0x1cf]);
  stars rung = BREAK_ALLIANCE < att (direct short cmp);
  starlanes rung = START_ATTITUDE + 20 < att (dword[0x1d3]>>16 =
  word[0x1d5]).

## 10. Session-matrix window census + RETRACTION (t77b, 2026-10-12)

Static re-read (objdump, authoritative): the chooser entry at 0x447ba is
`cmp BYTE PTR [ebp+0x1c0],0 / JE skip` — the chooser runs ONLY when the
relation-state byte is NONZERO (0 = no active relationship: matrix cell
default/self). What the nonzero values MEAN is NOT settled by the banked
corpus: §7 pairs state 1 with DA_DeclareWar/DA_ProposeAlliance, state 3
with DA_OfferPeace/DA_BreakAlliance, and the third-party loops pair the
SAME matrix cells with both break-alliance and declare-war actions; no
injective enum ({war, allied, ?}) fits every rung from idle data alone,
and the corpus contains NO value other than 1. State-enum semantics are
therefore OPEN sub-items, capture-gated (need a session that fights
and/or accepts an alliance).

CORRECTION TO AN EARLIER §10 DRAFT (same turn, retracted before any code
site depended on it): a raw census of the window base 0x12e16 stride 0x1ee
across 945 banked idle slots reported an off-diagonal relation census of
{0,1}-only with 'war pairs present at turn 0'. Those readings ARE NOT
TRUSTED: (a) 0x12e16 static base was never re-validated per-run by an
independent law in those slots (heap can relocate; the t56b BASE-DRIFT
hazard law applies); (b) 'state 1 = at war' contradicted the chooser gate
above — caught by cross-audit, so the state semantics in the draft are
VOID; (c) a follow-up drift-filter rerun mis-implemented the row test and
returned a meaningless all-drifted result (noted so nobody re-reads the
first census as confirmed).

What IS kept: the window STRUCTURE law (attitude i16 +0x1b2+2t, state byte
+0x1c0+t per row 0x1ee) stands from §7's static decode; START_ATTITUDE
values (310..620) genuinely appear in that window in banked RAM. Closing
the OBSERVED state-transition law (contact->war fires, alliance formation)
needs a campaign that actually fights/accepts — capture-gated like OQ-021,
banked in BLOCKED.md. OQ-023 ledger status unchanged (open, W-B engine
gate, 'no RE unknowns for selection ORDER').

## 11. FIRST BANKED TRANSITIONS (t85b, playcap multi-sitting capture, races Chamachies=player/Orfa/Ungooma/Minions)

The user-run playcap (work/r1/playcap, turns 37..1131, 28k trusted
observations after the t85b streaming/dedup/stale-instance laws — see
scripts/r1_stream.py) produced the FIRST real relation transitions. Distinct
nonzero cell values across the whole trusted stream: {1, 2} (rec matrix and
third-party mirror move together, cell-for-cell).

Player-stated actions (user): declared war on the Minions and proposed an
alliance with the Orfa around in-game day 887 (manual slot 3 saved then).
Banked transitions at that boundary (t887->t888, wall 10-19 15:17..15:21):
  * rec[Chamachies->Minions] 1->2 AND rec[Minions->Chamachies] 1->2
    (reciprocal, sustained >240 turns to the end of capture; att 318/318,
    far below both DW thresholds 210/290 — so state, not attitude, carries
    the war: per §7 a state-1 cell with att<DW would re-fire declare-war
    every cadence, which is NOT what a war looks like).
  * rec[Chamachies->Orfa] stays 1; attitude i16 jumps 315 -> 595 in the SAME
    boundary and holds ~600 for the rest of capture (live t=1131 slot:
    att=600; Orfa ACCEPT_ALLIANCE=570, PROPOSE_ALLIANCE=750).
WORKING ADJUDICATION [inferred from banked transition + player statement;
one campaign, n=1 each]: 2 = AT WAR; 1 = peacetime/no active relationship
(pre-war EVERY pair sat at 1, so 1 cannot mean allied); alliance state does
NOT appear in the +0x1c0 cell — the Orfa proposal shows ONLY as the attitude
bonus (+280, sustained). If true, 'allied' is carried elsewhere (candidate:
the chooser's state-3 rows are what the ORIGINAL sets on alliance formation
— unobserved here; or a separate all-you-can-see alliance table). What is
NOT banked: an ACCEPTED alliance transition, peace, break-alliance — those
transitions remain capture-gated.
Cross-empire AI wars banked the same 0->1 pattern with no player action
(Orfa<->Ungooma t536->541, Chamachies<->Minions t566->567, Orfa<->Minions
t642->643, Ungooma<->Minions t719->720, Chamachies<->Orfa t791->792,
Chamachies<->Ungooma t1016->1017): AI contact fires 0->1 BOTH directions on
one turn boundary. None of these AI 0->1 cells ever advanced to 2 without
the player's declared war, supporting state 2 being set by an actual
war-declaration action, not by hostile attitude alone.
CAVEAT (why older drafts of this §11 were wrong): the raw stream contains
12.5k stale-instance rows (a second dosbox picking up an older save, always
rewinding); diffing in file order fabricates bounce transitions
(780->692->782). All numbers above use scripts/r1_stream.py trusted order.

## §12. t85c adjudication: alliance REJECTION explained, campaign race window

Player testimony (2026-10-22, this campaign): the Orfa NEVER accepted the
alliance; war was indeed declared on the Minions at the manual-save-3
boundary. Banked stream + §7 threshold law adjudicate both:

* ACCEPTANCE GATE IS THE AI-SIDE CELL. The proposal bonus landed on
  att[Chamachies->Orfa] (315->595 at t887->888, held ~600 to t1131) but
  att[Orfa->Chamachies] peaked ~485 (t908..964) and decayed to 451 by
  t1131 — ORFA's own ACCEPT_ALLIANCE=570 (its row th) was NEVER crossed.
  A player-initiated PROPOSE does not move the AI-side attitude, so
  re-proposing at att 451/570 cannot flip the decision [inferred from the
  banked two-cell trajectories; n=1]. The §7 chooser law is CONSISTENT:
  no accept fired, no accept was due.
* CAMPAIGN RACE WINDOW n=4, CONSTANT. Every trusted row t=37..1131
  (28,843 rows) carries n=4, names [Chamachies, Orfa, Ungooma, Minions];
  ship-array owner census ever-seen = {0(player), 1(Orfa), 2(Ungooma),
  3(Minions)} + 65535 free-record. The player-visible "Nimbuloids" is
  NOT in the campaign window (race20 holds SA_IndustryBoost, help.txt
  L2476; the only static.txt hit is flavor prose). Nor is Frutmaka
  (race08, SA_RepelAlienShips "warp alien ships out of your colonies'
  stars"). Therefore the "continually repelled in the red link" CANNOT be
  a Nimbuloid or Frutmaka ability firing [verified against the window +
  ability table]. Closest documented effect: UNGOOMA (owner 2, the power-
  rival present at the contested link, 8-9 ships at war end) holds
  SA_BumpShipsInLanes "bump all ships in star lanes backward to their
  stars of origin" — the player's stuck ships were exactly in a lane.
  [INFERRED attribution; un-modelled red-lane/territory rules are the
  alternative.] Verify cheaply next sitting: read the live relation
  window (n + names); if the game shows a 5th race on screen while the
  window says 4, the window law (not the memory) is wrong.

Frame-to-frame DIRECTION-REVERSAL census (displacement >25u two frames in
a row, dot<0; the kinematic signature of a bump/warp-back), whole capture:
  owner 0 (player): 454 reversals / 885 moves   owner 1 (Orfa): 263/394
  owner 2 (Ungooma): 256/372                    owner 3 (Minion): 62/101
  during the Minion war (t>=888): 246 / 91 / 115 / 3.
Honest reading: reversals are roughly PROPORTIONAL to movement for every
owner, so kinematics alone cannot isolate WHO fired the lane ability —
the attribution above rests on the ability table (in this window only
Ungooma holds any lane effect). One open adjudication the player can close
in ten seconds: read the four RACE NAMES off the in-game diplomacy screen.
Memory decodes row 2 as "Ungooma"; if the screen instead shows
"Nimbuloids", the +0x1c0 window NAME decode (not the player's memory) is
wrong and §12's attribution flips to whoever the screen names — the row
STRUCTURE (att i16 @+0x1b2+2t, state byte @+0x1c0+t, stride 0x1ee) is
unaffected either way.

§12 CHECK RESOLVED (player, 2026-10-22): the in-game race names match the
memory decode — "Ungooma" is correct; the earlier "Nimbuloids" was a
typo by the player, not a decode failure. The +0x1c0 window name-byte law
is therefore VALIDATED by testimony, the campaign really is n=4
[Chamachies, Orfa, Ungooma, Minions], and the red-link repulsion
attribution (only Ungooma holds a lane effect, SA_BumpShipsInLanes)
stands with no surviving alternative race candidate. Nimbuloids and
Frutmaka: confirmed ABSENT.
UI INVENTORY (player): the game-screen buttons are Planets, Ships,
Research, Special Ability, Species — NO score screen, NO diplomacy button
(contact/alliance flows are reached through map interaction).


## §13. STATE-ENUM WRITER LAW — OQ-023 RESIDUAL BOUNDED STATICALLY (t180, 2026-10-28)

The t85g-named route nobody ran (find code storing imm 3 into the relation
cell) is RUN AND ANSWERED. Method: one linear objdump of code object 0
[0x14bb0,0x82bb0) over work/ascend_restored.bin (t60 file-provenance law),
grepped at mnemonic level for stores to the cell displacement, cross-checked
against scripts/r1_t107_writers_full.py 0x1c0 (independent encoding-
enumeration + function-start boundary verification). Both methods return the
SAME site set. Tools: scripts/r1_t180_state3_writers.py (census),
scripts/r1_t180_switchtbl.py, scripts/r1_t180_offer_switch.py (switch tables).
Raw disasm retained at work/r1/t180/code0.txt (140,902 lines).

### 13.1 The mutation funnel and its two arguments
FUN_000454a4 (0x454a4..0x45c30, exactly THREE callers: 0x36b2f, 0x36c47,
0x4470e) is the relation-state mutator:
    454dd  cmp bl,0xe / ja 0x45c30        ; bl = DA_ index (0..14)
    454ea  lea ebp,[eax*4]                 ; EBP reused as switch index
    45560  jmp DWORD PTR cs:[ebp+0x308b8]  ; cs base +0x14bb0 (R13 law)
                                          ; -> table image 0x45468, 15/15
                                          ; targets inside the body range
The sweep caller 0x446d9..0x4470e establishes the argument law: FUN_00044fc0
(the §6 offer-state setter) is called first, `movsx ecx,al` puts its VERDICT
CODE in cl, and the out-param at [esp+8] (the chosen DA index) goes to bl.
So transition = f(DA index, verdict code). cl provenance is cited for this
caller ONLY; the other two load ecx differently and are not claimed.

### 13.2 ALLIANCE-FORMATION LAW [verified at instruction level, n=0 observed]
FUN_00044fc0 rung for bl=3 (DA_ProposeAlliance), 0x44ffc..0x45029:
    mov ax, WORD [esi + other*2 + 0x1b2]    ; att[self][other]
    cmp ax, WORD [esi+0x1d1]                ; +0x1d1 = ACCEPT_ALLIANCE (§8,
                                            ; loader FUN_00044290 positional)
    jle -> al = 5 (reject)   else al = 4 (accept)
FUN_000454a4 case bl=3 (0x45608) then:
    4561f  cmp cl,0x4 / jne 0x45674
    4562f  mov BYTE [edi+eax*1+0x1c0], 0x3          ; SELF row
    45641  mov BYTE [edx+esi*1+0x1c0], al(re-read)  ; MIRROR row
    45648..66  attitude += 10 on BOTH cells
=> state 3 is written to both cells IFF att > race.ACCEPT_ALLIANCE. This is
causal, not correlative: it explains why 28,843 trusted rows never produced
a 3 (Orfa att 485 peak vs its 570, §12) without needing any new capture.
A second alliance-shaped channel exists at case bl=11 (0x45aa3): requires
cl == 19 (emitted at 0x45420) AND att > (other_att - 10), then writes 3 to
both cells with +5/+5/+0xf/+10/+10 attitude bumps. Its cl provenance is
UNRESOLVED — banked as a lead, not a law.

### 13.3 THE FOUR-VALUE ENUM, each value backed two ways
  0 NO ACTIVE RELATIONSHIP — chooser entry 0x447ba skips the whole dialogue
    rung iff the cell is 0; scenario seeding never writes 0.
  1 PEACETIME / CONTACTED (not allied) — live: pre-war every pair sat at 1
    and AI contact fires 0->1 both ways (§11); static: case bl=0 (0x45567)
    sets 1 while COPYING attitude from [+0x1d5]=START_ATTITUDE (§8); lock:
    consumer 0x44ce0 needs self==2 AND third==1 to emit DA 9
    DA_DeclareWarOnOtherRace, so 1 must be non-allied.
  2 AT WAR — live: player declaration 1->2 reciprocal, sustained 244 turns
    (§11); static: case bl=2 (0x455cb) sets 2 both ways with attitude -40;
    lock: 0x44c71 needs self==3 AND third==2 to emit DA 7
    DA_OfferPeaceToOtherRace, so 2 must be at war.
  3 ALLIED — static formation law 13.2; lock: 0x44c1a needs self==2 AND
    third==3 to emit DA 10 DA_BreakAllianceWithOtherRace, so 3 must be the
    alliance; consumer set exhausts {0,1,2,3} and no other value.
Ordering none < peace < war < alliance is therefore carried by cited
comparators on BOTH the writer and reader sides. The §10 "no injective enum
fits every rung" position is SUPERSEDED: it was derived before the third-
party rungs were keyed, and each rung's state pair is now named.

### 13.4 Two structural laws learned for free
(a) ROW LAW CODE-CONFIRMED: `imul ebx, edx, 0x1ee` at 0x44bf3/0x44c14/
    0x44c62/... plus base constant `mov edi/eax,0x12e16` baked at 0x446bf,
    0x454d4, 0x2748c. Row-relative [rowbase + other + 0x1c0] and absolute
    [other + owner*0x1ee + 0x12fd6] are the SAME cell (0x12e16+0x1c0 =
    0x12fd6). The §10 window structure no longer rests on RAM inference
    alone. Per-run relocation is a separate, untouched capture question.
(b) SCENARIO SEEDING IS A STATE-1 WRITER: 0x27476..0x27511 loops races
    (count WORD ds:0x13b98), copies attitude from [+0x12feb] into both
    cells, writes `mov cl,1; mov BYTE [edi+0x12fd6],cl` and the row-form
    equivalent, skipping the player's own row, gated on ds:0x10ba0 != 0.
    This is the static origin of "pre-war EVERY pair sat at 1".

### 13.5 What is NOT closed (honest scope — strict-close holds)
* No observed cell==3 anywhere in the corpus. 13.2 is an instruction-level
  derivation from static image only; the enum reading in 13.3 is corroborated
  live for 1 and 2 only. A plausible enum is still not a measurement.
* Case bl=11's trigger (cl==19 rung, 0x4536a) unresolved.
* The 0x45xxx cases beyond {0,2,3,8,8',9,9',10,11} are enumerated in the
  switch table but their attitude deltas were not each read.
* cl provenance for callers 0x36b2f / 0x36c47 (non-sweep paths).
OQ-023 therefore STAYS OPEN but is downgraded from "semantics unknown" to
"mechanism derived statically, one live observation of state 3 outstanding".
The capture test is now PRECISE rather than exploratory: raise the target's
attitude above ITS OWN ACCEPT_ALLIANCE (per-race, §8) and propose — cell 3
is then expected in BOTH directions with +10 attitude, and DA 10 should
become selectable against any empire the acceptor is at war with.

Census artefacts worth naming so nobody re-reads them as cells: the tool also
surfaces `mov DWORD PTR [esi+0x1c0],0x1df` @0x2d24f and a reader comparing
against 0x162 @0x260eb. Those are a DWORD store and a non-{0..3} compare, so
they are a DIFFERENT record's +0x1c0/+0x162 fields, not the relation-state
byte (the cell is written byte-wise with imm in {0,1,2,3} and read byte-wise
against exactly {0,1,2,3} — 23/6/20/23 compare sites respectively).

## §15 — t187 LIVE sitting (2026-10-28 23:40 EDT, turns 1255..1335+):
### first WAR->PEACE transition banked; Orfa attitude drifting UP unattended

First-row relation snapshots per turn (scripts/r1_t85g_sitting.py RC=0 on
work/r1/playcap, 45140 trusted pts):
- t1254 row: states0 = [0,1,2,2] AND states2[0] = 2 — the reciprocal 1->2
  war-declaration pair (t85b law re-confirmed in a fresh window), att2[0]
  477->437 (-40 DECLINE penalty consistent).
- t1255 row: BOTH cells are back to 1. This 2->1 direction had NEVER been
  banked (§12 explicitly listed "peace ... NOT banked"). One reciprocal
  WAR->PEACE transition, MEASURED, sustained 0 turns (declared and made
  peace inside the same ~1-turn autosave granularity — player action,
  exact UI sequence untestified).
- STATE-3 CELLS: ZERO across every trusted row t1255..1335
  (scripts/r1_t187_delta.py). Row OQ-023 STAYS OPEN — honest negative.
- NEW UNATTENDED TREND: att[Orfa->Chamachies] (AI side, the row t85g put
  at 526 after the proposal) is DRIFTING UP on its own: 526@1254,
  529@1261, 532@1271, 535@1284 — +3 per ~3-4-turn interval, consistent
  with vendor AI-side trade cadence rather than player action
  (att0[1] is frozen at 590 the whole window, so the player is NOT
  gifting). Linear extrapolation crosses ACCEPT_ALLIANCE=570 around
  t1295-1300 IF the cadence holds. PLAYER ASK (banks the closure):
  propose alliance to Orfa once in-game attitude reads high; acceptance
  writes a cell holding 3 -> row CLOSES.

## §16 — FIRST STATE-3 (ALLIANCE) EVENT BANKED; mid-turn-write methodology law
(t189b merge 2026-10-29 of the pairing-session findings — material produced
alongside iter-111; raw sources work/r1/t188b_findings.md (deleted on merge),
scripts/r1_t187_session.py + scripts/r1_t188_state3_arbiter.py, both RC=0,
over work/r1/playcap. Supersedes iter-110's "no cell3 = measured non-event"
pre-check: correct AT SCAN TIME, but the ring grew and the alliance frame
exists.)

### 16.1 The event (raw-per-row walk, arbiter), t=1335 wall-clock sequence
    23:47:22 atti0=613 state0i=1
    23:47:33 att0i=605 atti0=631 state0i=1
    23:47:43 cell0i=3 celli0=3, att bumps +10/+10 (615/644) — sustained 68 rows
This CORROBORATES the §13 static alliance law end-to-end by capture: state 3
written to BOTH cells IFF att > race ACCEPT_ALLIANCE=570 with +10 on both
cells (§13 case bl=3: write 0x3 to self cell @0x4562f AND mirror @0x45641,
attitude +10 both sides). The flipping comparator is the
AI-side cell atti0 (=631 > 570 at the flip frame); the UI "disposition" the
player reads (605) is the att0i cell. Player testimony matches the frame walk
exactly: proposals refused at UI-disposition 590/595 while atti0 sat BELOW 570
(refusal frames show atti0 526/529/532/535...569), drifting +3/turn unattended
(the §15 gift/trade-drift note), crossing 570 around the 595-proposal,
acceptance landing when atti0=631. The +10/+10 is EXACTLY the §13 bl=3
prediction.

### 16.2 METHODOLOGY LAW (applies to every future sitting adjudicator)
Scripts that take only the FIRST row per turn MISS mid-turn relation writes —
alliance/peace flips happen mid-autosave (the flip here sits inside turn 1335's
autosave cadence at 23:47:43). Adjudicators must walk RAW rows per frame, as
scripts/r1_t188_state3_arbiter.py does; r1_t85g_sitting.py's first-row-per-turn
view is fine for trends but is NOT an event witness.

### 16.3 Enum semantics CLOSED by observed transitions
2=WAR (t85b bank), 1=PEACE (t187 first 2->1 bank), 3=ALLIANCE (this event).
Full enum identity {1,2,3} is now cited by OBSERVED transitions, matching the
vendor RELNAMES@0x89074 ordering (Unknown/Peace/War/Alliance, §t85f
debugflags.md) and the third-party semantic locks (§13). OQ-023's RE-unknown
residual is closed; the row's remaining residual is ENGINE-BUILD (rewrite
still emits only the two-party threshold branch — tracked in PLAN, not an RE
unknown).
