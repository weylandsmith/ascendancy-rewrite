// SPDX-License-Identifier: GPL-3.0-or-later

// tNG-C NEW GAME CONTENT LAW pins (cycle 2). Laws + every measurement:
// docs/re/_wip_tNGC.md F3/F7/F9/F9b/F10/F12/F13.
//   1. PLANET INDEX LAW (D19 seed #2 CLOSED): the DESC planet is
//      smhome.shp k<selected race row> NATIVE 52x52 (vendor 0x5231d name
//      fetch "DATA\\smhome.shp" -> 0x5236d blit 0x5caac, pushes (72,205)
//      NEWGAMEWND-rel; windows.txt L584 X0=334 Y0=12 -> anchor screen
//      (406,217); bbox (L,T)=(-24,-26) census -> content (382,191)).
//      Bounds 0x523b1: race row < 0x15 == 21 records.
//   2. CHIP RAMP LAW (D19 seed #4 CLOSED): chip i renders the selected
//      race's raceflag record with palette slots 16..19 :=
//      game.pal[16+4i..19+4i] (FUN_00053ee0 four-slot rewrite, loop 0..3;
//      ink census: ONLY {16,17,18,19} occur as ramp ink, navy 242 and
//      strays pass through). Witness: chip-i brightest ink == pal[4i+19]
//      EXACT i=1..6 on scratchpad/newgame-original.png. Geometry head
//      0x5258d: rect (381+16i,433)..(395+16i,463), SEVEN chips pitch 16;
//      frame rows 434/458 white hlines (refcap white-px census).
//   3. WHEEL FRAME BIJECTION (F9b, parent writes child obj+0x72):
//      density rank verbatim k0..k4; species COUNT+2 k5..k9 (domain
//      3..Seven, the cycle wraps 8->3 so 8/2 are OFF-domain); atmosphere
//      idx+10 k10..k12 (cycle wraps 3->0 so 3 is OFF-domain).
#include "ui/menulaw.h"
#include "ui/ui_internal.h"
#include "formats/shp.h"

#include <string>
#include <vector>

#include "harness.h"

namespace {
namespace au = ascend::ui;
namespace af = ascend::formats;
const std::string kRepo = ASCENDANCY_SOURCE_DIR;
const std::string kData = kRepo + "/extracted/ascend01/data/";
}  // namespace

TEST(tngc_smhome_index_law) {
    // Class law: smhome.shp holds EXACTLY 21 records (the 0x523b1 assert
    // value == race count), every one content 52x52 at bbox (-24,-26).
    // If the lib shape changes, the DESC planet law must be re-derived.
    REQUIRE_DATA();
    af::ShapeLibrary lib;
    std::string err;
    if (!lib.load(kData + "smhome.shp", &err)) {
        CHECK(false);  // load failure is a real failure with data present
        return;
    }
    CHECK(lib.count() == 21);
    for (int i = 0; i < lib.count(); i++) {
        const auto& r = lib.record(i);
        CHECK(r.width == 52);
        CHECK(r.height == 52);
        CHECK(r.left == -24);
        CHECK(r.top == -26);
    }
    // Anchor law: kDescPlanetCentre is the WINDOW push (72,205) in screen
    // coords (334+72, 12+205); dest = anchor + bbox = (382, 191).
    CHECK(au::kDescPlanetCentre.x == 334 + 72);
    CHECK(au::kDescPlanetCentre.y == 12 + 205);
    CHECK(au::kDescPlanetCentre.x - 24 == 382);
    CHECK(au::kDescPlanetCentre.y - 26 == 191);
}

