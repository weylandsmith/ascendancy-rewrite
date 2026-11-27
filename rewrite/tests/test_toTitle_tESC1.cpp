// SPDX-License-Identifier: GPL-3.0-or-later

// tESC-1 EJECT-TO-TITLE LAW (D31, 2026-11-27). Vendor Escape at the
// campaign screen-stack bottom does NOT end the process: the hotkey
// dispatcher fn 0x54d18's ESC arm 0x54e96 calls ONLY the pop
// FUN_00057020(obj, -1) — no exit syscall anywhere in the chain — and the
// ejection lands on the TITLE menu with the campaign ALIVE in RAM (t285
// LIVE witness: one Escape at the bare map -> title, autosave kept
// writing; work/r1/bank-t285-flip1255/). The port must model exactly
// that. Full citations: docs/re/_wip_tESC1.md (P1-P6).
//
// Pins are source-scan (the established ui.cpp pattern, cf.
// test_quitcause_tPF1d): the eject leg names its cause AND sets the flag,
// the handoff happens ONLY on the eject leg, and main() re-enters the
// title loop with the per-entry newGame reset. Runtime counterpart:
// scripts/tESC1_eject_witness.sh (4 legs, all asserted).
#include "harness.h"

#include <fstream>
#include <sstream>
#include <string>

#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif

namespace {
const std::string kRepo = ASCENDANCY_SOURCE_DIR;
std::string slurp(const std::string& rel) {
    std::ifstream f(kRepo + "/" + rel);
    std::stringstream ss;
    ss << f.rdbuf();
    return ss.str();
}
}  // namespace

TEST(toTitle_eject_leg_sets_flag_and_cause_tESC1) {
    const std::string src = slurp("rewrite/src/ui/ui.cpp");
    // The bottom-of-stack branch names the cause (tPF-1d instrument stays
    // intact) AND raises the eject flag before quitting the loop.
    const size_t cause = src.find("quitCause = escCause;");
    const size_t flag = src.find("toTitle = true;");
    const size_t quitsite = src.find("quit = true;", flag);
    CHECK(cause != std::string::npos);
    CHECK(flag != std::string::npos);
    CHECK(quitsite != std::string::npos);
    if (cause == std::string::npos || flag == std::string::npos) return;
    CHECK(cause < flag && flag < quitsite);
    // Anti-comment trap (tPF-10 law): the statement must sit on a line that
    // is NOT a comment (a `// toTitle = true;` mutation must not satisfy the
    // substring scan).
    {
        const size_t ls = src.rfind('\n', flag);
        const std::string line = src.substr(ls + 1, 80);
        const std::string::size_type t = line.find_first_not_of(" \t");
        CHECK(t != std::string::npos && line.compare(t, 2, "//") != 0);
    }
    // The witness line prints BEFORE 'ui ok' (D31 ordering law shared with
    // the quit-cause instrument).
    const size_t print = src.find("if (toTitle) std::printf(\"ui to title");
    const size_t ok = src.find("ui ok: turn %d");
    CHECK(print != std::string::npos);
    CHECK(ok != std::string::npos);
    if (print != std::string::npos && ok != std::string::npos)
        CHECK(print < ok);
    // Exactly one eject-flag setter and one witness emit site (anti-vacuity).
    CHECK(src.find("toTitle = true;") == src.rfind("toTitle = true;"));
}

TEST(toTitle_window_handoff_only_on_eject_tESC1) {
    const std::string src = slurp("rewrite/src/ui/ui.cpp");
    // The window is handed back ONLY when the eject leg fired AND the
    // caller asked for it; every other leg keeps the standing destroy.
    const size_t handoff = src.find("const bool handOff = toTitle && windowOut");
    CHECK(handoff != std::string::npos);
    if (handoff == std::string::npos) return;
    const std::string tail = src.substr(handoff, 400);
    CHECK(tail.find("if (owned && !handOff) SDL_DestroyWindow(win);") !=
          std::string::npos);
    CHECK(tail.find("if (handOff) *windowOut = win;") != std::string::npos);
    CHECK(tail.find("if (outToTitle) *outToTitle = toTitle;") !=
          std::string::npos);
    // Title side: windowIn reuse (t385 single-window law — creating a
    // second window would eat the title's first synthetic click).
    const std::string title = slurp("rewrite/src/ui/title.cpp");
    CHECK(title.find("static_cast<SDL_Window*>(windowIn)") !=
          std::string::npos);
    CHECK(title.find("const bool winOwned = win == nullptr;") !=
          std::string::npos);
}

TEST(toTitle_main_reentry_loop_tESC1) {
    const std::string src = slurp("rewrite/src/main.cpp");
    // main() loops title<->campaign: the runCampaignUi call passes BOTH
    // handoff out-params, the loop breaks only when NOT ejecting, and the
    // re-entry witness names the live turn.
    CHECK(src.find("&toTitle, &handedWindow);") != std::string::npos);
    CHECK(src.find("if (!toTitle) break;") != std::string::npos);
    CHECK(src.find("main: campaign -> title (campaign alive turn %d)") !=
          std::string::npos);
    // Per-entry reset: a stale Begin triple must NOT rebuild (destroy) the
    // live mid-game campaign on title re-entry. The reset sits INSIDE the
    // loop, before the runTitleScreen call.
    const size_t reset = src.find("newGame = ascend::ui::NewGameSettings{};");
    const size_t call = src.find("const BootState exit = ascend::ui::runTitleScreen(");
    const size_t reentry = src.find("entryState = BootState::Title;");
    CHECK(reset != std::string::npos);
    CHECK(call != std::string::npos);
    CHECK(reentry != std::string::npos);
    if (reset == std::string::npos || call == std::string::npos) return;
    CHECK(reset < call);
    // Re-entry lands on Title (vendor draws the title overlay; --resume
    // players pick RESUME msg 1/1) — and it sits AFTER the break check,
    // i.e. only the eject path reaches it.
    const size_t brk = src.find("if (!toTitle) break;");
    CHECK(brk != std::string::npos && brk < reentry);
}
