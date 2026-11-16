// SPDX-License-Identifier: GPL-3.0-or-later

#pragma once
// t410: THE SYSTEM VIEW (state 16, the vendor's "System Display") + THE
// SCREEN STACK (the map -> system -> planet chain the owner "never found":
// D13 "haven't found any way to pull up the system view screen, or planet
// view screen"). Pure (no SDL); pins tests/test_sysview_t410.cpp; working
// log docs/re/_wip_t410.md (F1-F4).
//
//   STATE IDENTITY [verified, two independent citations, _wip_t410 F1/F2]:
//   windows.txt: EXACTLY 20 records carry STATE "1 16" — BatModeWnd TYPE 4
//   rect 7,7-465,472 (== the COSMOSWnd rect; CURSORSHAPE 2, HELPINDEX
//   batmode ln1178-1190), BatControlWnd TYPE 19 rect 0,0-0,0 (parent-only,
//   NEVER a hit target — t338), BatListWnd TYPE 10 474,142-632,394
//   SHAPEFRAME 7, and the console buttons tabled verbatim in kSysCtl below.
//   t338 LIVE: SET-STATE fn 0x56e10 entered edx=0x10 on core 0x2bc35c when
//   the galaxy-map Icarus pip (238,282) was clicked; 13 oracle reads
//   state==16 through the battery (docs/re/_wip_t338.md ln49/57-58/80).
//   COSMOSWnd's own STATE list is "4 1 3 7 13" — NO 16 — so in the vendor
//   system view the galaxy rail/children are NOT live (the t369 playtest
//   "NEXTTURN clicks STUCK in the system view" note is now table-cited).
//
//   ENTRY LAW: a single LEFT click on a star pip on the map (t338 measured
//   the entry on a pip click; t293/t296 measured the FLEET-ROW jump into the
//   same view). NOT double-click — no vendor record or witness says double.
//   Empty-space clicks stay silent + inert (t404 MapClick law; t312
//   MEASURED that sprite/empty clicks in the vendor system view select
//   nothing either).
//
//   CHAIN LAW: planet.txt info00 (ln16) verbatim — "There are two ways to
//   access a planet. The first is by entering the System Display, and then
//   selecting the planet by clicking on it"; help batmode page 2 (ln1170-
//   1176) — "You can view a selected planet by clicking it again." Escape
//   unwinds ONE level per press [verified t252 pixel-diff 82k -> 3.4k
//   intel -> species -> galaxy; corroborated t369 system-view]. The full
//   chain is 1 -> 16 -> 17; Esc 17->16, Esc 16->1, Esc 1 = the standing
//   port quit (t388 law).
//
//   CHROME [verified TYPE-100 ln1140-1142]: STATENUMBER 16 SHAPEFILE
//   DATA\16BATTLE.SHP — the system view IS art-backed (unlike FLEET, t391:
//   no 18*.shp exists). The lib has NO full-screen record (dims census
//   work/r1/t410_16battle_dims.py: n=20, largest 173x141) => the blue
//   orbital-grid plane is CODE-DRAWN (the t244 live dossier: "orbital grid:
//   blue wireframe plane, bodies on yellow stalks"). Console faces map
//   SHAPEFRAME -> record IDENTITY (t394 law) with dims parity verified
//   14/16 (_wip_t410 F3); My^Items FR7 (65x28 vs 69x30) and ABANDON FR8
//   (67x29 vs 69x30) are OFF-PARITY — k7/k8/k9 is a size ladder and the
//   mapping of those two is a NAMED SEAM (vector + label, no face).
//
//   ORBITAL LAYOUT [PORT LAW — no vendor per-planet position datum exists
//   in the rewrite model]: centre = viewport centre, ring radius
//   orbitRadius(i) = kOrbitBase + kOrbitPitch*i, angle orbitAngle(i) =
//   i * kGoldenAngle wrapped into [0,2pi) — deterministic, ZERO rng, zero
//   Campaign mutation (seed md5s untouched by construction). Colonised dot
//   == planet index 0 iff the star is owned (t406: the port models ONE
//   PlanetState per star, the per-star colonised world). The vendor organic
//   positions are the same class of seam t408 named for the research tree.
//
//   SHIPS: the port cannot show them — ShipInTransit{owner,from,target} is
//   the ENTIRE ship state (t256c GAP ROW 16) and per-ship selection in the
//   vendor's own system view is the measured-dead OQ-019 hole (t312). The
//   order family (My^Items/Other^Items/W/S/Z/I/Pass/Auto/Repeat) therefore
//   seam-logs, and BatListWnd paints its frame with ZERO rows + the reason.
//   ABANDON (TYPE 31, msg 84) is REFUSED, never wired: t369 live, a misaimed
//   console click opened "Are you sure you want to abandon Vega II?" — this
//   button destroys planets.

#include <optional>
#include <vector>

#include "game/campaign.h"
#include "ui/cam3d.h"
#include "ui/layout.h"
#include "ui/statuslaw.h"

