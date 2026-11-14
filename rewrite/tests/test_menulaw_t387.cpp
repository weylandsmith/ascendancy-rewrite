// SPDX-License-Identifier: GPL-3.0-or-later

// t387 menu-law pins: NEWGAMEWND geometry + hit-map (windows.txt L575-673
// verbatim) and the LOAD slot-list law over REAL files built in a temp dir
// (torn-tolerance law t366/t369; u32@0 game-day law, Observer::rawDay).
// Synthetic points + temp files — headless-safe by construction.
#include "ui/menulaw.h"

#include <filesystem>
#include <fstream>

#include "harness.h"

namespace {
namespace au = ascend::ui;
namespace fs = std::filesystem;
using au::Pt;

// Write a raw .SAV whose u32@0 == day (the game-day law).
void makeSav(const fs::path& p, uint32_t day) {
    uint8_t h[4] = {uint8_t(day), uint8_t(day >> 8), uint8_t(day >> 16),
                    uint8_t(day >> 24)};
    std::ofstream f(p, std::ios::binary);
    f.write(reinterpret_cast<char*>(h), 4);
    // Body bytes so the file is not header-only (slot files are MBs; the
    // listing law reads only the header).
    f << std::string(64, 'x');
}
}  // namespace

TEST(menulaw_newgame_geometry_windows_txt) {
    // Verbatim windows.txt values. If this fails, someone typed a number.
    CHECK(au::kNewgameWnd.x0 == 334);
    CHECK(au::kNewgameWnd.y0 == 12);
    CHECK(au::kNewgameWnd.x1 == 488);
    CHECK(au::kNewgameWnd.y1 == 364);
    CHECK(au::kRaceList.x0 == 502 && au::kRaceList.y0 == 45);
    CHECK(au::kRaceList.x1 == 632 && au::kRaceList.y1 == 372);
    CHECK(au::kNewgameControlCount == 3);

    struct Exp { const char* n; int x0, y0, x1, y1, msg; } exp[3] = {
        {"GALAXY_MORE", 7, 381, 122, 472, 501},
        {"PLAYERS_MORE", 131, 381, 246, 472, 503},
        {"DIFFICULTYMORE", 255, 381, 370, 472, 505},
    };
    for (int i = 0; i < 3; i++) {
        const au::NewgameControl& c = au::kNewgameControls[i];
        CHECK(std::string(c.name) == exp[i].n);
        CHECK(c.rect.x0 == exp[i].x0 && c.rect.y0 == exp[i].y0);
        CHECK(c.rect.x1 == exp[i].x1 && c.rect.y1 == exp[i].y1);
        CHECK(c.message == exp[i].msg);
    }
    // Bottom-row law [verified]: equal widths, 9-px gutters, disjoint.
    for (int i = 0; i < 3; i++) {
        CHECK(au::kNewgameControls[i].rect.x1 - au::kNewgameControls[i].rect.x0 == 115);
        CHECK(au::kNewgameControls[i].rect.y1 - au::kNewgameControls[i].rect.y0 == 91);
        if (i) CHECK(au::kNewgameControls[i].rect.x0 -
                         au::kNewgameControls[i - 1].rect.x1 == 9);
    }
    // Player^Color neighbour (PARENT NONE, msg 0 — not a control): the row
    // ends before its x0=379 with the same 9-px gutter.
    CHECK(au::kNewgameControls[2].rect.x1 + 9 == 379);
}

TEST(menulaw_newgame_hitmap) {
    using au::newgameControlAt;
    CHECK(newgameControlAt({7, 381}) == 0);      // top-left corner inclusive
    CHECK(newgameControlAt({122, 472}) == 0);    // bottom-right inclusive
    CHECK(newgameControlAt({131, 381}) == 1);
    CHECK(newgameControlAt({255, 420}) == 2);
    CHECK(newgameControlAt({126, 400}) == -1);   // gutter: dead space
    CHECK(newgameControlAt({379, 381}) == -1);   // Player^Color is not ours
    CHECK(newgameControlAt({400, 200}) == -1);   // inside NEWGAMEWND, no control
    CHECK(newgameControlAt({0, 0}) == -1);
    // No clamp law: an off-by-one past each edge misses.
    CHECK(newgameControlAt({6, 381}) == -1);
    CHECK(newgameControlAt({123, 472}) == -1);
}

