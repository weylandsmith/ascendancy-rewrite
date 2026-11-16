// SPDX-License-Identifier: GPL-3.0-or-later
// t388 screen law — see statuslaw.h for the citations. Pure data + lookup;
// no SDL (compiled into run_tests directly, hudlayout.cpp precedent).
#include "ui/statuslaw.h"

namespace ascend::ui {

bool screenKnown(int screen) {
    switch (screen) {
        case kScreenMap:
        case kScreenSpecies:
        case kScreenStatus:
        case kScreenIntel:
        case kScreenFleet:
        case kScreenResearch:
        case kScreenPlanet:   // t406 PLANETALLOC (opener = status row click)
        case kScreenSystemView:  // t410 the System Display (opener = map star
                                 // click, t338 measured; STATE "1 16" x20)
            return true;
        default:
            return false;  // 13 NEGSCREEN (t409 seam), 0 title, ...: no chrome
    }
}

int screenAfterRailPress(int cur, int msg, int param1) {
    // The switch law: msg 1 = "change screen to param1" (t264: param1 ==
    // the target window's STATE number for all four window-openers; RACES
    // 7 re-read this session). msg 5 / 7 / 8 are not switches; an unknown
    // target is inert. NEVER clamp cur to something "close".
    if (msg == 1 && screenKnown(param1)) return param1;
    return cur;
}

bool railActive(RailButton b, int screen) {
    // Intelligence: STATE "1 7" — the species menu only.
    if (b == RailButton::Intelligence) return screen == kScreenSpecies;
    // The other five: STATE "1 1" — the map only.
    return screen == kScreenMap;
}

std::optional<RailButton> railButtonForScreen(Pt p, int screen) {
    // Same file-order / last-hit scan as railButtonFor (t264), filtered by
    // the STATE id-list law. On the map only RACES can ever hit (Intelligence
    // is inactive), so t264's 14-px overlap cannot arise; in the species
    // menu only Intelligence can hit.
    std::optional<RailButton> hit;
    for (int i = 0; i < kRailButtonCount; ++i) {
        const RailButton b = static_cast<RailButton>(i);
        if (railActive(b, screen) && inRect(kRail[i].rect, p)) hit = b;
    }
    return hit;
}

bool escapeToMap(int screen) { return screen != kScreenMap; }

const Rect kRaceRows[7] = {
    {474, 7, 632, 37},    {474, 46, 632, 76},   {474, 85, 632, 115},
    {474, 124, 632, 154}, {474, 163, 632, 193}, {474, 202, 632, 232},
    {474, 241, 632, 271},
};

const char* screenTitle(int screen) {
    // TEXTITEM 0 strings verbatim (windows.txt; '^' join joined to spaces).
    switch (screen) {
        case kScreenStatus:   return "Planets";        // STATUS
        case kScreenFleet:    return "Ships";          // FLEET
        case kScreenResearch: return "Research";       // RESEARCH
        case kScreenSpecies:  return "Species";        // RACES
        case kScreenIntel:    return "Intelligence";   // Intelligence
        default:              return "";               // map; no cited title
    }
}

const char* screenName(int screen) {
    if (screen == kScreenMap) return "map";
    // t410: the System Display has no TEXTITEM (no rail button opens it —
    // the name is help.txt ln1149 "System Display" verbatim, header of the
    // batmode help page).
    if (screen == kScreenSystemView) return "System Display";
    // t410: state 17's help.txt name verbatim ("Planet Display", ln1501-7)
    // so the Escape-chain log line names the screen instead of "?".
    if (screen == kScreenPlanet) return "Planet Display";
    const char* t = screenTitle(screen);
    return *t ? t : "?";
}

const char* const kRailName[kRailButtonCount] = {
    "STATUS", "FLEET", "RESEARCH", "SPECIALAB", "RACES", "Intelligence",
};

const char* railLabel(RailButton b) {
    // TEXTITEM 0 verbatim ('^' word-join joined to spaces).
    switch (b) {
        case RailButton::Status:         return "Planets";
        case RailButton::Fleet:          return "Ships";
        case RailButton::Research:       return "Research";
        case RailButton::SpecialAbility: return "Special Ability";
        case RailButton::Races:          return "Species";
        case RailButton::Intelligence:   return "Intelligence";
    }
    return "";
}

const char* screenShapeLib(int screen) {
    // Naming law: the STATE-id N screen's art file is DATA\<N><name>.SHP —
    // the eight TYPE-100 blocks (0/1/3/7/8/13/16/20) are the census this is
    // generalised from; 10status/14intel/2savegam/4loadgam follow the same
    // prefix law [inferred] and both 10status (k0 639x479 V) and 14intel
    // (10 records) decode (scripts/r388_status_census.py). RESWIN's era art
    // is 20res.shp per windows.txt TYPE-100 STATENUMBER 20.
    switch (screen) {
        case kScreenMap:      return "1starmap.shp";
        case kScreenStatus:   return "10status.shp";
        case kScreenPlanet:   return "17np.shp";  // t406: STATE-id prefix +
                                   // k0 639x479 decoded, panel borders land
                                   // on the windows.txt panel rects
                                   // (_wip_t406.md F6) [inferred binding]
        case kScreenIntel:      return "14intel.shp";
        case kScreenResearch:  return "20res.shp";
        case kScreenSystemView: return "16battle.shp";  // t410: TYPE-100
                                   // STATENUMBER 16 ln1140-1142 names it
                                   // EXPLICITLY (not the prefix law); no
                                   // full-screen record exists in the lib
                                   // (dims census _wip_t410 F3) so the
                                   // backdrop test declines it — faces only
        default:              return nullptr;  // species menu, FLEETWND:
    }                                            // no cited library
}

}  // namespace ascend::ui
