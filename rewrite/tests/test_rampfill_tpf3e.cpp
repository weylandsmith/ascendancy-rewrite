// SPDX-License-Identifier: GPL-3.0-or-later

// tPF-3e RAMP-FILL LAW pins.
// Law: docs/re/_wip_tPF3.md F15/F16/F17 (filler 0x62d15 arg law + push
// sequence 0x3be31..0x3be4b; tables byte-stable 60/60 banked saves; ladder
// 0x3bbd6..0x3bc4b over the cell class byte, writer 0x3c2cc).
// The tables themselves are law data in ui/rampfill_law.h, regenerated +
// re-verified against the corpus by scripts/tPF3e_gen_tables.py. These pins
// lock (1) the ladder, (2) the embedded transcription against the MEASURED
// structural facts (distinct-value counts, fixed points, spot bytes from the
// F16 hex), so a bad regeneration or a hand edit fails loudly.
#include <cstdio>
#include <fstream>
#include <iterator>
#include <string>

#include "ui/planetview.h"
#include "ui/rampfill_law.h"
#include "harness.h"

namespace {
namespace au = ascend::ui;

#define REQUIRE(cond)                        \
    do {                                     \
        if (!(cond)) {                       \
            printf("REQUIRE FAIL %s\n", #cond); \
            ascend::test::failures()++;      \
            return;                          \
        }                                    \
    } while (0)

int distinctCount(const uint8_t* row) {
    bool seen[256] = {};
    int n = 0;
    for (int i = 0; i < 256; i++)
        if (!seen[row[i]]) { seen[row[i]] = true; n++; }
    return n;
}

TEST(rampfill_index_law_tpf3e) {
    // 1. THE LADDER (0x3bbd6..0x3bc4b, F15(2)/F17): exact-equality compares on
    //    the cell class byte; default 13. NEVER 0 -> the fill-skip tests
    //    0x3bd31/0x3be2a never fire in the overlay pass (class 0 fills too).
    CHECK(au::tileOverlayFillIndex(0) == 7);    // 0x3bbf5
    CHECK(au::tileOverlayFillIndex(2) == 8);    // 0x3bc1b
    CHECK(au::tileOverlayFillIndex(3) == 9);    // 0x3bc33
    CHECK(au::tileOverlayFillIndex(4) == 10);   // 0x3bc4b
    CHECK(au::tileOverlayFillIndex(1) == 13);   // default path (0x3bbea)
    CHECK(au::tileOverlayFillIndex(5) == 13);
    CHECK(au::tileOverlayFillIndex(8) == 13);   // rock flag alone
    CHECK(au::tileOverlayFillIndex(10) == 13);  // rock+class2: NO compare hits
    CHECK(au::tileOverlayFillIndex(11) == 13);  // rock+class3
    CHECK(au::tileOverlayFillIndex(12) == 13);  // rock+class4
    CHECK(au::tileOverlayFillIndex(255) == 13);
    for (int c = 0; c < 256; c++)
        CHECK(au::tileOverlayFillIndex(c) != 0);
}

TEST(rampfill_table_transcription_tpf3e) {
    // 2. THE EMBEDDED TABLES match the F16-measured structural facts. The
    //    distinct-value counts (39/252/103/92/80/83/112) are read from the
    //    banked-corpus hex (F16); a transcription error changes one of them.
    CHECK(distinctCount(au::rampFillRow(0)) == 39);
    CHECK(distinctCount(au::rampFillRow(1)) == 252);
    CHECK(distinctCount(au::rampFillRow(7)) == 103);
    CHECK(distinctCount(au::rampFillRow(8)) == 92);
    CHECK(distinctCount(au::rampFillRow(9)) == 80);
    CHECK(distinctCount(au::rampFillRow(10)) == 83);
    CHECK(distinctCount(au::rampFillRow(13)) == 112);
    // idx 1 is the identity EXCEPT four measured swaps (byte-exact re-count of
    // the F16 corpus hex tPF-3e — the tPF-3d doc list omitted one swap AND had
    // the first two's directions TRANSPOSED; this is the measured truth):
    // 0x79->0x80, 0x7f->0x57, 0xf1->0xf0, 0xf3->0x0f (252 distinct).
    const uint8_t* t1 = au::rampFillRow(1);
    int diffs = 0;
    for (int i = 0; i < 256; i++) diffs += (t1[i] != uint8_t(i));
    CHECK(diffs == 4);
    CHECK(t1[0x79] == 0x80);
    CHECK(t1[0x7f] == 0x57);
    CHECK(t1[0xf1] == 0xf0);
    CHECK(t1[0xf3] == 0x0f);
    // Spot bytes from the F16 hex (first bytes of each ladder row):
    CHECK(au::rampFillRow(7)[0] == 0x00);
    CHECK(au::rampFillRow(8)[0] == 0x70);
    CHECK(au::rampFillRow(9)[0] == 0x10);
    CHECK(au::rampFillRow(10)[0] == 0x68);
    CHECK(au::rampFillRow(13)[0] == 0x04);
    // The slots the overlay pass never selects return no row.
    CHECK(au::rampFillRow(0) != nullptr);   // law data present for completeness
    CHECK(au::rampFillRow(2) == nullptr);
    CHECK(au::rampFillRow(6) == nullptr);
    CHECK(au::rampFillRow(11) == nullptr);
    CHECK(au::rampFillRow(0x100) == nullptr);
}

TEST(rampfill_fixed_point_law_tpf3e) {
    // 3. F18: each class pen is a FIXED POINT of its own ladder table — the
    //    reason the vendor screen keeps crisp class-coloured lines even though
    //    the filler runs AFTER the line loop (0x3bd1d loop, 0x3be4b fill).
    //    Pen law F9/tPL-V1: 0->0, 2->117, 3->146, 4->255, else 12.
    CHECK(au::rampFillRow(7)[0] == 0);          // class 0 black
    CHECK(au::rampFillRow(8)[117] == 117);      // class 2 red
    CHECK(au::rampFillRow(9)[146] == 146);      // class 3 green
    CHECK(au::rampFillRow(10)[255] == 255);     // class 4 blue
    // The EXCEPTION (measured F18): class-1 white pen 12 maps to 13 through
    // T13 — the vendor's own white lines on a barren cell take ramp-13.
    CHECK(au::rampFillRow(13)[12] == 13);
    // The pass-1 screen value 150 is NOT a fixed point anywhere in the ladder
    // (that is the visible fill: the interior modulates).
    CHECK(au::rampFillRow(7)[150] != 150);
    CHECK(au::rampFillRow(8)[150] != 150);
    CHECK(au::rampFillRow(9)[150] != 150);
    CHECK(au::rampFillRow(10)[150] != 150);
    CHECK(au::rampFillRow(13)[150] != 150);
}

TEST(rampfill_paint_wiring_tpf3e) {
    // 4. The painter ships the SINGLE-PASS edge-set law (F19): inside pass 3
    //    the map row is consulted, edge pixels take the pen index and the
    //    interior takes 150, and NO separate SDL line draw remains in the
    //    overlay pass (the mapped fixed-point pen IS the line).
    const std::string path = std::string(ASCENDANCY_SOURCE_DIR) +
                             "/rewrite/src/ui/ui.cpp";
    std::string src;
    {
        std::ifstream f(path);
        if (!f) { printf("SKIP rampfill_paint_wiring_tpf3e\n"); return; }
        src.assign(std::istreambuf_iterator<char>(f),
                   std::istreambuf_iterator<char>());
    }
    const size_t pass3 = src.find("PASS 3: tPF-3b/3c/3e THE TILE OVERLAY");
    REQUIRE(pass3 != std::string::npos);
    const size_t end = src.find("Structure art ON the tiles", pass3);
    REQUIRE(end != std::string::npos);
    const std::string body = src.substr(pass3, end - pass3);
    CHECK(body.find("rampFillRow(") != std::string::npos);
    CHECK(body.find("? penIdx") != std::string::npos);
    CHECK(body.find(": 150;") != std::string::npos);
    // F19: no raw line pass left inside the overlay (edge-set law).
    CHECK(body.find("SDL_RenderDrawLine(ren, c.x - he.left") ==
          std::string::npos);
    // The edge raster covers all four diamond edges.
    CHECK(body.find("mark(0, -he.top, -he.left, 0);") != std::string::npos);
    CHECK(body.find("mark(-he.left, 0, 0, he.bottom);") != std::string::npos);
    CHECK(body.find("mark(0, he.bottom, he.right, 0);") != std::string::npos);
    CHECK(body.find("mark(he.right, 0, 0, -he.top);") != std::string::npos);
}

}  // namespace
