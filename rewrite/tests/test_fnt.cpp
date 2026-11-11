// SPDX-License-Identifier: GPL-3.0-or-later

// Vendor .fnt font tests — invariants from docs/re/fnt.md (OQ-017 CLOSED),
// checked against the REAL files in extracted/ (read-only, gate-safe). The
// same law is asserted by scripts/fnt_probe.py (gate 3p); this file pins
// the C++ port to the identical facts.
#include "formats/fnt.h"
#include "harness.h"

#include <cstdio>
#include <string>
#include <vector>

namespace af = ascend::formats;
static const std::string kRepo = ASCENDANCY_SOURCE_DIR;
static const std::string kA01 = kRepo + "/extracted/ascend01/data/";

TEST(fnt_load_all_vendor_fonts) {
    REQUIRE_DATA();
    af::Font sm, big, intro;
    std::string err;
    CHECK(sm.load(kA01 + "smfont.fnt", &err));
    CHECK(big.load(kA01 + "bigfont.fnt", &err));
    CHECK(intro.load(kRepo + "/extracted/ascend02/data/intro.fnt", &err));
    CHECK(sm.height() == 8);
    CHECK(big.height() == 11);
    CHECK(intro.height() == 39);
    (void)err;
}

TEST(fnt_glyph_widths_measured) {
    REQUIRE_DATA();
    // Widths from fnt.md (space=4/5/16, A=6/8/22 sm/big/intro).
    af::Font sm, big, intro;
    std::string err;
    CHECK(sm.load(kA01 + "smfont.fnt", &err));
    CHECK(big.load(kA01 + "bigfont.fnt", &err));
    CHECK(intro.load(kRepo + "/extracted/ascend02/data/intro.fnt", &err));
    CHECK(sm.glyph(' ').width == 4);
    CHECK(sm.glyph('A').width == 6);
    CHECK(sm.glyph('I').width == 4);
    CHECK(big.glyph(' ').width == 5);
    CHECK(big.glyph('A').width == 8);
    CHECK(intro.glyph(' ').width == 16);
    CHECK(intro.glyph('A').width == 22);
}

TEST(fnt_ink_census_pinned) {
    REQUIRE_DATA();
    // Measured 2026-10-04 over all 128 glyphs: the unimplemented block
    // (0..31 and @^{|}~ in sm/big) carries no ink.
    af::Font sm, big, intro;
    std::string err;
    CHECK(sm.load(kA01 + "smfont.fnt", &err));
    CHECK(big.load(kA01 + "bigfont.fnt", &err));
    CHECK(intro.load(kRepo + "/extracted/ascend02/data/intro.fnt", &err));
    CHECK(sm.inkCensus() == 1075ull);
    CHECK(big.inkCensus() == 1514ull);
    CHECK(intro.inkCensus() == 11877ull);
}

TEST(fnt_letterform_shape_solid) {
    REQUIRE_DATA();
    // smfont 'I' (w=4, h=8) is .### / ..#. / ..#. / ..#. / ..#. / ..#. /
    // .### / .... in the vision-confirmed sheet — assert the exact bitmap,
    // and that 0xF3 is the ONLY ink byte smfont ever uses (fnt.md alphabet).
    af::Font sm;
    std::string err;
    CHECK(sm.load(kA01 + "smfont.fnt", &err));
    const auto& g = sm.glyph('I');
    CHECK(g.width == 4);
    auto rowInk = [&](int y) {
        std::string s;
        for (uint32_t x = 0; x < g.width; x++)
            s += g.px[y * g.width + x] == 0xF3 ? '#' : '.';
        return s;
    };
    CHECK(rowInk(0) == ".###");
    CHECK(rowInk(1) == "..#.");
    CHECK(rowInk(5) == "..#.");
    CHECK(rowInk(6) == ".###");
    CHECK(rowInk(7) == "....");
    // 0xF3 is the ONLY ink byte in smfont (fnt.md ink alphabet).
    bool onlyF3 = true;
    for (int c = 32; c < 127; c++)
        for (uint32_t i = 0; i < sm.glyph(c).width * 8; i++)
            if (sm.glyph(c).px[i] != 0xF3 && sm.glyph(c).px[i] != 0xFF) onlyF3 = false;
    CHECK(onlyF3);
}

TEST(fnt_render_argb) {
    REQUIRE_DATA();
    af::Font sm;
    std::string err;
    CHECK(sm.load(kA01 + "smfont.fnt", &err));
    std::vector<uint32_t> px(4 * 8);
    sm.renderGlyphArgb('I', px.data());
    CHECK(px[0] == 0xFF121218u);           // background pixel (0,0)
    CHECK(px[0 * 4 + 1] == 0xFF828282u);   // 0xF3 ink -> 40+3*30 = 130 = 0x82
    CHECK(px[7 * 4 + 0] == 0xFF121218u);   // baseline row empty
}

TEST(fnt_rejects_garbage) {
    REQUIRE_DATA();
    // (a) header N != 128 must reject; (b) a hand-built WELL-FORMED font
    // (128 zero-width glyphs, offsets spaced 4, so every slot is exactly
    // 4+0*h and the last ends at EOF) must LOAD; (c) appending one junk byte
    // breaks the EOF-tiling law and must reject again.
    std::vector<uint8_t> d(16 + 4 * 128, 0);
    d[0] = '1'; d[1] = '.';
    auto put = [&](int i, uint32_t v) {
        d[16 + 4 * i] = v & 0xFF; d[16 + 4 * i + 1] = v >> 8 & 0xFF;
        d[16 + 4 * i + 2] = v >> 16 & 0xFF; d[16 + 4 * i + 3] = v >> 24;
    };
    const auto write = [&](const std::vector<uint8_t>& v) {
        FILE* w = fopen("/tmp/ascendancy_fnt_garbage.fnt", "wb");
        fwrite(v.data(), 1, v.size(), w);
        fclose(w);
    };
    const char* tmp = "/tmp/ascendancy_fnt_garbage.fnt";
    af::Font f;
    std::string err;

    write(d);                       // N==0 (header u32s still zero)
    CHECK(!f.load(tmp, &err));

    d[4] = 128;                     // N=128, height=8? height is d[8..11]:
    d[8] = 8;                       // h=8, v255 stays 0 -> must reject header
    write(d);
    CHECK(!f.load(tmp, &err));

    d[12] = 255;                    // v255 ok; build the zero-width glyph run
    uint32_t o = 16 + 4 * 128;
    for (int i = 0; i < 128; i++) put(i, o), o += 4;  // w=0 => slot == 4
    d.resize(o);                    // glyph bodies are 0 bytes; ends at EOF
    write(d);
    CHECK(f.load(tmp, &err));       // well-formed (empty) font loads
    CHECK(f.height() == 8);

    d.push_back(0x42);              // trailing junk -> EOF tiling broken
    write(d);
    CHECK(!f.load(tmp, &err));
}
