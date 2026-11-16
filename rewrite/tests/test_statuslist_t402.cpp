// SPDX-License-Identifier: GPL-3.0-or-later

// t402 PLANETS LIST law pins: the static.txt word tables joined against the
// SHIPPED file, the two line-assembly templates byte-exact, the days law
// (FUN_0x47010 arithmetic incl. the sentinel), the t249 membership law over a
// seeded campaign, the 3-row scroll window, and the row hit-map. Citations:
// docs/re/statuslist law block (planets-ui.md t402), docs/re/_wip_t402.md,
// docs/re/selfplay.md t248/t249.
#include "ui/statuslist.h"

#include <cstdio>
#include <fstream>
#include <optional>
#include <sstream>
#include <memory>
#include <string>
#include <vector>

#include "game/campaign.h"
#include "ui/planetwin.h"  // formatPlanetHeader (the #151 template)
#include "harness.h"

#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif

namespace {
namespace au = ascend::ui;
namespace ag = ascend::game;
const std::string kRepo = ASCENDANCY_SOURCE_DIR;

// Shipped static.txt quoted strings in file order (the getter law: getter(n)
// == nth quoted string; docs/re/aicode.md). Comments (# n - m) skipped.
std::vector<std::string> staticTxtStrings() {
    std::ifstream f(kRepo + "/extracted/ascend00/static.txt", std::ios::binary);
    std::vector<std::string> out;
    std::string line;
    while (std::getline(f, line)) {
        if (!line.empty() && line.back() == '\r') line.pop_back();
        if (line.empty() || line[0] == '/') continue;
        if (line.front() != '"' || line.back() != '"') continue;
        std::string s = line.substr(1, line.size() - 2);
        // unescape \n as the loader does (aicode.md: quote-strip + \n unescape)
        size_t p = 0;
        while ((p = s.find("\\n", p)) != std::string::npos)
            s.replace(p, 2, "\n");
        out.push_back(s);
    }
    return out;
}

// Seeded campaign over the SHIPPED data (test_planetwin_t276 fixture
// pattern; REQUIRE_DATA() gates the caller when vendor data is absent).
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

// ---- word tables vs the shipped file --------------------------------------
TEST(statuslist_word_tables_match_static_txt_t402) {
    // Data-optional law (t396): without static.txt the vector is EMPTY and the
    // s[41+i] reads below are OOB UB -> run_tests SIGSEGV on data-less clones
    // (MEASURED t403 on export /tmp/pubpush-t403: FAIL line 100 then 139).
    REQUIRE_DATA();
    const auto s = staticTxtStrings();
    CHECK(s.size() >= 57);
    // #41-45 sizes, #46-56 types (0-indexed quoted strings).
    static const char* kSizes[5] = {"Tiny", "Small", "Medium", "Large",
                                    "Enormous"};
    static const char* kTypes[11] = {"Husk",     "Primordial", "Congenial",
                                     "Eden",     "Mineral",    "Supermineral",
                                     "Chapel",   "Cathedral",  "Special",
                                     "Tycoon",   "Cornucopia"};
    for (int i = 0; i < 5; i++) {
        CHECK(s[41 + i] == kSizes[i]);
        const char* w = au::statusSizeWord(i);
        CHECK(w && s[41 + i] == w);
    }
    for (int i = 0; i < 11; i++) {
        CHECK(s[46 + i] == kTypes[i]);
        const char* w = au::statusTypeWord(i);
        CHECK(w && s[46 + i] == w);
    }
    // Out of domain -> nullptr (refuse-not-crash; no fabricated word).
    CHECK(au::statusSizeWord(5) == nullptr);
    CHECK(au::statusSizeWord(-1) == nullptr);
    CHECK(au::statusTypeWord(11) == nullptr);
}

// ---- the refcap assembly (the vendor's own pinned screenshot) -------------
TEST(statuslist_line1_refcap_assembly_t402) {
    // docs/assets/refcap/original-planet-view.png shows "Xerxes I (Enormous
    // Supermineral Planet)" -> size 4, type 5.
    CHECK(au::statusLine1("Xerxes I", 4, 5) ==
          "Xerxes I (Enormous Supermineral Planet)");
    // The t3 capture row 1: "Oslo II (Large Cathedral Planet)" -> 3, 7.
    CHECK(au::statusLine1("Oslo II", 3, 7) == "Oslo II (Large Cathedral Planet)");
    // Self-managed leg (0x5077f): name REPLACED, suffix still assembled.
    CHECK(au::statusLine1("Vega IV", 2, 1, true) ==
          "Self-Managed (Medium Primordial Planet)");
    // Refusal keeps the bare name (no invented words).
    CHECK(au::statusLine1("Vega IV", 9, 0) == "Vega IV");
}

// ---- line 2: the project suffix law ---------------------------------------
TEST(statuslist_line2_project_law_t402) {
    // "No Project" verbatim; #142 appended ONLY with pop==used.
    CHECK(au::statusLine2NoProject(false) == "No Project");
    CHECK(au::statusLine2NoProject(true) ==
          "No Project   (No Free Population)");  // three spaces, byte-exact
    // Sentinel -> " - No Progress"
    CHECK(au::statusLine2("Factory", -1) == "Building Factory - No Progress");
    // Cited plural pair: singular iff days == 1 (0x5084e/0x50855).
    CHECK(au::statusLine2("Factory", 1) ==
          "Building Factory - 1 day until completion");
    CHECK(au::statusLine2("Factory", 2) ==
          "Building Factory - 2 days until completion");
    // Item flags bit 2 -> suffix leg SKIPPED entirely (0x507fc).
    CHECK(au::statusLine2("Colony Base", -1, true) == "Building Colony Base");
    CHECK(au::statusLine2("Colony Base", 7, true) == "Building Colony Base");
}

// ---- the days arithmetic (FUN_0x47010) ------------------------------------
TEST(statuslist_days_law_t402) {
    CHECK(au::statusDays(100, 0, 0) == -1);    // IND<=0 -> 0xffff sentinel
    CHECK(au::statusDays(100, 0, -3) == -1);
    CHECK(au::statusDays(100, 0, 10) == 10);   // exact division
    CHECK(au::statusDays(100, 0, 30) == 4);    // ceil(100/30)
    CHECK(au::statusDays(100, 95, 10) == 1);   // last partial day
    // PAID case: the vendor formula is (n-1)/ind+1 with C truncation toward
    // zero: n=0 -> (-1)/10 == 0 -> +1 == 1 (the display shows "1 day" the
    // turn the project completes; verified arithmetic shape of 0x47010).
    CHECK(au::statusDays(100, 100, 10) == 1);
    CHECK(au::statusDays(0, 0, 5) == 1);
    CHECK(au::statusDays(100, 140, 10) == 0);  // far-overpaid clamps at 0
    CHECK(au::statusDays(30, 0, 7) == 5);      // ceil(30/7)
}

// ---- membership + window (t249 law) over a seeded campaign -----------------
TEST(statuslist_membership_and_window_t402) {
    REQUIRE_DATA();
    auto copt = seededCampaign();
    CHECK(copt.has_value());
    if (!copt) return;
    ag::Campaign& c = *copt;
    const auto all = au::statusPlanets(c, ag::kPlayer);
    // Membership: EXACTLY the planets of player-owned stars (t249 filter).
    int expect = 0;
    for (const auto& s : c.galaxy().stars)
        if (c.starOwner(s.id) == ag::kPlayer)
            expect += static_cast<int>(s.planets.size());
    CHECK(int(all.size()) == expect);
    CHECK(expect > au::kStatusVisibleRows);  // the window is load-bearing
    // Order: (star, index) ascending.
    for (size_t i = 1; i < all.size(); i++)
        CHECK(all[i - 1].star < all[i].star ||
              (all[i - 1].star == all[i].star &&
               all[i - 1].planetIndex <= all[i].planetIndex));
    // Window: always 3 rows inside the range; clamps at both ends; the LAST
    // window ends with the last planet (no gap, no repeat).
    CHECK(au::statusWindow(all, 0).size() == size_t(au::kStatusVisibleRows));
    CHECK(au::statusWindow(all, -5).size() == size_t(au::kStatusVisibleRows));
    const int maxS = expect - au::kStatusVisibleRows;
    CHECK(au::statusWindow(all, maxS + 99).size() ==
          size_t(au::kStatusVisibleRows));
    CHECK(au::statusWindow(all, 0)[0].star == all[0].star);
    CHECK(au::statusWindow(all, maxS)[2].star == all.back().star);
    CHECK(au::statusWindow(all, maxS)[2].planetIndex == all.back().planetIndex);
    // Small list (< 3): window == list.
    std::vector<au::StatusRowKey> two{{3, 0}, {3, 1}};
    CHECK(au::statusWindow(two, 0).size() == 2);
    CHECK(au::statusWindow(two, 4).size() == 2);
    std::vector<au::StatusRowKey> none;
    CHECK(au::statusWindow(none, 0).empty());
}

// ---- header counts (screen-open snapshot law, t248/t249) -------------------
TEST(statuslist_header_counts_t402) {
    REQUIRE_DATA();
    auto copt = seededCampaign();
    CHECK(copt.has_value());
    if (!copt) return;
    ag::Campaign& c = *copt;
    const auto h = au::statusHeaderFor(c, ag::kPlayer);
    int planets = 0, systems = 0;
    for (const auto& s : c.galaxy().stars)
        if (c.starOwner(s.id) == ag::kPlayer) {
            ++systems;
            planets += static_cast<int>(s.planets.size());
        }
    CHECK(h.planets == planets);
    CHECK(h.systems == systems);
    // The format round-trip through the planetwin law (double space).
    CHECK(au::formatPlanetHeader("Minions", 1, 1) ==
          "Minions  (1 Planet Occupied, 1 System Controlled)");
}

// ---- row geometry (measured pitch 112.6 +- 0.2, three markers) -------------
TEST(statuslist_row_geometry_t402) {
    CHECK(au::kStatusVisibleRows == 3);
    CHECK(au::kStatusRowPitch >= 112 && au::kStatusRowPitch <= 113);
    const int top = au::kStatusInterior.y0;
    CHECK(au::statusRowAt(au::Pt{300, top}, top).value_or(-9) == 0);
    CHECK(au::statusRowAt(au::Pt{300, top + au::kStatusRowPitch - 1}, top)
              .value_or(-9) == 0);
    CHECK(au::statusRowAt(au::Pt{300, top + au::kStatusRowPitch}, top)
              .value_or(-9) == 1);
    CHECK(au::statusRowAt(
                au::Pt{300, top + 3 * au::kStatusRowPitch - 1}, top)
                .value_or(-9) == 2);
    CHECK(!au::statusRowAt(au::Pt{300, top + 3 * au::kStatusRowPitch}, top));
    CHECK(!au::statusRowAt(au::Pt{300, top - 1}, top));
    // Three rows fit the measured interior exactly once (46..457 = 412 px;
    // 3 x 112 = 336 <= 412 < 4 x 112 — the witness shows THREE, not four).
    CHECK(3 * au::kStatusRowPitch <= au::kStatusInterior.y1 -
                                        au::kStatusInterior.y0 + 1);
    CHECK(4 * au::kStatusRowPitch > au::kStatusInterior.y1 -
                                        au::kStatusInterior.y0 + 1);
}
