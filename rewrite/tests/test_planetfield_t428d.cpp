// SPDX-License-Identifier: GPL-3.0-or-later

// t428d PLANET-FIELD STARFIELD pins (law docs/re/_wip_t428d.md F1/F3):
//   1. The paint-body blit-1 law: 17np record 4 (IMMEDIATE selector $0x4
//      at 0x3b9c6 — not the SENDMESSAGE gate value; t428 F4 correction)
//      at screen (7,115) (pushes $0x73=y, $0x7=x; push order calibrated
//      against the t428c measured registration of k4 at exactly (7,115)).
//   2. Library census: 17np conforms (9 records, rec 4 = 625x357); the
//      gauge libs (21 x 107x99) must NOT conform.
//   3. BYTE CENSUS on the DECODED record 4: mostly idx 0 (>=99%) with a
//      scattered speckle (lit px 200..400; vendor-measured 269,
//      scripts/t428c_field_register.py). This binds the SPECIFIC record:
//      rec 0 (639x479 frame) fails the speckle stats, rec 1 (9x9 sprite)
//      fails the dims.
#include <cstdio>
#include <string>
#include <vector>

#include "formats/shp.h"
#include "ui/planetstrip.h"
#include "harness.h"

namespace {
namespace au = ascend::ui;
namespace af = ascend::formats;
const std::string kRepo = ASCENDANCY_SOURCE_DIR;
const std::string kData = kRepo + "/extracted/ascend01/data/";
}  // namespace

TEST(planetfield_blit_law_t428d) {
    // The constants ARE the asm law (citations in planetstrip.h).
    CHECK(au::kFieldRecord == 4);
    CHECK(au::kFieldBlitOrigin.x == 7);
    CHECK(au::kFieldBlitOrigin.y == 115);
    // tA1 BBOX-DIFF LAW: k4 bbox (0,0,625,357) -> content 626x358.
    CHECK(au::kFieldRecordW == 626);
    CHECK(au::kFieldRecordH == 358);
    // The blit reaches the visible field: k4 at (7,115) spans y 115..471
    // (within the 480-row display) and x 7..631 — the t428c witness peak.
    CHECK(au::kFieldBlitOrigin.y + au::kFieldRecordH <= 480);
    CHECK(au::kFieldBlitOrigin.x + au::kFieldRecordW <= 640);
}

TEST(planetfield_library_census_t428d) {
    REQUIRE_DATA();
    std::string err;
    if (!au::fieldLibraryConforms(kData + "17np.shp", &err)) {
        std::printf("  field census 17np.shp: %s\n", err.c_str());
    }
    CHECK(au::fieldLibraryConforms(kData + "17np.shp", &err));
    // Controls: the gauge libs must NOT pass the field gate.
    for (int i = 0; i < 3; i++)
        CHECK(!au::fieldLibraryConforms(kData + au::kStripGaugeLibs[i], &err));
}

TEST(planetfield_record4_speckle_t428d) {
    REQUIRE_DATA();
    af::ShapeLibrary lib;
    std::string err;
    if (!lib.load(kData + "17np.shp", &err)) {
        std::printf("  load: %s\n", err.c_str());
    }
    CHECK(lib.count() == 9);
    if (lib.count() != 9) return;
    const auto& r = lib.record(au::kFieldRecord);
    CHECK(int(r.width) == au::kFieldRecordW &&
          int(r.height) == au::kFieldRecordH);
    std::vector<uint8_t> px;
    CHECK(lib.decode(au::kFieldRecord, px));
    CHECK(int(px.size()) == au::kFieldRecordW * au::kFieldRecordH);
    if (int(px.size()) != au::kFieldRecordW * au::kFieldRecordH) return;
    // Speckle stats: >=99% idx 0, lit px in [200,400] (vendor 269).
    long lit = 0;
    int minx = 1 << 30, maxx = -1, miny = 1 << 30, maxy = -1;
    for (int y = 0; y < int(r.height); y++)
        for (int x = 0; x < int(r.width); x++)
            if (px[size_t(y) * r.width + x]) {
                lit++;
                if (x < minx) minx = x;
                if (x > maxx) maxx = x;
                if (y < miny) miny = y;
                if (y > maxy) maxy = y;
            }
    std::printf("  rec4 speckle: lit=%ld bbox x%d..%d y%d..%d\n", lit, minx,
                maxx, miny, maxy);
    CHECK(lit >= 200 && lit <= 400);
    // Scattered (starfield), not a blob: the bbox covers most of the frame.
    CHECK(maxx - minx > au::kFieldRecordW / 2);
    CHECK(maxy - miny > au::kFieldRecordH / 2);
    // Control: rec 0 is the full-frame backdrop class — NOT a sparse
    // speckle (measured: 49558 lit px of 639x479 = 16.2%, vs rec4's 269).
    std::vector<uint8_t> p0;
    CHECK(lib.decode(0, p0));
    long lit0 = 0;
    for (size_t i = 0; i < p0.size(); i++)
        if (p0[i]) lit0++;
    CHECK(lit0 > 4000);  // frame class, not speckle (lit range [200,400])
}
