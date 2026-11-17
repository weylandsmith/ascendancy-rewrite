// SPDX-License-Identifier: GPL-3.0-or-later

#pragma once
// t419: THE CORNER "Exit <ESC>" POPUP LAW (D15 addendum verbatim: "There
// should also be a UI feature where putting the mouse in a corner pops up a
// box that says 'Exit <ESC>', I think you found an image file for that in a
// previous round"). Pure module (no SDL); pins tests/test_exitpopup_t419.cpp;
// working log docs/re/_wip_t419.md F4/F6.
//
// ART [verified, docs/re/shp.md S27 (t344) + S28 (t367) + _wip_d1page.md]:
// mouse.shp records k4..k7 are ONE 78x47 glyph anchored at the FOUR screen
// corners — the painted planes are byte-identical (md5 b2d049bbf5b5, all
// four), and the signed bbox halves are the corner anchors (k4 (0,0), k5
// (-77,-46) bottom-right, k6 (77,0) top-right-ish, k7 (-8,-8); the vendor
// painted the same prompt tucked into each corner). The glyph reads "Exit
// <ESC>" (white + lime text, beveled frame — t344 vision of the render).
// The library's canonical dims gate refuses k5..k7 (zero half of the signed
// pair); the t367 CORNER-ANCHOR FALLBACK (shp.cpp, D1 ruling KEEP) decodes
// EXACTLY those three. k9/k10/k11 in the directory carry the same 78x47
// signed bboxes (measured this session: k9 (0,0)-(77,46), k10 (-77,0)-(0,46),
// k11 ...); the port blits the FALLBACK-DECODING record (record 5 decodes
// 78x47 via the signed path) and declines with no-op when the lib refused.
//
// TRIGGER LAW [port default, labelled — no vendor capture covers the corner
// probe]: cursor within kCornerProbePx of BOTH a screen edge pair (any of
// the four corners) -> popup shown at that corner; leaving clears. The
// popup is an AFFORDANCE HINT only: it changes no state. Esc keeps the
// t410 CHAIN LAW (unwind one level) — the glyph text names it.

#include "ui/layout.h"

namespace ascend::ui {

inline constexpr int kCornerProbePx = 24;   // [port default]
inline constexpr int kExitGlyphW = 78;      // [verified signed bbox W]
inline constexpr int kExitGlyphH = 47;      // [verified signed bbox H]
inline constexpr int kExitGlyphRec = 5;     // the t367-decoding record

enum class ExitCorner { None, TopLeft, TopRight, BottomLeft, BottomRight };

// Corner whose probe box contains (px,py) inside a w x h field; None else.
// Edges are inclusive of the screen edge itself.
ExitCorner exitCornerFor(int px, int py, int w, int h,
                         int probe = kCornerProbePx);

// Where the glyph is PAINTED for corner c (tucked inside the screen, the
// vendor anchor posture: flush to the two corner edges).
Rect exitPopupRect(ExitCorner c, int w, int h);

}  // namespace ascend::ui
