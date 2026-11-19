// SPDX-License-Identifier: GPL-3.0-or-later

// t428 PLANET-SCREEN STRIP pins (laws docs/re/_wip_t428.md F5/F9):
//   1. The three gauge panels blit planres/planind/planpro record
//      selector[i] at the windows.txt TYPE-29 rect origins (7,7 / 123,7 /
//      239,7 — all 108x100); selectors inside the 21-record domain
//      (clamp0..20 law, planets-ui.md S3 + the S2 dispatch order).
//   2. Library census (F9, byte-level): each gauge lib parses to EXACTLY
//      21 records of 107x99 (the rect-fill witness); 17np (9 records)
//      must NOT conform.
//   3. The pop grid anchors at the PLPOP rect origin (355,7) with the
//      t263 loop law: cell i at ((i%10)*10, (i/10)*10)+origin, selector
//      == record in 1..3, count == cap.
//   4. Out-of-domain star: zeroed plan, never crash.
#include <cstdio>
#include <memory>
#include <optional>
#include <string>
#include <vector>

#include "formats/shp.h"
#include "game/campaign.h"
#include "ui/planetstrip.h"
#include "harness.h"

namespace {
namespace au = ascend::ui;
namespace ag = ascend::game;
namespace af = ascend::formats;
const std::string kRepo = ASCENDANCY_SOURCE_DIR;
const std::string kData = kRepo + "/extracted/ascend01/data/";

// Campaign fixture (shape verbatim from test_planetview_t406).
std::optional<ag::Campaign> seededCampaign() {
    static ag::StarStats stats;
    static std::vector<std::string> names;
    static ag::ResearchTree tree;
    static std::vector<ag::PlanetItem> items;
    static std::vector<ag::Gizmo> gizmos;
    static std::vector<ag::DipFile> ai;
    static bool loaded = false;
    if (!loaded) {
        std::string e;
        auto st = ag::StarStats::load(kRepo + "/extracted/ascend00/starstat.txt", &e);
        if (!st) return std::nullopt;
        stats = *st;
        names = ag::loadStarNames(kRepo + "/extracted/ascend00/names.txt", &e);
        tree = ag::ResearchTree::loadFromFile(kRepo + "/extracted/ascend00/restree.txt", e);
        items = ag::loadPlanItems(kRepo + "/extracted/ascend00/planitem.txt", e);
        gizmos = ag::loadGizmos(kRepo + "/extracted/ascend00/gizmos.txt", e);
        for (int i = 0; i < 6; ++i) {
            ag::DipFile df;
            char path[256];
            std::snprintf(path, sizeof(path), "%s/extracted/ascend00/race%02d.dip",
                          ASCENDANCY_SOURCE_DIR, i);
            if (!df.loadFromFile(path, &e)) return std::nullopt;
            ai.push_back(std::move(df));
        }
        loaded = !items.empty();
    }
    if (!loaded) return std::nullopt;
    ag::CampaignConfig cfg;
    cfg.seed = 2024;
    cfg.aiCount = 6;
    cfg.freeForAll = true;
    ag::MapConfig mc;
    mc.seed = 2024;
    std::string err;
    ag::Galaxy g = ag::MapGenerator(mc, stats, names).generate();
    if (g.stars.empty()) return std::nullopt;
    auto camp = std::make_optional<ag::Campaign>(cfg, g, &tree, items, gizmos, ai, &err);
    if (!err.empty()) return std::nullopt;
    return camp;
}
}  // namespace

TEST(planetstrip_gauge_rects_t428) {
    REQUIRE_DATA();
    auto camp = seededCampaign();
    CHECK(camp.has_value());
    if (!camp) return;
    // The windows.txt rects, verbatim (planetwin.cpp table lines cited).
    const au::Rect want[3] = {{7, 7, 114, 106}, {123, 7, 230, 106},
                              {239, 7, 346, 106}};
    const auto sp = au::stripPlanFor(*camp, 0);
    for (int i = 0; i < 3; i++) {
        CHECK(sp.gauges[i].lib == i);  // dispatch order PLRES/PLIND/PLPRO
        const auto& r = sp.gauges[i].rect;
        CHECK(r.x0 == want[i].x0);
        CHECK(r.y0 == want[i].y0);
        CHECK(r.x1 == want[i].x1);
        CHECK(r.y1 == want[i].y1);
        CHECK(sp.gauges[i].rec >= 0 &&
              sp.gauges[i].rec < au::kStripGaugeRecords);
    }
    // 108x100 rect vs 107x99 record: the record fills the panel.
    CHECK(want[0].x1 - want[0].x0 + 1 == 108);
    CHECK(want[0].y1 - want[0].y0 + 1 == 100);
    // Selector law: RES/IND compressed ^0.75, PROS identity (S3).
    const auto cw = camp->channelWordsFor(0);
    CHECK(sp.gauges[0].rec == au::gaugeSelector(cw.res));
    CHECK(sp.gauges[1].rec == au::gaugeSelector(cw.ind));
    CHECK(sp.gauges[2].rec == au::prosSelector(cw.pros));
}

TEST(planetstrip_library_census_t428) {
    REQUIRE_DATA();
    for (int i = 0; i < 3; i++) {
        std::string err;
        if (!au::stripGaugeLibraryConforms(kData + au::kStripGaugeLibs[i],
                                          &err)) {
            std::printf("  census %s: %s\n", au::kStripGaugeLibs[i],
                        err.c_str());
        }
        CHECK(au::stripGaugeLibraryConforms(kData + au::kStripGaugeLibs[i],
                                            &err));
    }
    // Control: 17np (9 records) must NOT conform to the gauge census.
    std::string err;
    CHECK(!au::stripGaugeLibraryConforms(kData + "17np.shp", &err));
}

TEST(planetstrip_pop_anchor_t428) {
    REQUIRE_DATA();
    auto camp = seededCampaign();
    CHECK(camp.has_value());
    if (!camp) return;
    const auto sp = au::stripPlanFor(*camp, 0);
    const auto bands = camp->popBandsFor(0);
    CHECK(int(sp.popCells.size()) == int(bands.size()));
    bool ok = true;
    for (size_t i = 0; i < sp.popCells.size(); i++) {
        const auto& c = sp.popCells[i];
        ok = ok &&
             c.pos.x == au::kPopGridOrigin.x + int(i % 10) * au::kPopSlotPitch &&
             c.pos.y == au::kPopGridOrigin.y + int(i / 10) * au::kPopSlotPitch &&
             c.selector >= 1 && c.selector <= 3 && c.record == c.selector;
    }
    CHECK(ok);
    // The anchor IS the PLPOP rect origin (windows.txt ln1587 block).
    CHECK(au::kPopGridOrigin.x == 355 && au::kPopGridOrigin.y == 7);
}

TEST(planetstrip_star_domain_t428) {
    REQUIRE_DATA();
    auto camp = seededCampaign();
    CHECK(camp.has_value());
    if (!camp) return;
    const auto sp = au::stripPlanFor(*camp, -1);
    CHECK(sp.popCells.empty());
    CHECK(sp.projectItem == -1);
    // Owned star: projectItem mirrors pendingItemFor (the +0x54 analog).
    const auto sp0 = au::stripPlanFor(*camp, 0);
    CHECK(sp0.projectItem == camp->pendingItemFor(0));
}
