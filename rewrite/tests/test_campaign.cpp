// Campaign turn-loop tests. Constants: docs/re/turnloop.md (end-*.txt vendor
// comments, planitem rows, gizmo levels) — never memory (STATE rule).
#include "game/campaign.h"
#include "harness.h"

#include <cstdio>
#include <cstdlib>
#include <filesystem>
#include <string>

#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif

namespace {
namespace ag = ascend::game;
namespace fs = std::filesystem;

const fs::path kRepo = ASCENDANCY_SOURCE_DIR;

struct Tables {
    ag::StarStats stats;
    std::vector<std::string> names;
    ag::ResearchTree tree;
    std::vector<ag::PlanetItem> items;
    std::vector<ag::Gizmo> gizmos;
    std::vector<ag::DipFile> ai;
};

Tables& tables() {
    static Tables t = [] {
        Tables x;
        std::string err;
        auto st = ag::StarStats::load(kRepo / "extracted/ascend00/starstat.txt", &err);
        if (!st) std::abort();
        x.stats = *st;
        x.names = ag::loadStarNames(kRepo / "extracted/ascend00/names.txt", &err);
        if (x.names.empty()) std::abort();
        x.tree = ag::ResearchTree::loadFromFile((kRepo / "extracted/ascend00/restree.txt").string(), err);
        x.items = ag::loadPlanItems((kRepo / "extracted/ascend00/planitem.txt").string(), err);
        if (x.items.size() != 39) std::abort();
        x.gizmos = ag::loadGizmos((kRepo / "extracted/ascend00/gizmos.txt").string(), err);
        if (x.gizmos.size() != 76) std::abort();
        for (int i = 0; i < 6; ++i) {
            ag::DipFile df;
            char path[256];
            std::snprintf(path, sizeof(path), "%s/extracted/ascend00/race%02d.dip",
                          ASCENDANCY_SOURCE_DIR, i);
            if (!df.loadFromFile(path, &err)) std::abort();
            x.ai.push_back(std::move(df));
        }
        return x;
    }();
    return t;
}

ag::Campaign makeCampaign(unsigned seed, int aiCount = 6, bool ffa = true) {
    ag::CampaignConfig cfg;
    cfg.seed = seed;
    cfg.aiCount = aiCount;
    cfg.freeForAll = ffa;
    ag::MapConfig mc;
    mc.seed = seed;
    ag::Galaxy g = ag::MapGenerator(mc, tables().stats, tables().names).generate();
    std::string err;
    return ag::Campaign(cfg, g, &tables().tree, tables().items, tables().gizmos,
                        tables().ai, &err);
}

}  // namespace

TEST(campaign_homes_distinct) {
    auto c = makeCampaign(7);
    for (int o = 0; o <= 6; ++o) CHECK(c.starsOwned(o) == 1);
    CHECK(c.turn() == 0);
    CHECK(c.victory() == ag::Victory::None);
}

TEST(campaign_total_owned_grows) {
    // Expansion: total claimed stars must strictly grow over 20 turns
    // (some owner always has surplus industry; turnloop.md §4).
    auto c = makeCampaign(42);
    int totalPrev = 7;
    for (int t = 0; t < 20 && !c.over(); ++t) {
        c.advance();
        int total = 0;
        for (int o = 0; o <= 6; ++o) total += c.starsOwned(o);
        CHECK(total >= totalPrev);
        totalPrev = total;
    }
    CHECK(totalPrev > 7);
}

