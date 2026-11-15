// SPDX-License-Identifier: GPL-3.0-or-later

#pragma once
// GALAXY-MAP SIDEBAR LAW (t394) — the vendor's state-1 map screen is a
// chrome-clad screen, not a string dump. Every rect below is verbatim from
// extracted/ascend00/windows.txt (line cited per row); every SHAPEFRAME is
// verbatim from the same record. Instrument log: docs/re/_wip_t394.md.
//
// MEASURED ON THE USER-SUPPLIED VENDOR ORIGINAL (scratchpad/galaxymap-
// original.png, 642x481) [verified t394]:
//   - capture->screen mapping here is IDENTITY (png x,y == screen x,y);
//     button bevel lines land at y=130/169/208/248/286 vs table 130/169/
//     208/247/286. The t393 "minus 1" law was capture-tool chrome on that
//     one capture and does NOT generalise.
//   - FIVE green digit ovals at screen x 482/513/544/575/606 (pitch 31,
//     ~19 px wide), green rows y10..40 — INSIDE the TURNCOUNT rect
//     474,7-632,43 (TYPE 15, SHAPEFRAME 65, DIGITFRAMES 55, ln521-537).
//     The ovals + digits ARE the resource readout; the vendor map screen
//     shows NO stats string (D10 "status line" removal is cited).
//   - RACECONTROLS (ln415-435): frame 474,442-632,472 SHAPEFRAME 19,
//     NUMCONTROLS 7, slots RACE<N>CONTROL <bit> x0 449 x1 465 at x0 =
//     479+22i (16x16), bits 1/2/4/8/16/32/64. Slot 1 green square
//     measured at screen 479,448-495,465 = rect EXACT. The frame strip is
//     1starmap k19 (158x30 = 632-474+1 x 472-442+1 EXACT size match).
//   - SPIN/ZOOM/TOGGLE cluster (COSMOSWnd children ln223-414) sits at x
//     479..626, y 364..433: SHAPEFRAMEs 8..18 into 1starmap.shp (dims
//     census t394: k8 14x30, k9 15x30, k10 30x15, k11/k12 30x14, k13
//     30x15, k14..k18 30x30 — every SHAPEFRAME record's dims match its
//     rect's WxH transposed-or-exact, see table).
//   - NEXTTURN SHAPEFRAME 65 (74x30) + NEXTTURNCONT SHAPEFRAME 66 (75x30)
//     button faces; 1starmap k65/k66 are EXACTLY 74x30 / 75x30.
//
// BEHAVIOUR SEAMS (honest, named): the oval CONTENTS (which resource each
// oval holds, digit blit law) is NOT cited — TYPE 15's DIGITFRAMES 55
// implies frames k55..k64 are the digit faces (census: ten 24x33-ish
// records — plausible, uncited); draw ovals + values via the port's text
// face instead and label the seam. Spin/zoom buttons are DRAWN (cited
// art) but their SENDMESSAGE 50..56 map/pan/zoom behaviour is a seam (the
// port's CosmosView has no pan/zoom model).

#include <optional>

#include "ui/layout.h"

