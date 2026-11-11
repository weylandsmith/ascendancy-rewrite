// SPDX-License-Identifier: GPL-3.0-or-later

// t202b DEMOLISH CHANNEL PIN — the two victim scans + the +0x4c used-pop
// law inside the AI build evaluator FUN_0003f130.
// Law source: docs/re/_wip_t202.md S1/S3/S5/S11/S13 FINAL (verbatim disasm
// work/ai_selector_disasm.txt 0x3f178..0x3f209, 0x3f354..0x3f418; corpus
// fire-rates scripts/r202_triage_census.py — over-cap LIVE 220/2900, always
// used==pop==cap; used-pop model scripts/r202d_usedpop_models.py M4
// 2760/2900). Item indices/columns per scripts/r202b_item_table.py.
#include "harness.h"
#include "game/campaign.h"

namespace ag = ascend::game;

// Factory (UPOP 1, MPOP 0, REQUIRES 255), Colony Base (id 5: MPOP 2,
// REQUIRES 5), Ship (23) and Outpost (20) / Tubes (21) flags&0x40 rows.
ag::Campaign makeCampaignForDemolish(unsigned seed);  // test_campaign.cpp

TEST(campaign_demolish_pickers_t202b) {
    REQUIRE_DATA();
    // ---- OVER-CAP VICTIM 0x3f1bb..0x3f1c7 (pure statics) ----------------
    // (O1) empty slots / empty planet -> no candidate (the original takes
    //      the 0x3f20b assert/recalc RETURN path).
    CHECK(ag::Campaign::overCapDemolishPick({}, {}, {}) == -1);
    CHECK(ag::Campaign::overCapDemolishPick({-1, -1}, {0, 0}, {1, 1}) == -1);
    // (O2) Colony Base (item 5) SKIPPED even as the only item — the
    //      over-cap channel never kills the home.
    CHECK(ag::Campaign::overCapDemolishPick({5}, {0}, {1}) == -1);
    // (O3) MPOP != 0 skipped (0x3f1bb cmp byte[item+3],0 jne next): Habitat
    //      MPOP 3, Metroplex MPOP 2 -> no candidate among them.
    CHECK(ag::Campaign::overCapDemolishPick({3, 4}, {3, 2}, {1, 1}) == -1);
    // (O4) UPOP == 0 NEVER wins: best init 0 @0x3f17c, strict >.
    CHECK(ag::Campaign::overCapDemolishPick({31, 31}, {0, 0}, {0, 0}) == -1);
    // (O5) STRICT largest UPOP; ties keep the FIRST cell.
    CHECK(ag::Campaign::overCapDemolishPick({0, 0, 0}, {0, 0, 0}, {1, 2, 1}) == 1);
    CHECK(ag::Campaign::overCapDemolishPick({0, 0, 0}, {0, 0, 0}, {3, 2, 3}) == 0);
    CHECK(ag::Campaign::overCapDemolishPick({0, 0, 0}, {0, 0, 0}, {2, 2, 3}) == 2);
    // (O6) mixed field: skipped items are NOT scored, only excluded — the
    //      lone MPOP-0 item wins even against larger hidden UPOPs.
    CHECK(ag::Campaign::overCapDemolishPick({5, 3, 0}, {2, 3, 0}, {9, 9, 1}) == 2);

    // ---- MIN-REQUIRES SWEEP VICTIM 0x3f354..0x3f3d5 ---------------------
    // (S1) NO item-5 skip: a Colony Base CAN be swept.
    CHECK(ag::Campaign::minRequiresDemolishPick({5}, {0}, {5}, 1) == 0);
    // (S2) MPOP >= margin skipped; MPOP < margin participates (margin =
    //      cap - pop, the FREE-cell figure [esp+0xcc]).
    //      margin 1: Habitat mpop3 out, CB mpop2 out, Factory mpop0 in.
    CHECK(ag::Campaign::minRequiresDemolishPick({3, 5, 0}, {3, 2, 0}, {26, 5, 255}, 1) == 2);
    //      margin 3: CB mpop2 < 3 now participates, REQUIRES 5 < 255 wins.
    CHECK(ag::Campaign::minRequiresDemolishPick({3, 5, 0}, {3, 2, 0}, {26, 5, 255}, 3) == 1);
    // (S3) STRICT smallest REQUIRES, ties keep the FIRST cell.
    CHECK(ag::Campaign::minRequiresDemolishPick({0, 0, 0}, {0, 0, 0}, {7, 3, 3}, 5) == 1);
    // (S4) The 0xFF sentinel REQUIRES PARTICIPATES (0x3f354 mov ecx,0x1869f
    //      never prunes: any u8 < 99999). A lone 0xFF wins; 0xFF-pair keeps
    //      the first cell; a real REQUIRES 0 beats it only when EARLIER? NO:
    //      strict <, so Factory(req 255) then Shipyard(req 0) -> Shipyard.
    CHECK(ag::Campaign::minRequiresDemolishPick({0}, {0}, {255}, 1) == 0);
    CHECK(ag::Campaign::minRequiresDemolishPick({0, 0}, {0, 0}, {255, 255}, 1) == 0);
    CHECK(ag::Campaign::minRequiresDemolishPick({0, 22}, {0, 0}, {255, 0}, 1) == 1);
    // (S5) empty slots skipped; the running best survives them.
    CHECK(ag::Campaign::minRequiresDemolishPick({-1, 22, -1}, {0, 0, 0}, {0, 9, 0}, 2) == 1);
}

