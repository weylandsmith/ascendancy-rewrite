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

#include <cmath>
#include <cstdio>
#include <algorithm>
#include <vector>

#include "formats/gif.h"
#include "formats/shp.h"
#include "game/campaign.h"
#include "ui/boot.h"
#include "ui/cam3d.h"  // t414: neutralTint (preview point families)
#include "ui/menulaw.h"

// tA1-CONT DIMSCHECK WITNESS: one-shot printf of the cited record dims +
// destination anchor at each gated blit, consumed by
// scripts/t441_screen_diff.py (G2). Names are region keys; printed once
// per name per process.
namespace {
void dimsCheck(const char* name, int w, int h, int x, int y) {
    static std::vector<std::string> seen;
    const std::string n(name);
    for (const auto& s : seen)
        if (s == n)
            return;
    seen.push_back(n);
    std::printf("ui dimscheck %s %d %d %d %d\n", name, w, h, x, y);
    std::fflush(stdout);
}
}  // namespace
#include "ui/mapchrome.h"  // t401: textureColourAt (the §4 hash-noise law)
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
// t400: the button fills moved to boot.h titleButtonFill(hovered) — the
// vendor's hovered fill (0,28,36) vs (0,0,8) is MEASURED law there.
// t393 New Game screen colours [measured on the user-supplied original;
// capture is JPEG-lossy so greys land on the canonical (97,97,97)/(12,32,48)
// values the census converges to]. CVD rule: meaning is never carried by
// hue alone here (selection = luminance band, labels carry the words).
const SDL_Color kPanel{12, 32, 48, 255};      // navy panel interior
const SDL_Color kBevel{97, 97, 97, 255};      // grey bevel lines
// tA3 TEXT LAW: the newgame screen runs on game.pal, where the label ink
// core measures (255,255,255) on the user original (Begin label 48 core
// px, Player Species header 61 px; edges blend to (225,227,229)/(164,171,
// 177) in the browser capture — the CORE is the class). kInk (215) is the
// TITLE palette's white and stays title-only.
const SDL_Color kNewgameInk{255, 255, 255, 255};
const SDL_Color kLore{0, 142, 69, 255};       // vendor green ink
const SDL_Color kSelBg{28, 56, 74, 255};      // selection band (lighter navy)
const SDL_Color kDisc{128, 128, 128, 255};    // portrait-seam disc + ring
const SDL_Color kArrowFill{26, 87, 146, 255};   // arrow square fill (measured)
const SDL_Color kArrowInk{190, 255, 255, 255};  // arrow glyph (measured)

