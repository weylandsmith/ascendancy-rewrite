// SPDX-License-Identifier: GPL-3.0-or-later

// t405 SUB-SCREEN NAVIGATION + RAIL STATEMENT pins.
//
// LAW (docs/re/_wip_t405.md F1-F8, this session's measurements):
//  1. The rail is MAP-ONLY by the windows.txt STATE id-list law: the five
//     plain rail buttons carry STATE "1 1"; NO sub-screen id (10/14/18/20)
//     appears in any rail-button list. Corroborated by the vendor backdrop
//     10status.shp k0 (decoded + native-vision-graded): full-width art with
//     NO button faces at the rail y-bands — the rail column is OCCUPIED by
//     screen art (race-standings panel + scrollbar). So "screens swap, rail
//     hidden" is the vendor law; the t405 queue premise ("rail stays live")
//     is REFUTED. railActive() already implemented it; these pins freeze it.
//  2. The status-screen hit-map is UNIFIED with precedence arrows ->
//     scroll-column -> rows, arrow rects MEASURED on the backdrop pixel
//     plane (top box x619..638 y48..94, bottom box x620..638 y425..476).
//     The old PORT rects started at x566 and the raw row test accepted any
//     x, so a click at the rail's last-known position (x>=566) scrolled or
//     selected — the owner's D13 "Ships/Research clicks route into the
//     status scroll". statusHitFor must return None there.
// No vendor data is read: no REQUIRE_DATA() needed (t403 guard census).
#include "ui/statuslaw.h"
#include "ui/statuslist.h"

#include "harness.h"

namespace {
namespace au = ascend::ui;
constexpr int kTop = au::kStatusRowsTop;
}  // namespace

TEST(statusnav_arrows_measured_t405) {
    using H = au::StatusHit;
    // Inside the measured art boxes -> arrows.
    CHECK(au::statusHitFor(au::Pt{628, 60}, kTop).kind == H::ArrowUp);
    CHECK(au::statusHitFor(au::Pt{628, 450}, kTop).kind == H::ArrowDown);
    // The D13 defect zone: the old 566-wide arrows covered (566..632,
    // 46..70). Those points are NOT arrows anymore — x 566..618 is list.
    CHECK(au::statusHitFor(au::Pt{580, 60}, kTop).kind == H::Row);
    CHECK(au::statusHitFor(au::Pt{580, 60}, kTop).row == 0);
    // Trough between the boxes: inert (must not scroll, must not select).
    CHECK(au::statusHitFor(au::Pt{628, 200}, kTop).kind == H::None);
    // Outside the column entirely: None.
    CHECK(au::statusHitFor(au::Pt{633, 200}, kTop).kind == H::None);
}

TEST(statusnav_rows_are_the_table_t405) {
    using H = au::StatusHit;
    const auto r =
        au::statusHitFor(au::Pt{300, kTop + au::kStatusRowPitch + 5}, kTop);
    CHECK(r.kind == H::Row && r.row == 1);
    CHECK(au::statusHitFor(au::Pt{300, kTop - 1}, kTop).kind == H::None);
    CHECK(au::statusHitFor(au::Pt{300, kTop + 3 * au::kStatusRowPitch}, kTop)
              .kind == H::None);
    // Left of the table interior (x < 7): outside the list.
    CHECK(au::statusHitFor(au::Pt{2, kTop + 10}, kTop).kind == H::None);
    // The scrollbar-column boundary in the TROUGH band (between the arrow
    // boxes): x=619 inert, x=618 still row. (At y inside an arrow box the
    // arrow wins first — tested above.)
    CHECK(au::statusHitFor(au::Pt{619, 200}, kTop).kind == H::None);
    CHECK(au::statusHitFor(au::Pt{618, 200}, kTop).kind == H::Row);
}

TEST(statusnav_rail_is_map_only_vendor_law_t405) {
    // windows.txt STATE "1 1": active on the map ONLY. Corroborated by the
    // 10status k0 backdrop (no rail faces; standings art occupies x>=474).
    for (const int s : {au::kScreenStatus, au::kScreenFleet, au::kScreenIntel,
                        au::kScreenResearch}) {
        CHECK(!au::railActive(au::RailButton::Status, s));
        CHECK(!au::railActive(au::RailButton::Fleet, s));
        CHECK(!au::railActive(au::RailButton::Research, s));
        CHECK(!au::railActive(au::RailButton::Races, s));
        // A click at the rail's map position inside a sub-screen hits NO
        // button (the vendor backdrop is painted over it).
        CHECK(!au::railButtonForScreen(au::Pt{553, 145}, s).has_value());
    }
    CHECK(au::railActive(au::RailButton::Status, au::kScreenMap));
    CHECK(au::railButtonForScreen(au::Pt{553, 145}, au::kScreenMap)
              .value_or(au::RailButton::Status) == au::RailButton::Status);
}

TEST(statusnav_swap_and_escape_chain_t405) {
    // msg 1 resolves to the target from ANY current screen (swap law):
    CHECK(au::screenAfterRailPress(au::kScreenStatus, 1, 18) == au::kScreenFleet);
    CHECK(au::screenAfterRailPress(au::kScreenStatus, 1, 20) == au::kScreenResearch);
    // Unknown targets (13 NEGSCREEN, 17 PLANETALLOC) never clamp.
    CHECK(au::screenAfterRailPress(au::kScreenStatus, 1, 13) == au::kScreenStatus);
    // Esc returns to the map from EVERY sub-screen (t252 live law).
    CHECK(au::escapeToMap(au::kScreenStatus));
    CHECK(au::escapeToMap(au::kScreenFleet));
    CHECK(au::escapeToMap(au::kScreenIntel));
    CHECK(au::escapeToMap(au::kScreenResearch));
    CHECK(au::escapeToMap(au::kScreenSpecies));
    CHECK(!au::escapeToMap(au::kScreenMap));
}
