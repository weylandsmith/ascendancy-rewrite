// SPDX-License-Identifier: GPL-3.0-or-later

// tPF-1d QUIT-CAUSE INSTRUMENT (D31, 2026-11-26 steering). The day-20 exit
// the user reported is an UNREPRODUCED defect (the Escape-at-bottom closure
// was REFUTED by testimony: "the mouse never moved from the next day
// button"). D30/D31 law: never close a user-reported defect by attributing
// the symptom to the user — ship the self-diagnosing instrument instead:
// EVERY exit path from runCampaignUi prints "ui quit cause=<CAUSE> turn=N"
// BEFORE "ui ok: turn N", so the user's own next run names the path.
//
// Pins are source-scan (the established ui.cpp pattern, cf.
// test_timecontrols_tPF1): the print exists, sits BEFORE the ui-ok line,
// occurs exactly once, and every named path assigns its cause.
#include "harness.h"

#include <fstream>
#include <sstream>
#include <string>

#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif

namespace {
const std::string kRepo = ASCENDANCY_SOURCE_DIR;
std::string uiSrc() {
    std::ifstream f(kRepo + "/rewrite/src/ui/ui.cpp");
    std::stringstream ss;
    ss << f.rdbuf();
    return ss.str();
}
}  // namespace

TEST(quitcause_print_before_ui_ok_tPF1d) {
    const std::string src = uiSrc();
    const size_t cause = src.find("ui quit cause=%s turn=%d");
    const size_t ok = src.find("ui ok: turn %d");
    CHECK(cause != std::string::npos);
    CHECK(ok != std::string::npos);
    if (cause == std::string::npos || ok == std::string::npos) return;
    // D31 ordering: the cause line must precede "ui ok" in program order.
    CHECK(cause < ok);
    // Anti-vacuity: the print fires unconditionally on the exit path (the
    // only guard is the loop exit itself) — exactly one emit site.
    CHECK(src.find("ui quit cause=%s turn=%d") == src.rfind("ui quit cause=%s turn=%d"));
    const std::string tail = src.substr(ok, 700);
    CHECK(tail.find("txt.release()") != std::string::npos);
}

TEST(quitcause_every_path_named_tPF1d) {
    const std::string src = uiSrc();
    // Every quit=true site carries a tPF-1d cause. Count census: the
    // instrument must cover ALL of them, so quit=true assignments and
    // cause assignments must be the same count (plus doEscape's shared
    // else-branch, which takes the cause as a parameter).
    size_t quits = 0, causes = 0;
    for (size_t p = src.find("quit = true;"); p != std::string::npos;
         p = src.find("quit = true;", p + 1))
        ++quits;
    for (size_t p = src.find("quitCause ="); p != std::string::npos;
         p = src.find("quitCause =", p + 1))
        ++causes;
    // 5 quit=true sites: doEscape else-branch, SDL_QUIT, load-screen, cap,
    // victory. Causes: declaration initializer + the same 5 assignments = 6
    // (doEscape's site takes the cause via its parameter).
    CHECK(quits == 5);
    CHECK(causes == 6);
    // The named paths (D31's list, minus victory which is its own test).
    CHECK(src.find("\"sdl-window-close\"") != std::string::npos);
    CHECK(src.find("\"escape-key-at-bottom\"") != std::string::npos);
    CHECK(src.find("\"corner-exit-click\"") != std::string::npos);
    CHECK(src.find("\"load-screen-quit\"") != std::string::npos);
    CHECK(src.find("\"harness-turn-cap\"") != std::string::npos);
    // doEscape must take the cause so the keyboard leg and the corner-click
    // leg are distinguishable (both share the else-branch).
    CHECK(src.find("doEscape(\"escape-key-at-bottom\")") != std::string::npos);
    CHECK(src.find("doEscape(\"corner-exit-click\")") != std::string::npos);
}

TEST(quitcause_victory_names_enum_tPF1d) {
    const std::string src = uiSrc();
    const size_t leg = src.find("if (camp.over() && !quit)");
    CHECK(leg != std::string::npos);
    if (leg == std::string::npos) return;
    const std::string block = src.substr(leg, 300);
    // The enum NAME (victoryName), not a hardcoded word — the cause reads
    // "victory:Control" etc. via the pinned campaign.cpp:103 table.
    CHECK(block.find("victoryName(camp.victory())") != std::string::npos);
    CHECK(block.find("\"victory:\"") != std::string::npos);
    // Anti-overwrite: once the cap latched, the victory leg must not steal
    // the cause (the !quit guard above is the pin).
}
