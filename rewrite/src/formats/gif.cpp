// SPDX-License-Identifier: GPL-3.0-or-later
#include "formats/gif.h"

#include <cstdio>
#include <cstring>

namespace ascend::formats {
namespace {

// LZW bit-stream reader (LSB-first, per GIF87a "packed codes").
struct BitReader {
    const uint8_t* p;
    size_t left;
    uint32_t acc = 0;
    int nbits = 0;
    bool ok = true;

    uint32_t read(int w) {
        while (nbits < w) {
            if (!left) { ok = false; return 0; }
            acc |= uint32_t(*p++) << nbits;
            left--;
            nbits += 8;
        }
        const uint32_t v = acc & ((1u << w) - 1);
        acc >>= w;
        nbits -= w;
        return v;
    }
};

constexpr int kMaxCode = 1 << 12;
constexpr int kFirstCodeCap = 256 + 2;  // min code size 8: clear + EOI
// Output-prefix table: suffix byte + parent link (no malloc per code).
constexpr int kTableCap = kMaxCode;

}  // namespace

bool gifDecodeFrame(const uint8_t* d, size_t len, GifFrame* out,
                    std::string* err) {
    auto fail = [&](const char* why) {
        if (err) *err = why;
        return false;
    };
    if (len < 13) return fail("gif: file shorter than header");
    if (std::memcmp(d, "GIF87a", 6) != 0) return fail("gif: not GIF87a");
    const uint32_t sw = uint32_t(d[6]) | (uint32_t(d[7]) << 8);
    const uint32_t sh = uint32_t(d[8]) | (uint32_t(d[9]) << 8);
    const uint8_t packed = d[10];
    if (!((packed >> 7) & 1)) return fail("gif: no global colour table");
    const size_t ntab = 3u << ((packed & 7) + 1);
    size_t i = 13;
    if (i + ntab > len) return fail("gif: truncated GCT");
    std::vector<uint8_t> gct(d + i, d + i + ntab);
    i += ntab;

    // Skip extensions until the FIRST image descriptor; a SECOND image is a
    // refusal (our law covers exactly one frame — title-art.md §3).
    for (;;) {
        if (i >= len) return fail("gif: no image descriptor");
        if (d[i] == 0x3b) return fail("gif: trailer before image");
        if (d[i] == 0x21) {  // extension: label + sub-blocks
            i += 2;
            while (i < len && d[i]) {
                if (i + 1 + d[i] > len) return fail("gif: truncated extension");
                i += 1 + d[i];
            }
            i++;  // block terminator
            continue;
        }
        if (d[i] == 0x2c) break;
        return fail("gif: unexpected block type");
    }
    if (i + 10 > len) return fail("gif: truncated image descriptor");
    const uint32_t ix = uint32_t(d[i + 1]) | (uint32_t(d[i + 2]) << 8);
    const uint32_t iy = uint32_t(d[i + 3]) | (uint32_t(d[i + 4]) << 8);
    const uint32_t iw = uint32_t(d[i + 5]) | (uint32_t(d[i + 6]) << 8);
    const uint32_t ih = uint32_t(d[i + 7]) | (uint32_t(d[i + 8]) << 8);
    const uint8_t ip = d[i + 9];
    if ((ip >> 7) & 1) return fail("gif: local colour table not supported");
    if ((ip >> 6) & 1) return fail("gif: interlaced image not supported");
    if (ix != 0 || iy != 0 || iw != sw || ih != sh)
        return fail("gif: image does not fill the logical screen");
    i += 10;
    if (i >= len) return fail("gif: missing LZW min code size");
    const uint8_t mcs = d[i++];
    if (mcs != 8) return fail("gif: LZW min code size != 8");

    // Gather the compressed stream (sub-block chains until 0x00).
    std::vector<uint8_t> comp;
    for (;;) {
        if (i >= len) return fail("gif: truncated LZW sub-blocks");
        const uint8_t sz = d[i++];
        if (sz == 0) break;
        if (i + sz > len) return fail("gif: truncated LZW sub-block");
        comp.insert(comp.end(), d + i, d + i + sz);
        i += sz;
    }
    // ONE frame law (title-art.md §3: the file's own shape): after the
    // stream terminator, a further image descriptor is a refusal, not a
    // silently-ignored animation.
    for (size_t j = i; j < len; j++) {
        if (d[j] == 0x2c) return fail("gif: more than one image");
        if (d[j] == 0x3b) break;
        if (d[j] == 0x21) {  // trailing extension: skip its sub-blocks
            j += 2;
            while (j < len && d[j]) j += d[j];
            continue;
        }
    }

    const size_t plane = size_t(iw) * ih;
    out->width = iw;
    out->height = ih;
    out->gct.swap(gct);
    out->indices.assign(plane, 0);

    // LZW (classical chain decoder, t390): entry(code) is the byte sequence
    // suffix[code] at the END, linked by parent[] toward the front; the new
    // entry after reading `code` is bytes(prev) + first(bytes(code)), stored
    // as suffix[next]=first, parent[next]=prev. KwKwK (code == next) emits
    // bytes(prev) + first(bytes(prev)). CODE-WIDTH LAW MEASURED AGAINST THE
    // PIL REFERENCE PLANE (scripts/t390_lzwmirror.py): grow when
    // next >= 2^width — the "early change" variant desyncs at output 11208
    // on this very file (title-art.md §6.3 family of traps).
    BitReader br{comp.data(), comp.size()};
    const uint32_t clearCode = 256, eoiCode = 257;
    const uint32_t kNoPrev = 0xFFFFFFFFu;
    int width = mcs + 1;
    uint32_t next = kFirstCodeCap;
    uint32_t prev = kNoPrev;
    uint8_t suffix[kTableCap];
    uint16_t parent[kTableCap];
    size_t o = 0;
    uint8_t rev[kTableCap + 2];  // chain bytes back-to-front (depth <= next)
    for (;;) {
        const uint32_t code = br.read(width);
        if (!br.ok) return fail("gif: LZW stream overrun");
        if (code == eoiCode) break;
        if (code == clearCode) {
            width = mcs + 1;
            next = kFirstCodeCap;
            prev = kNoPrev;
            continue;
        }
        if (code > next || (code == next && prev == kNoPrev))
            return fail("gif: LZW code beyond table");
        // Entry(code) = root byte + forward chain of suffixes. rev[] holds
        // the chain back-to-front; emit = first, then reversed(rev), then
        // the root AGAIN for the KwKwK code (entry == prev + prev[0]).
        const bool kwk = (code == next);
        uint32_t walk = kwk ? prev : code;
        size_t rn = 0;
        while (walk >= kFirstCodeCap) {
            if (rn >= sizeof rev) return fail("gif: LZW chain too deep");
            rev[rn++] = suffix[walk];
            walk = parent[walk];
        }
        const uint8_t first = uint8_t(walk);  // chain root = entry[0]
        if (o + rn + 1 + (kwk ? 1 : 0) > plane) return fail("gif: plane overflow");
        out->indices[o++] = first;
        while (rn) out->indices[o++] = rev[--rn];
        if (kwk) out->indices[o++] = first;
        if (prev != kNoPrev && next < uint32_t(kTableCap)) {
            suffix[next] = first;
            parent[next] = uint16_t(prev);
            // After KwKwK, code has NO table slot of its own (chain(code)
            // is stale); the entry just added at `next` IS the emitted
            // sequence, so it becomes prev for the next round.
            prev = kwk ? next : code;
            next++;
            if (width < 12 && next >= (uint32_t(1) << width)) width++;
        } else {
            prev = code;
        }
    }
    if (o != plane) {
        char buf[96];
        std::snprintf(buf, sizeof buf, "gif: decoded %zu bytes, plane is %zu",
                      o, plane);
        if (err) *err = buf;
        return false;
    }
    return true;
}

bool gifDecodeFile(const std::string& path, GifFrame* out, std::string* err) {
    std::FILE* f = std::fopen(path.c_str(), "rb");
    if (!f) {
        if (err) *err = "gif: cannot open " + path;
        return false;
    }
    std::vector<uint8_t> buf;
    uint8_t tmp[65536];
    size_t n;
    while ((n = std::fread(tmp, 1, sizeof tmp, f)) > 0)
        buf.insert(buf.end(), tmp, tmp + n);
    std::fclose(f);
    return gifDecodeFrame(buf.data(), buf.size(), out, err);
}

}  // namespace ascend::formats