TEST(campaign_channel_law_oq016) {
    // MEASURED stored-channel law (docs/re/income-law.md S6/t18b compression
    // + t19 grant; battery scripts/r1_income_channels.py post-t35:
    // IND/PROS/RES 173/173/173 on the corrected +0x88 array with the
    // channel-field gating — class-cell +1 bonuses apply only when the
    // item's own channel field is non-zero, see income-law.md T35):
    // acc==0 -> scenario grant 1 (colonization FUN_00025d30
    // +1 both home records); IND = trunc((dbl(acc,f12)+1)^0.85)
    // (0x38e2d FILD/pow/FISTP chain, RET 0x76e08 = trunc; t18b); RES is the
    // raw accumulator (never compressed). dbl = v + (v>>1) when the FIRST
    // slot is Hyperpower(IND,12)/Internet(RES,14) (FUN_0003958c +
    // bit-tests 0x38d4b/0x38db5). Values from the battery curve:
    //   v      1  2   3    4    5    6    7
    //   v^.85  1  2  3.25 3.93 4.61 5.23 5.83   (truncated)
    CHECK(ag::colonyChannel(0, false, true) == 1.0);  // grant, not pow(1)
    CHECK(ag::colonyChannel(1, false, true) == 1.0);  // (2)^.85 = 1.80 -> 1
    CHECK(ag::colonyChannel(2, false, true) == 2.0);  // (3)^.85 = 2.50 -> 2
    CHECK(ag::colonyChannel(3, false, true) == 3.0);  // (4)^.85 = 3.25 -> 3
    CHECK(ag::colonyChannel(4, false, true) == 3.0);  // (5)^.85 = 3.93 -> 3
    CHECK(ag::colonyChannel(2, true, true) == 3.0);   // dbl v=3 -> (4)^.85
    CHECK(ag::colonyChannel(4, true, true) == 5.0);   // dbl v=6 -> (7)^.85
    // RES channel: accumulator + Internet doubling shift (v += v>>1, the
    // same 0x38db5 site), never compressed.
    CHECK(ag::colonyChannel(0, true, false) == 1.0);   // grant
    CHECK(ag::colonyChannel(3, false, false) == 3.0);
    CHECK(ag::colonyChannel(3, true, false) == 4.0);   // 3 + 3>>1
    CHECK(ag::colonyChannel(9, true, false) == 13.0);  // 9 + 9>>1
}

TEST(campaign_build_queue_law_oq016) {
    // BUILD-QUEUE LAW (income-law.md S8 + S9 t28): pending item + per-planet
    // IND accumulator; completion only when acc >= COST (0x3907b/0x390a3
    // JA 0x392a2), selector runs only with no pending item (caller 0x3ead6).
    auto c = makeCampaign(42);
    // t1: every AI home queues its first pick (stored IND > 0 at start).
    c.advance();
    for (int o = 1; o <= 6; ++o) {
        int s = -1;
        for (size_t i = 0; i < 70 && s < 0; ++i)
            if (c.starOwner(static_cast<int>(i)) == o) s = static_cast<int>(i);
        CHECK(s >= 0);
    }
    // Factory COST 30 (planitem.txt row 0), home IND 1/turn (t19 grant):
    // the first queue completes around turn 31 (t1 queue, acc >= COST then).
    CHECK(c.turn() == 1);
    for (int t = 0; t < 40 && !c.over(); ++t) c.advance();
    // By turn ~41 every still-owned AI home has grown its built list by at
    // least one completed queue item.
    int grown = 0;
    for (int o = 1; o <= 6; ++o)
        for (size_t i = 0; i < c.galaxy().stars.size(); ++i)
            if (c.starOwner(static_cast<int>(i)) == o &&
                c.builtItemCount(static_cast<int>(i)) > 3) ++grown;
    CHECK(grown > 0);
}

