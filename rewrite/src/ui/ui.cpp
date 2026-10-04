#include "ui/ui.h"

#include <SDL.h>
#include <SDL_ttf.h>

#include <cstdio>
#include <vector>

#include "game/campaign.h"
#include "ui/layout.h"

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

struct TextCache {
    TTF_Font* f12 = nullptr;
    TTF_Font* f16 = nullptr;
    bool open(const std::string& path) {
        f12 = TTF_OpenFont(path.c_str(), 12);
        f16 = TTF_OpenFont(path.c_str(), 16);
        return f12 && f16;
    }
    void draw(SDL_Renderer* r, int x, int y, const std::string& s, bool big,
              SDL_Color c) {
        if (s.empty()) return;
        TTF_Font* f = big ? f16 : f12;
        SDL_Surface* su = TTF_RenderUTF8_Blended(f, s.c_str(), c);
        if (!su) return;
        SDL_Texture* t = SDL_CreateTextureFromSurface(r, su);
        SDL_FreeSurface(su);
        if (!t) return;
        SDL_Rect dst{x, y, 0, 0};
        SDL_QueryTexture(t, nullptr, nullptr, &dst.w, &dst.h);
        SDL_RenderCopy(r, t, nullptr, &dst);
        SDL_DestroyTexture(t);
    }
    ~TextCache() {
        if (f12) TTF_CloseFont(f12);
        if (f16) TTF_CloseFont(f16);
    }
};

void filledCircle(SDL_Renderer* r, int cx, int cy, int rad) {
    for (int dy = -rad; dy <= rad; ++dy)
        for (int dx = -rad; dx <= rad; ++dx)
            if (dx * dx + dy * dy <= rad * rad)
                SDL_RenderDrawPoint(r, cx + dx, cy + dy);
}

}  // namespace

int runCampaignUi(ag::Campaign& camp, int turns, bool autoplay,
                  const std::string& fontPath) {
    if (TTF_Init() != 0) {
        std::printf("TTF_Init: %s\n", TTF_GetError());
        return 1;
    }
    TextCache txt;
    if (!txt.open(fontPath)) {
        std::printf("font load failed: %s (%s)\n", fontPath.c_str(), TTF_GetError());
        TTF_Quit();
        return 1;
    }
    SDL_Window* win = SDL_CreateWindow("Ascendancy rewrite (P5a)",
                                       SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
                                       kDisplayW, kDisplayH, SDL_WINDOW_SHOWN);
    if (!win) {
        std::printf("CreateWindow: %s\n", SDL_GetError());
        return 1;  // fonts freed by ~TextCache; see teardown note below
    }
    SDL_Renderer* ren = SDL_CreateRenderer(win, -1, SDL_RENDERER_ACCELERATED);
    if (!ren) ren = SDL_CreateRenderer(win, -1, SDL_RENDERER_SOFTWARE);
    if (!ren) {
        std::printf("CreateRenderer: %s\n", SDL_GetError());
        SDL_DestroyWindow(win);
        return 1;  // ditto
    }

    CosmosView view;  // mapSize default matches MapConfig default (layout.h)
    int selected = -1;
    int played = 0;
    Uint32 nextAuto = autoplay ? SDL_GetTicks() + 250 : 0xFFFFFFFFu;
    bool quit = false;

    auto advanceOnce = [&] {
        if (!camp.over()) {
            camp.advance();
            ++played;
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
                    advanceOnce();
                } else if (inRect(kCosmosWnd, p)) {
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
    SDL_DestroyRenderer(ren);
    SDL_DestroyWindow(win);
    // NOTE: no TTF_Quit here — `txt` (which holds the open fonts) destructs
    // AFTER this function returns; calling TTF_Quit before it segfaulted
    // (caught by the Xvfb UI smoke, 2026-10-04). TTF shares one init ref
    // across the process and the fonts are closed by ~TextCache.
    return 0;
}

}  // namespace ascend::ui
