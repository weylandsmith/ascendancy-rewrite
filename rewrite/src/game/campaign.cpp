#include "game/campaign.h"

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <limits>

namespace ascend::game {
namespace {

// Build order policy [documented default, turnloop.md §4]: factories (IND),
// labs (RES), then agriplots (PROS). Tech gates use the MEASURED availability
// law (economy.h requiresAvailable, OQ-014 CLOSED): req==255 ungated, real
// row must be owned, 254 permanently dead.
struct BuildStep {
    const char* name;
    int want;
};
const BuildStep kBuildOrder[] = {{"Factory", 2}, {"Laboratory", 1},
                                 {"Agriplot", 2}, {"Shipyard", 1}};

// Colony income channels, MEASURED law (docs/re/income-law.md S6/t18b +
// t19/t20 battery r1_income_channels.py 138/139/136): the original stores
// per planet  IND->rec+0x44, RES->+0x46, PROS->+0x48  as
//   acc == 0            -> scenario grant (captured value 1: FUN_00025d30
//                          colonization +1 on both linked home records)
//   otherwise           -> trunc((dbl(acc, f) + 1) ^ 0.85)   [IND, PROS]
//                          dbl(acc) + 1 - 1                   [RES: linear,
//                            never pow-compressed; the +1/-1 keeps the same
//                            shape — stored value is the accumulator]
// dbl(v, f) = v + (v >> 1) when the FIRST table slot k is occupied+ACTIVE
// (FUN_0003958c + bit-test @0x38d4b/0x38d90/0x38db5): k=12 Hyperpower Plant
// doubles IND, k=13 Fertilization Plant doubles PROS, k=14 Internet doubles
// RES. The rewrite has no per-slot terrain model, so the cls==2/3/4 +1
// accumulation bonuses are absent [documented gap], and no planet upkeep
// field exists to carry the PROS -= upkeep/4 penalty (growth-counter law
// still open, income-law.md S6b) — PROS here is the pre-penalty stored
// value.
constexpr double kColonyIncomeGrant = 1.0;

double colonyChannel(int acc, bool firstDoubleActive, bool compress) {
    if (acc == 0) return kColonyIncomeGrant;  // grant survives recalc JZ-skip
    int v = acc + (firstDoubleActive ? acc >> 1 : 0);
    if (!compress) return static_cast<double>(v);
    return std::floor(std::pow(static_cast<double>(v + 1), 0.85));
}

// Planet SIZE classes map onto grid-C surface-cell counts {7,11,23,45,73};
// the rewrite's mapgen does not yet assign per-star size classes (parking
// lot, STATE.md), so builds are capped with the MEASURED class-2 default.
constexpr int kDefaultSizeClass = 2;

// (member impl below) — see Campaign::driveHopsFor

}  // namespace

const char* victoryName(Victory v) {
    switch (v) {
        case Victory::None: return "None";
        case Victory::Control: return "Control";
        case Victory::Captured: return "Captured";
        case Victory::Unification: return "Unification";
        case Victory::Extinct: return "Extinct";
        case Victory::LastAlive: return "LastAlive";
    }
    return "?";
}

const char* victoryConditionFile(Victory v) {
    switch (v) {
        case Victory::Control: return "end-ctrl";   // "over half the galaxy"
        case Victory::Captured: return "end-capt";  // "captured all home worlds"
        case Victory::Unification: return "end-unit"; // "one alliance, player alive"
        case Victory::Extinct: return "end-xtnc";   // "Player extinct"
        case Victory::LastAlive: return "end-dest"; // "destroyed other races"
        case Victory::None: return "";
    }
    return "";
}

Campaign::Campaign(const CampaignConfig& cfg, Galaxy galaxy, const ResearchTree* tree,
                   const std::vector<PlanetItem>& items, const std::vector<Gizmo>& gizmos,
                   std::vector<DipFile> aiDip, std::string* errOut)
    : Campaign(cfg, std::move(galaxy), tree, items, gizmos, std::move(aiDip), {}, errOut) {}

Campaign::Campaign(const CampaignConfig& cfg, Galaxy galaxy, const ResearchTree* tree,
                   const std::vector<PlanetItem>& items, const std::vector<Gizmo>& gizmos,
                   std::vector<DipFile> aiDip, std::vector<SpeciesAbility> abilities,
                   std::string* errOut)
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
    // Species ability assignment (docs/re/abilities.md §1): explicit vector
    // wins; otherwise derive from dip header tokens (race02 stays Unknown —
    // its header has no token, and the help.txt cross-check lives in
    // loadAbilities, callers that care pass abilities explicitly).
    ability_.assign(Nowner_, SpeciesAbility::Unknown);
    if (!abilities.empty()) {
        if (abilities.size() != aiDip_.size())
            *errOut = "campaign: abilities vector size " + std::to_string(abilities.size()) +
                      " != dip files " + std::to_string(aiDip_.size());
        for (size_t i = 0; i < abilities.size() && i < aiDip_.size() && int(i) < cfg_.aiCount; ++i)
            ability_[i + 1] = abilities[i];
    } else {
        for (size_t i = 0; i < aiDip_.size() && int(i) < cfg_.aiCount; ++i)
            ability_[i + 1] = abilityFromToken(aiDip_[i].abilityToken);
    }
    if (cfg_.playerSpecies >= 0 && cfg_.playerSpecies < static_cast<int>(SpeciesAbility::kCount))
        ability_[kPlayer] = static_cast<SpeciesAbility>(cfg_.playerSpecies);
    charge_.assign(Nowner_, 0);  // first activation one full charge away
    for (int o = 0; o < Nowner_; ++o)
        if (abilityIsCharged(ability_[o])) charge_[o] = abilityChargeTurns(ability_[o]);
    doublePower_.assign(Nowner_, 0);
    sapActive_.assign(Nowner_, 0);
    fleetDamage_.assign(Nowner_, 0);
    invincible_.assign(galaxy_.stars.size(), 0);
    laneBlock_.assign(galaxy_.stars.size(), 0);
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
    homeStar_ = assigned;  // fixed at setup; Captured tests these ids (§1)
}