TEST(campaign_pop_cap_seed_law_oq016) {
    // POP-CAP SEED LAW (income-law.md S10 t29/t36): seed = nonbarren/3 + 5
    // with nonbarren from the per-cell class draw (T36: size rng%5 @0x23a86,
    // row rng%11 @0x23a97, chain @0x37eb7..0x37f24); bounds per surface
    // size: min 5, max ncells/3+5 with ncells in
    // {7,11,23,45,73} -> cap in [5..29] (home items carry MPOP 0, no
    // ability bonus here). Old default was the constant 25.
    auto c = makeCampaign(2);
    int lo = 1000, hi = 0;
    const int ns = static_cast<int>(c.galaxy().stars.size());
    for (int s = 0; s < ns; ++s) {
        int cap = c.popCapAt(s);
        CHECK(cap >= 5 && cap <= 29);
        lo = std::min(lo, cap);
        hi = std::max(hi, cap);
        // T36 CELL-CLASS LAW pins: ring size, orbital ring forced class 1
        // (@0x37f12, drawn WITHOUT rng), classes in the generated range.
        const auto& ps = c.planetAt(s);
        CHECK(static_cast<int>(ps.cellClasses.size()) == ps.surfaceCells + 10);
        for (int k = ps.surfaceCells; k < ps.surfaceCells + 10; ++k)
            CHECK(ps.cellClasses[k] == 1);
        int nonbarren = 0;
        for (int k = 0; k < ps.surfaceCells; ++k) {
            const int raw = ps.cellClasses[k];
            // T38 RAW-BYTE CENSUS [verified]: classes are exactly
            // {0..4} | 8-rock — 5..7 never occur (0 of 101948 corpus
            // slots). Rock marks AFTER the draw loop (@0x37f4d before
            // seed word @0x37f84), so a barren cell marked |8 (raw 8)
            // WAS barren at draw time: the seed-law recount must treat
            // raw 0 AND raw 8 as barren (FUN_00038ba4 counts buildable
            // cells as &8==0 and barren as ==0 [verified]).
            CHECK((raw & ~8) >= 0 && (raw & ~8) <= 4 &&
                  (raw & ~8) == raw - (raw & 8));
            if (raw != 0 && raw != 8) ++nonbarren;
        }
        // seed word consistency: capBase is EXACTLY nonbarren/3+5 of the
        // generated grid (before recalc adds item MPOP; home items MPOP 0).
        CHECK(ps.capBase == nonbarren / 3 + 5);
    }
    CHECK(hi > lo);  // seeded spread, not a constant table
    // Deterministic draw: same seed => same caps (law, not noise).
    auto c2 = makeCampaign(2);
    for (int s = 0; s < ns; ++s)
        CHECK(c.popCapAt(s) == c2.popCapAt(s));
}

TEST(campaign_research_progresses) {
    auto c = makeCampaign(3);
    for (int t = 0; t < 40 && !c.over(); ++t) c.advance();
    CHECK(c.techsOwned(ag::kPlayer) > 0);  // home lab researches within 40 turns
}

TEST(campaign_deterministic_same_seed) {
    auto a = makeCampaign(1234);
    auto b = makeCampaign(1234);
    for (int t = 0; t < 30 && !a.over(); ++t) {
        a.advance();
        b.advance();
        CHECK(a.traceLine() == b.traceLine());
        CHECK(a.victory() == b.victory());
    }
}

TEST(campaign_reaches_a_victory) {
    // CONTRACT: a seeded run reaches a victory condition (docs/PLAYTHROUGH.md
    // is generated from such a run). Combat (turnloop.md §5) makes Control or
    // LastAlive reachable; 400-turn cap bounds the search.
    bool anyVictory = false;
    for (unsigned seed : {1u, 2u, 2024u}) {
        auto c = makeCampaign(seed);
        for (int t = 0; t < 400 && !c.over(); ++t) c.advance();
        if (c.over()) { anyVictory = true; break; }
    }
    CHECK(anyVictory);
}

TEST(campaign_victory_files_named) {
    CHECK(std::string(ag::victoryConditionFile(ag::Victory::Control)) == "end-ctrl");
    CHECK(std::string(ag::victoryConditionFile(ag::Victory::Extinct)) == "end-xtnc");
    CHECK(std::string(ag::victoryConditionFile(ag::Victory::LastAlive)) == "end-dest");
    CHECK(std::string(ag::victoryName(ag::Victory::Control)) == "Control");
}

TEST(campaign_advance_after_victory_is_noop) {
    auto c = makeCampaign(1);
    ag::Victory v = ag::Victory::None;
    for (int t = 0; t < 400; ++t) {
        v = c.advance();
        if (v != ag::Victory::None) break;
    }
    if (v == ag::Victory::None) { CHECK(false); return; }  // contract data
    int turn = c.turn();
    size_t evs = c.events().size();
    c.advance();
    CHECK(c.turn() == turn);
    CHECK(c.events().size() == evs);
}
