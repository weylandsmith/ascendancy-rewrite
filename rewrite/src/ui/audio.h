// SPDX-License-Identifier: GPL-3.0-or-later

#pragma once
#include <cstdint>
#include <string>
#include <unordered_map>
#include <vector>

#include "formats/voc.h"

// Mix_Chunk/Mix_Music come from the vendor header directly. Do NOT
// forward-declare them: the struct TAGS drifted between SDL2_mixer
// versions (2.8.0 declares `struct _Mix_Music`, 2.8.1 declares `struct
// Mix_Music`), so a hand-written tag compiles on one and conflicts on the
// other — measured on a user build, 2026-11-14.
#include <SDL_mixer.h>

namespace ascend::ui {
// SDL2_mixer over the vendor samples (docs/re/audio.md §5). One instance
// per process; dtor frees chunks + closes the device.
class AudioEngine {
  public:
    // Opens the device at 22050 Hz (MEASURED OQ-006: original open chain
    // 0x4f690/0x4f90b PUSH 22050 -> 0x68816 -> 0x6e000 stores [obj+0x3c];
    // constructor default 11025 at 0x6df3e is always overwritten), loads
    // every SFX from dataDir (ascend01/data) and theme00 music
    // (ascend02/data). `mute` loads everything but sets master volume 0.
    // Returns false with *err if the device or ANY referenced sample fails
    // (no fakery, §5).
    bool init(const std::string& dataDir, bool mute, std::string* err);
    void play(const std::string& sfxName);   // unknown name -> no-op
    void playMusic();                        // theme00, looping
    ~AudioEngine();

    int chunksLoaded() const { return int(chunks_.size()); }
    unsigned long musicBytes() const { return musicBytes_; }

  private:
    bool inited_ = false;
    std::unordered_map<std::string, Mix_Chunk*> chunks_;
    Mix_Music* music_ = nullptr;
    unsigned long musicBytes_ = 0;
    // Mix_LoadMUS_RW STREAMS from the RWops, so the wrapped WAV buffer must
    // outlive the music handle (an init()-local vector caused a use-after-
    // free segfault under the dummy driver; gate 4d caught it).
    std::vector<uint8_t> musicWav_;
};
}  // namespace ascend::ui
