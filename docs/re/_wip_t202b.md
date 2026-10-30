# WIP t202b — DEMOLISH CHANNEL: code + pins (inputs = _wip_t202 S1..S13)
Trigger triage: timeline size 5721578066 == frozen baseline, md5(tail4k)
faa71c20 stable, dosbox down, tree clean at 9520c9a -> no sitting.

## T1 Scope (from STATE NEXT ACTION + _wip_t202 S14)
1. usedPopFor -> item-UPOP-sum (M4 2760/2900; excl item23, item flags&0x40;
   gov-35 term KEPT). Pending term REMOVED (INERT 2900/2900).
2. buildPhase AI branch: over-cap block 0x3f178 + triage gate 0x3f252 +
   sweep 0x3f354 + shared gate 0x3f41e, inserted BEFORE t201 chain block;
   t201 wiring untouched (S12 CORRECTION: faithful).
3. Pins: statics overCapDemolishPick/minRequiresDemolishPick + end-to-end.
4. Docs: ai-dossier gap row4 -> MODELLED; income-law.md S9 OVER-CAP para
   correction; OQ-016 STATUS t202b.

## T2 CODE FACTS (verified this session)
- usedPopFor campaign.h:220 (pending UPOP + gov35). Call sites:
  campaign.h:245 popBandsFor, campaign.cpp:846 needClassFor popMinusPend,
  campaign.cpp:1032 buildPhase usedPop.
- PlanetState (campaign.h:31): pop double, capBase, surfaceCells,
  cellClasses (bit8 rock, 0 barren/cls0), items (ACTIVE only), itemCells
  parallel vec, pendingItem, governor.
- storedCapFor campaign.cpp:745 = clamp(capBase + MPOP sum(items)) (+capBonus).
- PlanetItem (economy.h:30): ind/res/pros/mpop/upop/cost/requires/flags.
- itemIsSurface = idx < kPlanitemSurfaceCount (economy.h:66).
- abilityOf(o) == SpeciesAbility::BuildOnBlack <-> ability byte 2
  (species.h:15 enum: SuperMarines=0, DoubleHull, BuildOnBlack).
- Test harness: makeCampaign(seed) test_campaign.cpp:57; loads real 39-row
  planitem table from extracted/. NO mutation hooks -> end-to-end pin must
  find a naturally-occurring state OR drive many turns.

## T3 LAWS AS CODED (final from _wip_t202 S13)
- over-cap gate: usedPopFor(s) >= storedCapFor(s).
  victim = overCapDemolishPick(items, mpop, upop): cell order, skip item 5,
  skip mpop!=0, STRICT-max upop (first cell ties), init best 0 (upop==0
  never wins). none -> SKIP selector entirely (0x3f20b assert+return).
  erase items[k]+itemCells[k]; recompute used'; used'>=pop -> SKIP.
- non-over-cap: used>=pop -> SKIP (0x3f220).
- triage gate: RUN sweep iff eNR<2 OR (eNR==eB AND ab!=BuildOnBlack);
  eNR = empty non-rock surface cells, eB = empty cls-0 subset.
- sweep: margin = cap-pop; occupied cells only; skip mpop>=margin;
  strict-min requires (255 PARTICIPATES); first ties. Demolish.
- shared gate 0x3f41e (facts AFTER demolish recompute): eNR==0 -> SKIP
  chain+scorer; eB==eNR && ab!=BB -> SKIP.
- usedPop for scoring gates 0x3f587 recomputed AFTER any demolish.

## T4 PROGRESS LOG
- (init) reads done; starting edits: campaign.h usedPopFor + picker decls.
- usedPopFor UPGRADED (item-UPOP sum, excl 23/flags&0x40, gov-35 kept);
  overCapDemolishPick + minRequiresDemolishPick statics added campaign.h.
- buildPhase AI branch: full demolish channel wired (over-cap 0x3f178 ->
  recheck -> no-free-pop 0x3f220 -> triage gate 0x3f252 -> sweep 0x3f354 ->
  shared gate 0x3f41e -> t201 chain + scorer UNCHANGED). Cell-ordered slot
  view (stable_sort by itemCells; demolishAt rebases `order` indices — the
  two sweeps CAN both fire in one turn via the 0x3f22f fallthrough).
- BLAST RADIUS (measured, not guessed): 0x3f220 became REAL traffic — with
  used=item-UPOP-sum, an AI planet at used==pop queues NOTHING until growth.
  seed 42 first colony t169->t279; seed 2024 Control win t831->t1255 (CLI,
  FINITE). Widened pacing guards (each dated, law untouched):
  campaign_total_owned_grows 220->420 turns; species victory + ships
  expansion victory guards 1200->1600; gate.sh seed-2024 budget 1200->1600.
- PINS tests/test_demolish_t202b.cpp (CMake-registered; makeCampaignFor-
  Demolish shim exported from test_campaign.cpp):
  campaign_demolish_pickers_t202b (O1-O6/S1-S5 edge classes),
  campaign_used_pop_item_sum_t202b (23/0x40 exclusions, gov-35 reversible,
  band formula intact),
  campaign_over_cap_demolish_e2e_t202b (used==pop==cap -> ONE Factory gone
  in ONE advance(), CB alive, run reaches queue),
  campaign_barren_sweep_demolishes_cb_e2e_t202b (eNR==0 -> triage runs, CB
  REQUIRES-5 swept, Factory-255 survives).
  119 tests, 0 FAILED.
- DOCS: income-law.md S9 OVER-CAP paragraph corrected (largest-MPOP ->
  largest-UPOP-among-MPOP-0 w/ cited byte identities) + pre-triage gate
  folded into the sweep paragraph + sentinel reason corrected + M4 line;
  ai-dossier gap row 4 GAP -> MODELLED (tubes sub-item = dead-path note);
  OQ-016 STATUS t202b appended, row STAYS OPEN (strict-close: no in-corpus
  demolition EVENT witness; +0x54/0x3f4b8/M3-discriminator residues).
- TOOL: scripts/r202b_item_table.py (planitem dump mirroring loadPlanItems;
  pitfall: planitem rows are NAME-line THEN numeric-line, name may contain
  spaces, flags = 1<<pos over v[7:-1] — first two parses mis-aligned).
- GATE_EXIT=0; LEDGER AUDIT OK (open=['OQ-005','OQ-016','OQ-019','OQ-021']).
- HONEST NOTE: e2e pins mutate PlanetState via const_cast (t45 idiom) to
  FORCE the corpus shapes; the natural-traffic witness remains the corpus
  220/2900 census from t202, not a fresh live capture.
