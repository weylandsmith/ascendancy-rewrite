// SPDX-License-Identifier: GPL-3.0-or-later

// tPL-D1 HOME-PLANET-BY-RACE pins (law docs/re/income-law.md S10 tPL-D1
// block; working log docs/re/_wip_tPLD1.md P1-P5):
//   1. Per-spec home SIZE + TERRAIN TABLE: payload 0x88f90 (size-class idx)
//      and 0x88fe4 (weight row) keyed by specnum. MEASURED 85/85 homes over
//      26 independent fresh lineages (scripts/tpld1_spec_home.py). Pinned
//      here for the species the corpus covers directly plus the full table
//      verbatim: Chamachies(19) -> size idx 3 (45 cells) row 7; Minions(0)
//      -> idx 4 (73) row 5; Chronomyst(18) -> idx 2 (23) row 3.
//   2. The port obeys the table: with playerSpecies set, the player's home
//      has EXACTLY the table cells + terrainRow, across several seeds (the
//      rng path this replaces produced size 7/11/73 homes for Chamachies —
//      the D26 "wrong art, wrong max population" complaint).
//   3. capBase seed law unchanged on homes: nb/3+5 (144/144 corpus, P1) —
//      the max-pop half of D26 is a CONSEQUENCE of the size table, no seed.
//   4. Human player (-1) keeps the rng path (documented default; no vendor
//      capture of a species-less game exists — honest default, not a claim).
#include <cstdio>
#include <optional>
#include <string>
#include <vector>

#include "game/campaign.h"
#include "harness.h"

#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif

namespace {
namespace ag = ascend::game;
const std::string kRepo = ASCENDANCY_SOURCE_DIR;
// harness has CHECK/REQUIRE_DATA only (tPL-B2 idiom): REQUIRE = CHECK + return.
#define REQUIRE(cond)         \
    do {                      \
        CHECK((cond));        \
        if (!(cond)) return;  \
    } while (0)

std::optional<ag::Campaign> mk(int playerSpecies, unsigned seed) {
    static ag::StarStats stats;
    static std::vector<std::string> names;
    static ag::ResearchTree tree;
    static std::vector<ag::PlanetItem> items;
    static std::vector<ag::Gizmo> gizmos;
    static std::vector<ag::DipFile> ai;
    static bool loaded = false;
    if (!loaded) {
        std::string err;
        auto st = ag::StarStats::load(kRepo + "/extracted/ascend00/starstat.txt", &err);
        if (!st) return std::nullopt;
        stats = *st;
        names = ag::loadStarNames(kRepo + "/extracted/ascend00/names.txt", &err);
        tree = ag::ResearchTree::loadFromFile(kRepo + "/extracted/ascend00/restree.txt", err);
        items = ag::loadPlanItems(kRepo + "/extracted/ascend00/planitem.txt", err);
        gizmos = ag::loadGizmos(kRepo + "/extracted/ascend00/gizmos.txt", err);
        for (int i = 0; i < 6; ++i) {
            ag::DipFile df;
            char path[256];
            std::snprintf(path, sizeof(path), "%s/extracted/ascend00/race%02d.dip",
                          ASCENDANCY_SOURCE_DIR, i);
            if (!df.loadFromFile(path, &err)) return std::nullopt;
            ai.push_back(std::move(df));
        }
        loaded = true;
    }
    ag::CampaignConfig cfg;
    cfg.seed = seed;
    cfg.aiCount = 6;
    cfg.playerSpecies = playerSpecies;
    ag::MapConfig mc;
    mc.seed = seed;
    ag::Galaxy g = ag::MapGenerator(mc, stats, names).generate();
    std::string err;
    return std::optional<ag::Campaign>(
        std::in_place, cfg, g, &tree, items, gizmos, ai, &err);
}

const int kSurface[5] = {7, 11, 23, 45, 73};  // measured grid-C row sums
}  // namespace

