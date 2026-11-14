// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
// Shared internal renderer pieces for the SDL UI layers (title screen +
// campaign loop). NOT a public API — consumers use ui/ui.h.
#include <SDL.h>

#include <cstdint>
#include <string>
#include <vector>

#include "formats/fnt.h"
#include "ui/layout.h"

namespace ascend::ui {

// Vendor text faces (docs/re/fnt.md, OQ-017 CLOSED): SMALLFONT/BIGFONT as
// windows.txt:30-32 maps them (ui-runtime.md §3). Each face is blitted from a
// white-with-alpha atlas (one row, glyphs packed left-to-right with a 1px
// gutter) tinted per draw call via SDL_SetTextureColorMod. sm/big ink is the
// SINGLE value 0xF3 [verified corpus-wide, fnt_probe]: binary ink/background,
// so atlas alpha is 255/0 — no intensity ramp is invented. advance == width,
// no bearings [verified]; codes 0..31 and @^{|}~ carry no ink (blank, still
// advance) exactly as in the vendor font.
struct VendorText {
    ascend::formats::Font sm, big;
    struct Face {
        SDL_Texture* tex = nullptr;
        int gx[ascend::formats::Font::kGlyphCount] = {};
        int gw[ascend::formats::Font::kGlyphCount] = {};
        int h = 0;
    };
    Face smFace, bigFace;

    bool buildFace(SDL_Renderer* r, const ascend::formats::Font& f, Face* out,
                   std::string* err);
    bool load(SDL_Renderer* r, const std::string& root, std::string* err);
    void draw(SDL_Renderer* r, int x, int y, const std::string& s, bool large,
              SDL_Color c);
    // Width of `s` in px on `large` face (advance == width law).
    int width(const std::string& s, bool large) const;
    void release();
    ~VendorText() { release(); }
};

}  // namespace ascend::ui
