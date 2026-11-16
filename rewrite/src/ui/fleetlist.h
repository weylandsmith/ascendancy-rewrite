// SPDX-License-Identifier: GPL-3.0-or-later

#pragma once
// t407: THE SHIPS (FLEET) LIST SCREEN LAW (D13 "ships screen is EMPTY").
// State 18 = FLEETWND (windows.txt TYPE 17, rect 7,7-632,472) + child
// STATSHIPLST (rect 7,46-632,472; ui-runtime.md §6c). Pure module (no SDL),
// the ui/statuslist.h precedent. Full working log: docs/re/_wip_t407.md F5-F8.
//
//   HEADER LAW [verified static.txt #152 "%s  (%d Ship%s, %d more allowed)",
//   byte-cited this session; the t253 vision read "Chamachies (25 Ships, 12
//   more allowed)" is the witness]. The template + plural pair are ALREADY
//   pinned byte-exact by planetwin (kFmtShips, formatShipHeader, t276) —
//   reuse, never duplicate.
//
//   ROW MEMBERSHIP LAW [port census, labelled]: rows == the campaign's live
//   ship records for the owner. The VENDOR census is every owned ship record
//   (ships.md item 3: 14 named owner-0 records == the FLEET header count
//   exactly; orbiting ships included). The rewrite's entire ship state is
//   ShipInTransit{owner,from,target} (campaign.h:120, the t256c GAP-ROW-16
//   boundary) and expansionPhase() clears arrivals (campaign.cpp:1511) — the
//   model has NO idle-fleet state, so the honest port census is the transit
//   set and an empty list on a quiet turn is the HONEST ZERO, not a stub.
//   NAMED SEAM: vendor orbit rows (#143 "Orbiting %s" leg, fn 0x50d12 case
//   kind-1) cannot be emitted without per-ship orbit state.
//
//   LOCATION LAW [verified fn 0x50d12 disasm, work/r331_disasm.txt; the
//   static #143 getter site 0x50dc5 pins the function identity]:
//     orderKind 1 (orbit): #143 "Orbiting %s" (planet name [rec+0x24]).
//     orderKind 2 (lane):  #146 "In Starlane to %s System\nETA - %d Day%s"
//       with the destination SYSTEM name visibility-gated at [star+0x17]
//       (0x51010..0x5102d, the OQ-026 twin byte) and the plural pair
//       getter(28)""/getter(29)"s" by cmp n,1 (0x51030..0x51041 — the SAME
//       pair t402 cited for the #139 days line).
//     The vendor ETA = round(remaining/speed)+1 (0x50fd4..0x51007, speed =
//     dist/const clamped >=1.0, 0x50e6d..0x50fac) — needs per-ship pos/speed
//     the port does NOT carry (t256c). PORT DEFAULT: ETA 1 day, labelled;
//     the port's transit resolves at the next boundary.
//
//   ROW NAME: the vendor shows the DESIGN name (design screen
//   `Chamachies "Sparrowhawk"`, ui-runtime.md §6c). rec+0x34 is the HULL
//   CLASS word (t379 death witness: 'Medium' at +0x34), NOT the row name —
//   the STATE queue row's "(word 26 law)" is WRONG (#26 == "Selected
//   System", measured). The port has no design model: name = the planitem
//   hull row the campaign actually spends ("Ship", itemId law) [labelled
//   PORT DEFAULT; seam: designRec name ptr, ships.md:191].
//
//   GEOMETRY [MEASURED this session on work/screens/t253/fleet_open_game.png,
//   640x480 NATIVE — numpy colour-band census + native-vision read (D13
//   policy); corroborates the t253 dossier "pages 4 rows for 25 ships via the
//   right-rail scroll pair", arrow glyph CENTRES (620,63)/(620,453)]:
//     rows top y 52, PITCH 106 +- 1 (blue-sphere column bands (52,148)
//     (159,254)(264,360)(370,466)), FOUR visible rows; columns: ship render
//     x~10..150 | NAME green x159 | chevrons x270..323 | spheres x358..382 |
//     LOCATION x389..~500 | arrow boxes x606..635. Arrow BOX extents around
//     the cited centres are [measured-approximate] and named as such.
//     Hit precedence mirrors t405: arrows -> scroll column (inert) -> rows
//     (rows own x 7..605 only).
//   CHROME: honestly-vector is DECISIVE — t391 proved NO 18*.shp exists among
//   the 165 data .shp files and no SHAPEFILE names one (ui-runtime.md t391).

