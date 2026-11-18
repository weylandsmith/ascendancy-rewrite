// SPDX-License-Identifier: GPL-3.0-or-later

#include "formats/shp.h"

#include <cstring>
#include <fstream>

namespace ascend::formats {

namespace {

uint32_t rd32(const std::vector<uint8_t>& b, size_t off) {
    return uint32_t(b[off]) | (uint32_t(b[off + 1]) << 8) |
           (uint32_t(b[off + 2]) << 16) | (uint32_t(b[off + 3]) << 24);
}

int32_t rd32s(const std::vector<uint8_t>& b, size_t off) {
    return int32_t(rd32(b, off));
}

// t423 PARTIAL WALK (docs/re/_wip_t423.md F5b): 3cfgnew.shp k12 is
// truncated IN THE SHIPPED ARCHIVE (ascend01.cob blob size == extracted
// twin md5, both end mid-row ~55 of 79). The vendor blit has no length
// arg and paints whatever bytes are resident, so the honest port model of
// a truncated LAST record is: paint the rows that walk cleanly, leave
// rows at/below EOF untouched (transparent-skip semantics), report
// *partial=true. k0..k11 cross the directory span into the NEXT record's
// bytes exactly as before (t197), so this NEVER changes their result:
// only a walk that hits img_.end can partial.
// One row walk per the S9 grammar; rows_this is the row-height guess.
// Returns true iff every row terminated (C==0) inside the IMAGE (file
// bytes), never the directory span: t197 measured (shp.md S20.2/S21) that
// the blit FUN_0005caac takes no stream-length argument, has no
// stream-overrun error code (-1 dims @0x5cb2b, -2 empty clip @0x5cb36,
// -3 fully outside @0x5cea5 only), and draws from a VERBATIM whole-library
// cache copy (S10/S12) — so rows that run past [rec,nxt) read resident
// bytes the vendor decodes, and the span bound was our validator's
// invention. Writes clamp at W; destination bytes for skipped/clamped
// pixels are left untouched (original semantics, S14 clamp branches).
bool walkRows(const std::vector<uint8_t>& img, uint32_t stream,
              uint32_t W, uint32_t rows_this,
              std::vector<uint8_t>& out, uint32_t outW,
              bool partialOk = false) {
    size_t i = stream;
    for (uint32_t r = 0; r < rows_this; ++r) {
        uint32_t p = 0;
        for (;;) {
            if (i >= img.size()) {
                // t423: rows completed BEFORE this point stay painted;
                // the truncated row keeps whatever partial bytes existed
                // before EOF (the vendor paints the same partial stream —
                // it has no length arg and reads resident bytes).
                if (partialOk) return true;
                return false;
            }
            uint8_t C = img[i++];
            if (C == 0) break;
            if (C == 1) {
                if (i >= img.size()) {
                    if (partialOk) return true;
                    return false;
                }
                p += img[i++];  // transparent skip (dst untouched)
                continue;
            }
            uint32_t n = C >> 1;
            if (C & 1) {  // literal copy
                if (i + n > img.size()) {
                    // t423: copy the bytes that DO exist, then stop the
                    // walk (the vendor copies from resident memory; we
                    // only own the file — named seam on the past-EOF
                    // bytes themselves, not on the partial row).
                    if (!partialOk) return false;
                    while (i < img.size()) {
                        if (p < W) out[size_t(r) * outW + p] = img[i];
                        ++p;
                        ++i;
                    }
                    return true;
                }
                for (uint32_t k = 0; k < n; ++k, ++p) {
                    if (p < W) out[size_t(r) * outW + p] = img[i + k];
                }
                i += n;
            } else {  // run fill
                if (i + 1 > img.size()) {
                    if (partialOk) return true;
                    return false;
                }
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

bool ShapeLibrary::decode(int i, std::vector<uint8_t>& out,
                          bool* swapped) const {
    if (swapped) *swapped = false;
    if (i < 0 || i >= count()) return false;
    const Record& r = records_[i];
    // Dims sanity bound == the Python validator's (4096): FAIL-class
    // records carry garbage dim words (e.g. 1starmap rec0x1 = 0x7ffffdbb,
    // cos_star k40..k51 = 0) and must be REPORTED as decode failures,
    // never allocated against. t197: this clamp is KEPT even though the
    // span bound below was removed — it models the vendor's dims check,
    // our span bound modelled nothing that exists in the image.
    if (r.width == 0 || r.height == 0 || r.width > 4096 || r.height > 4096) {
        // CORNER-ANCHOR GATE FALLBACK (t367, shp.md S28; D1 ruling keep).
        // The canonical gate above models the vendor blit's -1 check and
        // stays FIRST and UNTOUCHED for every record that passes it —
        // measured t367: canonical dims == bbox-diff for only 3 of 1,313
        // valid k>=1 records, so a blanket signed-bbox dims read is REFUTED.
        // But mouse.shp k4..k7 are ONE 78x47 glyph at four screen-corner
        // anchors (t344 S27): k5/k6/k7 read (0,46)/(77,0)/(0,0) in the
        // unsigned pair because the slot holds half of a SIGNED bbox
        // (L,T,R,B at rec+0x08/0xc/0x10/0x14) whose negative half the
        // unsigned gate threw away. This fallback fires ONLY when the
        // canonical gate just failed AND the signed bbox is >=2x2 AND at
        // least one anchor component is negative. Measured corpus-wide it
        // admits EXACTLY mouse k5/k6/k7: cos_star k40..k51 (zero header,
        // 1x1, no negative), 1starmap k1 (no negative) and sg50expl k9
        // (1x1) all stay rejected, matching the vendor -1 gate (t328 S25).
        if (i >= 1 && r.start + 0x1c <= img_.size()) {
            const int32_t L = rd32s(img_, r.start + 0x08);
            const int32_t T = rd32s(img_, r.start + 0x0c);
            const int32_t Rr = rd32s(img_, r.start + 0x10);
            const int32_t B = rd32s(img_, r.start + 0x14);
            const int32_t BW = Rr - L + 1, BH = B - T + 1;
            if ((L < 0 || T < 0) && BW >= 2 && BH >= 2 && BW <= 4096 &&
                BH <= 4096) {
                out.assign(size_t(BW) * size_t(BH), 0);
                if (walkRows(img_, r.stream, uint32_t(BW), uint32_t(BH), out,
                             uint32_t(BW)))
                    return true;
                out.clear();
            }
        }
        return false;
    }
    if (out.size() < size_t(r.width) * r.height)
        out.resize(size_t(r.width) * r.height);
    // t423 PARTIAL: the LAST record of a library is the only one whose
    // stream can hit true EOF (3cfgnew k12, truncated IN the shipped
    // ascend01.cob blob — F5b). Paint the rows that walk; the vendor
    // paints resident bytes there, we own only the file (named seam).
    const bool partialOk = (i == count() - 1);
    // Canonical row count is the SECOND u32 of the dims pair (H);
    // orientation residue of the S16 residual class may store it first.
    // NO directory-span bound (t197, shp.md S20.2): the blit has no length
    // arg and the cache is verbatim whole-library, so records whose streams
    // legitimately cross the directory span (planind k0..k12, 3cfgnew
    // k0..k11, 14intel k8, 1starmap k3/k4/k6 — the X class) decode here.
    // Rows past the span desync into the next record's bytes and PAINT
    // (r1_t197_pastrows.py); whether any widget SHOWS those bands is the
    // paint-routine question owned by the gauge-library queue item, not a
    // decode-law question. Destination semantics unchanged either way.
    if (walkRows(img_, r.stream, r.width, r.height, out, r.width, partialOk))
        return true;
    if (r.width != r.height) {
        // Residual-class fallback (S16 [inferred]): swap the pair.
        std::vector<uint8_t> alt(out);
        if (walkRows(img_, r.stream, r.height, r.width, alt, r.height,
                     partialOk)) {
            out.swap(alt);
            if (swapped) *swapped = true;
            return true;
        }
    }
    // CORNER-ANCHOR GATE FALLBACK (t367, shp.md S28; D1 ruling keep). The
    // canonical dims gate above models the vendor blit's -1 check and stays
    // FIRST and UNTOUCHED for every record that passes it — measured t367:
    // canonical dims == bbox-diff for only 3 of 1,313 valid k>=1 records, so
    // a blanket signed-bbox dims read is REFUTED. But mouse.shp k4..k7 are
    // ONE 78x47 glyph at four screen-corner anchors (t344 S27): k5/k6/k7
    // store (0,46)/(77,0)/(0,0) in the unsigned pair because the slot holds
    // half of a SIGNED bbox (L,T,R,B at rec+0x08/0xc/0x10/0x14) whose
    // negative half the unsigned gate threw away. This fallback fires ONLY
    // when the canonical gate failed AND the signed bbox is >=2x2 AND at
    // least one anchor component is negative. Measured corpus-wide this
    // admits EXACTLY mouse k5/k6/k7: cos_star k40..k51 (zero header, 1x1,
    // no negative), 1starmap k1 (no negative), sg50expl k9 (1x1) and the
    // 16 expl-class walk-failures all stay rejected, matching the vendor's
    // -1 gate (t328 S25).
    if (i >= 1 && r.start + 0x1c <= img_.size()) {
        const int32_t L = rd32s(img_, r.start + 0x08);
        const int32_t T = rd32s(img_, r.start + 0x0c);
        const int32_t Rr = rd32s(img_, r.start + 0x10);
        const int32_t B = rd32s(img_, r.start + 0x14);
        const int32_t BW = Rr - L + 1, BH = B - T + 1;
        if ((L < 0 || T < 0) && BW >= 2 && BH >= 2 && BW <= 4096 && BH <= 4096) {
            std::vector<uint8_t> alt;
            alt.resize(size_t(BW) * size_t(BH));
            if (walkRows(img_, r.stream, uint32_t(BW), uint32_t(BH), alt,
                         uint32_t(BW))) {
                out.swap(alt);
                return true;
            }
        }
    }
    return false;
}

}  // namespace ascend::formats
