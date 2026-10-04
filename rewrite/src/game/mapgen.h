#pragma once
// Galaxy generator. Model + citations: docs/re/mapgen.md section 4.
// Deterministic: the same Config/seed produces a byte-identical galaxy.

#include <cstdint>
#include <random>
#include <string>
#include <vector>

#include "game/starstat.h"

namespace ascend::game {

struct Planet {
    int index = 0;       // 0-based orbit slot
    std::string name;    // "<star base> <roman>", docs/re/mapgen.md §3
};

struct Star {
    int id = 0;
    int x = 0, y = 0;    // logical map units (kMapSize grid, OQ-012)
    int type = 0;        // index into StarStats rows, docs/re/mapgen.md §1
    std::string name;    // base name, unnumbered (§2)
    std::vector<Planet> planets;
};

// Undirected star lane.
struct Lane {
    int a = 0, b = 0;
};

struct Galaxy {
    int seed = 0;
    std::vector<Star> stars;
    std::vector<Lane> lanes;

    int degree(int starId) const;
    std::vector<int> neighbours(int starId) const;
    // BFS reachability from any star; used by tests (connectivity invariant).
    bool connected() const;
    double meanDegree() const;
};

struct MapConfig {
    // Defaults measured from the golden snapshot (docs/re/mapgen.md §3-4).
    int starCount = 75;   // snapshot has 75 distinct star bases
    int mapSize = 1024;   // OQ-012 (snapshot bounds <= 639x479)
    int minSeparation = 60;
    int maxPlanets = 5;   // orbit numerals never exceed V in the snapshot
    unsigned seed = 1;
};

class MapGenerator {
  public:
    MapGenerator(MapConfig cfg, const StarStats& stats, std::vector<std::string> names);

    // Throws std::logic_error only for impossible configs (too many stars for
    // the separation grid, fewer than 2 names). Normal use is fine.
    Galaxy generate() const;

  private:
    MapConfig cfg_;
    const StarStats* stats_;
    std::vector<std::string> names_;
};

}  // namespace ascend::game
