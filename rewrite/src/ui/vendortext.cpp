// SPDX-License-Identifier: GPL-3.0-or-later
// VendorText implementation — moved verbatim out of ui.cpp (t385) so the
// title-screen loop (title.cpp) and the campaign loop share ONE renderer.
// Laws + citations live in ui_internal.h / docs/re/fnt.md.
#include "ui/ui_internal.h"

#include <algorithm>

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

bool blitShape(SDL_Renderer* ren, const ascend::formats::ShapeLibrary& lib,
               int rec, int x, int y) {
    return blitShapeScaled(ren, lib, rec, x, y, 1);
}

bool blitShapeScaled(SDL_Renderer* ren,
                     const ascend::formats::ShapeLibrary& lib, int rec,
                     int x, int y, int scale) {
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
    for (size_t k = 0; k < a.size(); k++) {
        const uint8_t idx = a[k];
        uint32_t rgb;
        if (g_chromePal.ready()) {
            rgb = g_chromePal.argb(idx) & 0x00FFFFFFu;
        } else {
            const uint32_t lum = 40u + (uint32_t(idx) * 185u) / 255u;
            rgb = (lum << 16) | (lum << 8) | lum;
        }
        argb[k] = (a[k] == b[k] ? 0xFF000000u : 0x00000000u) | rgb;
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

}  // namespace ascend::ui
