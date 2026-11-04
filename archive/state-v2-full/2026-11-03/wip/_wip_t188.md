# WIP t188 — flight scale-law extraction (STATE NEXT ACTION at launch)

## Intake (2026-10-29 ~00:15)
- Trigger A report re-confirmed REAL but ALREADY ADJUDICATED: sitting
  re-run scripts/r1_t85g_sitting.py RC=0 on shared work/r1/playcap
  (work/r1/t188_sitting_dump.txt): 45227 trusted turn-change rows (was
  45140 at t187). NO NEW TURNS beyond t1335 in the trusted stream — the
  +2.93MB growth is the save-rotation churn: player at t=1335 kept
  autosaving; from 23:51 the watcher re-read the whole 41..60 rotation
  repeatedly, and after ~00:09 the newly-written saves report t=0
  planets=1 ships=0 with DAT_482fb=21 retained (NEW GAME SAVED INTO THE
  SAME ROTATION, or in-game turn-0 save; dosbox NOT running at probe
  time; last timeline row 00:12:44). t=0 rows are untrusted/watcher-
  filtered; sitting trusted corpus unchanged in substance.
- PRE-CHECKS (t188 assignment): grep -o 'sel=[1-9]' watch.out -> 0 hits;
  grep -c 'DAT_482fb=2[5-9]' -> 0. OQ-021 boundary NOT crossed (still
  21/50). No relation cell 3 in sitting window (states stay 0/1/2 at
  t1250..1335). So no override fires -> proceed with scale law.

## NEW from this sitting re-run vs t187 (bank it)
- Orfa (owner-1) att toward player crossed the alliance-extrapolation
  band WITHOUT player action: 535@t1284 -> 569@t1285 -> 572@t1286 ->
  575@t1295 -> 577@t1301/1306 -> 613@t1335. t187 predicted crossing
  ~t1295-1300; actual first 570+ reading t1285. Still states[0][1]=1
  (no alliance proposed by anyone). Govorom att0[1] 590->595 @t1335.
  OQ-023 row stays open (needs a cell==3 or a proposal event).
- t1335 slot-21 (state1) and slot-39 (state3!) appear-then-vanish INSIDE
  the same turn between duplicate first-row reads (autosave mid-write
  partials) — watcher partial artifact, NOT game events; do not count.
  NB state-3 ships were seen in older turns (t1254 slot33 state3) — the
  OQ-023 relation state 3 (alliance) is distinct from ship state 3.

## FINDING 1 (t188, r1_t188_frame.py + re-parse of t187_scale_dump.txt):
## THE 14u LANE MARCH IS NOT THE T1 WALK LAW AND NOT SHIP-UNIT-MOVES
- Star table read LIVE from ring save 49.sav (anchor law, H=136, 50 stars):
  NEW GAME map — extent x[-424,400] y[-381,430] z[-402,381], star-star
  dist min 55 med 515 max 880. CAUTION: this is the PLAYER'S NEW t=0 game
  saved into the same ring (see Intake); the t1255..1335 campaign's star
  table was OVERWRITTEN by rotation and is NOT recoverable from live saves.
- Re-parse of t187 scale dump (75 turn-pair rows): ALL consecutive-turn
  small steps are EXACTLY d=14.000 (own0 MOVES=6 x12, own1 x6, own2 x5)
  or 4.670 (=14/3, own1 MOVES=4 x18), plus one 10.000 (own0 MOVES=6 x1).
  The '28/56' values are ARTIFACTS of missing turns (t1257, 1263 etc.
  absent): when turns are consecutive the step is 14 or 14/3. d/MOVES is
  NOT constant (10, 14, 21, 7.005) => step INDEPENDENT of MOVES budget.
  T1 law prediction for these rows (walk=min(d,MOVES) sugar, 160u/sugar,
  d>>MOVES, fuel 10-12>=steps) is displacement = MOVES*160 = 640-1920u —
  REFUTED by 45/45 rows. ALSO walk=14/160=0.0875/day implies arrived
  (walk==d) on day one — refuted (march runs 20+ turns).
- GEOMETRY of slot-13 march (full series t1255..1284): y=0.000 EXACTLY and
  z=1824.0 CONSTANT for the whole march; pure +x motion. Sagitta test
  kills orbit-interpolation (r=1824 chord=14 => 0.013/day, would show in
  3-decimal printout). z=1824/(-1824) values are OUTSIDE any plausible
  star extent (new-game z range ±402). STRONGLY [inferred, geometry-cited]:
  st5 lane-march xyz is SYSTEM/ROUTE-LOCAL frame (lane along +x), not
  galactic world — the 1100-2500u 'discontinuities' at st4<->5 flips are
  REFRAMES, not transits. NB campaign §17-T3 'world units 123-2278'
  nearest-star distances were from OLD campaign runs (r1deep), a LARGER
  map than the new game — do not mix ranges.
- Big movers census: 27 rows, ALL attach to st4<->5 or st4->4 flips
  (5->4 x14, 4->5 x11, 4->4 x2), each row ALSO flips k59 — consistent with
  REORDER/reframe, zero big steps on st5->5 rows.

