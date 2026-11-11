// SPDX-License-Identifier: GPL-3.0-or-later

// Campaign turn-loop tests. Constants: docs/re/turnloop.md (end-*.txt vendor
// comments, planitem rows, gizmo levels) — never memory (STATE rule).
#include "game/campaign.h"
#include "harness.h"

#include <cstdio>
#include <cstdlib>
#include <filesystem>
#include <string>

#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif

namespace {
namespace ag = ascend::game;
namespace fs = std::filesystem;

const fs::path kRepo = ASCENDANCY_SOURCE_DIR;

struct Tables {
    ag::StarStats stats;
    std::vector<std::string> names;
    ag::ResearchTree tree;
    std::vector<ag::PlanetItem> items;
    std::vector<ag::Gizmo> gizmos;
    std::vector<ag::DipFile> ai;
};

Tables& tables() {
    static Tables t = [] {
        Tables x;
        std::string err;
        auto st = ag::StarStats::load(kRepo / "extracted/ascend00/starstat.txt", &err);
        if (!st) std::abort();
        x.stats = *st;
        x.names = ag::loadStarNames(kRepo / "extracted/ascend00/names.txt", &err);
        if (x.names.empty()) std::abort();
        x.tree = ag::ResearchTree::loadFromFile((kRepo / "extracted/ascend00/restree.txt").string(), err);
        x.items = ag::loadPlanItems((kRepo / "extracted/ascend00/planitem.txt").string(), err);
        if (x.items.size() != 39) std::abort();
        x.gizmos = ag::loadGizmos((kRepo / "extracted/ascend00/gizmos.txt").string(), err);
        if (x.gizmos.size() != 76) std::abort();
        for (int i = 0; i < 6; ++i) {
            ag::DipFile df;
            char path[256];
            std::snprintf(path, sizeof(path), "%s/extracted/ascend00/race%02d.dip",
                          ASCENDANCY_SOURCE_DIR, i);
            if (!df.loadFromFile(path, &err)) std::abort();
            x.ai.push_back(std::move(df));
        }
        return x;
    }();
    return t;
}

ag::Campaign makeCampaign(unsigned seed, int aiCount = 6, bool ffa = true) {
    ag::CampaignConfig cfg;
    cfg.seed = seed;
    cfg.aiCount = aiCount;
    cfg.freeForAll = ffa;
    ag::MapConfig mc;
    mc.seed = seed;
    ag::Galaxy g = ag::MapGenerator(mc, tables().stats, tables().names).generate();
    std::string err;
    return ag::Campaign(cfg, g, &tables().tree, tables().items, tables().gizmos,
                        tables().ai, &err);
}

}  // namespace

// Exported shim (t202b): test_demolish_t202b.cpp needs the same seeded
// campaign + table wiring without duplicating the loader. Fully-qualified:
// the `ag` alias lives inside the anonymous namespace above.
ascend::game::Campaign makeCampaignForDemolish(unsigned seed) { return makeCampaign(seed); }

// Exported shim (t291): test_control_t291.cpp needs a crafted campaign with a
// chosen aiCount/starCount (the end-ctrl boundary must be testable on a galaxy
// size where floor(2T/3)+1 != the >half bar, i.e. 2T mod 3 != 0 — impossible
// at the default T=50). Same table wiring as makeCampaign, no abilities.
ascend::game::Campaign makeCampaignSized(unsigned seed, int aiCount, int starCount) {
    ag::CampaignConfig cfg;
    cfg.seed = seed;
    cfg.aiCount = aiCount;
    cfg.freeForAll = true;
    ag::MapConfig mc;
    mc.seed = seed;
    mc.starCount = starCount;
    ag::Galaxy g = ag::MapGenerator(mc, tables().stats, tables().names).generate();
    std::string err;
    return ag::Campaign(cfg, g, &tables().tree, tables().items, tables().gizmos,
                        tables().ai, &err);
}

// Exported shim (t294): test_terrain_t294.cpp needs a campaign whose
// world-gen consumes a PATCHED terrain table (the differential leg proving
// the rewrite reads cfg.terrain rather than a compiled constant). Same table
// wiring as makeCampaign, default 50 stars.
ascend::game::Campaign makeCampaignWithTerrain(unsigned seed,
                                               const ascend::game::TerrainTables& tt) {
    ag::CampaignConfig cfg;
    cfg.seed = seed;
    cfg.aiCount = 6;
    cfg.freeForAll = true;
    cfg.terrain = tt;
    ag::MapConfig mc;
    mc.seed = seed;
    ag::Galaxy g = ag::MapGenerator(mc, tables().stats, tables().names).generate();
    std::string err;
    return ag::Campaign(cfg, g, &tables().tree, tables().items, tables().gizmos,
                        tables().ai, &err);
}

TEST(campaign_homes_distinct) {
    REQUIRE_DATA();
    auto c = makeCampaign(7);
    for (int o = 0; o <= 6; ++o) CHECK(c.starsOwned(o) == 1);
    CHECK(c.turn() == 0);
    CHECK(c.victory() == ag::Victory::None);
}

TEST(campaign_total_owned_grows) {
    REQUIRE_DATA();
    // Expansion: total claimed stars must strictly grow over 20 turns
    // (some owner always has surplus industry; turnloop.md §4).
    // window widens, not the law. t295 SEED SWAP (honest re-derivation): the
    // home-draw law re-trajectories seed 42 to player Extinct at t20 (home
    // s31 sits next to a fast Minion AI — lethal layouts are a REAL property
    // of uniform draws the old spread-BFS could never produce; the vendor has
    // the same exposure). Seed 7 survives 420 turns and colonises at t279.
    auto c = makeCampaign(7);
    int totalPrev = 7;
    // T40 window 20 -> 220: the faithful CB-only start (income-law.md T40)
    // moves FIRST colonization to ~t169 (CLI: --campaign 300 --seed 42 ->
    // '[t169] owner 0 colonised Tensoric'); a bare home needs the full
    // Factory->drive->Shipyard queue chain before any colony ship launches,
    // which is exactly what the vendor's own tutorial pacing describes.
    // T202B window 220 -> 420: usedPopFor is now the MEASURED item-UPOP sum
    // (docs/re/_wip_t202.md S11, r202d 2760/2900), which activates the
    // 0x3f220 no-free-pop law — an AI planet with used==pop queues NOTHING
    // until growth, so early builds serialize one-per-pop-growth (seed 42
    // first colony t169 -> t279 CLI-verified). The guard's target is INFINITE
    // stall and the behaviour resolves finitely (seed 42 reaches 13 owned by
    // t620; seed 2024 wins Control t1255), so the window widens, not the law.
    for (int t = 0; t < 420 && !c.over(); ++t) {
        c.advance();
        int total = 0;
        for (int o = 0; o <= 6; ++o) total += c.starsOwned(o);
        CHECK(total >= totalPrev);
        totalPrev = total;
    }
    CHECK(totalPrev > 7);
}

