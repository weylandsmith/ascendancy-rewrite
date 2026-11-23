// SPDX-License-Identifier: GPL-3.0-or-later

#include "game/mapgen.h"

#include <algorithm>
#include <cmath>
#include <numeric>
#include <queue>
#include <stdexcept>
#include <unordered_set>

namespace ascend::game {

// Measured shell-population law (docs/re/mapgen.md §OQ-025, t79): build the
// per-slot shell-radius table for ANY galaxy size: shell0 = n/2+1 stars at
// r=440, each next shell (365,290,215,140,65) takes half the remainder
// (a remainder of 1 keeps it), shell6 (r=50) takes the final tail. At
// n=50 this reproduces the k0..k49 battery table exactly (26/12/6/3/1/1/1).
// tNGS P4: PUBLIC — the newgame preview starfield draws each slot at its
// shell radius (docs/re/_wip_tNGS.md S15; the vendor generator FUN_00022878
// scales the normalized direction by the shell accumulator).
std::vector<int> shellRadiiFor(int n) {
    static const int kRadii[7] = {440, 365, 290, 215, 140, 65, 50};
    std::vector<int> out;
    out.reserve(static_cast<size_t>(n));
    int rem = n;
    for (int j = 0; j < 7 && rem > 0; ++j) {
        const int c = (j == 0) ? rem / 2 + 1
                      : (j == 6) ? rem
                      : (rem >= 2 ? rem / 2 : rem);
        for (int i = 0; i < c; ++i) out.push_back(kRadii[j]);
        rem -= c;
    }
    return out;
}

namespace {

uint64_t dist2(const Star& a, const Star& b) {
    const int64_t dx = a.x - b.x, dy = a.y - b.y;
    return static_cast<uint64_t>(dx * dx + dy * dy);
}

}  // namespace

int Galaxy::degree(int starId) const {
    int d = 0;
    for (const auto& l : lanes)
        if (l.a == starId || l.b == starId) ++d;
    return d;
}

std::vector<int> Galaxy::neighbours(int starId) const {
    std::vector<int> out;
    for (const auto& l : lanes) {
        if (l.a == starId) out.push_back(l.b);
        else if (l.b == starId) out.push_back(l.a);
    }
    std::sort(out.begin(), out.end());
    return out;
}

bool Galaxy::connected() const {
    if (stars.empty()) return true;
    std::vector<char> seen(stars.size(), 0);
    std::vector<int> stack{0};
    seen[0] = 1;
    size_t count = 1;
    while (!stack.empty()) {
        const int s = stack.back();
        stack.pop_back();
        for (const auto& l : lanes) {
            int other = -1;
            if (l.a == s) other = l.b;
            else if (l.b == s) other = l.a;
            if (other >= 0 && !seen[other]) {
                seen[other] = 1;
                ++count;
                stack.push_back(other);
            }
        }
    }
    return count == stars.size();
}

double Galaxy::meanDegree() const {
    if (stars.empty()) return 0.0;
    double s = 0;
    for (size_t i = 0; i < stars.size(); ++i) s += degree(static_cast<int>(i));
    return s / static_cast<double>(stars.size());
}

MapGenerator::MapGenerator(MapConfig cfg, const StarStats& stats, std::vector<std::string> names)
    : cfg_(cfg), stats_(&stats), names_(std::move(names)) {}

Galaxy MapGenerator::generate() const {
    if (cfg_.starCount < 2) throw std::logic_error("mapgen: need >= 2 stars");
    if (cfg_.minSeparation <= 0 || cfg_.mapSize <= 2 * cfg_.minSeparation)
        throw std::logic_error("mapgen: bad separation/mapSize");
    // (Shell placement has no capacity limit — the original overlaps stars on
    // a shell freely — so the old rejection-grid capacity check is gone.)
    if (static_cast<int>(names_.size()) < cfg_.starCount)
        throw std::logic_error("mapgen: not enough star names for starCount (names.txt has 101)");

    Galaxy g;
    g.seed = static_cast<int>(cfg_.seed);
    std::mt19937 rng(cfg_.seed);

    // --- 1. positions: measured SHELL law (docs/re/mapgen.md §4.1 +
    //        §OQ-025). Star at table slot k sits at shell radius SHELL[k]
    //        x a random direction. The ORIGINAL's law is on the 3D radius
    //        name-0x14 f32[x,y,z] over a sphere (OQ-012(d)+(c)); this 2D
    //        engine maps that 3D radius onto the plane radius directly —
    //        the v1 hybrid model choice that reproduces the measured mean
    //        degree 2.225 (§4.4b) — so shell rings here, sphere there.
    //        SHELL POPULATIONS for any total n follow the MEASURED halving
    //        law (OQ-025 t79, scripts/r1_t79_pos.py: fits T = 15/25/50/75/
    //        100 exactly — shell0 = n/2+1, each next shell halves the
    //        remainder (rem 1 keeps it), shell6 (r=50) takes the tail):
    //        50 -> 26/12/6/3/1/1/1 (identical to the k0..k49 battery table
    //        of 2026-10-06p), 75 -> 38/18/9/5/2/1/2, 100 -> 51/24/12/6/3/
    //        2/2, 15 -> 8/3/2/1/1, 25 -> 13/6/3/1/1/1. This REPLACES the
    //        old i%50 wrap-around, which was measured WRONG for T>50 (the
    //        original keeps slot 50+ on shell 440, not back on 365). No
    //        min-separation is enforced (closest observed pair 24.4 units).
    const std::vector<int> shellR = shellRadiiFor(cfg_.starCount);
    const double kOuterR = 440.0;  // outermost measured shell (original units)
    // Default mapSize (1024) keeps the ORIGINAL radii untouched (scale 1.0);
    // smaller maps scale the whole shell system down to fit
    // (docs/re/mapgen.md §4.1 scale note).
    const double scale =
        static_cast<double>(cfg_.mapSize) >= 2.0 * (kOuterR + cfg_.minSeparation)
            ? 1.0
            : (cfg_.mapSize / 2.0 - cfg_.minSeparation) / kOuterR;
    const double cx = cfg_.mapSize / 2.0, cy = cfg_.mapSize / 2.0;
    const double kTau = 6.283185307179586;
    std::uniform_real_distribution<double> uang(0.0, kTau);
    g.stars.reserve(cfg_.starCount);
    for (int i = 0; i < cfg_.starCount; ++i) {
        Star s;
        s.id = i;
        const double a = uang(rng);
        const double r = shellR[static_cast<size_t>(i)] * scale;
        s.x = static_cast<int>(std::llround(cx + r * std::cos(a)));
        s.y = static_cast<int>(std::llround(cy + r * std::sin(a)));
        // t399 field depth (Star.z): splitmix64(seed, slot) — NOT rng_, so
        // the seeded trajectory stream is untouched (gate 3l byte identity).
        // Uniform-marginal over [-r, r] like the measured sphere z law
        // (r1-savestate OQ-012(c)); xy stays the documented 2D hybrid.
        uint64_t h = static_cast<uint64_t>(cfg_.seed) * 0x9E3779B97F4A7C15ull +
                     static_cast<uint64_t>(i) * 0xD1B5BA8D4B2B2A1ull + 0x7A5B6C3Dull;
        h ^= h >> 30; h *= 0xBF58476D1CE4E5B9ull;
        h ^= h >> 27; h *= 0x94D049BB133111EBull;
        h ^= h >> 31;
        s.z = static_cast<int>(std::llround(r * (double(h) / 18446744073709551616.0 * 2.0 - 1.0)));
        g.stars.push_back(std::move(s));
    }

    // --- 2. star types: weighted by the percent column (§4.2)
    std::uniform_real_distribution<double> u01(0.0, 1.0);
    for (auto& s : g.stars) s.type = stats_->pickType(u01(rng));

    // --- 3. planets: uniform count 1..maxPlanets, names "<base> <roman>"
    //        (§4.3; orbit numerals I..V verified, docs/re/mapgen.md §3)
    std::uniform_int_distribution<int> nplan(1, cfg_.maxPlanets);
    for (auto& s : g.stars) {
        const int n = nplan(rng);
        s.planets.reserve(n);
        for (int k = 0; k < n; ++k) {
            Planet p;
            p.index = k;
            s.planets.push_back(std::move(p));
        }
    }

    // Names: shuffle the pool once, hand out unique bases (§2, §4.5).
    std::vector<std::string> pool = names_;
    std::shuffle(pool.begin(), pool.end(), rng);
    for (size_t i = 0; i < g.stars.size(); ++i) {
        g.stars[i].name = pool[i];
        for (auto& p : g.stars[i].planets) p.name = pool[i] + " " + roman(p.index + 1);
    }

    // --- 4. lanes (§4.4):
    //   a) connectivity spine: greedy nearest-neighbour tree (each star joins
    //      the nearest already-connected star). Chosen so interstellar travel
    //      is always possible (inferred constraint, §4.4).
    std::vector<char> inTree(g.stars.size(), 0);
    std::vector<Lane> edges;
    inTree[0] = 1;
    for (size_t step = 1; step < g.stars.size(); ++step) {
        int best = -1;
        uint64_t bestD2 = ~0ull;
        for (size_t c = 0; c < g.stars.size(); ++c) {
            if (inTree[c]) continue;
            for (size_t t = 0; t < g.stars.size(); ++t) {
                if (!inTree[t]) continue;
                const uint64_t dd = dist2(g.stars[c], g.stars[t]);
                if (dd < bestD2) {
                    bestD2 = dd;
                    best = static_cast<int>(c);
                    // remember the partner by re-deriving: cheap at n=50
                }
            }
        }
        if (best < 0) throw std::logic_error("mapgen: tree growth failed");
        // find partner of best (deterministic: lowest tree index at bestD2)
        int partner = -1;
        for (size_t t = 0; t < g.stars.size(); ++t) {
            if (inTree[t] && dist2(g.stars[best], g.stars[t]) == bestD2) {
                partner = static_cast<int>(t);
                break;
            }
        }
        inTree[best] = 1;
        edges.push_back({std::min(best, partner), std::max(best, partner)});
    }

    //   b) extra lanes until sum(degree) reaches sum(per-type mean lanes).
    double target = 0.0;
    for (const auto& s : g.stars) target += (*stats_).rows()[s.type].lanes;
    std::vector<std::pair<uint64_t, Lane>> cand;
    cand.reserve(g.stars.size() * g.stars.size());
    for (size_t i = 0; i < g.stars.size(); ++i)
        for (size_t j = i + 1; j < g.stars.size(); ++j)
            cand.push_back({dist2(g.stars[i], g.stars[j]), Lane{static_cast<int>(i), static_cast<int>(j)}});
    std::sort(cand.begin(), cand.end(), [](const auto& x, const auto& y) {
        if (x.first != y.first) return x.first < y.first;
        if (x.second.a != y.second.a) return x.second.a < y.second.a;
        return x.second.b < y.second.b;
    });
    std::unordered_set<uint64_t> have;
    auto key = [](const Lane& l) { return static_cast<uint64_t>(l.a) << 16 | static_cast<uint64_t>(l.b); };
    for (const auto& e : edges) have.insert(key(e));

    std::vector<int> deg(g.stars.size(), 0);
    for (const auto& e : edges) {
        ++deg[e.a];
        ++deg[e.b];
    }
    double totalDeg = 2.0 * static_cast<double>(edges.size());
    // Stop when sum(degree) reaches the table-derived target (§4.4b). A star
    // may take one more lane only while it is still strictly below its own
    // type mean (integer degree vs fractional mean gives the rounding
    // headroom); this keeps distance-greedy from inflating local hubs. An
    // earlier revision stopped at target + starCount, which let hubs grow and
    // pushed realised mean degree outside the +-0.35 band (caught by test).
    for (const auto& c : cand) {
        if (totalDeg + 2.0 > target) break;
        if (have.count(key(c.second))) continue;
        const double ta = (*stats_).rows()[g.stars[c.second.a].type].lanes;
        const double tb = (*stats_).rows()[g.stars[c.second.b].type].lanes;
        if (static_cast<double>(deg[c.second.a]) + 1.0 > ta) continue;
        if (static_cast<double>(deg[c.second.b]) + 1.0 > tb) continue;
        edges.push_back(c.second);
        have.insert(key(c.second));
        ++deg[c.second.a];
        ++deg[c.second.b];
        totalDeg += 2.0;
    }

    std::sort(edges.begin(), edges.end(), [](const Lane& x, const Lane& y) {
        if (x.a != y.a) return x.a < y.a;
        return x.b < y.b;
    });
    g.lanes = std::move(edges);
    return g;
}

}  // namespace ascend::game
