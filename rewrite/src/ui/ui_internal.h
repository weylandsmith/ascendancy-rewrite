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
#include "ui/boot.h"
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

// t414: blitShapeScaled with an optional CIRCULAR CLIP (clipR > 0 discards
// scaled pixels outside radius clipR about the rect centre — the vendor's
// ring-clipped race portraits; docs/re/_wip_t414.md S2e). clipR == 0 is
// exactly blitShapeScaled.
bool blitShapeCircular(SDL_Renderer* ren,
                       const ascend::formats::ShapeLibrary& lib, int rec,
                       int x, int y, int scale, int clipR);

// t398: load DATA\game.pal for blitShape's colour path (process-wide; the
// data root never changes mid-session — only the FIRST call in a process
// reads the file and prints the diagnostic line; later calls just report
// readiness). Success: `ui palette: game.pal ...`; failure names the tried
// path and the greyscale-ramp degradation (never aborts — silent-degrade).
bool loadChromePalette(const std::string& dataRoot);

// t412: the loaded game.pal entry as ARGB (alpha 255), or 0xFF808080 when
// the palette refused to load (callers draw something honest, never abort).
// Used by the race-intro ink law game.pal[racebyte*4 + 0x13]
// (docs/re/_wip_t412.md F4).
uint32_t chromePaletteArgb(int index);

// t388: the load screen moved out of title.cpp's anonymous namespace so the
// campaign loop can reuse it (t388 task: Save/Load reuse the t387 windows).
// Return >=0 accepted slot index; kLoadCancel (Esc); kLoadQuit (SDL_QUIT).
constexpr int kLoadCancel = -1;
constexpr int kLoadQuit = -2;
int runLoadScreen(SDL_Renderer* ren, VendorText& txt,
                  const std::string& dataRoot,
                  const std::vector<SaveSlot>& slots);

// t412: the race-intro screen (docs/re/raceintro.h + _wip_t412.md F3-F5 +
// _wip_t415.md F1-F5). Reads history.txt (supply-your-own; a refusal
// prints the reason and the screen STILL renders the chrome — silent-
// degrade), draws the framed three-well panel (chrome page, lgrace
// portrait, raceflag emblem, centred text) and blocks until a click or
// any key. raceName feeds the centred "<Name>: <POWER>" header (empty ->
// the bare POWER line). Returns BootState::Campaign or Quit.
BootState runRaceIntro(SDL_Renderer* ren, VendorText& txt,
                       const std::string& dataRoot, int specnum,
                       int atmosphere, const std::string& raceName);

}  // namespace ascend::ui
