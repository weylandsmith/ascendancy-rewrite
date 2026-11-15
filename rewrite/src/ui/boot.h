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
    // t392: the button's SECOND TEXTITEM display string, verbatim from
    // windows.txt ("Alt-L"/"Alt-S"/"Alt-X"), or nullptr for the four
    // single-item buttons (WINITEMS 1). The vendor draws it under the
    // label; docs/re/boot.md §7 (t392 measurement).
    const char* hint;
    BootState target;      // state this click selects from Title
    int message;           // SENDMESSAGE
    int param1;            // SENDPARAM1 (the vendor's command id)
};

// t392 TEXT BASELINE LAW (measured on the pinned vendor shot
// docs/assets/refcap/original-title-menu.png, capture shift +40):
// single-line labels (WINITEMS 1) ink rows y0+8..y0+17/18 -> draw TOP
// y0+8; two-item buttons ink rows y0+4..13 (label) and y0+18..27 (hint),
// matching their TEXTITEM dy fields 4/18 -> draw TOPs y0+4 and y0+18.
// Both lines are horizontally CENTRED (vendor ink spans symmetric about
// rect centre 318). NO underline is rendered for the '^' hotkey letter
// (row census inside the rect holds EXACTLY fill+ink, no third colour).
inline constexpr int kTitleLabelTopSingle = 8;   // y0 + 8 (font 3, dy 0)
inline constexpr int kTitleLabelTopPair   = 4;   // y0 + 4 (font 2, dy 4)
inline constexpr int kTitleHintTop        = 18;  // y0 + 18 (font 2, dy 18)
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
