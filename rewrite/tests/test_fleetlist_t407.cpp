// SPDX-License-Identifier: GPL-3.0-or-later

// t407 SHIPS LIST (FLEET, state 18) law pins.
// LAW (docs/re/_wip_t407.md F5-F8, this session's measurements):
//  1. Header = static.txt #152 "%s  (%d Ship%s, %d more allowed)" (byte-cited;
//     the t253 vision read is the witness). Reuses the t276-pinned
//     planetwin formatShipHeader — these pins freeze the JOIN (double space,
//     plural pair) and the census argument, not a new template.
//  2. LOCATION = static.txt #146 "In Starlane to %s System\nETA - %d Day%s"
//     (fn 0x50d12 kind-2 leg; getter sites 0x51041/0x5104e; plural pair
//     getter(28)/getter(29) == pluralSuffix). #143 "Orbiting %s" pinned for
//     the orbit seam.
//  3. GEOMETRY MEASURED on work/screens/t253/fleet_open_game.png (native
//     640x480): rows top 52, pitch 106, FOUR rows, arrow boxes x606..635
//     around the t253-measured glyph centres (620,63)/(620,453). Hit
//     precedence arrows -> inert scroll column -> rows (x 7..605).
//  4. MEMBERSHIP = the campaign's ship census for the owner (the port's
//     entire ship state is ShipInTransit — t256c boundary; an honest empty
//     list is the honest zero, NOT a stub).
#include "ui/fleetlist.h"

#include <cctype>
#include <cstdio>
#include <fstream>
#include <map>
#include <memory>
#include <optional>
#include <string>
#include <vector>

#include "game/campaign.h"
#include "ui/planetwin.h"  // formatShipHeader + pluralSuffix (pinned t276)
#include "harness.h"

#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif

