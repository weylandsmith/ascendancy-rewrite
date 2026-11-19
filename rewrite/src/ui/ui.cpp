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
#include "ui/statusbg.h"
#include "ui/statuslaw.h"
#include "ui/planetwin.h"
#include "ui/statuslist.h"
#include "ui/planetview.h"
#include "ui/abilitylaw.h"
#include "ui/speciesmenu.h"
#include "ui/fleetlist.h"
#include "ui/researchview.h"
#include "ui/exitpopup.h"
#include "ui/sysview.h"
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

// t418b: F2 tile diamond 68x34 (x cx±0x22, y cy±0x11 — the corners the
// paint body pushes at 0x3c224/0x3c252/0x3bc78). Scanline fill; the hit
// region matches tileHitFor's |dx|/34+|dy|/17<=1 law exactly.
void filledDiamond(SDL_Renderer* r, int cx, int cy) {
    for (int dy = -17; dy <= 17; ++dy) {
        const int half = 34 - 2 * std::abs(dy);  // |dy|/17 + |dx|/34 <= 1
        SDL_RenderDrawLine(r, cx - half, cy + dy, cx + half, cy + dy);
    }
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
                  void* window, const std::string& savesDir,
                  const std::vector<ag::SpeciesInfo>* roster) {
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
    Uint32 lastPumpMs = 0, lastSysPumpMs = 0;  // t416 pump cadence
    cam.mapSize = 1024;  // MapConfig default (mapgen.h)
    bool lanesOn = kCtlDefaultLanes;
    // t425 TOGGLE LAYER STATE [verified msg map 0x26b34 + BUTTONSTATE
    // defaults in windows.txt ln360-414]: TOGSHIPS BS 1, TOGCOLONIES BS 1,
    // TOGEMPIRE BS 0 (the vendor's empire overlay starts OFF).
    bool shipsOn = kCtlDefaultShips, coloniesOn = kCtlDefaultColonies,
         empireOn = kCtlDefaultEmpire;
    // t425 RACE FILTER MASK (vendor byte[win+0xd8], init 0xff at 0x271b4;
    // msg 62 toggles bit (1<<slot); consumer 0x27258 skips a race's records
    // when its bit is clear). bit i == race slot i VISIBLE.
    unsigned raceVisibleMask = kRaceFilterInit;
    int selected = -1;
    // t402 PLANETS LIST screen state: scroll step + selected row (indices
    // into statusPlanets(); selection is PORT law — the vendor row click
    // opens the planet detail screen (state 17), which the port does not
    // have yet: the selection marker is shown and the seam printed).
    int statusScroll = 0;
    int statusSel = -1;
    // t406 PLANET VIEW (state 17) session state: the planet the list opened
    // (star + display name) and whether the PLBUILD->PLANLIST project list
    // is open (planet.txt info04: clicking the Project Display shows the
    // list; an order closes it).
    int planetStar = -1;
    std::string planetName;
    bool projectOpen = false;
    // t418b SURFACE TILE GRID session state: the tile the player selected
    // (surface cell index into planetAt(planetStar); -1 = none). The vendor
    // PLSQUARE child (windows.txt ln1520) takes the cell click as the build
    // CELL selection feeding the fn 0x38840 cmd0 cell leg; the port's order
    // lands item-only (planetview.h), so the selection drives the F3
    // adjacency REPORT (orderCellBlock) + the tile outline.
    int planetCell = -1;
    // t407 FLEET LIST (state 18) session state: scroll step + selected row
    // (index into fleetRows()). The vendor LEFT click jumps the camera to
    // the ship (help fleetwin + t253 live); the port SELECTS + logs instead
    // — named seam, no fake camera move. RIGHT click deselects per the
    // selfplay.md RIGHT-CLICK DESELECT law (user testimony + live witness
    // 2026-11-11: "right-click ... to clear the ship selection").
    int fleetScroll = 0;
    int fleetSel = -1;
    // t408 RESEARCH VIEW (state 20) session state: the tree-field pan
    // offsets (px). The four pan buttons are windows.txt children OUTSIDE
    // the RESWIN rect (msg 50..53); rotate pair pans X, move pair pans Y
    // (t252 pixel-diff). No clamp law exists in vendor data -> the offsets
    // are unbounded [labelled port choice]; nodes derive from them purely.
    int resPanX = 0, resPanY = 0;
    // t419 RESEARCH 3D: dedicated camera on the t416 basis law (latch +
    // pump). focal == kResStandoff makes the REST projection scale-exact
    // 1:1 with the t408 2D law (researchview.h 3D LAW). The rotate dials
    // pressSpin; the move pair scrolls resPanY (user spec).
    Camera3d resCam;
    resCam.focal = kResStandoff;
    resCam.bounds = kResWin;
    Uint32 lastResPumpMs = 0;
    // t419 corner "Exit <ESC>" popup state (ui/exitpopup.h): the corner the
    // cursor currently probes into (None = hidden).
    ExitCorner exitCorner = ExitCorner::None;
    ascend::formats::ShapeLibrary mouseLib;
    {
        std::string merr;
        if (!mouseLib.load(dataRoot + "/extracted/ascend01/data/mouse.shp",
                           &merr))
            std::printf("ui mouse lib refused: %s\n", merr.c_str());
    }
    // t409 ABILITY DIALOG session state: the SPECIALAB press opens the
    // ABILITYWIN modal (ui/abilitylaw.h — vendor msg-5 path 0x55ffb ->
    // 0x37b14: sprintf("abil%02d") of the PLAYER SPECIES into ABILITYWIN,
    // then WAIT). Modal: while open, clicks inside the full window rect are
    // the ABILBUTTON msg-50 dismiss (both buttons cover 60,100-395,355),
    // clicks outside are inert, Escape also dismisses.
    bool abilityOpen = false;
    // t410 THE SCREEN STACK (ui/sysview.h): the chain the owner never found.
    // The map is the bottom level; a star click pushes the System Display
    // (state 16, t338-measured entry), a colonised-dot click pushes the
    // planet view (state 17, planet.txt info00 route 1); Escape pops ONE
    // level (t252 pixel-diff law). `systemCam` is the view's own camera over
    // kBatModeWnd (same vendor pinhole law as the galaxy field, cam3d.h);
    // `gridOn` is the TOGGRID state (port default ON — t244 wireframe
    // witness). Rail presses REPLACE the top level (the rail is only live
    // on states 1/7 anyway — the STATE lists say so).
    ScreenStack stack(kScreenMap);
    // `screen` stays the single read variable (every transition site below
    // updates BOTH it and the stack; a reference to topRef() would dangle
    // the first time push() resizes the vector).
    int screen = stack.top();
    Camera3d systemCam;
    systemCam.bounds = kBatModeWnd;
    // FIT LAW (pinned test_sysview_t410): at the DEFAULT focal (zs=1) the
    // outer ring of a 5-body system is orbitRadius(4) = 60+34*4 = 196 px,
    // inside the kBatModeWnd half-height (472-7)/2 = 232. Zoom is user-driven.
    bool gridOn = true;
    int played = 0;
    Uint32 nextAuto = autoplay ? SDL_GetTicks() + 250 : 0xFFFFFFFFu;
    bool quit = false;

    // ---- t388: the campaign is a set of vendor SCREENS (state ids) -------
    // Screen law + citations: ui/statuslaw.h, docs/re/_wip_t388.md. Chrome
    // libraries load ONCE (files are 3-40 KB; per-frame reload would be
    // absurd). A screen whose lib refuses to load still draws frame + title
    // (honest degraded chrome, never a blank swap).
    // (t410: `screen` is the ScreenStack top reference, declared above.)
    // t402: planets.shp joins the set for the PLANETS LIST row spheres
    // (55 records = 11 groups x 5-size ladder 11/18/25/35/47, shp.md S23.3
    // — the group/size axes match the status row's type/size words; the
    // group law itself is a NAMED SEAM, see the row painter).
    // t427: suns.shp joins the set — THE ROW SUN (init 0x51954 resolves
    // "DATA\\suns.shp" into the row-paint slot global; selector = raw star
    // type, count 13 == the 13 starstat types; docs/re/_wip_t427.md F1/F2).
    // t406: 17np.shp joins the set — the PLANETALLOC backdrop candidate
    // (k0 639x479, decoded this session, docs/re/_wip_t406.md F6).
    // t410: 16battle.shp joins the set — the SYSTEM VIEW console faces
    // (TYPE-100 STATENUMBER 16 ln1140-1142; dims census _wip_t410 F3: the
    // lib has NO backdrop record, so backdropFor() declines it and only the
    // SHAPEFRAME-identified faces blit).
    const char* kLibFiles[8] = {"1starmap.shp", "10status.shp", "14intel.shp",
                                "20res.shp", "planets.shp", "17np.shp",
                                "16battle.shp", "suns.shp"};
    ascend::formats::ShapeLibrary kLibs[8];
    for (int i = 0; i < 8; i++) {
        std::string lerr;
        if (!kLibs[i].load(dataRoot + "/extracted/ascend01/data/" + kLibFiles[i],
                           &lerr))
            std::printf("ui chrome lib refused %s: %s\n", kLibFiles[i],
                        lerr.c_str());
    }
    // t418b PLANET-VIEW ART libs: planalNN.shp (11 libs x 5 recs, dims
    // ladder 47/75/103/140/189 verified this session from the directories —
    // the size axis is cited, the terrainRow->lib axis is the [inferred] F4
    // seam) is THE PLANET PICTURE; planitem.shp (40 x ~33px, record index ==
    // itemIdx, shp.md S23.4 1:1 pixel-match law) is the structure art ON the
    // tiles. Refusal degrades to bare tiles (never a blank screen swap).
    ascend::formats::ShapeLibrary planalLibs[11];
    for (int i = 0; i < 11; i++) {
        char fname[32];
        std::snprintf(fname, sizeof(fname), "planal%02d.shp", i);
        std::string lerr;
        if (!planalLibs[i].load(dataRoot + "/extracted/ascend01/data/" + fname,
                                &lerr))
            std::printf("ui planal lib refused %s: %s\n", fname,
                        lerr.c_str());
    }
    ascend::formats::ShapeLibrary planitemLib;
    {
        std::string lerr;
        if (!planitemLib.load(dataRoot + "/extracted/ascend01/data/planitem.shp",
                              &lerr))
            std::printf("ui planitem lib refused: %s\n", lerr.c_str());
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
    // t409 ABILITY DIALOG panels (ui/abilitylaw.h): the help.txt abilNN
    // blocks that the vendor's msg-5 opener sprintf's into ABILITYWIN.
    // Refusal = the Special Ability press logs the seam and no-ops (never
    // a blank/garbled modal).
    std::vector<AbilityPanel> abilityPanels;
    {
        std::string aerr;
        if (!loadAbilityPanels(dataRoot + "/extracted/ascend00/help.txt",
                               &abilityPanels, &aerr)) {
            std::printf("ui ability panels refused: %s\n", aerr.c_str());
            abilityPanels.clear();
        }
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
    // t417b STATUS BACKDROP TEXTURES [measured law ui/statusbg.h]: the
    // status screen's perimeter bands (four edges, textureColourAt family)
    // and the header speckle band (per-pixel weighted census F5), each
    // built ONCE (18k+ draw-dots per frame would be absurd). Deterministic
    // per pixel; no engine rng_. Alpha 0 everywhere else.
    SDL_Texture* statusPerimTex = nullptr;
    SDL_Texture* statusSpeckleTex = nullptr;
    {
        statusPerimTex = SDL_CreateTexture(ren, SDL_PIXELFORMAT_ARGB8888,
                                          SDL_TEXTUREACCESS_STATIC,
                                          kDisplayW, kDisplayH);
        if (statusPerimTex) {
            std::vector<uint32_t> px(size_t(kDisplayW) * kDisplayH, 0u);
            for (int b = 0; b < kStatusTextureBandCount; b++)
                for (int y = kStatusTextureBands[b].y0;
                     y <= kStatusTextureBands[b].y1; y++)
                    for (int x = kStatusTextureBands[b].x0;
                         x <= kStatusTextureBands[b].x1; x++) {
                        const RGB c = textureColourAt(x, y);
                        px[size_t(y) * kDisplayW + x] =
                            0xFF000000u | (uint32_t(c.r) << 16) |
                            (uint32_t(c.g) << 8) | c.b;
                    }
            SDL_UpdateTexture(statusPerimTex, nullptr, px.data(),
                              kDisplayW * int(sizeof(uint32_t)));
        }
        statusSpeckleTex = SDL_CreateTexture(
            ren, SDL_PIXELFORMAT_ARGB8888, SDL_TEXTUREACCESS_STATIC,
            kStatusSpeckleRect.x1 - kStatusSpeckleRect.x0 + 1,
            kStatusSpeckleRect.y1 - kStatusSpeckleRect.y0 + 1);
        if (statusSpeckleTex) {
            const int w = kStatusSpeckleRect.x1 - kStatusSpeckleRect.x0 + 1;
            std::vector<uint32_t> px(size_t(w) *
                                         (kStatusSpeckleRect.y1 -
                                          kStatusSpeckleRect.y0 + 1),
                                     0u);
            for (int y = kStatusSpeckleRect.y0; y <= kStatusSpeckleRect.y1;
                 y++)
                for (int x = kStatusSpeckleRect.x0; x <= kStatusSpeckleRect.x1;
                     x++) {
                    const RGB c = statusSpeckleAt(x, y);
                    px[size_t(y - kStatusSpeckleRect.y0) * w +
                       (x - kStatusSpeckleRect.x0)] =
                        0xFF000000u | (uint32_t(c.r) << 16) |
                        (uint32_t(c.g) << 8) | c.b;
                }
            SDL_UpdateTexture(statusSpeckleTex, nullptr, px.data(),
                              w * int(sizeof(uint32_t)));
        }
    }
    // t410 HOME-STAR DIAGNOSTIC (display-only, zero rng): the projected
    // home-star pixel under the DEFAULT camera, printed once so a witness
    // can click the map->system-view entry without guessing a pip.
    {
        const int hs = camp.homeStarFor(ag::kPlayer);
        if (hs >= 0 && hs < int(camp.galaxy().stars.size())) {
            const Pt hp = projectStar(cam, camp.galaxy().stars[size_t(hs)]);
            std::printf("ui home star %s at %d,%d\n",
                        camp.galaxy().stars[size_t(hs)].name.c_str(), hp.x,
                        hp.y);
            std::fflush(stdout);
        }
    }
    // Index into kLibs for a screen, or -1.
    auto libFor = [&](int s) -> int {
        const char* want = screenShapeLib(s);
        if (!want) return -1;
        for (int i = 0; i < 8; i++)
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
                if (const char* sfx = sfxForEvent(ev[i].text)) {
                    audio->play(sfx);  // t404: sfxForEvent law (audio.md §5)
                    break;
                }
        }
    };

    // t425: the Escape CHAIN factored out so the corner "Exit <ESC>" popup
    // click performs the SAME action the glyph names (t419 drew it; the D17
    // grade row: "corner popup drawn but INERT"). t409 modal precedence +
    // t410 one-level unwind + quit-at-bottom, verbatim.
    auto doEscape = [&] {
        if (abilityOpen) {
            abilityOpen = false;
            std::printf("ui ability dialog dismiss (esc)\n");
            std::fflush(stdout);
        } else if (stack.escape()) {
            const int from = screen;
            screen = stack.top();
            std::printf("ui screen %s -> %s (esc)\n",
                        screenName(from), screenName(screen));
            std::fflush(stdout);
        } else {
            quit = true;
        }
    };

    while (!quit) {
        // One event per frame at ~60fps; WaitEventTimeout sleeps when idle so
        // autoplay/gates do not spin CPU. (A trailing SDL_PollEvent here once
        // DISCARDED the next event — do not re-add it.)
        SDL_Event ev;
        const bool gotEvent = SDL_WaitEventTimeout(&ev, 16) != 0;
        if (gotEvent) {
            if (ev.type == SDL_QUIT) quit = true;
            else if (ev.type == SDL_KEYDOWN && screen == kScreenMap &&
                     !abilityOpen &&  // t409: the modal waits (vendor CALL
                                       // 0x37b14 blocks; keys are inert)
                     (ev.key.keysym.sym == SDLK_RETURN || ev.key.keysym.sym == SDLK_SPACE)) {
                std::printf("ui key next\n");
                advanceOnce();
            } else if (ev.type == SDL_KEYDOWN && ev.key.keysym.sym == SDLK_ESCAPE) {
                doEscape();
            } else if (ev.type == SDL_KEYDOWN && (ev.key.keysym.mod & KMOD_ALT) &&
                       !abilityOpen) {  // t409 modal: chords inert too
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
                if (abilityOpen) {
                    // t409 MODAL LAW: ABILBUTTON0/1 both cover the full
                    // ABILITYWIN rect (windows.txt ln2152-2185) — any click
                    // inside dismisses (msg 50 family); outside, the click
                    // is inert (the vendor waits; nothing else is live).
                    if (abilityDialogHit(p.x, p.y)) {
                        abilityOpen = false;
                        std::printf("ui ability dialog dismiss\n");
                        std::fflush(stdout);
                    }
                } else if (exitCornerFor(p.x, p.y, kDisplayW, kDisplayH) != ExitCorner::None &&
                           inRect(exitPopupRect(exitCornerFor(p.x, p.y, kDisplayW, kDisplayH),
                                                kDisplayW, kDisplayH), p)) {
                    // t425 CORNER POPUP ACTIVATION (D17: "corner popup drawn
                    // but INERT (no action)"). The glyph literally names the
                    // action — "Exit <ESC>" — so the click performs the
                    // Escape chain verbatim (modal dismiss / one-level
                    // unwind / quit at the bottom).
                    std::printf("ui corner exit popup click\n");
                    std::fflush(stdout);
                    doEscape();
                } else {
                // t388: the rail is the screen switch. railButtonForScreen
                // honours the STATE id-list law, so on a non-map screen no
                // rail button hits at all (vendor: rail hidden inside
                // screens; Escape is the cited way back).
                const auto rb = railButtonForScreen(p, screen);
                if (rb.has_value()) {
                    // t404: rail presses click like every other button press
                    // (sfxForPress law; owner pin "rail click click08").
                    if (const char* sfx = sfxForPress(UiPressSite::RailButton))
                        if (audio) audio->play(sfx);
                    const RailControl rc = railControl(*rb);
                    const int next =
                        screenAfterRailPress(screen, rc.sendMessage, rc.sendParam1);
                    if (next != screen) {
                        std::printf("ui screen %s -> %s (%s)\n",
                                    screenName(screen), screenName(next),
                                    kRailName[static_cast<int>(*rb)]);
                        std::fflush(stdout);
                        stack.push(next);  // t410: replaces the top level if
                        screen = next;     // already present (no duplicates)
                    } else if (rb == RailButton::SpecialAbility &&
                               rc.sendMessage == 5) {
                        // t409 msg 5 IS WIRED in the vendor (never a silent
                        // no-op): the winmgr path looks ABILITYWIN up by
                        // name and the opener fills it with the PLAYER
                        // SPECIES' help.txt abilNN panel, then waits
                        // (ui/abilitylaw.h, docs/re/_wip_t409.md F2).
                        const int abIdx = int(camp.abilityOf(ag::kPlayer));
                        if (abIdx >= 0 && panelForIndex(abilityPanels, abIdx)) {
                            abilityOpen = true;
                            std::printf("ui ability dialog open (abil%02d)\n",
                                        abIdx);
                        } else {
                            // Human player (-1) or panels refused: the
                            // vendor always has a species row; the port
                            // says so instead of guessing a panel.
                            std::printf("ui ability dialog seam: no player "
                                        "species panel (ability %d)\n", abIdx);
                        }
                        std::fflush(stdout);
                    } else {
                        // Not a switch (SPECIALAB msg 5) or a target with no
                        // chrome: acknowledge, never guess.
                        std::printf("ui rail %s msg %d p1 %d (no screen change)\n",
                                    kRailName[static_cast<int>(*rb)], rc.sendMessage, rc.sendParam1);
                        std::fflush(stdout);
                    }
                } else if (screen == kScreenSpecies) {
                    // t409: a race-row press. The vendor sends msg 1 p1 13
                    // (NEGSCREEN); the port has no state-13 chrome, so the
                    // t388 known-set law makes it inert — but the press is
                    // LOGGED (witness surface), and an Extinct row prints
                    // the highlight-only law (help.txt:775, diplomacy.md
                    // §21.3).
                    const auto rows = speciesMenuRows(camp, roster);
                    for (size_t i = 0; i < rows.size() && i + 1 < 7; i++) {
                        const Rect& slot = kRaceRows[i + 1];
                        if (p.x >= slot.x0 && p.x <= slot.x1 &&
                            p.y >= slot.y0 && p.y <= slot.y1) {
                            std::printf("ui species row %s (%s)\n",
                                        rows[i].extinct ? "Extinct - highlight only"
                                                        : rows[i].name.c_str(),
                                        "NEGSCREEN state 13 seam");
                            std::fflush(stdout);
                            break;
                        }
                    }
                } else if (screen == kScreenStatus &&
                           statusHitFor(p, kStatusRowsTop).kind != StatusHit::None) {
                    // t405 UNIFIED HIT-MAP (statuslist.h): arrows own their
                    // measured art rects; the scrollbar column is inert
                    // (None); rows own the table left of x 619. Replaces the
                    // three-branch chain whose 566-wide arrows + unbounded
                    // row test swallowed every rail-position click (D13).
                    const auto h = statusHitFor(p, kStatusRowsTop);
                    if (h.kind == StatusHit::ArrowUp) {
                        statusScroll = std::max(0, statusScroll - 1);
                        std::printf("ui status scroll up %d\n", statusScroll);
                    } else if (h.kind == StatusHit::ArrowDown) {
                        ++statusScroll;  // statusWindow clamps
                        std::printf("ui status scroll down %d\n", statusScroll);
                    } else {
                        const auto all = statusPlanets(camp, ag::kPlayer);
                        const auto win = statusWindow(all, statusScroll);
                        if (h.row < int(win.size())) {
                            statusSel = statusScroll + h.row;
                            // t406: the row click OPENS the planet view
                            // (state 17) — planet.txt info05: from the
                            // Planets screen "click on either the planet or
                            // the star to go directly to them". (The old
                            // line printed a state-17 seam instead.)
                            const auto& key = win[h.row];
                            const auto& s = camp.galaxy().stars[key.star];
                            planetStar = key.star;
                            planetName = key.planetIndex < int(s.planets.size())
                                             ? s.planets[key.planetIndex].name
                                             : s.name;
                            projectOpen = false;
                            planetCell = -1;  // t418b: fresh tile selection
                            stack.push(kScreenPlanet);  // t410: chain level
                            screen = kScreenPlanet;
                            std::printf("ui status select %s -> planet view "
                                        "(state 17)\n", planetName.c_str());
                        }
                    }
                } else if (screen == kScreenStatus) {
                    // t405: clicks the unified map rejects (outside the
                    // table, scroll column) are SILENT and inert — the
                    // D13 fall-through (rail-position clicks scrolling the
                    // list) is closed by the hit-map, not by a sound.
                } else if (screen == kScreenFleet &&
                           fleetHitFor(p, kFleetRowsTop).kind !=
                               FleetHit::None) {
                    // t407 FLEET LIST hit-map (fleetlist.h): arrows own
                    // their measured boxes, the scroll column is inert, rows
                    // own x 7..605. Rejected points fall through silent —
                    // MapClick law (t404): the list interior is not a sound.
                    const auto h = fleetHitFor(p, kFleetRowsTop);
                    if (h.kind == FleetHit::ArrowUp) {
                        fleetScroll = std::max(0, fleetScroll - 1);
                        std::printf("ui fleet scroll up %d\n", fleetScroll);
                    } else if (h.kind == FleetHit::ArrowDown) {
                        ++fleetScroll;  // fleetWindow clamps
                        std::printf("ui fleet scroll down %d\n", fleetScroll);
                    } else {
                        const auto all = fleetRows(camp, ag::kPlayer);
                        const auto win = fleetWindow(all, fleetScroll);
                        if (h.row < int(win.size())) {
                            fleetSel = fleetScroll + h.row;
                            // PORT seam (labelled): the vendor row click
                            // JUMPS the camera to the ship (help fleetwin,
                            // t253 live (200,93)); the port has no per-ship
                            // position (t256c) — select + log, never fake
                            // the jump.
                            std::printf("ui fleet select row %d\n", fleetSel);
                        }
                    }
                    std::fflush(stdout);
                } else if (screen == kScreenResearch && camp.researchTree() &&
                           researchHit(*camp.researchTree(),
                                       researchNodes(camp, *camp.researchTree(),
                                                     ag::kPlayer),
                                       p.x, p.y, resPanX, resPanY, resCam)
                                   .kind != ResHit::None) {
                    // t408 RESEARCH hit-map (researchview.h): the four pan
                    // buttons (windows.txt msg 50..53, OUTSIDE the RESWIN
                    // rect) first, then the node grid. Click law = help
                    // reswin: an Available ("empty disk") node SETS the
                    // study topic; Owned = dossier read; Blocked = silent.
                    const auto& tree = *camp.researchTree();
                    const auto nodes = researchNodes(camp, tree, ag::kPlayer);
                    const auto h = researchHit(tree, nodes, p.x, p.y,
                                               resPanX, resPanY, resCam);
                    bool panned = true;
                    switch (h.kind) {
                        // t419: the rotate pair LATCHES the camera spin on
                        // the t416 press law (vendor msg 50/51 == the cosmos
                        // dial msgs; pump signs +1/-1), the move pair
                        // SCROLLS (user spec "up/down"; t252 pixel-diff).
                        case ResHit::RotLeft:  resCam.pressSpin(+1); break;
                        case ResHit::RotRight: resCam.pressSpin(-1); break;
                        case ResHit::MoveUp:   resPanY += 78; break;
                        case ResHit::MoveDown: resPanY -= 78; break;
                        case ResHit::Node: {
                            panned = false;
                            const std::string tname = tree.all()[h.row].name;
                            if (setStudy(camp, tree, ag::kPlayer, h.row))
                                std::printf("ui research study %s\n",
                                            tname.c_str());
                            else if (camp.techRowOwnedFor(ag::kPlayer, h.row))
                                std::printf("ui research readout %s\n",
                                            tname.c_str());
                            // Blocked: SILENT (no capture shows reject
                            // feedback; MapClick law t404).
                            break;
                        }
                        default: panned = false; break;
                    }
                    if (panned)
                        std::printf("ui research pan %d %d\n", resPanX,
                                    resPanY);
                    std::fflush(stdout);
                } else if (screen == kScreenPlanet && projectOpen &&
                           projectRowFor(p, 0)) {
                    // t406 PROJECT SET leg 2: pick from the PLANLIST. The
                    // order law (fn 0x38840 cmd0 gates) lives in
                    // Campaign::orderProject / ui/planetview.h; a gate
                    // failure is a SILENT reject (vendor shape, SOUNDCHANNEL
                    // 0 on every PLANETALLOC child).
                    const int item = *projectRowFor(p, 0);
                    const auto opts = projectOptionsFor(camp, planetStar);
                    if (item >= 0 && item < int(opts.size())) {
                        const bool ok =
                            camp.orderProject(planetStar, opts[item].item);
                        // t418b: the F3 adjacency leg REFUSES at the vendor's
                        // checker, not at orderProject's cmd0 gates — when a
                        // tile is selected and the pick would touch an ACTIVE
                        // neighbour, report the refuse (the port's order is
                        // item-only, so this is the honesty line, never a
                        // fake rollback).
                        const auto blk = orderCellBlock(
                            camp, planetStar, opts[item].item, planetCell);
                        std::printf("ui planet project %s %s (%s%s)\n",
                                    planetName.c_str(), opts[item].name.c_str(),
                                    ok ? "ordered" : "rejected",
                                    ok && blk == OrderCellBlock::ActiveNeighbour
                                        ? ", cell refuses: active neighbour"
                                        : "");
                        std::fflush(stdout);
                        if (ok) projectOpen = false;
                    }
                } else if (screen == kScreenPlanet && !projectOpen &&
                           planetStar >= 0 &&
                           !inRect(kPlanetPanels[4].rect, p)) {
                    // t418b TILE SELECT: the PLSQUARE cell click (vendor
                    // planet.txt info02 "individual squares on which
                    // structures may be built"). Diamond hit-map (F2).
                    const auto& ptt2 = camp.terrainTables();
                    const int sz2 = ag::Campaign::sizeClassFor(
                        camp.planetAt(planetStar).surfaceCells);
                    const int hit =
                        sz2 >= 0
                            ? tileHitFor(ptt2, sz2,
                                         camp.planetAt(planetStar).surfaceCells,
                                         p)
                            : -1;
                    if (hit >= 0) {
                        planetCell = hit;
                        std::printf("ui planet tile %d selected\n", hit);
                        std::fflush(stdout);
                    }
                } else if (screen == kScreenPlanet &&
                           inRect(kPlanetPanels[4].rect, p)) {
                    // PLBUILD "Project Display" click opens the project list
                    // (planet.txt info04). Sound: click08 per the sfxForPress
                    // button law (PORT: the vendor panel's SOUNDCHANNEL is 0;
                    // the owner's t404 pin covers rail/next-turn/title only).
                    projectOpen = !projectOpen;
                    std::printf("ui planet project-list %s\n",
                                projectOpen ? "open" : "closed");
                } else if (screen == kScreenMap && inRect(kNextTurnBtn, p)) {
                    // NEXTTURN's STATE is "1 1" (map-only) — same gate.
                    std::printf("ui click next-turn\n");
                    if (const char* sfx = sfxForPress(UiPressSite::NextTurn))
                        if (audio) audio->play(sfx);
                    advanceOnce();
                } else if (screen == kScreenMap && inRect(kNextTurnCont, p)) {
                    // t394 NEXTTURNCONT (msg 8, ln556): the vendor's mid-turn
                    // combat-continue pump. The port's advance() runs a full
                    // turn with no pause, so there is nothing to continue —
                    // NAMED SEAM: inert with a printed line, never a fake.
                    std::printf("ui click next-turn-cont seam (no mid-turn pause model)\n");
                } else if (screen == kScreenMap && mapCtlFor(p)) {
                    // t416 DIAL LAW (D15 fix; cam3d.h citations): a dial
                    // press LATCHES continuous motion (vendor wnd+0xc0 bit
                    // pairs, handler chain 0x27da2..0x279eb) — click starts
                    // the spin, click again stops it, the opposite dial
                    // flips direction. The pump (vendor msg 0x3b @0x27a18;
                    // port SDL_GetTicks below) applies 2 DEG/tick about
                    // WORLD Y (spin pair) / WORLD X (tilt pair). Signs
                    // verbatim from the pump: ROTLEFT +2 / ROTRIGHT -2 /
                    // ROTUP -2 / ROTDOWN +2.
                    switch (*mapCtlFor(p)) {
                        case MapCtl::RotRight: cam.pressSpin(-1); break;
                        case MapCtl::RotLeft:  cam.pressSpin(+1); break;
                        case MapCtl::RotUp:    cam.pressTilt(-1); break;
                        case MapCtl::RotDown:  cam.pressTilt(+1); break;
                        case MapCtl::ZoomIn:   cam.pressZoom(+1); break;
                        case MapCtl::ZoomOut:  cam.pressZoom(-1); break;
                        case MapCtl::CenterHolo: cam.reset(); break;
                        case MapCtl::TogLanes: lanesOn = !lanesOn; break;
                        case MapCtl::TogEmpire:
                        case MapCtl::TogShips:
                        case MapCtl::TogColonies:
                            // t425 MSG MAP [verified, handler 0x26b34]:
                            // TOGEMPIRE(60)->toggle dword[win+0x58a];
                            // TOGSHIPS(58)->toggle dword[win+0xc8];
                            // TOGCOLONIES(61)->toggle dword[win+0xd0] AND
                            // dword[win+0xcc] (0x27b29/0x27d40/0x27cce
                            // sete/dec pairs). Init 0x2718c sets c8/cc/d0 =
                            // -1 (visible); 0x58a takes its default from
                            // BUTTONSTATE (windows.txt: EMPIRE 0, the other
                            // three 1). The port's overlay layers: SHIPS =
                            // the transit-fleet pips (campaign.fleet(), the
                            // port's entire ship state, campaign.h:284);
                            // COLONIES = star-owner tinting; EMPIRE = the
                            // lane web's owner colouring. Each toggle flips
                            // REAL state and repaints — no printed-only seam.
                            if (*mapCtlFor(p) == MapCtl::TogShips)
                                shipsOn = !shipsOn;
                            else if (*mapCtlFor(p) == MapCtl::TogColonies)
                                coloniesOn = !coloniesOn;
                            else
                                empireOn = !empireOn;
                            break;
                    }
                    std::printf("ui cam yaw %.2f pitch %.2f focal %.0f lanes %d ships %d colonies %d empire %d\n",
                                cam.yawLog(), cam.pitchLog(), cam.focal,
                                lanesOn ? 1 : 0, shipsOn ? 1 : 0,
                                coloniesOn ? 1 : 0, empireOn ? 1 : 0);
                } else if (screen == kScreenMap && kRaceControlsFrame.x0 <= p.x &&
                           inRect(kRaceControlsFrame, p)) {
                    // t425 RACE FILTER LAW [verified]: RACECONTROLS sends
                    // msg 62 (windows.txt ln424); handler 0x27824 toggles
                    // byte[win+0xd8] bit dl, where dl is the RACE<N>CONTROL
                    // row's bit column (ln429-435: bits 1,2,4,8,16,32,64 ==
                    // 1<<slot). Consumer 0x27258..0x272ac skips every record
                    // of a race whose bit is clear. t425b S-f UPDATE: the
                    // vendor's per-race COLOUR is DATA-DRIVEN — the star
                    // paint site 0x29980 reads race-record byte +2 (row =
                    // 0x12e16 + 0x1ee*i, base VALIDATED by the +0 == i and
                    // diagonal-0 anchors, scripts/t425b_race_probe.py) and
                    // indexes a table with 0x10 + 4*byte; the byte census
                    // [0,1,6,2,1] is NON-INJECTIVE so byte+2 is NOT a colour
                    // permutation and the permutation stays UNRESOLVED
                    // (docs/re/_wip_t425.md F6, honest negative). The port's
                    // analog: slot i == owner index i (kOwnerRgb order), so a
                    // cleared slot hides that owner's star tint and fleet pips.
                    if (const auto slot = raceSlotFor(p)) {
                        raceVisibleMask ^= (1u << *slot);
                        std::printf("ui race filter slot %d mask 0x%02x\n",
                                    *slot + 1, raceVisibleMask);
                        std::fflush(stdout);
                    } else {
                        std::printf("ui click race-controls seam (slot %s)\n", "frame");
                    }
                } else if (screen == kScreenMap && inRect(kTurnCount, p)) {
                    // TURNCOUNT MOUSEFOCUS 0 (ln525): inert by the table.
                } else if (screen == kScreenMap && inRect(kCosmosWnd, p)) {
                    // COSMOSWnd's own STATE list excludes the opened screens,
                    // so map selection is inert inside a screen too.
                    // Right-click deselect (selfplay.md) will land HERE once
                    // selection widgets exist — no selection UI this row.
                    // t404 INPUT HYGIENE (D13): map clicks are SILENT. The
                    // laser01 here was an early placeholder that fired on
                    // EVERY click; the vendor SOUNDCHANNEL table names no
                    // sample (audio.md §6.5/§6.6) and the port has no
                    // fire-order interaction, so laser01 plays NOWHERE
                    // until combat UI exists (sfxForPress law).
                    if (const char* sfx = sfxForPress(UiPressSite::MapClick))
                        if (audio) audio->play(sfx);
                    selected = hitStarCam(cam, camp.galaxy(), p);
                    std::printf("ui click map (%d,%d) -> %s\n", p.x, p.y,
                                selected >= 0 ? camp.galaxy().stars[selected].name.c_str()
                                              : "none");
                    if (selected >= 0) {
                        // t410 ENTRY LAW: the star click opens the System
                        // Display (state 16) — t338 MEASURED SET-STATE fn
                        // 0x56e10 edx=0x10 on exactly this click (the Icarus
                        // pip at (238,282)); planet.txt info00 names it route
                        // one to a planet. Silent like every map click (t404).
                        stack.push(kScreenSystemView);
                        screen = kScreenSystemView;
                        std::printf("ui system view %s (state 16)\n",
                                    camp.galaxy().stars[selected].name.c_str());
                    }
                } else if (screen == kScreenSystemView) {
                    // t410 state-16 CLICK CHAIN (ui/sysview.h): console
                    // buttons first (windows.txt file order), then the
                    // orbital dots (planet.txt info00/info05 + help batmode
                    // "view a selected planet by clicking it again").
                    // Everything else is inert + silent (MapClick law; t312
                    // measured vendor empty clicks do nothing here either).
                    const SysCtl ctl = sysCtlFor(p);
                    if (ctl != SysCtl::None) {
                        const SysCtlControl& cc =
                            kSysCtl[static_cast<int>(ctl)];
                        switch (ctl) {
                            case SysCtl::RotateLeft:  systemCam.pressSpin(+1); break;
                            case SysCtl::RotateRight: systemCam.pressSpin(-1); break;
                            case SysCtl::ZoomIn:      systemCam.zoom(+1); break;
                            case SysCtl::ZoomOut:     systemCam.zoom(-1); break;
                            case SysCtl::Recenter:    systemCam.reset(); break;
                            case SysCtl::TogGrid:     gridOn = !gridOn; break;
                            case SysCtl::Abandon:
                                // REFUSED (header): msg 84 DESTROYS the planet
                                // (t369 live hazard). No sim mutation, ever.
                                std::printf("ui sysview abandon refused "
                                            "(no destruction model)\n");
                                break;
                            default:
                                std::printf("ui sysview seam %s (msg %d: no "
                                            "per-ship order model, t256c)\n",
                                            cc.name, cc.sendMessage);
                                break;
                        }
                        std::printf("ui sysview cam yaw %.2f pitch %.2f focal %.0f grid %d\n",
                                    systemCam.yawLog(), systemCam.pitchLog(),
                                    systemCam.focal, gridOn ? 1 : 0);
                        std::fflush(stdout);
                    } else if (inRect(kBatModeWnd, p)) {
                        const auto dots = systemOrbits(camp, selected,
                                                       systemCam);
                        const int hit = hitOrbitDot(dots, p);
                        if (hit >= 0 && hit < int(dots.size()) &&
                            dots[size_t(hit)].colonised) {
                            const auto& s = camp.galaxy().stars[selected];
                            planetStar = selected;
                            planetName = hit < int(s.planets.size())
                                             ? s.planets[size_t(hit)].name
                                             : s.name;
                            projectOpen = false;
                            planetCell = -1;  // t418b: fresh tile selection
                            stack.push(kScreenPlanet);
                            screen = kScreenPlanet;
                            std::printf("ui system planet %s -> planet view "
                                        "(state 17)\n", planetName.c_str());
                            std::fflush(stdout);
                        } else if (hit >= 0) {
                            // Bare body: the port models ONE PlanetState per
                            // star (t406) — opening state 17 here would show
                            // data that does not exist. Honest inert + seam
                            // line, never a fabricated readout.
                            std::printf("ui system planet seam (bare body "
                                        "%d: no per-orbit model)\n", hit);
                            std::fflush(stdout);
                        }
                    }
                }
                }  // t409 end: !abilityOpen left-click chain
            } else if (ev.type == SDL_MOUSEBUTTONDOWN &&
                       ev.button.button == SDL_BUTTON_RIGHT &&
                       screen == kScreenFleet) {
                // t407 RIGHT-CLICK DESELECT (selfplay.md, user testimony +
                // live witness 2026-11-11): right-click clears the ship
                // selection. The witness cleared it from empty space too —
                // the port clears anywhere inside the FLEET window (the
                // t256c-adjacent shape: no per-widget hit law was captured
                // for the right button). Silent: MapClick law.
                if (fleetSel >= 0) {
                    std::printf("ui fleet deselect (was row %d)\n", fleetSel);
                    fleetSel = -1;
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
        // t417b STATUS DECLINE [measured, docs/re/_wip_t417.md F1/F6]: the
        // vendor binds NO shape lib to state 10 (TYPE-100 census: states
        // 0,1,3,7,8,13,16,20,TESTDLG only) and 10status k0 registers 4.5%
        // exact on the t3 live capture (navy interior vs vendor black). The
        // full-frame k0 blit WAS the D15 defect; the status chrome is
        // code-drawn per ui/statusbg.h (painted below the clear).
        const int lib = screenPaintsShapeBackdrop(screen) &&
                                backdropFor(libFor(screen))
                            ? libFor(screen)
                            : -1;
        if (lib >= 0) blitShape(ren, kLibs[lib], 0, 0, 0);
        // t417b STATUS CODE-DRAWN CHROME [measured law ui/statusbg.h]: black
        // interior (the vendor rows zone is p_black 0.925 outside art — the
        // kBg (16,16,24) clear is NOT it), perimeter texture bands, header
        // speckle, divider ramp y38..46, left border x7. NO row separator
        // lines (F4 hline scan: zero).
        if (screen == kScreenStatus) {
            SDL_Rect black{0, 0, kDisplayW, kDisplayH};
            SDL_SetRenderDrawColor(ren, 0, 0, 0, 255);
            SDL_RenderFillRect(ren, &black);
            if (statusPerimTex)
                SDL_RenderCopy(ren, statusPerimTex, nullptr, nullptr);
            if (statusSpeckleTex) {
                SDL_Rect dst{kStatusSpeckleRect.x0, kStatusSpeckleRect.y0,
                             kStatusSpeckleRect.x1 - kStatusSpeckleRect.x0 + 1,
                             kStatusSpeckleRect.y1 - kStatusSpeckleRect.y0 + 1};
                SDL_RenderCopy(ren, statusSpeckleTex, nullptr, &dst);
            }
            for (int y = 38; y <= 46; y++) {
                RGB c;
                if (!statusRampColourAt(y, &c)) continue;
                SDL_SetRenderDrawColor(ren, c.r, c.g, c.b, 255);
                SDL_RenderDrawLine(ren, 7, y, 631, y);
            }
            SDL_SetRenderDrawColor(ren, kStatusBorderRgb.r,
                                   kStatusBorderRgb.g, kStatusBorderRgb.b, 255);
            SDL_RenderDrawLine(ren, kStatusBorderX, kStatusBorderY0,
                               kStatusBorderX, kStatusBorderY1);
        }

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
            // cosmos frame + the field clip: zoomed-in stars beyond the
            // frame must not paint the rail. t426 BORDER LAW [measured,
            // docs/re/_wip_t426.md F1; supersedes the t411 two-line ramp]:
            // in the PALETTE-PURE refcap the chrome texture runs INTO the
            // window edge on all four sides (top rows 0..6 full-width
            // texture, left cols 0..6 texture, col 7+ pure black; right
            // col 466 texture; scratchpad bottom rows 473+ texture) and the
            // field interior is PURE BLACK to 7,7..465,472. The vendor has
            // NO bevel line at the edge — the old kBevelMid/kBevelIn rects
            // were the port defect (t411's "x7 (49,54,53)" scan was the
            // non-pure scratchpad; the pure refcap says col 7 is black).
            // Top/bottom texture bands are the frameTex extension below;
            // the in-band luminance GRADIENT toward the edge stays a named
            // seam (textureColourAt is a flat census mix).
            SDL_Rect field{kCosmosWnd.x0, kCosmosWnd.y0,
                           kCosmosWnd.x1 - kCosmosWnd.x0 + 1,
                           kCosmosWnd.y1 - kCosmosWnd.y0 + 1};
            SDL_SetRenderDrawColor(ren, 0, 0, 0, 255);
            SDL_RenderFillRect(ren, &field);
            SDL_RenderSetClipRect(ren, &field);
            // t426 PLAYER PLAQUE (upper-LEFT law, user verbatim 2026-11-17):
            // 15x25 idx19 outline + navy interior at (10,10), raceflag
            // k<player species> blitted at frame+(0,+2) — 100.0% exact
            // (322/322) against the pure refcap. Human (-1) has no flag
            // record (rail precedent): frame stays, slot honest-empty.
            {
                SDL_Rect pf{kPlaqueX, kPlaqueY, kPlaqueW, kPlaqueH};
                SDL_SetRenderDrawColor(ren, 12, 32, 48, 255);
                SDL_RenderFillRect(ren, &pf);
                const uint32_t ga = chromePaletteArgb(kPlaqueFrameIdx);
                SDL_SetRenderDrawColor(ren, uint8_t((ga >> 16) & 0xff),
                                       uint8_t((ga >> 8) & 0xff),
                                       uint8_t(ga & 0xff), 255);
                SDL_RenderDrawRect(ren, &pf);
                const int ps = camp.playerSpecies();
                if (ps >= 0 && ps < int(raceflagLib.count()))
                    blitShape(ren, raceflagLib, ps, kPlaqueX, kPlaqueY);
            }
        }
        if (lanesOn) {
            for (size_t li = 0; li < camp.galaxy().lanes.size(); ++li) {
                if (!camp.laneVisibleTo(int(li), ag::kPlayer)) continue;
                const auto& ln = camp.galaxy().lanes[li];
                Pt a = projectStar(cam, camp.galaxy().stars[ln.a]);
                Pt b2 = projectStar(cam, camp.galaxy().stars[ln.b]);
                SDL_SetRenderDrawColor(ren, kLane.r, kLane.g, kLane.b, 255);
                SDL_RenderDrawLine(ren, a.x, a.y, b2.x, b2.y);
                // t425 EMPIRE LAYER (msg 60 TOGEMPIRE toggles dword
                // [win+0x58a]; BUTTONSTATE 0 = OFF by default, windows.txt
                // ln365). ON: a lane whose endpoints share one owner is
                // redrawn in that owner's colour (the vendor's empire
                // overlay reads the same scene param frame as the lanes —
                // paint snapshot 0x29514 copies +0x58a at offset +8).
                if (empireOn) {
                    const int oa = camp.starOwner(ln.a), ob = camp.starOwner(ln.b);
                    if (oa >= 0 && oa == ob &&
                        (raceVisibleMask & (1u << (oa % 7))) != 0) {
                        const RGB c = kOwnerRgb[oa % 7];
                        SDL_SetRenderDrawColor(ren, c.r, c.g, c.b, 255);
                        SDL_RenderDrawLine(ren, a.x, a.y, b2.x, b2.y);
                    }
                }
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
                // t425 RACE FILTER (vendor d8 consumer 0x27258): a cleared
                // slot hides that owner's records entirely. Slot i covers
                // owner index i (kOwnerRgb order; the vendor's 7 RACE rows
                // cover all seven playable races, the player among them).
                if (o >= 0 && (raceVisibleMask & (1u << (o % 7))) == 0)
                    continue;
                // t425 COLONIES LAYER (msg 61 toggles win+0xd0/+0xcc): with
                // the layer off, owned stars render as plain neutral points —
                // the ownership tinting IS the layer.
                const bool owned = coloniesOn && o >= 0;
                // t416: the ladder bands the TRANSFORMED depth (node+0xd =
                // transformed z, FUN_000284bc) — view-axis field depth, not
                // raw s.z. Identical at the rest basis (t399 pins hold).
                const int cls = depthClass(viewDepth(cam, s) -
                                           Camera3d::kStandoff);
                const int r = pipRadius(cls, owned);
                const int dim = pipDim256(cls);  // t411 depth dim
                if (owned) {
                    SDL_Color c = toSdl(kOwnerRgb[o]);
                    c.r = uint8_t(int(c.r) * dim / 256);
                    c.g = uint8_t(int(c.g) * dim / 256);
                    c.b = uint8_t(int(c.b) * dim / 256);
                    SDL_SetRenderDrawColor(ren, c.r, c.g, c.b, 255);
                } else {
                    SDL_Color c = toSdl(neutralTint(s.type));
                    c.r = uint8_t(int(c.r) * dim / 256);
                    c.g = uint8_t(int(c.g) * dim / 256);
                    c.b = uint8_t(int(c.b) * dim / 256);
                    SDL_SetRenderDrawColor(ren, c.r, c.g, c.b, 255);
                }
                filledCircle(ren, q.x, q.y, r);
                if (s.id == home) {
                    // t426 HOME MARKER LAW [measured 100.0% exact 322/322,
                    // docs/re/_wip_t426.md F3]: ONE white ring (game.pal
                    // idx15, ellipse rx 6 centred (starx, stary-2)) + the
                    // plaque frame + raceflag crest at (starx-7, stary+3).
                    // The user's "two rings" second ring is the lane-trace
                    // diamond (idx111/idx115), not a marker ring — the
                    // vendor paints no second ring (pure-refcap radius
                    // census). Replaces the t399 white-square seam.
                    SDL_SetRenderDrawColor(ren, 255, 255, 255, 255);
                    for (int a = 0; a < 64; a++) {
                        const double th = a * 6.2831853 / 64.0;
                        const int rxp = q.x + int(0.5 + kCrestRingRx * std::cos(th));
                        const int ryp = q.y + kCrestRingDy +
                                        int(0.5 + (kCrestRingRx - 2) * std::sin(th));
                        SDL_RenderDrawPoint(ren, rxp, ryp);
                    }
                    SDL_Rect cf{q.x + kCrestDx, q.y + kCrestDy, kPlaqueW,
                                kPlaqueH};
                    SDL_SetRenderDrawColor(ren, 12, 32, 48, 255);
                    SDL_RenderFillRect(ren, &cf);
                    const uint32_t ca = chromePaletteArgb(kPlaqueFrameIdx);
                    SDL_SetRenderDrawColor(ren, uint8_t((ca >> 16) & 0xff),
                                           uint8_t((ca >> 8) & 0xff),
                                           uint8_t(ca & 0xff), 255);
                    SDL_RenderDrawRect(ren, &cf);
                    const int ps = camp.playerSpecies();
                    if (ps >= 0 && ps < int(raceflagLib.count()))
                        blitShape(ren, raceflagLib, ps, cf.x, cf.y);
                }
                if (s.id == selected) {
                    SDL_SetRenderDrawColor(ren, kText.r, kText.g, kText.b, 255);
                    SDL_Rect sel{q.x - 6, q.y - 6, 13, 13};
                    SDL_RenderDrawRect(ren, &sel);
                }
            }
        }
        // t425 SHIPS LAYER (msg 58 TOGSHIPS toggles dword[win+0xc8]; init
        // -1 visible; COS_SHIP.SHP is the vendor's sprite lib). The port's
        // entire ship state is the transit vector (campaign.h:284), so the
        // layer draws one owner-coloured pip per ship in transit at the
        // from/target midpoint. shipsOn OFF hides them — a REAL state change.
        if (shipsOn) {
            for (const auto& sh : camp.fleet()) {
                if (sh.from < 0 || sh.from >= int(camp.galaxy().stars.size()) ||
                    sh.target < 0 || sh.target >= int(camp.galaxy().stars.size()))
                    continue;
                if ((raceVisibleMask & (1u << (sh.owner % 7))) == 0) continue;
                const Pt a = projectStar(cam, camp.galaxy().stars[sh.from]);
                const Pt b2 = projectStar(cam, camp.galaxy().stars[sh.target]);
                const RGB c = kOwnerRgb[sh.owner % 7];
                SDL_SetRenderDrawColor(ren, c.r, c.g, c.b, 255);
                const int mx = (a.x + b2.x) / 2, my = (a.y + b2.y) / 2;
                SDL_Rect pip{mx - 2, my - 2, 5, 5};
                SDL_RenderFillRect(ren, &pip);
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
        //    t425c TOGGLE-STATE WELL LAW [measured 900/900 bit-exact x4,
        //    scripts/t425c_toggle_state_law.py]: the four layer toggles blit
        //    their SHAPEFRAME with well idx242 -> idx80 (game.pal raw
        //    (22,6,14) = conv (89,24,56) maroon) when their layer is ON, raw
        //    navy when OFF. The spin/zoom row is NOT state-painted (negative
        //    control: the same swap degrades it 74.6% -> 21.5%).
        {
            const int iconLib = libFor(kScreenMap);
            for (int i = 0; i < kMapCtlCount; i++) {
                const MapControl& mc = kMapCtl[i];
                SDL_Rect r{mc.rect.x0, mc.rect.y0,
                           mc.rect.x1 - mc.rect.x0 + 1,
                           mc.rect.y1 - mc.rect.y0 + 1};
                bool on = false;
                switch (MapCtl(i)) {
                    case MapCtl::TogLanes: on = lanesOn; break;
                    case MapCtl::TogEmpire: on = empireOn; break;
                    case MapCtl::TogShips: on = shipsOn; break;
                    case MapCtl::TogColonies: on = coloniesOn; break;
                    default: on = false; break;
                }
                const bool isToggle = i >= int(MapCtl::TogLanes);
                const bool painted =
                    iconLib >= 0 &&
                    (isToggle ? blitShapePalSwap(
                                     ren, kLibs[iconLib], mc.shapeFrame, r.x,
                                     r.y, kToggleWellIdx,
                                     on ? kToggleWellOnIdx : kToggleWellIdx)
                               : blitShape(ren, kLibs[iconLib], mc.shapeFrame,
                                          r.x, r.y));
                if (!painted) {
                    SDL_SetRenderDrawColor(ren, 40, 40, 56, 255);
                    SDL_RenderFillRect(ren, &r);
                    SDL_SetRenderDrawColor(ren, kText.r, kText.g, kText.b, 255);
                    SDL_RenderDrawRect(ren, &r);
                }
            }
        }
        // 4) RACECONTROLS strip 474,442-632,472 (SHAPEFRAME 19 = 1starmap
        //    k19 158x30; MEASURED slot-1 square 479,448-495,465 == table).
        //    t425b: slots paint their OWN vendor FACE (family law
        //    mapchrome.h: visible = outlined member, filtered = grey member),
        //    coloured through game.pal by blitShape. The t425 "runtime ramp"
        //    seam was REFUTED (docs/re/_wip_t425.md F3): the faces decode fine
        //    in the static palette; cycle 1 had compared refcap pixels against
        //    the RAW 6-bit table and had measured the toggle-button row (the
        //    strip is at png rows 482..512, outside the 640x480 shot).
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
                const bool visible = (raceVisibleMask & (1u << i)) != 0u;
                const int face = visible ? kRaceSlotFrameVisible(i)
                                         : kRaceSlotFrameHidden(i);
                if (iconLib >= 0 && blitShape(ren, kLibs[iconLib], face,
                                              r.x, r.y))
                    continue;
                // DEGRADED (data-less clone path, publish law): CVD-safe
                // kOwnerRgb fill, luminance-halved when filtered.
                RGB c = kOwnerRgb[i];
                if (!visible)
                    c = RGB{uint8_t(c.r / 2), uint8_t(c.g / 2), uint8_t(c.b / 2)};
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
                case kScreenResearch: hdr = Rect{kResWin.x0, kResWin.y0, kResWin.x1, 34};
                                      interior = kResWin; break;
                case kScreenPlanet:   hdr = Rect{};  // 17np k0 backdrop IS
                                       interior = kPlanetAllocRect; break;  // the frame
                case kScreenSystemView:  // t410: no TEXTITEM header (help
                    hdr = Rect{};          // batmode titles the screen
                    interior = kBatModeWnd;  // itself); the viewport frame is
                    break;                 // drawn by the content branch
                case kScreenSpecies: hdr = Rect{};  // NO cited header: the
                                     interior = Rect{}; break;          // menu
                                                                        // is rows
                                                                        // over the
                                                                        // map
                default: hdr = Rect{7, 7, 632, 34}; interior = Rect{7, 46, 632, 472};
            }
            if (hdr.x1 > hdr.x0 && screen != kScreenStatus) {
                // t417b: the status header carries the CODE-DRAWN speckle +
                // ramp chrome painted above (statusbg.h law) — the vendor
                // shows NO tan header box there (t3 census: speckle + border
                // x7 only).
                SDL_Rect hs{hdr.x0, hdr.y0, hdr.x1 - hdr.x0 + 1,
                            hdr.y1 - hdr.y0 + 1};
                SDL_SetRenderDrawColor(ren, 150, 130, 110, 255);
                SDL_RenderDrawRect(ren, &hs);
                // t402: on the status screen the HEADER is the static.txt
                // #151 string (t246/t249 law), drawn centred below — the
                // generic rail-label title would collide with it.
                if (screen != kScreenStatus && screen != kScreenResearch)
                    txt.draw(ren, hs.x + 8, hs.y + 6, screenTitle(screen), true,
                             kText);
            }
            if (screen != kScreenSpecies && screen != kScreenPlanet &&
                screen != kScreenSystemView && screen != kScreenStatus) {
                // t406: the planet screen's frame IS the 17np k0 backdrop
                // (outer frame measured on the decode) — no vector overlay.
                // t410: the system view draws its own viewport frame.
                // t417b: the status screen's frame IS the code-drawn border
                // x7 (33,56,57) + perimeter bands (statusbg.h) — the grey
                // kLane box at 7,46-632,472 is the port's own invention.
                SDL_Rect is{interior.x0, interior.y0,
                            interior.x1 - interior.x0 + 1, interior.y1 - interior.y0 + 1};
                SDL_SetRenderDrawColor(ren, kLane.r, kLane.g, kLane.b, 255);
                SDL_RenderDrawRect(ren, &is);
            }
            // t409 SPECIES MENU (state 7) CONTENT (ui/speciesmenu.h law):
            // the slot-0 window is the static.txt #11 header ("3 of 3
            // Species Known" — t252 live), the six rows below it are the
            // KNOWN species: dip-header name in the owner colour + the
            // raceflag.shp face (specnum-indexed, t400 §2), or static.txt
            // #12 "Extinct" when the owner holds no stars (t252: extinct
            // rows highlight only). Rows are msg 1 p1 13 (NEGSCREEN) — no
            // chrome in the port, so clicks stay inert (t388 known-set law)
            // and the seam prints. The Intelligence item below (STATE "1 7")
            // is drawn by the rail loop.
            if (screen == kScreenSpecies) {
                const std::string hdr = speciesMenuHeader(camp);
                {
                    const int w = txt.width(hdr, false);
                    txt.draw(ren, kRaceRows[0].x0 +
                                 ((kRaceRows[0].x1 - kRaceRows[0].x0 + 1 - w) / 2),
                             kRaceRows[0].y0 + 8, hdr, false, kText);
                }
                const auto rows = speciesMenuRows(camp, roster);
                for (size_t i = 0; i < rows.size() && i + 1 < 7; i++) {
                    const Rect& slot = kRaceRows[i + 1];
                    SDL_Rect rr{slot.x0, slot.y0, slot.x1 - slot.x0 + 1,
                                slot.y1 - slot.y0 + 1};
                    SDL_SetRenderDrawColor(ren, kLane.r, kLane.g, kLane.b, 255);
                    SDL_RenderDrawRect(ren, &rr);
                    // flag face (raceflag.shp frame == specnum; refusal or
                    // human rows simply omit the face — honest)
                    const SpeciesRow& sr = rows[i];
                    int tx = slot.x0 + 8;
                    if (sr.flagSpecnum >= 0 &&
                        sr.flagSpecnum < int(raceflagLib.count())) {
                        blitShape(ren, raceflagLib, sr.flagSpecnum, tx,
                                  slot.y0 + 3);
                        tx += 14 + 6;
                    }
                    const std::string label =
                        sr.extinct ? std::string("Extinct")  // static #12
                                   : sr.name;
                    SDL_Color c = toSdl(kOwnerRgb[sr.owner % 7]);
                    txt.draw(ren, tx, slot.y0 + 8, label, false, c);
                }
                if (rows.empty())
                    txt.draw(ren, kRaceRows[1].x0, kRaceRows[1].y0 + 8,
                             "no species known", false, kDim);
            } else if (screen == kScreenStatus) {
                // ---- t402 PLANETS LIST (D11 "wrong and unusable" FIXED).
                // Law: ui/statuslist.h (row assembly 0x50647..0x5091f cited
                // instruction-exact; word tables content-anchored; pitch 112
                // + three rows MEASURED on the t3 capture; membership t249).
                const auto all = statusPlanets(camp, ag::kPlayer);
                const auto win = statusWindow(all, statusScroll);
                // Header (static.txt #151 via planetwin; owner display name
                // from the species roster, fallback "Player").
                std::string owner = "Player";
                if (roster) {
                    const int ps = camp.playerSpecies();
                    if (ps >= 0 && ps < int(roster->size()) &&
                        !roster->at(size_t(ps)).dipName.empty())
                        owner = roster->at(size_t(ps)).dipName;
                }
                const auto hdr = statusHeaderFor(camp, ag::kPlayer);
                const std::string htxt =
                    formatPlanetHeader(owner, hdr.planets, hdr.systems);
                {
                    // t417b MEASURED (F2/F5): the vendor header title is
                    // GREEN (0,170,82) at text rows y20..26 — centred.
                    const int w = txt.width(htxt, true);
                    txt.draw(ren, kStatusWnd.x0 +
                                 ((kStatusWnd.x1 - kStatusWnd.x0 + 1 - w) / 2),
                             18, htxt, true, SDL_Color{0, 170, 82, 255});
                }
                // Scroll arrows (PORT triangles; the vendor arrow GLYPH art
                // is uncited — honest vector). Box rects t405-measured; the
                // well fill is the F4 navy (8,32,49), NOT the k0 idx-242
                // navy (12,32,48) — that colour is the fingerprint of the
                // never-painted backdrop record (F1).
                for (const auto& ar : {kStatusArrowUp, kStatusArrowDown}) {
                    SDL_Rect rr{ar.x0, ar.y0, ar.x1 - ar.x0 + 1,
                                ar.y1 - ar.y0 + 1};
                    SDL_SetRenderDrawColor(ren, kStatusWellNavy.r,
                                           kStatusWellNavy.g,
                                           kStatusWellNavy.b, 255);
                    SDL_RenderFillRect(ren, &rr);
                    SDL_SetRenderDrawColor(ren, 200, 200, 200, 255);
                    const int cx = (ar.x0 + ar.x1) / 2, cy = (ar.y0 + ar.y1) / 2;
                    const bool up = (&ar == &kStatusArrowUp);
                    SDL_RenderDrawLine(ren, cx - 6, cy + (up ? 3 : -3),
                                       cx + 6, cy + (up ? 3 : -3));
                    SDL_RenderDrawLine(ren, cx, cy + (up ? -4 : 4),
                                       cx, cy + (up ? 3 : -3));
                }
                // Rows (pitch kStatusRowPitch from kStatusRowsTop).
                const int planetLibIdx = 4;  // planets.shp (kLibFiles order)
                const int sunLibIdx = 7;     // suns.shp (t427)
                for (size_t i = 0; i < win.size(); i++) {
                    const auto& key = win[i];
                    const auto& s = camp.galaxy().stars[key.star];
                    const int y = kStatusRowsTop + int(i) * kStatusRowPitch;
                    // t427 SELECTION LAW [measured]: the vendor marks the
                    // selected row by line-1 TEXT COLOUR (white vs green),
                    // NOT a marker rect — the t417b flat (255,0,0) capsule
                    // was fitted to the SUN ART's upper-left arc (rows 1/2
                    // red px below x185 = ZERO; docs/re/_wip_t427.md F6).
                    // Capsule DELETED.
                    // NO row frame [F4 measured]: the vendor interior is
                    // black with ZERO separator lines (hline scan y100..470
                    // = none). The t402 navy fill + outline painted over the
                    // never-painted k0 grid they were fitted to.
                    // t427 BLIT #1 SUN (row painter 0x50525..0x5053a: lib
                    // suns.shp, selector = raw star type; 2x scale per the
                    // measured 130-px drawn sun vs 61-px record; centre
                    // MEASURED x80 y=row+64).
                    if (sunLibIdx < 8 && kLibs[sunLibIdx].count() > 0) {
                        const int sel = statusSunSelector(s.type);
                        if (sel >= 0 && sel < int(kLibs[sunLibIdx].count())) {
                        const auto& sr = kLibs[sunLibIdx].record(sel);
                        blitShapeScaled(ren, kLibs[sunLibIdx], sel,
                                        kStatusSunCx - int(sr.width),
                                        y + kStatusSunCy - int(sr.height),
                                        kStatusArtScale);
                        }
                    }
                    // t427 BLIT #3 FLAG (raceflag.shp, slot [0x6fd84]=32
                    // measured; vendor paints it for owned rows — our list
                    // membership is owner-law (t249), so EVERY row qualifies
                    // for the local player). Palette-ramp tint is seam
                    // T427-D; native record colours.
                    {
                        const int fps = camp.playerSpecies();
                        if (fps >= 0 && fps < int(raceflagLib.count()))
                            blitShape(ren, raceflagLib, fps,
                                      kStatusFlagX, y + kStatusFlagY);
                    }
                    // t427 BLIT #2 PLANET (0x50565..0x50592: planets.shp,
                    // selector 5*type + size — the same +0x16/+0x14 words
                    // the row string reads; 2x scale, centre MEASURED
                    // x215 y=row+53 on the t3 capture).
                    const auto& ps = camp.planetAt(key.star);
                    const int sizeIdx = ag::Campaign::sizeClassFor(ps.surfaceCells);
                    const int typeIdx = ps.terrainRow;
                    const int prec = statusPlanetSelector(typeIdx, sizeIdx);
                    if (planetLibIdx < 8 && kLibs[planetLibIdx].count() == 55 &&
                        prec >= 0) {
                        const auto& r = kLibs[planetLibIdx].record(prec);
                        blitShapeScaled(ren, kLibs[planetLibIdx], prec,
                                        kStatusPlanetCx - int(r.width),
                                        y + kStatusPlanetCy - int(r.height),
                                        kStatusArtScale);
                    }
                    // line 1 + line 2 (the cited assembly)
                    std::string pname = s.name;
                    if (key.planetIndex < int(s.planets.size()))
                        pname = s.planets[key.planetIndex].name;
                    const std::string l1 = statusLine1(pname, sizeIdx, typeIdx);
                    std::string l2;
                    const auto cw0 = camp.channelWordsFor(key.star);
                    const int pend = camp.pendingItemFor(key.star);
                    if (pend < 0) {
                        l2 = statusLine2NoProject(
                            int(camp.planetAt(key.star).pop) ==
                            camp.usedPopFor(key.star));
                    } else if (const auto* pi = camp.planetItem(pend)) {
                        // IND word = channelWordsFor().ind (the cited
                        // +0x44 analog, incl. the Hyperpower leg).
                        l2 = statusLine2(pi->name,
                                         statusDays(pi->cost,
                                                    camp.buildAccFor(key.star),
                                                    cw0.ind),
                                         (pi->flags & 0x2) != 0);
                    } else {
                        l2 = "Building ???";  // refuse-not-crash
                    }
                    // t417b MEASURED (F5 row-0 column census): the vendor's
                    // planet-name text starts x288 (green cluster x288..341;
                    // the cyan x190..260 cluster is the SYSTEM name — the
                    // port folds system+planet into one line1). The old 200
                    // landed inside the system-name zone.
                    const int tx = 288;
                    // t427 SELECTION LAW [measured]: line1 WHITE on the
                    // selected row, GREEN (0,170,82) otherwise.
                    txt.draw(ren, tx, y + 14, l1, true,
                             statusScroll + int(i) == statusSel
                                 ? toSdl(kStatusLine1Sel)
                                 : toSdl(kStatusLine1Norm));
                    txt.draw(ren, tx, y + 40, l2, false, kDim);
                    // t427 POP PIP GRID [measured F6]: 10 cols x 4 rows,
                    // pitch 5 at x498, y = rowTop+50 (bands measured
                    // y107..124 on row 0 = row-rel 50..67), red family.
                    // Replaces the t417b 10-band strip at x428 (wrong
                    // column AND wrong shape).
                    const auto bands = camp.popBandsFor(key.star);
                    for (size_t b = 0; b < bands.size(); b++) {
                        int px0, py0;
                        if (!statusPipAt(int(b), y, px0, py0)) break;
                        const SDL_Color c = bands[b] == 1
                                              ? SDL_Color{200, 60, 60, 255}
                                              : bands[b] == 2
                                              ? SDL_Color{200, 180, 60, 255}
                                              : SDL_Color{60, 120, 90, 255};
                        SDL_Rect px{px0, py0, 2, 2};
                        SDL_SetRenderDrawColor(ren, c.r, c.g, c.b, 255);
                        SDL_RenderFillRect(ren, &px);
                    }
                    // gauges RES/IND/PRO selectors as numbers (content law;
                    // the dot-ladder art is the state-17 panel's, seam)
                    const auto cw = camp.channelWordsFor(key.star);
                    char gbuf[64];
                    std::snprintf(gbuf, sizeof(gbuf), "RES %d  IND %d  PRO %d",
                                  gaugeSelector(cw.res), gaugeSelector(cw.ind),
                                  prosSelector(cw.pros));
                    txt.draw(ren, tx, y + 84, gbuf, false, kDim);
                }
                if (win.empty())
                    txt.draw(ren, interior.x0 + 8, interior.y0 + 8,
                             "No planets owned", false, kDim);
            } else if (screen == kScreenPlanet) {
                // ---- t406 PLANET VIEW (state 17 PLANETALLOC) -------------
                // Composition cited windows.txt ln1486..1604 via planetwin.h;
                // readout law ui/planetview.h. The five TYPE-29 panels are
                // the windows.txt rects; PLBUILD is the PROJECT slot whose
                // click opens the PLANLIST (planet.txt info04).
                const auto pv = planetViewFor(camp, planetStar, planetName);
                for (int pi = 0; pi < kPlanetPanelCount; pi++) {
                    const auto& pan = kPlanetPanels[pi];
                    SDL_Rect pr{pan.rect.x0, pan.rect.y0,
                                pan.rect.x1 - pan.rect.x0 + 1,
                                pan.rect.y1 - pan.rect.y0 + 1};
                    SDL_SetRenderDrawColor(ren, 90, 90, 110, 255);
                    SDL_RenderDrawRect(ren, &pr);
                }
                // ---- t418b SURFACE TILE GRID (D15 "no planet visible") ---
                // Laws ui/planetview.h + docs/re/_wip_t418.md F1/F2/F3/F4/F5:
                // the disc = planal[terrainRow].record(sizeIdx) [inferred F4
                // seam, dims ladder cited], tiles = the 15-row diamond grid
                // (F1) at F2 positions, structure art = planitem k[item] (F5).
                const auto& psv = camp.planetAt(planetStar >= 0 ? planetStar : 0);
                const int psize = planetStar >= 0
                                      ? ag::Campaign::sizeClassFor(psv.surfaceCells)
                                      : -1;
                const auto& ptt = camp.terrainTables();
                if (planetStar >= 0 && psize >= 0) {
                    // Grid bbox centre (F2 lattice over the VALID cells).
                    int minx = 1 << 30, maxx = -(1 << 30), miny = 1 << 30,
                        maxy = -(1 << 30);
                    for (int row = 0; row < 15; row++)
                        for (int col = ptt.rowOffset[psize][row];
                             col < ptt.rowOffset[psize][row] +
                                   ptt.rowWidth[psize][row]; col++) {
                            const Pt c = tileCenter(psize, row, col);
                            minx = std::min(minx, c.x - 34);
                            maxx = std::max(maxx, c.x + 34);
                            miny = std::min(miny, c.y - 17);
                            maxy = std::max(maxy, c.y + 17);
                        }
                    const int gcx = (minx + maxx) / 2, gcy = (miny + maxy) / 2;
                    // THE PLANET PICTURE under the grid (F4 [inferred]:
                    // terrainRow picks the lib, sizeIdx the rung).
                    const int trow = psv.terrainRow;
                    if (trow >= 0 && trow < 11 && planalLibs[trow].count() == 5) {
                        const auto& dr = planalLibs[trow].record(psize);
                        blitShape(ren, planalLibs[trow], psize,
                                  gcx - int(dr.width) / 2,
                                  gcy - int(dr.height) / 2);
                    }
                    // Tiles (F1 valid cells, F2 lattice). Bare fill pal[150]
                    // (immediate 0x960000 @0x3c274); per-class colour table
                    // 0x892ac UNRESOLVED (named seam) — rock cells |8 draw a
                    // DARKER fill [documented default].
                    const uint32_t bare = chromePaletteArgb(150);
                    for (int row = 0; row < 15; row++)
                        for (int col = ptt.rowOffset[psize][row];
                             col < ptt.rowOffset[psize][row] +
                                   ptt.rowWidth[psize][row]; col++) {
                            const int cell = gridCellFor(ptt, psize, row, col);
                            if (cell < 0) continue;
                            const Pt c = tileCenter(psize, row, col);
                            const bool rock =
                                cell < int(psv.cellClasses.size()) &&
                                (psv.cellClasses[cell] & 8);
                            const uint32_t argb =
                                rock ? ((bare >> 1) & 0x7F7F7F) | 0xFF000000u
                                     : bare;
                            SDL_SetRenderDrawColor(
                                ren, (argb >> 16) & 0xFF, (argb >> 8) & 0xFF,
                                argb & 0xFF, 255);
                            filledDiamond(ren, c.x, c.y);
                            // diamond outline (edge edges, 68x34)
                            SDL_SetRenderDrawColor(ren, 24, 24, 32, 255);
                            SDL_RenderDrawLine(ren, c.x - 34, c.y, c.x, c.y - 17);
                            SDL_RenderDrawLine(ren, c.x, c.y - 17, c.x + 34, c.y);
                            SDL_RenderDrawLine(ren, c.x + 34, c.y, c.x, c.y + 17);
                            SDL_RenderDrawLine(ren, c.x, c.y + 17, c.x - 34, c.y);
                        }
                    // Structure art ON the tiles (F5: planitem record index
                    // == itemIdx, 1:1 pixel-match law shp.md S23.4).
                    if (planitemLib.count() == 40)
                        for (size_t ii = 0; ii < psv.items.size(); ii++) {
                            const int cell = psv.itemCells[ii];
                            int row = 0, col = 0;
                            if (cell < 0 || !gridRowCol(ptt, psize,
                                                        psv.surfaceCells, cell,
                                                        &row, &col))
                                continue;  // orbital ring: no surface tile
                            const int item = psv.items[ii];
                            if (item < 0 || item >= 40) continue;
                            const Pt c = tileCenter(psize, row, col);
                            const auto& sr = planitemLib.record(item);
                            blitShape(ren, planitemLib, item,
                                      c.x - int(sr.width) / 2,
                                      c.y - int(sr.height) / 2);
                        }
                    // Selected tile: bright outline (port affordance — the
                    // vendor PLSQUARE cell-select, ln1520).
                    if (planetCell >= 0) {
                        int row = 0, col = 0;
                        if (gridRowCol(ptt, psize, psv.surfaceCells, planetCell,
                                       &row, &col)) {
                            const Pt c = tileCenter(psize, row, col);
                            SDL_SetRenderDrawColor(ren, 255, 255, 255, 255);
                            SDL_RenderDrawLine(ren, c.x - 34, c.y, c.x, c.y - 17);
                            SDL_RenderDrawLine(ren, c.x, c.y - 17, c.x + 34, c.y);
                            SDL_RenderDrawLine(ren, c.x + 34, c.y, c.x, c.y + 17);
                            SDL_RenderDrawLine(ren, c.x, c.y + 17, c.x - 34, c.y);
                        }
                    }
                }
                txt.draw(ren, 12, 118, pv.title, true, kText);
                char pbuf[160];
                std::snprintf(pbuf, sizeof(pbuf), "Population %d / %d  (working %d)",
                              pv.pop, pv.cap, pv.used);
                txt.draw(ren, 12, 142, pbuf, false, kText);
                std::snprintf(pbuf, sizeof(pbuf), "RES %d   IND %d   PROS %d",
                              pv.res, pv.ind, pv.pros);
                txt.draw(ren, 12, 162, pbuf, false, kDim);
                // The PROJECT slot (PLBUILD panel, 463,8-632,106): current
                // project or "No Project" + the open-list affordance.
                {
                    const Rect& pb = kPlanetPanels[4].rect;  // PLBUILD
                    std::string pl;
                    if (pv.noProject)
                        pl = statusLine2NoProject(pv.noFreePopulation);
                    else if (const auto* it = camp.planetItem(pv.pendingItem)) {
                        pl = "Project: ";
                        pl += it->name;
                        if (pv.days < 0) pl += " - No Progress";
                        else { char db[64];
                            std::snprintf(db, sizeof(db), " - %d day%s until completion",
                                          pv.days, pv.days == 1 ? "" : "s");
                            pl += db; }
                    } else pl = "Project: ???";
                    txt.draw(ren, pb.x0 + 6, pb.y0 + 8, pl, false, kText);
                    txt.draw(ren, pb.x0 + 6, pb.y1 - 14,
                             projectOpen ? "list open: pick one" : "click: set project",
                             false, kDim);
                }
                if (projectOpen) {
                    // PLANLIST (120,120-520,420) over the field: the
                    // REQUIRES-gated options in table order.
                    const auto& lr = kProjectListRect;
                    SDL_Rect lb{lr.x0, lr.y0, lr.x1 - lr.x0 + 1,
                                lr.y1 - lr.y0 + 1};
                    SDL_SetRenderDrawColor(ren, 8, 12, 20, 235);
                    SDL_RenderFillRect(ren, &lb);
                    SDL_SetRenderDrawColor(ren, 150, 130, 110, 255);
                    SDL_RenderDrawRect(ren, &lb);
                    const auto opts = projectOptionsFor(camp, planetStar);
                    for (size_t oi = 0; oi < opts.size() &&
                                      int(oi) < kProjectVisibleRows; oi++) {
                        const int ry = lr.y0 + 2 + int(oi) * kProjectRowPitch;
                        const bool ok = projectOrderable(camp, planetStar,
                                                         opts[oi].item);
                        // t418b: with a tile selected, the F3 leg joins the
                        // report (the vendor checker refuses an inactive new
                        // item touching an ACTIVE neighbour, 0x386fe).
                        const bool cellOk =
                            planetCell < 0 ||
                            orderCellBlock(camp, planetStar, opts[oi].item,
                                           planetCell) !=
                                OrderCellBlock::ActiveNeighbour;
                        char ob[128];
                        std::snprintf(ob, sizeof(ob), "%-24s cost %3d%s%s",
                                      opts[oi].name.c_str(), opts[oi].cost,
                                      ok ? "" : "  (no free population)",
                                      ok && !cellOk ? "  (cell refuses)" : "");
                        txt.draw(ren, lr.x0 + 8, ry + 4, ob, false,
                                 ok && cellOk ? kText : kDim);
                    }
                    if (opts.empty())
                        txt.draw(ren, lr.x0 + 8, lr.y0 + 6,
                                 "No projects available", false, kDim);
                }
            } else if (screen == kScreenFleet) {
                // ---- t407 SHIPS LIST (D13 "ships screen is EMPTY") ------
                // Law ui/fleetlist.h: header #152 via the t276-pinned
                // formatShipHeader; rows = the campaign's ship census;
                // geometry MEASURED on work/screens/t253/fleet_open_game.png
                // (rows top 52, pitch 106, four rows, columns name/chevron/
                // spheres/location, arrow boxes x606..635). Chrome is
                // honestly-vector DECISIVE (t391: no 18*.shp exists).
                const auto all = fleetRows(camp, ag::kPlayer);
                const auto win = fleetWindow(all, fleetScroll);
                std::string owner = "Player";
                if (roster) {
                    const int ps = camp.playerSpecies();
                    if (ps >= 0 && ps < int(roster->size()) &&
                        !roster->at(size_t(ps)).dipName.empty())
                        owner = roster->at(size_t(ps)).dipName;
                }
                const std::string htxt =
                    fleetHeaderText(camp, ag::kPlayer, owner, int(all.size()));
                {
                    const int w = txt.width(htxt, true);
                    txt.draw(ren, kFleetWnd.x0 +
                                 ((kFleetWnd.x1 - kFleetWnd.x0 + 1 - w) / 2),
                             kFleetWnd.y0 + 6, htxt, true, kText);
                }
                // Arrow boxes (honest vector triangles, same shape as the
                // status pair; boxes MEASURED fleetlist.h).
                for (const auto& ar : {kFleetArrowUp, kFleetArrowDown}) {
                    SDL_Rect rr{ar.x0, ar.y0, ar.x1 - ar.x0 + 1,
                                ar.y1 - ar.y0 + 1};
                    SDL_SetRenderDrawColor(ren, 12, 32, 48, 255);
                    SDL_RenderFillRect(ren, &rr);
                    SDL_SetRenderDrawColor(ren, 200, 200, 200, 255);
                    const int cx = (ar.x0 + ar.x1) / 2, cy = (ar.y0 + ar.y1) / 2;
                    const bool up = (&ar == &kFleetArrowUp);
                    SDL_RenderDrawLine(ren, cx - 6, cy + (up ? 3 : -3),
                                       cx + 6, cy + (up ? 3 : -3));
                    SDL_RenderDrawLine(ren, cx, cy + (up ? -4 : 4),
                                       cx, cy + (up ? 3 : -3));
                }
                const std::string shipName = fleetShipName(camp);
                for (size_t i = 0; i < win.size(); i++) {
                    const auto& sh = camp.fleet()[win[i].fleetIndex];
                    const int y = kFleetRowsTop + int(i) * kFleetRowPitch;
                    // selection marker (CVD-safe luminance bar, statuslist
                    // precedent; the vendor's own marker is art this port
                    // does not have)
                    if (fleetScroll + int(i) == fleetSel) {
                        SDL_Rect mk{20, y + 20, 10, 15};
                        SDL_SetRenderDrawColor(ren, 0, 200, 80, 255);
                        SDL_RenderFillRect(ren, &mk);
                    }
                    // row frame (PORT vector; no fleet backdrop art exists)
                    SDL_Rect rf{60, y, kFleetRowsRight - 60,
                                kFleetRowPitch - 8};
                    SDL_SetRenderDrawColor(ren, 40, 40, 56, 255);
                    SDL_RenderFillRect(ren, &rf);
                    SDL_SetRenderDrawColor(ren, 90, 90, 110, 255);
                    SDL_RenderDrawRect(ren, &rf);
                    // NAME column green at x159 (MEASURED); LOCATION at
                    // x389 (MEASURED) — the #146 lane string, ETA default 1
                    // (the port's transit resolves at the next boundary).
                    txt.draw(ren, 159, y + 10, shipName, true,
                             SDL_Color{0, 230, 90, 255});
                    const auto& dest = camp.galaxy().stars[sh.target];
                    const std::string loc = fleetLaneLocation(dest.name, 1);
                    // multi-line draw: split on '\n' (the renderer draws one
                    // line per call; the vendor string IS multi-line)
                    int ly = y + 10;
                    size_t pos = 0;
                    while (pos <= loc.size()) {
                        const size_t nl = loc.find('\n', pos);
                        txt.draw(ren, 389, ly,
                                 loc.substr(pos, nl == std::string::npos
                                                     ? std::string::npos
                                                     : nl - pos),
                                 false, SDL_Color{0, 200, 220, 255});
                        if (nl == std::string::npos) break;
                        pos = nl + 1;
                        ly += 14;
                    }
                }
                if (win.empty())
                    txt.draw(ren, interior.x0 + 8, interior.y0 + 8,
                             all.empty()
                                 ? "No ships in transit (the model holds no "
                                   "idle fleets — named seam)"
                                 : "Scrolled past the last ship",
                             false, kDim);
            } else if (screen == kScreenResearch) {
                // ---- t408 RESEARCH SCREEN (D13 "research is empty") ------
                // Law ui/researchview.h: header = static #130 first-%s join
                // centred (t252/t268 native grade: green "Chamachies
                // Knowledge" y~17); nodes = rings r30 at the derived layout
                // (depth x row; vendor positions = named seam); RIGHT PANEL
                // x484..632 is CODE-DRAWN (the STATE "1 20" census is RESWIN
                // + the four pan buttons ONLY). Chrome honestly-vector WITH
                // citation: 20res.shp holds the arrow faces only (t391).
                const auto* tree = camp.researchTree();
                if (tree) {
                    const auto nodes = researchNodes(camp, *tree, ag::kPlayer);
                    std::string owner = "Player";
                    if (roster) {
                        const int ps = camp.playerSpecies();
                        if (ps >= 0 && ps < int(roster->size()) &&
                            !roster->at(size_t(ps)).dipName.empty())
                            owner = roster->at(size_t(ps)).dipName;
                    }
                    const std::string htxt = researchHeaderText(owner);
                    {
                        const int w = txt.width(htxt, true);
                        txt.draw(ren, (640 - w) / 2, 14, htxt, true,
                                 SDL_Color{0, 230, 90, 255});
                    }
                    // Tree field: clip to the RESWIN interior so panning
                    // never paints the header or the right panel.
                    SDL_Rect clip{7, 46, 470, 427};
                    SDL_RenderSetClipRect(ren, &clip);
                    // t419: ONE layout + ONE projected-centre pass per frame
                    // (was O(n^2 x graph) per frame — the D15 CPU stall).
                    const auto resLayout = researchLayoutFor(*tree);
                    const auto centres = researchNodeScreen(
                        resLayout, nodes, resPanX, resPanY, resCam);
                    for (size_t i = 0; i < nodes.size(); ++i) {
                        // prereq edges first (thin blue, the capture's lanes)
                        const auto& c = centres[i];
                        for (int pr : tree->all()[nodes[i].row].prereqs) {
                            if (pr < 0 || pr >= int(centres.size())) continue;
                            const auto& pc = centres[size_t(pr)];
                            SDL_SetRenderDrawColor(ren, 40, 40, 160, 255);
                            SDL_RenderDrawLine(ren, pc.x, pc.y, c.x, c.y);
                        }
                    }
                    // Painter order: far nodes first (z2 descending) so the
                    // near disks overlap the far ones under rotation.
                    std::vector<size_t> order(nodes.size());
                    for (size_t i = 0; i < order.size(); ++i) order[i] = i;
                    std::sort(order.begin(), order.end(),
                              [&](size_t a, size_t b) {
                                  return centres[a].z2 > centres[b].z2;
                              });
                    for (size_t oi = 0; oi < order.size(); ++oi) {
                        const auto& nd = nodes[order[oi]];
                        const auto& c = centres[order[oi]];
                        SDL_Color ring = {120, 130, 190, 255};   // empty disk
                        bool fill = false;
                        if (nd.state == TechNodeState::Owned)
                            ring = {90, 200, 255, 255};          // discovered
                        if (nd.state == TechNodeState::Study)
                            ring = {230, 160, 40, 255};          // gold rim
                        if (nd.state == TechNodeState::Blocked) {
                            ring = {70, 70, 90, 255};            // dim [port
                            // choice; the captures never show a blocked node]
                        }
                        if (nd.state == TechNodeState::Owned) fill = true;
                        // t419: ring radius follows the perspective scale
                        // (rest scale == 1 -> exactly r30/r27, the t408 law).
                        const int rr0 = c.r;
                        for (int rr : {rr0, rr0 - 3}) {
                            SDL_SetRenderDrawColor(ren, ring.r, ring.g,
                                                   ring.b, 255);
                            int x = rr, y = 0, err = 1 - rr;
                            while (x >= y) {
                                const SDL_Point pts[8] = {
                                    {c.x + x, c.y + y}, {c.x + y, c.y + x},
                                    {c.x - y, c.y + x}, {c.x - x, c.y + y},
                                    {c.x - x, c.y - y}, {c.x - y, c.y - x},
                                    {c.x + y, c.y - x}, {c.x + x, c.y - y}};
                                SDL_RenderDrawPoints(ren, pts, 8);
                                y++;
                                if (err < 0) err += 2 * y + 1;
                                else { x--; err += 2 * (y - x) + 1; }
                            }
                        }
                        if (fill) {  // discovered = filled disk (help reswin)
                            SDL_SetRenderDrawColor(ren, ring.r / 3, ring.g / 3,
                                                   ring.b / 2, 255);
                            for (int dy = -rr0 + 4; dy <= rr0 - 4; ++dy) {
                                const int dx2 = (rr0 - 4) * (rr0 - 4) -
                                                dy * dy;
                                int dx = 0;
                                while ((dx + 1) * (dx + 1) <= dx2) ++dx;
                                SDL_RenderDrawLine(ren, c.x - dx, c.y + dy,
                                                   c.x + dx, c.y + dy);
                            }
                        }
                    }
                    SDL_RenderSetClipRect(ren, nullptr);
                    // Pan button faces (honest vector; 20res frames 0..3 are
                    // the cited art, 15x30 each — blit seam named).
                    auto arrowBox = [&](const Rect& r, bool horiz, bool neg) {
                        SDL_Rect rr{r.x0, r.y0, r.x1 - r.x0 + 1,
                                    r.y1 - r.y0 + 1};
                        SDL_SetRenderDrawColor(ren, 12, 32, 48, 255);
                        SDL_RenderFillRect(ren, &rr);
                        SDL_SetRenderDrawColor(ren, 200, 60, 40, 255);
                        const int cx = (r.x0 + r.x1) / 2, cy = (r.y0 + r.y1) / 2;
                        if (horiz) {
                            SDL_RenderDrawLine(ren, cx - 8, cy, cx + 8, cy);
                            const int s = neg ? -1 : 1;
                            SDL_RenderDrawLine(ren, cx + 8 * s, cy,
                                               cx + 4 * s, cy - 4);
                            SDL_RenderDrawLine(ren, cx + 8 * s, cy,
                                               cx + 4 * s, cy + 4);
                        } else {
                            SDL_RenderDrawLine(ren, cx, cy - 8, cx, cy + 8);
                            const int s = neg ? -1 : 1;
                            SDL_RenderDrawLine(ren, cx, cy + 8 * s,
                                               cx - 4, cy + 4 * s);
                            SDL_RenderDrawLine(ren, cx, cy + 8 * s,
                                               cx + 4, cy + 4 * s);
                        }
                    };
                    arrowBox(kResRotLeft, true, false);
                    arrowBox(kResRotRight, true, true);
                    arrowBox(kResMoveUp, false, true);
                    arrowBox(kResMoveDown, false, false);
                    // RIGHT PANEL x 484..632 (code-drawn; t252 verbatim
                    // order): #122, name (wrapped), #124 days, #125, Allows
                    // entries. No project -> panel BLANK (t268 witness;
                    // #123 "(No Progress)" is data, never rendered there).
                    SDL_Rect pf{484, 46, 632 - 484 + 1, 472 - 46 + 1};
                    SDL_SetRenderDrawColor(ren, 90, 90, 110, 255);
                    SDL_RenderDrawRect(ren, &pf);
                    const int panelCx = (484 + 632) / 2;
                    int queued = -1;
                    for (const auto& nd : nodes)
                        if (nd.state == TechNodeState::Study) queued = nd.row;
                    if (queued >= 0) {
                        const std::string tname = tree->all()[queued].name;
                        const double remain =
                            tree->all()[queued].runtimeCost() -
                            camp.techProgressFor(ag::kPlayer);
                        const std::string days = researchDaysLine(
                            remain, camp.techRateFor(ag::kPlayer));
                        auto centred = [&](int y, const std::string& s,
                                           SDL_Color col) {
                            const int w = txt.width(s, false);
                            txt.draw(ren, panelCx - w / 2, y, s, false, col);
                        };
                        const SDL_Color grn{0, 230, 90, 255};
                        centred(56, "Current Project:", grn);   // static #122
                        // naive wrap at ~18 chars (the capture wrapped
                        // "Accel Energy / Replenishment"); wrap width =
                        // labelled port choice
                        std::string a = tname, b;
                        size_t sp = a.find(' ');
                        while (sp != std::string::npos &&
                               a.substr(0, sp).size() <= 17 &&
                               a.size() > 18) {
                            size_t sp2 = a.find(' ', sp + 1);
                            if (sp2 == std::string::npos ||
                                sp2 > 18) break;
                            sp = sp2;
                        }
                        if (a.size() > 18 && sp != std::string::npos) {
                            b = a.substr(sp + 1);
                            a = a.substr(0, sp);
                        }
                        centred(104, a, grn);
                        int yy = 120;
                        if (!b.empty()) { centred(yy, b, grn); yy += 16; }
                        centred(yy, days, grn);
                        yy += 16;
                        const auto allows = allowsList(camp, queued);
                        if (!allows.empty()) {
                            centred(yy, "Allows", grn);   // static #125
                            yy += 16;
                            for (size_t i = 0; i < allows.size() && i < 6;
                                 ++i) {
                                centred(yy, allows[i], grn);
                                yy += 16;
                            }
                        }
                    }
                }
            } else if (screen == kScreenSystemView) {
                // ---- t410 THE SYSTEM DISPLAY (state 16) ------------------
                // Law ui/sysview.h (STATE census + t338 entry + help batmode
                // verbatim). Blue wireframe plane + bodies (t244 dossier);
                // console rects verbatim; faces from 16battle.shp under the
                // SHAPEFRAME->record identity law (t394 parity 14/16, F3).
                if (selected < 0 || selected >= int(camp.galaxy().stars.size()))
                    txt.draw(ren, kBatModeWnd.x0 + 8, kBatModeWnd.y0 + 8,
                             "no system selected", false, kDim);
                {
                    // viewport frame + clip (rail never paints through)
                    SDL_Rect vf{kBatModeWnd.x0 - 1, kBatModeWnd.y0 - 1,
                                kBatModeWnd.x1 - kBatModeWnd.x0 + 3,
                                kBatModeWnd.y1 - kBatModeWnd.y0 + 3};
                    SDL_SetRenderDrawColor(ren, kLane.r, kLane.g, kLane.b, 255);
                    SDL_RenderDrawRect(ren, &vf);
                    SDL_RenderSetClipRect(ren, &vf);
                    const int ccx = (kBatModeWnd.x0 + kBatModeWnd.x1) / 2;
                    const int ccy = (kBatModeWnd.y0 + kBatModeWnd.y1) / 2;
                    if (gridOn) {
                        // Wireframe plane rings + spokes (t244 "blue
                        // wireframe plane"; colour/pitch = port law).
                        SDL_SetRenderDrawColor(ren, 40, 40, 160, 255);
                        for (int i = 0; i < 6; i++) {
                            const int rr = int(orbitRadius(i) *
                                               systemCam.focal / Camera3d().focal);
                            int x = rr, y = 0, err = 1 - rr;
                            while (x >= y) {
                                const SDL_Point pts[8] = {
                                    {ccx + x, ccy + y}, {ccx + y, ccy + x},
                                    {ccx - y, ccy + x}, {ccx - x, ccy + y},
                                    {ccx - x, ccy - y}, {ccx - y, ccy - x},
                                    {ccx + y, ccy - x}, {ccx + x, ccy - y}};
                                SDL_RenderDrawPoints(ren, pts, 8);
                                y++;
                                if (err < 0) err += 2 * y + 1;
                                else { x--; err += 2 * (y - x) + 1; }
                            }
                        }
                        for (int k = 0; k < 8; k++) {
                            const double a = k * 6.283185307179586 / 8.0;
                            const double r = orbitRadius(5) *
                                             systemCam.focal / Camera3d().focal;
                            SDL_RenderDrawLine(ren, ccx, ccy,
                                               ccx + int(r * std::cos(a)),
                                               ccy + int(r * std::sin(a)));
                        }
                    }
                    const auto dots = systemOrbits(camp, selected, systemCam);
                    for (const auto& d : dots) {
                        // stalk star->body (t244 "bodies on yellow stalks")
                        SDL_SetRenderDrawColor(ren, 150, 140, 60, 255);
                        SDL_RenderDrawLine(ren, ccx, ccy, d.pos.x, d.pos.y);
                        SDL_Color c = d.owner >= 0
                                          ? toSdl(kOwnerRgb[d.owner % 7])
                                          : toSdl(kNeutralRgb);
                        SDL_SetRenderDrawColor(ren, c.r, c.g, c.b, 255);
                        filledCircle(ren, d.pos.x, d.pos.y, d.radius);
                        if (d.colonised) {
                            // colonised ring (CVD: shape, not colour alone)
                            SDL_SetRenderDrawColor(ren, 255, 255, 255, 255);
                            SDL_Rect cr{d.pos.x - d.radius - 3,
                                        d.pos.y - d.radius - 3,
                                        2 * (d.radius + 3) + 1,
                                        2 * (d.radius + 3) + 1};
                            SDL_RenderDrawRect(ren, &cr);
                        }
                    }
                    if (selected >= 0) {
                        const auto& s = camp.galaxy().stars[selected];
                        const std::string info =
                            s.name + (camp.starOwner(selected) == ag::kPlayer
                                          ? "  [yours]"
                                          : camp.starOwner(selected) > 0
                                                ? "  [other]"
                                                : "  [neutral]");
                        txt.draw(ren, kBatModeWnd.x0 + 6,
                                 kBatModeWnd.y1 - 34, info, false, kDim);
                    }
                    SDL_RenderSetClipRect(ren, nullptr);
                }
                // console: faces where cited, vector box + initial elsewhere
                const int batLib = libFor(kScreenSystemView);
                for (int i = 0; i < kSysCtlCount; i++) {
                    const SysCtlControl& cc = kSysCtl[i];
                    SDL_Rect rr{cc.rect.x0, cc.rect.y0,
                                cc.rect.x1 - cc.rect.x0 + 1,
                                cc.rect.y1 - cc.rect.y0 + 1};
                    const int rec = sysCtlShapeRecord(static_cast<SysCtl>(i));
                    if (rec >= 0 && batLib >= 0 &&
                        blitShape(ren, kLibs[batLib], rec, rr.x, rr.y))
                        continue;
                    SDL_SetRenderDrawColor(ren, 12, 32, 48, 255);
                    SDL_RenderFillRect(ren, &rr);
                    SDL_SetRenderDrawColor(ren, kText.r, kText.g, kText.b, 255);
                    SDL_RenderDrawRect(ren, &rr);
                    const std::string lbl(1, cc.name[0]);
                    txt.draw(ren, rr.x + 4, rr.y + 8, lbl, false, kText);
                }
                // BatListWnd: honest frame + the honest zero (t256c: no
                // per-ship presence in the model; vendor orbit rows = seam).
                SDL_Rect bl{kBatListWnd.x0, kBatListWnd.y0,
                            kBatListWnd.x1 - kBatListWnd.x0 + 1,
                            kBatListWnd.y1 - kBatListWnd.y0 + 1};
                SDL_SetRenderDrawColor(ren, kLane.r, kLane.g, kLane.b, 255);
                SDL_RenderDrawRect(ren, &bl);
                txt.draw(ren, kBatListWnd.x0 + 6, kBatListWnd.y0 + 6,
                         "ships: seam (t256c)", false, kDim);
            } else {
                txt.draw(ren, interior.x0 + 8, interior.y0 + 8,
                         "frame + title only: content law seam", false, kDim);
            }
            if (interior.x1 > interior.x0)
                txt.draw(ren, interior.x0 + 8, interior.y1 - 16,
                         "Esc: return to galaxy", false, kDim);
        }
        // ---- t409 ABILITY DIALOG (ABILITYWIN) — drawn LAST over the
        // current screen: the vendor path (0x55ffb -> CALL 0x37b14) opens
        // the modal over whatever state is showing and waits. windows.txt
        // ln2136: rect 60,100-395,355, SHAPEFRAME -1 => CODE-DRAWN (no art
        // cited). Text layout uses the FIRST cited geometry in the block:
        // pos 10 50 (title) / 10 125 (body) / 10 160 (charge line),
        // WINDOW-RELATIVE. Button faces: the block's `title` strings; the
        // per-button split of the full-rect hit law is unmapped (S1 seam) —
        // every inside click dismisses.
        if (abilityOpen) {
            const int ai = int(camp.abilityOf(ag::kPlayer));
            const AbilityPanel* ap = panelForIndex(abilityPanels, ai);
            if (ap) {
                SDL_Rect win{kAbilityWin.x0, kAbilityWin.y0,
                             kAbilityWin.x1 - kAbilityWin.x0 + 1,
                             kAbilityWin.y1 - kAbilityWin.y0 + 1};
                SDL_SetRenderDrawColor(ren, 8, 12, 24, 255);
                SDL_RenderFillRect(ren, &win);
                SDL_SetRenderDrawColor(ren, 150, 130, 110, 255);
                SDL_RenderDrawRect(ren, &win);
                const SDL_Color grn{0, 230, 90, 255};
                txt.draw(ren, kAbilityWin.x0 + 10, kAbilityWin.y0 + 50,
                         ap->title, false, grn);
                // body (pos 10 125): wrapped to the modal width (seam S2:
                // wrap width is a port rendering choice; the bytes are the
                // verbatim block)
                int y = kAbilityWin.y0 + 125;
                for (const auto& ln : wrapBody(ap->body, 44)) {
                    txt.draw(ren, kAbilityWin.x0 + 10, y, ln, false, kText);
                    y += 12;
                }
                if (!ap->chargeLine.empty()) {
                    const int cad = ascend::game::abilityChargeTurns(
                        camp.abilityOf(ag::kPlayer));
                    const int rem = cad - camp.chargeFor(ag::kPlayer);
                    txt.draw(ren, kAbilityWin.x0 + 10, kAbilityWin.y0 + 160,
                             formatChargeLine(ap->chargeLine, rem), false,
                             kDim);
                }
                int bx = kAbilityWin.x0 + 10;
                for (const auto& b : ap->buttons) {
                    const int w = txt.width(b.title, false) + 12;
                    SDL_Rect br{bx, kAbilityWin.y1 - 40, w, 22};
                    SDL_SetRenderDrawColor(ren, 24, 48, 96, 255);
                    SDL_RenderFillRect(ren, &br);
                    SDL_SetRenderDrawColor(ren, kText.r, kText.g, kText.b, 255);
                    SDL_RenderDrawRect(ren, &br);
                    txt.draw(ren, br.x + 6, br.y + 5, b.title, false, kText);
                    bx += w + 10;
                }
            }
        }
        // t416 PUMP (vendor msg 0x3b handler 0x27a18; t302 measured the
        // pump live at ~1/s): a latched dial applies its delta every tick
        // until the opposite press stops it. Port cadence kSpinTickMs is a
        // documented default; only a MOVING camera repaints beyond the
        // event-driven frame (idle cost unchanged — gates/autoplay law).
        {
            const Uint32 nowMs = SDL_GetTicks();
            if (cam.moving() && nowMs - lastPumpMs >= (Uint32)Camera3d::kSpinTickMs) {
                cam.tick();
                lastPumpMs = nowMs;
            }
            if (systemCam.moving() &&
                nowMs - lastSysPumpMs >= (Uint32)Camera3d::kSpinTickMs) {
                systemCam.tick();
                lastSysPumpMs = nowMs;
            }
            // t419 research tree spin pump (same vendor msg-0x3b latch law).
            if (resCam.moving() &&
                nowMs - lastResPumpMs >= (Uint32)Camera3d::kSpinTickMs) {
                resCam.tick();
                lastResPumpMs = nowMs;
            }
        }
        // t419 CORNER "Exit <ESC>" POPUP (ui/exitpopup.h): polled pointer
        // (SDL_GetMouseState gives logical coords under SetLogicalSize —
        // title.cpp precedent; synthetic MotionNotify is rejected by SDL so
        // motion EVENTS are not an option). Drawn LAST: it is an overlay
        // hint over every screen. Transition log only (no per-frame spam).
        {
            int mx = 0, my = 0;
            SDL_GetMouseState(&mx, &my);
            const ExitCorner c = exitCornerFor(mx, my, kDisplayW, kDisplayH);
            if (c != exitCorner) {
                exitCorner = c;
                if (c != ExitCorner::None)
                    std::printf("ui corner exit popup shown\n");
                else
                    std::printf("ui corner exit popup hidden\n");
                std::fflush(stdout);
            }
            if (c != ExitCorner::None && mouseLib.count() > kExitGlyphRec) {
                const Rect r = exitPopupRect(c, kDisplayW, kDisplayH);
                if (!blitShape(ren, mouseLib, kExitGlyphRec, r.x0, r.y0))
                    blitShape(ren, mouseLib, kExitGlyphRec == 5 ? 4 : 5,
                              r.x0, r.y0);  // k4 fallback (canonical gate)
            }
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