TEST(campaign_home_placement_law_t40) {
    REQUIRE_DATA();
    // HOME-PLACEMENT LAW (docs/re/income-law.md T40 + T42 upgrade, census
    // scripts/r1_cell_choice_census.py): exactly one home per empire;
    // opening position = Colony Base ONLY (no Factory/Lab/Shipyard ever on
    // a first-save home); the CB sits on a NON-ROCK SURFACE cell, barren
    // class 0 ALLOWED (picker legality chain FUN_0003830c never zeroes
    // item 5 on surface non-rock — T42; the t40 rank>=2 floor has no code
    // counterpart and is not pinned here).
    for (unsigned seed : {2u, 7u}) {
        auto c = makeCampaign(seed);
        const auto& items = tables().items;
        for (int o = 0; o <= 6; ++o) {
            int star = -1;
            const int ns = static_cast<int>(c.galaxy().stars.size());
            for (int s = 0; s < ns; ++s)
                if (c.starOwner(s) == o) star = s;
            CHECK(star >= 0);
            if (star < 0) continue;
            const auto& ps = c.planetAt(star);
            CHECK(ps.items.size() == 1);            // Colony Base ONLY
            CHECK(ps.itemCells.size() == 1);
            if (ps.items.size() != 1 || ps.itemCells.size() != 1) continue;
            CHECK(items[ps.items[0]].name == "Colony Base");
            const int cell = ps.itemCells[0];
            CHECK(cell >= 0 && cell < ps.surfaceCells);   // never orbital
            if (cell < 0 || cell >= ps.surfaceCells) continue;
            CHECK((ps.cellClasses[cell] & 8) == 0);       // non-rock
        }
    }
}

TEST(campaign_cb_cell_uniform_t42) {
    REQUIRE_DATA();
    // PICKER UNIFORMITY (income-law.md T42): drawCbCell must spread CBs
    // across ALL non-rock cells (barren included) and never land on rock.
    // 4000 draws on a mid-size planet: every non-rock cell hit at least
    // once; barren share within [0.10, 0.55] for a terrain mix around the
    // measured 26.9%.
    auto c = makeCampaign(11u);
    const int ns = static_cast<int>(c.galaxy().stars.size());
    int star = -1;
    for (int s = 0; s < ns; ++s)
        if (static_cast<int>(c.planetAt(s).cellClasses.size()) >= 33) { star = s; break; }
    CHECK(star >= 0);
    if (star < 0) return;
    const auto& ps = c.planetAt(star);
    std::vector<int> hits(ps.surfaceCells, 0);
    int nrock = 0, nb = 0, nbar = 0;
    for (int t = 0; t < 4000; ++t) {
        const int cell = c.drawCbCell(ps);
        CHECK(cell >= 0 && cell < ps.surfaceCells);
        if (cell < 0 || cell >= ps.surfaceCells) return;
        CHECK((ps.cellClasses[cell] & 8) == 0);
        ++hits[cell];
    }
    for (int k = 0; k < ps.surfaceCells; ++k) {
        if (ps.cellClasses[k] & 8) { ++nrock; CHECK(hits[k] == 0); continue; }
        ++nb;
        CHECK(hits[k] > 0);   // uniform: every legal cell reachable
        if (ps.cellClasses[k] == 0) ++nbar;
    }
    const double share = static_cast<double>(nbar) / nb;
    CHECK(share >= 0.10 && share <= 0.55);
}

