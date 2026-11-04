// t294 TERRAIN SOURCE-TABLE PINS (OQ-016 residue 3 CLOSED).
// Law (docs/re/income-law.md S10 t294 block, raw-asm this session): the
// vendor loader FUN_00037fc0 fills the terrain weight rows at DS:0x744f4, the
// surface-cell grid at 0x744a8, and the pop-growth scalar at DS:0x66e4 from
// planitem.txt — the rows are NOT compiled into the EXE (0x744f4 lies past the
// initialised data segment; the image-wide SIB-aware store census finds the
// loader @0x3805f as the window's ONLY writer). File grammar: after the lone
// '#' line, integer tokens in order: scalar, 11x4 weights (row-major),
// grid B 5x15 (unmapped), grid C 5x15 (+0x18 = row sum).
//
// Pins: (1) the loader reproduces the MEASURED runtime table from the shipped
// file (file == banked runtime == live RAM 58/59/60.sav, t294); (2-4) the
// campaign CONSUMES cfg.terrain — patched weights/grid change world-gen
// deterministically (mutation-verified: revert campaign.cpp to the old
// hardcoded kRows and legs 2-4 fail); (5) strict rejection laws.
#include "harness.h"
#include "game/campaign.h"
#include "game/economy.h"

#include <filesystem>
#include <fstream>
#include <string>

#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif

namespace ag = ascend::game;

// Seeded campaign factory with an injected terrain table (test_campaign.cpp;
// t202b/t291 extern-wrapper precedent).
ag::Campaign makeCampaignWithTerrain(unsigned seed, const ag::TerrainTables& tt);

namespace {
const std::filesystem::path kPlanitem =
    std::filesystem::path(ASCENDANCY_SOURCE_DIR) / "extracted" / "ascend00" /
    "planitem.txt";

int barrenPct(const ag::Campaign& c, int n) {
    long barren = 0, cells = 0;
    for (int s = 0; s < n; ++s) {
        const ag::PlanetState& ps = c.planetAt(s);
        for (int i = 0; i < ps.surfaceCells; ++i) {
            ++cells;
            if ((ps.cellClasses[i] & ~8) == 0) ++barren;  // rock bit stripped
        }
    }
    return cells ? static_cast<int>(100 * barren / cells) : 0;
}
}  // namespace

TEST(terrain_tables_match_measured_runtime_0x744f4) {
    ag::TerrainTables tt;
    std::string err;
    CHECK(ag::loadTerrainTables(kPlanitem.string(), tt, err));
    CHECK(err.empty());
    // The banked runtime census (income-law S10, 13 captures) == file rows.
    static const int kMeasured[11][4] = {
        {100,0,0,0},   {50,2,2,2},   {20,3,5,3},   {0,3,20,3},   {40,10,2,2},
        {20,20,2,2},   {40,2,2,10},  {20,3,3,20},  {40,10,10,10},{20,15,15,15},
        {0,33,34,33}};
    for (int i = 0; i < 11; ++i)
        for (int j = 0; j < 4; ++j) CHECK(tt.weights[i][j] == kMeasured[i][j]);
    CHECK(tt == ag::vendorTerrainTables());
    // grid C row sums == live +0x18 census (2650/2650 records, OQ-014).
    CHECK(tt.surfaceBySize[0] == 7);  CHECK(tt.surfaceBySize[1] == 11);
    CHECK(tt.surfaceBySize[2] == 23); CHECK(tt.surfaceBySize[3] == 45);
    CHECK(tt.surfaceBySize[4] == 73);
    // pop-growth scalar DS:0x66e4 == 50 (S6c decisive capture).
    CHECK(tt.popGrowth == 50);
}

