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
        struct Row { int w[4]; };
        static const Row kRows[11] = {
            {{100,0,0,0}},   {{50,2,2,2}},   {{20,3,5,3}},   {{0,3,20,3}},
            {{40,10,2,2}},   {{20,20,2,2}},  {{40,2,2,10}},  {{20,3,3,20}},
            {{40,10,10,10}}, {{20,15,15,15}},{{0,33,34,33}},
        };  // 0x744f4 rows [verified identical in all captures]
        // +0x18 surface counts per size class 0..4: the original sums 15
        // table bytes 0x744a8[15*size+j] (@0x37de3 loop); only the row SUMS
        // are verified against live +0x18 (7/11/23/45/73, exact on sampled
        // planets), the per-byte split is not observed — carried as sums.
        static const int kSurfaceBySize[5] = {7, 11, 23, 45, 73};
        for (int s = 0; s < n; ++s) {
            const int size = next() % 5;  // rng%5 @0x23a86/95
            const int row = next() % 11;  // rng%11 @0x23a97/aa8
            const int cells = kSurfaceBySize[size];  // +0x18 analog
            planets_[s].surfaceCells = cells;
            auto scaled = [](int w) { return (w * 32768 - w) / 100; };
            const int lim[4] = {scaled(kRows[row].w[0]), scaled(kRows[row].w[1]),
                                scaled(kRows[row].w[2]), scaled(kRows[row].w[3])};
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
                cls[next() % cells] |= 8;  // +0x66 |= 2 has no consumer
                                           // in the rewrite; not stubbed
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
    std::vector<int> legal;
    for (int c = 0; c < ps.surfaceCells; ++c) {
        if (used[c] || (ps.cellClasses[c] & 8)) continue;
        if (szc >= 0 && !cellActiveNeighbour(active, szc, ps.surfaceCells, c))
            continue;
        legal.push_back(c);
    }
    if (legal.empty()) return -1;
    return legal[worldNext() % legal.size()];
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
    // doubling, never compressed (S6).
    const ChannelAcc a = channelAccFor(star);
    return static_cast<int>(colonyChannel(a.res, a.dblR, /*compress=*/false));
}

int Campaign::storedProsFor(int star) const {
    // +0x48 DISPLAY-WORD analog (income-law.md T34, 2720 stored samples):
    // max(1, PROS accumulator (class bonuses gated per T35) + richPros -
    // pop>>2-floor). The grant floor-1 and the pop deduction are MEASURED
    // (0-clamp scores 40.99% vs 94.82%; gov switch at +0x54 dead — queue
    // id). T37b: this WORD is also the GROWTH-COUNTER INPUT (corpus
    // battery scripts/r1_pros_growth.py VERDICT disp, raw/gated
    // eliminated 3/5) — incomeAndGrow charges it directly, matching
    // FUN_00038f68 @0x39302, and needClassFor (FUN_0003fec4 reads the
    // +0x48 WORD) sees the same value the original's selector saw.
    double pros = planets_[star].richPros + channelAccFor(star).pros;
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
    // capBonus keeps SA_MoreMaxPop [documented default; the original's
    // ability site is not yet lifted].
    const PlanetState& ps = planets_[star];
    int mpopSum = 0;
    for (int it : ps.items) {
        mpopSum += (*items_)[it].mpop;
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
                if (itemIsSurface(ps.pendingItem)) {
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
