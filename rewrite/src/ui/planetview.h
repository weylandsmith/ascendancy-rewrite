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

// ---- t418b SURFACE TILE GRID (laws docs/re/_wip_t418.md F1/F2/F3) ---------
//
//   F1 GRID LAW [verified verbatim FUN_000395c4 + FUN_0003965c]: 15 row-
//   slots per size class; valid cols B[size][row] <= col < B+C (B = grid B
//   rowOffset @0x7445c, C = grid C rowWidth @0x744a8, planitem.txt tokens
//   45..194 via TerrainTables); cell = cumWidth(size,row) + col - B.
//   Inverse (0x396af..0x396c2): cell < surfaceCells required, walks rows
//   while cum+B+C <= target; col = target - cum + B[size][row].
//
//   F2 ISOMETRIC LAW [verified immediates, paint body 0x3b96c]: center =
//   origin + col*(34,17) + row*(17,-34); x-cursor 110 +17/row, y 410 -34/row
//   => origin at (row,col)=(0,0) is (110,410). Tile diamond 68x34 (x±0x22,
//   y..y+0x22 mid y+0x11); hit-test |dx|/34 + |dy|/17 <= 1. The lattice
//   steps ARE the diamond-tiling half-steps, so the four probe neighbours
//   (row±1,col),(row,col±1) are the four visual edge-neighbours.
//
//   F3 PLACEMENT LAW [verified raw asm 0x38444..0x386fc, VETO chain: EDI is
//   reset to 0 at 0x38444 for the placement region and the return 0x38706
//   hands back -1 (legal) only when EDI != 0 — the region's zeroing arms are
//   the vetoes; the two `mov edi,-1` legs (0x3848e bit0/race-state, 0x384d6
//   occupied/demolish/bit2) are RE-GRANT arms whose literal polarity is
//   AMBIGUOUS and NOT modelled. The veto reading is the one corroborated by
//   MEASUREMENT: r1_built_cell_law.py 0/362 active Factories without an
//   active neighbour (rule G must be able to refuse) and t341 S1 item 0
//   RESERVED on an empty cell (a fresh empty surface placement must be
//   legal) — docs/re/_wip_tPLB1.md F7.
//     - 0x3843a cell >= +0x1a (slot-array cap) exits early; 0x385b7 cell >=
//       +0x18 (surfaceCells) skips adjacency — the orbital ring is NOT
//       asked (the port has no ring model: ring cells return None).
//     - F10 CORRECTION (docs/re/_wip_tPLB1.md): 0x38444 `xor edi,edi`
//       resets EDI at the placement-region entry — the region is a GRANT
//       ACCUMULATOR (mov edi,-1 legs grant, xor legs veto). Rule B
//       (0x38493) reads the CELL-CLASS byte (byte0 != 0 grants), NOT
//       occupancy; it is always granted for observed play (t43 barren-build
//       census 263/892 == terrain rate; the picker filters by this
//       checker). THERE IS NO OCCUPIED VETO — occupancy (word+2 bit0) is
//       read only by own-active 0x385ee (a skip of adjacency) and rules
//       E/F. t43's "built items land on EMPTY cells" is a PICKER law; the
//       port's completion re-picks the cell, so an occupied click cannot
//       overwrite.
//     - 0x38554 item 36 Terraforming vetoes unless byte0==0 (barren) &&
//       byte1==0xff (empty) && surface (ring class 1 vetoes).
//     - XOR law 0x384db, ONLY for item < 31 (0x384e0 cmp 0x1e ja):
//       (cell < +0x18) != (item < ds:0x73e3c == 22) REFUSES — surface items
//       need a surface cell, orbital items (22..30) need the ring; 31..38
//       exempt. Raw 0x38513/0x38515: `cmp eax,ecx; je` SKIPS the veto, so
//       EQUAL booleans pass and DIFFERING booleans zero EDI.
//     - ROCK leg 0x38519: veto iff (byte0 bit3) != (item == 38) — Xeno Dig
//       legal ONLY ON ROCK (dig arm 0x38546 sete), normal items refuse on
//       rock (income-law.md S4 agrees).
//     - ADJACENCY 0x385b7..0x386fc: SKIPPED when the cell's own slot is
//       ACTIVE (0x385ee jne), item == 5 Colony Base (0x385f6) or item == 35
//       Automation (0x385ff cmp dl,0x23 — NOT 38; the t418b header had this
//       wrong). Else FOUR probes via 0x395c4 — (row+1,col),(row-1,col),
//       (row,col-1),(row,col+1): an existing neighbour with word+2 bit0 set
//       exits the block via `jne 0x386fe` WITHOUT executing 0x386fc
//       `xor edi,edi` => ACTIVE neighbour = LEGAL; ALL FOUR inactive/absent
//       => 0x386fc zeroes EDI => REFUSE. t43 static law
//       (r1_built_cell_law.py header "BUILT ITEMS MUST ADJOIN AN ACTIVE
//       ITEM") + vendor help planet.txt info02 ln54-56 corroborate. The
//       t418b port had this INVERTED (tPL-B1 F5); tPL-B1b flips it.

