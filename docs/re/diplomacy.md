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
