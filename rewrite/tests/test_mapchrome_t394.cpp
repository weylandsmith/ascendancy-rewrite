// SPDX-License-Identifier: GPL-3.0-or-later

// t394 galaxy-map sidebar chrome law pins. Law source: mapchrome.h
// (windows.txt state-1 records verbatim) + docs/re/_wip_t394.md (the
// pixel measurements on the user-supplied vendor original + the 1starmap
// dims census). The dims-parity test reads the REAL extracted/ascend01/
// data/1starmap.shp (read-only, gate-safe, REQUIRE_DATA).
#include "ui/mapchrome.h"

#include <string>

#include "formats/shp.h"
#include "harness.h"

#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif

namespace {
const std::string kA01 =
    std::string(ASCENDANCY_SOURCE_DIR) + "/extracted/ascend01/data/";
}  // namespace
using namespace ascend::ui;
using ascend::ui::inRect;
using ascend::ui::Pt;

TEST(mapchrome_t394_rail_table_verbatim) {
    // Spot-check the cluster table against windows.txt line cites
    // (full table = mapchrome.cpp).
    using ascend::ui::kMapCtl;
    CHECK(kMapCtl[0].rect.x0 == 495 && kMapCtl[0].rect.y0 == 364 &&
          kMapCtl[0].rect.x1 == 509 && kMapCtl[0].rect.y1 == 394 &&
          kMapCtl[0].shapeFrame == 8 && kMapCtl[0].sendMessage == 51);  // ROTRIGHT ln223
    CHECK(kMapCtl[1].rect.x0 == 479 && kMapCtl[1].shapeFrame == 9 &&
          kMapCtl[1].sendMessage == 50);                                // ROTLEFT ln240
    CHECK(kMapCtl[6].rect.x0 == 596 && kMapCtl[6].rect.x1 == 626 &&
          kMapCtl[6].shapeFrame == 14 && kMapCtl[6].sendMessage == 56); // CENTERHOLO ln325
    CHECK(kMapCtl[7].rect.y0 == 403 && kMapCtl[7].rect.y1 == 433 &&
          kMapCtl[7].shapeFrame == 15 && kMapCtl[7].sendMessage == 57); // TOGLANES ln342
    CHECK(kMapCtl[10].shapeFrame == 18 && kMapCtl[10].sendMessage == 61);  // TOGCOLONIES ln396
    // TURNCOUNT + NEXTTURN pair + RACECONTROLS frame (ln521/539/556/415)
    CHECK(kTurnCount.x0 == 474 && kTurnCount.y0 == 7 && kTurnCount.x1 == 632 &&
          kTurnCount.y1 == 43);
    CHECK(kNextTurnShape == 65 && kNextTurnContShape == 66);
    CHECK(kNextTurnCont.x0 == 557 && kNextTurnCont.y0 == 52 &&
          kNextTurnCont.x1 == 632 && kNextTurnCont.y1 == 82);
    CHECK(kRaceControlsFrame.x0 == 474 && kRaceControlsFrame.y0 == 442 &&
          kRaceControlsFrame.x1 == 632 && kRaceControlsFrame.y1 == 472 &&
          kRaceControlsShape == 19);
}

TEST(mapchrome_t394_race_slots_verbatim) {
    using ascend::ui::kRaceSlots;
    // RACE<N>CONTROL <bit> x0 449 x1 465, x0 = 479 + 22i (ln429-435)
    for (int i = 0; i < 7; i++) {
        CHECK(kRaceSlots[i].bit == (1 << i));
        CHECK(kRaceSlots[i].rect.x0 == 479 + 22 * i);
        CHECK(kRaceSlots[i].rect.x1 == kRaceSlots[i].rect.x0 + 16);
        CHECK(kRaceSlots[i].rect.y0 == 449 && kRaceSlots[i].rect.y1 == 465);
    }
    // Slot 1 == the MEASURED green square on the vendor original
    // (479,448-495,465 green component; _wip_t394.md S3).
    CHECK(ascend::ui::raceSlotFor(Pt{487, 457}).has_value() &&
          *ascend::ui::raceSlotFor(Pt{487, 457}) == 0);
    // Gaps between slots (pitch 22, width 17 inclusive) hit NOTHING.
    CHECK(!ascend::ui::raceSlotFor(Pt{498, 457}).has_value());
    CHECK(!ascend::ui::raceSlotFor(Pt{520, 457}).has_value());
}

