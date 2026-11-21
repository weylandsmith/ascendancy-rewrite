// SPDX-License-Identifier: GPL-3.0-or-later

// Population panel law — see poppanel.h for the citations. Pure math + a
// library-conformance gate; no SDL (ascend_ui links it; run_tests compiles
// this file directly, layout.cpp precedent).
#include "ui/poppanel.h"

#include "formats/shp.h"
#include "game/campaign.h"

namespace ascend::ui {

int popSlotRecord(int selector) {
    // IDENTITY law [verified t254]: the runtime selector table at copy+8 +
    // 8*sel maps sel 0..8 to record stream starts 0..8 exactly (9/9), so the
    // band selectors 1..3 address records k1/k2/k3 directly. Values outside
    // 1..3 are outside the band formula's output range; report -1 rather
    // than invent a record.
    return (selector >= 1 && selector <= 3) ? selector : -1;
}

PopSlotRole popSlotRoleOf(int selector) {
    switch (selector) {
        case 1: return PopSlotRole::Busy;   // k1 sideways red + blue tool
        case 2: return PopSlotRole::Free;   // k2 front-facing yellow
        default: return PopSlotRole::Empty; // k3 hollow ring (and unreachable)
    }
}

std::vector<PopCell> popPanelCells(const std::vector<int>& bands, Pt origin) {
    // Vendor iteration order preserved: the loop walks i = 0..cap-1 and each
    // cell lands on the pitch grid (10 columns, 10 px). Cells whose selector
    // has no record (never from popBands) are still EMITTED at their grid
    // position with record -1 — the vendor blits whatever the cache holds;
    // the caller decides whether to draw record -1.
    std::vector<PopCell> cells;
    cells.reserve(bands.size());
    for (size_t i = 0; i < bands.size(); ++i) {
        PopCell c;
        c.selector = bands[i];
        c.record = popSlotRecord(bands[i]);
        c.pos = {origin.x + int(i % kPopSlotsPerRow) * kPopSlotPitch,
                 origin.y + int(i / kPopSlotsPerRow) * kPopSlotPitch};
        cells.push_back(c);
    }
    return cells;
}

int popPanelRows(int cap) {
    // The row counter (EBP) advances only when i % 10 == 9, so a partial
    // final row is still ONE row of paint: rows = ceil(cap/10). The cap exit
    // (0x3ce87 jge) makes cap <= 0 draw nothing.
    if (cap <= 0) return 0;
    return (cap + kPopSlotsPerRow - 1) / kPopSlotsPerRow;
}

std::vector<PopCell> popPanelFor(const ascend::game::Campaign& camp, int star,
                                 Pt origin) {
    // +0x4c/+0x42/+0x4a analogs via the t199 band law (campaign.h popBands:
    // SEL(i) = 1 + [i>=used] + [i>=pop] over i < cap).
    return popPanelCells(camp.popBandsFor(star), origin);
}

bool popSlotLibraryConforms(const std::string& path, std::string* err) {
    // Census from docs/re/_wip_t263.md S2/S3 (this session) + shp.md S23:
    // 9 records; k1 9x9, k2 7x9, k3 8x8. Every invariant is a MEASURED fact,
    // so a mismatch means this file is not the pop-slot library.
    ascend::formats::ShapeLibrary lib;
    std::string local;
    if (!lib.load(path, &local)) {
        if (err) *err = "container: " + local;
        return false;
    }
    if (lib.count() != 9) {
        if (err) *err = "record count " + std::to_string(lib.count()) +
                        " != 9 (17np census: 9)";
        return false;
    }
    // tA1 BBOX-DIFF re-cite: k1 9x9, k2 6x9 (L,T=(2,1)), k3 8x8 (bboxes verbatim)
    const int want[3][2] = {{9, 9}, {6, 9}, {8, 8}};
    for (int r = 0; r < 3; ++r) {
        const auto& rec = lib.record(r + 1);
        if (int(rec.width) != want[r][0] || int(rec.height) != want[r][1]) {
            if (err)
                *err = "k" + std::to_string(r + 1) + " dims " +
                       std::to_string(rec.width) + "x" +
                       std::to_string(rec.height) + " != " +
                       std::to_string(want[r][0]) + "x" + std::to_string(want[r][1]);
            return false;
        }
    }
    return true;
}

}  // namespace ascend::ui
