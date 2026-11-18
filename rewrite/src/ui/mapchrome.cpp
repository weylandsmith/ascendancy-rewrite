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

// t422 CHROME FIELD LAW (docs/re/chrome.md + _wip_t422.md F1-F9) replaces
// the t400/t411 hash-noise + 6x6-cell generator. MEASURED on the pinned
// 640x480 vendor captures (docs/assets/refcap/original-strategic-map.png,
// original-planet-view.png, original-species-research.png):
//  * The mottle is a SCREEN-FIXED noise FIELD, not window art: the left
//    band x1..6 is 83-99% pixel-identical across three different screens
//    at zero shift (map vs planet 83.2%, planet vs species 99.1%).
//  * NOT a repeating tile: y-periodicity k=8..240 all at noise floor.
//  * NOT iid colour sampling and NOT a cell grid: vendor vertical run
//    lengths 0.616/0.234/0.092/0.026 (k=1..4) vs iid 0.907/0.08; lag-1
//    luminance h 0.62 / v 0.40 vs iid 1.36/1.36 vs our old per-pixel
//    hash 1.46/1.21 (t411's 0.23 calibration band x474..632 was
//    CONTAMINATED by sidebar widget art — the cell grid it produced is
//    REFUTED on the pure left band).
//  * LAW: per-pixel Markov field — P(repeat the pixel above)=0.385,
//    P(copy the pixel left)=0.05 (grid fit over 8 statistics, mean abs
//    dev 0.063; scripts/t422_fit.py), else a fresh weighted draw from the
//    PER-COLUMN census below. Deterministic: the chain is replayed
//    backwards from (x,y) to its fresh-draw anchor using splitmix64 of
//    (x,y), so the function stays pure (no rng_, no state).
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
    // t422 MARKOV FIELD LAW [measured, docs/re/chrome.md]: per-pixel
    // chain — P(copy pixel LEFT)=0.05, else P(repeat pixel ABOVE)=0.25,
    // else a fresh weighted draw from the per-column census (left band
    // x0..6) or the right-zone census (x466..; every producible colour is
    // an exact game.pal entry). Deterministic WITHOUT state: the chain
    // decision at each step is splitmix64(x,y); recursion walks up/left
    // to the fresh-draw anchor (bounded: 480 up + 7 left). Replaces the
    // t411 6x6 cell grid — REFUTED on the PURE left band (the t411
    // calibration band x474..632 was contaminated by sidebar widget art;
    // vendor pure-band run stats 0.616/0.234/0.092 match a Markov chain,
    // cells give 0.574/0.262 with lag-1 v 0.55 vs vendor 0.40).
    uint64_t z = (uint64_t(uint32_t(x)) << 32) ^ uint64_t(uint32_t(y)) ^
                 0x9e3779b97f4a7c15ull;
    z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ull;
    z = (z ^ (z >> 27)) * 0x94d045bb41f336ull;
    z = z ^ (z >> 31);
    const uint64_t r = z % 1000000ull;
    if (r < 50000ull && x > 0) return textureColourAt(x - 1, y);   // 5%
    if (r < 300000ull && y > 0) return textureColourAt(x, y - 1);  // 25%
    // Fresh draw. kLeft = per-column census of the vendor left chrome
    // band (pinned original-strategic-map.png rows 40..479; weights are
    // raw pixel counts; docs/re/_wip_t422.md F7). kRight = right-zone
    // chrome census (F10, chrome-set colours of x466..639).
    struct Ent { uint8_t r, g, b, pad; int w; };
    static const Ent kLeft[7][10] = {
        /* x0 */ {{97,97,97,0,98},{77,113,117,0,130},{85,125,125,0,120},{89,134,138,0,53},{97,146,146,0,8},{89,89,89,0,26},{81,81,81,0,5},{0,0,0,0,0},{0,0,0,0,0},{0,0,0,0,0}},
        /* x1 */ {{97,97,97,0,46},{77,113,117,0,209},{85,125,125,0,94},{89,134,138,0,59},{89,89,89,0,28},{81,81,81,0,2},{97,146,146,0,2},{0,0,0,0,0},{0,0,0,0,0},{0,0,0,0,0}},
        /* x2 */ {{81,81,81,0,42},{69,105,109,0,143},{77,113,117,0,126},{85,125,125,0,45},{89,89,89,0,76},{89,134,138,0,6},{73,73,85,0,2},{0,0,0,0,0},{0,0,0,0,0},{0,0,0,0,0}},
        /* x3 */ {{60,93,97,0,58},{69,105,109,0,150},{77,113,117,0,49},{73,73,85,0,92},{89,89,89,0,53},{48,48,48,0,15},{81,81,81,0,11},{85,125,125,0,8},{89,134,138,0,2},{60,52,56,0,2}},
        /* x4 */ {{28,28,28,0,5},{48,48,48,0,47},{48,77,81,0,83},{60,93,97,0,103},{69,105,109,0,90},{73,73,85,0,92},{60,52,56,0,10},{77,113,117,0,7},{85,125,125,0,1},{89,134,138,0,2}},
        /* x5 */ {{48,48,48,0,39},{48,77,81,0,80},{60,93,97,0,117},{69,105,109,0,76},{73,73,85,0,108},{60,52,56,0,10},{40,65,69,0,1},{56,85,89,0,1},{77,113,117,0,5},{85,125,125,0,3}},
        /* x6 */ {{28,28,28,0,6},{48,48,48,0,123},{24,48,40,0,45},{36,56,60,0,143},{40,65,69,0,86},{48,77,81,0,27},{56,85,89,0,7},{60,93,97,0,1},{77,113,117,0,2},{0,0,0,0,0}},
    };
    static const Ent kRight[10] = {
        {77,113,117,0,7587},{97,97,97,0,3514},{85,125,125,0,3093},{89,89,89,0,2018},
        {89,134,138,0,1997},{97,146,146,0,1483},{24,48,40,0,1163},{36,56,60,0,1095},
        {28,28,28,0,968},{60,93,97,0,928},
    };
    const Ent* tab; int n;
    if (x >= 0 && x <= 6) { tab = kLeft[x]; n = 10; }
    else { tab = kRight; n = 10; }
    int total = 0;
    for (int i = 0; i < n; i++) total += tab[i].w;
    const uint64_t d = (z >> 20) % uint64_t(total ? total : 1);
    int acc = 0;
    for (int i = 0; i < n; i++) {
        acc += tab[i].w;
        if (int(d) < acc)
            return RGB{tab[i].r, tab[i].g, tab[i].b};
    }
    return RGB{tab[n - 1].r, tab[n - 1].g, tab[n - 1].b};
}

}  // namespace ascend::ui
