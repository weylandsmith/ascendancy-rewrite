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
    int requires = 255;              // raw REQUIRES byte; see requiresAvailable
    int flags = 0;                   // bitset; bit meanings MEASURED (economy.md §4)
};

// REQUIRES semantics MEASURED from the original loader FUN_00037fc0 and its
// availability checker FUN_0003830c (docs/re/economy.md §4):
//   item available  <=>  req == 255 (sentinel)
//                        || (req < techCount && ownedTech[req])
// exactly one shipped row (Interstellar Trucking) carries 254, which is NOT
// 255 and NOT < 66, so the original gates it OFF permanently. 254 is a dead
// item, not a second "no research" sentinel.
inline bool requiresAvailable(int req, int techCount, const std::vector<bool>& owned) {
    if (req == 255) return true;
    return req >= 0 && req < techCount && owned[req];
}
// Raw structural test (was the gate predicate before OQ-014 closed): true iff
// req names a real restree row. Kept for gizmo sites; the planitem gate must
// use requiresAvailable, NOT this + owned (that composition lets 254 through).
inline bool requiresValidTech(int req, int techCount) {
    return req >= 0 && req < techCount;
}

// MEASURED placement/size laws (loader FUN_00037fc0 + checker FUN_0003830c +
// init FUN_00037d80; docs/re/economy.md §4). The count triple "39 22 9": 39
// items total (asserted == record count at 0x38115), 22 SURFACE items (global
// 0x73e3c == 22 in 4/4 captures; drives the XOR placement law at
// FUN_0003830c:0x384db — invalid iff (slot < surfaceCells) XOR (item < 22);
// the checker bound DL<=0x1e EXEMPTS the 8 specials), 9 ORBITAL items
// (global 0x73e3e == 9; file rows 22..30), rows 31..38 specials.
constexpr int kPlanitemSurfaceCount = 22;
constexpr int kPlanitemOrbitalCount = 9;
inline bool itemIsSurface(int itemIndex) { return itemIndex < kPlanitemSurfaceCount; }
// Surface/orbital slot law: surface slots are [0, surfaceCells), orbital
// slots [surfaceCells, surfaceCells+10) (FUN_00037d80: cap = cells + 10,
// RAM-verified 2650/2650 planet records). Specials are exempt (checker
// applies the XOR rule only for item index <= 30).
inline bool itemSlotAllows(int itemIndex, int cell, int surfaceCells) {
    if (itemIndex < 0 || cell < 0) return false;
    if (itemIndex >= kPlanitemSurfaceCount + kPlanitemOrbitalCount) return true;
    return (cell < surfaceCells) == itemIsSurface(itemIndex);
}
// Surface cell count per planet SIZE class 0..4: SUM of planitem.txt grid C
// row (the count grid at guest-phys 0x744a8). FUN_00037d80 accumulates the
// row into +0x18 (assert <=100); live +0x18 == {7,11,23,45,73} on 2650/2650
// records across 17 captures, exactly the grid-C row sums.
inline int planetSurfaceCells(int sizeClass) {
    static const int kCells[5] = {7, 11, 23, 45, 73};
    return (sizeClass >= 0 && sizeClass < 5) ? kCells[sizeClass] : 0;
}

// Strict loaders (reject on any invariant violation, errOut set). The 255
// terminator is SHARED with the flag list — the last value is always 255 and
// is NOT a flag bit (economy.md §1 / gizmos.md §1; this is the parse trap
// that silently shifts fields if you split on 255).
std::vector<Gizmo> loadGizmos(const std::string& path, std::string& errOut);
std::vector<PlanetItem> loadPlanItems(const std::string& path, std::string& errOut);

// Convenience views used by ship design / production (pinned by tests).
// (gatedBy() removed when OQ-014 closed: `req != 255` alone was the wrong
// predicate — 254 must NOT pass. Use requiresAvailable().)
std::vector<int> gizmosByCategory(const std::vector<Gizmo>& gz, GizmoCat cat);
// Max travel distance among owned drives (sugar-cube units, gizmos.md §1).
int bestDriveRange(const std::vector<Gizmo>& gz, const std::vector<bool>& owned);

}  // namespace ascend::game
