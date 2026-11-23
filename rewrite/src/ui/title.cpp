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
#include <optional>
#include <vector>

#include "formats/gif.h"
#include "formats/shp.h"
#include "game/campaign.h"
#include "game/mapgen.h"  // tNG-B B1: wheel-galaxy rebuild (MapGenerator)
#include "game/starstat.h"
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
// kArrowFill/kArrowInk REMOVED (tNG-F2): the race-list scroll arrows are the
// cited 16x17 glyph-cell law (menulaw arrowGlyphColourAt), not a blue square
// plus drawn triangle. See docs/re/_wip_tNGF.md F3.

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
                         const std::vector<std::string>* lore,
                         NewGameSettings* newGameOut) {
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
    // tNG-B B2 SPECIES DEFAULT LAW [verified window-init 0x52c55]: the
    // vendor opens the screen with word[win+0xb9]=5 and child wheel art
    // +0x72 = 7 (k7 'Five' — the t401 anchor). The old value 7 was the
    // port's campaign player-count coupling (player + 6 AI); the vendor
    // wheel is INDEPENDENT of the built campaign (the click runs 0x22ce4
    // race-assignment, applying settings to play is the t393 named seam).
    // This was the B3 'species content confound ours k9 vs vendor k7'.
    int speciesSetting = 5;
    int atmosphere = 1;       // Neutral (measured vendor default, see above)
    int selSlot = 0, scrollOffset = 0;  // RACELIST window (3 of roster)
    // tNG-B B1 WHEEL-GALAXY LAW [verified disasm 0x52db9..0x52e57 + t295 S2]:
    // the vendor density click calls FUN_000226e4 = FULL REGENERATE (0x22878
    // parse + 0x22728 rand-consumer star POSITIONS + 0x234a4 lanes + 0x22ce4
    // reset) with N = hiword(dword[esp + rank*4 - 2]) = sorted ladder rung
    // {15,25,50,75,100}[rank]. The preview cosmos and the Begin-panel
    // starfield (count law word[obj+0x572]) are consequences of THAT galaxy:
    // every click draws a NEW star set (rand), never the same set clipped to
    // N (the pre-tNG-B defect: splitmix points were per-index stable, so the
    // field only grew/shrank at the tail). The port models the DISPLAY
    // galaxy with MapGenerator (placement laws untouched, splitmix-keyed,
    // never the sim rng — gate 3l byte identity); applying settings to the
    // LIVE campaign remains the t393 named seam (Begin enters play on the
    // built galaxy).
    const unsigned wheelBaseSeed =
        previewCamp ? unsigned(previewCamp->galaxy().seed) : 1u;
    int wheelGen = 0;
    std::optional<ascend::game::Galaxy> wheelGal;
    auto rebuildWheelGalaxy = [&](int rank, unsigned gen) {
        std::string werr;
        auto stats = ascend::game::StarStats::load(
            dataRoot + "/extracted/ascend00/starstat.txt", &werr);
        auto names = ascend::game::loadStarNames(
            dataRoot + "/extracted/ascend00/names.txt", &werr);
        if (!stats || names.empty()) return;  // honest: keep previous galaxy
        ascend::game::MapConfig mc;
        mc.starCount = densityStarCount(rank);
        mc.seed = wheelBaseSeed + gen;  // new set per regen (rand law)
        wheelGal = ascend::game::MapGenerator(mc, *stats, std::move(names))
                       .generate();
    };
    rebuildWheelGalaxy(densityIdx, 0);
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
    // tNG-C PLANET INDEX LAW [verified 0x5231d..0x5236d + bbox census]:
    // the DESC panel's planet = smhome.shp k<selected race row> NATIVE
    // 52x52 (name fetch 0x5231d "DATA\\smhome.shp", push (72,205) win-rel,
    // blit 0x5caac with bbox (-24,-26) -> screen (382,191); bounds assert
    // cmp 0x15 == 21 records). The t414 planets.shp k[(sel%11)*5+1]
    // invented biome mapping is REPLACED (named seam t414 closed).
    ascend::formats::ShapeLibrary smhomeLib;
    {
        std::string ferr;
        if (!smhomeLib.load(
                dataRoot + "/extracted/ascend01/data/smhome.shp", &ferr))
            std::printf("ui raceconfig smhome refused: %s\n", ferr.c_str());
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

            // tNG-S S27 PUMP (shared by BOTH fields; docs S27-X2/X5): the
            // vendor msg-0x3b pump (~1/s, t302) applies +-2 DEG world-Y per
            // tick to the preview orientation; the big field reads it as
            // POSITION, the Begin cluster as the rotated-depth CLASS term
            // (cited 0x526f0..0x5282f). One accumulator, both consumers.
            static double newgameSpinDeg = 0.0;
            static Uint32 newgameSpinMs = 0;
            {
                const Uint32 nowMs = SDL_GetTicks();
                if (newgameSpinMs == 0) newgameSpinMs = nowMs;
                while (nowMs - newgameSpinMs >=
                       Uint32(kPreviewSpinTickMs)) {
                    newgameSpinDeg += kPreviewSpinDegPerTick;
                    newgameSpinMs += Uint32(kPreviewSpinTickMs);
                }
            }

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
            // S2b). WHICH stars these are = preview, not the map: the
            // original's preview does not match its own map either (it is
            // a generic cosmos).
            // tNGS P4 PLACEMENT LAW (docs/re/_wip_tNGS.md S15; RETIRES the
            // t423 FUN_00022728 cylinder AND the pre-t423 splitmix
            // sphere-surface sampler): the vendor star generator is
            // FUN_00022878 — per star k THREE draws v = rng%1000-500,
            // NORMALIZE to the unit sphere (FUN_00052fa0), scale by the
            // SHELL ACCUMULATOR (440 start, -75 step, reset 50 — the
            // mapgen §OQ-025 table; shellRadiiFor). Camera (0,0,-1500),
            // FOV 35 (S5/FUN_00026a9c); focal 769.1 px puts the shell-440
            // ring at 225.6 px inside the well half-width 242.5.
            // Projection = perspective divide + 0.5 bias + viewport centre
            // (FUN_00053374). Sprite SEL = 4*type + cls with the S5 class
            // ladder v = round(z): >220 -> 0, 1..220 -> 1, -219..0 -> 2,
            // <=-220 -> 3 (cos_star; type from the wheel galaxy this field
            // mirrors for the count law — tNG-B B1; dims-zero types
            // 10..12 skip honestly, t200). NO sphere clip (S5).
            // ROTATION (S27 CYCLE 4 MEASURED+CODED; the S22 "does NOT
            // auto-spin" clause is WITHDRAWN — S26 re-read its 12 s
            // sampling as an aliasing artifact). LAW: the newgame field IS
            // the state==3 COSMOSWnd branch (rect 17,12,324,320 = the
            // vision-confirmed well); init 0x26dd1 latches [win+0xc0]=1
            // and the msg-0x3b pump (dispatcher 0x27a18, imm 2 at 0x27a32;
            // cadence t302 ~1/s) rotates WORLD Y by +-2 DEG per tick with
            // NO input. Witness run tngs4-20261123-010310 (61 frames @1 s,
            // cursor parked (600,250) outside both fields): big field ~950
            // changed px/step, ctrl 0; matched bright stars median 3.58
            // px/s at r~100 = 2.05 deg/s (vendor refcaps 1.8 deg/s). The
            // t423 F7 hover-armed zone is NOT modelled as a rate ADDER
            // this cycle: the witness parked the cursor outside the zone
            // and shows the pump alone at 2 deg/s; whether hovering adds
            // rate is unmeasured (named seam, owed a cursor-in-zone
            // witness), and D22 rules the base spin mouse-independent.
            {
                // S27: pump advance lives at the top of this screen block
                // (newgameSpinDeg) — ONE accumulator for both fields.
                // S28-X3 SIGN [MEASURED, run dbg-tngr-20261123-103130]: the
                // vendor spins the CAMERA BASIS fwd azimuth atan2(x,z) +2
                // deg/fire (latch bit0, mouse parked); a fixed star then
                // APPARENTLY drifts -2 deg/fire in view. The port rotates the
                // STAR model in a fixed camera, so the accumulator enters
                // NEGATED (this closes checklist #5 for the newgame field;
                // pre-S28 the sign was an unmeasured coin flip — M4 seam).
                const double previewYaw = -newgameSpinDeg;
                // tNG-B B1: N = the WHEEL galaxy's star count (count law
                // word[obj+0x572] is the regenerated galaxy, not the ladder
                // label), and each star's hash keys on wheelGen so a density
                // click DRAWS A NEW SET (vendor 0x22728 rand consumer) —
                // pre-tNG-B the points were per-index stable across clicks.
                const int n = wheelGal ? int(wheelGal->stars.size())
                                       : kDensityStarCounts[densityIdx];
                // tNG-B: the rendered cosmos count is an observable law line
                // (witness asserts it tracks the regen rungs; the pre-fix
                // defect froze n independently of the wheel galaxy).
                static int lastCosmosN = -1;
                if (n != lastCosmosN) {
                    std::printf("ui raceconfig cosmos n %d\n", n);
                    std::fflush(stdout);
                    lastCosmosN = n;
                }
                const double cx =
                    (kNewgameCosmosRect.x0 + kNewgameCosmosRect.x1) / 2.0;
                const double cy =
                    (kNewgameCosmosRect.y0 + kNewgameCosmosRect.y1) / 2.0;
                // tNGS P4: per-slot shell radius table (mapgen §OQ-025 law,
                // S15 step -75 from 440, reset 50).
                const std::vector<int> shellR =
                    ascend::game::shellRadiiFor(n);
                for (int i = 0; i < n; i++) {
                    const uint64_t z = cosmosHash(i, unsigned(wheelGen));
                    const auto d = previewDraws(z);
                    // S15 box draw -> normalize -> shell; the S27 pump spin
                    // is a WORLD-Y yaw of the model point BEFORE the depth
                    // band + divide (previewStar applies it; class cycles
                    // with depth, matching the measured reclass churn).
                    const double r = double(i < int(shellR.size())
                                                ? shellR[size_t(i)] : 50);
                    auto s = previewStar(d.vx, d.vy, d.vz, r, cx, cy,
                                         kNewgameCosmosRect, previewYaw);
                    if (!s.inWell) continue;  // honest well clip (S5)
                    // SEL law t200 (planets-ui §6): SEL = 4*K + cls, K = the
                    // star TYPE (13 starstat families; cos_star k(4K)..k(4K+3)
                    // = one bright-ramp per family — file census tNG-F: K0
                    // blues, K2 reds, K3 oranges, K5 tans, ...). tNG-F F1
                    // stands: types come from the wheel galaxy (the pre-fix
                    // K=0 seam painted every star blue). dims-zero cells
                    // (types 10..12, t200) blit nothing -> honest skip.
                    const int ktype =
                        wheelGal && i < int(wheelGal->stars.size())
                            ? wheelGal->stars[size_t(i)].type
                            : int((z >> 42) % 13);
                    const int rec = 4 * ktype + s.cls;
                    bool drew = false;
                    // t200 cited law: cells k40..k51 (types 10..12) are
                    // dims-zero — the vendor blit walks zero rows = draws
                    // NOTHING. Skip honestly (no fallback tint).
                    if (!(rec >= 40 && rec <= 51) && cosStarLib.count() > rec)
                        drew = blitShape(ren, cosStarLib, rec, s.sx - 1,
                                         s.sy - 1);
                    if (!drew && (rec < 40 || rec > 51)) {
                        // cos_star unavailable/empty-cell: 2x2 tint block in
                        // the SAME family law (neutralTint rows = the port
                        // palette per star type; no fake art).
                        const RGB t = neutralTint(ktype);
                        SDL_SetRenderDrawColor(ren, t.r, t.g, t.b, 255);
                        SDL_Rect q{s.sx - 1, s.sy - 1, 2, 2};
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
                // tNG-F2 PLATE LAW (D20 F2, refined cycle 2): the vendor
                // backing is the dark speckle family, NOT flat black —
                // measured census + grain in mapchrome.h speciesPlateAt.
                // (Cycle 1's flat black rect was the "painted over" look;
                // pre-fix the chrome texture showed through entirely.)
                for (int py = 8; py <= 37; py++)
                    for (int px2 = 503; px2 <= 633; px2++) {
                        const RGB c = speciesPlateAt(px2, py);
                        SDL_SetRenderDrawColor(ren, c.r, c.g, c.b, 255);
                        SDL_RenderDrawPoint(ren, px2, py);
                    }
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
                // tNG-C PLANET INDEX LAW (D19 seed #2 CLOSED): smhome.shp
                // k<selected race row> NATIVE at the window push (72,205) —
                // NEWGAMEWND X0=334 Y0=12 (windows.txt L584) plus bbox
                // (L,T)=(-24,-26) [census: every smhome record] puts the
                // content at screen (382,191), i.e. kDescPlanetCentre +
                // (L,T) with centre (406,217). 0x523b1 asserts the row <
                // 0x15 (21 race records) — the port refuses instead of
                // asserting. The t414 planets-ladder biome mapping is gone.
                if (smhomeLib.count() >= 21 && selIndex >= 0 &&
                    selIndex < 21) {
                    const auto& pr = smhomeLib.record(selIndex);
                    dimsCheck("desc-planet", int(pr.width), int(pr.height),
                              kDescPlanetCentre.x + int(pr.left),
                              kDescPlanetCentre.y + int(pr.top));
                    blitShape(ren, smhomeLib, selIndex,
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
            for (int i = 0; i < 2; i++) {  // tNG-F2: cited glyph cells (D20 F3)
                const bool up = i == 0;
                for (int y = 47 + (up ? 0 : 309); y <= 63 + (up ? 0 : 309); y++)
                    for (int x = kRaceArrowUp.x0; x <= kRaceArrowUp.x1; x++) {
                        const RGB c = arrowGlyphColourAt(up, x, y);
                        SDL_SetRenderDrawColor(ren, c.r, c.g, c.b, 255);
                        SDL_RenderDrawPoint(ren, x, y);
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
                    // tNG-B B3: per-control anchor residual (menulaw.h
                    // kWheelBlitDx/Dy, F15-1c measured) — the uniform
                    // anchor left a 1-2 px offset per panel.
                    const bool drew = blitShape(
                        ren, cfgNew, frame,
                        cxp - kWheelBlitHalfW + kWheelBlitDx[i],
                        kWheelBlitTop + kWheelBlitDy[i]);
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
                // tNG-C CHIP ROW LAW (D19 seed #4 CLOSED) [verified head
                // 0x5258d..0x52647 + 0x53ee0 decompile + F13 refcap]: the
                // vendor blits the SELECTED race's raceflag emblem SEVEN
                // times at (381+16i,433), chip i through the palette ramp
                // slots 16..19 := game.pal[16+4i..19+4i] (blitShapePalRamp;
                // witness chip-i brightest ink == pal[4i+19] EXACT i=1..6).
                // The player's own chip (i == playerColourIdx, the 0x52621
                // compare) gets the FUN_0002fe04 frame: white hlines 434/
                // 458, grey vlines 435..457 (constants in menulaw.h). The
                // t401 solid kPlayerChipRgb swatches are REMOVED (D19 "the
                // artwork is rendered incorrectly in the bottom row").
                for (int k = 0; k < kPlayerChipCount; k++) {
                    const int cx = kPlayerChipX0 + k * kPlayerChipPitch;
                    if (raceflagLib.count() > selIndex && selIndex >= 0) {
                        const auto& cr = raceflagLib.record(selIndex);
                        dimsCheck("playercolor-chiprow", int(cr.width),
                                  int(cr.height), cx + int(cr.left),
                                  kPlayerChipY + int(cr.top));
                        blitShapePalRamp(ren, raceflagLib, selIndex,
                                         cx + cr.left, kPlayerChipY + cr.top,
                                         k);
                    }
                    if (k == playerColourIdx) {
                        for (int x = cx; x < cx + kPlayerChipW; x++) {
                            SDL_SetRenderDrawColor(ren, 255, 255, 255, 255);
                            SDL_RenderDrawPoint(ren, x, kChipFrameTop);
                            SDL_RenderDrawPoint(ren, x, kChipFrameBottom);
                        }
                        for (int y = kChipFrameTop + 1; y < kChipFrameBottom;
                             y++) {
                            SDL_SetRenderDrawColor(
                                ren, kChipFrameLeftGrey.r,
                                kChipFrameLeftGrey.g, kChipFrameLeftGrey.b,
                                255);
                            SDL_RenderDrawPoint(ren, cx, y);
                            SDL_SetRenderDrawColor(
                                ren, kChipFrameRightGrey.r,
                                kChipFrameRightGrey.g, kChipFrameRightGrey.b,
                                255);
                            SDL_RenderDrawPoint(ren, cx + kPlayerChipW - 1, y);
                        }
                    }
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
                // (c) tNG-C3 BEGIN STARFIELD (D19 seed #3; cited law body
                // 0x526f0..0x5282f, F15-3): EVERY galaxy star (count law
                // word[obj+0x572]) shrunk into the panel: x = mx/5 + 5,
                // y = my/5 + 5 with (mx,my) the map pixel coords (hiword
                // law — our 1024-grid scaled 640/480 per 1024), panel
                // origin (502,381), clipped to kBeginPanelVisual. Sprite =
                // cos_star record 4*K + cls (K=0 named seam, same as the
                // map screen); FOUR-WAY class law (0x52817..0x5282d):
                // v>220 -> 0, 0<v<=220 -> 1, -220<v<=0 -> 2, v<=-220 -> 3
                // with v the rotated depth term (plane rotation of the
                // shell vector by preview yaw — [inferred] formula, class
                // ORDER is cited). Positions are STATIC (the rotation
                // drives only the class). Drawn BEFORE the ring/portrait
                // (refcap: no star px over the emblem disc) and after the
                // dots. tNG-B B1: the star SET is the WHEEL galaxy (the
                // density click regenerates it — word[obj+0x572] is that
                // galaxy's count), falling back to the built campaign only
                // when no wheel galaxy could be built (honest zero).
                const std::vector<ascend::game::Star>* beginStars = nullptr;
                if (wheelGal)
                    beginStars = &wheelGal->stars;
                else if (previewCamp)
                    beginStars = &previewCamp->galaxy().stars;
                if (beginStars) {
                    // tNG-F F4 CONTAINMENT LAW (D20 "taking up too much of
                    // the frame and not spherical"; refcap census
                    // scripts/tNGF_begin_probe.py): the vendor stars occupy a
                    // CLUSTER bbox x510..568 y389..448 (59x60) centred
                    // (538.1,417.4) r99=31 — NOT the full panel rect. The
                    // /5+5 law stands (cited 0x527b1/0x527c9); the vendor
                    // new-game galaxy is CLUSTERED in map space (source of
                    // that clustering = named seam), so the port fits the
                    // field into the measured circle: offset from the panel
                    // centre scaled to the cluster radius, then hard-clipped
                    // to the circle. Dots stay panel-wide (measured: 778/799
                    // dot px are OUTSIDE the star circle — dots and stars are
                    // different families).
                    SDL_Rect clip{vis.x0, vis.y0, vis.x1 - vis.x0 + 1,
                                  vis.y1 - vis.y0 + 1};
                    SDL_RenderSetClipRect(ren, &clip);
                    // S27: the class-cycling term is the SAME pump as the
                    // big field (measured run 010308: cluster positions
                    // static — 130/145 matched peaks at displacement 0.0 —
                    // while ~700 px/step churn brightness: the vendor
                    // rotation drives ONLY the class). kPreviewSpinDegPerTick
                    // replaces the per-frame kPreviewSpinPerFrame fudge.
                    const double beginYaw =
                        -newgameSpinDeg * 3.14159265358979323846 / 180.0;
                        // S28-X3: same negation law as previewYaw (camera
                        // basis spins +2/fire => apparent class drift -2/fire).
                    const double kClCx = 538.1, kClCy = 417.4, kClR = 32.0;
                    const double kPcX = (vis.x0 + vis.x1) / 2.0,
                                 kPcY = (vis.y0 + vis.y1) / 2.0;
                    const double kFit = kClR / 66.0;  // /5+5 half-extent 66
                    for (const ascend::game::Star& s : *beginStars) {
                        const int px0 = vis.x0 + (s.x * 640 / 1024) / 5 + 5;
                        const int py0 = vis.y0 + (s.y * 480 / 1024) / 5 + 5;
                        const int px =
                            int(kClCx + (px0 - kPcX) * kFit + 0.5);
                        const int py =
                            int(kClCy + (py0 - kPcY) * kFit + 0.5);
                        const double ddx = px - kClCx, ddy = py - kClCy;
                        if (ddx * ddx + ddy * ddy > kClR * kClR) continue;
                        const double rr = double(s.z);
                        const double ang =
                            std::atan2(double(s.y - 512), double(s.x - 512)) +
                            beginYaw;
                        const long v = lround(rr * std::sin(ang));
                        const int cls = v > 220 ? 0
                                      : v > 0   ? 1
                                      : v > -220 ? 2
                                                 : 3;
                        // tNG-F F4: SAME type-K colour law as the big
                        // preview (D20: vendor Begin stars are multi-
                        // colour too); dims-zero cells draw nothing.
                        const int rec = 4 * s.type + cls;
                        if (rec >= 40 && rec <= 51) continue;
                        if (cosStarLib.count() > rec) {
                            // bbox quad (-2,-2,2,2): content 5x5 at
                            // (L,T); dest = anchor + (L,T) -> centred.
                            blitShape(ren, cosStarLib, rec, px - 2, py - 2);
                        } else {
                            SDL_SetRenderDrawColor(ren, 225, 227, 229, 255);
                            SDL_Rect q{px - 1, py - 1, 2, 2};
                            SDL_RenderFillRect(ren, &q);
                        }
                    }
                    SDL_RenderSetClipRect(ren, nullptr);
                }
                // (b) emblem ring + portrait of the SELECTED species.
                // tNG-C3 THICK BEVELED RING LAW (refcap census,
                // docs/re/_wip_tNGC.md F15-3b): centre (600,417.5), OUTER
                // diam 57 (x572..628 @ y418; rows 389..393/442..446 @
                // x601), band 5 px. Measured radial rungs: top (out->in)
                // (10,46,51),(0,142,69),(0,124,61),(0,113,56),(8,82,43);
                // bottom (out->in) (0,153,74),(0,153,74),(0,142,69),
                // (0,110,54),(5,65,43). The 1-px kLore circle r28 (the D19
                // "1-px vs THICK BEVELED" defect) is REPLACED by the
                // annulus r in [23.5,29] with a top/bottom bevel blend.
                static const RGB kRingTop[5] = {{10, 46, 51}, {0, 142, 69},
                                                {0, 124, 61}, {0, 113, 56},
                                                {8, 82, 43}};
                static const RGB kRingBot[5] = {{0, 153, 74}, {0, 153, 74},
                                                {0, 142, 69}, {0, 110, 54},
                                                {5, 65, 43}};
                const double kcx = 600.0, kcy = 417.5;
                for (int ry = 388; ry <= 447; ry++)
                    for (int rx = 571; rx <= 629; rx++) {
                        const double dx = rx - kcx, dy = ry - kcy;
                        const double rr = std::sqrt(dx * dx + dy * dy);
                        if (rr < 23.5 || rr > 29.0) continue;
                        const int t =
                            std::min(4, std::max(0, int((29.0 - rr) / 1.1)));
                        const double bv = (dy + 29.0) / 58.0;  // 0 top 1 bot
                        SDL_SetRenderDrawColor(
                            ren,
                            uint8_t(kRingTop[t].r + (kRingBot[t].r - kRingTop[t].r) * bv),
                            uint8_t(kRingTop[t].g + (kRingBot[t].g - kRingTop[t].g) * bv),
                            uint8_t(kRingTop[t].b + (kRingBot[t].b - kRingTop[t].b) * bv),
                            255);
                        SDL_RenderDrawPoint(ren, rx, ry);
                    }
                // Portrait clipped to the ring HOLE (refcap: the emblem
                // fills the 47-px hole exactly, the annulus stays fully
                // visible — the raw native blit overflowed it): smrace
                // content 100x100 at (L,T)=(-50,-50), NATIVE at the ring
                // centre with blitShapeCircular clipR=23 about the rect
                // centre (vendortext.cpp clip law).
                if (const auto* pl = portraitFor(scrollOffset + selSlot)) {
                    const auto& pr0 = pl->record(0);
                    blitShapeCircular(ren, *pl, 0, 600 + int(pr0.left),
                                      417 + int(pr0.top), 1, 23);
                }
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
                        if (ci == 0) {
                            // tNG-B B1 [verified 0x52db9..0x52e57]: the
                            // density click REGENERATES the display galaxy
                            // (FUN_000226e4 full-regen, rand consumer) —
                            // the visible star set changes EVERY click.
                            densityIdx = densityRankNext(densityIdx);
                            rebuildWheelGalaxy(densityIdx, ++wheelGen);
                            // SET-IDENTITY hash (witness discriminator):
                            // hash of the first 15 star positions (15 = the
                            // min ladder rung, so always defined). MapGen
                            // at a FIXED seed is prefix-structured (same
                            // stream clipped by count), so a seed NOT
                            // riding gen yields the SAME h15 across the
                            // 15/25-rung clicks — the witness requires h15
                            // to differ EVERY click (rand-consumer law).
                            uint64_t h15 = 1469598103934665603ull;
                            if (wheelGal)
                                for (size_t si = 0;
                                     si < 15 && si < wheelGal->stars.size();
                                     si++) {
                                    h15 = (h15 ^ uint64_t(wheelGal->stars[si].x)) *
                                          1099511628211ull;
                                    h15 = (h15 ^ uint64_t(wheelGal->stars[si].y)) *
                                          1099511628211ull;
                                }
                            std::printf(
                                "ui raceconfig galaxy regen gen %d stars %d "
                                "h15 %016llx\n",
                                wheelGen,
                                wheelGal ? int(wheelGal->stars.size()) : -1,
                                (unsigned long long)h15);
                            std::fflush(stdout);
                        } else if (ci == 1) {
                            // tNG-B B2 SPECIES CLICK LAW [verified
                            // 0x52e58..0x52ecc]: word[+0xb9]++ with wrap
                            // 8->3, then FUN_00022ce4 = RACE ASSIGNMENT:
                            // word[state+0xd88]=N, star owner/OR bytes and
                            // home worlds re-rolled, species ids re-drawn
                            // distinct, colours re-derived (its tail calls
                            // FUN_000232ec). STAR POSITIONS ARE PRESERVED —
                            // the opposite of the density arm's full regen.
                            // Port model: roster count + colours re-derive;
                            // wheelGal UNCHANGED (the h15 law line below is
                            // the invariant witness term).
                            speciesSetting = speciesRankNext(speciesSetting);
                            colourLcg = 0x12e10u;  // seam: per-click reseed
                            assignRaceColours(playerColourIdx, speciesSetting,
                                              &colourLcg, raceColours);
                            uint64_t rh = 1469598103934665603ull;
                            if (wheelGal)
                                for (size_t si = 0;
                                     si < 15 && si < wheelGal->stars.size();
                                     si++) {
                                    rh = (rh ^ uint64_t(wheelGal->stars[si].x)) *
                                         1099511628211ull;
                                    rh = (rh ^ uint64_t(wheelGal->stars[si].y)) *
                                         1099511628211ull;
                                }
                            std::printf(
                                "ui raceconfig roster n %d wheelgen %d h15 "
                                "%016llx\n",
                                speciesSetting, wheelGen,
                                (unsigned long long)rh);
                            std::fflush(stdout);
                        } else {
                            // tNG-B B4 ATMOSPHERE CLICK LAW [verified
                            // 0x52eec..0x52f01]: word[+0xbb]++ wrap 3 (own
                            // word via the straddle dword). NO state-fn call
                            // — the value reaches play state ONLY via the
                            // Begin press (0x52b3c/0x52b44 -> byte[0x13bc4],
                            // the dip-on-attack subtrahend key).
                            atmosphere = atmosphereRankNext(atmosphere);
                            std::printf("ui raceconfig atmos wheel %d\n",
                                        atmosphere);
                            std::fflush(stdout);
                        }
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
                        // tNG-B B4 SETTINGS-APPLY LAW [verified begin block
                        // 0x52a44..0x52b75]: Begin passes ebx=0 to worldgen
                        // (0x52a65) — density/species are NOT re-applied
                        // here because the click arms ALREADY wrote the play
                        // state base 0x12e10 (state-identity law, 0x52dfe/
                        // 0x52e8d eax operand). The vendor Begin delta:
                        // world layer (0x238e8 planets over the CURRENT
                        // starfield) + byte[win+0xbb] -> byte[0x13bc4]
                        // (0x52b3c/0x52b44, sole wheel writer). Port: the
                        // out-param is the handoff contract the campaign
                        // builder consumes (main.cpp rebuilds play from the
                        // wheel triple — closes the t393 named seam).
                        if (newGameOut) {
                            *newGameOut = newGameSettings(densityIdx,
                                                          speciesSetting,
                                                          atmosphere);
                            std::printf("ui newgame apply stars %d owners %d "
                                        "gov %d\n",
                                        newGameOut->stars, newGameOut->owners,
                                        newGameOut->gov);
                        }
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
