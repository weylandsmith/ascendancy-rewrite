// SPDX-License-Identifier: GPL-3.0-or-later

#include "formats/bin_table.h"
#include "formats/cob.h"
#include "harness.h"

#include <filesystem>

#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif

namespace fs = std::filesystem;
using ascend::formats::BinTable;
using ascend::formats::CobArchive;

namespace {

std::vector<uint8_t> mkBin(const std::vector<std::array<uint32_t, 6>>& recs, bool good_magic = true) {
    std::vector<uint8_t> b;
    auto put = [&](uint32_t v) {
        for (int i = 0; i < 4; ++i) b.push_back(static_cast<uint8_t>((v >> (8 * i)) & 0xff));
    };
    put(good_magic ? 60u : 61u);
    put(0);
    put(0);
    put(0);
    for (const auto& r : recs)
        for (uint32_t v : r) put(v);
    return b;
}

}  // namespace

TEST(bin_parses_header_and_records) {
    auto img = mkBin({{1, 2, 3, 3, 1000, 0}, {7, 8, 9, 1, 2000, 5}});
    std::string err;
    auto t = BinTable::parse(img.data(), img.size(), &err);
    CHECK(t.has_value());
    if (!t) return;
    CHECK(t->rows() == 2);
    CHECK(t->records[0][0] == 1 && t->records[0][5] == 0);
    CHECK(t->records[1][2] == 9 && t->records[1][4] == 2000);
}

TEST(bin_rejects_wrong_magic) {
    auto img = mkBin({{1, 1, 1, 1, 1, 1}}, false);
    std::string err;
    CHECK(!BinTable::parse(img.data(), img.size(), &err).has_value());
}

TEST(bin_rejects_body_not_multiple_of_24) {
    auto img = mkBin({{1, 1, 1, 1, 1, 1}});
    img.pop_back();  // 23-byte body
    std::string err;
    CHECK(!BinTable::parse(img.data(), img.size(), &err).has_value());
}

TEST(bin_all_shipped_tables_parse_at_stride_24) {
    // Mirrors gate stage 3b: every .bin in the corpus must satisfy the
    // 16-byte-header + N x 24 invariant (docs/re/tables.md).
    std::string err;
    auto a = CobArchive::load(fs::path(ASCENDANCY_SOURCE_DIR) / "game" / "ascend02.cob", &err);
    if (!a) return;  // outside the repo
    int parsed = 0;
    for (const auto& e : a->entries()) {
        const size_t dot = e.name.rfind('.');
        if (dot == std::string::npos || e.name.compare(dot, 4, ".bin") != 0) continue;
        const uint8_t* p = nullptr;
        uint32_t n = 0;
        if (!a->find(e.name, &p, &n)) continue;
        auto t = BinTable::parse(p, n, &err);
        CHECK(t.has_value());
        if (t) ++parsed;
    }
    CHECK(parsed == 7);  // docs/re/tables.md: 7 tables, 7/7 exact
}