#include <string>
#include <vector>

#include "game/campaign.h"
#include "ui/layout.h"

namespace ascend::ui {

// One row = one ship record index into Campaign::fleet() (the port census).
struct FleetRowKey { int fleetIndex = -1; };

// Membership law: every live ship of `owner`, array order (the vendor sort
// law is UNKNOWN — ships.md correction 2 — so array order is the labelled
// port default, same posture as the t402 planets order seam).
std::vector<FleetRowKey> fleetRows(const ascend::game::Campaign& camp,
                                   int owner);

// The 4-row scroll window (kFleetVisibleRows) over `all` given scroll step
// (clamped 0..max(0, size-4); empty list -> empty).
std::vector<FleetRowKey> fleetWindow(const std::vector<FleetRowKey>& all,
                                     int scroll);

// The vendor #152 header, joined through planetwin's pinned formatShipHeader.
// ships == all.size() (the census), moreAllowed == fleetAllowedFor().
std::string fleetHeaderText(const ascend::game::Campaign& camp, int owner,
                            const std::string& ownerName, int ships);

// Allowance [inferred DEFAULT, n=2 witnesses — _wip_t407 F7: (25,12)@36
// sole-systems and (14,13)@26 both fit total == systems + 1; help shipdes
// states proportionality, not the coefficient]. max(0, systems+1 - ships).
// Strict-close: this is a labelled default, it CLOSES nothing.
int fleetAllowedFor(const ascend::game::Campaign& camp, int owner, int ships);

// The row name (labelled port default: the planitem hull row "Ship"; seam
// named in the header block). Never empty: falls back to "Ship".
std::string fleetShipName(const ascend::game::Campaign& camp);

// The LOCATION string for one transit row: #146 shape with the destination
// star name and the port ETA default (1). Multi-line: the returned string
// carries the REAL newlines the vendor file spells "\n" (loader-interprets
// law, planets-ui.md #149/#150 note). `starName` is passed in (not looked up)
// so the module stays testable without a galaxy.
std::string fleetLaneLocation(const std::string& starName, int etaDays);
// The #143 orbit shape (emitted only if some future model has orbit state;
// pinned as a law for the seam).
std::string fleetOrbitLocation(const std::string& planetName);

// ---- geometry (measured; see header block) --------------------------------
inline constexpr int kFleetVisibleRows = 4;   // t253 dossier + sphere bands
inline constexpr int kFleetRowPitch = 106;    // MEASURED 106 +- 1
inline constexpr int kFleetRowsTop = 52;      // MEASURED (interior 46 + 6)
// Arrow boxes: x-extent MEASURED (blue-pixel bands x 606..635); y-extents
// [approx] around the t253-measured glyph centres (620,63)/(620,453).
inline constexpr Rect kFleetArrowUp{606, 48, 635, 80};
inline constexpr Rect kFleetArrowDown{606, 438, 635, 470};
// Scroll column between the boxes: inert (t405 law shape).
inline constexpr Rect kFleetScrollCol{606, 48, 635, 470};
// Rows own the table left of the scroll column.
inline constexpr int kFleetRowsRight = 605;

enum class FleetHit { None, ArrowUp, ArrowDown, Row };
struct FleetHitResult {
    FleetHit kind = FleetHit::None;
    int row = -1;  // visible-row index (0..kFleetVisibleRows-1) for Row
};
FleetHitResult fleetHitFor(Pt p, int topY);

}  // namespace ascend::ui
