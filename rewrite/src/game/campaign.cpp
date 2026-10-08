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

}  // namespace

double colonyChannel(int acc, bool firstDoubleActive, bool compress) {
    if (acc == 0) return kColonyIncomeGrant;  // grant survives recalc JZ-skip
    int v = acc + (firstDoubleActive ? acc >> 1 : 0);
    if (!compress) return static_cast<double>(v);
    return std::floor(std::pow(static_cast<double>(v + 1), 0.85));
}

namespace {

// Planet SIZE classes map onto grid-C surface-cell counts {7,11,23,45,73};
// the rewrite's mapgen does not yet assign per-star size classes (parking
// lot, STATE.md), so builds are capped with the MEASURED class-2 default.
// (kDefaultSizeClass retired t29: every star now carries its OWN seeded
// surfaceCells + capBase per the world-gen seed law, income-law.md S10.)

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
    // WORLD-GEN POP-CAP SEED (income-law.md S10 t29): per planet the cell
    // loop draws rng(0..99) < w0 -> barren (w0 = preset row [0] at runtime
    // 0x744f4, MEASURED table {100,50,20,0,40,20,40,20,40,20,0}); non-barren
    // surface cells counted; seed word = count/3 + 5 written to +0x55 AND
    // +0x4a (@0x37f84..0x37f9e). Preset-per-planet assignment comes from the
    // scenario template (open residue; measured near-uniform 0..10 over 151
    // planets, so uniform draw [documented default]). Binomial law
    // reproduces the measured per-size ranges {5..7,5..8,5..12,5..20,5..29}.
    {
        static const int kBarrenW[11] = {100, 50, 20, 0, 40, 20, 40, 20, 40, 20, 0};
        std::uniform_int_distribution<int> presetDraw(0, 10);
        std::uniform_int_distribution<int> cellDraw(0, 99);
        std::uniform_int_distribution<int> sizeDraw(0, 4);
        for (int s = 0; s < n; ++s) {
            const int preset = presetDraw(rng_);
            const int cells = planetSurfaceCells(sizeDraw(rng_));
            planets_[s].surfaceCells = cells;  // +0x18 analog
            int nonbarren = 0;
            for (int c = 0; c < cells; ++c)
                if (cellDraw(rng_) >= kBarrenW[preset]) ++nonbarren;
            planets_[s].capBase = nonbarren / 3 + 5;  // @0x37f8b..0x37f9e
        }
    }
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

int Campaign::popCapFor(int star) const {
    // +0x4a public accessor — now the MEASURED seed law (S10 t29), not the
    // old cfg_.popCap default. cfg_.popCap remains only as a legacy field.
    return storedCapFor(star);
}

int Campaign::storedIndFor(int star) const {
    // S6 recalc IND channel (income-law.md §6): raw IND sum + Hyperpower
    // doubling (v + v>>1), compressed trunc((v+1)^0.85); grant 1 at acc 0
    // (t19). Same law incomeAndGrow charges into the empire budget.
    int acc = 0;
    bool dbl = false;
    const int idHyper = itemId("Hyperpower Plant");
    for (int it : planets_[star].items) {
        acc += (*items_)[it].ind;
        if (it == idHyper) dbl = true;
    }
    return static_cast<int>(colonyChannel(acc, dbl, /*compress=*/true));
}

int Campaign::storedResFor(int star) const {
    // RES channel: raw accumulator + Internet doubling, never compressed (S6).
    int acc = 0;
    bool dbl = false;
    const int idNet = itemId("Internet");
    for (int it : planets_[star].items) {
        acc += (*items_)[it].res;
        if (it == idNet) dbl = true;
    }
    return static_cast<int>(colonyChannel(acc, dbl, /*compress=*/false));
}

int Campaign::storedProsFor(int star) const {
    // PROS accumulator as the growth counter spends it (income-law.md S6c):
    // raw item PROS + rich-world ability bonus. Upkeep (MPOP sum /4) is NOT
    // deducted here — incomeAndGrow measured growth deltas against the RAW
    // sum (chase capture 06e: +3 == stored PROS 3), so the rewrite's growth
    // path consumes this value verbatim.
    double pros = planets_[star].richPros;
    for (int it : planets_[star].items) pros += (*items_)[it].pros;
    return static_cast<int>(pros);
}

int Campaign::storedCapFor(int star) const {
    // +0x4a analog (income-law.md S10 t29): recalc head reads capBase
    // (+0x55) raw, the item loop adds MPOP, the tail clamps 0..100
    // (@0x38f01..0x38f18). MPOP sum skips items with flags&4 (measured rows
    // 17/28/29/30) AND Colony Base (S10 residual derivation: including its
    // +2 produced EXACTLY -2 residuals on every Colony-Base-active planet).
    // capBonus keeps SA_MoreMaxPop [documented default; the original's
    // ability site is not yet lifted].
    const PlanetState& ps = planets_[star];
    const int cb = itemId("Colony Base");
    int mpopSum = 0;
    for (int it : ps.items) {
        if (it == cb) continue;
        const PlanetItem& pi = (*items_)[it];
        if (pi.flags & 4) continue;
        mpopSum += pi.mpop;
    }
    int cap = ps.capBase + mpopSum;
    if (cap < 0) cap = 0;
    if (cap > 100) cap = 100;
    return cap + static_cast<int>(ps.capBonus);
}

int Campaign::needClassFor(int star) const {
    // FUN_0003fec4 verbatim (income-law.md S9 t28). EAX field analogues:
    // +0x44 IND, +0x46 RES, +0x48 PROS, +0x42 pop, +0x4a cap, +0x4c pending.
    const PlanetState& ps = planets_[star];
    const int ind = storedIndFor(star);
    const int res = storedResFor(star);
    const int pros = storedProsFor(star);
    const int capMinusPop = storedCapFor(star) - static_cast<int>(ps.pop);
    const int popMinusPend = static_cast<int>(ps.pop) - (ps.pendingItem >= 0 ? (*items_)[ps.pendingItem].upop : 0);
    if (capMinusPop < 2 && popMinusPend < 2) return 3;  // 0x3fedc
    if (pros < 2) return 2;                              // 0x3fef2
    if (ind < 2) return 1;                               // 0x3ff0f
    if (ind >= 4 && pros >= 2) {
        // 0x3ff49: if 50/PROS > 15 (PROS < 4 impossible here since PROS>=2;
        // PROS==3 -> 16 > 15) AND cap-pop > 3 AND pop-pending != 1 -> 2.
        if (pros > 0 && 50 / pros > 15 && capMinusPop > 3 && popMinusPend != 1)
            return 2;                                    // 0x3ff80
        // 0x3ffba race-mask gate skipped (tail byte == 0 in every capture,
        // S9): item12(Hyperpower) slot -> RES-side += IND>>1; item14
        // (Internet) slot -> IND-side += RES>>1; pick the bigger side.
        int indSide = ind, resSide = res;
        const int h = itemId("Hyperpower Plant"), n = itemId("Internet");
        for (int it : ps.items) {
            if (it == h) resSide += ind >> 1;
            if (it == n) indSide += res >> 1;
        }
        return indSide > resSide ? 1 : 0;                // 0x40002/0x40006
    }
    return 0;
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
        // PROS channel: raw accumulator + ability bonus (stored value is
        // compressed-then-upkeep-deducted in the original, income-law.md S6;
        // the empire budget does not spend PROS, only growth does below).
        double pros = planets_[s].richPros;
        for (int it : planets_[s].items) pros += (*items_)[it].pros;
        // POP GROWTH — MEASURED counter law (docs/re/income-law.md S6c+S6e;
        // decisive capture r1deep-20261007-224831 slots 45->46: counter
        // 48 -> wrap -> 0 with pop +1 on four AI colonies simultaneously).
        // FUN_00038f68 @0x392f4: gate upkeep < cap (else counter reset);
        // @0x39302: counter += stored PROS; @0x39319: +1 more when owner !=
        // current-turn player AND PROS < 4 (unmeasured [verified disasm,
        // @0x3933b: at counter >= 50 (DAT_000066e4) pop += 1,
        // counter := 0. The +1-extra bonus is an ACTIVE CLONING PLANT
        // (CORRECTED t27: raw disasm 0x393ad MOV EDX,0xf = item 15, slot
        // finder FUN_0003958c takes itemIdx in EDX — the old "Hyperpower"
        // reading used the wrong literal; income-law.md S6b/S8). The
        // rewrite's item list has no slot order, so active-ness maps to
        // "item is built" [inferred mapping].
        bool hasClone = false;
        for (int it : planets_[s].items)
            if (it == itemId("Cloning Plant")) hasClone = true;
        PlanetState& ps = planets_[s];
        const int cap = storedCapFor(s);  // storedCapFor already folds capBonus
        if (ps.pop < cap) {
            ps.growthCounter += static_cast<int>(pros);
            if (o != kPlayer && pros < 4) ps.growthCounter += 1;
            if (ps.growthCounter >= 50) {  // DAT_000066e4 [verified value]
                ps.pop += 1 + (hasClone ? 1 : 0);
                if (ps.pop > cap) ps.pop = cap;
                ps.growthCounter = 0;
            }
        } else {
            ps.growthCounter = 0;  // upkeep >= cap resets @0x393f9
        }
    }
    for (size_t i = 0; i < income.size(); ++i) ind_[i] += income[i];  // stockpile
    // SCALE NOTE (t24): pop fields now carry ORIGINAL dot units (colonise
    // :=2, cap 13..28 — income-law.md S6e). The combat read sites below
    // (pop/10 fleet + local defense) were calibrated on the v1 0..100
    // logistic; original combat scaling is its own open item (OQ-017
    // family), so the divisor stays a documented default rather than a
    // silently re-fudged constant.
    // Fleet "power" regens at 5/turn once sapped [documented default,
    // abilities.md §3 — no data exposes a repair rate or its precondition].
    for (int o = 0; o < Nowner_; ++o) {
        if (fleetDamage_[o] <= 0) continue;
        fleetDamage_[o] = std::max(0, fleetDamage_[o] - 5);
    }
}

