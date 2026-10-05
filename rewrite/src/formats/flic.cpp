// FLC decoder — 1:1 port of scripts/flc_probe.py (the probe is the reference
// implementation, validated against both vendor files zero-residue and
// visually: docs/re/flc.md §1,§3). Rules cite docs/re/flc.md §2.
#include "formats/flic.h"

#include <cstdio>
#include <cstring>

namespace ascend::formats {

namespace {
inline uint16_t rd16(const uint8_t* p) {
    return static_cast<uint16_t>(p[0] | (p[1] << 8));
}
inline uint32_t rd32(const uint8_t* p) {
    return static_cast<uint32_t>(p[0]) | (static_cast<uint32_t>(p[1]) << 8) |
           (static_cast<uint32_t>(p[2]) << 16) | (static_cast<uint32_t>(p[3]) << 24);
}
}  // namespace

bool Flic::load(const std::string& path, std::string* err) {
    std::FILE* f = std::fopen(path.c_str(), "rb");
    if (!f) {
        *err = "flic: cannot open " + path;
        return false;
    }
    std::fseek(f, 0, SEEK_END);
    const long n = std::ftell(f);
    std::fseek(f, 0, SEEK_SET);
    if (n < 128 + 16) {
        std::fclose(f);
        *err = "flic: file too small";
        return false;
    }
    data_.resize(static_cast<size_t>(n));
    if (std::fread(data_.data(), 1, data_.size(), f) != data_.size()) {
        std::fclose(f);
        *err = "flic: short read";
        return false;
    }
    std::fclose(f);
    const uint8_t* d = data_.data();
    // Header: size,type,frames,width,height,depth,flags at 0..13; speed at 16
    // (docs/re/flc.md §2, compuphase FLIC_HEADER).
    if (rd16(d + 4) != 0xAF12) {
        *err = "flic: not an FLC (magic)";
        return false;
    }
    if (rd32(d) != data_.size()) {
        *err = "flic: header size != file size";
        return false;
    }
    nframes_ = rd16(d + 6);
    w_ = static_cast<int16_t>(rd16(d + 8));
    h_ = static_cast<int16_t>(rd16(d + 10));
    if (rd16(d + 12) != 8) {
        *err = "flic: depth != 8 unsupported";
        return false;
    }
    speed_ = rd32(d + 16);
    // Top-level chain from 128 (oframe1/oframe2 are ZERO in both vendor
    // files — measured, docs/re/flc.md §1; chain walk is the portable route).
    size_t o = 128;
    while (o < data_.size()) {
        const uint32_t csz = rd32(d + o);
        const uint16_t ct = rd16(d + o + 4);
        if (csz < 6 || o + csz > data_.size()) {
            *err = "flic: top chunk does not tile";
            return false;
        }
        if (ct == kFrame) {
            Chunk c;
            c.off = static_cast<uint32_t>(o);
            c.size = csz;
            c.nchunks = rd16(d + o + 6);
            c.delay = rd16(d + o + 8);
            frames_.push_back(c);
        } else if (ct != 0xF100) {  // PREFIX tolerated (both files carry one)
            *err = "flic: unexpected top chunk type";
            return false;
        }
        o += csz;
    }
    if (o != data_.size() || frames_.empty()) {
        *err = "flic: chain walk residue or no frames";
        return false;
    }
    return true;
}

bool Flic::subchunks(const uint8_t* d, const Chunk& c,
                     std::vector<Sub>* subs) const {
    size_t so = c.off + 16;  // FRAME_TYPE header is 16 B (flc.md §2)
    const size_t end = c.off + c.size;
    subs->clear();
    uint16_t n = 0;
    while (c.nchunks ? (n < c.nchunks) : (so + 6 <= end)) {
        if (so + 6 > end) return false;
        Sub s;
        s.off = static_cast<uint32_t>(so);
        s.size = rd32(d + so);
        s.type = rd16(d + so + 4);
        if (s.size < 6 || so + s.size > end) return false;
        subs->push_back(s);
        so += s.size;
        ++n;
    }
    return so == end;
}

bool Flic::repairCopy(std::vector<Sub>* subs, const Chunk& c) const {
    // compuphase "Frequent errors": writers emit FLI_COPY with a WRONG chunk
    // size. Repair ONLY type-16 sizes to 6+w*h, then demand exact tiling
    // (port of flc_probe.repair_copy).
    std::vector<Sub> out = *subs;
    for (Sub& s : out)
        if (s.type == kFliCopy && s.size != 6u + static_cast<unsigned>(w_ * h_))
            s.size = 6u + static_cast<unsigned>(w_ * h_);
    if (out.empty()) return false;
    size_t p = out[0].off;
    for (const Sub& s : out) {
        if (s.off != p) return false;
        p += s.size;
    }
    if (p - out[0].off != c.size - 16) return false;
    subs->swap(out);
    return true;
}

namespace {

using Sub = Flic::Sub;

bool decodeColor(const uint8_t* d, const Sub& s, uint8_t* pal, bool scale64,
                 std::string* err) {
    const size_t off = s.off, end = s.off + s.size;
    const uint16_t npk = rd16(d + off + 6);
    size_t p = off + 8;
    size_t idx = 0;
    for (uint16_t k = 0; k < npk; ++k) {
        if (p + 2 > end) return *err = "COLOR packet header OOB", false;
        size_t skip = d[p];
        size_t cnt = d[p + 1] ? d[p + 1] : 256;
        p += 2;
        idx += skip;
        if (idx + cnt > 256 || p + cnt * 3 > end)
            return *err = "COLOR packet range", false;
        for (size_t i = 0; i < cnt; ++i) {
            uint8_t r = d[p], g = d[p + 1], b = d[p + 2];
            p += 3;
            pal[(idx + i) * 3 + 0] = scale64 ? static_cast<uint8_t>(r << 2) : r;
            pal[(idx + i) * 3 + 1] = scale64 ? static_cast<uint8_t>(g << 2) : g;
            pal[(idx + i) * 3 + 2] = scale64 ? static_cast<uint8_t>(b << 2) : b;
        }
    }
    if (end - p > 1) return *err = "COLOR residue", false;  // 1 B = even pad
    return true;
}

bool decodeBrun(const uint8_t* d, const Sub& s, uint8_t* px, int w, int h,
                std::string* err) {
    const size_t end = s.off + s.size;
    size_t p = s.off + 6;
    for (int y = 0; y < h; ++y) {
        if (p >= end) return *err = "BYTE_RUN ran out", false;
        ++p;  // packet count holdover — IGNORE, width is the criterion (§2)
        int x = 0;
        while (x < w) {
            if (p >= end) return *err = "BYTE_RUN packet OOB", false;
            const int8_t c = static_cast<int8_t>(d[p]);
            ++p;
            if (c > 0) {
                if (p >= end || x + c > w) return *err = "BYTE_RUN replicate OOB", false;
                std::memset(px + static_cast<size_t>(y) * w + x, d[p], c);
                ++p;
                x += c;
            } else if (c < 0) {
                const int n = -c;
                if (static_cast<long>(p) + n > static_cast<long>(end) || x + n > w)
                    return *err = "BYTE_RUN literal OOB", false;
                std::memcpy(px + static_cast<size_t>(y) * w + x, d + p, n);
                p += n;
                x += n;
            } else {
                return *err = "BYTE_RUN zero count", false;
            }
        }
    }
    if (static_cast<long>(end) - static_cast<long>(p) > 1)
        return *err = "BYTE_RUN residue", false;
    return true;
}

bool decodeCopy(const uint8_t* d, const Sub& s, uint8_t* px, int w, int h,
                std::string* err) {
    const size_t need = static_cast<size_t>(w) * h;
    if (s.off + 6 + need > s.off + s.size) return *err = "FLI_COPY truncated", false;
    std::memcpy(px, d + s.off + 6, need);
    return true;
}

bool decodeDelta(const uint8_t* d, const Sub& s, uint8_t* px, int w, int h,
                 std::string* err) {
    const size_t end = s.off + s.size;
    size_t p = s.off + 6;
    const uint16_t nlines = rd16(d + p);
    p += 2;
    int y = 0, done = 0;
    const size_t npix = static_cast<size_t>(w) * h;
    while (done < nlines) {
        if (p + 2 > end) return *err = "DELTA opcode OOB", false;
        const uint16_t op = rd16(d + p);
        p += 2;
        const uint16_t top = op & 0xC000;
        if (top == 0xC000) {  // signed negation skip (flc.md §2; MEASURED)
            y -= static_cast<int16_t>(op);
            if (y > h) return *err = "DELTA skip past bottom", false;
            continue;
        }
        if (top == 0x8000) {
            if (y >= h) return *err = "DELTA last-byte OOB", false;
            px[static_cast<size_t>(y) * w + (w - 1)] = op & 0xFF;
            continue;
        }
        if (top == 0x4000) return *err = "DELTA undefined opcode", false;
        const uint16_t npk = op;
        int x = 0;
        if (y >= h) return *err = "DELTA packet past bottom", false;
        for (uint16_t k = 0; k < npk; ++k) {
            if (p + 2 > end) return *err = "DELTA packet header OOB", false;
            const int skip = d[p];
            const int cnt = static_cast<int8_t>(d[p + 1]);
            p += 2;
            x += skip;
            if (cnt > 0) {
                const int nb = cnt * 2;
                if (static_cast<long>(p) + nb > static_cast<long>(end))
                    return *err = "DELTA copy data OOB", false;
                const size_t base = static_cast<size_t>(y) * w + x;
                if (base + nb > npix) return *err = "DELTA copy OOB", false;
                std::memcpy(px + base, d + p, nb);
                p += nb;
                x += nb;
            } else if (cnt < 0) {
                if (p + 2 > end) return *err = "DELTA replicand OOB", false;
                const int n = -cnt * 2;
                const size_t base = static_cast<size_t>(y) * w + x;
                if (base + n > npix) return *err = "DELTA replicate OOB", false;
                for (int i = 0; i < n; i += 2) {
                    px[base + i] = d[p];
                    px[base + i + 1] = d[p + 1];
                }
                p += 2;
                x += n;
            }
            // cnt == 0: skip-only packet, already added
        }
        ++y;
        ++done;
    }
    while (p < end) {  // trailing skip opcodes are legal
        if (p + 2 > end) return *err = "DELTA odd trailing byte", false;
        if ((rd16(d + p) & 0xC000) != 0xC000) return *err = "DELTA trailing opcode", false;
        p += 2;
    }
    return true;
}

bool decodePstamp(const uint8_t* d, const Sub& s, std::string* err) {
    // Structure only (the port never draws the stamp): 12 B header, embedded
    // chunks, type-18 embedded = 256 B six-cube table (flc.md §2).
    if (rd16(d + s.off + 4) != Flic::kPstamp) return *err = "PSTAMP magic", false;
    size_t so = s.off + 12;
    const size_t end = s.off + s.size;
    while (so + 6 <= end) {
        const uint32_t isz = rd32(d + so);
        const uint16_t it = rd16(d + so + 4);
        if (isz < 6 || so + isz > end) return *err = "PSTAMP subchunk OOB", false;
        if (it == Flic::kPstamp && isz != 6 + 256) return *err = "PSTAMP table size", false;
        so += isz;
    }
    if (so != end) return *err = "PSTAMP residue", false;
    return true;
}

}  // namespace

bool Flic::applyChunk(const uint8_t* data, size_t size, uint16_t nchunks,
                      uint8_t* px, uint8_t* pal, int* repaired,
                      std::string* err) const {
    // Frame chunk view over an arbitrary buffer (data must be the start of a
    // 0xF1FA chunk inside `data`).
    if (size < 16 || rd16(data + 4) != kFrame) return *err = "not a frame chunk", false;
    Chunk c;
    c.off = 0;
    c.size = static_cast<uint32_t>(size);
    c.nchunks = nchunks;
    c.delay = rd16(data + 8);
    if (rd16(data + 12) || rd16(data + 14)) return *err = "EGI size override", false;
    std::vector<Sub> subs;
    if (!subchunks(data, c, &subs)) {
        if (!repairCopy(&subs, c)) return *err = "frame subchunks do not tile", false;
        if (repaired) ++*repaired;
    }
    for (const Sub& s : subs) {
        switch (s.type) {
            case kColor256:
                if (!decodeColor(data, s, pal, false, err)) return false;
                break;
            case kColor64:
                if (!decodeColor(data, s, pal, true, err)) return false;
                break;
            case kByteRun:
                if (!decodeBrun(data, s, px, w_, h_, err)) return false;
                break;
            case kFliCopy:
                if (!decodeCopy(data, s, px, w_, h_, err)) return false;
                break;
            case kDeltaFlc:
                if (!decodeDelta(data, s, px, w_, h_, err)) return false;
                break;
            case kPstamp:
                if (!decodePstamp(data, s, err)) return false;
                break;
            default:
                return *err = "unknown subchunk type", false;
        }
    }
    return true;
}

bool Flic::replay(const std::function<void(int, const uint8_t*, const uint8_t*)>& cb,
                  std::string* err, int* repairedOut) const {
    std::vector<uint8_t> px(static_cast<size_t>(w_) * h_, 0), pal(256 * 3, 0);
    int repaired = 0;
    int i = 0;
    for (const Chunk& c : frames_) {
        if (!applyChunk(data_.data() + c.off, c.size, c.nchunks, px.data(),
                        pal.data(), &repaired, err)) {
            *err += " (frame " + std::to_string(i) + ")";
            return false;
        }
        cb(i++, px.data(), pal.data());
    }
    if (repairedOut) *repairedOut = repaired;
    return true;
}

}  // namespace ascend::formats
