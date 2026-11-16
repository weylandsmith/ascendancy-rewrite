// SPDX-License-Identifier: GPL-3.0-or-later
#include "ui/boot.h"

namespace ascend::ui {

// Verbatim from extracted/ascend00/windows.txt L38-175 (block order; every
// rect/label/message measured, law + table in docs/re/boot.md §1). The '^'
// in vendor TEXTITEM strings is a word join; labels here are the display
// spelling. Sub-grammar after the string ("3 0 0" etc.) is OQ-015 territory
// and deliberately unused.
const TitleButton kTitleButtons[kTitleButtonCount] = {
    {"INTRO", {159, 200, 477, 230}, "Play Introduction", nullptr,
     BootState::Intro, 1, 6},
    {"PLAYTUTORIAL", {159, 240, 477, 270}, "Tutorial", nullptr,
     BootState::Tutorial, 1, 15},
    {"FRESHGAME", {159, 280, 477, 310}, "New Game", nullptr,
     BootState::RaceConfig, 1, 3},
    {"RESUME", {159, 320, 477, 350}, "Return to Current Game", nullptr,
     BootState::Campaign, 1, 1},
    {"LOAD", {159, 360, 477, 390}, "Load Game", "Alt-L", BootState::Load,
     1, 4},
    {"SAVE", {159, 400, 477, 430}, "Save Game", "Alt-S", BootState::Save,
     1, 2},
    {"EXITTODOS", {159, 440, 477, 470}, "Exit to DOS", "Alt-X",
     BootState::Quit, 2, 0},
};

int titleButtonAt(Pt p) {
    for (int i = 0; i < kTitleButtonCount; i++)
        if (inRect(kTitleButtons[i].rect, p)) return i;
    return -1;
}

BootState bootHotkey(BootState from, char letter) {
    if (from != BootState::Title) return from;
    if (letter == 'l') return BootState::Load;
    if (letter == 's') return BootState::Save;
    // t392: windows.txt EXITTODOS carries a second TEXTITEM "Alt-X"
    // (L170) — the vendor's Exit hotkey twin, same shape as Alt-L/S.
    if (letter == 'x') return BootState::Quit;
    return from;
}

BootState bootClick(BootState from, Pt p) {
    switch (from) {
        case BootState::Title: {
            const int i = titleButtonAt(p);
            return i < 0 ? from : kTitleButtons[i].target;
        }
        case BootState::RaceConfig:
            // Race-configuration overlay keeps the vendor column live; the
            // RESUME button (msg 1/1) is the documented edge into play.
            return titleButtonAt(p) == 3 ? BootState::Campaign : from;
        case BootState::Intro:
        case BootState::Tutorial:
        case BootState::Load:
        case BootState::Save:
        case BootState::RaceIntro:
            // Overlay states: their exit is driver-signalled (movie EOF,
            // cancel key), not a blind click. Inert here by law. (t412:
            // RaceIntro's dismiss is handled by its own driver loop in
            // title.cpp, same pattern as Load's runLoadScreen.)
            return from;
        case BootState::Campaign:
        case BootState::Quit:
            return from;  // Campaign loop owns its own input; Quit is terminal
    }
    return from;
}

bool bootReachableFromTitle(BootState s) {
    for (int i = 0; i < kTitleButtonCount; i++)
        if (kTitleButtons[i].target == s) return true;
    return false;
}

const char* bootStateName(BootState s) {
    switch (s) {
        case BootState::Title: return "title";
        case BootState::Intro: return "intro";
        case BootState::Tutorial: return "tutorial";
        case BootState::RaceConfig: return "raceconfig";
        case BootState::RaceIntro: return "raceintro";
        case BootState::Load: return "load";
        case BootState::Save: return "save";
        case BootState::Campaign: return "campaign";
        case BootState::Quit: return "quit";
    }
    return "?";
}

}  // namespace ascend::ui
