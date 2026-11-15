// SPDX-License-Identifier: GPL-3.0-or-later
#include "formats/gamepal.h"

#include <cstdio>
#include <fstream>

namespace ascend::formats {

namespace {
constexpr size_t kFileBytes = 768;  // 256 RGB triples, no header (media.md §6)
}

bool GamePalette::load(const std::string& path, std::string* err) {
    std::ifstream in(path, std::ios::binary | std::ios::ate);
    if (!in) {
        if (err) *err = "cannot open " + path;
        return false;
    }
    const auto sz = in.tellg();
    if (sz != static_cast<std::streamoff>(kFileBytes)) {
        if (err)
            *err = path + ": expected " + std::to_string(kFileBytes) +
                   " B, got " + std::to_string(static_cast<long long>(sz));
        return false;
    }
    std::vector<uint8_t> bytes(kFileBytes);
    in.seekg(0);
    in.read(reinterpret_cast<char*>(bytes.data()), kFileBytes);
    return parse(std::move(bytes), err);
}

bool GamePalette::parse(std::vector<uint8_t> bytes, std::string* err) {
    if (bytes.size() != kFileBytes) {
        if (err)
            *err = "expected " + std::to_string(kFileBytes) + " B, got " +
                   std::to_string(bytes.size());
        loaded_ = false;
        return false;
    }
    for (int i = 0; i < kSize * 3; ++i) {
        const uint8_t v = bytes[i];
        // DOSBox 6->8-bit saturating conversion (gamepal.h header law).
        conv_[i] = static_cast<uint8_t>((v << 2) | (v >> 4));
    }
    loaded_ = true;
    return true;
}

void GamePalette::rgb(int index, uint8_t out[3]) const {
    const int i = (index & 0xff) * 3;
    out[0] = conv_[i];
    out[1] = conv_[i + 1];
    out[2] = conv_[i + 2];
}

uint32_t GamePalette::argb(int index) const {
    const int i = (index & 0xff) * 3;
    return 0xFF000000u | (static_cast<uint32_t>(conv_[i]) << 16) |
           (static_cast<uint32_t>(conv_[i + 1]) << 8) | conv_[i + 2];
}

}  // namespace ascend::formats
