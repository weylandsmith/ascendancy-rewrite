// SPDX-License-Identifier: GPL-3.0-or-later

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
// DIMS ORIENTATION RESIDUE (S16, [inferred], NOT law): the residual class
// stores dims whose pair orientation at the V/A slots is unknown; decode
// therefore tries H rows, then W rows, before failing.
//
// WALK BOUND (t197, docs/re/shp.md S20.2/S21): the row walk is bounded by
// the FILE, not by the directory span [rec,nxt). The blit FUN_0005caac has
// no stream-length argument and no stream-overrun error code, and the
// draw-time cache is a verbatim whole-library copy (S10/S12) — the span
// bound was our validator's invention. Records whose streams cross the
// span (X class: planind k0..k12, 3cfgnew k0..k11, 14intel k8, 1starmap
// k3/k4/k6) decode; past-span rows desync into the next record's bytes and
// paint whatever the vendor would paint. Records that still fail: garbage
// dims words (cos_star k40..k51, 1starmap k1) and genuine EOF truncation
// (3cfgnew k12) — reported, never silently stubbed
// (docs/BLOCKED.md t68 residue).
//
// CORNER-ANCHOR GATE FALLBACK (t367, docs/re/shp.md S28, D1 ruling KEEP):
// when the canonical dims gate FAILS for k>=1, a SIGNED bbox read
// (L,T,R,B u32 as int32 at rec+0x08/0x0c/0x10/0x14, W=R-L+1, H=B-T+1) is
// attempted ONLY if (L<0 || T<0) and W,H in [2,4096] and the walk completes.
// This decodes mouse.shp k5/k6/k7 (78x47 — one glyph at four corner
// anchors, t344 S27) and NOTHING else corpus-wide (measured t367: the
// zero-header cos_star k40..k51, 1starmap k1 and sg50expl k9 have no
// negative anchor component or degenerate 1x1 bbox and stay rejected).
// The canonical gate is unchanged for every record that passes it.

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
    // returns false only when neither walk completes inside the FILE
    // (t197: no directory-span bound; see WALK BOUND above).
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
