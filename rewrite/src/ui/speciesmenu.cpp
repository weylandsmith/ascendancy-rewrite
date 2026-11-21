// SPDX-License-Identifier: GPL-3.0-or-later
#include "ui/speciesmenu.h"

#include <cmath>

namespace ascend::ui {

namespace ag = ascend::game;

std::vector<int> speciesSpecnumOfOwner(
    const ag::Campaign& camp, const std::vector<ag::SpeciesInfo>* roster) {
    // owner -> specnum: the scenario build law (main.cpp buildCampaign —
    // "six AI races = first six specnums that are not the player's",
    // documented default policy; owner i+1 takes the i-th roster entry
    // that survives the skip).
    std::vector<int> specnumOfOwner(size_t(camp.ownerCount()), -1);
    specnumOfOwner[0] = camp.playerSpecies();  // owner 0 = player
    if (roster)
        for (const auto& si : *roster) {
            size_t next = 1;
            while (next < specnumOfOwner.size() && specnumOfOwner[next] != -1)
                next++;
            if (next >= specnumOfOwner.size()) break;
            if (si.specnum == camp.playerSpecies()) continue;
            specnumOfOwner[next] = si.specnum;
        }
    return specnumOfOwner;
}

Pt speciesPortraitSlot(const Rect& fld, int k, int nslots) {
    // [measured t441 T6, t252 pair] four 109x109 repaints at r=170 about the
    // cosmos centre (234.2,238.0 ~ kCosmosWnd centre (236,239)), angles
    // 89.7/180.3/269.9/0.0 for rows 0..3. Screen y is down -> sin negated.
    // nslots<2 falls back to 4 (the measured case).
    const int n = nslots >= 2 ? nslots : 4;
    const double a = (90.0 + 360.0 / n * k) * M_PI / 180.0;
    const int cx = (fld.x0 + fld.x1) / 2, cy = (fld.y0 + fld.y1) / 2;
    return Pt{cx + int(std::lround(kSpeciesRingRadius * std::cos(a))),
              cy - int(std::lround(kSpeciesRingRadius * std::sin(a)))};
}

std::vector<SpeciesRow> speciesMenuRows(const ag::Campaign& camp,
                                        const std::vector<ag::SpeciesInfo>* roster) {
    std::vector<SpeciesRow> rows;
    const std::vector<int> specnumOfOwner = speciesSpecnumOfOwner(camp, roster);
    for (int o = 1; o < camp.ownerCount(); ++o) {
        if (!camp.playerKnows(o)) continue;  // static #11 "known" gate
        SpeciesRow r;
        r.owner = o;
        r.extinct = camp.starsOwned(o) == 0;  // static #12 "Extinct"
        if (roster && o < int(specnumOfOwner.size())) {
            r.flagSpecnum = specnumOfOwner[size_t(o)];
            for (const auto& si : *roster)
                if (si.specnum == r.flagSpecnum) { r.name = si.dipName; break; }
        }
        if (r.name.empty()) r.name = camp.ownerName(o);
        rows.push_back(std::move(r));
    }
    return rows;
}

std::string speciesMenuHeader(const ag::Campaign& camp) {
    int known = 0;
    const int total = camp.ownerCount() - 1;  // AI owners
    for (int o = 1; o < camp.ownerCount(); ++o)
        if (camp.playerKnows(o)) ++known;
    // static.txt #11 template verbatim.
    return std::to_string(known) + " of " + std::to_string(total) +
           " Species Known";
}

}  // namespace ascend::ui
