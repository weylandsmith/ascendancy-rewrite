// SPDX-License-Identifier: GPL-3.0-or-later

#pragma once
// HUD RAIL + SHIP-DESIGN TAB layout law — t264.
//
// The right-hand rail and the ship-design tab grid are pure DATA in
// extracted/ascend00/windows.txt, and the rail icons / tab->gizmo-category
// bindings are MEASURED live facts (docs/re/ui-runtime.md §6a t252, §6c
// t253). This module is the wiring those measurements produced: no SDL, no
// drawing (vendor sprites stay OQ-005-scoped, ui-runtime.md §2), just the
// hit-map, the icon law, and the category table. Module template:
// ui/poppanel.h (t263).
//
//   RAIL LAW [verified windows.txt, re-parsed t264 docs/re/_wip_t264.md S1]:
//     six controls live on x-band 474..632 with inclusive rects;
//     each opens/acts via SENDMESSAGE + SENDPARAM1, and for the four
//     window-opening buttons SENDPARAM1 == the target window's STATE number
//     (10 STATUSWND line 1020, 18 FLEETWND 1725, 20 RESWIN 1763, 14
//     INTELSCREEN 1109; RACES 7 = the '1 7' species-menu class [inferred]).
//
//   ICON LAW [verified windows.txt WINITEMS lines + t252 live clicks]:
//     RESEARCH/FLEET/STATUS/SPECIALAB are WINITEMS 2 = TEXTITEM 0 +
//     SHAPEITEM 1 data\1starmap.shp <frame> 109 0 with frames
//     3=Research 4=Ships 5=Planets 7=Special. RACES has WINITEMS 1 (text
//     only) and Intelligence WINITEMS 0 — buttons WITHOUT icons exist, so
//     an unconditional icon lookup is wrong by construction.
//
//   TAB -> GIZMO-CATEGORY MAP [measured 6/6 live t253 against gizmos.txt's
//   category field and file order; structurally re-corroborated t264]:
//     WEAPONS(msg 51)=cat0  DEFENSES(52)=cat1  ENGINES(54)=cat2
//     SENSORS(53)=cat3      ENERGY(55)=cat4    SPECIAL(57)=cat5
//     HULL(50) is NOT a gizmo category (pressing it left the GIZLIST at
//     0 px change; it is the hull-SIZE selector, help hull). msg 56 belongs
//     to no tab. THE MAP IS NOT DERIVABLE: the middle pair is swapped
//     relative to message order (53->cat3, 54->cat2), so any rewrite that
//     computes a category from the message number or the tile index is
//     WRONG. The table below is the law; test_hudlayout_t264 pins it.
//
//   GIZLIST ORDER LAW [verified file-level t264]: gizmos.txt records group
//   contiguously by category in file order 0..5 (counts 10/6/5/6/5/44,
//   76 total == economy.cpp's loadGizmos invariant), so the vendor's
//   per-category list order == file order == game::gizmosByCategory().

#include <optional>
#include <vector>

#include "game/economy.h"  // Gizmo, GizmoCat, gizmosByCategory
#include "ui/layout.h"     // Rect, Pt, inRect

