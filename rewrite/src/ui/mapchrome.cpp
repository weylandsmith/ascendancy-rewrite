// SPDX-License-Identifier: GPL-3.0-or-later

// Galaxy-map sidebar chrome law — see mapchrome.h for the citations. Pure
// data + hit-testing (no SDL), pin: tests/test_mapchrome_t394.cpp.
#include "ui/mapchrome.h"

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

}  // namespace ascend::ui
