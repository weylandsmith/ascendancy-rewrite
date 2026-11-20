// SPDX-License-Identifier: GPL-3.0-or-later

// Vendor sample format tests — invariants from docs/re/audio.md §1-§4,
// checked against the REAL files in extracted/ (read-only, gate-safe).
#include "formats/voc.h"
#include "ui/audio.h"
#include "harness.h"

#include <array>
#include <cstdio>
#include <cstdlib>
#include <filesystem>
#include <string>


namespace af = ascend::formats;
static const std::string kRepo = ASCENDANCY_SOURCE_DIR;
static const std::string kData = kRepo + "/extracted/ascend01/data/";

TEST(audio_manifest_soundfx) {
    REQUIRE_DATA();
    std::string err;
    auto names = af::loadSoundfxManifest(kRepo + "/extracted/ascend00/soundfx.txt", &err);
    CHECK(names.size() == 86);
    CHECK(names[0] == "button");
    CHECK(names[2] == "laser01");
    (void)err;
}

TEST(audio_manifest_music) {
    REQUIRE_DATA();
    std::string err;
    auto m = af::loadMusicManifest(kRepo + "/extracted/ascend00/music.txt", &err);
    CHECK(m.size() == 29);
    CHECK(m[0] == "theme00.raw");
    CHECK(m.back() == "race20.raw");
}

TEST(audio_headered_voc) {
    REQUIRE_DATA();
    // bang01.voc: rate 22050, mono, PCM 41389 bytes (audio.md §2 table).
    af::Sample s;
    std::string err;
    CHECK(af::loadSample(kData + "bang01.voc", "bang01", &s, &err));
    CHECK(s.rate == 22050);
    CHECK(s.channels == 1);
    CHECK(s.pcm.size() == 41377);  // bytes 42..EOF-1 (§2; len@27=41389 is the
                                   // vendor region length, OQ-018)
    CHECK(s.pcm.front() == 0x80);  // silence start
    // bullet.voc is the lone 11025/stereo file.
    af::Sample b;
    CHECK(af::loadSample(kData + "bullet.voc", "bullet", &b, &err));
    CHECK(b.rate == 11025);
    CHECK(b.channels == 2);
    CHECK(b.pcm.size() == 8070);
}

TEST(audio_headerless_defaults) {
    REQUIRE_DATA();
    af::Sample s;
    std::string err;
    CHECK(af::loadSample(kData + "destroy.voc", "destroy", &s, &err));
    CHECK(s.rate == 22050);       // documented default (OQ-006)
    CHECK(s.channels == 1);
    CHECK(s.pcm.size() == 28708);  // whole file, no header stripped
    CHECK(s.pcm.front() == 0x80);
    // music .raw loads through the same path
    af::Sample m;
    CHECK(af::loadSample(kRepo + "/extracted/ascend02/data/theme00.raw",
                         "theme00", &m, &err));
    CHECK(m.pcm.size() == 8191719);
}

