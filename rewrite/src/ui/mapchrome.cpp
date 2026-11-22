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

// ---- t426c BAND GRADIENT LAW [measured, docs/re/_wip_t426.md F6.1-F6.3] ----
// The band census is EDGE-NORMAL and per-EDGE, not one flat mix:
//  * TOP band (screen rows 0..6, FULL WIDTH incl. over the sidebar): a
//    per-ROW census whose colour families run bright (55/6/56/57/176) ->
//    mid (53/54/52/157/4) -> dark (50/51/49/48) -> near-black (2/1/200).
//    Cross-screen identity rows 0..6 x0..465 vs planet-view AND
//    species-research: row0 99.8%, rows2-5 92-97% -> the gradient belongs
//    to the same screen-fixed field (chrome.md F1), so it is census data,
//    not a ramp generator. Chain runs ALONG-band: copy-left 25%, NO
//    repeat-up (tuner scripts/t426c_tune.py: edge-normal 5/25 blows the
//    per-row chi-square on rows 2-4 — 147/182/168 vs 18/14/12; along-band
//    h-run k1 0.609 vs vendor 0.653).
//  * RIGHT field-edge strip x466..472: per-COLUMN census (rows 60..460,
//    n=401/col, pure refcap). col467/468 carry a BRIGHT idx58/173/59
//    ridge — colours ABSENT from kRight, so the flat law was refuted for
//    these columns; the right edge does NOT mirror the dark left edge.
//    Chain stays edge-normal 5/25 (strip v-run k1 0.574 == the left
//    band's along-band orientation).
//  * BOTTOM band rows 473..479: mean-lum profile measured on the
//    scratchpad (65 -> ridge 160 at 475) but the scratchpad census is
//    24-100% OFF-palette interpolation — NO colour table is derivable
//    from any on-disk pure shot (every refcap is png=screen+40, clipped
//    at screen 439). It stays the flat kRight law; NAMED SEAM.
// Entries are {r,g,b,pad, weight} with VENDOR rounded pixels
// (round(v*255/63)) and RAW census counts as weights.
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
    // t426c: the top band's noise runs ALONG the band (copy-left 25%, no
    // repeat-up); every other chrome class keeps the t422 5/25 chain.
    if (y >= 0 && y <= 6) {
        if (r < 250000ull && x > 0) return textureColourAt(x - 1, y);
    } else {
        if (r < 50000ull && x > 0) return textureColourAt(x - 1, y);   // 5%
        if (r < 300000ull && y > 0) return textureColourAt(x, y - 1);  // 25%
    }
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
    // t426c kTopRow[7]: per-row census of the vendor TOP band, FULL WIDTH
    // (pinned original-strategic-map.png png rows 40..46 = screen 0..6,
    // x7..465, n=459/row, round-palette space, OFF=0). docs/re/_wip_t426.md
    // F6.2. The y-branch precedes the x-branch: rows 0..6 read this table
    // across the whole width (the census over x466..639 matches the same
    // per-row shape), and the corners x0..6 y0..6 belong to it too (the
    // vendor corner px are the 56/53/52 bright family, not kLeft[0]).
    static const Ent kTopRow[7][10] = {
        /* y0 */ {{77,113,117,0,149},{97,97,97,0,104},{85,125,125,0,99},{89,134,138,0,53},{89,89,89,0,37},{97,146,146,0,10},{81,81,81,0,7},{0,0,0,0,0},{0,0,0,0,0},{0,0,0,0,0}},
        /* y1 */ {{77,113,117,0,202},{85,125,125,0,90},{97,97,97,0,79},{89,89,89,0,44},{89,134,138,0,40},{97,146,146,0,3},{81,81,81,0,1},{0,0,0,0,0},{0,0,0,0,0},{0,0,0,0,0}},
        /* y2 */ {{61,93,97,0,157},{69,105,109,0,71},{57,85,89,0,64},{73,73,85,0,58},{65,65,65,0,46},{77,113,117,0,22},{49,77,81,0,16},{61,53,57,0,11},{85,125,125,0,9},{89,89,89,0,5}},
        /* y3 */ {{40,65,69,0,131},{49,77,81,0,109},{36,57,61,0,74},{57,85,89,0,71},{61,93,97,0,32},{49,49,49,0,15},{24,49,40,0,14},{28,28,28,0,9},{77,113,117,0,3},{69,105,109,0,1}},
        /* y4 */ {{24,49,40,0,136},{36,57,61,0,110},{28,28,28,0,72},{40,65,69,0,64},{49,77,81,0,33},{12,12,12,0,22},{57,85,89,0,10},{12,12,16,0,9},{0,0,0,0,2},{61,93,97,0,1}},
        /* y5 */ {{24,49,40,0,120},{36,57,61,0,117},{40,65,69,0,77},{28,28,28,0,61},{49,77,81,0,40},{12,12,12,0,31},{57,85,89,0,10},{12,12,16,0,2},{61,93,97,0,1},{0,0,0,0,0}},
        /* y6 */ {{28,28,28,0,151},{12,12,12,0,125},{24,49,40,0,95},{36,57,61,0,45},{12,12,16,0,32},{40,65,69,0,10},{0,0,0,0,1},{0,0,0,0,0},{0,0,0,0,0},{0,0,0,0,0}},
    };
    // t426c kRightEdge[7]: per-column census of the RIGHT field-edge strip
    // x466..472 (pinned map rows 60..460, n=401/col, OFF=0). col467/468 =
    // bright idx58/173/59 ridge; the strip does NOT mirror the dark left
    // edge. Trailing colours past 14 entries are <1% and folded into the
    // dominant neighbours' mass (chi2 re-verified in F6.3's shape).
    static const Ent kRightEdge[7][14] = {
        /* x466 */ {{81,81,81,0,151},{89,89,89,0,138},{61,93,97,0,82},{69,105,109,0,30},{0,0,0,0,0},{0,0,0,0,0},{0,0,0,0,0},{0,0,0,0,0},{0,0,0,0,0},{0,0,0,0,0},{0,0,0,0,0},{0,0,0,0,0},{0,0,0,0,0},{0,0,0,0,0}},
        /* x467 */ {{97,146,146,0,217},{125,121,138,0,102},{105,154,154,0,68},{117,117,117,0,8},{109,162,166,0,6},{0,0,0,0,0},{0,0,0,0,0},{0,0,0,0,0},{0,0,0,0,0},{0,0,0,0,0},{0,0,0,0,0},{0,0,0,0,0},{0,0,0,0,0},{0,0,0,0,0}},
        /* x468 */ {{97,146,146,0,208},{125,121,138,0,102},{105,154,154,0,77},{117,117,117,0,9},{109,162,166,0,5},{0,0,0,0,0},{0,0,0,0,0},{0,0,0,0,0},{0,0,0,0,0},{0,0,0,0,0},{0,0,0,0,0},{0,0,0,0,0},{0,0,0,0,0},{0,0,0,0,0}},
        /* x469 */ {{89,134,138,0,137},{117,117,117,0,117},{97,146,146,0,53},{85,125,125,0,39},{97,97,97,0,35},{125,121,138,0,12},{105,154,154,0,4},{77,113,117,0,3},{109,162,166,0,1},{0,0,0,0,0},{0,0,0,0,0},{0,0,0,0,0},{0,0,0,0,0},{0,0,0,0,0}},
        /* x470 */ {{69,105,109,0,94},{97,97,97,0,67},{85,125,125,0,65},{77,113,117,0,61},{89,134,138,0,45},{89,89,89,0,37},{117,117,117,0,13},{81,81,81,0,7},{97,146,146,0,4},{109,162,166,0,2},{73,73,85,0,2},{125,121,138,0,2},{65,65,65,0,1},{105,154,154,0,1}},
        /* x471 */ {{61,93,97,0,71},{77,113,117,0,64},{69,105,109,0,51},{73,73,85,0,49},{49,77,81,0,42},{85,125,125,0,27},{97,97,97,0,27},{89,89,89,0,20},{89,134,138,0,12},{65,65,65,0,10},{57,85,89,0,6},{97,146,146,0,4},{105,154,154,0,4},{61,53,57,0,4}},
        /* x472 */ {{77,113,117,0,75},{73,73,85,0,53},{61,93,97,0,47},{49,77,81,0,42},{69,105,109,0,37},{97,97,97,0,30},{65,65,65,0,23},{85,125,125,0,22},{89,89,89,0,17},{61,53,57,0,8},{97,146,146,0,5},{150,150,150,0,5},{40,65,69,0,5},{89,134,138,0,4}},
    };
    const Ent* tab; int n;
    if (y >= 0 && y <= 6) { tab = kTopRow[y]; n = 10; }
    else if (x >= 466 && x <= 472) { tab = kRightEdge[x - 466]; n =
        (x - 466 == 4 || x - 466 == 5 || x - 466 == 6) ? 14 : 9; }
    else if (x >= 0 && x <= 6) { tab = kLeft[x]; n = 10; }
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

