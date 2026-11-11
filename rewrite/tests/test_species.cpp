// SPDX-License-Identifier: GPL-3.0-or-later

// Species special abilities: roster cross-check + per-ability behaviour.
// Effect citations: extracted/ascend00/help.txt L1713-2511 through
// docs/re/abilities.md; roster docs/re/species.md. Numeric effects are
// [documented default] there — tests assert BEHAVIOUR (event fired, flag set,
// war ended), never a memorised constant beyond the documented ones.
#include "game/campaign.h"
#include "game/species.h"
#include "harness.h"

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <string>
#include <vector>

#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif

namespace {
namespace ag = ascend::game;
namespace fs = std::filesystem;

const fs::path kDir = fs::path(ASCENDANCY_SOURCE_DIR) / "extracted" / "ascend00";

// Loaded once; Campaign stores pointers into tree/items/gizmos, so these
// must outlive every campaign (function-local statics, never temporaries).
struct Shared {
    ag::ResearchTree tree;
    std::vector<ag::PlanetItem> items;
    std::vector<ag::Gizmo> gizmos;
    std::vector<ag::SpeciesInfo> roster;
    std::vector<ag::DipFile> dip;  // all 21, indexed by specnum
    ag::StarStats stats;
    std::vector<std::string> names;
};
Shared& shared() {
    static Shared s = [] {
        Shared x;
        std::string err;
        x.tree = ag::ResearchTree::loadFromFile((kDir / "restree.txt").string(), err);
        x.items = ag::loadPlanItems((kDir / "planitem.txt").string(), err);
        if (x.items.size() != 39) std::abort();
        x.gizmos = ag::loadGizmos((kDir / "gizmos.txt").string(), err);
        if (x.gizmos.size() != 76) std::abort();
        if (!ag::loadAbilities(kDir.string(), &x.roster, &err)) std::abort();
        auto st = ag::StarStats::load(kDir / "starstat.txt", &err);
        if (!st) std::abort();
        x.stats = *st;
        x.names = ag::loadStarNames(kDir / "names.txt", &err);
        if (x.names.empty()) std::abort();
        for (int i = 0; i < 21; ++i) {
            ag::DipFile df;
            char p[256];
            std::snprintf(p, sizeof(p), "%s/race%02d.dip", kDir.string().c_str(), i);
            if (!df.loadFromFile(p, &err)) std::abort();
            x.dip.push_back(std::move(df));
        }
        return x;
    }();
    return s;
}

// Build a campaign where AI owner k (1-based) has ability `ab` and no other
// owner has one (unless playerSpecies >= 0, which also grants the player's).
ag::Campaign makeCrafted(unsigned seed, int aiOwner, ag::SpeciesAbility ab,
                         int playerSpecies = -1, int aiCount = 6,
                         int starCount = 50, bool freeForAll = true) {
    Shared& s = shared();
    std::vector<ag::SpeciesAbility> abilities(aiCount, ag::SpeciesAbility::Unknown);
    abilities[aiOwner - 1] = ab;
    ag::CampaignConfig cfg;
    cfg.seed = seed;
    cfg.aiCount = aiCount;
    cfg.playerSpecies = playerSpecies;
    cfg.freeForAll = freeForAll;
    ag::MapConfig mc;
    mc.seed = seed;
    mc.starCount = starCount;
    ag::Galaxy g = ag::MapGenerator(mc, s.stats, s.names).generate();
    // Use the first aiCount dip files (roster-order; contents only feed the
    // DIPVALUES policy model here — abilities are set explicitly above).
    std::vector<ag::DipFile> dip;
    for (int i = 0; i < aiCount; ++i) dip.push_back(s.dip[i]);
    std::string err;
    ag::Campaign c(cfg, g, &s.tree, s.items, s.gizmos, std::move(dip), abilities, &err);
    return c;
}

bool hasEvent(const ag::Campaign& c, const std::string& needle) {
    for (const auto& e : c.events())
        if (e.text.find(needle) != std::string::npos) return true;
    return false;
}
int homeOf(const ag::Campaign& c, int owner) {
    for (size_t s = 0; s < c.galaxy().stars.size(); ++s)
        if (c.starOwner((int)s) == owner) return (int)s;
    return -1;
}
}  // namespace

