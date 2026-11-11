// SPDX-License-Identifier: GPL-3.0-or-later

// UI layout math tests. Rect constants are the windows.txt values cited in
// docs/re/ui-runtime.md §1 (COSMOSWnd 7,7..465,472; NEXTTURN 474,52..548,82).
#include "ui/layout.h"

#include <cmath>
#include <cstdlib>

#include "game/mapgen.h"
#include "harness.h"

namespace {
namespace au = ascend::ui;
using ascend::game::Galaxy;
using ascend::game::MapConfig;
using ascend::game::MapGenerator;
using ascend::game::StarStats;
}  // namespace

TEST(layout_constants_match_windows_txt) {
    REQUIRE_DATA();
    CHECK(au::kCosmosWnd.x0 == 7);
    CHECK(au::kCosmosWnd.y0 == 7);
    CHECK(au::kCosmosWnd.x1 == 465);
    CHECK(au::kCosmosWnd.y1 == 472);
    CHECK(au::kNextTurnBtn.x0 == 474);
    CHECK(au::kNextTurnBtn.y0 == 52);
    CHECK(au::kNextTurnBtn.x1 == 548);
    CHECK(au::kNextTurnBtn.y1 == 82);
    CHECK(au::kDisplayW == 640);
    CHECK(au::kDisplayH == 480);
}

TEST(layout_nextturn_outside_cosmos) {
    REQUIRE_DATA();
    // The verified rects prove the HUD rail sits beside the map: no corner
    // of NEXTTURN is inside COSMOSWnd.
    CHECK(!au::inRect(au::kCosmosWnd, {au::kNextTurnBtn.x0, au::kNextTurnBtn.y0}));
    CHECK(au::inRect(au::kNextTurnBtn, {500, 60}));
    CHECK(!au::inRect(au::kNextTurnBtn, {500, 90}));  // y1=82 inclusive, 90 out
    CHECK(au::inRect(au::kNextTurnBtn, {au::kNextTurnBtn.x1, au::kNextTurnBtn.y1}));
}

TEST(layout_star_projection_within_bounds) {
    REQUIRE_DATA();
    au::CosmosView v;  // mapSize 1024 default (MapConfig default)
    ascend::game::Star s;
    s.x = 0; s.y = 0;
    CHECK(au::starScreenPos(v, s).x == au::kCosmosWnd.x0);
    CHECK(au::starScreenPos(v, s).y == au::kCosmosWnd.y0);
    s.x = 1023; s.y = 1023;
    auto q = au::starScreenPos(v, s);
    CHECK(q.x <= au::kCosmosWnd.x1);
    CHECK(q.y <= au::kCosmosWnd.y1);
    s.x = 512; s.y = 512;
    auto m = au::starScreenPos(v, s);
    CHECK(m.x > au::kCosmosWnd.x0 && m.x < au::kCosmosWnd.x1);
}

TEST(layout_palette_cvd_separable) {
    REQUIRE_DATA();
    // Rule (docs/re/ui-runtime.md §4), evaluated under BOTH the
    // deuteranopia and protanopia transforms, with gaps measured on the
    // SIMULATED colours: owner pair OK iff luminance gap >= 32 OR chroma
    // distance >= 90 with gap >= 12. Neutral is drawn at a smaller radius
    // (redundant size coding), so it passes on gap >= 28 OR chroma >= 90.
    auto sim = [](int t, au::RGB c) {
        au::RGB o;
        if (t == 0) au::simulateDeuteranopia(c, &o);
        else au::simulateProtanopia(c, &o);
        return o;
    };
    auto check_pair = [&](au::RGB x, au::RGB y, bool neutral) {
        for (int t = 0; t < 2; ++t) {
            au::RGB a = sim(t, x), b = sim(t, y);
            int dl = std::abs((int)au::luminance601(a) - (int)au::luminance601(b));
            int d = (int)std::sqrt((double)(a.r - b.r) * (a.r - b.r) +
                                   (double)(a.g - b.g) * (a.g - b.g) +
                                   (double)(a.b - b.b) * (a.b - b.b));
            if (neutral) CHECK(dl >= 28 || d >= 90);
            else CHECK(dl >= 32 || (d >= 90 && dl >= 12));
        }
    };
    for (int i = 0; i < 7; ++i) {
        for (int j = i + 1; j < 7; ++j)
            check_pair(au::kOwnerRgb[i], au::kOwnerRgb[j], false);
        check_pair(au::kNeutralRgb, au::kOwnerRgb[i], true);
    }
}