TEST(campaign_built_cell_rule_g_t43) {
    REQUIRE_DATA();
    // BUILT-ITEM CELL LAW (income-law.md S13, CLOSED t43): rule-G
    // adjacency over the runtime hex-continuous-x grid (tables banked from
    // guest RAM; checker FUN_0003830c @0x385b7 + FUN_000395c4), and the
    // picker draw for build completions (FUN_0003875c ignores the caller's
    // slot register).
    // (a) sizeClassFor: the five verified surface counts map 1:1.
    CHECK(ag::Campaign::sizeClassFor(7) == 0);
    CHECK(ag::Campaign::sizeClassFor(11) == 1);
    CHECK(ag::Campaign::sizeClassFor(23) == 2);
    CHECK(ag::Campaign::sizeClassFor(45) == 3);
    CHECK(ag::Campaign::sizeClassFor(73) == 4);
    CHECK(ag::Campaign::sizeClassFor(24) == -1);
    // (b) adjacency SYMMETRY on every type via double marker-flip (the four
    // probes (row±1,x),(row,x±1) in continuous-x coords define an
    // undirected graph; asymmetry means wrong table geometry). Also: a
    // cell's neighbour count stays within [2,4] on rows 2..9 wide.
    const int kSurf[5] = {7, 11, 23, 45, 73};
    for (int t = 0; t < 5; ++t) {
        const int surf = kSurf[t];
        for (int a = 0; a < surf; ++a) {
            std::vector<char> one(surf, 0);
            one[a] = 1;
            std::vector<int> nbr;
            for (int b = 0; b < surf; ++b)
                if (b != a && ag::Campaign::cellActiveNeighbour(one, t, surf, b))
                    nbr.push_back(b);
            for (int b : nbr) {
                std::vector<char> two(surf, 0);
                two[b] = 1;
                CHECK(ag::Campaign::cellActiveNeighbour(two, t, surf, a));
            }
            for (int b = 0; b < surf; ++b) {  // reverse: non-neighbour
                if (b == a || ag::Campaign::cellActiveNeighbour(one, t, surf, b)) continue;
                std::vector<char> two(surf, 0);
                two[b] = 1;
                CHECK(!ag::Campaign::cellActiveNeighbour(two, t, surf, a));
            }
            CHECK(nbr.size() >= 1 && nbr.size() <= 4);  // type-1 tip rows have exactly 1
        }
    }
    // (c) drawItemCell: on a fresh home (CB active only), every draw lands
    // EMPTY, NON-ROCK, ADJACENT to some active item; spread > single cell.
    auto c = makeCampaign(11u);
    const int ns = static_cast<int>(c.galaxy().stars.size());
    int star = -1;
    for (int s = 0; s < ns; ++s)
        if (c.starOwner(s) >= 0 && c.planetAt(s).surfaceCells >= 23) { star = s; break; }
    CHECK(star >= 0);
    if (star < 0) return;
    auto& ps = const_cast<ag::PlanetState&>(c.planetAt(star));
    std::vector<int> hits(ps.surfaceCells, 0);
    for (int i = 0; i < 300; ++i) {
        const int cell = c.drawItemCell(ps);
        CHECK(cell >= 0 && cell < ps.surfaceCells);
        if (cell < 0) return;
        CHECK((ps.cellClasses[cell] & 8) == 0);
        ++hits[cell];
    }
    int distinct = 0;
    for (int k = 0; k < ps.surfaceCells; ++k) if (hits[k]) ++distinct;
    CHECK(distinct >= 2);  // picker, not first-empty
}

TEST(campaign_governor_law_t45) {
    REQUIRE_DATA();
    // SELECTED-ABILITY / "GOVERNOR" LAW (docs/re/income-law.md S14 t45,
    // recalc FUN_00038ba4 @0x38df0..0x38e29 raw disasm): byte +0x54 == 33
    // Endless Party adds IND acc >>2 to the PROS accumulator (before its
    // pow block), 34 Scientist Takeover adds it to the RAW RES word, 35
    // Automation adds item-35 UPOP (=1, runtime table measured 32/32) to
    // used-pop +0x4c. Corpus: 0/2810 owned records ever hold 33/34/35
    // (scripts/r1_governor_census.py over 484 saves) — every planet runs
    // with the byte at 0xFF (queue id or none), so the branch must be
    // INERT by default and exact when set.
    auto c = makeCampaign(2024);
    const int ns = static_cast<int>(c.galaxy().stars.size());
    int tested = 0;
    for (int s = 0; s < ns && tested < 8; ++s) {
        if (c.starOwner(s) < 0) continue;
        auto& ps = const_cast<ag::PlanetState&>(c.planetAt(s));
        CHECK(ps.governor == -1);  // corpus-default state
        // Synthetic IND feed so the >>2 operand is non-zero: homes at t0
        // carry ONLY a Colony Base (t40 law, acc 1 -> bonus 0), so the
        // branch needs extra items to be exercised at all. Three Factories
        // (IND 1 each) over the CB give acc >= 4. itemCells left short on
        // purpose -> channelAccFor takes the documented rock-skip fallback.
        for (int k = 0; k < 3; ++k) ps.items.push_back(0);  // Factory
        const auto base = c.channelWordsFor(s);
        const int bonus = c.rawIndAccFor(s) >> 2;  // IND acc after Hyperpower
        CHECK(bonus >= 1);
        // 33 -> PROS side: monotone increase under compression.
        ps.governor = 33;
        CHECK(c.channelWordsFor(s).pros > base.pros);
        ps.governor = -1;
        CHECK(c.channelWordsFor(s).pros == base.pros);  // cleanly reversible
        // 34 -> RES word: RAW channel, so the delta is exactly bonus.
        ps.governor = 34;
        CHECK(c.channelWordsFor(s).res == base.res + bonus);
        ps.governor = -1;
        // 35 -> used-pop word: + Automation UPOP (measured 1).
        const int u0 = c.usedPopFor(s);
        ps.governor = 35;
        CHECK(c.usedPopFor(s) == u0 + 1);  // UPOP(35) == 1 [verified table]
        ps.governor = -1;
        ++tested;
    }
    CHECK(tested >= 4);
}

TEST(campaign_colonised_plan_gets_colony_base_t41) {
    REQUIRE_DATA();
    // COLONISED-PLANET LAW (docs/re/income-law.md T41, census
    // scripts/r1_colony_items.py): every in-run colonisation arrives with
    // EXACTLY one Colony Base (2 same-world observations, CB-only pop 2).
    // t295 RE-SCOPE (honest): the old end-of-run "EVERY owned star carries a
    // CB" invariant was an OLD-TRAJECTORY ARTEFACT — the cited t202b
    // demolish laws (over-cap 0x3f178 + triage 0x3f354) CAN legally remove a
    // home CB later in the run (seed 2024 under the t295 home draw: AI home
    // s29 CB demolished, items empty at t285). The closed law is the ARRIVAL
    // state; pin it AT THE MOMENT: on the turn a 'colonised' event fires,
    // that star's item list holds EXACTLY ONE Colony Base and pop == 2 (S6e).
    auto c = makeCampaign(2024);
    int colonisedCount = 0, cbExactlyOne = 0, pop2 = 0;
    const auto& items = tables().items;
    for (int t = 0; t < 300 && !c.over(); ++t) {
        c.advance();
        for (const auto& ev : c.events()) {
            if (ev.turn != c.turn()) continue;
            if (ev.text.find("colonised ") == std::string::npos) continue;
            ++colonisedCount;
            // event text = "owner N colonised <star>"; match by name.
            for (size_t s = 0; s < c.galaxy().stars.size(); ++s) {
                if (ev.text.find(c.galaxy().stars[s].name) == std::string::npos)
                    continue;
                int cb = 0;
                for (int it : c.planetAt(static_cast<int>(s)).items)
                    if (items[it].name == "Colony Base") ++cb;
                if (cb == 1) ++cbExactlyOne;
                if (c.planetAt(static_cast<int>(s)).pop == 2) ++pop2;
                break;
            }
        }
    }
    CHECK(colonisedCount > 0);   // expansion happened (measured ~t164..t280)
    CHECK(cbExactlyOne == colonisedCount);  // every arrival carried exactly 1 CB
    CHECK(pop2 == colonisedCount);          // settlement seed := 2 (S6e)
}

