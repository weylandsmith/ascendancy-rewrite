// SPDX-License-Identifier: GPL-3.0-or-later

// Planet-screen strip law — see planetstrip.h for the citations. Pure math
// + a library census; no SDL (planetwin.cpp / poppanel.cpp precedent).
// Working notes: docs/re/_wip_t428.md F5/F9.
#include "ui/planetstrip.h"

#include "formats/shp.h"
#include "game/campaign.h"
#include "ui/planetwin.h"

namespace ascend::ui {

StripPlan stripPlanFor(const ascend::game::Campaign& camp, int star) {
    StripPlan s;
    if (star < 0) return s;  // zeroed plan (rec 0 panels, no cells, no project)
    // Gauge selectors [verified planets-ui.md S3 + S2 dispatch table]:
    // PLRES = clamp0..20(round(RES^0.75)) on the +0x46 analog, PLIND the
    // same on +0x44, PLPRO identity on +0x48.
    const auto cw = camp.channelWordsFor(star);
    const int sel[3] = {gaugeSelector(cw.res), gaugeSelector(cw.ind),
                        prosSelector(cw.pros)};
    for (int i = 0; i < 3; i++) {
        s.gauges[i].lib = i;
        s.gauges[i].rec = sel[i];
        s.gauges[i].rect = kPlanetPanels[i].rect;  // PLRES/PLIND/PLPRO order
    }
    // Pop grid: the t263 loop law, anchored at the PLPOP rect origin.
    s.popCells = popPanelFor(camp, star, kPopGridOrigin);
    // Project panel: planitem record index == item (shp.md S23.4); -1 =
    // static.txt #141 "No Project" (witness A).
    s.projectItem = camp.pendingItemFor(star);
    return s;
}

bool stripGaugeLibraryConforms(const std::string& path, std::string* err) {
    ascend::formats::ShapeLibrary lib;
    std::string lerr;
    if (!lib.load(path, &lerr)) {
        if (err) *err = "load refused: " + lerr;
        return false;
    }
    if (int(lib.count()) != kStripGaugeRecords) {
        if (err)
            *err = "record count " + std::to_string(lib.count()) +
                   " != 21 (the clamp0..20 gauge domain)";
        return false;
    }
    for (int i = 0; i < kStripGaugeRecords; i++) {
        const auto& r = lib.record(i);
        // tA1: under the bbox law the gauge WIDTH is 108 on all 21
        // records of all three libs (verbatim); heights VARY per record
        // (planind {77,80,89,95,99}) so height is not an identity term.
        if (r.width != 108) {
            if (err)
                *err = "record " + std::to_string(i) + " dims " +
                       std::to_string(r.width) + "x" +
                       std::to_string(r.height) + " != 107x99 (rect-fill)";
            return false;
        }
    }
    return true;
}

bool fieldLibraryConforms(const std::string& path, std::string* err) {
    ascend::formats::ShapeLibrary lib;
    std::string lerr;
    if (!lib.load(path, &lerr)) {
        if (err) *err = "load refused: " + lerr;
        return false;
    }
    if (lib.count() != 9) {
        if (err)
            *err = "record count " + std::to_string(lib.count()) +
                   " != 9 (17np census: 9)";
        return false;
    }
    const auto& r = lib.record(kFieldRecord);
    if (int(r.width) != kFieldRecordW || int(r.height) != kFieldRecordH) {
        if (err)
            *err = "record " + std::to_string(kFieldRecord) + " dims " +
                   std::to_string(r.width) + "x" + std::to_string(r.height) +
                   " != 625x357 (the t428c-registered starfield)";
        return false;
    }
    return true;
}

}  // namespace ascend::ui
