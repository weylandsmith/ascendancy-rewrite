// SPDX-License-Identifier: GPL-3.0-or-later
// tPF-4 ROW/SHAPE ART-SOURCE LAW pins (docs/re/_wip_tPF4.md P4/P6).
// Law: shape producer 0x3c84c defaults to WORD[ds:0x6fd80] (=30=planitem.shp,
// measured 60/60 saves) and ONLY item 23 (Ship) swaps to
// WORD[ds:0x6fd60 + 2*specnum] with selector 0 (0x3c888..0x3c8a6); measured
// registry join: specnum 0..6 -> smship{19,2,11,0,9,5,6}.shp.
#include "ui/planetview.h"
#include "harness.h"

#include <fstream>
#include <sstream>
#include <string>

namespace au = ascend::ui;

TEST(ship_shape_file_law_tpf4) {
    // The permutation is MEASURED data (scripts/tPF4_rowart_runtime.py x the
    // cache registry, unanimous 60/60 across three banks). Pin every leg.
    const int want[7] = {19, 2, 11, 0, 9, 5, 6};
    for (int r = 0; r < 7; r++)
        CHECK(au::shipShapeFileNum(au::kShipItem, r) == want[r]);
    // Non-Ship items NEVER take the race table (the je-leg is item-keyed).
    for (int item = 0; item < 40; item++) {
        if (item == au::kShipItem) continue;
        CHECK(au::shipShapeFileNum(item, 0) == -1);
        CHECK(au::shipShapeFileNum(item, 3) == -1);
    }
    // Unknown specnum -> planitem fallback (port default, named in the header).
    CHECK(au::shipShapeFileNum(au::kShipItem, -1) == -1);
    CHECK(au::shipShapeFileNum(au::kShipItem, 7) == -1);
    CHECK(au::shipShapeFileNum(au::kShipItem, 20) == -1);

}

TEST(ship_shape_corpus_files_tpf4) {
    // The permutation must name files that EXIST in the corpus (the registry
    // names were read FROM the running game; the port must be able to load
    // what it names). smhome.shp is slot specnum 20's name — out of the
    // shipped 7-race range and NOT a smship file; that is the vendor's own
    // table shape, cited.
    for (int r = 0; r < 7; r++) {
        char path[256];
        std::snprintf(path, sizeof(path),
                      "%s/extracted/ascend01/data/smship%02d.shp",
                      ASCENDANCY_SOURCE_DIR, au::kShipShapeFile[r]);
        std::ifstream f(path, std::ios::binary);
        CHECK(f.is_open());
    }

}

TEST(ship_shape_wiring_tpf4) {
    // Source-text wiring pin (house style): the PLANLIST row render must use
    // the law, and the race libs must be loaded from the permutation.
    std::ifstream f(std::string(ASCENDANCY_SOURCE_DIR) +
                      "/rewrite/src/ui/ui.cpp");
    std::stringstream ss;
    ss << f.rdbuf();
    const std::string s = ss.str();
    CHECK(s.find("shipShapeFileNum(") != std::string::npos);
    CHECK(s.find("smshipLibs[rowSpec].record(0)") !=
          std::string::npos);  // selector 0 leg (0x3c8a6 mov word,0)
    CHECK(s.find("smship%02d.shp") != std::string::npos);
    CHECK(s.find("kShipShapeFile[i]") != std::string::npos);
    // The Ship row must scale 0.5 (0x3d08c..0x3d091 cmp 0x17 -> 0x8000/0x10000).
    CHECK(s.find("blitShapeScaleF(ren, smshipLibs[rowSpec], 0,") !=
          std::string::npos);

}
