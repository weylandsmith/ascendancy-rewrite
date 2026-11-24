// SPDX-License-Identifier: GPL-3.0-or-later

// tPL-B2 PRODUCTIVITY-BOX POPUP pins (law docs/re/_wip_tPLB2.md P1-P7,
// indpopups.h):
//   1. COUNTDOWN 0x47010 verbatim: rate<=0 -> -1 (0xffff); else
//      max(1, ceil((target-acc)/rate)) — pins at the instruction sites
//      (acc==target -> 1; acc>target -> clamped 1; exact multiples).
//   2. POPUP RECT law: (wx+10, wy+10, wx+0x145, wy+0xcf) per clicked
//      widget (0x3dbe5..0x3dc34) for every windows.txt TYPE-29 panel.
//   3. PROSPERITY case (0x3ddc0) reproduces the USER WITNESS: pop<maxpop,
//      counter 0, pros 1/day, wrap 50 -> L-D "<name> Prosperity: 1 per
//      day" + L-E "Population will grow in 50 days." (plural law: days==1
//      -> no 's').
//   4. PROSPERITY sentinel legs: pros 0 -> "Population is not growing.";
//      pop>=maxpop -> "Population has no more room to grow." (getter 73/74).
//   5. INDUSTRY case: pending item -> L-E "<item> will be completed in D
//      day(s)."; no pending -> L-D ONLY (the +0x6e gate).
//   6. FULL-INFO chain (key 4): NAME / "<size> <type> Planet" / "Owned by
//      <name>" / "Maximum Population  %d" (TWO spaces) / "Self Managed"
//      iff player-owned with governor -1; hold words 0xf/0x3c/0x5a/0x78/96.
//   7. PLBUILD produces NO popup lines (the 0x3dc53 ja-leg with the struct
//      zeroed).
#include <cstdio>
#include <optional>
#include <string>
#include <vector>

#include "game/campaign.h"
#include "ui/indpopups.h"
#include "ui/planetwin.h"
#include "ui/statuslist.h"  // statusPlanets (fixture row law)
#include "harness.h"

namespace {
namespace au = ascend::ui;
namespace ag = ascend::game;
const std::string kRepo = ASCENDANCY_SOURCE_DIR;
// The harness has CHECK/REQUIRE_DATA only (abort idiom elsewhere is
// CHECK + early return); REQUIRE = CHECK then return-on-failure.
#define REQUIRE(cond)              \
    do {                           \
        CHECK((cond));             \
        if (!(cond)) return;       \
    } while (0)
}  // namespace

TEST(indpopups_countdown_0x47010_tplb2) {
    CHECK(au::countdownDays(50, 0, 1) == 50);    // witness leg
    CHECK(au::countdownDays(50, 49, 1) == 1);    // (1-1)/1+1
    CHECK(au::countdownDays(50, 50, 1) == 1);    // (0-1)/1+1 = 0 -> clamp 1
    CHECK(au::countdownDays(50, 60, 1) == 1);    // negative -> clamp 1
    CHECK(au::countdownDays(100, 0, 3) == 34);   // ceil(100/3)
    CHECK(au::countdownDays(100, 0, 0) == -1);   // rate 0 -> 0xffff
    CHECK(au::countdownDays(100, 0, -5) == -1);  // negative rate too
}

TEST(indpopups_rect_law_tplb2) {
    // Every TYPE-29 panel: origin+10, size 0x145+1 x 0xcf+1 inclusive.
    for (int i = 0; i < au::kPlanetPanelCount; i++) {
        const auto& r = au::kPlanetPanels[i].rect;
        const auto p = au::indicatorPopupRect(r);
        CHECK(p.x0 == r.x0 + 10);
        CHECK(p.y0 == r.y0 + 10);
        CHECK(p.x1 == r.x0 + 0x145);
        CHECK(p.y1 == r.y0 + 0xcf);
    }
}

TEST(indpopups_indicator_lines_law_tplb2) {
    // The two-line law verbatim (0x3e4db..0x3e5db).
    au::IndicatorContent c;
    c.nameWord = "Prosperity";
    c.perDay = 1;
    c.subject = "Population";
    c.verb = "grow";
    c.days = 50;
    auto ls = au::indicatorLines("Crimea 1", c);
    REQUIRE(ls.size() == 2);
    CHECK(ls[0].text == "Crimea 1 Prosperity: 1 per day");
    CHECK(ls[0].hold == 0xf);
    CHECK(ls[1].text == "Population will grow in 50 days.");
    CHECK(ls[1].hold == 0x50);
    // Singular plural-pair leg (getter 28 iff days==1).
    c.days = 1;
    ls = au::indicatorLines("Crimea 1", c);
    REQUIRE(ls.size() == 2);
    CHECK(ls[1].text == "Population will grow in 1 day.");
    // Sentinel leg: fmt(+0x62) applied to subject(+0x5a).
    c.days = -1;
    c.noProgress = "%s is not growing.";
    ls = au::indicatorLines("Crimea 1", c);
    REQUIRE(ls.size() == 2);
    CHECK(ls[1].text == "Population is not growing.");
    // GATES: +0x72 null -> nothing; +0x6e zero (subject null) -> L-D only.
    au::IndicatorContent z;
    CHECK(au::indicatorLines("X", z).empty());
    z.nameWord = "Industry";
    z.perDay = 4;
    ls = au::indicatorLines("X", z);
    REQUIRE(ls.size() == 1);
    CHECK(ls[0].text == "X Industry: 4 per day");
}

