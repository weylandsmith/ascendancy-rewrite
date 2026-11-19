// SPDX-License-Identifier: GPL-3.0-or-later
// t426c CHROME-BAND GRADIENT LAW pins. Law + measurement trail:
// docs/re/_wip_t426.md F6.1-F6.3 (scripts/t426c_band_gradient.py census,
// scripts/t426c_chi2.py + scripts/t426c_tune.py replay/tuning). The vendor
// top band (screen rows 0..6, full width) is a PER-ROW census of the same
// screen-fixed Markov field (cross-screen identity 92-99.8% vs
// planet-view/species-research), with the chain running ALONG the band;
// the right field-edge strip x466..472 is a per-column census whose
// bright idx58/173/59 ridge is absent from the flat kRight set. Pins here
// are census-shape invariants on our own generator (the port may not read
// the vendor png at runtime), tuned so the SHIPPED law passes and the two
// refuted shapes (flat mix for the band; edge-normal chain for the band)
// fail — mutation-verified.
#include <cstdint>
#include <map>
#include <set>
#include <string>
#include <vector>
#include <cmath>

#include "harness.h"
#include "ui/mapchrome.h"

using namespace ascend::ui;

static uint32_t pack(const RGB& c) {
    return (uint32_t(c.r) << 16) | (uint32_t(c.g) << 8) | c.b;
}

TEST(band_gradient_rows_distinct_t426c) {
    // (1) DETERMINISM on the band (no rng_).
    for (int i = 0; i < 30; i++) {
        const RGB a = textureColourAt(50 + i, 3), b = textureColourAt(50 + i, 3);
        CHECK(a.r == b.r && a.g == b.g && a.b == b.b);
    }
    // (2) The per-row law: the BRIGHT family (luminance > 70) dominates
    // rows 0-1 and the NEAR-BLACK family (luminance < 60) dominates row 6
    // [measured mean-lum profile 106.5/106.2/83.7/65.5/45.3/46.9/28.3].
    // NOTE the bright check alone does NOT kill the flat-kRight mutant
    // (its bright fraction is 0.83); the row-6 dark check + the envelope
    // below do (flat dark fraction 0.13, flat row means ~equal).
    auto lumf = [](const RGB& c) {
        return 0.2126 * c.r + 0.7152 * c.g + 0.0722 * c.b;
    };
    for (int row = 0; row <= 1; row++) {
        int bright = 0, tot = 0;
        for (int x = 7; x < 466; x++) { bright += lumf(textureColourAt(x, row)) > 70.0; tot++; }
        CHECK(bright * 100 >= 70 * tot);   // vendor row 1.000 (all 7 colours lum>70); flat ~0.45
    }
    {
        int dark = 0, tot = 0;
        for (int x = 7; x < 466; x++) { dark += lumf(textureColourAt(x, 6)) < 60.0; tot++; }
        // [measured vendor row6: EVERY census colour (2/1/48/49/200/50/0)
        // has lum < 60 -> fraction 1.000; our shipped law 1.000; the
        // REFUTED flat-kRight mix sits at ~0.13.]
        CHECK(dark * 100 >= 85 * tot);
    }
    // (3) MONOTONE ENVELOPE: mean luminance of row 0 >= row 3 >= row 6
    // (the edge-normal gradient). Tolerant to chain noise, kills any
    // permuting of the row table.
    double l0 = 0, l3 = 0, l6 = 0;
    for (int x = 7; x < 466; x++) {
        l0 += lumf(textureColourAt(x, 0));
        l3 += lumf(textureColourAt(x, 3));
        l6 += lumf(textureColourAt(x, 6));
    }
    CHECK(l0 > l3 * 1.3);                  // measured 106.5 vs 65.5 = 1.63
    CHECK(l3 > l6 * 1.5);                  // measured 65.5 vs 28.3 = 2.31
}

TEST(band_along_chain_t426c) {
    // The band's noise runs ALONG the band: horizontal repeat fraction in
    // row 3 [measured: vendor h-run k1 0.653 -> repeat 0.347; the shipped
    // along-band law replays at 0.406; the REFUTED edge-normal 5/25 chain
    // gives h-run k1 0.788 -> repeat 0.212; iid census floor ~0.15].
    // Window [0.27,0.45] admits the law, rejects both refuted shapes.
    int rep = 0, tot = 0;
    for (int x = 7; x < 465; x++) {
        const RGB a = textureColourAt(x, 3), b = textureColourAt(x + 1, 3);
        rep += (a.r == b.r && a.g == b.g && a.b == b.b); tot++;
    }
    CHECK(rep * 100 >= 27 * tot);
    CHECK(rep * 100 <= 45 * tot);
    // AND the vertical direction is NOT the repeat direction: the band's
    // v-repeat fraction stays well BELOW its h-repeat fraction (measured
    // ours v 0.126 vs h 0.406 — the anisotropy is the rotated-noise law;
    // a mutant that swaps the chain to edge-normal gives v >= h).
    int vrep = 0, vtot = 0;
    for (int y = 0; y < 6; y++)
        for (int x = 7; x < 466; x++) {
            const RGB a = textureColourAt(x, y), b = textureColourAt(x, y + 1);
            vrep += (a.r == b.r && a.g == b.g && a.b == b.b); vtot++;
        }
    // vrep/vtot < (2/3) * rep/tot, cross-multiplied (different denoms).
    CHECK(vrep * tot * 3 < rep * vtot * 2);
}

TEST(right_edge_ridge_t426c) {
    // The right field-edge strip is per-column, NOT the flat kRight mix:
    // cols 467/468 carry the BRIGHT idx58/173/59 ridge (mean lum >= 100)
    // while col 466 is mid (measured mean 88-113 across the strip; the
    // flat kRight census mean is ~85 and CANNOT produce (125,121,138)).
    auto lumf = [](const RGB& c) {
        return 0.2126 * c.r + 0.7152 * c.g + 0.0722 * c.b;
    };
    double m467 = 0, m468 = 0;
    std::set<uint32_t> cols;
    for (int y = 60; y < 460; y++) {
        m467 += lumf(textureColourAt(467, y));
        m468 += lumf(textureColourAt(468, y));
        cols.insert(pack(textureColourAt(467, y)));
    }
    m467 /= 400; m468 /= 400;
    CHECK(m467 >= 100.0);                  // vendor 133.6/133.7; our law ~130
    CHECK(m468 >= 100.0);
    // the ridge mauve (125,121,138) == idx173 is PRODUCIBLE at x467 and is
    // in NO other shipped table — flat-law mutant produces 0 of these.
    CHECK(cols.count(0x7D798Au) > 0);
    // and the strip is v-repeat dominated (same field, along-band =
    // vertical here): repeat fraction above iid floor.
    int rep = 0, tot = 0;
    for (int y = 60; y < 459; y++) {
        const RGB a = textureColourAt(467, y), b = textureColourAt(467, y + 1);
        rep += (a.r == b.r && a.g == b.g && a.b == b.b); tot++;
    }
    CHECK(rep * 100 >= 40 * tot);          // measured 1-run 0.574 -> rep ~0.42+
}
