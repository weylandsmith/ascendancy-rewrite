// PLANETALLOC window composition law — see planetwin.h for the citations.
// Pure data + lookup; no SDL (compiled into run_tests directly, hudlayout.cpp
// / poppanel.cpp precedent). Working notes: docs/re/_wip_t276.md.
#include "ui/planetwin.h"

#include <cstdio>

namespace ascend::ui {

// windows.txt verbatim (lines cited in planetwin.h / _wip_t276.md S1).
// Order == enum order == file order == left-to-right (disjoint X-bands with
// a uniform 9 px gutter starting at x=7).
const PlanetPanelInfo kPlanetPanels[kPlanetPanelCount] = {
    /* {{  X0,  Y0,   X1,   Y1 }, msg, p1, help } */
    {{  7,   7,  114, 106}, 50, 0, "plres"},    // PLRES   line 1536
    {{123,   7,  230, 106}, 50, 1, "plind"},    // PLIND   line 1553
    {{239,   7,  346, 106}, 50, 2, "plpro"},    // PLPRO   line 1570
    {{355,   7,  454, 106}, 50, 4, "plpop"},    // PLPOP   line 1587
    {{463,   8,  632, 106}, 51, 1, "plbuild"},  // PLBUILD line 1604 (Y0 8!)
};

std::optional<PlanetPanel> planetPanelFor(Pt p) {
    // Disjoint rects -> at most one hit; no z-order question (unlike the
    // hudlayout rail). PLANLIST/PLSQUARE are deliberately not consulted:
    // they are list-mode children, not TYPE-29 paint panels.
    for (int i = 0; i < kPlanetPanelCount; ++i)
        if (inRect(kPlanetPanels[i].rect, p))
            return static_cast<PlanetPanel>(i);
    return std::nullopt;
}

int paintKey(int sendMessage, int sendParam1) {
    // Dispatch 0x3cc15..0x3cca6 verbatim (planets-ui.md S2): start from the
    // SENDPARAM1-slot byte, apply remap 4->3, then the SENDMESSAGE==51 -> 4
    // override, then range-check against the five verified case bodies.
    int key = sendParam1;
    if (key == 4) key = 3;                 // 0x3cc1c: PLPOP param
    if (sendMessage == 51) key = 4;        // 0x3cc29: PLBUILD (msg 0x33)
    return (key >= 0 && key <= 4) ? key : -1;  // else default 0x3d1bc
}

int paintKeyFor(PlanetPanel p) {
    const int i = static_cast<int>(p);
    const PlanetPanelInfo& w = kPlanetPanels[i >= 0 && i < kPlanetPanelCount
                                                ? i : kPlanetPanelCount - 1];
    return paintKey(w.sendMessage, w.sendParam1);
}

const char* pluralSuffix(int n) {
    // [inferred] singular-iff-==1 with the vendor generic pair #28/#29 —
    // see header block for the evidence boundary.
    return n == 1 ? kPluralNone : kPluralS;
}

std::string formatPlanetHeader(const std::string& owner, int planets,
                               int systems) {
    char buf[512];
    std::snprintf(buf, sizeof(buf), kFmtPlanetsOccupied, owner.c_str(),
                  planets, pluralSuffix(planets), systems,
                  pluralSuffix(systems));
    return std::string(buf);
}

std::string formatShipHeader(const std::string& owner, int ships,
                             int moreAllowed) {
    char buf[512];
    std::snprintf(buf, sizeof(buf), kFmtShips, owner.c_str(), ships,
                  pluralSuffix(ships), moreAllowed);
    return std::string(buf);
}

std::string constructionText(const std::string& planetName) {
    char buf[512];
    std::snprintf(buf, sizeof(buf), kStrUnderConstruction, planetName.c_str());
    return std::string(buf);
}

std::string refitText(const std::string& planetName) {
    char buf[512];
    std::snprintf(buf, sizeof(buf), kStrBeingRefitted, planetName.c_str());
    return std::string(buf);
}

std::string movingToPlanetText() { return std::string(kStrMovingToPlanet); }
std::string movingToStarlaneText() { return std::string(kStrMovingToStarlane); }

PlanetGauges planetGaugesFor(const ascend::game::Campaign& camp, int star) {
    // S3 table: PLRES <- +0x46 RES, PLIND <- +0x44 IND (pow-0.75 ladder),
    // PLPRO <- +0x48 PROS (identity). channelWordsFor is the cited triple.
    const auto w = camp.channelWordsFor(star);
    return {gaugeSelector(w.res), gaugeSelector(w.ind), prosSelector(w.pros)};
}

std::optional<PlBuildIcon> plbuildIcon(int itemIdx) {
    // planitem.shp: 40 records (shp.md S23.3). Identity record-index ==
    // itemIdx is CITED for 34 -> k34 only (shp.md S23.4, live MAD 1.5);
    // extended [inferred] over the domain. Out-of-domain -> no icon rather
    // than fabricate one.
    if (itemIdx < 0 || itemIdx >= 40) return std::nullopt;
    return PlBuildIcon{"data\\planitem.shp", itemIdx};
}

}  // namespace ascend::ui
