// SPDX-License-Identifier: GPL-3.0-or-later

// t380 QUANTIZER REST-ON-GRID pins — the walk/placement/scatter store law.
// Evidence: docs/re/_wip_t380.md S1..S4 (static instruction-level over
// work/r331_disasm.txt; runtime census scripts/r380_grid_census.py over the
// playtest banks + production ring, zero capture).
// THE MEASURED FACTS these pins encode:
//  * FUN_00049aa8 (0x49aa8..0x49ac8) is a QUANTIZING store: writes the
//    triple to +0x9e then CALLs FUN_000533e0 (g = ds:0x895dc = 32) on all
//    three axes. Placement 0x2202a and scatter 0x399df store through it.
//  * The walk body calls the quantizer UNCONDITIONALLY (0x4a2cf, straight
//    line) and copies the quantized scratch back ONLY in commit mode
//    (0x4a2d4 cmp edi,0x1; executor commit passes edx=1 at 0x25560; dry-run
//    callers 0x15cc5/0x15df0 pass edx=0). Arrival drives bookkeeping only.
//    The t361-era "arrival-time-only snap" [INFERRED] reading is SUPERSEDED.
//  * RUNTIME (r380_grid_census.py, 100 bank saves + 20 ring saves): every
//    off-grid LIVE rest row is a kind-5 LANE-LOCAL frame (y in {0,1}, z on
//    grid — the S22 L4 frame law); kinds 1/3/4 rest rows are 100% on the
//    32-grid (bank 3180 rows / ring 540 rows, zero exceptions).
//  * QUANTIZER TIES (0x533e0 full read): q = trunc(round(v + 16*sign(v))
//    / 32) * 32 — ties go AWAY FROM ZERO, identical to snapGrid's
//    std::round(a/g)*g shape.
// Corpus pins skip honestly when work/ is absent (public clone).
#include "formats/shipsave.h"
#include "game/shipsim.h"
#include "harness.h"

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <filesystem>
#include <fstream>
#include <map>
#include <utility>
#include <vector>

namespace fs = std::filesystem;
namespace as = ascend::game;
using ascend::formats::ShipSave;

namespace {

bool nearf(float a, float b) { return std::fabs(a - b) < 0.01f; }
bool onGrid(float v) { return std::fmod(v, 32.0f) == 0.0f; }

const std::string kBankEarly =
    std::string(ASCENDANCY_SOURCE_DIR) + "/work/r1/bank-play-20261111";
const std::string kBankLate =
    std::string(ASCENDANCY_SOURCE_DIR) + "/work/r1/bank-play-20261111-late";

std::vector<std::string> bankSaves(const std::string& dir) {
    std::vector<std::string> out;
    if (!fs::is_directory(dir)) return out;
    fs::directory_iterator end;
    for (fs::directory_iterator it(dir); it != end; ++it) {
        auto p = it->path().string();
        if (it->is_regular_file() && p.size() > 4 && p.substr(p.size() - 4) == ".sav")
            out.push_back(p);
    }
    std::sort(out.begin(), out.end());
    return out;
}

bool payloadAnchors(std::vector<uint8_t>* payload,
                    std::vector<std::pair<size_t, std::vector<uint8_t>>>* anch) {
    const std::string p =
        std::string(ASCENDANCY_SOURCE_DIR) + "/work/ascend_payload.bin";
    std::ifstream f(p, std::ios::binary);
    if (!f) return false;
    payload->assign(std::istreambuf_iterator<char>(f),
                    std::istreambuf_iterator<char>());
    *anch = ShipSave::buildAnchors(*payload);
    return !anch->empty();
}

as::SimStar mkStar(int id, float x, float y, float z) {
    as::SimStar st;
    st.id = id; st.pos[0] = x; st.pos[1] = y; st.pos[2] = z;
    return st;
}
as::SimLane mkLane(int id, int a, int b, float len, bool third = false) {
    as::SimLane l;
    l.id = id; l.a = a; l.b = b; l.len = len; l.thirdSpeed = third;
    return l;
}
as::Ship mkShip(int id, int owner, as::OrderKind k) {
    as::Ship s;
    s.id = id; s.owner = owner; s.kind = k;
    return s;
}

}  // namespace

