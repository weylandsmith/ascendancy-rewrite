// SPDX-License-Identifier: GPL-3.0-or-later

// tA3 TEXT LAW pins (PHASE-17 Stage A row 3). Law + every measurement:
// docs/re/_wip_tA3.md (F1-F4). Sources: docs/assets/refcap/original-
// strategic-map.png (palette-exact; root row = window + 40),
// scratchpad/newgame-original.png (user browser shot; crop law
// screen = image - 1), windows.txt TEXTITEM lines verbatim, and the
// vendor .fnt extents (docs/re/fnt.md: big H=11 caps rows 0..9, sm H=8
// caps rows 0..6, advance == width). The live face/baseline witness is
// scripts/r1_tA3_witness.py (template fits vs our Xvfb render).
#include "ui/hudlayout.h"
#include "ui/menulaw.h"
#include "ui/statuslaw.h"

#include "harness.h"

namespace {
namespace au = ascend::ui;

// bigfont advance sums, script-measured from
// extracted/ascend01/data/bigfont.fnt (advance == width law). The
// loader-side glyph identity is pinned by test_fnt.cpp; these sums pin
// the CENTRE arithmetic the draw sites rely on.
int bigAdv(const char* s) {
    static const struct { const char* w; int adv; } kAdv[] = {
        {"Species", 40},         {"Star Density", 66},
        {"Atmosphere", 61},      {"Player Color", 65},
        {"Begin New Game", 88},  {"Player Species", 78},
        {"Planets", 38},         {"Ships", 28},
        {"Research", 49},        {"Special Ability", 71},
    };
    for (const auto& e : kAdv)
        if (std::string(s) == e.w) return e.adv;
    return -1;
}
int absd(int v) { return v < 0 ? -v : v; }
}  // namespace

TEST(ta3_rail_text_law_constants) {
    // TEXTITEM "0 Species 0 2 2" family: draw TOP = y0+2 (measured EXACT
    // on the map refcap, root=window+40), cell origin x0+2 ('S' cell 476
    // in rect x0 474; bigfont 'S' inks from cell column 1).
    CHECK(au::kRailLabelDx == 2);
    CHECK(au::kRailLabelDy == 2);
    // The widest rail label must clear the SHAPEITEM icon at dx=109.
    CHECK(au::kRailLabelDx + bigAdv("Special Ability") < au::kRailIconDx);
    // Labels are the TEXTITEM display strings verbatim.
    CHECK(std::string(au::railLabel(au::RailButton::Status)) == "Planets");
    CHECK(std::string(au::railLabel(au::RailButton::Fleet)) == "Ships");
    CHECK(std::string(au::railLabel(au::RailButton::Research)) == "Research");
    CHECK(std::string(au::railLabel(au::RailButton::SpecialAbility)) ==
          "Special Ability");
    CHECK(std::string(au::railLabel(au::RailButton::Races)) == "Species");
}

TEST(ta3_newgame_text_law_constants) {
    // Control labels: TEXTITEM dy=10 verbatim; Player Color y0+12
    // (browser row 394 minus the same-window +1 drift the dy=10 trio
    // shows — all three measure 392 for logical 391).
    CHECK(au::kControlLabelDy == 10);
    CHECK(au::kPlayerColorLabelDy == 12);
    // Ink tops [measured, crop-law screen rows]: name 17..26, header
    // 15..24, summary tops 326/339/352 pitch 13, lore 265 pitch 11.
    CHECK(au::kNameTop == 17);
    CHECK(au::kHeaderTop == 15);
    CHECK(au::kSummaryTop == 326);
    CHECK(au::kSummaryPitch == 13);
    CHECK(au::kLoreTextTop == 265);
    CHECK(au::kLoreLinePitch == 11);
    CHECK(au::kBeginLabelTop == 455);
    // Ordering sanity: lore text starts INSIDE its box on the sm cell.
    CHECK(au::kLoreTextTop >= au::kLoreBox.y0);
    CHECK(au::kLoreTextTop + 8 <= au::kLoreBox.y1);
}

TEST(ta3_centre_law_within_1px_of_measured_fits) {
    // The centred draw law (cell x = (x0+x1)/2 - adv/2, integer div —
    // the form every port draw site uses) must land within 1 px of every
    // template-fit x measured on the user original (browser shot; the +1
    // drift law maps them to logical).
    struct Site {
        const char* word;
        int x0, x1;   // rect (inclusive)
        int measured; // fit x [verified, _wip_tA3 F2/F3]
    };
    const Site sites[] = {
        {"Star Density", 7, 122, 31},   {"Species", 131, 246, 168},
        {"Atmosphere", 255, 370, 282},  {"Player Color", 379, 493, 403},
        {"Player Species", 502, 632, 528},
    };
    for (const auto& s : sites) {
        const int x = (s.x0 + s.x1) / 2 - bigAdv(s.word) / 2;
        CHECK(absd(x - s.measured) <= 1);
    }
    // Begin New Game centres on the panel rect 502..632: measured fit 523
    // == 502 + (131-88)/2 == (502+632)/2 - 88/2.
    CHECK((502 + 632) / 2 - bigAdv("Begin New Game") / 2 == 523);
    // Summary centre law: "Neutral Atmosphere" (adv 103) at centre 170
    // measured fit x=119 y=352 [verified iou 0.657 vs off-centre 0.13-0.22].
    CHECK(170 - 103 / 2 == 119);
}