double Campaign::popCapFor(int star) const {
    return cfg_.popCap + planets_[star].capBonus;  // SA_MoreMaxPop bonus
}

bool Campaign::lanePassable(int owner, int target) const {
    // SA_BlockStarLanes (help.txt L2314 "block all star lanes entering your
    // colonized systems"): lanes into a star blocked THIS turn admit no
    // launches or invasions by anyone but the blocker itself. [inferred
    // duration: one turn; vendor gives no number — abilities.md §3]
    if (laneBlock_[target] && owner_[target] != owner) return false;
    return true;
}

void Campaign::incomeAndGrow() {
    std::vector<double> income(res.size(), 0.0);
    const int idHyper = itemId("Hyperpower Plant");
    const int idNet = itemId("Internet");
    for (size_t s = 0; s < galaxy_.stars.size(); ++s) {
        int o = owner_[s];
        if (o < 0) continue;
        // Per-planet stored channels under the MEASURED law (helper cites
        // income-law.md). The original charges the COMPRESSED stored value
        // into the empire budget each turn (turn tick FUN_00038f68 sums
        // +0x44/+0x46 across owned planets; income accumulation site
        // banked with the channel battery).
        int accI = 0, accR = 0;
        bool dblI = false, dblR = false;
        for (int it : planets_[s].items) {
            const PlanetItem& pi = (*items_)[it];
            accI += pi.ind;
            accR += pi.res;
            // first-occupied-slot doubling law uses TABLE index order; the
            // rewrite builds in kBuildOrder order, so "first occupied" is
            // approximated by "first listed as built" per channel below.
            if (!dblR && it == idNet) dblR = true;
            if (!dblI && it == idHyper) dblI = true;
        }
        income[o] += colonyChannel(accI, dblI, /*compress=*/true);
        res[o] += colonyChannel(accR, dblR, /*compress=*/false);
        // PROS: growth model upgrade waits on the open accumulation-36
        // anomaly (income-law.md S6b), so pop growth keeps the v1 raw-PROS
        // additive default [documented default, turnloop.md §3];
        // SA_Cornucopia's richPros rides the same channel.
        double pros = planets_[s].richPros;
        for (int it : planets_[s].items) pros += (*items_)[it].pros;
        double g = 1.0;
        PlanetState& ps = planets_[s];
        const double cap = popCapFor(static_cast<int>(s));  // SA_MoreMaxPop
        ps.pop += g * 4.0 * ps.pop * (cap - ps.pop) / (cap * cap);
        if (ps.pop < cap) ps.pop += pros;
        if (ps.pop > cap) ps.pop = cap;
    }
    for (size_t i = 0; i < income.size(); ++i) ind_[i] += income[i];  // stockpile
    // Fleet "power" regens at 5/turn once sapped [documented default,
    // abilities.md §3 — no data exposes a repair rate or its precondition].
    for (int o = 0; o < Nowner_; ++o) {
        if (fleetDamage_[o] <= 0) continue;
        fleetDamage_[o] = std::max(0, fleetDamage_[o] - 5);
    }
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
            // OQ-014 CLOSED (economy.md §4): gate == req==255 || (req<count &&
            // owned). 254 (Interstellar Trucking) is NEITHER -> permanently
            // unavailable in the original; the old requiresValidTech-based
            // test let it build. Surface items are additionally capped at the
            // planet's surface slot count (size-class default until mapgen
            // assigns classes — parking lot, STATE.md).
            if (!requiresAvailable(pi.requires, static_cast<int>(tree_->all().size()),
                                   ownedTech[o]))
                continue;
            if (itemIsSurface(id)) {
                int surface = 0;
                for (int it : ps.items)
                    if (itemIsSurface(it)) ++surface;
                if (surface >= planetSurfaceCells(kDefaultSizeClass)) break;
            }
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
        // OQ-013 CLOSED (research.md §7): the original loads only the 66
        // main-tree rows, so variants are not in play -> includeVariants=false.
        auto avail = tree_->available(ownedTech[o], /*includeVariants=*/false);
        if (queuedTech[o] < 0 || ownedTech[o][queuedTech[o]]) {
            if (avail.empty()) continue;
            if (o == kPlayer) {
                int best = avail[0];
                for (int t : avail)
                    if (tree_->all()[t].runtimeCost() < tree_->all()[best].runtimeCost() ||
                        (tree_->all()[t].runtimeCost() == tree_->all()[best].runtimeCost() && t < best))
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
        if (techProgress[o] >= tq.runtimeCost()) {
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
            // BFS frontier up to `hops`, nearest-first. Knowledge gate
            // (starKnown: own star or adjacent-to-own; SA_KnowStarLanes sees
            // everything — abilities.md §2) and SA_BlockStarLanes gate.
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
                    if (!lanePassable(o, nb)) {
                        next.push_back(nb);  // SA_BlockStarLanes: can't target it
                        continue;
                    }
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
            if (!requiresAvailable(g.resReq, static_cast<int>(tree_->all().size()),
                                   ownedTech[owner]))
                continue;  // OQ-014 gate law (economy.h)
            if (g.level > lvl) lvl = g.level;
        }
    }
    if (lvl <= 0) return 0;
    int hops = lvl / 2;
    // SA_FastLaneTravel (help.txt L2409-2410 "move quickly through star
    // lanes"): +1 lane hop [documented mapping, abilities.md §2 — the vendor
    // gives no numeric speed; hop scale itself is OQ-019]. Applied to the
    // HOP count before the clamp — an earlier cut did ++lvl before lvl/2,
    // which silently did nothing at odd quotients (lvl 2 -> 1 hop, lvl 3 ->
    // 1 hop; self-caught while planning the end-capt reachability test).
    if (ability_[owner] == SpeciesAbility::FastLaneTravel) ++hops;
    return std::max(1, std::min(3, hops));
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
        } else if (act == DipAction::ProposePeace && war_[owner * Nowner_ + kPlayer]) {
            // Player accepts, always [inferred from verified numbers,
            // docs/re/diplomacy.md §1]: a proposal only fires at
            // attitude >= PROPOSE_PEACE (race range 200..530), and the
            // player's ACCEPT_PEACE is 100 — strictly below the minimum
            // proposal threshold, so any state that can propose can also
            // accept. An earlier cut proposed into the void (dead branch,
            // self-caught while wiring end-unit reachability).
            setWar(owner, kPlayer, false);
            st.atWar = false;
            events_.push_back({turn_, aiDip_[i].displayName +
                                  " proposed peace; accepted"});
        } else if (act == DipAction::BreakAlliance && war_[owner * Nowner_ + kPlayer]) {
            // already at war; nothing to break (alliance bookkeeping R1-blocked)
        } else if (act == DipAction::ProposeAlliance && !st.allied) {
            st.allied = true;
            events_.push_back({turn_, aiDip_[i].displayName + " allied with the player"});
        }
    }
}

