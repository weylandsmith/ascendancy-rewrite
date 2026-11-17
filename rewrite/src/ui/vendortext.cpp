// SPDX-License-Identifier: GPL-3.0-or-later
// VendorText implementation — moved verbatim out of ui.cpp (t385) so the
// title-screen loop (title.cpp) and the campaign loop share ONE renderer.
// Laws + citations live in ui_internal.h / docs/re/fnt.md.
#include "ui/ui_internal.h"

#include <algorithm>
#include <cstdio>
#include <fstream>
#include <iterator>

#include "ui/mapchrome.h"  // t415: textureColourAt (the chrome page law)
#include "ui/raceintro.h"

namespace ascend::ui {

bool VendorText::buildFace(SDL_Renderer* r, const ascend::formats::Font& f,
                           Face* out, std::string* err) {
    out->h = f.height();
    int total = 1;
    for (int i = 0; i < ascend::formats::Font::kGlyphCount; i++) {
        out->gx[i] = total;
        out->gw[i] = int(f.glyph(i).width);
        total += out->gw[i] + 1;  // 1px gutter, NEAREST sampling anyway
    }
    std::vector<uint32_t> px(size_t(total) * out->h, 0x00000000u);
    for (int i = 0; i < ascend::formats::Font::kGlyphCount; i++) {
        const auto& g = f.glyph(i);
        for (int y = 0; y < out->h; y++)
            for (uint32_t x = 0; x < g.width; x++)
                if (g.px[size_t(y) * g.width + x] != 0xFF)  // 0xFF = bg [fnt.md]
                    px[size_t(y) * total + out->gx[i] + x] = 0xFFFFFFFFu;
    }
    out->tex = SDL_CreateTexture(r, SDL_PIXELFORMAT_ARGB8888,
                                 SDL_TEXTUREACCESS_STATIC, total, out->h);
    if (!out->tex) {
        *err = std::string("atlas: ") + SDL_GetError();
        return false;
    }
    SDL_SetTextureBlendMode(out->tex, SDL_BLENDMODE_BLEND);
    SDL_UpdateTexture(out->tex, nullptr, px.data(), total * int(sizeof(uint32_t)));
    return true;
}

bool VendorText::load(SDL_Renderer* r, const std::string& root, std::string* err) {
    const std::string smPath = root + "/extracted/ascend01/data/smfont.fnt";
    const std::string bigPath = root + "/extracted/ascend01/data/bigfont.fnt";
    if (!sm.load(smPath, err)) return false;
    if (!big.load(bigPath, err)) return false;
    if (!buildFace(r, sm, &smFace, err)) return false;
    if (!buildFace(r, big, &bigFace, err)) return false;
    return true;
}

void VendorText::draw(SDL_Renderer* r, int x, int y, const std::string& s,
                      bool large, SDL_Color c) {
    if (s.empty()) return;
    Face& fa = large ? bigFace : smFace;
    SDL_SetTextureColorMod(fa.tex, c.r, c.g, c.b);
    for (unsigned char ch : s) {
        // Vendor fonts define codes 0..127 only (docs/re/fnt.md). CP437
        // high bytes in event text render as a space-width gap, not UB.
        const int gw = ch < ascend::formats::Font::kGlyphCount
                           ? fa.gw[ch]
                           : fa.gw[' '];
        if (gw > 0 && ch < ascend::formats::Font::kGlyphCount) {
            // Whole-glyph clipping at the display edge: a half-drawn
            // glyph reads as corruption; a missing one reads as wrap.
            if (x + gw > kDisplayW) break;
            SDL_Rect src{fa.gx[ch], 0, gw, fa.h};
            SDL_Rect dst{x, y, gw, fa.h};
            SDL_RenderCopy(r, fa.tex, &src, &dst);
        }
        x += gw;  // advance == width [verified, fnt.md]
    }
}

int VendorText::width(const std::string& s, bool large) const {
    const Face& fa = large ? bigFace : smFace;
    int w = 0;
    for (unsigned char ch : s)
        w += ch < ascend::formats::Font::kGlyphCount ? fa.gw[ch] : fa.gw[' '];
    return w;
}

void VendorText::release() {
    if (smFace.tex) SDL_DestroyTexture(smFace.tex), smFace.tex = nullptr;
    if (bigFace.tex) SDL_DestroyTexture(bigFace.tex), bigFace.tex = nullptr;
}

// ---- t388 shared chrome helpers (declared in ui_internal.h) ---------------
// Moved verbatim out of title.cpp's anonymous namespace so the campaign loop
// (ui.cpp) can draw vendor chrome with the SAME semantics as the title loop.
//
// blitShape: decode a .shp record's palette-index plane and upload it as an
// ARGB texture, honouring the vendor's untouched-destination semantics
// (formats/shp.h: skipped/clamped pixels keep the destination). Mask law:
// decode twice into two differently-prefilled buffers and diff — a pixel that
// decodes identically from both prefills was WRITTEN; one that differs was
// skipped, so it gets alpha 0 and the backdrop shows through. Mechanical, no
// guessed transparent index value.
//
// PALETTE [t398 CLOSED]: chrome indices render through DATA\game.pal — the
// exe loads it by name (payload 0x83579/0x84207) and every pixel of the
// pinned in-game refcap shots lies inside it under the DOSBox 6->8-bit
// conversion, while the title screen sits at 8.79% (different palette, the
// t386 TSV). 1starmap k3/k4/k5 register at the cited kRail rects through it
// (mean |RGB diff| 3..6/765). formats/gamepal.h carries the law. If the file
// is unavailable the ramp remains, with a one-time printed degradation line
// (silent-degrade law: never abort the frame loop over a palette).
static ascend::formats::GamePalette g_chromePal;

bool loadChromePalette(const std::string& dataRoot) {
    // Once per process: the title loop and the campaign loop both call this;
    // the data root never changes mid-session, and the diagnostic line prints
    // exactly once either way.
    static bool attempted = false;
    if (attempted) return g_chromePal.ready();
    attempted = true;
    std::string err;
    if (g_chromePal.load(dataRoot + "/extracted/ascend01/data/game.pal",
                         &err)) {
        std::printf("ui palette: game.pal (256 entries, 6->8 bit)\n");
        return true;
    }
    std::printf("ui palette: %s (degraded: greyscale ramp)\n", err.c_str());
    return false;
}

uint32_t chromePaletteArgb(int index) {
    if (!g_chromePal.ready()) return 0xFF808080u;
    return g_chromePal.argb(index & 0xff);
}

bool blitShape(SDL_Renderer* ren, const ascend::formats::ShapeLibrary& lib,
               int rec, int x, int y) {
    return blitShapeScaled(ren, lib, rec, x, y, 1);
}

// t414: blitShape at scale WITH an optional circular clip (clipR > 0
// discards scaled pixels outside radius clipR about the rect centre; 0 =
// no clip). Definition below; header law in ui_internal.h.
bool blitShapeCircular(SDL_Renderer* ren,
                       const ascend::formats::ShapeLibrary& lib, int rec,
                       int x, int y, int scale, int clipR);

bool blitShapeScaled(SDL_Renderer* ren,
                     const ascend::formats::ShapeLibrary& lib, int rec,
                     int x, int y, int scale) {
    return blitShapeCircular(ren, lib, rec, x, y, scale, 0);
}

// t414: the vendor's race-list portraits are CIRCULAR ART clipped to the
// ring (measured on the user original — 2x crop native-vision read: disc +
// ring, no square corners; docs/re/_wip_t414.md S2e). clipR > 0 discards
// every source pixel whose scaled centre falls outside a circle of that
// radius about the scaled rect's centre (alpha 0 -> BLEND skips it, the
// same skip-dst-untouched semantics as a TRANSPARENT-SKIP stream pixel).
bool blitShapeCircular(SDL_Renderer* ren,
                       const ascend::formats::ShapeLibrary& lib, int rec,
                       int x, int y, int scale, int clipR) {
    if (scale < 1) scale = 1;  // refuse-not-clamp applies to the FRAME,
                               // never to the draw scale (a 0-scale blit
                               // would be an invisible no-op at best)
    std::vector<uint8_t> a, b;
    if (!lib.decode(rec, a) || a.empty()) return false;
    b = a;
    std::fill(b.begin(), b.end(), uint8_t(0x55));
    std::fill(a.begin(), a.end(), uint8_t(0xAA));
    if (!lib.decode(rec, a) || !lib.decode(rec, b)) return false;
    const auto& r = lib.record(rec);
    std::vector<uint32_t> argb(a.size());
    // t414 circular clip: source pixel (sx,sy) centre in scaled destination
    // coords is (sx+0.5)*scale from the rect left; clip about the rect
    // centre (W*scale/2, H*scale/2).
    const double halfW = double(r.width) * scale / 2.0;
    const double halfH = double(r.height) * scale / 2.0;
    const long clipR2 = long(clipR) * long(clipR);
    for (size_t k = 0; k < a.size(); k++) {
        const uint8_t idx = a[k];
        uint32_t rgb;
        if (g_chromePal.ready()) {
            rgb = g_chromePal.argb(idx) & 0x00FFFFFFu;
        } else {
            const uint32_t lum = 40u + (uint32_t(idx) * 185u) / 255u;
            rgb = (lum << 16) | (lum << 8) | lum;
        }
        uint32_t alpha = a[k] == b[k] ? 0xFF000000u : 0x00000000u;
        if (clipR > 0 && alpha != 0) {
            const double dx = (double(k % r.width) + 0.5) * scale - halfW;
            const double dy = (double(k / r.width) + 0.5) * scale - halfH;
            if (dx * dx + dy * dy > double(clipR2)) alpha = 0x00000000u;
        }
        argb[k] = alpha | rgb;
    }
    SDL_Texture* tex = SDL_CreateTexture(ren, SDL_PIXELFORMAT_ARGB8888,
                                         SDL_TEXTUREACCESS_STATIC,
                                         int(r.width), int(r.height));
    if (!tex) return false;
    // t411 TRANSPARENCY LAW [measured]: SDL_CreateTexture defaults the
    // blend mode to NONE, which IGNORES the alpha byte — every .shp
    // TRANSPARENT-SKIP pixel (never written by walkRows, so it keeps the
    // 0xAA first-decode stuffer -> game.pal[170] (146,178,134) pale sage)
    // painted OPAQUE. Measured: 3340 px of exactly (146,178,134) across our
    // map screen's chrome zones (docs/re/_wip_t411.md F2) — the washed-out
    // digit faces / dial faces / rail bands defect. BLEND makes alpha 0
    // mean skip, matching the vendor blit (skip = dst untouched).
    SDL_SetTextureBlendMode(tex, SDL_BLENDMODE_BLEND);
    SDL_UpdateTexture(tex, nullptr, argb.data(),
                      int(r.width) * int(sizeof(uint32_t)));
    SDL_Rect dst{x, y, int(r.width) * scale, int(r.height) * scale};
    SDL_RenderCopy(ren, tex, nullptr, &dst);  // SDL default scale mode is
                                              // NEAREST (integer upscale)
    SDL_DestroyTexture(tex);
    return true;
}

// The load screen (t387 windows, t388-reusable). Windows law: LOADSCREEN
// title strip (7,7)-(632,37) + LOADLIST interior (7,46)-(632,472) over the
// 4loadgam.shp k0 backdrop (single 639x479 record; [inferred] backdrop role
// — no TYPE 100 block names it, the engine opens it by name like
// 0opening.gif). Rows come from listSaveSlots (supply-your-own dir ONLY) via
// the loadRowAt pitch law.
int runLoadScreen(SDL_Renderer* ren, VendorText& txt,
                  const std::string& dataRoot,
                  const std::vector<SaveSlot>& slots) {
    const SDL_Color kChromeBg{10, 12, 26, 255};
    const SDL_Color kInk{235, 235, 235, 255};
    const SDL_Color kBand{150, 130, 110, 255};
    const SDL_Color kSelInk{255, 244, 160, 255};
    ascend::formats::ShapeLibrary bg;
    std::string serr;
    const bool haveBg =
        bg.load(dataRoot + "/extracted/ascend01/data/4loadgam.shp", &serr);
    std::printf("ui load open slots=%zu backdrop=%s\n", slots.size(),
                haveBg ? "4loadgam.shp k0" : serr.c_str());
    std::fflush(stdout);

    int hover = -1;
    for (;;) {
        SDL_SetRenderDrawColor(ren, kChromeBg.r, kChromeBg.g, kChromeBg.b, 255);
        SDL_RenderClear(ren);
        if (haveBg) blitShape(ren, bg, 0, 0, 0);
        // LOADSCREEN strip frame + caption.
        SDL_Rect strip{kLoadScreen.x0, kLoadScreen.y0,
                       kLoadScreen.x1 - kLoadScreen.x0 + 1,
                       kLoadScreen.y1 - kLoadScreen.y0 + 1};
        SDL_SetRenderDrawColor(ren, kBand.r, kBand.g, kBand.b, 255);
        SDL_RenderDrawRect(ren, &strip);
        txt.draw(ren, strip.x + 8, strip.y + 8, "Load Game", true, kInk);
        if (slots.empty()) {
            txt.draw(ren, kLoadList.x0 + 8, kLoadList.y0 + 8,
                     "No save slots: supply a saves dir (--saves DIR)", false,
                     kInk);
        }
        for (size_t i = 0; i < slots.size(); i++) {
            const int ry = kLoadList.y0 + int(i) * kLoadRowPitch;
            if (ry + kLoadRowH > kLoadList.y1) break;  // list clipped by frame
            const SaveSlot& s = slots[i];
            const std::string line =
                s.name + (s.torn ? "  (torn)" : "  day " + std::to_string(s.day));
            if (int(i) == hover) {
                SDL_Rect hl{kLoadList.x0, ry,
                            kLoadList.x1 - kLoadList.x0 + 1, kLoadRowH};
                SDL_SetRenderDrawColor(ren, 40, 44, 66, 255);
                SDL_RenderFillRect(ren, &hl);
            }
            txt.draw(ren, kLoadList.x0 + 8, ry + 4, line, false,
                     int(i) == hover ? kSelInk : kInk);
        }
        SDL_RenderPresent(ren);

        SDL_Event e;
        if (!SDL_WaitEvent(&e)) continue;
        if (e.type == SDL_QUIT) return kLoadQuit;
        if (e.type == SDL_KEYDOWN && e.key.keysym.sym == SDLK_ESCAPE) {
            std::printf("ui load cancel\n");
            std::fflush(stdout);
            return kLoadCancel;
        }
        if (e.type == SDL_MOUSEMOTION) {
            hover = loadRowAt(Pt{e.motion.x, e.motion.y}, int(slots.size()));
            continue;
        }
        if (e.type == SDL_MOUSEBUTTONDOWN && e.button.button == SDL_BUTTON_LEFT) {
            const int idx = loadRowAt(Pt{e.button.x, e.button.y},
                                       int(slots.size()));
            if (idx < 0) continue;  // click in a gutter / outside: no-op
            std::string why;
            if (!loadPickAccepts(slots, idx, &why)) {
                std::printf("ui load refuse %s (%s)\n",
                            slots[size_t(idx)].name.c_str(), why.c_str());
                std::fflush(stdout);
                continue;  // refusal is not a cancel and never a clamp
            }
            std::printf("ui load pick %s day %u\n", slots[size_t(idx)].name.c_str(),
                        slots[size_t(idx)].day);
            std::fflush(stdout);
            return idx;
        }
    }
}

// ---- t412/t415 race intro (docs/re/raceintro.h; law _wip_t412.md F3-F5
// + _wip_t415.md F1-F5) ------------------------------------------------------
// The vendor loads history.txt at scenario start (FUN_0002b48a) and draws
// the player species' block in THREE wells (decompile rects + screenshot
// census agree): header (7,7)-(632,37) emblem+name, right well
// (312,46)-(632,245) INTRO block white, body (7,261)-(632,465) TEXT(+gate)
// in race ink; the portrait lgrace k0 sits at (7,46) native. LGRACE is
// preloaded per race at boot (FUN_00023388: SMRACE/LGRACE/SMSHIP/DKSHIP
// registered per race byte, stride 0x1ee).
static void introWellLines(const std::vector<std::string>& paras,
                           int wrapPx, int charW,
                           std::vector<std::string>* out) {
    for (const auto& para : paras)
        for (auto& l : wrapIntroLine(para, wrapPx, charW))
            out->push_back(std::move(l));
}

BootState runRaceIntro(SDL_Renderer* ren, VendorText& txt,
                       const std::string& dataRoot, int specnum,
                       int atmosphere, const std::string& raceName) {
    std::ifstream f(dataRoot + "/extracted/ascend00/history.txt",
                    std::ios::binary);
    std::string history;
    if (f)
        history.assign(std::istreambuf_iterator<char>(f),
                       std::istreambuf_iterator<char>());
    IntroPanel panel;
    std::string err;
    const bool ok =
        f && buildIntroPanel(history, specnum, atmosphere, &panel, &err);
    std::printf("ui raceintro specnum %d atmosphere %d %s\n", specnum,
                atmosphere, ok ? "ok" : err.c_str());
    std::fflush(stdout);

    // Ink: game.pal[racebyte*4 + 0x13] (F4). kIntroRaceBytes is the static
    // table census; chromePaletteArgb degrades to grey with no palette.
    const int raceByte =
        (specnum >= 0 && specnum < 21) ? kIntroRaceBytes[specnum] : 0;
    const uint32_t argb = chromePaletteArgb(introPalIndex(raceByte));
    const SDL_Color ink{uint8_t((argb >> 16) & 0xff),
                        uint8_t((argb >> 8) & 0xff), uint8_t(argb & 0xff),
                        255};
    // Right-well ink [measured t415 F5]: white; the Ghidra colour
    // immediate 0xf3 == 243 decodes game.pal[243] = (252,252,252).
    const uint32_t whiteArgb = chromePaletteArgb(0xf3);
    const SDL_Color whiteInk{uint8_t((whiteArgb >> 16) & 0xff),
                             uint8_t((whiteArgb >> 8) & 0xff),
                             uint8_t(whiteArgb & 0xff), 255};
    // Frame ink [measured t415 F5]: (125,182,182) ~= game.pal[62].
    const uint32_t frameArgb = chromePaletteArgb(62);
    const SDL_Color frameInk{uint8_t((frameArgb >> 16) & 0xff),
                             uint8_t((frameArgb >> 8) & 0xff),
                             uint8_t(frameArgb & 0xff), 255};

    // Art: lgrace portrait (ascend02 data; refuse-once law) + raceflag
    // emblem (ascend01; the t401 crest class).
    ascend::formats::ShapeLibrary lgrace;
    {
        char path[64];
        std::snprintf(path, sizeof(path),
                      "%s/extracted/ascend02/data/lgrace%02d.shp",
                      dataRoot.c_str(), specnum);
        std::string aerr;
        if (!lgrace.load(path, &aerr))
            std::printf("ui raceintro portrait refused: %s\n", aerr.c_str());
        std::fflush(stdout);
    }
    ascend::formats::ShapeLibrary raceflag;
    {
        std::string aerr;
        if (!raceflag.load(dataRoot + "/extracted/ascend01/data/raceflag.shp",
                           &aerr))
            std::printf("ui raceintro raceflag refused: %s\n", aerr.c_str());
        std::fflush(stdout);
    }

    // Wrap law (t415): right well kIntroRightWrap, body kIntroBodyWrap,
    // small face (pitch 13 measured; smfont h8). Honest truncation, count
    // printed once (no scroll driver — named seam).
    const int cw = txt.width("M", false);
    std::vector<std::string> rightLines, bodyLines;
    introWellLines(panel.introWell, kIntroRightWrap, cw, &rightLines);
    introWellLines(panel.textWell, kIntroBodyWrap, cw, &bodyLines);
    const int rightShown = std::min(int(rightLines.size()),
                                    kIntroRightMaxLines);
    const int bodyShown =
        std::min(int(bodyLines.size()), kIntroBodyMaxLines);
    if (int(rightLines.size()) > rightShown)
        std::printf("ui raceintro right truncated %d of %zu lines\n",
                    int(rightLines.size()) - rightShown, rightLines.size());
    if (int(bodyLines.size()) > bodyShown)
        std::printf("ui raceintro body truncated %d of %zu lines\n",
                    int(bodyLines.size()) - bodyShown, bodyLines.size());
    std::fflush(stdout);

    // Chrome page (t414 frame law): the textureColourAt noise texture as
    // ONE static texture; the vendor intro shows the speckle inside every
    // well (measured), so nothing is black-filled.
    static SDL_Texture* chromePage = nullptr;
    if (!chromePage) {
        chromePage = SDL_CreateTexture(ren, SDL_PIXELFORMAT_ARGB8888,
                                       SDL_TEXTUREACCESS_STATIC, kDisplayW,
                                       kDisplayH);
        if (chromePage) {
            std::vector<uint32_t> px(size_t(kDisplayW) * kDisplayH);
            for (int y = 0; y < kDisplayH; y++)
                for (int x = 0; x < kDisplayW; x++) {
                    const RGB c = textureColourAt(x, y);
                    px[size_t(y) * kDisplayW + x] =
                        0xFF000000u | (uint32_t(c.r) << 16) |
                        (uint32_t(c.g) << 8) | uint32_t(c.b);
                }
            SDL_UpdateTexture(chromePage, nullptr, px.data(),
                              kDisplayW * int(sizeof(uint32_t)));
        }
    }

    // Centred line helper (t415: both wells centre their lines).
    const auto drawCentred = [&](int x0, int x1, int y,
                                 const std::string& s, const SDL_Color& c) {
        if (s.empty()) return;
        const int w = txt.width(s, false);
        txt.draw(ren, x0 + ((x1 - x0) - w) / 2, y, s, false, c);
    };

    for (;;) {
        if (chromePage)
            SDL_RenderCopy(ren, chromePage, nullptr, nullptr);
        else {
            SDL_SetRenderDrawColor(ren, 0, 0, 0, 255);
            SDL_RenderClear(ren);
        }

        // FRAME (measured bright runs): outer rect + header divider + band
        // divider + vertical separator (TOP BAND ONLY — verified present
        // at y44..60 and y232..244, absent below y250).
        SDL_SetRenderDrawColor(ren, frameInk.r, frameInk.g, frameInk.b, 255);
        for (int t = 0; t < 2; t++) {  // 2-px-thick lines
            SDL_Rect top{kIntroFrameX0, kIntroFrameY0 + t,
                         kIntroFrameX1 - kIntroFrameX0 + 1, 1};
            SDL_Rect bot{kIntroFrameX0, kIntroFrameY1 - t,
                         kIntroFrameX1 - kIntroFrameX0 + 1, 1};
            SDL_Rect lft{kIntroFrameX0 + t, kIntroFrameY0, 1,
                         kIntroFrameY1 - kIntroFrameY0 + 1};
            SDL_Rect rgt{kIntroFrameX1 - t, kIntroFrameY0, 1,
                         kIntroFrameY1 - kIntroFrameY0 + 1};
            SDL_RenderFillRect(ren, &top);
            SDL_RenderFillRect(ren, &bot);
            SDL_RenderFillRect(ren, &lft);
            SDL_RenderFillRect(ren, &rgt);
        }
        {
            SDL_Rect hdr{kIntroFrameX0, kIntroHeaderDivY,
                         kIntroFrameX1 - kIntroFrameX0 + 1, 1};
            SDL_Rect band{kIntroFrameX0, kIntroBandDivY,
                          kIntroFrameX1 - kIntroFrameX0 + 1, 1};
            SDL_Rect sep{kIntroSepX, kIntroHeaderDivY + 1, 1,
                         kIntroBandDivY - kIntroHeaderDivY - 1};
            SDL_RenderFillRect(ren, &hdr);
            SDL_RenderFillRect(ren, &band);
            SDL_RenderFillRect(ren, &sep);
        }

        if (ok) {
            // Header: emblem (raceflag native 14x24 at (9,10)) + centred
            // "<Name>: <POWER>" in race ink (measured centre 319.4 == 320;
            // the "%s: " pool prefix is verified FUN_0002b48a).
            if (specnum >= 0 && specnum < raceflag.count())
                blitShape(ren, raceflag, specnum, kIntroEmblemX,
                          kIntroEmblemY);
            if (!panel.header.empty()) {
                const std::string h =
                    raceName.empty() ? panel.header : raceName + ": " + panel.header;
                const int w = txt.width(h, false);
                txt.draw(ren, (kDisplayW - w) / 2, 17, h, false, ink);
            }
            // Portrait: lgrace k0 NATIVE at (7,46) (template match MSE 73;
            // never scaled, never clamped — it fits its well exactly).
            if (lgrace.count() > 0)
                blitShape(ren, lgrace, 0, kIntroPortraitX, kIntroPortraitY);
            // Right well: INTRO paras, white, centred, pitch 13 from one
            // pitch inside the well top (measured first row y56 = 46+13-3;
            // glyph top offset within the 13-px row ~3 px [measured]).
            for (int i = 0; i < rightShown; i++)
                drawCentred(kIntroSepX + 2, kIntroRightX1,
                            kIntroRightY + kIntroLinePitch * (i + 1) - 3,
                            rightLines[size_t(i)], whiteInk);
            // Body well: TEXT(+gated) paras, race ink, centred (measured
            // first row y271 = 261+13-3).
            for (int i = 0; i < bodyShown; i++)
                drawCentred(kIntroBodyX, kIntroBodyX1,
                            kIntroBodyY + kIntroLinePitch * (i + 1) - 3,
                            bodyLines[size_t(i)], ink);
        } else {
            txt.draw(ren, kIntroBodyX, kIntroBodyY + 13,
                     "History file unavailable - supply extracted/ascend00/"
                     "history.txt",
                     false, ink);
        }
        SDL_RenderPresent(ren);

        SDL_Event e;
        SDL_WaitEvent(&e);
        if (e.type == SDL_QUIT) return BootState::Quit;
        if (e.type == SDL_KEYDOWN ||
            (e.type == SDL_MOUSEBUTTONDOWN &&
             e.button.button == SDL_BUTTON_LEFT)) {
            std::printf("ui raceintro dismiss -> campaign\n");
            std::fflush(stdout);
            return BootState::Campaign;
        }
    }
}

}  // namespace ascend::ui
