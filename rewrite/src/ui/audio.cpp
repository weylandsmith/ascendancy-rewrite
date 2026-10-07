#include "ui/audio.h"

#include <SDL_mixer.h>

#include <cctype>
#include <cstdio>
#include <cstring>
#include <vector>

namespace ascend::ui {
namespace af = ascend::formats;

namespace {
// SDL2_mixer has no raw-PCM loader; wrap vendor PCM in a minimal RIFF WAV
// in memory (docs/re/audio.md §5). u8 mono/stereo PCM.
std::vector<uint8_t> wrapWav(const af::Sample& s) {
    std::vector<uint8_t> w;
    auto put32 = [&](uint32_t v) {
        w.push_back(v & 0xFF); w.push_back((v >> 8) & 0xFF);
        w.push_back((v >> 16) & 0xFF); w.push_back((v >> 24) & 0xFF);
    };
    auto put16 = [&](uint16_t v) {
        w.push_back(v & 0xFF); w.push_back((v >> 8) & 0xFF);
    };
    const uint32_t dataLen = uint32_t(s.pcm.size());
    w.insert(w.end(), {'R', 'I', 'F', 'F'});
    put32(36 + dataLen);
    w.insert(w.end(), {'W', 'A', 'V', 'E', 'f', 'm', 't', ' '});
    put32(16);
    put16(1);                                   // PCM
    put16(s.channels);
    put32(s.rate);
    put32(s.rate * s.channels);                 // byte rate (u8 samples)
    put16(uint16_t(s.channels));                // block align
    put16(8);                                   // bits
    w.insert(w.end(), {'d', 'a', 't', 'a'});
    put32(dataLen);
    w.insert(w.end(), s.pcm.begin(), s.pcm.end());
    return w;
}
}  // namespace

bool AudioEngine::init(const std::string& dataDir, bool mute,
                       std::string* err) {
    // MEASURED rate law (OQ-006 CLOSED 2026-10-07): the original opens
    // audio at 22050 Hz. Chain in ascend_payload.bin: PUSH 0x5622 (22050)
    // at 0x4f690 and 0x4f90b -> CALL 0x68816 (audio-open wrapper, forwards
    // at 0x68882 -- its ONLY call edge) -> 0x6e000 rate setter, which
    // stores the argument at [audioObj+0x3c]. The constructor default at
    // 0x6df3e is 11025 ([EAX+0x3c]=0x2b11), overwritten by both open sites
    // -- so headerless samples play at 22050 (docs/re/audio.md §3).
    // Channel count has no setter in this chain (0x44/+0x40 hold buffer
    // size/volume plumbing), so stereo below remains a rewrite choice.
    if (Mix_OpenAudio(22050, MIX_DEFAULT_FORMAT, 2, 512) != 0) {
        if (err) *err = std::string("Mix_OpenAudio: ") + Mix_GetError();
        return false;
    }
    inited_ = true;
    Mix_Volume(-1, mute ? 0 : MIX_MAX_VOLUME);

    std::string merr;
    const std::string manifest = dataDir + "/extracted/ascend00/soundfx.txt";
    auto names = af::loadSoundfxManifest(manifest, &merr);
    if (names.empty()) {
        if (err) *err = merr;
        return false;
    }
    for (const auto& n : names) {
        if (chunks_.count(n)) continue;  // 'shield' is listed twice (§1)
        // Names are mixed-case in the manifest; on-disk files are lowercase.
        std::string lower = n;
        for (auto& c : lower) c = char(std::tolower(c));
        const std::string path = dataDir + "/extracted/ascend01/data/" + lower + ".voc";
        af::Sample s;
        if (!af::loadSample(path, n, &s, &merr)) {
            if (err) *err = merr;
            return false;
        }
        auto wav = wrapWav(s);
        SDL_RWops* rw = SDL_RWFromConstMem(wav.data(), int(wav.size()));
        Mix_Chunk* ch = Mix_LoadWAV_RW(rw, 1);  // 1: closes rw
        if (!ch) {
            if (err) *err = "Mix_LoadWAV " + n + ": " + Mix_GetError();
            return false;
        }
        chunks_.emplace(n, ch);
    }

    const std::string theme = dataDir + "/extracted/ascend02/data/theme00.raw";
    // Track 0 is MEASURED-correct for every captured game state: the global
    // tune selector DAT_00010ba0 (image) has exactly one writer (0x21309,
    // writes -1 under an option check) and reads 0 in all banked saves
    // (ck005/ck010 x5 runs); 0 == music.txt track 0 == theme00.raw.
    // Residue: the 0x1d4d0 span check in FUN_00059c70 vs theme00 span
    // 8,191,719 — see docs/re/audio.md §3.3 (chunked-read hypothesis).
    af::Sample ms;
    if (!af::loadSample(theme, "theme00", &ms, &merr)) {
        if (err) *err = merr;
        return false;
    }
    musicBytes_ = ms.pcm.size();
    musicWav_ = wrapWav(ms);  // member: music streams from this (see .h)
    SDL_RWops* rw = SDL_RWFromConstMem(musicWav_.data(), int(musicWav_.size()));
    music_ = Mix_LoadMUS_RW(rw, 1);
    if (!music_) {
        if (err) *err = std::string("Mix_LoadMUS theme00: ") + Mix_GetError();
        return false;
    }
    return true;
}

void AudioEngine::play(const std::string& sfxName) {
    auto it = chunks_.find(sfxName);
    if (it != chunks_.end()) Mix_PlayChannel(-1, it->second, 0);
}

void AudioEngine::playMusic() {
    if (music_ && !Mix_PlayingMusic()) Mix_PlayMusic(music_, -1);
}

AudioEngine::~AudioEngine() {
    if (music_) Mix_FreeMusic(music_);
    for (auto& kv : chunks_) Mix_FreeChunk(kv.second);
    if (inited_) Mix_CloseAudio();
}

}  // namespace ascend::ui
