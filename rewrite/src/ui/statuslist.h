// SPDX-License-Identifier: GPL-3.0-or-later

#pragma once
// t402: THE PLANETS LIST SCREEN LAW (D11 "the planets list screen is wrong
// and unusable"). State 10 = STATUSWND (windows.txt ln1019, rect 7,7-632,472)
// + child STATPLANLST (ln1035, TYPE 10, 7,46-632,472). This module is the
// ROW-ASSEMBLY law — pure (no SDL), the ui::planetwin precedent. Full working
// notes: docs/re/_wip_t402.md; law block banked docs/re/planets-ui.md.
//
//   HEADER LAW [verified, planetwin.h + selfplay.md t248/t249]: static.txt
//   #151 "%s  (%d Planet%s Occupied, %d System%s Controlled)"; the PLANETS
//   number is the SCREEN-OPEN SNAPSHOT count == count(player-owned planets)
//   at open (t249 live: 80/80 EXACT), the SYSTEMS number the sole-owner loop
//   (FUN_00051684; 36 @t1254 EXACT).
//
//   LIST MEMBERSHIP LAW [verified t249 + the same-turn list walk
//   scripts/r402_listobj_census.py on 60.sav]: the list holds EXACTLY the
//   planets whose owner == the player race, refilled on every open; the
//   vendor's own entry order at t1086 was {Oslo II, Vega IV, Vega V,
//   Vega III, Vega I, Vega II, Icarus IV, ...} (star-cluster grouping,
//   not name-sorted) — ORDER SOURCE UNRESOLVED [named seam; the port sorts
//   by (star id, planet index), a labelled default].
//
//   ROW ROW-ASSEMBLY LAW [verified disasm 0x50647..0x5091f, the status.cpp
//   row builder; sites located by scripts/t402_status_getters.py — getter
//   args are MOV EAX,imm32 + CALL 0x21a20 (regparm), NOT push]:
//     LINE 1 = planet name + " " + sprintf(static.txt #136 "(%s %s Planet)",
//              SIZE_WORDS[WORD[PL+0x14]], TYPE_WORDS[WORD[PL+0x16]])
//       SIZE_WORDS = 5-slot table ln ds:0x7452c, TYPE_WORDS = 11-slot table
//       ln ds:0x74540; both tables located by CONTENT anchor in a banked
//       save (r402_sizetype_census.py PASS): the strings are static.txt
//       #41-45 Tiny/Small/Medium/Large/Enormous and #46-56
//       Husk/Primordial/Congenial/Eden/Mineral/Supermineral/Chapel/
//       Cathedral/Special/Tycoon/Cornucopia IN FILE ORDER.
//       The rewrite's model feeds these: +0x14 analog ==
//       Campaign::sizeClassFor(surfaceCells) (verified 1:1 across 484
//       saves), +0x16 analog == PlanetState::terrainRow (income-law.md S10;
//       t281 measured its domain 0..10 == the 11 type words EXACTLY — the
//       type-word consumer found this session resolves the t281 tension:
//       word 10 == "Cornucopia" and SA_Cornucopia skips +0x16==10).
//       IF [PL+0x5a] == -1 the name is REPLACED by #137 "Self-Managed"
//       (0x5077f; the rewrite has no per-planet self-managed state — the
//       leg is pure-module only, pinned synthetically).
//     LINE 2 (project) [verified 0x507ca..0x508b9]:
//       pending == 0xFF (planetwin kNoPending):  #141 "No Project", and
//         ADDITIONALLY iff pop(+0x42 analog) == used(+0x4c analog):
//         append #142 "   (No Free Population)" (THREE leading spaces,
//         byte-exact static.txt).
//       else: item name = planitem row name (OQ-014 name30@+10; the runtime
//         copy is stride 40 with the name at +0xa — 0x5088f reads 10 chars);
//         if item flags bit 2 (0x507fc and al,2) -> progress leg SKIPPED;
//         else days = FUN_0x39558: cost WORD (planitem COST@+8) with the
//         Automation x3 leg (slot item 35 && +0x52 match, 0x39545 — NOT
//         modelled, named), then FUN_0x47010: IND <= 0 -> 0xffff sentinel;
//         else days = (cost - acc - 1)/IND + 1 == ceil((cost-acc)/IND)
//         [instruction-exact: sub ecx,edx; lea edx,[ecx-1]; idiv ebx; inc].
//           0xffff -> append #138 " - No Progress"
//           else   -> append #139 " - %d day%s until completion" with the
//                     CITED plural pair getter(28)""/getter(29)"s" (static
//                     .txt #28/#29 — the t276 [inferred] law is now cited)
//         line2 = sprintf #140 "Building %s%s" (itemName, progressSuffix).
//
//   ROW GEOMETRY [measured, work/screens/t3/planets_header_t1086_after_open
//   .png, capture 800x600 of 640x480 (scale 1.25); capture->native = /1.25]:
//     selection marker bands native y 128.0-143.2 / 240.8-256.0 /
//     353.6-368.8 -> three rows, PITCH 112.6 +- 0.2 px, marker 15 px tall
//     at the left edge (x ~16-66 native, red census 80..178); interior
//     frame fill lines native y 116.8 / 457.6. Row count on screen = 3
//     (scroll arrows step the window). Column x's from the same census +
//     the external vision read of the same capture: system name cyan band
//     x 224-252; the gauge-dot columns x ~350-500; scroll arrows right edge
//     x ~716-719 capture = 573-575 native. PITCH is the only EXACT law; the
//     column x's inside a row are [measured-approximate] and named as such.
//     The port law below uses pitch 112 clipped to the STATPLANLST interior
//     and keeps 3 visible rows exactly like the witness.
//
//   GAUGE/POP CONTENT: reuse the cited selectors — ui::gaugeSelector /
//   ui::prosSelector (planets-ui.md S3) and Campaign::popBandsFor (S4);
//   the per-row 5-column dot ladder is the same selector values the state-17
//   TYPE-29 panels consume (planetwin.h gauge table).

