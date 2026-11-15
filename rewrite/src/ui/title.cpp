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
#include <algorithm>
#include <vector>

#include "formats/gif.h"
#include "formats/shp.h"
#include "ui/boot.h"
#include "ui/menulaw.h"
#include "ui/titlepalette.h"
#include "ui/ui_internal.h"

namespace ascend::ui {

namespace {
const SDL_Color kTitleBg{10, 12, 26, 255};
// t390 band-closure law (measured per band on the pinned vendor shot,
// scripts/t390_strip_witness.py C): every pixel inside a button rect is
// EXACTLY the flat fill (0,0,8) or the label white (215,215,215).
const SDL_Color kInk{215, 215, 215, 255};
const SDL_Color kBand{150, 130, 110, 255};
const SDL_Color kButtonFill{0, 0, 8, 255};

// t390: build the title texture once — 0opening.gif index plane through the
// t386 palette, index 255 (the menu key-solid, title-art.md §2) as alpha 0
// so the button column composites on top. False + reason on any refusal
// (no fake art substituted; the frame then renders honestly-vector).
bool buildTitleTexture(SDL_Renderer* ren, const std::string& dataRoot,
                       SDL_Texture** out, std::string* err) {
    ascend::formats::GifFrame fr;
    if (!ascend::formats::gifDecodeFile(
            dataRoot + "/extracted/ascend01/data/0opening.gif", &fr, err))
        return false;
    TitlePalette pal;
    std::string perr;
    if (!pal.load(dataRoot, fr.gct.data(), fr.gct.size(), &perr)) {
        // Palette TSV absent (data-less clone): GCT fallback would be
        // honest-vector but NOT the vendor colours — refuse instead.
        *err = perr;
        return false;
    }
    if (fr.width != kDisplayW || fr.height != kDisplayH) {
        *err = "title gif is not 640x480";
        return false;
    }
    std::vector<uint32_t> argb(fr.indices.size());
    for (size_t i = 0; i < fr.indices.size(); i++) {
        const uint8_t idx = fr.indices[i];
        if (idx == 255) { argb[i] = 0x00000000u; continue; }  // key hole
        argb[i] = 0xFF000000u | (uint32_t(pal.rgb[idx][0]) << 16) |
                  (uint32_t(pal.rgb[idx][1]) << 8) | pal.rgb[idx][2];
    }
    SDL_Texture* tex =
        SDL_CreateTexture(ren, SDL_PIXELFORMAT_ARGB8888,
                          SDL_TEXTUREACCESS_STATIC, int(fr.width),
                          int(fr.height));
    if (!tex) {
        *err = std::string("title texture: ") + SDL_GetError();
        return false;
    }
    SDL_UpdateTexture(tex, nullptr, argb.data(),
                      int(fr.width) * int(sizeof(uint32_t)));
    *out = tex;
    return true;
}
}  // namespace

BootState runTitleScreen(const std::string& dataRoot, BootState initial,
                         int maxIntroFrames, std::string* err,
                         void** windowOut, const std::string& savesDir,
                         AudioEngine* audio) {
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

    // t387: the NEWGAMEWND wheel library loads ONCE (per-frame loading would
    // re-read 27 KB every 16 ms). count()>0 == available; a refusal prints
    // the reason once and the frame renders without the wheel face.
    ascend::formats::ShapeLibrary cfgNew;
    {
        std::string cerr;
        if (!cfgNew.load(dataRoot + "/extracted/ascend01/data/3cfgnew.shp",
                         &cerr))
            std::printf("ui raceconfig backdrop refused: %s\n", cerr.c_str());
        std::fflush(stdout);
    }

    // t390 TITLE ART (docs/re/title-art.md §7): the GIF decodes ONCE and
    // lives as a static texture (the cfgNew pattern). A refusal prints the
    // reason ONCE and the frame renders honestly-vector (no fake art).
    SDL_Texture* titleArt = nullptr;
    {
        std::string aerr;
        if (!buildTitleTexture(ren, dataRoot, &titleArt, &aerr)) {
            std::printf("ui title art refused: %s\n", aerr.c_str());
            std::fflush(stdout);
        } else {
            std::printf("ui title art ok 640x480 key255-hole\n");
            std::fflush(stdout);
        }
    }

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
        // ---- draw: ART first, then the seven-button column in its hole ----
        SDL_SetRenderDrawColor(ren, kTitleBg.r, kTitleBg.g, kTitleBg.b, 255);
        SDL_RenderClear(ren);
        if (titleArt) {
            // The wordmark and creature are INSIDE the GIF (t386 §7) — no
            // text is drawn for them. Index 255 carries alpha 0, so the
            // button column below shows through the key hole.
            SDL_RenderCopy(ren, titleArt, nullptr, nullptr);
        } else {
            // Honestly-vector fallback (pre-t390 render): caption band
            // frame + game name (TITLERECT, subtitle.txt / ui.md §4).
            SDL_Rect band{0, 379, 640, 41};
            SDL_SetRenderDrawColor(ren, kBand.r, kBand.g, kBand.b, 255);
            SDL_RenderDrawRect(ren, &band);
            const std::string name = "ASCENDANCY";
            const int w = txt.width(name, true);
            txt.draw(ren, (kDisplayW - w) / 2, 385, name, true, kInk);
        }
        for (int i = 0; i < kTitleButtonCount; i++) {
            const TitleButton& b = kTitleButtons[i];
            // Band-closure law (measured on the pinned vendor shot): the
            // rect is EXACTLY flat fill + white label; the GIF's key hole
            // is the same rect, so fill before the label either way.
            SDL_Rect r{b.rect.x0, b.rect.y0,
                       b.rect.x1 - b.rect.x0 + 1, b.rect.y1 - b.rect.y0 + 1};
            SDL_SetRenderDrawColor(ren, kButtonFill.r, kButtonFill.g,
                                   kButtonFill.b, 255);
            SDL_RenderFillRect(ren, &r);
            const int w = txt.width(b.label, true);
            txt.draw(ren, b.rect.x0 + (b.rect.x1 - b.rect.x0 - w) / 2,
                     b.rect.y0 + 4, b.label, true, kInk);
        }
        if (st == BootState::RaceConfig) {
            // NEWGAMEWND chrome (windows.txt L575-673, law docs/re/boot.md
            // §6): the TYPE-18 frame + its three state-3 child buttons +
            // the RACELIST frame. Absolute coords — PARENT is containment,
            // not an offset (_wip_t387 coordinate-space witness). The k0
            // wheel face (SHAPEITEM 1 data\3cfgnew.shp 0 0 0) blits inside
            // each child rect; setting the wheel values is a named seam.
            const bool haveCfg = cfgNew.count() > 0;
            SDL_Rect wf{kNewgameWnd.x0, kNewgameWnd.y0,
                        kNewgameWnd.x1 - kNewgameWnd.x0 + 1,
                        kNewgameWnd.y1 - kNewgameWnd.y0 + 1};
            if (haveCfg) {
                // k0 is 84x79, not a window backdrop: draw it centred in the
                // frame as the declared wheel face, frame edges on top.
                blitShape(ren, cfgNew, 0,
                          wf.x + (wf.w - int(cfgNew.record(0).width)) / 2,
                          wf.y + 40);
            }
            SDL_SetRenderDrawColor(ren, kBand.r, kBand.g, kBand.b, 255);
            SDL_RenderDrawRect(ren, &wf);
            SDL_Rect rl{kRaceList.x0, kRaceList.y0,
                        kRaceList.x1 - kRaceList.x0 + 1,
                        kRaceList.y1 - kRaceList.y0 + 1};
            SDL_RenderDrawRect(ren, &rl);  // RACELIST frame (rows = t388 seam)
            for (int i = 0; i < kNewgameControlCount; i++) {
                const NewgameControl& c = kNewgameControls[i];
                if (haveCfg)
                    blitShape(ren, cfgNew, 0, c.rect.x0, c.rect.y0);  // k0 face
                const int w = txt.width(c.label, false);
                txt.draw(ren, c.rect.x0 +
                                 ((c.rect.x1 - c.rect.x0 + 1) - w) / 2,
                         c.rect.y0 + 4, c.label, false, kInk);
            }
            txt.draw(ren, wf.x + 12, wf.y + 8,
                     "New game setup. Press Return to Current Game.", false,
                     kInk);
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
                // t387: NEWGAMEWND child buttons first (absolute rects; they
                // sit OUTSIDE the title column, so bootClick cannot see them).
                // Routing law: the buttons ACKNOWLEDGE (print) — the wheel
                // values feed a campaign-seed seam that does not exist yet.
                if (st == BootState::RaceConfig) {
                    const int ci = newgameControlAt(p);
                    if (ci >= 0) {
                        std::printf("ui raceconfig click %s msg %d\n",
                                    kNewgameControls[ci].name,
                                    kNewgameControls[ci].message);
                        std::fflush(stdout);
                        continue;
                    }
                }
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
                      maxIntroFrames, audio);
            // Vendor law: movie exit -> title. Menu music on the captured
            // selector is track 0 = theme00 (audio.md §3.3: DAT_00010ba0
            // == 0 in every banked save), so the title restores it after
            // the intro tunes; the script's own VOLUME 127 cue (frame 988)
            // has already reset the fade by this point.
            if (audio) audio->playTune(0);
            st = BootState::Title;
        } else if (st == BootState::Tutorial) {
            seamLoop("tutorial driver absent (seam, docs/re/boot.md §3)");
            st = BootState::Title;
        } else if (st == BootState::Load) {
            // t387: real load screen over 4loadgam chrome. The vendor's
            // RESUME.GAM is NOT faked (REFUTED-ROUTES: resume.gam lacks the
            // reference metadata; supply-your-own slots only). An accepted
            // slot prints its pick; importing it into a live Campaign is the
            // named seam (Observer is read-only by contract, t382) — so the
            // screen returns to Title with the pick banked on stdout.
            const std::vector<SaveSlot> slots = listSaveSlots(savesDir);
            const int pick = runLoadScreen(ren, txt, dataRoot, slots);
            if (pick == kLoadQuit) { st = BootState::Quit; break; }
            st = BootState::Title;
        } else if (st == BootState::Save) {
            seamLoop("save chrome lands t388 (STATUSWND)");
            st = BootState::Title;
        }
    }

    txt.release();  // atlases before their renderer
    if (titleArt) SDL_DestroyTexture(titleArt);
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
