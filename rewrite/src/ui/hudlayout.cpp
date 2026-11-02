// HUD rail + ship-design tab law — see hudlayout.h for the citations. Pure
// data + lookup; no SDL (compiled into run_tests directly, layout.cpp /
// poppanel.cpp precedent).
#include "ui/hudlayout.h"

namespace ascend::ui {

// windows.txt verbatim (block lines cited in hudlayout.h / _wip_t264.md S1).
// Order == kRailButtonCount enum order.
const RailControl kRail[kRailButtonCount] = {
    /* Status          {{ X0,  Y0,   X1,   Y1 }, msg, p1 } */
    {{474, 130, 632, 160}, 1, 10},   // STATUS      line 481  -> STATUSWND
    {{474, 169, 632, 199}, 1, 18},   // FLEET       line 460  -> FLEETWND
    {{474, 208, 632, 238}, 1, 20},   // RESEARCH    line 439  -> RESWIN
    {{474, 247, 632, 277}, 5, 0},    // SPECIALAB   line 500  (ability, no win)
    {{474, 286, 632, 316}, 1, 7},    // RACES       line 180  -> species menu
    {{474, 303, 632, 333}, 1, 14},   // Intelligence line 843 -> INTELSCREEN
};

std::optional<RailButton> railButtonFor(Pt p) {
    // Intelligence is listed AFTER RACES and is shown when the species-menu
    // STATE ('1 7') is active; enumerating in file order and returning the
    // LAST hit resolves the documented 14 px overlap (y 303..316) to the
    // item on top. Off-rail points miss every rect (x < 474 or > 632).
    std::optional<RailButton> hit;
    for (int i = 0; i < kRailButtonCount; ++i)
        if (inRect(kRail[i].rect, p))
            hit = static_cast<RailButton>(i);
    return hit;
}

RailControl railControl(RailButton b) {
    const int i = static_cast<int>(b);
    return kRail[i >= 0 && i < kRailButtonCount ? i : kRailButtonCount - 1];
}

std::optional<ShapeRef> sidebarIcon(RailButton b) {
    // SHAPEITEM lines verbatim: "SHAPEITEM 1 data\1starmap.shp <f> 109 0".
    // RACES (WINITEMS 1) and Intelligence (WINITEMS 0) have NO shape item —
    // returning a frame for them would fabricate an icon the file lacks.
    switch (b) {
        case RailButton::Research:  return ShapeRef{"data\\1starmap.shp", 3};
        case RailButton::Fleet:     return ShapeRef{"data\\1starmap.shp", 4};
        case RailButton::Status:    return ShapeRef{"data\\1starmap.shp", 5};
        case RailButton::SpecialAbility: return ShapeRef{"data\\1starmap.shp", 7};
        default:                    return std::nullopt;
    }
}

int gizmoCatForShipTab(int sendMessage) {
    // THE TABLE (t253 measured 6/6 live; header block for why it cannot be
    // arithmetic). -1: HULL is the hull-size selector, msg 56 has no tab.
    switch (sendMessage) {
        case 51: return 0;  // WEAPONS  -> Weapon
        case 52: return 1;  // DEFENSES -> Shield
        case 54: return 2;  // ENGINES  -> Drive
        case 53: return 3;  // SENSORS  -> Scanner   (pair swapped vs msg!)
        case 55: return 4;  // ENERGY   -> Generator
        case 57: return 5;  // SPECIAL  -> Special
        default: return -1;  // includes HULL (50)
    }
}

int shipTabForGizmoCat(int gizmoCat) {
    switch (gizmoCat) {
        case 0: return 51;
        case 1: return 52;
        case 2: return 54;
        case 3: return 53;
        case 4: return 55;
        case 5: return 57;
        default: return -1;
    }
}

std::vector<int> gizmoListForTab(const std::vector<ascend::game::Gizmo>& gizmos,
                                 int sendMessage) {
    const int cat = gizmoCatForShipTab(sendMessage);
    if (cat < 0) return {};
    return ascend::game::gizmosByCategory(
        gizmos, static_cast<ascend::game::GizmoCat>(cat));
}

}  // namespace ascend::ui
