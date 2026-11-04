# _wip_t291 — UPGRADE the rewrite Control arm to the cited two-thirds law + blast-radius retrap

Session 2026-11-03 ~16:10. Task: STATE.md NEXT t291. Inputs: docs/re/_wip_t290.md
S1 (comparator V >= floor(2T/3)+1, V=DAT_482fb, T=DAT_16143, disasm file
0x24b9c..0x24bbe), S2 (sole caller 0x252e9, gate sel==0 AND [0x10ba4]==0).

SESSION-START SCREEN CHECK (t287 law): production pid 660167 alive
(`ps -p 660167` -> dosbox-x -conf work/r1/vnc/session.conf -nogui -time-limit
172800); ring work/r1/playcap/save/ fresh (43.sav 16:11); timeline tail scan
(<=400 KB, OOM law) max turn 1150 == the t289 driven point. NO new sitting ->
r1_t85g_sitting.py NOT run (nothing to adjudicate); t291 stands.

## S1. CODE SITE (pre-change, verbatim)

rewrite/src/game/campaign.cpp:2157 (checkVictory, last arm before None):

    if (mine * 2 > total) return Victory::Control;  // end-ctrl (OQ-021: "> half" vs prose "two-thirds")

`mine = starsOwned(kPlayer)` (campaign.cpp:2117). The vendor operand is NOT
starsOwned: it is V = scoreStars_ (DAT_482fb), the PRODUCED controlled-system
count from the pruned flood (score.md S17/S18, _wip_t290 S1). So the fix is a
different variable AND a different threshold.

rewrite/src/game/campaign.cpp:2262 recomputeScoreStars() sets scoreStars_ in the
end-of-turn pass BEFORE checkVictory() (advance(): recomputeScoreStars();
victory_ = checkVictory();) — ordering already correct for the new arm.

## S2. THE CHANGE

Control arm becomes:

    const int thr = (2 * total) / 3 + 1;
    if (scoreStars_ >= thr) return Victory::Control;   // V >= floor(2T/3)+1

(2*total)/3 is integer floor for total>=0 (all corpus T=50 -> thr=34). All other
arms byte-identical; arm-ORDER comment kept.

## S3. BLAST-RADIUS RETRAP (measured, pre vs post, --campaign 1600)

seed | BASE (mine*2>total)              | POST (V>=floor(2T/3)+1)
1    | Control t1131 (score 50%)         | Control t1337 (score 70%)
2    | Control t1110 (score 52%)         | Control t1427 (score 70%)
13   | Extinct t747 (score 0%)           | Extinct t747 (score 0%)   [unchanged]
42   | Extinct t979 (score 0%)           | Extinct t979 (score 0%)   [unchanged]
2024 | Control t1255 (score 46%)         | Extinct t1555 (score 0%)  [VICTORY-TYPE FLIP]

Readings: scores 70% are the flood metric (1+lanes scale, score.md S7 unit =
lanes), not 70% of stars. Seeds 1/2 still win Control, later (1337/1427 > the
1200/1600 windows in test_campaign_reaches_a_victory / campaign_advance_after_
victory_is_noop / test_species 1600-window). Seed 2024 FLIPPED: the player is
killed out t1553-1555 by owner 3 before ever reaching 34 controlled systems
(events tail: 'owner 3 captured ...' x5, then end-xtnc) — under the >half
default it took Control at 46% first; under the cited law 46% is not a win and
the war of attrition ran to the player's extinction. A VICTORY-TYPE CHANGE is
within the assignment's blast radius: the law stands, the seeded expectations
get re-pinned (t89 precedent: "finite resolve" is the contract, type-agnostic
for campaign_reaches_a_victory).

## S4. TEST SUITE STATE (measured)

- rewrite/tests/test_control_t291.cpp NEW, 4 pins, all ok:
  control_threshold_t50_t291 (V=33 None / V=34 Control at T=50);
  control_bar_is_two_thirds_not_half_t291 (T=14: V=8 and V=9 None, V=10 Control
  — a galaxy size where 2T mod 3 != 0 separates the readings; T=50 cannot);
  control_operand_is_v_not_owned_t291 (owned>=8 of 14 with V staged to 1 ->
  None; V=10 -> Control);
  control_end_to_end_flood_wins_t291 (real advance(), 1-AI map, revealed:
  producer-then-comparator wiring reports Control).
- Pin surface additions campaign.h: checkVictoryForTest(),
  setScoreStarsForTest() (documented thin setters, existing ForTest pattern).
- Factory shim makeCampaignSized(seed, aiCount, starCount) exported from
  test_campaign.cpp (t202b wrapper precedent) — makeCrafted is anon-namespace
  in test_species.cpp and not linkable.
- MUTATION-VERIFIED: (M1) threshold reverted to total/2+1 -> CAUGHT, 3 failures
  across control_threshold_t50 + control_bar_is_two_thirds; (M2) operand flipped
  scoreStars_->mine -> CAUGHT, 4 failures incl. control_operand_is_v_not_owned.
  Restored -> 170 tests, 0 failed.
- test_score_t284.cpp: NO >1/2-shaped expectations (grepped: all CHECKs are on
  the flood producer itself) — no updates needed there.
- test_campaign.cpp expansion-window test (420) unaffected (monotonicity only).

## S5. DOCS + GATE WIRING (measured)

- docs/re/score.md S19 appended: permanent distillation of _wip_t290 S1-S3
  (comparator law, caller/gate, result map + presenter table, rewrite upgrade)
  per assignment item (6) — _wip files are working logs, not durable citations.
- docs/re/turnloop.md §1 Control row rewritten from [inferred] >1/2 to the cited
  law with the t290 cite.
- docs/PLAYTHROUGH.md REGENERATED via scripts/record_playthrough.sh (rc=0, 97
  lines; hand-author trap avoided — BLOCKED.md says it is generated output).
  Script budgets 1200 -> 1600 with dated t291 rationale; run B re-pinned seed
  42 -> 1 (42 is an Extinct seed; the gate greps PLAYTHROUGH for BOTH
  'VICTORY Control' and 'VICTORY Extinct' — run A (2024 Extinct t1555) + run C
  (13 Extinct t747) keep the Extinct grep green, run B (seed 1 Control t1337)
  carries the Control grep).
- gate.sh 4b runs `--campaign 1600 --seed 2024`: post-law that run ends Extinct
  t1555 < 1600, exit 0 with a '^VICTORY ' line -> gate assertion unchanged, no
  gate edit needed (the guard's target is stall, not victory type).
- OPEN-QUESTIONS OQ-021: STATUS t291 appended, row STAYS OPEN (strict-close);
  sole residue = live end-ctrl presenter witness (sel==5 @0x24d9f firing).
