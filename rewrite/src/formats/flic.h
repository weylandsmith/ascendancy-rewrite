#pragma once
#include <cstdint>
#include <functional>
#include <string>
#include <vector>

namespace ascend::formats {
// Autodesk FLC (Animator Pro, magic 0xAF12) decoder, 8 bpp.
// Spec + evidence: docs/re/flc.md (rules quoted from compuphase.com/flic.htm;
// every chunk instance of BOTH vendor files validated zero-residue by
// scripts/flc_probe.py; C++ identity pinned by rewrite/tests/data/
// flc_golden.tsv). Chunks implemented: 0xF1FA FRAME (16 B header),
// COLOR_256(4)/COLOR_64(11), BYTE_RUN(15), FLI_COPY(16), DELTA_FLC(7),
// PSTAMP(18, structure-checked only — the port never displays the stamp).
class Flic {
public:
    static constexpr int kColor256 = 4;
    static constexpr int kDeltaFlc = 7;
    static constexpr int kColor64 = 11;
    static constexpr int kByteRun = 15;
    static constexpr int kFliCopy = 16;
    static constexpr int kPstamp = 18;
    static constexpr int kFrame = 0xF1FA;

    struct Sub {  // one sub-chunk header; offsets RELATIVE TO THE BUFFER BASE
                  // handed to the walk (frame-chunk start inside applyChunk)
        uint32_t off = 0;
        uint32_t size = 0;
        uint16_t type = 0;
    };

    struct Chunk {  // one top-level 0xF1FA frame chunk, pre-scanned
        uint32_t off = 0;    // file offset of the chunk header
        uint32_t size = 0;
        uint16_t nchunks = 0;
        uint16_t delay = 0;  // ms override; 0 = header speed
    };

    bool load(const std::string& path, std::string* err);

    int width() const { return w_; }
    int height() const { return h_; }
    uint32_t speedMs() const { return speed_; }
    uint16_t declaredFrames() const { return nframes_; }
    const std::vector<Chunk>& frames() const { return frames_; }

    // Applies one frame chunk to the running (pixels, palette) state — the
    // FLC delta model: state carries from frame to frame. `repaired` counts
    // FLI_COPY chunks whose declared size is wrong (compuphase "Frequent
    // errors"; the vendor's logic.flc ring frame is exactly one).
    bool applyChunk(const uint8_t* data, size_t size, uint16_t nchunks,
                    uint8_t* px, uint8_t* pal256x3, int* repaired,
                    std::string* err) const;

    // Replays every frame chunk in order; cb(frame_index, pixels, palette)
    // after each. Returns false on the first decode violation.
    bool replay(const std::function<void(int, const uint8_t*, const uint8_t*)>& cb,
                std::string* err, int* repaired = nullptr) const;

private:
    // Size-delimited walk from off+16; honours nchunks when non-zero. Tiles
    // check: subs must end exactly at the frame chunk's end.
    bool subchunks(const uint8_t* d, const Chunk& c, std::vector<Sub>* subs) const;
    // compuphase FLI_COPY repair: force size 6+w*h, re-check tiling.
    bool repairCopy(std::vector<Sub>* subs, const Chunk& c) const;

    std::vector<uint8_t> data_;
    int w_ = 0, h_ = 0;
    uint16_t nframes_ = 0;
    uint32_t speed_ = 0;
    std::vector<Chunk> frames_;
};
}  // namespace ascend::formats
