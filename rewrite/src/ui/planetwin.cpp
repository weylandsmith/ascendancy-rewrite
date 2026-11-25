// SPDX-License-Identifier: GPL-3.0-or-later

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

// ---- tPF-2d POPUP BUTTON LAW ------------------------------------------------
// Citations docs/re/_wip_tPF2d.md D2 (live registry), D3 (consumer disasm
// 0x3d591..0x3d67e + 0x3d684 single-button path), D5 (refcap pixel check).

const char* popupButtonLabel(int id) {
    // The runtime registry u32[ds:0x744a0 + id*4], MEASURED 20/20 banked
    // saves (scripts/tPF2d_label_registry.py, bank-play-20261111-t377):
    // strings Tiny..Cornucopia at ids 35..50, actions at 51..58.
    switch (id) {
        case 35: return "Tiny";        case 36: return "Small";
        case 37: return "Medium";      case 38: return "Large";
        case 39: return "Enormous";    case 40: return "Husk";
        case 41: return "Primordial";  case 42: return "Congenial";
        case 43: return "Eden";        case 44: return "Mineral";
        case 45: return "Supermineral";case 46: return "Chapel";
        case 47: return "Cathedral";   case 48: return "Special";
        case 49: return "Tycoon";      case 50: return "Cornucopia";
        case kPbCancel:       return "Cancel";
        case kPbCreateColony: return "Create Colony";
        case kPbAbandon:      return "Abandon";
        case kPbBuild:        return "Build";
        case kPbLeaveOrbit:   return "Leave Orbit";
        case kPbRefit:        return "Refit";
        case kPbInvade:       return "Invade";
        case kPbAutomate:     return "Automate";
        default: return "";
    }
}

std::vector<int> popupButtonIds(int cellItem,
                                const std::function<bool(int)>& buildable) {
    std::vector<int> ids;
    if (cellItem == 0xff) {
        // 0x3d550: loop ecx = 0..0x26 (skip 5 = Colony Base); the FIRST item
        // the checker 0x3830c(ecx, cell) passes appends 54 and the loop
        // BREAKS — 0x3d582..0x3d58e FALLS THROUGH to the tail 0x3d591 (the
        // loop-back edge 0x3d559 is only the checker-FAIL path 0x3d580).
        // tPF-2c C6's "one 54 per buildable item" is REFUTED at byte level
        // (docs/re/_wip_tPF2d.md D6). The -0x7c disp at 0x3d586 is the same
        // array as -0x78 (index+1 write style: -0x7c+(n+1)*4 == -0x78+n*4).
        for (int item = 0; item <= 0x26; ++item) {
            if (item == 5) continue;                       // 0x3d55f
            if (buildable(item)) {                         // 0x3d582
                ids.push_back(kPbBuild);
                break;
            }
        }
    } else if (cellItem != 0x17) {
        // 0x3d506 non-empty non-ship: 53 iff item != 5.
        if (cellItem != 5) ids.push_back(kPbAbandon);
        // 0x3d51d: 58 iff checker(item ARG 35 = Automation, cell).
        if (buildable(35)) ids.push_back(kPbAutomate);
    }
    // 0x3d591..0x3d5a4: every path appends 51 last.
    ids.push_back(kPbCancel);
    return ids;
}

std::vector<Rect> popupButtonRects(int n) {
    // Consumer 0x3d594..0x3d65c: cursor ebx starts 0xa0=160; per button
    // w = (0x1df - x) / remaining (idiv, 0x3d61f); rec+4 = x, rec+0xc = w,
    // y band rec+8 = 0x151 = 337, rec+0x10 = 0x16f = 367; next cursor
    // x + w + 1 clamped 0x1df (0x3d636..0x3d65c).
    std::vector<Rect> out;
    int x = 160;
    for (int i = 0; i < n; ++i) {
        const int w = (479 - x) / (n - i);
        out.push_back(Rect{x, 337, x + w, 367});
        x = std::min(x + w, 479) + 1;  // 0x3d636 clamp, 0x3d655 inc
    }
    return out;
}

const char* popupButtonText(const std::vector<int>& ids, int i) {
    // 0x3d684: if the array holds exactly ONE button, the label is REPLACED
    // by getter(30) "OK" regardless of id (the refcap non-buildable popup).
    if (ids.size() == 1) return "OK";
    return (i >= 0 && i < int(ids.size())) ? popupButtonLabel(ids[i]) : "";
}

}  // namespace ascend::ui
