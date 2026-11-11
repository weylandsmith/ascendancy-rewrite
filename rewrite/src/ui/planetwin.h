// SPDX-License-Identifier: GPL-3.0-or-later

#pragma once
// PLANET SCREEN (PLANETALLOC) window composition law — t276.
//
// The vendor planet screen is one TYPE-7 parent window with two list/square
// children and FIVE TYPE-29 paint panels, left to right. Everything below is
// either verbatim windows.txt data or a cited paint law; the module is pure
// (no SDL, no drawing — vendor sprites stay OQ-005-scoped, ui-runtime.md §2),
// the hit-map + dispatch key + header-format + selector composition ready
// for the blit layer. Module template: ui/hudlayout.h (t264), ui/poppanel.h
// (t263). Full working notes: docs/re/_wip_t276.md.
//
//   PANEL TABLE [verified verbatim windows.txt, _wip_t276.md S1]:
//     parent PLANETALLOC (line 1486) TYPE 7 rect 0,0..639,479 msg 3;
//     children in FILE ORDER: PLANLIST (10, 120,120..520,420, line 1504),
//     PLSQUARE (14, 152,120..487,375, line 1520), then the five TYPE-29
//     panels PLRES/PLIND/PLPRO/PLPOP/PLBUILD (lines 1536/1553/1570/1587/
//     1604). All five carry STATE '1 17', MOUSEFOCUS 0, SHAPEFRAME -1 (NO
//     windows.txt shape binding — planets-ui.md S1), WINITEMS 0.
//     The X-bands are DISJOINT with a uniform 9 px gutter and file order ==
//     left-to-right order; that order IS the paint-dispatch order (S2).
//
//   DISPATCH KEY LAW [verified planets-ui.md S2, planwin paint body
//   0x3cc15..0x3cca6; case-body table read live from 41.sav 0x3cb98 =
//   [0x3cca7,0x3cd3b,0x3cdcf,0x3ce39,0x3cefd]]:
//     key = widget SENDPARAM1-slot byte (+0x47), then TWO code-side remaps:
//       0x3cc1c: key 4 -> 3          (PLPOP, whose SENDPARAM1 is 4)
//       0x3cc29: SENDMESSAGE == 51 -> 4  (PLBUILD; without this its
//                 SENDPARAM1 1 would collide with PLIND's key 1 — the remap
//                 is load-bearing, pinned by test_planetwin_t276)
//     key 0=PLRES 1=PLIND 2=PLPRO 3=PLPOP 4=PLBUILD; key>4 -> default case
//     0x3d1bc (unreachable from windows.txt data).
//
//   HEADER GETTER LAW [verified selfplay.md t246/t248 + aicode.md getter
//   convention; records are the 0-indexed quoted strings of static.txt,
//   count 191 == live 0xbf law (aicode.md:700-706)]:
//     #147 "%s" construction text prefix   'Under Construction at %s'
//     #148 'Being Refitted at %s'
//     #149 '\nMoving to Planet'   #150 '\nMoving to Starlane'
//          (file bytes carry a LITERAL backslash-n; the fleet row renders
//           the location on a second line, ui-runtime.md §6c — the loader
//           interprets it [inferred]. Constants below hold a REAL newline.)
//     #151 '%s  (%d Planet%s Occupied, %d System%s Controlled)' — the planet
//          LIST header. DOUBLE SPACE byte-exact. Measured: systems leg ==
//          systems_any EXACT at t1086 (26) and t1254 (36); planets leg is a
//          maintained counter, NOT the table count (selfplay.md PROOF 3:
//          heap-window u16 read at FUN_00051684; table count 80 vs header 60
//          @t1086). Callers therefore PASS the counts; nothing here derives
//          them.
//     #152 '%s  (%d Ship%s, %d more allowed)' — the FLEET header (headroom
//          form, vision-read "Chamachies (25 Ships, 12 more allowed)",
//          ui-runtime.md §6c).
//     #153 'Player Species'.
//     PLURALIZATION [inferred]: singular iff count==1 with the vendor's
//     generic plural pair static.txt #28 '' / #29 's' (the exact pair the
//     ability countdown uses per aicode.md §8.2 cmp edx,1 @0x37bfb). No
//     cited call-site proof exists for #151/#152 specifically — live
//     testimony shows plural forms only. Treat as rewrite default.
//
//   GAUGE WIRING [verified planets-ui.md S3 table]: PLRES reads u16 +0x46
//   RES, PLIND reads u16 +0x44 IND (both selector clamp0..20(round(L^0.75))
//   == ui::gaugeSelector), PLPRO reads u16 +0x48 PROS identity clamp0..20
//   == ui::prosSelector. Campaign::channelWordsFor(star) is the exact
//   +0x44/+0x46/+0x48 analog triple (incl. the t45 governor branch).
//
//   PLBUILD ICON [shp.md S23.4]: planitem.shp rec == current-project item
//   art; cited for item idx 34 == rec k34 (live MAD 1.5 vs next best 42.1).
//   The identity mapping for the other 39 items stays an OQ-005 contact-
//   sheet fold [inferred] — plbuildIcon documents that boundary.