namespace {
namespace au = ascend::ui;
namespace ag = ascend::game;
const std::string kRepo = ASCENDANCY_SOURCE_DIR;

// static.txt entries keyed by the file's OWN "// N" comment markers (the
// getter index law: getter(n) == entry n). The naive quoted-line counter
// MISALIGNS from entry 90 on (multi-line entries shift it) — measured this
// session; the marker walk below is the correct reader.
std::map<int, std::string> staticTxtEntries() {
    std::ifstream f(kRepo + "/extracted/ascend00/static.txt", std::ios::binary);
    std::map<int, std::string> out;
    std::vector<std::string> lines;
    std::string line;
    while (std::getline(f, line)) {
        if (!line.empty() && line.back() == '\r') line.pop_back();
        lines.push_back(line);
    }
    for (size_t i = 0; i < lines.size(); i++) {
        std::string s = lines[i];
        // trim
        size_t b = s.find_first_not_of(" \t");
        if (b == std::string::npos) continue;
        s = s.substr(b);
        if (s.size() < 3 || s[0] != '/' || s[1] != '/') continue;
        // parse "// N" or "// N - M"
        std::string t = s.substr(2);
        size_t p = 0;
        while (p < t.size() && (t[p] == ' ' || t[p] == '\t')) p++;
        size_t q = p;
        while (q < t.size() && isdigit(static_cast<unsigned char>(t[q]))) q++;
        if (q == p) continue;
        int a = std::stoi(t.substr(p, q - p));
        int n = 1;
        size_t d = q;
        while (d < t.size() && (t[d] == ' ' || t[d] == '\t')) d++;
        if (d < t.size() && t[d] == '-') {
            d++;
            while (d < t.size() && (t[d] == ' ' || t[d] == '\t')) d++;
            size_t r = d;
            while (r < t.size() && isdigit(static_cast<unsigned char>(t[r]))) r++;
            if (r > d) n = std::stoi(t.substr(d, r - d)) - a + 1;
        }
        // consume n quoted entries following (multi-line entries merged)
        int got = 0;
        for (size_t j = i + 1; j < lines.size() && got < n; j++) {
            std::string u = lines[j];
            size_t bb = u.find_first_not_of(" \t");
            if (bb == std::string::npos) {
                if (got) break;
                continue;
            }
            u = u.substr(bb);
            if (u.empty() || u[0] != '"') {
                if (u.size() > 1 && u[0] == '/' && got) break;
                if (got) break;
                continue;
            }
            std::string e = u;
            while (e.size() < 2 || e.back() != '"') {  // multi-line entry
                j++;
                if (j >= lines.size()) break;
                std::string nx = lines[j];
                e.pop_back();  // drop trailing newline artifact if merged
                e += nx;
            }
            e = e.substr(1, e.size() - 2);
            size_t np = 0;
            while ((np = e.find("\\n", np)) != std::string::npos)
                e.replace(np, 2, "\n");
            out[a + got] = e;
            got++;
        }
    }
    return out;
}

// Seeded campaign over the SHIPPED data (t402 fixture pattern).
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

// ---- the shipped strings behind the two templates -------------------------
TEST(fleetlist_static_templates_t407) {
    REQUIRE_DATA();
    auto s = staticTxtEntries();
    CHECK(s.count(152) == 1);
    CHECK(s[152] == "%s  (%d Ship%s, %d more allowed)");   // #152, DOUBLE space
    CHECK(s[146] == "In Starlane to %s System\nETA - %d Day%s");  // #146
    CHECK(s[143] == "Orbiting %s");                        // #143
    CHECK(s[28] == "");                                     // plural pair
    CHECK(s[29] == "s");
    // The reader law itself: file markers are the getter index (a naive
    // quoted-line counter misaligns from entry 90 — measured t407).
    CHECK(s[131] == "Small");
    CHECK(s[151] == "%s  (%d Planet%s Occupied, %d System%s Controlled)");
}

TEST(fleetlist_location_laws_t407) {
    // #146 shape (fn 0x50d12 kind-2). Real newlines (loader-interprets law).
    CHECK(au::fleetLaneLocation("Vega", 2) ==
          "In Starlane to Vega System\nETA - 2 Days");
    // plural pair rides cmp n,1 (0x51030): singular iff exactly 1.
    CHECK(au::fleetLaneLocation("Vega", 1) ==
          "In Starlane to Vega System\nETA - 1 Day");
    // #143 orbit shape (the seam's law; 0x50dc5).
    CHECK(au::fleetOrbitLocation("Pulveran II") == "Orbiting Pulveran II");
}

TEST(fleetlist_header_join_t407) {
    // The join == planetwin's pinned formatShipHeader applied to the census;
    // double space + plural frozen against the SHIPPED template.
    REQUIRE_DATA();
    auto s = staticTxtEntries();
    auto camp = seededCampaign();
    if (!camp) return;
    // fleetHeaderText consults the campaign for the allowance; compare only
    // the template leg: build the same call with the same allowance.
    const int ships = 25;
    const std::string got =
        au::fleetHeaderText(*camp, ag::kPlayer, "Chamachies", ships);
    const int allowed = au::fleetAllowedFor(*camp, ag::kPlayer, ships);
    char want[512];
    std::snprintf(want, sizeof(want), s[152].c_str(), "Chamachies", ships,
                  au::pluralSuffix(ships), allowed);
    CHECK(got == want);
    CHECK(std::string(au::pluralSuffix(1)) == "");  // "1 Ship" leg
}

TEST(fleetlist_membership_census_t407) {
    REQUIRE_DATA();
    auto camp = seededCampaign();
    if (!camp) return;
    // Honest zero: a fresh campaign may hold ships; pin the FILTER law
    // instead of the count: rows == owner's entries, array order, indices
    // point into fleet().
    camp->setFleetForTest({{ag::kPlayer, 0, 1}, {1, 2, 3}, {ag::kPlayer, 4, 5},
                           {2, 1, 0}});
    const auto rows = au::fleetRows(*camp, ag::kPlayer);
    CHECK(rows.size() == 2);
    CHECK(rows.size() <= camp->fleet().size());
    if (rows.size() == 2) {
        CHECK(rows[0].fleetIndex == 0);
        CHECK(rows[1].fleetIndex == 2);
    }
    // The other owners see their own single row each.
    CHECK(au::fleetRows(*camp, 1).size() == 1);
    CHECK(au::fleetRows(*camp, 2).size() == 1);
    CHECK(au::fleetRows(*camp, 9).empty());
}

TEST(fleetlist_window_clamp_t407) {
    std::vector<au::FleetRowKey> all(6);
    for (int i = 0; i < 6; i++) all[i].fleetIndex = i;
    CHECK(au::fleetWindow(all, 0).size() == 4);
    CHECK(au::fleetWindow(all, -3).size() == 4);      // clamps up
    CHECK(au::fleetWindow(all, 2).size() == 4);       // max scroll
    CHECK(au::fleetWindow(all, 99).size() == 4);      // clamps down
    const auto w = au::fleetWindow(all, 2);
    if (w.size() == 4) CHECK(w[0].fleetIndex == 2);   // window slid by 2
    CHECK(au::fleetWindow({}, 0).empty());
    std::vector<au::FleetRowKey> two(2);
    CHECK(au::fleetWindow(two, 0).size() == 2);       // fewer than a page
}

TEST(fleetlist_geometry_measured_t407) {
    using H = au::FleetHit;
    constexpr int kTop = au::kFleetRowsTop;
    // MEASURED constants (fleetlist.h header block).
    CHECK(kTop == 52);
    CHECK(au::kFleetRowPitch == 106);
    CHECK(au::kFleetVisibleRows == 4);
    // The t253-measured glyph centres fall INSIDE the boxes.
    CHECK(au::fleetHitFor(au::Pt{620, 63}, kTop).kind == H::ArrowUp);
    CHECK(au::fleetHitFor(au::Pt{620, 453}, kTop).kind == H::ArrowDown);
    // Trough between the boxes: inert (t405 law shape).
    CHECK(au::fleetHitFor(au::Pt{620, 200}, kTop).kind == H::None);
    // Right of the column: None.
    CHECK(au::fleetHitFor(au::Pt{636, 200}, kTop).kind == H::None);
    // Rows: row bands from top 52, pitch 106; row 1 probe at 52+106+5.
    const auto r = au::fleetHitFor(au::Pt{300, kTop + au::kFleetRowPitch + 5}, kTop);
    CHECK(r.kind == H::Row && r.row == 1);
    CHECK(au::fleetHitFor(au::Pt{300, kTop - 1}, kTop).kind == H::None);
    CHECK(au::fleetHitFor(au::Pt{300, kTop + 4 * au::kFleetRowPitch}, kTop).kind ==
          H::None);
    // The row/right-column boundary at y 200 (between the arrow boxes, so
    // the column side is the INERT trough, never a row): 605 row, 606 None.
    CHECK(au::fleetHitFor(au::Pt{605, 200}, kTop).kind == H::Row);
    CHECK(au::fleetHitFor(au::Pt{606, 200}, kTop).kind == H::None);
    // Left of the STATSHIPLST interior (x < 7): outside.
    CHECK(au::fleetHitFor(au::Pt{5, kTop + 5}, kTop).kind == H::None);
}

TEST(fleetlist_allowed_default_t407) {
    REQUIRE_DATA();
    auto camp = seededCampaign();
    if (!camp) return;
    // [inferred default systems+1-ships, F7] — the pin freezes the DEFAULT
    // SHAPE (never negative, decreases with ships), not a vendor law.
    const int a0 = au::fleetAllowedFor(*camp, ag::kPlayer, 0);
    CHECK(a0 >= 1);  // at least the home system + 1
    const int a1 = au::fleetAllowedFor(*camp, ag::kPlayer, a0);
    CHECK(a1 == 0);
    // Overshoot clamps at 0, never negative.
    CHECK(au::fleetAllowedFor(*camp, ag::kPlayer, a0 + 100) == 0);
}

TEST(fleetlist_ship_name_hull_row_t407) {
    REQUIRE_DATA();
    auto camp = seededCampaign();
    if (!camp) return;
    // Labelled port default: the planitem hull row the campaign spends.
    CHECK(au::fleetShipName(*camp) == "Ship");
}