void Campaign::abilityPhase() {
    // Turn-boundary: clear one-shot flags (vendor texts are all "this turn"
    // scoped: DoublePower "for the rest of this turn" L1945-1946, Shield
    // "invincible" + lanes until next amass; abilities.md §3 [inferred]).
    std::fill(doublePower_.begin(), doublePower_.end(), 0);
    std::fill(sapActive_.begin(), sapActive_.end(), 0);
    std::fill(invincible_.begin(), invincible_.end(), 0);
    std::fill(laneBlock_.begin(), laneBlock_.end(), 0);

    for (int o = 0; o < Nowner_; ++o) {
        const SpeciesAbility ab = ability_[o];
        if (ab == SpeciesAbility::Unknown) continue;
        if (abilityIsCharged(ab)) {
            if (--charge_[o] > 0) continue;
            charge_[o] = abilityChargeTurns(ab);
        }
        const std::string who = std::string(abilityName(ab)) + " (owner " +
                                std::to_string(o) + "): ";
        switch (ab) {
            case SpeciesAbility::SuperMarines:
            case SpeciesAbility::KnowHomeWorlds:
            case SpeciesAbility::KnowRaces:
            case SpeciesAbility::BuildOnBlack:
                break;  // passives applied at their hook sites / filed no-ops
            case SpeciesAbility::DoubleHull:
                break;  // passive: halved hull damage in combatPhase
            case SpeciesAbility::HealShips:  // help.txt L1824 "repair all damage to your ships"
                fleetDamage_[o] = 0;
                events_.push_back({turn_, who + "repaired all ships"});
                break;
            case SpeciesAbility::ForcePeace: {  // L1870-1871 "force all aliens to make peace"
                int n = 0;
                for (int e = 0; e < Nowner_; ++e)
                    if (e != o && war_[o * Nowner_ + e]) { setWar(o, e, false); ++n; }
                events_.push_back({turn_, who + (n ? "forced peace on " + std::to_string(n) + " enemies"
                                                   : "no enemies to force peace")});
                break;
            }
            case SpeciesAbility::DoublePower:  // L1917-1918 "double the power of all your ships"
                doublePower_[o] = 1;
                events_.push_back({turn_, who + "ships at double power this turn"});
                break;
            case SpeciesAbility::RepelAlienShips: {  // L1965-1966 "warp alien ships out of your colonies' stars"
                const size_t before = fleet_.size();
                fleet_.erase(std::remove_if(fleet_.begin(), fleet_.end(),
                                            [&](const ShipInTransit& sh) {
                                                return sh.owner != o && owner_[sh.target] == o;
                                            }),
                             fleet_.end());
                events_.push_back({turn_, who + "warped " + std::to_string(before - fleet_.size()) +
                                      " alien ships from colony stars"});
                break;
            }
            case SpeciesAbility::SapAlienPower:  // L2012-2013 "wipe out the power of all alien ships in systems you occupy"
                sapActive_[o] = 1;
                events_.push_back({turn_, who + "sapping alien hulls in occupied systems"});
                break;
            case SpeciesAbility::Cornucopia: {  // L2059-2060 "turn your least populated colony into a rich world"
                int best = -1;
                for (size_t s = 0; s < galaxy_.stars.size(); ++s)
                    if (owner_[s] == o && planets_[s].pop > 0 &&
                        (best < 0 || planets_[s].pop < planets_[best].pop))
                        best = static_cast<int>(s);
                if (best >= 0) {
                    planets_[best].richPros += 2;  // Agriplot PROS=2 [verified planitem.txt]
                    events_.push_back({turn_, who + "enriched " + galaxy_.stars[best].name});
                }
                break;
            }
            case SpeciesAbility::BumpShipsInLanes: {  // L2106-2107 "bump all ships in star lanes backward to their stars of origin"
                const size_t bumped = fleet_.size();
                fleet_.clear();  // returned ships = no longer in transit (model has no idle fleets)
                events_.push_back({turn_, who + "bumped " + std::to_string(bumped) +
                                      " ships out of the lanes"});
                break;
            }
            case SpeciesAbility::StealResearch: {  // L2154-2155 "steal any technology known by at least two other races"
                int n = 0;
                for (size_t t = 0; t < tree_->all().size(); ++t) {
                    if (ownedTech[o][t]) continue;
                    int holders = 0;
                    for (int e = 0; e < Nowner_; ++e)
                        if (e != o && ownedTech[e][t]) ++holders;
                    if (holders >= 2) { ownedTech[o][t] = true; ++n; }
                }
                events_.push_back({turn_, who + "stole " + std::to_string(n) +
                                      " shared technologies"});
                break;
            }
            case SpeciesAbility::ShieldPlanets: {  // L2201-2202 "all your colonies invincible for one day"
                int n = 0;
                for (size_t s = 0; s < galaxy_.stars.size(); ++s)
                    if (owner_[s] == o) { invincible_[s] = 1; ++n; }
                events_.push_back({turn_, who + std::to_string(n) + " colonies invincible"});
                break;
            }
            case SpeciesAbility::MoreMaxPop: {  // L2248-2249 "increase the maximum population of all your colonies"
                for (size_t s = 0; s < galaxy_.stars.size(); ++s)
                    if (owner_[s] == o) planets_[s].capBonus += 25;  // [documented default]
                events_.push_back({turn_, who + "raised colony pop caps"});
                break;
            }
            case SpeciesAbility::KnowStarLanes:
                break;  // passive (no amass line, L2295 block); filed no-op —
                        // the sim has no fog of war (see abilities.md §2)
            case SpeciesAbility::BlockStarLanes: {  // L2314-2315 "block all star lanes entering your colonized systems"
                int n = 0;
                for (size_t s = 0; s < galaxy_.stars.size(); ++s)
                    if (owner_[s] == o) { laneBlock_[s] = 1; ++n; }
                events_.push_back({turn_, who + "blocked lanes into " + std::to_string(n) + " stars"});
                break;
            }
            case SpeciesAbility::CauseWar: {  // L2361-2362 "alien species to strongly dislike any species at war with you"
                // PARTIAL [documented, abilities.md §2]: the dip model carries
                // one attitude vector (AI -> player); AI-vs-AI relationships
                // do not exist (R1-blocked). Wired here: races at war with the
                // Marmosians have their player-facing attitude reduced by 250
                // (strong dislike scale vs START_ATTITUDE 310..620) and the
                // effect is announced; third-party redirect is a no-op.
                int n = 0;
                for (int e = 1; e < Nowner_; ++e)
                    if (e != o && war_[o * Nowner_ + e] && dipState_[e - 1].attitude > -1000) {
                        dipState_[e - 1].attitude -= 250;
                        ++n;
                    }
                events_.push_back({turn_, who + std::to_string(n) +
                                      " belligerents marked for dislike"});
                break;
            }
            case SpeciesAbility::FastLaneTravel:
                break;  // passive: +1 launch hop in driveHopsFor
            case SpeciesAbility::FreeResearch: {  // L2429-2430 "immediately achieve any discovery you are pursuing"
                int t = queuedTech[o];
                if (t < 0) {
                    auto avail = tree_->available(ownedTech[o], /*includeVariants=*/false);
                    t = -1;
                    for (int c : avail)
                        if (t < 0 || tree_->all()[c].runtimeCost() < tree_->all()[t].runtimeCost()) t = c;
                }
                if (t >= 0 && !ownedTech[o][t]) {
                    ownedTech[o][t] = true;
                    events_.push_back({turn_, who + "completed " + tree_->all()[t].name});
                } else {
                    events_.push_back({turn_, who + "nothing pending to complete"});
                }
                queuedTech[o] = -1;
                techProgress[o] = 0;
                break;
            }
            case SpeciesAbility::IndustryBoost:  // L2476-2477 "boost the progress on all your colonies' projects"
                ind_[o] += 20;  // = 2 Factory-costs [planitem Factory cost; documented default]
                events_.push_back({turn_, who + "boosted construction (+20 IND)"});
                break;
            case SpeciesAbility::kCount:
            case SpeciesAbility::Unknown:
                break;
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
            bool ok = requiresAvailable(g.resReq, static_cast<int>(tree_->all().size()),
                                        ownedTech[owner]);
            if (ok) wlvl = std::max(wlvl, g.level);
        }
    }
    // SA_SapAlienPower / SA_HealShips semantics: fleetDamage_ IS the sapped
    // "power" (abilities.md §2) — subtracted from fleet strength until
    // repaired. Floor at 0 keeps a sapped empire able to defend its homes.
    return std::max(0, static_cast<int>(pop / 10.0) + wlvl - fleetDamage_[owner]);
}

