// SPDX-License-Identifier: GPL-3.0-or-later

// t417b STATUS BACKGROUND LAW pins (D15 root cause CLOSED t417; laws
// docs/re/_wip_t417.md F1-F7 + t417b re-verify F8).
//   1. The status screen paints NO shape backdrop (screenPaintsShapeBackdrop
//      declines kScreenStatus; TYPE-100 census F6 binds no lib to state 10;
//      k0 registers 4.5% exact on the t3 live capture F1). 17np k0 (state 17)
//      still passes the size test unchanged.
//   2. Geometry REPLACED: kStatusRowsTop 57, kStatusRowPitch 141 (F3 flag
//      bands 57/198/339 + autocorrelation peak 0.634); 3 rows land EXACTLY
//      on the screen bottom (57 + 3*141 == 480).
//   3. Header speckle census (F5): weights reproduce the measured shares and
//      statusSpeckleAt is deterministic + inside the census set.
//   4. Divider ramp (F5/F8): verbatim per-row table y38..46 ending solid
//      (33,56,57); nothing outside 38..46.
//   5. Marker law (F5/F8): red capsule x16..69, row-rel y2..25.
// No vendor data is read: no REQUIRE_DATA() needed (t403 guard census).
#include "ui/statusbg.h"
#include "ui/statuslaw.h"
#include "ui/statuslist.h"

#include "harness.h"

namespace {
namespace au = ascend::ui;
}  // namespace

TEST(statusbg_declines_10status_t417b) {
    // The D15 defect was the full-frame 10status k0 blit; the pure law now
    // declines it. Other screens keep the ui.cpp size test.
    CHECK(!au::screenPaintsShapeBackdrop(au::kScreenStatus));
    CHECK(au::screenPaintsShapeBackdrop(au::kScreenPlanet));
    CHECK(au::screenPaintsShapeBackdrop(au::kScreenSystemView));
    CHECK(au::screenPaintsShapeBackdrop(au::kScreenMap));
    // The naming law still maps state 10 -> 10status.shp (faces/rail icons
    // may still come from the lib; only the BACKDROP role is declined).
    CHECK(std::string(au::screenShapeLib(au::kScreenStatus)) == "10status.shp");
}

TEST(statusbg_geometry_f3_t417b) {
    // F3 [measured]: rows top 57, pitch EXACTLY 141, three rows land exactly
    // on the 480-px screen bottom.
    CHECK(au::kStatusRowsTop == 57);
    CHECK(au::kStatusRowPitch == 141);
    CHECK(au::kStatusVisibleRows == 3);
    CHECK(au::kStatusRowsTop + au::kStatusVisibleRows * au::kStatusRowPitch == 480);
    // The vendor divider is solid at y46 (F5): row 0 starts below it, and a
    // click in the black strip y47..56 hits no row.
    CHECK(au::kStatusRowsTop > 46);
    CHECK(!au::statusRowAt(au::Pt{300, 56}, au::kStatusRowsTop));
    CHECK(au::statusRowAt(au::Pt{300, 57}, au::kStatusRowsTop).value_or(-9) == 0);
    // Row bands: 0 = 57..197, 1 = 198..338, 2 = 339..479 (flag-icon bands
    // 57/198/339 sit AT the tops, F3).
    CHECK(au::statusRowAt(au::Pt{300, 197}, au::kStatusRowsTop).value_or(-9) == 0);
    CHECK(au::statusRowAt(au::Pt{300, 198}, au::kStatusRowsTop).value_or(-9) == 1);
    CHECK(au::statusRowAt(au::Pt{300, 339}, au::kStatusRowsTop).value_or(-9) == 2);
    CHECK(!au::statusRowAt(au::Pt{300, 480}, au::kStatusRowsTop));
    // Hit-map integration: row-zone click at row 2 top resolves Row/2; the
    // arrow boxes keep their t405 rects (x619..638 — outside the row zone).
    const auto h = au::statusHitFor(au::Pt{300, 340}, au::kStatusRowsTop);
    CHECK(h.kind == au::StatusHit::Row && h.row == 2);
    CHECK(au::statusHitFor(au::Pt{628, 60}, au::kStatusRowsTop).kind ==
          au::StatusHit::ArrowUp);
}

TEST(statusbg_speckle_census_t417b) {
    // F5 rect + census set. Weights reproduce the measured ordering: black
    // and (8,12,16) dominate, the two .006/.011 teals are rare.
    CHECK(au::kStatusSpeckleRect.x0 == 8 && au::kStatusSpeckleRect.y0 == 8);
    CHECK(au::kStatusSpeckleRect.x1 == 630 && au::kStatusSpeckleRect.y1 == 36);
    CHECK(au::kSpeckleWeights[0] == 37 && au::kSpeckleWeights[1] == 35);
    // The weights MUST sum to the modulus (98) — a larger sum starves the
    // rare entries (t417b census CAUGHT this on the first draft).
    {
        int sum = 0;
        for (int i = 0; i < au::kSpeckleCount; i++) sum += au::kSpeckleWeights[i];
        CHECK(sum == 98);
    }
    // Deterministic + inside the census set over the whole header band;
    // the two dominant colours together take a clear majority (>60% of the
    // 98-weight law says 87/98 = .888; the margin guards hash skew).
    int counts[8] = {0, 0, 0, 0, 0, 0, 0, 0};  // [6]=other, [7]=dominant pair
    for (int y = 8; y <= 36; y += 1)
        for (int x = 8; x <= 630; x += 2) {
            const au::RGB c = au::statusSpeckleAt(x, y);
            CHECK(au::statusSpeckleAt(x, y).r == c.r);  // pure function
            int idx = -1;
            for (int i = 0; i < au::kSpeckleCount; i++)
                if (c.r == au::kSpeckleColours[i].r &&
                    c.g == au::kSpeckleColours[i].g &&
                    c.b == au::kSpeckleColours[i].b)
                    idx = i;
            CHECK(idx >= 0);  // never outside the measured set
            if (idx >= 0) counts[idx]++;
            if (idx == 0 || idx == 1) counts[7]++;
        }
    const int total = (36 - 8 + 1) * ((630 - 8) / 2 + 1);
    CHECK(counts[7] * 100 > total * 60);
    // The rare teals stay rare (< 10% combined) AND the .062 teal actually
    // FIRES (a modulus/weight mismatch starves indices 3..5 — the t417b
    // witness census caught exactly this on the first draft, n=0).
    CHECK((counts[4] + counts[5]) * 100 < total * 10);
    CHECK(counts[3] > 0);
}

