# _wip_t208 — positive end-to-end pin for the t207 guarantee-war clamp

Trigger triage: live-timeline.jsonl mtime 1793294532 / size 5,721,578,066 ==
TRIGGER-A frozen baselines; dosbox-x down; tree clean at e77fd03. No sitting
-> STATE t208 assignment stood.

## S1 — fixture anatomy (read, this session)
- Wiring site: campaign.cpp combatPhase capture branch — t204 handler at
  :1935 (applyAttackDipCost, needs a==kPlayer + war bit), gate :1946
  (invadesAlwaysSucceeds -> charge ind_ shipCostC else hullHit>defenseScore),
  clamp guaranteeWarOnInvasion at :1967, owner flip :1969, `break` :1975.
- Player guaranteed-capture lever EXISTS: CampaignConfig::playerSpecies
  (campaign.h:131) -> ability_[kPlayer] set in ctor :234-235;
  invadesAlwaysSucceeds(0) == SuperMarines. Gap was ONLY: fixture never set
  playerSpecies and ind_[0] starts 0 (ctor :204) while the gate demands
  ind_[0] >= shipCostC (Ship cost 20) at the engagement turn.
- ind_ accumulates as a stockpile in incomeAndGrow BEFORE combatPhase, but
  the t1 player home-star industry is not measured-citable, so the pin must
  not depend on it -> new thin pin-surface setter setIndustryForTest (same
  established ForTest idiom as setStarOwnerForTest/setWarForTest).
- Post-advance attitude bookkeeping: combatPhase clamps to 280, THEN
  diplomacyPhase (same advance()) runs decideDipAction on 280: 280 < DECL 290
  -> DeclareWar -> st.atWar=true and st.attitude = (280 + mood-term) -
  negPlayerTurns/4 (diplomacy.cpp:243). mood(turn 1)==0 empirically (t204's
  pin asserted att==320 AFTER advance()). The pin therefore replicates the
  chooser formula (incl. the m<0 doubling arm, diplomacy.cpp:163) instead of
  hardcoding, and ALSO asserts the distinguishing consequence
  st.atWar==true (no-clamp fixture keeps it false: att 320 -> act None).
- Negative side already pinned (T3 invasion_combat_phase_clamp_t207: player
  NO ability -> repelled -> -20 only, 320). T3 must keep playerSpecies=-1.

## S2 — code delta (IMPLEMENTED this session)
1. campaign.h: void setIndustryForTest(int owner, double v) { ind_[owner]=v; }
   next to the other ForTest hooks. HEADER-INLINE SCENARIO HOOK ONLY — no
   production call site, zero semantic delta -> blast radius UNCHANGED
   (Control t1255 / Extinct t979 stand per the t206 precedent rule).
2. test_invasion_war_t207.cpp: buildFixture207 gains an int playerSpecies
   param (T3 passes -1; new T4 passes SuperMarines=0); NEW T4
   test_invasion_capture_war_e2e_t208: 340 pre -> war -> industry 50 ->
   advance(): capture runs (starOwner(1)==0), handler -20, clamp 320->280,
   chooser flips st.atWar==true and attitude == replicated expected
   (280 + mood(1) - negPlayerTurns/4); attacked mark bit1 set.

## S3 — residue-line housekeeping (STATE item 2)
- OPEN-QUESTIONS OQ-016 + ai-dossier gap row 13: 'planet-event callers
  unwired' is stale — both callers READ t207 (bombard = honest no-delta;
  invasion = clamp WIRED, attempt-time-vs-under-fire position documented);
  residue now = 'per-ship invasion/bombard channel = OQ-019 family' +
  zero in-corpus clamp witnesses (strict-close keeps row open).
- _wip_t207 S7e residue (a): CLOSED by this session's T4 e2e pin.

## Results (this session)
- Self-caught bug: first T4 run failed 3/3 arms because I added the
  playerSpecies PARAM but never assigned cfg.playerSpecies — capture never
  ran. Fixed in buildFixture207. (Same class as t207's 320!=280 self-catch:
  the e2e side fails LOUD, which is the point of an e2e pin.)
- run_tests: 134 tests, 0 failed (was 133; +invasion_capture_war_e2e_t208).
- T3 pin UNCHANGED (default playerSpecies=-1 keeps the negative arm).
- gate: see STATE LANDED block (run after docs complete).
