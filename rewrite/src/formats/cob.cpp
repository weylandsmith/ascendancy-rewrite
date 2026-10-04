#include "formats/cob.h"

#include <fstream>
#include <cstring>

namespace ascend::formats {
namespace {

uint32_t rd32(const uint8_t* p) {
    uint32_t v;
    std::memcpy(&v, p, 4);
    return v;  // x86/x64 are little-endian; the archives are LE (docs/FINDINGS.md P1a)
}

}  // namespace

std::optional<CobArchive> CobArchive::load(const std::filesystem::path& path, std::string* err) {
    std::ifstream f(path, std::ios::binary | std::ios::ate);
    if (!f) {
        if (err) *err = "cannot open " + path.string();
        return std::nullopt;
    }
    const std::streampos len = f.tellg();
    f.seekg(0);
    std::vector<uint8_t> buf(static_cast<size_t>(len));
    if (!f.read(reinterpret_cast<char*>(buf.data()), len)) {
        if (err) *err = "short read on " + path.string();
        return std::nullopt;
    }
    return parse(std::move(buf), err);
}

std::optional<CobArchive> CobArchive::parse(std::vector<uint8_t> bytes, std::string* err) {
    auto fail = [&](const std::string& m) -> std::optional<CobArchive> {
        if (err) *err = m;
        return std::nullopt;
    };

    const size_t n = bytes.size();
    if (n < 4) return fail("file smaller than the u32 count field");
    const uint32_t count = rd32(bytes.data());
    if (count == 0 || count > 100000) return fail("implausible file count " + std::to_string(count));

    // --- name records: NUL-terminated, padded with NULs to the next non-NUL.
    size_t off = 4;
    std::vector<std::string> names;
    names.reserve(count);
    for (uint32_t i = 0; i < count; ++i) {
        const size_t z = [&]() {
            for (size_t k = off; k < n; ++k)
                if (bytes[k] == 0) return k;
            return n;
        }();
        if (z >= n) return fail("unterminated name record at entry " + std::to_string(i));
        names.emplace_back(reinterpret_cast<const char*>(bytes.data() + off), z - off);
        off = z + 1;
        while (off < n && bytes[off] == 0) ++off;
    }
    const size_t dir_end = off;

    // --- offset table: exactly `count` u32 entries (OQ-001 CLOSED).
    if (dir_end + 4ull * count > n)
        return fail("offset table runs past EOF");
    std::vector<uint32_t> tab(count);
    for (uint32_t i = 0; i < count; ++i) tab[i] = rd32(bytes.data() + dir_end + 4ull * i);

    for (uint32_t i = 0; i + 1 < count; ++i) {
        if (tab[i] >= tab[i + 1])
            return fail("offset table not strictly increasing at entry " + std::to_string(i));
    }
    // The table is immediately followed by the data area.
    if (static_cast<size_t>(tab[0]) != dir_end + 4ull * count)
        return fail("off[0]=" + std::to_string(tab[0]) + " != dir_end+4N=" +
                    std::to_string(dir_end + 4ull * count));
    if (tab.back() >= n) return fail("last offset past EOF");

    CobArchive a;
    a.image_ = std::move(bytes);
    a.entries_.reserve(count);
    for (uint32_t i = 0; i < count; ++i) {
        const uint32_t begin = tab[i];
        const uint32_t end = (i + 1 < count) ? tab[i + 1] : static_cast<uint32_t>(a.image_.size());
        a.entries_.push_back({names[i], begin, end - begin});
    }

    // Accounting must close to the byte (standing rule): blob sizes sum to the
    // data area exactly.
    uint64_t sum = 0;
    for (const auto& e : a.entries_) sum += e.size;
    if (sum != a.image_.size() - (dir_end + 4ull * count))
        return fail("blob sizes sum to " + std::to_string(sum) + ", data area is " +
                    std::to_string(a.image_.size() - (dir_end + 4ull * count)));
    if (err) err->clear();
    return a;
}

bool CobArchive::find(const std::string& name, const uint8_t** out, uint32_t* len) const {
    for (const auto& e : entries_) {
        if (e.name == name) {
            *out = image_.data() + e.offset;
            *len = e.size;
            return true;
        }
    }
    return false;
}

size_t CobArchive::extractAll(const std::filesystem::path& outDir, std::string* err) const {
    size_t written = 0;
    for (const auto& e : entries_) {
        // Names carry DOS backslash separators (docs/FINDINGS.md P1a).
        std::string rel = e.name;
        for (auto& c : rel)
            if (c == '\\') c = '/';
        const std::filesystem::path dst = outDir / rel;
        std::error_code ec;
        if (dst.has_parent_path()) std::filesystem::create_directories(dst.parent_path(), ec);
        std::ofstream f(dst, std::ios::binary | std::ios::trunc);
        if (!f) {
            if (err) *err = "cannot write " + dst.string();
            return written;
        }
        f.write(reinterpret_cast<const char*>(image_.data() + e.offset), e.size);
        if (!f) {
            if (err) *err = "short write on " + dst.string();
            return written;
        }
        ++written;
    }
    if (err) err->clear();
    return written;
}

}  // namespace ascend::formats
