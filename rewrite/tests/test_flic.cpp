// SPDX-License-Identifier: GPL-3.0-or-later

// FLC codec tests — C++ decoder vs the Python reference golden hashes
// (docs/re/flc.md §3). The TSV ships in-tree; game/ is the same corpus the
// gate checksums. Hash: FNV-1a-64 over frame pixels then 256 RGB triples —
// byte order fixed by scripts/flc_probe.py Frame.fnv1a64.
#include "formats/flic.h"
#include "harness.h"

#include <cstdio>
#include <cstring>
#include <fstream>
#include <map>
#include <sstream>
#include <string>

namespace af = ascend::formats;
static const std::string kRepo = ASCENDANCY_SOURCE_DIR;

// Harness has CHECK only; express "must be true or bail" explicitly.
#define ASSERT_OK(expr)                          \
    do {                                         \
        if (!(expr)) {                           \
            CHECK(expr);                         \
            std::printf("    (bail: %s)\n", #expr); \
            return;                              \
        }                                        \
    } while (0)

namespace {

uint64_t fnv1a64(const uint8_t* px, size_t n, const uint8_t* pal) {
    uint64_t h = 0xcbf29ce484222325ULL;
    auto mix = [&h](uint8_t b) {
        h ^= b;
        h *= 0x100000001b3ULL;
    };
    for (size_t i = 0; i < n; ++i) mix(px[i]);
    for (size_t i = 0; i < 768; ++i) mix(pal[i]);
    return h;
}

std::map<int, uint64_t> loadGolden(const std::string& file) {
    std::map<int, uint64_t> g;
    std::ifstream in(kRepo + "/rewrite/tests/data/flc_golden.tsv");
    std::string line;
    std::getline(in, line);  // header
    while (std::getline(in, line)) {
        std::istringstream ss(line);
        std::string f, idx, sha, h;
        if (!std::getline(ss, f, '\t')) continue;
        std::getline(ss, idx, '\t');
        std::getline(ss, sha, '\t');
        std::getline(ss, h, '\t');
        if (f == file) g[std::stoi(idx)] = std::stoull(h, nullptr, 16);
    }
    return g;
}

// Decodes every frame, compares each frame-state hash against the golden
// map, and names the FIRST mismatching frame index on regression.
void checkAgainstGolden(const std::string& path, const std::string& base) {
    af::Flic f;
    std::string err;
    ASSERT_OK(f.load(path, &err));
    const auto golden = loadGolden(base);
    CHECK(golden.size() == f.frames().size());
    int bad = -1, checked = 0;
    const size_t npix = static_cast<size_t>(f.width()) * f.height();
    const bool ok = f.replay(
        [&](int i, const uint8_t* px, const uint8_t* pal) {
            ++checked;
            auto it = golden.find(i);
            if (it == golden.end()) return;
            if (fnv1a64(px, npix, pal) != it->second && bad < 0) bad = i;
        },
        &err);
    if (!ok) std::printf("    replay error: %s\n", err.c_str());
    if (bad >= 0) std::printf("    first mismatching frame: %d\n", bad);
    CHECK(ok);
    CHECK(bad == -1);
    CHECK(checked == static_cast<int>(golden.size()));
}

}  // namespace

TEST(flc_logic_golden) {
    REQUIRE_DATA();
    checkAgainstGolden(kRepo + "/game/logic.flc", "logic.flc");
}

TEST(flc_intro_golden) {
    REQUIRE_DATA();
    checkAgainstGolden(kRepo + "/extracted/ascend02/data/intro65a.flc",
                       "intro65a.flc");
}

TEST(flc_header_facts) {
    REQUIRE_DATA();
    // Both vendor files: 640x480x8, speed 71 ms; the header's frame count
    // excludes the ring frame (docs/re/flc.md §1 measurements).
    af::Flic f;
    std::string err;
    ASSERT_OK(f.load(kRepo + "/game/logic.flc", &err));
    CHECK(f.width() == 640);
    CHECK(f.height() == 480);
    CHECK(f.speedMs() == 71);
    CHECK(f.frames().size() == 226);
    CHECK(f.declaredFrames() == 225);
    af::Flic g;
    ASSERT_OK(g.load(kRepo + "/extracted/ascend02/data/intro65a.flc", &err));
    CHECK(g.frames().size() == 1144);
    CHECK(g.declaredFrames() == 1143);
}

TEST(flc_ring_copy_decodes) {
    REQUIRE_DATA();
    // The ring frame of logic.flc is the vendor's wrong-sized FLI_COPY
    // (declared 307204, true 6+640*480; compuphase "Frequent errors",
    // docs/re/flc.md §1). With the repair in force, replay() must SUCCEED
    // and the LAST frame must carry the copy image; flc_logic_golden pins
    // its content hash, so a broken repair shows up as a frame-225 mismatch.
    af::Flic f;
    std::string err;
    ASSERT_OK(f.load(kRepo + "/game/logic.flc", &err));
    int last_nonblack = -1;
    const size_t npix = 640 * 480;
    const bool ok = f.replay(
        [&](int i, const uint8_t* px, const uint8_t*) {
            for (size_t k = 0; k < npix; ++k)
                if (px[k]) { last_nonblack = i; break; }
        },
        &err);
    CHECK(ok);
    CHECK(err.empty());
    CHECK(last_nonblack == static_cast<int>(f.frames().size()) - 1);
}
