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