#include <optional>
#include <string>
#include <vector>

#include "game/campaign.h"
#include "ui/layout.h"

namespace ascend::ui {

// ---- static.txt word tables (FILE ORDER == runtime table slot order,
// verified by r402_sizetype_census.py content anchor) --------------------
const char* statusSizeWord(int sizeIdx);   // 0..4, nullptr out of domain
const char* statusTypeWord(int typeIdx);   // 0..10, nullptr out of domain

// ---- line assembly (pure; the two legs of the ROW ROW-ASSEMBLY LAW) -----
// selfManaged replaces the name per 0x5077f. name may be empty (never
// happens from Campaign; refused-not-crashed).
std::string statusLine1(const std::string& name, int sizeIdx, int typeIdx,
                        bool selfManaged = false);

// days == -1 == the 0xffff sentinel leg (" - No Progress").
// skipProgress == item flags bit 2 (the suffix leg never runs).
std::string statusLine2(const std::string& itemName, int days,
                        bool skipProgress = false);
// The pending==0xFF line: "No Project" + "   (No Free Population)" iff
// pop == used (0x508da: cmp [PL+0x42],[PL+0x4c]).
std::string statusLine2NoProject(bool noFreePopulation);

// The days law itself (FUN_0x39558 Automation leg EXCLUDED + FUN_0x47010):
// ind <= 0 -> -1; else ceil((cost-acc)/ind) clamped >= 0 (acc may exceed
// cost between the tick and completion; the vendor's formula returns 0 then
// — verified shape of 0x47010 when ecx-edx <= 0: (n-1)/ind+1 with n<=0
// yields <= 0 for ind>=1; the port clamps at 0, labelled).
int statusDays(int cost, int acc, int ind);

// ---- the visible-row window (list membership + scroll) -------------------
struct StatusRowKey { int star; int planetIndex; };

// One entry per planet owned by `owner` (the t249 membership law), ordered
// by (star id, planet index) — [documented default; vendor order source
// unresolved, see header].
std::vector<StatusRowKey> statusPlanets(const ascend::game::Campaign& camp,
                                        int owner);

// The 3-row scroll window (kStatusVisibleRows) over `all` given scroll step
// (clamped 0..max(0, size-3); empty list -> empty).
std::vector<StatusRowKey> statusWindow(const std::vector<StatusRowKey>& all,
                                       int scroll);
inline constexpr int kStatusVisibleRows = 3;   // measured (three markers)
// t417b ROW PITCH REPLACED [measured, docs/re/_wip_t417.md F3]: the t3
// capture's flag-icon bands sit at y57/198/339 (pitch EXACTLY 141; column-
// profile autocorrelation single peak 0.634; user original agrees ~140).
// The old 112 was fitted to the SURFACE-THUMBNAIL art-centres (135.6/248.8/
// 360.8 = row-top + ~78), not row tops — REFUTED by the capture t402 itself
// cited. 3 rows exact: 57 + 3*141 = 480 == screen bottom.
inline constexpr int kStatusRowPitch = 141;    // measured 141 exactly (F3)
inline constexpr Rect kStatusInterior{7, 46, 632, 457};  // t402 frame lines
// RETIRED BY F4: the vendor interior is BLACK with NO row separators
// (hline scan zero) — kStatusInterior is kept only for the hit-map's left
// edge; its y1 no longer governs row fit (rows govern themselves: top+3*pitch
// == 480).
// Row 0 top — t417b MEASURED (F3): rows start at 57, immediately below the
// code-drawn divider (solid (33,56,57) at y46, black y47). The t406 "117"
// anchored rows BELOW the 10status k0 ART header cells — but the vendor
// never paints k0 (F1/F6), so those cells do not exist on screen; 117 left a
// 60 px black gap the vendor does not show.
inline constexpr int kStatusRowsTop = 57;
// Scroll arrows — t405 RECTS MEASURED on the vendor backdrop itself
// (10status.shp k0, decoded via tools/shp_pngdump this session;
// docs/re/_wip_t405.md F8): the arrow BOXES are painted in the art at
// x 619..638, top box y 48..94, bottom box y 425..478. The old PORT rects
// {566,...} were 50px too wide on the left and swallowed clicks that the
// vendor gives to the list. Hit order: arrow boxes first, then rows, and
// the scrollbar column (below) never hits a row.
inline constexpr Rect kStatusArrowUp{619, 48, 638, 94};
inline constexpr Rect kStatusArrowDown{620, 425, 638, 476};
// The scrollbar column of the vendor list (art: trough + thumb between the
// two arrow boxes; verticals at x 619/621 and the right frame at 638).
// Clicks here are NOT row clicks (vendor: trough/page area; the port has no
// thumb-drag model — inert, named seam).
inline constexpr Rect kStatusScrollCol{619, 48, 638, 476};

// ---- t427 ROW COMPOSITION LAW (docs/re/_wip_t427.md F1-F6) -------------
// The vendor row painter fn 0x500e0 (state-10 STATUS list; disasm
// work/r331_disasm.txt 0x504d0..0x50647) composes each row from THREE
// shape blits + text, on a row surface:
//   BLIT #1 sun:  lib slot [0x8957e] (init 0x51954 resolves
//                 "DATA\\suns.shp", string verbatim at file 0x856a7),
//                 selector = raw star-type dword (suns.shp count 13 ==
//                 the 13 starstat types, mapgen.md S1).
//   BLIT #2 planet: lib slot [0x69d0] (init 0x51911 resolves
//                 "data\\planets.shp"), selector = 5*type + size
//                 (0x50567..0x50581 words +0x16/+0x14 = the SAME words
//                 the row string reads via word tables #46-56/#41-45).
//   BLIT #3 flag: raceflag.shp (slot global [0x6fd84]=32 MEASURED in
//                 60.sav) via FUN_0x53dd8 at row-local (10,4), gated by
//                 the owner-mask law 0x505f1..0x50647 (planet owned by
//                 this species -> paint).
// SCALE LAW (t427 F5/F6): MEASURED drawn sun 130x126 vs suns k0 content
// 61x68 (u32 pair rec+0x10), and the "Large" planet ~70px vs content 35
// => the row art blits at 2x (blitShapeScaled path). Drawn-centre anchors
// are MEASURED on the t3 capture (warm-px bbox row0 x16..145 y59..184;
// blue bbox x174..~240 y66..155; rows 1/2 centres agree within +-3 px):
inline constexpr int kStatusArtScale = 2;      // 2x blit (F5)
inline constexpr int kStatusSunCx = 80;        // sun centre x (row-rel 0)
inline constexpr int kStatusSunCy = 64;        // sun centre y offset
inline constexpr int kStatusPlanetCx = 215;    // planet centre x
inline constexpr int kStatusPlanetCy = 53;     // planet centre y offset
inline constexpr int kStatusFlagX = 12;        // flag top-left x (bbox 12..26)
inline constexpr int kStatusFlagY = 0;         // flag top-left y (bbox y57..81)
// The vendor flag is PALETTE-RAMP-TINTED (0x53e81..0x53ea5 rewrites
// palette slots 15..19 := raceByte - i, i=0..4, before the blit): the
// port blits the record's native colours — NAMED SEAM T427-D.
// SELECTION LAW [measured t427 F6, decisive]: row 0 (selected) line-1
// text is WHITE (255,255,255) x522 px; rows 1/2 (unselected) GREEN
// (0,170,82) x551/x375 px. There is NO capsule/marker rect — the t417b
// flat (255,0,0) block x16..69 was fitted to the SUN ART's upper-left
// arc (rows 1/2 red px below x185 = ZERO) and is DELETED.
inline constexpr RGB kStatusLine1Sel{255, 255, 255};
inline constexpr RGB kStatusLine1Norm{0, 170, 82};
// POP PIP GRID [measured F6]: 10 cols x 4 rows, pitch 5, dot ~2px, at
// x498..544 (col pairs 498/499,503/504,...) y row+50..row+67 (bands
// 107/112/117/122 on row 0), red family. Replaces the t417b single
// 10-band strip at x428 (wrong column AND wrong shape).
inline constexpr int kStatusPipX = 498, kStatusPipY = 50;
inline constexpr int kStatusPipPitch = 5, kStatusPipCols = 10,
                     kStatusPipRows = 4;
// Pure pip position (index clamped to the 40-cell grid; returns false for
// i >= capacity so callers paint nothing beyond 40 bands).
inline bool statusPipAt(int i, int rowTop, int& x, int& y) {
    if (i < 0 || i >= kStatusPipCols * kStatusPipRows) return false;
    x = kStatusPipX + (i % kStatusPipCols) * kStatusPipPitch;
    y = rowTop + kStatusPipY + (i / kStatusPipCols) * kStatusPipPitch;
    return true;
}

// t405 UNIFIED STATUS HIT-MAP (pure; pins test_statusnav_t405.cpp).
// Vendor precedence evidence: the arrow boxes are painted OVER the list
// column in the backdrop, so they own their rects; the list interior owns
// everything left of x 619; the scroll column between the arrows is inert.
enum class StatusHit { None, ArrowUp, ArrowDown, Row };
struct StatusHitResult {
    StatusHit kind = StatusHit::None;
    int row = -1;  // visible-row index (0..kStatusVisibleRows-1) for Row
};
StatusHitResult statusHitFor(Pt p, int topY);

// Hit-map: which visible row owns point p (0..2), nullopt outside rows.
// `topY` = native y of row 0's top (the port anchors row 0 at interior y0).
// DEPRECATED for click routing (use statusHitFor, which honours the arrow
// boxes and the scroll column); kept as the raw row-band math.
std::optional<int> statusRowAt(Pt p, int topY);

// ---- the header count pair (screen-open snapshot law) --------------------
struct StatusHeader { int planets; int systems; };
// planets == count(player planets) AT CALL TIME (the port has no frozen
// snapshot — it recomputes per frame; the vendor freezes per open. NAMED
// SEAM: the freeze is cosmetic for a live session, cited as frozen by t249).
// systems == sole-owner stars (Campaign::soleSystemsForPlayer if present,
// else the loop of FUN_00051684 re-expressed: stars whose owner is the
// player; the home star INCLUDED per PROOF 3 "sole + home = 36").
StatusHeader statusHeaderFor(const ascend::game::Campaign& camp, int owner);

}  // namespace ascend::ui
