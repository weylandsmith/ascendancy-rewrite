// SPDX-License-Identifier: GPL-3.0-or-later

#include "formats/cob.h"
#include "harness.h"

#include <cstring>
#include <filesystem>
#include <fstream>
#include <vector>

#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif

namespace fs = std::filesystem;
using ascend::formats::CobArchive;

namespace {

const fs::path kRepo = ASCENDANCY_SOURCE_DIR;

std::vector<uint8_t> slurp(const fs::path& p) {
    std::ifstream f(p, std::ios::binary | std::ios::ate);
    if (!f) return {};
    std::vector<uint8_t> b(static_cast<size_t>(f.tellg()));
    f.seekg(0);
    f.read(reinterpret_cast<char*>(b.data()), f.tellg() >= 0 ? std::streamsize(b.size()) : 0);
    return b;
}

// Builds a synthetic archive exactly per the verified layout so the parser can
// be tested without depending on the shipped files.
std::vector<uint8_t> buildArchive(const std::vector<std::pair<std::string, std::string>>& files,
                                  size_t* dirEndOut = nullptr) {
    std::vector<uint8_t> b;
    auto put32 = [&](uint32_t v) {
        b.push_back(v & 0xff);
        b.push_back((v >> 8) & 0xff);
        b.push_back((v >> 16) & 0xff);
        b.push_back((v >> 24) & 0xff);
    };
    put32(static_cast<uint32_t>(files.size()));
    for (const auto& kv : files) {
        for (char c : kv.first) b.push_back(static_cast<uint8_t>(c));
        b.push_back(0);
        b.push_back(0);  // at least one NUL of padding
    }
    const size_t dir_end = b.size();
    if (dirEndOut) *dirEndOut = dir_end;
    std::vector<uint32_t> offs;
    uint32_t cur = static_cast<uint32_t>(dir_end + 4 * files.size());
    for (const auto& kv : files) {
        offs.push_back(cur);
        cur += static_cast<uint32_t>(kv.second.size());
    }
    for (uint32_t o : offs) put32(o);
    for (const auto& kv : files)
        for (char c : kv.second) b.push_back(static_cast<uint8_t>(c));
    return b;
}

}  // namespace

TEST(cob_parses_synthetic_and_round_trips_blobs) {
    auto img = buildArchive({{"alpha.txt", "hello"}, {"data\\sub\\b.bin", "\x01\x02\x03\x03"}});
    std::string err;
    auto a = CobArchive::parse(img, &err);
    CHECK(a.has_value());
    if (!a) return;
    CHECK(a->count() == 2);
    const uint8_t* p = nullptr;
    uint32_t n = 0;
    CHECK(a->find("alpha.txt", &p, &n));
    CHECK(n == 5);
    CHECK(std::string(p, p + n) == "hello");
    CHECK(a->find("data\\sub\\b.bin", &p, &n));
    CHECK(n == 4);
    CHECK(p[0] == 1 && p[3] == 3);
    CHECK(!a->find("nope.txt", &p, &n));
}

// The offset table begins at dir_end (the first byte after the padded name
// records), so corruption must be applied THERE. An earlier version of this
// test wrote at filesize-8, which for these sizes lands in the DATA area —
// and data bytes are not validated, so the archive legitimately parsed and
// the test failed for the wrong reason.
TEST(cob_rejects_non_monotonic_table) {
    size_t de = 0;
    auto img = buildArchive({{"a.txt", "aaaa"}, {"b.txt", "bbbb"}}, &de);
    // Swap the two offsets so the table decreases.
    const uint32_t o0 = img[de] | (img[de + 1] << 8) | (img[de + 2] << 16) | (img[de + 3] << 24);
    const uint32_t o1 = img[de + 4] | (img[de + 5] << 8) | (img[de + 6] << 16) | (img[de + 7] << 24);
    CHECK(o0 < o1);
    for (int i = 0; i < 4; ++i) {
        img[de + i] = static_cast<uint8_t>((o1 >> (8 * i)) & 0xff);
        img[de + 4 + i] = static_cast<uint8_t>((o0 >> (8 * i)) & 0xff);
    }
    std::string err;
    CHECK(!CobArchive::parse(img, &err).has_value());
}

TEST(cob_rejects_bad_first_offset) {
    size_t de = 0;
    auto img = buildArchive({{"a.txt", "aaaa"}, {"b.txt", "bbbb"}, {"c.txt", "cccc"}}, &de);
    // off[0] must equal dir_end + 4N exactly (docs/FINDINGS.md P1a).
    const uint32_t o0 = img[de] | (img[de + 1] << 8) | (img[de + 2] << 16) | (img[de + 3] << 24);
    const uint32_t bumped = o0 + 4;  // still increasing, but wrong start
    for (int i = 0; i < 4; ++i) img[de + i] = static_cast<uint8_t>((bumped >> (8 * i)) & 0xff);
    std::string err;
    CHECK(!CobArchive::parse(img, &err).has_value());
}

TEST(cob_reads_all_shipped_archives_and_matches_extracted_dir) {
    // Strongest available check: the C++ reader must reproduce, byte for byte,
    // the tree the verified Python extractor produced (gate stages 2 and 3b).
    struct Item {
        const char* cob;
        const char* dir;
        size_t min_entries;
    };
    const Item items[] = {
        {"game/ascend00.cob", "extracted/ascend00", 54},
        {"game/ascend01.cob", "extracted/ascend01", 260},
        {"game/ascend02.cob", "extracted/ascend02", 89},
    };
    for (const auto& it : items) {
        const fs::path cobp = kRepo / it.cob;
        if (!fs::exists(cobp)) continue;  // runs outside the repo: skip
        std::string err;
        auto a = CobArchive::load(cobp, &err);
        CHECK(a.has_value());
        if (!a) {
            std::printf("    %s: %s\n", it.cob, err.c_str());
            continue;
        }
        CHECK(a->count() >= it.min_entries);

        size_t checked = 0, mismatched = 0;
        for (const auto& e : a->entries()) {
            std::string rel = e.name;
            for (auto& c : rel)
                if (c == '\\') c = '/';
            const fs::path disk = kRepo / it.dir / rel;
            if (!fs::exists(disk)) continue;
            const std::vector<uint8_t> want = slurp(disk);
            const uint8_t* got = nullptr;
            uint32_t glen = 0;
            if (!a->find(e.name, &got, &glen)) continue;
            ++checked;
            if (glen != want.size() || std::memcmp(got, want.data(), want.size()) != 0)
                ++mismatched;
        }
        CHECK(checked > 10);
        if (mismatched) std::printf("    %s: %zu mismatched of %zu\n", it.cob, mismatched, checked);
        CHECK(mismatched == 0);
    }
}
