// SPDX-License-Identifier: GPL-3.0-or-later
// t409 ability-dialog law implementation. Parsing is deliberately dumb
// (line walk, no regex): the block grammar is fixed vendor text and the
// failure mode must be a refusal, never a silently-wrong panel.
#include "ui/abilitylaw.h"

#include <cctype>
#include <cstdlib>
#include <fstream>
#include <sstream>

#include "game/starstat.h"  // cp437ToUtf8 (single shared decoder)

namespace ascend::ui {

const Rect kAbilityWin{60, 100, 395, 355};  // windows.txt ln2136 verbatim

namespace {
std::string trim(const std::string& s) {
    size_t a = s.find_first_not_of(" \t\r\n");
    if (a == std::string::npos) return "";
    size_t b = s.find_last_not_of(" \t\r\n");
    return s.substr(a, b - a + 1);
}
}  // namespace

bool loadAbilityPanels(const std::string& helpTxtPath,
                       std::vector<AbilityPanel>* out, std::string* err) {
    std::ifstream f(helpTxtPath, std::ios::binary);
    if (!f) {
        if (err) *err = helpTxtPath + ": cannot open";
        return false;
    }
    std::vector<std::string> raw;
    std::string line;
    while (std::getline(f, line)) raw.push_back(line);

    out->clear();
    size_t i = 0;
    while (i < raw.size()) {
        const std::string t = trim(raw[i]);
        if (t.rfind("help abil", 0) != 0) { ++i; continue; }
        AbilityPanel p;
        try {
            p.index = std::stoi(t.substr(9));
        } catch (...) {
            if (err) *err = "help.txt: malformed abil header '" + t + "'";
            return false;
        }
        ++i;
        // Walk until the next `help ` header: collect text blocks (in order)
        // and buttons. The FIRST text block is the title, the SECOND the
        // body, an optional THIRD the charge line (the pos lines confirm
        // 50/125/160 but the ORDER is the law).
        std::vector<std::string> texts;
        bool inText = false;
        std::string cur;
        for (; i < raw.size(); i++) {
            const std::string s = trim(raw[i]);
            if (s.rfind("help ", 0) == 0) break;  // next block (any kind)
            if (s == "text") { inText = true; cur.clear(); continue; }
            if (inText && s == "endtext") {
                inText = false;
                texts.push_back(cur);
                continue;
            }
            if (inText) { cur += (cur.empty() ? "" : "\n") + s; continue; }
            if (s == "button") {
                AbilityButton b;
                for (; i + 1 < raw.size(); i++) {
                    const std::string n = trim(raw[i + 1]);
                    if (n.rfind("title ", 0) == 0)
                        b.title = n.substr(6);
                    else if (n.rfind("msg ", 0) == 0)
                        b.msg = std::atoi(n.c_str() + 4);
                    else if (n == "button" || n.rfind("help ", 0) == 0 ||
                             n.empty())
                        break;
                }
                // '^' word-join (windows.txt TEXTITEM convention).
                for (auto& c : b.title)
                    if (c == '^') c = ' ';
                p.buttons.push_back(b);
                continue;
            }
        }
        if (texts.empty()) {
            if (err) *err = "help.txt: abil" + std::to_string(p.index) +
                            " has no text block";
            return false;
        }
        p.title = texts[0];
        if (texts.size() > 1) p.body = texts[1];
        if (texts.size() > 2) p.chargeLine = texts[2];
        // cp437 -> utf8 exactly like every other vendor-text reader.
        p.title = ascend::game::cp437ToUtf8(p.title);
        p.body = ascend::game::cp437ToUtf8(p.body);
        p.chargeLine = ascend::game::cp437ToUtf8(p.chargeLine);
        out->push_back(std::move(p));
    }
    // Census law: exactly 21 blocks, indices 0..20 contiguous (gate 3m
    // ability_probe.py asserts the same over the raw file).
    if (out->size() != 21) {
        if (err) *err = "help.txt: expected 21 abil blocks, found " +
                        std::to_string(out->size());
        return false;
    }
    for (int k = 0; k < 21; k++)
        if ((*out)[size_t(k)].index != k) {
            if (err) *err = "help.txt: abil block order not 0..20 at " +
                            std::to_string(k);
            return false;
        }
    return true;
}

const AbilityPanel* panelForIndex(const std::vector<AbilityPanel>& panels,
                                  int idx) {
    if (idx < 0 || idx >= int(panels.size())) return nullptr;
    const auto& p = panels[size_t(idx)];
    return p.index == idx ? &p : nullptr;
}

bool abilityDialogHit(int x, int y) {
    return x >= kAbilityWin.x0 && x <= kAbilityWin.x1 &&
           y >= kAbilityWin.y0 && y <= kAbilityWin.y1;
}

std::string formatChargeLine(const std::string& tmpl, int remaining) {
    if (remaining < 0) remaining = 0;
    const std::string days = std::to_string(remaining);
    const std::string plural = remaining == 1 ? "" : "s";
    std::string out;
    size_t pos = 0;
    while (pos < tmpl.size()) {
        if (tmpl[pos] == '%' && pos + 1 < tmpl.size()) {
            if (tmpl[pos + 1] == 'd') { out += days; pos += 2; continue; }
            if (tmpl[pos + 1] == 's') { out += plural; pos += 2; continue; }
        }
        out += tmpl[pos++];
    }
    return out;
}

std::vector<std::string> wrapBody(const std::string& text, int maxChars) {
    std::vector<std::string> out;
    // The parser joined vendor lines with '\n'; each run is a soft-broken
    // sentence block. Re-flow per run.
    std::istringstream lines(text);
    std::string run;
    while (std::getline(lines, run)) {
        std::istringstream ws(run);
        std::string word, cur;
        while (ws >> word) {
            if (!cur.empty() && int(cur.size() + 1 + word.size()) > maxChars) {
                out.push_back(cur);
                cur.clear();
            }
            if (!cur.empty()) cur += ' ';
            cur += word;
        }
        if (!cur.empty()) out.push_back(cur);
        else if (run.empty()) out.push_back("");  // keep blank separator
    }
    return out;
}

}  // namespace ascend::ui
