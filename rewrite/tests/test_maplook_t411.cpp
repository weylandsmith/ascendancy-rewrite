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

TEST(mottle_field_law_t422) {
    // t422 SUPERSEDES the t411 6x6-cell mottle law (see _wip_t422.md F2/
    // F4: the cell grid was calibrated on a widget-contaminated band;
    // the vendor PURE left band has run stats 0.616/0.234/0.092 that
    // match a per-pixel Markov chain, not cells). Pins now:
    //  (1) determinism (same input -> same colour; no rng consumption);
    //  (2) NON-degeneracy (noise, not flat);
    //  (3) VERTICAL CORRELATION: in a 200-row column, repeat-count is
    //      far above the iid floor (Markov P(repeat)=0.25 + copy-left
    //      chains) but far below 1 (not stripes);
    //  (4) the cell law is GONE: a mutant that re-quantises to a 6x6
    //      grid must change at least some pixels (probe: pixels (1,y)
    //      and (6,y) inside one row are NOT systematically equal, and
    //      (x,y) vs (x - x%6, y - y%6) DIFFER for most pixels).
    for (int i = 0; i < 40; i++) {
        const RGB a = textureColourAt(3, 100 + i), b = textureColourAt(3, 100 + i);
        CHECK(a.r == b.r && a.g == b.g && a.b == b.b);
    }
    std::set<uint32_t> seen;
    for (int i = 0; i < 60; i++)
        seen.insert((uint32_t(textureColourAt(470 + i, 12).r) << 16) |
                    (uint32_t(textureColourAt(470 + i, 12).g) << 8) |
                    textureColourAt(470 + i, 12).b);
    CHECK(seen.size() >= 8);
    // Vertical correlation window [0.27,0.45] [measured: Markov law
    // gives vrep@x3 = 0.330; the iid floor for this column's census is
    // sum(w_i^2)/sum(w)^2 = 0.206 (mutant M2 "chain removed" caught at
    // the floor); the 6x6-cell grid gives 5/6 = 0.833 (mutant M1 caught
    // by both this and the cell probe)].
    int vrep = 0, vtot = 0;
    for (int y = 0; y < 200; y++) {
        const RGB a = textureColourAt(3, y), b = textureColourAt(3, y + 1);
        vtot++;
        if (a.r == b.r && a.g == b.g && a.b == b.b) vrep++;
    }
    CHECK(vrep * 100 >= 27 * vtot);
    CHECK(vrep * 100 <= 45 * vtot);
    // Cell quantisation must be ABSENT: (x,y) equals its own cell-anchor
    // colour for a MINORITY of pixels (a cell-grid generator gives 100%).
    int cellSame = 0, cellTot = 0;
    for (int y = 0; y < 120; y++)
        for (int x = 8; x < 40; x++) {
            const RGB a = textureColourAt(x, y);
            const RGB c = textureColourAt(x - x % 6, y - y % 6);
            cellTot++;
            if (a.r == c.r && a.g == c.g && a.b == c.b) cellSame++;
        }
    CHECK(cellSame * 100 < 60 * cellTot);  // mutant cell-grid: 100%
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
