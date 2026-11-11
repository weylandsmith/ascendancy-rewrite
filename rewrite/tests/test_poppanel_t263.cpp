// SPDX-License-Identifier: GPL-3.0-or-later

// Population panel law pins (t263). Law sources: docs/re/planets-ui.md S4
// (paint loop 0x3ce39..0x3cef8), docs/re/shp.md S23 + docs/re/_wip_t254.md
// (17np.shp identification), docs/re/_wip_t263.md S1..S5 (this task's
// re-measurements: gwshare entry census, 17np dims + palette fixture, panel
// arithmetic). Real extracted/ files, read-only, gate-safe.
#include "ui/poppanel.h"

#include <filesystem>
#include <fstream>
#include <vector>

#include "formats/shp.h"
#include "game/campaign.h"
#include "harness.h"

#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif

namespace {
namespace au = ascend::ui;
namespace ag = ascend::game;
using ascend::formats::ShapeLibrary;
const std::string kRepo = ASCENDANCY_SOURCE_DIR;
const std::string kA01 = kRepo + "/extracted/ascend01/data/";
}  // namespace

TEST(poppanel_gwshare_entry44_t263) {
    // LIBRARY-CHAIN pin (file half; live-RAM half cited t254: [0x6fd9c]=44 ->
    // cache slot 44 verbatim == 17np.shp). gwshare.txt is CRLF + blank-line
    // separated with a 0x1a terminator: the CACHE SLOT INDEX is the 0-based
    // index among non-blank lines, NOT the physical line number (17np is
    // entry #44 on physical line 63 — _wip_t263.md S1).
    std::ifstream f(kRepo + "/extracted/ascend00/gwshare.txt", std::ios::binary);
    CHECK(f.is_open());
    if (!f.is_open()) return;
    std::vector<std::string> entries;
    std::string line;
    while (std::getline(f, line)) {
        if (!line.empty() && line.back() == '\r') line.pop_back();
        // Strip surrounding blanks; drop empty lines and the 0x1a EOF marker.
        size_t b = line.find_first_not_of(" \t");
        if (b == std::string::npos) continue;
        std::string e = line.substr(b);
        if (e == "\x1a") continue;
        entries.push_back(e);
    }
    CHECK(entries.size() == 45);  // 45 .shp entries; 0x1a is not one
    if (entries.size() != 45) return;
    // The two t254 anchors: control slot 41 and pop slot 44.
    CHECK(entries.size() > 44);
    CHECK(entries[41] == "data\\14intel.shp");
    CHECK(entries[44] == "data\\17np.shp");
    // Last entry is the final boot-loaded library (t254 S5.3).
    CHECK(entries.back() == "data\\17np.shp");
}

