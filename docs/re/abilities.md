# Species special abilities — roster, effects, and wired semantics

Closes the audit finding "SA_* tokens parsed but unwired".
Roster source: docs/re/species.md (history.txt + raceNN.dip headers).
Effect source: `extracted/ascend00/help.txt` blocks `help abilNN`
(L1713-2511, [verified] 21 blocks, gate 3m via scripts/ability_probe.py).
Code: rewrite/src/game/species.{h,cpp} (roster, charge split, effect notes),
rewrite/src/game/campaign.cpp `abilityPhase()` + hook sites.

## §1 Roster reconciliation [verified]

Three sources agree on specnum order 0..20:
- raceNN.dip header tokens `SA_<Name>` (20 of 21 files);
- help.txt `// SA_<T>` + `help abilNN` blocks (all 21; indices contiguous,
  tokens and titles unique — probe-asserted);
- history.txt blurb names (docs/re/species.md mapping).

**race02.dip is the exception**: its header is `Diplomacy text for Orfa.`
with NO token [verified raw bytes]; its ability resolves to SA_BuildOnBlack
via help-abil02 title "Orfa" + position agreement (loadAbilities cross-check;
unit test species_roster_three_source). Header display names are NOT
identity-checked on tokened headers — the two sources disagree on spelling
("KAMBUCHA" in race03.dip vs "Kambuchka" in the help title), so the token is
the identity.

## §2 Effect mapping (vendor text -> wired behaviour)

Charged abilities fire on the MEASURED cadence law (t100): a per-owner
counter counts up from 0 and the body runs on the turn it equals
abilityChargeTurns() exactly (first activation turn == cad), then resets.
One-shot flags clear at every turn boundary in abilityPhase(). Every
token's one-line note lives in species.cpp `kNotes` (probe asserts 21/21
cite `[help.txt L`).

| ability | help.txt | wired effect |
|---|---|---|
| SA_SuperMarines | L1723 "planetary invasions will always succeed" | invasion always captures, capped ONE per owner per turn and charged the Ship hull cost 20 (planitem.txt row, ships.md §1). Both constraints are documented consequences: the text guarantees an attempt, not N attempts; an invasion costs ships or the Minions take a star per border per turn (measured: extinction-of-all on 8/8 seeds, PLAYTHROUGH Control runs destroyed). |
| SA_DoubleHull | L1743 "double-strength hulls" | halves incoming SA_SapAlienPower hits (15->8; the only damage channel the model has — see below). |
| SA_BuildOnBlack | L1763 "build on black planet squares" | **FILED NO-OP**: the sim has no planetary grid/buildable-slot model; "black square" has no referent. Roster-visible, no state to change. |
| SA_KnowHomeWorlds | L1783 "see all alien home stars" | **WIRED t195 (OQ-026 CLOSED)**: owner bits OR into every ALIEN HOME star's select/lane-follow twin (obj +0x16/+0x17 analogs `starLaneVis_`/`starSelVis_`) at scenario init — campaign.cpp `seedVisibility()`, pinned `campaign_visibility_law_oq026_t195` (case 5). Consumer law: ships.md S23 L9 (star-click FUN_00028e70 gates select on +0x17 & viewer, lane-follow on +0x16; stars are always DRAWN). [documented model: the vendor's internal consumer of the ability flag is unmapped — help.txt is the effect law and the mask layer is the only consumer surface proven to exist.] |
| SA_KnowRaces | L1803 "talk to all other races from the start" | **FILED NO-OP**: dialogue is never gated by contact in the sim. |
| SA_HealShips | L1824 "repair all damage to your ships" | clears own fleetDamage (the power pool). |
| SA_ForcePeace | L1870 "force all aliens to make peace" | ends ALL of the user's wars (war table symmetric bits). |
| SA_DoublePower | L1917 "double the power of all your ships" | attackScore x2 for the owner, this combat only (L1945 "for the rest of this turn"). |
| SA_RepelAlienShips | L1965 "warp alien ships out of your colonies' stars" | removes in-transit enemy ships whose TARGET is a user-owned star. |
| SA_SapAlienPower | L2012 "wipe out the power of all alien ships in systems you occupy" | +15 fleetDamage to each at-war owner of a star adjacent to a user star (8 vs DoubleHull). fleetDamage subtracts from attackScore and regens 5/turn (documented defaults). |
| SA_Cornucopia | L2059 "turn your least populated colony into a rich world" | least-pop user colony gains richPros 2 (= Agriplot PROS, planitem.txt); "rich world" ~ static.txt #56 "Cornucopia" planet-type name. |
| SA_BumpShipsInLanes | L2106 "bump all ships in star lanes backward to their stars of origin" | clears ALL in-transit fleets (model has no idle in-lane ships, so return-to-origin == removal; L2134 vendor result text says the same). |
| SA_StealResearch | L2154 "steal any technology known by at least two other races" | acquires every tech held by >=2 other owners (exact holder-count rule from the text); if the stolen row was the race's own research target, the target is cleared to re-pick (cited body law 0x43eec target-reset leg, added t256). |
| SA_ShieldPlanets | L2201 "all your colonies invincible for one day" | own stars skip capture this combat (one-shot). |
| SA_MoreMaxPop | L2248 "increase the maximum population of all your colonies" | +25 capBonus on every owned star (documented default step; pop growth uses cap). |
| SA_KnowStarLanes | L2295 "see all star lanes" | **WIRED t195 (OQ-026 CLOSED)**: owner bit ORs into EVERY lane mask (`laneVis_`, rec+0x20 analog) at scenario init — campaign.cpp `seedVisibility()`, pinned `campaign_visibility_law_oq026_t195` (case 4, both the player-species route and the race-token route). Consumer law: cosmos list builder FUN_00028fc0 withholds any lane with `rec+0x20 & viewer_mask == 0` (never drawn, never clickable; ships.md S23 L9). Passive (cadence word 0, L6 zero-set {0..4,15,18,21}) — effect applies once at init and is sticky (OR-only law, S23 L5). NOT a sim-side expansion cheat: the AI colonisation-target gate stays as measured (campaign.cpp expansionPhase comment). |
| SA_BlockStarLanes | L2314 "block all star lanes entering your colonized systems" | launches and invasions into blocked stars forbidden this turn (one-shot). |
| SA_CauseWar | L2361 "alien species to strongly dislike any species at war with you" | UPGRADED t256 to the cited body law SA_Hatred 0x440b5 (aicode.md §6.3): for every race r at war with the user, every THIRD-PARTY attitude cell above r's own DECLARE_WAR word is CEILINGED to exactly that word (x != r exclusion; ceiling not delta — the old flat -250 was uncited). Player-projection [documented]: the sim carries one attitude vector (AI->player), so the law runs when the USER owns it; an AI-owned CauseWar announces only (AI-vs-AI cells R1-blocked, gap row 12). Pinned species_cause_war_hatred_ceiling_t256 (exact + integration). |
| SA_FastLaneTravel | L2409 "move quickly through star lanes" | +1 launch hop in driveHopsFor before the [1..3] clamp (hop scale itself OQ-019). |
| SA_FreeResearch | L2429 "immediately achieve any discovery you are pursuing" | the QUEUED tech completes instantly (L2457 "complete in one day"); NOTHING happens with an empty queue — the cited body law 0x4414e gates on target != 0xffff (t256 removed the uncited "cheapest available" fallback leg). Pinned species_free_research_completes_only_the_queued_row_t256. |
| SA_IndustryBoost | L2476 "boost the progress on all your colonies' projects" | every owned planet WITH a pending project gains +100 on its build accumulator (cited body law 0x4418e `WORD [p+0x50] += 100` behind the [p+0x54]!=0xff pending gate, income-law.md S8; t256 replaced the wrong-operand ind_+=20 default — ind_ is the ship-launch budget). Pinned species_industry_boost_is_per_planet_accumulator_t256 (control differential). |

