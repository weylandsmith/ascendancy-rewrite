// SPDX-License-Identifier: GPL-3.0-or-later
// t400 pins: RAIL ICON PLACEMENT + SPECIES FLAGS + TITLE HOVER + FRAME
// TEXTURE. Laws + citations: ui/hudlayout.h, ui/boot.h, ui/mapchrome.h;
// measurement trail docs/re/_wip_t400.md (S1/S5 rail geometry, S3/S9 hover,
// S6/S11 flags, S12 texture). Pure-law pins (no SDL): the SDL wiring is
// witnessed by scripts/t400_rail_witness.sh (mechanical census).
#include <cstdio>

#include <set>
#include <string>

static const std::string kRepo = ASCENDANCY_SOURCE_DIR;

#include "harness.h"
#include "formats/gamepal.h"
#include "ui/boot.h"
#include "ui/hudlayout.h"
#include "ui/mapchrome.h"

using namespace ascend::ui;

TEST(rail_icon_placement_t400) {
    // dx verbatim 109 (SHAPEITEM lines); x = rect.x0 + 109 for EVERY icon
    // button, and the x is LEFT-anchored (independent of icon width).
    CHECK(kRailIconDx == 109);
    for (int i = 0; i < kRailButtonCount; i++) {
        const RailButton b = static_cast<RailButton>(i);
        const IconPos a = railIconPos(b, 24);
        const IconPos c = railIconPos(b, 30);
        CHECK(a.x == kRail[i].rect.x0 + kRailIconDx);
        CHECK(a.x == c.x);  // width-independent anchor
    }
    // Measured icon centres land within +-3 px of the button centres for
    // all four vendor rows (registration tops 130/175/213/248 + h/2 vs
    // button centres 145/184/223/262). Pin the law's own centring EXACTLY
    // (tolerance-only pins were MISSED by a top-align mutant at t400 M2):
    // y == centre - h/2 for every height, and y DIFFERS from rect.y0
    // whenever the face is shorter than the button.
    for (int h : {20, 24, 27, 30}) {
        const int cy = (kRail[0].rect.y0 + kRail[0].rect.y1) / 2;
        CHECK(railIconPos(RailButton::Status, h).y == cy - h / 2);
    }
    CHECK(railIconPos(RailButton::Status, 24).y != kRail[0].rect.y0);
    CHECK(railIconPos(RailButton::Status, 24).y > kRail[0].rect.y0);
    // The x lands RIGHT of the label zone: the vendor label ink ends well
    // before 583 (Species label content run ends x516, measured).
    CHECK(railIconPos(RailButton::Status, 27).x > 516);
    // Icons stay INSIDE their button rects (43-45 px wide faces, x0+109):
    for (int i = 0; i < kRailButtonCount; i++) {
        const RailButton b = static_cast<RailButton>(i);
        if (!sidebarIcon(b)) continue;
        const int x = railIconPos(b, 30).x;
        CHECK(x >= kRail[i].rect.x0 && x + 45 <= kRail[i].rect.x1 + 1);
    }
}

TEST(species_flag_slots_t400) {
    // MEASURED content runs x521..552 y288..314 (original): two native
    // 14x24 faces, lefts 521/540, inside the RACES rect 474,286-632,316.
    CHECK(kSpeciesFlagSlots[0].rect.x0 == 521);
    CHECK(kSpeciesFlagSlots[1].rect.x0 == 540);
    for (int i = 0; i < 2; i++) {
        const Rect& r = kSpeciesFlagSlots[i].rect;
        CHECK(r.x1 - r.x0 + 1 == 14);   // native raceflag width
        CHECK(r.y1 - r.y0 + 1 == 24);   // native raceflag height
        CHECK(inRect(kRail[4].rect, Pt{r.x0, r.y0}));
        CHECK(inRect(kRail[4].rect, Pt{r.x1, r.y1}));
    }
    // RACES itself has NO SHAPEITEM (the flags are NOT a windows.txt item):
    CHECK(!sidebarIcon(RailButton::Races));
}

