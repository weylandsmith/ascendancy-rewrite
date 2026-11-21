// SPDX-License-Identifier: GPL-3.0-or-later

// t401 New Game art-law pins (D11: framing missing / bottom-row artwork
// wrong / species column art not rendered / Begin box empty / description
// transparent). Laws + every measurement citation: docs/re/t401-newgame-art.md
// S1-S10 (user-supplied originals scratchpad/newgame-original{,-very-dense-}
// .png are allowed evidence per D10; windows.txt L575-717 cited).
// Headless-safe: pure law + real shape-library file reads (supply-your-own
// data rules; REQUIRE_DATA guards the file-read pins).
#include "ui/menulaw.h"

#include <cstdio>
#include <filesystem>
#include <vector>

#include "formats/shp.h"
#include "harness.h"

namespace {
namespace au = ascend::ui;
namespace af = ascend::formats;
namespace fs = std::filesystem;

fs::path dataPath(const char* rel) {
    return fs::path(ASCENDANCY_SOURCE_DIR) / rel;
}

// game.pal -> RGB with the t398 DOSBox conversion c=(v<<2)|(v>>4) (the
// same table blitShape paints through; test-local reader, law cited).
bool loadPal(std::vector<int>* rgb) {  // 256*3 ints
    std::vector<uint8_t> raw;
    {
        std::FILE* f = std::fopen(dataPath("extracted/ascend01/data/game.pal")
                                      .string()
                                      .c_str(), "rb");
        if (!f) return false;
        raw.resize(768);
        const size_t n = std::fread(raw.data(), 1, 768, f);
        std::fclose(f);
        if (n != 768) return false;
    }
    rgb->resize(768);
    for (int i = 0; i < 256; i++)
        for (int c = 0; c < 3; c++) {
            const int v = raw[3 * i + c];
            (*rgb)[3 * i + c] = (v << 2) | (v >> 4);
        }
    return true;
}
}  // namespace

TEST(newgame_t401_wheel_frame_law) {
    // t414 BIJECTION (revised; docs/re/_wip_t414.md S2c): 13 records =
    // 5 density + 5 species + 3 atmosphere steps, classes partition
    // dot-wells k0..k4 / icon-rings k5..k9 / orbs k10..k12 (native-vision
    // montage census scripts/t414_3cfgnew_dump.py).
    // Density: rank in the sorted ladder {15,25,50,75,100} -> k0..k4.
    CHECK(au::newgameWheelFrame(0, 15) == 0);
    CHECK(au::newgameWheelFrame(0, 25) == 1);
    CHECK(au::newgameWheelFrame(0, 50) == 2);
    CHECK(au::newgameWheelFrame(0, 75) == 3);
    CHECK(au::newgameWheelFrame(0, 100) == 4);  // t414: was the k3 repeat
    CHECK(au::newgameWheelFrame(0, 60) == -1);   // off-ladder refuses
    CHECK(au::newgameWheelFrame(0, 0) == -1);
    // Species: k(2+n); the MEASURED anchor is Five -> k7 (original shows
    // four icons; the k7 montage frame carries four icons).
    CHECK(au::newgameWheelFrame(1, 5) == 7);
    CHECK(au::newgameWheelFrame(1, 3) == 5);
    CHECK(au::newgameWheelFrame(1, 7) == 9);
    CHECK(au::newgameWheelFrame(1, 2) == -1);
    CHECK(au::newgameWheelFrame(1, 8) == -1);
    // Atmosphere: k(10+v) — green k10 / blue k11 / red-spiked k12.
    CHECK(au::newgameWheelFrame(2, 0) == 10);
    CHECK(au::newgameWheelFrame(2, 1) == 11);
    CHECK(au::newgameWheelFrame(2, 2) == 12);
    CHECK(au::newgameWheelFrame(2, 3) == -1);
    // Unknown control refuses; nothing clamps.
    CHECK(au::newgameWheelFrame(3, 50) == -1);
    CHECK(au::newgameWheelFrame(-1, 50) == -1);
    // The law is a BIJECTION over the usable range: 5+5+3 distinct frames.
    bool seen[13] = {};
    const int vals0[5] = {15, 25, 50, 75, 100};
    for (int v : vals0) seen[au::newgameWheelFrame(0, v)] = true;
    for (int v = 3; v <= 7; v++) seen[au::newgameWheelFrame(1, v)] = true;
    for (int v = 0; v <= 2; v++) seen[au::newgameWheelFrame(2, v)] = true;
    for (bool s : seen) CHECK(s);  // no frame unused, none repeated
}