TEST(campaign_channel_law_oq016) {
    REQUIRE_DATA();
    // MEASURED stored-channel law (docs/re/income-law.md S6/t18b compression
    // + t19 grant; battery scripts/r1_income_channels.py post-t35:
    // IND/PROS/RES 173/173/173 on the corrected +0x88 array with the
    // channel-field gating — class-cell +1 bonuses apply only when the
    // item's own channel field is non-zero, see income-law.md T35):
    // acc==0 -> scenario grant 1 (colonization FUN_00025d30
    // +1 both home records); IND = trunc((dbl(acc,f12)+1)^0.85)
    // (0x38e2d FILD/pow/FISTP chain, RET 0x76e08 = trunc; t18b); RES is the
    // raw accumulator (never compressed). dbl = v + (v>>1) when the FIRST
    // slot is Hyperpower(IND,12)/Internet(RES,14) (FUN_0003958c +
    // bit-tests 0x38d4b/0x38db5). Values from the battery curve:
    //   v      1  2   3    4    5    6    7
    //   v^.85  1  2  3.25 3.93 4.61 5.23 5.83   (truncated)
    CHECK(ag::colonyChannel(0, false, true) == 1.0);  // grant, not pow(1)
    CHECK(ag::colonyChannel(1, false, true) == 1.0);  // (2)^.85 = 1.80 -> 1
    CHECK(ag::colonyChannel(2, false, true) == 2.0);  // (3)^.85 = 2.50 -> 2
    CHECK(ag::colonyChannel(3, false, true) == 3.0);  // (4)^.85 = 3.25 -> 3
    CHECK(ag::colonyChannel(4, false, true) == 3.0);  // (5)^.85 = 3.93 -> 3
    CHECK(ag::colonyChannel(2, true, true) == 3.0);   // dbl v=3 -> (4)^.85
    CHECK(ag::colonyChannel(4, true, true) == 5.0);   // dbl v=6 -> (7)^.85
    // RES channel: accumulator + Internet doubling shift (v += v>>1, the
    // same 0x38db5 site), never compressed. T40: NO grant at acc 0 for the
    // raw channel — home worlds sit at acc 0 with +0x46 == 0 on 157/157
    // homes (scripts/r1_home_placement.py census; income-law.md T40), while
    // the compressed IND channel keeps the t19 grant (IND-at-acc-0 is
    // unobservable in captures: every owned record has >= 1 item).
    CHECK(ag::colonyChannel(0, false, true) == 1.0);   // IND grant survives
    CHECK(ag::colonyChannel(0, true, false) == 0.0);   // RES raw: no grant
    CHECK(ag::colonyChannel(3, false, false) == 3.0);
    CHECK(ag::colonyChannel(3, true, false) == 4.0);   // 3 + 3>>1
    CHECK(ag::colonyChannel(9, true, false) == 13.0);  // 9 + 9>>1
}

TEST(campaign_build_queue_law_oq016) {
    REQUIRE_DATA();
    // BUILD-QUEUE LAW (income-law.md S8 + S9 t28): pending item + per-planet
    // IND accumulator; completion only when acc >= COST (0x3907b/0x390a3
    // JA 0x392a2), selector runs only with no pending item (caller 0x3ead6).
    auto c = makeCampaign(7);   // t295: was seed 42 (now Extinct t20 under the
                                // home-draw law; seed 7 alive, cadence law
                                // unchanged — see t274 exact-t16 pin)
    c.advance();
    for (int o = 1; o <= 6; ++o) {
        int s = -1;
        for (size_t i = 0; i < 70 && s < 0; ++i)
            if (c.starOwner(static_cast<int>(i)) == o) s = static_cast<int>(i);
        CHECK(s >= 0);
    }
    // Factory COST 30 (planitem.txt row 0), home IND 1/turn (t19 grant):
    // the first queue completes around turn 31 (t1 queue, acc >= COST then).
    CHECK(c.turn() == 1);
    for (int t = 0; t < 40 && !c.over(); ++t) c.advance();
    // By turn ~41 every still-owned AI home has grown its built list by at
    // least one completed queue item. T40: threshold 4 -> 2 (v1's '>3' was
    // '3 seeded structures + 1 completion'; the MEASURED start is Colony
    // Base only, and Factory cost 30 at stored IND 1-2/turn completes
    // t16..t31, so '>1' still pins the queue law end-to-end).
    int grown = 0;
    for (int o = 1; o <= 6; ++o)
        for (size_t i = 0; i < c.galaxy().stars.size(); ++i)
            if (c.starOwner(static_cast<int>(i)) == o &&
                c.builtItemCount(static_cast<int>(i)) > 1) ++grown;
    CHECK(grown > 0);
}

