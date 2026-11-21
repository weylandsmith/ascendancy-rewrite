// SPDX-License-Identifier: GPL-3.0-or-later

#pragma once
// t428: THE PLANET-SCREEN STRIP LAW (state 17, the five TYPE-29 panels).
// Pure (no SDL); pins tests/test_planetstrip_t428.cpp; working notes
// docs/re/_wip_t428.md F5/F9.
//
//   PANEL ART PROVENANCE [verified byte-level this iteration + windows.txt]:
// planres.shp / planind.shp / planpro.shp each hold EXACTLY 21 records, all
// 107x99 (tools/shp_pngdump census on the extracted libs; rec0 = navy mottle
// = the 0-level panel). The windows.txt TYPE-29 rects PLRES 7,7-114,106 /
// PLIND 123,7-230,106 / PLPRO 239,7-346,106 are 108x100 — the records fill
// the rects at the rect origin, and 21 == the clamp0..20 domain of the
// gauge-selector law (layout.h gaugeSelector/prosSelector, planets-ui.md
// S3). The switch dispatch binds case key 0->PLRES 1->PLIND 2->PLPRO
// (planets-ui.md S2, table verified live), so panel i takes record
// selector[i] of lib i.
//
//   WITNESS [measured 1:1, work/r1/screens/t254/02_planet_detail.png screen
// origin (80,100) in its 800x600 frame]: the three gauge panels show the
// photographic panel art (starburst / city / alien-plant) exactly where the
// rects say; PLPOP x355..459 y5..109 shows the 10-per-row pitch-10 pop
// sprites (t254 S4 census [verified]); PLBUILD x463..632 shows the project
// NAME text top-centre plus a planitem.shp k[item] thumbnail below it.
//
//   POP GRID = poppanel.h t263 law verbatim (17np k1 busy / k2 free / k3
// empty, 10/row pitch 0x0a) anchored at the PLPOP rect origin.
//
//   PROJECT PANEL: pendingItem >= 0 -> planitem record index == item
// (1:1 pixel-match law shp.md S23.4, same as the t418 grid structures);
// pendingItem < 0 -> static.txt #141 "No Project" text only (witness A).

#include <string>
#include <vector>

#include "ui/layout.h"  // Rect
#include "ui/poppanel.h"  // PopCell

namespace ascend::game { class Campaign; }

namespace ascend::ui {

// The three gauge libraries in panel order (extracted/ascend01/data/).
inline constexpr const char* kStripGaugeLibs[3] = {
    "planres.shp", "planind.shp", "planpro.shp"};

// Selector domain of every gauge panel (record count AND the S3 clamp
// bound): 21 records, indices 0..20.
inline constexpr int kStripGaugeRecords = 21;

// ---- t428d FIELD STARFIELD (17np record 4) --------------------------------
// THE FIELD BLIT LAW [verified work/t198_planwin.asm 0x3b9c0..0x3b9df]:
// the PLSQUARE paint body's blit-1 pushes push $0x73 (y=115), push $0x7
// (x=7), push $0x4 (SELECTOR = RECORD 4, an IMMEDIATE — t428 F4's
// "selector = SENDMESSAGE" reading conflated the gate test at 0x3b9b1 with
// the arg pushes), payload = FUN_0x1fc34(cache 0x9f10c, slot WORD[0x6fd9c]
// = 44 = 17np.shp, shp.md S23.1), then call FUN_0x5caac (S12.1 arg map:
// pushes are reverse order — law calibrated against the t428c measured
// registration of k4 at exactly screen (7,115), 158/269 tol-8, shuffle
// control 6..12; scripts/t428c_field_register.py). k4 = 625x357, 99.88%
// idx 0, 269 navy/grey specks (starfield). It paints UNDER the strip
// panels and the lattice (the vendor witness shows 101/111 anchor
// mismatches as BRIGHT overpaint px).
inline constexpr int kFieldRecord = 4;
inline constexpr Pt kFieldBlitOrigin{7, 115};
inline constexpr int kFieldRecordW = 626;  // tA1 bbox (0,0,625,357)
inline constexpr int kFieldRecordH = 358;

// The PLPOP paint origin == the windows.txt rect origin (355,7) [verified
// ln1587 block; t263 panel-geometry note].
inline constexpr Pt kPopGridOrigin{355, 7};

// One panel's paint entry.
struct GaugePanel {
    int lib;   // index into kStripGaugeLibs (0/1/2)
    int rec;   // record index 0..20 (the compressed level selector)
    Rect rect; // windows.txt rect (verbatim from kPlanetPanels)
};

// The full strip plan for one owned planet.
struct StripPlan {
    GaugePanel gauges[3];
    std::vector<PopCell> popCells;  // poppanel law, origin kPopGridOrigin
    int projectItem = -1;           // planitem record index; -1 = "No Project"
};

// The strip plan for one planet: gauge selectors = the t276 wiring
// (gaugeSelector on the RES/IND channel words, prosSelector identity —
// planets-ui.md S3), pop grid = popPanelFor at kPopGridOrigin, project =
// pendingItemFor. Out-of-domain star: zeroed plan (all rec 0, no cells,
// no project).
StripPlan stripPlanFor(const ascend::game::Campaign& camp, int star);

// Library conformance gate (poppanel popSlotLibraryConforms precedent):
// true iff `path` parses with EXACTLY kStripGaugeRecords (21) records and
// EVERY record is 107x99 (the rect-fill dims census, F9). *err describes
// the first violation.
bool stripGaugeLibraryConforms(const std::string& path, std::string* err);

// t428d FIELD-library gate (stripGaugeLibraryConforms precedent): true iff
// `path` is the 17np pop/field library per the shp.md S23.2 census — magic
// ok, EXACTLY 9 records, and record kFieldRecord (4) is kFieldRecordW x
// kFieldRecordH (625x357, the starfield dims the t428c registration
// measured). *err describes the first violation.
bool fieldLibraryConforms(const std::string& path, std::string* err);

}  // namespace ascend::ui
