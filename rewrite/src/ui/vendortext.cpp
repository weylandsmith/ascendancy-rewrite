// SPDX-License-Identifier: GPL-3.0-or-later
// VendorText implementation — moved verbatim out of ui.cpp (t385) so the
// title-screen loop (title.cpp) and the campaign loop share ONE renderer.
// Laws + citations live in ui_internal.h / docs/re/fnt.md.
#include "ui/ui_internal.h"

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

}  // namespace ascend::ui
