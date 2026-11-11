// SPDX-License-Identifier: GPL-3.0-or-later

#include "formats/bin_table.h"

#include <cstring>
#include <fstream>

namespace ascend::formats {
namespace {
uint32_t rd32(const uint8_t* p) {
    uint32_t v;
    std::memcpy(&v, p, 4);
    return v;  // archives are u32 LE (docs/re/tables.md)
}
}  // namespace

std::optional<BinTable> BinTable::load(const std::filesystem::path& p, std::string* err) {
    std::ifstream f(p, std::ios::binary | std::ios::ate);
    if (!f) {
        if (err) *err = "cannot open " + p.string();
        return std::nullopt;
    }
    const std::streampos len = f.tellg();
    f.seekg(0);
    std::vector<uint8_t> buf(static_cast<size_t>(len));
    if (!f.read(reinterpret_cast<char*>(buf.data()), len)) {
        if (err) *err = "short read on " + p.string();
        return std::nullopt;
    }
    return parse(buf.data(), buf.size(), err);
}

std::optional<BinTable> BinTable::parse(const uint8_t* data, size_t len, std::string* err) {
    auto fail = [&](const std::string& m) -> std::optional<BinTable> {
        if (err) *err = m;
        return std::nullopt;
    };
    if (len < kBinHeaderSize) return fail("shorter than the 16-byte header");
    BinTable t;
    for (int i = 0; i < 4; ++i) t.header[i] = rd32(data + 4 * i);
    if (t.header[0] != kBinMagic0)
        return fail("header[0]=" + std::to_string(t.header[0]) + " != constant 60");
    for (int i = 1; i < 4; ++i)
        if (t.header[i] != 0)
            return fail("header[" + std::to_string(i) + "] nonzero (spec says always 0)");

    const size_t body = len - kBinHeaderSize;
    if (body % kBinRecordSize)
        return fail("body " + std::to_string(body) + " not a multiple of stride 24");
    const size_t nrec = body / kBinRecordSize;
    t.records.resize(nrec);
    for (size_t r = 0; r < nrec; ++r)
        for (uint32_t c = 0; c < kBinRecordFields; ++c)
            t.records[r][c] = rd32(data + kBinHeaderSize + r * kBinRecordSize + 4 * c);
    if (err) err->clear();
    return t;
}

}  // namespace ascend::formats
