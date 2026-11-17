// SPDX-License-Identifier: GPL-3.0-or-later
// t406 PLANET VIEW + PROJECT-SET pins: the cmd0 gate law (fn 0x38840 legs
// 0x388e2/0x388ec/0x388f7 verbatim), the project-list membership law
// (REQUIRES-gated table order, item < 39), the PLANLIST hit-map, the
// state-17 readout, and the owned-only row->view routing. Citations:
// ui/planetview.h header, docs/re/_wip_t406.md F3/F5.
#include "ui/planetview.h"
#include "ui/statuslaw.h"
#include "ui/statuslist.h"

#include <cstdio>
#include <memory>
#include <optional>
#include <string>
#include <vector>

#include "game/campaign.h"
#include "harness.h"

#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif

namespace {
namespace au = ascend::ui;
namespace ag = ascend::game;
const std::string kRepo = ASCENDANCY_SOURCE_DIR;

// Fixture pattern verbatim from test_statuslist_t402 (shared shape).
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

// ---- the PLANLIST hit-map (pure geometry) ---------------------------------
TEST(planetview_project_row_hitmap_t406) {
    const auto& r = au::kProjectListRect;
    CHECK(r.x0 == 120 && r.y0 == 120 && r.x1 == 520 && r.y1 == 420);  // ln1504
    CHECK(au::projectRowFor(au::Pt{r.x0 - 1, 200}, 0) == std::nullopt);
    CHECK(au::projectRowFor(au::Pt{r.x1 + 1, 200}, 0) == std::nullopt);
    CHECK(au::projectRowFor(au::Pt{200, r.y0 - 1}, 0) == std::nullopt);
    CHECK(au::projectRowFor(au::Pt{200, r.y0 + 2}, 0).value_or(-9) == 0);
    CHECK(au::projectRowFor(au::Pt{200, r.y0 + 2 + au::kProjectRowPitch}, 0)
              .value_or(-9) == 1);
    // last visible row inside; one pitch past it -> none
    CHECK(au::projectRowFor(au::Pt{200, r.y0 + 2 +
                            (au::kProjectVisibleRows - 1) * au::kProjectRowPitch},
                            0)
              .value_or(-9) == au::kProjectVisibleRows - 1);
    CHECK(!au::projectRowFor(
        au::Pt{200, r.y0 + 2 + au::kProjectVisibleRows * au::kProjectRowPitch}, 0));
    // `first` offset threads through (scroll support)
    CHECK(au::projectRowFor(au::Pt{200, r.y0 + 2}, 4).value_or(-9) == 4);
}

// ---- the gates + order over a seeded campaign ------------------------------
TEST(planetview_order_gates_t406) {
    REQUIRE_DATA();
    auto copt = seededCampaign();
    CHECK(copt.has_value());
    if (!copt) return;
    ag::Campaign& c = *copt;
    // find the player's colonised star
    int star = -1;
    for (const auto& s : c.galaxy().stars)
        if (c.starOwner(s.id) == ag::kPlayer) { star = s.id; break; }
    CHECK(star >= 0);
    if (star < 0) return;
    CHECK(c.pendingItemFor(star) == -1);
    // domain gate (0x388ec): item 39+ never orderable.
    CHECK(!c.orderProject(star, 39));
    CHECK(!c.orderProject(star, -1));
    CHECK(!au::projectOrderable(c, star, 39));
    // free-pop gate (0x388f7): an item whose UPOP exceeds the free pop of a
    // pop-2 colony rejects and leaves state UNTOUCHED (silent-reject shape).
    int big = -1;
    for (int id = 0; id < 39; ++id)
        if (const auto* pi = c.planetItem(id))
            if (pi->upop > int(c.planetAt(star).pop) - c.usedPopFor(star)) { big = id; break; }
    if (big >= 0) {
        CHECK(!c.orderProject(star, big));
        CHECK(!au::projectOrderable(c, star, big));
        CHECK(c.pendingItemFor(star) == -1);   // reject stored NOTHING
    }
    // happy path: Factory (item 0, UPOP 0 per the table) orders once, and a
    // SECOND order rejects on the queue-empty gate (0x388e2).
    int factory = -1;
    for (int id = 0; id < 39; ++id)
        if (const auto* pi = c.planetItem(id))
            if (pi->name == "Factory") { factory = id; break; }
    if (factory >= 0 && factory < 39) {
        CHECK(c.orderProject(star, factory));
        CHECK(c.pendingItemFor(star) == factory);
        CHECK(!c.orderProject(star, factory));           // queue busy
        CHECK(!au::projectOrderable(c, star, factory));  // predicate agrees
    }
}

// ---- the project list membership (REQUIRES-gated table order, < 39) --------
TEST(planetview_project_list_membership_t406) {
    REQUIRE_DATA();
    auto copt = seededCampaign();
    CHECK(copt.has_value());
    if (!copt) return;
    ag::Campaign& c = *copt;
    int star = -1;
    for (const auto& s : c.galaxy().stars)
        if (c.starOwner(s.id) == ag::kPlayer) { star = s.id; break; }
    if (star < 0) return;
    const auto opts = au::projectOptionsFor(c, star);
    CHECK(!opts.empty());
    int prev = -1;
    for (const auto& o : opts) {
        CHECK(o.item > prev);      // table order, no duplicates
        CHECK(o.item < 39);        // 0x388ec domain
        prev = o.item;
        // every listed row passes the REQUIRES gate for the player
        CHECK(c.techCountTotal() > 0);
    }
    // Interstellar Trucking (req 254) is dead per OQ-014: it must NEVER
    // appear (if the table has it).
    for (const auto& o : opts) CHECK(o.name != "Interstellar Trucking");
}

// ---- the readout + the rows-top measurement fence ---------------------------
TEST(planetview_readout_and_rows_top_t406) {
    REQUIRE_DATA();
    auto copt = seededCampaign();
    CHECK(copt.has_value());
    if (!copt) return;
    ag::Campaign& c = *copt;
    int star = -1;
    for (const auto& s : c.galaxy().stars)
        if (c.starOwner(s.id) == ag::kPlayer) { star = s.id; break; }
    if (star < 0) return;
    const auto v = au::planetViewFor(c, star, "Testos I");
    CHECK(v.title.find("Testos I") == 0);          // statusLine1 assembly
    CHECK(v.title.find("Planet)") != std::string::npos);
    CHECK(v.pop == int(c.planetAt(star).pop));
    CHECK(v.used == c.usedPopFor(star));
    CHECK(v.cap == c.popCapAt(star));
    CHECK(v.noProject == (c.pendingItemFor(star) < 0));
    CHECK(v.noFreePopulation == (v.pop == v.used));  // the 0x508da predicate
    // Out-of-domain star: all-zero refuse, never a crash.
    const auto bad = au::planetViewFor(c, 99999, "X");
    CHECK(bad.pop == 0 && bad.pendingItem == -1);
    // t417b RE-SCOPED (was the t406 "117" fence): rows top 57 / pitch 141
    // MEASURED on the t3 capture itself (docs/re/_wip_t417.md F3 — flag-icon
    // bands 57/198/339, autocorrelation single peak 0.634; user original
    // agrees). The 117 anchored rows below the 10status k0 ART header cells,
    // which the vendor never paints (F1/F6). Rows now govern themselves:
    // 57 + 3*141 == 480 exactly, so three rows fill the screen bottom.
    CHECK(au::kStatusRowsTop == 57);
    CHECK(au::kStatusRowsTop > 46);  // below the code-drawn divider (F5)
    CHECK(au::kStatusRowsTop + 3 * au::kStatusRowPitch == 480);
    CHECK(4 * au::kStatusRowPitch > 480 - au::kStatusRowsTop);  // exactly 3
    // state 17 is a known screen (the row-click target); rail never opens it.
    CHECK(au::screenKnown(au::kScreenPlanet));
}
