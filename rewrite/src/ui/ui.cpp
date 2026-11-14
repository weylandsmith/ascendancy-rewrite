// SPDX-License-Identifier: GPL-3.0-or-later

#include "ui/ui.h"

#include <SDL.h>

#include <cstdio>
#include <vector>

#include "formats/flic.h"
#include "formats/fnt.h"
#include "formats/shp.h"
#include "game/campaign.h"
#include "ui/boot.h"
#include "ui/hudlayout.h"
#include "ui/layout.h"
#include "ui/menulaw.h"
#include "ui/statuslaw.h"
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
                  void* window, const std::string& savesDir) {
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

    // ---- t388: the campaign is a set of vendor SCREENS (state ids) -------
    // Screen law + citations: ui/statuslaw.h, docs/re/_wip_t388.md. Chrome
    // libraries load ONCE (files are 3-40 KB; per-frame reload would be
    // absurd). A screen whose lib refuses to load still draws frame + title
    // (honest degraded chrome, never a blank swap).
    int screen = kScreenMap;
    const char* kLibFiles[4] = {"1starmap.shp", "10status.shp", "14intel.shp",
                                "20res.shp"};
    ascend::formats::ShapeLibrary kLibs[4];
    for (int i = 0; i < 4; i++) {
        std::string lerr;
        if (!kLibs[i].load(dataRoot + "/extracted/ascend01/data/" + kLibFiles[i],
                           &lerr))
            std::printf("ui chrome lib refused %s: %s\n", kLibFiles[i],
                        lerr.c_str());
    }
    std::fflush(stdout);
    // Index into kLibs for a screen, or -1.
    auto libFor = [&](int s) -> int {
        const char* want = screenShapeLib(s);
        if (!want) return -1;
        for (int i = 0; i < 4; i++)
            if (std::string(kLibFiles[i]) == want) return i;
        return -1;
    };
    // FULL-BACKDROP test [measured t388]: the backdrop class (10status k0,
    // 4loadgam k0, 2savegam k0) is a single record at screen size (639x479);
    // 1starmap k0 (158x75), 14intel k0 (18x18) and 20res k0 (15x30) are
    // element art. Only the screen-size record is blitted full-frame;
    // element libs get frame+title chrome instead. Mechanical size test,
    // not a per-file whitelist.
    auto backdropFor = [&](int i) -> bool {
        if (i < 0 || kLibs[i].count() == 0) return false;
        const auto& r = kLibs[i].record(0);
        return r.width >= 600 && r.height >= 400;
    };

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
            else if (ev.type == SDL_KEYDOWN && screen == kScreenMap &&
                     (ev.key.keysym.sym == SDLK_RETURN || ev.key.keysym.sym == SDLK_SPACE)) {
                std::printf("ui key next\n");
                advanceOnce();
            } else if (ev.type == SDL_KEYDOWN && ev.key.keysym.sym == SDLK_ESCAPE) {
                // t388 Escape law (t252 live): inside a screen, Esc returns
                // to the map; on the map it quits (standing port law).
                if (escapeToMap(screen)) {
                    std::printf("ui screen %s -> map (esc)\n",
                                screenTitle(screen));
                    std::fflush(stdout);
                    screen = kScreenMap;
                } else {
                    quit = true;
                }
            } else if (ev.type == SDL_KEYDOWN && (ev.key.keysym.mod & KMOD_ALT)) {
                // t388 PORT ADDITION (labelled): the title-screen D9 chords'
                // twins inside the campaign. windows.txt has NO save/load
                // control on the campaign rail (they are STATE "1 0" title
                // buttons), so this is convenience, not vendor law. Alt-L
                // reuses the t387 load window; Alt-S prints the seam — the
                // rewrite has no campaign-state writer (Observer is
                // read-only by contract, t382).
                const char letter = ev.key.keysym.sym >= SDLK_a &&
                                            ev.key.keysym.sym <= SDLK_z
                                        ? char('a' + (ev.key.keysym.sym - SDLK_a))
                                        : '?';
                if (letter == 'l') {
                    const std::vector<SaveSlot> slots = listSaveSlots(savesDir);
                    const int pick = runLoadScreen(ren, txt, dataRoot, slots);
                    if (pick == kLoadQuit) quit = true;
                } else if (letter == 's') {
                    std::printf("ui save seam: no campaign writer (t382)\n");
                    std::fflush(stdout);
                }
            } else if (ev.type == SDL_MOUSEBUTTONDOWN && ev.button.button == SDL_BUTTON_LEFT) {
                Pt p{ev.button.x, ev.button.y};
                // t388: the rail is the screen switch. railButtonForScreen
                // honours the STATE id-list law, so on a non-map screen no
                // rail button hits at all (vendor: rail hidden inside
                // screens; Escape is the cited way back).
                const auto rb = railButtonForScreen(p, screen);
                if (rb.has_value()) {
                    const RailControl rc = railControl(*rb);
                    const int next =
                        screenAfterRailPress(screen, rc.sendMessage, rc.sendParam1);
                    if (next != screen) {
                        std::printf("ui screen %s -> %s (%s)\n",
                                    screenName(screen), screenName(next),
                                    kRailName[static_cast<int>(*rb)]);
                        std::fflush(stdout);
                        screen = next;
                    } else {
                        // Not a switch (SPECIALAB msg 5) or a target with no
                        // chrome: acknowledge, never guess.
                        std::printf("ui rail %s msg %d p1 %d (no screen change)\n",
                                    kRailName[static_cast<int>(*rb)], rc.sendMessage, rc.sendParam1);
                        std::fflush(stdout);
                    }
                } else if (screen == kScreenMap && inRect(kNextTurnBtn, p)) {
                    // NEXTTURN's STATE is "1 1" (map-only) — same gate.
                    std::printf("ui click next-turn\n");
                    if (audio) audio->play("click08");
                    advanceOnce();
                } else if (screen == kScreenMap && inRect(kCosmosWnd, p)) {
                    // COSMOSWnd's own STATE list excludes the opened screens,
                    // so map selection is inert inside a screen too.
                    // Right-click deselect (selfplay.md) will land HERE once
                    // selection widgets exist — no selection UI this row.
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
        // t388: screen chrome backdrop (see backdropFor for the measured
        // full-backdrop test; the luminance-ramp palette seam is documented
        // on blitShape). Map screen intentionally keeps its vector map (no
        // 1starmap backdrop: its k0 is 158x75 element art, not a backdrop).
        const int lib = backdropFor(libFor(screen)) ? libFor(screen) : -1;
        if (lib >= 0) blitShape(ren, kLibs[lib], 0, 0, 0);

        const bool mapVisible =
            screen == kScreenMap || screen == kScreenSpecies;  // COSMOSWnd
                                                               // "4 1 3 7 13"
        if (mapVisible) {
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
        }  // cosmos (states 1, 7)

        // ---- t388 the rail (x-band 474; STATE id-lists decide activity) --
        // Vendor law: the rail's STATE list is "1 1" (Intelligence "1 7"),
        // so it draws ONLY on its active screen — inside an opened screen
        // there is no rail (t252: Escape returns to galaxy). No dimmed
        // ghosts: an inert button that looks live is the fakery this phase
        // bans. Icons per sidebarIcon (1starmap frames); text-only buttons
        // (RACES WINITEMS 1, Intelligence WINITEMS 0) get none.
        for (int i = 0; i < kRailButtonCount; i++) {
            const RailButton b = static_cast<RailButton>(i);
            if (!railActive(b, screen)) continue;
            const RailControl rc = kRail[i];
            SDL_Rect rr{rc.rect.x0, rc.rect.y0,
                        rc.rect.x1 - rc.rect.x0 + 1, rc.rect.y1 - rc.rect.y0 + 1};
            SDL_SetRenderDrawColor(ren, 40, 40, 56, 255);
            SDL_RenderFillRect(ren, &rr);
            SDL_SetRenderDrawColor(ren, kText.r, kText.g, kText.b, 255);
            SDL_RenderDrawRect(ren, &rr);
            int tx = rr.x + 6;
            // Icons come from 1starmap.shp (the sidebar icon law) — load it
            // for the icon regardless of the screen's own library.
            const int iconLib = libFor(kScreenMap);
            if (const auto icon = sidebarIcon(b); icon && iconLib >= 0) {
                if (blitShape(ren, kLibs[iconLib], icon->frame, rr.x + 4,
                              rr.y + (rr.h - 24) / 2))
                    tx = rr.x + 4 + int(kLibs[iconLib].record(icon->frame).width) + 6;
            }
            txt.draw(ren, tx, rr.y + 8, railLabel(b), false, kText);
        }

        if (screen == kScreenMap) {
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
        } else {
            // ---- opened screen: cited frame + title, content = seams ----
            // Title strip geometry: STATUSWND/INTELSCREEN-family windows put
            // the header at y0..(interior y0 - 12); interior = the child
            // list rect. Ship it per screen (statuslaw.h rects).
            Rect hdr, interior;
            switch (screen) {
                case kScreenStatus: hdr = Rect{kStatusWnd.x0, kStatusWnd.y0, kStatusWnd.x1, 34};
                                    interior = kStatPlanLst; break;
                case kScreenIntel:  hdr = kIntelScreen; interior = kIntelList; break;
                case kScreenFleet:  hdr = Rect{kFleetWnd.x0, kFleetWnd.y0, kFleetWnd.x1, 34};
                                    interior = Rect{7, 46, 632, 472}; break;
                case kScreenResearch: hdr = Rect{kResWin.x0, kResWin.y0, kResWin.x1, kResWin.y1};
                                      interior = kResWin; break;
                case kScreenSpecies: hdr = Rect{};  // NO cited header: the
                                     interior = Rect{}; break;          // menu
                                                                        // is rows
                                                                        // over the
                                                                        // map
                default: hdr = Rect{7, 7, 632, 34}; interior = Rect{7, 46, 632, 472};
            }
            if (hdr.x1 > hdr.x0) {
                SDL_Rect hs{hdr.x0, hdr.y0, hdr.x1 - hdr.x0 + 1,
                            hdr.y1 - hdr.y0 + 1};
                SDL_SetRenderDrawColor(ren, 150, 130, 110, 255);
                SDL_RenderDrawRect(ren, &hs);
                txt.draw(ren, hs.x + 8, hs.y + 6, screenTitle(screen), true, kText);
            }
            if (screen != kScreenSpecies) {
                SDL_Rect is{interior.x0, interior.y0,
                            interior.x1 - interior.x0 + 1, interior.y1 - interior.y0 + 1};
                SDL_SetRenderDrawColor(ren, kLane.r, kLane.g, kLane.b, 255);
                SDL_RenderDrawRect(ren, &is);
            }
            // Species menu: the seven RACE_1..7 row frames (cited rects).
            // Rows are msg 1 p1 13 (NEGSCREEN) — not in the known set, so
            // they render as frames and stay inert (no fake diplomacy).
            if (screen == kScreenSpecies) {
                for (int i = 0; i < 7; i++) {
                    SDL_Rect rr{kRaceRows[i].x0, kRaceRows[i].y0,
                                kRaceRows[i].x1 - kRaceRows[i].x0 + 1,
                                kRaceRows[i].y1 - kRaceRows[i].y0 + 1};
                    SDL_SetRenderDrawColor(ren, kLane.r, kLane.g, kLane.b, 255);
                    SDL_RenderDrawRect(ren, &rr);
                }
                txt.draw(ren, kRaceRows[0].x0, 280,
                         "race rows: NEGSCREEN seam (state 13)", false, kDim);
                txt.draw(ren, kRaceRows[0].x0, 340, "Esc: return to galaxy",
                         false, kDim);
            } else {
                txt.draw(ren, interior.x0 + 8, interior.y0 + 8,
                         "frame + title only: content law seam", false, kDim);
            }
            if (interior.x1 > interior.x0)
                txt.draw(ren, interior.x0 + 8, interior.y1 - 16,
                         "Esc: return to galaxy", false, kDim);
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
