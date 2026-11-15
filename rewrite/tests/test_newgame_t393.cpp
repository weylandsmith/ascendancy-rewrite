// SPDX-License-Identifier: GPL-3.0-or-later

// t393 New Game screen pins (D10: "garbled and unusable" -> full-screen
// rebuild). Laws: docs/re/_wip_t393.md S1-S12 (windows.txt L575-684 cited
// rects; cited measurement off the user-supplied original capture
// scratchpad/newgame-original.png at the documented capture->screen mapping).
// Headless-safe: pure law + one real-data file read (newgame.txt).
#include "ui/menulaw.h"

#include <filesystem>
#include <fstream>

#include "harness.h"

namespace {
namespace au = ascend::ui;
namespace fs = std::filesystem;
using au::Pt;
}  // namespace

TEST(newgame_t393_layout_fits_640x480) {
    // The D10 clipping symptom was rects falling off-screen. EVERY state-3
    // rect on the New Game screen must fit the logical display inclusive.
    const au::Rect rects[] = {
        au::kNewgameWnd,        au::kRaceList,
        au::kPlayerColorRect,   au::kBeginNewGameBtn,
        au::kLoreBox,           au::kRaceArrowUp,
        au::kRaceArrowDown,
    };
    for (const auto& r : rects) {
        CHECK(r.x0 >= 0 && r.y0 >= 0);
        CHECK(r.x1 < au::kDisplayW);
        CHECK(r.y1 < au::kDisplayH);
        CHECK(r.x1 >= r.x0 && r.y1 >= r.y0);
    }
    // The three wheel controls too (windows.txt row).
    for (int i = 0; i < au::kNewgameControlCount; i++) {
        const au::Rect& r = au::kNewgameControls[i].rect;
        CHECK(r.x0 >= 0 && r.y0 >= 0 && r.x1 < au::kDisplayW &&
              r.y1 < au::kDisplayH);
    }
}

TEST(newgame_t393_measured_rects_windows_txt) {
    // windows.txt verbatim additions beyond the t387 pins: Player^Color
    // (L653-661: 379,381-493,419 — NOTE y1=419, the SHORT fourth zone; the
    // bar's visual bottom is the Begin zone, not this one).
    CHECK(au::kPlayerColorRect.x0 == 379 && au::kPlayerColorRect.y0 == 381);
    CHECK(au::kPlayerColorRect.x1 == 493 && au::kPlayerColorRect.y1 == 419);
    // Begin New Game: cited measurement S8 (capture 495..640 x 374..473
    // minus the 1px border). x1 lands on the display edge (639) — the
    // original's Begin zone is flush right (bevel census row y=430).
    CHECK(au::kBeginNewGameBtn.x0 == 494 && au::kBeginNewGameBtn.y0 == 373);
    CHECK(au::kBeginNewGameBtn.x1 == 639 && au::kBeginNewGameBtn.y1 == 472);
    // Disjoint from every windows.txt control (no double-hit ambiguity).
    CHECK(au::kBeginNewGameBtn.x0 > au::kPlayerColorRect.x1);
    CHECK(!au::inRect(au::kNewgameWnd, {au::kBeginNewGameBtn.x0, 420}));
    // RACELIST right edge == Begin zone left edge + gutter of 1 bevel px.
    CHECK(au::kRaceList.x1 == 632);
}

TEST(newgame_t393_race_slots_and_arrows) {
    // Three-slot scroll window, measured bands 49-153 / 157-262 / 266-372.
    CHECK(au::kRaceSlotCount == 3);
    CHECK(au::newgameRowAt({560, 49}) == 0);
    CHECK(au::newgameRowAt({560, 153}) == 0);
    CHECK(au::newgameRowAt({560, 154}) == 0);  // slots tile the interior
    CHECK(au::newgameRowAt({560, 156}) == 0);  // (bevel gaps are not hit
    CHECK(au::newgameRowAt({560, 157}) == 1);  //  zones; no dead-row law)
    CHECK(au::newgameRowAt({560, 262}) == 1);
    CHECK(au::newgameRowAt({560, 266}) == 2);
    CHECK(au::newgameRowAt({560, 372}) == 2);
    CHECK(au::newgameRowAt({560, 373}) == -1);  // below interior
    CHECK(au::newgameRowAt({501, 100}) == -1);  // left of interior
    CHECK(au::newgameRowAt({633, 100}) == -1);  // right of interior
    // Arrow squares measured S: up (616,47)-(631,62), down (616,356)-(631,371).
    CHECK(au::newgameArrowAt({616, 47}) == 0);
    CHECK(au::newgameArrowAt({631, 62}) == 0);
    CHECK(au::newgameArrowAt({616, 356}) == 1);
    CHECK(au::newgameArrowAt({631, 371}) == 1);
    CHECK(au::newgameArrowAt({600, 55}) == -1);   // beside the square
    CHECK(au::newgameArrowAt({560, 200}) == -1);  // mid-list is a row, not arrow
}

