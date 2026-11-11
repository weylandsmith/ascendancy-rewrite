// SPDX-License-Identifier: GPL-3.0-or-later

// Vendor sample format tests — invariants from docs/re/audio.md §1-§4,
// checked against the REAL files in extracted/ (read-only, gate-safe).
#include "formats/voc.h"
#include "harness.h"

#include <array>
#include <cstdio>
#include <filesystem>
#include <string>


namespace af = ascend::formats;
static const std::string kRepo = ASCENDANCY_SOURCE_DIR;
static const std::string kData = kRepo + "/extracted/ascend01/data/";

TEST(audio_manifest_soundfx) {
    std::string err;
    auto names = af::loadSoundfxManifest(kRepo + "/extracted/ascend00/soundfx.txt", &err);
    CHECK(names.size() == 86);
    CHECK(names[0] == "button");
    CHECK(names[2] == "laser01");
    (void)err;
}

TEST(audio_manifest_music) {
    std::string err;
    auto m = af::loadMusicManifest(kRepo + "/extracted/ascend00/music.txt", &err);
    CHECK(m.size() == 29);
    CHECK(m[0] == "theme00.raw");
    CHECK(m.back() == "race20.raw");
}

TEST(audio_headered_voc) {
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