TEST(layout_hit_test_finds_nearest) {
    REQUIRE_DATA();
    // Synthetic 3-star galaxy directly (no generator needed).
    Galaxy g;
    for (int i = 0; i < 3; ++i) {
        ascend::game::Star s;
        s.id = i;
        s.x = 100 + i * 300;
        s.y = 500;  // bottom edge of map grid -> clamps near bounds
        g.stars.push_back(s);
    }
    au::CosmosView v;
    auto q = au::starScreenPos(v, g.stars[1]);
    CHECK(au::hitStar(v, g, q) == 1);
    CHECK(au::hitStar(v, g, {q.x + 2, q.y}) == 1);        // radius 6
    CHECK(au::hitStar(v, g, {q.x + 400, q.y + 400}) == -1);  // far away
}

TEST(layout_planet_gauge_selector_law_t199) {
    REQUIRE_DATA();
    // GAUGE COMPRESSION LAW (docs/re/planets-ui.md S3 [verified planwin
    // 0x3b96c switch cases; t198]): sel = clamp0..20(round(level^0.75)).
    // Round-to-nearest ties are IMPOSSIBLE (16*L^3 == odd^4 has no integer
    // solution — docs/re/_wip_t199.md S0), so this pins the x87 frndint
    // result exactly for every L.
    // Cited corpus anchors (planets-ui.md S3 measurement):
    CHECK(au::gaugeSelector(52) == 19);   // RES corpus max 52 reaches rec 19
    CHECK(au::gaugeSelector(53) == 20);   // "IND rec 20 from level >= 53"
    CHECK(au::gaugeSelector(77) == 20);   // IND corpus max 77 -> clamped
    CHECK(au::gaugeSelector(56) == 20);   // last level before unclamped 21
    CHECK(au::gaugeSelector(57) == 20);   // raw 21 clamps to 20
    CHECK(au::gaugeSelector(0) == 0);
    CHECK(au::gaugeSelector(-5) == 0);    // clamp0 side (word is u16; defensive)
    // The first-level table is anchored against the implementation itself
    // at every selector (kFirst monotone, boundary-exact both sides):
    for (int k = 1; k <= 20; ++k) {
        const int f = au::gaugeFirstLevelFor(k);
        CHECK(au::gaugeSelector(f) == k);
        CHECK(au::gaugeSelector(f - 1) == k - 1);
    }
    CHECK(au::gaugeFirstLevelFor(0) == 0);
    CHECK(au::gaugeFirstLevelFor(21) == -1);
    // Non-decreasing over the whole drawable+overflow range.
    for (int L = 1; L <= 300; ++L) CHECK(au::gaugeSelector(L) >= au::gaugeSelector(L - 1));
    // PROSPERITY identity law (case 2 @0x3cdcf): no pow, clamp only.
    // Corpus PROS max 16 NEVER saturates (planets-ui.md S3, 2900 records).
    for (int p = 0; p <= 16; ++p) CHECK(au::prosSelector(p) == p);
    CHECK(au::prosSelector(17) == 17);    // identity above the corpus range too
    CHECK(au::prosSelector(20) == 20);
    CHECK(au::prosSelector(21) == 20);
    CHECK(au::prosSelector(-1) == 0);
}

