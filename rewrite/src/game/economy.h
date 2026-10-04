#pragma once
// Ship devices ("gizmos") and planetary items.
// Grammar + measured invariants: docs/re/gizmos.md, docs/re/economy.md.
// REQUIRES/ResReq fields index ResearchTree::all() rows (docs/re/research.md).

#include <cstdint>
#include <string>
#include <vector>

namespace ascend::game {

// docs/re/gizmos.md §1 (vendor-documented categories)
enum class GizmoCat : int { Weapon = 0, Shield = 1, Drive = 2, Scanner = 3,
                            Generator = 4, Special = 5 };

struct Gizmo {
    std::string name;
    GizmoCat cat = GizmoCat::Special;
    int power = 0;      // op cost; generators: power supplied
    int range = 0;      // weapons/scanners: max range
    int level = 0;      // damage / shield strength / scan-per-turn / drive dist
    int numUses = 0;    // per turn, 0 = unlimited
    int industry = 0;   // industry added to the ship build cost
    int special1 = 0;   // vendor: "for future use"
    int special2 = 0;   // vendor: "for future use"
    int resReq = 255;   // restree row index or 255
    int flags = 0;      // bitset from flag_list bit POSITIONS (gizmos.md §1)
};

struct PlanetItem {
    std::string name;
    int ind = 0, res = 0, pros = 0;  // IND/RES/PROS columns (economy.md §1)
    int mpop = 0, upop = 0;          // MPOP/UPOP columns (units undocumented)
    int cost = 0;
    int requires = 255;              // raw REQUIRES byte; see requiresValidTech
    int flags = 0;                   // raw bitset; planitem flag MEANINGS are
                                     // vendor-undocumented (OQ-014)
};

// REQUIRES/ResReq semantics (docs/re/economy.md §1): a restree row index, or
// sentinel. Vendor comment says 255 = "no research required"; exactly one
// shipped row (Interstellar Trucking) carries 254, an undocumented second
// sentinel (OQ-014). Anything not a valid tech index must be treated as
// UNGATED by the game layer until R1 settles 254 — asserting it as a tech
// requirement would silently brick one item.
inline bool requiresValidTech(int req, int techCount) {
    return req >= 0 && req < techCount;
}

// Strict loaders (reject on any invariant violation, errOut set). The 255
// terminator is SHARED with the flag list — the last value is always 255 and
// is NOT a flag bit (economy.md §1 / gizmos.md §1; this is the parse trap
// that silently shifts fields if you split on 255).
std::vector<Gizmo> loadGizmos(const std::string& path, std::string& errOut);
std::vector<PlanetItem> loadPlanItems(const std::string& path, std::string& errOut);

// Convenience views used by ship design / production (pinned by tests).
inline bool gatedBy(int req) { return req != 255; }
std::vector<int> gizmosByCategory(const std::vector<Gizmo>& gz, GizmoCat cat);
// Max travel distance among owned drives (sugar-cube units, gizmos.md §1).
int bestDriveRange(const std::vector<Gizmo>& gz, const std::vector<bool>& owned);

}  // namespace ascend::game
