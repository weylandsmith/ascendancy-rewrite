// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
// t385: the vendor boot sequence as an EXPLICIT state machine (user ruling
// D8 2026-11-14: boot goes to the title screen, all menu options present).
// Pure data + math (no SDL) so the click-routing table is unit-testable
// headless. Geometry and labels are verbatim from extracted/ascend00/
// windows.txt L34-175 (seven TYPE-0 buttons; law banked docs/re/boot.md §1).
#include <cstddef>

#include "ui/layout.h"

namespace ascend::ui {

enum class BootState {
    Title,       // opening control screen (0OPENING chrome + 7 buttons)
    Intro,       // playing intro65a.flc (movie exit -> Title)
    Tutorial,    // seam: no tutorial driver exists in the rewrite yet
    RaceConfig,  // NEWGAMEWND (t387); RESUME edge -> Campaign
    Load,        // seam: 4loadgam.shp chrome + slot list (t387)
    Save,        // seam: STATUSWND save (t388)
    Campaign,    // runCampaignUi
    Quit,        // terminal (EXITTODOS)
};

// The seven title-menu buttons in windows.txt block order. Rects are the
// vendor values: column x 159..477, 30 px tall, pitch 40, first at y=200.
struct TitleButton {
    const char* name;      // vendor NAME (verbatim)
    Rect rect;             // vendor X0,Y0,X1,Y1 (inclusive)
    const char* label;     // TEXTITEM 0 string, '^' joined to spaces
    BootState target;      // state this click selects from Title
    int message;           // SENDMESSAGE
    int param1;            // SENDPARAM1 (the vendor's command id)
};
inline constexpr int kTitleButtonCount = 7;
extern const TitleButton kTitleButtons[kTitleButtonCount];

// Which button (index 0..6) contains p from the Title screen, -1 if none.
int titleButtonAt(Pt p);

// D9 LAW (user 2026-11-14; windows.txt LOAD/SAVE TEXTITEM hotkey items):
// from Title, 'l' = Load, 's' = Save (the Alt-chord twins of the on-screen
// buttons); any other key is a no-op. Takes the LOWERCASED letter so the
// caller owns the modifier decoding.
BootState bootHotkey(BootState from, char letter);

// Pure transition law (docs/re/boot.md §2): given the current state and a
// click, return the next state. No-op (returns `from`) when nothing is
// wired there — a click NEVER clamps or guesses.
//   Title: the seven vendor buttons.
//   Intro/Tutorial: movie/overlay exit lands back on Title (the driver
//     signals done via bootDone(); clicks inside are inert).
//   RaceConfig: the RESUME button (vendor msg 1/1) enters the campaign.
//   Quit: terminal, nothing leaves it.
BootState bootClick(BootState from, Pt p);

// True iff `s` is a state the Title screen can transition directly to
// (everything except Title itself and Quit's post-state bookkeeping).
bool bootReachableFromTitle(BootState s);

const char* bootStateName(BootState s);

}  // namespace ascend::ui
