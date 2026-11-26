// SPDX-License-Identifier: GPL-3.0-or-later

#pragma once
// t428: THE PLANET-SCREEN STRIP LAW (state 17, the five TYPE-29 panels).
// Pure (no SDL); pins tests/test_planetstrip_t428.cpp; working notes
// docs/re/_wip_t428.md F5/F9.
//
//   PANEL ART PROVENANCE [verified byte-level t428 + tPF-5 bbox census
// scripts/tPF5_strip_bbox.py + windows.txt]:
// planres.shp / planind.shp / planpro.shp each hold EXACTLY 21 records with
// bbox R=107, B=99 (so WIDTH=108 and the content's bottom-right pins to the
// windows.txt TYPE-29 rects PLRES 7,7-114,106 / PLIND 123,7-230,106 /
// PLPRO 239,7-346,106, all 108x100). planres and planpro are FULL-BLEED
// (L=0,T=0, 108x100 on all 21); planind is NOT: its records carry T in
// {23,20,11,5,1} by gauge level (H 77/80/89/95/99), i.e. the industry art is
// BOTTOM-anchored and must be blitted at rect origin + (L,T) per the vendor
// blit law (FUN_0005caac 0x5cb61/0x5cb6a add the bbox corner to screen x/y) —
// see tPF-5 in docs/re/_wip_tPF5.md and the call site in ui.cpp. rec0 = navy
// mottle = the 0-level panel. 21 == the clamp0..20 domain of the
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

// THE STRIP BLIT PLACEMENT LAW [verified raw bytes work/ascend_restored.bin
// FUN_0005caac 0x5cb5b..0x5cb7c]: the blit resolves the record entry
// (payload + [payload+8+8*sel]) and then ADDS the entry's signed bbox corner
// to the pushed screen x/y (dest_x = [entry+8] + x @0x5cb61, dest_y =
// [entry+0xc] + y @0x5cb6a; right/bottom likewise from +0x10/+0x14). The
// caller's x/y is therefore an ANCHOR, not a top-left. A caller that pushes a
// windows.txt rect ORIGIN (the strip panels do) must add (L,T) itself.
//
// This matters because planind's records are bottom-anchored inside the 108x100
// rect (bbox (0,T,107,99), T in {23,20,11,5,1}); dropping T painted the
// industry gauge T px too high with a band below it -- D28 item 10 verbatim.
// planres/planpro carry (0,0), so the term is a no-op there.
Pt stripGaugeBlitPos(const Rect& rect, int32_t recLeft, int32_t recTop);

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
// EVERY record has WIDTH 108 (bbox R=107). HEIGHT IS DELIBERATELY NOT AN
// IDENTITY TERM: planind's 21 records carry H in {77,80,89,95,99} (bottom-
// anchored art, tPF-5) and rejecting them would be a fabricated law. *err
// describes the first violation.
bool stripGaugeLibraryConforms(const std::string& path, std::string* err);

// t428d FIELD-library gate (stripGaugeLibraryConforms precedent): true iff
// `path` is the 17np pop/field library per the shp.md S23.2 census — magic
// ok, EXACTLY 9 records, and record kFieldRecord (4) is kFieldRecordW x
// kFieldRecordH (625x357, the starfield dims the t428c registration
// measured). *err describes the first violation.
bool fieldLibraryConforms(const std::string& path, std::string* err);

}  // namespace ascend::ui
