// SPDX-License-Identifier: GPL-3.0-or-later

// tPF5-A INDICATOR-POPUP MINERAL FRAME (D28 item 9 last leg, 2026-11-27).
// Law docs/re/_wip_tPF5A.md P1-P5: the msg-50 builder (FUN_0x3db80 prologue,
// 0x3dbb3 mov eax,0x9f10c / mov dx,[0x6fd8e] / call 0x1fc34 / push record /
// push widget+4 / call 0x5caac) blits lib ds:0x6fd8e == id 37 ==
// 'data\help.shp' (live-RAM 60/60 saves, scripts/tPF5A_indlib.py), frame
// record 0 (composer 0x341b5 writes [rec+0x18]=id, [rec+0x1e]=0), 1:1 AT THE
// WIDGET ORIGIN, before the key switch — one frame for all four tiles. The
// content rect is inset 10 from that origin (0x3dbe8/0x3dbf9), and on the
// tile popup the two laws meet exactly: PLSQUARE 152,120..487,375 == k0's
// measured extents (tPF-2d D8) with content 162..477 (right inset 10).
#include "harness.h"

#include <fstream>
#include <sstream>
#include <string>

#include "formats/shp.h"
#include "ui/indpopups.h"

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
// Drop // comments (tESC-1 M1 law: a commented statement must not
// false-satisfy a substring scan).
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

TEST(indicatorPopupFrameRect_isContentMinusTen_tPF5A) {
    // Indicator leg: PLRES X0=7 Y0=7 (windows.txt:1539-1540) -> content
    // 17,17..332,214 -> frame 7,7..342,262 (origin + 335/255).
    const ascend::ui::Rect content = ascend::ui::indicatorPopupRect(
        ascend::ui::Rect{7, 7, 114, 106});
    const ascend::ui::Rect fr = ascend::ui::indicatorPopupFrameRect(content);
    CHECK(fr.x0 == 7 && fr.y0 == 7);
    CHECK(fr.x1 == 7 + ascend::ui::kIndPopupFrameW - 1);
    CHECK(fr.y1 == 7 + ascend::ui::kIndPopupFrameH - 1);
    // Tile leg (the D8 three-way agreement): PLSQUARE origin 152,120 gives
    // frame 152..487 x 120..375 == PLSQUARE's own rect verbatim.
    const ascend::ui::Rect tContent = ascend::ui::indicatorPopupRect(
        ascend::ui::Rect{152, 120, 487, 375});
    const ascend::ui::Rect tFr = ascend::ui::indicatorPopupFrameRect(tContent);
    CHECK(tFr.x0 == 152 && tFr.y0 == 120 && tFr.x1 == 487 && tFr.y1 == 375);
    // The frame is BIGGER than the content box on every edge (a frame
    // blitted INTO the content rect is the refuted reading, P2/P4).
    CHECK(fr.x1 - fr.x0 > tContent.x1 - tContent.x0);
}

TEST(helpShpK0_dimsAre336x256_tPF5A) {
    // The frame extents are a MEASURED property of the shipped file under
    // the port loader (tPF-10 law: pin pixels via ShapeLibrary::decode,
    // never raw .idx words). k1 is the 171x76 help-text box — a second
    // record exists, so a mutation that swaps the record index changes the
    // painted art; count()==2 pins which record the port may use.
    ascend::formats::ShapeLibrary lib;
    std::string err;
    CHECK(lib.load(kRepo + "/extracted/ascend01/data/help.shp", &err));
    if (lib.count() < 1) return;
    CHECK(lib.count() == 2);
    const auto& r0 = lib.record(0);
    CHECK(int(r0.width) == ascend::ui::kIndPopupFrameW);
    CHECK(int(r0.height) == ascend::ui::kIndPopupFrameH);
}

TEST(ui_blitsHelpFrame_behindEveryPlanetPopup_tPF5A) {
    const std::string ui = stripComments(slurp("rewrite/src/ui/ui.cpp"));
    // The lib loads from the cited file, and the frame blit is wired with
    // record 0 at the frame rect derived from planetPopupRect.
    CHECK(ui.find("extracted/ascend01/data/help.shp") != std::string::npos);
    const size_t blit = ui.find("blitShape(ren, indPopupFrameLib, 0,");
    CHECK(blit != std::string::npos);
    if (blit == std::string::npos) return;
    CHECK(ui.rfind("indicatorPopupFrameRect(", blit) != std::string::npos);
    // The blit sits INSIDE the popup draw block: it must come after the
    // block's empty-guard and before the button-band band-fill.
    const size_t guard = ui.rfind("if (!planetPopup.empty())", blit);
    const size_t band = ui.find("12, 32, 48, 255", blit);
    CHECK(guard != std::string::npos && band != std::string::npos);
    if (guard != std::string::npos && band != std::string::npos)
        CHECK(guard < blit && blit < band);
    // The dim fill survives ONLY as the load-failure fallback: within the
    // popup draw block (guard .. button band) it appears exactly once.
    // (The project-list list-backing shares the colour at ui.cpp ~2982 —
    // file-wide counting false-fails, found the hard way.)
    const std::string block = ui.substr(guard, band - guard);
    size_t n = 0, pos = 0;
    while ((pos = block.find("8, 12, 20, 235", pos)) != std::string::npos) {
        ++n;
        pos += 3;
    }
    CHECK(n == 1);
}

TEST(ui_frameBlitIsRecordZero_sharedByBothPopups_tPF5A) {
    // Both popups share ONE planetPopup vector and ONE draw block (the
    // msg-50 builder blits before the key switch — key-independent). The
    // frame blit must not be gated on planetSquarePopup.
    const std::string ui = stripComments(slurp("rewrite/src/ui/ui.cpp"));
    const size_t blit = ui.find("blitShape(ren, indPopupFrameLib, 0,");
    CHECK(blit != std::string::npos);
    if (blit == std::string::npos) return;
    const std::string before = ui.substr(0, blit);
    const size_t blockStart = before.rfind("if (!planetPopup.empty())");
    CHECK(blockStart != std::string::npos);
    // No planetSquarePopup condition between the block guard and the blit
    // (the band buttons below MAY gate on it; the frame may not).
    CHECK(ui.substr(blockStart, blit - blockStart).find("planetSquarePopup") ==
          std::string::npos);
}
