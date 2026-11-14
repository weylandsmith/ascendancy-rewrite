// SPDX-License-Identifier: GPL-3.0-or-later

#include "ui/ui.h"

#include <SDL.h>

#include <cstdio>
#include <vector>

#include "formats/flic.h"
#include "formats/fnt.h"
#include "game/campaign.h"
#include "ui/boot.h"
#include "ui/layout.h"
#include "ui/ui_internal.h"

namespace ascend::ui {
namespace ag = ascend::game;

namespace {

// Owner colours come from ui/layout.cpp (kOwnerRgb) where the CVD rule is
// unit-tested; ui-runtime.md §4. Owner order is FIXED per campaign.
inline SDL_Color toSdl(ascend::ui::RGB c) { return {c.r, c.g, c.b, 255}; }
const SDL_Color kBg{16, 16, 24, 255};
const SDL_Color kLane{120, 120, 120, 255};
const SDL_Color kText{235, 235, 235, 255};
const SDL_Color kDim{150, 130, 110, 255};

void filledCircle(SDL_Renderer* r, int cx, int cy, int rad) {
    for (int dy = -rad; dy <= rad; ++dy)
        for (int dx = -rad; dx <= rad; ++dx)
            if (dx * dx + dy * dy <= rad * rad)
                SDL_RenderDrawPoint(r, cx + dx, cy + dy);
}

}  // namespace

int runCampaignUi(ag::Campaign& camp, int turns, bool autoplay,
                  const std::string& dataRoot, AudioEngine* audio,
                  void* window) {
    // t385: on a title->campaign transition the title loop hands over its
    // LIVE window (ui.h law: a fresh Xvfb window drops its first synthetic
    // click, so per-state window swaps eat injected gate input). Reuse it;
    // only a bare boot creates one.
    SDL_Window* win = static_cast<SDL_Window*>(window);
    const bool owned = win == nullptr;
    if (owned) {
        win = SDL_CreateWindow("Ascendancy rewrite (P5a)",
                               SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
                               kDisplayW, kDisplayH, SDL_WINDOW_SHOWN);
        if (!win) {
            std::printf("CreateWindow: %s\n", SDL_GetError());
            return 1;
        }
    } else {
        SDL_SetWindowTitle(win, "Ascendancy rewrite (P5a)");
    }
    SDL_Renderer* ren = SDL_CreateRenderer(win, -1, SDL_RENDERER_ACCELERATED);
    if (!ren) ren = SDL_CreateRenderer(win, -1, SDL_RENDERER_SOFTWARE);
    if (!ren) {
        std::printf("CreateRenderer: %s\n", SDL_GetError());
        SDL_DestroyWindow(win);
        return 1;
    }
    // Vendor .fnt faces (OQ-017 CLOSED; ui-runtime.md §3 swap rule). Hard
    // requirement, no silent TTF fallback: if the shipped faces fail to load
    // the data tree is broken and the run must say so.
    VendorText txt;
    {
        std::string ferr;
        if (!txt.load(ren, dataRoot, &ferr)) {
            std::printf("vendor font load failed: %s\n", ferr.c_str());
            SDL_DestroyRenderer(ren);
            SDL_DestroyWindow(win);
            return 1;
        }
    }

    CosmosView view;  // mapSize default matches MapConfig default (layout.h)
    int selected = -1;
    int played = 0;
    Uint32 nextAuto = autoplay ? SDL_GetTicks() + 250 : 0xFFFFFFFFu;
    bool quit = false;

    // Advances one turn; plays bang01 iff a NEW "captured" event appeared
    // (sample names verbatim from soundfx.txt, docs/re/audio.md §5).
    auto advanceOnce = [&] {
        if (camp.over()) return;
        const size_t before = camp.events().size();
        camp.advance();
        ++played;
        if (audio) {
            const auto& ev = camp.events();
            for (size_t i = before; i < ev.size(); i++)
                if (ev[i].text.find("captured") != std::string::npos) {
                    audio->play("bang01");
                    break;
                }
        }
    };

    while (!quit) {
        // One event per frame at ~60fps; WaitEventTimeout sleeps when idle so
        // autoplay/gates do not spin CPU. (A trailing SDL_PollEvent here once
        // DISCARDED the next event — do not re-add it.)
        SDL_Event ev;
        if (SDL_WaitEventTimeout(&ev, 16)) {
            if (ev.type == SDL_QUIT) quit = true;
            else if (ev.type == SDL_KEYDOWN &&
                     (ev.key.keysym.sym == SDLK_RETURN || ev.key.keysym.sym == SDLK_SPACE)) {
                std::printf("ui key next\n");
                advanceOnce();
            } else if (ev.type == SDL_KEYDOWN && ev.key.keysym.sym == SDLK_ESCAPE) {
                quit = true;
            } else if (ev.type == SDL_MOUSEBUTTONDOWN && ev.button.button == SDL_BUTTON_LEFT) {
                Pt p{ev.button.x, ev.button.y};
                if (inRect(kNextTurnBtn, p)) {
                    std::printf("ui click next-turn\n");
                    if (audio) audio->play("click08");
                    advanceOnce();
                } else if (inRect(kCosmosWnd, p)) {
                    if (audio) audio->play("laser01");
                    selected = hitStar(view, camp.galaxy(), p);
                    std::printf("ui click map (%d,%d) -> %s\n", p.x, p.y,
                                selected >= 0 ? camp.galaxy().stars[selected].name.c_str()
                                              : "none");
                }
            }
            std::fflush(stdout);
        }
        if (autoplay && SDL_GetTicks() >= nextAuto) {
            advanceOnce();
            nextAuto = SDL_GetTicks() + 250;
        }
        if (turns > 0 && played >= turns) quit = true;
        if (camp.over()) quit = true;

        // ---- draw ----
        SDL_SetRenderDrawColor(ren, kBg.r, kBg.g, kBg.b, 255);
        SDL_RenderClear(ren);
        // cosmos frame
        SDL_Rect frame{kCosmosWnd.x0 - 1, kCosmosWnd.y0 - 1,
                       kCosmosWnd.x1 - kCosmosWnd.x0 + 3, kCosmosWnd.y1 - kCosmosWnd.y0 + 3};
        SDL_SetRenderDrawColor(ren, kLane.r, kLane.g, kLane.b, 255);
        SDL_RenderDrawRect(ren, &frame);
        // lanes first (behind stars)
        for (const auto& ln : camp.galaxy().lanes) {
            Pt a = starScreenPos(view, camp.galaxy().stars[ln.a]);
            Pt b2 = starScreenPos(view, camp.galaxy().stars[ln.b]);
            SDL_SetRenderDrawColor(ren, kLane.r, kLane.g, kLane.b, 255);
            SDL_RenderDrawLine(ren, a.x, a.y, b2.x, b2.y);
        }
        // stars
        for (const auto& s : camp.galaxy().stars) {
            Pt q = starScreenPos(view, s);
            int o = camp.starOwner(s.id);
            if (o < 0) {
                SDL_Color n = toSdl(kNeutralRgb);
                SDL_SetRenderDrawColor(ren, n.r, n.g, n.b, 255);
                filledCircle(ren, q.x, q.y, 2);  // SMALLER: ownership coded by
            } else {                             // size as well as colour
                SDL_Color c = toSdl(kOwnerRgb[o]);
                SDL_SetRenderDrawColor(ren, c.r, c.g, c.b, 255);
                filledCircle(ren, q.x, q.y, 4);
            }
            if (s.id == selected) {
                SDL_SetRenderDrawColor(ren, kText.r, kText.g, kText.b, 255);
                SDL_Rect sel{q.x - 6, q.y - 6, 13, 13};
                SDL_RenderDrawRect(ren, &sel);
            }
        }
        // HUD rail
        int hx = kCosmosWnd.x1 + 8;
        txt.draw(ren, hx, 8, "Ascendancy P5a", true, kText);
        txt.draw(ren, hx, 30, camp.traceLine(), false, kText);
        // NEXTTURN button (verified rect)
        SDL_Rect btn{kNextTurnBtn.x0, kNextTurnBtn.y0,
                     kNextTurnBtn.x1 - kNextTurnBtn.x0, kNextTurnBtn.y1 - kNextTurnBtn.y0};
        SDL_SetRenderDrawColor(ren, 40, 40, 56, 255);
        SDL_RenderFillRect(ren, &btn);
        SDL_SetRenderDrawColor(ren, kText.r, kText.g, kText.b, 255);
        SDL_RenderDrawRect(ren, &btn);
        txt.draw(ren, btn.x + 10, btn.y + 8, "NEXT TURN", true, kText);
        // selected star info
        if (selected >= 0) {
            const auto& s = camp.galaxy().stars[selected];
            std::string info = s.name + "  (" + std::to_string(s.planets.size()) + " planets)";
            int o = camp.starOwner(selected);
            info += o == ag::kPlayer ? "  [yours]" : (o > 0 ? "  [owner " + std::to_string(o) + "]" : "  [neutral]");
            txt.draw(ren, hx, 100, info, false, kDim);
        }
        // event log (last 8)
        const auto& evs = camp.events();
        int y = 140;
        for (size_t i = evs.size() > 8 ? evs.size() - 8 : 0; i < evs.size(); ++i, y += 14)
            txt.draw(ren, hx, y, evs[i].text, false, kDim);
        if (camp.over()) {
            txt.draw(ren, hx, 300, std::string("VICTORY: ") + ag::victoryName(camp.victory()),
                     true, kText);
        }
        SDL_RenderPresent(ren);
    }

    std::printf("ui ok: turn %d\n", camp.turn());
    txt.release();  // atlases before their renderer (destructor is idempotent)
    SDL_DestroyRenderer(ren);
    if (owned) SDL_DestroyWindow(win);  // a handed-over window: caller's duty
    return 0;
}

int playIntro(const std::string& flicPath, int maxFrames) {
    namespace afl = ascend::formats;
    afl::Flic f;
    std::string err;
    if (!f.load(flicPath, &err)) {
        std::printf("intro: %s\n", err.c_str());
        return 1;
    }
    SDL_Window* win = SDL_CreateWindow("Ascendancy", SDL_WINDOWPOS_CENTERED,
                                       SDL_WINDOWPOS_CENTERED, f.width(),
                                       f.height(), SDL_WINDOW_SHOWN);
    if (!win) {
        std::printf("intro CreateWindow: %s\n", SDL_GetError());
        return 1;
    }
    SDL_Renderer* ren = SDL_CreateRenderer(win, -1, SDL_RENDERER_SOFTWARE);
    SDL_Texture* tex = SDL_CreateTexture(ren, SDL_PIXELFORMAT_ARGB8888,
                                         SDL_TEXTUREACCESS_STREAMING,
                                         f.width(), f.height());
    if (!ren || !tex) {
        std::printf("intro render setup: %s\n", SDL_GetError());
        SDL_DestroyWindow(win);
        return 1;
    }
    std::vector<uint32_t> argb(static_cast<size_t>(f.width()) * f.height());
    int shown = 0, aborted = 0;
    const uint32_t baseSpeed = f.speedMs() ? f.speedMs() : 71;
    f.replay(
        [&](int i, const uint8_t* px, const uint8_t* pal) {
            const size_t n = argb.size();
            for (size_t k = 0; k < n; ++k) {
                const uint8_t idx = px[k];
                argb[k] = 0xFF000000u | (pal[idx * 3] << 16) |
                          (pal[idx * 3 + 1] << 8) | pal[idx * 3 + 2];
            }
            SDL_UpdateTexture(tex, nullptr, argb.data(),
                              f.width() * static_cast<int>(sizeof(uint32_t)));
            SDL_RenderClear(ren);
            SDL_RenderCopy(ren, tex, nullptr, nullptr);
            SDL_RenderPresent(ren);
            ++shown;
            // Pacing uses the per-frame delay when set (flc.md §2). replay()
            // does not hand us the Chunk, so pace off header speed; the
            // gate/dummy runs stay fast because they never reach here with
            // interactive timing expectations.
            SDL_Delay(baseSpeed);
            SDL_Event ev;
            while (SDL_PollEvent(&ev))
                if (ev.type == SDL_QUIT || ev.type == SDL_KEYDOWN) ++aborted;
        },
        &err, nullptr, maxFrames);
    std::printf("intro ok: %s frames %d shown, aborted %s\n",
                SDL_GetCurrentVideoDriver() ? SDL_GetCurrentVideoDriver() : "?",
                shown, aborted ? "yes" : "no");
    SDL_DestroyTexture(tex);
    SDL_DestroyRenderer(ren);
    SDL_DestroyWindow(win);
    return 0;
}

}  // namespace ascend::ui