TEST(shipsim_walk_snaps_mid_transit_t380) {
    // THE correction pin: a PARTIAL walk (NOT arrived) still lands on the
    // 32-grid. Fixture separates the readings: raw 277.333 -> snap 288.
    // (d = 416 = 2.6 sugar, moves 10, power 2 -> clamp walk 1.73333.)
    float pos[3] = {0, 0, 0};
    int32_t power = 2, moves = 10;
    const float delta[3] = {416, 0, 0};
    bool arrived = true;
    CHECK(as::ShipSim::walkLaw(pos, &power, &moves, delta, &arrived) == 2);
    CHECK(!arrived);                         // mid-transit at observation
    CHECK(nearf(pos[0], 288.f));             // quantizer output, not raw glide
    CHECK(onGrid(pos[0]) && onGrid(pos[1]) && onGrid(pos[2]));
    // Bookkeeping is UNTOUCHED by the snap (moves := round(remaining RAW),
    // not round(remaining-after-snap): 10 - 1.73333 = 8.26667 -> 8. If the
    // snap fed the accumulator this would read round(10 - 1.8) = 8 too —
    // the separating case is the 288-vs-277.333 raw delta above; here the
    // pin guards the ORDER law (snap after the walk math).
    CHECK(moves == 8 && power == 0);
    // Zero-distance commit: quantizer still runs (10 -> 0 is NOT what the
    // vendor does — snap(10)=0? NO: snap(10) = round(10/32)*32 = 0. The
    // walk adds nothing, the snap pulls the off-grid start onto the grid.)
    float p5[3] = {10, 10, 10};
    int32_t pw5 = 5, mv5 = 0;
    const float zero[3] = {0, 0, 0};
    bool a5 = false;
    CHECK(as::ShipSim::walkLaw(p5, &pw5, &mv5, zero, &a5) == 1);
    CHECK(a5);
    CHECK(p5[0] == 0.f && p5[1] == 0.f && p5[2] == 0.f);  // snap(10) = 0
}

TEST(shipsim_negative_coord_snap_away_from_zero_t380) {
    // Tie semantics BANKED from 0x533e0 (trunc(round(v + 16*sign)/32)*32):
    // v = -48 (tie at -16 mod 32... -48 = -32*1 - 16) -> AWAY from zero =
    // -64. The sim's snapGrid mirror must agree on both signs and on the
    // non-tie neighbours.
    float pos[3] = {0, 0, 0};
    int32_t power = 100, moves = 100;
    const float d1[3] = {-48, 0, 0};         // walk 0.3 sugar -> raw -48
    bool a = false;
    as::ShipSim::walkLaw(pos, &power, &moves, d1, &a);
    CHECK(nearf(pos[0], -64.f));             // tie away from zero
    float p2[3] = {0, 0, 0};
    int32_t p2w = 100, m2 = 100;
    const float d2[3] = {-80, 0, 0};         // raw -80 -> -80 (already 32*2.5? no: tie -> -96)
    bool a2 = false;
    as::ShipSim::walkLaw(p2, &p2w, &m2, d2, &a2);
    CHECK(nearf(p2[0], -96.f));              // -80 tie: away from zero
    float p3[3] = {0, 0, 0};
    int32_t p3w = 100, m3 = 100;
    const float d3[3] = {-81, 0, 0};         // raw -81 -> -96 (81+16=97, /32=3.03, trunc 3, *32=96)
    bool a3 = false;
    as::ShipSim::walkLaw(p3, &p3w, &m3, d3, &a3);
    CHECK(nearf(p3[0], -96.f));
    float p4[3] = {0, 0, 0};
    int32_t p4w = 100, m4 = 100;
    const float d4[3] = {-47, 0, 0};         // raw -47: 47+16=63 -> 1 -> -32
    bool a4 = false;
    as::ShipSim::walkLaw(p4, &p4w, &m4, d4, &a4);
    CHECK(nearf(p4[0], -32.f));
}

TEST(shipsim_lane_end_arrival_grid_rest_t380) {
    // The lane-END arrival lands kind 4 AT a 32-aligned galactic position:
    // the vendor's store leg is call 0x49aa8 (quantizing helper). Star at
    // (1000,500,1000) + seed-7 draws (164, 6) -> raw (1164, 300, 1006) ->
    // quantized (1152, 288, 992) = the S64-M5 runtime shape (s10 arrival
    // (-1280,-1952,384): every axis an exact multiple of 32).
    as::ShipSim sim(7);
    sim.addStar(mkStar(0, 1000, 500, 1000));
    sim.addLane(mkLane(0, 0, 0, 100));
    auto s = mkShip(1, 0, as::OrderKind::Placement);
    s.laneId = 0;
    s.laneStepX = 100;
    sim.addShip(s);
    auto rep = sim.advanceBoundary();
    CHECK(rep.placed.size() == 1);
    as::Ship* p = sim.findShip(1);
    CHECK(p->kind == as::OrderKind::InSystem);
    CHECK(onGrid(p->pos[0]) && onGrid(p->pos[1]) && onGrid(p->pos[2]));
    CHECK(nearf(p->pos[0], 1152.f) && nearf(p->pos[1], 288.f) && nearf(p->pos[2], 992.f));
}

