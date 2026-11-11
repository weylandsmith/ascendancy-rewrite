// SPDX-License-Identifier: GPL-3.0-or-later

// t276 PLANETALLOC composition pins: the five-panel table joined against the
// SHIPPED windows.txt (t264 precedent), the dispatch-key remap law, the
// header format strings joined byte-exact against shipped static.txt, the
// gauge wiring through Campaign::channelWordsFor, and the poppanel panel-
// containment composition. Citations: docs/re/planets-ui.md S1-S4,
// docs/re/selfplay.md t246/t248, docs/re/ui-runtime.md §6c, docs/re/shp.md
// S23.3/S23.4, working notes docs/re/_wip_t276.md.
#include "ui/planetwin.h"

#include <cstdio>
#include <fstream>
#include <map>
#include <sstream>
#include <string>
#include <vector>
#include <optional>

#include "game/campaign.h"
#include "ui/layout.h"
#include "ui/poppanel.h"
#include "harness.h"

#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif

namespace {
namespace au = ascend::ui;
namespace ag = ascend::game;
const std::string kRepo = ASCENDANCY_SOURCE_DIR;

// ---- shipped-file readers (deliberately dumb: the file IS the law) --------
// windows.txt record: TYPE line precedes NAME; the keys we read all follow
// NAME before the next NAME line (verified block order, _wip S1).
struct WinRec {
    int type = -1;
    int x0 = 0, y0 = 0, x1 = 0, y1 = 0;
    int msg = -1, p1 = -1;
    std::string help;
};
std::map<std::string, WinRec> loadWindows(const std::string& path) {
    std::map<std::string, WinRec> out;
    std::ifstream f(path);
    std::string line, cur;
    WinRec rec;
    bool haveCur = false;
    int lastType = -1;  // TYPE line is immediately before its NAME line
    auto flush = [&]() {
        if (haveCur && !cur.empty()) out[cur] = rec;
        cur.clear();
        rec = WinRec();
        haveCur = false;
    };
    auto keyval = [&](const std::string& s, std::string& k, std::string& v) {
        size_t a = s.find_first_not_of(" \t\r");
        if (a == std::string::npos) return false;
        size_t b = s.find_first_of(" \t\r", a);
        if (b == std::string::npos) return false;
        k = s.substr(a, b - a);
        size_t c = s.find_first_not_of(" \t\r", b);
        v = c == std::string::npos ? "" : s.substr(c);
        while (!v.empty() && (v.back() == ' ' || v.back() == '\t' || v.back() == '\r'))
            v.pop_back();
        return true;
    };
    while (std::getline(f, line)) {
        std::string k, v;
        if (!keyval(line, k, v)) continue;
        if (k == "TYPE") {
            flush();
            lastType = std::stoi(v);
        } else if (k == "NAME") {
            flush();
            cur = v;
            rec.type = lastType;
            haveCur = true;
        } else if (haveCur) {
            if (k == "X0") rec.x0 = std::stoi(v);
            else if (k == "Y0") rec.y0 = std::stoi(v);
            else if (k == "X1") rec.x1 = std::stoi(v);
            else if (k == "Y1") rec.y1 = std::stoi(v);
            else if (k == "SENDMESSAGE") rec.msg = std::stoi(v);
            else if (k == "SENDPARAM1") rec.p1 = std::stoi(v);
            else if (k == "HELPINDEX") rec.help = v;
        }
    }
    flush();
    return out;
}
// static.txt quoted-record scan: records alternate outside/inside quotes;
// zero escaped quotes verified (_wip S3: 382 quote chars == 2x191).
std::vector<std::string> loadStaticRecords(const std::string& path) {
    std::vector<std::string> recs;
    std::ifstream f(path, std::ios::binary);
    std::stringstream ss;
    ss << f.rdbuf();
    const std::string s = ss.str();
    bool in = false;
    std::string cur;
    for (char c : s) {
        if (c == '"') {
            if (in) recs.push_back(cur);
            cur.clear();
            in = !in;
        } else if (in) {
            cur.push_back(c);
        }
    }
    return recs;
}
}  // namespace

