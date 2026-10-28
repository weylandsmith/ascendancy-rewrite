// shp_pngdump.cpp — t182 OQ-005 evidence driver (docs/BLOCKED.md t68,
// docs/re/shp.md S16/S17, docs/STATE.md t182).
//
// Purpose: run the REWRITE'S OWN decoder (ascend::formats::ShapeLibrary,
// rewrite/src/formats/shp.{h,cpp}) over a list of (library, record) pairs and
// dump the decoded palette-index plane as raw bytes for the Python front-end
// scripts/r1_t182_pngdump.py to PNG-encode. Using the library rather than a
// re-implemented walk is deliberate: the evidence must show what the rewrite
// would actually draw, not what a second independent implementation guesses.
//
// NO candidate search happens here (GOAL.txt: a 7th blind .shp codec sweep is
// FORBIDDEN; docs/REFUTED-ROUTES.md R2). Dims come from the S16/S17 V/A slots
// and the stream start from the uniform law — decode() returns false for the
// residue records whose dims are uninterpretable, and the tool REPORTS that
// rather than inventing a frame (strict-close policy).
//
// Usage:
//   shp_pngdump <spec-file> <out-dir>
//   spec-file lines:  <library-path><TAB><record-index>
//   stdout:            <library-path>\t<rec>\t<ok|fail>\t<W>\t<H>\t<stride>\t
//                      <swapped01>\t<rawrelpath>\t<err>
// Raw planes are written to <out-dir>/raw/<lib>--<rec>.idx.
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
    const std::string rawdir = outdir + "/raw";
    // mkdir -p-ish: the Python front-end creates outdir/raw first; if it did
    // not, we simply fail that record's write and say so in the err column.
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
        std::vector<uint8_t> plane;
        bool swapped = false;
        const bool ok = shape.decode(rec, plane, &swapped);
        const ascend::formats::ShapeLibrary::Record& r = shape.record(rec);
        if (!ok) {
            std::printf("%s\t%d\tfail\t%u\t%u\t0\t0\t\tdims/stream rejected "
                        "or walk incomplete in span 0x%x\n",
                        lib.c_str(), rec, r.width, r.height,
                        unsigned(r.end - r.start));
            ++n_fail;
            continue;
        }
        // Stride: canonical walk writes height rows of stride width;
        // the swapped fallback writes width rows of stride height
        // (see shp.h decode() contract).
        const uint32_t stride = swapped ? r.height : r.width;
        const std::string rel =
            "raw/" + basename_of(lib) + "--" + std::to_string(rec) + ".idx";
        const std::string full = outdir + "/" + rel;
        std::ofstream out(full, std::ios::binary | std::ios::trunc);
        if (!out) {
            std::printf("%s\t%d\tfail\t%u\t%u\t%u\t%d\t\twrite failed %s\n",
                        lib.c_str(), rec, r.width, r.height, stride,
                        int(swapped), full.c_str());
            ++n_fail;
            continue;
        }
        out.write(reinterpret_cast<const char*>(plane.data()),
                  std::streamsize(plane.size()));
        out.close();
        std::printf("%s\t%d\tok\t%u\t%u\t%u\t%d\t%s\t\n", lib.c_str(), rec,
                    r.width, r.height, stride, int(swapped), rel.c_str());
        ++n_ok;
    }
    std::fprintf(stderr, "shp_pngdump: ok=%zu fail=%zu\n", n_ok, n_fail);
    return 0;
}