int Campaign::defenseScore(int owner, int star) const {
    // [inferred] local pop /10 + best owned SHIELD level (1..5 [verified])
    // + terrain/fortify 2.
    double pop = planets_[star].pop;
    int slvl = 0;
    if (gizmos_) {
        for (const Gizmo& g : *gizmos_) {
            if (g.cat != GizmoCat::Shield) continue;
            bool ok = requiresAvailable(g.resReq, static_cast<int>(tree_->all().size()),
                                        ownedTech[owner]);
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
    // SA_SapAlienPower (help.txt L2012 "wipe out the power of all alien ships
    // in systems you occupy"): enemies owning stars adjacent to the Shevar's
    // stars take a power hit this combat — THE ONLY fleetDamage source (a
    // generic capture-damage channel was tried first and self-caught: it
    // starved every non-healing empire into death spirals and turned all
    // eight checked PLAYTHROUGH seeds Extinct; the vendor has no empire-wide
    // hull-damage pool — docs/re/abilities.md §2). Magnitude 15 is a
    // documented default (abilities.md §3); SA_DoubleHull ("double-strength
    // hulls", L1743) halves it.
    for (int o = 0; o < Nowner_; ++o) {
        if (!sapActive_[o]) continue;
        for (size_t s = 0; s < galaxy_.stars.size(); ++s) {
            if (owner_[s] != o) continue;
            for (int nb : galaxy_.neighbours(static_cast<int>(s))) {
                const int e = owner_[nb];
                if (e >= 0 && e != o && war_[o * Nowner_ + e]) {
                    const int amt = ability_[e] == SpeciesAbility::DoubleHull ? 8 : 15;
                    fleetDamage_[e] += amt;
                }
            }
        }
    }
    std::uniform_int_distribution<int> noise(0, 10);
    // SA_SuperMarines: "your planetary invasions will always succeed"
    // (L1723) — an ATTEMPT guarantee, not a multi-capture per turn, and an
    // attempt still means ships: invasions charge the hull cost (planitem
    // Ship 20, ships.md §1) and skip when the economy can't spare it.
    // Without that gate the Minions took one free star per border per turn
    // and exterminated every race by ~t170 on all eight checked seeds
    // (self-caught: PLAYTHROUGH Control runs vanished). Cap: one always-
    // success invasion per owner per turn. [documented default, abilities.md §2]
    const int shipCostC = [&] {
        int id = itemId("Ship");
        return id < 0 ? 20 : (*items_)[id].cost;
    }();
    std::vector<char> superUsed(Nowner_, 0);
    for (size_t s = 0; s < galaxy_.stars.size(); ++s) {
        const int a = owner_[s];
        if (a < 0) continue;
        for (int nb : galaxy_.neighbours(static_cast<int>(s))) {
            const int b = owner_[nb];
            if (b < 0 || b == a || !war_[a * Nowner_ + b]) continue;
            if (invincible_[nb]) continue;             // SA_ShieldPlanets (L2201)
            if (!lanePassable(a, nb)) continue;        // SA_BlockStarLanes (L2314)
            if (fortify_[nb] > 0) continue;
            if (invadesAlwaysSucceeds(a) && (superUsed[a] || ind_[a] < shipCostC))
                continue;
            // RNG DISCIPLINE: exactly two draws per evaluated border pair, in
            // the pre-abilities order (atk noise, def noise). Ability branch
            // logic must never add or skip draws — an earlier cut did, and the
            // whole campaign stream silently diverged by t195 while t40 still
            // matched (self-caught by head-vs-work diff bisection).
            int atk = attackScore(a) + noise(rng_);
            int def = defenseScore(b, nb) + noise(rng_) / 2;
            if (doublePower_[a]) atk *= 2;             // SA_DoublePower (L1917, "this turn")
            if (invadesAlwaysSucceeds(a)) {            // SA_SuperMarines (L1723 always succeed)
                ind_[a] -= shipCostC;                  // the invasion ships
                superUsed[a] = 1;
            } else if (atk <= def) {
                continue;
            }
            owner_[nb] = a;
            planets_[nb].pop = 10;  // settlement seed (turnloop.md §5)
            fortify_[nb] = 2;
            events_.push_back({turn_, "owner " + std::to_string(a) + " captured " +
                                  galaxy_.stars[nb].name});
            break;
        }
    }
}

Victory Campaign::checkVictory() const {
    const int total = static_cast<int>(galaxy_.stars.size());
    const int mine = starsOwned(kPlayer);
    const bool fleetPending = std::any_of(fleet_.begin(), fleet_.end(),
                                          [&](const ShipInTransit& x) { return x.owner == kPlayer; });
    if (mine == 0 && turn_ > 0 && !fleetPending) return Victory::Extinct;  // end-xtnc
    // ORDER [documented choice, turnloop.md §1 — vendor priority unknown]:
    // Extinct (with its fleetPending wait, above) > LastAlive > Captured >
    // Unification > Control; each earlier condition is strictly more
    // specific. Do NOT re-add a mine==0 Extinct check below: while a player
    // colony ship is still in transit it can colonise next turn (that is
    // what the fleetPending wait above exists for; self-caught).
    int alive = 0, last = -1, aliveAi = 0, aiAllied = 0;
    for (int o = 0; o < Nowner_; ++o) {
        if (starsOwned(o) <= 0) continue;
        ++alive; last = o;
        if (o != kPlayer) {
            ++aliveAi;
            if (dipState_[o - 1].allied) ++aiAllied;
        }
    }
    if (alive == 1 && last == kPlayer) return Victory::LastAlive;           // end-dest
    // end-capt: "Player captured all home worlds" [verified comment]. The
    // home world is the star fixed at setup (homeStar_), not "any star the
    // race ever owned".
    bool allHomesMine = cfg_.aiCount > 0 && mine > 0;
    for (size_t o = 1; allHomesMine && o < homeStar_.size(); ++o)
        if (homeStar_[o] >= 0 && owner_[homeStar_[o]] != kPlayer) allHomesMine = false;
    if (allHomesMine) return Victory::Captured;
    // end-unit: "Galaxy under one alliance, player alive" [verified
    // comment]. Player-relative reading [documented, turnloop.md §1]: every
    // live AI allied to the player and no player-AI war bit. AI-vs-AI wars
    // are deliberately NOT part of the test — the diplomacy model has no
    // AI-AI relations at all (OQ-020/abilities.md), so only player-relative
    // "one alliance" is internally expressible; the FFA arcade default's
    // AI-AI bits are a documented setup artifact, not vendor semantics.
    bool playerAtWar = false;
    for (int o = 1; o < Nowner_ && !playerAtWar; ++o)
        if (starsOwned(o) > 0 && war_[kPlayer * Nowner_ + o]) playerAtWar = true;
    if (aliveAi > 0 && aiAllied == aliveAi && !playerAtWar)
        return Victory::Unification;
    if (mine * 2 > total) return Victory::Control;  // end-ctrl (OQ-021: "> half" vs prose "two-thirds")
    return Victory::None;
}

Victory Campaign::advance() {
    if (over()) return victory_;
    ++turn_;
    abilityPhase();  // species abilities fire first (docs/re/abilities.md §3)
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
    if (ability_[kPlayer] != SpeciesAbility::Unknown)
        out += std::string(" | SA ") + abilityName(ability_[kPlayer]);
    return out;
}

}  // namespace ascend::game
