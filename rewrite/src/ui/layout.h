#pragma once
// Pure UI layout math (no SDL) so it is unit-testable in ascend_core.
// Geometry anchors: docs/re/ui-runtime.md §1 (windows.txt line numbers cited
// there). Scaling default: docs/re/ui-runtime.md §2.
#include "game/mapgen.h"

namespace ascend::ui {

struct Rect { int x0, y0, x1, y1; };
struct Pt { int x, y; };

// COSMOSWnd interior on a 640x480 display: rect 7,7..465,472 [verified].
inline constexpr Rect kCosmosWnd{7, 7, 465, 472};
// NEXTTURN button: 474,52..548,82 [verified].
inline constexpr Rect kNextTurnBtn{474, 52, 548, 82};
inline constexpr int kDisplayW = 640, kDisplayH = 480;  // media.md FLIC mode

// Maps generator grid (mapgen mapSize, default 1024) into the cosmos rect.
struct CosmosView {
    int mapSize = 1024;  // MapConfig.mapSize (mapgen.md §4 default)
    Rect bounds = kCosmosWnd;
};

Pt starScreenPos(const CosmosView& v, const ascend::game::Star& s);
// Returns star id within radius px of p, or -1.
int hitStar(const CosmosView& v, const ascend::game::Galaxy& g, Pt p, int radius = 6);
// True iff p is inside r (inclusive, as windows.txt rects are inclusive).
bool inRect(Rect r, Pt p);

// ---- owner palette (docs/re/ui-runtime.md §4) ------------------------------
// User constraint: never encode meaning in colour alone. The 7 owner colours
// are a SEARCHED set (min hue spread 45 deg) validated under BOTH the
// simulated deuteranopia and protanopia transforms by
// tests/test_ui_layout.cpp; ALL gaps are measured on the simulated
// (perceived) colours, never raw RGB. Rule:
//   owner pair OK iff perceived-luminance gap >= 32
//                OR sim-chroma distance >= 90 with perceived gap >= 12.
struct RGB { unsigned char r, g, b; };
extern const RGB kOwnerRgb[7];   // owner id order (0 = player white)
extern const RGB kNeutralRgb;    // unclaimed star
// Same transform used by the test, exposed so the two can never drift.
void simulateDeuteranopia(const RGB& c, RGB* out);
void simulateProtanopia(const RGB& c, RGB* out);
unsigned luminance601(const RGB& c);  // 0..255

}  // namespace ascend::ui
