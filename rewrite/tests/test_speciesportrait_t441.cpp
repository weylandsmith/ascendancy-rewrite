// SPDX-License-Identifier: GPL-3.0-or-later

// t441 SPECIES-SCREEN PORTRAIT LAW pins — seams T436-A (count) + T436-B (ring
// index) CLOSED (docs/re/_wip_t441.md T1..T6, law ui/speciesmenu.h).
//
// LAW [measured work/screens/t252/{baseline_game,species_menu_game,species2_game}
// .png, 1:1 640x480, campaign fingerprinted to bank-t251-live1255/45.sav via
// the watcher name law: rows Chamachies(colour 0)/Orfa(1)/Ungooma(6)/Minions(2)]:
//  * the species screen's repaint over the cosmos is EXACTLY FOUR 109x109
//    blobs (9416/9338/9320/8479 px; species2 identical) at centres
//    (235,68) (64,239) (404,238) (234,407) — r=170.0/170.3/169.8/169.0 about
//    (234.2,238.0), angles 89.7/180.3/269.9/0.0 for race rows 0..3.
//  * COUNT = one portrait per race-table row (word[state+0xd88]); the player
//    (row 0) HAS a portrait; elimination does NOT remove it (Minions: ships=0,
//    rows-list "Extinct", ring present). t436's home-star centring and
//    "player has no portrait" are REFUTED (baseline band under every slot is
//    90% pure black; star markers are 64-105 px away from 3 of 4 slots).
//  * RING INDEX = race colour byte (row+8, FUN_000232ec). Ungooma is row 2
//    with colour 6: the capture's ORANGE ring (k6) sits at ITS slot and the
//    GOLD ring (k2 = Minions' colour) at row 3's — owner%7 predicts gold for
//    Ungooma and is REFUTED (T436-B).
#include <cmath>

#include "ui/menulaw.h"
#include "ui/speciesmenu.h"
#include "game/campaign.h"
#include "harness.h"

#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif

// Exported shim from test_campaign.cpp (t291 idiom): seeded campaign with a
// chosen aiCount/starCount and the full vendor table wiring. GLOBAL scope —
// a declaration inside an anonymous namespace would define a new symbol.
namespace ascend { namespace game { class Campaign; } }
ascend::game::Campaign makeCampaignSized(unsigned seed, int aiCount, int starCount);

