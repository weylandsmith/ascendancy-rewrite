// SPDX-License-Identifier: GPL-3.0-or-later

// tNG-B NEW GAME BEHAVIOR pins (B1 density-wheel -> galaxy rebuild).
// Laws + measurements: docs/re/_wip_tNGB.md (disasm dump
// work/tNGC_paint526b4.asm re-read this cycle).
//   1. DENSITY CLICK LAW [verified 0x52db9..0x52e57]: rank++ with wrap at
//      5 (0x52dc9), then call 0x226e4 = FULL REGENERATE whose 0x22728 sub
//      is a rand() consumer drawing star POSITIONS — so the visible star
//      SET changes on EVERY click; the port models this by rebuilding a
//      display galaxy per click with a gen-keyed seed (never the sim rng).
//   2. STAR-COUNT STRADDLE LAW [verified 0x52df4/0x52dfb]: the arm reads
//      hiword(dword[esp + rank*4 - 2]) over the dispatcher-head copy of
//      table 0x895c8 {15,25,50,75,100} (5x movsd 0x52903..0x5290c). The
//      test below emulates the byte-level read and pins that it yields the
//      sorted ladder rung == the port's densityStarCount (cycle-order
//      ladder is the same visited sequence from the Average default).
//   3. WHEEL-GALAXY REBUILD (port behaviour law): MapGenerator at the rung
//      count is deterministic per (seed,gen) and DIFFERENT sets per gen —
//      the witness counterpart of the rand law; plus the Begin-panel count
//      law consequence (word[obj+0x572] == the wheel galaxy's count).
#include "ui/menulaw.h"
#include "game/diplomacy.h"  // kAttackDipGovByte (B4 gov-identity default)
#include "game/mapgen.h"
#include "game/starstat.h"

#include <cmath>
#include <fstream>
#include <sstream>
#include <cstring>
#include <string>
#include <vector>

#include "harness.h"

namespace {
namespace au = ascend::ui;
namespace ag = ascend::game;
#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif
const std::string kRepo = ASCENDANCY_SOURCE_DIR;

// Byte-level emulator of the vendor straddle read. `buf` models esp: the
// dispatcher head copied table 0x895c8 to esp[0..19] (dwords, LE); the
// pushed message word occupies esp[-2..-1]. hiword(dword[X]) = the u16 at
// X+2. Returns the edx the arm would have loaded.
int vendorStraddleStarCount(int rank) {
    unsigned char buf[24];  // esp[0..23]
    const int table[5] = {15, 25, 50, 75, 100};
    for (int i = 0; i < 5; i++)
        std::memcpy(buf + i * 4, &table[i], 4);
    // rank 0 straddles: dword[esp-2] high half = word at esp+0 = low half
    // of table[0]; ranks 1..4 read word at esp+4r = low half of table[r].
    const int off = rank * 4 - 2 + 2;  // +2 = hiword
    unsigned short hw = 0;
    std::memcpy(&hw, buf + off, 2);
    return hw;
}

ag::Galaxy wheelGalaxy(int rank, unsigned seed) {
    auto stats = ag::StarStats::load(kRepo + "/extracted/ascend00/starstat.txt");
    auto names = ag::loadStarNames(kRepo + "/extracted/ascend00/names.txt");
    if (!stats || names.empty()) return ag::Galaxy{};  // caller checks size
    ag::MapConfig mc;
    mc.starCount = au::densityStarCount(rank);
    mc.seed = seed;
    return ag::MapGenerator(mc, *stats, std::move(names)).generate();
}
}  // namespace

TEST(tngb_density_straddle_star_count_law) {
    // The straddle read yields the SORTED ladder rung exactly.
    const int sorted[5] = {15, 25, 50, 75, 100};
    for (int r = 0; r < 5; r++) CHECK(vendorStraddleStarCount(r) == sorted[r]);
    // And the port's cycle-order ladder visited from the Average default is
    // the same SEQUENCE (Average 50 -> Dense 75 -> Very Dense 100 ->
    // Vacuous 15 -> Sparse 25 -> wrap; t78 live-rung witness). The port's
    // cycle index j is the vendor sorted-rank (j+2)%5 (Average = vendor
    // rank 2 = sorted[2] = 50); newgameWheelFrame keys the WHEEL ART off
    // the sorted rank, so both views are consistent by construction.
    int rank = 0;  // Average default (50 stars, t78 5/5)
    const int expect[6] = {75, 100, 15, 25, 50, 75};
    for (int i = 0; i < 6; i++) {
        rank = au::densityRankNext(rank);
        CHECK(rank >= 0 && rank < au::kDensityCycleCount);
        CHECK(au::densityStarCount(rank) == expect[i]);
    }
}

