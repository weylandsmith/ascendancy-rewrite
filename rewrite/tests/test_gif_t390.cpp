// SPDX-License-Identifier: GPL-3.0-or-later

// t390 GIF decoder + title palette tests. Pins are PIL-plane values on the
// REAL vendor asset (reference rasterizer law, docs/re/title-art.md §6.3);
// regenerate with scripts/t390_gifref.py (venv python). The code-width law
// (grow at next >= 2^width, NOT early change) is pinned implicitly: the
// early-change variant desyncs at output 11208 of this file
// (scripts/t390_lzwmirror.py). Decode is pure CPU — headless-safe by
// construction; only vendor-data availability gates these tests.
#include "formats/gif.h"
#include "ui/titlepalette.h"
#include "harness.h"

#include <cstdio>
#include <cstring>
#include <fstream>
#include <set>
#include <string>

namespace af = ascend::formats;
namespace au = ascend::ui;
static const std::string kRepo = ASCENDANCY_SOURCE_DIR;

#define ASSERT_OK(expr)                          \
    do {                                         \
        if (!(expr)) {                           \
            CHECK(expr);                         \
            std::printf("    (bail: %s)\\n", #expr); \
            return;                              \
        }                                        \
    } while (0)

namespace {
uint64_t fnv1a64(const uint8_t* p, size_t n) {
    uint64_t h = 0xcbf29ce484222325ull;
    for (size_t i = 0; i < n; i++) { h ^= p[i]; h *= 0x100000001b3ull; }
    return h;
}
std::string gifPath() {
    return kRepo + "/extracted/ascend01/data/0opening.gif";
}
}  // namespace

TEST(gif_t390_full_plane_pins) {
    REQUIRE_DATA();
    af::GifFrame f;
    std::string err;
    ASSERT_OK(af::gifDecodeFile(gifPath(), &f, &err));
    CHECK(f.width == 640);
    CHECK(f.height == 480);
    CHECK(f.gct.size() == 768);
    CHECK(f.indices.size() == 307200);
    // scripts/t390_gifref.py (PIL 12.3.0 plane)
    CHECK(fnv1a64(f.indices.data(), f.indices.size()) == 0x91b5827cb913431bull);
    CHECK(fnv1a64(f.indices.data(), 4096) == 0x59ee8fbcec3b6325ull);
    CHECK(fnv1a64(f.indices.data(), 6144) == 0xf50a4efce9972a87ull);
    CHECK(fnv1a64(f.indices.data(), 640) == 0x734bf6292c601525ull);
}

TEST(gif_t390_key_solid) {
    REQUIRE_DATA();
    af::GifFrame f;
    std::string err;
    ASSERT_OK(af::gifDecodeFile(gifPath(), &f, &err));
    // title-art.md §2: index 255 is EXACTLY the union of the seven button
    // rects — count 69,223, bbox (159,200)-(477,470) inclusive.
    size_t key = 0;
    int x0 = 999999, y0 = 999999, x1 = -1, y1 = -1;
    for (uint32_t y = 0; y < f.height; y++)
        for (uint32_t x = 0; x < f.width; x++)
            if (f.indices[size_t(y) * f.width + x] == 255) {
                key++;
                if (int(x) < x0) x0 = int(x);
                if (int(x) > x1) x1 = int(x);
                if (int(y) < y0) y0 = int(y);
                if (int(y) > y1) y1 = int(y);
            }
    CHECK(key == 69223);
    CHECK(x0 == 159); CHECK(y0 == 200); CHECK(x1 == 477); CHECK(y1 == 470);
    std::set<uint8_t> d(f.indices.begin(), f.indices.end());
    CHECK(d.size() == 53);  // t386 §3 census
}

TEST(gif_t390_refusals) {
    // Synthesised shapes OUTSIDE the file's own shape must refuse, not
    // clamp. Build minimal GIFs in memory.
    auto base = [](std::vector<uint8_t>& g, bool interlace) {
        const char* sig = "GIF87a";
        g.insert(g.end(), sig, sig + 6);
        g.insert(g.end(), {0x80, 0x00, 0x60, 0x00});  // 128x96 screen
        g.push_back(0x80);                            // GCT flag, size 0 -> 2 entries
        g.push_back(0x00);                            // background colour index
        g.push_back(0x00);                            // pixel aspect ratio
        for (int i = 0; i < 6; i++) g.push_back(uint8_t(i));
        g.insert(g.end(), {0x2c, 0, 0, 0, 0, 0x80, 0x00, 0x60, 0x00,
                           uint8_t(interlace ? 0x40 : 0x00)});
    };
    std::string err;
    af::GifFrame f;
    {  // interlaced image descriptor -> refuse
        std::vector<uint8_t> g;
        base(g, true);
        CHECK(!af::gifDecodeFrame(g.data(), g.size(), &f, &err));
        CHECK(err.find("interlaced") != std::string::npos);
    }
    {  // truncated plane (no LZW data, then trailer) -> refuse
        std::vector<uint8_t> g;
        base(g, false);
        g.push_back(0x08);  // mcs
        g.push_back(0x00);  // empty sub-block chain
        g.push_back(0x3b);
        CHECK(!af::gifDecodeFrame(g.data(), g.size(), &f, &err));
    }
    {  // wrong signature -> refuse
        std::vector<uint8_t> g;
        base(g, false);
        g[4] = '9';
        CHECK(!af::gifDecodeFrame(g.data(), g.size(), &f, &err));
        CHECK(err.find("GIF87a") != std::string::npos);
    }
    {  // second image descriptor after the stream -> refuse
        std::vector<uint8_t> g;
        base(g, false);
        g.push_back(0x08);
        g.push_back(0x00);
        g.push_back(0x2c);  // another image start
        CHECK(!af::gifDecodeFrame(g.data(), g.size(), &f, &err));
        CHECK(err.find("more than one image") != std::string::npos);
    }
}

TEST(titlepalette_t390_roundtrip) {
    REQUIRE_DATA();
    af::GifFrame f;
    std::string err;
    ASSERT_OK(af::gifDecodeFile(gifPath(), &f, &err));
    au::TitlePalette pal;
    ASSERT_OK(pal.load("", f.gct.data(), f.gct.size(), &err));
    // 52 measured entries (rewrite/tests/data/title_palette_t386.tsv).
    int nMapped = 0;
    for (int i = 0; i < 256; i++) nMapped += pal.mapped[i] ? 1 : 0;
    CHECK(nMapped == 52);
    // t386 §4 example pair: idx128 [254,177,96] -> [215,138,56].
    CHECK(pal.rgb[128][0] == 215);
    CHECK(pal.rgb[128][1] == 138);
    CHECK(pal.rgb[128][2] == 56);
    // Unmapped index: GCT fallback, flagged NOT measured. Index 100 is not
    // in the TSV (census: TSV covers 0..9, 34..84 subset, 128..143, 157,
    // 164, 183).
    CHECK(!pal.mapped[100]);
    CHECK(pal.rgb[100][0] == f.gct[300] && pal.rgb[100][1] == f.gct[301] &&
          pal.rgb[100][2] == f.gct[302]);
    // Mapped values are NOT the GCT (the swap is real, t386 §4).
    CHECK(pal.rgb[128][0] != f.gct[384]);
}
