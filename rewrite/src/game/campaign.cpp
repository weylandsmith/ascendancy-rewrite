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
    if (acc == 0 && compress) return kColonyIncomeGrant;  // IND-only grant
    // (t19; IND-at-acc-0 is UNOBSERVABLE in captures — no owned planet ever
    // has zero items — so the grant survives for the compressed channel.
    // The uncompressed RES channel has NO grant: home worlds have acc 0 and
    // +0x46 == 0 on 157/157 homes, t40 census; T34's raw-accumulator law
    // 2720/2720 already implies this — the old grant here was a v1 default
    // the battery never discriminated because its records all had items.)
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
    // WORLD-GEN TERRAIN LAW (income-law.md S10 + T36): per planet the
    // original draws size = rng%5 (call-site 0x23a86 IDIV 5) and weight row
    // = rng%11 (0x23a97 IDIV 11; special scenario mode 0x23aaa..0x23ac2
    // overwrites BOTH from the 21-dword tables — normal mode is the law).
    // 0x37d80 header: size clamp min(,4) @0x37dcd, surfaceCells = sum of
    // 15 table bytes 0x744a8[15*size..] @0x37de3, +0x1a = +0x18+10
    // @0x37e23, row clamp >=0xb -> 2 @0x37e39. Class draw loop
    // @0x37eb7..0x37f24 per surface cell: rng (0..32767, FUN_0007824f) is
    // scaled ONCE w -> (w*32768-w)/100 (@0x37e55 SHL 0xF; SUB; DIV 100);
    // cumulative chain rng<s1 -> 2, <s2 -> 3, <s3 -> 4, else 1; then
    // rng<s0 -> 0 BARREN @0x37f22/24 (0x37ec0 sets 2 BEFORE that test, so
    // barren overrides class 2). Orbital cells i >= surfaceCells take
    // class 1 @0x37f12 WITHOUT drawing (rng survives). Row histogram on
    // all 11 measured rows matches these shares within sampling noise
    // (T36 battery, first saves 77k surface cells). Seed word
    // capBase = nonbarren/3 + 5 into +0x55/+0x4a @0x37f84..0x37f9e.
    // banked LCG (FUN_0007824f, income-law.md S10 t29b): state =
    // state*0x41C64E6D + 0x3039; value = (state >> 16) & 0x7fff. ONE stream
    // (member worldLcg_, advanced by worldNext()) serves the terrain draw,
    // the t40 home-CB placement AND the t41 colonised-planet CB grant; it
    // never touches the campaign rng_ sequence (REFUTED-ROUTES RNG
    // discipline). Initial state := cfg.seed [inferred; the original's
    // seed-injection path is unmeasured].
    worldLcg_ = static_cast<uint32_t>(cfg.seed);
    auto next = [this]() { return worldNext(); };
    {
        // t294 (OQ-016 residue 3 CLOSED): the rows below are NO LONGER a
        // hardcoded vendor constant — cfg_.terrain comes from
        // loadTerrainTables(planitem.txt) where data is available (the
        // original's ONLY source: 0x744f4 is past the initialised data
        // segment and the loader @0x3805f is the image's sole writer). The
        // CampaignConfig default remains the measured vendor table so
        // no-data harnesses keep identical behaviour.
        const int (&kRows)[11][4] = cfg_.terrain.weights;  // 0x744f4 analog
        // +0x18 surface counts per size class: grid C row SUMS (file values
        // per-byte MEASURED t294; the original sums 15 bytes @0x37de3).
        const int (&kSurfaceBySize)[5] = cfg_.terrain.surfaceBySize;
        for (int s = 0; s < n; ++s) {
            const int size = next() % 5;  // rng%5 @0x23a86/95
            const int row = next() % 11;  // rng%11 @0x23a97/aa8
            planets_[s].terrainRow = row;  // +0x16 analog (t281: read by the
                                           // SA_Cornucopia skip; see PlanetState)
            const int cells = kSurfaceBySize[size];  // +0x18 analog
            planets_[s].surfaceCells = cells;
            auto scaled = [](int w) { return (w * 32768 - w) / 100; };
            const int lim[4] = {scaled(kRows[row][0]), scaled(kRows[row][1]),
                                scaled(kRows[row][2]), scaled(kRows[row][3])};
            const int s1 = lim[0] + lim[1], s2 = s1 + lim[2], s3 = s2 + lim[3];
            auto& cls = planets_[s].cellClasses;
            cls.assign(cells + 10, 1);  // orbital ring is class 1, no draw
            int nonbarren = 0;
            for (int c = 0; c < cells; ++c) {
                const int r = next();  // one draw per SURFACE cell
                // Equivalent mapping to the original's execution order
                // (rng -> barren pre-test @0x37f20 -> chain @0x37eb7 on
                // JGE; addresses run out of order): chain picks 2/3/4/1,
                // and r < lim[0] forces the barren store 0 @0x37f24 —
                // exactly what the original's pre-test yields, incl. the
                // non-barren count (barren path skips INC ECX @0x37ebb).
                int k = r < s1 ? 2 : (r < s2 ? 3 : (r < s3 ? 4 : 1));
                if (r < lim[0]) k = 0;
                cls[c] = k;
                if (k) ++nonbarren;
            }
            // ROCK EVENT @0x37f4d [verified disasm, banked S10; ORDER is
            // after the draw loop, before the seed word @0x37f84]: one
            // rng%7 draw per PLANET (income-law.md T38: 1-rock on
            // 12244/12264 rock planets = 99.8%, rock planets 16.9% ~ 1/7
            // — per-cell draws would give ~99.9% multi-rock). If it hits,
            // cls[rng % surfaceCells] |= 8 and planet flag +0x66 |= 2.
            // Rock semantics [verified T38]: items NEVER occupy a |8 slot
            // (0 of 3192 active slots corpus-wide); builds SKIP rock cells
            // (350 mid-game-event holes below the build prefix + zero |8
            // item bytes ever); strict class equality in FUN_00038ba4
            // (~0x38bf0: CMP 2/3/4) means a |8 byte forfeits the class
            // bonus; +0x1c = empty NON-rock surface count (71762/72066).
            // capBase is NOT recomputed after the rock mark (the draw
            // loop's nonbarren counter predates it @0x37ebb) [verified by
            // the T36 first-save seed law holding with |8-stripped count].
            if (next() % 7 == 0) {  // [ESP+rng] idiv 7, test EDX @0x37f5c
                cls[next() % cells] |= 8;  // +0x66 |= 2 [t201: IS consumed —
                                           // emergency chain A (0x3fc57) buys
                                           // the Xeno dig off this bit;
                                           // digQueuedOrDone is the model]
                planets_[s].digQueuedOrDone = 1;
            }
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
    attacked_.assign(galaxy_.stars.size(), 0);  // [0x48304] per-star array (t205)
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
    charge_.assign(Nowner_, 0);  // count-up == original row+0x19e (t100):
    // scenario init counter 0, first fire exactly cadence word turns in.
    // (Old t30 model pre-loaded a full countdown — replaced by the measured
    // cadence law, docs/re/aicode.md §6.4.)
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
    // OQ-026 visibility seed (after homes exist; masks per ships.md S23 L5
    // + L9, seeding law per L6/L7 witnesses — see seedVisibility()).
    laneVis_.assign(galaxy_.lanes.size(), 0);   // rec+0x20 analog, zeroed
                                                // like pool-create 0x248ab
    starLaneVis_.assign(galaxy_.stars.size(), 0);
    starSelVis_.assign(galaxy_.stars.size(), 0);
    contacted_.assign(Nowner_ * Nowner_, 0);
    visLcg_ = static_cast<uint32_t>(cfg.seed) ^ 0x5eedu;  // own stream; the
                                    // original's share-rng identity is
                                    // unmapped [unverified], so it provably
                                    // cannot perturb campaign rng_ draws
    seedVisibility();
    for (int s = 0; s < n; ++s) {
        if (owner_[s] >= 0) planets_[s].pop = cfg_.initialPop;
    }
    // Opening position on every home: COLONY BASE ONLY, pop 2, CB UNIFORM
    // over the planet's NON-ROCK surface cells (barren INCLUDED). LAW CLOSED
    // t42 by raw disasm + census (income-law.md T42): home seed
    // FUN_000238e8 @0x23ca2 calls FUN_00038818 with EBX=0xffff (no slot) ->
    // picker FUN_0003875c (collect checker-legal empty slots, ONE rng %
    // count). Checker FUN_0003830c never zeroes legality for item 5 on a
    // surface non-rock cell (rule B's barren path enters rule C, which
    // SKIPS zeroing for item 5; only rock and orbital placement zero).
    // Census scripts/r1_cell_choice_census.py + r1_cb_rank_final.py: 19/72
    // (26%) turn<=1 home CBs on barren ~ terrain barren rate; zero CB on
    // rock in 2810 corpus CB cells; KS PASS uniform (D=0.085, crit 0.192).
    // t40's barren-exclusion is SUPERSEDED by the rule chain; the t40
    // rank>=2 floor is NOT refuted by data (rank<2 0/72, uniform-expected
    // 2.6, p~0.07) but has NO code counterpart — uniform draw per disasm.
    // Factory/Lab/Shipyard never on a first-save home (t40) — v1 seeding
    // stays RETIRED. The CB cell class feeds the channel words (T40).
    // Constructor opening-research grant unmeasured — banked open.
    for (int s = 0; s < n; ++s) {
        if (owner_[s] < 0) continue;
        int b = itemId("Colony Base");
        if (b < 0) continue;
        auto& ps = planets_[s];
        ps.items.push_back(b);
        ps.itemCells.push_back(drawCbCell(ps));
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

// ---------------------------------------------------------------------------
// OQ-026 PER-EMPIRE VISIBILITY LAYER.
// Law source: docs/re/ships.md S23 — L5 (t191: lane rec+0x20 is a per-empire
// bitmask, OR-only, no lane-pool-scoped clear), L6 (t192: FUN_00046354 share
// shape + N law + caller sites), L7 (t193: mid-game multi-bit witnesses),
// L9 (t194: the CONSUMER — cosmos list builder FUN_00028fc0 lane filter
// rec+0x20 & DAT_00089324; viewer setter FUN_00021a84; star-click
// FUN_00028e70 gates on obj +0x17/+0x16).
// The layer is a DISPLAY/INTERACTION surface exactly as measured: no sim rule
// consults it (there is no cited law that fog gates the AI's moves).
// ---------------------------------------------------------------------------

int Campaign::visNext() {
    // Same FUN_0007824f form as worldNext() (income-law.md S10 t29b) on its
    // OWN state: state = state*0x41C64E6D + 0x3039, value = (state>>16)&0x7fff.
    visLcg_ = visLcg_ * 0x41C64E6Du + 0x3039u;
    return static_cast<int>((visLcg_ >> 16) & 0x7fff);
}

bool Campaign::contactSeen(int a, int b) const {
    // Rewrite-side trigger condition for the receive leg (documented default:
    // the original's per-race event loop 0x55f1b..0x55f2e has no rewrite
    // counterpart). Two empires are "in contact" when a starlane joins a star
    // each of them holds.
    for (const Lane& l : galaxy_.lanes)
        if ((owner_[l.a] == a && owner_[l.b] == b) ||
            (owner_[l.a] == b && owner_[l.b] == a))
            return true;
    return false;
}

void Campaign::seedVisibility() {
    const int nl = static_cast<int>(galaxy_.lanes.size());
    for (int o = 0; o < Nowner_; ++o) {
        const int bit = viewerMaskFor(o);
        // Own claimed stars: interaction is impossible without them (the
        // click handler would refuse to select the player's own system).
        for (size_t s = 0; s < galaxy_.stars.size(); ++s)
            if (owner_[s] == o) { starLaneVis_[s] |= bit; starSelVis_[s] |= bit; }
        // Lanes of the empire's own claim (t192 new-game law: race r's list ==
        // EXACTLY {mask == 1<<r}; t193 re-read: the list is the race's OWN
        // claimed lanes).
        for (int i = 0; i < nl; ++i)
            if (owner_[galaxy_.lanes[i].a] == o || owner_[galaxy_.lanes[i].b] == o)
                laneVis_[i] |= bit;
    }
    // SPECIES ABILITIES wired into the same mask surface the UI filter reads.
    // [documented model: the vendor's internal consumer of the two ability
    // flags is unmapped; help.txt is the effect law.]
    for (int o = 0; o < Nowner_; ++o) {
        const int bit = viewerMaskFor(o);
        if (ability_[o] == SpeciesAbility::KnowStarLanes)   // L2295 "see all star lanes"
            for (int i = 0; i < nl; ++i) laneVis_[i] |= bit;
        if (ability_[o] == SpeciesAbility::KnowHomeWorlds)  // L1783 "see all alien home stars"
            for (int e = 0; e < Nowner_; ++e)
                if (e != o && homeStar_[e] >= 0) {
                    starLaneVis_[homeStar_[e]] |= bit;
                    starSelVis_[homeStar_[e]] |= bit;
                }
    }
}

int Campaign::shareLaneVision(int a, int b, bool bidirectional, bool allied) {
    // FUN_00046354 shape (S23 L6): __regparm3 EAX=diplo row of party-1,
    // EDX=party-2 index, EBX=mode. RNG modulus 6 iff relation state == 3
    // (ALLIANCE) else 3; N = rand%mod + 1 grants per call, counters per-call.
    const int mod = allied ? 6 : 3;
    const int N = visNext() % mod + 1;
    const int maskA = viewerMaskFor(a), maskB = viewerMaskFor(b);
    const int nl = static_cast<int>(galaxy_.lanes.size());
    int n = 0;
    // Receive leg (EBX != 0 shape 0x46402): party-1 takes lanes party-2 sees.
    for (int i = 0; i < nl && n < N; ++i)
        if ((laneVis_[i] & maskB) && !(laneVis_[i] & maskA)) { laneVis_[i] |= maskA; ++n; }
    if (bidirectional) {
        // Mirrored lend leg (0x46408/0x4641c -> OR rec+0x20, DL): party-2 takes
        // lanes party-1 sees, on its OWN per-call counter.
        int m = 0;
        for (int i = 0; i < nl && m < N; ++i)
            if ((laneVis_[i] & maskA) && !(laneVis_[i] & maskB)) { laneVis_[i] |= maskB; ++m; }
        n += m;
    }
    return n;
}

void Campaign::shareStarVision(int a, int b, bool bidirectional, bool allied) {
    // FUN_00046524 (S23 L6 "star twin ... same shape", modulus 4 if state==3
    // else 2). Each twin byte is shared with its own draw [inferred].
    const int mod = allied ? 4 : 2;
    const int maskA = viewerMaskFor(a), maskB = viewerMaskFor(b);
    const int ns = static_cast<int>(galaxy_.stars.size());
    for (int which = 0; which < 2; ++which) {
        std::vector<char>& v = which ? starSelVis_ : starLaneVis_;
        const int N = visNext() % mod + 1;
        int n = 0;
        for (int i = 0; i < ns && n < N; ++i)
            if ((v[i] & maskB) && !(v[i] & maskA)) { v[i] |= maskA; ++n; }
        if (bidirectional) {
            int m = 0;
            for (int i = 0; i < ns && m < N; ++i)
                if ((v[i] & maskA) && !(v[i] & maskB)) { v[i] |= maskB; ++m; }
        }
    }
}

bool Campaign::laneVisibleTo(int lane, int viewer) const {
    if (lane < 0 || lane >= static_cast<int>(laneVis_.size())) return false;
    return (laneVis_[lane] & viewerMaskFor(viewer)) != 0;   // filter 0x2914e
}
bool Campaign::starSelectableBy(int star, int viewer) const {
    if (star < 0 || star >= static_cast<int>(starSelVis_.size())) return false;
    return (starSelVis_[star] & viewerMaskFor(viewer)) != 0; // FUN_00028e70 select
}
bool Campaign::starLaneFollowableBy(int star, int viewer) const {
    if (star < 0 || star >= static_cast<int>(starLaneVis_.size())) return false;
    return (starLaneVis_[star] & viewerMaskFor(viewer)) != 0; // FUN_00028e70 follow
}
int Campaign::visibleLaneCountFor(int viewer) const {
    int n = 0;
    for (size_t i = 0; i < laneVis_.size(); ++i)
        if (laneVisibleTo(static_cast<int>(i), viewer)) ++n;
    return n;
}
std::vector<int> Campaign::cosmosLanesFor(int viewer) const {
    // Builder lane loop: bound word[0x177d3] = nlanes, index order, kind=1
    // entry ONLY when the mask admits it (S23 L9).
    std::vector<int> out;
    for (size_t i = 0; i < laneVis_.size(); ++i)
        if (laneVisibleTo(static_cast<int>(i), viewer)) out.push_back(static_cast<int>(i));
    return out;
}
std::vector<int> Campaign::cosmosStarsFor(int viewer) const {
    // HONEST NEGATIVE (S23 L9): the builder's kind-0 star entries are added
    // UNCONDITIONALLY — the star masks are not consumed there. Every star is
    // always drawn; visibility gates CLICKS, not star drawing.
    (void)viewer;
    std::vector<int> out(galaxy_.stars.size());
    for (size_t i = 0; i < out.size(); ++i) out[i] = static_cast<int>(i);
    return out;
}

int Campaign::popCapFor(int star) const {
    // +0x4a public accessor — now the MEASURED seed law (S10 t29), not the
    // old cfg_.popCap default. cfg_.popCap remains only as a legacy field.
    return storedCapFor(star);
}

Campaign::ChannelAcc Campaign::channelAccFor(int star) const {
    // BATTERY LAW accumulator (scripts/r1_income_channels.py 173/173/173,
    // income-law.md T35): per ACTIVE filled slot add the item's channel
    // field, plus +1 class-cell bonus ONLY when that field is non-zero
    // (the +1 nests inside the field test in FUN_00038ba4 — RES proof:
    // 49 cls-4-on-res-0 slots == 49 records == 49 pre-fix failures).
    // Cell lookup from T36b PLACEMENT + T38 ROCK-SKIP [verified]: items
    // are prefix-packed over NON-ROCK surface cells in slot order
    // (surface contiguous 17980/18620; every one of the 640 holed
    // records has rock cells explaining its holes OR 1-2 item preset
    // rows; zero |8 item bytes ever in 3192 active slots), orbital
    // prefix-packed 18620/18620, items on barren at exactly terrain rate
    // (263/892 = 29.5% vs 31.6%) — so the k-th surface item occupies the
    // k-th cell WITHOUT bit 3, and orbital items read ring cells
    // (always class 1 => never bonus-eligible: e.g. Shipyard ind=1 gets
    // no IND bonus on the ring).
    ChannelAcc a;
    const auto& ps = planets_[star];
    int si = 0, oi = 0;
    // T40: when the planet carries EXPLICIT cell assignments (home CB drawn
    // to a random buildable cell; buildPhase assigns the lowest free cell on
    // completion), the class comes from that cell. The positional walk below
    // remains only as a fallback for items added without assignment.
    const bool explicitCells = ps.itemCells.size() == ps.items.size();
    const int idHyper = itemId("Hyperpower Plant");       // IND doubler (12)
    const int idPros = itemId("Fertilization Plant");     // PROS doubler (13)
    const int idNet = itemId("Internet");                 // RES doubler (14)
    for (size_t ix = 0; ix < ps.items.size(); ++ix) {
        const int it = ps.items[ix];
        const PlanetItem& pi = (*items_)[it];
        int cls = 1;
        if (explicitCells && ps.itemCells[ix] >= 0 &&
            ps.itemCells[ix] < static_cast<int>(ps.cellClasses.size())) {
            cls = ps.cellClasses[ps.itemCells[ix]];
        } else if (itemIsSurface(it)) {
            // advance si past rocky cells (builds skip them, T38)
            while (si < ps.surfaceCells && (ps.cellClasses[si] & 8)) ++si;
            if (si < ps.surfaceCells) cls = ps.cellClasses[si];
            ++si;
        } else if (it < kPlanitemSurfaceCount + kPlanitemOrbitalCount) {
            if (oi < 10) cls = ps.cellClasses[ps.surfaceCells + oi];
            ++oi;
        } else {
            // specials exempt from the XOR law; occupy the non-rock
            // surface stream [placement of specials unmeasured — they add
            // 0 to every channel, so this only shifts later items' bonus]
            while (si < ps.surfaceCells && (ps.cellClasses[si] & 8)) ++si;
            ++si;
        }
        if (pi.ind) a.ind += pi.ind + (cls == 2 ? 1 : 0);
        if (pi.pros) a.pros += pi.pros + (cls == 3 ? 1 : 0);
        if (pi.res) a.res += pi.res + (cls == 4 ? 1 : 0);
        if (it == idHyper) a.dblI = true;
        if (it == idPros) a.dblP = true;
        if (it == idNet) a.dblR = true;
    }
    return a;
}

int Campaign::worldNext() {
    // banked LCG FUN_0007824f: state = state*0x41C64E6D + 0x3039;
    // value = (state >> 16) & 0x7fff (income-law.md S10 t29b).
    worldLcg_ = worldLcg_ * 0x41C64E6Du + 0x3039u;
    return static_cast<int>((worldLcg_ >> 16) & 0x7fffu);
}

void Campaign::seedColonyBaseColony(int star) {
    // Seed a freshly-claimed planet (COLONISED-PLANET LAW, t41 + t42
    // upgrade, docs/re/income-law.md T41/T42): ownership flip arrives with
    // EXACTLY one ACTIVE Colony Base, pop := 2 (income-law.md S6e); cap ==
    // seed + 2 follows from the closed recalc law (CB MPOP 2), observed
    // exact. Original paths (t42 raw disasm): the EVENT handler
    // FUN_0003aa0a @0x3b0bd..0x3b0d1 runs the ACTIVATOR FUN_00038840 mode 0
    // with the cargo slot record (+0xae); FUN_00041d64..0x41d7b runs pop
    // :=2 + the PICKER FUN_00038818 (uniform among checker-legal empty
    // cells). Cargo-slot chooser upstream of +0xae unrecovered [open]; the
    // rewrite uses the picker draw for arrivals (ranks 4/40 observed are
    // consistent). Cell = drawCbCell: ONE worldLcg_ draw over non-rock
    // cells, same stream as terrain and the home draw (REFUTED-ROUTES RNG
    // discipline).
    PlanetState& ps = planets_[star];
    ps.pop = 2;
    const int b = itemId("Colony Base");
    if (b < 0) return;
    ps.items.push_back(b);
    ps.itemCells.push_back(drawCbCell(ps));
}

int Campaign::drawCbCell(const PlanetState& ps) {
    // Uniform over the planet's picker-legal EMPTY cells for Colony Base =
    // ALL NON-ROCK SURFACE CELLS, BARREN INCLUDED. Disasm law (raw listing
    // of checker FUN_0003830c, income-law.md T42): legality = EDI!=0 &&
    // EBP!=0, EDI starts -1 (legal) and every rule only SETS it. For item
    // 5 (RAM flags word +6 == 0x0001, table dump t42): rule A (0x38446)
    // fires on item flags bit0 -> EDI:=-1; rule B (0x38493) NEVER zeroes
    // (barren branch only adds legality); rule C (0x384db) zeroes for
    // orbital placement (item 5 surface-bound); rule D (0x38519) zeroes on
    // ROCK (only exemption item 38); rule G adjacency is SKIPPED for items
    // 5/35 (0x385f6 CMP DL,5; JZ end). Net: CB legal on every non-rock
    // cell, barren included — census agrees (39/162 first-save CBs barren
    // ~ terrain rate; ZERO CB on rock in 2810 corpus CB cells; KS PASS on
    // turn<=1 homes: D=0.085 vs crit 0.192, z=+0.49, n=72 — scripts
    // r1_cb_rank_final.py). Picker FUN_0003875c: ONE rng % count (uniform).
    // ONE worldNext() draw here; returns -1 iff no non-rock cell (original:
    // picker yields 0xffff, FUN_00038718 no-ops, no CB placed).
    int nb = 0;
    for (int c = 0; c < ps.surfaceCells; ++c)
        if (!(ps.cellClasses[c] & 8)) ++nb;
    if (nb == 0) return -1;
    const int pick = worldNext() % nb;
    int seen = -1;
    for (int c = 0; c < ps.surfaceCells; ++c) {
        if (ps.cellClasses[c] & 8) continue;
        if (++seen == pick) return c;
    }
    return -1;
}

// SURFACE GRID GEOMETRY (runtime tables read byte-for-byte from guest RAM,
// kRows-anchored at (terrain weight rows - 152 / - 76; verified identical
// across 484 saves, row sums == live +0x18 per type). Planet-type index
// 0..4 (== surfaceCells 7/11/23/45/73 1:1): ROW_START[r] is the continuous-x
// origin of row r, row width kRowW[type][r]; cell index within surface =
// cumulative width + (x - start). This is FUN_0003965c (row/col from slot)
// and FUN_000395c4 (slot from row/col) rolled into one table walk.
static const int kRowStart[5][15] = {
    {0, 0, 0, 0, 4, 4, 5, 0, 0, 0, 0, 0, 0, 0, 0},
    {0, 0, 0, 4, 3, 4, 5, 6, 0, 0, 0, 0, 0, 0, 0},
    {0, 0, 3, 2, 3, 3, 4, 5, 7, 0, 0, 0, 0, 0, 0},
    {0, 2, 1, 1, 2, 2, 3, 4, 5, 7, 0, 0, 0, 0, 0},
    {1, 0, 0, 0, 1, 1, 2, 3, 4, 5, 7, 0, 0, 0, 0},
};
static const int kRowW[5][15] = {
    {0, 0, 0, 0, 2, 3, 2, 0, 0, 0, 0, 0, 0, 0, 0},
    {0, 0, 0, 1, 3, 3, 3, 1, 0, 0, 0, 0, 0, 0, 0},
    {0, 0, 1, 4, 4, 5, 4, 4, 1, 0, 0, 0, 0, 0, 0},
    {0, 2, 5, 6, 6, 7, 6, 6, 5, 2, 0, 0, 0, 0, 0},
    {3, 6, 7, 8, 8, 9, 8, 8, 7, 6, 3, 0, 0, 0, 0},
};

int Campaign::sizeClassFor(int surfaceCells) {
    for (int t = 0; t < 5; ++t) {
        int sum = 0;
        for (int r = 0; r < 15; ++r) sum += kRowW[t][r];
        if (sum == surfaceCells) return t;  // 7/11/23/45/73, distinct
    }
    return -1;
}

bool Campaign::cellActiveNeighbour(const std::vector<char>& active,
                                   int sizeClass, int surfaceCells, int cell) {
    if (sizeClass < 0 || cell < 0 || cell >= surfaceCells) return false;
    const int* ws = kRowW[sizeClass];
    const int* w0 = kRowStart[sizeClass];
    int cum = 0, row = -1, col = 0;
    for (int r = 0; r < 15; ++r) {
        if (!ws[r]) continue;
        if (cell < cum + ws[r]) {
            row = r;
            col = w0[r] + (cell - cum);
            break;
        }
        cum += ws[r];
    }
    if (row < 0) return false;
    for (int d = 0; d < 4; ++d) {
        const int nr = row + (d < 2 ? (d ? 1 : -1) : 0);
        const int nx = col + (d < 2 ? 0 : (d == 2 ? -1 : 1));
        if (nr < 0 || nr >= 15 || !ws[nr]) continue;
        if (nx < w0[nr] || nx >= w0[nr] + ws[nr]) continue;
        // rowStart is NOT an independent table: a neighbour cell exists only
        // when within the neighbour row's span; its surface index:
        int nsum = 0;
        for (int r = 0; r < nr; ++r) nsum += ws[r];
        const int ncell = nsum + nx - w0[nr];
        if (ncell >= 0 && ncell < surfaceCells && active[ncell]) return true;
    }
    return false;
}

int Campaign::drawItemCell(const PlanetState& ps) {
    // t43 BUILT-ITEM cell law (income-law.md S13): ONE worldNext() draw over
    // the EMPTY, NON-ROCK, rule-G-legal (active-neighbour) surface cells.
    // Picker FUN_0003875c collects checker-legal empties then ONE rng%count
    // — and the picker IGNORES the caller's slot register (59-instr listing:
    // item stashed @0x38769, no re-read of pushed EBX), so all 16 build
    // sites passing EBX=0 are picker draws too (refutes T40(6)
    // prefix-from-0 for the second time). Rule G adjacency from the same
    // checker @0x385b7 (CB exempt 0x385f9). Census r1_built_cell_law.py:
    // 213 worlds, 0/362 active Factories w/o active neighbour, 0
    // transitional anomalies. -1 = no legal empty cell.
    std::vector<char> active(ps.surfaceCells, 0);
    std::vector<char> used(ps.surfaceCells, 0);
    const int szc = sizeClassFor(ps.surfaceCells);
    for (size_t k = 0; k < ps.items.size() && k < ps.itemCells.size(); ++k) {
        const int c = ps.itemCells[k];
        if (c >= 0 && c < ps.surfaceCells) {
            used[c] = 1;
            if (itemIsSurface(ps.items[k])) active[c] = 1;
        }
    }
    // t203 RULE-D EXEMPTION (checker FUN_0003830c 0x38533..0x38552 verbatim:
    // legal iff (slot byte0 & 8) == (itemIdx == 0x26), rule-D block UNbounded
    // by the itemIdx<=30 XOR guard at 0x384e0): rock cells are legal EXACTLY
    // for item 38 Xeno Archeological Dig — dig requires rock, every other
    // item requires non-rock. Rule G adjacency applies to the dig too (the
    // exemptions at 0x385f6/0x385ff are items 5 and 35 only). The
    // completion-tail free-tech grant (FUN_00046e84 @0x39173) reads that rock
    // bit, so the dig draw must reach rock cells or the grant channel is dead.
    const bool digDraw = (ps.pendingItem == 38);
    std::vector<int> legal;
    for (int c = 0; c < ps.surfaceCells; ++c) {
        if (used[c]) continue;
        if (digDraw ? !(ps.cellClasses[c] & 8) : (ps.cellClasses[c] & 8))
            continue;
        if (szc >= 0 && !cellActiveNeighbour(active, szc, ps.surfaceCells, c))
            continue;
        legal.push_back(c);
    }
    if (legal.empty()) return -1;
    return legal[worldNext() % legal.size()];
}

int Campaign::freeTechGrantFor(int owner) {
    // FREE-TECH GRANT LAW, FUN_00046e84 verbatim 0x46e84..0x46f9d (t203,
    // docs/re/_wip_t203.md S1/S3). Candidate loop 0x46ec7..0x46f1a over rows
    // 0..word[base] (the 66-row live count, OQ-013) skipping (a) the owner's
    // research TARGET row (0x46ee6 [base+race*2+0x1d4e] == DAT_00076492, t91
    // field identity) and (b) rows already owned ([row+0x47]>>0x18 &
    // (1<<race) @0x46eff..0x46f0e). NO prereq legality call exists in the
    // function (calls are 0x46ec2 assert, 0x46f23 rng, 0x46f8c event) —
    // CORRECTS aicode.md §3b "legality = FUN_00046d3c" for this grant path:
    // a granted tech can land DEEP in the tree, prereqs unmet. Empty-guard
    // 0x46f1c precedes the rng draw (no draw when count==0). Uniform pick
    // rng % count @0x46f23..0x46f34 (rng 0x7824f = 15-bit LCG, always >= 0,
    // idiv at 0x46f2b never negative). Mark 0x46f4f..0x46f64: owned bits
    // +0x4a/+0x4b |= 1<<race (rewrite ownedTech bool). The TARGET SLOT IS
    // NEVER TOUCHED: the sole +0x1d4e reference is the candidate-loop read.
    // RNG stream: campaign rng_ (mid-turn consumer; worldLcg_ is reserved to
    // the worldgen law set per REFUTED-ROUTES RNG discipline; the original's
    // single-stream draw ORDER inside the completion tail is unrecoverable
    // [documented default]).
    std::vector<int> cand;
    for (int r : tree_->mainIndices()) {
        if (ownedTech[owner][r]) continue;
        if (queuedTech[owner] == r) continue;  // 0x46ee6 target exclusion
        cand.push_back(r);
    }
    if (cand.empty()) return -1;  // 0x46f1c
    const int pick = cand[static_cast<size_t>(rng_() % cand.size())];  // 0x46f23
    ownedTech[owner][pick] = true;  // 0x46f4f..0x46f64 (+0x4a AND +0x4b)
    if (owner == kPlayer)  // 0x46f77 cmp DAT_0007458e; UI event quirk modelled
                           // as a campaign event (vendor event text unrecovered)
        events_.push_back({turn_, "granted free tech " + tree_->all()[pick].name});
    return pick;
}

int Campaign::storedIndFor(int star) const {
    // S6 recalc IND channel (income-law.md §6 + T35 gating): IND
    // accumulator + class bonuses + Hyperpower doubling (v + v>>1),
    // compressed trunc((v+1)^0.85); grant 1 at acc 0 (t19).
    const ChannelAcc a = channelAccFor(star);
    return static_cast<int>(colonyChannel(a.ind, a.dblI, /*compress=*/true));
}

int Campaign::storedResFor(int star) const {
    // RES channel: raw accumulator (+ T35 class bonuses) + Internet
    // doubling, never compressed (S6). GOVERNOR BRANCH (S14 t45,
    // FUN_00038ba4): @0x38df6 EAX = [ESP+0x28]>>2 (IND accumulator AFTER
    // the Hyperpower x1.5 block @0x38d6a, BEFORE both pow blocks), then
    // @0x38e10 (DL==0x22 Scientist Takeover) ADDs it to the RES acc. The
    // branch is after the Internet doubler @0x38dbc, so the bonus is NOT
    // itself doubled; RES is never compressed (T34 +0x46 raw), so word =
    // dbl(acc) + bonus. Governor is -1 on 2810/2810 corpus records
    // (r1_governor_census.py) — inert on all measured state, wired for
    // law completeness, pinned by campaign_governor_law_t45.
    const PlanetState& ps = planets_[star];
    const ChannelAcc a = channelAccFor(star);
    const int bonus = ps.governor == 34 ? (a.ind + (a.dblI ? a.ind >> 1 : 0)) >> 2 : 0;
    return static_cast<int>(colonyChannel(a.res, a.dblR, /*compress=*/false)) + bonus;
}

int Campaign::storedProsFor(int star) const {
    // +0x48 DISPLAY-WORD analog (income-law.md T34, 2720 stored samples):
    // max(1, PROS accumulator (class bonuses gated per T35) -
    // pop>>2-floor). The grant floor-1 and the pop deduction are MEASURED
    // (0-clamp scores 40.99% vs 94.82%; gov switch at +0x54 dead — queue
    // id). T37b: this WORD is also the GROWTH-COUNTER INPUT (corpus
    // battery scripts/r1_pros_growth.py VERDICT disp, raw/gated
    // eliminated 3/5) — incomeAndGrow charges it directly, matching
    // FUN_00038f68 @0x39302, and needClassFor (FUN_0003fec4 reads the
    // +0x48 WORD) sees the same value the original's selector saw.
    // GOVERNOR BRANCH (S14 t45, FUN_00038ba4 @0x38df0): DL==0x21 (Endless
    // Party) adds IND acc >>2 to the PROS acc — BEFORE the pow block
    // (@0x38e62), so the word is max(1, round((dbl(pros+bonus)+1)^0.85));
    // the >>2 operand is post-Hyperpower (@0x38d6a). Governor is -1 on
    // 2810/2810 corpus records (r1_governor_census.py) — inert on all measured
    // state, wired for law completeness, pinned by campaign_governor_law_t45.
    // (The old `richPros` join is DELETED t281: SA_Cornucopia's real PROS
    // contribution arrives via the T35 class-cell bonuses in channelAccFor
    // once the body repaints cells — docs/re/_wip_t281.md.)
    const int govBonus = planets_[star].governor == 33 ? rawIndAccFor(star) >> 2 : 0;
    double pros = channelAccFor(star).pros + govBonus;
    pros -= static_cast<int>(planets_[star].pop) >> 2;
    return pros < 1.0 ? 1 : static_cast<int>(pros);
}

int Campaign::storedCapFor(int star) const {
    // +0x4a law = clamp(0..100, capBase + MPOP sum) over ALL active items
    // (income-law.md S10 t33). The t31/t32 "skip Colony Base" default and the
    // +2 residual were BOTH artefacts of a harness bug: the slot-array pointer
    // at planet+0x10 is the heap OBJECT address and the member array starts at
    // object+0x88 (pointer law, r1-savestate.md:188). With the corrected array
    // the disasm-exact model (add MPOP for every fl&1 slot; Colony Base IS
    // included; flags&4 adds nothing since all four rows 17/28/29/30 carry
    // mpop=0) is 72066/72066 exact across 466 saves. Orbital-slot items need
    // no special case in the rewrite: planets_[s].items holds ACTIVE items
    // only, so no orbital row can enter the sum here.
    // (t280: SA_MoreMaxPop feeds THIS equation via capBase (+2 per fire,
    // body 0x4402a) — the old post-clamp capBonus term is deleted.)
    const PlanetState& ps = planets_[star];
    int mpopSum = 0;
    for (int it : ps.items) {
        mpopSum += (*items_)[it].mpop;
    }
    int cap = ps.capBase + mpopSum;
    if (cap < 0) cap = 0;
    if (cap > 100) cap = 100;
    return cap;
}

// ---------------------------------------------------------------------------
// t201 EMERGENCY CHAIN — FUN_0003fc4c verbatim control flow (banked with
// addresses in docs/re/_wip_t201.md S1d/S2; raw listing
// work/t201_fc4c.txt). NOTE the original's distinctive shapes:
//  * chain-B PRECONDITION failures (IND<4, PROS==0, no Shipyard,
//    freeCells<3) EXIT the evaluator entirely (jl/je 0x3feb9 -> ret 0):
//    a planet failing them gets neither the Cloaker chain nor the
//    fallback template. threat>=6 and an ILLEGAL Surface Shield instead
//    SKIP to chain D (je/jge 0x3fde0).
//  * chain C (Mega Shield) is reached ONLY when item 18 is legal AND
//    already PRESENT (0x3fd0e jne 0x3fd30); ratio fires (unsigned
//    DIV @0x3fda1, jbe 0x3fde0 else) -> buy 19 if legal, buy 18 AGAIN
//    (0x3fdbf je 0x3fd15 shared buy block, no absence test).
//  * chain D present-cloaker skips WITHOUT buying (jne 0x3fe5e).
// Returns the FORCED item id (a buy was queued at the original site) or
// -1 == "none forced" (original ret 0 @0x3feb9; sole caller 0x3f4d5 tests
// only eax==-1 @0x3f4da).
// ---------------------------------------------------------------------------
int Campaign::emergencyChainPick(int ind, int pros, int freeCells,
                                 int shields, int owner,
                                 unsigned deltaDays, unsigned period,
                                 const EmergencyGate& g, int rngPct) {
    // A (0x3fc57): bit1 armed -> attempt the Xeno dig buy (the original's
    // 0x38818 does legality internally; failure falls through with the bit
    // STILL armed; success clears bit1 @0x3fc78).
    if (g.digArmed && g.digLegal && g.digAbsent) return 38;
    // B (0x3fc86..0x3fcd5): every precondition failure is a hard exit.
    if (ind < 4) return -1;
    if (pros == 0) return -1;
    if (!g.shipyard) return -1;
    if (freeCells < 3) return -1;
    if (shields < 6 && g.shieldLegal) {
        if (!g.shieldPresent) return 18;       // 0x3fd0e fallthrough buy
        // C (0x3fd30): UNSIGNED ratio fire.
        if (deltaDays / period > static_cast<unsigned>(shields))
            return g.megaLegal ? 19 : 18;          // illegal mega -> 18 again
    }
    // D (0x3fde0): odd owner, IND STRICTLY > 20 (cmp 0x14 jle @0x3fdfb —
    // t28's ">=20" corrected), rng%100 < 4 (0x3fe11), legal + ABSENT.
    if ((owner & 1) && ind > 20 && rngPct < 4 &&
        g.cloakLegal && g.cloakAbsent) return 11;
    // E (0x3fe5e): template MEASURED live {12,13,14,15,37}; first legal +
    // absent buys.
    static const int kTemplate[5] = {12, 13, 14, 15, 37};
    for (int i = 0; i < 5; ++i)
        if (g.templateLegal[i] && g.templateAbsent[i]) return kTemplate[i];
    return -1;
}

// Threat counters (recalc FUN_00038ba4 law, docs/re/_wip_t201.md S1e —
// MEASURED 2880/2900 (+0x58; the 20 misses are the evaluator self-init
// 0x3fb3e) and 2900/2900 (+0x59) over 2900 corpus records via
// scripts/r201_threat_law_verify.py). The rewrite stores no INACTIVE
// slots, so ACTIVE-count == items-count by construction.
int Campaign::shieldThreatFor(int star) const {
    int n = 0;
    for (int it : planets_[star].items)
        if ((*items_)[it].flags & 8) ++n;
    return n;
}
int Campaign::orbitalThreatFor(int star) const {
    int n = 0;
    for (int it : planets_[star].items)
        if ((*items_)[it].flags & 4) ++n;
    return n;
}

int Campaign::needClassFor(int star) const {
    // FUN_0003fec4 verbatim (income-law.md S9 t28). EAX field analogues:
    // +0x44 IND, +0x46 RES, +0x48 PROS, +0x42 pop, +0x4a cap, +0x4c USED-POP
    // (item-UPOP sum per t202b — the t28 "pending" label is superseded; the
    // pending term measures 0 on 2900/2900 corpus records).
    const PlanetState& ps = planets_[star];
    const int ind = storedIndFor(star);
    const int res = storedResFor(star);
    const int pros = storedProsFor(star);
    const int capMinusPop = storedCapFor(star) - static_cast<int>(ps.pop);
    // +0x4c analog = usedPopFor (item-UPOP sum + governor Automation
    // bonus, t202b upgrade of the pending-UPOP reading).
    const int popMinusPend = static_cast<int>(ps.pop) - usedPopFor(star);
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
    for (size_t s = 0; s < galaxy_.stars.size(); ++s) {
        int o = owner_[s];
        if (o < 0) continue;
        // Per-planet stored channels under the MEASURED battery law
        // (channelAccFor: T35 gating + T36b placement; income-law.md).
        // The original charges the COMPRESSED stored value into the
        // empire budget each turn (turn tick FUN_00038f68 sums
        // +0x44/+0x46 across owned planets; income accumulation site
        // banked with the channel battery).
        const ChannelAcc a = channelAccFor(static_cast<int>(s));
        income[o] += colonyChannel(a.ind, a.dblI, /*compress=*/true);
        res[o] += colonyChannel(a.res, a.dblR, /*compress=*/false);
        // PROS channel for GROWTH: the STORED +0x48 WORD (storedProsFor),
        // NOT the raw item sum (T37b correction, docs/re/income-law.md):
        // corpus battery scripts/r1_pros_growth.py over 13 runs — of the
        // counter-moving transitions, `disp` never loses a divergent
        // comparison while `raw` loses 3 (Feculon II: raw=1, alien boost
        // caps at +1, observed +3 EXCLUDES raw) and `gated` loses 5
        // (Delphinius II / Tensoric I rich worlds: raw=gated=1, stored
        // disp=2, observed +3 matches disp alone; gated never wins where
        // disp fails). The t24 "+3 == raw" reading was a TIE capture
        // (raw=gated=disp=3 there — non-discriminating). Disasm agrees
        // all along: FUN_00038f68 @0x39302 counter += stored PROS +0x48.
        double pros = storedProsFor(static_cast<int>(s));
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
        const int cap = storedCapFor(s);  // clamp(capBase + MPOP)
        if (ps.pop < cap) {
            ps.growthCounter += static_cast<int>(pros);
            if (o != kPlayer && pros < 4) ps.growthCounter += 1;
            if (ps.growthCounter >= cfg_.terrain.popGrowth) {  // DAT_000066e4
                // [verified value 50; t294 SOURCE cited: first integer after
                // planitem.txt '#', stored by the loader @0x3802c — file ==
                // live scalar, so a modded file drives the wrap like the
                // original]
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
                // CELL ASSIGNMENT on completion — LAW CLOSED t43
                // (income-law.md S13): the original routes EVERY build
                // completion through the picker (FUN_0003875c ignores the
                // caller's slot register; the 16 sites passing EBX=0 are
                // draws too) = uniform among EMPTY non-rock cells with an
                // ACTIVE neighbour (checker rule G @0x385b7; CB exempt
                // @0x385f9). Census scripts/r1_built_cell_law.py: 0/362
                // active Factories w/o active neighbour across 213 worlds.
                // Degenerate fallback when NO rule-G-legal empty exists
                // (selector gate is capacity-based so the original CAN
                // queue into one): lowest free non-rock — keeps
                // itemCells/channelAccFor in sync [documented default,
                // degenerate case only].
                if (ps.pendingItem == 38) {
                    // t203 DIG COMPLETION (completion tail 0x3913b..0x3917a
                    // verbatim + checker rule D 0x38533): the dig PLACES on a
                    // rock cell ((byte0&8) == (idx==0x26)). Completion on a
                    // rock slot: clear the rock bit (0x39156 and 0xF7), free
                    // the slot (0x39164 byte1 := 0xFF — the dig CONSUMES
                    // itself; banked T38 "zero |8 item bytes ever" is exactly
                    // this store), then call FUN_00046e84 = FREE-TECH GRANT
                    // (0x39173). Picker yields no legal rock (drawItemCell
                    // -1, or the drawn slot already lost its bit): the
                    // activator reads non-rock -> normal activation tail
                    // 0x3917a, item STANDS, no grant [faithful: slot view].
                    const int cell = drawItemCell(ps);  // rock-only set
                    if (cell >= 0 && (ps.cellClasses[cell] & 8)) {
                        ps.cellClasses[cell] &= ~8;      // 0x39156
                        ps.items.pop_back();             // 0x39164 slot freed
                        freeTechGrantFor(o);             // 0x39173
                    } else {
                        ps.itemCells.push_back(cell);    // 0xffff = unplaced
                    }                        // view keeps items/itemCells 1:1
                } else if (itemIsSurface(ps.pendingItem)) {
                    int cell = drawItemCell(ps);
                    if (cell < 0) {
                        std::vector<char> used(ps.surfaceCells, 0);
                        for (size_t k = 0; k < ps.items.size() - 1; ++k)
                            if (k < ps.itemCells.size() && ps.itemCells[k] >= 0 &&
                                ps.itemCells[k] < ps.surfaceCells)
                                used[ps.itemCells[k]] = 1;
                        int c = 0;
                        while (c < ps.surfaceCells && (ps.cellClasses[c] & 8 || used[c])) ++c;
                        cell = c < ps.surfaceCells ? c : -1;
                    }
                    ps.itemCells.push_back(cell);
                } else {
                    int ring = ps.surfaceCells;
                    std::vector<char> usedo(10, 0);
                    for (size_t k = 0; k < ps.items.size() - 1; ++k)
                        if (k < ps.itemCells.size() && ps.itemCells[k] >= ps.surfaceCells)
                            usedo[ps.itemCells[k] - ps.surfaceCells] = 1;
                    while (ring < ps.surfaceCells + 10 && usedo[ring - ps.surfaceCells]) ++ring;
                    ps.itemCells.push_back(ring);
                }
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
        int usedPop = usedPopFor(s);  // +0x4c analogue: item-UPOP sum (t202b)
        const bool aiPick = (o != kPlayer);
        // ------------------------------------------------------------------
        // t202b DEMOLISH CHANNEL — original order inside FUN_0003f130:
        // over-cap 0x3f178 -> no-free-pop 0x3f220 -> pre-triage gate 0x3f252
        // -> min-requires sweep 0x3f354 -> shared gate 0x3f41e -> emergency
        // chain 0x3f4d5 -> scorer 0x3f4ec (docs/re/_wip_t202.md S13 FINAL;
        // corpus fire-rates: over-cap LIVE 220/2900, always used==pop==cap).
        if (aiPick) {
            // Slot-order parallel arrays for the pickers. The original walks
            // the slot pointer +4i in CELL order (0xff empties skipped), so
            // ties ("first cell") mean lowest cell index — sort the rewrite's
            // push-ordered items by their assigned cell first.
            auto cellOf = [&](size_t k) {
                return k < ps.itemCells.size() ? ps.itemCells[k] : -1;
            };
            std::vector<size_t> order(ps.items.size());
            for (size_t k = 0; k < order.size(); ++k) order[k] = k;
            std::stable_sort(order.begin(), order.end(),
                             [&](size_t a, size_t b) {
                                 const int ca = cellOf(a), cb = cellOf(b);
                                 if (ca < 0 || cb < 0) return ca >= 0 && cb < 0;
                                 return ca < cb;
                             });
            std::vector<int> slotItems, slotMpop, slotUpop, slotReq;
            slotItems.reserve(order.size());
            for (size_t j : order) {
                const PlanetItem& pi = (*items_)[ps.items[j]];
                slotItems.push_back(ps.items[j]);
                slotMpop.push_back(pi.mpop);
                slotUpop.push_back(pi.upop);
                slotReq.push_back(pi.requires);
            }
            auto demolishAt = [&](size_t j) {
                const size_t k = order[j];
                ps.items.erase(ps.items.begin() + k);
                if (k < ps.itemCells.size()) ps.itemCells.erase(ps.itemCells.begin() + k);
                order.erase(order.begin() + j);
                // `order` entries are raw indices into ps.items: after the
                // erase, every survivor with a higher original index shifts
                // down by one (over-cap + sweep can BOTH fire in one turn —
                // 0x3f22f fallthrough — so a stale index would delete the
                // wrong item's cell on the second demolish).
                for (size_t& e : order)
                    if (e > k) --e;
                slotItems.erase(slotItems.begin() + j);
                slotMpop.erase(slotMpop.begin() + j);
                slotUpop.erase(slotUpop.begin() + j);
                slotReq.erase(slotReq.begin() + j);
            };
            // Empty-cell figures per the recalc law (income-law.md S6/T36):
            // eNR = empty NON-rock surface cells (+0x1c analog), eB = the
            // empty class-0/barren subset (+0x20 analog).
            auto emptyCells = [&](int& eNR, int& eB) {
                eNR = 0; eB = 0;
                for (int c = 0; c < ps.surfaceCells; ++c) {
                    bool occ = false;
                    for (size_t k = 0; k < ps.items.size(); ++k)
                        if (cellOf(k) == c) { occ = true; break; }
                    if (occ) continue;
                    if (ps.cellClasses[c] & 8) continue;  // rock: not countable
                    ++eNR;
                    if (ps.cellClasses[c] == 0) ++eB;
                }
            };
            const int pop = static_cast<int>(ps.pop);
            const int cap = storedCapFor(s);
            bool skipSelector = false;
            if (usedPop >= cap) {
                // 0x3f178 OVER-CAP EMERGENCY: victim = LARGEST UPOP among
                // MPOP==0 non-Colony-Base cells; NO candidate -> the original
                // takes the assert/recalc path 0x3f20b and RETURNS (rewrite
                // recomputes everything per turn -> skip selector outright).
                const int v = overCapDemolishPick(slotItems, slotMpop, slotUpop);
                if (v < 0) skipSelector = true;
                else {
                    demolishAt(static_cast<size_t>(v));
                    usedPop = usedPopFor(s);  // recheck 0x3f1fb re-reads +0x4c
                    if (usedPop >= pop) skipSelector = true;  // 0x3f203
                }
            } else if (usedPop >= pop) {
                skipSelector = true;  // 0x3f220 no-free-pop-no-build law
            }
            if (!skipSelector) {
                // 0x3f252 PRE-TRIAGE GATE (S2/S5 FINAL): triage RUNS iff
                // eNR<2 OR (eNR==eB AND ability != SA_BuildOnBlack) — the
                // emergency vacancy channel; healthy planets NEVER triage
                // (ability byte = diplo row +0x19d, census {0:19,1:2,2:11,
                // 3:0,4:8} over 60.sav; BuildOnBlack == 2).
                int eNR = 0, eB = 0;
                emptyCells(eNR, eB);
                const bool bb = abilityOf(o) == SpeciesAbility::BuildOnBlack;
                if (eNR < 2 || (eNR == eB && !bb)) {
                    // Tubes leg 0x3f2c8 DEAD CODE in the shipped scenario:
                    // research-mask bytes [0x743e5..0x7478b tail] measured
                    // all-zero 26 slots x 13 captures (t28) -> straight to
                    // the 0x3f354 min-REQUIRES sweep.
                    const int v = minRequiresDemolishPick(
                        slotItems, slotMpop, slotReq, cap - pop);
                    if (v >= 0) {
                        demolishAt(static_cast<size_t>(v));
                        usedPop = usedPopFor(s);
                        // Post-demolish free-pop recheck 0x3f414 provably
                        // unreachable (S13: pre-guard guarantees used<pop and
                        // demolish only lowers used).
                    }
                }
                // 0x3f41e SHARED GATE on post-demolish facts: eNR==0 ->
                // RETURN; eB==eNR && !BuildOnBlack -> RETURN (no scoring at
                // all; the ability-2 race can score on barren-only vacancy).
                emptyCells(eNR, eB);
                if (eNR == 0 || (eB == eNR && !bb)) skipSelector = true;
            }
            if (skipSelector) continue;  // consumes the selector turn only;
                                         // queue/tick effects above stand.
        }
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
            // t201 EMERGENCY CHAIN (FUN_0003fc4c, called at 0x3f4d5 BEFORE
            // the need-class scorer at 0x3f4ec; ret -1 skips scoring —
            // 0x3f4da cmp eax,-1; je 0x3f74c). Gates measured this session;
            // threat counters derived per recalc law (S1e). RNG note: the
            // original draws only at 0x3fe00 (chain D); here one pct draw
            // happens whenever owner is odd && IND>20 — stream DETERMINISM
            // kept, exact draw TIMING differs [documented default].
            {
                EmergencyGate g;
                g.digArmed = ps.digQueuedOrDone != 0;
                auto legal = [&](int id) {
                    return id >= 0 && id < static_cast<int>(items_->size()) &&
                           requiresAvailable((*items_)[id].requires,
                                             static_cast<int>(tree_->all().size()),
                                             ownedTech[o]);
                };
                auto absent = [&](int id) {
                    for (int it : ps.items)
                        if (it == id) return false;
                    return true;
                };
                g.digLegal = legal(38);      g.digAbsent = absent(38);
                g.shieldLegal = legal(18);   g.shieldPresent = !absent(18);
                g.megaLegal = legal(19);
                g.cloakLegal = legal(11);    g.cloakAbsent = absent(11);
                g.shipyard = !absent(22);
                static const int kTpl[5] = {12, 13, 14, 15, 37};
                for (int i = 0; i < 5; ++i) {
                    g.templateLegal[i] = legal(kTpl[i]);
                    g.templateAbsent[i] = absent(kTpl[i]);
                }
                int freeCells = 0;  // (+0x1c)-(+0x20): empty, non-rock, non-
                                    // class-0 surface cells (recalc loop law,
                                    // income-law.md S6/T36 accounting)
                for (int c = 0; c < ps.surfaceCells; ++c) {
                    if (ps.cellClasses[c] & 8 || ps.cellClasses[c] == 0) continue;
                    bool usedc = false;
                    for (size_t k = 0; k < ps.items.size(); ++k)
                        if (k < ps.itemCells.size() && ps.itemCells[k] == c)
                            usedc = true;
                    if (!usedc) ++freeCells;
                }
                // Hop = lane BFS to nearest OTHER owner's star; none/no
                // enemies -> 4 (tier 400; unreachable rows read 0xff>=4 in
                // the original) [documented default — the original's row
                // operand [ctx+7]->[+2]>>16 identity is UNVERIFIED].
                int hop = 4;
                {
                    std::vector<int> dist(galaxy_.stars.size(), -1);
                    std::vector<int> q{static_cast<int>(s)};
                    dist[s] = 0;
                    for (size_t h = 0; h < q.size() && hop == 4; ++h) {
                        for (int nb : galaxy_.neighbours(q[h])) {
                            if (dist[nb] >= 0) continue;
                            dist[nb] = dist[q[h]] + 1;
                            if (owner_[nb] >= 0 && owner_[nb] != o) {
                                hop = dist[nb];
                                break;
                            }
                            q.push_back(nb);
                        }
                    }
                }
                int rngPct = 100;
                if ((o & 1) && storedIndFor(s) > 20) {
                    std::uniform_int_distribution<int> pct(0, 99);
                    rngPct = pct(rng_);
                }
                pick = emergencyChainPick(storedIndFor(s), storedProsFor(s),
                                          freeCells, shieldThreatFor(s),
                                          static_cast<int>(o),
                                          static_cast<unsigned>(turn_ > ps.emergencyStamp
                                               ? turn_ - ps.emergencyStamp : 0),
                                          emergencyPeriodFor(hop), g, rngPct);
                if (pick == 38) ps.digQueuedOrDone = 0;  // bit1 clear 0x3fc78
                if (pick == 19) ps.emergencyStamp = turn_;  // stamp default
            }
            if (pick < 0) {
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
            }  // t201: normal-scorer guard (chain pick skips scoring entirely)
        }
        if (pick < 0) continue;
        if (itemIsSurface(pick)) {
            int surface = 0;
            for (int it : ps.items)
                if (itemIsSurface(it)) ++surface;
            // T38 ROCK-SKIP [verified]: builds prefix-pack over NON-ROCK
            // cells (zero |8 item bytes ever; 350 mid-event rock holes
            // below the prefix) — effective capacity is the buildable
            // cell count, the +0x1c analog (empty NON-rock count,
            // 71762/72066 recs).
            int buildable = 0;
            for (int k = 0; k < ps.surfaceCells; ++k)
                if (!(ps.cellClasses[k] & 8)) ++buildable;
            if (surface >= buildable) continue;  // +0x18 seeded per S10
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
                // t93 (OQ-016): AI PICK LAW = FUN_00040018 (body
                // 0x40018..0x40175, disassembly re-verified t93 —
                // docs/re/aicode.md §3c/§3d). Replaces the UNCITED
                // uniform-random pick. Tiers:
                //  1. Candidates: avail above IS the 0x4002e..0x40083
                //     build (row order, skip owned, prereq-chain legality
                //     == FUN_00046d3c), truncated to the vendor cap 0x20
                //     (cmp edi,0x20 @0x40044).
                //  2. Sentinel (0x400b3..0x400da): DAT_00074902 bit —
                //     live-measured 0x0f, EVERY shipped-scenario AI (t92).
                //     rng%100 < 45 (idiv 0x400d3, cmp edx,0x2d) sets
                //     chosen=-2, which exits the preferred scan at guard
                //     0x400fb. The uniform leg 0x40134 tests chosen>=0,
                //     so -2 is OVERWRITTEN, never stored: the sentinel
                //     skips the PREFERRED BIAS, not the pick (§3d — this
                //     corrects §3c's "no pick this turn" note). Modelled
                //     as aiResearchPreferred(sentinelHit) + fallback
                //     below; one rng draw per pick opportunity mirrors
                //     0x400c4, the fallback draw mirrors 0x4013f.
                //  3. Preferred scan (0x400e1..0x40134): first candidate
                //     (lowest row index) that is a member of the 23-word
                //     static list 0x67be wins — membership degenerates to
                //     {1,47} on the live 66-row table (§3c math); match
                //     stores once (re-guards 0x400fb/0x4010d).
                //  4. Fallback (0x4013f): uniform rng % candidate-count.
                const size_t ncand = std::min<size_t>(avail.size(), 32);  // cap 0x20 @0x40044
                const bool sentinelHit = (rng_() % 100) < 45;  // 0x400c4..0x400d8
                int chosen = aiResearchPreferred(
                    std::vector<int>(avail.begin(), avail.begin() + ncand), sentinelHit);
                if (chosen < 0) {
                    std::uniform_int_distribution<size_t> pick(0, ncand - 1);
                    chosen = avail[pick(rng_)];  // 0x4013f
                }
                queuedTech[o] = chosen;
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
            // CLAIM-VISIBILITY PAIR [documented default, t192 law extended]:
            // a claimed star carries the claimant's bits in BOTH star mask
            // bytes (+0x16/+0x17 analogs). seedVisibility() states the premise
            // (the click handler refuses to select a star without the bit);
            // t284 adds the producer consequence — FUN_00024274 tests the FAR
            // star's +0x17, so a colony without its owner's bit would prune
            // its own subtree out of the CONTROLLED count.
            starLaneVis_[sh.target] |= static_cast<char>(viewerMaskFor(sh.owner));
            starSelVis_[sh.target] |= static_cast<char>(viewerMaskFor(sh.owner));
            // settlement :=2 MEASURED (income-law.md S6e) + COLONY BASE
            // grant MEASURED t41 (r1_colony_items.py: 2720/2720 owned
            // records carry an active CB; every in-run colonisation
            // observation is CB-only pop 2 cap==seed+2).
            seedColonyBaseColony(sh.target);
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
            // (starKnown: own star or adjacent-to-own. SA_KnowStarLanes is
            // NOT a sim-side expansion cheat: since t195 its real effect is
            // the COSMOS-VISIBILITY layer (seedVisibility ORs the owner bit
            // into every lane mask — ships.md S23 L6/L9), a UI surface; this
            // AI targeting law stays as measured for the sim.) The frontier
            // gate itself and the SA_BlockStarLanes gate are unchanged.
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

// OQ-026 receive-leg sweep. Cited shape (ships.md S23 L6): caller 0x55f6e
// calls FUN_00046354 with EBX=-1 (receive-only) inside the per-race event
// loop 0x55f1b..0x55f2e, party-1 always the CURRENT player row ([0x7458e]
// set 0x55f35/0x55f55) => "the PLAYER receives lanes from each race in turn".
// Rewrite trigger: FIRST turn the player's holdings are lane-adjacent to that
// empire's holdings (one-shot per pair; the original's loop cadence is not
// recovered, so repeating the call every turn would over-grant against the
// t193 witness "masks md5-STATIC across a window with no alliance
// transition").
void Campaign::visibilityPhase() {
    for (int e = 1; e < Nowner_; ++e) {
        if (contacted_[kPlayer * Nowner_ + e]) continue;
        if (!contactSeen(kPlayer, e)) continue;
        contacted_[kPlayer * Nowner_ + e] = 1;
        const int allied = dipState_[e - 1].allied ? true : false;
        const int n = shareLaneVision(kPlayer, e, /*bidirectional=*/false, allied);
        shareStarVision(kPlayer, e, /*bidirectional=*/false, allied);
        if (n > 0 && e - 1 < static_cast<int>(aiDip_.size()))
            events_.push_back({turn_, "Shared star-lane intelligence with " +
                                          aiDip_[e - 1].displayName + " (" +
                                          std::to_string(n) + " lanes)"});
    }
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
            // LANE SHARE fires WHEN AN ALLIANCE IS MADE — cited caller 0x45778
            // (EBX=0 bidirectional, inside the alliance-formation handler that
            // writes row+0x1c0 state and the +10/+5 attitude bumps; ships.md
            // S23 L6). allied=true -> modulus 6 (lane budget doubles).
            shareLaneVision(kPlayer, owner, /*bidirectional=*/true, /*allied=*/true);
            shareStarVision(kPlayer, owner, /*bidirectional=*/true, /*allied=*/true);
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
            // MEASURED CADENCE LAW (t100, docs/re/aicode.md §6.4 + _wip_t99
            // F7/F9): charge_ == original row+0x19e COUNT-UP. The FUN_0003e6e0
            // tail bumps it +1/turn; FUN_00043b50 fires iff counter == cadence
            // word EXACTLY (gate 0x43b58 rejects cad > counter; equality routes
            // to the jump-table body). Reset-on-fire == 0x441c9 pre-stores
            // temp=0 -> exit T1 0x4400a stores row+0x19e := 0. The T2 variant
            // (0x43fe5, profile 13 ShieldPlanets: counter := cad - counter)
            // also stores 0 at the equality point — under the cited law it
            // only preserves phase on the not-due leg, so one reset models
            // both. The original EXCLUDES the player row from firing (tail
            // exit after the bump, F7); the rewrite auto-fires the player's
            // species ability as the documented sim model (abilities.md §2).
            if (++charge_[o] != abilityChargeTurns(ab)) continue;
            charge_[o] = 0;
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
                // t280 ERRATUM note (aicode.md amendment E2): the vendor body
                // 0x43bf0 does NOT end wars — for every other row x it FLOORS
                // word[row(x)+0x1b2+2*self] == att[x->self] at PP(x)+20 (x's
                // own PROPOSE_PEACE + 20), arming x's chooser rung `att >
                // proposePeace` (diplomacy.cpp:239) so x proposes peace to
                // self on a later turn — peace via the chooser chain, not
                // instantly. The rewrite keeps its end-the-wars abstraction:
                // DIVERGENCE banked (arrival-via-chooser vs same-turn clear);
                // wiring the floor for the player-holder case needs player->
                // AI attitudes, which the state does not carry (dipState_ is
                // AI->player). Pinned unchanged by
                // species_force_peace_ends_the_owner_wars.
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
                // CITED BODY LAW SA_Cornucopia 0x43de4 (aicode.md §6.3 t99,
                // re-read raw t281 work/t280_bodies.txt:152; docs/re/_wip_t281).
                // SELECT: pool scan, owner byte == self, SKIP WORD[rec+0x16]
                // ==10 (the zero-barren terrain row — measured r1_t281_w16_-
                // census.py: +0x16 is the stored weight-row index, NOT a
                // homeworld marker), MIN WORD[rec+0x42] strictly-less wins,
                // first record wins ties, none owned = no-op exit.
                // REPAINT: slot array [rec+0x10], bound WORD[rec+0x18] ==
                // SURFACE cells ONLY (the orbital ring is never touched),
                // raw class byte in {0,1} -> uniform pick {2,3,4} (pool
                // 0x6838, rng 0x7824f idiv 3). No occupied-slot gate: a cell
                // under a built item is repainted too — its income then rides
                // the T35 class-cell bonus in channelAccFor (the real channel
                // the old richPros+=2 stand-in approximated; field deleted).
                // RNG: worldLcg_ — terrain-mutation family (world-gen draw +
                // rock event precedent); the rng_ trajectories are untouched
                // [inferred stream choice, pick MEMBERSHIP {2,3,4} is cited].
                int best = -1;
                int bestPop = 0xffff;  // cx init @0x43de9
                for (size_t s = 0; s < galaxy_.stars.size(); ++s) {
                    if (owner_[s] != o) continue;                    // [rec+0x57]
                    if (planets_[s].terrainRow == 10) continue;      // [rec+0x16]
                    const int pop = static_cast<int>(planets_[s].pop);  // [rec+0x42]
                    if (pop >= bestPop) continue;                    // jbe prune @0x43e24
                    best = static_cast<int>(s);
                    bestPop = pop;
                }
                if (best < 0) break;  // 0x43e3a null-exit (no eligible colony)
                int painted = 0;
                auto& cls = planets_[best].cellClasses;
                const int bound = std::min(planets_[best].surfaceCells,
                                           static_cast<int>(cls.size()));  // [rec+0x18]
                for (int c = 0; c < bound; ++c) {
                    const int v = cls[c];  // RAW byte incl. rock bit: 8/9 fail
                                           // the {0,1} test exactly as the vendor's
                    if (v != 0 && v != 1) continue;
                    cls[c] = 2 + worldNext() % 3;  // pool 0x6838 {2,3,4} idiv 3
                    ++painted;
                }
                events_.push_back({turn_, who + "made " + galaxy_.stars[best].name +
                                      " a rich world (" + std::to_string(painted) +
                                      " cells repainted)"});
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
                // CITED BODY LAW SA_StealTech 0x43eec (aicode.md §6.3 t99):
                // for each research row, the per-race OWNERSHIP bitmask is
                // ORed in iff popcount(mask) >= 2 (the "known by at least two
                // other races" rule the vendor text states), AND — the leg the
                // rewrite was missing until t256 — if the stolen row IS this
                // race's own research target (0x76492[2*self] == i) the target
                // is set to 0xffff so it re-picks next turn. queuedTech -1 is
                // that sentinel here.
                int n = 0;
                const int target = queuedTech[o];
                bool targetStolen = false;
                for (size_t t = 0; t < tree_->all().size(); ++t) {
                    if (ownedTech[o][t]) continue;
                    int holders = 0;
                    for (int e = 0; e < Nowner_; ++e)
                        if (e != o && ownedTech[e][t]) ++holders;
                    if (holders >= 2) {
                        ownedTech[o][t] = true;
                        ++n;
                        if (static_cast<int>(t) == target) targetStolen = true;
                    }
                }
                if (targetStolen) { queuedTech[o] = -1; techProgress[o] = 0; }
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
                // CITED BODY LAW SA_MoreMaxPop 0x4402a (t280 — the body
                // aicode.md §6.3 never documented; jump-table case al=9 at
                // restored FILE 0x43b10+9*4, raw listing work/t280_bodies.txt):
                // scan the static planet pool 0x2b057 stride 0x7b (bound
                // u16@0x3a093), match owner byte [rec+0x57] == self, and for
                // EVERY match `WORD [rec+0x55] += 2` then per-planet recalc
                // 0x38ba4. Operand = the PRE-CLAMP cap seed word (capBase,
                // income-law.md S10), delta +2 — NOT a post-clamp +25 bonus
                // (the t280-removed capBonus field), and there is NO
                // pending-item gate (contrast IndustryBoost) and NO
                // [rec+0x16]==10 skip (contrast Cornucopia). income-law.md
                // S10 had already measured this exact site from the corpus
                // side ("+2: scan 0x4402a ... adds 2 to EVERY owned planet's
                // +0x55 then recalcs; no in-code caller found"); the caller IS
                // the ability dispatcher 0x441d8.
                int n = 0;
                for (size_t s = 0; s < galaxy_.stars.size(); ++s)
                    if (owner_[s] == o) { planets_[s].capBase += 2; ++n; }
                events_.push_back({turn_, who + "raised " + std::to_string(n) +
                                      " colony pop caps (+2 seed each)"});
                break;
            }
            case SpeciesAbility::KnowStarLanes:
                break;  // PASSIVE (no amass line, L2295 block; cadence word 0).
                        // REAL EFFECT since t195: wired at scenario init in
                        // seedVisibility() (owner bit ORed into every lane
                        // mask; ships.md S23 L6/L9) — not a no-op any more.
            case SpeciesAbility::BlockStarLanes: {  // L2314-2315 "block all star lanes entering your colonized systems"
                int n = 0;
                for (size_t s = 0; s < galaxy_.stars.size(); ++s)
                    if (owner_[s] == o) { laneBlock_[s] = 1; ++n; }
                events_.push_back({turn_, who + "blocked lanes into " + std::to_string(n) + " stars"});
                break;
            }
            case SpeciesAbility::CauseWar: {  // L2361-2362 "alien species to strongly dislike any species at war with you"
                // *** t280 ERRATUM against aicode.md §6.3 (and therefore
                // against t256's wiring, which mirrored it). Raw re-read of
                // 0x440b5..0x4414c (work/t280_bodies.txt; aicode.md t280
                // amendment E3): OUTER loop k != self over self's state
                // window byte[row(self)+0x1c0+k] == 2 (at war) — §6.3 right;
                // INNER loop x != self, x != k operates cell word[row(x) +
                // 0x1b2 + 2*k]. Cell law (row = HOLDER, col = TARGET; three
                // witnesses: §13.2, t207 §19, watcher relation() docstring):
                // that cell is att[x -> k] — the THIRD PARTY's attitude
                // toward the ENEMY — ceilinged at word[row(x)+0x1c9] ==
                // DECLARE_WAR(x), the third party's OWN line (help.txt
                // L2361: onlookers come to dislike your enemies). §6.3's
                // "[x toward self +0x1b2] > [r+0x1c9]" mislabeled both.
                // CONSEQUENCE for the rewrite: every cell the vendor law
                // touches has holder x != self AND target k != self, i.e.
                // AI->AI attitudes — the row-12 absent state (t256b census:
                // dipState_ carries AI->PLAYER only). The t256
                // Campaign::hatredClamp mutation clamped att[x->self] at
                // DW(r), which the vendor never does, so it is RETIRED
                // (campaign.h; pin species_cause_war_hatred_ceiling_t256
                // replaced by species_cause_war_two_party_boundary_t280).
                // Announce-only under EVERY owner, honestly labelled (blast
                // radius of the retirement measured nil on gate seeds —
                // CauseWar = specnum 17 never occupies default AI slots
                // 0..5, t256).
                events_.push_back({turn_, who +
                                      "stoked the aliens' rivalries (AI->AI "
                                      "attitudes unmodelled: no rewrite state)"});
                break;
            }
            case SpeciesAbility::FastLaneTravel:
                break;  // passive: +1 launch hop in driveHopsFor
            case SpeciesAbility::FreeResearch: {  // L2429-2430 "immediately achieve any discovery you are pursuing"
                // CITED BODY LAW SA_FreeResearch 0x4414e (aicode.md §6.3 t99
                // + t105 stride-75 correction): `if own target t != 0xffff:
                // progress := WORD cost(75*t)` — i.e. it completes the row
                // YOU ARE ALREADY PURSUING and does NOTHING when no row is
                // queued. The rewrite's earlier "pick the cheapest available
                // row if none queued" leg was an UNCITED bonus (t256 removal)
                // that made the Dubtak-free-research race jump tiers.
                const int t = queuedTech[o];
                if (t >= 0 && !ownedTech[o][t]) {
                    ownedTech[o][t] = true;
                    events_.push_back({turn_, who + "completed " + tree_->all()[t].name});
                } else {
                    events_.push_back({turn_, who + "nothing pending to complete"});
                }
                queuedTech[o] = -1;   // the original's re-pick-next-turn slot
                techProgress[o] = 0;
                break;
            }
            case SpeciesAbility::IndustryBoost: {  // L2476-2477 "boost the progress on all your colonies' projects"
                // CITED BODY LAW SA_IndustryBoost 0x4418e (aicode.md §6.3
                // t99): for every own planet with a pending project
                // ([p+0x54] != 0xff), `WORD [p+0x50] += 100` — the PER-PLANET
                // build accumulator, NOT an empire stockpile, and gated to
                // planets that actually have a project (income-law.md S8:
                // +0x54 == 0xFF means the queue is empty). The earlier
                // rewrite cut added 20 to ind_[owner], which is the
                // ship-launch budget (buildPhase never pays ind_ into a
                // planet queue) — wrong operand AND wrong magnitude (t256).
                int n = 0;
                for (size_t s = 0; s < galaxy_.stars.size(); ++s) {
                    if (owner_[s] != o) continue;
                    PlanetState& ps = planets_[s];
                    if (ps.pendingItem < 0) continue;  // [p+0x54]==0xff gate
                    ps.buildAcc += 100;
                    ++n;
                }
                events_.push_back({turn_, who + "boosted " + std::to_string(n) +
                                      " colony projects (+100 IND each)"});
                break;
            }
            case SpeciesAbility::kCount:
            case SpeciesAbility::Unknown:
                break;
        }
    }
}

int Campaign::attackScore(int owner) const {
    // UPGRADED t89 (OQ-010) to the cited original law. The original's volley
    // loop (0x4a5c1..0x4a5fc, docs/re/combat.md S2g, S2h-audited) fires
    // EVERY cat-0 weapon in the ship's gizmo slots in STORED order per
    // engagement, and each in-range hit applies design[+0x52] (= the file
    // Level column, column map CLOSED 76/76 t87, scripts/r1_t87_gizmo_table.py)
    // with NO hit roll (measured-negative, S2g "HIT PROBABILITY"). So the
    // aggregate volley damage of an empire's researched weapon set is the
    // SUM of researched weapon Levels, replacing v1's MAX (turnloop.md §5
    // [inferred]). Empires field whatever they can build, so the per-empire
    // scale still rides total owned pop /10 (reserves model, unchanged).
    double pop = 0;
    for (size_t s = 0; s < galaxy_.stars.size(); ++s)
        if (owner_[s] == owner) pop += planets_[s].pop;
    int volley = 0;
    if (gizmos_) {
        for (const Gizmo& g : *gizmos_) {
            if (g.cat != GizmoCat::Weapon) continue;
            bool ok = requiresAvailable(g.resReq, static_cast<int>(tree_->all().size()),
                                        ownedTech[owner]);
            // NumUses gate [verified gizmos.txt header + dispatcher 0x4a373..
            // 0x4a390 S2g]: a 0-use row engages nothing (every shipped cat-0
            // row has NumUses >= 1 — {1,1,1,1,5,1,2,2,2,3} — so this arm
            // never fires on shipped data, it refuses a 0-use row).
            if (ok && g.numUses != 0) volley += g.level;
        }
    }
    // SA_SapAlienPower / SA_HealShips semantics: fleetDamage_ IS the sapped
    // "power" (abilities.md §2) — subtracted from fleet strength until
    // repaired. Floor at 0 keeps a sapped empire able to defend its homes.
    return std::max(0, static_cast<int>(pop / 10.0) + volley - fleetDamage_[owner]);
}

int Campaign::defenseScore(int owner, int star) const {
    // UPGRADED t89 (OQ-010) to the cited TWO-LAYER model. The original's hit
    // path 0x4b740 (whole body disassembled, S2h-audited) never folds shields
    // into a single defense total: shield absorb = MIN(damage, [t+0x90]) with
    // the overflow SPILLING to hull [t+0x8c], both clamped, death at hull < 1
    // (0x4b7c4..0x4b8a6). So defenseScore is the HULL layer only — local-pop
    // reserves model — and the shield absorb is applied as a clamped split at
    // the engagement site (combatPhase). Fortify +2 is the rewrite's own
    // capture-protection term [documented default, unchanged].
    double pop = planets_[star].pop;
    return static_cast<int>(pop / 10.0) + 2;
}

int Campaign::shieldChargesFor(int owner) const {
    // SUM of researched CAT==1 (Shield) gizmo Levels == the original's
    // shield-charge law 0x49f15 (ship+0x90 += design[+0x56], +0x56 == file
    // Level for shields, S2d/S2f; 6 shipped shield rows, Levels 1..5
    // [verified gizmos.md]). The rewrite has no per-ship slot inventory
    // (S2i), so this is the empire-level aggregate analogue.
    int charges = 0;
    if (gizmos_) {
        for (const Gizmo& g : *gizmos_) {
            if (g.cat != GizmoCat::Shield) continue;
            if (requiresAvailable(g.resReq, static_cast<int>(tree_->all().size()),
                                  ownedTech[owner]))
                charges += g.level;
        }
    }
    return charges;
}

void Campaign::setAllTechs(int owner, bool owned) {
    if (owner < 0 || owner >= static_cast<int>(ownedTech.size())) return;
    // NOTE: vector<bool>::reference proxy — no `for (bool& b : ...)` here.
    auto& v = ownedTech[owner];
    for (size_t i = 0; i < v.size(); ++i) v[i] = owned;
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
            // DETERMINISTIC COMBAT LAW (t89, OQ-010): the original has NO hit
            // roll — full-body reads of the gun handler 0x4b8e4 + hit path
            // 0x4b740 contain no rng call and no random-compare, and zero
            // rel32 rng edges exist in the whole combat module family
            // [0x4a360,0x4f097) (docs/re/combat.md S2g "HIT PROBABILITY:
            // MEASURED NEGATIVE", S2h-audited). v1's uniform(0,10) draws here
            // were an UNCITED abstraction; removing them re-diverts campaign
            // rng_ ON PURPOSE (the combat-phase draws were never cited — the
            // remaining rng_ consumers incomeAndGrow/buildPhase keep their
            // sequences). RNG discipline still holds downstream: no feature
            // may ADD or SKIP draws around the remaining streams.
            //
            // TWO-LAYER CLAMPED ABSORB (0x4b7c4..0x4b8a6, S2h): the defender's
            // shield charges absorb the volley FIRST, clamped at the volley
            // (min law at 0x4b7c4), and only the SPILL reaches the hull layer.
            // Aggregate mapping (S2i: no per-ship inventory exists):
            //   volley  = attackScore(a)          (every researched cat-0 gun)
            //   absorb  = MIN(volley, shield charges of b)
            //   hullHit = volley - absorb  vs  defenseScore(b, nb) (hull/pop)
            // (SA_ShieldPlanets is the guard above — it skips the engagement,
            // the aggregate stand-in for the +0x9c 0x10 null-shield bit.)
            int volley = attackScore(a);
            if (doublePower_[a]) volley *= 2;          // SA_DoublePower (L1917)
            int absorb = 0, hullHit = 0;
            absorbSplit(volley, shieldChargesFor(b), absorb, hullHit);
            // t204 DIPLOMACY-ON-ATTACK — FUN_00043a4c AT ITS CITED CALL SITE
            // 0x4b875: the hostility cost lands BEFORE the shield/hull
            // subtraction (0x4b87a/0x4b888) — the price of FIRING, not of
            // capturing; a repelled attack still pays. Fires per engagement
            // resolution. t210 STACKING LAW (docs/re/_wip_t210.md S6): the
            // original charges once per COMMITTED weapon/victim (mode==1
            // gate 0x4b7f1; volley loop 0x4a5c1 is mode-0 cost-free; commit
            // loop 0x2550c one arm per matched gizmo; cat-5 splash loops
            // 0x4d0a5/0x4d2ab per victim) — this per-engagement charge is
            // the DOCUMENTED UNDER-MODEL (per-commit conversion crosses the
            // OQ-019 per-ship boundary; NO semantic change). Two-
            // party projection (gap row 12): dipState_ rows are AI->PLAYER,
            // the original's cell is victim->attacker, so the cell exists
            // exactly when the attacker is the player; AI-AI engagements
            // have NO attitude cell to charge (banked residue, _wip_t204 D2).
            // State proxy: dipState_.atWar/.allied == the row's state byte
            // 0x1c0 (2=WAR t85b / 3=ALLIANCE t189b).
            if (a == kPlayer && b >= 1 && b - 1 < static_cast<int>(dipState_.size())) {
                DipPolicyState& vst = dipState_[b - 1];
                if (applyAttackDipCost(aiDip_[b - 1].values, vst.atWar, vst.allied,
                                       kAttackDipGovByte, &vst.attitude)) {
                    // t205 INDEX CORRECTION: original 0x43afa ORs into
                    // byte[0x48304 + star_index] where the star is the
                    // ENGAGEMENT LOCATION (the handler's EDX is a STAR record
                    // built from the ship's +0x59 star pointer — 0x4b82c; the
                    // index is dword[star_record+2]>>16 == the star's own
                    // index). Not a per-race global byte as t204 mirrored.
                    attacked_[nb] |= static_cast<unsigned char>(1 << b);
                }
            }
            if (invadesAlwaysSucceeds(a)) {            // SA_SuperMarines (L1723 always succeed)
                ind_[a] -= shipCostC;                  // the invasion ships
                superUsed[a] = 1;
            } else if (hullHit <= defenseScore(b, nb)) {
                continue;
            }
            // t207 GUARANTEE-WAR CLAMP (FUN_0003a174 post-handler site
            // 0x3a25a..0x3a291, cited docs/re/_wip_t207.md S7b): the
            // INVASION path pays the t204 handler at 0x3a255 and on the -1
            // (not-at-war) return re-reads the cell and, while STILL
            // strictly above the victim's DECLARE_WAR line, slams it to
            // declareWar-10 — the t180 chooser then GUARANTEES war. Wiring
            // site = the rewrite's capture branch (below the repel test):
            // the one place an invasion resolution is KNOWN to have run.
            // t209 POSITION LAW (MEASURED, docs/re/_wip_t209.md S5): the
            // original clamps AT ATTEMPT TIME — 0x3a25a runs before the
            // defense score is even counted (loop 0x3a2c9.., result select
            // 0x3a327), success/repel branches only at 0x3a45c, and the
            // engine caller 0x42c8e DISCARDS the return (0x42c97 clobbers
            // EAX; no order/ship-survival branch keys on the outcome). So
            // a repelled invasion pays the clamp too in the original.
            // DOCUMENTED UNDER-MODEL (kept, no semantic change t209): the
            // rewrite's single aggregate volley cannot represent an
            // attempt independent of its outcome; clamping at the capture
            // branch under-fires vs the attempt-time law, and the gun-
            // bombard caller 0x39f00 pays WITHOUT clamping (t207 S7c).
            // Per-attempt wiring = OQ-019 boundary (BLOCKED-USER).
            if (a == kPlayer && b >= 1 && b - 1 < static_cast<int>(dipState_.size())) {
                DipPolicyState& vst = dipState_[b - 1];
                guaranteeWarOnInvasion(aiDip_[b - 1].values, vst.atWar, &vst.attitude);
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
    // t291 UPGRADE to the CITED vendor comparator (docs/re/_wip_t290.md S1,
    // evaluator FUN_00024a34 file 0x24b9c..0x24bbe, read verbatim):
    //     eax = floor(2*T/3) + 1 ; cmp eax, V ; jg skip ; -> Control
    // i.e. Control iff V >= floor(2T/3)+1  <=>  V > 2T/3 (integer-exact).
    // Operands: V = DAT_000482fb = scoreStars_ (the PRODUCED controlled-system
    // count from the pruned flood, score.md S17/S18) and T = DAT_00016143 ==
    // total stars (score.md S3, the same field the 'c' overlay disproducer
    // reads). The arm is therefore NOT starsOwned-based: the previous
    // `mine * 2 > total` default (the end-ctrl.txt header comment "over half")
    // is MEASURED-WRONG on both the operand and the threshold -- the prose in
    // enddesc/congrat ("over two-thirds", "more than two-thirds of the stars")
    // matches the code, and the code wins. (2*total)/3 truncates toward zero ==
    // floor for total >= 0, so this is the vendor's idiv pair exactly.
    const int ctrlThreshold = (2 * total) / 3 + 1;
    if (scoreStars_ >= ctrlThreshold) return Victory::Control;  // end-ctrl (OQ-021, t291 cited law)
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
    visibilityPhase();
    diplomacyPhase();
    // t284 cadence law: the producer runs in the END-OF-TURN pass only
    // (FUN_00024f24 tail, after the per-race loop, just before the turn
    // increment). Placed after diplomacy so an alliance formed THIS turn
    // already counts in the allied mask, as in the original (the pass reads
    // live relation cells).
    recomputeScoreStars();
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
    // t284 UPGRADE to the cited disproducer law (docs/re/score.md S2, raw bytes
    // 0x280be..0x280e5): displayed percent = TRUNC(100 * DAT_000482fb / T) with
    // T = total stars (u32 DAT_00016143 >> 16). The idiv at 0x280e3 TRUNCATES,
    // so no +0.5 here (the pre-t284 rounding of an owned-star share was a
    // documented default; the numerator AND the rounding are both replaced).
    const int total = static_cast<int>(galaxy_.stars.size());
    return total ? (100 * scoreStars_) / total : 0;
}

// t284 — replay of the witnessed producer FUN_00024274 (payload file
// 0x24274..0x243fc; Ghidra decompile cross-checked instruction-for-instruction
// against objdump of work/ascend_payload.bin; full law + corpus validation in
// docs/re/_wip_t284.md). One flood step: walk `star`'s lane list, admit a lane
// only if its far star passes visibility + presence and the lane is uncontested,
// then recurse INTO the far star (a failing lane prunes that whole subtree —
// this is what makes V jump by whole branches, e.g. t912 11->22 with zero
// systems change, and fall 23->14 in one combat sprint).
void Campaign::floodControlled(int star, std::vector<char>& laneDone,
                               unsigned allowedMask, int& count) const {
    if (star < 0 || star >= static_cast<int>(galaxy_.stars.size())) return;
    for (size_t li = 0; li < galaxy_.lanes.size(); ++li) {
        if (laneDone[li]) continue;
        const Lane& ln = galaxy_.lanes[li];
        if (ln.a != star && ln.b != star) continue;
        const int far = (ln.a == star) ? ln.b : ln.b == star ? ln.a : -1;
        if (far < 0) continue;
        // (a) visibility: original tests the far star's +0x17 (SELECT mask,
        // starSelVis_ analog) against 1<<(playerIdx&0x1f) ONLY — allied bits
        // do NOT satisfy it (the presence test below is where allies are
        // forgiven). Star reveal law: debugflags.md STAR REVEAL.
        if (!(starSelVis_[far] & viewerMaskFor(kPlayer))) continue;
        // (b) presence: original rejects the lane iff
        //     (far+0x14 | far+0x15) & ~(allied | 1<<player) & 0x7f  != 0.
        // The mask pair measured == races owning a planet at that star
        // (48/50 on the production save; the 2 exceptions are partial/multi-
        // owner presence the rewrite cannot express — owner_ is ONE owner per
        // star, so a contested star reads as its owner here [documented]).
        const int fo = owner_[far];
        if (fo != kPlayer && fo >= 0 && !((allowedMask >> fo) & 1u)) continue;
        // (c) contest: the original breaks the lane scan on any live ship with
        //     +0x59 == this lane pointer, owner != player, relation != 3
        //     (ALLIANCE, OQ-023). MEASURED: kind-5 (lane) orders really do hold
        //     lane-pool pointers (scripts/r284_contest_census.py re-read under
        //     the pointer law), so the rewrite's transit crossing this lane is
        //     the faithful analog.
        bool contested = false;
        for (const ShipInTransit& sh : fleet_) {
            if (sh.owner == kPlayer || sh.owner < 0) continue;
            if ((allowedMask >> sh.owner) & 1u) continue;   // allied traffic is free
            if ((sh.from == ln.a && sh.target == ln.b) ||
                (sh.from == ln.b && sh.target == ln.a)) { contested = true; break; }
        }
        if (contested) continue;
        laneDone[li] = 1;      // the original's lane rec+0x21 mark (per-pass)
        ++count;               // state->[+0x354eb] += 1
        floodControlled(far, laneDone, allowedMask, count);
    }
}

// t284 — the FUN_00024f24 TAIL: clear marks, seed from home presence, flood.
// Cadence is the law: this runs ONLY in the end-of-turn pass, which is why
// every banked post-load slot reads V==0 (score.md S10 #2) and why t283's
// watchpoint fired +3.1-3.3 s after NEXTTURN and never on idle.
void Campaign::recomputeScoreStars() {
    std::vector<char> laneDone(galaxy_.lanes.size(), 0);   // mark clear
    const int home = (kPlayer < static_cast<int>(homeStar_.size())) ? homeStar_[kPlayer] : -1;
    // Original gate: home star +0x14 bit for the player. owner_ proxy [as (b)].
    if (home < 0 || owner_[home] != kPlayer) { scoreStars_ = 0; return; }
    unsigned allowed = 1u << kPlayer;
    for (int o = 1; o < Nowner_; ++o)
        if (dipState_[o - 1].allied) allowed |= 1u << o;    // relation cell == 3
    int count = 1;             // the home system itself counts as 1
    floodControlled(home, laneDone, allowed, count);
    scoreStars_ = count;
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
