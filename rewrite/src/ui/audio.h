// SPDX-License-Identifier: GPL-3.0-or-later
// t388b SOUND FIDELITY (D9). Formats + rate law: docs/re/audio.md §1-§5.
// Music-track law (which tune plays where) + volume law: docs/re/audio.md §6.
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
// t388b VOLUME LAW (docs/re/audio.md §6, MEASURED): the vendor music-volume
// setter FUN_0004feec @0x4feec stores the byte ONLY when -1 < v <= 0x7f
// (out-of-range silently dropped — no clamp), then pokes the device via
// 0x6888c. Scale 0..127.
constexpr int kVendorVolMax = 127;
inline bool vendorVolumeOk(int v) { return v > -1 && v <= kVendorVolMax; }

// SDL2_mixer over the vendor samples (docs/re/audio.md §5,§6). One instance
// per process; dtor frees chunks + music + closes the device.
class AudioEngine {
  public:
    // Opens the device at 22050 Hz (MEASURED OQ-006: original open chain
    // 0x4f690/0x4f90b PUSH 22050 -> 0x68816 -> 0x6e000 stores [obj+0x3c];
    // constructor default 11025 at 0x6df3e is always overwritten), loads
    // every SFX from dataDir (ascend01/data) plus the CITED music tunes
    // (trackNames()). `mute` loads everything but sets master volume 0.
    // Returns false with *err if the device or ANY referenced sample fails
    // (no fakery, §5). Callers must treat false as silent-degrade, NEVER
    // abort the app (CI has no sound card; main.cpp owns that law).
    bool init(const std::string& dataDir, bool mute, std::string* err);
    void play(const std::string& sfxName);   // unknown name -> no-op

    // The loaded tune table in playTune() index order (music.txt basenames,
    // lowercase, no extension). Members are cited law only — see the .cpp.
    static const std::vector<std::string>& trackNames();
    // Plays tune #t. SWITCH law: the intro script fires DIGITALMUSIC twice
    // (subtitle.txt TUNEID 6 at FRAMENUMBER 20, TUNEID 7 at 988), so a
    // request for a different tune stops the current one first;
    // re-requesting the current tune is a no-op (never restarts). t == -1
    // stops music (vendor TUNEID -1 -> FUN_00067b85 stop path, audio.md §6).
    // Index law is STATIC (trackNames): the state machine is identical with
    // or without a device — headless-testable.
    void playTune(int t);
    void playMusic() { playTune(0); }  // theme00, looping (captured law §3.3)
    int currentTune() const { return currentTune_; }

    // Vendor-scale music volume (0..127). Out-of-range values are DROPPED
    // exactly like FUN_0004feec — no clamp.
    void setMusicVolume(int vendorScale);
    int musicVolume() const { return musicVol_; }

    // Headless-safe instrument: prints one "sfx <name>" / "music N <name>"
    // line per played sound (--audio-trace). Wiring is machine-verified;
    // hearing stays the USER's grade (R13).
    void setTrace(bool on) { trace_ = on; }

    ~AudioEngine();

    int chunksLoaded() const { return int(chunks_.size()); }
    unsigned long musicBytes() const { return musicBytes_; }  // tune 0 bytes
    int tunesLoaded() const { return int(music_.size()); }

  private:
    bool inited_ = false;
    bool trace_ = false;
    int currentTune_ = -1;
    int musicVol_ = kVendorVolMax;  // vendor constructor state: full scale
    std::unordered_map<std::string, Mix_Chunk*> chunks_;
    std::vector<Mix_Music*> music_;
    unsigned long musicBytes_ = 0;
    // Mix_LoadMUS_RW STREAMS from the RWops, so EVERY wrapped WAV buffer
    // must outlive its music handle (an init()-local vector caused a
    // use-after-free segfault under the dummy driver; gate 4d caught it).
    std::vector<std::vector<uint8_t>> musicWavs_;
};
}  // namespace ascend::ui
