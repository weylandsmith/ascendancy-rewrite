// SPDX-License-Identifier: GPL-3.0-or-later

#pragma once
// .bin data-table reader.
//
// FORMAT (verified 7/7 shipped tables — docs/re/tables.md, produced by
// scripts/table_probe.py, asserted by gate stage 3b):
//
//   +0x00  u32   constant 60
//   +0x04  u32   0
//   +0x08  u32   0
//   +0x0C  u32   0
//   +0x10  (body) N x 24 bytes, each 6 x u32 LE
//
// The body length must divide by 24 with zero remainder; that divisibility is
// the invariant, and this reader refuses anything else rather than guessing.
//
// WHAT THE COLUMNS MEAN IS STILL OPEN (OQ-004): docs/re/tables.md records
// per-column cardinality/range evidence but no semantics, because semantics
// require cross-references from the exe (docs/PLAN.md rule 3). Callers get
// raw u32 columns and must not rename them with an interpretation.

#include <array>
#include <cstdint>
#include <optional>
#include <string>
#include <vector>
#include <filesystem>

namespace ascend::formats {

inline constexpr uint32_t kBinHeaderSize = 16;   // docs/re/tables.md
inline constexpr uint32_t kBinRecordSize = 24;   // docs/re/tables.md
inline constexpr uint32_t kBinRecordFields = 6;  // 24 / 4
inline constexpr uint32_t kBinMagic0 = 60;       // docs/re/tables.md

struct BinTable {
    std::array<uint32_t, 4> header{};
    std::vector<std::array<uint32_t, kBinRecordFields>> records;

    size_t rows() const { return records.size(); }

    static std::optional<BinTable> load(const std::filesystem::path& p, std::string* err = nullptr);
    static std::optional<BinTable> parse(const uint8_t* data, size_t len, std::string* err = nullptr);
};

}  // namespace ascend::formats
