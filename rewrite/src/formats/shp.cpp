#include "formats/shp.h"

#include <cstring>
#include <fstream>

namespace ascend::formats {

namespace {

uint32_t rd32(const std::vector<uint8_t>& b, size_t off) {
    return uint32_t(b[off]) | (uint32_t(b[off + 1]) << 8) |
           (uint32_t(b[off + 2]) << 16) | (uint32_t(b[off + 3]) << 24);
}

// One row walk per the S9 grammar; rows_this is the row-height guess.
// Returns true iff every row terminated (C==0) inside [stream, end).
// Writes clamp at W; destination bytes for skipped/clamped pixels are
// left untouched (original semantics, S14 clamp branches).
bool walkRows(const std::vector<uint8_t>& img, uint32_t stream,
              uint32_t end, uint32_t W, uint32_t rows_this,
              std::vector<uint8_t>& out, uint32_t outW) {
    size_t i = stream;
    for (uint32_t r = 0; r < rows_this; ++r) {
        uint32_t p = 0;
        for (;;) {
            if (i >= end) return false;
            uint8_t C = img[i++];
            if (C == 0) break;
            if (C == 1) {
                if (i >= end) return false;
                p += img[i++];  // transparent skip (dst untouched)
                continue;
            }
            uint32_t n = C >> 1;
            if (C & 1) {  // literal copy
                if (i + n > end) return false;
                for (uint32_t k = 0; k < n; ++k, ++p) {
                    if (p < W) out[size_t(r) * outW + p] = img[i + k];
                }
                i += n;
            } else {  // run fill
                if (i + 1 > end) return false;
                uint8_t v = img[i++];
                for (uint32_t k = 0; k < n; ++k, ++p) {
                    if (p < W) out[size_t(r) * outW + p] = v;
                }
            }
        }
    }
    return true;
}

}  // namespace

bool ShapeLibrary::load(const std::string& path, std::string* err) {
    std::ifstream f(path, std::ios::binary | std::ios::ate);
    if (!f) {
        if (err) *err = path + ": open failed";
        return false;
    }
    std::vector<uint8_t> buf(size_t(f.tellg()));
    f.seekg(0);
    f.read(reinterpret_cast<char*>(buf.data()), std::streamsize(buf.size()));
    f.close();
    if (!parse(std::move(buf), err)) {
        if (err) *err = path + ": " + *err;
        return false;
    }
    return true;
}

bool ShapeLibrary::parse(std::vector<uint8_t> img, std::string* err) {
    auto fail = [&](const std::string& m) {
        if (err) *err = m;
        img_ = {};
        records_ = {};
        return false;
    };
    img_ = std::move(img);
    if (img_.size() < 0x10 || rd32(img_, 0) != kMagic)
        return fail("magic");
    const uint32_t count = rd32(img_, 4);
    const uint32_t tsz = rd32(img_, 8);
    if (count == 0 || tsz != 8u * (count + 1)) return fail("table-size");
    const uint32_t te = 0x10 + tsz;
    if (img_.size() < te) return fail("truncated directory");
    // starts: te, then (count-1) u64 directory entries (absolute file
    // offsets). shp.md S1; Python parse() parity.
    std::vector<uint32_t> starts;
    starts.reserve(count);
    starts.push_back(te);
    for (uint32_t k = 0; k + 1 < count; ++k) {
        uint64_t raw = rd32(img_, 0x10 + 8 * k) |
                       (uint64_t(rd32(img_, 0x10 + 8 * k + 4)) << 32);
        if (raw <= starts.back() || raw >= img_.size())
            return fail("directory monotonicity/bounds");
        starts.push_back(uint32_t(raw));
    }
    records_.clear();
    records_.reserve(count);
    for (uint32_t k = 0; k < count; ++k) {
        const uint32_t rec = starts[k];
        const uint32_t nxt = k + 1 < count ? starts[k + 1]
                                           : uint32_t(img_.size());
        const uint32_t d_off = k == 0 ? rec : rec + 0x10;
        const uint32_t s_off = k == 0 ? rec + 8 : rec + 0x18;
        if (d_off + 8 > img_.size() || s_off > nxt)
            return fail("record header out of span");
        Record r;
        r.width = rd32(img_, d_off);
        r.height = rd32(img_, d_off + 4);
        r.start = rec;
        r.end = nxt;
        r.stream = s_off;
        records_.push_back(r);
    }
    return true;
}

bool ShapeLibrary::decode(int i, std::vector<uint8_t>& out) const {
    if (i < 0 || i >= count()) return false;
    const Record& r = records_[i];
    // Dims sanity bound == the Python validator's (4096): FAIL-class
    // records carry garbage dim words (e.g. 1starmap rec0x1 = 0x7ffffdbb)
    // and must be REPORTED as decode failures, never allocated against.
    if (r.width == 0 || r.height == 0 || r.width > 4096 || r.height > 4096)
        return false;
    if (out.size() < size_t(r.width) * r.height)
        out.resize(size_t(r.width) * r.height);
    // Canonical row count is the SECOND u32 of the dims pair (H);
    // orientation residue of the S16 residual class may store it first.
    if (walkRows(img_, r.stream, r.end, r.width, r.height, out, r.width))
        return true;
    if (r.width != r.height) {
        // Residual-class fallback (S16 [inferred]): swap the pair.
        std::vector<uint8_t> alt(out);
        if (walkRows(img_, r.stream, r.end, r.height, r.width, alt,
                     r.height)) {
            out.swap(alt);
            return true;
        }
    }
    return false;
}

}  // namespace ascend::formats
