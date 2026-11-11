// SPDX-License-Identifier: GPL-3.0-or-later

#pragma once
// POPULATION PANEL (PLPOP) visualization law — t263.
//
// The vendor paints the planet screen's population panel as a CAPACITY-SIZED
// array of slot icons, ten per row on a 10 px pitch. Everything here is cited:
//
//   LOOP LAW   [verified 0x3ce39..0x3cef8, docs/re/planets-ui.md S4; asm
//               re-read this session from work/t198_planwin.asm]:
//     for i = 0..cap(+0x4a)-1:                      ; 0x3ce81 exit jge
//       SEL(i) = 1 + [i >= used(+0x4c)] + [i >= pop(+0x42)]
//       blit(cache 0x9f10c, slot [0x6fd9c], SEL, x=EDI, y=EBP)
//       EDI += 0x0a;  if (i % 10 == 9) { EDI = 0; EBP += 0x0a; }
//   so cell i sits at ((i%10)*10, (i/10)*10) relative to the panel origin,
//   and NO cell is painted at i >= cap (the branch t254 saw live on Vega IV:
//   cap 39 -> cell (row 3, col 9) never painted, docs/re/_wip_t254.md S7).
//
//   LIBRARY IDENTITY [verified live-RAM t254, docs/re/shp.md S23]: the slot
//   global u16[DAT 0x6fd9c] = 44 (bank-t251-live1255/41.sav) resolves cache
//   slot 44 to a verbatim copy of extracted/ascend01/data/17np.shp; entry #44
//   (0-based, blanks skipped) of extracted/ascend00/gwshare.txt is 17np.shp
//   (control: entry #41 = 14intel.shp, matching live cache slot 41).
//
//   RECORD/ROLE LAW [verified record-level t254 (vision oracle + player
//   testimony S19 corroboration) + palette census this session
//   (docs/re/_wip_t263.md S3)]: the selector indexes the library DIRECTLY
//   (record index == selector; the runtime selector table maps sel 0..8 ->
//   records 0..8, 9/9), and
//     SEL 1 -> k1 9x9  sideways humanoid, red body + BLUE TOOL = BUSY pop
//     SEL 2 -> k2 7x9  front-facing YELLOW figure (zero blue px) = FREE pop
//     SEL 3 -> k3 8x8  hollow ring (interior never painted) = EMPTY slot
//   pins: poppanel_17np_library_census_t263 binds these byte-level facts to
//   the selector values, so swapping the k1/k2 assignment fails the census.
//
//   PANEL GEOMETRY [verified]: windows.txt:1587 PLPOP X0 355 Y0 7 X1 454
//   Y1 106 -> 100x100 px; at the 10 px pitch the panel holds exactly 10 rows,
//   and storedCapFor clamps cap to 0..100 (campaign.cpp:811, income-law.md
//   S10 t33) — the clamp bound equals the panel capacity, so the paint can
//   never overflow the panel.
//
// Drawing the decoded sprites on screen stays blocked on OQ-005 scope
// decisions (ui-runtime.md §2: no vendor shapes drawn yet); this module is
// the pure selection/geometry law (t199 precedent: gaugeSelector/popBands),
// ready for the blit layer.

#include <string>
#include <vector>

#include "ui/layout.h"  // Pt, Rect

namespace ascend::game { class Campaign; }

namespace ascend::ui {

// The panel rect exactly as windows.txt:1587..1594 states it (inclusive).
inline constexpr Rect kPlPopRect{355, 7, 454, 106};

// Library + grid constants (citations in the header block above).
inline constexpr int kPopSlotCacheSlot = 44;   // == gwshare entry #44 == [0x6fd9c]
inline constexpr int kPopSlotsPerRow = 10;     // idiv-10 / cmp 9 law (0x3cee5)
inline constexpr int kPopSlotPitch = 0x0a;     // EDI/EBP += 0x0a (0x3ceed/6)
inline constexpr int kPopPanelMaxSlots = 100;  // 10 rows x 10 (panel capacity)

// Slot role per the band law (values are the vendor selector words).
enum class PopSlotRole {
    Busy = 1,  // working population (i < used)         -> k1
    Free = 2,  // population not working (used <= i < pop) -> k2
    Empty = 3  // beyond population (pop <= i < cap)    -> k3
};

// Selector -> 17np record index: IDENTITY (t254 selector-table law), defined
// only for 1..3; -1 otherwise (the band formula never emits other values).
int popSlotRecord(int selector);

// Selector -> role. Out-of-range selectors map to Empty (draw nothing
// meaningful rather than mislabel; unreachable from popBands output).
PopSlotRole popSlotRoleOf(int selector);

// One painted slot: which selector/record and WHERE (panel-local pixels,
// origin = top-left of the paint grid).
struct PopCell {
    int selector;     // 1..3
    int record;       // 17np record index (== selector)
    Pt pos;           // ((i%10)*10, (i/10)*10) + origin
};

// The paint plan for one planet: cells in vendor iteration order (i = 0..n-1),
// n == bands.size() == cap. `origin` is the grid anchor: the vendor loop runs
// EDI=EBP=0 before the per-case setup call at 0x5e940, so its coordinates are
// widget-relative [inferred — _wip_t263.md S4]; the default (0,0) is that
// panel-local frame. The t254 live census placed the grid inside the PLPOP
// panel region consistent with this law.
std::vector<PopCell> popPanelCells(const std::vector<int>& bands,
                                   Pt origin = {0, 0});

// Rows the vendor loop paints for a cap: ceil(cap/10) (the row counter only
// advances after a cell at i%10==9; negative/zero cap paints nothing -> 0).
int popPanelRows(int cap);

// Convenience: bands for a campaign planet (Campaign::popBandsFor, t199) fed
// through the layout law.
std::vector<PopCell> popPanelFor(const ascend::game::Campaign& camp, int star,
                                 Pt origin = {0, 0});

// Library conformance gate for whoever draws: true iff `path` is the pop-slot
// library per the t254 census — magic ok, EXACTLY 9 records, and k1/k2/k3
// dims 9x9 / 7x9 / 8x8 (shp.md S23.2/S23.3; the 10 px pitch excludes every
// other candidate library). *err describes the first violation.
bool popSlotLibraryConforms(const std::string& path, std::string* err);

}  // namespace ascend::ui