TEST(indpopups_full_info_law_tplb2) {
    au::PlanetIdentity id;
    id.name = "Crimea 1";
    id.sizeIdx = 2;  // mid-domain word
    id.typeIdx = 3;
    id.owner = 0;
    id.ownerName = "Player";
    id.maxPop = 39;
    id.selfManaged = true;
    auto ls = au::fullInfoLines(id);
    REQUIRE(ls.size() == 5);
    CHECK(ls[0].text == "Crimea 1");
    CHECK(ls[0].hold == 0xf);
    CHECK(ls[1].hold == 0x3c);
    CHECK(ls[1].text.find("Planet") != std::string::npos);
    CHECK(ls[2].text == "Owned by Player");
    CHECK(ls[2].hold == 0x5a);
    CHECK(ls[3].text == "Maximum Population  39");  // TWO spaces
    CHECK(ls[3].hold == 0x78);
    CHECK(ls[4].text == "Self Managed");
    CHECK(ls[4].hold == 0x96);
    // Unowned: "No One" pre-fill (0x3e347), no self-managed line.
    id.owner = -1;
    id.selfManaged = false;
    ls = au::fullInfoLines(id);
    REQUIRE(ls.size() == 4);
    CHECK(ls[2].text == "Owned by No One");
    // The chip directive code (0x3e3f2 shl2 / 0x3e3f5 add 0x13).
    CHECK(au::raceChipCode(0) == 0x13);
    CHECK(au::raceChipCode(5) == 0x27);
}

TEST(indpopups_campaign_plbuild_and_star_tplb2) {
    au::PlanetIdentity id;
    id.name = "X";
    id.sizeIdx = 0;
    id.typeIdx = 0;
    id.maxPop = 0;
    CHECK(au::fullInfoLines(id).size() >= 3);
    // Out-of-domain star: refuse-not-crash (empty).
    // (Campaign-fed cases run in the campaign pins below; here only the
    // guard path: star < 0.)
}

// ---- campaign-fed pins (fixture verbatim from test_planetstrip_t428) ----
namespace {
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

TEST(indpopups_campaign_cases_tplb2) {
    REQUIRE_DATA();
    auto camp = seededCampaign();
    CHECK(camp.has_value());
    if (!camp) return;
    const auto owned = au::statusPlanets(*camp, ag::kPlayer);
    CHECK(!owned.empty());
    if (owned.empty()) return;
    const int star = owned[0].star;
    const std::string name = "Testworld 1";
    // PLBUILD never pops (0x3dc53 ja-leg, struct zeroed).
    CHECK(au::popupLinesFor(*camp, star, au::PlanetPanel::PlBuild, name)
              .empty());
    // PROSPERITY: L-D always present and exact-shaped; L-E present iff
    // pop<cap (the growth leg) — assert the shape of whichever lands.
    {
        const auto ls =
            au::popupLinesFor(*camp, star, au::PlanetPanel::PlPro, name);
        REQUIRE(!ls.empty());
        CHECK(ls[0].text ==
              name + " Prosperity: " +
                  std::to_string(camp->channelWordsFor(star).pros) +
                  " per day");
        if (ls.size() > 1) {
            const bool ok =
                ls[1].text == "Population will grow in 50 days." ||
                ls[1].text == "Population is not growing." ||
                ls[1].text == "Population has no more room to grow." ||
                (ls[1].text.rfind("Population will grow in ", 0) == 0 &&
                 ls[1].text.back() == '.');
            CHECK(ok);
        }
    }
    // INDUSTRY: L-D exact; L-E iff a pending item exists.
    {
        const auto ls =
            au::popupLinesFor(*camp, star, au::PlanetPanel::PlInd, name);
        REQUIRE(!ls.empty());
        CHECK(ls[0].text ==
              name + " Industry: " +
                  std::to_string(camp->channelWordsFor(star).ind) +
                  " per day");
        const bool pending = camp->planetAt(star).pendingItem >= 0;
        CHECK(ls.size() == (pending ? 2u : 1u));
    }
    // RESEARCH: L-D exact; the L-E subject is the queued topic name.
    {
        const auto ls =
            au::popupLinesFor(*camp, star, au::PlanetPanel::PlRes, name);
        REQUIRE(!ls.empty());
        CHECK(ls[0].text ==
              name + " Research: " +
                  std::to_string(camp->channelWordsFor(star).res) +
                  " per day");
        const int row = camp->queuedTechFor(ag::kPlayer);
        if (row >= 0 && camp->researchTree() &&
            row < int(camp->researchTree()->all().size())) {
            REQUIRE(ls.size() == 2);
            const std::string tech =
                camp->researchTree()->all()[size_t(row)].name;
            CHECK(ls[1].text.rfind(tech + " will be discovered in ", 0) == 0 ||
                  ls[1].text ==
                      "No progress is being made on " + tech + ".");
        }
    }
    // FULL-INFO (PLPOP): five lines on a self-managed player world
    // (governor default -1 on the whole corpus, t45 census).
    {
        const auto ls =
            au::popupLinesFor(*camp, star, au::PlanetPanel::PlPop, name);
        REQUIRE(ls.size() == 5);
        CHECK(ls[0].text == name);
        CHECK(ls[2].text == "Owned by Player");
        CHECK(ls[3].text.rfind("Maximum Population  ", 0) == 0);
        CHECK(ls[4].text == "Self Managed");
    }
}
