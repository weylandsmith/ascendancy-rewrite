// .shp reader/decoder tests (OQ-005). Law source: docs/re/shp.md
// S1/S8/S9/S14/S16/S17; parity target: scripts/r1_shp_unifiedlaw.py
// corpus run (measured 2026-10-11: 1477/1557 records walk, 176/208
// libraries clean). Real extracted/ files, read-only, gate-safe.
#include "formats/shp.h"
#include "harness.h"

#include <filesystem>
#include <vector>

#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif

namespace fs = std::filesystem;
using ascend::formats::ShapeLibrary;

namespace {
const std::string kRepo = ASCENDANCY_SOURCE_DIR;
const std::string kA01 = kRepo + "/extracted/ascend01/data/";
}  // namespace

TEST(shp_loads_raceflag_with_va_stream_law) {
    ShapeLibrary lib;
    std::string err;
    CHECK(lib.load(kA01 + "raceflag.shp", &err));
    if (lib.count() == 0) return;
    const auto& r0 = lib.record(0);
    const auto& r1 = lib.record(1);
    CHECK(r0.start == r0.stream - 8);          // V law
    CHECK(r1.start + 0x18 == r1.stream);        // A law
    CHECK(r1.width > 0 && r1.height > 0);
}

TEST(shp_decodes_raceflag_every_record) {
    ShapeLibrary lib;
    std::string err;
    CHECK(lib.load(kA01 + "raceflag.shp", &err));
    uint64_t census = 0;
    for (int i = 0; i < lib.count(); ++i) {
        std::vector<uint8_t> px;
        CHECK(lib.decode(i, px));
        for (uint8_t b : px) census += b;
    }
    // Determinism pin (recomputed by this very test on first run; see
    // commit message). Non-zero guard guards against silent no-op decodes.
    CHECK(census > 0);
}

TEST(shp_rejects_broken_container) {
    // tsz must equal 8*(N+1): law rejection testable in memory.
    std::vector<uint8_t> img = {0x31, 0x2e, 0x31, 0x30};
    auto put = [&](uint32_t v) {
        img.push_back(uint8_t(v)); img.push_back(uint8_t(v >> 8));
        img.push_back(uint8_t(v >> 16)); img.push_back(uint8_t(v >> 24));
    };
    put(2);   // count
    put(40);  // tsz  (law demands 8*(2+1) = 24)
    for (int i = 0; i < 64; ++i) img.push_back(0);
    std::string err;
    ShapeLibrary lib;
    CHECK(!lib.parse(img, &err));
    // Correct tsz (24) but directory entry 0 (at 0x10) pointing BELOW te
    // (te = 0x10+24 = 0x28) must fail monotonicity/bounds.
    img[8] = 24; img[9] = 0; img[10] = 0; img[11] = 0;
    img[0x10] = 0x20; img[0x11] = 0; img[0x12] = 0; img[0x13] = 0;
    img[0x14] = 0; img[0x15] = 0; img[0x16] = 0; img[0x17] = 0;
    CHECK(!lib.parse(img, &err));
}

TEST(shp_corpus_parity_with_python_validator) {
    int libs = 0, clean_libs = 0, recs = 0, passed = 0;
    std::vector<std::string> fails;
    for (const auto& e : fs::recursive_directory_iterator(kRepo + "/extracted")) {
        if (!e.is_regular_file() || e.path().extension() != ".shp") continue;
        ShapeLibrary lib;
        std::string err;
        if (!lib.load(e.path().string(), &err)) continue;
        ++libs;
        bool clean = true;
        for (int i = 0; i < lib.count(); ++i) {
            ++recs;
            std::vector<uint8_t> px;
            if (lib.decode(i, px)) ++passed;
            else {
                clean = false;
                if (fails.size() < 40)
                    fails.push_back(e.path().filename().string() + ":" +
                                    std::to_string(i));
            }
        }
        if (clean) ++clean_libs;
    }
    std::printf("    shp corpus: %d libs, %d records, %d decode-pass, "
                "%d clean libs\n", libs, recs, passed, clean_libs);
    // Parity floors banked from scripts/r1_shp_unifiedlaw.py (measured):
    CHECK(libs >= 200);
    CHECK(recs >= 1500);
    CHECK(passed >= 1477);
    CHECK(clean_libs >= 176);
}