TEST(planetwin_panel_table_matches_windows_txt_t276) {
    auto w = loadWindows(kRepo + "/extracted/ascend00/windows.txt");
    const char* names[5] = {"PLRES", "PLIND", "PLPRO", "PLPOP", "PLBUILD"};
    for (int i = 0; i < 5; ++i) {
        auto it = w.find(names[i]);
        if (it == w.end()) { CHECK(false); return; }
        const WinRec& r = it->second;
        const au::PlanetPanelInfo& p = au::kPlanetPanels[i];
        CHECK(r.type == 29);
        CHECK(p.rect.x0 == r.x0);
        CHECK(p.rect.y0 == r.y0);
        CHECK(p.rect.x1 == r.x1);
        CHECK(p.rect.y1 == r.y1);
        CHECK(p.sendMessage == r.msg);
        CHECK(p.sendParam1 == r.p1);
        CHECK(std::string(p.helpIndex) == r.help);
    }
    // Parent + list children (verbatim constants vs file).
    auto parent = w.find("PLANETALLOC");
    if (parent == w.end()) { CHECK(false); return; }
    CHECK(parent->second.type == 7);
    CHECK(parent->second.msg == 3);
    CHECK(au::kPlanetAllocRect.x0 == parent->second.x0);
    CHECK(au::kPlanetAllocRect.y0 == parent->second.y0);
    CHECK(au::kPlanetAllocRect.x1 == parent->second.x1);
    CHECK(au::kPlanetAllocRect.y1 == parent->second.y1);
    auto list = w.find("PLANLIST");
    auto sq = w.find("PLSQUARE");
    if (list == w.end() || sq == w.end()) { CHECK(false); return; }
    CHECK(list->second.type == 10);
    CHECK(au::kPlanListRect.x0 == list->second.x0 &&
          au::kPlanListRect.y0 == list->second.y0 &&
          au::kPlanListRect.x1 == list->second.x1 &&
          au::kPlanListRect.y1 == list->second.y1);
    CHECK(sq->second.type == 14);
    CHECK(au::kPlSquareRect.x0 == sq->second.x0 &&
          au::kPlSquareRect.y0 == sq->second.y0 &&
          au::kPlSquareRect.x1 == sq->second.x1 &&
          au::kPlSquareRect.y1 == sq->second.y1);
}