// Cell index for (row, col) on a size-class grid; -1 outside the valid cols
// (0x395dc..0x39647 verbatim: row in [0,15), col >= B and col < B+C).
int gridCellFor(const ascend::game::TerrainTables& tt, int size, int row,
                int col);

// Inverse (FUN_0003965c): (row,col) for a terrain cell; false when the cell
// is not a surface cell (cell < 0 || cell >= surfaceCells — the vendor's
// 0xffffffff leg).
bool gridRowCol(const ascend::game::TerrainTables& tt, int size,
                int surfaceCells, int cell, int* row, int* col);

// F2 screen position of a tile centre on the planet-view field (col
// ABSOLUTE incl. B). Pure arithmetic; the ui painter uses it verbatim.
// tPL-V1: centre = (410 + 34*(col-row), 127 + 17*(col+row)) — an EXACT
// edge-to-edge diamond tiling (witness 100% vs the old transposed law 26%).
Pt tileCenter(int size, int row, int col);

// tPL-V1 F2: the vendor tile-EDGE game.pal index for a slot class byte
// (0->0 black, 2->117 red, 3->146 green, 4->255 blue, else 12 white —
// EXACT-equality compares 0x3bbd6..0x3bc52; a rock-flagged byte takes the
// white default). Converted colours per the t398 palette law.
int tileEdgePaletteIndex(int cellClass);

// F2 hit-test: the tile whose diamond contains p, or -1. Diamonds tile
// edge-to-edge (touching at vertices), so at most one strict hit; boundary
// ties resolve to the nearest centre [port tie law, named seam].
int tileHitFor(const ascend::game::TerrainTables& tt, int size,
               int surfaceCells, Pt p);

// Why a tile-click order would NOT land (the checker chain above; the
// projectOrderable gates are the queue law). None == legal (including every
// skip leg). tPL-B1b: renamed from t418b's OrderCellBlock{None,
// ActiveNeighbour}, which encoded the INVERTED polarity (F5).
enum class PlacementBlock { None, SurfaceVsRing, RockMismatch,
                            TerraformSite, NoActiveNeighbour };
PlacementBlock placementBlock(const ascend::game::Campaign& camp, int star,
                              int item, int cell);

// The FLAG-bit1 leg of the no-cell click path (0x3b3f5/0x3b402 + cmd2 skip
// 0x38a5a): true iff the item orders WITHOUT a cell.
bool ordersWithoutCell(const ascend::game::Campaign& camp, int item);

// ---- tPL-V2 ORBITAL SLOT LAW (docs/re/_wip_tPLV2.md F1..F5) ---------------
// The paint body FUN_0003b96c's SECOND loop (0x3c33a..0x3c4d9) paints the
// ORBITAL slots — the ten ring cells [surfaceCells, +10) — as a flat
// two-column x five-row grid LEFT of the sphere (NOT isometric, D26):
//   seed 0x3c33a/0x3c33f: X0 = 13, Y0 = 119; Y += 70 per slot (0x3c47e);
//   on (idx - surface)%5 == 4 (0x3c470 idiv 5): Y := 119, X += 70.
// => slot k (k = cell - surfaceCells, 0..9) origin (top-left):
//      X = 13 + 70*(k/5),  Y = 119 + 70*(k%5)      [exact immediates]
// Witness (work/r1/screens/t254/02_planet_detail.png, origin (80,100) per
// t428 F9): the two occupied art blobs measure screen x83..151 y127..183
// (col1 row0 box (83,119)) and x14..80 y404..468 (col0 row4 box (13,399))
// — both land exactly inside the predicted 70x70 boxes; the eight empty
// slots are starfield (vendor paints NOTHING for an empty slot at rest).
constexpr int kOrbitalSlots = 10;  // +0x1a == +0x18 + 10 (OQ-014 census)
constexpr int kOrbitalPitch = 70;  // 0x46: the slot pitch immediates
Pt orbitalSlotOrigin(int k);

// Hover/click cell for a field point (FUN_0003a880 orbital leg, verbatim):
//   if (x < 0xe || x > 0x98 || y < 0x78 || y > 0x1d4) -> NOT orbital;
//   else cell = surface + ((x-0xd)/0x46)*5 + ((y-0x77)/0x46).
// Returns the ring cell index (surfaceCells + k) or -1.
int orbitalSlotHitFor(int surfaceCells, Pt p);

// The HOVER OUTLINE law (0x3c546..0x3c5d7): the vendor paints a 69x69 box
// outline (call 0x2fe04, rect (X,Y)..(X+0x46), colour immediate 0x96 ==
// pal 150) on the hovered slot iff the slot is EMPTY (cell item byte
// 0xff), the hover word +0xac names it, and NO pick is pending (+0xab ==
// 0xff). That is D26's "thin greyish box outline should appear".
// `slot` is the k the paint loop is drawing: the vendor tests EACH slot
// against +0xac (per-slot compare), so only the hovered box outlines.
bool orbitalHoverOutline(const ascend::game::Campaign& camp, int star,
                         int slot, Pt p, bool pickPending);

// The active item occupying ring cell (surfaceCells + k), or -1.
int orbitalSlotItem(const ascend::game::Campaign& camp, int star, int k);

}  // namespace ascend::ui