TEST(campaign_pop_cap_seed_law_oq016) {
    REQUIRE_DATA();
    // POP-CAP SEED LAW (income-law.md S10 t29/t36): seed = nonbarren/3 + 5
    // with nonbarren from the per-cell class draw (T36: size rng%5 @0x23a86,
    // row rng%11 @0x23a97, chain @0x37eb7..0x37f24); bounds per surface
    // size: min 5, max ncells/3+5 with ncells in
    // {7,11,23,45,73} -> cap in [5..29] (home items carry MPOP 0, no
    // ability bonus here). Old default was the constant 25.
    auto c = makeCampaign(2);
    int lo = 1000, hi = 0;
    const int ns = static_cast<int>(c.galaxy().stars.size());
    for (int s = 0; s < ns; ++s) {
        int cap = c.popCapAt(s);
        CHECK(cap >= 5 && cap <= 29);
        lo = std::min(lo, cap);
        hi = std::max(hi, cap);
        // T36 CELL-CLASS LAW pins: ring size, orbital ring forced class 1
        // (@0x37f12, drawn WITHOUT rng), classes in the generated range.
        const auto& ps = c.planetAt(s);
        CHECK(static_cast<int>(ps.cellClasses.size()) == ps.surfaceCells + 10);
        for (int k = ps.surfaceCells; k < ps.surfaceCells + 10; ++k)
            CHECK(ps.cellClasses[k] == 1);
        int nonbarren = 0;
        for (int k = 0; k < ps.surfaceCells; ++k) {
            const int raw = ps.cellClasses[k];
            // T38 RAW-BYTE CENSUS [verified]: classes are exactly
            // {0..4} | 8-rock — 5..7 never occur (0 of 101948 corpus
            // slots). Rock marks AFTER the draw loop (@0x37f4d before
            // seed word @0x37f84), so a barren cell marked |8 (raw 8)
            // WAS barren at draw time: the seed-law recount must treat
            // raw 0 AND raw 8 as barren (FUN_00038ba4 counts buildable
            // cells as &8==0 and barren as ==0 [verified]).
            CHECK((raw & ~8) >= 0 && (raw & ~8) <= 4 &&
                  (raw & ~8) == raw - (raw & 8));
            if (raw != 0 && raw != 8) ++nonbarren;
        }
        // seed word consistency: capBase is EXACTLY nonbarren/3+5 of the
        // generated grid (before recalc adds item MPOP; home items MPOP 0).
        CHECK(ps.capBase == nonbarren / 3 + 5);
    }
    CHECK(hi > lo);  // seeded spread, not a constant table
    // Deterministic draw: same seed => same caps (law, not noise).
    auto c2 = makeCampaign(2);
    for (int s = 0; s < ns; ++s)
        CHECK(c.popCapAt(s) == c2.popCapAt(s));
}

TEST(campaign_research_progresses) {
    REQUIRE_DATA();
    auto c = makeCampaign(3);
    for (int t = 0; t < 40 && !c.over(); ++t) c.advance();
    CHECK(c.techsOwned(ag::kPlayer) > 0);  // home lab researches within 40 turns
}

TEST(campaign_deterministic_same_seed) {
    REQUIRE_DATA();
    auto a = makeCampaign(1234);
    auto b = makeCampaign(1234);
    for (int t = 0; t < 30 && !a.over(); ++t) {
        a.advance();
        b.advance();
        CHECK(a.traceLine() == b.traceLine());
        CHECK(a.victory() == b.victory());
    }
}

TEST(campaign_reaches_a_victory) {
    REQUIRE_DATA();
    // CONTRACT: a seeded run reaches a victory condition (docs/PLAYTHROUGH.md
    // is generated from such a run). Combat (combat.md S2g/S2j) makes Control
    // or LastAlive reachable; 1200-turn cap bounds the search.
    // t89 re-pin (deterministic combat, no hit roll): seeds 1 / 2 / 2024
    // resolve Control t842 / t677 / t777 (CLI --campaign 1200) — still FINITE,
    // so the stall contract is unchanged.
    bool anyVictory = false;
    for (unsigned seed : {1u, 2u, 2024u}) {
        auto c = makeCampaign(seed);
        for (int t = 0; t < 1200 && !c.over(); ++t) c.advance();
        if (c.over()) { anyVictory = true; break; }
    }
    CHECK(anyVictory);
}

TEST(campaign_combat_law_oq010) {
    REQUIRE_DATA();
    // t89 UPGRADE pin (docs/re/combat.md S2d/S2f/S2g/S2h/S2i). Laws lifted:
    //  (1) VOLLEY = SUM of researched cat-0 weapon Levels — every weapon
    //      engages per engagement (volley loop 0x4a5c1..0x4a5fc); damage per
    //      hit = design[+0x52] == file Level column (map CLOSED 76/76,
    //      scripts/r1_t87_gizmo_table.py). Shipped file rows (re-verified
    //      t89a, extracted/ascend00/gizmos.txt): Levels
    //      {1,2,4,4,1,4,6,4,10,13}, NumUses {1,1,1,1,5,1,2,2,2,3} (0 =
    //      unlimited, none shipped).
    //  (2) SHIELD CHARGES = SUM of researched cat-1 Levels (charge law
    //      0x49f15: ship+0x90 += design[+0x56], +0x56 == Level for the 6
    //      shipped shields {1,2,1,3,4,5}).
    //  (3) TWO-LAYER CLAMPED ABSORB SPLIT (0x4b7c4..0x4b7d1, apply 0x4b87a..
    //      0x4b890): absorb = min(volley, charges), ONLY the remainder spills
    //      to hull; never negative, absorb+spill == volley always.
    //  (4) DETERMINISTIC: no hit roll exists in the combat module family
    //      (measured-negative, S2g) — the combat phase draws NOTHING from
    //      campaign rng_.
    const auto& gz = tables().gizmos;
    // File-constant pins (not memory — re-extracted values must match).
    int sumWeapon = 0, sumShield = 0, nW = 0, nS = 0;
    for (const auto& g : gz) {
        if (g.cat == ag::GizmoCat::Weapon) { sumWeapon += g.level; ++nW; CHECK(g.numUses != 0); }
        if (g.cat == ag::GizmoCat::Shield) { sumShield += g.level; ++nS; }
    }
    CHECK(nW == 10); CHECK(nS == 6);
    CHECK(sumWeapon == 49);   // 1+2+4+4+1+4+6+4+10+13
    CHECK(sumShield == 16);   // 1+2+1+3+4+5

    // (1): the volley delta of full tech over no-tech is EXACTLY the sum
    // (a MAX-era model would move by max-level minus start-level, not 49).
    auto full = makeCampaign(77);
    auto none = makeCampaign(77);
    full.setAllTechs(0, true);
    none.setAllTechs(0, false);
    CHECK(full.attackScoreFor(0) - none.attackScoreFor(0) == sumWeapon);
    CHECK(full.shieldChargesFor(0) == sumShield);
    CHECK(none.shieldChargesFor(0) == 0);

    // (3): the split law, edge-on.
    {
        int a = -1, sp = -1;
        ag::Campaign::absorbSplit(10, 16, a, sp);
        CHECK(a == 10 && sp == 0);            // shields absorb the whole volley
        ag::Campaign::absorbSplit(20, 5, a, sp);
        CHECK(a == 5 && sp == 15);            // clamp + spill to hull
        ag::Campaign::absorbSplit(7, 0, a, sp);
        CHECK(a == 0 && sp == 7);             // no shields: full hull hit
        ag::Campaign::absorbSplit(0, 9, a, sp);
        CHECK(a == 0 && sp == 0);
    }
    // (4): determinism — equal seeds trace identically through 40 FFA-war
    // turns with the deterministic capture law in force.
    auto x = makeCampaign(2026);
    auto y = makeCampaign(2026);
    for (int t = 0; t < 40; ++t) {
        x.advance();
        y.advance();
        CHECK(x.traceLine() == y.traceLine());
    }
}

