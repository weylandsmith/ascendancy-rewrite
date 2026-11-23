// SPDX-License-Identifier: GPL-3.0-or-later

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
    // t399: field depth. The ORIGINAL's star position is f32[x,y,z] on a
    // sphere (r1-savestate.md OQ-012(c): shell radius x random unit vector,
    // z uniform-marginal). z here is a PURE function of (seed, slot) —
    // splitmix64, NOT the engine rng_ — so adding it cannot shift any
    // seeded trajectory (gate 3l byte-identity law); sim consumers (lane
    // distance, combat) keep using x/y. Scaled to the star's shell radius.
    int z = 0;
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
    // starCount: FRESH campaigns measured 50 systems exactly, 5/5 runs
    // (docs/re/r1-savestate.md 2026-10-06p star battery). The original's
    // GALAXY_MORE density cycle is MEASURED 2026-10-12 (mapgen.md
    // OQ-012(a)): Average 50 -> Dense 75 -> Very Dense 100 -> Vacuous 15
    // -> Sparse 25 -> wrap; default here = Average. Shell populations for
    // any size follow the MEASURED halving law (mapgen.md §OQ-025 t79;
    // shellRadiiFor in mapgen.cpp) — exact at all five densities.
    // minSeparation no longer gates placement (shells allow
    // overlap) but still pads the fit-to-map scale below.
    int starCount = 50;
    int mapSize = 1024;   // OQ-012 (snapshot bounds <= 639x479)
    int minSeparation = 60;
    int maxPlanets = 5;   // orbit numerals never exceed V in the snapshot
    unsigned seed = 1;
};

// Measured shell-population law (mapgen.md §OQ-025 t79): per-slot shell
// radius table for ANY galaxy size (shell0 = n/2+1 at 440, halving
// remainder through 365/290/215/140/65, tail at 50). tNGS P4: also drives
// the newgame preview starfield (docs/re/_wip_tNGS.md S15/S22).
std::vector<int> shellRadiiFor(int n);

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
