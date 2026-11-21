// SPDX-License-Identifier: GPL-3.0-or-later

// t394 galaxy-map sidebar chrome law pins. Law source: mapchrome.h
// (windows.txt state-1 records verbatim) + docs/re/_wip_t394.md (the
// pixel measurements on the user-supplied vendor original + the 1starmap
// dims census). The dims-parity test reads the REAL extracted/ascend01/
// data/1starmap.shp (read-only, gate-safe, REQUIRE_DATA).
#include "ui/mapchrome.h"
#include "ui/menulaw.h"  // tA2: kNewgameCosmosRect, kBeginPanelVisual

#include <string>

#include "formats/shp.h"
#include "harness.h"

#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif

namespace {
const std::string kA01 =
    std::string(ASCENDANCY_SOURCE_DIR) + "/extracted/ascend01/data/";
}  // namespace
using namespace ascend::ui;
using ascend::ui::inRect;
using ascend::ui::Pt;

TEST(mapchrome_t394_rail_table_verbatim) {
    // Spot-check the cluster table against windows.txt line cites
    // (full table = mapchrome.cpp).
    using ascend::ui::kMapCtl;
    CHECK(kMapCtl[0].rect.x0 == 495 && kMapCtl[0].rect.y0 == 364 &&
          kMapCtl[0].rect.x1 == 509 && kMapCtl[0].rect.y1 == 394 &&
          kMapCtl[0].shapeFrame == 8 && kMapCtl[0].sendMessage == 51);  // ROTRIGHT ln223
    CHECK(kMapCtl[1].rect.x0 == 479 && kMapCtl[1].shapeFrame == 9 &&
          kMapCtl[1].sendMessage == 50);                                // ROTLEFT ln240
    CHECK(kMapCtl[6].rect.x0 == 596 && kMapCtl[6].rect.x1 == 626 &&
          kMapCtl[6].shapeFrame == 14 && kMapCtl[6].sendMessage == 56); // CENTERHOLO ln325
    CHECK(kMapCtl[7].rect.y0 == 403 && kMapCtl[7].rect.y1 == 433 &&
          kMapCtl[7].shapeFrame == 15 && kMapCtl[7].sendMessage == 57); // TOGLANES ln342
    CHECK(kMapCtl[10].shapeFrame == 18 && kMapCtl[10].sendMessage == 61);  // TOGCOLONIES ln396
    // TURNCOUNT + NEXTTURN pair + RACECONTROLS frame (ln521/539/556/415)
    CHECK(kTurnCount.x0 == 474 && kTurnCount.y0 == 7 && kTurnCount.x1 == 632 &&
          kTurnCount.y1 == 43);
    CHECK(kNextTurnShape == 65 && kNextTurnContShape == 66);
    CHECK(kNextTurnCont.x0 == 557 && kNextTurnCont.y0 == 52 &&
          kNextTurnCont.x1 == 632 && kNextTurnCont.y1 == 82);
    CHECK(kRaceControlsFrame.x0 == 474 && kRaceControlsFrame.y0 == 442 &&
          kRaceControlsFrame.x1 == 632 && kRaceControlsFrame.y1 == 472 &&
          kRaceControlsShape == 19);
}

TEST(mapchrome_t394_race_slots_verbatim) {
    using ascend::ui::kRaceSlots;
    // RACE<N>CONTROL <bit> x0 449 x1 465, x0 = 479 + 22i (ln429-435)
    for (int i = 0; i < 7; i++) {
        CHECK(kRaceSlots[i].bit == (1 << i));
        CHECK(kRaceSlots[i].rect.x0 == 479 + 22 * i);
        CHECK(kRaceSlots[i].rect.x1 == kRaceSlots[i].rect.x0 + 16);
        CHECK(kRaceSlots[i].rect.y0 == 449 && kRaceSlots[i].rect.y1 == 465);
    }
    // Slot 1 == the MEASURED green square on the vendor original
    // (479,448-495,465 green component; _wip_t394.md S3).
    CHECK(ascend::ui::raceSlotFor(Pt{487, 457}).has_value() &&
          *ascend::ui::raceSlotFor(Pt{487, 457}) == 0);
    // Gaps between slots (pitch 22, width 17 inclusive) hit NOTHING.
    CHECK(!ascend::ui::raceSlotFor(Pt{498, 457}).has_value());
    CHECK(!ascend::ui::raceSlotFor(Pt{520, 457}).has_value());
}