TEST(audio_open_rate_measured_oq006) {
    REQUIRE_DATA();
    // MEASURED law (OQ-006 CLOSED 2026-10-07, audio.md §3.1): the original's
    // audio-open chain pushes 22050 (0x5622) and forwards it to the rate
    // setter. Pin the exact bytes at the three cited sites of the restored
    // image. work/ is not committed; skip cleanly when absent (test_cob
    // precedent).
    namespace fs = std::filesystem;
    const std::string imgp = kRepo + "/work/ascend_restored.bin";
    if (!fs::exists(imgp)) {
        std::printf("(skip: work/ascend_restored.bin absent) ");
        return;
    }
    std::FILE* f = std::fopen(imgp.c_str(), "rb");
    CHECK(f != nullptr);
    if (!f) return;
    auto at = [&](long off) {
        std::array<unsigned char, 8> b{};
        std::fseek(f, off, SEEK_SET);
        size_t n = std::fread(b.data(), 1, b.size(), f);
        (void)n;
        return b;
    };
    // 0x4f690: PUSH 0x5622 (68 22 56 00 00) then PUSH ESI (56 @0x4f695)
    // then CALL 0x68816 (e8 7b 91 01 00 @0x4f696).
    {
        auto b = at(0x4f690);
        CHECK(b[0] == 0x68 && b[1] == 0x22 && b[2] == 0x56 &&
              b[3] == 0x00 && b[4] == 0x00);
        CHECK(b[5] == 0x56);
        auto c = at(0x4f696);
        CHECK(c[0] == 0xe8 && c[1] == 0x7b && c[2] == 0x91 && c[3] == 0x01);
    }
    // 0x4f90b: same PUSH 0x5622 / PUSH EBP (55) / CALL 0x68816 shape.
    {
        auto b = at(0x4f90b);
        CHECK(b[0] == 0x68 && b[1] == 0x22 && b[2] == 0x56);
        CHECK(b[5] == 0x55);
        auto c = at(0x4f911);
        CHECK(c[0] == 0xe8 && c[1] == 0x00 && c[2] == 0x8f && c[3] == 0x01);
    }
    // 0x6df3e: constructor default MOV dword [EAX+0x3c], 0x2b11 (11025):
    // c7 40 3c 11 2b 00 00 — always overwritten by the two open sites.
    {
        auto b = at(0x6df3e);
        CHECK(b[0] == 0xc7 && b[1] == 0x40 && b[2] == 0x3c &&
              b[3] == 0x11 && b[4] == 0x2b);
    }
    std::fclose(f);
}

TEST(audio_tune_selector_oq018) {
    REQUIRE_DATA();
    // MEASURED (docs/re/audio.md §3.3): global tune selector DAT_00010ba0
    // has EXACTLY ONE writer in the image — MOV [0x10ba0],-1 @0x21309,
    // guarded by an option-key check (CALL 0x77ece) inside the music.txt
    // loader FUN_00020fd4. All banked saves read 0 == music.txt track 0 ==
    // theme00.raw, which is what playMusic() plays.
    namespace fs = std::filesystem;
    const std::string imgp = kRepo + "/work/ascend_restored.bin";
    if (!fs::exists(imgp)) {
        std::printf("(skip: work/ascend_restored.bin absent) ");
        return;
    }
    std::FILE* f = std::fopen(imgp.c_str(), "rb");
    CHECK(f != nullptr);
    if (!f) return;
    auto at = [&](long off) {
        std::array<unsigned char, 12> b{};
        std::fseek(f, off, SEEK_SET);
        size_t n = std::fread(b.data(), 1, b.size(), f);
        (void)n;
        return b;
    };
    // c7 05 a00b0100 ffffffff : MOV dword [0x00010ba0], 0xffffffff
    {
        auto b = at(0x21309);
        CHECK(b[0] == 0xc7 && b[1] == 0x05);
        CHECK(b[2] == 0xa0 && b[3] == 0x0b && b[4] == 0x01 && b[5] == 0x00);
        CHECK(b[6] == 0xff && b[7] == 0xff && b[8] == 0xff && b[9] == 0xff);
    }
    // 0x212f6: option-key probe prologue MOV EDX,0x943 / MOV EAX,(0x945
    // fixed up: 0x834f5 = 0x945+0x82BB0 in the restored image) / CALL
    // 0x77ece — the gate whose store branch is the sole writer above.
    {
        auto b = at(0x212f6);
        CHECK(b[0] == 0xba && b[1] == 0x43 && b[2] == 0x09);
        CHECK(b[5] == 0xb8 && b[6] == 0xf5 && b[7] == 0x34 && b[8] == 0x08);
        CHECK(b[10] == 0xe8);
    }
    std::fclose(f);
}

