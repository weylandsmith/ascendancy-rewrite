# _wip_t265 — OQ-019 LIVE MINING: st4 mid-turn displacement + magnetron USE frames

PREMISE (from STATE queue): the t193 census found 2238 st4 samples with ZERO
mid-turn displacement, but the turn NEVER advanced in that window — a real
drive changes the premise. Corpus: the t261 drive (production :9,
2026-11-01 21:24 -> 2026-11-02 ~01:27, turns 1086->1236; per-turn row counts
verified from a bounded 200 MB tail scan: every turn 1087..1236 has rows).
Game :9 PID 535172 alive at session start. No loadstate used (REFUTED t261).

## S1. st4 MID-TURN DISPLACEMENT CENSUS (tools r265_st4_magnetron.py, r265_pass2.py, r265_pass3.py; pass-3 output work/r1/t265_pass3.out)

MEASURED (drive regimes A 21:24-21:37 t1086..1111 + B 23:07-01:27 t1112..1236,
mtime-bucketed; the lexicographic-wall-bucket bug in pass-3 v1 was caught and
fixed — "23:07:00"<="01:59:00" is False, everything after midnight fell out):

1. THE t193 PREMISE IS MEASURED-DEAD. With 150 real turn advances in the
   window, st4 ships STILL show ZERO displacement: 21 multi-row st4 runs that
   SPANNED >=1 turn advance (longest slot 13 t1086..t1236 = 150 turns, 1014
   autosave rows) have net d = 0.00 and a CONSTANT order byte k59 throughout
   (69/133/197/101/229). st4 in the autosave stream is a DWELL state, not a
   flight state — the in-system per-turn march is NOT observable at ring
   granularity because resting ships do not move and moving ships leave st4
   within a turn (all big movers are 4<->5 frame-switch transitions:
   boundary class census (4,5,True) x60 + (5,4,True) x67 vs (4,4,True) x6
   which are all in the softlock window).
2. st5 LANE MARCH IS TURN-ATOMIC AT SAMPLING GRANULARITY: same-turn
   consecutive-row x-deltas EXACTLY 0.0 in 16,497 pairs (zero exceptions);
   turn-boundary deltas EXACTLY {4.6667 x2554, 14.0 x268, 28.0 x6}. t187's
   "4.67/day = three sub-steps?" hypothesis is DEAD — a single 14/3 step per
   turn, the 4.670 print was rounding. Entry-x values are multiples of the
   step {4.6667, 14, 42, 56, 84, 163.3333, 196, 224} — corroborates the S21
   x = k*step counter law on a SECOND independent corpus.
3. st5 ROW-LEVEL FRAME LAW RE-CONFIRMED: lane-control class (y exactly 0/1,
   z on the 32-grid) 25,936 rows, other 0 — the lane frame never leaks.
4. st4 row-level on-grid 9,360, off-grid 0 (all regimes incl. softlock).

## S2. MAGNETRON USE FRAMES — HONEST NEGATIVE
W2 signature (st->5, d>300u, y in [-200,0) from the 0x21f58 -200.0 offset,
x/z off-grid from the rng%200 jitter): ZERO candidates in the full drive
window incl. both softlock sub-windows. Corroborating zeros: no off-grid st4
row anywhere (S1.4), no st5 row off the lane-frame class (S1.3). The AI held
cidx-60 slots (360 occurrences banked t185) across 150 driven turns and never
fired the device; the player was absent. The magnetron use-site law
(ships.md S19 T3) stays STATIC-CITED with zero runtime witnesses. Row OQ-019
STAYS OPEN (strict-close): the runtime-witness residue merely moved from
"st4 mid-turn displacement" to "no engine state observable at ring cadence
carries the in-system march or the magnetron placement".

## S2b. t266 FEED (bug-class, banked in passing)
The only st4 mid-turn displacement in the entire corpus is slot 30 inside the
softlock window (walls 21:41:44..21:54:06, d=32/64/160/64, turn readout FROZEN
at 1255): the engine was processing turn-tail movement WITHOUT advancing the
turn counter. The S1-oscillation pairs repeat identically 3x across slots
(same (dx,dy,dz) triples). Tell for t266: turn-frozen-but-tail-running.

## S3. KEEPER (scripts/r265_keeper.py RC=0, final numbers)
K1 st5 consecutive-turn boundary delta == step0 or step0/3,
   step0 = float(u16[+0x8]+u16[+0xc]) same window: 2,400+ pairs over 27
   handle groups, VIOLATIONS 0. (First run showed 14 "violations" of
   116.6667 = 25 x 14/3 — the 23:05 re-drive REWIND boundary t1111->t1086;
   the t189 law is a consecutive-turn law, so the keeper now gates
   t == pturn+1. Rewind-drop is the same class of law as r1_stream's
   stale-echo law.)
K2 same-turn consecutive st5 pairs: 17,595, all delta == 0.0 (zero exceptions).
K3 magnetron W2 frames (st->5 transition hunt): 0.
K3b landing census over ALL st4 rows: y mod 32 == {0.0: 6184} (single bucket);
   off-grid-x-or-z st4 rows: 0. Magnetron never fired in the drive epoch.

## S4. DISPOSITION
Full law text banked at docs/re/ships.md S24 (the authoritative version);
OQ-019 row updated in docs/OPEN-QUESTIONS.md (STAYS OPEN, strict-close —
the route died, no law closed, no rewrite default changes). t266 inherits
the turn-frozen-but-tail-running tell (S24 item 5).