## FINDING 2 (t188, scripts/r1_t188_words_dump.txt + r1_t188_speedword.py,
## both RC=0): THE STATE-5 LANE MARCH IS A LANE-PROGRESS COUNTER, NOT THE
## T1 WALK LAW, AND ITS STEP IS TARGET-SCOPED, NOT SHIP-SCOPED
Word trace of the marching slots (first trusted row per turn, t1250..1340,
raw 177-u16 windows; work/r1/t188_words_dump.txt):
1. MOVES [+0x94] and POWER/FUEL [+0x88] are FROZEN for the entire march
   (every consecutive-turn delta measured 0: slot10 12/90 constant across
   t1250..1271 while x advanced 28/turn; slot13 4/12 constant across
   t1250..1295 while x advanced 14/turn). T1 (FUN_00049f54) SPENDS both
   ([+0x88] -= steps; [+0x94] := round(remaining walk)) => the st5 march
   does NOT run through the T1 commit path. MEASURED-NEGATIVE, 20+ rows.
2. Position along the lane is exactly x = k*step with k = turns since lane
   ENTRY (entry row has x == step: slot13 x=14.0000 at t1252 re-entry,
   slot10 x=28.0000 at t1262, slot17 x=4.6667 at t1262), and step is one of
   {14.0000, 28.0000 (=2x14), 14/3 = 4.6667} measured to 4 dp — 4.670 in the
   t187 dump was rounding, the exact value is 14/3.
3. STEP IS NOT A SHIP STAT. Slot 13 and slot 17 are the SAME owner (1), and
   a whole-record diff across 23 turns shows the ONLY u16 that is stable
   within each slot yet differs BETWEEN them is +0x52 (629 vs 770 = the
   route/target handle). Every other differing word varies turn-to-turn
   (position, fuel, state). PROOF from one ship: slot 13 marched step=14 in
   the z=1824 and z=-1824 lanes (t1252..1289) and step=14/3 in the z=544
   lane (t1301 x=28.0000 -> t1306 x=51.3333, 5 turns x 14/3) with d10=4,
   MOVES=4, POW=12 UNCHANGED throughout. Speed is therefore a property of
   the LANE/TARGET, not of the drive stat sum.
4. GEOMETRY: y is EXACTLY 0 or 1 across every lane row; z is always an exact
   multiple of 32 (1824=57x32, 544=17x32, 352=11x32, 1600=50x32, 32=1x32,
   -2144=-67x32, 2272=71x32); the st4 frame values are ALSO exact multiples
   of 32 (-1376=-43x32, 416=13x32, 1600=50x32) — the DAT_000895dc=32 grid
   law (T3) holds in the st4 frame; st5 lane x is off-grid exactly as T3's
   "off-grid ships are mid-transit raw offsets" carve-out predicts.
5. STATE 4 vs STATE 5 SEMANTICS (corpus, cited): state flips and FRAME flips
   are the same event. slot10: t1253 st5 x=224 z=-352 -> t1254 st4 x=-1376
   z=384 -> t1255 st5 x=28 z=352 (lane re-entry at x=step). Re-parse of the
   t187 dump: 25 of 27 big-mover rows (>300u) are 5->4 (x14) or 4->5 (x11),
   the other 2 are 4->4; ZERO big steps on st5->5 rows. So the 1100-2500u
   "discontinuities" are state/frame transitions between the on-grid node
   frame and the lane-progress frame — NOT instant flights. Magnetron
   (0x220a8+0x21f58 placement, ships.md S19) is EXONERATED for these rows:
   it writes +0x58:=5 with star-triple+rng%200 jitter, which would put the
   ship OFF the 32-grid, and none of the st4 rows are off-grid.
6. t187's "lane FLIP at t1277->1280 (z=1824 -> -1824, xy reset 224 -> 28)"
   = lane change (ship reached lane end x=224, entered the opposite lane at
   x=step) — consistent, not a turn-around mystery.

## Scale-law starting state (static law already cited, ships.md §17)
  d       = d_w * 0.00625            (= /160; f@0x25ff)  world->sugar
  walk    = min(d, float[ship+0x94])  (MOVES is SUGAR units)
  steps   = max(1, round(walk))
  if POW[+0x88] < steps: walk *= POW/steps; steps := POW
  per-step displacement = normalize(delta)*(walk/steps)*32.0*5.0
  => 1 sugar cube = 160 world units (verified FMUL pair 0x2603/0x2607).
Corpus regularities to explain (t187 scale dump, first-row snapshots):
  owner-0/2 lane movers: 14 u/turn @MOVES=4,6 and 28 @MOVES=12
  owner-1 lane movers:   4.67 = 14/3 u/turn @MOVES=4 (exact thirds ->
    an integer /3 divisor somewhere, owner/species-specific)
  state4 mid-turn lane movers: 448=(32,576,-288) component grid etc.
  frame-reframe jumps 1100-2500u at 4<->5 flips (UNVERIFIED).