TEST(mapchrome_t394_oval_slots_measured) {
    // MEASURED law (_wip_t394.md S3): five green oval components at x
    // 482/513/544/575/606 (pitch 31, ~19 wide), green rows y10..40, all
    // INSIDE TURNCOUNT 474,7-632,43.
    for (int i = 0; i < 5; i++) {
        CHECK(kOvalSlots[i].x0 == 482 + 31 * i);
        CHECK(kOvalSlots[i].x1 - kOvalSlots[i].x0 == 18);
        CHECK(kOvalSlots[i].y0 == 10 && kOvalSlots[i].y1 == 39);
        CHECK(inRect(kTurnCount, Pt{kOvalSlots[i].x0, kOvalSlots[i].y0}));
        CHECK(inRect(kTurnCount, Pt{kOvalSlots[i].x1, kOvalSlots[i].y1}));
    }
}

TEST(mapchrome_t394_shape_dims_parity_law) {
    REQUIRE_DATA();
    // THE DIMS LAW [verified t394 census over every SHAPEFRAME'd map
    // control]: rect (inclusive) == shape dims + 1 in BOTH axes — the
    // bevel margin. Pinned against the real 1starmap.shp for the cluster
    // (k8..k18), the NEXTTURN pair (k65/k66) and RACECONTROLS (k19).
    ascend::formats::ShapeLibrary lib;
    std::string err;
    CHECK(lib.load(kA01 + "1starmap.shp", &err));
    if (lib.count() == 0) return;
    auto parity = [&](int frame, const ascend::ui::Rect& r) {
        if (frame >= int(lib.count())) { CHECK(frame < int(lib.count())); return; }
        const auto& rec = lib.record(frame);
        // tA1 BBOX-DIFF LAW: content == the FULL inclusive rect (the old
        // minus-1 parity was the port mis-reading the R,B corner as dims).
        CHECK(int(rec.width) == r.x1 - r.x0 + 1);
        CHECK(int(rec.height) == r.y1 - r.y0 + 1);
    };
    for (int i = 0; i < ascend::ui::kMapCtlCount; i++)
        parity(kMapCtl[i].shapeFrame, kMapCtl[i].rect);
    parity(kNextTurnShape, ascend::ui::kNextTurnBtn);
    parity(kNextTurnContShape, kNextTurnCont);
    parity(kRaceControlsShape, kRaceControlsFrame);
}

TEST(mapchrome_t394_hit_laws) {
    using ascend::ui::mapCtlFor;
    // Shared-edge law: ROTUP y..379, ROTDOWN 380.. — inclusive edges,
    // distinct rows, no ambiguity.
    CHECK(mapCtlFor(Pt{530, 379}) == ascend::ui::MapCtl::RotUp);
    CHECK(mapCtlFor(Pt{530, 380}) == ascend::ui::MapCtl::RotDown);
    CHECK(mapCtlFor(Pt{610, 420}) == ascend::ui::MapCtl::TogColonies);
    // The gap column 466..473 and the map interior hit nothing.
    CHECK(!mapCtlFor(Pt{470, 420}).has_value());
    CHECK(!mapCtlFor(Pt{200, 200}).has_value());
    // Cluster + strip + panel rects all sit inside 640x480.
    auto fits = [](const ascend::ui::Rect& r) {
        return r.x0 >= 0 && r.y0 >= 0 && r.x1 <= 639 && r.y1 <= 479;
    };
    for (int i = 0; i < ascend::ui::kMapCtlCount; i++)
        CHECK(fits(kMapCtl[i].rect));
    CHECK(fits(kTurnCount));
    CHECK(fits(kNextTurnCont));
    CHECK(fits(kRaceControlsFrame));
}
