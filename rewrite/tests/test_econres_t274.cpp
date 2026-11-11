// SPDX-License-Identifier: GPL-3.0-or-later

// t274 ECONOMY/RESEARCH INTEGRATION TESTS — end-to-end campaign pins for the
// income-channel law, the pop-growth counter law, the build-queue completion
// cadence, and the research tier chain (FUN_00040018 model).
//
// Law sources (all banked; nothing from memory):
//   docs/re/income-law.md S6/t18b+t19 (channel formula), S6c+S6e (growth
//     counter threshold 50, colonise :=2), S8/S9 (queue + selector),
//     T56 (per-turn bracket: counter delta == stored PROS word player /
//     word+1 AI; channel words are RATES not stockpiles; fresh-run AI opening
//     item Agriplot 4/4 [thin, n=4]), T37b (growth input = stored +0x48 word).
//   docs/re/research.md §7 / OQ-013 (66 main rows only in play; runtime cost
//     row-multiplier law), docs/re/aicode.md §3b/§3d (FUN_00040018 pick law).
// Fixture policy (queue row): multi-turn fixtures from banked seeds; NO raw
// .sav parsing — the watcher JSON schema carries no per-planet economy
// scalars, so the per-planet law checks run against the rewrite sim itself,
// seeded deterministically, with vendor-truth constants cited from the docs.
#include "harness.h"
#include "game/campaign.h"

#include <algorithm>
#include <cstdio>
#include <string>
#include <vector>

#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif

namespace ag = ascend::game;

ag::Campaign makeCampaignForDemolish(unsigned seed);  // test_campaign.cpp

namespace {

// Restree + planitem re-load (test_economy.cpp idiom): the chain-legality
// pin needs prereq rows and COST values outside Campaign's public surface.
const std::string kRepo = ASCENDANCY_SOURCE_DIR;

struct Refs {
    ag::ResearchTree tree;
    std::vector<ag::PlanetItem> items;
};
Refs& refs() {
    static Refs r = [] {
        Refs x;
        std::string err;
        x.tree = ag::ResearchTree::loadFromFile(kRepo + "/extracted/ascend00/restree.txt", err);
        x.items = ag::loadPlanItems(kRepo + "/extracted/ascend00/planitem.txt", err);
        return x;
    }();
    return r;
}

std::vector<int> ownedStars(ag::Campaign& c, int owner) {
    std::vector<int> out;
    for (size_t s = 0; s < c.galaxy().stars.size(); ++s)
        if (c.starOwner(static_cast<int>(s)) == owner) out.push_back(static_cast<int>(s));
    return out;
}

bool hasItem(ag::Campaign& c, int star, const char* name) {
    for (int it : c.planetAt(star).items)
        if (refs().items[it].name == name) return true;
    return false;
}

}  // namespace

// ---------------------------------------------------------------------------
// T274-1 INCOME CHANNEL E2E. IND: buildPhase pays storedIndFor(star) into the
// per-queue accumulator every turn while pending (FUN_00038f68 0x39005/
// 0x3907b, income-law.md S8); completion at acc >= COST (0x390a3 JA 0x392a2).
// T56 fact 2: stored channel WORDS are per-turn RATES — they must not drift
// on planets whose item set is unchanged.
// ---------------------------------------------------------------------------
TEST(e2e_income_channel_rates_t274) {
    REQUIRE_DATA();
    auto c = makeCampaignForDemolish(77);
    c.advance();  // t1: AI homes queue, selector state established
    // Snapshot words + built/pending state; over 8 idle-bracket turns the
    // words on every planet with NO completion that turn must be unchanged,
    // and every acc delta on a pending planet must equal the word IND.
    for (int t = 0; t < 8; ++t) {
        struct Snap {
            int star, ind, res, pros, acc0, built0;
            bool pending;
        };
        std::vector<Snap> snaps;
        for (size_t s = 0; s < c.galaxy().stars.size(); ++s) {
            if (c.starOwner(static_cast<int>(s)) < 0) continue;
            const auto w = c.channelWordsFor(static_cast<int>(s));
            snaps.push_back({static_cast<int>(s), w.ind, w.res, w.pros,
                             c.buildAccFor(static_cast<int>(s)),
                             c.builtItemCount(static_cast<int>(s)),
                             c.pendingItemFor(static_cast<int>(s)) >= 0});
        }
        c.advance();
        for (const Snap& sn : snaps) {
            const bool completed = c.builtItemCount(sn.star) != sn.built0;
            const auto w = c.channelWordsFor(sn.star);
            if (!completed) {
                // RATE law: no item change -> no word change (T56 verified
                // 8 turns x 5 idle worlds; here every non-completing planet).
                CHECK(w.ind == sn.ind);
                CHECK(w.res == sn.res);
                CHECK(w.pros == sn.pros);
            }
            if (sn.pending && !completed) {
                CHECK(c.buildAccFor(sn.star) - sn.acc0 == sn.ind);  // 0x3907b
            }
            if (sn.pending && completed) {
                // Completion turn: the tick is still paid before the gate, so
                // the pre-reset value reached >= COST; post-reset acc == 0 and
                // exactly one item joined (queue capacity 1, S8).
                CHECK(c.buildAccFor(sn.star) == 0);
                CHECK(c.builtItemCount(sn.star) == sn.built0 + 1);
                CHECK(sn.acc0 + sn.ind >=
                      refs().items[c.planetAt(sn.star).items.back()].cost);
            }
        }
    }
}