namespace ascend::ui {

// ---- the screen stack (the chain's spine) ---------------------------------
// Bottom level is always the map. push() records a level (truncating deeper
// levels if the screen is already present — reopening a rail screen never
// stacks a duplicate of itself above an open screen). escape() pops ONE
// level and returns false at the bottom (the caller's standing Esc-quit).
class ScreenStack {
  public:
    explicit ScreenStack(int bottom = kScreenMap) : s_{bottom} {
        // The chain is 3 deep; reserve so topRef() can never dangle when
        // the ui loop holds a reference across pushes.
        s_.reserve(8);
    }
    void push(int screen);
    int top() const { return s_.back(); }
    int& topRef() { return s_.back(); }
    bool escape();
    int depth() const { return int(s_.size()); }
    const std::vector<int>& levels() const { return s_; }

  private:
    std::vector<int> s_;
};

// ---- the state-16 console (windows.txt records VERBATIM, file order) ------
// NOTE: None = -1 so the enum VALUE equals the kSysCtl ARRAY INDEX (the
// hit scan casts the array index straight to SysCtl).
enum class SysCtl : int {
    None = -1,
    TogGrid,       // TYPE 25 msg 74  557,403-587,433 FR0
    RotateLeft,    // TYPE 0  msg 50  479,403-493,433 FR1
    RotateRight,   // TYPE 0  msg 51  494,403-509,433 FR2
    ZoomIn,        // TYPE 0  msg 54  518,403-548,418 FR3
    ZoomOut,       // TYPE 0  msg 55  518,419-548,433 FR4
    Recenter,      // TYPE 0  msg 71  596,442-626,472 FR5
    TogElevation,  // TYPE 25 msg 76  596,403-626,433 FR6
    Abandon,       // TYPE 31 msg 84  479,442-548,472 FR8 (REFUSED)
    MyItems,       // TYPE 32 msg 804 479,103-548,133 FR7 (seam, off-parity)
    OtherItems,    // TYPE 0  msg 805 557,103-626,133 FR9
    Repeat,        // TYPE 0  msg 809 531,55-574,85   FR17
    Pass,          // TYPE 0  msg 807 479,55-522,85   FR16
    Auto,          // TYPE 0  msg 808 583,55-626,85   FR18
    W,             // TYPE 0  msg 810 479,103-509,133 FR12
    S,             // TYPE 0  msg 811 518,103-548,133 FR13
    Z,             // TYPE 0  msg 813 557,103-587,133 FR15
    I,             // TYPE 0  msg 812 596,103-626,133 FR14
};

struct SysCtlControl {
    const char* name;  // windows.txt NAME verbatim
    Rect rect;         // verbatim
    int sendMessage;   // verbatim SENDMESSAGE
    int shapeFrame;    // verbatim SHAPEFRAME (-1 = none)
};
// File order of the state-16 records (_wip_t410 F1 census). Hit law =
// LAST MATCH WINS (t264): W/S/Z/I (later records) beat the My^Items span
// they sit inside, exactly as the vendor table orders them.
extern const SysCtlControl kSysCtl[17];
inline constexpr int kSysCtlCount = 17;

// The console control owning p (file-order scan, last match wins); None
// outside every rect.
SysCtl sysCtlFor(Pt p);

// The 16battle.shp record for a control under the SHAPEFRAME->record
// IDENTITY law (t394 dims parity verified 14/16, _wip_t410 F3). -1 for the
// two off-parity named seams (MyItems FR7, Abandon FR8) and None.
int sysCtlShapeRecord(SysCtl c);

// ---- orbital layout (PORT law; header cites the witnesses) ----------------
inline constexpr double kGoldenAngle = 2.399963229728653;  // pi*(3-sqrt(5))
inline constexpr double kOrbitBase = 60.0;
inline constexpr double kOrbitPitch = 34.0;
double orbitAngle(int i);   // wrapped into [0, 2pi)
double orbitRadius(int i);  // px in field space

struct OrbitDot {
    int planetIndex = -1;
    Pt pos{};
    int radius = 0;
    bool colonised = false;
    int owner = -1;  // Campaign::starOwner semantics (-1 neutral, 0 player)
};

// One dot per star-record planet name (the vendor view shows every body;
// the t244 dossier: "planet-icons row selects planet"). `cam` is a
// Camera3d whose bounds are kBatModeWnd — the same vendor pinhole law as
// the galaxy field (cam3d.h), re-centred on the system.
std::vector<OrbitDot> systemOrbits(const ascend::game::Campaign& camp,
                                   int star, const Camera3d& cam);

// Nearest dot within `radius` px of p, or -1 (the planet.txt info00 click).
int hitOrbitDot(const std::vector<OrbitDot>& dots, Pt p, int radius = 9);

// ---- cited state-16 chrome rects (windows.txt, verbatim) ------------------
inline constexpr Rect kBatModeWnd{7, 7, 465, 472};      // TYPE 4 ln1178
inline constexpr Rect kBatControlWnd{0, 0, 0, 0};       // TYPE 19 (never hit)
inline constexpr Rect kBatListWnd{474, 142, 632, 394};  // TYPE 10 FR7

}  // namespace ascend::ui
