// SPDX-License-Identifier: GPL-3.0-or-later

#pragma once
// t406: THE PLANET VIEW (state 17 PLANETALLOC) + PROJECT-SET LAW. The owner's
// D13 complaints "can't click a planet" and "can't set a project on my home
// planet". Pure (no SDL), the statuslist.h/planetwin.h precedent; pins
// tests/test_planetview_t406.cpp; working notes docs/re/_wip_t406.md.
//
//   OPEN PATH [verified, extracted/ascend00/planet.txt vendor tutorial]:
//   info00 "There are two ways to access a planet. The first is by entering
//   the System Display, and then selecting the planet by clicking on it";
//   info05 (the Planets screen): "the ability to click on either the planet
//   or the star to go directly to them". So a STATUS LIST row click opens
//   state 17 for that planet — the route implemented here (the System-Display
//   route is queue row t410). No rail button targets 17 (windows.txt STATE
//   census, t405 F1): the ONLY openers are these clicks.
//
//   WINDOW COMPOSITION [verified verbatim windows.txt, tabled t276 in
//   ui/planetwin.h]: PLANETALLOC TYPE 7 ln1486 0,0-639,479 msg 3 HELPINDEX
//   planal; children STATE "1 17": PLANLIST TYPE 10 ln1504 120,120-520,420
//   SHAPEFRAME 7 msg 0 (the PROJECT LIST — opened by the PLBUILD panel per
//   planet.txt info04); PLSQUARE TYPE 14 ln1520 152,120-487,375 msg 1 (the
//   SURFACE GRID: "A planet's surface is divided into individual squares on
//   which structures may be built", planet.txt info02 — NOT painted here,
//   NAMED SEAM); five TYPE-29 panels PLRES/PLIND/PLPRO/PLPOP/PLBUILD (the
//   gauge strip, t276). help.txt: PLBUILD == "Project Display" (ln1622-8),
//   PLANETALLOC == "Planet Display" (ln1501-7).
//
//   PROJECT-SET LAW [verified fn 0x38840 cmd0 leg, work/r331_disasm.txt
//   verbatim; the t341 writer census pins this fn as the SOLE store of the
//   queue pair +0x52/+0x54; UI callers 0x3b349/0x3b411/0x3b482/0x3c9fc/
//   0x3ca44/0x3daa9 inside planet-window command fn 0x3aa0a (t342 S2.7)]:
//     reject (silent: recalc + return, 0x38b92) unless ALL of
//       (1) queue empty:  BYTE [rec+0x54] == 0xff            (0x388e2)
//       (2) item < 39:    cmp BYTE item, 0x27; jae reject    (0x388ec)
//       (3) free pop:     WORD[+0x42] - WORD[+0x4c] >= UPOP  (0x388f7..0x38922)
//     then: +0x54 := item (0x38b26); +0x52 := cell unless flags&2 item
//     (0x38af5/0x38b0c, t341 S1 class); the ACC word +0x50 is NOT touched
//     (resets live at 0x39290 completion / 0x37f8d worldgen / 0x3a153
//     demolish). The CELL word the UI passes feeds the checker leg only —
//     COMPLETION always routes through the picker (t43 law, campaign.cpp
//     buildPhase comment), so the port's order sets the ITEM and the picker
//     keeps assigning the cell at completion. planet.txt info04 describes
//     the vendor two-step ("choose it from the list, and then click on the
//     colored square"): the rewrite has no surface-grid painter, so the
//     click-a-cell step is a NAMED SEAM and the order lands item-only.
//     [honest negative] A fourth leg at 0x3892a compares
//     (item >= WORD ds:0x73e3c) against (cell >= WORD[rec+0x18]); its
//     semantics are UNRESOLVED (ds:0x73e3c sits immediately below the
//     item-table base 0x73e40). The port passes no cell, so the leg is
//     never exercised here — recorded, not modelled.
//
//   PROJECT LIST MEMBERSHIP: the vendor list is "a list of structures that
//   can be built ... As your scientists make discoveries, new structures
//   will become available" (planet.txt info04) — i.e. the REQUIRES-gated
//   partition of the planitem table (income-law.md S4 requiresAvailable,
//   CLOSED OQ-014). The item<39 gate (2) is the table-domain leg (planitem
//   has 40 rows, shp.md S23.3 domain; item 39 excluded by 0x388ec).
//
//   UPOP GATE (3) is the SAME predicate the status row's "   (No Free
//   Population)" suffix reports (0x508da cmp +0x42/+0x4c, statuslist.h) —
//   the row tells the player why ordering would fail before they click.

#include <optional>
#include <string>
#include <vector>

#include "game/campaign.h"
#include "ui/layout.h"

namespace ascend::ui {

// ---- the state-17 detail readout for one planet ---------------------------
struct PlanetView {
    std::string title;      // statusLine1(name, size, type) — the SAME
                            // assembly the list row uses (0x50647 law)
    int pop = 0;            // +0x42 analog (int, the stored counter)
    int used = 0;           // +0x4c analog
    int cap = 0;            // +0x4a analog (storedCapFor)
    int res = 0, ind = 0, pros = 0;  // gauge SELECTORS (t276 wiring)
    int pendingItem = -1;   // +0x54 analog (-1 == 0xff "no project")
    int days = -1;          // statusDays(cost, acc, ind); -1 == 0xffff
    bool noProject = true;
    bool noFreePopulation = false;  // pop == used (the 0x508da predicate)
};
// The readout for one owned planet; `name` is the planet-name string the
// caller resolved (the list keys rows by (star, planetIndex)). Out-of-domain
// star: all-zero view.
PlanetView planetViewFor(const ascend::game::Campaign& camp, int star,
                         const std::string& name);

// ---- the PROJECT LIST (PLBUILD -> PLANLIST) --------------------------------
struct ProjectOption { int item; std::string name; int cost; };
// Buildable options for one planet, planitem TABLE ORDER: rows with
// requiresAvailable(reqByte) (income-law S4) and item < 39 (0x388ec).
// Does NOT pre-filter the free-pop gate (3) — the vendor LIST shows them;
// the ORDER rejects them (and the row's suffix already says why).
std::vector<ProjectOption> projectOptionsFor(
    const ascend::game::Campaign& camp, int star);

// The cmd0 gate predicate (1)+(2)+(3) above, evaluated against campaign
// state. Pure; the caller's orderProject applies the SAME law — exposed so
// the UI can grey/report without duplicating the arithmetic.
bool projectOrderable(const ascend::game::Campaign& camp, int star, int item);

// ---- the project-list window (PLANLIST rect, verbatim ln1504) --------------
inline constexpr Rect kProjectListRect{120, 120, 520, 420};
inline constexpr int kProjectRowPitch = 24;  // PORT default (no vendor row
                                             // pitch witness; named seam)
inline constexpr int kProjectVisibleRows = 12;  // (420-120)/24 rounded down
// Which option row owns point p within the list (0-based over the visible
// window starting at `first`); nullopt outside the rect/rows.
std::optional<int> projectRowFor(Pt p, int first);

}  // namespace ascend::ui