TEST(poppanel_17np_library_census_t263) {
    // Record census + the byte-level ICON<->ROLE binding (fixture:
    // _wip_t263.md S2/S3, measured this session on game.pal 6-bit v*255//63).
    ShapeLibrary lib;
    std::string err;
    CHECK(lib.load(kA01 + "17np.shp", &err));
    if (lib.count() != 9) return;

    // (a) dims census: exactly 9 records, k1/k2/k3 = 9x9, 7x9, 8x8 — all fit
    //     the 0x0a pitch; every other pop candidate is excluded by min dims
    //     (planets 11x11, planitem 24x23, planalNN 47x47 — shp.md S23.3).
    CHECK(lib.record(1).width == 9 && lib.record(1).height == 9);
    CHECK(lib.record(2).width == 7 && lib.record(2).height == 9);
    CHECK(lib.record(3).width == 8 && lib.record(3).height == 8);

    // (b) the conformance gate agrees on the real file and rejects a
    //     lookalike library (14intel: 18x18 class, NOT a 10px-pitch set).
    CHECK(au::popSlotLibraryConforms(kA01 + "17np.shp", &err));
    CHECK(!au::popSlotLibraryConforms(kA01 + "14intel.shp", &err));

    // (c) ROLE<->RECORD binding, pixel-verified direction:
    //     SEL 1 (busy)   -> k1 has RED body pixels AND the blue tool (the
    //                       t254 vision testimony: "red/pink body + blue tool").
    //     SEL 2 (free)   -> k2 is YELLOW-dominant with ZERO blue pixels
    //                       (swapping SEL1/SEL2 fails BOTH checks below).
    //     SEL 3 (empty)  -> k3's centre is NEVER painted (hollow ring).
    // Palette: game.pal is 6-bit (max 0x3f, shp.md S19) scaled v*255/63.
    std::ifstream pf(kA01 + "game.pal", std::ios::binary);
    CHECK(pf.is_open());
    std::vector<uint8_t> raw(768, 0);
    pf.read(reinterpret_cast<char*>(raw.data()), 768);
    auto rgb = [&](uint8_t idx, int ch) { return raw[3 * idx + ch] * 255 / 63; };

    std::vector<uint8_t> px;
    CHECK(lib.decode(1, px));
    int k1Red = 0, k1Blue = 0;
    for (size_t i = 0; i < px.size(); ++i) {
        const int r = rgb(px[i], 0), g = rgb(px[i], 1), b = rgb(px[i], 2);
        if (r > g && r > b && r - std::max(g, b) > 40) ++k1Red;
        if (b > r && b > g && b - std::max(r, g) > 20) ++k1Blue;
    }
    CHECK(k1Red > 0);   // red/skin figure present
    CHECK(k1Blue > 0);  // the blue tool distinguishes k1 from k2

    px.clear();
    CHECK(lib.decode(2, px));
    int k2Yellow = 0, k2Blue = 0;
    for (size_t i = 0; i < px.size(); ++i) {
        const int r = rgb(px[i], 0), g = rgb(px[i], 1), b = rgb(px[i], 2);
        // "yellow" here = measured dominant hue family of k2: idx 89
        // (255,206,24) x12 plus orange shades (242..255 r, g 109..182, b<=56).
        if (r > 200 && g > 90 && b < 90) ++k2Yellow;
        if (b > r && b > g && b - std::max(r, g) > 20) ++k2Blue;
    }
    CHECK(k2Yellow > 0);
    CHECK(k2Blue == 0);  // k2 has NO blue pixels (fixture: 0 of 30 painted)

    px.clear();
    CHECK(lib.decode(3, px));
    // k3 is 8x8; the stream never writes the interior rows 2..5 cols 2..5
    // (the "hollow" law). Pre-fill with a sentinel and require the 16 centre
    // bytes untouched.
    std::vector<uint8_t> canvas(64, 0xA5);
    CHECK(lib.decode(3, canvas));
    int untouched = 0;
    for (int y = 2; y < 6; ++y)
        for (int x = 2; x < 6; ++x)
            untouched += canvas[y * 8 + x] == 0xA5;
    CHECK(untouched == 16);  // hollow circle, byte-confirmed

    // (d) selector indexing is IDENTITY (t254 runtime selector table 9/9).
    CHECK(au::popSlotRecord(1) == 1);
    CHECK(au::popSlotRecord(2) == 2);
    CHECK(au::popSlotRecord(3) == 3);
    CHECK(au::popSlotRecord(0) == -1);
    CHECK(au::popSlotRecord(4) == -1);
    CHECK(au::popSlotRoleOf(1) == au::PopSlotRole::Busy);
    CHECK(au::popSlotRoleOf(2) == au::PopSlotRole::Free);
    CHECK(au::popSlotRoleOf(3) == au::PopSlotRole::Empty);
}