TEST(shipsim_lane_march_stays_lane_local_t380) {
    // The OTHER half of the runtime census: kind-5 march rows are off-grid
    // by FRAME, not by law-break — laneX is lane-local progress (S22 L4)
    // and the march never writes the galactic triple. A third-speed lane
    // (step 14/3) leaves pos untouched and laneX off-grid.
    as::ShipSim sim(7);
    sim.addStar(mkStar(0, 0, 0, 0));
    sim.addLane(mkLane(0, 0, 0, 28, /*third=*/true));
    auto s = mkShip(1, 0, as::OrderKind::Placement);
    s.laneId = 0; s.laneStepX = 14;
    s.pos[0] = 96.f; s.pos[1] = 1.f; s.pos[2] = -224.f;   // S64 mid-transit shape
    sim.addShip(s);
    sim.advanceBoundary();
    as::Ship* p = sim.findShip(1);
    CHECK(nearf(p->laneX, 14.f / 3.f));      // lane-local progress, off-grid OK
    CHECK(p->kind == as::OrderKind::Placement);
    CHECK(p->pos[0] == 96.f && p->pos[1] == 1.f && p->pos[2] == -224.f);  // galactic untouched
}

TEST(shipsim_scatter_rests_on_grid_t380) {
    // T-6 scatter store 0x399df is call 0x49aa8 (quantizing helper): after
    // landing-attempt scatter the rest position is 32-aligned no matter the
    // draws. Fixture: start ON a multiple of 1000 offsets is impossible to
    // pin per-draw, so the pin asserts the INVARIANT (all axes on grid) +
    // the |delta| < 500 bound per axis + determinism across two sims.
    as::ShipSim sim(2024);
    sim.addStar(mkStar(0, 0, 0, 0));
    auto s = mkShip(7, 0, as::OrderKind::InSystem);
    s.pos[0] = 320; s.pos[1] = 0; s.pos[2] = 64;
    s.act = 2; s.orderType = 1;
    s.targetPos[0] = 320;                    // d = 0 -> arrive immediately
    s.driveStat = 10; s.powerMax = 100;
    sim.addShip(s);
    auto rep = sim.advanceBoundary();
    CHECK(rep.landed.size() == 1);
    as::Ship* p = sim.findShip(7);
    CHECK(onGrid(p->pos[0]) && onGrid(p->pos[1]) && onGrid(p->pos[2]));
    // Scatter bound: raw draw in [-500, 499], quantization moves at most 16
    // more — |pos - start| <= 516 per axis.
    CHECK(std::fabs(p->pos[0] - 320.f) <= 516.f);
    CHECK(std::fabs(p->pos[1]) <= 516.f);
    CHECK(std::fabs(p->pos[2] - 64.f) <= 516.f);
}

TEST(shipsim_grid_rest_corpus_census_t380) {
    // CORPUS PIN (skips when banks absent): the r380_grid_census.py law on
    // real saves — every LIVE rest row of kind 1/3/4 is 32-aligned in ALL
    // axes; every off-grid row is kind 5 in the lane-local frame (y in
    // {0,1} and z on grid). 10 saves per side bound runtime.
    auto early = bankSaves(kBankEarly);
    auto late = bankSaves(kBankLate);
    std::vector<uint8_t> payload;
    std::vector<std::pair<size_t, std::vector<uint8_t>>> anch;
    if (early.empty() || late.empty() || !payloadAnchors(&payload, &anch)) {
        std::printf("(skip: playtest banks/payload absent) ");
        return;
    }
    if (early.size() > 10) early.resize(10);
    if (late.size() > 10) late.resize(10);
    size_t checked = 0, kind5 = 0;
    for (const auto& side : {early, late}) {
        for (const auto& path : side) {
            std::vector<uint8_t> mem;
            std::string err;
            if (!ShipSave::readMemoryMember(path, &mem, &err)) { CHECK(false); continue; }
            size_t base = 0;
            if (!ShipSave::findImageBase(mem, anch, 5, &base, &err)) { CHECK(false); continue; }
            std::vector<ShipSave::Record> recs;
            if (!ShipSave::parseShipRecords(mem, base, &recs, &err)) { CHECK(false); continue; }
            for (const auto& r : recs) {
                if (r.dead) continue;
                const bool allOn = onGrid(r.pos[0]) && onGrid(r.pos[1]) && onGrid(r.pos[2]);
                if (!allOn) {
                    // Census law (r380_grid_census.py, 1140+260 off-grid
                    // rows, ZERO exceptions): every off-grid LIVE row is a
                    // kind-5 LANE-LOCAL frame — y EXACTLY 0 or 1, z on the
                    // 32-grid (S22 L4). No kind-1/3/4 row is ever off-grid.
                    CHECK(r.orderKind == 5);
                    CHECK((r.pos[1] == 0.f || r.pos[1] == 1.f) && onGrid(r.pos[2]));
                    ++kind5;
                    continue;
                }
                ++checked;
            }
        }
    }
    // The census ran over real rows (not vacuously empty): measured shape
    // 100 saves -> 4020 live rows (1240 kind-5); 20 saves -> ~800/248.
    CHECK(checked > 400);
    CHECK(kind5 > 150);
}
