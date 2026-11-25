// SPDX-License-Identifier: GPL-3.0-or-later

// tPF-1 TIME CONTROLS (D28 P7) — the NEXTTURNCONT continuous-advance law
// and the harness turn-cap honesty rule.
//
// Vendor law (VERBATIM sources):
//  - window windows.txt ln556 NEXTTURNCONT: TYPE 25, rect 557,52-632,82,
//    SHAPEFRAME 66, SENDMESSAGE 8, BUTTONSTATE 0 (map STATE "1 1").
//  - help.txt "help 1next2" (ln496-509): "This button is used to advance
//    time continually until an event requiring your attention occurs. When
//    such an event occurs, time advancement will automatically stop, and you
//    will be notified of the event."
// The vendor's event-ATTENTION set (which lines stop the pump) is NOT
// captured — seam TPF1-A (ui.h). The port's reading: a NEW event line
// attends iff it is player-relevant (VICTORY prefix, or names "player") or
// carries the one cited notification sound (sfxForEvent, audio.md §5).
//
// D28 P7(b) MEASURED (scripts/tPF1_repro_exit.sh): the plain `--ui` launch
// (no --campaign => turns=0) survives 30 manual NEXT TURN presses — the
// "exits after 20 days" was the HARNESS cap (ui.cpp turns>0 && played>=
// turns) firing on a `--ui --campaign 20` launch, silently. The cap must
// announce itself; these pins pin that announcement.
#include "ui/mapchrome.h"
#include "ui/ui.h"

#include <fstream>
#include <sstream>
#include <string>

#include "harness.h"

#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif

namespace {
namespace au = ascend::ui;
const std::string kRepo = ASCENDANCY_SOURCE_DIR;
}  // namespace

TEST(timecont_rect_matches_windows_txt_tPF1) {
    // NEXTTURNCONT ln556: X0 557 Y0 52 X1 632 Y1 82 (mapchrome.h).
    CHECK(au::kNextTurnCont.x0 == 557);
    CHECK(au::kNextTurnCont.y0 == 52);
    CHECK(au::kNextTurnCont.x1 == 632);
    CHECK(au::kNextTurnCont.y1 == 82);
    // Adjacent to NEXTTURN (474,52-548,82) with the 9-px gutter the vendor
    // draws between the two buttons — the hit maps must never overlap.
    CHECK(au::kNextTurnCont.x0 > au::kNextTurnBtn.x1);
    CHECK(au::kNextTurnCont.y0 == au::kNextTurnBtn.y0);
}

TEST(timecont_attends_player_victory_tPF1) {
    // The end-of-turn VICTORY producer line (campaign.cpp "VICTORY: ...")
    // always attends, and ONLY as a PREFIX.
    CHECK(au::nextTurnContAttends(
        "VICTORY: Control (end-ctrl.txt)"));
    // A line merely CONTAINING "VICTORY" mid-text is not the producer;
    // without the "player" word it stays non-attending (kills the
    // substring-instead-of-prefix mutant — note the UPPERCASE: a lowercase
    // "Victory" example would not distinguish find from rfind).
    CHECK(!au::nextTurnContAttends("the VICTORY of owner 3 celebrated"));
}

TEST(timecont_attends_player_relevance_tPF1) {
    // The player's OWN producer lines carry the raw id "owner 0 " prefix
    // (colonise campaign.cpp:1591, complete :1991).
    CHECK(au::nextTurnContAttends("owner 0 colonised Sol"));
    CHECK(au::nextTurnContAttends("owner 0 completed Nuclear Fusion"));
    // ... but "owner 10" (a two-digit rival) must NOT match the prefix leg.
    CHECK(!au::nextTurnContAttends("owner 10 colonised Vega"));
    // The player-touching diplomacy family (campaign.cpp:1716/1739 texts).
    CHECK(au::nextTurnContAttends(
        "Fludentri declared war on the player"));
    CHECK(au::nextTurnContAttends("Fludentri allied with the player"));
    // Pure AI-side lines (raw owner ids, no "player") do NOT attend —
    // this is what lets the pump keep running through noise.
    CHECK(!au::nextTurnContAttends("owner 3 researched Xenobiology"));
    CHECK(!au::nextTurnContAttends("owner 2 colonise fleet launched"));
    CHECK(!au::nextTurnContAttends("SA_HealShips (owner 6): repaired all ships"));
}

TEST(timecont_attends_notification_sfx_tPF1) {
    // The cited t404 law: an event line containing "captured" plays bang01
    // (audio.md §5) — loud enough to attend even without the word "player".
    CHECK(au::nextTurnContAttends("owner 1 captured star 7"));
    CHECK(!au::nextTurnContAttends("owner 1 bombarded star 7"));
}

TEST(timecont_wiring_tPF1) {
    // The click site latches the pump; NEXT TURN cancels it; the pump tests
    // the attention predicate; the harness cap announces itself.
    std::ifstream f(kRepo + "/rewrite/src/ui/ui.cpp");
    std::stringstream ss;
    ss << f.rdbuf();
    const std::string src = ss.str();

    const size_t click = src.find("inRect(kNextTurnCont, p)");
    CHECK(click != std::string::npos);
    if (click == std::string::npos) return;
    // The latch assignment sits within the click arm (before the next arm).
    const std::string arm = src.substr(click, 900);
    CHECK(arm.find("contMode = true") != std::string::npos);
    CHECK(arm.find("nextAuto = SDL_GetTicks()") != std::string::npos);
    // The t394 inert seam printf is GONE (superseded, not kept alongside).
    CHECK(src.find("next-turn-cont seam") == std::string::npos);

    const size_t manual = src.find("ui click next-turn\\n");
    CHECK(manual != std::string::npos);
    if (manual != std::string::npos) {
        const std::string mArm = src.substr(manual, 400);
        CHECK(mArm.find("contMode = false") != std::string::npos);
    }

    const size_t pump = src.find("if (contMode && !autoplay && SDL_GetTicks()");
    CHECK(pump != std::string::npos);
    if (pump != std::string::npos) {
        const std::string pBlock = src.substr(pump, 1400);
        CHECK(pBlock.find("nextTurnContAttends") != std::string::npos);
        CHECK(pBlock.find("ui cont advance stop") != std::string::npos);
        CHECK(pBlock.find("+ 250") != std::string::npos);  // banked cadence
        CHECK(pBlock.find("camp.over()") != std::string::npos);  // no spin
    }

    const size_t cap = src.find("if (turns > 0 && played >= turns)");
    CHECK(cap != std::string::npos);
    if (cap != std::string::npos) {
        const std::string cBlock = src.substr(cap, 500);
        CHECK(cBlock.find("ui turn cap") != std::string::npos);
    }
}