TEST(campaign_used_pop_item_sum_t202b) {
    REQUIRE_DATA();
    // +0x4c = UPOP SUM over slotted items (r202d model M4, 2760/2900 exact;
    // 140-row residual = Automation shape M3): item 23 (Ship) and
    // flags&0x40 rows (20 Outpost, 21 Transport Tubes) excluded; the
    // governor-35 Automation bonus (@0x38e16, row-35 UPOP) kept.
    // const_cast on planetAt is the established harness idiom (t45).
    auto c = makeCampaignForDemolish(2024);
    int star = -1;
    for (int s = 0; s < static_cast<int>(c.galaxy().stars.size()); ++s)
        if (c.starOwner(s) >= 1) { star = s; break; }
    CHECK(star >= 0);
    auto& ps = const_cast<ag::PlanetState&>(c.planetAt(star));
    CHECK(ps.items.size() == 1);            // CB-only home (t40 law)
    CHECK(c.usedPopFor(star) == 1);          // Colony Base UPOP 1
    ps.items.push_back(23);                  // Ship: EXCLUDED
    CHECK(c.usedPopFor(star) == 1);
    ps.items.push_back(20);                  // Outpost flags&0x40: EXCLUDED
    ps.items.push_back(21);                  // Tubes flags&0x40: EXCLUDED
    CHECK(c.usedPopFor(star) == 1);
    for (int k = 0; k < 4; ++k) ps.items.push_back(0);  // Factory UPOP 1 each
    CHECK(c.usedPopFor(star) == 5);
    ps.governor = 35;                        // Automation branch @0x38e16
    CHECK(c.usedPopFor(star) == 6);
    ps.governor = -1;                        // cleanly reversible
    CHECK(c.usedPopFor(star) == 5);
    ps.pop = 5;                              // keep the corpus law used<=pop
    // The t199 band FORMULA is untouched by the used-reading upgrade:
    // SEL(i) = 1 + [i>=used] + [i>=pop] over i < cap.
    std::vector<int> bands;
    ag::Campaign::popBands(5, 5, 7, bands);
    int c1 = 0, c2 = 0, c3 = 0;
    for (int v : bands) { c1 += v == 1; c2 += v == 2; c3 += v == 3; }
    CHECK(c1 == 5 && c2 == 0 && c3 == 2);
}

TEST(campaign_over_cap_demolish_e2e_t202b) {
    REQUIRE_DATA();
    // END-TO-END over-cap channel: an AI planet at used == pop == cap (the
    // 220/2900 corpus shape, r202_triage_census) demollishes ONE Factory
    // within a single advance(), the 0x3f1fb recheck passes (used' < pop —
    // exactly why the original CONTINUES via 0x3f22f), and the same
    // selector run reaches the queue.
    auto c = makeCampaignForDemolish(2024);
    int star = -1;
    for (int s = 0; s < static_cast<int>(c.galaxy().stars.size()); ++s)
        if (c.starOwner(s) >= 1) { star = s; break; }
    CHECK(star >= 0);
    auto& ps = const_cast<ag::PlanetState&>(c.planetAt(star));
    for (int k = 0; k < 5; ++k) ps.items.push_back(0);  // + CB = 6 UPOP
    ps.capBase = 4;                          // cap = 4 + CB MPOP 2 = 6
    ps.pop = 6;                              // used==pop==cap (corpus law)
    CHECK(c.usedPopFor(star) == 6);
    CHECK(c.popCapAt(star) == 6);
    c.advance();
    CHECK(ps.items.size() == 5);             // one Factory gone
    bool cbAlive = false;
    int factories = 0;
    for (int it : ps.items) { if (it == 5) cbAlive = true; if (it == 0) ++factories; }
    CHECK(cbAlive);                          // 0x3f1a8 skip item 5
    CHECK(factories == 4);
    CHECK(c.usedPopFor(star) == 5);          // recheck value used' = 5 < 6
}

TEST(campaign_barren_sweep_demolishes_cb_e2e_t202b) {
    REQUIRE_DATA();
    // SWEEP CHANNEL END-TO-END through the 0x3f252 pre-triage gate: a planet
    // with BOTH surface cells occupied (eNR == 0 < 2 -> triage RUNS; the
    // healthy-planet skip needs eNR>=2) is swept even though it is NOT
    // over-cap. The min-REQUIRES scan has NO item-5 skip, so the Colony Base
    // (REQUIRES 5) beats the 0xFF-requires Factory and is the victim; the
    // Factory survives. Post-demolish shared gate 0x3f41e passes (cell 0 is
    // empty non-rock) so the run reaches chain+scorer.
    auto c = makeCampaignForDemolish(2024);
    int star = -1;
    for (int s = 0; s < static_cast<int>(c.galaxy().stars.size()); ++s)
        if (c.starOwner(s) >= 1) { star = s; break; }
    CHECK(star >= 0);
    auto& ps = const_cast<ag::PlanetState&>(c.planetAt(star));
    ps.surfaceCells = 2;
    ps.cellClasses[0] = 1;
    ps.cellClasses[1] = 1;
    ps.items.push_back(0);                   // Factory REQUIRES 255
    ps.itemCells[0] = 0;                     // CB on cell 0 (explicit)
    ps.itemCells.push_back(1);               // Factory on cell 1
    ps.capBase = 8;                          // cap = 8 + CB MPOP 2 = 10
    ps.pop = 7;                              // used 2 << pop: free pop exists
    CHECK(c.usedPopFor(star) == 2);
    CHECK(c.popCapAt(star) == 10);
    c.advance();
    bool cbGone = true;
    int factories = 0;
    for (int it : ps.items) { if (it == 5) cbGone = false; if (it == 0) ++factories; }
    CHECK(cbGone);                           // CB swept (REQUIRES 5 minimal)
    CHECK(factories == 1);                   // Factory (255) survives
}
