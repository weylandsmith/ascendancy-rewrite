// SPDX-License-Identifier: GPL-3.0-or-later
// t395 SOUND AUDIBILITY pins (docs/re/audio.md §6.6): the menu-music entry
// law, the invalid-tune guard, and the tried-paths diagnostic.
#include "formats/voc.h"
#include "ui/audio.h"
#include "ui/boot.h"
#include "harness.h"

#include <filesystem>
#include <string>
#include <vector>

namespace au = ascend::ui;

TEST(boot_tune_entry_law_t395) {
    // Title screen requests tune 0 (theme00 == captured DAT_00010ba0 == 0);
    // every other state requests NOTHING (kTuneNoChange, NOT the -1 stop).
    CHECK(au::bootTune(au::BootState::Title) == 0);
    CHECK(au::bootTune(au::BootState::RaceConfig) == au::kTuneNoChange);
    CHECK(au::bootTune(au::BootState::Intro) == au::kTuneNoChange);
    CHECK(au::bootTune(au::BootState::Load) == au::kTuneNoChange);
    CHECK(au::bootTune(au::BootState::Campaign) == au::kTuneNoChange);
    // The sentinel must never be a valid playTune request: -2 is guarded.
    CHECK(au::kTuneNoChange == -2);
}

TEST(audio_invalid_tune_guard_t395) {
    // Headless state machine: kTuneNoChange / any t < -1 is a NO-OP (the
    // pre-t395 code would index music_[-2] — UB). -1 stays the cited stop.
    au::AudioEngine a;
    a.playTune(0);
    CHECK(a.currentTune() == 0);
    a.playTune(au::kTuneNoChange);
    CHECK(a.currentTune() == 0);      // unchanged, not stopped
    a.playTune(-7);
    CHECK(a.currentTune() == 0);      // unchanged
    a.playTune(-1);
    CHECK(a.currentTune() == -1);     // cited stop still works
}

TEST(audio_click08_offmanifest_t395) {
    // MEASURED: click08.voc exists in ascend01/data but soundfx.txt does NOT
    // name it (grep of the manifest = 0 hits) — so the manifest loop alone
    // left play("click08") a silent no-op (the D10 root cause). init() must
    // carry it: chunksLoaded = 85 manifest-unique + 1 = 86.
    REQUIRE_DATA();
    namespace fs = std::filesystem;
    static const std::string kRepo = ASCENDANCY_SOURCE_DIR;
    std::string err;
    auto names = ascend::formats::loadSoundfxManifest(
        kRepo + "/extracted/ascend00/soundfx.txt", &err);
    bool listed = false;
    for (const auto& n : names)
        if (n == "click08") listed = true;
    CHECK(!listed);
    CHECK(fs::exists(kRepo + "/extracted/ascend01/data/click08.voc"));
    // Full init law (needs a device; dummy is fine):
    ascend::ui::AudioEngine a;
    const bool ok = a.init(kRepo, true, &err);
    if (err.rfind("Mix_OpenAudio", 0) == 0) return;  // no device here
    CHECK(ok);
    CHECK(a.chunksLoaded() == 86);
}

TEST(audio_tried_paths_diagnostic_t395) {
    // A data-less root must fail (never ok) and, when a device exists so
    // init() gets past Mix_OpenAudio, name the manifest path it tried.
    au::AudioEngine a;
    std::string err;
    const bool ok = a.init("/nonexistent-root-t395", true, &err);
    CHECK(!ok);
    if (err.rfind("Mix_OpenAudio", 0) == 0) return;  // no device here
    CHECK(!a.triedPaths().empty());
    CHECK(a.triedPaths()[0].find("extracted/ascend00/soundfx.txt") !=
          std::string::npos);
}

TEST(audio_music_missing_names_layouts_t395) {
    // The music-failure line must name BOTH archive layouts (t395 item 4:
    // "--data without extracted/ beside the cobs" vs a dead device).
    // Scratch root: manifest + sfx present (symlinks), ascend02 absent ->
    // theme00 unfindable after the chunks load.
    REQUIRE_DATA();
    namespace fs = std::filesystem;
    static const std::string kRepo = ASCENDANCY_SOURCE_DIR;
    const fs::path root = fs::temp_directory_path() / "t395-audio-musicroot";
    std::error_code ec;
    fs::remove_all(root, ec);
    fs::create_directories(root / "extracted", ec);
    fs::create_symlink(kRepo + "/extracted/ascend00", root / "extracted" / "ascend00", ec);
    fs::create_symlink(kRepo + "/extracted/ascend01", root / "extracted" / "ascend01", ec);
    au::AudioEngine a;
    std::string err;
    const bool ok = a.init(root.string(), true, &err);
    if (err.rfind("Mix_OpenAudio", 0) == 0) {  // no device: law untestable here
        fs::remove_all(root, ec);
        return;
    }
    CHECK(!ok);
    CHECK(err.find("theme00.raw") != std::string::npos);
    CHECK(err.find("ascend02/data/theme00.raw") != std::string::npos);
    CHECK(err.find("ascend01/data/theme00.raw") != std::string::npos);
    fs::remove_all(root, ec);
}
