// SPDX-License-Identifier: GPL-3.0-or-later

// t406 PLANET VIEW + PROJECT-SET law — see planetview.h for the citations.
// Pure data + gate math (no SDL), compiled into run_tests (statuslist.cpp
// precedent). Working notes: docs/re/_wip_t406.md.
#include "ui/planetview.h"

#include "game/economy.h"  // requiresAvailable (OQ-014 CLOSED)
#include "ui/planetwin.h"  // planetGaugesFor (t276 gauge wiring)
#include "ui/statuslist.h"  // statusLine1 / statusDays (shared assembly)

namespace ascend::ui {

namespace {
// The 0x388ec domain gate: cmd0 rejects item >= 39 (cmp 0x27; jae reject).
inline bool inOrderDomain(int item) { return item >= 0 && item < 39; }
}  // namespace

PlanetView planetViewFor(const ascend::game::Campaign& camp, int star,
                         const std::string& name) {
    PlanetView v;
    const auto& g = camp.galaxy();
    if (star < 0 || star >= int(g.stars.size())) return v;
    const auto& ps = camp.planetAt(star);
    const int sizeIdx = ascend::game::Campaign::sizeClassFor(ps.surfaceCells);
    v.title = statusLine1(name, sizeIdx, ps.terrainRow);
    v.pop = int(ps.pop);                       // +0x42 analog
    v.used = camp.usedPopFor(star);            // +0x4c analog
    v.cap = camp.popCapAt(star);               // +0x4a analog
    const PlanetGauges gsg = planetGaugesFor(camp, star);
    v.res = gsg.res; v.ind = gsg.ind; v.pros = gsg.pros;
    v.pendingItem = camp.pendingItemFor(star);
    v.noProject = v.pendingItem < 0;
    v.noFreePopulation = (v.pop == v.used);    // the 0x508da predicate
    if (v.pendingItem >= 0) {
        if (const auto* pi = camp.planetItem(v.pendingItem))
            v.days = statusDays(pi->cost, camp.buildAccFor(star),
                                camp.channelWordsFor(star).ind);
    }
    return v;
}

std::vector<ProjectOption> projectOptionsFor(
    const ascend::game::Campaign& camp, int star) {
    // LIST MEMBERSHIP (planetview.h header): table order, REQUIRES-gated
    // (income-law S4), domain < 39 (0x388ec). Free-pop is an ORDER gate,
    // not a list filter — the vendor shows the row and the order rejects.
    std::vector<ProjectOption> out;
    if (star < 0 || star >= int(camp.galaxy().stars.size())) return out;
    const int n = camp.planItemCount();
    for (int id = 0; id < n && id < 39; ++id) {
        const auto* pi = camp.planetItem(id);
        if (!pi) continue;
        if (!ascend::game::requiresAvailable(pi->reqByte, camp.techCountTotal(),
                                             camp.playerTechs()))
            continue;
        out.push_back(ProjectOption{id, pi->name, pi->cost});
    }
    return out;
}

bool projectOrderable(const ascend::game::Campaign& camp, int star, int item) {
    // cmd0 gates (1)(2)(3) — verbatim order of the fn 0x38840 legs.
    if (!inOrderDomain(item)) return false;                       // 0x388ec
    if (camp.pendingItemFor(star) >= 0) return false;             // 0x388e2
    const auto* pi = camp.planetItem(item);
    if (!pi) return false;
    // 0x388f7: WORD[+0x42] - WORD[+0x4c] >= UPOP  (free population)
    const int freePop = int(camp.planetAt(star).pop) - camp.usedPopFor(star);
    if (freePop < pi->upop) return false;
    return true;
}

std::optional<int> projectRowFor(Pt p, int first) {
    if (!inRect(kProjectListRect, p)) return std::nullopt;
    const int rel = p.y - (kProjectListRect.y0 + 2);  // 2 px inner padding
    if (rel < 0) return std::nullopt;
    const int i = rel / kProjectRowPitch;
    if (i < 0 || i >= kProjectVisibleRows) return std::nullopt;
    return first + i;
}

}  // namespace ascend::ui
