// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
// t409 SPECIES MENU (state 7) content law (docs/re/_wip_t409.md F3).
//
// [verified windows.txt] state 7 = the RACE_1..7 rows (ln725.., TYPE 6,
// 474,7/46/85/124/163/202/241 - 632,+30, pitch 39, msg 1 p1 13) + the
// Intelligence item (STATE "1 7"); the COSMOSWnd STATE list "4 1 3 7 13"
// keeps the map visible behind the rows (the port already renders that).
//
// HEADER [verified static.txt #11 (coswnd.cpp pool block, ln50)]:
//   "%d of %d Species Known" — t252 LIVE witness rendered "3 of 3 Species
//   Known" on the species menu (ui-runtime.md §6b). Port reading: first =
//   AI owners the player has contacted (contacted_ law), second = total AI
//   owners. [documented port reading — the vendor's exact operand pair is
//   unmapped; the witness line "known of total" is the only live datum.]
//
// ROWS [verified t252 vision + static.txt #12 "Extinct" (ln53)]: race-
// colored names + flag icons, one row per KNOWN species; an eliminated
// race's row prints "Extinct" instead of the name and clicking it only
// highlights (help.txt:775 contact-refused, diplomacy.md §21.3). Port law:
// known == playerKnows(owner); extinct == starsOwned(owner)==0; name ==
// raceNN.dip header display name; colour == kOwnerRgb[owner] (the port's
// CVD-safe owner colours); flag == raceflag.shp face indexed by SPECNUM
// (t400 §2 law), resolved through the roster by ability token.
//
// ROW RECTS: the t287 live correction measured DRAWN bands y 61/100/139
// (pitch 39) in one sitting vs table rects starting y7 — the absolute top
// is [unverified] (sitting-dependent). Port law: header in the first table
// slot, race rows from kRaceRows[1] down (pitch 39 matches both sources).
//
// ROW CLICK: msg 1 p1 13 = NEGSCREEN, whose chrome is not in the port —
// the t388 known-set law makes it a NO-OP (never a blank screen). Honest.
//
// FOUR LARGE PORTRAITS over the map — law CLOSED t441 [measured t252 pair:
// species_menu_game.png + species2_game.png, both IDENTICAL 4-blob repaints
// (9416/9338/9320/8479 px) vs baseline_game.png; docs/re/_wip_t441.md T2/T6]:
//  * COUNT = ONE PORTRAIT PER RACE TABLE ROW (vendor word[state+0xd88]) — the
//    PLAYER IS INCLUDED (row0 = player = the TOP slot) and contact/elimination
//    state is IRRELEVANT: the eliminated Minions row (ships=0, rows-list prints
//    "Extinct") still carries a GOLD ring. t436's "player home carries NO
//    portrait" and "portraits are centred on the AI home stars" are REFUTED
//    (_wip_t441 T6: the baseline band under every slot is 90% pure black; the
//    white star markers are 64-105 px from three of the four slots).
//  * POSITION = FIXED SLOTS, not a projection: centre of the cosmos field,
//    radius 170, slot k at angle 90 + 90*k degrees (measured 89.7/180.3/269.9/
//    0.0 for rows 0..3 = top/left/bottom/right). n>4 campaigns: 7 slots exist
//    (kRaceRows) and t441 could not disambiguate 90+90k from 90+(360/n)k —
//    the port uses 90+90k, the measured one.
//  * RING INDEX = race-record colour byte (vendor row+8, assigned by
//    FUN_000232ec at New Game; port: the title's raceColours[]). t436-B CLOSED:
//    owner%7 is WRONG — row2 Ungooma is colour 6 (orange) at index 2, and the
//    capture's orange ring sits at ITS slot while gold (k2, Minions' colour)
//    sits at row3's slot (_wip_t441 T2). Race ink on the rows follows the same
//    byte (t436 F7) — second witness.
//  * CONTENT disc = smrace<specnum> rec 0 (49x49) at scale 2 clipped r49
//    (t436b; unchanged).
#include <string>
#include <vector>

#include "game/campaign.h"
#include "game/species.h"
#include "ui/layout.h"

namespace ascend::ui {

inline constexpr int kSpeciesRowFlagDx = 14, kSpeciesRowFlagDy = 3;
inline constexpr int kSpeciesPortraitScale = 1;   // tA1: native bbox dims
inline constexpr int kSpeciesPortraitClipR = 50;  // disc r (content 100)
inline constexpr int kSpeciesRingHalf = 55;       // racering content 109
inline constexpr int kSpeciesRingRadius = 170;    // [t441 T6] slot circle r, px

struct SpeciesRow {
    int owner = -1;         // campaign owner id (1..N)
    std::string name;       // dip header display name ("" if unknown)
    bool extinct = false;   // static.txt #12 replaces the name
    int flagSpecnum = -1;   // raceflag.shp face index; -1 = no face
};

// One row per AI owner the player has CONTACTED, in owner order.
std::vector<SpeciesRow> speciesMenuRows(
    const ascend::game::Campaign& camp,
    const std::vector<ascend::game::SpeciesInfo>* roster);

// owner -> specnum under the scenario build law (main.cpp buildCampaign: AI
// owners take roster specnums in order, skipping the player's). Index 0 = the
// player (cfg playerSpecies, -1 = human). Owners past the roster end (or a
// null roster) get -1 = no species lib. Pure; shared by the rows and the
// portrait ring (t441: portraits cover ALL owners incl. the player).
std::vector<int> speciesSpecnumOfOwner(
    const ascend::game::Campaign& camp,
    const std::vector<ascend::game::SpeciesInfo>* roster);

// The species-screen portrait slot for race row k (t441 T6): centre `fld` of
// the cosmos field, radius kSpeciesRingRadius, angle 90 + 360/nslots * k
// (y-down screen: sin negated). MEASURED at nslots=4 (the t252 campaign):
// pitch 90, slots top/left/bottom/right at 89.7/180.3/269.9/0.0. nslots>4 is
// UNMEASURED (no 5+ race capture exists); the even-distribution reading is
// what keeps race rows 4..6 off rows 0..2's pixels — a fixed 90 deg pitch
// would overlap them (a 7-row campaign draws SEVEN portraits per the count
// law, and overlapping discs is not a defensible default).
Pt speciesPortraitSlot(const ascend::ui::Rect& fld, int k, int nslots);

// The static.txt #11 header for the current campaign.
std::string speciesMenuHeader(const ascend::game::Campaign& camp);

}  // namespace ascend::ui
