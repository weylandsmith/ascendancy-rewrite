// SPDX-License-Identifier: GPL-3.0-or-later
#include "ui/speciesmenu.h"

namespace ascend::ui {

namespace ag = ascend::game;

std::vector<SpeciesRow> speciesMenuRows(const ag::Campaign& camp,
                                        const std::vector<ag::SpeciesInfo>* roster) {
    std::vector<SpeciesRow> rows;
    // owner -> specnum: the scenario build law (main.cpp buildCampaign —
    // "six AI races = first six specnums that are not the player's",
    // documented default policy; owner i+1 takes the i-th roster entry
    // that survives the skip). Recomputed here so the module stays a pure
    // read of (campaign, roster).
    std::vector<int> specnumOfOwner;
    if (roster) {
        specnumOfOwner.push_back(-1);  // owner 0 = player
        for (const auto& si : *roster) {
            if (int(specnumOfOwner.size()) >= camp.ownerCount()) break;
            if (si.specnum == camp.playerSpecies()) continue;
            specnumOfOwner.push_back(si.specnum);
        }
    }
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