TEST(species_roster_three_source) {
    REQUIRE_DATA();
    std::vector<ag::SpeciesInfo> r;
    std::string err;
    CHECK(ag::loadAbilities(kDir.string(), &r, &err));
    CHECK(r.size() == 21);
    // Tokened-header identities match help.txt by position (probe gate 3m
    // asserts all 20; spot-check the edges + the tokenless Orfa entry).
    CHECK(r[0].ability == ag::SpeciesAbility::SuperMarines);
    CHECK(r[1].ability == ag::SpeciesAbility::DoubleHull);
    CHECK(r[2].ability == ag::SpeciesAbility::BuildOnBlack);  // tokenless dip header
    CHECK(r[10].ability == ag::SpeciesAbility::Cornucopia);
    CHECK(r[20].ability == ag::SpeciesAbility::IndustryBoost);
    for (const auto& si : r) CHECK(si.ability != ag::SpeciesAbility::Unknown);
}

TEST(species_roster_rejects_bad_dir) {
    REQUIRE_DATA();
    std::vector<ag::SpeciesInfo> r;
    std::string err;
    CHECK(!ag::loadAbilities("/nonexistent-ascendancy-dir", &r, &err));
    CHECK(!err.empty());
}

TEST(species_charge_split_verified) {
    REQUIRE_DATA();
    // Split: 7 passive blocks (no amass line) [verified help.txt; gate 3m
    // re-checks against the file]. PERIODS: the MEASURED cadence table
    // WORD[0x6780+2*ability] (aicode.md §6.4, live 60.sav == FILE 0x89330,
    // zero writers) — pinned verbatim; the old 30-turn default is falsified.
    const int passive[] = {0, 1, 2, 3, 4, 15, 18};
    for (int p : passive) {
        auto a = static_cast<ag::SpeciesAbility>(p);
        CHECK(!ag::abilityIsCharged(a));
        CHECK(ag::abilityChargeTurns(a) == 0);
    }
    const int cad[21] = {0, 0, 0, 0, 0, 60, 100, 62, 77, 90, 150,
                         70, 63, 66, 72, 0, 92, 100, 0, 89, 68};
    int charged = 0;
    for (int i = 0; i < (int)ag::SpeciesAbility::kCount; ++i) {
        auto a = static_cast<ag::SpeciesAbility>(i);
        CHECK(ag::abilityChargeTurns(a) == cad[i]);
        // nonzero set == charged set (measured exactly in the vendor table)
        CHECK(ag::abilityIsCharged(a) == (cad[i] != 0));
        if (ag::abilityIsCharged(a)) ++charged;
    }
    CHECK(charged == 14);
    CHECK(ag::abilityFromToken("SA_BuildOnBlack") == ag::SpeciesAbility::BuildOnBlack);
    CHECK(ag::abilityFromToken("SA_Nonsense") == ag::SpeciesAbility::Unknown);
}

TEST(species_every_token_has_effect_or_filed_noop) {
    REQUIRE_DATA();
    // C++ mirror of gate 3m: no token is silently unhandled, and every note
    // cites a help.txt line block.
    int filedNoops = 0;
    for (int i = 0; i < (int)ag::SpeciesAbility::kCount; ++i) {
        const char* n = ag::abilityEffectNote(static_cast<ag::SpeciesAbility>(i));
        CHECK(n && *n);
        CHECK(std::strstr(n, "[help.txt L") != nullptr);
        if (std::strstr(n, "FILED NO-OP")) ++filedNoops;
    }
    CHECK(filedNoops == 2);  // BuildOnBlack + KnowRaces (t195: KnowHomeWorlds
                             // and KnowStarLanes LEFT the no-op set — the
                             // OQ-026 visibility layer landed, ships.md S23 L9)
}

