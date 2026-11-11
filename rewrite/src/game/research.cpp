// SPDX-License-Identifier: GPL-3.0-or-later

#include "game/research.h"
#include "game/starstat.h"  // cp437ToUtf8

#include <algorithm>
#include <cctype>
#include <fstream>
#include <sstream>
#include <unordered_set>

namespace ascend::game {
namespace {

constexpr int kTerminator = 255;

std::vector<std::string> splitWs(const std::string& s) {
    std::vector<std::string> out;
    std::istringstream ws(s);
    std::string t;
    while (ws >> t) out.push_back(t);
    return out;
}

bool allUpper(const std::string& name) {
    // A name is a "variant" row iff every LETTER is uppercase (research.md §4:
    // the vendor marks the 40 variant techs in ALL-CAPS). Digits/^-joined
    // segments do not decide it.
    bool anyLetter = false;
    for (unsigned char c : name) {
        if (std::isalpha(c)) {
            anyLetter = true;
            if (!std::isupper(c)) return false;
        }
    }
    return anyLetter;
}

}  // namespace

ResearchTree ResearchTree::loadFromFile(const std::string& path, std::string& errOut) {
    ResearchTree tree;
    std::ifstream f(path, std::ios::binary);
    if (!f) {
        errOut = "cannot open " + path;
        return {};
    }
    // Read the whole file, then split on CR/LF honouring the 0x1A EOF marker
    // (research.md §1: the marker terminates the LAST row mid-line, so it must
    // cut the stream, not merely be trimmed off a line).
    std::stringstream ss;
    ss << f.rdbuf();
    std::string raw = ss.str();
    const size_t mark = raw.find('\x1A');
    if (mark != std::string::npos) raw.resize(mark);

    std::vector<std::string> lines;
    size_t pos = 0;
    while (pos <= raw.size()) {
        size_t nl = raw.find_first_of("\r\n", pos);
        if (nl == std::string::npos) {
            lines.push_back(raw.substr(pos));
            break;
        }
        lines.push_back(raw.substr(pos, nl - pos));
        // consume a CRLF pair as one break
        if (raw[nl] == '\r' && nl + 1 < raw.size() && raw[nl + 1] == '\n') ++nl;
        pos = nl + 1;
    }
    if (lines.empty()) {
        errOut = "restree: empty file";
        return {};
    }
    // Line 1 = declared MAIN-tree count (research.md §1).
    auto head = splitWs(lines[0]);
    if (head.size() != 1) {
        errOut = "restree: count line must be a single integer: " + lines[0];
        return {};
    }
    char* endp = nullptr;
    const long declared = std::strtol(head[0].c_str(), &endp, 10);
    if (!endp || *endp != '\0' || declared <= 0) {
        errOut = "restree: bad count line: " + lines[0];
        return {};
    }

    for (size_t i = 1; i < lines.size(); ++i) {
        auto toks = splitWs(lines[i]);
        if (toks.empty()) continue;
        if (toks.size() < 3) {
            errOut = "restree: row " + std::to_string(i) + " has <3 fields: " + lines[i];
            return {};
        }
        if (toks.back() != std::to_string(kTerminator)) {
            errOut = "restree: row " + std::to_string(i) + " lacks 255 terminator: " + lines[i];
            return {};
        }
        Tech t;
        // '^' is a display word-joiner (research.md §1).
        std::string nm = toks[0];
        std::replace(nm.begin(), nm.end(), '^', ' ');
        t.name = cp437ToUtf8(nm);
        std::vector<long> nums;
        nums.reserve(toks.size() - 1);
        for (size_t k = 1; k + 1 < toks.size(); ++k) {
            char* e2 = nullptr;
            const long v = std::strtol(toks[k].c_str(), &e2, 10);
            if (!e2 || *e2 != '\0') {
                errOut = "restree: row " + std::to_string(i) + " non-numeric field '" + toks[k] + "'";
                return {};
            }
            nums.push_back(v);
        }
        if (nums.size() < 2) {  // flag + cost
            errOut = "restree: row " + std::to_string(i) + " missing flag/cost";
            return {};
        }
        t.flag = static_cast<int>(nums[0]);
        t.cost = static_cast<int>(nums[1]);
        for (size_t k = 2; k < nums.size(); ++k)
            t.prereqs.push_back(static_cast<int>(nums[k]));
        t.variant = allUpper(toks[0]);
        // 0-based FILE row index: the original's cost multiplier is keyed to
        // this, not to any later-filtered index (FUN_00046870 loops the
        // count-line rows in file order; docs/re/research.md §7).
        t.setRow(static_cast<int>(tree.techs_.size()));
        tree.techs_.push_back(std::move(t));
    }

    // Split off the main block: the first `declared` rows, which research.md
    // §4 verifies are exactly the non-variant rows.
    if (static_cast<long>(tree.techs_.size()) < declared) {
        errOut = "restree: only " + std::to_string(tree.techs_.size()) +
                 " rows for declared count " + std::to_string(declared);
        return {};
    }
    for (size_t i = 0; i < tree.techs_.size(); ++i) {
        if (static_cast<long>(i) < declared) {
            if (tree.techs_[i].variant) {
                errOut = "restree: main row " + std::to_string(i) +
                         " has an ALL-CAPS name (block boundary moved?)";
                return {};
            }
            tree.mainIdx_.push_back(static_cast<int>(i));
        } else {
            if (!tree.techs_[i].variant) {
                errOut = "restree: row " + std::to_string(i) +
                         " past the declared count has a Mixed-case name";
                return {};
            }
        }
    }
    // Main rows carry flag 0 (research.md §1).
    for (int idx : tree.mainIdx_)
        if (tree.techs_[idx].flag != 0) {
            errOut = "restree: main row " + std::to_string(idx) + " has flag " +
                     std::to_string(tree.techs_[idx].flag);
            return {};
        }
    // Variant rows must not gate on other variants (research.md §4).
    for (size_t i = declared; i < tree.techs_.size(); ++i)
        for (int p : tree.techs_[i].prereqs)
            if (p < 0 || p >= static_cast<int>(declared)) {
                errOut = "restree: variant row " + std::to_string(i) +
                         " references non-main row " + std::to_string(p);
                return {};
            }
    if (!tree.wellFormed(errOut)) return {};
    errOut.clear();
    return tree;
}

bool ResearchTree::wellFormed(std::string& errOut) const {
    const int n = static_cast<int>(techs_.size());
    for (int i = 0; i < n; ++i) {
        if (techs_[i].cost <= 0) {
            errOut = "restree: tech " + std::to_string(i) + " cost " +
                     std::to_string(techs_[i].cost) + " is not positive";
            return false;
        }
        for (int p : techs_[i].prereqs) {
            if (p < 0 || p >= n) {
                errOut = "restree: tech " + std::to_string(i) + " prereq " +
                         std::to_string(p) + " out of range";
                return false;
            }
            if (p == i) {
                errOut = "restree: tech " + std::to_string(i) + " is its own prereq";
                return false;
            }
        }
    }
    // Kahn over the WHOLE graph. Prereqs may point forward in file order
    // (research.md §2 measured 3 forward edges), so this is a graph test, not
    // a "is file order topological" test.
    std::vector<int> indeg(n, 0);
    std::vector<std::vector<int>> adj(n);
    for (int i = 0; i < n; ++i) {
        std::unordered_set<int> uniq(techs_[i].prereqs.begin(), techs_[i].prereqs.end());
        indeg[i] = static_cast<int>(uniq.size());
        for (int q : uniq) adj[q].push_back(i);
    }
    std::vector<int> stack;
    for (int i = 0; i < n; ++i)
        if (indeg[i] == 0) stack.push_back(i);
    int seen = 0;
    while (!stack.empty()) {
        const int i = stack.back();
        stack.pop_back();
        ++seen;
        for (int j : adj[i])
            if (--indeg[j] == 0) stack.push_back(j);
    }
    if (seen != n) {
        errOut = "restree: prerequisite graph has a cycle (ordered " +
                 std::to_string(seen) + "/" + std::to_string(n) + ")";
        return false;
    }
    return true;
}

std::vector<int> ResearchTree::available(const std::vector<bool>& owned,
                                         bool includeVariants) const {
    std::vector<int> out;
    const int n = static_cast<int>(techs_.size());
    for (int i = 0; i < n; ++i) {
        if (techs_[i].variant && !includeVariants) continue;
        if (i < static_cast<int>(owned.size()) && owned[i]) continue;
        bool ready = true;
        for (int p : techs_[i].prereqs) {
            const bool have = p < static_cast<int>(owned.size()) && owned[p];
            if (!have) {
                ready = false;
                break;
            }
        }
        if (ready) out.push_back(i);
    }
    return out;
}

}  // namespace ascend::game