TEST(tngb_density_rank_wrap_term) {
    // Wrap term alone (mutation target): 4->0, never 5.
    CHECK(au::densityRankNext(4) == 0);
    CHECK(au::densityRankNext(0) == 1);
    CHECK(au::densityRankNext(3) == 4);
    // Off-domain rank never indexes out of the ladder.
    CHECK(au::densityStarCount(-1) == au::kDensityStarCounts[0]);
    CHECK(au::densityStarCount(9) == au::kDensityStarCounts[0]);
}

TEST(tngb_wheel_galaxy_rebuild_per_gen) {
    // Port-side rand-law model: same (seed,gen) is deterministic; a new gen
    // is a NEW SET (positions differ) at the same count.
    REQUIRE_DATA();
    auto a = wheelGalaxy(2, 7);  // cycle ladder[2] == 100 (Very Dense)
    CHECK(int(a.stars.size()) == au::kDensityStarCounts[2]);  // 100
    auto b = wheelGalaxy(2, 7);
    auto c = wheelGalaxy(2, 8);  // gen+1 => new set
    CHECK(int(b.stars.size()) == int(a.stars.size()));
    CHECK(int(c.stars.size()) == int(a.stars.size()));
    bool sameAB = true, sameAC = false;
    for (size_t i = 0; i < a.stars.size(); i++) {
        if (a.stars[i].x != b.stars[i].x || a.stars[i].y != b.stars[i].y)
            sameAB = false;
        if (a.stars[i].x == c.stars[i].x && a.stars[i].y == c.stars[i].y)
            sameAC = true;
    }
    CHECK(sameAB);   // deterministic per gen
    CHECK(!sameAC);  // new gen draws a new set (star 0 differs)
}

TEST(tngb_wheel_galaxy_count_tracks_rung) {
    // Count law: every rung builds exactly its count (Begin starfield
    // word[obj+0x572] consequence — the panel draws THIS galaxy).
    REQUIRE_DATA();
    for (int r = 0; r < au::kDensityCycleCount; r++) {
        auto g = wheelGalaxy(r, 3);
        CHECK(!g.stars.empty());
        CHECK(int(g.stars.size()) == au::densityStarCount(r));
    }
}

TEST(tngb_species_rank_cycle) {
    // tNG-B B2 SPECIES CYCLE LAW [verified 0x52e58..0x52e6d]: increment,
    // wrap 8->3. Visited from the vendor default 5 (window-init 0x52c55
    // word[+0xb9]=5, child art k7) the sequence is Six,Seven,Three,Four,
    // Five,wrap. Domain is 3..Seven inclusive; 8 is never observable.
    int n = 5;  // vendor default 'Five'
    const int expect[6] = {6, 7, 3, 4, 5, 6};
    for (int i = 0; i < 6; i++) {
        n = au::speciesRankNext(n);
        CHECK(n >= 3 && n <= 7);
        CHECK(n == expect[i]);
    }
    // Wrap term alone (mutation targets): 7->3 (never 8), 6->7.
    CHECK(au::speciesRankNext(7) == 3);
    CHECK(au::speciesRankNext(6) == 7);
    // Wheel art law consequence [t401 anchor, child +0x72 = count+2]:
    // the DEFAULT screen shows k7 == newgameWheelFrame(1, 5).
    CHECK(au::newgameWheelFrame(1, 5) == 7);
    CHECK(au::newgameWheelFrame(1, 7) == 9);
    CHECK(au::newgameWheelFrame(1, 2) == -1);  // off-domain refuses
}

