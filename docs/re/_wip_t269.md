# t269 WIP — VICTORY-THRESHOLD MINING (OQ-021 end-ctrl)

## S0 Setup (session start, 2026-11-02 ~06:00 EST)
- Pre-flight `r1_game_health.py` RC=0 HEALTHY: game pid 535172, TL expiry
  2026-11-02 07:03:58, watcher 535187, ring 47.sav age 3 s.
  t269 is offline corpus work — no live-game clicks; TL expiry moot.
- Watcher schema (scripts/r1_slot.py read_slot): turn=u32[0x12e10],
  T=u32[0x16143]>>16 (TOTAL STARS), V=score_stars=u32[0x482fb],
  selector_byte=u8[0x43510], rank=u16[0x4350c], systems_any/full, planets_mine.
- The contradiction SOURCE re-read verbatim this session
  (extracted/ascend00/end-ctrl.txt): header comment lines 1-2 "Player controls
  over half the galaxy." vs enddesc "spans over two-thirds of the galaxy" vs
  congrat "more than two-thirds of the stars". The two-thirds prose also says
  "the other species may continue to bicker over the stars that remain" —
  [inferred] the prose is written for a galaxy-wide share, the comment for a
  >1/2 comparator; no numeric constant in either.

## S1 MEASURED — full-corpus threshold mining (scripts/r269_vthreshold.py,
## RC=0 x2; outputs work/r1/t269_vthreshold.out + _rank.out)
Corpus 7.69 GB, 314,173 lines, dedup 243,135 -> 71,038 trusted rows,
14,348 segments (session/segment law t262).
1. NO THRESHOLD EVENT: zero rows V>=25, ZERO rows with selector_byte != 0
   (sel census: {0: 71038}). No rank ever left the sentinel: rank census
   {65535: ALL rows} — rank DAT_4350c never computed -> the score evaluator
   (FUN_0002bfa8 clamp(DAT/10-1) family) never ran in captured play.
2. T CENSUS (first ever banked): T=50 rows=71,023; T=25 rows=12; T=0 rows=2;
   T=100 rows=1. The T=25/T=100 rows are NOT title-class (V=0@turn0 — check
   next probe): candidate SMALL-GALAXY campaign frames. If T=25 is real
   campaign state, half-threshold there is V>=13 — the driven corpus ALREADY
   shows V=23 profiles at T=50; a T=25 lineage with V>=13 would be a
   threshold-satisfying frame (still not an EVENT, but the closest artifact
   class reachable offline).
3. DISTANCE-TO-HALF statement (the honest product if no event lands):
   corpus max percent-controlled = 46.0% (V=23, T=50) at seg6929 t925 (and
   re-observed t958/t1015/t1016/t1087); strict majority needs V>=26 = 3 more
   controlled stars. systems_any rose to 36 (>half of 50) WHILE V stayed <=23
   — re-confirming the SEMANTIC NON-JOIN (V != owned-systems count) at the
   threshold neighbourhood specifically: whatever V counts, a player who
   "controls over half the galaxy" by the systems_any reading never armed the
   selector at V=23.
4. V-change boundary table: 61 boundaries banked in the out file (per-segment,
   turn-pair form V a->b with any/full/pm) — superset of t258's 38 (the
   per-segment trust law catches reload-class boundaries the global-watermark
   law dropped). Shape clues reproduced independently (11->22 @t911->912,
   22->11 @t1140->1141).

## S2 RESOLVED — anomaly census (scripts/r269_anom.py, RC=0)
All 24 anomaly rows (T!=50 or rank==0) are turn-0 in_game=False frames:
T=100 x2 (Oct-15 new-game setup), T=25 x14 (Oct-28 setup, any=11/pm=11 at
turn 0 = starfield mid-build), T=0/rank=0 x8 (all-zero title frames).
CONCLUSION: every IN-GAME frame ever captured ran T=50; no small-galaxy
campaign lineage exists; threshold denominator never variable.
Probe (b) skipped as redundant: bank dirs are copies of ring slots the watcher
already streamed; the whole-file pass covers them.
Probe (c): no V>=half in-game frame exists -> nothing to bank beyond the
trajectory; honest negative recorded, row STAYS OPEN (strict-close).

## S3 FINAL (session end)
- score.md S14 appended (dossier record).
- OQ-021 row annotated STATUS t269, stays open.
- STATE NEXT = t270 threshold-pursuit drive (queue drained after t269).
- Gate + ledger audit + commit in finish sequence.
