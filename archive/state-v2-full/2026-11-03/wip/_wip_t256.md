# t256 WIP — AI gap row 11: the 16 SA_ bodies vs the cited §6.3 laws

Task (STATE NEXT): ai-dossier.md gap map row 11 (16 SA_ bodies, §6.3/aicode
6.3). Row text is STALE: claims RepelAlienShips + BlockStarLanes are "still
FILED NO-OPs" — both are WIRED (campaign.cpp:1649 Repel erases in-transit
ships targeting own stars; campaign.cpp:1714 BlockStarLanes sets laneBlock_
consumed at :1490/:1893). Work = audit every body against the CITED law,
upgrade cheap representable divergences, pin, restate row 11 with evidence.

## S0 — trigger triage
- git clean at 03b1fe5 (t255). No new playcap-* dir under work/r1/playcap/
  (only caps/save + evidence file) -> no user sitting; assignment stands.
- Live dosbox PID 479968 running (:9 self-play); timeline 7,171,239,056 B at
  12:28 — always-growing watcher, NOT adjudicated as a sitting (t247 law).

## S1 — cited-law inventory (aicode.md §6.3 t99, cadence §6.4 t100/t105)
profile -> body -> cited effect -> rewrite reading:
 5 HealShips 0x43baf: own ships integrity:=max. rewrite: fleetDamage_=0. OK-ish (no per-ship hull; OQ-019).
 6 ForcePeace 0x43bf0: every OTHER row attitude-toward-self floored to ACCEPT_PEACE(+0x1cb)+20. rewrite: ends all own wars via symmetric war_ bits. DIVERGENT MECHANISM (no AI-AI attitude vector exists).
 7 DoublePower 0x43c3f: own ship +0x88 POWER <<=1. rewrite: volley*=2 this turn (:1919). OK.
 8 RepelAlienShips 0x43c79: alien ships order-kind==4 (attack) at own stars are REPLACED AT THE STAR (jittered), not destroyed. rewrite: ERASES in-transit ships whose target is own star. DIVERGENCE: destroy-vs-return + no order-kind gate.
 9 SapAlienPower 0x43d33: alien ships at own stars +0x88 := 0 (POWER zeroed). rewrite: fleetDamage_ +=15 (8 vs DoubleHull) to at-war owners adjacent to own stars. DIVERGENT magnitude + DoubleHull halving is a rewrite-invented channel (help.txt has no halving law).