namespace {
namespace au = ascend::ui;
namespace ag = ascend::game;

TEST(species_slot_geometry_matches_the_t252_measurement_t441) {
    // Measured centres vs the law on kCosmosWnd{7,7,465,472} (centre 236,239):
    // law gives (236,69)/(66,239)/(236,409)/(406,239) — max delta 2 px against
    // (235,68)/(64,239)/(234,407)/(404,238) (the 2 px is the vendor field
    // extent, not the law).
    const au::Rect fld{7, 7, 465, 472};
    const int mx[4] = {235, 64, 234, 404}, my[4] = {68, 239, 407, 238};
    for (int k = 0; k < 4; k++) {
        const au::Pt p = au::speciesPortraitSlot(fld, k, 4);
        CHECK(std::abs(p.x - mx[k]) <= 2);
        CHECK(std::abs(p.y - my[k]) <= 2);
        // Every slot sits on the measured r=170 circle about the field centre.
        const double dx = p.x - 236.0, dy = p.y - 239.0;
        CHECK(std::abs(std::hypot(dx, dy) - 170.0) <= 1.5);
    }
    CHECK(au::kSpeciesRingRadius == 170);
    // Cardinal order law: top, left, bottom, right (angles 90+90k measured
    // 89.7/180.3/269.9/0.0 — counterclockwise on a y-down screen).
    const au::Pt t = au::speciesPortraitSlot(fld, 0, 4), l = au::speciesPortraitSlot(fld, 1, 4),
                   b = au::speciesPortraitSlot(fld, 2, 4), r = au::speciesPortraitSlot(fld, 3, 4);
    CHECK(t.y < l.y && b.y > l.y);   // top above, bottom below the mid row
    CHECK(l.x < t.x && r.x > t.x);   // left of / right of the mid column
}

TEST(species_portrait_count_is_every_owner_including_the_player_t441) {
    // T436-A: the ring set is the RACE TABLE, not the known-AI set. The law's
    // consumer (ui.cpp) iterates owners 0..ownerCount()-1 (capped at the 7
    // vendor rows); the count must therefore equal ownerCount, and owner 0
    // (the player) must be in range. Pin the surface that produces it.
    REQUIRE_DATA();
    ag::Campaign camp = makeCampaignSized(7u, 3, 50);
    CHECK(camp.ownerCount() == 4);  // player + 3 AI == the t252 campaign shape
    // speciesSpecnumOfOwner covers EVERY owner incl. the player at index 0 —
    // unlike speciesMenuRows (known-AI rows only). If the consumer ever
    // switches back to the rows list, the player's slot silently disappears;
    // this pins the difference.
    const auto spec = au::speciesSpecnumOfOwner(camp, nullptr);
    CHECK(int(spec.size()) == camp.ownerCount());
    CHECK(spec[0] == camp.playerSpecies());  // -1 human default
    // The rows list (known-AI) is a DIFFERENT, smaller set on a fresh campaign.
    CHECK(int(au::speciesMenuRows(camp, nullptr).size()) <
          int(spec.size()));
}

TEST(species_ring_index_is_the_colour_byte_not_owner_mod_7_t441) {
    // T436-B. FUN_000232ec assigns DISTINCT colours; for 7 owners the
    // assignment (seed 0x12e10, chip 0 — the port's default call, and the
    // value the vendor's own init call shape produces) is
    //   {0,1,4,3,5,2,6}: owners 2,3,4,5 all have colour != owner%7.
    // The port must index racering by the COLOUR BYTE. Witness: at least one
    // owner in the 7-owner range must break the owner%7 identity — if a
    // future "simplification" re-derives ring = owner%7, the t252 capture
    // (Ungooma row2 colour 6 = orange ring) is violated.
    unsigned char out[8] = {0, 0, 0, 0, 0, 0, 0, 0};
    unsigned int lcg = 0x12e10u;
    au::assignRaceColours(0, 7, &lcg, out);
    CHECK(out[0] == 0);
    int differs = 0;
    for (int i = 0; i < 7; i++) {
        CHECK(out[i] < 7);                       // 7 = neutral is never drawn here
        for (int j = i + 1; j < 7; j++) CHECK(out[i] != out[j]);  // distinctness
        if (out[i] != i % 7) differs++;
    }
    CHECK(differs >= 1);  // the colour table is NOT the identity — owner%7 is wrong
    CHECK(out[2] != 2);   // the exact t252 discriminator class (row 2, colour 6)
}

TEST(species_slot_law_is_deterministic_and_distinct_for_seven_rows_t441) {
    const au::Rect fld{7, 7, 465, 472};
    // Deterministic (frame-stable, pure).
    const au::Pt a = au::speciesPortraitSlot(fld, 5, 7), b = au::speciesPortraitSlot(fld, 5, 7);
    CHECK(a.x == b.x && a.y == b.y);
    // nslots=4 reproduces the MEASURED pitch exactly: row k+1 is 90 deg
    // counterclockwise of row k about the field centre.
    for (int k = 0; k < 4; k++) {
        const au::Pt p = au::speciesPortraitSlot(fld, k, 4);
        const au::Pt q = au::speciesPortraitSlot(fld, k + 1, 4);
        const double pa = std::atan2(-(p.y - 239.0), p.x - 236.0) * 180 / M_PI;
        const double qa = std::atan2(-(q.y - 239.0), q.x - 236.0) * 180 / M_PI;
        double d = qa - pa;
        if (d > 180) d -= 360;
        if (d < -180) d += 360;
        CHECK(std::abs(d - 90.0) <= 0.5);
    }
    // A 7-row campaign (the vendor max, NUMCONTROLS 7) draws SEVEN portraits
    // per the count law; slots must be DISTINCT (the even-distribution reading
    // of the unmeasured n>4 tail — a fixed 90-deg pitch would put rows 4..6
    // back onto rows 0..2).
    for (int i = 0; i < 7; i++)
        for (int j = i + 1; j < 7; j++) {
            const au::Pt p = au::speciesPortraitSlot(fld, i, 7), q = au::speciesPortraitSlot(fld, j, 7);
            CHECK(!(p.x == q.x && p.y == q.y));
        }
}

}  // namespace
