# t377R WIP — MAGNETRON USE-SITE CODE LANDING (queue row t377, phase 9)

## S0 session state (2026-11-12 ~00:0x EST)
- STATE.md NEXT ACTION = t377R: execute docs/re/_wip_t377.md S3 verbatim in
  rewrite/src/game/shipsim.{h,cpp} + pins test_shipsim_t377.cpp + mutation
  campaign per the mutation-campaign skill (checkpoint FIRST).
- Sitting check RING-FIRST: scripts/t368_ring_turn.py parsed=20/20
  max_turn=1254 min_turn=1254 (same turn as t377's bank
  work/r1/bank-play-20261111-t377/). 1254 > 1086 => standing rule: run
  r1_t85g_sitting.py BEFORE the assignment -> launched background
  work/r1/t377R_sitting.out (result recorded in S0b below).
  NOTE t377 already adjudicated the 15:33->21:35 span (zero ship-record
  events, feedcheck 2236 frames diff 0/40); the ring cmp check this session:
  41.sav/60.sav cksums DIFFER from the 21:16 t377 bank => the ring kept
  cycling within turn 1254 after the bank (autosave rotation), not a new
  sitting. Adjudication output confirms/expands below.
- Evidence base: docs/re/_wip_t377.md S2 (C1..C8, verbatim static) + S3
  landing contract; docs/re/ships.md S64 (witnesses M1-M6). Static windows
  NOT re-read (NEXT text forbids; S2/S3 carry everything).
- Tree clean at session start (HEAD 9a53015).

## S0b sitting adjudication result
`r1_t85g_sitting.py work/r1/playcap` completed (work/r1/t377R_sitting.out):
presence events t>=1240 are EXACTLY the t1253->1254 boundary already witnessed
as M5 (s40/s39/s38/s37 vanish, owner-change 2->4 AI rows, s40 appear t1240)
plus t<=1054 history rows; the t=1335 block is the Oct-28 echo the t377 FEED
LAW predicts (sitting tool unfloored). Mid-turn offset census sitting t>=1240
vs baseline: owner=0 +0x88 x149 (power, glide) — no NEW offset class (no
+0x15e ring-removal burst beyond baseline x109). => NO new witness since the
t377 feedcheck span; M1-M6 remain the complete evidence base; t377R stands.

## S1 landing contract being executed (from _wip_t377.md S3, condensed)
Seam: public MagnetronReport useMagnetron(int shipId, int mode) =
dispatcher-entry composition for the kind-2 handler on the ACTIVE slot.
Order: C7 ammo law (numUses==0 unlimited; use==0 BLOCK before handler; DEC
mode-1-only, BEFORE handler, ungated by handler gates) -> C1 range gate
(FAIL iff dist < Range*32; Range==0 skips; dist from target triple) ->
C2 bit0 = affordable(cost<=power) AND rangeOK, bit1 = TARGETLANE flag
(return word only, commit tests bit0) -> C3 charge power -= min(power,cost)
at commit -> kind-2 tail case tree (cidx 0x3c magnetron leg only; other
legs named non-goals) -> 0x220a8 target gate (sim: targetStar must resolve)
-> kind:=5 -> target:=star -> placement C5 (star triple + (0,-200,0) +
two draws %200 on x/z) -> snapGrid -> kind:=4 -> clearSlot(activeSlot) [C4,
idx rebuild = identity in the sim's index space].
mode-0: DEC skipped (mode-1-only), 0x4cbcd exits before any store -> pure
probe, lands NOTHING.
Pins (queue row): burn-exact (M1 power 90->80, cost 10 = gizmos.txt row 60);
slot consumed-once; no second use (use-word 0 -> handler never runs);
zero-carried never fires; gate-fail-DECs-still (C7, mutant-visible); mode-0
probe lands nothing. Mutation targets = these six.
Honest negatives carried: which star (S64 neg-a) unreconciled — pins assert
placement FORM + delta class, never vendor coordinates; TARGETLANE bit1
consumer elsewhere (C2).

## S2 adjudications made during landing
(TBD as code lands)
