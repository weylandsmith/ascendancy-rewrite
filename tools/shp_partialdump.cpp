// SPDX-License-Identifier: GPL-3.0-or-later

// shp_partialdump.cpp — t196 OQ-005 residue TRIAGE dumper (docs/re/_wip_t196.md).
//
// Why this exists: at t196 ShapeLibrary::decode() FAILed the 71 residue
// records (dims/stream walk incomplete within the span). t197 PROVED the span
// bound was our artifact (shp.md S21): decode() now walks span-free and 29 of
// those records decode fully, so THIS tool's remaining reason to exist is the
// 44-record residue (garbage dims words + EOF truncation) plus the paint
// profile that started the correction (span-exhaustion row prefixes).
// NO candidate
// search happens here (GOAL.txt / REFUTED-ROUTES R2): dims come from the same
// S16/S17 slots decode() reads, the stream start from the same uniform law,
// and the row grammar is VERBATIM from shp.cpp walkRows() (control bytes C:
// 0=end-row, 1=transparent skip, odd=literal copy n=C>>1, even=run fill).
// The ONLY difference from decode() is that the row loop runs until the span
// is exhausted instead of demanding exactly H terminating rows. Records whose
// dims word is not a valid W (>0, <=4096) are NOT rendered and NOT guessed —
// the err column says why (strict-close).
//
// Usage:  shp_partialdump <spec-file> <out-dir>
//   spec lines:  <library-path><TAB><record-index>
//   stdout:      <lib>\t<rec>\t<ok|fail>\t<W>\t<H>\t<rows_done>\t<avail>\t
//                <rawrelpath>\t<err>
// Planes are width x rows_done bytes -> <out-dir>/raw_p/<lib>--<rec>.idx
#include "formats/shp.h"

#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <string>
#include <vector>

namespace {

std::string basename_of(const std::string& p) {
    const size_t s = p.find_last_of('/');
    std::string b = s == std::string::npos ? p : p.substr(s + 1);
    const size_t dot = b.find_last_of('.');
    return dot == std::string::npos ? b : b.substr(0, dot);
}

// walkRows from rewrite/src/formats/shp.cpp:19, row loop changed to
// stop-at-exhaustion. Returns rows completed; `out` must be pre-sized to
// width * height_max; destination for skipped pixels stays zero-filled.
uint32_t walkRowsPartial(const std::vector<uint8_t>& img, uint32_t stream,
                         uint32_t end, uint32_t W, std::vector<uint8_t>& out) {
    size_t i = stream;
    uint32_t r = 0;
    for (;;) {
        if (i >= end) return r;  // span exhausted: partial frame, honest stop
        uint32_t p = 0;
        for (;;) {
            if (i >= end) return r;      // row cut mid-op: discard partial row
            uint8_t C = img[i++];
            if (C == 0) break;
            if (C == 1) {
                if (i >= end) return r;
                p += img[i++];
                continue;
            }
            uint32_t n = C >> 1;
            if (C & 1) {  // literal copy
                if (i + n > end) return r;
                for (uint32_t k = 0; k < n; ++k, ++p) {
                    if (p < W && r < out.size() / (W ? W : 1))
                        out[size_t(r) * W + p] = img[i + k];
                }
                i += n;
            } else {  // run fill
                if (i + 1 > end) return r;
                uint8_t v = img[i++];
                for (uint32_t k = 0; k < n; ++k, ++p) {
                    if (p < W && r < out.size() / (W ? W : 1))
                        out[size_t(r) * W + p] = v;
                }
            }
        }
        ++r;
    }
}

}  // namespace

int main(int argc, char** argv) {
    if (argc != 3) {
        std::fprintf(stderr, "usage: %s <spec-file> <out-dir>\n", argv[0]);
        return 2;
    }
    std::ifstream in(argv[1]);
    if (!in) {
        std::fprintf(stderr, "cannot open spec %s\n", argv[1]);
        return 2;
    }
    const std::string outdir = argv[2];
    std::string line;
    size_t n_ok = 0, n_fail = 0;
    while (std::getline(in, line)) {
        if (line.empty()) continue;
        const size_t tab = line.find('\t');
        if (tab == std::string::npos) {
            std::fprintf(stderr, "bad spec line: %s\n", line.c_str());
            continue;
        }
        const std::string lib = line.substr(0, tab);
        const int rec = std::atoi(line.c_str() + tab + 1);

        ascend::formats::ShapeLibrary shape;
        std::string err;
        if (!shape.load(lib, &err)) {
            std::printf("%s\t%d\tfail\t0\t0\t0\t0\t\tcontainer: %s\n",
                        lib.c_str(), rec, err.c_str());
            ++n_fail;
            continue;
        }
        const ascend::formats::ShapeLibrary::Record& r = shape.record(rec);
        const uint32_t avail =
            r.end > r.stream ? r.end - r.stream : 0u;  // stream bytes in span
        if (r.width == 0 || r.width > 4096) {
            std::printf("%s\t%d\tfail\t%u\t%u\t0\t%u\t\tno-dims-word "
                        "(W=%u invalid; not guessed)\n",
                        lib.c_str(), rec, r.width, r.height, avail, r.width);
            ++n_fail;
            continue;
        }
        if (avail == 0) {
            std::printf("%s\t%d\tfail\t%u\t%u\t0\t0\t\tEMPTY slot "
                        "(zero stream bytes in span 0x%x)\n",
                        lib.c_str(), rec, r.width, r.height,
                        unsigned(r.end - r.start));
            ++n_fail;
            continue;
        }
        // Plane sized to the DECLARED frame; the walk stops at exhaustion so
        // rows beyond rows_done stay index-0 (honest underlay for the sheet).
        // mouse-class records carry H==0 with a real stream: cap the plane at
        // 512 rows; rows_done reports what the span actually held.
        const uint32_t hmax = r.height ? r.height : 512u;
        std::vector<uint8_t> out(size_t(r.width) * hmax, 0);
        // NOTE: ShapeLibrary keeps the image private; re-read it here so the
        // walk sees the same bytes the decoder sees (container parse and
        // stream/dims slots are the library's own).
        std::ifstream f(lib, std::ios::binary | std::ios::ate);
        std::vector<uint8_t> img(size_t(f.tellg()));
        f.seekg(0);
        f.read(reinterpret_cast<char*>(img.data()),
               std::streamsize(img.size()));
        f.close();
        std::fill(out.begin(), out.end(), uint8_t(0));
        const uint32_t rows_done =
            walkRowsPartial(img, r.stream, r.end, r.width, out);
        const uint32_t plane_rows = rows_done ? rows_done : 1u;
        const std::string rel =
            "raw_p/" + basename_of(lib) + "--" + std::to_string(rec) + ".idx";
        const std::string full = outdir + "/" + rel;
        std::ofstream po(full, std::ios::binary | std::ios::trunc);
        if (!po) {
            std::printf("%s\t%d\tfail\t%u\t%u\t%u\t%u\t\twrite failed %s\n",
                        lib.c_str(), rec, r.width, r.height, rows_done, avail,
                        full.c_str());
            ++n_fail;
            continue;
        }
        po.write(reinterpret_cast<const char*>(out.data()),
                 std::streamsize(size_t(r.width) * plane_rows));
        po.close();
        std::printf("%s\t%d\tok\t%u\t%u\t%u\t%u\t%s\t\n", lib.c_str(), rec,
                    r.width, r.height, rows_done, avail, rel.c_str());
        ++n_ok;
    }
    std::fprintf(stderr, "shp_partialdump: ok=%zu fail=%zu\n", n_ok, n_fail);
    return 0;
}
