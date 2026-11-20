// SPDX-License-Identifier: GPL-3.0-or-later

#include "ui/audio.h"

#include <SDL_mixer.h>

#include <cctype>
#include <cstdio>
#include <cstring>
#include <vector>

namespace ascend::ui {
namespace af = ascend::formats;

// t437 VENDOR CLICK-SFX LAW (see audio.h; audio.md §6.9, trail
// docs/re/_wip_t437.md F1-F6). MEASURED, replaces the t404 port choice:
// the windows.txt parser fn 0x575e4 stores the SOUNDCHANNEL line as
// mov WORD [rec+0x59],ax (0x57e7a) — the HIWORD of dword[rec+0x57] — and the
// strategic-window press handler plays exactly that value
// (mov edx,[esi+0x57]; sar edx,0x10; cmp edx,-1; je skip -> 0x4fb30 ->
// FUN_000500e0, site 0x30e75 inside the X0/Y0/X1/Y1 rect hit-test).
// SOUNDCHANNEL is 0 on all 119 file lines (file census) and +0x59 == 0 on all
// 2,400 file-declared window records in 20 saves (scripts/
// t437_soundchannel_store_census.py); manifest[0] == "button". So every
// file-declared button (rail, NEXTTURN, title, planet panels) plays
// soundfx.txt manifest[0] "button"; -1 (COSMOSWnd/BatModeWnd/INTROFLIC/
// WMGRDEBUG — runtime windows with no windows.txt block) is silent.
// MapClick therefore stays nullptr: the map surface is COSMOSWnd, +0x59 == -1
// in 20/20 saves => the vendor map click is SILENT (now cited, was assumed).
const char* sfxForPress(UiPressSite site) {
    switch (site) {
        case UiPressSite::MapClick:    return nullptr;   // COSMOSWnd -1 silent
        case UiPressSite::RailButton:  return "button";  // manifest[0]
        case UiPressSite::NextTurn:    return "button";  // NEXTTURN SC=0
        case UiPressSite::TitleButton: return "button";  // INTRO/RESUME SC=0
    }
    return nullptr;
}

// t404: the one event sound the port plays. audio.md §5 documents bang01 on
// a new event line containing "captured" (names verbatim from soundfx.txt);
// every other event text is silent — the vendor table names no id (§6.6).
const char* sfxForEvent(const std::string& eventText) {
    return eventText.find("captured") != std::string::npos ? "bang01"
                                                           : nullptr;
}

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

const std::vector<std::string>& AudioEngine::trackNames() {
    // LOADED tune table (playTune index order). Members of the music.txt
    // manifest (29 entries) chosen by CITED law only:
    //  0 theme00  == music.txt track 0 == the value the captured global
    //    selector DAT_00010ba0 holds in ALL banked saves (audio.md §3.3,
    //    §3.4 closed "engine unreachable in captured states").
    //  1 intro00  2 intro01  -- the intro-movie script law: subtitle.txt
    //    DIGITALMUSIC/TUNEID 6 at FRAMENUMBER 20 and TUNEID 7 at 988, with
    //    the FADEMUSIC dip 100->30 at frames 966-981 and VOLUME 127 restore
    //    at 988 (audio.md §6). TUNEID IS ZERO-BASED into the vendor's 29-
    //    entry music.txt-order table -- MEASURED t440 (index law 0x4f929..
    //    0x4f945 obj+0x37a+tuneid*28; table read from banked saves 20/20,
    //    scripts/t440_music_table.py): vendor 6 = intro00, vendor 7 =
    //    intro01. This vector is the port's OWN loaded subset; the cue
    //    table in ui.cpp translates vendor ids 6/7 to indices 1/2.
    // The race00..20 themes stay UNLOADED: the race->theme selector never
    // materialised in any capture (OQ-018 residue, §3.3) — named seam.
    static const std::vector<std::string> kNames{"theme00", "intro00",
                                                 "intro01"};
    return kNames;
}

bool AudioEngine::init(const std::string& dataDir, bool mute,
                       std::string* err) {
    // MEASURED rate law (OQ-006 CLOSED 2026-10-07): the original opens
    // audio at 22050 Hz. Chain in ascend_payload.bin: PUSH 0x5622 (22050)
    // at 0x4f690 and 0x4f90b -> CALL 0x68816 (audio-open wrapper, forwards
    // at 0x68882 -- its ONLY call edge) -> 0x6e000 rate setter, which
    // stores the argument at [audioObj+0x3c]. The constructor default at
    // 0x6df3e is 11025 ([EAX+0x3c]=0x2b11), overwritten by both open sites
    // -- so headerless samples play at 22050 (docs/re/audio.md §3).
    // Channel count has no setter in this chain (0x44/+0x44 hold buffer
    // size/volume plumbing), so stereo below remains a rewrite choice.
    if (Mix_OpenAudio(22050, MIX_DEFAULT_FORMAT, 2, 512) != 0) {
        if (err) *err = std::string("Mix_OpenAudio: ") + Mix_GetError();
        return false;
    }
    inited_ = true;
    Mix_Volume(-1, mute ? 0 : MIX_MAX_VOLUME);

    std::string merr;
    const std::string manifest = dataDir + "/extracted/ascend00/soundfx.txt";
    triedPaths_.push_back(manifest);  // t395 diagnostic
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
        triedPaths_.push_back(path);  // t395 diagnostic
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
    // t395 ROOT CAUSE for D10 silence: click08.voc EXISTS in ascend01/data
    // but is NOT listed in soundfx.txt (manifest = 86 names; the data dir
    // holds more samples than it names — MEASURED: ls + grep of the
    // manifest). The campaign map's play("click08") was therefore a silent
    // no-op on every build since t388. Load the referenced-but-unlisted
    // vendor sample explicitly; a missing file fails init (named path) like
    // any other sample.
    for (const char* extra : {"click08"}) {
        if (chunks_.count(extra)) continue;
        const std::string path = dataDir + "/extracted/ascend01/data/";
        const std::string xpath = path + extra + ".voc";
        triedPaths_.push_back(xpath);  // t395 diagnostic
        af::Sample s;
        if (!af::loadSample(xpath, extra, &s, &merr)) {
            if (err) *err = merr;
            return false;
        }
        auto wav = wrapWav(s);
        SDL_RWops* rw = SDL_RWFromConstMem(wav.data(), int(wav.size()));
        Mix_Chunk* ch = Mix_LoadWAV_RW(rw, 1);
        if (!ch) {
            if (err) *err = std::string("Mix_LoadWAV ") + extra + ": " + Mix_GetError();
            return false;
        }
        chunks_.emplace(extra, ch);
    }

    // Music: load the cited tune table (trackNames above). theme00 lives in
    // ascend02/data; the intro pair lives in ascend01/data (music.txt paths
    // name both archives' members flattened — audio.md §4).
    for (size_t t = 0; t < trackNames().size(); t++) {
        const std::string& tune = trackNames()[t];
        const std::string a02 = dataDir + "/extracted/ascend02/data/" + tune + ".raw";
        const std::string a01 = dataDir + "/extracted/ascend01/data/" + tune + ".raw";
        triedPaths_.push_back(a02); triedPaths_.push_back(a01);  // t395
        std::string path;
        if (FILE* probe = std::fopen(a02.c_str(), "rb")) {
            std::fclose(probe); path = a02;
        } else if (FILE* probe = std::fopen(a01.c_str(), "rb")) {
            std::fclose(probe); path = a01;
        } else {
            // t395: name BOTH probed layouts — the Athens report needs to
            // distinguish "--data has no extracted/" from a dead device.
            if (err) *err = "music track missing: " + tune + ".raw (tried " +
                            a02 + " and " + a01 + ")";
            return false;
        }
        af::Sample ms;
        if (!af::loadSample(path, tune, &ms, &merr)) {
            if (err) *err = merr;
            return false;
        }
        if (t == 0) musicBytes_ = ms.pcm.size();  // gate line reports track 0
        musicWavs_.push_back(wrapWav(ms));  // member: music streams from here
        const auto& w = musicWavs_.back();
        SDL_RWops* rw = SDL_RWFromConstMem(w.data(), int(w.size()));
        Mix_Music* m = Mix_LoadMUS_RW(rw, 1);
        if (!m) {
            if (err) *err = "Mix_LoadMUS " + tune + ": " + Mix_GetError();
            return false;
        }
        music_.push_back(m);
    }
    return true;
}

void AudioEngine::play(const std::string& sfxName) {
    auto it = chunks_.find(sfxName);
    if (it != chunks_.end()) {
        // fflush: the trace is read by automation that may SIGKILL the app
        // mid-movie (witness scripts); unbuffered lines survive teardown.
        if (trace_) { std::printf("sfx %s\n", sfxName.c_str()); std::fflush(stdout); }
        Mix_PlayChannel(-1, it->second, 0);
    }
}

void AudioEngine::playTune(int t) {
    // Out-of-range is a no-op against the STATIC law (trackNames), so the
    // request state machine behaves identically with or without a device —
    // that is what makes audio_tune_switch_law headless-testable.
    if (t >= int(trackNames().size())) return;
    // t395 HARDENING: any negative other than the cited -1 stop command is
    // an invalid request (kTuneNoChange == -2 lives in boot.h). Without this
    // guard `t < music_.size()` below is true for negatives and indexes UB.
    if (t < -1) return;
    // Stop request (vendor TUNEID -1 -> FUN_00067b85): halt, remember idle.
    if (t == -1) {
        if (inited_ && Mix_PlayingMusic()) Mix_HaltMusic();
        currentTune_ = -1;
        if (trace_) { std::printf("music stop\n"); std::fflush(stdout); }
        return;
    }
    // SWITCH law (subtitle.txt fires DIGITALMUSIC at frames 20 AND 988): a
    // different tune replaces the current one; the same tune never restarts.
    if (t == currentTune_) return;
    if (currentTune_ >= 0 && inited_ && Mix_PlayingMusic()) Mix_HaltMusic();
    if (inited_ && t < int(music_.size())) Mix_PlayMusic(music_[size_t(t)], -1);
    currentTune_ = t;
    if (trace_) {
        std::printf("music %d %s\n", t, trackNames()[size_t(t)].c_str());
        std::fflush(stdout);
    }
}

void AudioEngine::setMusicVolume(int vendorScale) {
    // MEASURED (docs/re/audio.md §6): FUN_0004feec @0x4feec stores the
    // volume byte ONLY when -1 < v <= 0x7f — out-of-range values are
    // silently dropped (NO clamp), then the device is poked via 0x6888c.
    // Mirror the drop, then map the 0..127 scale onto MIX_MAX_VOLUME.
    if (!vendorVolumeOk(vendorScale)) return;
    musicVol_ = vendorScale;
    if (inited_)
        Mix_VolumeMusic(int((MIX_MAX_VOLUME * musicVol_) / kVendorVolMax));
}

AudioEngine::~AudioEngine() {
    for (auto* m : music_) if (m) Mix_FreeMusic(m);
    for (auto& kv : chunks_) Mix_FreeChunk(kv.second);
    if (inited_) Mix_CloseAudio();
}

}  // namespace ascend::ui
