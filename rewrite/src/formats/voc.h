// SPDX-License-Identifier: GPL-3.0-or-later

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

// MEASURED voice-band law (OQ-018 audio part, docs/re/audio.md §3.2
// "HEADER-PAIR LAW, FINAL"): the vendor picks the sound's voice band by
// FILE SIZE against the soundfx.txt col2 thresholds (2 10000 / 3 45000 /
// 1 65000) — band = number of thresholds <= size, and a size >= the top
// threshold is a vendor error (FUN_000500e0 do-loop -> FUN_0002a428).
// Span table identity proven on live RAM (capture ck005: 327/328 file
// spans == disk sizes). Returns 0/1/2, or -1 for would-error sizes.
inline int voiceBand(uint32_t size) {
    if (size < 10000u) return 0;
    if (size < 45000u) return 1;
    if (size < 65000u) return 2;
    return -1;
}

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
