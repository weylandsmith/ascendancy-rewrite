// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
// game.pal — THE in-game palette (t398 palette-fidelity law).
//
// LAW [verified t398]: the vendor loads DATA\game.pal by name — the exe
// payload carries the NUL-delimited template "DATA\game.pal" at two sites
// (work/ascend_payload.bin 0x83579 in the corn.cpp title/init cluster beside
// resume.gam/0OPENING.GIF, and 0x84207 in the flicwin/font cluster). The
// file is 768 B = 256 RGB triples, every channel <= 0x3f (6-bit VGA DAC).
// DOSBox converts 6->8 bit as c = (v<<2)|(v>>4) (the standard VGA saturating
// law; t189b measured that raw 6-bit values rendered everything at 25%
// brightness, and the *4-scaled render passed the player's look check).
//
// DECISIVE WITNESS (docs/re/_wip_t398.md S2..S5): every pixel of the pinned
// in-game refcap shots (strategic map / species research / planet view) lies
// inside this table under that conversion (307200/307200 px, three shots),
// while the title screen lies inside it only at 8.79% (the title is a
// DIFFERENT palette — the t386 TSV, docs/re/title-art.md §4). The rail icon
// records 1starmap k3/k4/k5/k7 register against the pinned shot at the cited
// kRail rects through THIS table (mean |RGB diff| 3..6 of 765 for k3/k4/k5,
// 93..97% of pixels within 12; k7 = 36 with position exact — its flare is
// partly overpainted by the Intelligence row's fill overlap). The menu chrome
// is painted through game.pal; the t387 luminance ramp was the "greyscale
// art" defect (D11).
#include <cstdint>
#include <string>
#include <vector>

namespace ascend::formats {

class GamePalette {
  public:
    static constexpr int kSize = 256;

    // Loads DATA\game.pal (exactly 768 bytes; refuses anything else —
    // refuse-not-clamp). Returns false + *err on missing/short/long file.
    bool load(const std::string& path, std::string* err);

    // In-memory entry (house style) so law rejection is testable without
    // the filesystem. Same 768-byte rule.
    bool parse(std::vector<uint8_t> bytes, std::string* err);

    // 8-bit RGB after the DOSBox 6->8 conversion c=(v<<2)|(v>>4).
    void rgb(int index, uint8_t out[3]) const;

    // ARGB8888 (alpha 255) in host byte order as SDL_PIXELFORMAT_ARGB8888
    // expects it.
    uint32_t argb(int index) const;

    bool ready() const { return loaded_; }

  private:
    uint8_t conv_[kSize * 3] = {};  // already 6->8 converted
    bool loaded_ = false;
};

}  // namespace ascend::formats
