// SPDX-License-Identifier: GPL-3.0-or-later
// t412 — see raceintro.h for the citations. Pure law, no SDL (the
// hudlayout.cpp/statuslaw.cpp precedent): parsed straight into run_tests.
#include "ui/raceintro.h"

#include <cctype>

namespace ascend::ui {
namespace {

std::string trim(const std::string& s) {
    const auto b = s.find_first_not_of(" \t\r\n");
    if (b == std::string::npos) return "";
    const auto e = s.find_last_not_of(" \t\r\n");
    return s.substr(b, e - b + 1);
}

// The vendor keyword table (pool 0x83d5f.., verbatim UPPERCASE). The file
// carries lowercase section words; the compare helper FUN_000775aa's case
// law is unmapped, so the port compares case-insensitively [port choice,
// decider: a capture of a file with a mixed-case keyword — none exists].
bool kwIs(const std::string& line, const char* kw) {
    if (line.size() != std::char_traits<char>::length(kw)) return false;
    for (size_t i = 0; i < line.size(); i++)
        if (std::toupper(static_cast<unsigned char>(line[i])) !=
            std::toupper(static_cast<unsigned char>(kw[i])))
            return false;
    return true;
}

std::string toUpper(std::string s) {
    for (char& c : s) c = char(std::toupper(static_cast<unsigned char>(c)));
    return s;
}

}  // namespace

HistoryRace parseHistoryRace(const std::string& fileText, int specnum,
                             std::string* errOut) {
    HistoryRace r;
    // Split on '\n' (the file is CRLF; trim() eats the '\r').
    size_t pos = 0;
    bool inBlock = false, done = false;
    std::string section;  // current open section (UPPERCASE), "" = none
    while (pos <= fileText.size() && !done) {
        size_t nl = fileText.find('\n', pos);
        const bool last = nl == std::string::npos;
        std::string line = trim(fileText.substr(pos, last ? std::string::npos
                                                          : nl - pos));
        pos = last ? fileText.size() + 1 : nl + 1;
        if (line.empty() || line.rfind("//", 0) == 0 || line.rfind("#", 0) == 0)
            continue;  // comment/blank lines (file header uses //)

        if (!inBlock) {
            // Outside a block only "SPECNUM <n>" is meaningful (verified:
            // the loader scans "%s %d" against SPECNUM until it matches).
            std::string up = toUpper(line);
            if (up.rfind("SPECNUM", 0) != 0) continue;
            std::string rest = trim(up.substr(7));
            try {
                if (specnum >= 0 && std::stoi(rest) == specnum) inBlock = true;
            } catch (...) {
            }
            continue;
        }

        // Inside the player's block: section open/close per the keyword
        // chain. Any other line appends to the open section.
        if (kwIs(line, "ENDPOWER") || kwIs(line, "ENDINTRO") ||
            kwIs(line, "ENDPEACE") || kwIs(line, "ENDNEUTRAL") ||
            kwIs(line, "ENDHOSTILE") || kwIs(line, "ENDTEXT") ||
            kwIs(line, "END")) {
            section.clear();
            if (kwIs(line, "END")) done = true;  // block terminator
            continue;
        }
        if (kwIs(line, "POWER")) { section = "POWER"; continue; }
        if (kwIs(line, "INTRO")) { section = "INTRO"; continue; }
        if (kwIs(line, "PEACE")) { section = "PEACE"; continue; }
        if (kwIs(line, "NEUTRAL")) { section = "NEUTRAL"; continue; }
        if (kwIs(line, "HOSTILE")) { section = "HOSTILE"; continue; }
        if (kwIs(line, "TEXT")) { section = "TEXT"; continue; }
        if (toUpper(line).rfind("SPECNUM", 0) == 0) { done = true; continue; }
        // next race's block starts here: the shipped file has NO bare "end"
        // before each specnum (census: 126 ENDxxx, block terminators are
        // the next SPECNUM line), so a second SPECNUM must end our block.

        if (section.empty()) continue;
        // The vendor concatenates raw lines into the section buffer; the
        // transform later maps the separator to ' ' — join with '\n' so
        // introTransform() reproduces exactly that.
        std::string* dst = section == "POWER"   ? &r.power
                           : section == "INTRO" ? &r.intro
                           : section == "PEACE" ? &r.peace
                           : section == "NEUTRAL" ? &r.neutral
                           : section == "HOSTILE" ? &r.hostile
                                                  : &r.text;
        if (!dst->empty()) *dst += "\n";
        *dst += line;
    }
    r.found = inBlock;
    if (!inBlock && errOut)
        *errOut = "Species " + std::to_string(specnum) +
                  " not found in history file.";  // pool 0x83d71 verbatim
    return r;
}

std::string introTransform(const std::string& raw) {
    std::string out;
    out.reserve(raw.size());
    for (char c : raw)
        out.push_back(c == '@'      ? '\n'
                      : c == '_'    ? ' '
                      : c == '\n'   ? ' '
                                    : c);
    return out;
}

bool buildIntroPanel(const std::string& fileText, int specnum, int atmosphere,
                     IntroPanel* out, std::string* errOut) {
    const HistoryRace r = parseHistoryRace(fileText, specnum, errOut);
    if (!r.found) return false;
    out->header = introTransform(r.power);
    std::string body = introTransform(r.intro);
    if (!r.text.empty())
        body += (body.empty() ? "" : "\n") + introTransform(r.text);
    const std::string gated = atmosphere == 0   ? introTransform(r.peace)
                              : atmosphere == 1 ? introTransform(r.neutral)
                              : atmosphere == 2 ? introTransform(r.hostile)
                                                : std::string();
    if (!gated.empty())
        body += (body.empty() ? "" : "\n") + gated;
    // Split into paragraphs on the '@'-derived '\n'; the vendor draws the
    // body buffer as one text run, paragraphs are the display unit the
    // '@@' law implies.
    out->paragraphs.clear();
    size_t pos = 0;
    while (pos <= body.size()) {
        size_t nl = body.find('\n', pos);
        std::string p = trim(body.substr(
            pos, nl == std::string::npos ? std::string::npos : nl - pos));
        if (!p.empty()) out->paragraphs.push_back(p);
        if (nl == std::string::npos) break;
        pos = nl + 1;
    }
    return true;
}

std::vector<std::string> wrapIntroLine(const std::string& para, int maxPx,
                                       int charW) {
    std::vector<std::string> lines;
    if (maxPx <= 0 || charW <= 0) { lines.push_back(para); return lines; }
    const int maxChars = maxPx / charW;
    std::string cur;
    size_t pos = 0;
    while (pos < para.size()) {
        size_t sp = para.find(' ', pos);
        std::string word = para.substr(
            pos, sp == std::string::npos ? std::string::npos : sp - pos);
        pos = sp == std::string::npos ? para.size() : sp + 1;
        if (word.empty()) continue;
        if (!cur.empty() &&
            int((cur.size() + 1 + word.size()) * size_t(charW)) > maxPx) {
            lines.push_back(cur);
            cur.clear();
        }
        if (!cur.empty()) cur += ' ';
        cur += word;  // an over-long word stands alone (never truncated)
    }
    (void)maxChars;
    if (!cur.empty()) lines.push_back(cur);
    return lines;
}

}  // namespace ascend::ui
