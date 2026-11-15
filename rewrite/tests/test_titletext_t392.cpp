// SPDX-License-Identifier: GPL-3.0-or-later

// t392 title-text pins (D10 user grade: "text is a tad too high in the
// boxes" + "Alt-L/Alt-S/Alt-X second lines are missing"). Law + every
// measurement: docs/re/boot.md §7 + docs/re/_wip_t392.md. The geometry
// constants are the MEASURED ink-row tops on the pinned vendor shot
// docs/assets/refcap/original-title-menu.png; the hint strings are the
// vendor TEXTITEM display strings verbatim (windows.txt L129/149/170).
#include "ui/boot.h"

#include "harness.h"

namespace {
namespace au = ascend::ui;
using au::BootState;
}  // namespace

TEST(titletext_hint_table_matches_windows_txt) {
    // WINITEMS law: buttons 0..3 have ONE TEXTITEM (no hint); LOAD/SAVE/
    // EXITTODOS have TWO, the second being the Alt-* string VERBATIM
    // (hyphen, capital A, capital trailing letter — exactly as in the
    // table, not "Alt+L" or "ALT-L").
    REQUIRE_DATA();
    const char* exp[7] = {nullptr, nullptr, nullptr, nullptr, "Alt-L",
                          "Alt-S", "Alt-X"};
    for (int i = 0; i < 7; i++) {
        const char* h = au::kTitleButtons[i].hint;
        if (exp[i]) {
            CHECK(h != nullptr);
            if (h) CHECK(std::string(h) == exp[i]);
        } else {
            CHECK(h == nullptr);
        }
    }
}

TEST(titletext_baseline_law_constants) {
    // The three draw-TOP constants (measured ink rows on the vendor shot:
    // single-line ink starts dy8; pair buttons ink dy4 and dy18 — and the
    // TEXTITEM dy fields 4/18 land on the same rows).
    CHECK(au::kTitleLabelTopSingle == 8);
    CHECK(au::kTitleLabelTopPair == 4);
    CHECK(au::kTitleHintTop == 18);
    // Pair geometry sanity: hint row + small-ink band stays INSIDE the
    // 30-px vendor rect (18 + 11 = 29 <= 29). The pre-t390 +4 single draw
    // is what made the user read "too high" (our ink rows landed dy4..14
    // vs the vendor's dy8..18 — measured delta exactly -4).
    CHECK(au::kTitleHintTop + 11 <= 29);
    CHECK(au::kTitleLabelTopPair < au::kTitleHintTop);
}

TEST(titletext_hotkey_map_includes_alt_x) {
    // Alt-chord routing: l -> Load, s -> Save, x -> Quit (the EXITTODOS
    // twin, windows.txt L170); anything else is a no-op, and the map is
    // Title-only (never fires from Campaign/Quit/Intro).
    CHECK(au::bootHotkey(BootState::Title, 'l') == BootState::Load);
    CHECK(au::bootHotkey(BootState::Title, 's') == BootState::Save);
    CHECK(au::bootHotkey(BootState::Title, 'x') == BootState::Quit);
    CHECK(au::bootHotkey(BootState::Title, 'q') == BootState::Title);
    CHECK(au::bootHotkey(BootState::Campaign, 'x') == BootState::Campaign);
    CHECK(au::bootHotkey(BootState::RaceConfig, 'l') == BootState::RaceConfig);
    CHECK(au::bootHotkey(BootState::Quit, 'x') == BootState::Quit);
}

TEST(titletext_hint_targets_are_their_own_buttons) {
    // The hotkey target must be the state its button's own click selects
    // (twin law): LOAD row -> Load, SAVE row -> Save, EXITTODOS row ->
    // Quit. Derived from the table, so a retarget of either side trips.
    REQUIRE_DATA();
    using au::Pt;
    const au::TitleButton& load = au::kTitleButtons[4];
    const au::TitleButton& save = au::kTitleButtons[5];
    const au::TitleButton& quit = au::kTitleButtons[6];
    Pt c{200, 0};
    CHECK(au::bootClick(BootState::Title, {c.x, load.rect.y0 + 15}) ==
          au::bootHotkey(BootState::Title, 'l'));
    CHECK(au::bootClick(BootState::Title, {c.x, save.rect.y0 + 15}) ==
          au::bootHotkey(BootState::Title, 's'));
    CHECK(au::bootClick(BootState::Title, {c.x, quit.rect.y0 + 15}) ==
          au::bootHotkey(BootState::Title, 'x'));
}