10 Cornucopia 0x43de4: MIN word [p+0x42] planet (skip [p+0x16]==10): slot classes {0,1} := uniform {2,3,4}. rewrite: richPros+=2. DIVERGENT (no slot model; the rng draw in original is irrelevant to rewrite RNG discipline since abilities don't draw dip-pair noise).
11 BumpShipsInLanes 0x43e98: ships in lanes := placed at lane star. rewrite: fleet_.clear(). OK under no-idle-fleet model.
12 StealTech 0x43eec: popcount(ownermask)>>=2 -> OR own bit; IF row == own target (0x76492[2self]==i): target := 0xffff + accumulator recompute. rewrite: holders>=2 -> own (matches help.txt L2154); MISSING the target-reset leg.
13 Shield 0x43fba: own planets [p+0x62] := 0xffffffff. rewrite: invincible_[s]. OK.
15 KnowStarLanes NOP | 18 FastLaneTravel NOP (0x4400a). rewrite: passives (t195 visibility seed / +1 hop). OK.
16 BlockStarLanes 0x4405f: own stars' LANE ENTRIES byte[+0x23] |= 2. rewrite: laneBlock_ per star consumed as lane gate. OK shape.
17 Hatred 0x440b5: for every other row r state==2(AT WAR): every third x (not self/r): if attitude(x->self) > r.DECLARE_WAR(+0x1c9): := r.DECLARE_WAR. rewrite CauseWar: flat -250 on at-war-with-player races. DIVERGENT (ceiling law vs invented flat delta; no AI-AI matrix).
19 FreeResearch 0x4414e: iff own target t != 0xffff: progress := cost(75*t law t105). NO pick-if-none. rewrite: queued else CHEAPEST AVAILABLE completes. DIVERGENCE: rewrite fires when nothing queued.
20 IndustryBoost 0x4418e: own planets ([p+0+54]!=0xff): WORD [p+0x50] += 100 (build accumulator). rewrite: IND stockpile += 20 [documented default]. CANDIDATE UPGRADE: +100 per planet accumulator.

## S2 — decisions (this session)
D1 Scope: fix the three cheap exact-law divergences that need no new state:
    FreeResearch target-gate, StealResearch target-reset leg, IndustryBoost
    magnitude. Leave ForcePeace/Hatred mechanism divergence documented (needs
    the AI-AI matrix = row 12's missing state); leave Sap/Repel/Cornucopia as
    model-level abstractions (per-ship = OQ-019 boundary).
D2 Row-11 restatement must carry the stale-text correction verbatim.

## S3 — LANDED (code + pins)
U1 SA_FreeResearch (campaign.cpp abilityPhase): removed the UNCITED
   "pick cheapest if none queued" leg; completes ONLY the queued row
   (cited 0x4414e target!=0xffff gate). queuedTech=-1 + progress=0 mirror
   the original's re-pick sentinel.
U2 SA_StealResearch: added the MISSING target-reset leg (cited 0x43eec:
   stolen row == own target -> target := 0xffff).
U3 SA_IndustryBoost: ind_[o]+=20 [documented default] REPLACED by the
   cited per-planet law 0x4418e: every own planet with pendingItem>=0
   ([p+0x54]!=0xff gate, income-law S8) gets buildAcc += 100. ind_ was the
   WRONG OPERAND (ship-launch budget; buildPhase never pays ind_ into a
   planet queue — campaign.cpp:1027 pays storedIndFor(s)).
U4 SA_CauseWar: flat -250 REPLACED by the cited SA_Hatred 0x440b5 CEILING
   law via new pure static Campaign::hatredClamp(warWithSelf, rLine, &att)
   (campaign.h, same pin pattern as absorbSplit): for every belligerent r,
   every third-party cell (x != r) > r's DECLARE_WAR word := that word.
   Projection [documented]: cells exist only for AI->player, so the law
   runs iff self==player; AI-owned CauseWar announces only.
   MEASURED consequence (probe): clamped onlooker under its OWN
   DECLARE_WAR trips the chooser the same turn (race05 line 300 > clamped
   290+mood -> DeclareWar + negPlayerTurns/4 penalty) — the "hostility
   diverter" effect emergent, not invented.

## S4 — pins (test_species.cpp, 3 new; 137 tests 0 failed)
P1 species_cause_war_hatred_ceiling_t256: pure-law exact (clamp lands on
   line; x!=r exclusion; cells <= line untouched; multi-belligerent order)
   + integration (live campaign seed 32, 5 onlookers clamped from 620,
   belligerent cell untouched >400).
   PITFALL (self-caught first cut): asserting a tight +-8 band around
   290+mood FAILS because a clamped onlooker whose own DECLARE_WAR > the
   line declares war the same turn and pays negPlayerTurns/4 (race05:
   290-22-1=267). The cascade is the law's intent — assert directionally.
P2 species_industry_boost_is_per_planet_accumulator_t256: control
   differential (seed 33 ability-on vs -off; boosted total(items*1000+acc)
   strictly leads after the fire turn).
   PITFALL (self-caught first cut): per-planet delta>=100 FAILS because
   the +100 COMPLETES the project that turn (acc 36+100+tick >= cost ->
   reset 0; probe-observed on seed 33 star 10). Completion-reset bounds
   the accumulator far below 100 — pin via differential, never delta.
P3 species_free_research_completes_only_the_queued_row_t256 (seed 34,
   cad 89: the queued row is the completed row; single completion event).
Debug harness pattern: standalone g++ against rewrite/build/libascend_core.a
with -DASCENDANCY_SOURCE_DIR=<repo root> (CMake sets ${CMAKE_SOURCE_DIR}/..;
extracted/ lives at the REPO root — pointing the define at rewrite/ aborts
the shared() loader, self-caught).

## S5 — blast radius (measured)
- Default AI slots = specnums 0..5 (main.cpp roster-order, player species
  skipped), so CauseWar(17)/FreeResearch(19)/IndustryBoost(20) NEVER enter
  the default/gate scenarios. Gate seeds unaffected:
  seed 2024 Control t1255 FINITE (verbatim), seed 42 Extinct t979 FINITE
  (verbatim). PLAYTHROUGH.md numbers unchanged.
- kNotes CauseWar/IndustryBoost lines updated to cite the body laws
  (probe asserts 21/21 cite [help.txt L — still holds).
- abilities.md kNotes probe: gate 3m runs ability_probe.py — pending gate.

## S6 — ledger honesty
NO ledger row closed this session (strict-close). Gap-map row 11 is a
ai-dossier.md work item, not an OQ; its restatement records which bodies
now carry cited laws vs documented abstractions. OQ count unchanged: 4 open
(OQ-005, OQ-016, OQ-019, OQ-021 — STATE standing laws).
