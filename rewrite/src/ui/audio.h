#pragma once
#include <cstdint>
#include <string>
#include <unordered_map>
#include <vector>

#include "formats/voc.h"

struct Mix_Chunk;  // SDL_mixer.h:231 defines it as struct; tag must match
struct Mix_Music;  // SDL_mixer.h:269

namespace ascend::ui {
// SDL2_mixer over the vendor samples (docs/re/audio.md §5). One instance
// per process; dtor frees chunks + closes the device.
class AudioEngine {
  public:
    // Opens the device (rate 22050 per OQ-006 default), loads every SFX
    // from dataDir (ascend01/data) and theme00 music (ascend02/data).
    // `mute` loads everything but sets master volume 0. Returns false with
    // *err if the device or ANY referenced sample fails (no fakery, §5).
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