// t424b DARK SPECKLE FIELD (race-intro frame interior; docs/re/_wip_t424b.md
// F1/F2) [measured census, docs/re/_wip_t424b.md F2]: the vendor's race-intro
// background inside the outer frame is NOT the bright chrome page — it is a
// dark near-black speckle of game.pal {0:(0,0,0) 48%, 200:(12,12,16) 29%,
// 1:(12,12,12) 24%, 196:(12,28,48) 8%} (renormalised over the four-family
// base of the text-free well pixels). Grain law [measured]: mean |lum delta|
// at game-px lags 1..6 = 3.41/5.74/7.25/7.92/8.27/8.72 (sub-linear =>
// correlated, same Markov shape as the t422 chrome chain; iid would plateau
// by lag 2). Same stateless chain law as textureColourAt (copy-left 5%,
// repeat-up 25%, else fresh draw; splitmix64(x,y) decisions), different seed
// salt and different census. GENERATOR ORIGIN [named seam]: the vendor
// routine that produced this field is not yet cited (t433's memory-surface
// census is the route); the COLOUR census + grain statistics are measured.
RGB introSpeckleAt(int x, int y) {
    uint64_t z = (uint64_t(uint32_t(x)) << 32) ^ uint64_t(uint32_t(y)) ^
                 0x5851f42d403c3b23ull;  // distinct salt: decorrelate chrome
    z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ull;
    z = (z ^ (z >> 27)) * 0x94d045bb41f336ull;
    z = z ^ (z >> 31);
    const uint64_t r = z % 1000000ull;
    if (r < 50000ull && x > 0) return introSpeckleAt(x - 1, y);   // 5%
    if (r < 300000ull && y > 0) return introSpeckleAt(x, y - 1);  // 25%
    // Fresh draw from the measured census. Two independent censuses of the
    // text-free well pixels (_wip_t424b F2): exact-match renormalised over
    // the 4-family base = 40.2/32.5/24.1/3.2; tol-60 nearest over the
    // gap-band rows = 38.7/28.1/26.6/6.7 (the exact-match run under-counts
    // blends of 0). Weights = the two censuses averaged.
    static const struct { RGB c; int w; } kSpeckle[4] = {
        {{0, 0, 0}, 40},      // game.pal[0]
        {{12, 12, 16}, 30},   // game.pal[200]
        {{12, 12, 12}, 25},   // game.pal[1]
        {{12, 28, 48}, 5},    // game.pal[196]
    };
    const uint64_t d = (z >> 20) % 100ull;
    int acc = 0;
    for (int i = 0; i < 4; i++) {
        acc += kSpeckle[i].w;
        if (int(d) < acc) return kSpeckle[i].c;
    }
    return kSpeckle[0].c;
}