namespace ascend::ui {

// ---- the rail (windows.txt lines 481/460/439/500/180/843) -----------------
enum class RailButton {
    Status,       // "Planets"   474,130-632,160  msg 1 p1 10 -> STATUSWND
    Fleet,        // "Ships"     474,169-632,199  msg 1 p1 18 -> FLEETWND
    Research,     // "Research"  474,208-632,238  msg 1 p1 20 -> RESWIN
    SpecialAbility,  // "Special Ability" 474,247-632,277  msg 5 p1 0
    Races,        // "Species"   474,286-632,316  msg 1 p1 7  -> species menu
    Intelligence  // "Intelligence" 474,303-632,333 STATE '1 7' msg 1 p1 14
};
inline constexpr int kRailButtonCount = 6;

// Rect + message triple per rail button, verbatim from windows.txt (t264).
struct RailControl {
    Rect rect;
    int sendMessage;
    int sendParam1;
};
extern const RailControl kRail[kRailButtonCount];

// Which rail button (if any) owns point p. Inclusive edges (windows.txt
// rects are inclusive; layout.h inRect). Intelligence's rect overlaps
// RACES' (y 303..316 shared) — it is the menu-state item shown on top, so
// the overlap resolves to Intelligence [inferred z-order; the file gives no
// draw order, and no live click ever landed in the 14 px overlap].
std::optional<RailButton> railButtonFor(Pt p);

// Convenience: the (message, param1) pair to send for a rail button.
RailControl railControl(RailButton b);

// ---- rail icons (windows.txt SHAPEITEM lines, t252 live-corroborated) -----
struct ShapeRef {
    const char* shapeFile;  // vendor path, verbatim case as in windows.txt
    int frame;              // SHAPEITEM frame index
};
// The button's icon, or nullopt where the file has no SHAPEITEM (RACES,
// Intelligence). Drawing the referenced shape stays blocked on OQ-005.
std::optional<ShapeRef> sidebarIcon(RailButton b);

// ---- t400 RAIL ICON PLACEMENT LAW (D11 "wrong side / wrong size") ---------
// The SHAPEITEM line carries two trailing fields: "SHAPEITEM <en> <lib>
// <frame> <dx> <dy>" — dx=109, dy=0 verbatim on all four rail icons
// (windows.txt L456/477/498/517). MEASURED (docs/re/_wip_t400.md S1/S5,
// t398 registration + chromatic map of scratchpad/galaxymap-original.png):
// the vendor paints the icon RIGHT of the label at x = rect.x0 + 109
// (474+109 = 583; registration best-fit 584/585 — capture noise ±2), and
// VERTICALLY CENTRED in the 30 px button: measured icon centres land
// within ±3 px of the button centres on all four rows (k5 143.5/145,
// k4 186.5/184, k3 224/223, k7 263/262). Size law: NATIVE 1:1 — the
// records (43-45 px wide) fit the shot at that placement with 93-97% of
// pixels within 12 of game.pal (palette.md §4); the D11 "wrong size"
// symptom was the pre-t394 vector-rect build, not a vendor scale.
inline constexpr int kRailIconDx = 109;  // SHAPEITEM dx verbatim
struct IconPos { int x, y; };
// Placement for an icon of width `w`/height `h` (native record dims) in
// button `b`. x ignores `w` (LEFT-anchored at dx, the vendor law).
IconPos railIconPos(RailButton b, int h);

// ---- t400 SPECIES-ROW FLAGS (D11 "icons on the species button missing") ---
// RACES is WINITEMS 1 (no SHAPEITEM) and Intelligence WINITEMS 0, yet the
// vendor original shows TWO small race portraits right of the "Species"
// label (MEASURED content run x521..552 y288..314 = two 14 px boxes with a
// 4 px gap; docs/re/_wip_t400.md S6/S11). The art is raceflag.shp: 21
// records, ALL exactly 14x24 — the only lib in the corpus of that shape
// class at 21 records (21 races; frame index == specnum [inferred from the
// 21==21 census + the smraceNN sibling pattern]). Its dominant colour is
// EXACTLY the button fill (12,32,48), so it blits seamlessly.
// WHICH two races the vendor shows is uncited (NAMED SEAM — decider: a
// live witness with a known player species). Port law: LEFT box = the
// player's species flag (skipped for playerSpecies -1, no human flag
// exists), RIGHT box = the first AI specnum.
struct FlagSlot { Rect rect; };  // absolute screen rect, native 14x24
extern const FlagSlot kSpeciesFlagSlots[2];

// ---- ship-design tabs (windows.txt lines 897..1002, t253 measured) --------
// The seven tab SENDMESSAGE numbers, in FILE order (tile order: row 1
// WEAPONS HULL DEFENSES, row 2 ENGINES SENSORS ENERGY SPECIAL).
inline constexpr int kShipTabMessages[7] = {51, 50, 52, 54, 53, 55, 57};

// Tab message -> gizmo category id (0..5); -1 for HULL (50) and for any
// message that is not a tab (e.g. 56). NOT derivable from the message
// number — see the header block.
int gizmoCatForShipTab(int sendMessage);

// Inverse: gizmo category id -> the tab message that selects it. -1 for a
// category with no tab (impossible for 0..5; defensive for other input).
int shipTabForGizmoCat(int gizmoCat);

// The GIZLIST contents for the tab `sendMessage`, as indices into `gizmos`
// (file order). Empty for HULL / non-tabs. Identity with
// game::gizmosByCategory per the GIZLIST ORDER LAW, pinned by the test.
std::vector<int> gizmoListForTab(const std::vector<ascend::game::Gizmo>& gizmos,
                                 int sendMessage);

}  // namespace ascend::ui
