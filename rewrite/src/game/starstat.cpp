// SPDX-License-Identifier: GPL-3.0-or-later

#include "game/starstat.h"

#include <cctype>
#include <cmath>
#include <cstdlib>
#include <fstream>
#include <sstream>

namespace ascend::game {

namespace {

// CP437 -> UTF-8 for the bytes that can actually appear. docs/re/text.md:
// ascend00 text is CP437-clean (names.txt is ASCII-only in practice, but the
// decoder keeps the invariant honest for high bytes).
std::string cp437ToUtf8Impl(const std::string& in) {
    static const char* table = nullptr;  // ASCII fast path below covers names.txt
    std::string out;
    out.reserve(in.size());
    for (unsigned char c : in) {
        if (c < 0x80) {
            out.push_back(static_cast<char>(c));
        } else {
            // Box-drawing/accents are irrelevant for star names; emit '?' so a
            // regression is loud rather than silent mojibake.
            out.push_back('?');
        }
    }
    (void)table;
    return out;
}

std::string trim(const std::string& s) {
    size_t a = 0, b = s.size();
    while (a < b && std::isspace(static_cast<unsigned char>(s[a]))) ++a;
    while (b > a && std::isspace(static_cast<unsigned char>(s[b - 1]))) --b;
    return s.substr(a, b - a);
}

}  // namespace

std::optional<StarStats> StarStats::load(const std::filesystem::path& file, std::string* err) {
    std::ifstream f(file, std::ios::binary);
    if (!f) {
        if (err) *err = "cannot open " + file.string();
        return std::nullopt;
    }
    std::stringstream ss;
    ss << f.rdbuf();
    return parse(ss.str(), err);
}

std::optional<StarStats> StarStats::parse(const std::string& text, std::string* err) {
    // Grammar [verified docs/re/mapgen.md §1]: TYPE_<n>\t<pct> Percent\t<lanes> Lanes
    StarStats st;
    std::istringstream ls(text);
    std::string line;
    while (std::getline(ls, line)) {
        line = trim(line);
        if (line.empty()) continue;
        if (line.rfind("//", 0) == 0) continue;
        // Tokenise loosely; validate strictly.
        std::istringstream ws(line);
        std::string tag, pctS, pctWord, lanesS, lanesWord;
        if (!(ws >> tag >> pctS >> pctWord >> lanesS >> lanesWord)) {
            if (err) *err = "starstat: unparsable line: " + line;
            return std::nullopt;
        }
        if (tag.rfind("TYPE_", 0) != 0) {
            if (err) *err = "starstat: bad tag: " + tag;
            return std::nullopt;
        }
        if (pctWord != "Percent" || lanesWord != "Lanes") {
            if (err) *err = "starstat: bad units in: " + line;
            return std::nullopt;
        }
        char* endp = nullptr;
        const double pct = std::strtod(pctS.c_str(), &endp);
        if (!endp || *endp != '\0') {
            if (err) *err = "starstat: bad percent: " + pctS;
            return std::nullopt;
        }
        const double lanes = std::strtod(lanesS.c_str(), &endp);
        if (!endp || *endp != '\0') {
            if (err) *err = "starstat: bad lanes: " + lanesS;
            return std::nullopt;
        }
        // Index must follow TYPE_<n> order 0..12 contiguous (measured file).
        const int idx = static_cast<int>(st.rows_.size());
        if (std::to_string(idx) != tag.substr(5)) {
            if (err) *err = "starstat: non-contiguous index at " + tag;
            return std::nullopt;
        }
        st.rows_.push_back({pct, lanes});
    }
    // Invariants [verified docs/re/mapgen.md §1].
    if (st.rows_.size() != 13) {
        if (err) *err = "starstat: expected 13 types, got " + std::to_string(st.rows_.size());
        return std::nullopt;
    }
    double sum = 0;
    for (const auto& r : st.rows_) sum += r.percent;
    if (std::fabs(sum - 100.0) > 0.02) {
        if (err) *err = "starstat: percents sum to " + std::to_string(sum) + ", not 100+-0.02";
        return std::nullopt;
    }
    if (err) err->clear();
    return st;
}

double StarStats::meanLanes() const {
    double s = 0;
    for (const auto& r : rows_) s += r.lanes;
    return rows_.empty() ? 0.0 : s / static_cast<double>(rows_.size());
}

int StarStats::pickType(double u) const {
    if (u < 0.0) u = 0.0;
    if (u >= 1.0) u = 0.9999999;
    double total = 0.0;
    for (const auto& r : rows_) total += r.percent;
    double target = u * total;  // keep the shipped 100.01 scale, ratios intact
    double acc = 0.0;
    for (size_t i = 0; i < rows_.size(); ++i) {
        acc += rows_[i].percent;
        if (target < acc) return static_cast<int>(i);
    }
    return static_cast<int>(rows_.size()) - 1;
}

std::vector<std::string> loadStarNames(const std::filesystem::path& namesTxt, std::string* err) {
    std::ifstream f(namesTxt, std::ios::binary);
    if (!f) {
        if (err) *err = "cannot open " + namesTxt.string();
        return {};
    }
    std::vector<std::string> out;
    std::string line;
    while (std::getline(f, line)) {
        // CP437 text files terminate with a 0x1A EOF marker: measured on
        // names.txt (bytes 963 = 102 CRLF lines, final line is exactly 0x1A).
        const size_t eofmark = line.find('\x1A');
        if (eofmark != std::string::npos) line = line.substr(0, eofmark);
        line = trim(line);
        if (!line.empty()) out.push_back(cp437ToUtf8Impl(line));
    }
    // [verified docs/re/mapgen.md §2]: 100 non-empty bases, first "Vega".
    // (A Python-side count of 101 earlier was an artefact: str.strip() does
    // not remove the 0x1A EOF marker, so the marker counted as a name.)
    if (out.size() != 100) {
        if (err) *err = "names.txt: expected 100 bases, got " + std::to_string(out.size());
        return {};
    }
    if (err) err->clear();
    return out;
}

std::string cp437ToUtf8(const std::string& in) { return cp437ToUtf8Impl(in); }

std::string roman(int n) {
    // docs/re/mapgen.md §3 measured I..V; table extends the standard way.
    static const int vals[] = {1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1};
    static const char* sym[] = {"M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX",
                                "V", "IV", "I"};
    std::string out;
    if (n <= 0) return out;
    for (int i = 0; i < 13 && n > 0; ++i)
        while (n >= vals[i]) {
            out += sym[i];
            n -= vals[i];
        }
    return out;
}

}  // namespace ascend::game
