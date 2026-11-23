// SPDX-License-Identifier: GPL-3.0-or-later

// t436b SPECIES-SCREEN LAW pins (docs/re/_wip_t436.md F4/F4b/F7/F8/G1 +
// ui/speciesmenu.h, ui/mapchrome.h).
//
// LAW [measured work/screens/t252/species_menu_game.png 1:1 640x480 vs its
// own map baseline]:
//  * slot rects kRaceRows == windows.txt RACE_1..7 verbatim (474,7/46/85/
//    124/163/202/241 - 632,+30); the row CENTRE x is (474+632)/2 = 553, and
//    the vendor name bboxes centre there on all three populated rows
//    (Orfa x542..564, Ungooma x531..575, Extinct x536..570).
//  * populated rows are FLAT navy (8,32,49) at 91-94% == kStatusWellNavy;
//    (12,32,48) — the colour 7racesel k0..k6 decode to — occurs ZERO times
//    in both t252 captures (the F4 decisive colour law).
//  * header + EMPTY slots are the DARK SPECKLE family; the fitted chain is
//    the t424b shape with census game.pal {200:625, 0:257, 196:90} and
//    copy-left 45% + repeat-up 35% (G1: mean run h 4.03 / v 3.74 measured,
//    simulated 3.92; iid gives run 1.92 / same-adjacency 0.48).
//  * flag face at row-local (14,3) (bbox x488..502 on all three rows,
//    native 14x24 == raceflag record dims).
//  * portraits: smrace rec 0 (49x49) at scale 2 clipped r49 + racering
//    k<colour idx> (53x53) at scale 2 -> band r50..55 == the measured
//    three-tone owner ring (t423c2 ring-index law; palettes census F8).
#include "formats/gamepal.h"
#include "formats/shp.h"
#include "ui/mapchrome.h"
#include "ui/speciesmenu.h"
#include "ui/statusbg.h"
#include "ui/statuslaw.h"
#include "harness.h"