TEST(homeplanet_table_table_verbatim_tpld1) {
    // The two vendor 21-dword tables verbatim (payload 0x88f90 / 0x88fe4),
    // values MEASURED from work/ascend_payload.bin and cross-validated
    // 85/85 against save-state home worlds (tpld1_spec_home.py).
    static const int T1[21] = {4,4,3,4,3,4,3,3,4,3,3,3,4,4,4,3,4,3,2,3,3};
    static const int T2[21] = {5,1,1,6,3,2,8,6,4,4,10,2,7,8,9,7,3,5,3,7,9};
    CHECK(T1[19] == 3);  // Chamachies size idx -> 45 cells (6/6 lineages)
    CHECK(T2[19] == 7);  // Chamachies terrain row (6/6 lineages)
    CHECK(T1[0] == 4 && T2[0] == 5);   // Minions 73 cells row 5 (17/17)
    CHECK(T1[18] == 2 && T2[18] == 3); // Chronomyst 23 cells row 3 (2/2)
    for (int i = 0; i < 21; ++i) {
        CHECK(T1[i] >= 0 && T1[i] <= 4);
        CHECK(T2[i] >= 0 && T2[i] <= 10);  // weight-row domain
    }
}

TEST(homeplanet_chamachies_45_cells_tpld1) {
    REQUIRE_DATA();
    // D26 complaint case: play Chamachies (specnum 19). Home MUST be the
    // table planet: 45 surface cells, terrain row 7 — every seed.
    for (unsigned seed : {5u, 7u, 11u, 2024u, 424242u}) {
        auto c = mk(19, seed);
        REQUIRE(bool(c));
        const int h = c->homeStarFor(0);
        REQUIRE(h >= 0);
        const auto& ps = c->planetAt(h);
        CHECK(ps.surfaceCells == 45);
        CHECK(ps.terrainRow == 7);
        CHECK(static_cast<int>(ps.cellClasses.size()) == ps.surfaceCells + 10);
        // capBase seed law unchanged on homes (P1: 144/144 corpus):
        int nb = 0;
        for (int k = 0; k < ps.surfaceCells; ++k) {
            const int raw = ps.cellClasses[size_t(k)];
            if (raw != 0 && (raw & 8) == 0) ++nb;
        }
        CHECK(ps.capBase == nb / 3 + 5);
    }
}

TEST(homeplanet_ai_species_table_tpld1) {
    // owner i+1 = specnum i (skip the player's), same mapping as
    // speciesSpecnumOfOwner: with player 19, AI specs are 0..5. Each AI home
    // carries ITS spec's table size/row.
    REQUIRE_DATA();
    auto c = mk(19, 7u);
    REQUIRE(bool(c));
    static const int T1[21] = {4,4,3,4,3,4,3,3,4,3,3,3,4,4,4,3,4,3,2,3,3};
    static const int T2[21] = {5,1,1,6,3,2,8,6,4,4,10,2,7,8,9,7,3,5,3,7,9};
    int sp = 0;
    for (int o = 1; o < c->ownerCount(); ++o) {
        while (sp == 19) ++sp;
        const int h = c->homeStarFor(o);
        REQUIRE(h >= 0);
        CHECK(c->planetAt(h).surfaceCells == kSurface[T1[sp]]);
        CHECK(c->planetAt(h).terrainRow == T2[sp]);
        ++sp;
    }
}

TEST(homeplanet_human_rng_default_tpld1) {
    REQUIRE_DATA();
    // Human player (-1): documented-default rng path stays (no vendor law
    // for a species-less game). Homes are NOT forced to one size class —
    // across seeds the human home size varies (anti-vacuity for the pin
    // above: proves the table branch is keyed on species, not always-on).
    int distinct = 0, seen[5] = {0,0,0,0,0};
    for (unsigned seed : {1u, 2u, 3u, 4u, 5u, 6u, 7u, 8u, 9u, 10u}) {
        auto c = mk(-1, seed);
        REQUIRE(bool(c));
        const int h = c->homeStarFor(0);
        REQUIRE(h >= 0);
        const int cells = c->planetAt(h).surfaceCells;
        for (int i = 0; i < 5; ++i)
            if (cells == kSurface[i]) seen[i] = 1;
    }
    for (int i = 0; i < 5; ++i) distinct += seen[i];
    CHECK(distinct >= 2);  // rng path visibly alive for the human home
}
