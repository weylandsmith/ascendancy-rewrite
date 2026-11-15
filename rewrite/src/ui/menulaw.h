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
#include <functional>
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

// ---- New Game full-screen layout (t393; docs/re/_wip_t393.md S6-S12) ------
// D10 (user 2026-11-14): the vendor New Game screen is a FULL-SCREEN switch
// (starfield backdrop + panels), not an overlay. The four bottom-row panels
// above are windows.txt-cited; the fifth zone — the Begin New Game button —
// is NOT in windows.txt (STARTGAME L1866 carries STATE "1 12", so it is not
// the state-3 button): its rect is a CITED MEASUREMENT off the user-supplied
// original capture scratchpad/newgame-original.png (capture = 640x480 + 1px
// border; screen coord = capture coord - 1; anchor: GALAXY_MORE x0=7 lands
// exactly on the capture's navy/left-bevel boundary).
inline constexpr Rect kBeginNewGameBtn{494, 373, 639, 472};
// Player^Color (windows.txt L653, TYPE 0, PARENT NONE, MSG 0): the fourth
// bottom-row zone. Label + colour chips; MSG 0 means the vendor sends no
// message on click (inert zone in the window table).
inline constexpr Rect kPlayerColorRect{379, 381, 493, 419};
// Summary block centre x [measured]: the three white lines centre on screen
// x ~170 (bands x 116..224 / 140..204 / 121..221). Begin label white ink
// rows measured 456..464 -> label top 455.
inline constexpr int kSummaryCentreX = 170, kBeginLabelTop = 455;

// Text placements [measured S9, screen coords, ink rows]: species name
// (green) rows 18..27 centred x 412 ~= NEWGAMEWND centre 411; "Player
// Species" header (white) rows 16..25 centred x 568 ~= RACELIST centre 567;
// lore block inside NEWGAMEWND; summary block centred under the starfield.
inline constexpr int kNameTop = 18, kHeaderTop = 16;
inline constexpr Rect kLoreBox{334, 258, 488, 330};
inline constexpr int kLoreLinePitch = 11;  // measured bands pitch 11
inline constexpr int kSummaryTop = 327, kSummaryPitch = 13;

// RACELIST ROW LAW [MEASURED t393 on the user-supplied original]: the list
// is a THREE-SLOT scroll window, not a 7-row list. Silver bevel-ring census
// inside the interior gives row bands screen 49..153 / 157..262 / 266..372
// (pitch 108), x 506..631. Scroll arrows are 16x16 squares at the interior
// corners: up (616,47)-(631,62), down (616,356)-(631,371).
inline constexpr int kRaceSlotTop = 49, kRaceSlotH = 108, kRaceSlotPitch = 108;
inline constexpr int kRaceSlotCount = 3;
inline constexpr Rect kRaceArrowUp{616, 47, 631, 62};
inline constexpr Rect kRaceArrowDown{616, 356, 631, 371};
int newgameRowAt(Pt p);   // slot 0..2 or -1 (gutters/arrows dead for rows)
int newgameArrowAt(Pt p); // 0 = up, 1 = down, -1 = none

// The three setting words + summary (static.txt verbatim, L429-457 block):
// density words 155-159, atmosphere 160-162, species count 163-167, summary
// template 168 "%s Star Cluster\n%s Species\n%s Atmosphere". The word->star
// count law is the t78 MEASURED ladder (mapgen.md OQ-012(a)): Average 50 ->
// Dense 75 -> Very Dense 100 -> Vacuous 15 -> Sparse 25 -> wrap.
inline constexpr int kDensityCycleCount = 5;
extern const char* const kDensityWords[kDensityCycleCount];
extern const int kDensityStarCounts[kDensityCycleCount];  // parallel, cited
const char* densityWord(int starCount);  // "Average" for 50; nullptr off-ladder
const char* speciesCountWord(int n);     // "Three".."Seven"; nullptr else
const char* atmosphereWord(int v);       // 0 Peaceful / 1 Neutral / 2 Hostile
// Summary lines from a (density, species, atmosphere) triple; unknown values
// degrade to the bare noun ("Star Cluster") rather than inventing a word.
void newgameSummary(int starCount, int speciesCount, int atmosphere,
                    std::vector<std::string>* out);  // 3 lines, template 168

// LORE LAW (t393): extracted/ascend00/newgame.txt line N+1 == specnum N's
// sentence fragment ("are a mysterious group of robot creatures ..."); the
// vendor composes it with static.txt 154 "The %s %s" (name + fragment).
// Refuses (false, err) unless exactly 21 fragments parse (EOF marker 0x1a
// ends the file). Supply-your-own data rules apply: read, never embed.
bool loadNewgameLore(const std::string& path, std::vector<std::string>* out,
                     std::string* err);
std::string loreSentence(const std::string& name, const std::string& frag);

// Greedy word wrap against a measured-width function (the caller supplies
// VendorText::width; pure so it unit-tests without SDL). Never splits a
// word; a single word wider than maxW goes on its own line (honest overflow).
std::vector<std::string> wrapToWidth(
    const std::string& text, int maxW,
    const std::function<int(const std::string&)>& widthOf);

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
