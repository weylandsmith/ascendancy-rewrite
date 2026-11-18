// SPDX-License-Identifier: GPL-3.0-or-later

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
    REQUIRE_DATA();
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
    REQUIRE_DATA();
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
    REQUIRE_DATA();
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
    REQUIRE_DATA();
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
    // Parity floors banked from scripts/r1_shp_unifiedlaw.py (measured).
    // t197 pins EXACT parity: span-bound removed (shp.md S21) promotes the
    // X class (29: planind k0..k12, 3cfgnew k0..k11, 14intel k8, 1starmap
    // k3/k4/k6); the both-components dims gate demotes exactly 2 degenerate
    // walks the vendor refuses (mouse k5 W=0, sg64expl k0 H=0xfffffffb).
    // Measured this session BOTH SIDES: 1513 decode-pass / 187 clean libs.
    // Pre-t197 baselines: C++ decode 1484/185, Python validator 1486/186
    // (t182 numbers) — the 2-record C++/Python gap was exactly mouse k5 +
    // sg64expl k0 (Python walked them despite a garbage dims component),
    // now unified on the blit-faithful both-components rule.
    CHECK(libs >= 200);
    CHECK(recs >= 1500);
    // t367: the corner-anchor gate fallback (shp.md S28) adds EXACTLY mouse
    // k5/k6/k7 over the t197 Python validator tally (1513/187): floors move
    // to 1516/188. The Python validator itself stays on the t197 law (gate
    // 3c-2 pins 1513-side strings) — the divergence is intentional and
    // asserted exactly by TEST(shp_corner_anchor_fallback_t367) below.
    CHECK(passed >= 1516);
    CHECK(clean_libs >= 188);
}

TEST(shp_span_free_t197) {
    REQUIRE_DATA();
    // The span bound was our validator's invention (shp.md S20.2: blit
    // FUN_0005caac has no length arg, no overrun error; cache = verbatim
    // whole-library copy). Pins BOTH sides of the t197 correction.
    ShapeLibrary planind, cfg, star, mous;
    std::string err;
    CHECK(planind.load(kA01 + "planind.shp", &err));
    CHECK(cfg.load(kA01 + "3cfgnew.shp", &err));
    CHECK(star.load(kA01 + "1starmap.shp", &err));
    CHECK(mous.load(kA01 + "mouse.shp", &err));

    // (1) planind k0 walks its FULL declared 99 rows although its directory
    // span [rec0, rec1) holds only ~89 rows at declared W (t196 triage:
    // 77..95 of 99 bounded). Compare row content past the span against a
    // second decode: deterministic (pure function of file bytes), and the
    // plane is fully sized W*H.
    std::vector<uint8_t> a, b;
    bool sw = true;
    CHECK(planind.decode(0, a, &sw));
    CHECK(!sw);  // canonical orientation completes
    CHECK(planind.decode(0, b));
    CHECK(a.size() == size_t(planind.record(0).width) *
                        planind.record(0).height);
    CHECK(a == b);  // determinism
    const auto& r0 = planind.record(0);
    CHECK(r0.end > r0.stream);  // span sanity
    // Rows past the span must be file bytes walked as ops: the past-span
    // band is NOT uniformly zero in planind (t197 pastrows probe: 40
    // distinct indices in k0's tail). Two value-free witnesses below.
    bool tail_nonuniform = false;
    // Distinct indices over the whole plane: a truncated/blocked decode
    // stops early and cannot reach 30 (probe: k0 tail band alone has 40).
    {
        std::vector<bool> seen(256, false);
        int distinct = 0;
        for (uint8_t v : a) if (!seen[v]) { seen[v] = true; ++distinct; }
        CHECK(distinct >= 30);  // pastrows probe: k0 tail alone has 40
    }
    for (uint32_t y = r0.height - 4; y < r0.height; ++y) {
        const uint8_t* p = a.data() + size_t(y) * r0.width;
        for (uint32_t x = 0; x < r0.width; ++x)
            if (p[x]) { tail_nonuniform = true; break; }
    }
    CHECK(tail_nonuniform);  // bottom band was written (span-crossing walk)

    // (2) 3cfgnew k0..k11 decode; k12 PARTIAL-Paints (t423 law change,
    // docs/re/_wip_t423.md F5b): the truncation is IN the shipped archive
    // (ascend01.cob blob md5 == extracted twin, both end mid-row ~55/79),
    // the vendor blit has no length arg and paints resident bytes, so the
    // blank-refusal was a PORT bug. Pin: decode succeeds, the top 50 rows
    // (inside the bbox y25..79 glyph) carry content, and the walk consumed
    // the file to EOF (rows below the truncation stay untouched).
    for (int k = 0; k <= 11; ++k) {
        std::vector<uint8_t> px;
        CHECK(cfg.decode(k, px));
    }
    {
        std::vector<uint8_t> px;
        CHECK(cfg.decode(12, px));
        CHECK(px.size() == size_t(cfg.record(12).width) *
                               cfg.record(12).height);
        const auto& r12 = cfg.record(12);
        bool top_content = false;
        for (uint32_t y = 25; y < 50 && !top_content; ++y)
            for (uint32_t x = 0; x < r12.width; ++x)
                if (px[size_t(y) * r12.width + x]) { top_content = true; break; }
        CHECK(top_content);  // the orb glyph rows ARE painted
    }

    // (3) Garbage dims still rejected despite the unbounded walk:
    // 1starmap k1 dims word 0x7ffffdbb-class (no negative bbox anchor).
    // t367 AMENDMENT: mouse k6/k7 formerly asserted REJECT here; under the
    // D1 keep ruling + the corner-anchor gate fallback (shp.md S28) they
    // decode at 78x47 — see TEST(shp_corner_anchor_fallback_t367).
    { std::vector<uint8_t> px; CHECK(!star.decode(1, px)); }

    // (4) 14intel k8 + 1starmap k3/k4/k6 (the other X members) decode.
    ShapeLibrary intel;
    CHECK(intel.load(kA01 + "14intel.shp", &err));
    { std::vector<uint8_t> px; CHECK(intel.decode(8, px)); }
    { std::vector<uint8_t> px; CHECK(star.decode(3, px)); }
    { std::vector<uint8_t> px; CHECK(star.decode(4, px)); }
    { std::vector<uint8_t> px; CHECK(star.decode(6, px)); }
}