// tA2 NEW GAME WELL RECESS + RIDGE (mapchrome.h law; docs/re/_wip_tA2.md
// F3/F5). Geometry is kNewgameCosmosRect (8,8,492,372): recess = row 7
// x7..493 (top), col x7 rows 8..372 (left), col x493 rows 8..372 (right);
// ridge = rows 373..374 x7..493 (dark rung row, then the SAME
// x-quantisation one rung lighter). Censuses are the vendor rows verbatim
// (browser-shot display space, +1,+1 game-rect law). Chain = the t422
// 5/25 Markov law over the per-edge census; deterministic, no state.
bool newgameWellEdgeAt(int x, int y) {
    if (y == 7) return x >= 7 && x <= 493;
    if (y >= 8 && y <= 372) return x == 7 || x == 493;
    if (y == 373 || y == 374) return x >= 7 && x <= 493;
    return false;
}

// tA2 PANEL INSET LAW (the ONE frame law replacing the port's symmetric
// kBevel outline on every New Game panel; docs/re/_wip_tA2.md F3).
// [MEASURED browser shot +1,+1 law] GALAXY_MORE panel {7,381,122,472}:
// TOP inset row 381 x7..122 mean 27.1, census {12,24,34}x25 {12,24,36}x14
// {18,31,40}x12 {17,30,40}x8 {12,24,35}x8 {16,38,45}x7; LEFT inset col
// x7 rows 382..472 mean 33.0, census {15,35,49}x24 {16,34,48}x18
// {15,35,50}x10 {16,35,49}x9 {15,36,50}x7; RIGHT col x122 rows 382..472
// = 91/91 flat navy fill and BOTTOM row 472 = 115/116 flat fill — the
// vendor shows NO line at right/bottom (the RAISED edge reads as the dark
// inset above/left, light chrome below). Same law measured at the chips
// panel (topline y381 x384..493 mean 28.5, same families) and the Begin
// panel (topline y381 x494..639 mean 36.0, same families).
RGB newgamePanelTopAt(int x) {
    uint64_t z = (uint64_t(uint32_t(x)) << 32) ^ 0x8d3b0a1f2c4e6a77ull ^
                 (uint64_t(381) * 0x9e3779b97f4a7c15ull);
    z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ull;
    z = (z ^ (z >> 27)) * 0x94d045bb41f336ull;
    z = z ^ (z >> 31);
    static const struct { RGB c; int w; } kT[6] = {
        {{12, 24, 34}, 25}, {{12, 24, 36}, 14}, {{18, 31, 40}, 12},
        {{17, 30, 40}, 8},  {{12, 24, 35}, 8},  {{16, 38, 45}, 7},
    };
    int total = 0;
    for (int i = 0; i < 6; i++) total += kT[i].w;
    const uint64_t d = (z >> 20) % uint64_t(total);
    int acc = 0;
    for (int i = 0; i < 6; i++) {
        acc += kT[i].w;
        if (int(d) < acc) return kT[i].c;
    }
    return kT[0].c;
}
RGB newgamePanelLeftAt(int y) {
    uint64_t z = (uint64_t(uint32_t(y)) << 32) ^ 0x2f7c91a5d3e08b48ull ^
                 (uint64_t(7) * 0x9e3779b97f4a7c15ull);
    z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ull;
    z = (z ^ (z >> 27)) * 0x94d045bb41f336ull;
    z = z ^ (z >> 31);
    static const struct { RGB c; int w; } kL[5] = {
        {{15, 35, 49}, 24}, {{16, 34, 48}, 18}, {{15, 35, 50}, 10},
        {{16, 35, 49}, 9},  {{15, 36, 50}, 7},
    };
    int total = 0;
    for (int i = 0; i < 5; i++) total += kL[i].w;
    const uint64_t d = (z >> 20) % uint64_t(total);
    int acc = 0;
    for (int i = 0; i < 5; i++) {
        acc += kL[i].w;
        if (int(d) < acc) return kL[i].c;
    }
    return kL[0].c;
}