TEST(poppanel_grid_geometry_t263) {
    // Panel rect + pitch arithmetic (_wip_t263.md S5).
    CHECK(au::kPlPopRect.x0 == 355);  // windows.txt:1591
    CHECK(au::kPlPopRect.y0 == 7);    // windows.txt:1592
    CHECK(au::kPlPopRect.x1 == 454);  // windows.txt:1593
    CHECK(au::kPlPopRect.y1 == 106);  // windows.txt:1594
    const int panelW = au::kPlPopRect.x1 - au::kPlPopRect.x0 + 1;
    const int panelH = au::kPlPopRect.y1 - au::kPlPopRect.y0 + 1;
    CHECK(panelW == 100 && panelH == 100);
    // 10 rows x (10 slots x 10 px) == the panel: the storedCapFor clamp
    // (campaign.cpp:811) cannot overflow the panel.
    CHECK(au::kPopSlotsPerRow * au::kPopSlotPitch == panelW);
    CHECK(au::popPanelRows(au::kPopPanelMaxSlots) * au::kPopSlotPitch == panelH);
    CHECK(au::kPopPanelMaxSlots == au::kPopSlotsPerRow * au::kPopSlotsPerRow);

    // Row law: EBP advances only after i%10==9 -> ceil(cap/10) rows.
    CHECK(au::popPanelRows(0) == 0);
    CHECK(au::popPanelRows(-5) == 0);   // cap exit jge: nothing painted
    CHECK(au::popPanelRows(1) == 1);
    CHECK(au::popPanelRows(10) == 1);
    CHECK(au::popPanelRows(11) == 2);
    CHECK(au::popPanelRows(39) == 4);   // t254 Vega IV: 10,10,10,9
    CHECK(au::popPanelRows(100) == 10);

    // Cell placement law: (i%10)*10, (i/10)*10 from the origin, vendor
    // iteration order preserved.
    auto cells = au::popPanelCells({1, 1, 2, 3}, {0, 0});
    CHECK(cells.size() == 4);
    CHECK(cells[0].pos.x == 0 && cells[0].pos.y == 0);
    CHECK(cells[1].pos.x == 10 && cells[1].pos.y == 0);
    CHECK(cells[2].pos.x == 20 && cells[2].pos.y == 0);
    CHECK(cells[3].pos.x == 30 && cells[3].pos.y == 0);
    CHECK(cells[0].record == 1 && cells[2].record == 2 && cells[3].record == 3);
    auto wrapped = au::popPanelCells(std::vector<int>(11, 1), {5, 5});
    CHECK(wrapped.size() == 11);
    CHECK(wrapped[10].pos.x == 5 && wrapped[10].pos.y == 15);  // row 1, col 0
    // Out-of-band selector: still emitted at its grid slot, record -1.
    auto odd = au::popPanelCells({1, 7}, {0, 0});
    CHECK(odd[1].record == -1 && odd[1].pos.x == 10);
}

TEST(poppanel_campaign_integration_t263) {
    // End-to-end: campaign band law -> layout law. Table wiring mirrors
    // test_campaign.cpp's tables() verbatim (loaders, paths, race00..05).
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

    int starsChecked = 0;
    for (int s = 0; s < int(g.stars.size()); ++s) {
        const int cap = camp.popCapAt(s);
        auto cells = au::popPanelFor(camp, s);
        CHECK(cells.size() == size_t(std::max(0, cap)));
        if (cells.size() != size_t(std::max(0, cap))) continue;
        ++starsChecked;
        // Band shapes agree with the roles, and the geometry is the pitch law.
        int used = camp.usedPopFor(s), pop = int(camp.planetAt(s).pop);
        for (size_t i = 0; i < cells.size(); ++i) {
            const int expectSel = 1 + (i >= size_t(used) ? 1 : 0) +
                                  (i >= size_t(pop) ? 1 : 0);
            CHECK(cells[i].selector == expectSel);
            CHECK(cells[i].record == expectSel);  // identity indexing
            CHECK(cells[i].pos.x == int(i % 10) * 10);
            CHECK(cells[i].pos.y == int(i / 10) * 10);
            CHECK(cells[i].pos.x < 100 && cells[i].pos.y < 100);  // fits panel
        }
    }
    CHECK(starsChecked > 0);
}