// t414: the t393 map-preview primitives (toSdl/kLane/filledCircle) were
// REMOVED with the previewCamp backdrop — the t414 spinning preview draws
// neutralTint points directly (docs/re/_wip_t414.md S2b), and the 0-warning
// export law does not tolerate dead statics.

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
                         AudioEngine* audio,
                         const ascend::game::Campaign* previewCamp,
                         const std::vector<ascend::game::SpeciesInfo>* roster,
                         const std::vector<std::string>* lore) {
    SDL_Window* win = SDL_CreateWindow("Ascendancy", SDL_WINDOWPOS_CENTERED,
                                       SDL_WINDOWPOS_CENTERED, kDisplayW,
                                       kDisplayH, SDL_WINDOW_SHOWN);
    if (!win) {
        *err = std::string("title CreateWindow: ") + SDL_GetError();
        return BootState::Quit;
    }
    // t393 WINDOW DIAGNOSTIC (Athens report: user's window measured 512x384
    // = 0.8x of the 640x480 logical size; everything "small/wonky" follows).
    // Print the ACTUAL size so the next report says what the WM gave us.
    {
        int ww = 0, wh = 0;
        SDL_GetWindowSize(win, &ww, &wh);
        std::printf("ui window %dx%d (logical %dx%d)%s\n", ww, wh, kDisplayW,
                    kDisplayH,
                    (ww == kDisplayW && wh == kDisplayH) ? "" : " <- SCALED");
        std::fflush(stdout);
    }
    SDL_Renderer* ren = SDL_CreateRenderer(win, -1, SDL_RENDERER_ACCELERATED);
    if (!ren) ren = SDL_CreateRenderer(win, -1, SDL_RENDERER_SOFTWARE);
    // t394 WM-scale fix (ui.cpp applyLogicalSize comment; SDL_render.h
    // SDL_RenderSetLogicalSize doc: mouse events are scaled into logical
    // space). The title screen is where the user's 512x384 WM scale bites.
    if (ren) SDL_RenderSetLogicalSize(ren, kDisplayW, kDisplayH);
    // t398: chrome palette for blitShape's colour path (the title's OWN art
    // stays the t386 TSV — game.pal covers the in-game states, refutation
    // docs/re/title-art.md §4; chrome blits like 4loadgam/3cfgnew belong to
    // in-game states and take game.pal).
    loadChromePalette(dataRoot);
    VendorText txt;
    if (!ren || !txt.load(ren, dataRoot, err)) {
        *err = err->empty() ? std::string("title renderer: ") + SDL_GetError() : *err;
        SDL_DestroyRenderer(ren);
        SDL_DestroyWindow(win);
        return BootState::Quit;
    }

    BootState st = initial;
    std::fflush(stdout);

    // ---- t393 New Game screen state (SETTINGS; applying them to the live
    // campaign is the named seed seam — buildCampaign already ran, so Begin
    // enters play with the built galaxy and prints the wheel values).
    // Default density word = the ladder rung the built galaxy actually has
    // (o.stars 50 -> Average); species count word = the number of players
    // the campaign really has (player + 6 AI = Seven); atmosphere Neutral =
    // the vendor default AS MEASURED on the user-supplied original (the
    // capture shows "Neutral Atmosphere" on a fresh New Game screen) — the
    // wheel click does not model atmosphere (no atmosphere model exists).
    int densityIdx = 0;
    if (previewCamp)
        for (int i = 0; i < kDensityCycleCount; i++)
            if (int(kDensityStarCounts[i]) ==
                int(previewCamp->galaxy().stars.size()))
                densityIdx = i;
    int speciesSetting = 7;   // player + 6 AI (main.cpp buildCampaign law)
    int atmosphere = 1;       // Neutral (measured vendor default, see above)
    int selSlot = 0, scrollOffset = 0;  // RACELIST window (3 of roster)
    // t423c PLAYER COLOUR state [verified FUN_000232ec + racering census]:
    // byte[raceRow+8] = colour idx 0..7 (racering.shp record index — the
    // lib IS 8 colour-tinted 53x53 rings, docs/re/_wip_t423c2.md C2-F5).
    // Default idx 0 (green == the measured DESC ring (0,142,69) == racering
    // k0 (0,141,68)); AI races get distinct rand()%7 values. LCG seed is a
    // NAMED SEAM (vendor srand chain 0x21490 feeds saved state; no cited
    // initial value for a fresh New Game screen).
    int playerColourIdx = 0;
    unsigned int colourLcg = 0x12e10u;  // seam: seed value, not law
    unsigned char raceColours[8] = {0, 0, 0, 0, 0, 0, 0, 0};
    assignRaceColours(playerColourIdx, speciesSetting, &colourLcg,
                      raceColours);
    // t412: the Begin press carries the species pick + atmosphere into the
    // race intro (the intro's gated section is atmosphere-selected).
    int beginSpecies = 0, beginAtmosphere = 1;
    const auto rosterCount = [&]() { return roster ? int(roster->size()) : 0; };
    const auto speciesNameAt = [&](int specnum) -> std::string {
        if (roster && specnum >= 0 && specnum < int(roster->size())) {
            std::string n = roster->at(size_t(specnum)).dipName;
            if (!n.empty()) {
                // Header shape varies: race01 "for SNOVEMDOMAS", race00 "for
                // the Minions" [verified headers]. The vendor screen shows
                // the bare name ("Minions", green ink on the user-supplied
                // original), and static.txt //154 supplies the article —
                // strip a leading "the " so the template cannot render
                // "The the Minions are ...".
                if (n.size() > 4 && (n[0] == 't' || n[0] == 'T') &&
                    n[1] == 'h' && n[2] == 'e' && n[3] == ' ')
                    n = n.substr(4);
                return n;
            }
        }
        return "Species " + std::to_string(specnum);  // defensive, not shown
    };

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

    // t401 ART LIBRARIES (docs/re/t401-newgame-art.md S10): raceflag.shp (21x
    // 14x24 crest class — the description-panel emblem, measured exact-size
    // match) and the smraceNN.shp portrait cache (49x49 class; loaded on
    // demand per specnum, one refusal line each, never re-read per frame).
    ascend::formats::ShapeLibrary raceflagLib;
    {
        std::string ferr;
        if (!raceflagLib.load(
                dataRoot + "/extracted/ascend01/data/raceflag.shp", &ferr))
            std::printf("ui raceconfig raceflag refused: %s\n", ferr.c_str());
        std::fflush(stdout);
    }
    // t423 DEFECT (e): the species rings are the racering.shp RECORD
    // (k0 53x53 walk-OK; scripts/t423 census), not a vector stroke.
    ascend::formats::ShapeLibrary raceringLib;
    {
        std::string rerr;
        if (!raceringLib.load(
                dataRoot + "/extracted/ascend01/data/racering.shp", &rerr))
            std::printf("ui raceconfig racering refused: %s\n", rerr.c_str());
        std::fflush(stdout);
    }
    // t423 DEFECT (f): preview star sprites = cos_star.shp through the
    // t200 SEL = 4*type + cls law (planets-ui.md §6).
    ascend::formats::ShapeLibrary cosStarLib;
    {
        std::string serr;
        if (!cosStarLib.load(
                dataRoot + "/extracted/ascend01/data/cos_star.shp", &serr))
            std::printf("ui raceconfig cos_star refused: %s\n", serr.c_str());
        std::fflush(stdout);
    }
    std::vector<ascend::formats::ShapeLibrary> portraitLibs(21);
    // t414: planets.shp — the planet-sphere library for the DESC panel
    // (55 recs = 11 biome groups x size ladder; docs/re/shp.md geometry
    // census, dims re-verified scripts/t414_dims_census.py).
    ascend::formats::ShapeLibrary planetsLib;
    {
        std::string ferr;
        if (!planetsLib.load(
                dataRoot + "/extracted/ascend01/data/planets.shp", &ferr))
            std::printf("ui raceconfig planets refused: %s\n", ferr.c_str());
        std::fflush(stdout);
    }
    std::vector<bool> portraitTried(21, false), portraitOk(21, false);
    const auto portraitFor = [&](int specnum)
        -> const ascend::formats::ShapeLibrary* {
        if (specnum < 0 || specnum > 20) return nullptr;
        if (!portraitTried[size_t(specnum)]) {
            portraitTried[size_t(specnum)] = true;
            std::string perr;
            portraitOk[size_t(specnum)] = portraitLibs[size_t(specnum)].load(
                dataRoot + "/extracted/ascend01/data/" +
                    portraitLibName(specnum),
                &perr);
            if (!portraitOk[size_t(specnum)])
                std::printf("ui raceconfig portrait refused: smrace%02d: %s\n",
                            specnum, perr.c_str());
            std::fflush(stdout);
        }
        return portraitOk[size_t(specnum)] ? &portraitLibs[size_t(specnum)]
                                           : nullptr;
    };

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
        // t395 MENU-MUSIC ENTRY LAW (audio.md §6.6): tune 0 is requested
        // while the Title screen is UP, not only after the intro. Re-asking
        // the same tune is a no-op (audio.h switch law), so this is safe
        // every frame and also covers Title re-entries from Load/Tutorial.
        if (audio) {
            const int want = bootTune(st);
            if (want != kTuneNoChange) audio->playTune(want);
        }
        // t393 SCREEN LAW (D10; boot.md §7): RaceConfig is a FULL-SCREEN
        // SWITCH — the title chrome (art + button column) must NOT show
        // through. Draw one frame of exactly one screen per iteration.
        if (st == BootState::Title) {
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
            // t400 HOVER LAW (boot.h): the vendor's hovered button fills
            // (0,28,36) instead of (0,0,8) — MEASURED on the pinned shot
            // (the cursor sat on PLAYTUTORIAL). SDL tracks the mouse
            // position; no polling beyond what the loop already pumps.
            SDL_Rect r{b.rect.x0, b.rect.y0,
                       b.rect.x1 - b.rect.x0 + 1, b.rect.y1 - b.rect.y0 + 1};
            int mx = -1, my = -1;
            SDL_GetMouseState(&mx, &my);  // logical coords (SetLogicalSize law)
            const RGB fill = titleButtonFill(inRect(b.rect, Pt{mx, my}));
            SDL_SetRenderDrawColor(ren, fill.r, fill.g, fill.b, 255);
            SDL_RenderFillRect(ren, &r);
            // t392 TEXT BASELINE LAW (boot.h + boot.md §7): single-item
            // buttons draw ONE line at y0+8; the LOAD/SAVE/EXITTODOS pair
            // draws label at y0+4 and the vendor's Alt-* TEXTITEM verbatim
            // at y0+18 (the dy fields of the two TEXTITEM records land on
            // the measured ink rows). Both lines centred on the rect.
            const int cx = (b.rect.x0 + b.rect.x1 + 1) / 2;
            if (b.hint) {
                const int w1 = txt.width(b.label, true);
                txt.draw(ren, cx - w1 / 2, b.rect.y0 + kTitleLabelTopPair,
                         b.label, true, kInk);
                const int w2 = txt.width(b.hint, true);
                txt.draw(ren, cx - w2 / 2, b.rect.y0 + kTitleHintTop,
                         b.hint, true, kInk);
            } else {
                const int w = txt.width(b.label, true);
                txt.draw(ren, cx - w / 2, b.rect.y0 + kTitleLabelTopSingle,
                         b.label, true, kInk);
            }
        }
        } else {
            // ---- t393 NEW GAME FULL SCREEN (D10: was an overlay -> garbled
            // title bleeding through). Layout law docs/re/_wip_t393.md S1-S12
            // (windows.txt L575-684 cited rects + cited measurement off the
            // user-supplied original); this block only draws that table.
            SDL_SetRenderDrawColor(ren, 0, 0, 0, 255);
            SDL_RenderClear(ren);  // starfield zone measured BLACK (S: census)

            // (1a) t414 FRAME LAW (D15 "the decorative framing is still
            // wrong and mostly missing"; docs/re/_wip_t414.md S2a): the
            // original is a TEXTURED CHROME PAGE with the cosmos punched
            // in — texture runs the FULL screen (measured: left band ends
            // x7 at y=200, top ends y8 and bottom starts y374 at x=300,
            // the DESC->RACELIST gutter x494..501 and the bottom-panel
            // gaps are texture). t401 painted only 2 bands; the gaps read
            // as missing frame. The page is built ONCE as a static
            // texture (titleArt pattern — 307k splitmix points per frame
            // would starve the 16 ms budget), copied full-screen, then
            // the cosmos rect kNewgameCosmosRect (8,9)-(493,373) is
            // black-filled over it.
            static SDL_Texture* chromePage = nullptr;
            if (!chromePage) {
                chromePage =
                    SDL_CreateTexture(ren, SDL_PIXELFORMAT_ARGB8888,
                                      SDL_TEXTUREACCESS_STATIC, kDisplayW,
                                      kDisplayH);
                if (chromePage) {
                    std::vector<uint32_t> px(size_t(kDisplayW) * kDisplayH);
                    for (int y = 0; y < kDisplayH; y++)
                        for (int x = 0; x < kDisplayW; x++) {
                            // tA2 WELL EDGE LAW (mapchrome.h): the cosmos
                            // recess (row 7, cols x7/x493) and the 2-row
                            // RAISED ridge (rows 373/374) are part of the
                            // ONE page pass — no second renderer (G6).
                            const RGB c = newgameWellEdgeAt(x, y)
                                              ? newgameWellEdgeColourAt(x, y)
                                              : textureColourAt(x, y);
                            px[size_t(y) * kDisplayW + x] =
                                0xFF000000u | (uint32_t(c.r) << 16) |
                                (uint32_t(c.g) << 8) | uint32_t(c.b);
                        }
                    SDL_UpdateTexture(chromePage, nullptr, px.data(),
                                      kDisplayW * int(sizeof(uint32_t)));
                }
            }
            if (chromePage) SDL_RenderCopy(ren, chromePage, nullptr, nullptr);
            {
                SDL_Rect cosmos{kNewgameCosmosRect.x0, kNewgameCosmosRect.y0,
                                kNewgameCosmosRect.x1 - kNewgameCosmosRect.x0 + 1,
                                kNewgameCosmosRect.y1 - kNewgameCosmosRect.y0 + 1};
                SDL_SetRenderDrawColor(ren, 0, 0, 0, 255);
                SDL_RenderFillRect(ren, &cosmos);
            }

            // (1) t414 SPINNING PREVIEW (D15 "there should be a spinning
            // star field commensurate with the star density in the upper
            // left"; the Very Dense original capture shows ~100 COLOURED
            // points == ladder rung 100, no lanes — docs/re/_wip_t414.md
            // S2b). The t393 previewCamp projection (grey pips + lanes of
            // the 50-star build) is REPLACED: N = the density setting,
            // splitmix64 points on a sphere shell (NEVER the sim rng —
            // gate 3l byte-identity law), pinhole-projected with the
            // t399 camera maths (standoff 1760, focal 500 -> shell radius
            // 440 projects to 167 px, inside the rect half-height 182),
            // yaw advancing kPreviewSpinPerFrame per frame. Tints follow
            // the vendor point families via neutralTint (cam3d port
            // palette). WHICH stars these are = preview, not the map:
            // the original's preview does not match its own map either
            // (it is a generic cosmos).
            // t423 PREVIEW PLACEMENT + SPRITE LAW (defects f/g,
            // docs/re/_wip_t423.md F4/F7/F8): the vendor generator
            // FUN_00022728 places each star on a CIRCLE of radius 300 in
            // the screen plane (angle from the LCG rand chain) at depth
            // 1000 + UNIFORM(-300,+300) — a filled CYLINDER VOLUME, not a
            // sphere shell (the port's pre-t423 splitmix spherical-surface
            // model was the "fills the VOLUME not a shell" defect).
            // Sprites = cos_star.shp through the t200 SEL law SEL = 4*K +
            // cls, cls = 4-band ladder on the transformed depth (v>=220 ->
            // 0, 1..219 -> 1, -220..0 -> 2, v<-220 -> 3; planets-ui.md §6);
            // the preview records carry no type byte so K=0 (NAMED SEAM)
            // -> k1..k3 (2x2 vendor sprite at NATIVE size = larger than
            // the old 1px point and pixelated; k0's header overlap fails
            // the walk, F5). SPIN
            // PUMP (defect g): the vendor arms script @0x69b8 (SET
            // ds:0x7458e, read by the cosmos repaint; F7) while the cursor
            // is inside zone x379..493 y420..472 (dispatcher
            // 0x52993/0x529c1 cmp ebx 0x17b/0x1ed, ecx 0x1a4/0x1d8 — F2) —
            // the port advances yaw
            // faster while that zone is hovered, on top of the idle spin.
            {
                static double previewYaw = 0.0;
                int hmx = -1, hmy = -1;
                SDL_GetMouseState(&hmx, &hmy);
                const bool beginHover =
                    hmx >= 379 && hmx <= 493 && hmy >= 420 && hmy <= 472;
                previewYaw +=
                    kPreviewSpinPerFrame * (beginHover ? 6.0 : 1.0);
                const int n = kDensityStarCounts[densityIdx];
                const double cx =
                    (kNewgameCosmosRect.x0 + kNewgameCosmosRect.x1) / 2.0;
                const double cy =
                    (kNewgameCosmosRect.y0 + kNewgameCosmosRect.y1) / 2.0;
                const double focal = 500.0;
                for (int i = 0; i < n; i++) {
                    uint64_t z = uint64_t(i) * 0x9e3779b97f4a7c15ull +
                                 0x5851f42d403c3b23ull;
                    z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ull;
                    z = (z ^ (z >> 27)) * 0x94d045bb41f336ull;
                    z = z ^ (z >> 31);
                    // Vendor law: circle radius 300, depth 1000 +- 300.
                    const double th =
                        double(z % 1000000ull) / 1000000.0 * 6.283185307;
                    const double dz =
                        double((z >> 20) % 601ull) - 300.0;
                    const double x = 300.0 * std::cos(th + previewYaw);
                    const double y = 300.0 * std::sin(th + previewYaw);
                    const double depth = 1000.0 + dz;
                    const int px = int(cx + x * focal / depth);
                    const int py = int(cy + y * focal / depth);
                    if (px < kNewgameCosmosRect.x0 ||
                        px > kNewgameCosmosRect.x1 ||
                        py < kNewgameCosmosRect.y0 ||
                        py > kNewgameCosmosRect.y1)
                        continue;
                    // SEL law, K=0: cls from the transformed depth offset.
                    const long v = lround(dz);
                    const int cls = v >= 220 ? 0 : (v >= 1 ? 1 : (v >= -220 ? 2 : 3));
                    const int rec = 4 * 0 + cls;  // K=0 named seam
                    bool drew = false;
                    if (cosStarLib.count() > rec)
                        drew = blitShape(ren, cosStarLib, rec, px - 1, py - 1);
                    if (!drew) {
                        // cos_star unavailable/k0: 2x2 tint block (the
                        // point-family law stays honest, no fake art).
                        const RGB t = neutralTint(int((z >> 42) % 13));
                        SDL_SetRenderDrawColor(ren, t.r, t.g, t.b, 255);
                        SDL_Rect q{px - 1, py - 1, 2, 2};
                        SDL_RenderFillRect(ren, &q);
                    }
                }
            }

            // (2) Summary block: static.txt //168 template, white, centred
            // under the starfield (measured rows 327/340/353, pitch 13).
            std::vector<std::string> summary;
            newgameSummary(kDensityStarCounts[densityIdx], speciesSetting,
                           atmosphere, &summary);
            for (size_t i = 0; i < summary.size(); i++) {
                const int w = txt.width(summary[i], true);  // tA3 BIG face
                txt.draw(ren, kSummaryCentreX - w / 2,
                         kSummaryTop + int(i) * kSummaryPitch, summary[i],
                         true, kNewgameInk);
            }

            // (3) NEWGAMEWND description panel — t401 REBUILD (D11 "the
            // species description box ... is empty and transparent ... it
            // should be solid"). MEASURED on the user original: interior
            // BLACK 71.9% (39363/54715 px) + green ring (0,142,69) x357..461
            // rows 45..149 (centre (409,97) r 52) + portrait + purple planet
            // disc x383..419 y198..239 + green crest x441..455 y205..229
            // (raceflag NATIVE 14x24 exact-size match) + green lore. The
            // pre-t401 port drew only a 1-px outline = the defect.
            {
                SDL_Rect fill{kNewgameWnd.x0, kNewgameWnd.y0,
                              kNewgameWnd.x1 - kNewgameWnd.x0 + 1,
                              kNewgameWnd.y1 - kNewgameWnd.y0 + 1};
                SDL_SetRenderDrawColor(ren, 0, 0, 0, 255);
                SDL_RenderFillRect(ren, &fill);
            }

            // (4) Species name (green, rows 18..27, centred on the panel) +
            // "Player Species" header (white, rows 16..25, centred RACELIST).
            const int selIndex = scrollOffset + selSlot;
            const std::string selName = speciesNameAt(selIndex);
            {
                const int w = txt.width(selName, true);  // tA3 BIG face
                txt.draw(ren, (kNewgameWnd.x0 + kNewgameWnd.x1 + 1) / 2 - w / 2,
                         kNameTop, selName, true, kLore);
            }
            {
                const std::string hdr = "Player Species";  // static.txt //153
                const int w = txt.width(hdr, true);  // tA3 BIG face
                txt.draw(ren, (kRaceList.x0 + kRaceList.x1 + 1) / 2 - w / 2,
                         kHeaderTop, hdr, true, kNewgameInk);
            }

            // (3b) t401 PANEL ART: portrait ring (green, the vendor ring
            // colour (0,142,69) == kLore ink — measured ring px), portrait
            // smraceNN scaled 2x inside (scale = port law, seam), planet
            // disc (purple bands (40,20,32)/(109,56,93)/(125,121,138)
            // measured; honest-vector concentric circles), crest raceflag
            // k<specnum> NATIVE at (441,205). A missing lib degrades to the
            // ring-only drawing (never a fake stand-in).
            // t423 DEFECT (e): the ring is the racering.shp k0 RECORD
            // (53x53, walk-OK), NOT a vector stroke. Scale law pin: the
            // measured ring radius 53 (menulaw kDescRingR/kRaceRingR) ==
            // record 53 drawn at 2x — the SAME scale as the smrace
            // portraits (49 -> 98, t401 S8), so the class scale is 2.
            // tA1 BBOX-DIFF LAW: racering k<idx> is 109x109 CONTENT at
            // (L,T)=(-55,-55) [measured header verbatim] — the vendor blits
            // it NATIVE at centre+(L,T); the old 53x53/2x reading was the
            // port's own dims misparse (docs/re/_wip_tA1.md F2). Vector
            // fallback only when the lib is unavailable.
            {
                bool ringDrawn = false;
                if (raceringLib.count() > playerColourIdx) {
                    const auto& rr = raceringLib.record(playerColourIdx);
                    dimsCheck("desc-ring", int(rr.width), int(rr.height),
                              kDescRingCentre.x + int(rr.left),
                              kDescRingCentre.y + int(rr.top));
                    ringDrawn = blitShape(ren, raceringLib, playerColourIdx,
                                          kDescRingCentre.x + rr.left,
                                          kDescRingCentre.y + rr.top);
                }
                if (!ringDrawn) {
                    SDL_SetRenderDrawColor(ren, kLore.r, kLore.g, kLore.b,
                                           255);
                    for (int a = 0; a < 360; a += 1) {  // dense ring, 1px step
                        const double rad = a * 3.14159265 / 180.0;
                        SDL_RenderDrawPoint(
                            ren, kDescRingCentre.x + int(kDescRingR * cos(rad)),
                            kDescRingCentre.y + int(kDescRingR * sin(rad)));
                    }
                }
                if (const auto* pl = portraitFor(selIndex)) {
                    // tA1: smrace content = bbox 100x100 at (L,T)=(-50,-50)
                    // [measured verbatim]; NATIVE blit at the ring centre,
                    // the record's own TRANSPARENT-SKIP corners clip it to
                    // the disc (t414's manual circle compensated the port's
                    // truncated 49x49 read — no longer needed).
                    const auto& pr0 = pl->record(0);
                    dimsCheck("desc-portrait", int(pr0.width),
                              int(pr0.height),
                              kDescRingCentre.x + int(pr0.left),
                              kDescRingCentre.y + int(pr0.top));
                    blitShape(ren, *pl, 0, kDescRingCentre.x + pr0.left,
                              kDescRingCentre.y + pr0.top);
                }
                // t414 PLANET IMAGE (D15 "the planet image is missing from
                // the race info frame"): the zone x383..419 y198..239
                // (~37x42) carries a PLANET SPHERE record — planets.shp is
                // the planet-sphere library (55 recs = 11 biome groups x
                // size ladder 11/18/25/35/47, docs/re/shp.md S geometry);
                // the 35px class matches the measured zone (37x42). Group
                // = specnum % 11 (preview assignment, named seam — no
                // citation maps race->biome for the DESC panel). The t401
                // honest-vector purple circles are REPLACED.
                if (planetsLib.count() >= 55) {
                    // tA1 SIZE-CLASS CORRECTION [measured]: under the
                    // bbox-diff law the ladder is {24,38,52,71,95} and the
                    // DESC zone's measured chromatic extent 37x42 (t401 S8)
                    // matches size index 1 (38) ONLY; the old "+3" fitted
                    // the port's truncated dims read. NATIVE blit at
                    // centre+(L,T). The GROUP axis stays the named seam —
                    // tNG-C owns the race->planet law (D19).
                    const int rec = (selIndex % 11) * 5 + 1;
                    const auto& pr = planetsLib.record(rec);
                    dimsCheck("desc-planet", int(pr.width), int(pr.height),
                              kDescPlanetCentre.x + int(pr.left),
                              kDescPlanetCentre.y + int(pr.top));
                    blitShape(ren, planetsLib, rec,
                              kDescPlanetCentre.x + pr.left,
                              kDescPlanetCentre.y + pr.top);
                }
                if (raceflagLib.count() > 0 && selIndex >= 0 &&
                    selIndex < raceflagLib.count())
                    blitShape(ren, raceflagLib, selIndex, kDescCrestRect.x0,
                              kDescCrestRect.y0);
            }

            // (5) Lore: "The <Name> <fragment>" (static.txt //154 template +
            // newgame.txt line N+1), green, word-wrapped into kLoreBox.
            {
                const std::string frag =
                    selIndex >= 0 && lore && selIndex < int(lore->size())
                        ? (*lore)[size_t(selIndex)]
                        : std::string();
                if (!frag.empty()) {
                    const auto lines = wrapToWidth(
                        loreSentence(selName, frag),
                        kLoreBox.x1 - kLoreBox.x0 - 8,
                        [&](const std::string& s) {
                            return txt.width(s, false);
                        });
                    for (size_t i = 0; i < lines.size(); i++) {
                        const int w = txt.width(lines[i], false);  // SM face
                        txt.draw(ren,
                                 (kLoreBox.x0 + kLoreBox.x1 + 1) / 2 - w / 2,
                                 kLoreTextTop + int(i) * kLoreLinePitch,
                                 lines[i], false, kLore);
                    }
                }
            }

            // (6) RACELIST: navy interior + bevel + THREE portrait slots
            // (measured S: bands 49-153/157-262/266-372, pitch 108) + scroll
            // arrow squares. t401 (D11 "artwork isn't rendered at all in the
            // Player Species column"): the vendor rows are smraceNN portraits
            // scaled 2x (chromatic art run x505..613 measured; ring greys
            // x506..511/608..612 -> r 53, centre x 559) and carry NO text
            // (two independent vision reads of the original crop agree) —
            // the grey-disc + NAME stand-in is REMOVED. A refused lib
            // degrades to the ring alone (honest, no fake portrait).
            SDL_Rect rl{kRaceList.x0, kRaceList.y0,
                        kRaceList.x1 - kRaceList.x0 + 1,
                        kRaceList.y1 - kRaceList.y0 + 1};
            SDL_SetRenderDrawColor(ren, kPanel.r, kPanel.g, kPanel.b, 255);
            SDL_RenderFillRect(ren, &rl);
            // tA2 PANEL INSET LAW (mapchrome.h; replaces the fabricated
            // symmetric kBevel outline): dark inset top+left, NOTHING at
            // right/bottom. RACELIST left edge family (15,35,49) confirmed
            // on the row-200 probe (x503/x504).
            for (int x = kRaceList.x0; x <= kRaceList.x1; x++) {
                const RGB c = newgamePanelTopAt(x);
                SDL_SetRenderDrawColor(ren, c.r, c.g, c.b, 255);
                SDL_RenderDrawPoint(ren, x, kRaceList.y0);
            }
            for (int y = kRaceList.y0 + 1; y <= kRaceList.y1; y++) {
                const RGB c = newgamePanelLeftAt(y);
                SDL_SetRenderDrawColor(ren, c.r, c.g, c.b, 255);
                SDL_RenderDrawPoint(ren, kRaceList.x0, y);
            }
            for (int i = 0; i < kRaceSlotCount; i++) {
                const int specnum = scrollOffset + i;
                const int cy = kRaceSlotTop + i * kRaceSlotPitch +
                               kRaceSlotH / 2;
                if (i == selSlot) {  // selection: luminance change, not hue
                    SDL_SetRenderDrawColor(ren, kSelBg.r, kSelBg.g, kSelBg.b,
                                           255);
                    SDL_Rect band{kRaceList.x0 + 1, cy - kRaceSlotH / 2,
                                  kRaceList.x1 - kRaceList.x0 - 1, kRaceSlotH};
                    SDL_RenderFillRect(ren, &band);
                }
                if (specnum < rosterCount()) {
                    // tA1 BBOX-DIFF LAW (supersedes the t423c 2x reading):
                    // racering k7 content = 109x109 at (L,T)=(-55,-55),
                    // smrace content = 100x100 at (-50,-50) — NATIVE blits
                    // anchored at the row centre reproduce the MEASURED
                    // vendor art exactly (ring band r50..55, disc ~98-100;
                    // docs/re/_wip_tA1.md F2 witness 4). Vector fallback
                    // only when the lib is unavailable.
                    bool ringDrawn = false;
                    if (raceringLib.count() > 7) {
                        const auto& rr = raceringLib.record(7);
                        dimsCheck(("racelist-row" + std::to_string(i) +
                                   "-ring").c_str(),
                                  int(rr.width), int(rr.height),
                                  kRacePortraitCx + int(rr.left),
                                  cy + int(rr.top));
                        ringDrawn = blitShape(ren, raceringLib, 7,
                                              kRacePortraitCx + rr.left,
                                              cy + rr.top);
                    }
                    if (!ringDrawn) {
                        SDL_SetRenderDrawColor(ren, kBevel.r, kBevel.g,
                                               kBevel.b, 255);
                        for (int a = 0; a < 360; a += 2) {  // silver ring r53
                            const double rad = a * 3.14159265 / 180.0;
                            SDL_RenderDrawPoint(
                                ren,
                                kRacePortraitCx + int(kRaceRingR * cos(rad)),
                                cy + int(kRaceRingR * sin(rad)));
                        }
                    }
                    if (const auto* pl = portraitFor(specnum)) {
                        const auto& pr0 = pl->record(0);
                        dimsCheck(("racelist-row" + std::to_string(i) +
                                   "-portrait").c_str(),
                                  int(pr0.width), int(pr0.height),
                                  kRacePortraitCx + int(pr0.left),
                                  cy + int(pr0.top));
                        blitShape(ren, *pl, 0, kRacePortraitCx + pr0.left,
                                  cy + pr0.top);
                    }
                }
            }
            for (int i = 0; i < 2; i++) {  // arrows (measured corner squares)
                const Rect& ar = i == 0 ? kRaceArrowUp : kRaceArrowDown;
                SDL_Rect r{ar.x0, ar.y0, ar.x1 - ar.x0 + 1,
                           ar.y1 - ar.y0 + 1};
                SDL_SetRenderDrawColor(ren, kArrowFill.r, kArrowFill.g,
                                       kArrowFill.b, 255);
                SDL_RenderFillRect(ren, &r);
                SDL_SetRenderDrawColor(ren, kArrowInk.r, kArrowInk.g,
                                       kArrowInk.b, 255);
                const int cx = (ar.x0 + ar.x1) / 2, cy = (ar.y0 + ar.y1) / 2;
                for (int d = -4; d <= 4; d++) {
                    const int len = 4 - std::abs(d);
                    for (int t = 0; t <= len; t++)
                        SDL_RenderDrawPoint(
                            ren, cx + d,
                            i == 0 ? cy - t + 2 : cy + t - 2);
                }
            }

            // (7) Bottom config bar: four windows.txt-cited panels + the
            // measured Begin zone. Panels: navy fill + bevel + white label
            // (measured rows 393..403). t401 (D11 "the artwork is rendered
            // incorrectly in the bottom row"): the wheel face comes from
            // newgameWheelFrame(control, value) — a DIFFERENT 3cfgnew record
            // per setting (the pre-t401 port blitted k0 into every panel at
            // (cx-42, y0+26)); blit anchored so the record's content circle
            // centres on the panel ((cx-28, 408), measured bbox x38..92
            // y408..462). The in-panel value word is REMOVED: the original
            // has none (the summary block carries the values).
            for (int i = 0; i < kNewgameControlCount; i++) {
                const NewgameControl& c = kNewgameControls[i];
                SDL_Rect r{c.rect.x0, c.rect.y0, c.rect.x1 - c.rect.x0 + 1,
                           c.rect.y1 - c.rect.y0 + 1};
                SDL_SetRenderDrawColor(ren, kPanel.r, kPanel.g, kPanel.b, 255);
                SDL_RenderFillRect(ren, &r);
                // tA2 PANEL INSET LAW (mapchrome.h): dark inset top+left,
                // no line right/bottom (measured at this panel's edges —
                // topline y381 mean 27.1, left col x7 mean 33.0, right/
                // bottom flat fill; the symmetric kBevel rect was the port
                // defect).
                for (int x = c.rect.x0; x <= c.rect.x1; x++) {
                    const RGB e = newgamePanelTopAt(x);
                    SDL_SetRenderDrawColor(ren, e.r, e.g, e.b, 255);
                    SDL_RenderDrawPoint(ren, x, c.rect.y0);
                }
                for (int y = c.rect.y0 + 1; y <= c.rect.y1; y++) {
                    const RGB e = newgamePanelLeftAt(y);
                    SDL_SetRenderDrawColor(ren, e.r, e.g, e.b, 255);
                    SDL_RenderDrawPoint(ren, c.rect.x0, y);
                }
                const int cxp = (c.rect.x0 + c.rect.x1) / 2;
                const int wl = txt.width(c.label, true);  // tA3 BIG face
                txt.draw(ren, cxp - wl / 2, c.rect.y0 + kControlLabelDy,
                         c.label, true, kNewgameInk);
                const int value = i == 0
                                      ? kDensityStarCounts[densityIdx]
                                      : (i == 1 ? speciesSetting : atmosphere);
                const int frame = newgameWheelFrame(i, value);
                static bool wheelRefused[3] = {};
                if (frame >= 0 && frame < cfgNew.count()) {
                    // The 84x79 records carry a SECOND stacked-circle band
                    // below the content circle (t401 S10 k0 shape); the
                    // vendor panel shows only the top circle — clip the
                    // blit to the panel rect (measured: no second wheel in
                    // any original panel zone, docs/re/_wip_t414.md S4).
                    SDL_Rect clip{c.rect.x0, c.rect.y0,
                                  c.rect.x1 - c.rect.x0 + 1,
                                  c.rect.y1 - c.rect.y0 + 1};
                    SDL_RenderSetClipRect(ren, &clip);
                    const bool drew = blitShape(ren, cfgNew, frame,
                                                cxp - kWheelBlitHalfW,
                                                kWheelBlitTop);
                    SDL_RenderSetClipRect(ren, nullptr);
                    if (!drew && !wheelRefused[i]) {
                        // Present but UNDECODABLE after the t423 partial
                        // walk (k12 now paints rows 0..~54 — the shipped
                        // archive truncation is INSIDE ascend01.cob,
                        // F5b; only a load failure lands here). Print-once.
                        wheelRefused[i] = true;
                        std::printf("ui raceconfig wheel refused: ctrl %d "
                                    "k%d (lib %d recs)\n",
                                    i, frame, cfgNew.count());
                        std::fflush(stdout);
                    }
                } else if (frame >= 0 && !wheelRefused[i]) {
                    wheelRefused[i] = true;
                    std::printf("ui raceconfig wheel refused: ctrl %d k%d "
                                "(lib %d recs)\n",
                                i, frame, cfgNew.count());
                    std::fflush(stdout);
                }
            }
            // Player^Color (windows.txt L653, MSG 0 = inert). t414: the
            // zone carries SEVEN measured player icons (see the chip loop
            // below) — the t401 "no chromatic px" census scanned the label
            // rows and is REFUTED (docs/re/_wip_t414.md S2d).
            {
                const Rect c = kPlayerColorPanel;  // t414 visual extent
                SDL_Rect r{c.x0, c.y0, c.x1 - c.x0 + 1, c.y1 - c.y0 + 1};
                SDL_SetRenderDrawColor(ren, kPanel.r, kPanel.g, kPanel.b, 255);
                SDL_RenderFillRect(ren, &r);
                // tA2 PANEL INSET LAW (mapchrome.h): topline y381
                // x384..493 mean 28.5 same families (panel1 was 27.1);
                // symmetric kBevel rect REFUTED at this panel too.
                for (int x = c.x0; x <= c.x1; x++) {
                    const RGB e = newgamePanelTopAt(x);
                    SDL_SetRenderDrawColor(ren, e.r, e.g, e.b, 255);
                    SDL_RenderDrawPoint(ren, x, c.y0);
                }
                for (int y = c.y0 + 1; y <= c.y1; y++) {
                    const RGB e = newgamePanelLeftAt(y);
                    SDL_SetRenderDrawColor(ren, e.r, e.g, e.b, 255);
                    SDL_RenderDrawPoint(ren, c.x0, y);
                }
                const std::string lbl = "Player Color";  // NAME 'Player^Color'
                const int cxp = (c.x0 + c.x1) / 2;
                const int wl = txt.width(lbl, true);  // tA3 BIG face
                txt.draw(ren, cxp - wl / 2, c.y0 + kPlayerColorLabelDy, lbl,
                         true, kNewgameInk);
                // t414 PLAYER ICONS (D15 "the player icons are missing
                // from the 'Player Color' box"): MEASURED on the original
                // at rows 434..459, seven 14x26 chips at x 384+16k with
                // base+highlight colours (menulaw kPlayerChipRgb). The
                // t401 census scanned the LABEL rows and reported "no
                // chromatic px" — refuted (docs/re/_wip_t414.md S2d). The
                // highlight is the top 14 rows (measured hi-count 37 vs
                // base 60 per chip = a partial face; top-half placement is
                // the port reading of the bevel class).
                for (int k = 0; k < kPlayerChipCount; k++) {
                    const SDL_Rect body{kPlayerChipX0 + k * kPlayerChipPitch,
                                        kPlayerChipY, kPlayerChipW,
                                        kPlayerChipH};
                    const RGB& base = kPlayerChipRgb[k][0];
                    SDL_SetRenderDrawColor(ren, base.r, base.g, base.b, 255);
                    SDL_RenderFillRect(ren, &body);
                    const RGB& hi = kPlayerChipRgb[k][1];
                    SDL_SetRenderDrawColor(ren, hi.r, hi.g, hi.b, 255);
                    SDL_Rect top{kPlayerChipX0 + k * kPlayerChipPitch,
                                 kPlayerChipY, kPlayerChipW, 13};
                    SDL_RenderFillRect(ren, &top);
                }
            }
            // Begin New Game (measured rect; NOT windows.txt — STARTGAME is
            // STATE "1 12"). White label rows measured ~456. t401 (D11 "the
            // Begin New Game box is empty except for text"): the original
            // carries (a) a hash-noise dot cluster in the left band
            // x496..570 (greys (225,227,229)/(255,255,255)/(164,171,177)/
            // (103,116,126)/(97,97,97) + teals measured; splitmix64 law like
            // the page texture — the PATTERN is the named seam) and (b) the
            // species emblem: smrace NATIVE 49x49 at (577,394), inside the
            // green-ring zone x573..629 y390..446 (centre (601,418)).
            // tA2: the FILL uses the MEASURED visual extent (502,381)..
            // (632,472) — the hit rect kBeginNewGameBtn stays windows.txt
            // {494,373,639,472}; the old full-hit-rect navy fill painted
            // over the page-texture gutter x494..501 (docs F5). Inset law:
            // dark noise top row 381 + left col 502, nothing right/bottom.
            {
                const Rect vis = kBeginPanelVisual;
                SDL_Rect r{vis.x0, vis.y0, vis.x1 - vis.x0 + 1,
                           vis.y1 - vis.y0 + 1};
                SDL_SetRenderDrawColor(ren, kPanel.r, kPanel.g, kPanel.b, 255);
                SDL_RenderFillRect(ren, &r);
                for (int x = vis.x0; x <= vis.x1; x++) {
                    const RGB e = newgamePanelTopAt(x);
                    SDL_SetRenderDrawColor(ren, e.r, e.g, e.b, 255);
                    SDL_RenderDrawPoint(ren, x, vis.y0);
                }
                for (int y = vis.y0 + 1; y <= vis.y1; y++) {
                    const RGB e = newgamePanelLeftAt(y);
                    SDL_SetRenderDrawColor(ren, e.r, e.g, e.b, 255);
                    SDL_RenderDrawPoint(ren, vis.x0, y);
                }
                // (a) dot cluster: ~6% of the band pixels, deterministic.
                for (int y = kBeginDotsBand.y0; y <= kBeginDotsBand.y1; y++)
                    for (int x = kBeginDotsBand.x0; x <= kBeginDotsBand.x1;
                         x++) {
                        uint64_t z =
                            (uint64_t(uint32_t(x)) << 32) ^
                            uint64_t(uint32_t(y)) ^ 0x9e3779b97f4a7c15ull;
                        z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ull;
                        z = (z ^ (z >> 27)) * 0x94d045bb41f336ull;
                        z = z ^ (z >> 31);
                        if (z % 100u >= 6u) continue;
                        static const RGB kDot[6] = {
                            {255, 255, 255}, {225, 227, 229}, {164, 171, 177},
                            {103, 116, 126}, {97, 97, 97},    {69, 105, 109}};
                        const RGB& c = kDot[z % 6u];
                        SDL_SetRenderDrawColor(ren, c.r, c.g, c.b, 255);
                        SDL_RenderDrawPoint(ren, x, y);
                    }
                // (b) emblem ring + portrait of the SELECTED species.
                SDL_SetRenderDrawColor(ren, kLore.r, kLore.g, kLore.b, 255);
                for (int a = 0; a < 360; a += 2) {
                    const double rad = a * 3.14159265 / 180.0;
                    SDL_RenderDrawPoint(
                        ren, kBeginEmblemCentre.x + int(28 * cos(rad)),
                        kBeginEmblemCentre.y + int(28 * sin(rad)));
                }
                if (const auto* pl = portraitFor(scrollOffset + selSlot))
                    blitShape(ren, *pl, 0, kBeginEmblemRect.x0,
                              kBeginEmblemRect.y0);
                const std::string lbl = "Begin New Game";  // static.txt //169
                const int w = txt.width(lbl, true);  // tA3 BIG face
                txt.draw(ren,
                         (r.x + (r.w - w) / 2), kBeginLabelTop, lbl, true,
                         kNewgameInk);
            }
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
            // D9 LAW (user 2026-11-14) + t392 (windows.txt TEXTITEM items
            // 'Alt-L'/'Alt-S'/'Alt-X' L129/149/170): Alt-L = Load, Alt-S =
            // Save, Alt-X = Exit to DOS from the title screen — the on-
            // screen buttons' hotkey twins. Routing lives in bootHotkey
            // (pinned).
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
                // t393 NEW GAME input law (full screen — the title column is
                // NOT on this screen, so bootClick does not route here):
                // arrows -> scroll window, rows -> select, wheel -> cycle the
                // setting (SENDMESSAGE 501/503/505 = the vendor *_MORE
                // semantics), Begin -> Campaign, PlayerColor inert (MSG 0).
                if (st == BootState::RaceConfig) {
                    const int ai = newgameArrowAt(p);
                    if (ai >= 0) {
                        const int maxOff =
                            std::max(0, rosterCount() - kRaceSlotCount);
                        scrollOffset =
                            std::clamp(scrollOffset + (ai == 0 ? -1 : 1), 0,
                                       maxOff);
                        std::printf("ui raceconfig arrow %s offset %d\n",
                                    ai == 0 ? "up" : "down", scrollOffset);
                        std::fflush(stdout);
                        continue;
                    }
                    const int row = newgameRowAt(p);
                    if (row >= 0 && scrollOffset + row < rosterCount()) {
                        selSlot = row;
                        std::printf("ui raceconfig select specnum %d %s\n",
                                    scrollOffset + row,
                                    speciesNameAt(scrollOffset + row).c_str());
                        std::fflush(stdout);
                        continue;
                    }
                    const int ci = newgameControlAt(p);
                    if (ci >= 0) {
                        // *_MORE = advance one rung (density cycles the t78
                        // ladder; species 3..Seven; atmosphere 0..2).
                        if (ci == 0)
                            densityIdx = (densityIdx + 1) % kDensityCycleCount;
                        else if (ci == 1)
                            speciesSetting =
                                speciesSetting >= 7 ? 3 : speciesSetting + 1;
                        else
                            atmosphere = (atmosphere + 1) % 3;
                        std::printf("ui raceconfig click %s msg %d -> %s\n",
                                    kNewgameControls[ci].name,
                                    kNewgameControls[ci].message,
                                    ci == 0
                                        ? kDensityWords[densityIdx]
                                        : (ci == 1
                                               ? speciesCountWord(speciesSetting)
                                               : atmosphereWord(atmosphere)));
                        std::fflush(stdout);
                        continue;
                    }
                    const int chip = newgameChipAt(p);
                    if (chip >= 0) {
                        // t423c PLAYER-COLOUR REASSIGN [verified 0x529d2 +
                        // FUN_000232ec]: a click in x379..493 y420..472
                        // stores word[win+0xb5]=idx and re-derives every
                        // race-slot colour (player keeps the clicked idx,
                        // AI races draw distinct rand()%7). Visible here:
                        // the DESC-panel ring = racering k<idx> (C2-F5).
                        // windows.txt MSG 0 (L664) only means the zone
                        // SENDS no message — the handler is real (the
                        // t401 "inert" reading is REFUTED by the disasm).
                        playerColourIdx = chip;
                        colourLcg = 0x12e10u;  // seam: per-click reseed
                        assignRaceColours(playerColourIdx, speciesSetting,
                                          &colourLcg, raceColours);
                        std::printf(
                            "ui raceconfig player colour idx %d (races %d)\n",
                            playerColourIdx, speciesSetting);
                        std::fflush(stdout);
                        continue;
                    }
                    if (inRect(kPlayerColorRect, p)) {
                        std::printf("ui raceconfig click Player^Color msg 0\n");
                        std::fflush(stdout);
                        continue;  // label band (windows.txt L653) = MSG 0
                    }
                    if (inRect(kBeginNewGameBtn, p)) {
                        std::printf(
                            "ui raceconfig begin density %d species %d "
                            "atmosphere %d species-pick %d\n",
                            kDensityStarCounts[densityIdx], speciesSetting,
                            atmosphere, scrollOffset + selSlot);
                        std::fflush(stdout);
                        // t412: Begin -> the RACE INTRO (history.txt,
                        // FUN_0002b48a) -> map. The pick + atmosphere ride
                        // into the intro (the gated PEACE/NEUTRAL/HOSTILE
                        // section is chosen by the Atmosphere wheel).
                        beginSpecies = scrollOffset + selSlot;
                        beginAtmosphere = atmosphere;
                        // Call DIRECTLY: this `continue` re-tests the
                        // while-condition (Title||RaceConfig), so a mere
                        // `st = RaceIntro` here would EXIT the loop before
                        // the intro branch below could run (t412 witness:
                        // "ui title exit: raceintro").
                        st = runRaceIntro(ren, txt, dataRoot, beginSpecies,
                                          beginAtmosphere,
                                          speciesNameAt(beginSpecies));
                        continue;
                    }
                    continue;  // dead zone on the full screen
                }
                const int idx = titleButtonAt(p);
                const BootState next = bootClick(st, p);
                if (next == st) continue;  // click outside any live button
                // t437 BUTTON SFX: title-menu buttons play soundfx
                // manifest[0] "button" — the windows.txt SOUNDCHANNEL value
                // (0 on every file line) that the vendor's press handler
                // plays via HIWORD(record+0x57) (audio.md §6.9, cited;
                // supersedes the t395/t404 click08 port choice — click08 is
                // off-manifest and vendor-unreachable).
                if (const char* sfx = sfxForPress(UiPressSite::TitleButton))
                    if (audio) audio->play(sfx);
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
