#include "game/mapgen.h"
#include "game/starstat.h"
#include "harness.h"

#include <algorithm>
#include <cmath>
#include <filesystem>
#include <map>
#include <set>
#include <sstream>

#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif

namespace fs = std::filesystem;
using ascend::game::Galaxy;
using ascend::game::MapConfig;
using ascend::game::MapGenerator;
using ascend::game::StarStats;

namespace {

const fs::path kRepo = ASCENDANCY_SOURCE_DIR;

std::optional<StarStats> shippedStats() {
    return StarStats::load(kRepo / "extracted" / "ascend00" / "starstat.txt");
}

}  // namespace

TEST(starstat_parses_shipped_file_with_invariants) {
    auto st = shippedStats();
    CHECK(st.has_value());
    if (!st) return;
    CHECK(st->size() == 13);
    double sum = 0;
    for (const auto& r : st->rows()) sum += r.percent;
    CHECK(sum > 99.98 && sum < 100.02);           // docs/re/mapgen.md §1
    CHECK(std::abs(st->meanLanes() - 2.225) < 0.002);
    CHECK(st->rows()[0].percent == 12.57);        // spot values from the table
    CHECK(st->rows()[0].lanes == 2.62);
    CHECK(st->rows()[10].percent == 1.48);
    CHECK(st->rows()[10].lanes == 1.62);
}

TEST(starstat_rejects_bad_inputs) {
    std::string err;
    CHECK(!StarStats::parse("TYPE_0\t 1.0 Percent\t 2.0 Lanes\n", &err).has_value());  // 1 row
    // 13 rows but percent sums to 90: rejected, never renormalised silently
    std::string bad;
    for (int i = 0; i < 13; ++i)
        bad += "TYPE_" + std::to_string(i) + "\t 6.9 Percent\t 2.0 Lanes\n";
    CHECK(!StarStats::parse(bad, &err).has_value());
    // non-contiguous index
    std::string nc = "TYPE_0\t50.0 Percent\t2.0 Lanes\nTYPE_2\t50.0 Percent\t2.0 Lanes\n";
    CHECK(!StarStats::parse(nc, &err).has_value());
}

TEST(star_names_load_100_bases_and_roman_shape) {
    std::string err;
    auto names = ascend::game::loadStarNames(kRepo / "extracted" / "ascend00" / "names.txt", &err);
    CHECK(names.size() == 100);  // docs/re/mapgen.md §2
    if (names.empty()) return;
    CHECK(names[0] == "Vega");
    CHECK(ascend::game::roman(1) == "I");
    CHECK(ascend::game::roman(4) == "IV");
    CHECK(ascend::game::roman(5) == "V");   // max observed in snapshot §3
    CHECK(ascend::game::roman(14) == "XIV");
}

TEST(galaxy_is_deterministic_per_seed) {
    auto st = shippedStats();
    CHECK(st.has_value());
    if (!st) return;
    std::string err;
    auto names = ascend::game::loadStarNames(kRepo / "extracted" / "ascend00" / "names.txt", &err);
    MapConfig cfg;
    auto g1 = MapGenerator(cfg, *st, names).generate();
    auto g2 = MapGenerator(cfg, *st, names).generate();
    CHECK(g1.stars.size() == g2.stars.size());
    CHECK(g1.lanes.size() == g2.lanes.size());
    bool same = true;
    for (size_t i = 0; i < g1.stars.size() && i < g2.stars.size(); ++i) {
        same = same && g1.stars[i].x == g2.stars[i].x && g1.stars[i].y == g2.stars[i].y &&
               g1.stars[i].type == g2.stars[i].type && g1.stars[i].name == g2.stars[i].name &&
               g1.stars[i].planets.size() == g2.stars[i].planets.size();
        for (size_t k = 0; k < g1.stars[i].planets.size() && k < g2.stars[i].planets.size(); ++k)
            same = same && g1.stars[i].planets[k].name == g2.stars[i].planets[k].name;
    }
    for (size_t i = 0; same && i < g1.lanes.size() && i < g2.lanes.size(); ++i)
        same = same && g1.lanes[i].a == g2.lanes[i].a && g1.lanes[i].b == g2.lanes[i].b;
    CHECK(same);
    // different seed -> different layout (astronomically likely)
    MapConfig c2 = cfg;
    c2.seed = 12345;
    auto g3 = MapGenerator(c2, *st, names).generate();
    CHECK(g3.stars[0].x != g1.stars[0].x || g3.stars[0].name != g1.stars[0].name);
}