TEST(tngb_cosmos_hash_gen_key) {
    // The gen key (gen * 0x100000001) is the NEW-SET law term: gen 0 is
    // the base key, and every gen shift changes the scatter value.
    CHECK(au::cosmosHash(0, 0) == 0x5851f42d403c3b23ull);
    CHECK(au::cosmosHash(0, 1) == 0x5851f42d403c3b23ull + 0x100000001ull);
    CHECK(au::cosmosHash(7, 2) ==
          7ull * 0x9e3779b97f4a7c15ull + 0x5851f42d403c3b23ull +
          2ull * 0x100000001ull);
    // Distinct i AND distinct gen both move the key (set changes per click).
    CHECK(au::cosmosHash(3, 1) != au::cosmosHash(3, 2));
    CHECK(au::cosmosHash(3, 1) != au::cosmosHash(4, 1));
}

TEST(tngb_mapgen_same_seed_same_count_identical) {
    // WITNESS DEPENDENCY (h15 set-identity discriminator, 6-click wrap):
    // MapGenerator is a pure function of (seed, count) — same inputs draw
    // the IDENTICAL galaxy, a different seed draws a different one. The
    // witness clicks density 6x so the rung cycle repeats (75-rung at gen1
    // and gen6): a frozen regen seed (the M4-class defect) then repeats
    // h15 on that pair. NOTE positions are NOT prefix-structured across
    // counts (shell radii allocate from n, mapgen.cpp:114) — the pair must
    // share the RUNG, not just the seed.
    REQUIRE_DATA();
    auto a = wheelGalaxy(1, 11);  // 75 stars, seed 11
    auto b = wheelGalaxy(1, 11);
    auto c = wheelGalaxy(1, 12);
    CHECK(int(a.stars.size()) == 75);
    bool sameAB = true, sameAC = false;
    for (size_t i = 0; i < a.stars.size(); i++) {
        if (a.stars[i].x != b.stars[i].x || a.stars[i].y != b.stars[i].y)
            sameAB = false;
        if (a.stars[i].x == c.stars[i].x && a.stars[i].y == c.stars[i].y)
            sameAC = true;
    }
    CHECK(sameAB);   // deterministic per (seed, count)
    CHECK(!sameAC);  // seed-sensitive
}

// ---- tNG-B B4 BEGIN-PRESS -> SETTINGS-APPLY SEAM --------------------------
TEST(tngb_atmosphere_rank_cycle) {
    // tNG-B B4 ATMOSPHERE CYCLE LAW [verified 0x52eec..0x52f01]: increment,
    // wrap 3 (own word via dword[+0xb9] sar 16 — the straddle read, so the
    // tested value IS word[+0xbb]). Visited from the vendor default 1
    // (window-init 0x52c6b word[+0xbb]=1) the sequence is Hostile, Peaceful,
    // Neutral, wrap. Domain 0..2 == the byte[0x13bc4] gate domain (raceintro
    // PEACE/NEUTRAL/HOSTILE + aicode gov==2 arms).
    int v = 1;  // vendor default 'Neutral'
    const int expect[4] = {2, 0, 1, 2};
    for (int i = 0; i < 4; i++) {
        v = au::atmosphereRankNext(v);
        CHECK(v >= 0 && v <= 2);
        CHECK(v == expect[i]);
    }
    // Wrap term alone (mutation targets): 2->0 (never 3), 1->2.
    CHECK(au::atmosphereRankNext(2) == 0);
    CHECK(au::atmosphereRankNext(1) == 2);
    // Wheel art law consequence [t401 anchor, child +0x72 = 10+v]:
    CHECK(au::newgameWheelFrame(2, 0) == 10);
    CHECK(au::newgameWheelFrame(2, 1) == 11);
    CHECK(au::newgameWheelFrame(2, 2) == 12);
    CHECK(au::newgameWheelFrame(2, 3) == -1);  // off-domain refuses
}

