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
// FOUR LARGE PORTRAITS over the map (t252 vision): art source CLOSED t436b
// [measured t252 F5/F7/F8, docs/re/_wip_t436.md]: centred on home stars,
// content disc r~48 + three-tone owner ring r50..55 == smrace<specnum> rec 0
// (49x49) at scale 2 clipped r49, ringed by racering k<colour idx> (53x53)
// at scale 2 (the t423c2 ring-index law: ring record == colour index; the
// racering decoded palettes green/purple/gold/orange == the four measured
// rings). SEAM T436-A (open): the capture carries FOUR portraits vs THREE
// known rows and the player home has NO portrait — the count law is
// unresolved; the port paints one portrait per KNOWN AI owner (never a
// fourth invented one). SEAM T436-B: owner->racering colour index is the
// port's owner%7 reading (uncited for AI owners on this screen).
#include <string>
#include <vector>

#include "game/campaign.h"
#include "game/species.h"

namespace ascend::ui {

inline constexpr int kSpeciesRowFlagDx = 14, kSpeciesRowFlagDy = 3;
inline constexpr int kSpeciesPortraitScale = 2;   // class scale (t401 law)
inline constexpr int kSpeciesPortraitClipR = 49;  // disc r (smrace 49 x2/2)
inline constexpr int kSpeciesRingHalf = 53;       // racering 53x53 at 2x

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

// The static.txt #11 header for the current campaign.
std::string speciesMenuHeader(const ascend::game::Campaign& camp);

}  // namespace ascend::ui
