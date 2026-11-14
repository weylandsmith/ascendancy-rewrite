// SPDX-License-Identifier: GPL-3.0-or-later

#include "game/economy.h"
#include "game/starstat.h"

#include <algorithm>
#include <cctype>
#include <fstream>
#include <sstream>
#include <unordered_set>

namespace ascend::game {
namespace {

constexpr int kTerm = 255;

// Shared text-file preamble: whole-file read, 0x1A cuts mid-line, CR/LF split.
bool readTextLines(const std::string& path, std::vector<std::string>& out,
                   std::string& err) {
    std::ifstream f(path, std::ios::binary);
    if (!f) {
        err = "cannot open " + path;
        return false;
    }
    std::stringstream ss;
    ss << f.rdbuf();
    std::string raw = ss.str();
    const size_t mark = raw.find('\x1A');
    if (mark != std::string::npos) raw.resize(mark);
    size_t pos = 0;
    while (pos <= raw.size()) {
        size_t nl = raw.find_first_of("\r\n", pos);
        if (nl == std::string::npos) {
            out.push_back(raw.substr(pos));
            break;
        }
        out.push_back(raw.substr(pos, nl - pos));
        if (raw[nl] == '\r' && nl + 1 < raw.size() && raw[nl + 1] == '\n') ++nl;
        pos = nl + 1;
    }
    err.clear();
    return true;
}

bool isNumericRow(const std::string& s) {
    bool any = false;
    for (char c : s) {
        if (c == ' ' || c == '\t') continue;
        if (!std::isdigit(static_cast<unsigned char>(c))) return false;
        any = true;
    }
    return any;
}

std::vector<int> parseInts(const std::string& s) {
    std::vector<int> v;
    std::istringstream ws(s);
    int x;
    while (ws >> x) v.push_back(x);
    return v;
}

// Collect (name, numbers) pairs starting after the file's '#' data marker.
bool nameNumRecords(const std::vector<std::string>& lines, size_t from,
                    std::vector<std::pair<std::string, std::vector<int>>>& out) {
    std::string name;
    bool have = false;
    for (size_t i = from; i < lines.size(); ++i) {
        const std::string s = lines[i];
        // strip trailing spaces for the numeric test
        size_t e = s.find_last_not_of(" \t");
        const std::string t = e == std::string::npos ? "" : s.substr(0, e + 1);
        if (t.empty()) continue;
        if (isNumericRow(t)) {
            if (!have) return false;  // numeric row with no preceding name
            out.push_back({name, parseInts(t)});
            have = false;
        } else {
            if (have) return false;   // two names in a row
            name = t;
            have = true;
        }
    }
    if (have) return false;  // dangling trailing name
    return true;
}

int markerIndex(const std::vector<std::string>& lines, const std::string& want) {
    for (size_t i = 0; i < lines.size(); ++i) {
        std::string t = lines[i];
        size_t a = t.find_first_not_of(" \t");
        if (a != std::string::npos) t = t.substr(a);
        size_t b = t.find_last_not_of(" \t");
        if (b != std::string::npos) t = t.substr(0, b + 1);
        if (t == want) return static_cast<int>(i);
    }
    return -1;
}

// flag_list values are BIT POSITIONS (docs/re/gizmos.md §1).
int packFlags(const std::vector<int>& positions, std::string& err,
              const std::string& ctx) {
    int bits = 0;
    for (int p : positions) {
        if (p < 0 || p > 30) {
            err = ctx + ": flag bit position " + std::to_string(p) + " out of range";
            return -1;
        }
        bits |= (1 << p);
    }
    return bits;
}

}  // namespace

std::vector<Gizmo> loadGizmos(const std::string& path, std::string& errOut) {
    std::vector<std::string> lines;
    if (!readTextLines(path, lines, errOut)) return {};
    const int hash = markerIndex(lines, "#");
    if (hash < 0) {
        errOut = "gizmos: no '#' data marker";
        return {};
    }
    std::vector<std::pair<std::string, std::vector<int>>> recs;
    if (!nameNumRecords(lines, hash + 1, recs)) {
        errOut = "gizmos: name/number rows misaligned";
        return {};
    }
    // Invariants from docs/re/gizmos.md §2 (measured on the shipped file).
    if (recs.size() != 76) {
        errOut = "gizmos: expected 76 records, got " + std::to_string(recs.size());
        return {};
    }
    std::unordered_set<std::string> seen;
    std::vector<Gizmo> out;
    for (const auto& [rawName, v] : recs) {
        if (v.size() < 10 || v.back() != kTerm) {
            errOut = "gizmos: row '" + rawName + "' malformed (n=" +
                     std::to_string(v.size()) + ")";
            return {};
        }
        Gizmo g;
        std::string nm = rawName;
        std::replace(nm.begin(), nm.end(), '^', ' ');
        g.name = cp437ToUtf8(nm);
        if (!seen.insert(g.name).second) {
            errOut = "gizmos: duplicate name " + g.name;
            return {};
        }
        if (v[0] < 0 || v[0] > 5) {
            errOut = "gizmos: bad category " + std::to_string(v[0]);
            return {};
        }
        g.cat = static_cast<GizmoCat>(v[0]);
        g.power = v[1];
        g.range = v[2];
        g.level = v[3];
        g.numUses = v[4];
        // Industry is charged AS THE FILE VALUE: image-wide +0x46 census
        // (docs/re/ships.md §9) shows the gizmo-table parse store @0x491b5
        // is the only writer of gizmo-record Industry in the shipped exe
        // (JJTTODO "cost hack" absent; zero-wipe @0x37f41 is an error-path
        // reset of fields 0x42..0x66, not an alter).
        g.industry = v[5];
        g.special1 = v[6];
        g.special2 = v[7];
        g.resReq = v[8];
        // v[9..size-2] are flag bit positions; v.back() == 255 terminator.
        std::vector<int> pos(v.begin() + 9, v.end() - 1);
        const int bits = packFlags(pos, errOut, "gizmos " + g.name);
        if (bits < 0) return {};
        g.flags = bits;
        out.push_back(std::move(g));
    }
    errOut.clear();
    return out;
}

std::vector<PlanetItem> loadPlanItems(const std::string& path, std::string& errOut) {
    std::vector<std::string> lines;
    if (!readTextLines(path, lines, errOut)) return {};
    const int hash = markerIndex(lines, "#");
    if (hash < 0) {
        errOut = "planitem: no '#' data marker";
        return {};
    }
    // The item table starts AFTER the count triple '39 22 9' (economy.md §1);
    // the grids before it belong to the planet-type tables.
    const int triple = markerIndex(lines, "39 22 9");
    if (triple < 0 || triple < hash) {
        errOut = "planitem: count triple '39 22 9' not found after '#'";
        return {};
    }
    std::vector<std::pair<std::string, std::vector<int>>> recs;
    if (!nameNumRecords(lines, triple + 1, recs)) {
        errOut = "planitem: name/number rows misaligned";
        return {};
    }
    if (recs.size() != 39) {
        errOut = "planitem: expected 39 records, got " + std::to_string(recs.size());
        return {};
    }
    std::unordered_set<std::string> seen;
    std::vector<PlanetItem> out;
    for (const auto& [rawName, v] : recs) {
        // fixed 7 + optional flag positions + 255 terminator
        if (v.size() < 8 || v.back() != kTerm) {
            errOut = "planitem: row '" + rawName + "' malformed";
            return {};
        }
        PlanetItem it;
        std::string nm = rawName;
        std::replace(nm.begin(), nm.end(), '^', ' ');
        it.name = cp437ToUtf8(nm);
        if (!seen.insert(it.name).second) {
            errOut = "planitem: duplicate name " + it.name;
            return {};
        }
        it.ind = v[0];
        it.res = v[1];
        it.pros = v[2];
        it.mpop = v[3];
        it.upop = v[4];
        it.cost = v[5];
        it.reqByte = v[6];
        std::vector<int> pos(v.begin() + 7, v.end() - 1);
        const int bits = packFlags(pos, errOut, "planitem " + it.name);
        if (bits < 0) return {};
        it.flags = bits;
        out.push_back(std::move(it));
    }
    errOut.clear();
    return out;
}

// t294 TERRAIN SOURCE-TABLE LOADER (OQ-016 residue 3). Grammar MEASURED from
// the vendor loader FUN_00037fc0 (income-law.md S10 t294 block): after the
// lone '#' line, plain integer tokens in scanner order --
//   1 scalar          -> pop-growth wrap value (DS:0x66e4 @0x3802c, vendor 50)
//   11 rows x 4       -> terrain weight rows 0x744f4 (record 0x1ce0 loop)
//   5 rows x 15       -> grid B -> 0x7445c+15i (record 0x1ce3; UNMAPPED here)
//   5 rows x 15       -> grid C -> 0x744a8+15i (record 0x1ce6); +0x18 = row sum
// Rows are read INC-then-store (all 4 weights / all 15 cells land verbatim).
// Weights must fit the u8 store law (0..255); grid C rows must sum 1..100
// (the original asserts +0x18 <= 100 @0x37dfb region, economy.md).
bool loadTerrainTables(const std::string& path, TerrainTables& out,
                       std::string& errOut) {
    std::vector<std::string> lines;
    if (!readTextLines(path, lines, errOut)) return false;
    const int hash = markerIndex(lines, "#");
    if (hash < 0) { errOut = "terrain: no '#' data marker"; return false; }
    // Token stream of pure-integer lines after '#', stopping at the first
    // non-numeric non-blank line (the item table's name/number records).
    std::vector<int> tok;
    for (size_t i = static_cast<size_t>(hash) + 1; i < lines.size(); ++i) {
        std::istringstream is(lines[i]);
        std::vector<int> row;
        int v;
        while (is >> v) row.push_back(v);
        std::string rest;
        if (row.empty()) { if (!(is >> rest)) continue; break; }
        if (is >> rest) break;  // mixed line: not part of the numeric blocks
        for (int x : row) tok.push_back(x);
    }
    const size_t need = 1 + 44 + 75 + 75;
    if (tok.size() < need) {
        errOut = "terrain: expected " + std::to_string(need) +
                 " numeric tokens after '#', got " + std::to_string(tok.size());
        return false;
    }
    if (tok[0] <= 0) { errOut = "terrain: pop-growth scalar must be > 0"; return false; }
    out.popGrowth = tok[0];
    for (int i = 0; i < 11; ++i)
        for (int j = 0; j < 4; ++j) {
            const int v = tok[1 + i * 4 + j];
            if (v < 0 || v > 255) {
                errOut = "terrain: weight row " + std::to_string(i) +
                         " value " + std::to_string(v) + " outside u8 store law";
                return false;
            }
            out.weights[i][j] = v;
        }
    // grid B (tok 45..119) intentionally unread: no rewrite consumer (0x7445c
    // window semantics unmapped -- t294 WIP).
    for (int i = 0; i < 5; ++i) {
        int sum = 0;
        for (int j = 0; j < 15; ++j) sum += tok[120 + i * 15 + j];
        if (sum < 1 || sum > 100) {
            errOut = "terrain: grid C row " + std::to_string(i) + " sums to " +
                     std::to_string(sum) + ", outside +0x18 cap 1..100";
            return false;
        }
        out.surfaceBySize[i] = sum;
    }
    errOut.clear();
    return true;
}

std::vector<int> gizmosByCategory(const std::vector<Gizmo>& gz, GizmoCat cat) {
    std::vector<int> out;
    for (size_t i = 0; i < gz.size(); ++i)
        if (gz[i].cat == cat) out.push_back(static_cast<int>(i));
    return out;
}

int bestDriveRange(const std::vector<Gizmo>& gz, const std::vector<bool>& owned) {
    int best = 0;
    for (const auto& g : gz) {
        if (g.cat != GizmoCat::Drive) continue;
        // OQ-014 law (economy.h requiresAvailable): valid row -> owned;
        // 255 -> ungated; anything else (e.g. 254) -> dead. Gizmo rows
        // measured: all carry real techs or 255, so behaviour is unchanged
        // for shipped data — the predicate is now shared with planitems.
        if (requiresAvailable(g.resReq, static_cast<int>(owned.size()), owned) &&
            g.level > best)
            best = g.level;
    }
    return best;
}

}  // namespace ascend::game
