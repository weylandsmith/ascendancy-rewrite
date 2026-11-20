// SPDX-License-Identifier: GPL-3.0-or-later
// t424b: the race-intro DARK SPECKLE field law (docs/re/_wip_t424b.md F1/F2).
#include "harness.h"
#include "ui/mapchrome.h"

#include <cstdint>
#include <vector>

namespace au = ascend::ui;

static bool rgbEq(const au::RGB& a, const au::RGB& b) {
    return a.r == b.r && a.g == b.g && a.b == b.b;
}

TEST(introspeckle_t424b_deterministic) {
    // Stateless law: same (x,y) -> same colour every call (no rng).
    for (int i = 0; i < 3; i++) {
        CHECK(rgbEq(au::introSpeckleAt(120, 300), au::introSpeckleAt(120, 300)));
        CHECK(rgbEq(au::introSpeckleAt(7, 7), au::introSpeckleAt(7, 7)));
    }
}

TEST(introspeckle_t424b_census_membership) {
    // Every producible colour is one of the four measured census entries
    // (game.pal idx 0/200/1/196; _wip_t424b F2).
    const std::vector<au::RGB> ok = {{0, 0, 0}, {12, 12, 16}, {12, 12, 12},
                                     {12, 28, 48}};
    int hist[4] = {0, 0, 0, 0};
    for (int y = 46; y < 245; y++)
        for (int x = 12; x < 626; x++) {
            const au::RGB c = au::introSpeckleAt(x, y);
            int hit = -1;
            for (int i = 0; i < 4; i++)
                if (c.r == ok[i].r && c.g == ok[i].g && c.b == ok[i].b)
                    hit = i;
            CHECK(hit >= 0);
            if (hit < 0) return;
            hist[hit]++;
        }
    const long n = hist[0] + hist[1] + hist[2] + hist[3];
    // Census weights 40/30/25/5 +- chain smoothing: assert each family is
    // present at a plausible share (loose bands; the chain correlates but
    // does not change the fresh-draw mix appreciably over 120k px).
    CHECK(hist[0] * 100 > 25 * n && hist[0] * 100 < 55 * n);  // ~40%
    CHECK(hist[1] * 100 > 15 * n && hist[1] * 100 < 45 * n);  // ~30%
    CHECK(hist[2] * 100 > 10 * n && hist[2] * 100 < 40 * n);  // ~25%
    CHECK(hist[3] * 100 > 1 * n && hist[3] * 100 < 15 * n);   // ~5%
}

TEST(introspeckle_t424b_grain_is_correlated_not_iid) {
    // The vendor grain statistics (_wip_t424b F2) are measured through a
    // 1.6266x-scaled screenshot and cannot be graded pixel-for-pixel against
    // an unscaled render (named seam: generator origin + parameters, t433
    // route). What IS asserted: the field is CORRELATED, not iid — the
    // same-colour adjacency rate exceeds the iid expectation sum p_i^2 =
    // 0.4^2+0.3^2+0.25^2+0.05^2 = 0.315 (chain law: 5% copy-left lifts it
    // to ~0.35).
    int same = 0, n = 0;
    for (int y = 46; y < 245; y++)
        for (int x = 12; x < 625; x++) {
            same += rgbEq(au::introSpeckleAt(x, y),
                          au::introSpeckleAt(x + 1, y));
            n++;
        }
    CHECK(same * 1000 > 330 * n);  // > 0.33 > iid 0.315
}

TEST(introspeckle_t424b_decorrelated_from_chrome) {
    // Different salt: the fields must NOT be a translate of each other —
    // census agreement rate stays at chance, not 100%.
    int same = 0, n = 0;
    for (int y = 50; y < 240; y += 3)
        for (int x = 50; x < 620; x += 3) {
            const au::RGB a = au::introSpeckleAt(x, y);
            const au::RGB b = au::textureColourAt(x, y);
            same += (a.r == b.r && a.g == b.g && a.b == b.b);
            n++;
        }
    CHECK(same * 4 < n);  // < 25% coincidental match
}