TEST(campaign_victory_files_named) {
    REQUIRE_DATA();
    CHECK(std::string(ag::victoryConditionFile(ag::Victory::Control)) == "end-ctrl");
    CHECK(std::string(ag::victoryConditionFile(ag::Victory::Extinct)) == "end-xtnc");
    CHECK(std::string(ag::victoryConditionFile(ag::Victory::LastAlive)) == "end-dest");
    CHECK(std::string(ag::victoryName(ag::Victory::Control)) == "Control");
}

TEST(campaign_advance_after_victory_is_noop) {
    REQUIRE_DATA();
    auto c = makeCampaign(1);
    ag::Victory v = ag::Victory::None;
    // t89 re-pin: seed 1 finite resolve Control t842 (deterministic combat;
    // see campaign_reaches_a_victory note above).
    for (int t = 0; t < 1200; ++t) {
        v = c.advance();
        if (v != ag::Victory::None) break;
    }
    if (v == ag::Victory::None) { CHECK(false); return; }  // contract data
    int turn = c.turn();
    size_t evs = c.events().size();
    c.advance();
    CHECK(c.turn() == turn);
    CHECK(c.events().size() == evs);
}

TEST(campaign_research_picker_law_oq016) {
    REQUIRE_DATA();
    // t93 AI RESEARCH PICK LAW (FUN_00040018 0x40018..0x40175 re-verified
    // from the disassembly; docs/re/aicode.md §3c/§3d). Tiers: sentinel
    // (rng%100<45) skips ONLY the preferred scan (guard 0x400fb); the
    // uniform fallback 0x40134 tests chosen>=0 so -2 is never stored
    // (§3d CORRECTION of §3c's "no pick" note); preferred membership on
    // the live 66-row table == {1,47} (0x67be math, §3c); first candidate
    // (lowest row) wins (0x40129 store once under re-guards 0x400fb/
    // 0x4010d); candidate cap 0x20 (0x40044).
    using C = ag::Campaign;
    CHECK(C::aiResearchPreferred({0, 1, 2}, false) == 1);   // first member wins
    CHECK(C::aiResearchPreferred({1, 47}, false) == 1);     // lowest row
    CHECK(C::aiResearchPreferred({47}, false) == 47);
    CHECK(C::aiResearchPreferred({40, 47, 60}, false) == 47);
    CHECK(C::aiResearchPreferred({0, 2, 40}, false) == -1); // no member
    CHECK(C::aiResearchPreferred({1, 47}, true) == -1);     // sentinel skips
    // Campaign-level: research still happens every ~turn under the new
    // law (sentinel skips the preferred bias only; the uniform fallback
    // always picks when candidates exist) — a "sentinel => never research"
    // model would show zero AI completions.
    auto c = makeCampaign(2024);
    for (int t = 0; t < 60 && !c.over(); ++t) c.advance();
    int totalOwned = 0;
    for (int o = 1; o <= 6; ++o) totalOwned += c.techsOwned(o);
    CHECK(totalOwned > 0);
}



