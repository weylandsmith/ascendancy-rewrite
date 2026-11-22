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
#include "game/mapgen.h"
#include "game/starstat.h"

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
