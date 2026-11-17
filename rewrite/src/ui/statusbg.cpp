// SPDX-License-Identifier: GPL-3.0-or-later

// Status-screen background law — see statusbg.h for the citations. Pure
// data + math (no SDL), pin: tests/test_statusbg_t417b.cpp.
#include "ui/statusbg.h"

#include <cstdint>

#include "ui/statuslaw.h"  // Screen enum (kScreenStatus)

namespace ascend::ui {

bool screenPaintsShapeBackdrop(int screen) {
    // F6 [verified windows.txt re-census]: the TYPE-100 SHAPEFILE census is
    // states 0,1,3,7,8,13,16,20,TESTDLG ONLY — state 10 binds NO lib, so the
    // status screen has no shape backdrop (F1: k0 registers 4.5% exact on
    // the t3 live capture; its navy interior vs vendor black is the
    // fingerprint). Screens whose k0 IS a backdrop (17np, t406) keep the
    // ui.cpp size test; everything else declines by that test anyway.
    return screen != kScreenStatus;
}

// Measured speckle census (statusbg.h; t3 capture display-space values).
const RGB kSpeckleColours[kSpeckleCount] = {
    {0, 0, 0},      // .349
    {8, 12, 16},    // .327
    {8, 12, 8},     // .172
    {8, 28, 49},    // .062
    {8, 32, 49},    // .011
    {8, 36, 49},    // .006
};
// Renormalised to sum EXACTLY 98 (the modulus of statusSpeckleAt — the
// census caught a first draft summing 119, which starved indices 3..5):
// the .052 green is title TEXT; minors (41,20,33)/(41,28,66) fold into the
// rare-teal tail behaviour.
const int kSpeckleWeights[kSpeckleCount] = {37, 35, 18, 6, 1, 1};

RGB statusSpeckleAt(int x, int y) {
    // F5: the header band is PER-PIXEL noise (lag-1/dev 1.304), so this
    // hashes every pixel — the t411 6x6 cell grid belongs to the perimeter
    // texture (textureColourAt), not here. Deterministic splitmix64, same
    // discipline as cam3d Star.z (no engine rng_).
    uint64_t z = (uint64_t(uint32_t(x)) << 32) ^ uint64_t(uint32_t(y)) ^
                 0x9e3779b97f4a7c15ull;
    z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ull;
    z = (z ^ (z >> 27)) * 0x94d045bb41f336ull;
    z = z ^ (z >> 31);
    const int r = int(z % 98u);
    int acc = 0;
    for (int i = 0; i < kSpeckleCount; i++) {
        acc += kSpeckleWeights[i];
        if (r < acc) return kSpeckleColours[i];
    }
    static const RGB kTail[2] = {{41, 20, 33}, {41, 28, 66}};
    return kTail[z % 2u];
}

bool statusRampColourAt(int y, RGB* out) {
    // Verbatim per-row mode from the t3 game rect (statusbg.h header cites
    // the shares). Rows outside 38..46 draw nothing (y47+ is black
    // interior, y<=37 speckle/perimeter).
    switch (y) {
        case 38: *out = RGB{74, 113, 115}; return true;
        case 39:
        case 40: *out = RGB{123, 182, 181}; return true;
        case 41: *out = RGB{115, 117, 115}; return true;
        case 42: *out = RGB{66, 105, 107}; return true;
        case 43:
        case 44: *out = RGB{24, 48, 41}; return true;
        case 45: *out = RGB{24, 28, 24}; return true;
        case 46: *out = RGB{33, 56, 57}; return true;
        default: return false;
    }
}

}  // namespace ascend::ui