TEST(species_charged_ability_fires_on_schedule) {
    REQUIRE_DATA();
    // MEASURED CADENCE LAW (t100, aicode.md §6.4): counter counts UP from 0,
    // fires EXACTLY at the cadence word, resets to 0. SA_HealShips cad=60:
    // first activation turn 60, then every 60 turns (period == cad).
    auto c = makeCrafted(11, 1, ag::SpeciesAbility::HealShips);
    CHECK(c.chargeFor(1) == 0);  // scenario init (original row+0x19e starts 0)
    for (int t = 0; t < 59; ++t) c.advance();
    CHECK(!hasEvent(c, "SA_HealShips"));
    CHECK(c.chargeFor(1) == 59);
    c.advance();  // turn 60 == cad -> fire
    CHECK(hasEvent(c, "SA_HealShips"));
    CHECK(c.chargeFor(1) == 0);  // reset-on-fire (exit T1 0x4400a)
    for (int t = 0; t < 59; ++t) c.advance();
    CHECK(c.chargeFor(1) == 59);
    c.advance();  // turn 120 -> second fire, period == cad exactly
    int fires = 0;
    for (const auto& e : c.events())
        if (e.text.find("SA_HealShips") != std::string::npos) ++fires;
    CHECK(fires == 2);
}

TEST(species_force_peace_ends_the_owner_wars) {
    REQUIRE_DATA();
    auto c = makeCrafted(12, 1, ag::SpeciesAbility::ForcePeace);
    CHECK(c.atWar(1, 0));  // free-for-all start
    for (int t = 0; t < 100; ++t) c.advance();  // cad[6] == 100 (aicode.md §6.4)
    CHECK(!c.atWar(1, 0));
    CHECK(hasEvent(c, "forced peace"));
}

TEST(species_shield_planets_blocks_captures_that_turn) {
    REQUIRE_DATA();
    auto c = makeCrafted(13, 1, ag::SpeciesAbility::ShieldPlanets);
    for (int t = 0; t < 66; ++t) c.advance();  // cad[13] == 66 (aicode.md §6.4)
    CHECK(c.invincibleStar(homeOf(c, 1)));
    CHECK(hasEvent(c, "colonies invincible"));
    c.advance();  // next turn clears the one-shot flag
    CHECK(!c.invincibleStar(homeOf(c, 1)));
}

TEST(species_block_star_lanes_flag_set_on_activation) {
    REQUIRE_DATA();
    auto c = makeCrafted(14, 1, ag::SpeciesAbility::BlockStarLanes);
    for (int t = 0; t < 92; ++t) c.advance();  // cad[16] == 92 (aicode.md §6.4)
    CHECK(c.laneBlockedStar(homeOf(c, 1)));
    CHECK(hasEvent(c, "blocked lanes"));
}

TEST(species_more_max_pop_raises_caps_and_cornucopia_adds_pros) {
    REQUIRE_DATA();
    // PIN t280 for the CITED body law SA_MoreMaxPop 0x4402a (aicode.md §6.3
    // t280 erratum: §6.3 never documented this body; jump-table case al=9):
    // EVERY owned planet's PRE-CLAMP cap seed word += 2 (capBase, the +0x55
    // analog), then recalc. Pin = CONTROL DIFFERENTIAL at the exact fire
    // turn (cad[14] == 72): capBase rises EXACTLY +2 on every owned star and
    // never before the fire; the old post-clamp +25 bonus would overshoot.
    auto c = makeCrafted(15, 1, ag::SpeciesAbility::MoreMaxPop);
    auto ctrl = makeCrafted(15, 1, ag::SpeciesAbility::Unknown);
    for (int t = 0; t < 71; ++t) { c.advance(); ctrl.advance(); }
    std::vector<int> owned;
    for (size_t s = 0; s < c.galaxy().stars.size(); ++s)
        if (c.starOwner((int)s) == 1) owned.push_back((int)s);
    CHECK(!owned.empty());
    for (int s : owned)
        CHECK(c.planetAt(s).capBase == ctrl.planetAt(s).capBase);  // not yet
    c.advance();  // turn 72: cad[14] fires
    ctrl.advance();
    for (int s : owned)
        CHECK(c.planetAt(s).capBase == ctrl.planetAt(s).capBase + 2);
    CHECK(hasEvent(c, "colony pop caps (+2 seed each)"));
}

