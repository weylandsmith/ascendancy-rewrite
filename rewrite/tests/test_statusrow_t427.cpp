// SPDX-License-Identifier: GPL-3.0-or-later

// t427 PLANETS-LIST ROW COMPOSITION pins (laws docs/re/_wip_t427.md
// F1-F6, disasm work/r331_disasm.txt fn 0x500e0 0x504d0..0x50647).
//   1. suns.shp is the ROW SUN lib (init 0x51954 resolves "DATA\\suns.shp",
//      string verbatim at file 0x856a7): 13 records == 13 starstat types,
//      selector = raw star type (blit #1 0x50525, selector = [esi+0] dword
//      with NO 4*K banding). All 13 records decode under the port's
//      canonical dims law (drawn content frames, NOT the 150x150 u16
//      header pair — F6: the u32 pair walk is the one that terminates).
//   2. planets.shp selector = 5*type + size (blit #2 0x50565..0x50581)
//      over the 55-record lib; the size ladder k0..k4 per group is the
//      cited content dims 11/18/25/35/47 (shp.md S23.3).
//   3. SELECTION LAW [measured t3 capture]: selected line1 WHITE
//      (255,255,255) x522px, unselected GREEN (0,170,82) x551/x375; the
//      t417b red capsule is REFUTED (rows 1/2 red px below x185 = ZERO).
//   4. POP PIP GRID geometry [measured]: 10 cols x 4 rows pitch 5 at
//      x498, row-rel y+50; capacity 40, nothing beyond.
//   5. 2x SCALE law: drawn sun 130x126 vs content 61..68 (F5); anchors
//      kStatusSunCx/Cy, kStatusPlanetCx/Cy, flag (12, row+0).
#include "ui/statuslist.h"
#include "formats/shp.h"

#include <string>

#include "harness.h"

namespace {
namespace au = ascend::ui;
namespace af = ascend::formats;
const std::string kRepo = ASCENDANCY_SOURCE_DIR;
const std::string kData = kRepo + "/extracted/ascend01/data/";
}  // namespace

TEST(statusrow_suns_lib_identity_t427) {
    REQUIRE_DATA();
    af::ShapeLibrary suns;
    std::string err;
    CHECK(suns.load(kData + "suns.shp", &err));
    // 13 records == the 13 starstat.txt types (mapgen.md S1); the vendor
    // selector is the RAW star-type dword (no 4*K+cls banding like the map
    // pips), so the domain must cover every type index 0..12.
    CHECK(suns.count() == 13);
    for (int k = 0; k < 13; k++) {
        std::vector<uint8_t> px;
        CHECK(suns.decode(k, px));
        // content frames are SMALL (the drawn 130px sun is the 2x law);
        // a 150x150 read would mean the u16 header pair leaked in.
        CHECK(suns.record(k).width <= 140);   // tA1 bbox ladder 76..139
        CHECK(suns.record(k).height <= 142);
    }
    // tA1: k0 bbox (-65,-64,61,68) -> 127x133 content.
    CHECK(suns.record(0).width == 127 && suns.record(0).height == 133);
}

TEST(statusrow_planet_selector_domain_t427) {
    REQUIRE_DATA();
    af::ShapeLibrary pl;
    std::string err;
    CHECK(pl.load(kData + "planets.shp", &err));
    CHECK(pl.count() == 55);
    // selector = 5*type + size; the size axis is the cited content ladder
    // 11/18/25/35/47 (shp.md S23.3) within EVERY type group.
    // tA1 bbox ladder {24,38,52,71,95} (was 11/18/25/35/47 under the
    // R,B-corner misparse; the drawn-size witnesses match bbox 1:1).
    CHECK(pl.record(0).width == 24);
    CHECK(pl.record(4).width == 95);
    CHECK(pl.record(5).width == 24);   // next group restarts the ladder
    std::vector<uint8_t> px;
    CHECK(pl.decode(4 * 5 + 4, px));
}

