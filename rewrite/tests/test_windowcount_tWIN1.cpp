// SPDX-License-Identifier: GPL-3.0-or-later

// tWIN-1 SINGLE-WINDOW LAW ACROSS THE EJECT (D32 third leg, 2026-11-27).
// The user reported that escaping from the galaxy screen to the title
// "opens a new window" and things get buggy. REPRODUCED at the window
// level (scripts/tWIN1_window_witness.sh pre-fix run, banked
// docs/re/_wip_tWIN1.md W1): main.cpp's re-entry call to runTitleScreen
// omitted the 12th arg (windowIn, default nullptr), so title.cpp took the
// winOwned branch and SDL_CreateWindow'd a SECOND window while the
// handed-back campaign window survived renderer-less (ui.cpp destroys the
// renderer before the handOff check) — the "elements don't get drawn"
// half of the symptom. Vendor law: ONE window the whole session (t385).
//
// Pins follow the anchored-statement pattern (tSPEC-1 law): extract the
// runTitleScreen call's ARGUMENT TEXT between the parens and strip
// comments, so a mutation that deletes the arg — or hides it in a comment
// (tESC-1 M1 law) — cannot satisfy the scan.
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
// Drop // comments (line-wise) so commented-out statements cannot
// false-satisfy a substring scan (tESC-1 M1 trap).
std::string stripComments(const std::string& s) {
    std::string out;
    std::istringstream f(s);
    std::string line;
    while (std::getline(f, line)) {
        const size_t c = line.find("//");
        if (c != std::string::npos) line.resize(c);
        out += line;
        out += '\n';
    }
    return out;
}
}  // namespace

TEST(eject_reentry_passes_handedWindow_as_windowIn_tWIN1) {
    const std::string src = stripComments(slurp("rewrite/src/main.cpp"));
    const std::string anchor = "const BootState exit = ascend::ui::runTitleScreen(";
    const size_t call = src.find(anchor);
    CHECK(call != std::string::npos);
    if (call == std::string::npos) return;
    // Balanced-paren extraction of the argument text (args contain no
    // string literals with parens on this call; nested parens like
    // rosterForUi(o) are handled by the counter).
    size_t i = call + anchor.size(), depth = 1, start = i;
    while (i < src.size() && depth > 0) {
        if (src[i] == '(') depth++;
        else if (src[i] == ')') depth--;
        i++;
    }
    CHECK(depth == 0);
    if (depth != 0) return;
    const std::string args = src.substr(start, i - 1 - start);
    // THE fix: the window handoff word must appear in the arg list, and as
    // the LAST arg (the windowIn slot is the 12th/last parameter per
    // ui.h:34-55). Count commas at depth 0 to prove last-ness.
    CHECK(args.find("handedWindow") != std::string::npos);
    const size_t lastComma = args.rfind(',');
    CHECK(lastComma != std::string::npos);
    if (lastComma != std::string::npos) {
        const std::string lastArg = args.substr(lastComma + 1);
        CHECK(lastArg.find("handedWindow") != std::string::npos);
        CHECK(lastArg.find(',') == std::string::npos);  // truly last
    }
    // Anti-vacuity: the word exists elsewhere too (the campaign call), so
    // the extraction — not a file-wide grep — is what makes this a pin.
    CHECK(src.find("handedWindow") != src.rfind("handedWindow"));
}

TEST(title_reuse_and_eject_handoff_chain_intact_tWIN1) {
    // The two ends of the handoff must BOTH stay wired: title consumes
    // windowIn (no create when non-null), campaign hands back ONLY on the
    // eject leg. (tESC-1 pinned these statements; this pin re-anchors the
    // CHAIN, which is what the defect actually broke at main.cpp.)
    const std::string title = stripComments(slurp("rewrite/src/ui/title.cpp"));
    CHECK(title.find("static_cast<SDL_Window*>(windowIn)") != std::string::npos);
    CHECK(title.find("const bool winOwned = win == nullptr;") !=
          std::string::npos);
    // The create must stay GATED on winOwned (mutation: unconditional
    // create re-opens the second-window bug while keeping the cast).
    const size_t gate = title.find("if (winOwned)");
    const size_t create = title.find("SDL_CreateWindow(\"Ascendancy\"");
    CHECK(gate != std::string::npos);
    CHECK(create != std::string::npos);
    if (gate != std::string::npos && create != std::string::npos)
        CHECK(gate < create && create - gate < 400);
    const std::string ui = stripComments(slurp("rewrite/src/ui/ui.cpp"));
    CHECK(ui.find("const bool handOff = toTitle && windowOut") !=
          std::string::npos);
    CHECK(ui.find("if (owned && !handOff) SDL_DestroyWindow(win);") !=
          std::string::npos);
    CHECK(ui.find("if (handOff) *windowOut = win;") != std::string::npos);
}
