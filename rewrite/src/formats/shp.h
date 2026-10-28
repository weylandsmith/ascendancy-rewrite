#pragma once
// .shp shape-library reader + row-RLE pixel decoder (OQ-005).
//
// CONTAINER (docs/re/shp.md S1/S16; every invariant enforced, matching
// the standing Python validator scripts/r1_shp_unifiedlaw.py):
//   +0x00  u32  magic '1.10' (31 2E 31 30)
//   +0x04  u32  count        record count N
//   +0x08  u32  tsz          directory byte size == 8*(N+1) exactly
//   +0x10  u64  directory entries (N-1 of them): starts[k] = entry k-1
//                     (absolute file offsets); starts[0] == 0x10 + tsz.
//   data   record k spans [starts[k], starts[k+1]) ; last runs to EOF.
//
// RECORD HEADER / STREAM-START (V/A law, measured live-RAM uniform in
// docs/re/shp.md S16/S17 over the verbatim-cached corpus):
//   k == 0   dims u32 pair (W,H) at rec+0x00, RLE stream at rec+0x08
//   k >= 1   dims u32 pair (W,H) at rec+0x10, RLE stream at rec+0x18
//
// PIXEL STREAM (docs/re/shp.md S9 grammar, verbatim from FUN_0005caac
// 0x5cca3..0x5ce77; one byte per pixel = palette index, S5 note
// "light RLE over palette indices"):
//   per row, read control C:
//     C == 0        end of row
//     C == 1        L = next byte; advance pixel position by L (skip,
//                   destination untouched = transparency)
//     C odd  > 1    copy C>>1 bytes literally into the row
//     C even > 0    value = next byte, repeated C>>1 times
//   Pixel position advancing past W: WRITES CLAMP (mirroring the blit's
//   clamp branches at 0x5cd31/0x5cd62) but the stream still advances;
//   a completed row may exceed W without failing the walk (S14).
//
// DIMS ORIENTATION RESIDUE (S16, [inferred], NOT law): the 80-record
// residual class stores dims whose pair orientation at the V/A slots is
// unknown; decode therefore tries H rows, then W rows, before failing.
// Records failing both are the banked BLOCKED-USER-LEVEL residue
// (docs/BLOCKED.md t68 entry) — reported, never silently stubbed.

#include <cstdint>
#include <string>
#include <vector>
#include <cstddef>

namespace ascend::formats {

class ShapeLibrary {
  public:
    struct Record {
        uint32_t width = 0;
        uint32_t height = 0;
        uint32_t start = 0;   // header offset in the image
        uint32_t end = 0;     // exclusive span end
        uint32_t stream = 0;  // RLE stream start
    };

    // Loads and enforces every container invariant. False + *err on
    // violation (magic, tsz==8*(N+1), directory monotonicity, bounds).
    bool load(const std::string& path, std::string* err);

    // In-memory entry point (CobArchive::parse house style) so law
    // rejection is testable without touching the filesystem.
    bool parse(std::vector<uint8_t> img, std::string* err);

    int count() const { return static_cast<int>(records_.size()); }
    const Record& record(int i) const { return records_[i]; }

    // Decodes record i into out (exactly width*height bytes, 1 byte per
    // pixel palette index). Bytes never written (skipped pixels, clamped
    // overflow) keep whatever out held on entry: caller chooses the
    // underlay, mirroring the original's untouched-destination semantics.
    // Tries height rows, then width rows (S16 orientation residue);
    // returns false only when neither walk completes inside the span.
    // *swapped (optional, docs/BLOCKED.md t68 evidence tooling t182): true
    // iff only the swapped walk completed — the buffer then holds
    // record().width rows of stride record().height (the canonical walk
    // yields height rows of stride width).
    bool decode(int i, std::vector<uint8_t>& out,
                bool* swapped = nullptr) const;

    static constexpr uint32_t kMagic = 0x30312E31u;  // '1.10' LE

  private:
    std::vector<uint8_t> img_;
    std::vector<Record> records_;
};

}  // namespace ascend::formats
