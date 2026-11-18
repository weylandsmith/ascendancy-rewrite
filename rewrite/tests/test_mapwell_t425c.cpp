// SPDX-License-Identifier: GPL-3.0-or-later

// t425c TOGGLE-STATE WELL LAW pins. Law source: scripts/t425c_toggle_state_
// law.py measured 900/900 BIT-EXACT over the full 30x30 face of all four
// layer-toggle buttons in docs/assets/refcap/original-strategic-map.png
// (mapping png = screen + 40; the png's rows 0..39 are pure black and the
// TURNCOUNT digits land at png y52..80 vs table 7..43). Working log
// docs/re/_wip_t425.md F8/F9.
//
// THE LAW: a layer toggle blits its SHAPEFRAME (1starmap k15..k18) with ONE
// palette substitution — well index 242 (game.pal raw (3,8,12) -> converted
// (12,32,48) navy) renders as index 80 (raw (22,6,14) -> (89,24,56) maroon)
// when its layer is ON, and stays 242 when OFF.
//
// The pins below are the PURE DATA half (no SDL): the constants, the palette
// colours they name, the well's presence/dominance in every toggle face, and
// the state -> colour prediction that the refcap itself confirms. The paint
// wiring is blitShapePalSwap (vendortext.cpp) called from ui.cpp step 3.
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

TEST(mapctl_t425c_well_constants_name_the_measured_colours) {
    REQUIRE_DATA();
    ascend::formats::GamePalette pal;
    std::string err;
    CHECK(pal.load(kA01 + "game.pal", &err));
    if (!pal.ready()) return;
    uint8_t rgb[3];
    // Well (OFF) colour: converted (12,32,48). ON colour: converted
    // (89,24,56) — the maroon the refcap shows on the three BUTTONSTATE 1
    // toggles. Both are 6-bit values (<=0x3f) in the file; gamepal applies
    // the DOSBox law c=(v<<2)|(v>>4).
    pal.rgb(kToggleWellIdx, rgb);
    CHECK(rgb[0] == 12 && rgb[1] == 32 && rgb[2] == 48);
    pal.rgb(kToggleWellOnIdx, rgb);
    CHECK(rgb[0] == 89 && rgb[1] == 24 && rgb[2] == 56);
    // Distinctness is the whole point of the law: an ON well can never
    // render the same colour as an OFF well.
    CHECK(kToggleWellIdx != kToggleWellOnIdx);
}

TEST(mapctl_t425c_every_toggle_face_carries_the_well_as_background) {
    REQUIRE_DATA();
    ascend::formats::ShapeLibrary lib;
    std::string err;
    CHECK(lib.load(kA01 + "1starmap.shp", &err));
    if (lib.count() < 19) return;
    // The well must be the DOMINANT index of each toggle face (it is the
    // button's interior: 577..647 px of 900 measured by the census), and the
    // face must be exactly 30x30 (rect 479,403..509,433 minus the bevel).
    for (int i = int(MapCtl::TogLanes); i <= int(MapCtl::TogColonies); i++) {
        const int frame = kMapCtl[i].shapeFrame;
        std::vector<uint8_t> px;
        const bool ok = lib.decode(frame, px);
        CHECK(ok);
        if (!ok) continue;
        const auto& rec = lib.record(frame);
        CHECK(int(rec.width) == 30 && int(rec.height) == 30);
        CHECK(int(px.size()) == 900);
        int well = 0;
        for (size_t k = 0; k < px.size(); k++)
            if (px[k] == uint8_t(kToggleWellIdx)) well++;
        // Measured: TOGLANES 645, TOGEMPIRE 644, TOGSHIPS 647, TOGCOLONIES
        // 577. The substitution only ever touches these pixels, so the well
        // count is also the number of pixels the state law can change.
        CHECK(well >= 500);
        CHECK(well < 900);  // never the whole face: the glyph must survive
    }
}

TEST(mapctl_t425c_default_states_predict_the_refcap_well_colours) {
    // The refcap is a natural experiment: exactly one toggle (TOGEMPIRE) has
    // BUTTONSTATE 0, so its well stays navy while the other three are maroon.
    // The port's defaults must reproduce that pattern — this is the cited
    // cross-check between windows.txt BUTTONSTATE and the paint law, and it
    // is what makes 900/900 exactness possible on all four buttons at once.
    auto wellOf = [](bool on) {
        return on ? kToggleWellOnIdx : kToggleWellIdx;
    };
    CHECK(wellOf(kCtlDefaultLanes) == 80);      // BS 1 -> maroon
    CHECK(wellOf(kCtlDefaultEmpire) == 242);    // BS 0 -> navy
    CHECK(wellOf(kCtlDefaultShips) == 80);      // BS 1 -> maroon
    CHECK(wellOf(kCtlDefaultColonies) == 80);   // BS 1 -> maroon
    // Distinct control indices: the four toggles are the LAST four entries of
    // kMapCtl (ui.cpp gates the swap on i >= TogLanes); the spin/zoom row is
    // NOT state-painted (negative control 74.6% -> 21.5% under the swap).
    CHECK(int(MapCtl::TogColonies) == kMapCtlCount - 1);
    CHECK(int(MapCtl::TogLanes) == kMapCtlCount - 4);
    CHECK(kMapCtl[int(MapCtl::RotRight)].shapeFrame == 8);
    CHECK(kMapCtl[int(MapCtl::TogLanes)].shapeFrame == 15);
    CHECK(kMapCtl[int(MapCtl::TogColonies)].shapeFrame == 18);
}
