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
// t400: the button fills moved to boot.h titleButtonFill(hovered) — the
// vendor's hovered fill (0,28,36) vs (0,0,8) is MEASURED law there.
// t393 New Game screen colours [measured on the user-supplied original;
// capture is JPEG-lossy so greys land on the canonical (97,97,97)/(12,32,48)
// values the census converges to]. CVD rule: meaning is never carried by
// hue alone here (selection = luminance band, labels carry the words).
const SDL_Color kPanel{12, 32, 48, 255};      // navy panel interior
const SDL_Color kBevel{97, 97, 97, 255};      // grey bevel lines
const SDL_Color kLore{0, 142, 69, 255};       // vendor green ink
const SDL_Color kSelBg{28, 56, 74, 255};      // selection band (lighter navy)
const SDL_Color kDisc{128, 128, 128, 255};    // portrait-seam disc + ring
const SDL_Color kArrowFill{26, 87, 146, 255};   // arrow square fill (measured)
const SDL_Color kArrowInk{190, 255, 255, 255};  // arrow glyph (measured)

// t393 map-preview primitives: IDENTICAL to ui.cpp's anonymous-namespace
// pair (internal linkage each; the preview must project stars with the same
// CosmosView-default law or the backdrop would drift from play). If either
// changes, change both (pinned: preview uses starScreenPos law test).
inline SDL_Color toSdl(RGB c) { return {c.r, c.g, c.b, 255}; }
const SDL_Color kLane{120, 120, 120, 255};
void filledCircle(SDL_Renderer* r, int cx, int cy, int rad) {
    for (int dy = -rad; dy <= rad; ++dy)
        for (int dx = -rad; dx <= rad; ++dx)
            if (dx * dx + dy * dy <= rad * rad)
                SDL_RenderDrawPoint(r, cx + dx, cy + dy);
}

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

            // (1) BACKDROP = live map preview (COSMOSWnd is STATE "4 1 3 7 13"
            // — registered in state 3; the original shows the generated map
            // behind the panels). Same projection law as the campaign loop.
            if (previewCamp) {
                const ascend::game::Galaxy& g = previewCamp->galaxy();
                CosmosView view;  // mapSize default == MapConfig default
                SDL_SetRenderDrawColor(ren, kLane.r, kLane.g, kLane.b, 255);
                for (const auto& ln : g.lanes) {
                    Pt a = starScreenPos(view, g.stars[ln.a]);
                    Pt b2 = starScreenPos(view, g.stars[ln.b]);
                    SDL_RenderDrawLine(ren, a.x, a.y, b2.x, b2.y);
                }
                for (const auto& s : g.stars) {
                    Pt q = starScreenPos(view, s);
                    SDL_Color n = toSdl(kNeutralRgb);
                    SDL_SetRenderDrawColor(ren, n.r, n.g, n.b, 255);
                    filledCircle(ren, q.x, q.y, 2);
                }
            }

            // (2) Summary block: static.txt //168 template, white, centred
            // under the starfield (measured rows 327/340/353, pitch 13).
            std::vector<std::string> summary;
            newgameSummary(kDensityStarCounts[densityIdx], speciesSetting,
                           atmosphere, &summary);
            for (size_t i = 0; i < summary.size(); i++) {
                const int w = txt.width(summary[i], false);
                txt.draw(ren, kSummaryCentreX - w / 2,
                         kSummaryTop + int(i) * kSummaryPitch, summary[i],
                         false, kInk);
            }

            // (3) NEWGAMEWND panel: interior measured BLACK + grey bevel
            // (97,97,97). The k0 wheel face (84x79) is the config WHEEL art
            // for the bottom-row controls (SHAPEITEM records), not this
            // panel's backdrop — t387 drew it here on a wrong reading; the
            // panel carries name + lore text instead (original S9).
            SDL_Rect wf{kNewgameWnd.x0, kNewgameWnd.y0,
                        kNewgameWnd.x1 - kNewgameWnd.x0 + 1,
                        kNewgameWnd.y1 - kNewgameWnd.y0 + 1};
            SDL_SetRenderDrawColor(ren, kBevel.r, kBevel.g, kBevel.b, 255);
            SDL_RenderDrawRect(ren, &wf);

            // (4) Species name (green, rows 18..27, centred on the panel) +
            // "Player Species" header (white, rows 16..25, centred RACELIST).
            const int selIndex = scrollOffset + selSlot;
            const std::string selName = speciesNameAt(selIndex);
            {
                const int w = txt.width(selName, false);
                txt.draw(ren, (kNewgameWnd.x0 + kNewgameWnd.x1 + 1) / 2 - w / 2,
                         kNameTop, selName, false, kLore);
            }
            {
                const std::string hdr = "Player Species";  // static.txt //153
                const int w = txt.width(hdr, false);
                txt.draw(ren, (kRaceList.x0 + kRaceList.x1 + 1) / 2 - w / 2,
                         kHeaderTop, hdr, false, kInk);
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
                        const int w = txt.width(lines[i], false);
                        txt.draw(ren,
                                 (kLoreBox.x0 + kLoreBox.x1 + 1) / 2 - w / 2,
                                 kLoreBox.y0 + int(i) * kLoreLinePitch,
                                 lines[i], false, kLore);
                    }
                }
            }

            // (6) RACELIST: navy interior + bevel + THREE portrait slots
            // (measured S: bands 49-153/157-262/266-372, pitch 108) + scroll
            // arrow squares. PORTRAITS ARE A NAMED SEAM (t391: the 7racesel
            // strips stay unblitted without a stronger witness) — a grey
            // disc + the species NAME stands in, and says so in the docs.
            SDL_Rect rl{kRaceList.x0, kRaceList.y0,
                        kRaceList.x1 - kRaceList.x0 + 1,
                        kRaceList.y1 - kRaceList.y0 + 1};
            SDL_SetRenderDrawColor(ren, kPanel.r, kPanel.g, kPanel.b, 255);
            SDL_RenderFillRect(ren, &rl);
            SDL_SetRenderDrawColor(ren, kBevel.r, kBevel.g, kBevel.b, 255);
            SDL_RenderDrawRect(ren, &rl);
            for (int i = 0; i < kRaceSlotCount; i++) {
                const int specnum = scrollOffset + i;
                const int cy = kRaceSlotTop + i * kRaceSlotPitch +
                               kRaceSlotH / 2;
                const int cx = (kRaceList.x0 + kRaceList.x1) / 2;
                if (i == selSlot) {  // selection: luminance change, not hue
                    SDL_SetRenderDrawColor(ren, kSelBg.r, kSelBg.g, kSelBg.b,
                                           255);
                    SDL_Rect band{kRaceList.x0 + 1, cy - kRaceSlotH / 2,
                                  kRaceList.x1 - kRaceList.x0 - 1, kRaceSlotH};
                    SDL_RenderFillRect(ren, &band);
                }
                if (specnum < rosterCount()) {
                    SDL_SetRenderDrawColor(ren, kDisc.r, kDisc.g, kDisc.b, 255);
                    filledCircle(ren, cx, cy, kRaceSlotH / 2 - 2);
                    SDL_SetRenderDrawColor(ren, kBevel.r, kBevel.g, kBevel.b,
                                           255);
                    for (int a = 0; a < 360; a += 2) {  // ring (seam stand-in)
                        const double rad = a * 3.14159265 / 180.0;
                        SDL_RenderDrawPoint(
                            ren, cx + int((kRaceSlotH / 2 - 1) * cos(rad)),
                            cy + int((kRaceSlotH / 2 - 1) * sin(rad)));
                    }
                    const std::string nm = speciesNameAt(specnum);
                    const int w = txt.width(nm, false);
                    txt.draw(ren, cx - w / 2, cy - 4, nm, false, kInk);
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
            // (measured rows 393..403) + value word + k0 wheel face inside.
            for (int i = 0; i < kNewgameControlCount; i++) {
                const NewgameControl& c = kNewgameControls[i];
                SDL_Rect r{c.rect.x0, c.rect.y0, c.rect.x1 - c.rect.x0 + 1,
                           c.rect.y1 - c.rect.y0 + 1};
                SDL_SetRenderDrawColor(ren, kPanel.r, kPanel.g, kPanel.b, 255);
                SDL_RenderFillRect(ren, &r);
                SDL_SetRenderDrawColor(ren, kBevel.r, kBevel.g, kBevel.b, 255);
                SDL_RenderDrawRect(ren, &r);
                const int cxp = (c.rect.x0 + c.rect.x1) / 2;
                const int wl = txt.width(c.label, false);
                txt.draw(ren, cxp - wl / 2, c.rect.y0 + 12, c.label, false,
                         kInk);
                if (cfgNew.count() > 0)
                    blitShape(ren, cfgNew, 0,
                              cxp - int(cfgNew.record(0).width) / 2,
                              c.rect.y0 + 26);  // wheel face (SHAPEITEM cited)
                const char* vw = i == 0
                                     ? kDensityWords[densityIdx]
                                     : (i == 1 ? speciesCountWord(speciesSetting)
                                               : atmosphereWord(atmosphere));
                if (vw) {
                    const int wv = txt.width(vw, false);
                    txt.draw(ren, cxp - wv / 2, c.rect.y0 + 58, vw, false,
                             kInk);
                }
            }
            // Player^Color (windows.txt L653, MSG 0 = inert): label + six
            // owner-colour chips (the original shows six icons; WHICH six is
            // a named seam — kOwnerRgb is our CVD-safe set, cited as such).
            {
                const Rect c = kPlayerColorRect;
                SDL_Rect r{c.x0, c.y0, c.x1 - c.x0 + 1, c.y1 - c.y0 + 1};
                SDL_SetRenderDrawColor(ren, kPanel.r, kPanel.g, kPanel.b, 255);
                SDL_RenderFillRect(ren, &r);
                SDL_SetRenderDrawColor(ren, kBevel.r, kBevel.g, kBevel.b, 255);
                SDL_RenderDrawRect(ren, &r);
                const std::string lbl = "Player Color";  // NAME 'Player^Color'
                const int cxp = (c.x0 + c.x1) / 2;
                const int wl = txt.width(lbl, false);
                txt.draw(ren, cxp - wl / 2, c.y0 + 12, lbl, false, kInk);
                for (int k = 0; k < 6; k++) {
                    SDL_Color col = toSdl(kOwnerRgb[k]);
                    SDL_SetRenderDrawColor(ren, col.r, col.g, col.b, 255);
                    SDL_Rect chip{cxp - 45 + k * 16, c.y0 + 28, 12, 12};
                    SDL_RenderFillRect(ren, &chip);
                }
            }
            // Begin New Game (measured rect; NOT windows.txt — STARTGAME is
            // STATE "1 12"). White label rows measured ~456; thumbnail seam.
            {
                SDL_Rect r{kBeginNewGameBtn.x0, kBeginNewGameBtn.y0,
                           kBeginNewGameBtn.x1 - kBeginNewGameBtn.x0 + 1,
                           kBeginNewGameBtn.y1 - kBeginNewGameBtn.y0 + 1};
                SDL_SetRenderDrawColor(ren, kPanel.r, kPanel.g, kPanel.b, 255);
                SDL_RenderFillRect(ren, &r);
                SDL_SetRenderDrawColor(ren, kBevel.r, kBevel.g, kBevel.b, 255);
                SDL_RenderDrawRect(ren, &r);
                const std::string lbl = "Begin New Game";  // static.txt //169
                const int w = txt.width(lbl, false);
                txt.draw(ren,
                         (r.x + (r.w - w) / 2), kBeginLabelTop, lbl, false,
                         kInk);
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
                    if (inRect(kPlayerColorRect, p)) {
                        std::printf("ui raceconfig click Player^Color msg 0\n");
                        std::fflush(stdout);
                        continue;  // MSG 0 = inert zone (windows.txt L664)
                    }
                    if (inRect(kBeginNewGameBtn, p)) {
                        std::printf(
                            "ui raceconfig begin density %d species %d "
                            "atmosphere %d species-pick %d\n",
                            kDensityStarCounts[densityIdx], speciesSetting,
                            atmosphere, scrollOffset + selSlot);
                        std::fflush(stdout);
                        st = BootState::Campaign;
                        continue;
                    }
                    continue;  // dead zone on the full screen
                }
                const int idx = titleButtonAt(p);
                const BootState next = bootClick(st, p);
                if (next == st) continue;  // click outside any live button
                // t395 BUTTON SFX (D10): click08 on every title-menu button
                // press. DOCUMENTED PORT CHOICE, not vendor law — the
                // windows.txt SOUNDCHANNEL census {0 x118, -0 x1} carries no
                // sound id (audio.md §6.5, t395 re-census), so which sample
                // the vendor played per button class is uncited. Symmetric
                // with the campaign map's click08 (ui.cpp).
                if (audio) audio->play("click08");
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
