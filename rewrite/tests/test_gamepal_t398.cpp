// SPDX-License-Identifier: GPL-3.0-or-later

// t398 palette-fidelity pins: DATA\game.pal IS the in-game palette law
// (docs/re/_wip_t398.md S1..S5; law text formats/gamepal.h). Evidence class:
// the file itself (768 B, 6-bit channels) + measured refcap membership
// (307200/307200 px in three pinned in-game shots) + the registration of
// 1starmap rail records through the converted table.
#include "formats/gamepal.h"
#include "harness.h"

#include <cstdio>
#include <fstream>
#include <string>

namespace af = ascend::formats;
static const std::string kRepo = ASCENDANCY_SOURCE_DIR;

namespace {
std::string palPath() { return kRepo + "/extracted/ascend01/data/game.pal"; }
std::vector<uint8_t> readFile(const std::string& p) {
    std::ifstream in(p, std::ios::binary | std::ios::ate);
    if (!in) return {};
    std::vector<uint8_t> b(size_t(in.tellg()));
    in.seekg(0);
    in.read(reinterpret_cast<char*>(b.data()), b.size());
    return b;
}
}  // namespace

TEST(gamepal_t398_shape_and_conversion) {
    REQUIRE_DATA();
    const auto raw = readFile(palPath());
    CHECK(raw.size() == 768);
    // 6-bit DAC law [verified]: no channel byte exceeds 0x3f.
    bool all6 = true;
    for (uint8_t v : raw) all6 = all6 && v <= 0x3f;
    CHECK(all6);

    af::GamePalette pal;
    std::string err;
    CHECK(pal.parse(raw, &err));
    CHECK(pal.ready());

    // The DOSBox conversion is (v<<2)|(v>>4), NOT v*4: they differ whenever
    // v >= 16 (v*4 saturates differently at the top and loses the low bits).
    // Pinned triples (measured against the pinned refcap shots):
    uint8_t c[3];
    pal.rgb(242, c);  // rail teal  raw (3,8,12)   -> shot (12,32,48)
    CHECK(c[0] == 12 && c[1] == 32 && c[2] == 48);
    pal.rgb(55, c);   // chrome teal raw (19,28,29) -> shot (77,113,117)
    CHECK(c[0] == 77 && c[1] == 113 && c[2] == 117);
    pal.rgb(80, c);   // raw (22,6,14)              -> shot (89,24,56)
    CHECK(c[0] == 89 && c[1] == 24 && c[2] == 56);
    pal.rgb(0, c);
    CHECK(c[0] == 0 && c[1] == 0 && c[2] == 0);
    // Top-of-DAC saturates to full white — SYNTHETIC table (all bytes 63),
    // because index 63 of the REAL file is not an all-63 triple.
    {
        af::GamePalette white;
        CHECK(white.parse(std::vector<uint8_t>(768, 63), &err));
        white.rgb(63, c);
        CHECK(c[0] == 255 && c[1] == 255 && c[2] == 255);
        // (v<<2)|(v>>4) vs v*4 differ at v=16: 64|1=65 vs 64 — pin one.
        af::GamePalette v16;
        CHECK(v16.parse(std::vector<uint8_t>(768, 16), &err));
        v16.rgb(7, c);
        CHECK(c[0] == 65 && c[1] == 65 && c[2] == 65);
    }

    // Whole-table identity: FNV over all 768 converted bytes (probe run
    // banked docs/re/_wip_t398.md) — pins every entry, not just the four.
    uint64_t h = 0xcbf29ce484222325ull;
    for (int i = 0; i < 256; i++) {
        pal.rgb(i, c);
        for (int k = 0; k < 3; k++) { h ^= c[k]; h *= 0x100000001b3ull; }
    }
    CHECK(h == 0xe366ecb79ed61fc2ull);
}

TEST(gamepal_t398_argb_layout) {
    REQUIRE_DATA();
    af::GamePalette pal;
    std::string err;
    CHECK(pal.parse(readFile(palPath()), &err));
    // ARGB8888: alpha forced 255, channels as converted.
    const uint32_t a = pal.argb(242);
    CHECK(a == 0xFF0C2030u);  // (12,32,48) = 0x0C 0x20 0x30
    CHECK((pal.argb(0) & 0x00FFFFFFu) == 0x000000u);
    CHECK(pal.argb(256 + 242) == pal.argb(242));  // index wraps, never clamps
}

TEST(gamepal_t398_refuses_wrong_size) {
    // refuse-not-clamp: any size other than exactly 768 B is rejected and the
    // palette stays NOT ready (blitShape then keeps the documented ramp).
    af::GamePalette pal;
    std::string err;
    CHECK(!pal.parse(std::vector<uint8_t>(767, 7), &err));
    CHECK(!pal.ready());
    CHECK(!pal.parse(std::vector<uint8_t>(768 + 1, 7), &err));
    CHECK(!pal.ready());
    CHECK(!pal.parse(std::vector<uint8_t>(), &err));
    CHECK(!pal.ready());
    // A 768 B file loads even if a byte exceeds 63 (the vendor file doesn't,
    // but the LOADER's law is size-only; the <=63 fact is a property of the
    // data pinned above, not a load gate).
    CHECK(pal.parse(std::vector<uint8_t>(768, 200), &err));
    CHECK(pal.ready());
}

TEST(gamepal_t398_title_screen_is_NOT_gamepal) {
    REQUIRE_DATA();
    // The refutation half of the law (title-art.md §4 re-confirmed on the
    // palette axis): the title screen's dominant colours are NOT in game.pal,
    // so the title MUST keep the t386 TSV path. Dominant title colours
    // measured off docs/assets/refcap/original-title-menu.png:
    // (215,138,56) (0,0,8) (85,44,4) — none inside the converted table.
    af::GamePalette pal;
    std::string err;
    CHECK(pal.parse(readFile(palPath()), &err));
    const int kTitle[3][3] = {{215, 138, 56}, {0, 0, 8}, {85, 44, 4}};
    uint8_t c[3];
    for (int i = 0; i < 3; i++) {
        bool found = false;
        for (int idx = 0; idx < 256 && !found; idx++) {
            pal.rgb(idx, c);
            found = c[0] == kTitle[i][0] && c[1] == kTitle[i][1] &&
                    c[2] == kTitle[i][2];
        }
        CHECK(!found);
    }
}
