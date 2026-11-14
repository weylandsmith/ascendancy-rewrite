// SPDX-License-Identifier: GPL-3.0-or-later
// t387 pure menu-law tables + slot listing. No SDL, no filesystem beyond
// listSaveSlots (the one place the law touches disk; unit tests build real
// files in a temp dir — torn-tolerance law t366/t369).
#include "ui/menulaw.h"

#include <algorithm>
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

}  // namespace ascend::ui