// ---------------------------------------------------------------------------
// T274-2 POP GROWTH COUNTER E2E (income-law.md S6c+S6e, T56 fresh
// measurement): per owned planet per turn —
//   pop >= cap          -> counter := 0 (reset @0x393f9)
//   else counter += stored-PROS-word (+1 iff owner != 0 AND word < 4;
//        @0x39319; T56: PROS=1 -> player +1/turn, AI +2/turn)
//   counter >= 50       -> pop += 1 (+1 per built Cloning Plant, t27
//        correction: item 15 slot 0x393ad), clamp cap, counter := 0.
// The word used is the PRE-build snapshot (incomeAndGrow runs before
// buildPhase in advance()).
// ---------------------------------------------------------------------------
TEST(e2e_growth_counter_law_t274) {
    REQUIRE_DATA();
    auto c = makeCampaignForDemolish(99);
    int wraps = 0, ticks = 0;
    for (int t = 0; t < 80; ++t) {
        struct G {
            int star;
            int prosWord, cap;
            double pop0;
            int counter0;
            bool clone;
            int owner;
        };
        std::vector<G> g;
        for (size_t s = 0; s < c.galaxy().stars.size(); ++s) {
            const int o = c.starOwner(static_cast<int>(s));
            if (o < 0) continue;
            g.push_back({static_cast<int>(s), c.channelWordsFor(static_cast<int>(s)).pros,
                         c.popCapAt(static_cast<int>(s)), c.planetAt(static_cast<int>(s)).pop,
                         c.planetAt(static_cast<int>(s)).growthCounter,
                         hasItem(c, static_cast<int>(s), "Cloning Plant"), o});
        }
        c.advance();
        for (const G& p : g) {
            if (c.starOwner(p.star) != p.owner) continue;  // conquered/lost:
                // seedColonyBaseColony resets pop — out of the per-planet law scope
            const auto& ps = c.planetAt(p.star);
            int expect = p.prosWord + (p.owner != 0 && p.prosWord < 4 ? 1 : 0);
            if (p.pop0 >= p.cap) {
                CHECK(ps.growthCounter == 0);  // @0x393f9
                continue;
            }
            if (p.counter0 + expect >= 50) {
                ++wraps;
                CHECK(ps.growthCounter == 0);
                const double want = std::min<double>(p.cap, p.pop0 + 1 + (p.clone ? 1 : 0));
                CHECK(ps.pop == want);
            } else {
                ++ticks;
                CHECK(ps.growthCounter == p.counter0 + expect);
                CHECK(ps.pop == p.pop0);
            }
        }
    }
    CHECK(wraps > 0);   // the suite actually exercised the wrap branch
    CHECK(ticks > 0);
}

