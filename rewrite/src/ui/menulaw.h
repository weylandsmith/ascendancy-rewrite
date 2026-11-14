// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
// t387: the pure (no SDL) law side of the title-menu windows — NEWGAMEWND
// (New Game) geometry + hit-map, and the LOAD slot-list law. Geometry is
// verbatim from extracted/ascend00/windows.txt L575-717 (blocks read this
// iteration; law + coordinate-space witness banked docs/re/_wip_t387.md and
// distilled into docs/re/boot.md §6).
//
// COORDINATE SPACE [verified by geometry, _wip_t387]: every rect below is an
// ABSOLUTE screen coordinate — PARENT names a containment/dialogue owner, it
// is NOT a coordinate offset (relative reading puts RACELIST at x=836 and
// overlaps the bottom-row buttons; absolute puts them disjoint, equal-width,
// 9-px gutters).
#include <cstdint>
#include <string>
#include <vector>

#include "ui/layout.h"

namespace ascend::ui {

// ---- New Game (state 3, SHAPEFILE DATA\3CFGNEW.SHP) ----------------------
// windows.txt TYPE 18 NEWGAMEWND: PARENT NONE, STATE "1 3", SHAPEFRAME 0.
inline constexpr Rect kNewgameWnd{334, 12, 488, 364};
// TYPE 10 RACELIST, PARENT NEWGAMEWND, SHAPEFRAME 7 (list frame; the race
// rows themselves are state-7 TYPE 6 controls — racesel screen, t388 seam).
inline constexpr Rect kRaceList{502, 45, 632, 372};

// The three state-3 child buttons (TYPE 0, STATE "1 3", SHAPEFRAME -1,
// SHAPEITEM 1 data\3cfgnew.shp 0 0 0 — the k0 wheel face). Labels are the
// TEXTITEM 0 strings with the vendor '^' word-join joined to spaces.
struct NewgameControl {
    const char* name;   // vendor NAME (verbatim)
    Rect rect;          // absolute, inclusive
    int message;        // SENDMESSAGE
    const char* label;  // display label ('^' -> ' ')
};
inline constexpr int kNewgameControlCount = 3;
extern const NewgameControl kNewgameControls[kNewgameControlCount];

// Which control (0..2) contains p, -1 if none. Inclusive edges, no clamp
// (same law as titleButtonAt).
int newgameControlAt(Pt p);

// ---- Load (LOADSCREEN/LOADLIST) -------------------------------------------
// TYPE 11 LOADSCREEN (7,7)-(632,37): the title strip; TYPE 10 LOADLIST
// (7,46)-(632,472): the slot list interior. STATE "3 2 4 15" on both.
inline constexpr Rect kLoadScreen{7, 7, 632, 37};
inline constexpr Rect kLoadList{7, 46, 632, 472};
// Row geometry [inferred — no cited row rect exists for LOADLIST]: rows are
// 30 tall with pitch 39 starting at LOADLIST.y0, the verbatim law of the
// only list census in windows.txt (RACE_1..RACE_7, y 7/46/85/124/...).
inline constexpr int kLoadRowH = 30;
inline constexpr int kLoadRowPitch = 39;

// One entry of the save-slot list. Slot law (docs/re/r1-savestate.md;
// Observer::rawDay): a raw .SAV carries its game-day as u32@0. A file
// shorter than 4 bytes is TORN (autosave rewrites slots in place; a copy can
// catch one mid-write) — torn slots are LISTED and marked, never clamped
// (t366/t369 torn-tolerance law).
struct SaveSlot {
    std::string name;   // file name as on disk (e.g. "41.sav")
    uint32_t day = 0;   // u32@0 law; 0 and meaningless when torn
    bool torn = false;  // size < 4 bytes
};

// List *.SAV / *.sav (case-insensitive extension) in `dir`, sorted by name
// ascending (the slot-name order the vendor ring uses). A missing or
// unreadable directory yields an empty list — an honest zero, never a guess.
// NEVER point this at game/: supply-your-own dir only (README law).
std::vector<SaveSlot> listSaveSlots(const std::string& dir);

// Which row index a click inside the load screen selects, -1 if the point is
// outside LOADLIST or below the last row. Rows are kLoadRowPitch apart from
// kLoadList.y0; the 9-px gutters between rows are no-man's land (no row).
int loadRowAt(Pt p, int slotCount);

// Pick law (refusal-not-clamp): accept iff index is in range and the slot is
// not torn. On refusal *why names the reason. Acceptance means the FILE is
// verified playable material; importing the state into a live Campaign is a
// named seam (docs/re/boot.md §6) — the rewrite has no campaign-state
// importer yet (Observer is read-only by contract).
bool loadPickAccepts(const std::vector<SaveSlot>& slots, int index,
                     std::string* why);

}  // namespace ascend::ui