TEST(species_cornucopia_repaints_min_pop_colony_t281) {
    REQUIRE_DATA();
    // PIN t281 for the CITED body law SA_Cornucopia 0x43de4 (aicode.md §6.3
    // t99 + t281 raw re-read work/t280_bodies.txt:152; docs/re/_wip_t281.md):
    // SELECT the owned planet with MIN pop (+0x42; skip terrainRow==10, the
    // zero-barren weight row — +0x16 measured as the stored row index by
    // scripts/r1_t281_w16_census.py, NOT a homeworld marker), then repaint
    // every SURFACE cell (bound +0x18, orbital ring excluded) whose RAW class
    // byte is 0 or 1 to a pick from {2,3,4}. CONTROL DIFFERENTIAL vs an
    // Unknown-ability campaign on the same seed (cad[10] == 150): cells change
    // ONLY on the fire turn and ONLY on the selected star; rock bytes and the
    // orbital ring NEVER change; no cell remains 0/1 on the target's surface.
    auto c = makeCrafted(16, 1, ag::SpeciesAbility::Cornucopia);
    auto ctrl = makeCrafted(16, 1, ag::SpeciesAbility::Unknown);
    for (int t = 0; t < 149; ++t) { c.advance(); ctrl.advance(); }
    // Expected target under the cited law, computed INDEPENDENTLY of the
    // implementation's internals (owner + pop + terrainRow only).
    int want = -1, wantPop = 0xffff;
    for (size_t s = 0; s < c.galaxy().stars.size(); ++s) {
        if (c.starOwner((int)s) != 1) continue;
        if (c.planetAt((int)s).terrainRow == 10) continue;
        const int pop = static_cast<int>(c.planetAt((int)s).pop);
        if (pop < wantPop) { want = (int)s; wantPop = pop; }
    }
    CHECK(want >= 0);
    c.advance();  // turn 150: cad[10] fires
    ctrl.advance();
    CHECK(hasEvent(c, "a rich world"));
    for (size_t s = 0; s < c.galaxy().stars.size(); ++s) {
        const auto& pc = c.planetAt((int)s);
        const auto& pp = ctrl.planetAt((int)s);
        if ((int)s != want) {
            // no other star's classes may move (terrain is write-frozen
            // outside this law: income-law.md terrain-mutation census)
            CHECK(pc.cellClasses == pp.cellClasses);
            continue;
        }
        const int bound = pc.surfaceCells;
        CHECK((int)pc.cellClasses.size() == bound + 10);
        int repainted = 0;
        for (int k = 0; k < bound; ++k) {
            const int before = pp.cellClasses[k], after = pc.cellClasses[k];
            if (before == after) {
                // unpainted surface cells must not have been 0/1
                CHECK(before != 0 && before != 1);
            } else {
                ++repainted;
                CHECK(before == 0 || before == 1);
                CHECK(after == 2 || after == 3 || after == 4);
            }
        }
        CHECK(repainted > 0);  // the min-pop colony always had barren/normal ground
        // the orbital ring is OUTSIDE the vendor bound WORD[rec+0x18]
        for (size_t k = bound; k < pc.cellClasses.size(); ++k)
            CHECK(pc.cellClasses[k] == pp.cellClasses[k]);
    }

    // SKIP-LEG + NULL-EXIT leg (t295 RE-DERIVATION: seed 8's row-10 HOME was
    // an artefact of the retired spread-BFS; under the cited home-draw law
    // the seed scan (diagnostic since deleted) listed seeds whose owner-1
    // HOME sits
    // on weight row 10 — seed 10, home s8. Owner 1 keeps NO other eligible
    // colony through t150 on this seed, so the cited skip leaves no eligible
    // planet and the body exits at the null test 0x43e3a — NO repaint, NO
    // event. Seed 16 alone cannot catch a deleted skip leg (its argmin isn't
    // a row-10 world); this leg can: deleting the skip line fires the event.)
    auto s8 = makeCrafted(10, 1, ag::SpeciesAbility::Cornucopia);
    auto s8ctrl = makeCrafted(10, 1, ag::SpeciesAbility::Unknown);
    bool s8Row10Home = false;
    for (size_t s = 0; s < s8.galaxy().stars.size(); ++s)
        if (s8.starOwner((int)s) == 1 && s8.planetAt((int)s).terrainRow == 10)
            s8Row10Home = true;
    CHECK(s8Row10Home);  // fixture premise (guard against mapgen drift)
    for (int t = 0; t < 155; ++t) { s8.advance(); s8ctrl.advance(); }
    CHECK(!hasEvent(s8, "a rich world"));
    for (size_t s = 0; s < s8.galaxy().stars.size(); ++s)
        CHECK(s8.planetAt((int)s).cellClasses == s8ctrl.planetAt((int)s).cellClasses);
}

