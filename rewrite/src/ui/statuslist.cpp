// SPDX-License-Identifier: GPL-3.0-or-later

// t402 PLANETS LIST row-assembly law — see statuslist.h for the citations.
// Pure data + string math (no SDL), compiled into run_tests directly
// (planetwin.cpp precedent). Working notes: docs/re/_wip_t402.md.
#include "ui/statuslist.h"

#include <algorithm>
#include <cstdio>

namespace ascend::ui {

// static.txt #41-45 and #46-56 verbatim; slot order verified == runtime
// table order by the content-anchor census (r402_sizetype_census.py PASS).
static const char* kSizeWords[5] = {"Tiny", "Small", "Medium", "Large",
                                    "Enormous"};
static const char* kTypeWords[11] = {"Husk",      "Primordial", "Congenial",
                                     "Eden",      "Mineral",    "Supermineral",
                                     "Chapel",    "Cathedral",  "Special",
                                     "Tycoon",    "Cornucopia"};

const char* statusSizeWord(int sizeIdx) {
    return (sizeIdx >= 0 && sizeIdx < 5) ? kSizeWords[sizeIdx] : nullptr;
}
const char* statusTypeWord(int typeIdx) {
    return (typeIdx >= 0 && typeIdx < 11) ? kTypeWords[typeIdx] : nullptr;
}

std::string statusLine1(const std::string& name, int sizeIdx, int typeIdx,
                        bool selfManaged) {
    // 0x5077f: name replaced by #137 when the self-managed word is -1.
    const std::string shown = selfManaged ? std::string("Self-Managed") : name;
    const char* sw = statusSizeWord(sizeIdx);
    const char* tw = statusTypeWord(typeIdx);
    if (!sw || !tw) return shown;  // refuse-not-crash; no fabricated word
    char buf[256];
    // #136 verbatim "(%s %s Planet)"; the witness shows name + " " + form.
    std::snprintf(buf, sizeof(buf), "%s (%s %s Planet)", shown.c_str(), sw,
                  tw);
    return std::string(buf);
}

std::string statusLine2(const std::string& itemName, int days,
                        bool skipProgress) {
    // Suffix per 0x50809..0x50876; skipProgress = item flags bit 2 (0x507fc).
    std::string suffix;
    if (!skipProgress) {
        if (days < 0) {  // 0xffff sentinel leg
            suffix = " - No Progress";  // #138 verbatim
        } else {
            // #139 " - %d day%s until completion", pair #28/#29 (CITED at
            // 0x5084e/0x50855: singular iff days == 1).
            char buf[64];
            std::snprintf(buf, sizeof(buf), " - %d day%s until completion",
                          days, days == 1 ? "" : "s");
            suffix = buf;
        }
    }
    char buf[256];  // #140 "Building %s%s"
    std::snprintf(buf, sizeof(buf), "Building %s%s", itemName.c_str(),
                  suffix.c_str());
    return std::string(buf);
}

std::string statusLine2NoProject(bool noFreePopulation) {
    // #141 "No Project"; #142 "   (No Free Population)" THREE leading
    // spaces byte-exact, appended iff pop == used (0x508da cmp).
    return noFreePopulation ? std::string("No Project   (No Free Population)")
                            : std::string("No Project");
}

int statusDays(int cost, int acc, int ind) {
    // FUN_0x47010 verbatim shape: ind <= 0 -> 0xffff sentinel; else
    // (cost-acc-1)/ind + 1. The Automation x3 leg (FUN_0x394d8 0x39545) is
    // NOT modelled (named seam: needs the +0x52 slot-word equality state).
    if (ind <= 0) return -1;
    const int d = (cost - acc - 1) / ind + 1;
    return d < 0 ? 0 : d;  // labelled clamp (vendor returns <=0 pre-reset)
}

std::vector<StatusRowKey> statusPlanets(const ascend::game::Campaign& camp,
                                        int owner) {
    // t249 MEMBERSHIP LAW: exactly the planets whose owner == the player
    // race. The rewrite models one planet per star (campaign.h planets_ per
    // star); ownership is star-level (starOwner), so a player star
    // contributes its planets[] names exactly like the vendor list.
    std::vector<StatusRowKey> out;
    const auto& g = camp.galaxy();
    for (const auto& s : g.stars) {
        if (camp.starOwner(s.id) != owner) continue;
        for (const auto& p : s.planets)
            out.push_back({s.id, p.index});
    }
    std::sort(out.begin(), out.end(), [](const StatusRowKey& a,
                                         const StatusRowKey& b) {
        return a.star != b.star ? a.star < b.star : a.planetIndex < b.planetIndex;
    });
    return out;
}

std::vector<StatusRowKey> statusWindow(const std::vector<StatusRowKey>& all,
                                       int scroll) {
    const int maxScroll =
        std::max(0, static_cast<int>(all.size()) - kStatusVisibleRows);
    const int s = std::clamp(scroll, 0, maxScroll);
    const int n = std::min<int>(kStatusVisibleRows,
                                static_cast<int>(all.size()) - s);
    return std::vector<StatusRowKey>(all.begin() + s, all.begin() + s + n);
}

namespace {
inline bool inR(const ascend::ui::Rect& r, ascend::ui::Pt p) {
    return p.x >= r.x0 && p.x <= r.x1 && p.y >= r.y0 && p.y <= r.y1;
}
}  // namespace

// t405 UNIFIED HIT-MAP. Precedence: arrow boxes (painted over the list in
// the vendor backdrop) -> scroll column (inert; a trough/thumb click must
// NOT scroll or select — the old port let the row band swallow x 566..632)
// -> row bands. Points outside the list interior hit nothing.
StatusHitResult statusHitFor(Pt p, int topY) {
    StatusHitResult h;
    if (inR(kStatusArrowUp, p)) { h.kind = StatusHit::ArrowUp; return h; }
    if (inR(kStatusArrowDown, p)) { h.kind = StatusHit::ArrowDown; return h; }
    if (inR(kStatusScrollCol, p)) return h;  // None: trough/thumb seam
    if (const auto i = statusRowAt(p, topY)) {
        // Rows live inside the table: left frame x 7, right of the scrollbar
        // column boundary x 619 (vendor table verticals end at 619/621).
        if (p.x >= kStatusInterior.x0 && p.x < kStatusScrollCol.x0) {
            h.kind = StatusHit::Row;
            h.row = *i;
        }
    }
    return h;
}

std::optional<int> statusRowAt(Pt p, int topY) {
    if (p.y < topY) return std::nullopt;
    const int i = (p.y - topY) / kStatusRowPitch;
    if (i < 0 || i >= kStatusVisibleRows) return std::nullopt;
    return i;
}

StatusHeader statusHeaderFor(const ascend::game::Campaign& camp, int owner) {
    // PLANETS: count owned planets at call time (the vendor freezes the
    // number per screen OPEN, t249; the port recomputes per frame — named
    // seam, same value at open). SYSTEMS: sole-owner stars (FUN_00051684
    // loop; the rewrite's owner_ is a single id, so sole == owned).
    StatusHeader h{0, 0};
    const auto& g = camp.galaxy();
    for (const auto& s : g.stars) {
        if (camp.starOwner(s.id) != owner) continue;
        ++h.systems;
        h.planets += static_cast<int>(s.planets.size());
    }
    return h;
}

}  // namespace ascend::ui