TEST(newgame_t401_geometry_constants) {
    // Constants measured on the user original (citations menulaw.h t401
    // block): they must agree with the windows.txt-owned rects they sit in.
    CHECK(au::kWheelBlitTop == 408);
    CHECK(au::kWheelBlitHalfW == 28);
    // The wheel blit lands INSIDE every bottom-row control panel.
    for (int i = 0; i < au::kNewgameControlCount; i++) {
        const au::Rect& c = au::kNewgameControls[i].rect;
        const int cx = (c.x0 + c.x1) / 2;
        CHECK(cx - au::kWheelBlitHalfW >= c.x0);
        CHECK(au::kWheelBlitTop >= c.y0);
        CHECK(au::kWheelBlitTop + 55 <= c.y1);  // content circle h ~55
    }
    // Desc panel art sits inside NEWGAMEWND (334,12)-(488,364).
    CHECK(au::kDescRingCentre.x - au::kDescRingR >= au::kNewgameWnd.x0);
    CHECK(au::kDescRingCentre.x + au::kDescRingR <= au::kNewgameWnd.x1);
    CHECK(au::kDescRingCentre.y - au::kDescRingR >= au::kNewgameWnd.y0);
    CHECK(au::kDescRingCentre.y + au::kDescRingR <= au::kNewgameWnd.y1);
    CHECK(au::kDescCrestRect.x1 - au::kDescCrestRect.x0 + 1 == 14);
    CHECK(au::kDescCrestRect.y1 - au::kDescCrestRect.y0 + 1 == 24);
    // Begin-box art inside the measured Begin rect.
    CHECK(au::kBeginEmblemRect.x1 <= au::kBeginNewGameBtn.x1);
    CHECK(au::kBeginEmblemRect.y1 <= au::kBeginNewGameBtn.y1);
    CHECK(au::kBeginDotsBand.x0 >= au::kBeginNewGameBtn.x0);
    CHECK(au::kBeginDotsBand.x1 < au::kBeginEmblemRect.x0);  // dots LEFT
    // tA1 BBOX-DIFF LAW: the class scale is 1 (vendor blits content
    // native); the 100-px smrace content disc sits inside the r53 ring
    // bounding box, and the ring centre x is inside the list interior.
    CHECK(au::kRacePortraitScale == 1);
    CHECK(100 / 2 <= au::kRaceRingR + 1);
    CHECK(au::kRacePortraitCx > au::kRaceList.x0 &&
          au::kRacePortraitCx < au::kRaceList.x1);
    // Texture bands fit the display; right band starts RIGHT of the field
    // (x494 measured; NOT the map screen's 466 — the two screens differ).
    CHECK(au::kNewgameTextureBands[0].x0 == 0);
    CHECK(au::kNewgameTextureBands[1].x0 > 465);
    for (const auto& b : au::kNewgameTextureBands)
        CHECK(b.y1 < au::kDisplayH);
}

TEST(newgame_t414_frame_and_chip_law) {
    // t414 frame law: the cosmos rect sits INSIDE the display with a
    // texture margin all round (measured 8/9/493/373 on the original).
    CHECK(au::kNewgameCosmosRect.x0 > 0);
    CHECK(au::kNewgameCosmosRect.y0 > 0);
    CHECK(au::kNewgameCosmosRect.x1 < au::kDisplayW - 100);  // racelist side
    CHECK(au::kNewgameCosmosRect.y1 < au::kDisplayH - 10);   // bottom row
    // Player chips [tNG-C law supersedes the t414 swatch read]: SEVEN
    // raceflag emblems 15x25 at x 381+16k, content rows 433..457, inside
    // the VISUAL panel (379..493 x 381..472). Refcap tight content bbox
    // (381,433)-(491,458); frame rows 434/458 (docs F13).
    CHECK(au::kPlayerChipCount == 7);
    CHECK(au::kPlayerChipX0 == 381);
    CHECK(au::kPlayerChipX0 >= au::kPlayerColorPanel.x0);
    CHECK(au::kPlayerChipW == 15);
    CHECK(au::kPlayerChipH == 25);
    CHECK(au::kPlayerChipX0 + (au::kPlayerChipCount - 1) *
                                      au::kPlayerChipPitch +
              au::kPlayerChipW - 1 ==
          491);  // refcap strip right edge
    CHECK(au::kPlayerChipY == 433);
    CHECK(au::kPlayerChipY + au::kPlayerChipH - 1 == 457);  // emblem bottom
    CHECK(au::kChipFrameTop == 434 && au::kChipFrameBottom == 458);
    CHECK(au::kChipFrameLeftGrey.r == 164 && au::kChipFrameLeftGrey.g == 171);
    CHECK(au::kChipFrameRightGrey.r == 225 && au::kChipFrameRightGrey.g == 227);
}