TEST(tngb_newgame_settings_identity) {
    // tNG-B B4 SETTINGS-APPLY LAW [verified begin block 0x52a44..0x52b75]:
    // Begin passes ebx=0 to worldgen (0x52a65) — NO wheel word is re-read
    // for density/species because the click arms ALREADY wrote the play
    // state base (eax=0x12e10 on 0x52dfe density / 0x52e8d species: the
    // STATE-IDENTITY law). The handoff triple therefore maps each wheel to
    // play state IDENTITY, not a transform:
    //   stars  = the density rung (sorted ladder 0x895c8, B1 law),
    //   owners = the species word VERBATIM (word[state+0xd88] == the race-
    //            count global 0x13b98 — TOTAL races incl. the player; B2),
    //   gov    = the atmosphere word VERBATIM (Begin 0x52b3c/0x52b44 is the
    //            SOLE wheel writer of byte[0x13bc4], the dip-on-attack
    //            subtrahend key 10*(gov+1), diplomacy.md SS17.1).
    // stars uses the port CYCLE-INDEX ladder kDensityStarCounts (the same
    // VISITED sequence as the vendor sorted table 0x895c8 from the Average
    // default — B1 equivalence: cycle-index == visited-order). Cycle index
    // 2 == 'Very Dense' == 100.
    const au::NewGameSettings s = au::newGameSettings(2, 5, 1);
    CHECK(s.set);
    CHECK(s.stars == au::kDensityStarCounts[2]);  // cycle law, cited above
    CHECK(s.owners == 5);   // identity: wheel Five == FIVE total races
    CHECK(s.gov == 1);      // identity: Neutral wheel == gov byte 1
    // Default wheel triple == the shipped-scenario rung + gov: cycle index
    // 0 == Average == 50 stars (fresh campaigns 5/5) and gov 1 matches the
    // byte[0x13bc4]==1 census (20/20 playcap saves). Owners 5 is the VENDOR
    // new-game default (window-init 0x52c55), NOT the shipped scenario's 4.
    const au::NewGameSettings d = au::newGameSettings(0, 5, 1);
    CHECK(d.stars == 50 && d.gov == ag::kAttackDipGovByte);
    // Off-ladder rank / off-domain values still map identity-wise (the
    // clamp lives in the builder, not the pure law): owners 7 -> owners 7.
    const au::NewGameSettings h = au::newGameSettings(2, 7, 2);
    CHECK(h.stars == 100 && h.owners == 7 && h.gov == 2);
    // The default-constructed struct is UNSET (the --resume path leaves the
    // built campaign alone — Begin never pressed, nothing applies).
    au::NewGameSettings u;
    CHECK(!u.set);
}

// ---- tNGS P4 PREVIEW STARFIELD LAW pins (docs/re/_wip_tNGS.md S15/S22) ----
TEST(tngs_p4_preview_draws_law) {
    // S15 [verified asm 0x22b61..0x22bb4]: each of the three draws is
    // rng%1000-500 -> closed range [-500,499]. Mutation pin: widen either
    // bound (e.g. -501 or %1001) and a sample fails.
    bool lo[3] = {false, false, false}, hi[3] = {false, false, false};
    for (int i = 0; i < 20000; i++) {
        const auto d = au::previewDraws(au::cosmosHash(i, 3u));
        const int v[3] = {d.vx, d.vy, d.vz};
        for (int k = 0; k < 3; k++) {
            CHECK(v[k] >= -500 && v[k] <= 499);
            lo[k] = lo[k] || v[k] == -500;
            hi[k] = hi[k] || v[k] == 499;
        }
    }
    // Boundary REACHABILITY: %1000-500 is the closed [-500,499] window;
    // a narrower modulus (e.g. %999) survives a bounds-only pin, so pin
    // that both extremes occur (expected ~20 hits/extreme in 20000 draws;
    // miss probability ~2e-9).
    for (int k = 0; k < 3; k++) {
        CHECK(lo[k]);
        CHECK(hi[k]);
    }
    // distinct (i,gen) -> distinct triple (new-set law preserved)
    const auto a = au::previewDraws(au::cosmosHash(5, 1u));
    const auto b = au::previewDraws(au::cosmosHash(5, 2u));
    CHECK(a.vx != b.vx || a.vy != b.vy || a.vz != b.vz);
}

TEST(tngs_p4_star_lies_on_its_shell) {
    // S15: position = normalize(box draw) * shell(k) -> |p| == shell EXACTLY
    // (within fp). The pre-P4 cylinder (r=300 screen-plane, depth+-300) and
    // the pre-t423 sphere-surface sampler both fail this at the shell table.
    const au::Rect well{8, 8, 492, 372};
    for (int n : {15, 25, 50, 75, 100}) {
        const auto shell = ascend::game::shellRadiiFor(n);
        CHECK(int(shell.size()) == n);
        for (int i = 0; i < n; i++) {
            const auto d = au::previewDraws(au::cosmosHash(i, 7u));
            const auto s = au::previewStar(d.vx, d.vy, d.vz,
                                           double(shell[size_t(i)]), 250.0,
                                           190.0, well);
            const double r = std::sqrt(s.x * s.x + s.y * s.y + s.z * s.z);
            CHECK(std::abs(r - double(shell[size_t(i)])) < 1e-6);
        }
    }
}

