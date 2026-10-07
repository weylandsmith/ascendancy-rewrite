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
  0x1c6f) via line-helper 0x7892a into pools, stride 0x70 (112 bytes/entry),
  cap 0x7f (127 entries), selecting AI-vs-player pool base by EDI:
  ACTIONS AI 0x705e8 / player 0x71c78; RESPONSES-pair 0x70d68 / 0x723f8;
  helper 0x776f0 stores each line. Pool gaps 5776 = 0x1690 (not 127*112 —
  pools are 0x76=118-slot reserved; no claim).
- Capture corroboration (ck005 + ck010, byte-identical region): heap text at
  phys 0x39e267 holds the parsed DA_ templates in FILE ORDER
  (DA_Discover, DA_DiscoverAskHelp, DA_DeclareWar, DA_ProposeAlliance,
  DA_TradeStarlanes, DA_TradeStars, ...) == load order == pool index order.
- NOT found (clean negatives, do not re-run image scans for these):
  zero `DA_` bytes in the static image (templates are data-file-only); the
  selection/priority logic does NOT live in the loader — the loader only
  populates pools. Weighted choice lives in the negwnd/raceneg AI paths fed
  by the 15 DIPVALUES weights (docs/re/ai-data.md).