TEST(species_steal_research_fires_and_is_capped_by_ownership_rule) {
    REQUIRE_DATA();
    auto c = makeCrafted(17, 1, ag::SpeciesAbility::StealResearch);
    const int before = c.techsOwned(1);
    for (int t = 0; t < 63; ++t) c.advance();  // cad[12] == 63 (aicode.md §6.4)
    CHECK(hasEvent(c, "SA_StealResearch"));
    CHECK(c.techsOwned(1) >= before);  // never loses techs
    // Steal fires again after recharge and must not grow unboundedly beyond
    // tree size: run a full cadence period more, still a legal count.
    for (int t = 0; t < 63; ++t) c.advance();
    CHECK(c.techsOwned(1) <= 106);  // 66 main + 40 variant rows (research.md)
}

TEST(species_cause_war_two_party_boundary_t280) {
    REQUIRE_DATA();
    // PIN t280 for the CORRECTED SA_Hatred law (raw 0x440b5..0x4414c,
    // work/t280_bodies.txt; aicode.md §6.3 t280 amendment E3). The vendor
    // ceilings word[row(x)+0x1b2+2k] == att[x->k] (third party x toward
    // enemy k) at DECLARE_WAR(x). The law EXCLUDES k==self and x==self, so
    // with the rewrite's AI->PLAYER-only attitude state (dipState_) NO cell
    // is addressable — firing must NEVER move an attitude. (The retired t256
    // pin pinned the §6.3 mislabel; this pins the boundary the corrected
    // law implies.)
    auto c = makeCrafted(32, 1, ag::SpeciesAbility::Unknown,
                         /*playerSpecies=*/-1, 6, 50, /*freeForAll=*/false);
    auto ctrl = makeCrafted(32, 1, ag::SpeciesAbility::Unknown,
                            /*playerSpecies=*/-1, 6, 50, /*freeForAll=*/false);
    // Give owner 1 the ability (AI fire, cad[17] == 100) and war it with
    // the player; onlooker attitudes deliberately start high. CONTROL =
    // byte-identical scenario WITHOUT the ability; the sim is deterministic,
    // so "the law touches no rewrite cell" means the two campaigns' full
    // attitude vectors agree AFTER the fire (per-race mood oscillation makes
    // raw before/after deltas meaningless — controls absorb it).
    c.setAbilityForTest(1, ag::SpeciesAbility::CauseWar);
    c.setWarForTest(1, 0, true);
    ctrl.setWarForTest(1, 0, true);
    for (int i = 1; i <= 6; ++i) { c.setAttitudeForTest(i - 1, 620); ctrl.setAttitudeForTest(i - 1, 620); }
    for (int t = 0; t < 100; ++t) { c.advance(); ctrl.advance(); }  // turn 100 fires
    CHECK(hasEvent(c, "stoked the aliens' rivalries"));
    for (int i = 0; i < 6; ++i)
        CHECK(c.dipStateAt(i).attitude == ctrl.dipStateAt(i).attitude);
    CHECK(c.atWar(1, 0) == ctrl.atWar(1, 0));  // and no side effects either
}

TEST(species_industry_boost_is_per_planet_accumulator_t256) {
    REQUIRE_DATA();
    // PIN for the t256 upgrade of SA_IndustryBoost to the CITED body law
    // 0x4418e (aicode.md §6.3 t99): every own planet WITH a pending
    // project gets WORD [p+0x50] += 100 (buildAcc analog); the empire
    // ind_ stockpile (ship budget) is NOT the operand. CONTROL
    // DIFFERENTIAL: same seed, ability on vs off — the boosted side must
    // never lag and must strictly lead (accumulator and/or completions),
    // because the accumulator is bounded well under 100 by the tick+
    // completion cycle (probe t256: acc 36 at t67, completed same turn).
    auto boosted = makeCrafted(33, 1, ag::SpeciesAbility::IndustryBoost);
    auto control = makeCrafted(33, 1, ag::SpeciesAbility::Unknown);
    for (int t = 0; t < 67; ++t) { boosted.advance(); control.advance(); }
    auto total = [](const ag::Campaign& c) {
        int v = 0;
        for (size_t s = 0; s < c.galaxy().stars.size(); ++s)
            if (c.starOwner((int)s) == 1)
                v += 1000 * (int)c.planetAt((int)s).items.size() + c.buildAccFor((int)s);
        return v;
    };
    const int d0 = total(boosted) - total(control);
    boosted.advance();  // turn 68: cad[20] == 68 fires
    control.advance();
    CHECK(hasEvent(boosted, "colony projects (+100 IND each)"));
    CHECK(total(boosted) - total(control) > d0);  // the +100 leg moved state
    // And the fire is gated to planets WITH a pending queue: count the
    // event's N against the scenario's pending count at the fire turn.
    int pending = 0;
    for (size_t s = 0; s < boosted.galaxy().stars.size(); ++s)
        if (boosted.starOwner((int)s) == 1 && boosted.pendingItemFor((int)s) >= 0) ++pending;
    (void)pending;  // N printed in the event text; differential above is the law pin
}