TEST(planetwin_panel_order_and_disjointness_t276) {
    // File order == left-to-right: X0 strictly increasing...
    for (int i = 1; i < au::kPlanetPanelCount; ++i)
        CHECK(au::kPlanetPanels[i].rect.x0 > au::kPlanetPanels[i - 1].rect.x1);
    // ...with the uniform 9 px gutter between the first four pairs, and the
    // hit-test agreeing with containment for every panel centre + corners.
    for (int i = 0; i < au::kPlanetPanelCount; ++i) {
        const au::Rect& r = au::kPlanetPanels[i].rect;
        // Inclusive-edge widths: the four gauge/pop panels are 108/108/108/
        // 100 px wide (PLPOP 355..454 == 100 px INCLUSIVE, the t254 grid
        // anchor), PLBUILD is the wide one (463..632 == 170 px).
        CHECK(r.x1 - r.x0 == (i == 3 ? 99 : i == 4 ? 169 : 107));
        CHECK(au::planetPanelFor({r.x0, r.y0}) == static_cast<au::PlanetPanel>(i));
        CHECK(au::planetPanelFor({r.x1, r.y1}) == static_cast<au::PlanetPanel>(i));
        CHECK(au::planetPanelFor({(r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2}) ==
              static_cast<au::PlanetPanel>(i));
    }
    CHECK(au::kPlanetPanels[1].rect.x0 - au::kPlanetPanels[0].rect.x1 == 9);
    CHECK(au::kPlanetPanels[2].rect.x0 - au::kPlanetPanels[1].rect.x1 == 9);
    CHECK(au::kPlanetPanels[3].rect.x0 - au::kPlanetPanels[2].rect.x1 == 9);
    CHECK(au::kPlanetPanels[4].rect.x0 - au::kPlanetPanels[3].rect.x1 == 9);
    // Gutter points and list-child interiors hit NO panel.
    CHECK(!au::planetPanelFor({118, 50}).has_value());   // PLRES|PLIND gutter
    CHECK(!au::planetPanelFor({300, 250}).has_value());  // PLSQUARE interior
    CHECK(!au::planetPanelFor({300, 400}).has_value());  // below the strip
    CHECK(!au::planetPanelFor({639, 479}).has_value());  // parent corner
}

TEST(planetwin_dispatch_key_law_t276) {
    // Remap table verbatim (planets-ui.md S2): gauge params pass through,
    // param 4 -> 3, SENDMESSAGE 51 -> 4, out-of-range -> default (-1).
    CHECK(au::paintKey(50, 0) == 0);  // PLRES
    CHECK(au::paintKey(50, 1) == 1);  // PLIND
    CHECK(au::paintKey(50, 2) == 2);  // PLPRO
    CHECK(au::paintKey(50, 4) == 3);  // PLPOP remap at 0x3cc1c
    CHECK(au::paintKey(51, 1) == 4);  // PLBUILD override at 0x3cc29
    // THE LOAD-BEARING COLLISION: without the msg-51 override PLBUILD's
    // SENDPARAM1 1 would paint as PLIND. Message 51 must beat param 1.
    CHECK(au::paintKey(51, 1) != au::paintKey(50, 1));
    // 51 overrides ANY param (the cmp is on the message dword, not the key).
    CHECK(au::paintKey(51, 0) == 4);
    CHECK(au::paintKey(51, 4) == 4);
    // Unreachable/default territory.
    CHECK(au::paintKey(50, 5) == -1);
    CHECK(au::paintKey(3, 9) == -1);
    // The five shipped panels key 0..4 EXACTLY ONCE each (a composition with
    // two panels on one key or a missing case is a wiring bug).
    int seen[5] = {0, 0, 0, 0, 0};
    for (int i = 0; i < au::kPlanetPanelCount; ++i) {
        int k = au::paintKeyFor(static_cast<au::PlanetPanel>(i));
        CHECK(k >= 0 && k <= 4);
        if (k >= 0 && k <= 4) seen[k]++;
        CHECK(k == i);  // and case order == enum order == file order
    }
    for (int i = 0; i < 5; ++i) CHECK(seen[i] == 1);
}

TEST(planetwin_header_strings_match_static_txt_t276) {
    auto recs = loadStaticRecords(kRepo + "/extracted/ascend00/static.txt");
    if (recs.size() != 191) { CHECK(recs.size() == 191); return; }  // live 0xbf law
    // 0-INDEXED getter convention (selfplay.md t246 pins #151).
    CHECK(std::string(au::kFmtPlanetsOccupied) == recs[151]);
    CHECK(std::string(au::kFmtShips) == recs[152]);
    CHECK(std::string(au::kStrUnderConstruction) == recs[147]);
    CHECK(std::string(au::kStrBeingRefitted) == recs[148]);
    CHECK(std::string(au::kStrPlayerSpecies) == recs[153]);
    CHECK(std::string(au::kPluralNone) == recs[28]);
    CHECK(std::string(au::kPluralS) == recs[29]);
    // The double space is byte-exact in the shipped file (not a rendering
    // artifact) — assert it directly so a "helpful" reflow fails here.
    CHECK(std::string(recs[151]).substr(2, 3) == "  (");
    CHECK(std::string(recs[152]).substr(2, 3) == "  (");
    // #149/#150: the FILE bytes carry a literal backslash-n; the module
    // constant carries a real newline (loader-interprets-\n, [inferred]).
    CHECK(recs[149] == "\\nMoving to Planet");
    CHECK(recs[150] == "\\nMoving to Starlane");
    CHECK(au::movingToPlanetText() == "\nMoving to Planet");
    CHECK(au::movingToStarlaneText() == "\nMoving to Starlane");
}

TEST(planetwin_header_format_output_t276) {
    // Output shapes pinned to the two live vision reads:
    // "Chamachies (60 Planets Occupied, 26 Systems Controlled)" (t246/t248
    // era header screenshot) and "Chamachies (25 Ships, 12 more allowed)"
    // (ui-runtime.md §6c). Pluralization here is the [inferred] rewrite
    // default (singular iff ==1, pair #28/#29) — the format strings above
    // are the cited part; these two witnesses are plural.
    CHECK(au::formatPlanetHeader("Chamachies", 60, 26) ==
          "Chamachies  (60 Planets Occupied, 26 Systems Controlled)");
    CHECK(au::formatShipHeader("Chamachies", 25, 12) ==
          "Chamachies  (25 Ships, 12 more allowed)");
    // Singular branch (rewrite default; no live witness, honest boundary).
    CHECK(au::formatPlanetHeader("Vega", 1, 1) ==
          "Vega  (1 Planet Occupied, 1 System Controlled)");
    CHECK(au::formatShipHeader("Vega", 1, 0) == "Vega  (1 Ship, 0 more allowed)");
    CHECK(au::constructionText("Vega IV") == "Under Construction at Vega IV");
    CHECK(au::refitText("Vega IV") == "Being Refitted at Vega IV");
    CHECK(au::pluralSuffix(0) == std::string("s"));  // 0 is plural per ==1 rule
}

TEST(planetwin_gauge_wiring_t276) {
    // Wire check, not a re-pin of t199: for a SEEDED campaign the
    // composition's three selectors must equal gaugeSelector(res),
    // gaugeSelector(ind), prosSelector(pros) of the SAME channelWordsFor
    // triple the S3 table names (+0x46/+0x44/+0x48), stay in 0..20, and the
    // IND selector must sit on the ladder bounds for the stored level.
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
        if (!st) { CHECK(st.has_value()); return; }
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
            if (!df.loadFromFile(path, &e)) { CHECK(false); return; }
            ai.push_back(std::move(df));
        }
        loaded = !items.empty();
        CHECK(loaded);
        if (!loaded) return;
    }
    ag::CampaignConfig cfg;
    cfg.seed = 2024;
    cfg.aiCount = 6;
    cfg.freeForAll = true;
    ag::MapConfig mc;
    mc.seed = 2024;
    std::string err;
    ag::Galaxy g = ag::MapGenerator(mc, stats, names).generate();
    ag::Campaign camp(cfg, g, &tree, items, gizmos, ai, &err);
    if (!err.empty()) { CHECK(err.empty()); return; }
    int checked = 0;
    for (int s = 0; s < int(g.stars.size()); ++s) {
        const auto w = camp.channelWordsFor(s);
        au::PlanetGauges g = au::planetGaugesFor(camp, s);
        CHECK(g.res == au::gaugeSelector(w.res));
        CHECK(g.ind == au::gaugeSelector(w.ind));
        CHECK(g.pros == au::prosSelector(w.pros));
        CHECK(g.res >= 0 && g.res <= 20);
        CHECK(g.ind >= 0 && g.ind <= 20);
        CHECK(g.pros >= 0 && g.pros <= 20);
        // Ladder bound: selector s for level L implies firstLevel(s) <= L
        // (the S3 first-level table is monotone; t199 pinned exactness).
        if (w.ind >= 0) CHECK(au::gaugeFirstLevelFor(g.ind) <= w.ind || g.ind == 20);
        ++checked;
    }
    CHECK(checked > 0);
}