## §3 Numeric defaults and RNG discipline

- **Charge period: MEASURED per-ability cadence table** (t100, OQ-020
  CLOSED; docs/re/aicode.md §6.4). WORD[0x6780+2*ability] embedded in
  ascend.exe (live playcap/save/60.sav == restored FILE 0x89330, zero
  writers image-wide): cad = {5:60, 6:100, 7:62, 8:77, 9:90, 10:150, 11:70,
  12:63, 13:66, 14:72, 16:92, 17:100, 19:89, 20:68}, zero exactly at
  {0..4,15,18,21} == the passives. Semantics (campaign.cpp abilityPhase):
  counter counts UP from 0 (original row+0x19e), fires iff counter == cad
  EXACTLY, resets to 0 on fire (exit T1 0x4400a). The earlier 30-turn
  "a month" default is FALSIFIED per-ability. Verify tool:
  scripts/r1_t100_cad_verify.py (C++ table == FILE leg == LIVE save leg).
- **Turn order**: abilityPhase runs FIRST in advance() so ForcePeace shields
  the user from that turn's combat and BlockStarLanes gates that turn's
  launches. One-shot flags cleared here.
- **RNG DISCIPLINE (hard rule)**: campaign dynamics draw exactly two
  mt19937 values per evaluated border pair (atk noise, then def noise).
  Ability branches must not add or skip draws. An earlier cut drew def noise
  only on the non-SuperMarines branch; seed 2024 matched HEAD through t40 yet
  diverged by t195 purely from stream drift (self-caught via head-vs-work
  diff bisection). The def draw is now unconditional.
- fleetDamage is a per-owner abstraction of "ship power" (no per-ship hull
  bookkeeping exists — OQ-019); regen 5/turn, SapAlienPower +15, floor 0.
  A generic per-capture damage channel was tried and REJECTED: it starved
  non-healing empires into death spirals and turned 8/8 PLAYTHROUGH seeds
  Extinct (self-caught by the victory-distribution sweep).

## §4 Player species selection

`--species N` (0..20) grants owner 0 the specnum-N ability; the AI slot that
species would occupy is skipped (six AI = first six specnums excluding the
player's). Default -1 = human (player.dip carries no SA_ token [verified]).
traceLine() carries `SA_<Token>` when set. Slot-assignment policy of the
original is runtime-blocked (documented default).

## §5 Verification

- gate 3m: ability_probe.py (21 blocks/14+7 split/race02 title match/kNotes
  21 cited/4 filed no-ops) + a 65-turn smoke asserting SA_HealShips fired
  (cad 60, t100).
- unit tests rewrite/tests/test_species.cpp: roster three-source,
  bad-dir rejection, charge split + MEASURED cadence table pin (t100),
  every-token-noted, firing schedule (t60 count-up law), ForcePeace ends
  war, ShieldPlanets one-shot,
  BlockStarLanes flag, MoreMaxPop/Cornucopia, StealResearch bounds,
  player-species selection + no self-duplicate, silence without abilities,
  victory reachable with abilities, determinism with abilities.
- 70/70 total tests green; seeds {1,42,2024} Control, {3,7,13,99,555}
  Extinct — both victory files still exercised (PLAYTHROUGH regenerated).
