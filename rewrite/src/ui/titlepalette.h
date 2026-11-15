// SPDX-License-Identifier: GPL-3.0-or-later

#pragma once
// t390 title-screen colour table: the t386 derived palette
// (rewrite/tests/data/title_palette_t386.tsv, docs/re/title-art.md §4).
//
// LAW: the vendor title screen is 0opening.gif drawn through an
// index-preserving COLOUR REPLACEMENT (t386 §1 registration: 0 conflicts
// at shift +40 over all 52 mapped indices). The TSV is the measurement.
// The GIF's own GCT is NOT the title palette (t386 §4, refuted arms) — it
// is used here ONLY as the honest fallback for the 203 indices the TSV
// does not cover: those indices do not occur in the art region the vendor
// screen was measured over, so whatever they show is declared vector-grade
// substitution, never "the original colour".
#include <cstdint>
#include <string>
#include <vector>

namespace ascend::ui {

struct TitlePalette {
    uint8_t rgb[256][3];
    bool mapped[256];  // true = TSV-measured, false = GCT fallback

    // Load the TSV and fill from `gct` (3*ntab bytes) for unmapped indices.
    // TSV path is relative to the repo when `dataRoot` is empty; the
    // runtime lookup order is <dataRoot>/../rewrite/tests/data/... then
    // <repo ASCENDANCY_SOURCE_DIR>/rewrite/tests/data/... . False + *err
    // only if the TSV cannot be read AT ALL (no data clone: the caller
    // refuses the art blit and stays honestly-vector, t390 law).
    bool load(const std::string& dataRoot, const uint8_t* gct, size_t gctLen,
              std::string* err);
};

}  // namespace ascend::ui