TEST(newgame_t393_density_ladder_and_words) {
    // static.txt //155-159 words + t78 MEASURED counts (mapgen.md OQ-012(a)).
    CHECK(au::kDensityCycleCount == 5);
    CHECK(std::string(au::kDensityWords[0]) == "Average");
    CHECK(std::string(au::kDensityWords[1]) == "Dense");
    CHECK(std::string(au::kDensityWords[2]) == "Very Dense");
    CHECK(std::string(au::kDensityWords[3]) == "Vacuous");
    CHECK(std::string(au::kDensityWords[4]) == "Sparse");
    CHECK(au::kDensityStarCounts[0] == 50);
    CHECK(au::kDensityStarCounts[1] == 75);
    CHECK(au::kDensityStarCounts[2] == 100);
    CHECK(au::kDensityStarCounts[3] == 15);
    CHECK(au::kDensityStarCounts[4] == 25);
    CHECK(std::string(au::densityWord(50)) == "Average");
    CHECK(std::string(au::densityWord(100)) == "Very Dense");
    CHECK(au::densityWord(60) == nullptr);  // off-ladder: no cited word
    CHECK(std::string(au::speciesCountWord(3)) == "Three");
    CHECK(std::string(au::speciesCountWord(7)) == "Seven");
    CHECK(au::speciesCountWord(8) == nullptr);
    CHECK(au::speciesCountWord(0) == nullptr);
    CHECK(std::string(au::atmosphereWord(0)) == "Peaceful");
    CHECK(std::string(au::atmosphereWord(1)) == "Neutral");
    CHECK(std::string(au::atmosphereWord(2)) == "Hostile");
    CHECK(au::atmosphereWord(3) == nullptr);
}

TEST(newgame_t393_summary_template_static168) {
    // static.txt //168 "%s Star Cluster\n%s Species\n%s Atmosphere" — the
    // original's "Average Star Cluster / Five Species / Neutral Atmosphere".
    std::vector<std::string> out;
    au::newgameSummary(50, 5, 1, &out);
    CHECK(out.size() == 3);
    CHECK(out[0] == "Average Star Cluster");
    CHECK(out[1] == "Five Species");
    CHECK(out[2] == "Neutral Atmosphere");
    // Unknown values degrade to the bare noun (never an invented word).
    au::newgameSummary(60, 9, 7, &out);
    CHECK(out[0] == "Star Cluster");
    CHECK(out[1] == "Species");
    CHECK(out[2] == "Atmosphere");
}

TEST(newgame_t393_lore_file_real_data) {
    // The REAL extracted/ascend00/newgame.txt: 21 fragments, specnum order,
    // EOF marker 0x1a. Minions (specnum 0) quoted VERBATIM from the file
    // (the same sentence the user-supplied original shows in green).
    const fs::path p =
        fs::path(ASCENDANCY_SOURCE_DIR) / "extracted" / "ascend00" /
        "newgame.txt";
    std::vector<std::string> lore;
    std::string err;
    CHECK(au::loadNewgameLore(p.string(), &lore, &err));
    CHECK(lore.size() == 21);
    CHECK(lore[0] ==
          "are a mysterious group of robot creatures controlled by an "
          "unknown extra-galactic super force. They are hideously strong and "
          "quick.");
    // Every fragment starts lowercase (sentence continuation law).
    for (const auto& s : lore) CHECK(!s.empty() && s[0] >= 'a' && s[0] <= 'z');
    // Composition law static.txt //154 "The %s %s".
    CHECK(au::loreSentence("Minions", lore[0]) ==
          "The Minions are a mysterious group of robot creatures controlled "
          "by an unknown extra-galactic super force. They are hideously "
          "strong and quick.");
    // Refusal path: missing file, wrong count (temp file, never the tree).
    CHECK(!au::loadNewgameLore("/nonexistent/newgame.txt", &lore, &err));
    CHECK(!err.empty());
    const fs::path tmp = fs::temp_directory_path() / "t393_short_lore.txt";
    { std::ofstream f(tmp); f << "are short.\r\n\x1a\r\n"; }
    CHECK(!au::loadNewgameLore(tmp.string(), &lore, &err));
    fs::remove(tmp);
}

TEST(newgame_t393_wrap_to_width) {
    // Unit width = 1 per char (fake face): pure greedy wrap, no word split.
    auto w = [](const std::string& s) { return int(s.size()); };
    auto lines = au::wrapToWidth("the quick brown fox jumps", 10, w);
    CHECK(lines.size() == 3);
    CHECK(lines[0] == "the quick");
    CHECK(lines[1] == "brown fox");
    CHECK(lines[2] == "jumps");
    // Exact fit joins; a single over-long word keeps its own line whole.
    lines = au::wrapToWidth("ab cd ef", 5, w);
    CHECK(lines.size() == 2 && lines[0] == "ab cd" && lines[1] == "ef");
    lines = au::wrapToWidth("tiny extraordinarilylongword end", 12, w);
    CHECK(lines.size() == 3);
    CHECK(lines[1] == "extraordinarilylongword");
    CHECK(au::wrapToWidth("", 10, w).empty());
}