namespace {
namespace au = ascend::ui;
const std::string kA01 =
    std::string(ASCENDANCY_SOURCE_DIR) + "/extracted/ascend01/data/";

TEST(species_slot_rects_and_text_centre_t436) {
    // windows.txt RACE_1..7 verbatim + the 553 centre law.
    const int tops[7] = {7, 46, 85, 124, 163, 202, 241};
    for (int i = 0; i < 7; i++) {
        CHECK(au::kRaceRows[i].x0 == 474);
        CHECK(au::kRaceRows[i].x1 == 632);
        CHECK(au::kRaceRows[i].y0 == tops[i]);
        CHECK(au::kRaceRows[i].y1 == tops[i] + 30);
    }
    // The vendor name bbox centre 553 == the slot centre under the port's
    // centring law x = x0 + ((x1-x0+1) - w)/2 : for ANY w the painted bbox
    // centre is x0 + (x1-x0+1)/2 == 553.5 -> int-bbox centre 553 (the
    // measured value on all three rows).
    const int centre = au::kRaceRows[1].x0 +
                       (au::kRaceRows[1].x1 - au::kRaceRows[1].x0 + 1) / 2;
    CHECK(centre == 553 || centre == 554);  // 553 measured; 554 = round-up
    CHECK(au::kRaceRows[1].x0 + (au::kRaceRows[1].x1 - au::kRaceRows[1].x0) / 2 ==
          553);
}

TEST(species_populated_fill_is_the_measured_navy_t436) {
    // [measured F4] populated rows: (8,32,49) 91-94%.
    CHECK(au::kStatusWellNavy.r == 8 && au::kStatusWellNavy.g == 32 &&
          au::kStatusWellNavy.b == 49);
}

TEST(species_row_flag_offset_matches_the_measured_bbox_t436) {
    // [measured F7] flag bbox x488..502 == slot.x0 + 14 (474+14), rows
    // rowTop+3 .. rowTop+27 (native 14x24).
    CHECK(au::kSpeciesRowFlagDx == 14);
    CHECK(au::kSpeciesRowFlagDy == 3);  // tA1: flag bbox 15x25 at (0,0)
    REQUIRE_DATA();
    ascend::formats::ShapeLibrary flags;
    std::string err;
    CHECK(flags.load(kA01 + "raceflag.shp", &err));
    if (flags.count() < 1) return;
    CHECK(int(flags.record(0).width) == 15);   // tA1 bbox exact
    CHECK(int(flags.record(0).height) == 25);  // tA1 bbox exact
}

TEST(species_portrait_ring_radii_match_the_measured_band_t436) {
    // [measured F5/F7] content disc to r~48, ring band r50..55.
    // smrace 49x49 at scale 2 -> drawn 98 (r49 clipped); racering 53x53 at
    // scale 2 -> drawn 106 (outer r53; the ring's own band lands r50..55
    // because the record's ring px sit at r25..28 native x2).
    // tA1 BBOX-DIFF LAW: class scale 1; content disc 100 px (r50), ring
    // 109 px (outer r55 measured band r50..55 lands natively).
    CHECK(au::kSpeciesPortraitScale == 1);
    CHECK(au::kSpeciesPortraitClipR == 50);
    CHECK(au::kSpeciesRingHalf == 55);
    REQUIRE_DATA();
    ascend::formats::ShapeLibrary ring;
    std::string err;
    CHECK(ring.load(kA01 + "racering.shp", &err));
    ascend::formats::ShapeLibrary disc;
    CHECK(disc.load(kA01 + "smrace00.shp", &err));
    if (ring.count() < 1 || disc.count() < 1) return;
    CHECK(int(ring.record(0).width) == 109);  // tA1 bbox (-55,-55,53,53)
    CHECK(int(ring.record(0).height) == 109);
    CHECK(int(disc.record(0).width) == 100);  // tA1 bbox (-50,-50,49,49)
    CHECK(int(disc.record(0).height) == 100);
}

TEST(species_well_speckle_is_correlated_not_iid_t436) {
    // G1 fit law: the field must be strongly correlated (mean run ~3.9 at
    // these chain weights; iid gives 1.92) and must stay inside the
    // measured family set {pal200 (12,12,16), pal0 (0,0,0), pal196
    // (12,28,48)}.
    int runs = 0, same = 0;
    int c200 = 0, c0 = 0, c196 = 0, other = 0;
    for (int y = 163; y <= 192; y++) {
        int prev = -1;
        for (int x = 474; x <= 632; x++) {
            const au::RGB c = au::speciesWellAt(x, y);
            int id;
            if (c.r == 12 && c.g == 12 && c.b == 16) { id = 0; c200++; }
            else if (c.r == 0 && c.g == 0 && c.b == 0) { id = 1; c0++; }
            else if (c.r == 12 && c.g == 28 && c.b == 48) { id = 2; c196++; }
            else { id = 3; other++; }
            CHECK(id != 3);  // never leaves the measured family set
            if (prev == id) same++;
            else runs++;
            prev = id;
        }
    }
    // runs = number of segments; mean run = px/runs
    const double mean_run = double(158 * 30) / double(runs ? runs : 1);
    CHECK(mean_run > 2.6);   // iid floor 1.92; fitted law 3.92
    CHECK(mean_run < 6.0);
    const double same_adj = double(same) / double(157 * 30);
    CHECK(same_adj > 0.55);  // iid floor 0.48
    // census shares within a loose band of the G1 slot5 reading (62.5 /
    // 25.7 / 9.0); the port paints palette values, so shares (not rgb) are
    // the comparable statistic.
    const int tot = c200 + c0 + c196;
    CHECK(c200 * 100 / tot > 45 && c200 * 100 / tot < 75);
    CHECK(c0 * 100 / tot > 15 && c0 * 100 / tot < 45);
    CHECK(c196 * 100 / tot > 3 && c196 * 100 / tot < 20);
}

TEST(species_well_generator_is_deterministic_t436) {
    // Stateless law: same (x,y) -> same colour every call (frame-stable,
    // no rng_ state touched — the Star.z discipline).
    for (int i = 0; i < 50; i++) {
        const au::RGB a = au::speciesWellAt(500 + i, 200);
        const au::RGB b = au::speciesWellAt(500 + i, 200);
        CHECK(a.r == b.r && a.g == b.g && a.b == b.b);
    }
    // and decorrelated from the chrome field at the same coords (distinct
    // salt law)
    int diff = 0;
    for (int i = 0; i < 200; i++) {
        const au::RGB w2 = au::speciesWellAt(474 + i % 158, 163 + i / 158);
        const au::RGB t2 = au::textureColourAt(474 + i % 158, 163 + i / 158);
        if (w2.r != t2.r || w2.g != t2.g || w2.b != t2.b) diff++;
    }
    CHECK(diff > 150);  // the two fields are not the same generator
}

}  // namespace
