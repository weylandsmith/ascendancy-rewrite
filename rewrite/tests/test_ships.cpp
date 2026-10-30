// Ship-system data invariants: docs/re/ships.md (rows verified against
// extracted/ascend00/{planitem,gizmos}.txt).
#include "game/campaign.h"
#include "harness.h"

#include <cstdio>
#include <filesystem>

namespace {
namespace ag = ascend::game;

std::string repo() {
#ifdef ASCENDANCY_SOURCE_DIR
    return ASCENDANCY_SOURCE_DIR;
#else
    return ".";
#endif
}

// Shared table load (same pattern as test_campaign.cpp; abort on missing
// data so a broken checkout fails loudly rather than silently skipping).
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
        auto st = ag::StarStats::load(repo() + "/extracted/ascend00/starstat.txt", &err);
        if (!st) std::abort();
        x.stats = *st;
        x.names = ag::loadStarNames(repo() + "/extracted/ascend00/names.txt", &err);
        if (x.names.empty()) std::abort();
        x.tree = ag::ResearchTree::loadFromFile(repo() + "/extracted/ascend00/restree.txt", err);
        x.items = ag::loadPlanItems(repo() + "/extracted/ascend00/planitem.txt", err);
        if (x.items.size() != 39) std::abort();
        x.gizmos = ag::loadGizmos(repo() + "/extracted/ascend00/gizmos.txt", err);
        if (x.gizmos.size() != 76) std::abort();
        for (int i = 0; i < 6; ++i) {
            ag::DipFile df;
            char path[256];
            std::snprintf(path, sizeof(path), "%s/extracted/ascend00/race%02d.dip",
                          repo().c_str(), i);
            if (!df.loadFromFile(path, &err)) std::abort();
            x.ai.push_back(std::move(df));
        }
        return x;
    }();
    return t;
}

ag::Campaign makeShipCampaign(unsigned seed, int aiCount = 6) {
    ag::CampaignConfig cfg;
    cfg.seed = seed;
    cfg.aiCount = aiCount;
    ag::MapConfig mc;
    mc.seed = seed;
    ag::Galaxy g = ag::MapGenerator(mc, tables().stats, tables().names).generate();
    std::string err;
    return ag::Campaign(cfg, g, &tables().tree, tables().items, tables().gizmos,
                        tables().ai, &err);
}
}  // namespace

TEST(ship_hull_rows_verified) {
    std::string err;
    auto items = tables().items;
    int ship = -1, yard = -1;
    for (size_t i = 0; i < items.size(); i++) {
        if (items[i].name == "Ship") ship = int(i);
        if (items[i].name == "Shipyard") yard = int(i);
    }
    CHECK(ship >= 0 && yard >= 0);
    CHECK(items[ship].cost == 20 && items[ship].requires == 1);
    CHECK(items[yard].cost == 240 && items[yard].requires == 0);
}

TEST(ship_drive_levels_verified) {
    int drives = 0;
    for (const auto& g : tables().gizmos) {
        if (g.cat != ag::GizmoCat::Drive) continue;
        ++drives;
        // (level, resReq) pairs verified in ships.md §3
        if (g.name == "Tonklin Motor")         CHECK(g.level == 2 && g.resReq == 2);
        if (g.name == "Ion Banger")            CHECK(g.level == 4 && g.resReq == 10);
        if (g.name == "Graviton Projector")    CHECK(g.level == 6 && g.resReq == 23);
        if (g.name == "Inertia Negator")       CHECK(g.level == 6 && g.resReq == 46);
        if (g.name == "Nanowave Space Bender") CHECK(g.level == 10 && g.resReq == 54);
    }
    CHECK(drives == 5);
    // "Hypersphere Driver" is a WEAPON despite the name (ships.md §3).
    bool found = false;
    for (const auto& g : tables().gizmos)
        if (g.name == "Hypersphere Driver") {
            found = true;
            CHECK(g.cat == ag::GizmoCat::Weapon);
        }
    CHECK(found);
}

TEST(ship_drive_hops_gate_launches) {
    // Early turns: drives gated (resReq row 7) -> grounded owners must have
    // driveHopsFor 0 or a researched ladder value; after enough turns owner
    // 0 must clear the gate and reach hops>=1.
    auto c = makeShipCampaign(7);
    for (int t = 0; t < 40 && c.driveHopsFor(0) == 0; t++) c.advance();
    CHECK(c.driveHopsFor(0) >= 1);
    CHECK(c.driveHopsFor(0) <= 3);  // clamp in ships.md §3
}

TEST(ship_expansion_survives_gates) {
    // The gate-critical invariant: Shipyard launch precondition + drive-range
    // BFS must not stall expansion to the point of no-victory (mirrors the
    // frozen-front bug the fortify fix addressed). T37: the class-cell
    // channel law shifted this seed past 600 (finite resolve — CLI proxy
    // wins on seed 2024); guard is against infinite stall, bar now 1200.
    // T202B 1200 -> 1600: measured usedPopFor (item-UPOP sum) activates the
    // 0x3f220 no-free-pop law — AI builds serialize behind pop growth and
    // this seed resolves at ~t1420 (CLI --campaign 1600 --seed 2024), still
    // FINITE, which is what this guard actually tests. Window widens; law
    // stands.
    auto c = makeShipCampaign(2024);
    ag::Victory v = ag::Victory::None;
    int t = 0;
    for (; t < 1600 && v == ag::Victory::None; ++t) v = c.advance();
    CHECK(v != ag::Victory::None);
    CHECK(c.turn() >= 2);
}
