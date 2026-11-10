# _wip_t365 — ENGINE FLIP: campaign turn loop calls shipsim (2026-11-10)

Task (STATE.md queue VERBATIM): campaign turn loop calls shipsim; aggregate
code demoted to rewrite/src/game/aggregate_oracle.{h,cpp} used ONLY by tests;
full pinned-seed suite green; gate green; DECISIONS.md D2 annotated APPLIED;
OQ-019 residue status updated (annotate 'model exists, awaiting user
acceptance' — row itself closes only on user ruling per t329 packet).

## S1 DESIGN (decided BEFORE coding, from the surfaces read this session)

D-0 MECHANISM: bridge class `CampaignFleetBridge` (rewrite/src/game/
  campaign_fleet_bridge.{h,cpp}) owning a ShipSim member. Campaign keeps NO
  direct shipsim member (shipsim.h includes formats/shipsave.h — keep it out
  of campaign.h); it holds a `std::unique_ptr<CampaignFleetBridge> fleetSim_`
  (forward-declared; Campaign has no user-declared dtor today, unique_ptr +
  incomplete type at header + complete type at campaign.cpp is safe).
  Shipsim.cpp itself is NOT modified this task (integration only; any shipsim
  law delta would need its own pins — none needed).

D-1 THE CALL SITE: Campaign::combatPhase() (campaign.cpp:1992) — the place
  combatPhase runs today per the queue wording. Per engagement (star s owner a
  attacking neighbour nb owner b, all pre-existing gates BEFORE any sim call:
  invincible_, lanePassable, fortify_, SuperMarines economy gate unchanged):
    1. seed: bridge seeds one attacker shooter in system nb per engagement
       NOT already fought this boundary + all defenders of nb (first turn
       only — sim state persists across boundaries in the bridge).
    2. attacker mode-0 probe volley (AI semantics K6: probes never apply,
       C3) -> aggregate volley = sum rowWeapon over the shooter's cat-0
       slots (volleyTail + companionScan seams). The probe mutates ONLY
       engagement state (+0x62/63/67/68/activeSlot), never damage.
    3. doublePower_ doubles the volley NUMBER (documented default rides the
       number, not the vendor Power column — named choice).
    4. absorbSplit(volley, shieldChargesFor(b)) -> hullHit (aggregate law
       stays the capture DECIDER; the per-ship two-layer absorb runs inside
       the sim for the model record, see D-4).
    5. hullHit > defenseScore(b, nb) -> capture branch EXACTLY as today
       (guaranteeWarOnInvasion, owner_, pop 2, fortify, event) — t204/t207
       pins preserved.
    6. MODE-1 COMMIT through the cited resolver: bridge.engage(race=b side
       defended? NO — race=a, target = a seeded victim stand-in in nb,
       objectivePlanetShielded = invincible_[nb], mode 1). Leg A can fire
       (carrier law); Leg B is first-eligible shooter -> commitShot(gates,
       ammo DEC, charge, two-layer absorb, death finalizer). Reported in the
       BattleReport per-ship fields.
  RNG discipline: shipsim's Lcg is ISOLATED (shipsim.h header law); zero
  campaign rng_ draws added or skipped -> seed trajectories can only shift via
  the sim INFLUENCING decisions, and it doesn't (D-2) — trajectories are
  expected IDENTICAL; the t365 pin measures that (honestly: agreement here is
  the seed-comparison oracle N10 evidence, not proof of behavioral equivalence
  — the sim does not yet DRIVE outcomes; that conversion is post-acceptance,
  N10).

D-2 VOLLEY-DRIVES-CAPTURE, NOT THE SIM YET (honest core of the flip): the
  aggregate capture math (attackScore/absorbSplit/defenseScore) remains the
  DECIDER because the sim has no pop-reserve analogue (defenseScore = local
  pop/10+2 is a documented default, not a cited law) and the pinned-seed suite
  is contractually about the campaign engine the seeds validated. The sim is
  THE engine for per-ship STATE (positions, engagement state, ammo, hull,
  deaths, carriers) and for the cited engagement law executed verbatim at mode
  1; the oracle records whether the aggregate decider and the per-ship
  resolver AGREE per engagement (oracleAgreements/oracleDisagreements).
  Disagreement data is the acceptance packet for the user (D2 ruling: "removed
  after seeds agree"). State it plainly in OPEN-QUESTIONS + DECISIONS:
  MODEL EXISTS, DRIVES STATE, DOES NOT YET DRIVE CAPTURE — awaiting user
  acceptance.

D-3 CHASE LEG (t364 named t365 scope): DECISION (a) — targetPos = victim pos
  at stance time, set by the BRIDGE when it seeds/stances a shooter
  (Ship.targetPos := victim->pos). The caller re-issues stance each boundary
  it wants pressure; no new shipsim field, no invented vendor law (the walk-
  toward-+0x68 leg is uncited; modelling it would invent). Named in ships.md.

D-4 aggregate demotion: attackScore/defenseScore bodies MOVE to
  rewrite/src/game/aggregate_oracle.{h,cpp} (namespace ascend::game),
  campaign.cpp keeps thin delegators (tests call attackScoreFor/shieldCharges
  For via public surface; delegate = zero trajectory change). The oracle files
  header states: test oracle per D2 ruling; capture decider until user
  acceptance; REMOVAL only after seeds agree (pership-spec N10).
  shieldChargesFor stays in campaign.cpp (empire tech state, not a combat
  resolver; the sim path uses it as the aggregate shield operand).

D-5 activeSlot default -1 (t364 seam): bridge always calls setStance before
  any commitShot; seeded shooters carry inv cat-0 rows from the GIZMO TABLE
  (gizmos.txt -> SimDesign via the bridge's designTable(): cat/power/range/
  level/numUses/industry/special1 + rowWeapon/rowShield per the recalc cat
  switch law; targetShip bit0; upkeepGate bit 0x20 — flags already parsed by
  loadGizmos).

D-6 PINS (test_campaign_fleet_t365.cpp): (P1) seeded bridge: two-empire
  engagement runs, per-ship state observable (hull drops, ammo DEC, corpse
  owner -1), determinism digest two runs; (P2) chase: shooter targetPos ==
  victim pos at seed time; (P3) capture-decider unchanged (oracle vs direct:
  attackScoreFor delta == sumWeapon still; existing t89 pin covers); (P4)
  full-campaign determinism: seed 2024 x2 traceLines equal 40 turns + a
  recorded digest of the sim state at t40 (engine-state pin); (P5) oracle
  agreement census over a 40-turn seed-2024 run (honest count, no threshold
  claim). Suite baseline 218 -> 223.

## S2 STATUS LOG
- sitting check NEGATIVE (8,917,535,608 B unchanged, 16/16 tail rows turn 1086).
- design banked (this file S1). coding next.

## S5 BUILD-AND-TEST REALITY (measured 2026-11-10, this iteration)
- Flip wired: campaign_fleet_bridge.{h,cpp} + aggregate_oracle.{h,cpp} added to
  rewrite/CMakeLists.txt ascend_core; Campaign gained fleetSim_ unique_ptr,
  out-of-line ~Campaign()/Campaign(Campaign&&) (incomplete-type plumbing),
  attackScore/defenseScore bodies moved VERBATIM to aggregate_oracle.cpp and
  now delegate; combatPhase() calls advanceBoundary()+resolveEngagement() and
  reads out.captured for the capture verdict.
- Shield law CORRECTION [verified economy.cpp:138-170 + campaign.cpp:1957-1970]:
  loadGizmos NEVER assigns Gizmo::shield (fields set: cat/power/range/level/
  numUses/industry=v[5]/special1=v[6]/special2=v[7]/resReq=v[8]/flags from
  v[9..end-1], v.back()==255). The campaign's shield charge is
  SUM(g.level for cat==Shield && requiresAvailable) — i.e. LEVEL, not a
  per-record shield field. A bridge that copies g.shield materialises 0
  charges and silently hands the defender no shield layer (sim dmgT = full
  volley), which is exactly the class of campaign-pin breakage seen after the
  flip (run_tests 154 failures).