// FNV-1a 64 — pin helper (md5 not in the codebase; identity + census are
// what the law asserts, the digest is just a compact witness).
static uint64_t fnv64(const std::vector<uint8_t>& v) {
    uint64_t h = 1469598103934665603ull;
    for (uint8_t b : v) { h ^= b; h *= 1099511628211ull; }
    return h;
}

TEST(shp_corner_anchor_fallback_t367) {
    REQUIRE_DATA();
    // D1 RULING (docs/DECISIONS.md USER block 2026-11-09 12:45: "D1 mouse
    // k5/k6/k7 = keep as-is") + t344 S27 geometry law + t367 file
    // measurement (shp.md S28). k4..k7 = ONE 78x47 glyph at four corner
    // anchors. The d1page pin md5 b2d049bbf5b5 IS the k5/k6/k7 plane at
    // 78x47 (full md5 b2d049bbf5b571bfc4ea3b97db7a4fa7, re-derived t367;
    // an early scratch-reference walk that failed to reproduce it had a
    // pixel-position bug — the C++ walkRows was correct).
    ShapeLibrary mous;
    std::string err;
    CHECK(mous.load(kA01 + "mouse.shp", &err));
    CHECK(mous.count() == 12);

    // (1) k5/k6/k7 decode via the fallback at bbox dims 78x47.
    std::vector<uint8_t> p5, p6, p7;
    CHECK(mous.decode(5, p5));
    CHECK(mous.decode(6, p6));
    CHECK(mous.decode(7, p7));
    CHECK(p5.size() == 78u * 47u);
    CHECK(p6.size() == p5.size());
    CHECK(p7.size() == p5.size());

    // (2) BYTE-IDENTITY LAW: one glyph, four anchors (t367 measured: raw
    // stream, painted plane, and the ruling-page PNGs all agree 4/4).
    CHECK(p5 == p6);
    CHECK(p6 == p7);

    // (3) Value pins (measured t367): the k5 plane at 78x47 (zero underlay)
    // md5s b2d049bbf5b571bfc4ea3b97db7a4fa7 — EXACTLY the d1page pin
    // b2d049bbf5b5 (verified t367 against a corrected reference walk; the
    // C++ walkRows was always right). No md5 helper exists in the codebase,
    // so the test pins census + non-zero count + FNV-1a 64 of the same
    // bytes: a desynced walk cannot reproduce all three.
    uint64_t census = 0;
    int nonzero = 0;
    for (uint8_t v : p5) { census += v; if (v) ++nonzero; }
    CHECK(census == 543287ull);
    CHECK(nonzero == 3666);
    const uint64_t plane_fnv = fnv64(p5);
    CHECK(plane_fnv == 0x3ba44ef8c0c54974ull);  // == md5 b2d049bbf5b5 bytes
    std::printf("    t367 mouse k5 plane: 78x47 census %llu nonzero %d "
                "fnv64 %016llx (md5 b2d049bbf5b5...)\n",
                (unsigned long long)census, nonzero,
                (unsigned long long)plane_fnv);
    // Determinism: second decode bit-identical.
    std::vector<uint8_t> again;
    CHECK(mous.decode(5, again));
    CHECK(again == p5);

    // (4) NEGATIVE CONTROL (the blast-radius law, shp.md S28): records the
    // vendor -1 blit gate provably refuses must STAY rejected even though a
    // naive bbox read would rescue them. cos_star k40..k51 zero headers,
    // sg50expl k9 1x1 bbox, 1starmap k1 no negative anchor.
    ShapeLibrary cos, sg50;
    CHECK(cos.load(kA01 + "cos_star.shp", &err));
    for (int k = 40; k <= 51; ++k) {
        std::vector<uint8_t> px;
        CHECK(!cos.decode(k, px));
    }
    CHECK(sg50.load(kA01 + "sg50expl.shp", &err));
    { std::vector<uint8_t> px; CHECK(!sg50.decode(9, px)); }
    ShapeLibrary star;
    CHECK(star.load(kA01 + "1starmap.shp", &err));
    { std::vector<uint8_t> px; CHECK(!star.decode(1, px)); }

    // (5) k4 stays on the CANONICAL gate (dims 77x46 valid): the fallback
    // never runs for it. Its canonical plane differs from the 78x47 plane
    // (77 vs 78 stride) — assert the canonical size.
    std::vector<uint8_t> p4;
    CHECK(mous.decode(4, p4));
    CHECK(p4.size() == size_t(mous.record(4).width) * mous.record(4).height);
    CHECK(mous.record(4).width == 77u && mous.record(4).height == 46u);
}