TEST(galaxy_invariants_over_many_seeds) {
    auto st = shippedStats();
    CHECK(st.has_value());
    if (!st) return;
    std::string err;
    auto names = ascend::game::loadStarNames(kRepo / "extracted" / "ascend00" / "names.txt", &err);
    double degSum = 0;
    int runs = 40;
    int maxOrbit = 0;
    for (int s = 1; s <= runs; ++s) {
        MapConfig cfg;
        cfg.seed = static_cast<unsigned>(s) * 7919u;
        Galaxy g = MapGenerator(cfg, *st, names).generate();
        CHECK(g.stars.size() == 50u);
        CHECK(g.connected());                     // lanes spine (§4.4a)
        std::set<std::string> starNames, planetNames;
        for (const auto& star : g.stars) {
            CHECK(starNames.insert(star.name).second);   // unique bases
            CHECK(!star.planets.empty() && star.planets.size() <= 5);  // §3
            CHECK(star.x >= 60 && star.x <= 1024 - 60);
            CHECK(star.type >= 0 && star.type < 13);
            int k = 1;
            for (const auto& p : star.planets) {         // contiguous I..k (§3)
                CHECK(p.index == k - 1);
                CHECK(p.name == star.name + " " + ascend::game::roman(k));
                CHECK(planetNames.insert(p.name).second);
                maxOrbit = std::max(maxOrbit, k);
                ++k;
            }
            CHECK(g.degree(star.id) >= 1);               // no isolated star
        }
        degSum += g.meanDegree();
    }
    // Realised mean degree should track the table mean 2.225 (docs §4.4b).
    CHECK(std::abs(degSum / runs - 2.225) < 0.35);
    CHECK(maxOrbit <= 5);
}

TEST(galaxy_positions_follow_measured_shell_law) {
    // docs/re/r1-savestate.md 2026-10-06p: radius-by-slot shells 440(k<26)
    // 365(26..37) 290(38..43) 215(44..46) 140(47) 65(48) 50(49), identity
    // across 5 campaigns; default mapSize keeps scale 1.0 so radii are exact.
    auto st = shippedStats();
    if (!st) return;
    std::string err;
    auto names = ascend::game::loadStarNames(kRepo / "extracted" / "ascend00" / "names.txt", &err);
    auto shell = [](int k) {
        return k < 26 ? 440 : k < 38 ? 365 : k < 44 ? 290 : k < 47 ? 215 : k == 47 ? 140 : k == 48 ? 65 : 50;
    };
    for (unsigned s = 1; s <= 10; ++s) {
        MapConfig cfg;
        cfg.seed = s * 104729u;
        Galaxy g = MapGenerator(cfg, *st, names).generate();
        int pops[7] = {0, 0, 0, 0, 0, 0, 0};
        for (size_t k = 0; k < g.stars.size(); ++k) {
            const double dx = g.stars[k].x - 512.0, dy = g.stars[k].y - 512.0;
            const double r = std::sqrt(dx * dx + dy * dy);
            // rounding of int coords: |r - shell| <= ~0.71
            CHECK(std::abs(r - shell(static_cast<int>(k))) < 1.0);
            int band = k < 26 ? 0 : k < 38 ? 1 : k < 44 ? 2 : k < 47 ? 3 : k == 47 ? 4 : k == 48 ? 5 : 5;
            ++pops[band];
        }
        // measured populations 26/12/6/3/1/1/1 (bands merged: outer..5)
        CHECK(pops[0] == 26 && pops[1] == 12 && pops[2] == 6 && pops[3] == 3 && pops[4] == 1 &&
              pops[5] == 2);
    }
}