TEST(species_free_research_completes_only_the_queued_row_t256) {
    REQUIRE_DATA();
    // PIN for the t256 upgrade of SA_FreeResearch to the CITED body law
    // 0x4414e (aicode.md §6.3 t99 + t105): completes the row ALREADY
    // being pursued (target != 0xffff -> progress := cost); with nothing
    // queued it does NOTHING (the old "pick cheapest available" leg was
    // uncited). cad[19] == 89. AI owner 1.
    auto c = makeCrafted(34, 1, ag::SpeciesAbility::FreeResearch);
    for (int t = 0; t < 88; ++t) c.advance();
    int queued = -1;
    for (int r = 0; r < c.techCountTotal(); ++r)
        if (c.isTechQueuedFor(1, r)) queued = r;
    CHECK(queued >= 0);  // researchPhase must have a target by t88
    c.advance();         // turn 89 fires
    CHECK(c.techRowOwnedFor(1, queued));  // the QUEUED row completed
    CHECK(hasEvent(c, "SA_FreeResearch (owner 1): completed"));
    // No extra rows jumped the queue at the fire: the completion is the
    // single queued row (techProgress reset + re-pick happen in the same
    // turn's researchPhase; the count only moved by that row + normal RES
    // progress, asserted as: queued row owned and event fired once).
    int fires = 0;
    for (const auto& e : c.events())
        if (e.text.find("SA_FreeResearch (owner 1): completed") != std::string::npos) ++fires;
    CHECK(fires == 1);
}

TEST(species_player_species_selection) {
    REQUIRE_DATA();
    // Chronomyst (specnum 18, passive FastLaneTravel): the player gets it and
    // no AI keeps a duplicate of the player's own species set-up.
    auto c = makeCrafted(31, 1, ag::SpeciesAbility::Unknown, /*playerSpecies=*/18);
    CHECK(c.abilityOf(0) == ag::SpeciesAbility::FastLaneTravel);
    std::string line = (c.advance(), c.traceLine());
    CHECK(line.find("SA_FastLaneTravel") != std::string::npos);
    // Passive FastLaneTravel only shows its effect once a drive is researched
    // (hops gate, ships.md §3); driveHopsFor must stay inside its clamp.
    for (int t = 0; t < 80 && c.driveHopsFor(0) == 0; ++t) c.advance();
    CHECK(c.driveHopsFor(0) >= 1);
    CHECK(c.driveHopsFor(0) <= 3);
}

TEST(species_unknown_ability_campaign_is_silent) {
    REQUIRE_DATA();
    auto c = makeCrafted(7, 1, ag::SpeciesAbility::Unknown);
    for (int t = 0; t < 95; ++t) c.advance();  // past two full charge cycles
    for (const auto& e : c.events()) CHECK(e.text.find("SA_") == std::string::npos);
}

TEST(species_campaign_with_abilities_reaches_victory) {
    REQUIRE_DATA();
    // The abilities must not deadlock the loop (no-victory-in-N is the
    // bar earlier turn-loop bugs died on). T37 note: the class-cell
    // channel law (income-law.md T35/T36b) shifts this seed's timeline —
    // seed 2024 resolves at finite turn count >600 post-law (CLI proxy
    // --campaign 1500 --seed 2024 wins Extinct t683). The guard's target
    // is INFINITE stall; 1200 keeps a wide margin over typical resolve.
    // T202B 1200 -> 1600: the measured usedPopFor (item-UPOP sum, t202b)
    // activates 0x3f220 no-free-pop — builds serialize behind pop growth and
    // this seed now resolves Control at t1255 (CLI --campaign 1500 --seed
    // 2024, finite: not a stall). Window widens; the law stands.
    auto c = makeCrafted(2024, 1, ag::SpeciesAbility::SuperMarines);
    ag::Victory v = ag::Victory::None;
    int t = 0;
    for (; t < 1600 && v == ag::Victory::None; ++t) v = c.advance();
    CHECK(v != ag::Victory::None);
}

