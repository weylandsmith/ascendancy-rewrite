// SPDX-License-Identifier: GPL-3.0-or-later
// t411 MAP LOOK PASS 2 pins. Laws + citations: ui/mapchrome.h (mottle cell
// law), ui/cam3d.h (depth dim); measurement trail docs/re/_wip_t411.md
// (F2 blend root cause is SDL wiring — witnessed mechanically by
// scripts/t411_maplook_witness.sh pale-pixel census; F4 mottle statistic
// swept by scripts/t411_mottle.py; F5 bevel ramp constants are the wiring).
#include <cstdint>
#include <set>

#include "harness.h"
#include "ui/cam3d.h"
#include "ui/mapchrome.h"

using namespace ascend::ui;

TEST(mottle_cell_law_t411) {
    // t411 F4: texture colour is constant over a 6x6 CELL (the vendor band
    // is smooth at pixel scale: lag-1 0.23 vs per-pixel 1.45), still
    // deterministic, and the cell grid must NOT be a power of two (a cell-4
    // mutant must fail: pixel 11 vs 12 straddle a cell boundary, 7 vs 8 do
    // not under >>2).
    for (int x = 0; x < 64; x += 1)
        for (int y = 0; y < 64; y += 1) {
            const RGB a = textureColourAt(x, y);
            CHECK(a.r == textureColourAt(x - x % 6, y - y % 6).r);
            CHECK(a.g == textureColourAt(x - x % 6, y - y % 6).g);
            CHECK(a.b == textureColourAt(x - x % 6, y - y % 6).b);
        }
    // Determinism (same input -> same colour; no rng consumption).
    for (int i = 0; i < 40; i++) {
        const RGB a = textureColourAt(3, 100 + i), b = textureColourAt(3, 100 + i);
        CHECK(a.r == b.r && a.g == b.g && a.b == b.b);
    }
    // Non-degenerate: distinct cells produce distinct colours (if EVERY
    // cell mapped to one colour the texture would be flat).
    std::set<uint32_t> seen;
    for (int i = 0; i < 60; i++)
        seen.insert((uint32_t(textureColourAt(6 * i, 12).r) << 16) |
                    (uint32_t(textureColourAt(6 * i, 12).g) << 8) |
                    textureColourAt(6 * i, 12).b);
    CHECK(seen.size() >= 8);
    // Cell-boundary probe: x=5 and x=6 are in DIFFERENT cells (kills a
    // cell-8 mutant that keeps 5|6 together).
    int diffs = 0;
    for (int y = 0; y < 60; y++)
        if (textureColourAt(5, 6 * y).r != textureColourAt(6, 6 * y).r ||
            textureColourAt(5, 6 * y).g != textureColourAt(6, 6 * y).g ||
            textureColourAt(5, 6 * y).b != textureColourAt(6, 6 * y).b)
            diffs++;
    CHECK(diffs >= 30);  // ~66% chance the weighted draw differs per row
}

TEST(depth_dim_law_t411) {
    // t411 F7: monotone non-decreasing with nearness (cls 0 far .. 3 near),
    // near band unscaled, far band at least a quarter dimmer, domain safe.
    CHECK(pipDim256(0) < pipDim256(1));
    CHECK(pipDim256(1) < pipDim256(2));
    CHECK(pipDim256(2) < pipDim256(3));
    CHECK(pipDim256(3) == 256);
    CHECK(pipDim256(0) <= 128);
    CHECK(pipDim256(-1) == 256 && pipDim256(4) == 256);
    // Dimming must be VISIBLE (a multiplier that rounds away differences
    // between adjacent classes on a mid tint would be a silent no-op):
    const int mid = 200;
    CHECK(mid * pipDim256(0) / 256 < mid * pipDim256(2) / 256);
}

TEST(bevel_darker_than_field_frame_t411) {
    // t411 F5: the bevel constants are law data in mapchrome.h; pin the
    // CONTRACT the witness diffs rendered pixels against: both near-black
    // (vendor scan maxima (49,54,53) and (5,6,6)), strictly ramped inward,
    // and strictly darker than the lane colour (120,120,120) the vendor
    // NEVER shows at the field edge.
    CHECK(kBevelMid.r < 120 && kBevelMid.g < 120 && kBevelMid.b < 120);
    CHECK(kBevelIn.r < kBevelMid.r && kBevelIn.g < kBevelMid.g &&
          kBevelIn.b < kBevelMid.b);
    CHECK(int(kBevelMid.r) + kBevelMid.g + kBevelMid.b <= 3 * 65);
    CHECK(int(kBevelIn.r) + kBevelIn.g + kBevelIn.b <= 3 * 10);
    // (49,54,53)/(5,6,6) verbatim from the vendor scans — a mutant may not
    // drift them brighter while keeping the ordering.
    CHECK(kBevelMid.r == 49 && kBevelMid.g == 54 && kBevelMid.b == 53);
    CHECK(kBevelIn.r == 5 && kBevelIn.g == 6 && kBevelIn.b == 6);
}
