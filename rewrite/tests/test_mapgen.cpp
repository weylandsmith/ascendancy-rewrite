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
        CHECK(g.stars.size() == 75u);
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
        CHECK(l.a >= 0 && l.b >= 0 && l.a < 75 && l.b < 75);
        CHECK(l.a != l.b);                                    // no self-loops
        CHECK(seen.insert({l.a, l.b}).second);                // no duplicates
        CHECK(seen.find({l.b, l.a}) == seen.end());           // undirected, one copy
    }
}
