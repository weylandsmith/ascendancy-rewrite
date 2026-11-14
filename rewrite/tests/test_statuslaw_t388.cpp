// SPDX-License-Identifier: GPL-3.0-or-later
// t388 screen-law pins: the STATE field as an id-list (123/123 records,
// docs/re/_wip_t388.md), the msg-1 screen switch, rail activity per screen,
// the Escape law, and the verbatim chrome rects / labels / shape-library
// naming. Synthetic points only — headless-safe by construction.
#include "ui/statuslaw.h"

#include <string>

#include "harness.h"

namespace {
namespace au = ascend::ui;
using au::Pt;
}  // namespace

TEST(statuslaw_switch_msg1_known_target) {
    // The window-openers: SENDPARAM1 == target state id (t264 + re-read).
    CHECK(au::screenAfterRailPress(au::kScreenMap, 1, 10) == au::kScreenStatus);
    CHECK(au::screenAfterRailPress(au::kScreenMap, 1, 18) == au::kScreenFleet);
    CHECK(au::screenAfterRailPress(au::kScreenMap, 1, 20) == au::kScreenResearch);
    CHECK(au::screenAfterRailPress(au::kScreenMap, 1, 7) == au::kScreenSpecies);
    // Intelligence opens from the SPECIES MENU (its STATE list is "1 7");
    // the law itself is screen-agnostic, the activity filter handles that.
    CHECK(au::screenAfterRailPress(au::kScreenSpecies, 1, 14) == au::kScreenIntel);
    // Map id 1 is a legal target (COSMOSWnd's list contains 1).
    CHECK(au::screenAfterRailPress(au::kScreenStatus, 1, 1) == au::kScreenMap);
}

TEST(statuslaw_switch_no_clamp) {
    // msg 5 (SPECIALAB) and msg 7/8 (NEXTTURN/CONT) are NOT switches.
    CHECK(au::screenAfterRailPress(au::kScreenMap, 5, 0) == au::kScreenMap);
    CHECK(au::screenAfterRailPress(au::kScreenStatus, 7, 0) == au::kScreenStatus);
    CHECK(au::screenAfterRailPress(au::kScreenStatus, 8, 0) == au::kScreenStatus);
    // Unknown target ids are inert — never clamped into the known set.
    // 13 = NEGSCREEN (RACE rows' target), 17 = PLANETALLOC, 99 = nothing.
    CHECK(au::screenAfterRailPress(au::kScreenMap, 1, 13) == au::kScreenMap);
    CHECK(au::screenAfterRailPress(au::kScreenMap, 1, 17) == au::kScreenMap);
    CHECK(au::screenAfterRailPress(au::kScreenMap, 1, 99) == au::kScreenMap);
    CHECK(!au::screenKnown(13) && !au::screenKnown(17) && au::screenKnown(10));
    // msg 0 (window bookkeeping) never switches either.
    CHECK(au::screenAfterRailPress(au::kScreenFleet, 0, 10) == au::kScreenFleet);
}

TEST(statuslaw_rail_activity_state_lists) {
    // "1 1" buttons: map only.
    for (int s : {au::kScreenStatus, au::kScreenFleet, au::kScreenIntel,
                  au::kScreenResearch, au::kScreenSpecies}) {
        CHECK(!au::railActive(au::RailButton::Status, s));
        CHECK(!au::railActive(au::RailButton::Fleet, s));
        CHECK(!au::railActive(au::RailButton::Research, s));
        CHECK(!au::railActive(au::RailButton::SpecialAbility, s));
        CHECK(!au::railActive(au::RailButton::Races, s));
    }
    CHECK(au::railActive(au::RailButton::Status, au::kScreenMap));
    CHECK(au::railActive(au::RailButton::Races, au::kScreenMap));
    // Intelligence: species menu ONLY (STATE "1 7") — the t264 overlap's
    // z-order inference is replaced by this table fact.
    CHECK(au::railActive(au::RailButton::Intelligence, au::kScreenSpecies));
    CHECK(!au::railActive(au::RailButton::Intelligence, au::kScreenMap));
}

