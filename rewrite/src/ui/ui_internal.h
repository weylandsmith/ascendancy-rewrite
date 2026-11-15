// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
// Shared internal renderer pieces for the SDL UI layers (title screen +
// campaign loop). NOT a public API — consumers use ui/ui.h.
#include <SDL.h>

#include <cstdint>
#include <string>
#include <vector>

#include "formats/fnt.h"
#include "formats/gamepal.h"
#include "formats/shp.h"
#include "ui/layout.h"
#include "ui/menulaw.h"

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

// t388: chrome blit shared by the title loop (title.cpp) and the campaign
// loop (ui.cpp). Definition in vendortext.cpp; semantics documented there.
bool blitShape(SDL_Renderer* ren, const ascend::formats::ShapeLibrary& lib,
               int rec, int x, int y);

// t401: same decode/palette path as blitShape, drawn at scale (integer,
// NEAREST filter — the scale FACTOR for RACELIST portraits is a port law;
// the vendor's own filter is a named seam, docs/re/t401-newgame-art.md S10).
bool blitShapeScaled(SDL_Renderer* ren,
                     const ascend::formats::ShapeLibrary& lib, int rec,
                     int x, int y, int scale);

// t398: load DATA\game.pal for blitShape's colour path (process-wide; the
// data root never changes mid-session — only the FIRST call in a process
// reads the file and prints the diagnostic line; later calls just report
// readiness). Success: `ui palette: game.pal ...`; failure names the tried
// path and the greyscale-ramp degradation (never aborts — silent-degrade).
bool loadChromePalette(const std::string& dataRoot);

// t388: the load screen moved out of title.cpp's anonymous namespace so the
// campaign loop can reuse it (t388 task: Save/Load reuse the t387 windows).
// Return >=0 accepted slot index; kLoadCancel (Esc); kLoadQuit (SDL_QUIT).
constexpr int kLoadCancel = -1;
constexpr int kLoadQuit = -2;
int runLoadScreen(SDL_Renderer* ren, VendorText& txt,
                  const std::string& dataRoot,
                  const std::vector<SaveSlot>& slots);

}  // namespace ascend::ui