TEST(audio_voice_band_law_oq018) {
    REQUIRE_DATA();
    // MEASURED (docs/re/audio.md §3.2 HEADER-PAIR LAW, FINAL): the vendor
    // bands sounds by FILE SIZE vs soundfx.txt col2 (2 10000 / 3 45000 /
    // 1 65000): band = count(threshold <= size), size >= 65000 = vendor
    // error. Span-table identity proven on live RAM (ck005: 327/328 file
    // spans == disk sizes; laser01.voc span 45277 = disk). Boundary pins:
    CHECK(af::voiceBand(9999) == 0);
    CHECK(af::voiceBand(10000) == 1);   // threshold inclusive (<=)
    CHECK(af::voiceBand(44999) == 1);
    CHECK(af::voiceBand(45000) == 2);
    CHECK(af::voiceBand(64999) == 2);
    CHECK(af::voiceBand(65000) == -1);  // all three <= size -> error path
    // Shipped-data census (on-disk tree, same lookup rule as AudioEngine):
    // must be band {4,73,1} over resolvable manifest names, ZERO errors.
    const std::string repo = ASCENDANCY_SOURCE_DIR;
    auto names = af::loadSoundfxManifest(
        repo + "/extracted/ascend00/soundfx.txt", nullptr);
    CHECK(names.size() == 86);
    int b0 = 0, b1 = 0, b2 = 0, bad = 0, resolvable = 0;
    for (auto n : names) {
        for (auto& c : n) c = char(std::tolower(c));
        std::error_code ec;
        const auto p = std::filesystem::path(
            repo + "/extracted/ascend01/data/" + n + ".voc");
        if (!std::filesystem::exists(p, ec)) continue;  // 9 names live only
        resolvable++;                                   // inside archives
        switch (af::voiceBand(
            uint32_t(std::filesystem::file_size(p, ec)))) {
            case 0: b0++; break;
            case 1: b1++; break;
            case 2: b2++; break;
            default: bad++; break;
        }
    }
    CHECK(resolvable == 86);  // 85 unique names + 'shield' listed twice;
    CHECK(b0 == 4);           // all on-disk files are lowercase .voc
    CHECK(b1 == 81);   // 10000..45000 (3 voices); shield counted twice
    CHECK(b2 == 1);    // laser01.voc 45277 (1 voice)
    CHECK(bad == 0);   // shipped data never hits the vendor error path
}

TEST(audio_rejects_garbage_magic) {
    REQUIRE_DATA();
    // A file that lies about being a VOC (magic but wrong block fields)
    // must fail, not silently play garbage.
    const std::string p = "/tmp/ascend_fake.voc";
    FILE* f = std::fopen(p.c_str(), "wb");
    // magic + 0x1A terminator, then byte 20 = 0x00 (real files: 0x1A/26)
    std::fwrite("Creative Voice File"
                "\x1a\x00\x14\x01\x20\x11\x09\x01\x00\x00\x22\x56"
                "\x00\x00\x08\x01\x00\x00\x00\x00\x00\x00\x80\x80", 1, 43, f);
    std::fclose(f);
    af::Sample s;
    std::string err;
    CHECK(!af::loadSample(p, "fake", &s, &err));
}

// ---------------------------------------------------------------------------
// t388b SOUND FIDELITY pins (docs/re/audio.md §6)

