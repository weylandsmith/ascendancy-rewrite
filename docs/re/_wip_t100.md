# t100 WIP — REWRITE: measured per-ability cadence table (OQ-020 closer)

Assignment (STATE.md NEXT ACTION t100): replace abilityChargeTurns'
plausible-default 30 (rewrite/src/game/species.cpp:85) with the CITED word
table (aicode.md §6.4), wire abilityPhase (campaign.cpp:1076) to the
original counter semantics (row+0x19e: +1/turn, reset-on-fire, fire iff
counter == cadence word), pin the table in tests, run the suite.

## Cited table (copy verbatim from aicode.md §6.4 — do NOT re-derive)
WORD[0x6780 + 2*ability] (live 60.sav == restored FILE 0x89330; zero stores
image-wide => constant table):
  cad[5]=60 6=100 7=62 8=77 9=90 10=150 11=70 12=63 13=66 14=72 16=92
  17=100 19=89 20=68; ZERO at 0,1,2,3,4,15,18,21
  nonzero set == rewrite chargedIdx exactly (14 abilities).

## Cited counter semantics (aicode.md §6.1/§6.4)
- row+0x19e +1 per turn in FUN_0003e6e0 tail (0x3e7cf..0x3e805) iff
  [[row+7]+0x14]&0x80; PLAYER ROW EXCLUDED (0x43b50 gate at 0x3eb1d is on
  the per-race AI loop call sites 0x25083/0x250a5 only).
- FUN_00043b50 gate 0x43b58: WORD[cad] > counter -> return -1 (not-due);
  dispatch iff counter == cad EXACTLY (equal passes gate; >cad never routes
  to a body — it takes the counter-bump exit 0x4400a).
- FIRE EXITS: T1 0x4400a counter := 0 (reset-on-fire, all bodies);
  T2 0x43fe5 (profile-13 body) counter := cad - counter (phase-preserving).
- UI leg 0x37b6c dx==1 shows cad - counter.

## Rewrite state read (before delta)
- species.cpp:85 abilityChargeTurns = `charged ? 30 : 0` (placeholder).
- campaign.cpp:232-234 init: charge_=0 then charged owners set to FULL
  (count-DOWN model); abilityPhase 1089: `if (--charge_[o] > 0) continue;
  charge_[o] = abilityChargeTurns(ab);` then switch fires the body.
- chargeFor(owner) accessor (campaign.h:163) used ONLY by tests.

## Landing decisions
1. COUNT-UP faithful model: charge_ == row+0x19e (turns since last fire).
   abilityPhase: `++charge_[o] != cad -> continue;` then reset 0 (== the
   original's 0x441c9 pre-dispatch store esp+0x6c8=0 -> T1 exit), then run
   body. Init = all zeros (first fire exactly at turn cad).
2. T2 (profile-13/SA_ShieldPlanets counter := cad-counter): under the
   fires-at-exact-equality law counter==cad at fire -> T2 stores 0 == T1.
   No separate code; cited comment instead.
3. Original excludes the PLAYER row from firing (0x3e7cf tail exit after
   bump [verified F7]); the rewrite's auto-fire-player-ability is the
   documented sim model (abilities.md §2) — KEPT, comment notes the
   original asymmetry. AI-enable bit [[row+7]+0x14]&0x80 has no rewrite
   analogue (all AIs enabled; scenario scenario-template OQ-016 residual).
4. kCad[21] = {0,0,0,0,0,60,100,62,77,90,150,70,63,66,72,0,92,100,0,89,68}
   — verbatim §6.4.
5. GATE 3m breaks by design: expects SA_HealShips by turn 40 (old 30).
   HealShips cad=60 -> raise stage to --campaign 65, update strings.
6. Campaign timelines shift (StealResearch 63 vs 30 etc. change state) ->
   record_playthrough.sh re-run + finiteness check <1200 (t89/t93 pattern).
7. Ledger: OQ-020 CLOSES (row subject = SA_ charge period, cited + wired +
   pinned per its own t99 closing criterion); item-ability amass note kept
   inside as out-of-scope per T57b ("separate object" finding).
   ledger_audit default --expect drops OQ-020.

## RESULTS (final)
- scripts/r1_t100_cad_verify.py RC=0: C++ kCad == FILE 0x89330 == LIVE
  60.sav (all 21 words byte-exact; nonzero-set + F9 pins OK). Live-leg
  trap: high-entropy anchor vote against the CURRENT game/ascend.exe is
  WEAK on this save (exe differs from capture-time needle — t98 context);
  deterministic anchor = b"\x1e\x00Factory" at B+0x82bb0+0x73e40+8 (item
  record's cost u16 then name) -> B=0x1bf4d8, matching STATE's pinned base.
- Build clean; 110 tests 0 failed (schedule pins t60/t120, cadence words
  ForcePeace 100, ShieldPlanets 66, BlockStarLanes 92, MoreMaxPop 72,
  Cornucopia 150, StealResearch 63).
- Timeline seeds UNCHANGED by the law swap: 2024 Control t737, 42 Extinct
  t688, 13 Extinct t503, 1 Control t836, 2 Control t657 — PLAYTHROUGH.md
  already current, no regeneration needed; record_playthrough.sh comment
  updated (t93 stale-echo issue from its own LANDED note closed).
- Gate 3m 40->65 turns (HealShips cad 60 fires t60 <= 65).
- Docs: abilities.md §2/§3/§5 + species.h header comment rewritten to the
  measured law; OPEN-QUESTIONS OQ-020 row CLOSED with both legs + code
  sites + caveat; STATE ledger mirrors; ledger_audit default open set =
  {003,005,016,019,021,023}.
