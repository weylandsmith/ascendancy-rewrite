// SPDX-License-Identifier: GPL-3.0-or-later

// tPF-11 RESEARCH-SCREEN CHROME pins (D28 item 22 "the mineral framing is
// missing from this screen"). Laws MEASURED on the vendor capture
// work/screens/t252/research_open_game.png — scripts/tPF11_chrome_measure.py
// + tPF11_panel_edges.py, banked docs/re/_wip_tPF11.md P3 + statusbg.h.
//   1. Band table reproduces the measured edge cases: perimeter 0..6 /
//      633..639 full height, top rows 0..6, bottom resumes at y473 (y472
//      measured BLACK in the tree-field span x10..469), panel left band
//      x477..484 y46..433 (x477 tex run 44..472 minus the ramp rows; the
//      interior x485 is black), panel bottom well y434..472, panel top
//      texture rows 38..45.
//   2. The tree-field interior is NOT a band: (100,100), (7,300) [flush-
//      black left edge, x7 measured (0,0,0) 423/423], (476,472), (485,100).
//   3. Research ramp rows 38..45 verbatim modes; NO y46 (measured BLACK
//      580/580) and NO y37/y47.
//   4. The status ramp keeps its own y46 SOLID (33,56,57) tail (the
//      per-screen split is two-way: shipping research must not move status).
// No vendor data is read: no REQUIRE_DATA() needed (t403 guard census).
#include "ui/statusbg.h"
#include "ui/statuslaw.h"

#include <fstream>

#include "harness.h"

namespace {
namespace au = ascend::ui;
}  // namespace

TEST(reschrome_bands_tpf11) {
    // Perimeter bands [measured texfrac 1.000 all four edges].
    CHECK(au::resChromeBandAt(0, 0));
    CHECK(au::resChromeBandAt(6, 240));
    CHECK(au::resChromeBandAt(633, 240));
    CHECK(au::resChromeBandAt(639, 479));
    CHECK(au::resChromeBandAt(320, 6));    // top band rows 0..6
    CHECK(au::resChromeBandAt(320, 473));  // bottom resumes y473
    // y472 measured BLACK across the tree-field span x10..469 (the status
    // band law kStatusTextureBands starts at y472 — the research law is
    // measured ONE ROW LOWER; do not "unify" them).
    CHECK(!au::resChromeBandAt(100, 472));
    // Panel left border band x477..484 y46..433; interior x485 black.
    CHECK(au::resChromeBandAt(477, 46));
    CHECK(au::resChromeBandAt(484, 433));
    CHECK(!au::resChromeBandAt(485, 250));
    CHECK(!au::resChromeBandAt(476, 250));  // tree field flush to x476
    // Panel bottom well y434..472 (the pan buttons paint OVER it).
    CHECK(au::resChromeBandAt(477, 434));
    CHECK(au::resChromeBandAt(639, 472));
    // Panel top texture rows 38..45 x477..639 [measured: y39/y41 tex runs
    // reach x639].
    CHECK(au::resChromeBandAt(500, 41));
    // Tree-field interior is NOT chrome (header speckle is a separate
    // texture; the field is flush-black).
    CHECK(!au::resChromeBandAt(100, 100));
    CHECK(!au::resChromeBandAt(7, 300));   // x7 measured (0,0,0) 423/423
    CHECK(!au::resChromeBandAt(240, 46));
}

TEST(reschrome_ramp_tpf11) {
    au::RGB c{};
    CHECK(au::resRampColourAt(38, &c));
    CHECK(c.r == 82 && c.g == 125 && c.b == 123);
    CHECK(au::resRampColourAt(39, &c) && c.r == 123 && c.g == 182);
    CHECK(au::resRampColourAt(40, &c));
    CHECK(au::resRampColourAt(41, &c) && c.r == 115 && c.g == 117);
    CHECK(au::resRampColourAt(42, &c) && c.r == 66 && c.g == 105);
    CHECK(au::resRampColourAt(43, &c) && c.r == 33 && c.g == 56 && c.b == 57);
    CHECK(au::resRampColourAt(44, &c) && c.r == 24 && c.g == 48 && c.b == 41);
    CHECK(au::resRampColourAt(45, &c) && c.r == 24 && c.g == 28 && c.b == 24);
    // y46 measured BLACK 580/580 on the research capture: no ramp colour.
    CHECK(!au::resRampColourAt(46, &c));
    CHECK(!au::resRampColourAt(37, &c));
    CHECK(!au::resRampColourAt(47, &c));
}