// ---------------------------------------------------------------------------
// T274-3 BUILD-QUEUE CADENCE + T56 OPENING WITNESS. Fresh run, turn 1: every
// AI home flips from no-queue to a pending item (T56(3): 4/4 AI homes, word
// +0x52 idle 0xFFFF -> cell index with byte +0x54 := 0x01 Agriplot; the
// PLAYER home stays unqueued — manual control has no queue). Then the exact
// completion turn of each home's first queue is pinned (deterministic sim,
// acc += stored IND law): measured values below are from THIS sim under the
// cited law, re-measurable by un-commenting the printf.
// ---------------------------------------------------------------------------
TEST(e2e_build_queue_opening_t274) {
    REQUIRE_DATA();
    auto c = makeCampaignForDemolish(7);
    const int nstars = static_cast<int>(c.galaxy().stars.size());
    // t0: nothing queued anywhere (fresh world; selector first runs in t1's
    // buildPhase).
    for (int s = 0; s < nstars; ++s)
        if (c.starOwner(s) >= 0) CHECK(c.pendingItemFor(s) < 0);
    c.advance();
    // PLAYER QUEUE STATE — DIVERGENCE BANKED t274 (income-law.md T274): the
    // T56 vendor witness says the player home stayed 0xFFFF (manual control
    // has no queue; FUN_0003f130 is AI-only [verified t28]). The rewrite
    // deliberately auto-queues kBuildOrder for owner 0 as a DOCUMENTED
    // DEFAULT (campaign.cpp buildPhase header comment) so headless runs have
    // a player economy. Re-wiring that is out of t274's scope (it would
    // re-trajectory every seeded pin + PLAYTHROUGH); pin the sim's behaviour.
    for (int s : ownedStars(c, 0))
        if (c.builtItemCount(s) == 1) CHECK(c.pendingItemFor(s) >= 0);
    // AI homes: all queued at t1 (T56(3): all AI homes flipped idle->pending
    // at the FIRST End Turn; selector gate stored IND > 0 @0x3f146).
    std::vector<int> homes;
    for (int o = 1; o <= 6; ++o) {
        auto st = ownedStars(c, o);
        CHECK(!st.empty());
        homes.push_back(st[0]);
        CHECK(c.pendingItemFor(st[0]) >= 0);
    }
    // OPENING PICK: the sim's selector model (first ABSENT candidate in row
    // order, COST/stored-IND 30/1 < 70 so no scan abort — income-law.md S9)
    // queues row 0 Factory on every AI home. WITNESS DIVERGENCE BANKED
    // t274: the T56 vendor reading (n=4, one run) says opening byte +0x54
    // == 0x01 (Agriplot). The rewrite does NOT assert the thin witness over
    // the cited law; the divergence is banked in docs (income-law.md T274)
    // for a future selector-session to adjudicate. Pin = deterministic sim
    // behaviour: uniform opening item across homes.
    int factory = 0;
    const std::string first = refs().items[c.pendingItemFor(homes[0])].name;
    for (int s : homes) {
        CHECK(refs().items[c.pendingItemFor(s)].name == first);
        if (refs().items[c.pendingItemFor(s)].name == "Factory") ++factory;
    }
    CHECK(factory == 6);  // sim law: row-0 Factory; T56 says Agriplot (banked)
    // Completion cadence: first completion per home at acc >= COST. Track to
    // first completion; pin the measured turn for this seed.
    int firstTurn = -1;
    for (int t = 0; t < 60 && firstTurn < 0; ++t) {
        c.advance();
        for (int s : homes)
            if (c.builtItemCount(s) > 1) { firstTurn = t + 2; break; }
    }
    std::printf("[first AI completion t%d]\n", firstTurn);
    // EXACT CADENCE PIN (regression catcher for the completion gate
    // 0x390a3 >= vs >): t295 RE-DERIVATION on seed 7 — the AI home's stored
    // IND word is 1 (terrain-drawn channel per T35), Factory COST 30 queued
    // at t1, accumulator lands EXACTLY on 30 at tick 30 -> completion t31.
    // A `>` gate needs 31 and slips EXACTLY one turn to t32 (re-verified by
    // mutation this session). Original seed-7-old-layout value was t16 with
    // stored IND word 2 (2/turn); the gate law is unchanged, the IND seed
    // came off the world-gen draw the t295 home law re-sits. Changing the
    // sim's opening order, IND law, or the gate re-trajectories this line ON
    // PURPOSE.
    CHECK(firstTurn == 31);
}