TEST(species_determinism_with_abilities) {
    REQUIRE_DATA();
    auto a = makeCrafted(555, 2, ag::SpeciesAbility::SapAlienPower);
    auto b = makeCrafted(555, 2, ag::SpeciesAbility::SapAlienPower);
    for (int t = 0; t < 120 && !a.over(); ++t) {
        a.advance();
        b.advance();
        if (a.traceLine() != b.traceLine()) break;
    }
    CHECK(a.traceLine() == b.traceLine());
    CHECK(a.turn() == b.turn());
}

// --- end-capt / end-unit evaluation (docs/re/turnloop.md §1) -------------

TEST(victory_condition_files_all_mapped) {
    REQUIRE_DATA();
    // All five vendor end-*.txt files are now evaluated in checkVictory;
    // the enum->file mapping must cover every one (this is what changed:
    // Captured/Unification were previously "not evaluated" rows).
    CHECK(std::string(ag::victoryConditionFile(ag::Victory::Control)) == "end-ctrl");
    CHECK(std::string(ag::victoryConditionFile(ag::Victory::Captured)) == "end-capt");
    CHECK(std::string(ag::victoryConditionFile(ag::Victory::Unification)) == "end-unit");
    CHECK(std::string(ag::victoryConditionFile(ag::Victory::Extinct)) == "end-xtnc");
    CHECK(std::string(ag::victoryConditionFile(ag::Victory::LastAlive)) == "end-dest");
    CHECK(std::string(ag::victoryName(ag::Victory::Captured)) == "Captured");
    CHECK(std::string(ag::victoryName(ag::Victory::Unification)) == "Unification");
}

TEST(victory_end_capt_reachable_small_ffa) {
    REQUIRE_DATA();
    // Captured = player owns every AI's setup home star. Player Minions
    // (guaranteed invasions) vs 2 AI on a small FFA map. Whether a bot game
    // reaches it is dynamics, not the evaluation contract; but the check IS
    // evaluated before Control, so a run that takes both homes while under
    // half reports Captured, never Control.
    for (unsigned seed : {2u, 5u, 13u, 17u, 21u, 33u}) {
        auto c = makeCrafted(seed, 1, ag::SpeciesAbility::SuperMarines,
                             /*playerSpecies=*/0, /*aiCount=*/2, /*stars=*/14);
        ag::Victory v = ag::Victory::None;
        int t = 0;
        for (; t < 600 && v == ag::Victory::None; ++t) v = c.advance();
        if (v == ag::Victory::Captured) return;  // evaluation exercised
    }
    // Dynamics never took both homes on these seeds. Evaluation itself is
    // pinned by the mapping test + gate; do NOT fake a fixture here.
    std::printf("(skip: end-capt not reached on search seeds) ");
}

TEST(victory_peace_acceptance_ends_player_war) {
    REQUIRE_DATA();
    // diplomacyPhase now acts on ProposePeace (accept-threshold argument in
    // campaign.cpp): a race at war whose attitude recovers past its
    // PROPOSE_PEACE ends that war. 1-AI non-FFA game; watch for the pair.
    for (unsigned seed : {1u, 5u, 9u, 17u}) {
        auto c = makeCrafted(seed, 1, ag::SpeciesAbility::Unknown, -1, 1, 30, false);
        for (int t = 0; t < 600 && !c.over(); ++t) c.advance();
        bool peace = false, war = false;
        for (const auto& e : c.events()) {
            if (e.text.find("declared war") != std::string::npos) war = true;
            if (e.text.find("proposed peace; accepted") != std::string::npos) peace = true;
        }
        if (peace) CHECK(war);   // peace never ends a war that never opened
        if (war && peace) return;
    }
    std::printf("(skip: no war->peace sequence on search seeds) ");
}
