// SPDX-License-Identifier: GPL-3.0-or-later

// tRS-V2w RESEARCH APPLY LAW + FRELOADER TERM (cited FUN_00046aec;
// disassembly work/tRSV2w_46aec.asm; law docs/re/income-law.md tRS-V2w
// block + docs/re/research.md S9(e); diagnosis docs/re/_wip_tRSV2.md P11).
//
// Vendor chain (call site 0x25028 mov eax,0x74744 / 0x2502f call 0x46aec):
//   bucket[race] rebuilds each turn: + word[planet+0x46] per owned planet
//   (0x46b80/0x46b84), +1 per NON-current-player planet iff
//   byte[0x13bc4]==2 AND word[+0x46] < 15 (0x46b5b..0x46b77).
//   APPLY (0x46bcd..0x46c1b): bucket==0 -> je 0x46c02 adds NOTHING; else
//   progress word[0x764a0+2r] += TRUNC((bucket+1)^0.85) — the immediates
//   0x3feb3333:0x33333333 ARE the double 0.85 (push 0x46bdc/0x46be5), pow
//   0x78a90, frndint-CHOP 0x76e08, fistp 0x46bfe. Same (v+1)^0.85 floor
//   shape as the IND display law (income-law.md T34) — NEVER the raw
//   stockpile the old port added (campaign.cpp:1514 pre-fix).
#include "game/campaign.h"

#include <cmath>
#include <fstream>
#include <iterator>
#include <string>

#include "harness.h"

#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif

namespace {
// Values recomputed from the law, NEVER transcribed (tRS-V2p hex lesson):
// trunc((b+1)^0.85) for b = 0..15.
int expectedAdd(int b) {
    return static_cast<int>(std::floor(std::pow(static_cast<double>(b) + 1.0,
                                                0.85)));
}
}  // namespace

TEST(resapply_zero_bucket_adds_nothing_tRSV2w) {
    // 0x46bd7 test eax,eax / je 0x46c02: a zero bucket adds NOTHING
    // (the tRS-V2p grown-leg mystery: player bucket 0 for ~117 turns on
    // seed 5 -> progress 0 is VENDOR FAITHFUL, not a defect).
    CHECK(ascend::game::researchProgressAdd(0.0) == 0);
    CHECK(ascend::game::researchProgressAdd(-3.0) == 0);
}

TEST(resapply_compression_law_tRSV2w) {
    // trunc((b+1)^0.85) on the whole small-bucket range. The RAW add the
    // port used to do is refuted from b>=2 upward; floor-vs-round is
    // discriminated at b=1 (2^0.85 = 1.8025 -> 1, round would give 2) and
    // b=4 (5^0.85 = 3.928 -> 3).
    // b==0 is the zero-gate leg (test above), NOT the pow leg: start at 1.
    for (int b = 1; b <= 15; ++b)
        CHECK(ascend::game::researchProgressAdd(static_cast<double>(b)) ==
              expectedAdd(b));
    CHECK(expectedAdd(1) == 1);   // not 2 (round) and not 1.8025 (raw)
    CHECK(expectedAdd(15) == 10); // 16^0.85 = 10.556 -> 10
    CHECK(expectedAdd(14) == 9);  // 15^0.85 = 9.9929 -> 9 (floor edge)
}

TEST(resfreeloader_gates_tRSV2w) {
    // 0x46b63 cmp byte[0x13bc4],2 (gov gate; live ==1 20/20 saves => the
    // whole term is DEAD in the shipped scenario) and 0x46b72 cmp edx,0xf
    // (stored RES word < 15 STRICT).
    CHECK(ascend::game::resFreeloaderAdd(0, 1) == 0);    // shipped gov 1
    CHECK(ascend::game::resFreeloaderAdd(14, 1) == 0);
    CHECK(ascend::game::resFreeloaderAdd(0, 2) == 1);    // gov 2, RES 0
    CHECK(ascend::game::resFreeloaderAdd(14, 2) == 1);   // < 15 strict
    CHECK(ascend::game::resFreeloaderAdd(15, 2) == 0);   // 15 NOT < 15
    CHECK(ascend::game::resFreeloaderAdd(99, 2) == 0);
}

TEST(resapply_port_wiring_tRSV2w) {
    // researchPhase must apply the LAW function, not the raw stockpile,
    // and incomeAndGrow must carry the freeloader arm (source-text pin,
    // the tNGS29 precedent).
    std::ifstream f(std::string(ASCENDANCY_SOURCE_DIR) +
                    "/rewrite/src/game/campaign.cpp");
    std::string src((std::istreambuf_iterator<char>(f)),
                    std::istreambuf_iterator<char>());
    CHECK(!f.fail());
    CHECK(src.find("researchProgressAdd(res[o])") != std::string::npos);
    CHECK(src.find("techProgress[o] += res[o]") == std::string::npos);
    CHECK(src.find("resFreeloaderAdd(") != std::string::npos);
}
