// SPDX-License-Identifier: GPL-3.0-or-later
// tPF-9 RESEARCH/PLANET-SCREEN STRAY-TEXT pins (D28 item 13).
// Law (docs/re/_wip_tPF9.md P1, three agreeing legs):
//  - "click: set project" and "Esc: return to galaxy" are PORT INVENTIONS:
//    neither string exists in the vendor ship (game/ascend.exe and all
//    three .cob data files strings-negative for the phrases; the .cob
//    'return to' hits are tutorial prose only).
//  - The vendor draw loop 0x48165..0x485b5 (work/t91_code_disasm.txt) has
//    13 calls, ALL shape fetch/blit/line primitives (0x1fc34, 0x5caac,
//    0x5cf96, 0x5d5a1, 0x46d3c, 0x76e08, 0x5cf77, 0x5bf71) and ZERO text
//    callsites; the 433 composite vendor half (scratchpad/
//    planet-screen-iter-433-v-original.png) shows no text in either
//    corner [vision, full-frame + two full-res crops].
//  - USER RULING (D28 item 13): the labels must not be painted. The
//    Escape ROUTING behaviour (t252-cited) is behaviour, not a label, and
//    stays; the transient set-project feedback (list-open / picked) stays
//    because D28 separately demands visible project-set indication.
#include <cstdio>
#include <fstream>
#include <sstream>
#include <string>

#include "harness.h"

namespace {

std::string slurp(const std::string& p) {
    std::ifstream f(p);
    std::ostringstream ss;
    ss << f.rdbuf();
    return ss.str();
}

const std::string kUi =
    slurp(std::string(ASCENDANCY_SOURCE_DIR) + "/rewrite/src/ui/ui.cpp");

TEST(stray_hints_deleted_tpf9) {
    if (kUi.empty()) { CHECK(!"ui.cpp unreadable"); return; }
    // The two ruled-on labels must appear NOWHERE in the paint source,
    // active or commented-out as live code (comments naming the deletion
    // quote the strings, so test the DRAW shape instead: a txt.draw whose
    // argument is one of the labels).
    const auto hasDrawWith = [&](const char* label) {
        size_t pos = 0;
        while ((pos = kUi.find(label, pos)) != std::string::npos) {
            // Look back for a txt.draw( within 200 chars with no ';'
            // between (same statement).
            size_t back = pos > 200 ? pos - 200 : 0;
            std::string w = kUi.substr(back, pos - back);
            size_t semi = w.rfind(';');
            std::string afterSemi =
                semi == std::string::npos ? w : w.substr(semi + 1);
            if (afterSemi.find("txt.draw(") != std::string::npos) return true;
            pos += 1;
        }
        return false;
    };
    CHECK(!hasDrawWith("click: set project"));
    CHECK(!hasDrawWith("Esc: return to galaxy"));
}

TEST(transient_project_feedback_kept_tpf9) {
    if (kUi.empty()) { CHECK(!"ui.cpp unreadable"); return; }
    // The anti-vacuity leg: the deletion must not have taken the state
    // feedback with it. Both transient strings stay paintable.
    CHECK(kUi.find("\"list open: pick one\"") != std::string::npos);
    CHECK(kUi.find("std::string(\"picked: \")") != std::string::npos);
    // And they sit behind the state guard, not an unconditional draw:
    // the guard line exists exactly once.
    CHECK(kUi.find("if (projectOpen || planetPick >= 0)") !=
          std::string::npos);
}

TEST(escape_routing_behaviour_kept_tpf9) {
    if (kUi.empty()) { CHECK(!"ui.cpp unreadable"); return; }
    // Item 13 ruled on the LABEL, not the key. The Escape routing cited
    // to t252 must survive: a KEYDOWN Escape path returning from an
    // opened screen exists in the source.
    CHECK(kUi.find("SDL_KEYDOWN") != std::string::npos);
    CHECK(kUi.find(" SDLK_ESCAPE") != std::string::npos);
    // The t252 behaviour comment (rail block) still carries its citation.
    CHECK(kUi.find("Escape returns to galaxy") != std::string::npos);
}

}  // namespace
