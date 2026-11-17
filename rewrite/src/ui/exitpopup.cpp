// SPDX-License-Identifier: GPL-3.0-or-later

// t419 corner "Exit <ESC>" popup — law + citations in exitpopup.h.

#include "ui/exitpopup.h"

namespace ascend::ui {

ExitCorner exitCornerFor(int px, int py, int w, int h, int probe) {
    if (probe < 1) probe = 1;
    const bool left = px >= 0 && px < probe;
    const bool right = px <= w - 1 && px >= w - probe;
    const bool top = py >= 0 && py < probe;
    const bool bottom = py <= h - 1 && py >= h - probe;
    if (top && left) return ExitCorner::TopLeft;
    if (top && right) return ExitCorner::TopRight;
    if (bottom && left) return ExitCorner::BottomLeft;
    if (bottom && right) return ExitCorner::BottomRight;
    return ExitCorner::None;
}

Rect exitPopupRect(ExitCorner c, int w, int h) {
    switch (c) {
        case ExitCorner::None: break;
        case ExitCorner::TopLeft:
            return Rect{0, 0, kExitGlyphW - 1, kExitGlyphH - 1};
        case ExitCorner::TopRight:
            return Rect{w - kExitGlyphW, 0, w - 1, kExitGlyphH - 1};
        case ExitCorner::BottomLeft:
            return Rect{0, h - kExitGlyphH, kExitGlyphW - 1, h - 1};
        case ExitCorner::BottomRight:
            return Rect{w - kExitGlyphW, h - kExitGlyphH, w - 1, h - 1};
    }
    return Rect{0, 0, -1, -1};  // None: empty rect (nothing paints)
}

}  // namespace ascend::ui
