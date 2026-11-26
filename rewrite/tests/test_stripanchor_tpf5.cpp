// SPDX-License-Identifier: GPL-3.0-or-later

// tPF-5 (D28 item 10) STRIP-ART ANCHOR pins.
//
// LAW [verified raw bytes work/ascend_restored.bin, FUN_0005caac prologue
// 0x5caac..0x5cb90]:
//   0x5cb5b  esi = payload + [payload + 8 + 8*sel]        (record entry)
//   0x5cb61  dest_x = [esi+0x8]  + [ebp+0x14]             (L ADDED)
//   0x5cb6a  dest_y = [esi+0xc]  + [ebp+0x18]             (T ADDED)
//   0x5cb73  right  = [esi+0x10] + [ebp+0x14]
//   0x5cb7c  bottom = [esi+0x14] + [ebp+0x18]
//   0x5cb85  stream = entry + 0x18
// so the caller's x/y is an ANCHOR, not a top-left: the blit adds the record's
// signed bbox corner. The port's strip call site (ui.cpp) therefore routes the
// rect origin through ui::stripGaugeBlitPos(), which adds (L,T) — the pins
// below call THAT function, so mutating it breaks them.
//
// DATA [measured scripts/tPF5_strip_bbox.py over the extracted libs]:
//   planres/planpro  all 21 records bbox (0,0,107,99) -> 108x100 full-bleed
//   planind          bbox (0,T,107,99), T in {23,20,11,5,1} by gauge level
//                    -> H in {77,80,89,95,99}; bottom-right pinned.
// The reported bug (D28 item 10: "too high in the frame, with the top cut off
// ... on the bottom there is either an empty black band") is exactly painting
// at rect.y0 instead of rect.y0 + T.
#include <cstdio>
#include <fstream>
#include <sstream>
#include <string>

#include "formats/shp.h"
#include "ui/layout.h"
#include "ui/planetstrip.h"
#include "harness.h"

namespace {
namespace au = ascend::ui;
namespace af = ascend::formats;
const std::string kData =
    std::string(ASCENDANCY_SOURCE_DIR) + "/extracted/ascend01/data/";

// windows.txt TYPE-29 rects, verbatim (X0,Y0,X1,Y1).
struct WRect {
    const char* name;
    const char* lib;
    int x0, y0, x1, y1;
};
const WRect kRects[3] = {{"PLRES", "planres.shp", 7, 7, 114, 106},
                         {"PLIND", "planind.shp", 123, 7, 230, 106},
                         {"PLPRO", "planpro.shp", 239, 7, 346, 106}};

bool loadLib(const std::string& file, af::ShapeLibrary& lib) {
    std::string e;
    return lib.load(kData + file, &e);
}

// Shipped law + the record's own anchor, exactly as ui.cpp composes them.
au::Pt shippedPos(const af::ShapeLibrary& lib, int rec, const WRect& w) {
    const auto& r = lib.record(rec);
    au::Rect rect{w.x0, w.y0, w.x1, w.y1};
    return au::stripGaugeBlitPos(rect, r.left, r.top);
}
}  // namespace

// 1. planind is the ONLY gauge lib with a non-zero anchor, and its T ladder is
//    the measured one. planres/planpro must stay (0,0) — if a data swap ever
//    anchored them, the port's no-op assumption would silently change.
TEST(stripanchor_tpf5_planind_is_the_anchored_lib) {
    REQUIRE_DATA();
    af::ShapeLibrary res, ind, pro;
    CHECK(loadLib("planres.shp", res) && loadLib("planind.shp", ind) &&
          loadLib("planpro.shp", pro));
    CHECK(res.count() == 21 && ind.count() == 21 && pro.count() == 21);

    for (int k = 0; k < 21; k++) {
        CHECK(res.record(k).left == 0 && res.record(k).top == 0);
        CHECK(res.record(k).width == 108 && res.record(k).height == 100);
        CHECK(pro.record(k).left == 0 && pro.record(k).top == 0);
        CHECK(pro.record(k).width == 108 && pro.record(k).height == 100);
    }

    // planind: L always 0, T from the measured ladder, H == 100 - T.
    static const int kT[21] = {23, 23, 20, 20, 20, 20, 11, 11, 5, 5, 5,
                               5,  5,  1,  1,  1,  1,  1,  1,  1,  1};
    int ladderViolations = 0, heightViolations = 0, lViolations = 0;
    for (int k = 0; k < 21; k++) {
        const auto& r = ind.record(k);
        if (r.left != 0) lViolations++;
        if (r.top != kT[k]) ladderViolations++;
        if (int(r.width) != 108 || int(r.height) != 100 - kT[k])
            heightViolations++;
    }
    CHECK(lViolations == 0);
    CHECK(ladderViolations == 0);
    CHECK(heightViolations == 0);
    // Anti-vacuity: the ladder must be non-trivial.
    CHECK(ind.record(0).top == 23 && ind.record(20).top == 1);
}