TEST(menulaw_load_list_real_files) {
    namespace fs = std::filesystem;
    const fs::path dir = fs::temp_directory_path() / "t387_saves";
    std::error_code ec;
    fs::remove_all(dir, ec);
    fs::create_directories(dir);
    makeSav(dir / "42.sav", 1086);
    makeSav(dir / "7.sav", 300);
    makeSav(dir / "41.SAV", 44);            // uppercase extension too
    { std::ofstream f(dir / "43.sav"); f << "ab"; }  // 2 bytes: TORN
    { std::ofstream f(dir / "notes.txt"); f << "ignore me"; }  // not a slot

    const auto slots = au::listSaveSlots(dir.string());
    CHECK(slots.size() == 4);  // name-ascending: 41.SAV 42.sav 43.sav 7.sav
    if (slots.size() == 4) {
        CHECK(slots[0].name == "41.SAV" && slots[0].day == 44 && !slots[0].torn);
        CHECK(slots[1].name == "42.sav" && slots[1].day == 1086);
        CHECK(slots[2].name == "43.sav" && slots[2].torn);   // listed + marked
        CHECK(slots[3].name == "7.sav" && slots[3].day == 300);
    }
    fs::remove_all(dir, ec);
}

TEST(menulaw_load_list_missing_dir_is_honest_zero) {
    const auto slots = au::listSaveSlots("/nonexistent/t387/nowhere");
    CHECK(slots.empty());
}

TEST(menulaw_load_row_geometry_and_refusal) {
    // Row law: pitch 39 from LOADLIST.y0=46, row band 30, gutter dead.
    CHECK(au::kLoadRowH == 30 && au::kLoadRowPitch == 39);
    CHECK(au::loadRowAt({100, 46}, 3) == 0);       // first row top edge
    CHECK(au::loadRowAt({100, 75}, 3) == 0);       // row 0 bottom (46+29)
    CHECK(au::loadRowAt({100, 76}, 3) == -1);      // gutter starts
    CHECK(au::loadRowAt({100, 84}, 3) == -1);      // gutter ends (46+38)
    CHECK(au::loadRowAt({100, 85}, 3) == 1);       // row 1 top (46+39)
    CHECK(au::loadRowAt({100, 124}, 3) == 2);      // row 2 top (46+78)
    CHECK(au::loadRowAt({100, 153}, 3) == 2);      // row 2 bottom (rel 107)
    CHECK(au::loadRowAt({100, 163}, 3) == -1);     // rel 117 -> idx 3: past end
    CHECK(au::loadRowAt({100, 45}, 3) == -1);      // above LOADLIST
    CHECK(au::loadRowAt({6, 100}, 3) == -1);       // left of LOADLIST (x0=7)
    CHECK(au::loadRowAt({100, 50}, 0) == -1);      // empty list: no rows
    CHECK(au::loadRowAt({100, 500}, 3) == -1);     // below last row / frame

    // Refusal-not-clamp law.
    std::vector<au::SaveSlot> slots(2);
    slots[0].name = "a.sav";
    slots[1].name = "b.sav";
    slots[1].torn = true;
    std::string why;
    CHECK(au::loadPickAccepts(slots, 0, &why) == true);
    CHECK(au::loadPickAccepts(slots, 1, &why) == false);  // torn
    CHECK(why.find("torn") != std::string::npos);
    CHECK(au::loadPickAccepts(slots, 2, &why) == false);  // past end: no clamp
    CHECK(au::loadPickAccepts(slots, -1, &why) == false);
}