TEST(statuslaw_hitmap_overlap_cannot_arise) {
    // The 14-px RACES/Intelligence overlap zone (y 303..316, x 474..632):
    // on the map it hits RACES (Intelligence inactive); in the species menu
    // it hits Intelligence (RACES inactive). The ambiguity t264 had to
    // [infer] is gone.
    const Pt overlap{553, 310};
    auto onMap = au::railButtonForScreen(overlap, au::kScreenMap);
    CHECK(onMap.has_value() && *onMap == au::RailButton::Races);
    auto onSpecies = au::railButtonForScreen(overlap, au::kScreenSpecies);
    CHECK(onSpecies.has_value() && *onSpecies == au::RailButton::Intelligence);
    // Inside an opened screen nothing on the rail hits at all.
    CHECK(!au::railButtonForScreen(overlap, au::kScreenStatus).has_value());
    CHECK(!au::railButtonForScreen({553, 145}, au::kScreenStatus).has_value());
    // Off-rail x misses everywhere.
    CHECK(!au::railButtonForScreen({100, 145}, au::kScreenMap).has_value());
    // Inclusive edges (windows.txt rects are inclusive).
    auto edge = au::railButtonForScreen({474, 130}, au::kScreenMap);
    CHECK(edge.has_value() && *edge == au::RailButton::Status);
    auto edge2 = au::railButtonForScreen({632, 160}, au::kScreenMap);
    CHECK(edge2.has_value() && *edge2 == au::RailButton::Status);
}

TEST(statuslaw_rects_verbatim_windows_txt) {
    CHECK(au::kStatusWnd.x0 == 7 && au::kStatusWnd.y0 == 7 &&
          au::kStatusWnd.x1 == 632 && au::kStatusWnd.y1 == 472);
    CHECK(au::kStatPlanLst.x0 == 7 && au::kStatPlanLst.y0 == 46 &&
          au::kStatPlanLst.x1 == 632 && au::kStatPlanLst.y1 == 472);
    CHECK(au::kIntelScreen.x0 == 7 && au::kIntelScreen.y0 == 7 &&
          au::kIntelScreen.x1 == 632 && au::kIntelScreen.y1 == 34);
    CHECK(au::kIntelList.y0 == 46 && au::kIntelList.x1 == 632 &&
          au::kIntelList.y1 == 472);
    CHECK(au::kFleetWnd.x0 == 7 && au::kFleetWnd.y1 == 472);
    CHECK(au::kResWin.x0 == 7 && au::kResWin.y0 == 46 &&
          au::kResWin.x1 == 476 && au::kResWin.y1 == 472);
    // RACE_1..RACE_7: y 7/46/85/124/163/202/241, pitch 39, x-band 474.
    int y = 7;
    for (int i = 0; i < 7; i++, y += 39) {
        CHECK(au::kRaceRows[i].x0 == 474 && au::kRaceRows[i].y0 == y);
        CHECK(au::kRaceRows[i].x1 == 632 && au::kRaceRows[i].y1 == y + 30);
    }
}

TEST(statuslaw_titles_are_the_opening_buttons_textitem) {
    // TEXTITEM 0 verbatim; the map has no cited title (empty, not invented).
    CHECK(std::string(au::screenTitle(au::kScreenStatus)) == "Planets");
    CHECK(std::string(au::screenTitle(au::kScreenFleet)) == "Ships");
    CHECK(std::string(au::screenTitle(au::kScreenResearch)) == "Research");
    CHECK(std::string(au::screenTitle(au::kScreenSpecies)) == "Species");
    CHECK(std::string(au::screenTitle(au::kScreenIntel)) == "Intelligence");
    CHECK(std::string(au::screenTitle(au::kScreenMap)).empty());
}

TEST(statuslaw_shape_lib_naming) {
    // TYPE-100 census names 1=1starmap + 20=20res verbatim; 10status and
    // 14intel follow the STATE-id prefix law (censused decodable t388).
    // Screens with NO cited library return nullptr — never a guess.
    CHECK(std::string(au::screenShapeLib(au::kScreenMap)) == "1starmap.shp");
    CHECK(std::string(au::screenShapeLib(au::kScreenStatus)) == "10status.shp");
    CHECK(std::string(au::screenShapeLib(au::kScreenIntel)) == "14intel.shp");
    CHECK(std::string(au::screenShapeLib(au::kScreenResearch)) == "20res.shp");
    CHECK(au::screenShapeLib(au::kScreenSpecies) == nullptr);
    CHECK(au::screenShapeLib(au::kScreenFleet) == nullptr);
}

TEST(statuslaw_escape) {
    // Every non-map screen returns to the map (t252 live: "Escape returns
    // to galaxy"); the map itself keeps the port's Esc-quit.
    CHECK(au::escapeToMap(au::kScreenStatus));
    CHECK(au::escapeToMap(au::kScreenSpecies));
    CHECK(au::escapeToMap(au::kScreenIntel));
    CHECK(!au::escapeToMap(au::kScreenMap));
}
