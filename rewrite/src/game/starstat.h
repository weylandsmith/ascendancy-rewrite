#pragma once
// Star-type statistics + name pools for galaxy generation.
// Citations: docs/re/mapgen.md sections 1-2.

#include <cstdint>
#include <optional>
#include <string>
#include <vector>
#include <filesystem>

namespace ascend::game {

// docs/re/mapgen.md §1: TYPE_<n>\t<pct> Percent\t<lanes> Lanes, 13 rows,
// percent column sums to 100.01 (2-dp rounding).
struct StarTypeStat {
    double percent = 0.0;  // occurrence share, %
    double lanes = 0.0;    // mean star-lane degree for this type
};

class StarStats {
  public:
    // Fails (returns nullopt) unless exactly 13 rows parse AND the percent
    // column sums to 100 within +-0.02 — the two invariants measured in
    // docs/re/mapgen.md §1. Never clamps silently.
    static std::optional<StarStats> load(const std::filesystem::path& file,
                                         std::string* err = nullptr);
    static std::optional<StarStats> parse(const std::string& text, std::string* err = nullptr);

    const std::vector<StarTypeStat>& rows() const { return rows_; }
    size_t size() const { return rows_.size(); }

    // Mean of the lanes column over all types (docs/re/mapgen.md §1: 2.225).
    double meanLanes() const;

    // Type index for a uniform draw in [0,1) using the percent column as
    // weights (normalised at load; we do NOT re-normalise to exactly 100 so
    // the shipped 100.01 stays visible in behaviour, only in ratios).
    int pickType(double u) const;

  private:
    std::vector<StarTypeStat> rows_;
};

// docs/re/mapgen.md §2: names.txt holds 100 star bases (C-side count; the
// file ends with two blank lines + a 0x1A EOF marker); planets are named
// "<base> <roman>" (the generator never numbers stars themselves).
std::vector<std::string> loadStarNames(const std::filesystem::path& namesTxt,
                                       std::string* err = nullptr);

// 1..13 (orbit numerals observed I..V; the table extends the obvious way and
// nothing emits 0) — docs/re/mapgen.md §3.
std::string roman(int n);

}  // namespace ascend::game