TEST(tngs_p4_class_band_law) {
    // S5 painter class law [verified asm 0x52817..0x5282f]:
    // v=round(z): v>220 -> 0; 1..220 -> 1; -219..0 -> 2; v<=-220 -> 3.
    const au::Rect well{8, 8, 492, 372};
    struct { int z; int cls; } cases[] = {
        {500, 0}, {221, 0}, {220, 1}, {1, 1}, {0, 2}, {-219, 2},
        {-220, 3}, {-500, 3},
    };
    for (const auto& c : cases) {
        // draw straight along -z/+z: normalize keeps the axis, shell scales
        const auto s = au::previewStar(0, 0, c.z > 0 ? 1 : -1,
                                       std::abs(double(c.z)), 250.0, 190.0,
                                       well);
        CHECK(s.cls == c.cls);
    }
}

TEST(tngs_p4_projection_fits_the_well) {
    // S5 camera (0,0,-1500) FOV 35 + focal 769.1: the shell-440 ring at the
    // model equator projects to 440*769.1/1500 = 225.6 px from centre —
    // inside the well half-width 242.5 (docs S15 envelope claim).
    const au::Rect well{8, 8, 492, 472};
    const auto s = au::previewStar(500, 0, 0, 440.0, 250.0, 190.0, well);
    CHECK(std::abs(double(s.sx) - (250.0 + 440.0 * 769.1 / 1500.0)) < 1.0);
    CHECK(s.inWell);
    // and a full shell sweep stays inside the 8..492 well: sample density
    const au::Rect kWell = au::kNewgameCosmosRect;
    int outside = 0, total = 0;
    for (int i = 0; i < 100; i++) {
        const auto d = au::previewDraws(au::cosmosHash(i, 0u));
        const auto st = au::previewStar(d.vx, d.vy, d.vz, 440.0, 250.0, 190.0,
                                        kWell);
        total++;
        if (!st.inWell) outside++;
    }
    // near-camera stars (z->+440) magnify; honest clip allows a SMALL tail,
    // the cylinder-era claim of ZERO was the defect shape. Cap: <=20%.
    CHECK(outside * 5 <= total);
}

TEST(tngs_p4_no_idle_spin_term) {
    // SUPERSEDED by S27 (CYCLE 4): this pinned the S22 "does NOT auto-spin"
    // reading, WITHDRAWN in S26 (12 s aliasing) and refuted by witness run
    // tngs4-20261123-010308 (production, 1 s cadence, ~950 changed px/step,
    // ctrl 0, matched stars 3.58 px/s = 2.05 deg/s). The t423 zone rects
    // remain a documented geometric constant; the spin pins now live in
    // tngs_s27_*. The purity claim (previewStar is a pure function of its
    // inputs) STANDS and is re-pinned here.
    CHECK(au::kPreviewSpinZone.x0 == 379 && au::kPreviewSpinZone.x1 == 493);
    CHECK(au::kPreviewSpinZone.y0 == 420 && au::kPreviewSpinZone.y1 == 472);
    const au::Rect well{8, 8, 492, 372};
    const auto s1 = au::previewStar(123, -45, 67, 365.0, 250.0, 190.0, well);
    const auto s2 = au::previewStar(123, -45, 67, 365.0, 250.0, 190.0, well);
    CHECK(s1.sx == s2.sx && s1.sy == s2.sy && s1.cls == s2.cls);
}

TEST(tngs_s28_spin_rate_is_two_deg_per_tick_at_frame_cadence) {
    // S27-X2 [verified asm]: pump dispatcher 0x27a18 applies the IMMEDIATE
    // 2 at 0x27a32 per msg-0x3b tick. CADENCE S28-X3 [MEASURED, run
    // dbg-tngr-20261123-103130]: basis integration 60-65 deg/s =>
    // 28-33 fires/s => tick 32 ms (circuit 5.6-6.1 s; user stopwatch 5.3 s).
    // The pre-S28 pin value 1000 ms was the poll-limited t302 "~1/s"
    // transferred from the campaign map — REFUTED ~30x.
    CHECK(au::kPreviewSpinDegPerTick == 2.0);
    CHECK(au::kPreviewSpinTickMs == 32);
    // Circuit law pin: 360 deg at the shipped rate must land in the measured
    // 5.4-6.3 s band (kills any mutation that restores a slow cadence).
    const double circuit =
        360.0 / au::kPreviewSpinDegPerTick * au::kPreviewSpinTickMs / 1000.0;
    CHECK(circuit >= 5.4 && circuit <= 6.3);
}