TEST(audio_subtitle_script_cues_oq018) {
    REQUIRE_DATA();
    // MEASURED law: the intro-movie cue table IS subtitle.txt (flic.cpp
    // engine; loader refs 'SUBTITLE.TXT' payload 0x83fb0, parser 0x2e46c,
    // verb-number dispatch 0x2e4fe..0x2e525 — audio.md §6.1). Pin the file
    // contents the port's cue table mirrors.
    std::FILE* f = std::fopen((kRepo + "/extracted/ascend00/subtitle.txt").c_str(), "rb");
    CHECK(f != nullptr);
    if (!f) return;
    std::string all;
    char buf[4096];
    size_t n;
    while ((n = std::fread(buf, 1, sizeof(buf), f)) > 0) all.append(buf, n);
    std::fclose(f);
    // DIGITALMUSIC lines: TUNEID 6 at FRAMENUMBER 20, TUNEID 7 at 988
    // (intro00 over the bulk of the movie, intro01 over the tail — audio.md
    // §6.3; TUNEID base measured t440, see audio_tuneid_zero_based_t440).
    CHECK(all.find("DIGITALMUSIC  16\r\nTUNEID        6\r\nCOMMAND       1\r\nFRAMENUMBER   20 ") != std::string::npos);
    CHECK(all.find("DIGITALMUSIC  16\r\nTUNEID        7\r\nCOMMAND       1\r\nFRAMENUMBER   988 ") != std::string::npos);
    // FADEMUSIC ramp: 100/80/60/30 at 966/971/976/981, 127 at 988
    CHECK(all.find("FADEMUSIC     11\r\nCHANNEL       0\r\nVOLUME        100\r\nFRAMENUMBER   966 ") != std::string::npos);
    CHECK(all.find("VOLUME        30\r\nFRAMENUMBER   981 ") != std::string::npos);
    CHECK(all.find("VOLUME        127\r\nFRAMENUMBER   988 ") != std::string::npos);
}

TEST(audio_music_tune_table_law) {
    REQUIRE_DATA();
    // The loaded tune table is cited-law-only (audio.cpp comment; audio.md
    // §3.3 captured selector + §6 script). Members and ORDER are the pin.
    const auto& t = ascend::ui::AudioEngine::trackNames();
    CHECK(t.size() == 3);
    CHECK(t[0] == "theme00");
    CHECK(t[1] == "intro00");
    CHECK(t[2] == "intro01");
    // Files exist where the loader looks, sizes match the banked census:
    // theme00 8191719 (ascend02), intro00 2000000 / intro01 479670
    // (ascend01) — same numbers as audio.md §4 + t388b WIP inventory.
    std::error_code ec;
    CHECK(std::filesystem::file_size(kRepo + "/extracted/ascend02/data/theme00.raw", ec) == 8191719u);
    CHECK(std::filesystem::file_size(kRepo + "/extracted/ascend01/data/intro00.raw", ec) == 2000000u);
    CHECK(std::filesystem::file_size(kRepo + "/extracted/ascend01/data/intro01.raw", ec) == 479670u);
    // Headerless shape: first bytes are 0x80-region PCM silence, NOT a
    // RIFF/VOC magic (the .raw loader must not be handed a headered file
    // by accident; §3 re-verified for the tune set here).
    af::Sample s;
    std::string err;
    CHECK(af::loadSample(kRepo + "/extracted/ascend01/data/intro00.raw", "intro00", &s, &err));
    CHECK(s.rate == 22050);
    CHECK(s.channels == 1);
    CHECK(std::abs(int(s.pcm.front()) - 0x80) <= 4);
}

