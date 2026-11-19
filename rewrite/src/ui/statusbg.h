// SPDX-License-Identifier: GPL-3.0-or-later

#pragma once
// t417b STATUS SCREEN BACKGROUND LAW (D15 "the background... seems to be
// using one of those images we determined wasn't used anywhere").
//
// ROOT CAUSE CLOSED WITH MEASUREMENT (docs/re/_wip_t417.md F1-F6): the port
// blitted 10status.shp k0 full-frame as the status backdrop; the vendor NEVER
// paints k0 there. PROOF [measured, scripts/t417_k0_register.py on the t3
// LIVE capture work/screens/t3/planets_header_t1086_after_open.png]:
// registration at shift(0,0) = 4.5% exact / 6.4% within-30 / mean|d| 149;
// k0's interior is idx 242 navy (12,32,48) x186,722 where the vendor shows
// (0,0,0). windows.txt re-census (F6): the TYPE-100 SHAPEFILE section binds
// ONLY states 0,1,3,7,8,13,16,20,TESTDLG — NO record binds 10status to any
// state. The status chrome is CODE-DRAWN, exactly as the pixel census shows.
//
// VENDOR LAW [measured on the t3 capture AND the user original
// scratchpad/planets-screen-original.png — both independent, both agree]:
//   - BLACK interior (rows zone p_black 0.925 outside art);
//   - perimeter mottled texture band ~7 px (x0..6, x633..639 full height;
//     y0..6, y472..479): texfrac 0.94-1.0, the t400/t411 texture family
//     (same generator, textureColourAt);
//   - header band y8..36 x8..630: PER-PIXEL dark speckle (lag-1/dev 1.304
//     — per-pixel draws, NOT the 6x6-cell mottle the perimeter wants),
//     colour census in kSpeckle* below; green title text rows y20..26;
//   - divider ramp below the header, full width x7..631, rows y38..46
//     ending SOLID (33,56,57) at y46, black from y47 (statusRampColourAt);
//   - left border line x7 (33,56,57) y48..470 (423/423 px);
//   - NO row separator lines anywhere (hline scan: zero rows with >300 mid
//     px in y100..470) — the t402 navy row frames are REFUTED.
// Display-space values [honest negative, F5]: the speckle values do NOT map
// to game.pal under the (v<<2)|(v>>4) conv (t3 is a DOSBox X11 grab) — draw
// them verbatim, do not claim palette indices.
//
// GEOMETRY [measured, F3 — REFUTES the t402 fit]: rows top 57 (flag-icon
// bands y57/198/339), pitch EXACTLY 141 (column-profile autocorrelation
// single peak 0.634; user original agrees ~140), 3 visible rows exact
// (57 + 3*141 = 480 == screen bottom). t402's 112 was fitted to the
// SURFACE-THUMBNAIL art-centres (135.6/248.8/360.8 = row-top + ~78), not
// row tops. Constants live in statuslist.h (single source).

#include "ui/layout.h"

namespace ascend::ui {

// The backdrop DECLINE law (F7 item 1): the status screen paints NO shape
// backdrop — the vendor binds no lib to state 10 (F6 census) and k0
// registers failing on the live capture (F1). Every other screen keeps the
// mechanical full-backdrop size test in ui.cpp (17np k0 still passes t406).
bool screenPaintsShapeBackdrop(int screen);

// Perimeter texture bands on the status screen [measured F2/F4]: the four
// ~7 px edges, full extent, textureColourAt family.
inline constexpr int kStatusTextureBandCount = 4;
inline constexpr Rect kStatusTextureBands[kStatusTextureBandCount] = {
    {0, 0, 639, 6},      // top rows 0..6 (texfrac 0.936)
    {0, 472, 639, 479},  // bottom rows 472..479
    {0, 0, 6, 479},      // left  x0..6 (texfrac 1.0)
    {633, 0, 639, 479},  // right x633..639 (texfrac 1.0)
};

// Header speckle rect [measured F5]: y8..36 x8..630 (n=18,067 px).
inline constexpr Rect kStatusSpeckleRect{8, 8, 630, 36};

// Speckle colour set + percent weights [measured F5, t3 census]:
// (0,0,0) .349, (8,12,16) .327, (8,12,8) .172, (8,28,49) .062,
// (8,32,49) .011, (8,36,49) .006; the green title (0,170,82) .052 is TEXT
// (the port draws its own header string), excluded from the speckle set and
// the remaining shares renormalised to weights summing 98 (tail 2% = the
// measured minors (41,20,33)/(41,28,66)).
inline constexpr int kSpeckleCount = 6;
extern const RGB kSpeckleColours[kSpeckleCount];
extern const int kSpeckleWeights[kSpeckleCount];
// Deterministic per-pixel speckle colour (F5: per-pixel noise, lag-1/dev
// 1.304 — no 6x6 cell grid here, unlike textureColourAt). No engine rng_.
RGB statusSpeckleAt(int x, int y);

// Divider ramp below the header [measured F4/F5 + t417b re-verify on the t3
// game rect: per-row dominant shares]: y38 (74,113,115) .56; y39-40 pale
// (123,182,181) .73; y41 (115,117,115) .29; y42 (66,105,107) .23; y43/44
// (24,48,41) (F4 y44 cited; F5 y43 .25 mode); y45 (24,28,24) .31; y46 SOLID
// (33,56,57) 1.000; y47 black .997. True + *out for y in 38..46; false
// elsewhere (caller draws nothing).
bool statusRampColourAt(int y, RGB* out);

// Left border line [measured F4]: x7, (33,56,57), y48..470 (423/423 px).
inline constexpr int kStatusBorderX = 7;
inline constexpr int kStatusBorderY0 = 48;
inline constexpr int kStatusBorderY1 = 470;
inline constexpr RGB kStatusBorderRgb{33, 56, 57};

// Selection marker: RETIRED t427b. The t417b "red capsule x16..69" was
// REFUTED by measurement (docs/re/_wip_t427.md F6): rows 1/2 (unselected)
// have ZERO red px below x185 in the same shot — the fitted zone was the
// SUN ART's upper-left arc. The vendor selection law is line-1 TEXT COLOUR
// (WHITE vs GREEN; kStatusLine1Sel/kStatusLine1Norm in statuslist.h). The
// constant kStatusMarkerRect is deleted with it.

// Arrow-well box fill [measured F4]: the wells carry navy (8,32,49) — NOT
// the k0 idx-242 navy (12,32,48) the port painted (that colour is the F1
// fingerprint of the never-painted backdrop record).
inline constexpr RGB kStatusWellNavy{8, 32, 49};

}  // namespace ascend::ui
