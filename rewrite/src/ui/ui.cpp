// SPDX-License-Identifier: GPL-3.0-or-later

#include "ui/ui.h"

#include <SDL.h>

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <vector>

#include "formats/flic.h"
#include "formats/fnt.h"
#include "formats/shp.h"
#include "game/campaign.h"
#include "ui/boot.h"
#include "ui/cam3d.h"
#include "ui/hudlayout.h"
#include "ui/layout.h"
#include "ui/menulaw.h"
#include "ui/mapchrome.h"
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

int ipow10(int e) { int v = 1; while (e-- > 0) v *= 10; return v; }

// t394 WM-SCALE FIX (D10 "everything small/wonky"; diagnosis _wip_t394.md
// S1): the user's WM rescales our 640x480 window to 512x384. SDL's own
// header law (SDL_render.h:805-810, "Set a device independent resolution
// for rendering"): with a logical size set, "mouse and touch events in the
// window will be filtered and scaled so they seem to arrive within the
// logical resolution" — which is exactly the hit-map fix (every windows.txt
// rect is logical). Rendering letterboxes/scales to whatever the WM gives
// us; SDL_HINT_RENDER_LOGICAL_SIZE_MODE is left at its documented default
// ("letterbox", SDL_hints.h:1942). Applied to EVERY window we create.
void applyLogicalSize(SDL_Renderer* ren) {
    SDL_RenderSetLogicalSize(ren, kDisplayW, kDisplayH);
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
    applyLogicalSize(ren);  // t394 WM-scale fix (see helper for the law)
    // t398: chrome palette (game.pal) for every blitShape colour path.
    loadChromePalette(dataRoot);
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

    // t399: 3D field camera (cam3d.h; vendor affine+pinhole law cited there)
    // + the TOGLANES layer state (windows.txt ln342 control; default ON —
    // lanes are drawn, subject to the t192 visibility law).
    Camera3d cam;
    cam.mapSize = 1024;  // MapConfig default (mapgen.h)
    bool lanesOn = true;
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
    // t400: raceflag.shp (21 x 14x24 species flags for the Species rail
    // row; law ui/hudlayout.h). Refusal just drops the two flags.
    ascend::formats::ShapeLibrary raceflagLib;
    {
        std::string ferr;
        if (!raceflagLib.load(dataRoot + "/extracted/ascend01/data/raceflag.shp",
                              &ferr))
            std::printf("ui raceflag lib refused: %s\n", ferr.c_str());
    }
    // t400 FRAME TEXTURE (mapchrome.h law): one static texture over the
    // measured bands (alpha 0 elsewhere), built ONCE — 87k draw-points per
    // frame would be absurd. Deterministic per pixel (no rng_).
    SDL_Texture* frameTex = nullptr;
    {
        frameTex = SDL_CreateTexture(ren, SDL_PIXELFORMAT_ARGB8888,
                                     SDL_TEXTUREACCESS_STATIC, kDisplayW,
                                     kDisplayH);
        if (frameTex) {
            std::vector<uint32_t> px(size_t(kDisplayW) * kDisplayH, 0u);
            for (int b = 0; b < kTextureBandCount; b++)
                for (int y = kTextureBands[b].y0; y <= kTextureBands[b].y1; y++)
                    for (int x = kTextureBands[b].x0; x <= kTextureBands[b].x1; x++) {
                        const RGB c = textureColourAt(x, y);
                        px[size_t(y) * kDisplayW + x] =
                            0xFF000000u | (uint32_t(c.r) << 16) |
                            (uint32_t(c.g) << 8) | c.b;
                    }
            SDL_UpdateTexture(frameTex, nullptr, px.data(),
                              kDisplayW * int(sizeof(uint32_t)));
        }
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
                } else if (screen == kScreenMap && inRect(kNextTurnCont, p)) {
                    // t394 NEXTTURNCONT (msg 8, ln556): the vendor's mid-turn
                    // combat-continue pump. The port's advance() runs a full
                    // turn with no pause, so there is nothing to continue —
                    // NAMED SEAM: inert with a printed line, never a fake.
                    std::printf("ui click next-turn-cont seam (no mid-turn pause model)\n");
                } else if (screen == kScreenMap && mapCtlFor(p)) {
                    // t399: the cluster DRIVES the camera (msg numbers cited
                    // in mapchrome.cpp; behaviour law cam3d.h). Per-click
                    // step is the documented default (vendor continuous
                    // right-drag, help.txt 1spin, not implemented).
                    switch (*mapCtlFor(p)) {
                        case MapCtl::RotRight: cam.rotate(+1); break;
                        case MapCtl::RotLeft:  cam.rotate(-1); break;
                        case MapCtl::RotUp:    cam.tilt(+1); break;
                        case MapCtl::RotDown:  cam.tilt(-1); break;
                        case MapCtl::ZoomIn:   cam.zoom(+1); break;
                        case MapCtl::ZoomOut:  cam.zoom(-1); break;
                        case MapCtl::CenterHolo: cam.reset(); break;
                        case MapCtl::TogLanes: lanesOn = !lanesOn; break;
                        default:
                            // TOGEMPIRE/TOGSHIPS/TOGCOLONIES: the port has
                            // no ship/colony overlay layers yet — named
                            // seam, printed, never a fake toggle.
                            std::printf("ui click map-ctl seam (msg %d)\n",
                                        kMapCtl[static_cast<int>(*mapCtlFor(p))].sendMessage);
                    }
                    std::printf("ui cam yaw %.2f pitch %.2f focal %.0f lanes %d\n",
                                cam.yaw, cam.pitch, cam.focal, lanesOn ? 1 : 0);
                } else if (screen == kScreenMap && kRaceControlsFrame.x0 <= p.x &&
                           inRect(kRaceControlsFrame, p)) {
                    std::printf("ui click race-controls seam (slot %s)\n",
                                raceSlotFor(p) ? std::to_string(*raceSlotFor(p) + 1).c_str()
                                               : "frame");
                } else if (screen == kScreenMap && inRect(kTurnCount, p)) {
                    // TURNCOUNT MOUSEFOCUS 0 (ln525): inert by the table.
                } else if (screen == kScreenMap && inRect(kCosmosWnd, p)) {
                    // COSMOSWnd's own STATE list excludes the opened screens,
                    // so map selection is inert inside a screen too.
                    // Right-click deselect (selfplay.md) will land HERE once
                    // selection widgets exist — no selection UI this row.
                    if (audio) audio->play("laser01");
                    selected = hitStarCam(cam, camp.galaxy(), p);
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
        // t400: the map screen's frame texture (mapchrome.h law — measured
        // on the vendor map shot; opened screens have no texture witness,
        // so it is drawn on the map ONLY, honestly-degraded elsewhere).
        if (frameTex && screen == kScreenMap)
            SDL_RenderCopy(ren, frameTex, nullptr, nullptr);
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
        // ---- t399: THE 3D FIELD (D11 headline). Every galaxy star renders
        // (count == galaxy count; the vendor builder adds stars
        // UNCONDITIONALLY, ships.md S23 L9 star side). Lanes follow the
        // CITED visibility law: an empire sees ONLY lanes incident to stars
        // it owns (t192 new-game witness; SA_KnowStarLanes widens through
        // laneVisibleTo) — at game start that is exactly the lanes leading
        // off the home systems. Projection law = cam3d.h (vendor affine
        // FUN_00053324 + pinhole FUN_00053374).
        {
            // cosmos frame (same anchor as t394: rect +1 outset) + the field
            // clip: zoomed-in stars beyond the frame must not paint the rail.
            SDL_Rect frame{kCosmosWnd.x0 - 1, kCosmosWnd.y0 - 1,
                           kCosmosWnd.x1 - kCosmosWnd.x0 + 3,
                           kCosmosWnd.y1 - kCosmosWnd.y0 + 3};
            SDL_SetRenderDrawColor(ren, kLane.r, kLane.g, kLane.b, 255);
            SDL_RenderDrawRect(ren, &frame);
            SDL_RenderSetClipRect(ren, &frame);
        }
        if (lanesOn) {
            for (size_t li = 0; li < camp.galaxy().lanes.size(); ++li) {
                if (!camp.laneVisibleTo(int(li), ag::kPlayer)) continue;
                const auto& ln = camp.galaxy().lanes[li];
                Pt a = projectStar(cam, camp.galaxy().stars[ln.a]);
                Pt b2 = projectStar(cam, camp.galaxy().stars[ln.b]);
                SDL_SetRenderDrawColor(ren, kLane.r, kLane.g, kLane.b, 255);
                SDL_RenderDrawLine(ren, a.x, a.y, b2.x, b2.y);
            }
        }
        {
            const int home = camp.homeStarFor(ag::kPlayer);
            // far pips first so nearer ones paint over them (depth order)
            std::vector<int> order(camp.galaxy().stars.size());
            for (size_t i = 0; i < order.size(); ++i) order[i] = int(i);
            std::sort(order.begin(), order.end(), [&](int a, int b) {
                return viewDepth(cam, camp.galaxy().stars[a]) >
                       viewDepth(cam, camp.galaxy().stars[b]);
            });
            for (int sid : order) {
                const auto& s = camp.galaxy().stars[sid];
                Pt q = projectStar(cam, s);
                const int o = camp.starOwner(s.id);
                const bool owned = o >= 0;
                const int r = pipRadius(depthClass(double(s.z)), owned);
                if (owned) {
                    SDL_Color c = toSdl(kOwnerRgb[o]);
                    SDL_SetRenderDrawColor(ren, c.r, c.g, c.b, 255);
                } else {
                    SDL_Color c = toSdl(neutralTint(s.type));
                    SDL_SetRenderDrawColor(ren, c.r, c.g, c.b, 255);
                }
                filledCircle(ren, q.x, q.y, r);
                if (s.id == home) {
                    // HOME MARKER [named seam shape]: the vendor original
                    // shows a distinct marker at the player's system
                    // (external vision read, scratchpad/galaxymap-original
                    // .png); the record is unmapped, so the port rings it —
                    // shape + colour redundancy (CVD law).
                    SDL_SetRenderDrawColor(ren, 255, 255, 255, 255);
                    SDL_Rect hm{q.x - r - 3, q.y - r - 3, 2 * (r + 3) + 1,
                                2 * (r + 3) + 1};
                    SDL_RenderDrawRect(ren, &hm);
                }
                if (s.id == selected) {
                    SDL_SetRenderDrawColor(ren, kText.r, kText.g, kText.b, 255);
                    SDL_Rect sel{q.x - 6, q.y - 6, 13, 13};
                    SDL_RenderDrawRect(ren, &sel);
                }
            }
        }
        SDL_RenderSetClipRect(ren, nullptr);  // end field clip
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
            // t400: vendor rail fill MEASURED (12,32,48) == game.pal idx 242
            // (palette.md §4; the t398 witness's single outside colour was
            // this port's own (40,40,56)). The raceflag faces' dominant
            // colour is the same value — they blit seamlessly on it.
            SDL_SetRenderDrawColor(ren, 12, 32, 48, 255);
            SDL_RenderFillRect(ren, &rr);
            SDL_SetRenderDrawColor(ren, kText.r, kText.g, kText.b, 255);
            SDL_RenderDrawRect(ren, &rr);
            int tx = rr.x + 6;
            // Icons come from 1starmap.shp (the sidebar icon law) — load it
            // for the icon regardless of the screen's own library.
            const int iconLib = libFor(kScreenMap);
            // t400 PLACEMENT LAW (hudlayout.h): x = rect.x0 + dx(109) = RIGHT
            // of the label, native size, vertically centred. The old code
            // painted at rr.x+4 (LEFT) — the D11 "wrong side" defect.
            if (const auto icon = sidebarIcon(b); icon && iconLib >= 0) {
                const IconPos ip =
                    railIconPos(b, int(kLibs[iconLib].record(icon->frame).height));
                if (blitShape(ren, kLibs[iconLib], icon->frame, ip.x, ip.y)) {
                    // label keeps its left slot; the icon sits right of it
                } else {
                    tx = rr.x + 4 + int(kLibs[iconLib].record(icon->frame).width) + 6;
                }
            }
            txt.draw(ren, tx, rr.y + 8, railLabel(b), false, kText);
            // t400 SPECIES FLAGS (hudlayout.h law): RACES has no SHAPEITEM
            // yet the vendor shows two 14x24 raceflag faces right of the
            // label (measured runs x521..552). Left = player species
            // (-1 human -> no flag exists, slot stays empty honestly);
            // right = first AI specnum (0, skipping the player's).
            if (b == RailButton::Races && raceflagLib.count() > 0) {
                const int ps = camp.playerSpecies();
                int right = 0;
                if (right == ps) right = 1;
                if (ps >= 0 && ps < int(raceflagLib.count()))
                    blitShape(ren, raceflagLib, ps, kSpeciesFlagSlots[0].rect.x0,
                              kSpeciesFlagSlots[0].rect.y0);
                if (right < int(raceflagLib.count()))
                    blitShape(ren, raceflagLib, right, kSpeciesFlagSlots[1].rect.x0,
                              kSpeciesFlagSlots[1].rect.y0);
            }
        }

        if (screen == kScreenMap) {
        // ---- t394 VENDOR SIDEBAR CHROME (mapchrome.h; windows.txt state-1
        // records verbatim; rects MEASURED on the user-supplied original).
        // The old string dump ("Ascendancy P5a / turn|stars|score / events")
        // is REMOVED per D10: the vendor map screen has no stats string —
        // TURNCOUNT (TYPE 15, ln521) carries the turn as five LARGE DIGITS.
        // 1) TURNCOUNT panel 474,7-632,43 + five digit slots MEASURED at x
        //    482/513/544/575/606 (pitch 31, y10..39). t399 CLOSED the t394
        //    named seam: the DIGITFRAMES 55 faces 1starmap k55..k64 map
        //    IDENTITY to digits 0..9 — measured decode (scripts/
        //    t399_digit_faces.py): k56 is uniquely the narrow face (w=18 vs
        //    >=24) and reads as '1'. Faces render VENDOR ART through
        //    game.pal (t398), 1:1, clipped to the panel; the oval
        //    OUTLINES are GONE (D11: "green circles ... with smaller numbers
        //    inside" was the defect; original = large green numbers, dark
        //    box, thin border — external vision read of the supplied
        //    original). No lib: big VendorText face in green, never ovals.
        {
            SDL_Rect panel{kTurnCount.x0, kTurnCount.y0,
                           kTurnCount.x1 - kTurnCount.x0 + 1,
                           kTurnCount.y1 - kTurnCount.y0 + 1};
            SDL_SetRenderDrawColor(ren, 0, 0, 0, 255);
            SDL_RenderFillRect(ren, &panel);
            SDL_SetRenderDrawColor(ren, 0, 200, 80, 255);  // LED green frame
            SDL_RenderDrawRect(ren, &panel);
            const int turn = camp.turn();
            const int faceLib = libFor(kScreenMap);
            // faces are 33..35 px tall vs the 30 px slot: blit 1:1 centred
            // on the slot and CLIP to the panel (vendor faces never spill
            // over the box border; k64's descender is inside the panel).
            SDL_RenderSetClipRect(ren, &panel);
            for (int i = 0; i < 5; i++) {
                const OvalSlot& o = kOvalSlots[i];
                const int d = (turn / ipow10(4 - i)) % 10;  // right-aligned
                const int rec = kDigitFirstFrame + d;
                bool art = false;
                if (faceLib >= 0 && kLibs[faceLib].count() > rec) {
                    const auto& fr = kLibs[faceLib].record(rec);
                    const int ox = (o.x0 + o.x1 - int(fr.width)) / 2;
                    const int oy = (o.y0 + o.y1 - int(fr.height)) / 2;
                    art = blitShape(ren, kLibs[faceLib], rec, ox, oy);
                }
                if (!art) {
                    std::string ds(1, char('0' + d));
                    const int cx = (o.x0 + o.x1) / 2;
                    txt.draw(ren, cx - txt.width(ds, true) / 2, o.y0 + 1, ds,
                             true, SDL_Color{0, 230, 90, 255});
                }
            }
            SDL_RenderSetClipRect(ren, nullptr);
        }
        // 2) NEXTTURN / NEXTTURNCONT faces (SHAPEFRAME 65/66 verbatim;
        //    1starmap k65 74x30 / k66 75x30 EXACT size match of the rects).
        {
            const int iconLib = libFor(kScreenMap);
            const SDL_Rect a{kNextTurnBtn.x0, kNextTurnBtn.y0,
                             kNextTurnBtn.x1 - kNextTurnBtn.x0 + 1,
                             kNextTurnBtn.y1 - kNextTurnBtn.y0 + 1};
            const SDL_Rect b{kNextTurnCont.x0, kNextTurnCont.y0,
                             kNextTurnCont.x1 - kNextTurnCont.x0 + 1,
                             kNextTurnCont.y1 - kNextTurnCont.y0 + 1};
            if (iconLib >= 0 &&
                blitShape(ren, kLibs[iconLib], kNextTurnShape, a.x, a.y) &&
                blitShape(ren, kLibs[iconLib], kNextTurnContShape, b.x, b.y)) {
                // art-backed: faces carry the vendor label art
            } else {  // honest degraded chrome, same rects
                SDL_SetRenderDrawColor(ren, 24, 48, 96, 255);
                SDL_RenderFillRect(ren, &a);
                SDL_RenderFillRect(ren, &b);
                SDL_SetRenderDrawColor(ren, kText.r, kText.g, kText.b, 255);
                SDL_RenderDrawRect(ren, &a);
                SDL_RenderDrawRect(ren, &b);
                txt.draw(ren, a.x + 10, a.y + 8, "NEXT TURN", true, kText);
                txt.draw(ren, b.x + 6, b.y + 8, "END TURN", true, kText);
            }
        }
        // 3) spin/zoom/toggle cluster (COSMOSWnd children ln223-414,
        //    SHAPEFRAMEs 8..18 -> 1starmap; DRAW cited, pan/zoom BEHAVIOUR is
        //    the named seam — CosmosView has no scroll model to drive).
        {
            const int iconLib = libFor(kScreenMap);
            for (int i = 0; i < kMapCtlCount; i++) {
                const MapControl& mc = kMapCtl[i];
                SDL_Rect r{mc.rect.x0, mc.rect.y0,
                           mc.rect.x1 - mc.rect.x0 + 1,
                           mc.rect.y1 - mc.rect.y0 + 1};
                if (!(iconLib >= 0 && blitShape(ren, kLibs[iconLib],
                                                mc.shapeFrame, r.x, r.y))) {
                    SDL_SetRenderDrawColor(ren, 40, 40, 56, 255);
                    SDL_RenderFillRect(ren, &r);
                    SDL_SetRenderDrawColor(ren, kText.r, kText.g, kText.b, 255);
                    SDL_RenderDrawRect(ren, &r);
                }
            }
        }
        // 4) RACECONTROLS strip 474,442-632,472 (SHAPEFRAME 19 = 1starmap
        //    k19 158x30; MEASURED slot-1 square 479,448-495,465 == table).
        //    Slot SQUARES carry species colour — vendor palette is the named
        //    luminance seam, so the port's CVD-safe kOwnerRgb fills them.
        {
            const int iconLib = libFor(kScreenMap);
            if (!(iconLib >= 0 && blitShape(ren, kLibs[iconLib],
                                            kRaceControlsShape,
                                            kRaceControlsFrame.x0,
                                            kRaceControlsFrame.y0))) {
                SDL_Rect f{kRaceControlsFrame.x0, kRaceControlsFrame.y0,
                           kRaceControlsFrame.x1 - kRaceControlsFrame.x0 + 1,
                           kRaceControlsFrame.y1 - kRaceControlsFrame.y0 + 1};
                SDL_SetRenderDrawColor(ren, 20, 20, 28, 255);
                SDL_RenderFillRect(ren, &f);
                SDL_SetRenderDrawColor(ren, kText.r, kText.g, kText.b, 255);
                SDL_RenderDrawRect(ren, &f);
            }
            for (int i = 0; i < 7; i++) {
                const RaceSlot& rs = kRaceSlots[i];
                SDL_Rect r{rs.rect.x0, rs.rect.y0,
                           rs.rect.x1 - rs.rect.x0 + 1,
                           rs.rect.y1 - rs.rect.y0 + 1};
                const RGB c = kOwnerRgb[i];
                SDL_SetRenderDrawColor(ren, c.r, c.g, c.b, 255);
                SDL_RenderFillRect(ren, &r);
                SDL_SetRenderDrawColor(ren, 0, 0, 0, 255);
                SDL_RenderDrawRect(ren, &r);
            }
        }
        // Selection info (PORT SEAM: the vendor shows a colony panel here,
        // unmapped; a single dim line inside the cosmos interior).
        if (selected >= 0) {
            const auto& s = camp.galaxy().stars[selected];
            std::string info = s.name + "  (" + std::to_string(s.planets.size()) + " planets)";
            int o = camp.starOwner(selected);
            info += o == ag::kPlayer ? "  [yours]" : (o > 0 ? "  [owner " + std::to_string(o) + "]" : "  [neutral]");
            txt.draw(ren, kCosmosWnd.x0 + 6, kCosmosWnd.y1 - 16, info, false, kDim);
        }
        if (camp.over()) {
            txt.draw(ren, kCosmosWnd.x0 + 6, kCosmosWnd.y1 - 34,
                     std::string("VICTORY: ") + ag::victoryName(camp.victory()),
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

int playIntro(const std::string& flicPath, int maxFrames, AudioEngine* audio) {
    namespace afl = ascend::formats;
    afl::Flic f;
    std::string err;
    if (!f.load(flicPath, &err)) {
        std::printf("intro: %s\n", err.c_str());
        return 1;
    }
    // SUBTITLE.TXT cue table (the vendor subtitle script for this movie;
    // law + addresses docs/re/audio.md §6). DIGITALMUSIC lines carry the
    // 1-based music.txt TUNEIDs (6, 7); we address our own loaded table
    // (audio.cpp trackNames: 0 theme00, 1 intro00, 2 intro01).
    struct Cue {
        int frame;   // FRAMENUMBER verbatim from subtitle.txt
        int tune;    // playTune index, or -1 = none
        int volume;  // vendor 0..127 scale, or -1 = none
    };
    static const Cue kCues[] = {
        {20, 1, -1},    // DIGITALMUSIC TUNEID 6  -> intro00 (bulk of movie)
        {966, -1, 100}, // FADEMUSIC VOLUME ramp (CHANNEL 0): fade tune 6 out
        {971, -1, 80},
        {976, -1, 60},
        {981, -1, 30},
        {988, -1, 127}, // VOLUME 127 restore — same frame as...
        {988, 2, -1},   // DIGITALMUSIC TUNEID 7  -> intro01 (movie tail)
    };
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
            // Cue firing uses the frame JUST SHOWN (1-based: replay() hands
            // 0-based indices, subtitle.txt FRAMENUMBER counts from 1).
            if (audio) {
                const int shown1 = i + 1;
                for (const Cue& c : kCues) {
                    if (c.frame != shown1) continue;
                    if (c.tune >= 0) audio->playTune(c.tune);
                    if (c.volume >= 0) audio->setMusicVolume(c.volume);
                }
            }
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