TEST(newgame_t401_portrait_lib_name) {
    CHECK(au::portraitLibName(0) == "smrace00.shp");
    CHECK(au::portraitLibName(7) == "smrace07.shp");
    CHECK(au::portraitLibName(20) == "smrace20.shp");
    CHECK(au::portraitLibName(21).empty());  // refuse, never clamp
    CHECK(au::portraitLibName(-1).empty());
}

TEST(newgame_t401_raceflag_crest_class) {
    // The description-panel crest is raceflag k<specnum> at NATIVE size.
    // Class law (t400 §2, re-verified here): raceflag.shp holds EXACTLY 21
    // records, every one EXACTLY 14x24 — unique in the corpus at that
    // size x count. If the library shape ever changes, the crest blit law
    // must be re-derived, so this pin guards it.
    REQUIRE_DATA();
    af::ShapeLibrary lib;
    std::string err;
    if (!lib.load(dataPath("extracted/ascend01/data/raceflag.shp").string(),
                  &err)) {
        CHECK(false);  // load failure is a real failure with data present
        return;
    }
    CHECK(lib.count() == 21);
    for (int i = 0; i < lib.count(); i++) {
        CHECK(lib.record(i).width == 15);  // tA1 bbox (L,T)=(0,0)
        CHECK(lib.record(i).height == 25);
    }
}

TEST(newgame_t401_wheel_frames_exist_real) {
    // Every frame the law can select MUST exist in the real library and
    // decode: the wheel law selects k0..k3, k5, k7, k9, k10, k11.
    REQUIRE_DATA();
    af::ShapeLibrary lib;
    std::string err;
    if (!lib.load(dataPath("extracted/ascend01/data/3cfgnew.shp").string(),
                  &err)) {
        CHECK(false);
        return;
    }
    const int selected[] = {0, 1, 2, 2, 3, 5, 7, 9, 10, 11};
    for (int f : selected) {
        CHECK(f < lib.count());
        std::vector<uint8_t> px;
        CHECK(lib.decode(f, px));
        CHECK(!px.empty());
    }
    // Monotonic dot census (the law's measured basis, docs/re/t401-newgame-art.md
    // S10): game.pal-converted bright pixels (r+g+b > 200) k0 < k1 < k2 <
    // k3 — dots increase with frame index. Indices alone would NOT prove
    // this (navy is index 242), hence the palette path.
    std::vector<int> pal;
    if (!loadPal(&pal)) {
        CHECK(false);
        return;
    }
    long bright[4] = {0, 0, 0, 0};
    for (int f = 0; f < 4; f++) {
        std::vector<uint8_t> px;
        if (!lib.decode(f, px)) {
            CHECK(false);
            return;
        }
        for (uint8_t v : px)
            if (pal[3 * v] + pal[3 * v + 1] + pal[3 * v + 2] > 200)
                bright[f]++;
    }
    CHECK(bright[0] < bright[1]);
    CHECK(bright[1] < bright[2]);
    CHECK(bright[2] < bright[3]);
}

TEST(newgame_t401_portrait_smrace_decodes) {
    // The portrait class the New Game screen now blits: smrace00/07/20 all
    // load with a 49x49 record 0 (the dims census class, t401 S6).
    REQUIRE_DATA();
    for (int specnum : {0, 7, 20}) {
        af::ShapeLibrary lib;
        std::string err;
        const std::string p =
            dataPath("extracted/ascend01/data").string() + "/" +
            au::portraitLibName(specnum);
        if (!lib.load(p, &err)) {
            CHECK(false);
            continue;
        }
        CHECK(lib.count() >= 1);
        CHECK(lib.record(0).width == 100);  // tA1 bbox (-50,-50,49,49)
        CHECK(lib.record(0).height == 100);
        std::vector<uint8_t> px;
        CHECK(lib.decode(0, px));
        CHECK(px.size() == size_t(100) * 100);
    }
}