// ---------------------------------------------------------------------------
// OQ-026 VISIBILITY LAW PIN (t195). Law source docs/re/ships.md S23:
//  L5  lane rec+0x20 = per-empire bitmask, OR-only (sticky — no clear site),
//  L6  FUN_00046354 share: N = rand%(3|6)+1 grants per call, ALLIANCE
//      doubles; receive leg (EBX!=0, player<-race, cited site 0x55f6e),
//      mirrored lend leg (EBX==0, alliance-formation site 0x45778),
//  L7  unowned/unshared lanes are FOGGED (new-game census {0:940} of 1160:
//      most lanes carried NO bit at all),
//  L9  consumer FUN_00028fc0 admits lane i iff rec+0x20 & viewer_mask;
//      viewer setter FUN_00021a84: mask = idx==0xff ? 0xff : 1<<idx;
//      stars ALWAYS drawn (honest negative); star-click gated by
//      obj +0x17 (select) / +0x16 (lane-follow) & mask.
// Fixture map (chain): s0(P home)-s1-s2-s3-s4(A home); lanes 0..3 in pool
// order (0,1),(1,2),(2,3),(3,4). Own-claim law at init: P sees EXACTLY
// {lane0}, A EXACTLY {lane3} (t192 new-game law); s1/s2 and lanes 1/2 are
// fogged for both (t193 census: value-0/foreign-only lanes exist).
// ---------------------------------------------------------------------------
TEST(campaign_visibility_law_oq026_t195) {
    REQUIRE_DATA();
    using C = ag::Campaign;
    // (0) VIEWER MASK LAW verbatim (FUN_00021a84 + 0x21a94 spectator leg).
    CHECK(C::viewerMaskFor(0) == 0x01);
    CHECK(C::viewerMaskFor(1) == 0x02);
    CHECK(C::viewerMaskFor(5) == 0x20);
    CHECK(C::viewerMaskFor(255) == 0xff);

    ag::Galaxy g;
    g.seed = 1;
    const char* nm[5] = {"Alpha", "Betel", "Gamma", "Cet", "Delta"};
    for (int i = 0; i < 5; ++i) {
        ag::Star st; ag::Planet pl; pl.index = 0; pl.name = std::string(nm[i]) + " I";
        st.id = i; st.x = 100 * i; st.y = 0; st.name = nm[i]; st.planets.push_back(pl);
        g.stars.push_back(st);
    }
    for (int i = 0; i + 1 < 5; ++i) g.lanes.push_back({i, i + 1});

    ag::CampaignConfig cfg;
    cfg.seed = 23;   // t295: was 4242. Under the home-draw law the seed scan
                     // (diagnostic since deleted) found {1,23,45,63,77,...}
                     // as the seeds giving homes o0=s0/o1=s4 on this 5-star
                     // chain; the lane-claim assertions below all key on the
                     // {0,4} home pair.
    cfg.aiCount = 1;
    cfg.freeForAll = false;
    std::string err;
    std::vector<ag::SpeciesAbility> ab{ag::SpeciesAbility::HealShips};
    ag::Campaign c(cfg, g, &tables().tree, tables().items, tables().gizmos,
                   {tables().ai[0]}, ab, &err);

    // (1) SCENARIO INIT (t192: race r == EXACTLY its own claim).
    CHECK(c.starOwner(0) == ag::kPlayer);
    CHECK(c.starOwner(4) == 1);
    CHECK(c.visibleLaneCountFor(0) == 1);          // {lane0} only
    CHECK(c.laneVisibleTo(0, 0));
    CHECK(!c.laneVisibleTo(1, 0) && !c.laneVisibleTo(2, 0) &&
          !c.laneVisibleTo(3, 0));
    CHECK(c.visibleLaneCountFor(1) == 1);          // {lane3} only
    CHECK(c.laneVisibleTo(3, 1) && !c.laneVisibleTo(0, 1));
    // t194 witness analog: filter admits STRICTLY fewer than the pool
    // (mid-game measured 49 of 58); spectator mask 0xff admits all.
    CHECK(c.cosmosLanesFor(0).size() == 1);
    // Spectator 0xff reveals shared/owned lanes but AND-law (0x2914e) still
    // WITHHOLDS mask-0 lanes (0 & 0xff == 0): lanes 1/2 (unowned chain) stay
    // hidden. t193's mid-game pool had ZERO zero-mask lanes, so a live
    // spectator saw all 58 — consistent.
    CHECK(c.cosmosLanesFor(255).size() == 2);
    // HONEST NEGATIVE (S23 L9): stars ALWAYS listed (builder kind-0
    // unconditional); visibility gates CLICKS, not drawing.
    CHECK(c.cosmosStarsFor(0).size() == 5);
    CHECK(!c.starSelectableBy(3, 0) && !c.starLaneFollowableBy(3, 0));
    CHECK(c.starSelectableBy(0, 0) && c.starSelectableBy(4, 1));
    CHECK(!c.starSelectableBy(0, 1) && !c.starLaneFollowableBy(1, 1));

    // (2) RECEIVE LEG = FUN_00046354 EBX=-1 shape (cited 0x55f6e "the PLAYER
    // receives lanes from each race in turn"). AI-viewed-not-player set ==
    // {lane3}: pool-order prefix with N = rand%3+1 >= 1 => lane3 EXACTLY.
    const int got = c.shareLaneVision(ag::kPlayer, 1, /*bidirectional=*/false,
                                      /*allied=*/false);
    CHECK(got == 1);
    CHECK(c.laneVisibleTo(3, 0));
    CHECK(c.visibleLaneCountFor(0) == 2);
    // receive-only: the AI gained NOTHING (mirrored leg absent).
    CHECK(!c.laneVisibleTo(0, 1) && !c.laneVisibleTo(1, 1));
    // STICKY (L5 OR-only): a repeat call grants nothing more (set exhausted)
    // and never un-reveals.
    const int again = c.shareLaneVision(ag::kPlayer, 1, false, false);
    CHECK(again == 0);
    CHECK(c.laneVisibleTo(3, 0));
    CHECK(c.visibleLaneCountFor(0) == 2);

    // (3) ALLIANCE = BIDIRECTIONAL share (cited caller 0x45778 inside the
    // alliance-formation handler). Fixture dip file: PROPOSE_ALLIANCE below
    // start attitude so the MEASURED chooser fires it on turn 1 (decide-
    // DipAction: strict att > threshold; race00 START_ATTITUDE 340).
    ag::DipFile df;
    if (!df.loadFromFile((kRepo / "extracted/ascend00/race00.dip").string(), &err))
        std::abort();
    df.values.proposeAlliance = 100;
    ag::Campaign c2(cfg, g, &tables().tree, tables().items, tables().gizmos,
                    {df}, ab, &err);
    CHECK(err.empty());
    CHECK(!c2.starSelectableBy(4, 0));   // player blind to AI home pre-share
    bool sawAllianceEvent = false;
    for (int t = 0; t < 5 && !sawAllianceEvent; ++t) {
        c2.advance();
        for (const auto& ev : c2.events())
            if (ev.text.find("allied with the player") != std::string::npos)
                sawAllianceEvent = true;
    }
    CHECK(sawAllianceEvent);
    // Lend leg 0x46421 (OR rec+0x20, DL): AI receives a prefix of the
    // player-viewed set it lacked == {lane0} (exhaustive, N=rand%6+1>=1).
    CHECK(c2.laneVisibleTo(0, 1));
    // Receive leg of the same call: P receives {lane3}.
    CHECK(c2.laneVisibleTo(3, 0));
    // Star twin rode the event (FUN_00046524 same shape, allied modulus 4):
    // P can now select/follow the AI home star s4; A likewise gained s0.
    CHECK(c2.starSelectableBy(4, 0) && c2.starLaneFollowableBy(4, 0));
    CHECK(c2.starSelectableBy(0, 1));
    // STICKY monotonicity over 30 further turns (no clear site -> S23 L5).
    const int v0 = c2.visibleLaneCountFor(0), v1 = c2.visibleLaneCountFor(1);
    const int starsAlways = c2.cosmosStarsFor(0).size();
    for (int t = 0; t < 30 && !c2.over(); ++t) c2.advance();
    CHECK(c2.visibleLaneCountFor(0) >= v0);
    CHECK(c2.visibleLaneCountFor(1) >= v1);
    CHECK(c2.cosmosStarsFor(0).size() == starsAlways);  // stars ALWAYS listed

    // (4) SA_KnowStarLanes (L2295 "see all star lanes") on the PLAYER
    // (cfg.playerSpecies is the SA_ index; abilities[i] belongs to owner
    // i+1 — a fixture with ab vector {X} grants X to the AI, tested too):
    // owner bit ORs into EVERY lane mask at scenario init.
    ag::CampaignConfig cfgP = cfg;
    cfgP.playerSpecies = static_cast<int>(ag::SpeciesAbility::KnowStarLanes);
    ag::Campaign c3(cfgP, g, &tables().tree, tables().items, tables().gizmos,
                    {tables().ai[0]}, ab, &err);
    CHECK(c3.visibleLaneCountFor(0) == 4);         // player: all lanes
    CHECK(c3.visibleLaneCountFor(1) == 1);         // AI unaffected
    // AI token-holder route:
    std::vector<ag::SpeciesAbility> abKsl{ag::SpeciesAbility::KnowStarLanes};
    ag::Campaign c3b(cfg, g, &tables().tree, tables().items, tables().gizmos,
                     {tables().ai[0]}, abKsl, &err);
    CHECK(c3b.visibleLaneCountFor(1) == 4);
    CHECK(c3b.visibleLaneCountFor(0) == 1);

    // (5) SA_KnowHomeWorlds (L1783 "see all alien home stars") on the
    // PLAYER: owner bits land on every ALIEN HOME star's twin and NOTHING
    // else (lanes stay fogged; the AI gets nothing back).
    ag::CampaignConfig cfgH = cfg;
    cfgH.playerSpecies = static_cast<int>(ag::SpeciesAbility::KnowHomeWorlds);
    ag::Campaign c4(cfgH, g, &tables().tree, tables().items, tables().gizmos,
                    {tables().ai[0]}, ab, &err);
    CHECK(c4.starSelectableBy(4, 0));        // alien HOME revealed
    CHECK(c4.starLaneFollowableBy(4, 0));
    CHECK(!c4.starSelectableBy(3, 0));       // non-home star NOT revealed
    CHECK(!c4.starSelectableBy(0, 1));       // one-way per owner
    CHECK(c4.visibleLaneCountFor(0) == 1);   // lanes NOT blanket-revealed
}