TEST(reschrome_status_split_tpf11) {
    // The per-screen split is TWO-WAY: the status screen keeps its y46
    // SOLID (33,56,57) tail + x7 border (t3 capture law, statusbg.h) —
    // shipping the research variant must not move the status table.
    au::RGB c{};
    CHECK(au::statusRampColourAt(46, &c));
    CHECK(c.r == 33 && c.g == 56 && c.b == 57);
    CHECK(au::kStatusBorderX == 7);
    // ... and the research law declines exactly that row.
    CHECK(!au::resRampColourAt(46, &c));
    // Research is a known screen and keeps the state-20 lib naming (the
    // 20res.shp BUTTONS law t435 F5 is untouched by the chrome ship).
    CHECK(au::screenKnown(au::kScreenResearch));
}

TEST(reschrome_speckle_shared_tpf11) {
    // The header speckle is the SAME generator + census rect as status
    // [measured: research census holds the same six non-text colours
    // (0,0,0)/(8,12,16)/(8,12,8)/(8,28,49)/(8,32,49)/(8,36,49)].
    // Determinism + census-set membership over the rect.
    const au::Rect& r = au::kStatusSpeckleRect;
    CHECK(r.x0 == 8 && r.y0 == 8 && r.x1 == 630 && r.y1 == 36);
    const au::RGB a = au::statusSpeckleAt(100, 20);
    CHECK(au::statusSpeckleAt(100, 20).r == a.r &&
          au::statusSpeckleAt(100, 20).g == a.g &&
          au::statusSpeckleAt(100, 20).b == a.b);
    bool inCensus = false;
    for (int i = 0; i < au::kSpeckleCount; i++)
        if (a.r == au::kSpeckleColours[i].r &&
            a.g == au::kSpeckleColours[i].g &&
            a.b == au::kSpeckleColours[i].b) inCensus = true;
    CHECK(inCensus);
}

// 5. WIRING (source-text; pins are blind to ui.cpp — tPF-7 M4 lesson).
//    (a) the research paint arm copies the chrome texture AND the speckle
//        texture AND runs the ramp loop 38..45 via resRampColourAt;
//    (b) the tan header-box condition declines kScreenResearch;
//    (c) the gray kLane interior-rect condition declines kScreenResearch;
//    (d) the retired invented panel border (the 90/90/110 draw-rect) is
//        GONE from ui.cpp.
//    WINDOW-PIN LAW (tPF-1b): windows sized generously past the anchor,
//    npos-guarded (tPF-10 crash trap), and NO check counts a marker whose
//    literal may appear in comments.
TEST(reschromewiring_tpf11) {
    std::ifstream f(std::string(ASCENDANCY_SOURCE_DIR) +
                    "/rewrite/src/ui/ui.cpp");
    CHECK(f.is_open());
    std::string src((std::istreambuf_iterator<char>(f)),
                    std::istreambuf_iterator<char>());
    const auto armAt = src.find("if (screen == kScreenResearch) {\n"
                                "            SDL_Rect black{0, 0, kDisplayW, kDisplayH};");
    CHECK(armAt != std::string::npos);
    if (armAt != std::string::npos) {
        const auto win = src.substr(armAt, 1800);
        CHECK(win.find("SDL_RenderCopy(ren, resChromeTex, nullptr, nullptr)") !=
              std::string::npos);
        CHECK(win.find("SDL_RenderCopy(ren, statusSpeckleTex, nullptr, &dst)") !=
              std::string::npos);
        CHECK(win.find("resRampColourAt(y, &c)") != std::string::npos);
        // The ramp loop spans 38..45 — NOT 38..46 (the y46 tail is
        // status-only, measured black here).
        CHECK(win.find("for (int y = 38; y <= 45; y++)") != std::string::npos);
        CHECK(win.find("y <= 46") == std::string::npos);
    }
    // (b) tan header box declines research.
    CHECK(src.find("if (hdr.x1 > hdr.x0 && screen != kScreenStatus &&\n"
                   "                screen != kScreenResearch) {") !=
          std::string::npos);
    // (c) gray interior rect declines research.
    CHECK(src.find("screen != kScreenSystemView && screen != kScreenStatus &&\n"
                   "                screen != kScreenResearch) {") !=
          std::string::npos);
    // (d) the invented panel border colour is gone (de-literalised comment
    //     law: this numeric triple must not appear ANYWHERE in ui.cpp).
    CHECK(src.find("90, 90, 110") == std::string::npos);
}