TEST(planetwin_poppanel_containment_t276) {
    // Composition leg: feeding popPanelFor the PLPOP panel origin must keep
    // every painted cell (plus the 9x9 max sprite, shp.md S23.3) inside the
    // windows.txt panel rect — the t33 cap clamp (<=100 slots == 10x10 grid)
    // is what guarantees it; this test catches an origin/rect drift.
    static ag::StarStats stats;
    static std::vector<std::string> names;
    static ag::ResearchTree tree;
    static std::vector<ag::PlanetItem> items;
    static std::vector<ag::Gizmo> gizmos;
    static bool loaded = false;
    if (!loaded) {
        std::string e;
        auto st = ag::StarStats::load(kRepo + "/extracted/ascend00/starstat.txt", &e);
        if (!st) { CHECK(st.has_value()); return; }
        stats = *st;
        names = ag::loadStarNames(kRepo + "/extracted/ascend00/names.txt", &e);
        tree = ag::ResearchTree::loadFromFile(kRepo + "/extracted/ascend00/restree.txt", e);
        items = ag::loadPlanItems(kRepo + "/extracted/ascend00/planitem.txt", e);
        gizmos = ag::loadGizmos(kRepo + "/extracted/ascend00/gizmos.txt", e);
        loaded = !items.empty();
        CHECK(loaded);
        if (!loaded) return;
    }
    ag::CampaignConfig cfg;
    cfg.seed = 2024;
    cfg.aiCount = 0;  // empty dip list -> ctor errors unless count is 0
    ag::MapConfig mc;
    mc.seed = 2024;
    std::string err;
    ag::Galaxy g = ag::MapGenerator(mc, stats, names).generate();
    ag::Campaign camp(cfg, g, &tree, items, gizmos, {}, &err);
    if (!err.empty()) { CHECK(err.empty()); return; }
    const au::Pt origin{au::kPlPopRect.x0, au::kPlPopRect.y0};
    int cells = 0;
    for (int s = 0; s < int(g.stars.size()); ++s) {
        for (const au::PopCell& c : au::popPanelFor(camp, s, origin)) {
            // Sprite box top-left c.pos, max dims 9x9 -> inclusive bottom-
            // right must stay within the panel (x1 454, y1 106).
            CHECK(c.pos.x >= origin.x && c.pos.x + 8 <= au::kPlPopRect.x1);
            CHECK(c.pos.y >= origin.y && c.pos.y + 8 <= au::kPlPopRect.y1);
            ++cells;
        }
    }
    CHECK(cells > 0);
}

TEST(planetwin_plbuild_icon_t276) {
    // CITED point: item 34 ("Scientist Takeover", income-law.md S6h) -> k34
    // (shp.md S23.4 live MAD 1.5). Domain edges: planitem.shp has 40 records.
    auto icon = au::plbuildIcon(34);
    CHECK(icon.has_value());
    if (icon) {
        CHECK(icon->record == 34);
        CHECK(std::string(icon->shapeFile) == "data\\planitem.shp");
    }
    CHECK(!au::plbuildIcon(-1).has_value());
    CHECK(!au::plbuildIcon(40).has_value());
    // The shape path is a gwshare library (gwshare.txt:37 lists it) — join
    // the basename against the shipped gwshare list so a typo'd path fails.
    std::ifstream f(kRepo + "/extracted/ascend00/gwshare.txt");
    std::string line;
    bool found = false;
    while (std::getline(f, line)) {
        while (!line.empty() && (line.back() == '\r' || line.back() == '\n'))
            line.pop_back();
        if (line == "data\\planitem.shp") { found = true; break; }
    }
    CHECK(found);
}
