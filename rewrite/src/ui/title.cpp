// SPDX-License-Identifier: GPL-3.0-or-later
// t385 title-screen loop (user D8 2026-11-14: boot goes to the title screen,
// all menu options present). Chrome law: docs/re/boot.md §1 (windows.txt
// button column) + the TITLERECT caption band (subtitle.txt via ui.md §4).
// The vendor opening ART (0OPENING.SHP STATENUMBER 0) is t386's identity
// question — until it is settled NO art is drawn and no lookalike is faked
// (R13 / ui-runtime.md §2). Every accepted action prints one line so
// automation verifies input WITHOUT reading pixels (ui-runtime.md §5).
#include "ui/ui.h"

#include <SDL.h>

#include <cstdio>

#include "ui/boot.h"
#include "ui/ui_internal.h"

namespace ascend::ui {

namespace {
const SDL_Color kTitleBg{10, 12, 26, 255};
const SDL_Color kInk{235, 235, 235, 255};
const SDL_Color kBand{150, 130, 110, 255};
}  // namespace

BootState runTitleScreen(const std::string& dataRoot, BootState initial,
                         int maxIntroFrames, std::string* err,
                         void** windowOut) {
    SDL_Window* win = SDL_CreateWindow("Ascendancy", SDL_WINDOWPOS_CENTERED,
                                       SDL_WINDOWPOS_CENTERED, kDisplayW,
                                       kDisplayH, SDL_WINDOW_SHOWN);
    if (!win) {
        *err = std::string("title CreateWindow: ") + SDL_GetError();
        return BootState::Quit;
    }
    SDL_Renderer* ren = SDL_CreateRenderer(win, -1, SDL_RENDERER_ACCELERATED);
    if (!ren) ren = SDL_CreateRenderer(win, -1, SDL_RENDERER_SOFTWARE);
    VendorText txt;
    if (!ren || !txt.load(ren, dataRoot, err)) {
        *err = err->empty() ? std::string("title renderer: ") + SDL_GetError() : *err;
        SDL_DestroyRenderer(ren);
        SDL_DestroyWindow(win);
        return BootState::Quit;
    }

    BootState st = initial;
    std::fflush(stdout);

    // Overlay states that have no driver yet: draw the seam message, any
    // key/click-outside returns to Title. Never silently do nothing.
    auto seamLoop = [&](const char* line) {
        std::printf("ui title seam: %s\n", line);
        std::fflush(stdout);
        SDL_Event e;
        for (;;) {
            if (!SDL_WaitEventTimeout(&e, 16)) continue;  // timeout: e untouched
            if (e.type == SDL_QUIT) { st = BootState::Quit; return; }
            if (e.type == SDL_KEYDOWN || e.type == SDL_MOUSEBUTTONDOWN) return;
        }
    };

    while (st == BootState::Title || st == BootState::RaceConfig) {
        // ---- draw: caption band + the seven-button column ----
        SDL_SetRenderDrawColor(ren, kTitleBg.r, kTitleBg.g, kTitleBg.b, 255);
        SDL_RenderClear(ren);
        // TITLERECT 0,379-639,419 [verified, subtitle.txt / ui.md §4]: the
        // vendor caption band. Title art identity is t386; the band frame +
        // game name are what is geometry-verified today.
        SDL_Rect band{0, 379, 640, 41};
        SDL_SetRenderDrawColor(ren, kBand.r, kBand.g, kBand.b, 255);
        SDL_RenderDrawRect(ren, &band);
        {
            const std::string name = "ASCENDANCY";
            const int w = txt.width(name, true);
            txt.draw(ren, (kDisplayW - w) / 2, 385, name, true, kInk);
        }
        for (int i = 0; i < kTitleButtonCount; i++) {
            const TitleButton& b = kTitleButtons[i];
            // Label centred in the vendor rect; the rect itself is the hit
            // law (boot.h), drawn here only as its text baseline frame.
            const int w = txt.width(b.label, true);
            txt.draw(ren, b.rect.x0 + (b.rect.x1 - b.rect.x0 - w) / 2,
                     b.rect.y0 + 4, b.label, true, kInk);
        }
        if (st == BootState::RaceConfig) {
            SDL_Rect ov{120, 120, 400, 60};
            SDL_SetRenderDrawColor(ren, 30, 30, 46, 255);
            SDL_RenderFillRect(ren, &ov);
            SDL_SetRenderDrawColor(ren, kBand.r, kBand.g, kBand.b, 255);
            SDL_RenderDrawRect(ren, &ov);
            txt.draw(ren, ov.x + 12, ov.y + 8,
                     "New game setup lands t387.", false, kInk);
            txt.draw(ren, ov.x + 12, ov.y + 28,
                     "Press Return to Current Game.", false, kInk);
        }
        SDL_RenderPresent(ren);

        // ---- input: one event per frame, routing via the pure law ----
        SDL_Event e;
        if (SDL_WaitEventTimeout(&e, 16)) {
            if (e.type == SDL_QUIT) { st = BootState::Quit; break; }
            if (e.type == SDL_KEYDOWN && e.key.keysym.sym == SDLK_ESCAPE) {
                std::printf("ui title esc\n");
                std::fflush(stdout);
                st = BootState::Quit;
                break;
            }
            // D9 LAW (user 2026-11-14 + vendor screenshot): Alt-L = Load,
            // Alt-S = Save from the title screen — the on-screen buttons'
            // hotkey twins (windows.txt LOAD/SAVE blocks carry the 'Alt-L'/
            // 'Alt-S' TEXTITEM items). Routing lives in bootHotkey (pinned).
            if (e.type == SDL_KEYDOWN &&
                (e.key.keysym.mod & KMOD_ALT)) {
                const char letter =
                    e.key.keysym.sym >= SDLK_a && e.key.keysym.sym <= SDLK_z
                        ? char('a' + (e.key.keysym.sym - SDLK_a))
                        : '?';
                const BootState next = bootHotkey(st, letter);
                if (next != st) {
                    std::printf("ui title hotkey Alt-%c -> %s\n",
                                letter - 'a' + 'A', bootStateName(next));
                    std::fflush(stdout);
                    st = next;
                }
            }
            if (e.type == SDL_MOUSEBUTTONDOWN && e.button.button == SDL_BUTTON_LEFT) {
                Pt p{e.button.x, e.button.y};
                const int idx = titleButtonAt(p);
                const BootState next = bootClick(st, p);
                if (next == st) continue;  // click outside any live button
                std::printf("ui title click %s -> %s\n",
                            idx >= 0 ? kTitleButtons[idx].name : "?",
                            bootStateName(next));
                std::fflush(stdout);
                st = next;
            }
        }

        // ---- non-Title states reached this frame ----
        if (st == BootState::Intro) {
            playIntro(dataRoot + "/extracted/ascend02/data/intro65a.flc",
                      maxIntroFrames);
            st = BootState::Title;  // vendor law: movie exit -> title
        } else if (st == BootState::Tutorial) {
            seamLoop("tutorial driver absent (seam, docs/re/boot.md §3)");
            st = BootState::Title;
        } else if (st == BootState::Load) {
            seamLoop("load chrome lands t387 (4loadgam)");
            st = BootState::Title;
        } else if (st == BootState::Save) {
            seamLoop("save chrome lands t388 (STATUSWND)");
            st = BootState::Title;
        }
    }

    txt.release();  // atlases before their renderer
    SDL_DestroyRenderer(ren);
    if (st == BootState::Campaign && windowOut) {
        // Hand the SAME window to the campaign loop (ui.h law: the first
        // synthetic click a freshly-created Xvfb window receives is dropped;
        // swapping windows per state would eat the gate's injected input).
        *windowOut = win;
    } else {
        SDL_DestroyWindow(win);
    }
    return st;
}

}  // namespace ascend::ui