TEST(tngc_chip_ramp_law) {
    // FUN_00053ee0 slot law: slots 16..19 -> 16+4i..19+4i; EVERYTHING else
    // (navy 242, strays 151/196, below-range 15, above-range 20) identity.
    for (int i = 0; i < au::kPlayerChipCount; i++) {
        CHECK(au::chipInkSlot(i, 16) == 16 + 4 * i);
        CHECK(au::chipInkSlot(i, 17) == 17 + 4 * i);
        CHECK(au::chipInkSlot(i, 18) == 18 + 4 * i);
        CHECK(au::chipInkSlot(i, 19) == 19 + 4 * i);  // brightest-ink witness
        CHECK(au::chipInkSlot(i, 242) == 242);        // navy untouched
        CHECK(au::chipInkSlot(i, 15) == 15);
        CHECK(au::chipInkSlot(i, 20) == 20);
    }
    CHECK(au::chipInkSlot(0, 19) == 19);  // family 0 = identity = blitShape
    // Geometry (head 0x5258d seed ebx=0x17d ecx=0x18b, y 0x1b1/0x1cf):
    CHECK(au::kPlayerChipX0 == 0x17d);
    CHECK(au::kPlayerChipPitch == 16);
    CHECK(au::kPlayerChipY == 0x1b1);
    CHECK(au::kPlayerChipCount == 7);
    // Selected-chip frame constants (refcap chip0 white-px census F13:
    // hlines y=434/y=458; the greys are the vline family).
    CHECK(au::kChipFrameTop == 434);
    CHECK(au::kChipFrameBottom == 458);
    CHECK(au::kChipFrameLeftGrey.r == 164 && au::kChipFrameLeftGrey.g == 171 &&
          au::kChipFrameLeftGrey.b == 177);
    CHECK(au::kChipFrameRightGrey.r == 225 &&
          au::kChipFrameRightGrey.g == 227 &&
          au::kChipFrameRightGrey.b == 229);
}

TEST(tngc_chip_ramp_data_witness) {
    // The library the vendor blits word[0x6fd84]-slot, selector = race row
    // (0x525f6/0x52603 verbatim): raceflag.shp, 21 records, 15x25, bbox
    // (L,T)=(0,0) — the blit dest is the rect corner verbatim. Ramp ink
    // census law: every decoded index is ramp {16..19}, navy 242, stray
    // {151,196} (k3), or a skip-0 — never a 4th distinct ramp value that
    // 0x53ee0's four-slot rewrite could not produce.
    REQUIRE_DATA();
    af::ShapeLibrary lib;
    std::string err;
    if (!lib.load(kData + "raceflag.shp", &err)) {
        CHECK(false);
        return;
    }
    CHECK(lib.count() == 21);
    for (int i = 0; i < lib.count(); i++) {
        CHECK(lib.record(i).width == 15);
        CHECK(lib.record(i).height == 25);
        CHECK(lib.record(i).left == 0);
        CHECK(lib.record(i).top == 0);
    }
    for (int k = 0; k < 7; k++) {
        std::vector<uint8_t> a;
        if (!lib.decode(k, a)) { CHECK(false); continue; }
        bool ok = true;
        for (uint8_t v : a)
            if (v != 0 && v != 16 && v != 17 && v != 18 && v != 19 &&
                v != 242 && v != 151 && v != 196)
                ok = false;
        CHECK(ok);
    }
}

TEST(tngc_wheel_frame_bijection_wrap_terms) {
    // F9b verbatim: density rank k0..k4; species COUNT+2 with the cycle
    // 3..7 (wrap 8->3 => 8 and 2 are OFF-domain, refuse); atmosphere
    // idx+10 with the cycle 0..2 (wrap 3->0 => 3 is OFF-domain).
    CHECK(au::newgameWheelFrame(1, 3) == 5);
    CHECK(au::newgameWheelFrame(1, 5) == 7);   // t401 anchor
    CHECK(au::newgameWheelFrame(1, 7) == 9);
    CHECK(au::newgameWheelFrame(1, 8) == -1);  // wrap 8->3: 8 never renders
    CHECK(au::newgameWheelFrame(1, 2) == -1);  // domain floor 3
    CHECK(au::newgameWheelFrame(2, 0) == 10);
    CHECK(au::newgameWheelFrame(2, 1) == 11);
    CHECK(au::newgameWheelFrame(2, 2) == 12);  // hostile = k12 (D19)
    CHECK(au::newgameWheelFrame(2, 3) == -1);  // wrap 3->0: 3 never renders
    CHECK(au::newgameWheelFrame(0, 15) == 0);   // sorted ladder
    CHECK(au::newgameWheelFrame(0, 50) == 2);   // {15,25,50,75,100}
    CHECK(au::newgameWheelFrame(0, 100) == 4);  // top rung
    CHECK(au::newgameWheelFrame(0, 11) == -1);  // off-ladder refuses
}