TEST(mapchrome_t394_oval_slots_measured) {
    // MEASURED law (_wip_t394.md S3): five green oval components at x
    // 482/513/544/575/606 (pitch 31, ~19 wide), green rows y10..40, all
    // INSIDE TURNCOUNT 474,7-632,43.
    for (int i = 0; i < 5; i++) {
        CHECK(kOvalSlots[i].x0 == 482 + 31 * i);
        CHECK(kOvalSlots[i].x1 - kOvalSlots[i].x0 == 18);
        CHECK(kOvalSlots[i].y0 == 10 && kOvalSlots[i].y1 == 39);
        CHECK(inRect(kTurnCount, Pt{kOvalSlots[i].x0, kOvalSlots[i].y0}));
        CHECK(inRect(kTurnCount, Pt{kOvalSlots[i].x1, kOvalSlots[i].y1}));
    }
}

TEST(mapchrome_t394_shape_dims_parity_law) {
    REQUIRE_DATA();
    // THE DIMS LAW [verified t394 census over every SHAPEFRAME'd map
    // control]: rect (inclusive) == shape dims + 1 in BOTH axes — the
    // bevel margin. Pinned against the real 1starmap.shp for the cluster
    // (k8..k18), the NEXTTURN pair (k65/k66) and RACECONTROLS (k19).
    ascend::formats::ShapeLibrary lib;
    std::string err;
    CHECK(lib.load(kA01 + "1starmap.shp", &err));
    if (lib.count() == 0) return;
    auto parity = [&](int frame, const ascend::ui::Rect& r) {
        if (frame >= int(lib.count())) { CHECK(frame < int(lib.count())); return; }
        const auto& rec = lib.record(frame);
        // tA1 BBOX-DIFF LAW: content == the FULL inclusive rect (the old
        // minus-1 parity was the port mis-reading the R,B corner as dims).
        CHECK(int(rec.width) == r.x1 - r.x0 + 1);
        CHECK(int(rec.height) == r.y1 - r.y0 + 1);
    };
    for (int i = 0; i < ascend::ui::kMapCtlCount; i++)
        parity(kMapCtl[i].shapeFrame, kMapCtl[i].rect);
    parity(kNextTurnShape, ascend::ui::kNextTurnBtn);
    parity(kNextTurnContShape, kNextTurnCont);
    parity(kRaceControlsShape, kRaceControlsFrame);
}

TEST(mapchrome_t394_hit_laws) {
    using ascend::ui::mapCtlFor;
    // Shared-edge law: ROTUP y..379, ROTDOWN 380.. — inclusive edges,
    // distinct rows, no ambiguity.
    CHECK(mapCtlFor(Pt{530, 379}) == ascend::ui::MapCtl::RotUp);
    CHECK(mapCtlFor(Pt{530, 380}) == ascend::ui::MapCtl::RotDown);
    CHECK(mapCtlFor(Pt{610, 420}) == ascend::ui::MapCtl::TogColonies);
    // The gap column 466..473 and the map interior hit nothing.
    CHECK(!mapCtlFor(Pt{470, 420}).has_value());
    CHECK(!mapCtlFor(Pt{200, 200}).has_value());
    // Cluster + strip + panel rects all sit inside 640x480.
    auto fits = [](const ascend::ui::Rect& r) {
        return r.x0 >= 0 && r.y0 >= 0 && r.x1 <= 639 && r.y1 <= 479;
    };
    for (int i = 0; i < ascend::ui::kMapCtlCount; i++)
        CHECK(fits(kMapCtl[i].rect));
    CHECK(fits(kTurnCount));
    CHECK(fits(kNextTurnCont));
    CHECK(fits(kRaceControlsFrame));
}

