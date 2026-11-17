// SPDX-License-Identifier: GPL-3.0-or-later
// t387 pure menu-law tables + slot listing. No SDL, no filesystem beyond
// listSaveSlots (the one place the law touches disk; unit tests build real
// files in a temp dir — torn-tolerance law t366/t369).
#include "ui/menulaw.h"

#include <algorithm>
#include <cstdio>
#include <filesystem>
#include <fstream>

#include "game/observer.h"

namespace ascend::ui {
namespace fs = std::filesystem;

// windows.txt L596-673 verbatim (block order GALAXY_MORE, PLAYERS_MORE,
// DIFFICULTYMORE; messages 501/503/505, SENDPARAM1/2 all 0).
const NewgameControl kNewgameControls[kNewgameControlCount] = {
    {"GALAXY_MORE", {7, 381, 122, 472}, 501, "Star Density"},
    {"PLAYERS_MORE", {131, 381, 246, 472}, 503, "Species"},
    {"DIFFICULTYMORE", {255, 381, 370, 472}, 505, "Atmosphere"},
};

namespace {
bool inside(Rect r, Pt p) {
    return p.x >= r.x0 && p.x <= r.x1 && p.y >= r.y0 && p.y <= r.y1;
}
}  // namespace

int newgameControlAt(Pt p) {
    // Disjoint rects [verified — equal 115-px widths, 9-px gutters], so the
    // scan order cannot change the answer; first match keeps it simple.
    for (int i = 0; i < kNewgameControlCount; i++)
        if (inside(kNewgameControls[i].rect, p)) return i;
    return -1;
}

// ---- t393 New Game full-screen law ----------------------------------------
int newgameRowAt(Pt p) {
    if (!inside(kRaceList, p)) return -1;
    for (int i = 0; i < kRaceSlotCount; i++) {
        Rect slot{kRaceList.x0, kRaceSlotTop + i * kRaceSlotPitch,
                  kRaceList.x1, kRaceSlotTop + i * kRaceSlotPitch + kRaceSlotH - 1};
        if (inside(slot, p)) return i;
    }
    return -1;  // gutters dead
}

int newgameArrowAt(Pt p) {
    if (inside(kRaceArrowUp, p)) return 0;
    if (inside(kRaceArrowDown, p)) return 1;
    return -1;
}

// static.txt //155-159 verbatim; star counts = the t78 MEASURED cycle
// (docs/re/mapgen.md OQ-012(a): Average 50 measured 5/5, Dense 75, Very
// Dense 100, Vacuous 15, Sparse 25; cycle order Average->Dense->Very
// Dense->Vacuous->Sparse->wrap, live-rung witness r1size-* captures).
const char* const kDensityWords[kDensityCycleCount] = {
    "Average", "Dense", "Very Dense", "Vacuous", "Sparse"};
const int kDensityStarCounts[kDensityCycleCount] = {50, 75, 100, 15, 25};

const char* densityWord(int starCount) {
    for (int i = 0; i < kDensityCycleCount; i++)
        if (kDensityStarCounts[i] == starCount) return kDensityWords[i];
    return nullptr;  // off the measured ladder: no word is cited, say so
}

const char* speciesCountWord(int n) {  // static.txt //163-167
    static const char* const kWords[5] = {"Three", "Four", "Five", "Six",
                                          "Seven"};
    return n >= 3 && n <= 7 ? kWords[n - 3] : nullptr;
}

const char* atmosphereWord(int v) {  // static.txt //160-162
    static const char* const kWords[3] = {"Peaceful", "Neutral", "Hostile"};
    return v >= 0 && v <= 2 ? kWords[v] : nullptr;
}

void newgameSummary(int starCount, int speciesCount, int atmosphere,
                    std::vector<std::string>* out) {
    // Template static.txt //168 "%s Star Cluster\n%s Species\n%s Atmosphere".
    // An uncited word degrades to the bare noun — the line still says what
    // it is about, it just stops claiming a value it cannot cite.
    const char* d = densityWord(starCount);
    const char* s = speciesCountWord(speciesCount);
    const char* a = atmosphereWord(atmosphere);
    out->clear();
    out->push_back(std::string(d ? d : "") + (d ? " " : "") + "Star Cluster");
    out->push_back(std::string(s ? s : "") + (s ? " " : "") + "Species");
    out->push_back(std::string(a ? a : "") + (a ? " " : "") + "Atmosphere");
}

bool loadNewgameLore(const std::string& path, std::vector<std::string>* out,
                     std::string* err) {
    std::ifstream f(path, std::ios::binary);
    if (!f) {
        if (err) *err = "newgame.txt: cannot open " + path;
        return false;
    }
    out->clear();
    std::string line;
    while (std::getline(f, line)) {
        if (!line.empty() && line.back() == '\r') line.pop_back();
        if (line == "\x1a") break;  // vendor EOF marker after line 22
        if (line.empty()) continue;  // blank padding lines 22-23
        out->push_back(line);
    }
    if (out->size() != 21) {
        if (err)
            *err = "newgame.txt: expected 21 species fragments, got " +
                   std::to_string(out->size());
        return false;
    }
    return true;
}

std::string loreSentence(const std::string& name, const std::string& frag) {
    return "The " + name + " " + frag;  // static.txt //154 "The %s %s"
}

std::vector<std::string> wrapToWidth(
    const std::string& text, int maxW,
    const std::function<int(const std::string&)>& widthOf) {
    std::vector<std::string> lines;
    std::string cur;
    std::istringstream words(text);
    std::string w;
    while (words >> w) {
        const std::string cand = cur.empty() ? w : cur + " " + w;
        if (cur.empty() || widthOf(cand) <= maxW)
            cur = cand;
        else {
            lines.push_back(cur);
            cur = w;
        }
    }
    if (!cur.empty()) lines.push_back(cur);
    return lines;
}

std::vector<SaveSlot> listSaveSlots(const std::string& dir) {
    std::vector<SaveSlot> out;
    std::error_code ec;
    if (!fs::is_directory(dir, ec)) return out;  // honest zero
    for (const auto& e : fs::directory_iterator(dir, ec)) {
        if (ec) break;
        if (!e.is_regular_file(ec)) continue;
        std::string ext = e.path().extension().string();
        std::transform(ext.begin(), ext.end(), ext.begin(), ::tolower);
        if (ext != ".sav") continue;
        SaveSlot s;
        s.name = e.path().filename().string();
        std::ifstream f(e.path(), std::ios::binary);
        if (!f) { s.torn = true; out.push_back(s); continue; }
        std::vector<uint8_t> buf(4);
        f.read(reinterpret_cast<char*>(buf.data()), 4);
        if (f.gcount() < 4) {
            s.torn = true;  // autosave-in-progress artifact: listed, marked
        } else {
            s.day = ascend::game::Observer::rawDay(buf);  // u32@0 law, one impl
        }
        out.push_back(s);
    }
    std::sort(out.begin(), out.end(),
              [](const SaveSlot& a, const SaveSlot& b) { return a.name < b.name; });
    return out;
}

int loadRowAt(Pt p, int slotCount) {
    if (!inside(kLoadList, p) || slotCount <= 0) return -1;
    const int rel = p.y - kLoadList.y0;
    if (rel < 0) return -1;
    const int idx = rel / kLoadRowPitch;
    if (idx >= slotCount) return -1;
    // Inside the row band? The pitch-row gutter is dead space by the RACE_n
    // geometry law (rows are 30 of 39).
    if (rel - idx * kLoadRowPitch >= kLoadRowH) return -1;
    return idx;
}

bool loadPickAccepts(const std::vector<SaveSlot>& slots, int index,
                     std::string* why) {
    if (index < 0 || index >= int(slots.size())) {
        if (why) *why = "no such slot";
        return false;  // never clamp to nearest
    }
    if (slots[size_t(index)].torn) {
        if (why) *why = "slot is torn (partial autosave)";
        return false;
    }
    return true;
}

// ---- t401 NEW GAME ART LAW (header docblock carries the citations) --------
// Page-texture bands on the New Game screen [measured on the user original;
// docs/re/t401-newgame-art.md S8/S10 — same t400 §4 texture class, different band
// extents because the starfield runs to ~x493 here].
const Rect kNewgameTextureBands[2] = {
    {0, 0, 6, 479},       // left margin (t400 §4 band, same extent)
    {494, 0, 639, 479},   // right side (texture columns measured at y=200)
};

int newgameWheelFrame(int control, int value) {
    switch (control) {
        case 0: {  // Star Density: rank in the sorted ladder -> k0..k4
                   // (t414 bijection; was k0..k3,k3).
            // Sorted copy of the t78 ladder rungs {50,75,100,15,25}.
            int ladder[5] = {kDensityStarCounts[0], kDensityStarCounts[1],
                             kDensityStarCounts[2], kDensityStarCounts[3],
                             kDensityStarCounts[4]};
            for (int i = 0; i < 4; i++)
                for (int j = i + 1; j < 5; j++)
                    if (ladder[j] < ladder[i]) std::swap(ladder[i], ladder[j]);
            int rank = -1;
            for (int i = 0; i < 5; i++)
                if (ladder[i] == value) rank = i;
            if (rank < 0) return -1;  // off-ladder: refuse, never clamp
            return rank;
        }
        case 1:  // Species: k(2+n), 3..Seven (anchor k7 @ Five, measured).
            if (value < 3 || value > 7) return -1;
            return 2 + value;
        case 2:  // Atmosphere: orbs k(10+v) — t414 bijection (was 0/1->k10).
            if (value < 0 || value > 2) return -1;
            return 10 + value;
        default:
            return -1;
    }
}

// Player^Color chip colours [measured on the user original, rows 434..459,
// chip runs x384..492; docs/re/_wip_t414.md S2d]. Base = the chip body
// colour; hi = the highlight face (both counted per 14x26 chip zone).
const RGB kPlayerChipRgb[kPlayerChipCount][2] = {
    {{5, 118, 69}, {1, 78, 41}},      // green
    {{103, 63, 127}, {158, 81, 174}}, // purple
    {{164, 159, 79}, {255, 235, 97}}, // yellow
    {{154, 108, 127}, {239, 154, 174}},  // pink
    {{121, 105, 69}, {107, 96, 66}},     // tan (measured dominant; weak)
    {{27, 85, 147}, {36, 117, 207}},     // blue
    {{151, 88, 20}, {235, 121, 4}},      // orange
};

std::string portraitLibName(int specnum) {
    if (specnum < 0 || specnum > 20) return std::string();  // refuse
    char buf[32];
    std::snprintf(buf, sizeof(buf), "smrace%02d.shp", specnum);
    return std::string(buf);
}

}  // namespace ascend::ui
