// Vendor sample format tests — invariants from docs/re/audio.md §1-§4,
// checked against the REAL files in extracted/ (read-only, gate-safe).
#include "formats/voc.h"
#include "harness.h"

#include <cstdio>


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