TEST(statusbg_ramp_table_t417b) {
    // F5/F8 verbatim rows: y38 (74,113,115); y39/40 pale (123,182,181);
    // y41 (115,117,115); y42 (66,105,107); y43/44 (24,48,41); y45
    // (24,28,24); y46 SOLID (33,56,57). Nothing outside 38..46.
    au::RGB c{1, 2, 3};
    CHECK(au::statusRampColourAt(38, &c) && c.r == 74 && c.g == 113 && c.b == 115);
    CHECK(au::statusRampColourAt(39, &c) && c.r == 123 && c.g == 182 && c.b == 181);
    CHECK(au::statusRampColourAt(40, &c) && c.r == 123 && c.g == 182 && c.b == 181);
    CHECK(au::statusRampColourAt(41, &c) && c.r == 115 && c.g == 117 && c.b == 115);
    CHECK(au::statusRampColourAt(42, &c) && c.r == 66 && c.g == 105 && c.b == 107);
    CHECK(au::statusRampColourAt(43, &c) && c.r == 24 && c.g == 48 && c.b == 41);
    CHECK(au::statusRampColourAt(44, &c) && c.r == 24 && c.g == 48 && c.b == 41);
    CHECK(au::statusRampColourAt(45, &c) && c.r == 24 && c.g == 28 && c.b == 24);
    CHECK(au::statusRampColourAt(46, &c) && c.r == 33 && c.g == 56 && c.b == 57);
    CHECK(!au::statusRampColourAt(37, &c));
    CHECK(!au::statusRampColourAt(47, &c));
    // The left border shares the y46 solid colour (F4: x7 (33,56,57)
    // 423/423 px over y48..470).
    CHECK(au::kStatusBorderRgb.r == 33 && au::kStatusBorderRgb.g == 56 &&
          au::kStatusBorderRgb.b == 57);
    CHECK(au::kStatusBorderX == 7);
    CHECK(au::kStatusBorderY0 == 48 && au::kStatusBorderY1 == 470);
}

TEST(statusbg_marker_and_wells_t417b) {
    // F5/F8: RED marker capsule x16..69, row-rel y2..25 (top+2, h~24).
    CHECK(au::kStatusMarkerRect.x0 == 16 && au::kStatusMarkerRect.x1 == 69);
    CHECK(au::kStatusMarkerRect.y0 == 2);
    CHECK(au::kStatusMarkerRect.y1 - au::kStatusMarkerRect.y0 + 1 >= 20 &&
          au::kStatusMarkerRect.y1 - au::kStatusMarkerRect.y0 + 1 <= 26);
    // The marker sits INSIDE the row band (row 2: 339+2..339+25 < 339+141).
    CHECK(au::kStatusMarkerRect.y1 < au::kStatusRowPitch);
    // Arrow-well navy is the MEASURED (8,32,49) — explicitly NOT the k0
    // idx-242 navy (12,32,48) that fingerprinted the never-painted backdrop.
    CHECK(au::kStatusWellNavy.r == 8 && au::kStatusWellNavy.g == 32 &&
          au::kStatusWellNavy.b == 49);
}

TEST(statusbg_perimeter_bands_t417b) {
    // F2/F4: four ~7 px edge bands covering the full perimeter.
    CHECK(au::kStatusTextureBandCount == 4);
    const au::Rect* b = au::kStatusTextureBands;
    CHECK(b[0].x0 == 0 && b[0].y0 == 0 && b[0].x1 == 639 && b[0].y1 == 6);
    CHECK(b[1].x0 == 0 && b[1].y0 == 472 && b[1].x1 == 639 && b[1].y1 == 479);
    CHECK(b[2].x0 == 0 && b[2].y0 == 0 && b[2].x1 == 6 && b[2].y1 == 479);
    CHECK(b[3].x0 == 633 && b[3].y0 == 0 && b[3].x1 == 639 && b[3].y1 == 479);
    // The LEFT/RIGHT bands never encroach on the interior (x7 is the border
    // line, x8+ the speckle/rows): left band ends at x6, right band starts
    // at x633 (F4: right border x630 pale segment + x633 texture).
    CHECK(b[2].x1 == 6);
    CHECK(b[3].x0 == 633);
    // Top band ends at y6, bottom band starts at y472 (speckle starts y8).
    CHECK(b[0].y1 == 6);
    CHECK(b[1].y0 == 472);
}