TEST(galaxy_density_ladder_matches_measured_sizes) {
    // docs/re/mapgen.md OQ-012(a) (t78, 2026-10-12): the original's
    // GALAXY_MORE cycle measures T = 50/75/100/15/25 (Average/Dense/Very
    // Dense/Vacuous/Sparse, wraps at 5). Pin: our generator produces the
    // exact same sizes, every star respects the measured outer envelope
    // r <= 440 (verified across all measured runs), and the map is
    // connected at every rung.
    // OQ-025 (t79) ADDS the shell-population law per size: slot-ordered
    // radii are NON-INCREASING runs at (440,365,290,215,140,65,50) with
    // populations = halving law (shell0 = T/2+1, halve remainder, last
    // shell takes tail) — verified vs live RAM at all five densities
    // (scripts/r1_t79_pos.py).
    auto st = shippedStats();
    if (!st) return;
    std::string err;
    auto names = ascend::game::loadStarNames(kRepo / "extracted" / "ascend00" / "names.txt", &err);
    const int ladder[5] = {50, 75, 100, 15, 25};
    const std::vector<std::vector<int>> expect = {
        {26, 12, 6, 3, 1, 1, 1},   // 50 (== 2026-10-06p battery table)
        {38, 18, 9, 5, 2, 1, 2},   // 75 (measured r1size-041459)
        {51, 24, 12, 6, 3, 2, 2},  // 100 (measured r1size-042719)
        {8, 3, 2, 1, 1},           // 15 (measured r1size-043229 head-15)
        {13, 6, 3, 1, 1, 1},       // 25 (measured r1size-044658 head-25)
    };
    const double kR[7] = {440, 365, 290, 215, 140, 65, 50};
    for (int n = 0; n < 5; ++n) {
        MapConfig cfg;
        cfg.seed = 77u + static_cast<unsigned>(n);
        cfg.starCount = ladder[n];
        Galaxy g = MapGenerator(cfg, *st, names).generate();
        CHECK(static_cast<int>(g.stars.size()) == ladder[n]);
        CHECK(g.connected());
        std::vector<int> radii;
        radii.reserve(g.stars.size());
        for (const auto& s : g.stars) {
            const double dx = s.x - 512.0, dy = s.y - 512.0;
            CHECK(dx * dx + dy * dy <= 441.0 * 441.0);
            radii.push_back(static_cast<int>(std::llround(std::sqrt(dx * dx + dy * dy))));
        }
        // runs of the NEAREST shell index (integer-rounded coords carry
        // <=0.71 radius error; shells are >=15 apart, so nearest is exact)
        auto nearestShell = [&kR](double r) {
            int best = 0;
            for (int j = 1; j < 7; ++j)
                if (std::abs(r - kR[j]) < std::abs(r - kR[best])) best = j;
            return best;
        };
        std::vector<int> pops;
        for (size_t i = 0; i < radii.size();) {
            const int sh = nearestShell(radii[i]);
            size_t j = i;
            while (j < radii.size() && nearestShell(radii[j]) == sh) ++j;
            pops.push_back(static_cast<int>(j - i));
            i = j;
        }
        CHECK(pops == expect[n]);
    }
}

TEST(galaxy_lanes_are_simple_and_bounds_checked) {
    auto st = shippedStats();
    if (!st) return;
    std::string err;
    auto names = ascend::game::loadStarNames(kRepo / "extracted" / "ascend00" / "names.txt", &err);
    MapConfig cfg;
    cfg.seed = 4242;
    Galaxy g = MapGenerator(cfg, *st, names).generate();
    std::set<std::pair<int, int>> seen;
    for (const auto& l : g.lanes) {
        CHECK(l.a >= 0 && l.b >= 0 && l.a < 50 && l.b < 50);
        CHECK(l.a != l.b);                                    // no self-loops
        CHECK(seen.insert({l.a, l.b}).second);                // no duplicates
        CHECK(seen.find({l.b, l.a}) == seen.end());           // undirected, one copy
    }
}
