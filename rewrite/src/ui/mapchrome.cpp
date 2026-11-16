// SPDX-License-Identifier: GPL-3.0-or-later

// Galaxy-map sidebar chrome law — see mapchrome.h for the citations. Pure
// data + hit-testing (no SDL), pin: tests/test_mapchrome_t394.cpp.
#include "ui/mapchrome.h"

#include <cstdint>

namespace ascend::ui {

// windows.txt verbatim (line cites in mapchrome.h / _wip_t394.md).
// Order == MapCtl enum order.
const MapControl kMapCtl[kMapCtlCount] = {
    {{495, 364, 509, 394}, 8, 51},   // ROTRIGHT   ln223
    {{479, 364, 494, 394}, 9, 50},   // ROTLEFT    ln240
    {{518, 364, 548, 379}, 10, 52},  // ROTUP      ln257
    {{518, 380, 548, 394}, 11, 53},  // ROTDOWN    ln274
    {{557, 380, 587, 394}, 12, 55},  // ZOOMOUT    ln291
    {{557, 364, 587, 379}, 13, 54},  // ZOOMIN     ln308
    {{596, 364, 626, 394}, 14, 56},  // CENTERHOLO ln325
    {{479, 403, 509, 433}, 15, 57},  // TOGLANES   ln342
    {{518, 403, 548, 433}, 16, 60},  // TOGEMPIRE  ln360
    {{557, 403, 587, 433}, 17, 58},  // TOGSHIPS   ln378
    {{596, 403, 626, 433}, 18, 61},  // TOGCOLONIES ln396
};

std::optional<MapCtl> mapCtlFor(Pt p) {
    // File order, LAST hit wins (documented shared-edge law; the only
    // overlaps are ROTUP/ROTDOWN and ZOOMIN/ZOOMOUT at y 379|380).
    std::optional<MapCtl> hit;
    for (int i = 0; i < kMapCtlCount; ++i)
        if (inRect(kMapCtl[i].rect, p))
            hit = static_cast<MapCtl>(i);
    return hit;
}

// RACE<N>CONTROL <bit> x0 449 x1 465 verbatim (ln429-435); x0 = 479 + 22i.
const RaceSlot kRaceSlots[7] = {
    {1, {479, 449, 495, 465}},   // RACE1CONTROL
    {2, {501, 449, 517, 465}},   // RACE2CONTROL
    {4, {523, 449, 539, 465}},   // RACE3CONTROL
    {8, {545, 449, 561, 465}},   // RACE4CONTROL
    {16, {567, 449, 583, 465}},  // RACE5CONTROL
    {32, {589, 449, 605, 465}},  // RACE6CONTROL
    {64, {611, 449, 627, 465}},  // RACE7CONTROL
};

std::optional<int> raceSlotFor(Pt p) {
    for (int i = 0; i < 7; ++i)
        if (inRect(kRaceSlots[i].rect, p)) return i;
    return std::nullopt;
}

// t400 texture census (mapchrome.h): colour set + percent weights as
// MEASURED on the pinned shot's margin bands (docs/re/_wip_t400.md S12).
// The residue (100 - sum = 34%) is spread over the remaining game.pal
// greys/teals of the same luminance families by the hash tail below.
const RGB kTextureColours[10] = {
    {0, 0, 0},        //  4.5% black
    {77, 113, 117},   // 14.9% mode
    {85, 125, 125},   //  8.7%
    {97, 146, 146},   //  8.0%
    {69, 105, 109},   //  7.4%
    {97, 97, 97},     //  7.2%
    {89, 134, 138},   //  6.7%
    {89, 89, 89},     //  6.6%
    {60, 93, 97},     //  5.6%
    {73, 73, 85},     //  4.1%
};
const int kTextureWeights[10] = {4, 15, 9, 8, 7, 7, 7, 7, 6, 4};

RGB textureColourAt(int x, int y) {
    // t411 MOTTLE LAW [measured]: the vendor texture is SMOOTH at pixel
    // scale — lag-1 neighbour diff / mean dev = 0.23 on the sidebar band
    // (4x4-block lag-1 0.28), while our old per-pixel hash measured 1.45
    // (pure TV static). The pattern SOURCE record is still unidentified
    // (t400 seam), so the port keeps the cited colour set + weights but
    // generates them on a 6x6 CELL grid (one colour per cell): within-cell
    // neighbours identical, cell-to-cell weighted-random. scripts/
    // t411_mottle.py sweeps this generator's own lag-1 statistic: cell 1
    // (old) 1.57, cell 2 0.78, cell 4 0.38, cell 6 0.25, cell 8 0.19 —
    // cell 6 is the closest to the vendor's measured 0.23. Still
    // deterministic per pixel (no engine rng_; law mirrors Star.z).
    const int cx = x / 6, cy = y / 6;
    uint64_t z = (uint64_t(uint32_t(cx)) << 32) ^ uint64_t(uint32_t(cy)) ^
                 0x9e3779b97f4a7c15ull;
    z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ull;
    z = (z ^ (z >> 27)) * 0x94d045bb41f336ull;
    z = z ^ (z >> 31);
    const int r = int(z % 100u);
    int acc = 0;
    for (int i = 0; i < 10; i++) {
        acc += kTextureWeights[i];
        if (r < acc) return kTextureColours[i];
    }
    // Residue tail: neighbours of the mode within the measured families
    // (all game.pal entries; (48,77,81) and (105,154,144)-family greys
    // observed in the census).
    static const RGB kTail[4] = {{48, 77, 81}, {105, 154, 154},
                                 {81, 81, 81}, {36, 56, 60}};
    return kTail[z % 4u];
}

}  // namespace ascend::ui