namespace ascend::ui {

// ---- TURNCOUNT + oval panel (windows.txt ln521-537) ------------------------
inline constexpr Rect kTurnCount{474, 7, 632, 43};
// The five oval slots as MEASURED on the vendor original (see header).
// x = left edge, width, and the digit baseline band; y band shared.
struct OvalSlot { int x0, y0, x1, y1; };
inline constexpr OvalSlot kOvalSlots[5] = {
    {482, 10, 500, 39}, {513, 10, 531, 39}, {544, 10, 562, 39},
    {575, 10, 593, 39}, {606, 10, 624, 39},
};

// ---- NEXTTURN pair (ln539-572) ----------------------------------------------
inline constexpr int kNextTurnShape = 65;    // SHAPEFRAME verbatim
inline constexpr int kNextTurnContShape = 66;
inline constexpr Rect kNextTurnCont{557, 52, 632, 82};

// ---- spin/zoom/toggle cluster (COSMOSWnd children, ln223-414) --------------
enum class MapCtl {
    RotRight, RotLeft, RotUp, RotDown, ZoomOut, ZoomIn, CenterHolo,
    TogLanes, TogEmpire, TogShips, TogColonies
};
inline constexpr int kMapCtlCount = 11;
struct MapControl {
    Rect rect;        // verbatim X0,Y0,X1,Y1
    int shapeFrame;   // verbatim SHAPEFRAME (1starmap.shp)
    int sendMessage;  // verbatim SENDMESSAGE
};
extern const MapControl kMapCtl[kMapCtlCount];  // order == enum

// Which cluster control (if any) owns p. Only meaningful on the map screen
// (children of COSMOSWnd; their STATE lists are "3 1 7 13" so they are
// alive on the map). Rects do not overlap except ROTUP/ROTDOWN and
// ZOOMIN/ZOOMOUT share an edge at y 379/380 — inclusive edges mean the
// shared line resolves to the LATER record; no live click lands there.
std::optional<MapCtl> mapCtlFor(Pt p);

// ---- RACECONTROLS (ln415-435) ----------------------------------------------
inline constexpr Rect kRaceControlsFrame{474, 442, 632, 472};
inline constexpr int kRaceControlsShape = 19;  // SHAPEFRAME verbatim (k19)
struct RaceSlot { int bit; Rect rect; };       // verbatim RACE<N>CONTROL
extern const RaceSlot kRaceSlots[7];

// The race-control slot (if any) owning p. Slots are disjoint (pitch 22,
// width 16: gaps 517..522 etc. hit nothing).
std::optional<int> raceSlotFor(Pt p);  // returns index 0..6

// ---- t400 FRAME TEXTURE LAW (D11 "background art ... rendered in
// greyscale" / cluster bg) ----------------------------------------------------
// The vendor map screen carries a mottled grey-teal texture in VERTICAL
// BANDS outside the cosmos field [measured on BOTH independent vendor
// shots — pinned docs/assets/refcap/original-strategic-map.png and the
// user-supplied scratchpad/galaxymap-original.png; docs/re/_wip_t400.md
// S12]: left margin x0..6 for the full height, and the whole right column
// x466..639 (the sidebar gaps included — the texture shows BETWEEN the
// buttons and behind the cluster zone). The field interior is black: the
// texture is chrome, not backdrop art of the map. Colour census of the
// bands (pinned shot): (77,113,117) 14.9%, (85,125,125) 8.7,
// (97,146,146) 8.0, (69,105,109) 7.4, (97,97,97) 7.2, (89,134,138) 6.7,
// (89,89,89) 6.6, (60,93,97) 5.6, black 4.5, (73,73,85) 4.1 — every one
// verified inside game.pal. The SOURCE RECORD is unidentified: 1starmap
// k0 (158x75) is REFUTED at the cluster zone (registration 7172
// conflicts, 21% in palette); no .shp record matches the band extent. The
// port therefore paints DETERMINISTIC hash-noise over the measured colour
// set with the measured weights — the noise PATTERN is a named seam
// (decider: a vendor screen-record of a scroll, or the identifying
// record); the geometry and the palette are cited.
inline constexpr int kTextureBandCount = 2;
inline constexpr Rect kTextureBands[kTextureBandCount] = {
    {0, 0, 6, 479},       // left margin  [user original full height; the
                          // pinned +40-shift capture confirms rows 0..439]
    {466, 0, 639, 479},   // right column incl. sidebar + cluster bg
};
// The census colour set (game.pal entries; index 0 = black).
extern const RGB kTextureColours[10];
extern const int kTextureWeights[10];  // percent weights, sum 74 (tail = 26)
// Deterministic texture colour for a pixel: splitmix64 over (x,y) mapped
// through the weighted colour set. Same input -> same colour every frame
// (no rng_ touched; law mirrors cam3d's Star.z discipline).
RGB textureColourAt(int x, int y);

}  // namespace ascend::ui
