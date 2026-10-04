#include "formats/voc.h"

#include <cstdlib>
#include <cstring>
#include <fstream>
#include <sstream>

namespace ascend::formats {

namespace {
constexpr char kMagic[] = "Creative Voice File";  // 19 chars, then 0x1A 0x1A
uint32_t le32(const uint8_t* p) {
    return uint32_t(p[0]) | uint32_t(p[1]) << 8 | uint32_t(p[2]) << 16 |
           uint32_t(p[3]) << 24;
}
}  // namespace

bool loadSample(const std::string& path, const std::string& name,
                Sample* out, std::string* err) {
    std::ifstream f(path, std::ios::binary | std::ios::ate);
    if (!f) {
        if (err) *err = "cannot open " + path;
        return false;
    }
    const auto size = size_t(f.tellg());
    f.seekg(0);
    std::vector<uint8_t> d(size);
    f.read(reinterpret_cast<char*>(d.data()), std::streamsize(size));
    out->name = name;
    out->rate = 22050;   // docs/re/audio.md §3 default (OQ-006)
    out->channels = 1;
    if (size >= 42 && std::memcmp(d.data(), kMagic, 19) == 0 &&
        d[19] == 0x1A) {
        // Headered vendor block (audio.md §2). Invariants on all 15 files:
        // ver@20==26, type@24==0x1F, len@27==size-31, bits@34==8.
        if (d[20] != 26 || d[24] != 0x1F || d[34] != 8) {
            if (err) *err = "unexpected vendor VOC header fields in " + path;
            return false;
        }
        out->rate = le32(&d[30]);
        out->channels = d[35];
        // PCM = bytes 42..EOF-1 (trailing 0x00 terminator, §2).
        out->pcm.assign(d.begin() + 42, d.end() - 1);
        return true;
    }
    // Headerless PCM (§3): whole file is samples. No terminator convention
    // is claimed for .raw, so we take the full bytes and let the mixer
    // handle the click; the 77 .voc all end 0x00 but that equals silence
    // anyway, so dropping one byte would be a cosmetic difference.
    out->pcm = std::move(d);
    return true;
}

std::vector<std::string> loadSoundfxManifest(const std::string& path,
                                             std::string* err) {
    std::ifstream f(path);
    if (!f) {
        if (err) *err = "cannot open " + path;
        return {};
    }
    // §1: three "N NNNNN" header lines, then the literal count, then names.
    std::vector<std::string> lines, all;
    std::string ln;
    while (std::getline(f, ln)) {
        if (!ln.empty() && ln.back() == '\r') ln.pop_back();
        if (!ln.empty()) all.push_back(ln);
    }
    if (all.size() < 5) {
        if (err) *err = "soundfx.txt too short";
        return {};
    }
    const int count = std::atoi(all[3].c_str());
    for (size_t i = 4; i < all.size() && int(lines.size()) < count; i++)
        lines.push_back(all[i]);
    return lines;
}

std::vector<std::string> loadMusicManifest(const std::string& path,
                                           std::string* err) {
    std::ifstream f(path);
    if (!f) {
        if (err) *err = "cannot open " + path;
        return {};
    }
    std::vector<std::string> out;
    std::string ln;
    while (std::getline(f, ln)) {
        if (!ln.empty() && ln.back() == '\r') ln.pop_back();
        const auto sep = ln.find_last_of("\\/");
        if (sep == std::string::npos || sep + 1 >= ln.size()) continue;
        out.push_back(ln.substr(sep + 1));
    }
    return out;
}

}  // namespace ascend::formats