RGB newgameWellEdgeColourAt(int x, int y) {
    // splitmix64 decisions, chrome salt (one field family).
    uint64_t z = (uint64_t(uint32_t(x)) << 32) ^ uint64_t(uint32_t(y)) ^
                 0x9e3779b97f4a7c15ull;
    z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ull;
    z = (z ^ (z >> 27)) * 0x94d045bb41f336ull;
    z = z ^ (z >> 31);
    const uint64_t r = z % 1000000ull;
    if (r < 50000ull && x > 7) return newgameWellEdgeColourAt(x - 1, y);
    // tA2-CONT CHAIN-ANCHOR FIX: the repeat-up recursion stays INSIDE the
    // pixel's band. The ridge rows 373/374 NEVER recurse up: (x,372) is the
    // pure-black well interior, and drawing from the kLeft/kRight RECESS
    // tabs there dragged 25% of ridge pixels dark (witness 50.6/90.4 vs
    // tab means 64.4/102.8). Pulling 374->373 instead mixes the DARK rung
    // into row 374 (stationary expectation 0.7*102.8+0.3*64.4 ~ 92.7,
    // outside the +-6 window) — and the vendor census shows each ridge row
    // holds its OWN rung family in matching counts (grey 169/169, teal
    // 108/107, 71/70), i.e. per-row draws from the rung-shifted tables,
    // not a vertical carry. Rows 373/374 draw fresh-or-left-anchored from
    // their own tab; recess columns 8..372 chain up within their column as
    // before (witness col7 6.5 == vendor 6.5). docs/re/_wip_tA2.md F6.
    if (r < 300000ull && y > 7 && y != 373 && y != 374)
        return newgameWellEdgeColourAt(x, y - 1);
    struct Ent { RGB c; int w; };
    // Top recess row 7 x7..493: n=487 mean 24.3 — dark noise: greys
    // 147 / teals 155 / near-black 185 (family split F3 probe).
    static const Ent kTop[6] = {
        {{24, 24, 24}, 93},  {{10, 10, 10}, 62},  {{21, 42, 35}, 54},
        {{12, 12, 12}, 26},  {{32, 49, 53}, 26},  {{10, 10, 14}, 25},
    };
    // Left recess col x7 rows 8..372: n=365 mean 6.5.
    static const Ent kLeft[4] = {
        {{5, 7, 8}, 90},  {{6, 6, 6}, 71},  {{5, 8, 9}, 43},  {{3, 6, 5}, 22},
    };
    // Right recess col x493 rows 8..372: n=365 mean 22.9.
    static const Ent kRight[4] = {
        {{0, 0, 0}, 102},   {{30, 30, 30}, 65},  {{33, 33, 33}, 40},
        {{23, 35, 36}, 36},
    };
    // Ridge row 373 (dark rungs; n=487 mean 64.5) and row 374 (same
    // x-quantisation rung-lighter; n=487 mean 102.8). FULL 98.5%-mass
    // censuses (top-3-only scored 50.8/90.3 vs vendor 64.5/102.8 — the
    // blend tail is BRIGHT, truncation skews dark; verified witness
    // scripts run 2026-11-21).
    static const Ent kRidge0[14] = {
        {{61, 61, 61}, 169}, {{53, 78, 78}, 108}, {{48, 71, 73}, 71},
        {{50, 69, 72}, 22},  {{53, 77, 78}, 22},  {{49, 72, 74}, 22},
        {{59, 62, 62}, 21},  {{50, 73, 75}, 13},  {{56, 64, 65}, 10},
        {{53, 67, 68}, 9},   {{51, 75, 76}, 4},   {{56, 72, 72}, 4},
        {{60, 63, 63}, 4},   {{54, 76, 76}, 3},
    };
    static const Ent kRidge1[14] = {
        {{97, 97, 97}, 169},  {{85, 125, 125}, 107},  {{77, 113, 117}, 71},
        {{84, 124, 124}, 22}, {{78, 114, 118}, 22},   {{80, 111, 114}, 22},
        {{95, 99, 99}, 21},   {{80, 117, 120}, 12},   {{90, 103, 105}, 10},
        {{84, 107, 110}, 9},  {{82, 121, 122}, 5},    {{96, 100, 100}, 4},
        {{90, 114, 114}, 4},  {{86, 122, 122}, 3},
    };
    const Ent* tab = kTop;
    int n = 6;
    if (y >= 8 && y <= 372) { tab = (x <= 250) ? kLeft : kRight; n = 4; }
    if (y == 373) { tab = kRidge0; n = 14; }
    if (y == 374) { tab = kRidge1; n = 14; }
    int total = 0;
    for (int i = 0; i < n; i++) total += tab[i].w;
    const uint64_t d = (z >> 20) % uint64_t(total);
    int acc = 0;
    for (int i = 0; i < n; i++) {
        acc += tab[i].w;
        if (int(d) < acc) return tab[i].c;
    }
    return tab[0].c;
}

