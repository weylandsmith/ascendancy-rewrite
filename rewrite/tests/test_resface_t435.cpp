// SPDX-License-Identifier: GPL-3.0-or-later

// t435 RESEARCH PAN-FACE LAW pins (docs/re/_wip_t435.md F5).
// LAW: windows.txt (extracted/ascend00/windows.txt ln1778-1792 + siblings)
// binds STATE-20's four pan children to DATA\20RES.SHP (TYPE-100 L1755-1758)
// with SHAPEFRAME 0..3; SHAPEFRAME n selects 20res.shp RECORD n and the
// child rect equals the record dims EXACTLY:
//   RESROTLEFT  524,442-539,472 (15x30) k0 | RESROTRIGHT 540..554 (14x30) k1
//   RESMOVEUP   563,442-593,457 (30x15) k2 | RESMOVEDOWN 563,458-593,472
//   (30x14) k3.  Records decoded this session via the rewrite's own decoder
//   (tools/shp_pngdump): k0 LEFT arrow, k1 RIGHT arrow, k2/k3 vertical pair;
//   face background index (12,32,48) == the port's panel fill, dominant.
//   k4/k5 exist (30x15/30x14) but NO windows.txt record consumes them — the
//   t408 F6 "third arrow pair" candidate; NOT blitted (no citation).
#include "ui/researchview.h"
#include "formats/gamepal.h"
#include "formats/shp.h"
#include "harness.h"

namespace {
namespace au = ascend::ui;
const std::string kA01 =
    std::string(ASCENDANCY_SOURCE_DIR) + "/extracted/ascend01/data/";

TEST(research_pan_faces_are_20res_records_0_to_3_t435) {
    REQUIRE_DATA();
    ascend::formats::ShapeLibrary lib;
    std::string err;
    CHECK(lib.load(kA01 + "20res.shp", &err));
    CHECK(lib.count() >= 6);
    if (lib.count() < 6) return;
    struct { const au::Rect* r; int frame; } cases[] = {
        {&au::kResRotLeft, 0}, {&au::kResRotRight, 1},
        {&au::kResMoveUp, 2},  {&au::kResMoveDown, 3},
    };
    for (const auto& c : cases) {
        const auto& rec = lib.record(c.frame);
        // windows.txt child rects are HALF-OPEN on the far edge for these
        // children [measured]: 539-524=15 == k0.w, 554-540=14 == k1.w,
        // 593-563=30 == k2.w, 472-458=14 == k3.w (the +1-inclusive reading
        // fails all four; the vendor blit uses the record dims regardless).
        CHECK(int(rec.width) == c.r->x1 - c.r->x0);
        CHECK(int(rec.height) == c.r->y1 - c.r->y0);
        std::vector<uint8_t> px;
        CHECK(lib.decode(c.frame, px));
        CHECK(px.size() == size_t(rec.width) * rec.height);
    }
}

TEST(research_pan_face_background_is_the_panel_fill_t435) {
    REQUIRE_DATA();
    ascend::formats::ShapeLibrary lib;
    ascend::formats::GamePalette pal;
    std::string err;
    CHECK(lib.load(kA01 + "20res.shp", &err));
    CHECK(pal.load(kA01 + "game.pal", &err));
    if (lib.count() < 6 || !pal.ready()) return;
    // The dominant record index must be the navy panel fill (12,32,48) the
    // port already uses as its fallback box colour, so blit and fallback
    // chrome agree.
    int bgIdx = -1;
    uint8_t rgb[3];
    for (int i = 0; i < 256 && bgIdx < 0; i++) {
        pal.rgb(i, rgb);
        if (rgb[0] == 12 && rgb[1] == 32 && rgb[2] == 48) bgIdx = i;
    }
    CHECK(bgIdx >= 0);
    if (bgIdx < 0) return;
    for (int f = 0; f < 4; f++) {
        std::vector<uint8_t> px;
        if (!lib.decode(f, px)) continue;
        int bg = 0;
        for (uint8_t v : px) bg += (v == uint8_t(bgIdx));
        int best = 0;
        int hist[256] = {};
        for (uint8_t v : px) hist[v]++;
        for (int h : hist) best = h > best ? h : best;
        // The fill is the PLURALITY colour (measured 220..243 of 420..450 —
        // just under half, the glyph + bevel take the rest) and never less
        // than a quarter of the face.
        CHECK(bg == best);
        CHECK(bg * 4 > int(px.size()));
    }
}
}  // namespace