// ---------------------------------------------------------------------------
// T274-4 RESEARCH TIER CHAIN E2E. researchPhase models FUN_00040018
// (candidate build = row order + prereq legality == FUN_00046d3c, cap 0x20;
// preferred {1,47}; uniform fallback) and the RES-fuel/completion law
// (progress += stockpile, complete at runtimeCost, research.md §7). Pins,
// per AI owner over a long run:
//   (a) variants (rows >= 66) NEVER owned (OQ-013 closed sub-law);
//   (b) every completion had ALL prereqs owned at completion time;
//   (c) the queued row is always a legal candidate (main row, unowned,
//       prereqs satisfied) whenever a queue is set;
//   (d) completion timing: cumulative RES injected since the queue was set
//       >= runtimeCost(row) at the completing turn (fuel law; injection =
//       sum of raw RES channel words, the same quantity researchPhase moves).
// ---------------------------------------------------------------------------
TEST(e2e_research_tier_chain_t274) {
    REQUIRE_DATA();
    auto c = makeCampaignForDemolish(2024);
    const int nrow = c.techCountTotal();
    CHECK(nrow == 106);  // 66 main + 40 variants on the shipped file
    std::vector<double> fuel(7, 0.0);
    int completions = 0;
    for (int t = 0; t < 240 && !c.over(); ++t) {
        // RES injection per owner this turn (pre-advance words; incomeAndGrow
        // charges exactly this before researchPhase consumes it).
        std::vector<double> inc(7, 0.0);
        for (size_t s = 0; s < c.galaxy().stars.size(); ++s) {
            const int o = c.starOwner(static_cast<int>(s));
            if (o < 0) continue;
            inc[o] += c.channelWordsFor(static_cast<int>(s)).res;
        }
        // (c) legality of the CURRENT queue before the turn runs.
        std::vector<int> queuedBefore(7, -1);
        for (int o = 0; o <= 6; ++o) {
            for (int r = 0; r < nrow; ++r)
                if (c.isTechQueuedFor(o, r)) { queuedBefore[o] = r; break; }
            const int q = queuedBefore[o];
            if (q >= 0) {
                CHECK(q < 66);                                   // main rows only
                CHECK(c.techRowOwnedFor(o, q) == false);         // unowned
                for (int p : refs().tree.all()[q].prereqs)
                    CHECK(c.techRowOwnedFor(o, p));              // FUN_00046d3c
            }
        }
        std::vector<int> before(7, 0);
        for (int o = 0; o <= 6; ++o) before[o] = c.techsOwned(o);
        c.advance();
        for (int o = 0; o <= 6; ++o) fuel[o] += inc[o];
        for (int o = 0; o <= 6; ++o) {
            const int delta = c.techsOwned(o) - before[o];
            if (delta == 0) continue;
            CHECK(delta == 1);  // one completion per owner per turn max
            ++completions;
            // The completing row == the queue snapshotted before the turn
            // (single-queue law: researchPhase completes queuedTech[o]).
            const int row = queuedBefore[o];
            CHECK(row >= 0);
            if (row < 0) continue;
            CHECK(c.techRowOwnedFor(o, row));
            for (int p : refs().tree.all()[row].prereqs)
                CHECK(c.techRowOwnedFor(o, p));  // (b) prereq-before-complete
            // (d) fuel law: researchPhase moves the WHOLE stockpile each turn
            // into progress, so cumulative injected >= charged cost.
            CHECK(fuel[o] >= refs().tree.all()[row].runtimeCost());
            fuel[o] = 0.0;  // researchPhase zeroes the stockpile on completion
        }
        // (a) variants never in play — full sweep every 20 turns keeps cost sane.
        if (t % 20 == 0)
            for (int o = 0; o <= 6; ++o)
                for (int r = 66; r < nrow; ++r)
                    CHECK(c.techRowOwnedFor(o, r) == false);
    }
    CHECK(completions > 0);  // the chain actually fired (research happens)
}
