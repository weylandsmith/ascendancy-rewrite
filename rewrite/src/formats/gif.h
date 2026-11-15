// SPDX-License-Identifier: GPL-3.0-or-later

#pragma once
// GIF87a single-frame 8-bpp INDEX-PLANE decoder (t390).
//
// SCOPE IS DELIBERATELY THE FILE'S OWN SHAPE (docs/re/title-art.md §1/§3,
// measured law for extracted/ascend01/data/0opening.gif): GIF87a header,
// one image descriptor 640x480 at (0,0), global colour table 256 entries,
// LZW min code size 8, sub-blocks, trailer. Anything outside that shape is
// REFUSED with a reason — never clamped or silently substituted
// (docs/BLOCKED.md t68 residue law).
//
// INTERLACE TRAP (t390 measurement): the LOGICAL SCREEN packed byte of this
// file (0xd7) has the interlace bit SET while the IMAGE DESCRIPTOR packed
// byte (0x00) has it CLEAR. Interlace is defined by the image descriptor
// (GIF87a spec); this decoder reads it there and refuses an interlaced
// image rather than guessing row order (the file we must render is not
// interlaced; a future interlaced asset is a new measurement, not a flag).
//
// LZW follows the convention the PIL reference decoder uses on this file:
// code width INCREMENTS WHEN next >= (1<<width), i.e. NOT "early change".
// Measured law (scripts/t390_lzwmirror.py): early change desyncs at output
// index 11208 of this very file (the title-art.md §6.3 family of traps —
// the stdlib-python decoder desyncs at 6096 for the same class of reason).
// Pins in tests/test_gif_t390.cpp are PIL-plane values (reference
// rasterizer law, title-art.md §6.3).

#include <cstdint>
#include <cstddef>
#include <string>
#include <vector>

namespace ascend::formats {

struct GifFrame {
    uint32_t width = 0;
    uint32_t height = 0;
    std::vector<uint8_t> indices;   // width*height palette indices
    std::vector<uint8_t> gct;       // 3*ntab global colour-table bytes
};

// Decode the FIRST image of a GIF87a file held in memory. False + *err on
// any shape violation (signature, >1 image, interlace, local colour
// table, position, min-code-size != 8, stream overrun, plane size).
bool gifDecodeFrame(const uint8_t* data, size_t len, GifFrame* out,
                    std::string* err);

// File convenience wrapper (reads the whole file; these assets are ~45 KB).
bool gifDecodeFile(const std::string& path, GifFrame* out, std::string* err);

}  // namespace ascend::formats