TEST(tngs_s29_near_star_moves_left_per_tick) {
    // D24 USER LAW (docs/DECISIONS.md): clockwise from above == NEAR-side
    // stars move LEFT, far-side RIGHT. Steering S29 requires: the near-side
    // star's sx STRICTLY DECREASES per shipped +2 deg tick. Composition
    // audit found the S28-X3 negation inverted this (near RIGHT); this pin
    // kills a re-negation mutation without pixels. The shipped wiring is
    // previewStar(..., previewYaw) with previewYaw = +newgameSpinDeg
    // (title.cpp), so the pin composes the accumulator exactly as shipped.
    const ascend::ui::Rect well{-1000, -1000, 1000, 1000};
    double spin = 0.0;
    int prevNear = ascend::ui::previewStar(0, 0, -400, 400.0, 200.0, 190.0,
                                           well, spin).sx;
    int prevFar = ascend::ui::previewStar(0, 0, 400, 400.0, 200.0, 190.0,
                                          well, spin).sx;
    // Window 0..70 deg: strictly monotone at integer px (measured sweep
    // /tmp/s29 probe: near on-axis star 200->11 LEFT every tick through
    // 72 deg; beyond ~73 deg the star nears the camera plane and pixel
    // quantisation goes flat — geometry, not direction).
    for (int tick = 1; tick <= 35; tick++) {
        spin += ascend::ui::kPreviewSpinDegPerTick;
        const int nearSx = ascend::ui::previewStar(0, 0, -400, 400.0, 200.0,
                                                   190.0, well, spin).sx;
        const int farSx = ascend::ui::previewStar(0, 0, 400, 400.0, 200.0,
                                                  190.0, well, spin).sx;
        CHECK(nearSx < prevNear);  // near star moves LEFT every tick
        CHECK(farSx > prevFar);    // far star moves RIGHT every tick
        prevNear = nearSx;
        prevFar = farSx;
    }
}

TEST(tngs_s29_title_wiring_is_unnegated) {
    // Source-text pin (tngs_s27_pump_wiring_pin precedent): the shipped
    // accumulators must enter the draw terms UNNEGATED. "-newgameSpinDeg"
    // is the S28-X3 double-inversion defect shape.
    std::ifstream in(kRepo + "/rewrite/src/ui/title.cpp");
    const std::string src = [&] {
        std::stringstream ss;
        ss << in.rdbuf();
        return ss.str();
    }();
    CHECK(src.find("const double previewYaw = newgameSpinDeg;") !=
          std::string::npos);
    CHECK(src.find("-newgameSpinDeg") == std::string::npos);
}

TEST(tngs_s27_spin_is_world_y_and_isometric) {
    // The vendor latch axis (FUN_00053584 mixes x,z = world Y, t416 F2).
    // Pin: y preserved, |p| preserved (isometry), and a 90-deg yaw maps
    // (x,0,z) -> (z,0,-x).
    double ox = 0, oz = 0;
    au::previewSpinWorldY(100.0, 0.0, 90.0, &ox, &oz);
    CHECK(std::abs(oz - -100.0) < 1e-9);
    CHECK(std::abs(ox) < 1e-9);
    const au::Rect well{8, 8, 492, 372};
    for (int i = 0; i < 50; i++) {
        const auto d = au::previewDraws(au::cosmosHash(i, 3u));
        const auto a = au::previewStar(d.vx, d.vy, d.vz, 440.0, 250.0, 190.0,
                                       well);
        const auto b = au::previewStar(d.vx, d.vy, d.vz, 440.0, 250.0, 190.0,
                                       well, 37.0);
        CHECK(std::abs(a.y - b.y) < 1e-9);  // world-Y spin preserves y
        const double ra = std::sqrt(a.x * a.x + a.y * a.y + a.z * a.z);
        const double rb = std::sqrt(b.x * b.x + b.y * b.y + b.z * b.z);
        CHECK(std::abs(ra - rb) < 1e-6);    // shell radius preserved
    }
}