#include <optional>
#include <string>

#include "game/campaign.h"
#include "ui/layout.h"  // Rect, Pt, inRect

namespace ascend::ui {

// ---- the five TYPE-29 panels (windows.txt lines 1536..1604) ----------------
enum class PlanetPanel { PlRes, PlInd, PlPro, PlPop, PlBuild };
inline constexpr int kPlanetPanelCount = 5;

struct PlanetPanelInfo {
    Rect rect;             // inclusive, windows.txt verbatim
    int sendMessage;       // SENDMESSAGE
    int sendParam1;        // SENDPARAM1 (pre-remap; see paintKey)
    const char* helpIndex; // HELPINDEX (lowercase words.txt keys)
};
// Order == enum order == file order == left-to-right paint order.
extern const PlanetPanelInfo kPlanetPanels[kPlanetPanelCount];

// Parent + non-panel children (verbatim; the composition keeps them separate
// from the panel strip — PLANLIST/PLSQUARE are the list-mode widgets).
inline constexpr Rect kPlanetAllocRect{0, 0, 639, 479};   // line 1486 TYPE 7
inline constexpr Rect kPlanListRect{120, 120, 520, 420};  // line 1504 TYPE 10
inline constexpr Rect kPlSquareRect{152, 120, 487, 375};  // line 1520 TYPE 14

// Which TYPE-29 panel owns point p (inclusive edges; panels are disjoint so
// the answer is unique). nullopt for every other pixel — including
// PLANLIST/PLSQUARE interiors, which are NOT panels.
std::optional<PlanetPanel> planetPanelFor(Pt p);

// The paint-dispatch key for a widget's (SENDMESSAGE, SENDPARAM1) pair,
// applying the two remaps of the DISPATCH KEY LAW. Keys: see header. -1 ==
// the default case 0x3d1bc (no windows.txt widget reaches it).
int paintKey(int sendMessage, int sendParam1);

// Convenience: the dispatch key of one panel from the table.
int paintKeyFor(PlanetPanel p);

// ---- header strings (static.txt verbatim; getter index in citations) ------
// NOTE the DOUBLE SPACE between %s and '(' in #151/#152 (byte-exact).
inline constexpr const char* kFmtPlanetsOccupied =
    "%s  (%d Planet%s Occupied, %d System%s Controlled)";  // #151
inline constexpr const char* kFmtShips =
    "%s  (%d Ship%s, %d more allowed)";                    // #152
inline constexpr const char* kStrUnderConstruction = "Under Construction at %s";  // #147
inline constexpr const char* kStrBeingRefitted = "Being Refitted at %s";          // #148
inline constexpr const char* kStrMovingToPlanet = "\nMoving to Planet";            // #149
inline constexpr const char* kStrMovingToStarlane = "\nMoving to Starlane";        // #150
inline constexpr const char* kStrPlayerSpecies = "Player Species";                 // #153
// The generic plural pair (static.txt #28/#29) used by the formatters below.
inline constexpr const char* kPluralNone = "";   // #28
inline constexpr const char* kPluralS = "s";     // #29

// pluralSuffix(n) — [inferred law, header block]: "" iff n == 1, else "s".
const char* pluralSuffix(int n);

// snprintf wrappers over the verbatim templates (buffer-safe; returns the
// formatted string). planetsArg/systemsArg feed #151's two counts; the
// caller supplies the MAINTAINED counter for planets (see HEADER GETTER LAW
// — the table count is provably NOT the source).
std::string formatPlanetHeader(const std::string& owner, int planets,
                               int systems);
std::string formatShipHeader(const std::string& owner, int ships,
                             int moreAllowed);
std::string constructionText(const std::string& planetName);
std::string refitText(const std::string& planetName);
// #149/#150: fragments appended to a name (leading newline is in the string).
std::string movingToPlanetText();
std::string movingToStarlaneText();

// ---- gauge wiring (planets-ui.md S3 via Campaign::channelWordsFor) --------
struct PlanetGauges {
    int res;    // selector for PLRES  (gaugeSelector of +0x46 analog)
    int ind;    // selector for PLIND  (gaugeSelector of +0x44 analog)
    int pros;   // selector for PLPRO  (prosSelector of +0x48 analog)
};
// The three gauge selectors for one campaign planet, each clamp0..20.
PlanetGauges planetGaugesFor(const ascend::game::Campaign& camp, int star);

// ---- PLBUILD current-project icon ------------------------------------------
struct PlBuildIcon {
    const char* shapeFile;  // vendor path, verbatim case as windows.txt uses
    int record;             // planitem.shp record index
};
// The PLBUILD panel's project icon for item index `itemIdx`. CITED for 34 ->
// k34 (shp.md S23.4); nullopt for out-of-domain input (planitem.shp has 40
// records, shp.md S23.3), identity elsewhere per the [inferred] extension.
std::optional<PlBuildIcon> plbuildIcon(int itemIdx);

}  // namespace ascend::ui
