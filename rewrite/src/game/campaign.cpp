#include "game/campaign.h"

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <limits>

namespace ascend::game {
namespace {

// Build order policy [documented default, turnloop.md §4]: factories (IND),
// labs (RES), then agriplots (PROS). Tech gates honoured when REQUIRES is a
// valid tech index (economy.h requiresValidTech); sentinels are UNGATED per
// the economy.md decision.
struct BuildStep {
    const char* name;
    int want;
};
const BuildStep kBuildOrder[] = {{"Factory", 2}, {"Laboratory", 1},
                                 {"Agriplot", 2}, {"Shipyard", 1}};

// (member impl below) — see Campaign::driveHopsFor

}  // namespace

const char* victoryName(Victory v) {
    switch (v) {
        case Victory::None: return "None";
        case Victory::Control: return "Control";
        case Victory::Extinct: return "Extinct";
        case Victory::LastAlive: return "LastAlive";
    }
    return "?";
}

const char* victoryConditionFile(Victory v) {
    switch (v) {
        case Victory::Control: return "end-ctrl";   // "over half the galaxy"
        case Victory::Extinct: return "end-xtnc";   // "Player extinct"
        case Victory::LastAlive: return "end-dest"; // "destroyed other races"
        case Victory::None: return "";
    }
    return "";
}

Campaign::Campaign(const CampaignConfig& cfg, Galaxy galaxy, const ResearchTree* tree,
                   const std::vector<PlanetItem>& items, const std::vector<Gizmo>& gizmos,
                   std::vector<DipFile> aiDip, std::string* errOut)
    : cfg_(cfg), galaxy_(std::move(galaxy)), tree_(tree), items_(&items),
      gizmos_(&gizmos), aiDip_(std::move(aiDip)), rng_(cfg.seed) {
    if (cfg_.aiCount < 0 || cfg_.aiCount > static_cast<int>(aiDip_.size())) {
        *errOut = "campaign: aiCount " + std::to_string(cfg_.aiCount) +
                  " exceeds supplied dip files " + std::to_string(aiDip_.size());
        cfg_.aiCount = static_cast<int>(aiDip_.size());
    }
    if (cfg_.aiCount > 6) {  // NUMCONTROLS 7 [verified windows.txt]
        *errOut = "campaign: aiCount clamped to 6 (NUMCONTROLS 7, turnloop.md §2)";
        cfg_.aiCount = 6;
    }
    const int n = static_cast<int>(galaxy_.stars.size());
    owner_.assign(n, -1);
    planets_.resize(n);
    const int owners = cfg_.aiCount + 1;
    ownedTech.resize(owners);
    for (auto& o : ownedTech) o.assign(tree_->all().size(), false);
    res.assign(owners, 0.0);
    ind_.assign(owners, 0.0);  // IND accumulates as a stockpile (§3)
    queuedTech.assign(owners, -1);
    techProgress.assign(owners, 0.0);
    dipState_.assign(cfg_.aiCount, DipPolicyState{});
    // Relationship starts at the race's own START_ATTITUDE [verified field,
    // docs/re/diplomacy.md §1; start-at-zero is a campaign-level choice that
    // would put EVERY race under its DECLARE_WAR threshold on turn 1].
    for (int i = 0; i < cfg_.aiCount; ++i)
        dipState_[i].attitude = aiDip_[i].values.startAttitude;
    Nowner_ = cfg_.aiCount + 1;
    war_.assign(Nowner_ * Nowner_, 0);
    fortify_.assign(galaxy_.stars.size(), 0);
    if (cfg_.freeForAll)  // arcade default; turnloop.md §5
        for (int x = 0; x < Nowner_; ++x)
            for (int y = 0; y < Nowner_; ++y)
                if (x != y) war_[x * Nowner_ + y] = 1;
    pickHomeStars();
    for (int s = 0; s < n; ++s) {
        if (owner_[s] >= 0) planets_[s].pop = cfg_.initialPop;
    }
    // Opening position on every home (documented default; tutorial.txt in
    // ascend00 describes exactly this state: "we ended after beginning
    // construction of our first Shipyard... Further research has been
    // completed which will allow building a useful ship"; exact start list
    // stays OQ-016). Factory+Lab = economy; Shipyard + restree rows
    // {0 Orbital Structures, 1 Interplanetary Exploration, 2 Tonklin Diary}
    // = the ability to launch a basic ship (docs/re/ships.md §1,§3).
    for (int s = 0; s < n; ++s) {
        if (owner_[s] < 0) continue;
        int f = itemId("Factory"), l = itemId("Laboratory"), y = itemId("Shipyard");
        if (f >= 0) planets_[s].items.push_back(f);
        if (l >= 0) planets_[s].items.push_back(l);
        if (y >= 0) planets_[s].items.push_back(y);
    }
    if (tree_ && tree_->all().size() > 2)
        for (auto& techSet : ownedTech)
            if (techSet.size() > 2) { techSet[0] = true; techSet[1] = true; techSet[2] = true; }
}

int Campaign::itemId(const std::string& name) const {
    for (size_t i = 0; i < items_->size(); ++i)
        if ((*items_)[i].name == name) return static_cast<int>(i);
    return -1;
}

void Campaign::pickHomeStars() {
    // Deterministic spread: each new home maximises min graph-distance to the
    // already-assigned homes (BFS hops), tie -> lowest star id. [documented]
    const int n = static_cast<int>(galaxy_.stars.size());
    std::vector<int> assigned;
    const int owners = cfg_.aiCount + 1;
    for (int o = 0; o < owners; ++o) {
        int best = -1;
        int bestMin = -1;
        for (int s = 0; s < n; ++s) {
            if (std::find(assigned.begin(), assigned.end(), s) != assigned.end()) continue;
            int mind = std::numeric_limits<int>::max();
            for (int a : assigned) {
                // BFS hop distance
                std::vector<int> dist(n, -1);
                std::vector<int> q{a};
                dist[a] = 0;
                for (size_t h = 0; h < q.size(); ++h) {
                    for (int nb : galaxy_.neighbours(q[h]))
                        if (dist[nb] < 0) { dist[nb] = dist[q[h]] + 1; q.push_back(nb); }
                }
                mind = std::min(mind, dist[s]);
            }
            if (assigned.empty()) {
                if (bestMin < 0) { bestMin = 0; best = s; }  // first home: lowest id
                continue;
            }
            if (mind > bestMin || (mind == bestMin && (best < 0 || s < best))) {
                bestMin = mind;
                best = s;
            }
        }
        owner_[best] = o;
        assigned.push_back(best);
    }
}

void Campaign::incomeAndGrow() {
    std::vector<double> income(res.size(), 0.0);
    for (size_t s = 0; s < galaxy_.stars.size(); ++s) {
        int o = owner_[s];
        if (o < 0) continue;
        // Base industry 1 per planet [inferred]; item IND/RES columns
        // [verified planitem rows] drive income (turnloop.md §3).
        income[o] += 1.0;  // industry income (spend currency) [inferred]
        double resGain = 0;
        for (int it : planets_[s].items) {
            const PlanetItem& pi = (*items_)[it];
            income[o] += pi.ind;  // Factory IND=1 [verified]
            resGain += pi.res;    // Laboratory RES=1 [verified]
        }
        res[o] += resGain;
        // Pop growth: logistic toward cap (turnloop.md §3 [inferred]); built
        // items' PROS (Agriplot PROS=2 [verified]) adds while below cap (§3).
        double pros = 0;
        for (int it : planets_[s].items) pros += (*items_)[it].pros;  // Agriplot PROS=2
        double g = 1.0;
        PlanetState& ps = planets_[s];
        ps.pop += g * 4.0 * ps.pop * (cfg_.popCap - ps.pop) /
                  (static_cast<double>(cfg_.popCap) * cfg_.popCap);
        if (ps.pop < cfg_.popCap) ps.pop += pros;
        if (ps.pop > cfg_.popCap) ps.pop = cfg_.popCap;
    }
    for (size_t i = 0; i < income.size(); ++i) ind_[i] += income[i];  // stockpile
}

void Campaign::buildPhase() {
    // One item per owned star per turn if industry covers it (policy
    // [inferred]); order kBuildOrder until quotas, then cheapest Agriplot.
    for (size_t s = 0; s < galaxy_.stars.size(); ++s) {
        int o = owner_[s];
        if (o < 0 || ind_[o] <= 0) continue;
        PlanetState& ps = planets_[s];
        for (const BuildStep& step : kBuildOrder) {
            int have = 0;
            for (int it : ps.items)
                if ((*items_)[it].name == step.name) ++have;
            if (have >= step.want) continue;
            int id = itemId(step.name);
            if (id < 0) continue;
            const PlanetItem& pi = (*items_)[id];
            if (requiresValidTech(pi.requires, tree_->all().size()) &&
                !ownedTech[o][pi.requires])
                continue;  // gated and not researched
            if (ind_[o] >= pi.cost) {
                ind_[o] -= pi.cost;
                ps.items.push_back(id);
            }
            break;  // one build per star per turn
        }
    }
}

void Campaign::researchPhase() {
    for (size_t o = 0; o < ownedTech.size(); ++o) {
        auto avail = tree_->available(ownedTech[o], /*includeVariants=*/true);
        if (queuedTech[o] < 0 || ownedTech[o][queuedTech[o]]) {
            if (avail.empty()) continue;
            if (o == kPlayer) {
                int best = avail[0];
                for (int t : avail)
                    if (tree_->all()[t].cost < tree_->all()[best].cost ||
                        (tree_->all()[t].cost == tree_->all()[best].cost && t < best))
                        best = t;
                queuedTech[o] = best;
            } else {
                std::uniform_int_distribution<size_t> pick(0, avail.size() - 1);
                queuedTech[o] = avail[pick(rng_)];
            }
        }
        const Tech& tq = tree_->all()[queuedTech[o]];
        techProgress[o] += res[o];  // all stockpiled RES goes into research
        res[o] = 0;
        if (techProgress[o] >= tq.cost) {
            ownedTech[o][queuedTech[o]] = true;
            events_.push_back({turn_, "owner " + std::to_string(o) + " researched " + tq.name});
            queuedTech[o] = -1;
            techProgress[o] = 0;
        }
    }
}

void Campaign::expansionPhase() {
    // Arrivals claim targets first (one lane per turn [inferred]).
    for (const ShipInTransit& sh : fleet_) {
        if (owner_[sh.target] < 0) {
            owner_[sh.target] = sh.owner;
            planets_[sh.target].pop = 10;  // settlement seed [inferred]
            events_.push_back({turn_, "owner " + std::to_string(sh.owner) + " colonised " +
                                  galaxy_.stars[sh.target].name});
        }
    }
    fleet_.clear();
    // Launch (docs/re/ships.md §5): precondition = the source star HAS a
    // Shipyard (vendor tutorial: it "makes building ships possible") and
    // the target is within the owner's researched drive range (§3). Hull
    // industry cost 20 [verified planitem row] charged per launch.
    const int shipCost = [&] {
        int id = itemId("Ship");
        return id < 0 ? 20 : (*items_)[id].cost;
    }();
    const int shipyardId = itemId("Shipyard");
    const int owners = cfg_.aiCount + 1;
    for (int o = 0; o < owners; ++o) {
        const int hops = driveHopsFor(o);
        if (hops <= 0) continue;  // no researched drive -> nothing flies (§3)
        for (size_t s = 0; s < galaxy_.stars.size(); ++s) {
            if (owner_[s] != o) continue;
            if (ind_[o] < shipCost) break;  // economy can't spare it
            bool hasYard = shipyardId < 0;
            if (shipyardId >= 0)
                for (int it : planets_[s].items)
                    if (it == shipyardId) { hasYard = true; break; }
            if (!hasYard) continue;  // docs/re/ships.md §1
            // BFS frontier up to `hops`, nearest-first.
            std::vector<int> frontier = galaxy_.neighbours(static_cast<int>(s));
            std::vector<char> seen(galaxy_.stars.size(), 0);
            seen[s] = 1;
            for (int d = 1; d <= hops; ++d) {
                bool launched = false;
                std::vector<int> next;
                for (int nb : frontier) {
                    if (nb < 0 || nb >= (int)seen.size() || seen[nb]) continue;
                    seen[nb] = 1;
                    bool taken = owner_[nb] >= 0;
                    if (!taken)
                        taken = std::any_of(fleet_.begin(), fleet_.end(),
                                            [&](const ShipInTransit& x) { return x.target == nb; });
                    if (taken) { next.push_back(nb); continue; }
                    ind_[o] -= shipCost;
                    fleet_.push_back({o, static_cast<int>(s), nb});
                    launched = true;
                    break;
                }
                if (launched || d == hops) break;
                std::vector<int> expand;
                for (int e : next)
                    for (int nb2 : galaxy_.neighbours(e)) expand.push_back(nb2);
                frontier.swap(expand);
            }
        }
    }
}

int Campaign::driveHopsFor(int owner) const {
    // docs/re/ships.md §3: launch range = best RESEARCHED drive Level / 2
    // lane hops, clamped [1,3] (sugar-cube scale = documented default;
    // drive (level, gate) pairs verified in ships.md §3).
    int lvl = 0;
    if (gizmos_ && owner >= 0 && owner < int(ownedTech.size())) {
        for (const Gizmo& g : *gizmos_) {
            if (g.cat != GizmoCat::Drive) continue;
            if (requiresValidTech(g.resReq, tree_->all().size()) &&
                !ownedTech[owner][g.resReq])
                continue;
            if (g.level > lvl) lvl = g.level;
        }
    }
    return lvl > 0 ? std::max(1, std::min(3, lvl / 2)) : 0;
}

void Campaign::diplomacyPhase() {
    for (int i = 0; i < cfg_.aiCount; ++i) {
        const DipValues& v = aiDip_[i].values;
        AttitudeModel mood(v);
        DipPolicyState& st = dipState_[i];
        DipAction act = decideDipAction(v, mood, turn_, &st);
        const int owner = i + 1;
        if (act == DipAction::DeclareWar && !war_[owner * Nowner_ + kPlayer]) {
            setWar(owner, kPlayer, true);
            events_.push_back({turn_, aiDip_[i].displayName + " declared war on the player"});
        } else if (act == DipAction::BreakAlliance && war_[owner * Nowner_ + kPlayer]) {
            // already at war; nothing to break (alliance bookkeeping R1-blocked)
        } else if (act == DipAction::ProposeAlliance && !st.allied) {
            st.allied = true;
            events_.push_back({turn_, aiDip_[i].displayName + " allied with the player"});
        }
    }
}

int Campaign::attackScore(int owner) const {
    // [inferred, turnloop.md §5] empire fleet strength = total owned pop /10
    // (reserves model) + best OWNED weapon gizmo level (levels 1..13
    // [verified gizmos.md]; gating via resReq -> ownedTech).
    double pop = 0;
    for (size_t s = 0; s < galaxy_.stars.size(); ++s)
        if (owner_[s] == owner) pop += planets_[s].pop;
    int wlvl = 0;
    if (gizmos_) {
        for (const Gizmo& g : *gizmos_) {
            if (g.cat != GizmoCat::Weapon) continue;
            bool ok = !gatedBy(g.resReq) ||
                      (requiresValidTech(g.resReq, tree_->all().size()) &&
                       ownedTech[owner][g.resReq]);
            if (ok) wlvl = std::max(wlvl, g.level);
        }
    }
    return static_cast<int>(pop / 10.0) + wlvl;
}

int Campaign::defenseScore(int owner, int star) const {
    // [inferred] local pop /10 + best owned SHIELD level (1..5 [verified])
    // + terrain/fortify 2.
    double pop = planets_[star].pop;
    int slvl = 0;
    if (gizmos_) {
        for (const Gizmo& g : *gizmos_) {
            if (g.cat != GizmoCat::Shield) continue;
            bool ok = !gatedBy(g.resReq) ||
                      (requiresValidTech(g.resReq, tree_->all().size()) &&
                       ownedTech[owner][g.resReq]);
            if (ok) slvl = std::max(slvl, g.level);
        }
    }
    return static_cast<int>(pop / 10.0) + slvl + 2;
}

void Campaign::setWar(int a, int b, bool on) {
    war_[a * Nowner_ + b] = on ? 1 : 0;
    war_[b * Nowner_ + a] = on ? 1 : 0;
}

void Campaign::combatPhase() {
    // Fortify protects CAPTURED stars (a captured star cannot be attacked for
    // 2 turns — prevents instant ping-pong; a first cut checked the ATTACKER
    // star instead and produced 5k oscillating captures with a frozen front,
    // caught by the no-victory test).
    for (int& f : fortify_) if (f > 0) --f;
    std::uniform_int_distribution<int> noise(0, 10);
    for (size_t s = 0; s < galaxy_.stars.size(); ++s) {
        const int a = owner_[s];
        if (a < 0) continue;
        for (int nb : galaxy_.neighbours(static_cast<int>(s))) {
            const int b = owner_[nb];
            if (b < 0 || b == a || !war_[a * Nowner_ + b]) continue;
            if (fortify_[nb] > 0) continue;
            int atk = attackScore(a) + noise(rng_);
            int def = defenseScore(b, nb) + noise(rng_) / 2;
            if (atk > def) {
                owner_[nb] = a;
                planets_[nb].pop = 10;  // settlement seed (turnloop.md §5)
                fortify_[nb] = 2;
                events_.push_back({turn_, "owner " + std::to_string(a) + " captured " +
                                      galaxy_.stars[nb].name});
                break;
            }
        }
    }
}

Victory Campaign::checkVictory() const {
    const int total = static_cast<int>(galaxy_.stars.size());
    const int mine = starsOwned(kPlayer);
    const bool fleetPending = std::any_of(fleet_.begin(), fleet_.end(),
                                          [&](const ShipInTransit& x) { return x.owner == kPlayer; });
    if (mine == 0 && turn_ > 0 && !fleetPending) return Victory::Extinct;  // end-xtnc
    int alive = 0, last = -1;
    for (int o = 0; o < Nowner_; ++o)
        if (starsOwned(o) > 0) { ++alive; last = o; }
    if (alive == 1 && last == kPlayer) return Victory::LastAlive;          // end-dest
    if (mine * 2 > total) return Victory::Control;                          // end-ctrl "> half"
    return Victory::None;
}

Victory Campaign::advance() {
    if (over()) return victory_;
    ++turn_;
    incomeAndGrow();
    buildPhase();
    researchPhase();
    combatPhase();
    expansionPhase();
    diplomacyPhase();
    victory_ = checkVictory();
    if (victory_ != Victory::None) {
        events_.push_back({turn_, std::string("VICTORY: ") + victoryName(victory_) +
                                  " (" + victoryConditionFile(victory_) + ".txt)"});
    }
    return victory_;
}

int Campaign::starsOwned(int owner) const {
    return static_cast<int>(std::count(owner_.begin(), owner_.end(), owner));
}

int Campaign::techsOwned(int owner) const {
    int n = 0;
    for (bool b : ownedTech[owner]) n += b ? 1 : 0;
    return n;
}

double Campaign::resources(int owner) const { return res[owner]; }

int Campaign::playerScorePct() const {
    const int total = static_cast<int>(galaxy_.stars.size());
    return total ? static_cast<int>(100.0 * starsOwned(kPlayer) / total + 0.5) : 0;
}

std::string Campaign::traceLine() const {
    char buf[192];
    std::snprintf(buf, sizeof(buf),
                  "turn %3d | player stars %2d score %3d%% techs %2d | ai stars",
                  turn_, starsOwned(kPlayer), playerScorePct(), techsOwned(kPlayer));
    std::string out(buf);
    for (int o = 1; o <= cfg_.aiCount; ++o)
        out += " " + std::to_string(starsOwned(o));
    return out;
}

}  // namespace ascend::game