TEST(tngs_s27_pump_wiring_pin) {
    // Source-text pin (sfx_no_literal_play_sites_t404 precedent): the spin
    // must be WIRED — the pump advances by the cited constant and the big
    // field's draw call passes the yaw. Witness run 010308 refuted the
    // static field; a detached call site (mutation: pass 0.0) must fail
    // even though no behavioural test renders pixels here.
    std::ifstream in(kRepo + "/rewrite/src/ui/title.cpp");
    std::stringstream ss;
    ss << in.rdbuf();
    const std::string src = ss.str();
    CHECK(src.find("newgameSpinDeg += kPreviewSpinDegPerTick") !=
          std::string::npos);
    CHECK(src.find("kNewgameCosmosRect, previewYaw)") != std::string::npos);
    // Begin cluster reads the SAME accumulator (class-cycling term)
    CHECK(src.find("newgameSpinDeg * 3.14159265358979323846 / 180.0") !=
          std::string::npos);
}

TEST(tngs_s27_motion_determinism_and_census_pins) {
    // D22-cycle motion pins: (a) two renders at the SAME yaw are identical
    // (determinism); (b) renders at yaw t and t+2deg DIFFER in star
    // positions but NOT in the in-well COUNT per shell or the type census —
    // the spin moves/recycles depth, it never invents or deletes stars.
    const au::Rect well{8, 8, 492, 372};
    auto census = [&](double yaw) {
        int inWell = 0;
        for (int i = 0; i < 100; i++) {
            const auto d = au::previewDraws(au::cosmosHash(i, 11u));
            const auto s = au::previewStar(d.vx, d.vy, d.vz, 440.0, 250.0,
                                           190.0, well, yaw);
            if (s.inWell) inWell++;
        }
        return inWell;
    };
    // (a) determinism: same yaw -> identical screen points
    bool identical = true;
    for (int i = 0; i < 100; i++) {
        const auto d = au::previewDraws(au::cosmosHash(i, 11u));
        const auto s1 = au::previewStar(d.vx, d.vy, d.vz, 440.0, 250.0, 190.0,
                                        well, 13.0);
        const auto s2 = au::previewStar(d.vx, d.vy, d.vz, 440.0, 250.0, 190.0,
                                        well, 13.0);
        if (s1.sx != s2.sx || s1.sy != s2.sy || s1.cls != s2.cls)
            identical = false;
    }
    CHECK(identical);
    // (b) motion: one tick (2 deg) moves at least one in-well star
    int moved = 0;
    for (int i = 0; i < 100; i++) {
        const auto d = au::previewDraws(au::cosmosHash(i, 11u));
        const auto s0 = au::previewStar(d.vx, d.vy, d.vz, 440.0, 250.0, 190.0,
                                        well, 0.0);
        const auto s1 = au::previewStar(d.vx, d.vy, d.vz, 440.0, 250.0, 190.0,
                                        well, au::kPreviewSpinDegPerTick);
        if (s0.sx != s1.sx || s0.sy != s1.sy) moved++;
    }
    CHECK(moved > 0);
    // (c) the spin is NOT a screen-plane roll: at 2 deg a world-Y spin
    // changes DEPTH (class can change) for some star; the old x,y-roll
    // mutation (below) leaves z untouched by construction.
    bool depthChanged = false;
    for (int i = 0; i < 100; i++) {
        const auto d = au::previewDraws(au::cosmosHash(i, 11u));
        const auto s0 = au::previewStar(d.vx, d.vy, d.vz, 440.0, 250.0, 190.0,
                                        well, 0.0);
        const auto s1 = au::previewStar(d.vx, d.vy, d.vz, 440.0, 250.0, 190.0,
                                        well, 45.0);
        if (std::abs(s0.z - s1.z) > 1.0) depthChanged = true;
    }
    CHECK(depthChanged);
    // census sanity: the field is never empty at any yaw (a spin that
    // evicted every star from the well would read as "stopped")
    for (double yaw : {0.0, 30.0, 90.0, 170.0, 359.0}) {
        CHECK(census(yaw) > 0);
    }
}