TEST(mapchrome_tA2_well_edge_law) {
    using namespace ascend::ui;
    // Geometry follows kNewgameCosmosRect {8,8,492,372} (tA2 recess law):
    CHECK(kNewgameCosmosRect.x0 == 8);
    CHECK(kNewgameCosmosRect.y0 == 8);
    CHECK(kNewgameCosmosRect.x1 == 492);
    CHECK(kNewgameCosmosRect.y1 == 372);
    // Recess: row 7 x7..493, cols x7/x493 rows 8..372, ridge rows 373/374.
    CHECK(newgameWellEdgeAt(7, 7));
    CHECK(newgameWellEdgeAt(493, 7));
    CHECK(!newgameWellEdgeAt(6, 7));
    CHECK(!newgameWellEdgeAt(494, 7));
    CHECK(newgameWellEdgeAt(7, 200));
    CHECK(newgameWellEdgeAt(493, 200));
    CHECK(!newgameWellEdgeAt(8, 200));   // well interior is NOT an edge
    CHECK(!newgameWellEdgeAt(492, 200));
    CHECK(newgameWellEdgeAt(250, 373));
    CHECK(newgameWellEdgeAt(250, 374));
    CHECK(!newgameWellEdgeAt(250, 375)); // chrome resumes
    CHECK(!newgameWellEdgeAt(250, 8));
    // RAISED law: ridge row 374 is LIGHTER than row 373 for every census
    // entry pair (dark above, light below).
    const RGB d0 = newgameWellEdgeColourAt(100, 373);
    const RGB l0 = newgameWellEdgeColourAt(100, 374);
    CHECK(int(d0.r) + d0.g + d0.b < int(l0.r) + l0.g + l0.b);
    // tA2-CONT PIN STRENGTHING (mutation-campaign skill rule 4/5): the
    // census WEIGHTS and the chain-anchor law are only observable through
    // band statistics. Chain math: the left/up pull chain preserves the
    // tab MARGINAL distribution (mean AND per-colour shares) in
    // stationarity, so any shift = wrong weights or a chain crossing a
    // band boundary. Row 373 recursing up (the fixed defect) drags the
    // mean to ~50 (witnessed 50.6 pre-fix). Share windows are +-0.10
    // around w/total: n=365..487 with run-inflated variance (mean run
    // ~3-4) gives sd <=0.045; a weight mutation like 169->60 lands at
    // 0.16 (CAUGHT) while mean moves <1.5 (blind). Tolerances cited from
    // vendor means in docs/re/_wip_tA2.md F3.
    {
        auto lum = [](const RGB& c) { return (int(c.r) + c.g + c.b) / 3.0; };
        auto eq = [](const RGB& c, int r, int g, int b) {
            return c.r == uint8_t(r) && c.g == uint8_t(g) && c.b == uint8_t(b);
        };
        double m373 = 0, m374 = 0, m7 = 0;
        int n24 = 0, n61 = 0, n97 = 0, n12_24_34 = 0;
        for (int x = 7; x <= 493; x++) {
            const RGB a = newgameWellEdgeColourAt(x, 373);
            const RGB b = newgameWellEdgeColourAt(x, 374);
            const RGB c = newgameWellEdgeColourAt(x, 7);
            m373 += lum(a); m374 += lum(b); m7 += lum(c);
            if (eq(a, 61, 61, 61)) n61++;
            if (eq(b, 97, 97, 97)) n97++;
            if (eq(c, 24, 24, 24)) n24++;
        }
        m373 /= 487; m374 /= 487; m7 /= 487;
        CHECK(m373 >= 58.0 && m373 <= 71.0);    // vendor 64.5
        CHECK(m374 >= 96.0 && m374 <= 110.0);   // vendor 102.8
        CHECK(m7 >= 17.0 && m7 <= 28.0);        // vendor 24.3
        // Exact-colour shares vs tab marginal w/sum (pull-chain copies
        // exact colours, fresh draws hit the tab exactly: marginal IS the
        // tab's). Windows = expected +-5 sd (run-inflated n_eff ~ n/4).
        CHECK(n24 >= 0.16 * 487 && n24 <= 0.45 * 487);    // 93/306 = 0.304
        CHECK(n61 >= 0.21 * 487 && n61 <= 0.50 * 487);    // 169/482 = 0.351
        CHECK(n97 >= 0.21 * 487 && n97 <= 0.50 * 487);    // 169/481 = 0.351
        double ml = 0, mr = 0;
        int n578 = 0, n000 = 0;
        for (int y = 8; y <= 372; y++) {
            const RGB l = newgameWellEdgeColourAt(7, y);
            const RGB rr = newgameWellEdgeColourAt(493, y);
            ml += lum(l); mr += lum(rr);
            if (eq(l, 5, 7, 8)) n578++;
            if (eq(rr, 0, 0, 0)) n000++;
        }
        ml /= 365; mr /= 365;
        CHECK(ml >= 4.0 && ml <= 9.5);          // vendor 6.5
        CHECK(mr >= 14.0 && mr <= 26.0);        // vendor 22.9
        CHECK(n578 >= 0.25 * 365 && n578 <= 0.55 * 365);  // 90/226 = 0.398
        CHECK(n000 >= 0.27 * 365 && n000 <= 0.57 * 365);  // 102/243 = 0.420
        double mp = 0, mql = 0;
        for (int x = 7; x <= 493; x++) {
            const RGB p = newgamePanelTopAt(x);
            mp += lum(p);
            if (eq(p, 12, 24, 34)) n12_24_34++;
        }
        mp /= 487;
        int npl = 0;
        for (int y = 382; y <= 472; y++) {
            const RGB q = newgamePanelLeftAt(y);
            mql += lum(q);
            if (eq(q, 15, 35, 49)) npl++;
        }
        mql /= 91;
        CHECK(npl >= 0.17 * 91 && npl <= 0.52 * 91);  // 24/74 = 0.324
        CHECK(mp >= 21.0 && mp <= 33.0);        // vendor topline 27.1-36.0
        CHECK(mql >= 27.0 && mql <= 40.0);      // vendor left inset 33.0
        CHECK(n12_24_34 >= 0.19 * 487 && n12_24_34 <= 0.50 * 487);  // 25/74
    }
    // Determinism (no state): same pixel -> same colour, twice.
    {
        const RGB a = newgameWellEdgeColourAt(123, 7), b = newgameWellEdgeColourAt(123, 7);
        CHECK(a.r == b.r && a.g == b.g && a.b == b.b);
    }
    // Recess is DARK: row-7 / col-7 samples stay below the chrome band.
    for (int x = 7; x <= 493; x += 37) {
        const RGB c = newgameWellEdgeColourAt(x, 7);
        CHECK(int(c.r) + c.g + c.b < 330);
    }
    const RGB lc = newgameWellEdgeColourAt(7, 150);
    CHECK(int(lc.r) + lc.g + lc.b < 120);
    // Panel inset law: top/left noise is dark navy, deterministic.
    const RGB pt = newgamePanelTopAt(60);
    CHECK(pt.r < 32 && pt.g < 64 && pt.b < 72);
    const RGB pl = newgamePanelLeftAt(430);
    CHECK(int(pl.r) + pl.g + pl.b > int(pt.r) + pt.g + pt.b);  // navy band
    {
        const RGB a = newgamePanelTopAt(60), b = newgamePanelTopAt(60);
        CHECK(a.r == b.r && a.g == b.g && a.b == b.b);
    }
    // Begin panel: MEASURED visual extent {502,381,632,472} (browser shot
    // +1,+1), strictly inside the windows.txt hit rect kBeginNewGameBtn
    // {494,373,639,472}. Exact values pinned: a shrunk x0 re-paints the
    // chrome gutter x494..501 navy (the landed defect).
    CHECK(kBeginPanelVisual.x0 == 502);
    CHECK(kBeginPanelVisual.y0 == 381);
    CHECK(kBeginPanelVisual.x1 == 632);
    CHECK(kBeginPanelVisual.y1 == 472);
    CHECK(kBeginPanelVisual.x0 > kBeginNewGameBtn.x0);   // gutter stays chrome
    CHECK(kBeginPanelVisual.x1 < kBeginNewGameBtn.x1);
}