// t436b SPECIES-SCREEN EMPTY-WELL SPECKLE (docs/re/_wip_t436.md G1).
// [measured t252 species_menu_game.png x474..632, slots 4/5/6 + header]:
// display-space families (8,12,16) 50-63% / (0,0,0) 26-47% / (8,28,49)
// 2.5-9%; mean run length h 4.03 v 3.74 (N=3434/3694) — correlated field,
// NOT iid (iid: run 1.92, same-adjacency 0.48). The display triplets are
// the DOSBox-scaled readings of game.pal {200:(3,3,4), 0:(0,0,0),
// 196:(3,7,12)} under round(v*255/63) = {(12,12,16), 0, (12,28,48)} (the
// t424b family set minus pal[1]); the port paints the PALETTE values, the
// witness grades OUR 1:1 render against the family shares. Chain weights
// 45% copy-left + 35% repeat-up fitted on the run-length statistic
// (simulated run 3.92 vs measured 3.88 pooled; grid scripts see G1).
RGB speciesWellAt(int x, int y) {
    uint64_t z = (uint64_t(uint32_t(x)) << 32) ^ uint64_t(uint32_t(y)) ^
                 0x436b1f7c2a9d5e11ull;  // distinct salt: decorrelate chrome
    z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ull;
    z = (z ^ (z >> 27)) * 0x94d045bb41f336ull;
    z = z ^ (z >> 31);
    const uint64_t r = z % 1000000ull;
    if (r < 450000ull && x > 0) return speciesWellAt(x - 1, y);    // 45%
    if (r < 800000ull && y > 0) return speciesWellAt(x, y - 1);    // +35%
    static const struct { RGB c; int w; } kWell[3] = {
        {{12, 12, 16}, 625},  // game.pal[200]
        {{0, 0, 0}, 257},     // game.pal[0]
        {{12, 28, 48}, 90},   // game.pal[196]
    };
    const uint64_t d = (z >> 20) % 972ull;
    int acc = 0;
    for (int i = 0; i < 3; i++) {
        acc += kWell[i].w;
        if (int(d) < acc) return kWell[i].c;
    }
    return kWell[0].c;
}

