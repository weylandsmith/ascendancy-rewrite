// SPDX-License-Identifier: GPL-3.0-or-later
// t404 CLICK-SFX LAW pins (D13 regression: "clicking anywhere in the galaxy
// map makes a laser-fire sound"). Law + citations: ui/audio.h, audio.cpp
// sfxForPress(); measurement trail docs/re/_wip_t404.md + audio.md §6.5-§6.7.
#include <fstream>
#include <sstream>
#include <string>

static const std::string kRepo = ASCENDANCY_SOURCE_DIR;

#include "harness.h"
#include "ui/audio.h"

using namespace ascend::ui;

namespace {
// Null-safe compare: CHECK(std::string(sfxForPress(...)) == ...) would
// construct std::string(nullptr) (UB, suite-crash) whenever a mutant makes
// a site silent — t404 mutation M2/M4/M5 proved this shape. Compare through
// here instead so a silent mutant fails CLEANLY with a named FAIL.
bool streq(const char* a, const char* b) {
    if (!a || !b) return false;
    return std::string(a) == std::string(b);
}
}  // namespace

TEST(sfx_press_mapclick_silent_t404) {
    // The owner-visible bug: EVERY map click played laser01. The vendor
    // SOUNDCHANNEL census {0 x118, -0 x1} names no sample for any control
    // (audio.md §6.6), and the port has no fire-order interaction, so a map
    // click must play NOTHING.
    CHECK(sfxForPress(UiPressSite::MapClick) == nullptr);
}

TEST(sfx_press_buttons_button_t437) {
    // t437 MEASURED LAW (supersedes the t404 click08 port choice): the
    // windows.txt SOUNDCHANNEL store 0x57e7a (mov WORD [rec+0x59],ax) feeds
    // the strategic press handler's play (HIWORD dword[rec+0x57], site
    // 0x30e75); SOUNDCHANNEL == 0 on all 119 file lines and +0x59 == 0 on
    // 2,400/2,400 file-declared records in 20 saves; manifest[0] == "button"
    // (audio.md §6.9, docs/re/_wip_t437.md F1-F5). click08 is OFF-manifest
    // (t395) — the vendor cannot play it at all.
    CHECK(streq(sfxForPress(UiPressSite::RailButton), "button"));
    CHECK(streq(sfxForPress(UiPressSite::NextTurn), "button"));
    CHECK(streq(sfxForPress(UiPressSite::TitleButton), "button"));
}

TEST(sfx_press_out_of_range_silent_t404) {
    // An unmapped site must resolve to silence, never a garbage sample
    // (same defensive shape as playTune's t395 guard).
    CHECK(sfxForPress(static_cast<UiPressSite>(99)) == nullptr);
}

TEST(sfx_event_captured_bang01_t404) {
    // audio.md §5 documented port choice: a NEW event line containing
    // "captured" calls bang01; every other event text is silent (the vendor
    // table names no id, §6.6).
    CHECK(streq(sfxForEvent("Highbeam was captured!"), "bang01"));
    CHECK(sfxForEvent("Research completed: Robotics") == nullptr);
    CHECK(sfxForEvent("") == nullptr);
}

TEST(sfx_no_literal_play_sites_in_ui_t404) {
    // Source-text pin for the sweep half of the row: after t404 EVERY sound
    // the UI plays routes through sfxForPress/sfxForEvent, so no file under
    // rewrite/src may call play() with a string literal. A re-added
    // placeholder fails here even if no behavioural test covers its rect.
    for (const char* f : {"rewrite/src/ui/ui.cpp", "rewrite/src/ui/title.cpp",
                          "rewrite/src/main.cpp"}) {
        std::ifstream in(kRepo + "/" + f);
        std::stringstream ss;
        ss << in.rdbuf();
        const std::string src = ss.str();
        CHECK(src.find("play(\"") == std::string::npos);
    }
}
