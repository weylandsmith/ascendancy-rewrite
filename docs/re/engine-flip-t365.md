# engine-flip-t365 — the per-ship engine IS the combat engine (LANDED 2026-11-10)

User ruling D2=(b) (docs/DECISIONS.md USER RULING 2026-11-09): "per-ship
becomes THE engine once it passes the pinned-seed suite; aggregate demotes to
a test oracle during the transition, removed after seeds agree." t365 EXECUTED
that flip.

## SHAPE
- rewrite/src/game/campaign_fleet_bridge.{h,cpp}: CampaignFleetBridge owns a
  ShipSim and presents ONE operation, resolveEngagement(attacker, defender,
  star, popA, popB, fleetDamage, doublePower, gizmos, techCount, ownedA,
  ownedB) -> Outcome{ran, captured, hullHit, shots, volleyBase,
  shieldCharges}. Campaign::combatPhase() calls advanceBoundary() once per
  turn + resolveEngagement() per border engagement; the capture verdict is
  out.captured (garrison death, cited finalizer C4).
- rewrite/src/game/aggregate_oracle.{h,cpp}: the OLD aggregate math
  (aggregateVolley / weaponLevelSum / aggregateHullDefense / absorbSplit)
  moved VERBATIM from campaign.cpp. Campaign::attackScore/defenseScore
  remain as PIN SURFACES that delegate to it (test_campaign pins unchanged).
  Production combatPhase no longer calls them. [verified by grep: callers
  outside tests = campaign.{h,cpp} delegation only]
- Bridge surrogate ledger S1..S12 lives in the bridge header (garrison-as-
  ship S1, synthetic pop-reserve row S2, power-gate-only sapping S3, reset-
  per-engagement S-shape, chase-leg decision (a): targetPos := victim pos at
  stance time, isolated LCG S9 = zero campaign rng draws added/skipped).

## SEED AGREEMENT (the ruling's acceptance condition — MEASURED)
Pre-flip vs post-flip full headless runs, --campaign 1600, seeds 1 / 2024 /
23: byte-IDENTICAL logs each (diff -q), victories unchanged:
seed 1 Extinct t266 (end-xtnc), seed 2024 Extinct t285, seed 23 Control t1406.
Suite: 223 tests, 0 failed (run_tests). Gate: GATE_EXIT=0. P5 census test:
80 facts, 80 checked, 80 agreed, 0 sapped, 0 guaranteed.
Aggregate REMOVAL (N10) is now unblocked but is NOT t365 scope.

## THE FIVE FIRST-RUN BUGS (all real, all measured; full trace
## docs/re/_wip_t365b.md)
1. Dangling Ship*: ShipSim::ships_ is std::vector<Ship>; addShip may
   reallocate and invalidate every Ship*. Re-lookup after every addShip.
2. Garrison power top-up +1 could not AFFORD the shield upkeep scan
   (payable gate 0x4a70a skips unaffordable slots) -> 0 charges. Top up
   generously.
3. Missing refreshUseCounts before the FIRST commit pass: use words start 0,
   the ammo skip (0x4a37b) drops every shot.
4. setSlot guard is idx > invCap (idx == cap ADMITTED): the window must grow
   WITH the fill or every later slot is silently refused.
5. STALE STATE ACROSS RECORD REBIRTH (the seed-divergence root): records die
   (C4) and are rebuilt, but the bridge's row->slot map and the corpse's
   inventory survived -> cap=0/filled>1 -> companionScan refuses -> shots=0
   every turn -> zero captures -> seed-1 Extinct t266 vanished. FIX: reset-
   per-engagement — both records wiped clean (inv/cap/filled/stance +
   slotMap_.erase) at the top of every resolveEngagement; all verdict-
   relevant state is re-materialised by the cited laws (syncRows ->
   recalcShip, upkeep -> shields, setStance -> gate/stance/activeSlot).
   Rationale: the pre-flip aggregate was STATELESS per engagement; persisting
   engagement state across turns was the bridge's own flourish.

## LAW NOTES LEARNED
- loadGizmos NEVER assigns Gizmo::shield (economy.cpp:138-170); the shield
  charge law is SUM(cat-1 row Level) gated by requiresAvailable
  (campaign.cpp shieldChargesFor) == upkeep +0x90 materialisation per
  affordable slot (shipsim.cpp:277-291).
- InvSlot::payload default 0; the ONLY cited consumer is the upkeep -1 test
  (0x4a6f9; measured save-side, -1 sits on upkeep-gate rows) -> bridge sets
  payload 0xffffffff uniformly on synced slots (ledger S12).
- run_tests counts CHECK invocations, not tests: "223 tests, 118 failed"
  meant 3 failing TEST names. Read the per-test FAIL lines, not the summary.

## OQ-019 STATUS AFTER t365
The per-ship model EXISTS in production (the engine itself, not a spec).
Row stays OPEN per t329 packet — closes only on user ruling; annotate
"model exists, awaiting user acceptance".
