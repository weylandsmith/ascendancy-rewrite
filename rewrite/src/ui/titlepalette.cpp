// SPDX-License-Identifier: GPL-3.0-or-later
#include "ui/titlepalette.h"

#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <sstream>

#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif

namespace ascend::ui {

namespace {
bool tryTsv(const std::string& path, TitlePalette* out, std::string* err) {
    std::ifstream f(path);
    if (!f) return false;
    std::string line;
    int rows = 0;
    while (std::getline(f, line)) {
        if (line.empty() || line[0] == '#') continue;
        // format: index \t r,g,b (gif GCT) \t r,g,b (vendor shot)
        std::istringstream ss(line);
        std::string a, b, c;
        if (!(std::getline(ss, a, '\t') && std::getline(ss, b, '\t') &&
              std::getline(ss, c)))
            continue;
        const int idx = std::atoi(a.c_str());
        if (idx < 0 || idx > 255) continue;
        // vendor-shot rgb is the THIRD field: "r,g,b"
        int r = 0, g = 0, bl = 0;
        const char* p = c.c_str();
        r = std::atoi(p);
        while (*p && *p != ',') p++;
        if (*p == ',') p++;
        g = std::atoi(p);
        while (*p && *p != ',') p++;
        if (*p == ',') p++;
        bl = std::atoi(p);
        out->rgb[idx][0] = uint8_t(r);
        out->rgb[idx][1] = uint8_t(g);
        out->rgb[idx][2] = uint8_t(bl);
        out->mapped[idx] = true;
        rows++;
    }
    if (rows == 0) {
        if (err) *err = "titlepalette: no rows in " + path;
        return false;
    }
    return true;
}
}  // namespace

bool TitlePalette::load(const std::string& dataRoot, const uint8_t* gct,
                        size_t gctLen, std::string* err) {
    for (int i = 0; i < 256; i++) {
        mapped[i] = false;
        const size_t o = size_t(i) * 3;
        rgb[i][0] = o + 2 < gctLen ? gct[o] : 0;
        rgb[i][1] = o + 2 < gctLen ? gct[o + 1] : 0;
        rgb[i][2] = o + 2 < gctLen ? gct[o + 2] : 0;
    }
    const std::string rel = "/rewrite/tests/data/title_palette_t386.tsv";
    if (tryTsv(std::string(ASCENDANCY_SOURCE_DIR) + rel, this, err) ||
        tryTsv(dataRoot + "/../rewrite/tests/data/title_palette_t386.tsv",
               this, err))
        return true;
    // No TSV at all: the whole table is GCT fallback. The caller decides
    // whether that is acceptable; we report honestly.
    if (err) *err = "titlepalette: title_palette_t386.tsv not found";
    return false;
}

}  // namespace ascend::ui