TEST(audio_tuneid_zero_based_t440) {
    REQUIRE_DATA();
    // MEASURED LAW (t440, audio.md 6.1 + 6.3a): the vendor's DIGITALMUSIC
    // consumer FUN_0004f86c indexes names at obj+0x37a + tuneid*28 with NO
    // bias (0x4f929 movsx / 0x4f92c lea [edx*8] / 0x4f933 sub eax,edx /
    // 0x4f93a shl 2 => tuneid*28), bounds-checked against WORD[obj+0x6fa]
    // (0x4f89a), which reads 29 in 20/20 banked saves
    // (scripts/t440_music_table.py VERDICT PASS). The table decodes in
    // music.txt order, so TUNEID is a ZERO-BASED index: 6=intro00, 7=intro01.
    // Leg 1: the vendor data agrees with the measured base.
    std::FILE* f = std::fopen((kRepo + "/extracted/ascend00/music.txt").c_str(), "rb");
    CHECK(f != nullptr);
    if (!f) return;
    std::string all;
    char buf[4096];
    size_t n;
    while ((n = std::fread(buf, 1, sizeof(buf), f)) > 0) all.append(buf, n);
    std::fclose(f);
    std::vector<std::string> lines;
    size_t pos = 0;
    while (pos < all.size()) {
        size_t e = all.find('\n', pos);
        if (e == std::string::npos) e = all.size();
        std::string l = all.substr(pos, e - pos);
        while (!l.empty() && (l.back() == '\r' || l.back() == ' ')) l.pop_back();
        if (!l.empty()) lines.push_back(l);
        pos = e + 1;
    }
    // Line 0 is the COUNT line ("29"); the names follow in file order.
    CHECK(!lines.empty() && lines[0] == "29");
    CHECK(lines.size() == 30);                       // 1 count + 29 names
    if (lines.size() == 30) {
        const std::string* L = lines.data() + 1;     // L[t] = TUNEID t
        CHECK(L[0] == "data\\theme00.raw");
        CHECK(L[6] == "data\\intro00.raw");
        CHECK(L[7] == "data\\intro01.raw");
        CHECK(L[8] == "data\\race00.raw");
    }
    // Leg 2: the port's cue translation lands on the same tunes the vendor
    // names. trackNames() is the port's OWN subset, so the invariant is the
    // PAIRING, not the numeric index: vendor 6 -> intro00, vendor 7 -> intro01.
    const auto& t = ascend::ui::AudioEngine::trackNames();
    CHECK(t.size() == 3);
    if (t.size() == 3) {
        CHECK(t[1] == "intro00");
        CHECK(t[2] == "intro01");
        CHECK(t[1] != t[2]);                         // a swap is detectable
    }
    // Leg 3: the intro cue table maps the two DIGITALMUSIC frames to the
    // intro members in vendor order (frame 20 -> intro00, 988 -> intro01).
    std::FILE* s = std::fopen((kRepo + "/rewrite/src/ui/ui.cpp").c_str(), "rb");
    CHECK(s != nullptr);
    if (s) {
        std::string src;
        while ((n = std::fread(buf, 1, sizeof(buf), s)) > 0) src.append(buf, n);
        std::fclose(s);
        CHECK(src.find("{20, 1, -1},") != std::string::npos);
        CHECK(src.find("{988, 2, -1},") != std::string::npos);
    }
}

TEST(audio_vendor_volume_scale_law) {
    // MEASURED (FUN_0004feec @0x4feec, audio.md §6.2): store iff
    // -1 < v <= 0x7f; out-of-range is DROPPED, never clamped.
    CHECK(ascend::ui::vendorVolumeOk(0));
    CHECK(ascend::ui::vendorVolumeOk(100));
    CHECK(ascend::ui::vendorVolumeOk(127));
    CHECK(!ascend::ui::vendorVolumeOk(-1));
    CHECK(!ascend::ui::vendorVolumeOk(128));
    // State machine (headless, no device): setMusicVolume keeps the last
    // ACCEPTED value; a dropped request leaves it untouched.
    ascend::ui::AudioEngine a;
    CHECK(a.musicVolume() == 127);          // constructor: full scale
    a.setMusicVolume(100);
    CHECK(a.musicVolume() == 100);
    a.setMusicVolume(300);                  // dropped, not clamped
    CHECK(a.musicVolume() == 100);
}

TEST(audio_tune_switch_law) {
    // Headless state machine (no device opened): playTune tracks the
    // current tune; SWITCH replaces, SAME never restarts, -1 stops, junk
    // indices are no-ops. Mirrors the subtitle-script behaviour where
    // DIGITALMUSIC fires at frames 1 AND 20 without restarting tune 7.
    ascend::ui::AudioEngine a;
    CHECK(a.currentTune() == -1);
    a.playTune(0);
    CHECK(a.currentTune() == 0);
    a.playTune(0);                          // same tune: state unchanged
    CHECK(a.currentTune() == 0);
    a.playTune(1);                          // switch
    CHECK(a.currentTune() == 1);
    a.playTune(2);
    CHECK(a.currentTune() == 2);
    a.playTune(3);                          // out of range: no-op
    CHECK(a.currentTune() == 2);
    a.playTune(-1);                         // stop (vendor TUNEID -1)
    CHECK(a.currentTune() == -1);
}
