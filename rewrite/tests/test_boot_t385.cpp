// SPDX-License-Identifier: GPL-3.0-or-later

// t385 boot state machine pins. Geometry is windows.txt L34-175 verbatim
// (law: docs/re/boot.md §1); the routing table is the pure bootClick law
// (§2). Synthetic points, no display — headless-safe by construction.
#include "ui/boot.h"

#include "harness.h"

namespace {
namespace au = ascend::ui;
using au::BootState;
using au::Pt;

constexpr Pt centre(au::Rect r) { return {(r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2}; }
}  // namespace

TEST(boot_title_rects_match_windows_txt) {
    // Every rect/name/message measured from extracted/ascend00/windows.txt
    // (block order INTRO..EXITTODOS). If this test fails, someone typed a
    // number instead of reading the file.
    REQUIRE_DATA();
    CHECK(au::kTitleButtonCount == 7);
    struct Exp { const char* n; int x0, y0, x1, y1, msg, p1; } exp[7] = {
        {"INTRO", 159, 200, 477, 230, 1, 6},
        {"PLAYTUTORIAL", 159, 240, 477, 270, 1, 15},
        {"FRESHGAME", 159, 280, 477, 310, 1, 3},
        {"RESUME", 159, 320, 477, 350, 1, 1},
        {"LOAD", 159, 360, 477, 390, 1, 4},
        {"SAVE", 159, 400, 477, 430, 1, 2},
        {"EXITTODOS", 159, 440, 477, 470, 2, 0},
    };
    for (int i = 0; i < 7; i++) {
        const au::TitleButton& b = au::kTitleButtons[i];
        CHECK(std::string(b.name) == exp[i].n);
        CHECK(b.rect.x0 == exp[i].x0);
        CHECK(b.rect.y0 == exp[i].y0);
        CHECK(b.rect.x1 == exp[i].x1);
        CHECK(b.rect.y1 == exp[i].y1);
        CHECK(b.message == exp[i].msg);
        CHECK(b.param1 == exp[i].p1);
    }
    // Column law [verified]: one column, width 318, height 30, pitch 40.
    for (int i = 0; i < 7; i++) {
        CHECK(au::kTitleButtons[i].rect.x1 - au::kTitleButtons[i].rect.x0 == 318);
        CHECK(au::kTitleButtons[i].rect.y1 - au::kTitleButtons[i].rect.y0 == 30);
        if (i) CHECK(au::kTitleButtons[i].rect.y0 - au::kTitleButtons[i - 1].rect.y1 == 10);
    }
}

TEST(boot_click_routing_table) {
    // The transition law itself: each button from Title goes where the
    // vendor wiring + D8 mapping say (docs/re/boot.md §2).
    CHECK(au::bootClick(BootState::Title, centre(au::kTitleButtons[0].rect)) == BootState::Intro);
    CHECK(au::bootClick(BootState::Title, centre(au::kTitleButtons[1].rect)) == BootState::Tutorial);
    CHECK(au::bootClick(BootState::Title, centre(au::kTitleButtons[2].rect)) == BootState::RaceConfig);
    CHECK(au::bootClick(BootState::Title, centre(au::kTitleButtons[3].rect)) == BootState::Campaign);
    CHECK(au::bootClick(BootState::Title, centre(au::kTitleButtons[4].rect)) == BootState::Load);
    CHECK(au::bootClick(BootState::Title, centre(au::kTitleButtons[5].rect)) == BootState::Save);
    CHECK(au::bootClick(BootState::Title, centre(au::kTitleButtons[6].rect)) == BootState::Quit);
    // RaceConfig: the RESUME edge (msg 1/1) enters Campaign; other buttons
    // are inert there (no double-dispatch back through Title).
    CHECK(au::bootClick(BootState::RaceConfig, centre(au::kTitleButtons[3].rect)) == BootState::Campaign);
    CHECK(au::bootClick(BootState::RaceConfig, centre(au::kTitleButtons[0].rect)) == BootState::RaceConfig);
}

TEST(boot_clicks_are_exact_and_never_clamp) {
    // Rect inclusivity + no-op law: clicks outside the column change nothing
    // from ANY state; Quit is terminal; edge pixels belong to the button
    // (windows.txt rects are inclusive, layout.h inRect law).
    const Pt outside{100, 210};  // left of the column, INTRO row height
    CHECK(au::titleButtonAt(outside) == -1);
    for (int s = 0; s <= 7; s++) {
        const BootState st = static_cast<BootState>(s);
        CHECK(au::bootClick(st, outside) == st);
    }
    CHECK(au::titleButtonAt({159, 200}) == 0);   // INTRO top-left corner
    CHECK(au::titleButtonAt({477, 470}) == 6);   // EXITTODOS bottom-right corner
    CHECK(au::titleButtonAt({159, 199}) == -1);  // 1px above the column
    CHECK(au::titleButtonAt({477, 471}) == -1);  // 1px below
    // Gaps between buttons (pitch 40, height 30) hit nothing.
    CHECK(au::titleButtonAt({300, 235}) == -1);
    CHECK(au::bootClick(BootState::Quit, centre(au::kTitleButtons[3].rect)) == BootState::Quit);
    // Overlay states ignore clicks (exit is driver-signalled, boot.h law).
    CHECK(au::bootClick(BootState::Intro, centre(au::kTitleButtons[6].rect)) == BootState::Intro);
    CHECK(au::bootClick(BootState::Load, centre(au::kTitleButtons[6].rect)) == BootState::Load);
}

TEST(boot_d9_hotkeys_t385b) {
    // D9 LAW (user 2026-11-14 + vendor title screenshot): Alt-L -> Load,
    // Alt-S -> Save from Title; every other letter is a no-op; the hotkeys
    // do NOT fire from overlay states (they belong to the title screen).
    CHECK(au::bootHotkey(BootState::Title, 'l') == BootState::Load);
    CHECK(au::bootHotkey(BootState::Title, 's') == BootState::Save);
    CHECK(au::bootHotkey(BootState::Title, 'n') == BootState::Title);
    CHECK(au::bootHotkey(BootState::Title, 'r') == BootState::Title);
    CHECK(au::bootHotkey(BootState::RaceConfig, 'l') == BootState::RaceConfig);
    CHECK(au::bootHotkey(BootState::Intro, 's') == BootState::Intro);
    CHECK(au::bootHotkey(BootState::Quit, 'l') == BootState::Quit);
}

TEST(boot_reachability_from_title) {
    // Every target the seven buttons name is reachable; Campaign is the
    // RESUME edge; Quit is reachable (EXITTODOS) but terminal.
    CHECK(au::bootReachableFromTitle(BootState::Intro));
    CHECK(au::bootReachableFromTitle(BootState::Tutorial));
    CHECK(au::bootReachableFromTitle(BootState::RaceConfig));
    CHECK(au::bootReachableFromTitle(BootState::Campaign));
    CHECK(au::bootReachableFromTitle(BootState::Load));
    CHECK(au::bootReachableFromTitle(BootState::Save));
    CHECK(au::bootReachableFromTitle(BootState::Quit));
    CHECK(!au::bootReachableFromTitle(BootState::Title));
    for (int i = 0; i < au::kTitleButtonCount; i++)
        CHECK(au::bootReachableFromTitle(au::kTitleButtons[i].target));
}

TEST(boot_labels_are_vendor_strings) {
    // TEXTITEM 0 strings with '^' joined to spaces (windows.txt verbatim;
    // RESUME's label is "Return to Current Game", NOT "Load Last Save" —
    // the vendor RESUME resumes the in-progress game, LOAD is msg 1/4).
    REQUIRE_DATA();
    CHECK(std::string(au::kTitleButtons[0].label) == "Play Introduction");
    CHECK(std::string(au::kTitleButtons[1].label) == "Tutorial");
    CHECK(std::string(au::kTitleButtons[2].label) == "New Game");
    CHECK(std::string(au::kTitleButtons[3].label) == "Return to Current Game");
    CHECK(std::string(au::kTitleButtons[4].label) == "Load Game");
    CHECK(std::string(au::kTitleButtons[5].label) == "Save Game");
    CHECK(std::string(au::kTitleButtons[6].label) == "Exit to DOS");
}