// tNG-F2 PLAYER-SPECIES PLATE LAW (D20 F2 "missing the black backing";
// docs/re/_wip_tNGF.md V0-F2 follow-up). The vendor plate behind the
// "Player Species" header (x503..633 rows 8..37) is NOT flat black and NOT
// the cosmos field (that is 98% pure black): it is the dark speckle family.
// [MEASURED refcap census over the 4 nearest families, text excluded]
// (0,0,0) 46.3% (12,12,16) 35.0% (12,12,12) 7.1% (12,28,48) 11.6%.
// [MEASURED grain, family-luminance lags, text-free rows 26..37]
// h 8.59/12.26/16.36 v 5.50/10.35/13.86 — correlated, ANISOTROPIC (vertical
// runs longer). Chain fitted on these lags (same statistic law as
// speciesWellAt) over a 0.00-0.95 grid of (copy-left, repeat-up):
// 45% copy-left + 50% repeat-up simulates h 9.03/15.16/18.80
// v 7.19/12.13/15.94 — best fit of the grid (cycle-2's 55/30 measured
// h 14.02 v 17.96 on screen: visibly too sparse). GENERATOR ORIGIN is
// a named seam (vendor routine uncited, as for introSpeckleAt); the CENSUS
// and GRAIN are measured.
RGB speciesPlateAt(int x, int y) {
    // Salt chosen (from 200 candidates) so the REALISED census of the fixed
    // 131x30 plate window matches the measured census within noise (chain
    // propagation drifts the realised mix away from the fresh-draw weights;
    // witness census at this salt 49.0/34.3/4.6/12.1, grain h
    // 7.17/13.10/16.62 v 6.47/10.73/13.19 — vs vendor 46.0/34.8/7.1/12.1,
    // h 8.59/12.26/16.36 v 5.50/10.35/13.86).
    uint64_t z = (uint64_t(uint32_t(x)) << 32) ^ uint64_t(uint32_t(y)) ^
                 0x420e8910b5e72c97ull;  // salt: plate-window calibration
    z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ull;
    z = (z ^ (z >> 27)) * 0x94d045bb41f336ull;
    z = z ^ (z >> 31);
    const uint64_t r = z % 1000000ull;
    if (r < 450000ull && x > 0) return speciesPlateAt(x - 1, y);    // 45%
    if (r < 950000ull && y > 0) return speciesPlateAt(x, y - 1);    // +50%
    static const struct { RGB c; int w; } kPlate[4] = {
        {{0, 0, 0}, 463},      // game.pal[0]
        {{12, 12, 16}, 350},   // game.pal[200]
        {{12, 12, 12}, 71},    // game.pal[1]
        {{12, 28, 48}, 116},   // game.pal[196]
    };
    const uint64_t d = (z >> 20) % 1000ull;
    int acc = 0;
    for (int i = 0; i < 4; i++) {
        acc += kPlate[i].w;
        if (int(d) < acc) return kPlate[i].c;
    }
    return kPlate[0].c;
}

}  // namespace ascend::ui
