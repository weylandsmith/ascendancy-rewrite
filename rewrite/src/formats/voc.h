#pragma once
#include <cstdint>
#include <string>
#include <vector>

namespace ascend::formats {
// Vendor sample container. Spec: docs/re/audio.md §2,§3. Two shapes:
//  - headered .voc (15 files): magic "Creative Voice File\0" + vendor block;
//    rate/bits/channels explicit; PCM = bytes 42..EOF-1 (trailing 0x00).
//  - headerless .voc/.raw (77+29 files): pure PCM; default 22050 mono
//    (OQ-006), same trailing-0x00 convention is NOT assumed for .raw.
struct Sample {
    std::string name;        // manifest name, verbatim
    uint32_t rate = 22050;   // headered: header value; else default (§3)
    uint8_t channels = 1;
    std::vector<uint8_t> pcm;  // 8-bit unsigned, 0x80 = silence
};

// Parses one file. Unknown magic-with-garbage -> false with *err.
bool loadSample(const std::string& path, const std::string& name,
                Sample* out, std::string* err);

// soundfx.txt manifest: skips 3 header pairs + the count line (§1).
std::vector<std::string> loadSoundfxManifest(const std::string& path,
                                             std::string* err);

// music.txt manifest: "data\<name>.raw" lines (§4), returns basenames.
std::vector<std::string> loadMusicManifest(const std::string& path,
                                           std::string* err);
}  // namespace ascend::formats