TEST(statusrow_selection_law_t427) {
    // Measured on the t3 capture (row 0 selected / rows 1,2 not):
    // line1 WHITE vs GREEN; NO marker rect (capsule refuted).
    CHECK(au::kStatusLine1Sel.r == 255 && au::kStatusLine1Sel.g == 255 &&
          au::kStatusLine1Sel.b == 255);
    CHECK(au::kStatusLine1Norm.r == 0 && au::kStatusLine1Norm.g == 170 &&
          au::kStatusLine1Norm.b == 82);
    // The two must be DISTINCT — the colour IS the selection marker.
    CHECK(!(au::kStatusLine1Sel.r == au::kStatusLine1Norm.r &&
            au::kStatusLine1Sel.g == au::kStatusLine1Norm.g));
}

TEST(statusrow_pip_grid_t427) {
    int x = -1, y = -1;
    CHECK(au::statusPipAt(0, 57, x, y));
    CHECK(x == 498 && y == 107);  // measured first dot (y107 row band)
    CHECK(au::statusPipAt(9, 57, x, y));
    CHECK(x == 543 && y == 107);  // 10 cols, pitch 5 (498..543)
    CHECK(au::statusPipAt(10, 57, x, y));
    CHECK(x == 498 && y == 112);  // row 1 of the grid
    CHECK(au::statusPipAt(39, 57, x, y));
    CHECK(x == 543 && y == 122);  // 4 rows: bands 107/112/117/122
    CHECK(!au::statusPipAt(40, 57, x, y));  // capacity 40
    CHECK(!au::statusPipAt(-1, 57, x, y));
}

TEST(statusrow_selector_laws_t427b) {
    // BLIT #1: raw star type, domain 0..12 (13 starstat types), else -1.
    CHECK(au::statusSunSelector(0) == 0);
    CHECK(au::statusSunSelector(12) == 12);
    CHECK(au::statusSunSelector(13) == -1);
    CHECK(au::statusSunSelector(-1) == -1);
    // BLIT #2: 5*type + size (0x50567..0x50581 imul 5 / add), NOT
    // 5*size + type and NOT 4*K banding: asymmetric args pin the form.
    CHECK(au::statusPlanetSelector(4, 3) == 23);
    CHECK(au::statusPlanetSelector(3, 4) == 19);
    CHECK(au::statusPlanetSelector(0, 0) == 0);
    CHECK(au::statusPlanetSelector(10, 4) == 54);   // last record
    CHECK(au::statusPlanetSelector(11, 0) == -1);   // 11 type words max
    CHECK(au::statusPlanetSelector(0, 5) == -1);    // 5 size words max
    CHECK(au::statusPlanetSelector(-1, 0) == -1);
}

TEST(statusrow_scale_and_anchors_t427) {
    // tA1 BBOX-DIFF LAW: content dims == drawn size (k1 130x127 vs
    // measured 130x126); the old 2x compensated the port misparse.
    CHECK(au::kStatusArtScale == 1);
    // Drawn centres measured on the t3 capture (warm-px bbox x16..145
    // y59..184 row 0 -> centre (80,64)+; blue sphere x174..245 y66..155).
    CHECK(au::kStatusSunCx == 80);
    CHECK(au::kStatusSunCy == 64);
    CHECK(au::kStatusPlanetCx == 215);
    CHECK(au::kStatusPlanetCy == 53);
    // Flag top-left (vendor blit row-local (10,4); measured green bbox
    // x12..26 y57..81 == 14x24 record at (12, row+0)).
    CHECK(au::kStatusFlagX == 12);
    CHECK(au::kStatusFlagY == 0);
    // Row geometry stays the t417b measurement (the row painter composes
    // INSIDE it).
    CHECK(au::kStatusRowsTop == 57);
    CHECK(au::kStatusRowPitch == 141);
}
