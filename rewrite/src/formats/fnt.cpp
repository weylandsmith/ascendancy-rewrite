#include "formats/fnt.h"

#include <cstring>
#include <fstream>

namespace ascend::formats {

namespace {
uint32_t le32(const uint8_t* p) {
    return uint32_t(p[0]) | uint32_t(p[1]) << 8 | uint32_t(p[2]) << 16 |
           uint32_t(p[3]) << 24;
}
}  // namespace

// Every check below mirrors scripts/fnt_probe.py (docs/re/fnt.md): the
// Python validator and this parser enforce the identical law on the same
// vendor files; tests/test_fnt.cpp pins both against the real data.
bool Font::load(const std::string& path, std::string* err) {
    std::ifstream f(path, std::ios::binary | std::ios::ate);
    if (!f) {
        if (err) *err = "cannot open " + path;
        return false;
    }
    const auto size = size_t(f.tellg());
    f.seekg(0);
    img_.resize(size);
    f.read(reinterpret_cast<char*>(img_.data()), std::streamsize(size));

    const uint8_t* d = img_.data();
    if (size < 16 + 4 * kGlyphCount || d[0] != '1' || d[1] != '.' || d[2] || d[3]) {
        if (err) *err = "bad .fnt magic/size in " + path;
        return false;
    }
    const uint32_t n = le32(d + 4), h = le32(d + 8), v255 = le32(d + 12);
    if (n != uint32_t(kGlyphCount) || v255 != 255 || h == 0 || h > 64) {
        if (err) *err = "unexpected .fnt header in " + path;
        return false;
    }
    const uint8_t* off = d + 16;
    uint32_t prev = 0;
    for (int i = 0; i < kGlyphCount; i++) {
        const uint32_t o = le32(off + 4 * i);
        if (i && o <= prev) {
            if (err) *err = "glyph offsets not strictly increasing in " + path;
            return false;
        }
        prev = o;
        const size_t e = i + 1 < kGlyphCount ? size_t(le32(off + 4 * i + 4)) : size;
        if (o + 4 > size || e < o + 4) {
            if (err) *err = "glyph slot out of range in " + path;
            return false;
        }
        const uint32_t w = le32(d + o);
        if (e - o != 4 + size_t(w) * h) {
            if (err) *err = "glyph slot != 4+w*h in " + path;
            return false;
        }
        Glyph g;
        g.width = w;
        g.px = d + o + 4;
        glyphs_.push_back(g);
    }
    // Last body must end exactly at EOF (fnt.md §Container).
    if (size_t(le32(off + 4 * (kGlyphCount - 1))) + 4 +
            size_t(glyphs_.back().width) * h != size) {
        if (err) *err = "last glyph does not end at EOF in " + path;
        return false;
    }
    h_ = int(h);
    return true;
}

void Font::renderGlyphArgb(int code, uint32_t* out) const {
    const Glyph& g = glyph(code);
    if (!g.px) return;
    for (int y = 0; y < h_; y++)
        for (uint32_t x = 0; x < g.width; x++) {
            const uint8_t v = g.px[size_t(y) * g.width + x];
            if (v == 0xFF) {
                out[size_t(y) * g.width + x] = 0xFF121218u;  // dark chrome bg
            } else {
                // intensity 40..(40+14*30) clamps to 255 (greyscale; fnt.md
                // §Pixel semantics) — clamp BEFORE the channel spread.
                uint32_t c = uint32_t(40 + (v - 0xF0) * 30);
                if (c > 255) c = 255;
                out[size_t(y) * g.width + x] = 0xFF000000u | c * 0x010101u;
            }
        }
}

uint64_t Font::inkCensus() const {
    uint64_t c = 0;
    for (const Glyph& g : glyphs_)
        for (size_t i = 0; i < size_t(g.width) * h_; i++)
            c += g.px[i] != 0xFF;
    return c;
}

}  // namespace ascend::formats
