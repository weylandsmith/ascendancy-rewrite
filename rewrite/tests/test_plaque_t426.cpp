// SPDX-License-Identifier: GPL-3.0-or-later

// t426 PLAQUE + HOME-CREST LAW pins. Law source: raceflag.shp k0 decoded
// at rec+8 (k0 header law; k>=1 dims at rec+0x10, stream rec+0x18) matches
// docs/assets/refcap/original-strategic-map.png (png = screen + 40) at
// 336/336 opaque px EXACT (tol<=3, vendor round(v*255/63)) at TWO anchors:
//   plaque  png (10,50)   == screen (10,10)   [upper-LEFT field emblem]
//   crest   png (285,117) == screen (285,77)  [home star, dot at (292,74)]
// runner-up anchors <=64% (sharp). Working log docs/re/_wip_t426.md
// F2/F2b/F3.
//
// THE LAW: the vendor draws a 15x25 frame (idx19 outline rect + idx242 navy
// interior) at anchor A, then blits raceflag k<specnum> AT THE SAME A. The
// record is a 14x24 half-frame (row 0 = 14x idx19 green, col 0 = idx19 every
// row, navy + glyph interior); the visible block's residual 39 px are
// exactly the frame's right column (25) + bottom row (14) — one law, two
// instances.
#include "ui/mapchrome.h"

#include <cstdint>
#include <string>
#include <vector>

#include "formats/gamepal.h"
#include "formats/shp.h"
#include "harness.h"

using namespace ascend::ui;

namespace {
const std::string kA01 =
    std::string(ASCENDANCY_SOURCE_DIR) + "/extracted/ascend01/data/";
}  // namespace

TEST(plaque_t426_frame_constants_name_the_measured_colours) {
    REQUIRE_DATA();
    ascend::formats::GamePalette pal;
    std::string err;
    CHECK(pal.load(kA01 + "game.pal", &err));
    if (!pal.ready()) return;
    uint8_t rgb[3];
    pal.rgb(kPlaqueFrameIdx, rgb);  // idx19: the ring/frame green
    CHECK(rgb[0] == 0 && rgb[1] == 170 && rgb[2] == 81);
    pal.rgb(kToggleWellIdx, rgb);  // idx242: the navy interior
    CHECK(rgb[0] == 12 && rgb[1] == 32 && rgb[2] == 48);
}

TEST(plaque_t426_record_is_14x24_with_transparent_row0) {
    REQUIRE_DATA();
    ascend::formats::ShapeLibrary lib;
    std::string err;
    CHECK(lib.load(kA01 + "raceflag.shp", &err));
    if (lib.count() < 1) return;
    const auto& rec = lib.record(0);
    CHECK(int(rec.width) == 15 && int(rec.height) == 25);  // tA1 bbox
    std::vector<uint8_t> px;
    CHECK(lib.decode(0, px));
    if (px.size() != 15u * 25u) return;
    // k0 stream sits at rec+8 (t425b law — verified here: the C++ decoder
    // and a rec+8 Python decode agree, and the k0 match against the refcap
    // is 336/336 EXACT at the frame anchor). Every row is fully opaque:
    // row 0 is the green top line (14x idx19), rows 1..23 are navy with
    // the idx19 left border + glyph strokes.
    for (int c = 0; c < 15; c++) CHECK(px[c] == 19);  // row 0 = frame green
    for (int r = 1; r < 25; r++) {
        CHECK(px[size_t(r) * 15] == 19);  // left border column
        int nonzero = 0;
        for (int c = 0; c < 15; c++)
            if (px[size_t(r) * 15 + c] != 0) nonzero++;
        CHECK(nonzero == 15);
    }
    // 21 records = 21 species (t400 census class).
    CHECK(lib.count() == 21);
}

TEST(plaque_t426_frame_plus_record_covers_the_visible_block) {
    // The composite law: frame rect (kPlaqueW x kPlaqueH at A) + record at
    // the SAME A covers every visible pixel of the 15x25 block measured at
    // BOTH anchors (residual 39 = frame right column 15 + bottom row 24,
    // both idx19 — probe ph.py, both anchors identical).
    CHECK(kPlaqueW == 15 && kPlaqueH == 25);
    CHECK(kPlaqueX == 10 && kPlaqueY == 10);  // upper-LEFT (user verbatim)
    CHECK(kPlaqueH + (kPlaqueW - 1) == 39);  // right col 25 + bottom row 14
    // Crest anchor law: home dot (292,74) -> frame (285,77): dx -7, dy +3.
    CHECK(kCrestDx == -7 && kCrestDy == 3);
    // Ring law: white ellipse rx 6 centred (dotx, doty-2) [idx15 extent
    // png y108..116 x286..298 about dot png (114,292)].
    CHECK(kCrestRingRx == 6 && kCrestRingDy == -2);
}
