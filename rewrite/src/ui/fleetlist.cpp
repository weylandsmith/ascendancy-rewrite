// SPDX-License-Identifier: GPL-3.0-or-later
// t407 FLEET LIST law implementation — see ui/fleetlist.h for the citations.
#include "ui/fleetlist.h"

#include <algorithm>

#include "ui/planetwin.h"  // formatShipHeader (#152, pinned byte-exact t276)

namespace ascend::ui {

std::vector<FleetRowKey> fleetRows(const ascend::game::Campaign& camp,
                                   int owner) {
    // Membership: every live ship record of the owner, array order (the
    // vendor sort law is UNKNOWN — ships.md correction 2 — labelled default,
    // same posture as the t402 planets order seam).
    std::vector<FleetRowKey> out;
    const auto& f = camp.fleet();
    for (size_t i = 0; i < f.size(); i++)
        if (f[i].owner == owner) out.push_back({int(i)});
    return out;
}

std::vector<FleetRowKey> fleetWindow(const std::vector<FleetRowKey>& all,
                                     int scroll) {
    const int maxScroll =
        std::max(0, int(all.size()) - kFleetVisibleRows);
    const int s = std::clamp(scroll, 0, maxScroll);
    std::vector<FleetRowKey> out;
    for (int i = s; i < int(all.size()) && i < s + kFleetVisibleRows; i++)
        out.push_back(all[i]);
    return out;
}

std::string fleetHeaderText(const ascend::game::Campaign& camp, int owner,
                            const std::string& ownerName, int ships) {
    return formatShipHeader(ownerName, ships, fleetAllowedFor(camp, owner, ships));
}

int fleetAllowedFor(const ascend::game::Campaign& camp, int owner, int ships) {
    // [inferred DEFAULT — _wip_t407 F7]. help shipdes: "the number of ships
    // you can maintain ... is proportional to the number of star systems you
    // control". The two banked witnesses ((25 ships, 12 more) at the t249
    // sole-owner count 36; (14, 13) at the t1086 header's 26 systems) both
    // fit total == systems + 1. The rewrite's owner_ is a single id, so
    // controlled == owned (same equivalence statusHeaderFor uses).
    int systems = 0;
    for (const auto& s : camp.galaxy().stars)
        if (camp.starOwner(s.id) == owner) ++systems;
    return std::max(0, systems + 1 - ships);
}

std::string fleetShipName(const ascend::game::Campaign& camp) {
    // Labelled PORT DEFAULT (header block): the campaign's expansion launch
    // spends the planitem "Ship" row (campaign.cpp shipCost law); with no
    // design model that hull row IS the display name. Lookup through the
    // PUBLIC read-only table accessors (itemId is private). Falls back to
    // "Ship" when the table is absent (never crashes, never lies with a
    // design name the model does not have).
    for (int i = 0; i < camp.planItemCount(); i++) {
        const ascend::game::PlanetItem* it = camp.planetItem(i);
        if (it && it->name == "Ship") return it->name;
    }
    return "Ship";
}

std::string fleetLaneLocation(const std::string& starName, int etaDays) {
    // #146 "In Starlane to %s System\nETA - %d Day%s" (fn 0x50d12 kind-2;
    // plural pair getter(28)""/getter(29)"s" == planetwin pluralSuffix, the
    // law cited for #139 in t402 and re-cited for #146 in _wip_t407 F5).
    // Real newline (loader-interprets law, planets-ui.md note).
    return "In Starlane to " + starName + " System\nETA - " +
           std::to_string(etaDays) + " Day" + pluralSuffix(etaDays);
}

std::string fleetOrbitLocation(const std::string& planetName) {
    return "Orbiting " + planetName;  // #143 (fn 0x50d12 kind-1, 0x50dc5)
}

FleetHitResult fleetHitFor(Pt p, int topY) {
    // Precedence (t405 law shape): arrow boxes first, scroll column inert,
    // rows own the table left of kFleetRowsRight.
    auto in = [](const Rect& r, Pt q) {
        return q.x >= r.x0 && q.x <= r.x1 && q.y >= r.y0 && q.y <= r.y1;
    };
    FleetHitResult h;
    if (in(kFleetArrowUp, p)) { h.kind = FleetHit::ArrowUp; return h; }
    if (in(kFleetArrowDown, p)) { h.kind = FleetHit::ArrowDown; return h; }
    if (in(kFleetScrollCol, p)) return h;  // trough: inert
    // STATSHIPLST interior x0 == 7 (windows.txt rect 7,46-632,472).
    if (p.x < 7 || p.x > kFleetRowsRight) return h;
    if (p.y < topY) return h;
    const int row = (p.y - topY) / kFleetRowPitch;
    if (row >= kFleetVisibleRows) return h;
    h.kind = FleetHit::Row;
    h.row = row;
    return h;
}

}  // namespace ascend::ui
