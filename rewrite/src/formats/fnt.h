// SPDX-License-Identifier: GPL-3.0-or-later

#pragma once
#include <cstdint>
#include <string>
#include <vector>

namespace ascend::formats {
// Vendor .fnt font face. Spec: docs/re/fnt.md (OQ-017 CLOSED). Container:
// magic '1.'+0000, u32 N=128, u32 HEIGHT, u32 255, N u32 glyph offsets
// (strictly increasing), each glyph = u32 width + EXACTLY width*HEIGHT
// bytes, 1 byte per pixel row-major, no stride padding, last body at EOF.
// 0xFF = background; other values = ink, BRIGHTER with higher byte value
// (measured edge/interior census, fnt.md): sm/bigfont are solid 0xF3 faces,
// intro.fnt is a 0xF0(fringe)..0xFE(core) anti-alias ramp.
class Font {
  public:
    struct Glyph {
        uint32_t width = 0;
        const uint8_t* px = nullptr;  // width*height bytes into the image
    };

    // Parses and enforces every container invariant (same law the Python
    // validator scripts/fnt_probe.py asserts). False + *err on violation.
    bool load(const std::string& path, std::string* err);

    int height() const { return h_; }
    const Glyph& glyph(int code) const {
        static const Glyph kEmpty;
        return code >= 0 && code < kGlyphCount ? glyphs_[code] : kEmpty;
    }

    // Greyscale ARGB (0xAARRGGBB) blit target: dark chrome background,
    // ink brightened by intensity. out must hold w*h pixels.
    void renderGlyphArgb(int code, uint32_t* out) const;

    // Total ink-pixel census over all 128 glyphs (test pin, measured
    // 2026-10-04: sm=1075, big=1514, intro=11877; codes 0..31 and the
    // unimplemented printables carry no ink, so 32..126 sums match).
    uint64_t inkCensus() const;

    static constexpr int kGlyphCount = 128;

  private:
    std::vector<uint8_t> img_;
    std::vector<Glyph> glyphs_;
    int h_ = 0;
};
}  // namespace ascend::formats