void Campaign::buildPhase() {
    // BUILD-QUEUE + SELECTOR LAW (income-law.md S8 + S9 t28), replacing the
    // v1 instant-buy-from-stockpile default. Mechanics, each cited:
    //  * Queue capacity 1 per planet (+0x52/+0x54 single pair). The per-turn
    //    tick pays stored IND into the accumulator ONLY while pending
    //    (FUN_00038f68 0x39005: +0x54==0xFF jumps the accumulator block);
    //    completion at acc >= COST(item) (0x390a3 call 0x394d8 / JA 0x392a2),
    //    then +0x50 resets (0x3929a).
    //  * The AI selector (FUN_0003f130) runs ONLY on planets with no pending
    //    item (caller law 0x3ead6) and requires stored IND > 0 (0x3f146).
    //  * Candidates: surface rows 0..21, Colony Base row 5 excluded,
    //    research-gated per S4, UPOP gate popCap - pendingUPOP >= UPOP(new)
    //    (0x3f574/0x3f587) AND buy legality pop - pendingUPOP >= UPOP(new)
    //    (cmd0 0x388f7..0x38922).
    //  * Pick law (0x3f672..0x3f733): first candidate NOT already built wins
    //    IMMEDIATELY, unless COST/storedIND >= 70, which ABORTS the scan
    //    keeping the best already-built candidate (score = need-class column
    //    FUN_0003fec4, 65% full-sum / 35% primary roll @0x3f6fb).
    // Planet builds never touch the empire IND stockpile (payment is the
    // per-planet accumulator, S8); ind_ remains the ship-launch budget only.
    // Player planets: the original is UI-driven (no auto selector); the
    // rewrite keeps kBuildOrder as the pick policy under the SAME queue law
    // [documented default].
    for (size_t s = 0; s < galaxy_.stars.size(); ++s) {
        int o = owner_[s];
        if (o < 0) continue;
        PlanetState& ps = planets_[s];
        const PlanetItem* pend = ps.pendingItem >= 0 ? &(*items_)[ps.pendingItem] : nullptr;
        // --- tick (FUN_00038f68 0x3907b) ---
        if (pend) {
            ps.buildAcc += storedIndFor(s);
            if (ps.buildAcc >= pend->cost) {
                ps.items.push_back(ps.pendingItem);
                // LUSH GROWTH BOMB completion (income-law.md S10): governor
                // byte == item 37 && !(+0x66&1) -> capBase += 10 once, flag
                // set (@0x39212..0x39229).
                if (ps.pendingItem == itemId("Lush Growth Bomb") && !ps.growthBoom) {
                    ps.capBase += 10;
                    ps.growthBoom = 1;
                }
                ps.pendingItem = -1;
                ps.buildAcc = 0;
            }
            continue;  // selector never runs on a planet with a queue
        }
        // --- selector (FUN_0003f130) ---
        int ind0 = storedIndFor(s);
        if (ind0 <= 0) continue;  // 0x3f146
        int usedPop = pend ? pend->upop : 0;  // +0x4c analogue (queue draw)
        const bool aiPick = (o != kPlayer);
        int pick = -1;
        if (!aiPick) {
            for (const BuildStep& step : kBuildOrder) {
                int have = 0;
                for (int it : ps.items)
                    if ((*items_)[it].name == step.name) ++have;
                if (have >= step.want) continue;
                int id = itemId(step.name);
                if (id < 0) continue;
                const PlanetItem& pi = (*items_)[id];
                if (pi.upop > storedCapFor(s) - usedPop) continue;  // 0x3f574
                if (pi.upop > ps.pop - usedPop) continue;        // cmd0 gate
                if (!requiresAvailable(pi.requires, static_cast<int>(tree_->all().size()),
                                       ownedTech[o]))
                    continue;
                pick = id;
                break;
            }
        } else {
            const int needClass = needClassFor(s);
            int bestScore = 0, bestItem = -1;
            // roll law 0x3f6fb: rng%100 > 65 -> full-sum score, else primary
            std::uniform_int_distribution<int> pct(0, 99);
            const bool useSum = pct(rng_) > 65;
            for (int id = 0; id < 22 && id < static_cast<int>(items_->size()); ++id) {
                if (id == 5) continue;  // Colony Base excluded 0x3f52d
                const PlanetItem& pi = (*items_)[id];
                if (!requiresAvailable(pi.requires, static_cast<int>(tree_->all().size()),
                                       ownedTech[o]))
                    continue;  // S4 research law
                if (pi.upop > storedCapFor(s) - usedPop) continue;  // 0x3f587
                bool built = false;
                for (int it : ps.items)
                    if (it == id) { built = true; break; }
                if (!built) {
                    if (pi.cost >= 70 * ind0) break;  // ABORT scan 0x3f6ee
                    pick = id;                        // immediate pick 0x3f6f0
                    break;
                }
                int col = 0;
                switch (needClass) {  // stub columns (income-law.md S9)
                    case 0: col = pi.ind; break;
                    case 1: col = pi.res; break;
                    case 2: col = pi.pros; break;
                    default: col = pi.mpop; break;
                }
                int score = useSum ? (pi.ind + pi.res + pi.pros + pi.mpop) : col;
                if (score > bestScore) {  // strict > 0x3f713 (jle keeps first)
                    bestScore = score;
                    bestItem = id;
                }
            }
            if (pick < 0 && bestItem >= 0) pick = bestItem;  // scan end w/ built-best
        }
        if (pick < 0) continue;
        if (itemIsSurface(pick)) {
            int surface = 0;
            for (int it : ps.items)
                if (itemIsSurface(it)) ++surface;
            if (surface >= ps.surfaceCells) continue;  // +0x18 seeded per S10
        }
        ps.pendingItem = pick;
        ps.buildAcc = 0;
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
            planets_[sh.target].pop = 2;  // settlement seed :=2 MEASURED (income-law.md S6e)
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
            planets_[nb].pop = 2;  // settlement seed :=2 MEASURED (income-law.md S6e)
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
