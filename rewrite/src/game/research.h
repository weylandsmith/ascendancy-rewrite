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
    int cost = 0;          // field1, research points (research.md §3)
    std::vector<int> prereqs;  // field[2:-1], indices into ResearchTree::all()
    bool variant = false;  // true for the 40 ALL-CAPS rows (research.md §4)
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
    // owned. 'owned' is indexed by Tech index. includeVariants implements the
    // OQ-013 default (single-player run sees the full superset tree).
    std::vector<int> available(const std::vector<bool>& owned,
                               bool includeVariants = true) const;

    // true iff every prereq of every tech resolves and the graph is acyclic.
    bool wellFormed(std::string& errOut) const;

private:
    std::vector<Tech> techs_;
    std::vector<int> mainIdx_;
};

}  // namespace ascend::game
