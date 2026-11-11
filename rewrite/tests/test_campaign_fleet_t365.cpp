// SPDX-License-Identifier: GPL-3.0-or-later

// t365 ENGINE FLIP pins — the per-ship engine is THE combat engine and the
// aggregate code is the oracle (user ruling D2=(b); bridge surrogate ledger
// rewrite/src/game/campaign_fleet_bridge.h S1..S11; design docs/re/_wip_t365).
// P1  campaign-driven engagement: per-ship state lands (hull, death
//     finalizer C4) and the run stays deterministic.
// P2  ORACLE EQUIVALENCE (the D2 "seeds agree" evidence, per-engagement
//     exact form): for fleetDamage == 0 the bridge's capture verdict and
//     hull spill EQUAL the aggregate comparison hullHit > defenseScore with
//     the cited absorb split — matrix over pop/shield/tech/double inputs.
//     The named divergence class (partially sapped attacker, S3) is pinned
//     too: suppression at fd >= volley, FULL row damage below it.
// P3  chase-leg decision (a): shooter targetPos == garrison pos at seed time.
// P4  full-campaign determinism through the flip (equal seeds, equal traces,
//     equal sim digests).
// P5  census agreement over a 40-turn seed-2024 run: every non-guaranteed,
//     non-sapped fact's verdict matches the oracle recomputation; the sapped
//     count is recorded honestly with NO threshold claim.
#include "game/campaign.h"
#include "game/campaign_fleet_bridge.h"
#include "game/aggregate_oracle.h"
#include "game/economy.h"
#include "harness.h"

#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <filesystem>
#include <vector>

#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif

// Exported shim from test_campaign.cpp (GLOBAL scope there, same table
// wiring; the t202b pattern).
ascend::game::Campaign makeCampaignForDemolish(unsigned seed);

namespace {
namespace ag = ascend::game;
namespace fs = std::filesystem;

const std::vector<ag::Gizmo>& gizmoTable() {
    static const std::vector<ag::Gizmo> g = [] {
        std::string err;
        auto v = ag::loadGizmos(
            (fs::path(ASCENDANCY_SOURCE_DIR) / "extracted/ascend00/gizmos.txt").string(),
            err);
        if (v.size() != 76) std::abort();
        return v;
    }();
    return g;
}
int techCount() {
    static int n = [] {
        std::string err;
        auto t = ag::ResearchTree::loadFromFile(
            (fs::path(ASCENDANCY_SOURCE_DIR) / "extracted/ascend00/restree.txt").string(), err);
        if (t.all().empty()) std::abort();
        return static_cast<int>(t.all().size());
    }();
    return n;
}
std::vector<bool> techs(bool owned) { return std::vector<bool>(techCount(), owned); }

}  // namespace

TEST(campaign_fleet_engagement_t365_p1) {
    REQUIRE_DATA();
    // Drive a real FFA campaign until combat happens; the per-ship engine
    // must have records, engagement state, and a death when stars fall.
    ag::Campaign c = makeCampaignForDemolish(2024);
    ag::Campaign d = makeCampaignForDemolish(2024);
    for (int t = 0; t < 40 && !c.over(); ++t) { c.advance(); d.advance(); }
    const auto* bridge = c.fleetSim();
    CHECK(bridge != nullptr);
    const auto& cen = bridge->census();
    CHECK(!cen.empty());                       // FFA wars engage by t40
    // Census facts are coherent: every fact that ran fired shots or was a
    // zero-volley engagement; captured facts imply shots.
    for (const auto& f : cen) {
        // Suppression is the ONLY skip reason (S3), and it is exactly
        // volleyBase - fleetDamage <= 0 (the cited power gate).
        if (!f.ran) { CHECK(f.volleyBase - f.fleetDamage <= 0); CHECK(!f.simCaptured); }
        if (f.simCaptured) CHECK(f.shots > 0);
    }
    // Garrison records exist in the sim (id space >= 100000); a death ran
    // the C4 finalizer (owner -1, kind 0 — or the record was re-armed by a
    // later engagement on the same pair, which resets both).
    bool garrisons = false;
    for (const auto& s : bridge->sim().ships())
        if (s.id >= 100000) garrisons = true;
    CHECK(garrisons);
    // Determinism: same seed, same engagement census, same digests.
    CHECK(c.traceLine() == d.traceLine());
    CHECK(c.fleetSim()->sim().digest() == d.fleetSim()->sim().digest());
    CHECK(c.fleetSim()->census().size() >= cen.size());
}