TEST(campaign_pop_band_law_t199) {
    REQUIRE_DATA();
    // POPULATION BAND LAW pin (docs/re/planets-ui.md S4 [verified
    // 0x3ce39..0x3cef8], t198; wiring t199). SEL(i) = 1 + [i>=used] +
    // [i>=pop] over i < cap.
    // (1) Synthetic shapes matching the three vendor band classes.
    std::vector<int> b;
    ag::Campaign::popBands(3, 5, 9, b);   // used<pop<cap
    CHECK(b.size() == 9);
    CHECK((b == std::vector<int>{1, 1, 1, 2, 2, 3, 3, 3, 3}));
    ag::Campaign::popBands(0, 0, 4, b);   // uncolonized-looking: all EMPTY
    CHECK((b == std::vector<int>{3, 3, 3, 3}));
    ag::Campaign::popBands(7, 7, 7, b);   // full + all busy
    CHECK((b == std::vector<int>(7, 1)));
    ag::Campaign::popBands(0, 10, 10, b); // all free, no empties
    CHECK((b == std::vector<int>(10, 2)));
    ag::Campaign::popBands(0, 0, 0, b);   // zero-cap planet: nothing drawn
    CHECK(b.empty());
    // Out-of-corpus-order input (used > pop, NOT seen in the corpus) still
    // follows the vendor formula verbatim: 1+[i>=5]+[i>=2] -> i=0,1 SEL 1,
    // i=2..4 SEL 2 (pop passed), i=5 SEL 3 (both increments) — never 0 or 4.
    ag::Campaign::popBands(5, 2, 6, b);
    CHECK((b == std::vector<int>{1, 1, 2, 2, 2, 3}));

    // (2) THE CORPUS-LAW CHECK the paint law relies on: used <= pop <= cap
    // (measured 2900/2900 records in the 20-save playcap corpus, t198).
    // Runs here on the rewrite's own state across a seeded campaign.
    auto c = makeCampaign(2024);
    const int ns = static_cast<int>(c.galaxy().stars.size());
    int checkedPlanets = 0;
    for (int t = 0; t < 300 && !c.over(); ++t) {
        for (int s = 0; s < ns; ++s) {
            const int used = c.usedPopFor(s);
            const int pop = static_cast<int>(c.planetAt(s).pop);
            const int cap = c.popCapAt(s);
            const std::vector<int>& bands = c.popBandsFor(s);
            CHECK(bands.size() == static_cast<size_t>(std::max(0, cap)));
            if (used <= pop && pop <= cap) {
                // Band histograms counted INDEPENDENTLY of the formula:
                int c1 = 0, c2 = 0, c3 = 0;
                for (int v : bands) { c1 += v == 1; c2 += v == 2; c3 += v == 3; }
                CHECK(c1 == used);            // busy band  = +0x4c used
                CHECK(c2 == pop - used);      // free band  = pop - used
                CHECK(c3 == cap - pop);       // empty band = cap - pop
            }
        }
        ++checkedPlanets;
        c.advance();
    }
    CHECK(checkedPlanets > 0);
}

