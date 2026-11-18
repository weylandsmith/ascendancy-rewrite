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

// t425 TOGGLE-LAYER DEFAULTS [verified windows.txt BUTTONSTATE lines:
// TOGLANES ln347 BS 1, TOGSHIPS ln382 BS 1, TOGCOLONIES ln400 BS 1,
// TOGEMPIRE ln365 BS 0 (the vendor's empire overlay starts OFF); the
// handler init 0x2718c..0x271b4 sets dword win+0xc4/c8/cc/d0 = -1 and
// byte win+0xd8 = 0xff — visible]. RACE filter starts all-visible (0xff).
inline constexpr bool kCtlDefaultLanes = true;
inline constexpr bool kCtlDefaultShips = true;
inline constexpr bool kCtlDefaultColonies = true;
inline constexpr bool kCtlDefaultEmpire = false;
inline constexpr unsigned kRaceFilterInit = 0xff;

// t425 MSG MAP of the COSMOSWnd handler 0x26b34 [verified, capstone
// base-0 work/ascend_restored.bin, full table docs/re/_wip_t425.md F1b]:
// 26 store win+0xd9; 27..55 dial latch chain 0x27d6f; 56 CENTERHOLO
// recenter 0x27b02 (call 0x26a9c); 57 TOGLANES toggle win+0xc4 0x27b58;
// 58 TOGSHIPS toggle win+0xc8 0x27d40; 59 pump 0x27a18; 60 TOGEMPIRE
// toggle win+0x58a 0x27b29; 61 TOGCOLONIES toggle win+0xd0 AND win+0xcc
// 0x27cce; 62 RACECONTROLS toggle byte win+0xd8 bit(param) 0x27824;
// 63 latch mask-clear 0x27ad2; 66 0x27b87; default -> parent 0x336b4.

// ---- RACECONTROLS (ln415-435) ----------------------------------------------
inline constexpr Rect kRaceControlsFrame{474, 442, 632, 472};
inline constexpr int kRaceControlsShape = 19;  // SHAPEFRAME verbatim (k19)
struct RaceSlot { int bit; Rect rect; };       // verbatim RACE<N>CONTROL
extern const RaceSlot kRaceSlots[7];

// t425b FACE FAMILY LAW (docs/re/_wip_t425.md F5, census
// scripts/t425b_face_census.py over extracted/ascend01/data/1starmap.shp):
// slot i owns FIVE records at base = 20 + 5i —
//   +0 16x16 dark tone, +1 16x16 brighter tone,
//   +2 17x17 dark tone + idx103 OUTLINE, +3 17x17 brighter + outline,
//   +4 16x16 GREY variant (idx0/idx6, neutral).
// The windows.txt SHAPEFRAME column (20,25,...,50) is the +0 member, and the
// control RECT is 17x17 inclusive (479..495 / 449..465) — exactly the size of
// the outlined members. Which member the vendor paints is decided by the
// vendor's own help text (extracted/ascend00/help.txt ln370-373, HELPINDEX
// rcontrol == the RACECONTROLS HELPINDEX, verbatim): "Only information
// pertaining to the species whose colors are OUTLINED will be displayed" =>
// VISIBLE = +2 (outlined), FILTERED = +4 (grey). Measured over the 17x17 rect
// with the stride backdrop (k19 idx200): visible mean lum 82.8..149.8 and
// CHROMATIC per slot; hidden 23.2 and NEUTRAL (max-min channel < 1) — so the
// on/off encoding is hue+outline AND luminance (the CVD law is satisfied by
// the vendor art itself, no port ramp needed).
inline constexpr int kRaceSlotFrameBase(int i) { return 20 + 5 * i; }
inline constexpr int kRaceSlotFrameVisible(int i) { return kRaceSlotFrameBase(i) + 2; }
inline constexpr int kRaceSlotFrameHidden(int i) { return kRaceSlotFrameBase(i) + 4; }

// The race-control slot (if any) owning p. Slots are disjoint (pitch 22,
// width 16: gaps 517..522 etc. hit nothing).
std::optional<int> raceSlotFor(Pt p);  // returns index 0..6

// ---- t400 FRAME TEXTURE LAW (D11 "background art ... rendered in
// greyscale" / cluster bg) — GEOMETRY still valid, GENERATOR superseded
// by the t422 MARKOV FIELD LAW (docs/re/chrome.md) ------------------------
// The vendor map screen carries a mottled grey-teal texture in VERTICAL
// BANDS outside the cosmos field [measured on BOTH independent vendor
// shots — pinned docs/assets/refcap/original-strategic-map.png and the
// user-supplied scratchpad/galaxymap-original.png; docs/re/_wip_t400.md
// S12]: left margin x0..6 for the full height, and the whole right column
// x466..639 (the sidebar gaps included — the texture shows BETWEEN the
// buttons and behind the cluster zone). The field interior is black: the
// texture is chrome, not backdrop art of the map.
// t422 UPDATE [measured]: the field is SCREEN-FIXED noise (83-99% pixel-
// identical across three different vendor screens at zero shift), NOT a
// shape record — 1starmap k0 stays REFUTED (t400), and no SHAPEFRAME
// governs it. The hash-noise generator (t400) and the 6x6-cell grid
// (t411) are BOTH superseded by the Markov chain in textureColourAt;
// census per column in docs/re/_wip_t422.md F7 + chrome.md.
inline constexpr int kTextureBandCount = 2;
inline constexpr Rect kTextureBands[kTextureBandCount] = {
    {0, 0, 6, 479},       // left margin  [user original full height; the
                          // pinned +40-shift capture confirms rows 0..439]
    {466, 0, 639, 479},   // right column incl. sidebar + cluster bg
};
// ---- t411 COSMOS BEVEL LAW (docs/re/_wip_t411.md F5) -----------------------
// The vendor starfield sits in a RECESS: texture luminance ramps DOWN to
// near-black at the field edge on all four sides [measured scans of
// scratchpad/galaxymap-original.png: left x6 (65,65,65) x7 (49,54,53)
// x8 (5,6,6) x9 black; top y7 (31,46,49) y8 black; right x466 (27,32,33)
// then texture; bottom y472 black y473 (54,76,76)]. The port reproduces the
// ramp with two lines: kBevelMid at the rect outset (x0-1), kBevelIn at the
// windows.txt rect itself; both strictly darker than the old flat
// (120,120,120) frame line the vendor never shows at the edge. The recess
// ART record stays the t400 named seam.
inline constexpr RGB kBevelMid{49, 54, 53};
inline constexpr RGB kBevelIn{5, 6, 6};
// The census colour set (game.pal entries; index 0 = black).
extern const RGB kTextureColours[10];
extern const int kTextureWeights[10];  // percent weights, sum 74 (tail = 26)
// Deterministic texture colour for a pixel: splitmix64 over (x,y) mapped
// through the weighted colour set. Same input -> same colour every frame
// (no rng_ touched; law mirrors cam3d's Star.z discipline).
RGB textureColourAt(int x, int y);

}  // namespace ascend::ui
