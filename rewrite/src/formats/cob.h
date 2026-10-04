#pragma once
// .cob resource-archive reader.
//
// FORMAT (verified, all three shipped archives; docs/FINDINGS.md P1a and
// OQ-001 in docs/OPEN-QUESTIONS.md, re-derivable with scripts/cob.py):
//
//   +0x00  u32      N  file count
//   +0x04  N records: NUL-terminated name, then NUL padding so the NEXT
//                     record starts on the next non-NUL byte. Observed name
//                     lengths cover every residue mod 4, so this is NOT a
//                     4-byte-aligned fixed width (see the standing rule in
//                     docs/FINDINGS.md).
//   dir_end       (N) x u32 LE little-endian offsets, strictly increasing,
//                     with off[0] == dir_end + 4*N exactly (the data area
//                     begins immediately after the table).
//   data          blob[i] = data[off[i], off[i+1]) ; the LAST blob runs to EOF.
//
// No compression in any archive (docs/FINDINGS.md P1a).
//
// The table has exactly N entries, NOT N+1. OQ-001 closed this; an earlier
// extractor that assumed N+1 (or that used off[i+1] for every entry) silently
// dropped each archive's last file — ascend02 lost data\intro65a.flc, 19 MB.
// This implementation appends a synthetic EOF sentinel so callers can use
// (off[i], off[i+1]) safely, and it REFUSES an archive whose invariants fail.

#include <cstdint>
#include <optional>
#include <string>
#include <vector>
#include <filesystem>

namespace ascend::formats {

struct CobEntry {
    std::string name;    // as stored, e.g. "data\\shapes.shp" (backslashes kept)
    uint32_t offset = 0;
    uint32_t size = 0;
};

class CobArchive {
  public:
    // Parses and validates. Returns nullopt and sets *err when an invariant
    // breaks (non-monotonic table, off[0] mismatch, table past EOF).
    static std::optional<CobArchive> load(const std::filesystem::path& path,
                                          std::string* err = nullptr);

    // Parses from an in-memory image (used by tests).
    static std::optional<CobArchive> parse(std::vector<uint8_t> bytes,
                                           std::string* err = nullptr);

    const std::vector<CobEntry>& entries() const { return entries_; }
    size_t count() const { return entries_.size(); }

    // Blob bytes; empty + false if the name is absent.
    bool find(const std::string& name, const uint8_t** out, uint32_t* len) const;

    // Extracts every entry under out_dir, translating '\' path separators.
    // Returns the number of files written. Mirrors scripts/cob.py extract.
    size_t extractAll(const std::filesystem::path& outDir,
                      std::string* err = nullptr) const;

  private:
    std::vector<uint8_t> image_;
    std::vector<CobEntry> entries_;
};

}  // namespace ascend::formats