TEST(title_hover_fill_t400) {
    // MEASURED on the pinned vendor shot: unhovered fill (0,0,8), hovered
    // fill (0,28,36), SAME ink both states (the ink constant stays in
    // title.cpp; here pin the FILL law + distinctness + never-clamp).
    CHECK(kTitleFill.r == 0 && kTitleFill.g == 0 && kTitleFill.b == 8);
    CHECK(kTitleFillHover.r == 0 && kTitleFillHover.g == 28 &&
          kTitleFillHover.b == 36);
    const RGB a = titleButtonFill(false), b = titleButtonFill(true);
    CHECK(a.r == 0 && a.g == 0 && a.b == 8);
    CHECK(b.r == 0 && b.g == 28 && b.b == 36);
    // Hover geometry: titleButtonAt is the SAME hit-map the fill uses —
    // a point on button 1 (PLAYTUTORIAL 159,240-477,270) resolves to 1,
    // a point between buttons (pitch 40, gap rows y231..239) to none.
    CHECK(titleButtonAt(Pt{318, 245}) == 1);
    CHECK(titleButtonAt(Pt{318, 235}) == -1);
    // Every button rect is hoverable geometry (no zero-rect):
    for (int i = 0; i < kTitleButtonCount; i++) {
        const Rect& r = kTitleButtons[i].rect;
        CHECK(inRect(r, Pt{(r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2}));
    }
}

TEST(frame_texture_law_t400) {
    // Bands [verified both vendor shots]: left margin + right column.
    // t426 EXTENDS the law to four sides (top rows 0..6, bottom rows
    // 473..479; docs/re/_wip_t426.md F1 — the pure refcap's chrome frames
    // the field on all four edges; the old 2-band set was the "map border
    // missing" defect). Vertical-band geometry unchanged.
    CHECK(kTextureBandCount == 4);
    CHECK(kTextureBands[0].x0 == 0 && kTextureBands[0].x1 == 6);
    CHECK(kTextureBands[1].x0 == 466 && kTextureBands[1].x1 == 639);
    CHECK(kTextureBands[2].y1 == 6 && kTextureBands[3].y0 == 473);
    // Determinism: same pixel -> same colour across calls (no rng_).
    for (int i = 0; i < 5; i++)
        {
            const RGB c1 = textureColourAt(3, 100 + i), c2 = textureColourAt(3, 100 + i);
            CHECK(c1.r == c2.r && c1.g == c2.g && c1.b == c2.b);
        }
    // Distinctness: the field is noise, not flat — 500 pixels in the
    // right column produce >= 6 distinct colours.
    std::set<uint32_t> seen;
    for (int y = 100; y < 350; y++)
        for (int x = 470; x < 475; x++)
            seen.insert((uint32_t(textureColourAt(x, y).r) << 16) |
                        (uint32_t(textureColourAt(x, y).g) << 8) |
                        textureColourAt(x, y).b);
    CHECK(seen.size() >= 6);
    // PALETTE LAW: every producible colour is a game.pal entry. Build the
    // full producible set (10 census colours + 4 tail colours) and check
    // membership against the REAL converted table when data is present.
    // The census values are themselves pinned against the vendor table.
    ascend::formats::GamePalette gp;
    std::string err;
    if (gp.load(kRepo + "/extracted/ascend01/data/game.pal", &err)) {
        for (int i = 0; i < 10; i++) {
            // kTextureColours[i] must be some table index's converted rgb.
            bool found = false;
            uint8_t out[3];
            for (int k = 0; k < 256 && !found; k++) {
                gp.rgb(k, out);
                found = out[0] == kTextureColours[i].r &&
                        out[1] == kTextureColours[i].g &&
                        out[2] == kTextureColours[i].b;
            }
            CHECK(found);
        }
    } else {
        std::printf("  (no vendor data: palette membership half skipped)\n");
    }
    // Weights sum to 74; the residue goes to the tail (documented).
    int sum = 0;
    for (int i = 0; i < 10; i++) sum += kTextureWeights[i];
    CHECK(sum == 74);
}
