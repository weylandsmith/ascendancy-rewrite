#pragma once
// Research tree loader + availability queries.
// Grammar and field roles: docs/re/research.md §1-§2 (from
// scripts/restree_probe.py). Variant-block semantics: §4 and OQ-013.

#include <cstdint>
#include <string>
#include <vector>

namespace ascend::game {

struct Tech {
    std::string name;      // CP437-decoded, '^' replaced by ' '
    int flag = 0;          // field0; always 0 on main rows (research.md §1)
    int cost = 0;          // field1, FILE cost (research.md §3). Gameplay does
                           // NOT charge this: see runtimeCost() (research.md §7).
    std::vector<int> prereqs;  // field[2:-1], indices into ResearchTree::all()
    bool variant = false;  // true for the 40 ALL-CAPS rows (research.md §4)

    // MEASURED RUNTIME COST LAW (research.md §7; loader FUN_00046870 at
    // work/ascend_restored.bin:00046870 — iVar4 starts -20, +=2 per row, and
    // cost *= iVar4 once row index > 10, clamped to 65000). Verified against
    // live RAM: 66/66 rows in 27 slots across 13 captures, and the vendor
    // resume.gam persists the scaled value at record +62. Example: row 65
    // (Illusory Machinations) file cost 300 -> charged 33000.
    // 'row' is the 0-based FILE row index (== all() index; the original loads
    // only rows 0..count-1 in file order).
    static int runtimeCost(int fileCost, int row) {
        if (row <= 10) return fileCost;
        long long v = static_cast<long long>(fileCost) * (2 * row - 20);
        if (v > 65000) v = 65000;
        return static_cast<int>(v);
    }
    int runtimeCost() const { return runtimeCost(cost, row_); }

    void setRow(int row) { row_ = row; }

private:
    int row_ = 0;  // 0-based file row, set by the loader
};

class ResearchTree {
public:
    // Strict loader: rejects a count line that does not match the number of
    // main rows, non-positive costs, out-of-range or self prerequisites,
    // variant rows that reference other variants, and cycles. Prerequisites
    // may point FORWARD in file order (research.md §2), so validation runs
    // after the full parse.
    static ResearchTree loadFromFile(const std::string& path, std::string& errOut);

    const std::vector<Tech>& all() const { return techs_; }
    const std::vector<int>& mainIndices() const { return mainIdx_; }
    int mainCount() const { return static_cast<int>(mainIdx_.size()); }

    // A tech is available when it is not owned and every prerequisite is
    // owned. 'owned' is indexed by Tech index. includeVariants defaults to
    // FALSE: OQ-013 CLOSED (research.md §7) — the original's loader
    // FUN_00046870 parses only the count-line rows (66 main), so the 40
    // ALL-CAPS variant rows never enter the live table (0/40 names in RAM
    // across 27 slots x 13 captures; absent from resume.gam's table too).
    std::vector<int> available(const std::vector<bool>& owned,
                               bool includeVariants = false) const;

    // true iff every prereq of every tech resolves and the graph is acyclic.
    bool wellFormed(std::string& errOut) const;

private:
    std::vector<Tech> techs_;
    std::vector<int> mainIdx_;
};

}  // namespace ascend::game