TEST(campaign_fleet_oracle_equivalence_t365_p2) {
    REQUIRE_DATA();
    // THE seed-comparison evidence, exact per-engagement form. Aggregate
    // expectation from the oracle (attackScore demoted body + the cited
    // absorb split) vs the bridge's per-ship run, fleetDamage == 0.
    for (int popA : {0, 5, 25, 100, 123}) {
        for (int popB : {0, 30, 300, 512}) {
            for (int tech : {0, 1}) {
                for (int dbl : {0, 1}) {
                    ag::CampaignFleetBridge b(7);
                    auto out = b.resolveEngagement(
                        /*attacker=*/1, /*defender=*/2, /*star=*/7,
                        popA, popB, /*fleetDamage=*/0, dbl != 0,
                        gizmoTable(), techCount(), techs(tech != 0), techs(tech != 0));
                    // Oracle side (the pre-t365 decider math verbatim).
                    const int wsum = ag::weaponLevelSum(gizmoTable(), techCount(),
                                                        techs(tech != 0));
                    int volley = ag::aggregateVolley(popA, wsum, 0);
                    if (dbl) volley *= 2;
                    int shields = 0;
                    if (tech)
                        for (const auto& g : gizmoTable())
                            if (g.cat == ag::GizmoCat::Shield) shields += g.level;
                    int absorb = 0, spill = 0;
                    ag::Campaign::absorbSplit(volley, shields, absorb, spill);
                    const int defense = ag::aggregateHullDefense(popB);
                    CHECK(out.ran == (volley > 0));       // 0-volley == gate
                    CHECK(out.volleyBase == volley - (dbl ? volley / 2 : 0));
                    CHECK(out.shieldCharges == shields);
                    // Verdict equality AND the clamped-apply bookkeeping:
                    // a destroyed garrison consumed EXACTLY its hull seed
                    // (defense+1); a survivor took the full telescoped spill.
                    if (spill > defense) {
                        CHECK(out.captured);
                        CHECK(out.hullHit == defense + 1);
                    } else {
                        CHECK(!out.captured);
                        CHECK(out.hullHit == spill);
                    }
                }
            }
        }
    }
    // The NAMED divergence class (S3): partially sapped attacker fires FULL
    // row damage (cited design[+0x52]); fully sapped suppresses (cited
    // power gate 0x4a561). Both branches pinned.
    {
        ag::CampaignFleetBridge b(7);
        const int wsum = ag::weaponLevelSum(gizmoTable(), techCount(), techs(true));
        auto part = b.resolveEngagement(1, 2, 3, 100, 300, /*fd=*/50, false,
                                        gizmoTable(), techCount(), techs(true), techs(true));
        // volleyBase 49+10 == 59 measured by the sim; fd 50 gates power to
        // 9 (>0 so it RUNS) and damage is UNATTENUATED (cited design[+0x52]):
        // the aggregate would have hit 59-50=9 <= 32 (no capture); the sim
        // spills 59-16=43 onto hull 33 -> CAPTURE. That is the S3 divergence,
        // pinned in both directions (hull clamps the applied total to 33).
        CHECK(part.ran && part.volleyBase == wsum + 10);
        CHECK(part.captured);
        CHECK(part.hullHit == 300 / 10 + 2 + 1);
        CHECK((wsum + 10 - 50) <= 300 / 10 + 2);   // aggregate: NO capture
        ag::CampaignFleetBridge z(7);
        auto full = z.resolveEngagement(1, 2, 3, 0, 300, /*fd=*/500, false,
                                        gizmoTable(), techCount(), techs(true), techs(true));
        CHECK(!full.ran && !full.captured && full.shots == 0);
    }
}

TEST(campaign_fleet_chase_targetpos_t365_p3) {
    REQUIRE_DATA();
    // S6 decision (a): the bridge sets shooter targetPos := victim pos at
    // stance time (the walk-toward-+0x68 leg is uncited — not modelled).
    ag::CampaignFleetBridge b(7);
    b.resolveEngagement(1, 2, 11, 50, 50, 0, false, gizmoTable(), techCount(),
                        techs(true), techs(true));
    auto* sh = b.simForTest().findShip(ag::CampaignFleetBridge::shooterId(1, 11));
    auto* gr = b.simForTest().findShip(ag::CampaignFleetBridge::garrisonId(2, 11));
    CHECK(sh && gr);
    CHECK(sh->targetPos[0] == gr->pos[0] && sh->targetPos[1] == gr->pos[1] &&
          sh->targetPos[2] == gr->pos[2]);
    CHECK(sh->fireTarget == gr->id);           // +0x68 stance store
    CHECK(sh->dispatcherGate == 1);            // +0x62 set by the stance leg
}

TEST(campaign_fleet_determinism_t365_p4) {
    REQUIRE_DATA();
    // Equal seeds trace identically THROUGH the flip (determinism pin, not
    // pre-t365 preservation — see bridge S11 trajectory note), and the
    // per-ship engine digest is part of the reproducible state.
    ag::Campaign x = makeCampaignForDemolish(2024);
    ag::Campaign y = makeCampaignForDemolish(2024);
    for (int t = 0; t < 40; ++t) {
        x.advance();
        y.advance();
        CHECK(x.traceLine() == y.traceLine());
    }
    CHECK(x.fleetSim()->sim().digest() == y.fleetSim()->sim().digest());
    CHECK(!x.fleetSim()->census().empty());
    CHECK(x.fleetSim()->census().size() == y.fleetSim()->census().size());
}

TEST(campaign_fleet_census_agreement_t365_p5) {
    REQUIRE_DATA();
    // Over a real 40-turn FFA run: EVERY non-guaranteed, non-sapped
    // engagement's per-ship verdict equals the oracle recomputation from the
    // recorded inputs. Sapped facts are counted, never thresholded.
    ag::Campaign c = makeCampaignForDemolish(2024);
    for (int t = 0; t < 40 && !c.over(); ++t) c.advance();
    const auto& cen = c.fleetSim()->census();
    CHECK(!cen.empty());
    int checked = 0, agreed = 0, sapped = 0, guaranteed = 0;
    for (const auto& f : cen) {
        if (f.guaranteed) { ++guaranteed; continue; }
        if (f.fleetDamage > 0) { ++sapped; continue; }
        int volley = f.popATen + f.weaponSum;
        if (f.doublePower) volley *= 2;
        int absorb = 0, spill = 0;
        ag::Campaign::absorbSplit(volley, f.shieldCharges, absorb, spill);
        ++checked;
        agreed += (f.simCaptured == (spill > f.hullDefense)) ? 1 : 0;
    }
    std::printf("t365 P5 census: %zu facts, %d checked, %d agreed, "
                "%d sapped, %d guaranteed\n",
                cen.size(), checked, agreed, sapped, guaranteed);
    CHECK(checked > 0);
    CHECK(agreed == checked);
}
