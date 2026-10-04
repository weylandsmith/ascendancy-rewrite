#include "game/mapgen.h"

#include <algorithm>
#include <cmath>
#include <numeric>
#include <queue>
#include <stdexcept>
#include <unordered_set>

namespace ascend::game {
namespace {

uint64_t sq(int v) { return static_cast<uint64_t>(v) * static_cast<uint64_t>(v); }
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
    if (cfg_.minSeparation <= 0 || cfg_.mapSize <= cfg_.minSeparation)
        throw std::logic_error("mapgen: bad separation/mapSize");
    // Rough capacity bound for rejection sampling; beyond it the grid cannot
    // seat the requested count and we fail loudly instead of spinning.
    const uint64_t cells = sq(cfg_.mapSize / cfg_.minSeparation);
    if (static_cast<uint64_t>(cfg_.starCount) > cells)
        throw std::logic_error("mapgen: starCount exceeds placement capacity for separation");
    if (static_cast<int>(names_.size()) < cfg_.starCount)
        throw std::logic_error("mapgen: not enough star names for starCount (names.txt has 101)");

    Galaxy g;
    g.seed = static_cast<int>(cfg_.seed);
    std::mt19937 rng(cfg_.seed);

    // --- 1. positions: uniform in [pad, mapSize-pad], rejection-sampled to
    //        minSeparation (docs/re/mapgen.md §4.1). Deterministic order.
    const int pad = cfg_.minSeparation;
    g.stars.reserve(cfg_.starCount);
    for (int i = 0; i < cfg_.starCount; ++i) {
        std::uniform_int_distribution<int> coord(pad, cfg_.mapSize - pad);
        bool placed = false;
        for (int attempt = 0; attempt < 500 && !placed; ++attempt) {
            Star s;
            s.id = i;
            s.x = coord(rng);
            s.y = coord(rng);
            bool ok = true;
            for (const auto& t : g.stars) {
                if (dist2(s, t) < static_cast<uint64_t>(sq(cfg_.minSeparation))) {
                    ok = false;
                    break;
                }
            }
            if (ok) {
                g.stars.push_back(s);
                placed = true;
            }
        }
        if (!placed) throw std::logic_error("mapgen: rejection sampling exhausted");
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
                    // remember the partner by re-deriving: cheap at n=75
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