// 2. BOTTOM-RIGHT PINNING via the SHIPPED function: for every record of every
//    gauge lib, anchored placement lands the content's bottom-right exactly on
//    the windows.txt rect's bottom-right corner.
TEST(stripanchor_tpf5_bottom_right_pinning) {
    REQUIRE_DATA();
    for (const auto& w : kRects) {
        af::ShapeLibrary lib;
        CHECK(loadLib(w.lib, lib));
        int mismatches = 0;
        for (int k = 0; k < lib.count(); k++) {
            const au::Pt p = shippedPos(lib, k, w);
            const auto& r = lib.record(k);
            if (p.x + int(r.width) - 1 != w.x1) mismatches++;
            if (p.y + int(r.height) - 1 != w.y1) mismatches++;
        }
        CHECK(mismatches == 0);
    }
}

// 3. ANTI-VACUITY + SYMPTOM CITATION through the SHIPPED function: at PLIND,
//    the shipped y differs from the old (anchorless) y by exactly T on all 21
//    records, and the old law is the one leaving a band below the art.
TEST(stripanchor_tpf5_dropped_anchor_is_the_bug) {
    REQUIRE_DATA();
    af::ShapeLibrary ind;
    CHECK(loadLib("planind.shp", ind));
    const WRect w = kRects[1];  // PLIND 123,7..230,106
    const int rectH = w.y1 - w.y0 + 1;
    int differ = 0;
    for (int k = 0; k < 21; k++) {
        const auto& r = ind.record(k);
        const au::Pt p = shippedPos(ind, k, w);
        const int oldY = w.y0;
        CHECK(p.x == w.x0);  // L == 0 everywhere: no horizontal shift
        if (p.y != oldY) differ++;
        CHECK(p.y == w.y0 + int(r.top));
        // OLD law painted [y0, y0+H): rectH-H rows of the panel left exposed
        // below the art == exactly the dropped T.
        CHECK(rectH - int(r.height) == int(r.top));
        // NEW law: nothing exposed below.
        CHECK(w.y1 - (p.y + int(r.height) - 1) == 0);
    }
    CHECK(differ == 21);  // every industry gauge moved
}

// 4. WIRING (tngs_s29_title_wiring_is_unnegated precedent): the shipped strip
// call site must route the rect origin through stripGaugeBlitPos() and must
// NOT blit at the bare rect origin. Without this, the law above could be
// correct while ui.cpp silently reverts to the anchorless call.
TEST(stripanchor_tpf5_ui_call_site_is_wired) {
    std::ifstream in(std::string(ASCENDANCY_SOURCE_DIR) +
                     "/rewrite/src/ui/ui.cpp");
    const std::string src = [&] {
        std::stringstream ss;
        ss << in.rdbuf();
        return ss.str();
    }();
    CHECK(!src.empty());
    // The anchor call is present exactly once in the strip block...
    CHECK(src.find("stripGaugeBlitPos(gr.rect, grr.left,") != std::string::npos);
    // ...and the gauge blit consumes its result, not the raw rect origin.
    CHECK(src.find("blitShape(ren, gl, gr.rec, gp.x, gp.y);") !=
          std::string::npos);
    // The anchorless shape from before tPF-5 must be GONE.
    CHECK(src.find("blitShape(ren, gl, sp.gauges[gi].rec,") ==
          std::string::npos);
}

// 5. The conformance gate accepts planind's VARYING heights and still rejects
//    a wrong record count (so the fix cannot later be "corrected" into a
//    fabricated uniform-dims law).
TEST(stripanchor_tpf5_gate_accepts_varying_heights) {
    REQUIRE_DATA();
    std::string err;
    CHECK(au::stripGaugeLibraryConforms(kData + "planind.shp", &err));
    CHECK(au::stripGaugeLibraryConforms(kData + "planres.shp", &err));
    CHECK(au::stripGaugeLibraryConforms(kData + "planpro.shp", &err));
    err.clear();
    CHECK(!au::stripGaugeLibraryConforms(kData + "17np.shp", &err));
    CHECK(err.find("21") != std::string::npos);
}