TEST(terrain_weights_are_consumed_not_hardcoded) {
    // All rows [100,0,0,0]: scaled w0 = 32767, so rng(0..32767) < w0 on every
    // draw -> BARREN everywhere (r==32767 exactly takes the chain's class-1
    // remainder; >=99.9% barren is the law's own prediction). Control: the
    // stock table at the same seed is NOT anywhere near that.
    ag::TerrainTables allBarren = ag::vendorTerrainTables();
    for (int i = 0; i < 11; ++i)
        for (int j = 0; j < 4; ++j) allBarren.weights[i][j] = (j == 0) ? 100 : 0;
    const int n = 50;
    auto ca = makeCampaignWithTerrain(7, allBarren);
    CHECK(barrenPct(ca, n) >= 99);
    auto cb = makeCampaignWithTerrain(7, ag::vendorTerrainTables());
    CHECK(barrenPct(cb, n) < 90);  // stock rows mix w0 0..100
    // And the seed law follows: capBase = nonbarren/3 + 5 == 5 everywhere.
    for (int s = 0; s < n; ++s) CHECK(ca.planetAt(s).capBase == 5);
}

TEST(terrain_surface_grid_is_consumed) {
    // Grid C patched to 1 cell per size class: every planet carries exactly
    // one surface cell (+10 orbital), whatever the size draw.
    ag::TerrainTables one = ag::vendorTerrainTables();
    for (int i = 0; i < 5; ++i) one.surfaceBySize[i] = 1;
    auto c = makeCampaignWithTerrain(7, one);
    for (int s = 0; s < 50; ++s) CHECK(c.planetAt(s).surfaceCells == 1);
    auto d = makeCampaignWithTerrain(7, ag::vendorTerrainTables());
    int distinct = 0;
    for (int s = 0; s < 50; ++s)
        if (d.planetAt(s).surfaceCells != 1) ++distinct;
    CHECK(distinct > 0);  // stock grid varies by size class (7/11/23/45/73)
}

TEST(terrain_pop_growth_scalar_is_consumed) {
    // popGrowth 1: every turn with stored PROS >= 1 wraps immediately, so pop
    // climbs to cap fast; stock 50 is the ~25-turn cadence (income-law S6c).
    ag::TerrainTables fast = ag::vendorTerrainTables();
    fast.popGrowth = 1;
    auto a = makeCampaignWithTerrain(7, fast);
    auto b = makeCampaignWithTerrain(7, ag::vendorTerrainTables());
    for (int t = 0; t < 10; ++t) { a.advance(); b.advance(); }
    long pa = 0, pb = 0;
    for (int s = 0; s < 50; ++s) {
        if (a.starOwner(s) >= 0) pa += static_cast<long>(a.planetAt(s).pop);
        if (b.starOwner(s) >= 0) pb += static_cast<long>(b.planetAt(s).pop);
    }
    CHECK(pa > pb);  // deterministic seeded campaigns: not a flake window
}

TEST(terrain_loader_rejects_out_of_range) {
    namespace fs = std::filesystem;
    const fs::path tmp = fs::temp_directory_path() / "t294_bad_planitem.txt";
    std::string err;
    ag::TerrainTables tt;
    {
        std::ofstream f(tmp, std::ios::binary);
        f << "junk\r\n#\r\n\r\n50\r\n";
        f << "300 0 0 0\r\n";  // u8 store law violation on first weight
        for (int i = 1; i < 11; ++i) f << "1 1 1 1\r\n";
        for (int g = 0; g < 2; ++g)
            for (int i = 0; i < 5; ++i) {
                for (int j = 0; j < 15; ++j) f << (j ? " 1" : "0");
                f << "\r\n";
            }
    }
    CHECK(!ag::loadTerrainTables(tmp.string(), tt, err));
    CHECK(err.find("u8") != std::string::npos);
    {
        std::ofstream f(tmp, std::ios::binary);
        f << "junk\r\n#\r\n\r\n50\r\n";
        for (int i = 0; i < 11; ++i) f << "1 1 1 1\r\n";
        f << "\r\n";
        for (int g = 0; g < 2; ++g)
            for (int i = 0; i < 5; ++i) {
                for (int j = 0; j < 15; ++j) f << (j ? " 9" : "9");
                f << "\r\n";  // every grid row sums 135 > 100 (+0x18 cap)
            }
    }
    CHECK(!ag::loadTerrainTables(tmp.string(), tt, err));
    CHECK(err.find("100") != std::string::npos);
    fs::remove(tmp);
}
