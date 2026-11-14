// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
// t388: the in-game SCREEN law — the campaign is a set of vendor screens
// (state ids), and the rail buttons are screen switches. Pure data + math
// (no SDL), pinned by tests/test_statuslaw_t388.cpp.
//
// THE STATE FIELD IS A LIST, NOT A FLAG [verified 123/123 records,
// docs/re/_wip_t388.md]: "STATE 1 10" means "<count=1> <id=10>" — the
// leading integer equals the number of ids that follow, in every record of
// extracted/ascend00/windows.txt. A control/window is ACTIVE iff its id
// list contains the current state id. Consequences, all table facts:
//   - the five plain rail buttons (STATE "1 1") are active on the map
//     (state 1) ONLY;
//   - Intelligence (STATE "1 7") is active in the species menu (state 7)
//     ONLY — never on the map. This DISSOLVES t264's [inferred] z-order
//     rule for the 14-px RACES/Intelligence overlap: the overlap resolves
//     by screen, not by draw order.
//   - STATUSWND (STATE "1 10") is active in state 10 only; it
//     is a full independent screen (rect 7,7-632,472 contains the cosmos
//     rect, but the cosmos window's own STATE list "4 1 3 7 13" excludes
//     10, so the two never co-render).
//
// SCREEN SWITCH LAW [verified table + t264]: SENDMESSAGE 1 with SENDPARAM1
// = the target screen's state id, for STATUS(10) FLEET(18) RESEARCH(20)
// RACES(7) Intelligence(14). msg 5 (SPECIALAB) and msg 7/8 (NEXTTURN/
// NEXTTURNCONT) are NOT switches. A press whose target has no chrome in
// this port (e.g. RACE rows' 13 = NEGSCREEN) is a NO-OP, never a blank
// screen and never a clamp.
//
// HONEST NEGATIVE [verified]: the vendor SAVE and LOAD buttons exist ONLY
// in STATE "1 0" (the title menu, windows.txt L118-160). The campaign rail
// has NO save/load control, and windows.txt contains NO button named
// Galaxy, Production, or Design anywhere. The port's Alt-L/Alt-S chords
// inside the campaign are labelled PORT ADDITIONS (the title-screen D9
// hotkey twins), not vendor campaign law.
#include <optional>

#include "ui/hudlayout.h"
#include "ui/layout.h"

namespace ascend::ui {

// Campaign screens, values = the vendor STATE ids (windows.txt TYPE-100 /
// STATE fields; docs/re/_wip_t388.md carries the per-screen census).
enum Screen : int {
    kScreenMap = 1,          // COSMOSWnd (STATE list "4 1 3 7 13")
    kScreenSpecies = 7,      // species menu (RACE_1..7 474,7.. rows)
    kScreenStatus = 10,      // STATUSWND 7,7-632,472 + STATPLANLST 7,46-632,472
    kScreenIntel = 14,       // INTELSCREEN 7,7-632,34 header + INTELLIST 7,46-632,472
    kScreenFleet = 18,       // FLEETWND 7,7-632,472
    kScreenResearch = 20,    // RESWIN 7,46-476,472
};

// True iff the port renders chrome for `screen` (the known set). Presses
// targeting anything else are inert no-ops.
bool screenKnown(int screen);

// The screen-switch law: msg 1 with a known target id switches; everything
// else (msg 5, msg 7/8, unknown target) returns `cur` unchanged.
int screenAfterRailPress(int cur, int msg, int param1);

// Rail activity per screen (STATE id-lists; see header). The five plain
// buttons live on the map; Intelligence lives in the species menu; NO rail
// button is active inside Status/Fleet/Intel/Research.
bool railActive(RailButton b, int screen);

// Hit-map that honours activity: nullopt when the point's button is not
// active on `screen` (the t264 overlap law falls out of the tables).
std::optional<RailButton> railButtonForScreen(Pt p, int screen);

// Escape law [verified t252 live, ui-runtime.md §6b: "Escape returns to
// galaxy"]. True = go back to the map; false = the map itself, where the
// port's standing Esc-quit applies.
bool escapeToMap(int screen);

// ---- cited screen chrome rects (windows.txt, verbatim) --------------------
inline constexpr Rect kStatusWnd{7, 7, 632, 472};    // TYPE 16 STATUSWND
inline constexpr Rect kStatPlanLst{7, 46, 632, 472}; // TYPE 10 child, SHAPEFRAME 7
inline constexpr Rect kIntelScreen{7, 7, 632, 34};   // TYPE 12 INTELSCREEN (header)
inline constexpr Rect kIntelList{7, 46, 632, 472};   // TYPE 10 INTELLIST
inline constexpr Rect kFleetWnd{7, 7, 632, 472};     // TYPE 17 FLEETWND
inline constexpr Rect kResWin{7, 46, 476, 472};      // TYPE 9  RESWIN
// Species-menu race rows RACE_1..RACE_7 (TYPE 6, STATE "1 7", msg 1 p1 13
// = NEGSCREEN, not in the known set -> inert here). y 7/46/85/... pitch 39.
extern const Rect kRaceRows[7];

// The verbatim TEXTITEM label of the button that OPENS `screen` (Planets /
// Ships / Research / Species / Intelligence); "" for the map and for
// screens no cited button opens.
const char* screenTitle(int screen);

// Display name for log lines per screen id ("map" for 1; the TEXTITEM title
// otherwise). For stdout verification, not vendor text.
const char* screenName(int screen);

// Rail button names (the windows.txt NAME field, verbatim) in enum order —
// so log lines print the vendor identifier, not an invented one.
extern const char* const kRailName[kRailButtonCount];

// The button's TEXTITEM 0 label verbatim ('^' join joined to spaces):
// Planets / Ships / Research / Special Ability / Species / Intelligence.
const char* railLabel(RailButton b);

// The chrome shape library for `screen` by the windows.txt naming law
// (STATE id N ships its screen art as DATA\<N><name>.SHP: 1=1starmap,
// 20=20res, 10=10status, 14=14intel — the last two named by the phase-10
// evidence base + the STATE-id prefix [inferred], censused t388: both hold
// decodable records). nullptr = no library; draw frame + title only.
const char* screenShapeLib(int screen);

}  // namespace ascend::ui
