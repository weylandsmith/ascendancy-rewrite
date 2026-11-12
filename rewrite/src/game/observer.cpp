// SPDX-License-Identifier: GPL-3.0-or-later

// t382 read-only observer — laws in observer.h / docs/re/_wip_t382.md.
#include "game/observer.h"

#include <algorithm>
#include <cmath>
#include <cstring>
#include <sstream>

namespace ascend::game {
namespace {

uint32_t rd32(const uint8_t* p) {
    return uint32_t(p[0]) | (uint32_t(p[1]) << 8) | (uint32_t(p[2]) << 16) |
           (uint32_t(p[3]) << 24);
}
uint16_t rd16(const uint8_t* p) { return uint16_t(p[0]) | (uint16_t(p[1]) << 8); }
float rdf(const uint8_t* p) {
    uint32_t u = rd32(p);
    float f;
    std::memcpy(&f, &u, 4);
    return f;
}

constexpr uint32_t kStarStride = 0x60;
constexpr int kStarNameX = 0x1c;

bool saneF32(float v) { return std::isfinite(v) && std::fabs(v) < 100000.f; }

// Star-slot record sanity (shape law: K8 table, planets-ui.md §1): type index
// 0..12 (the 13 starstat types, mapgen.md S1), printable NUL-term CP437 name
// at +0x1c, sane coords triple at +0x08.
bool saneStar(const uint8_t* r) {
    if (rd32(r) > 12) return false;
    if (!saneF32(rdf(r + 0x08)) || !saneF32(rdf(r + 0x0c)) || !saneF32(rdf(r + 0x10)))
        return false;
    int n = 0;
    for (int i = 0; i < 24; ++i) {
        uint8_t c = r[kStarNameX + i];
        if (c == 0) break;
        if (c < 0x20 || c >= 0x7f) return false;
        ++n;
    }
    return n >= 3;  // shortest vendor star name is 4 chars (Vega); 3 tolerant
}

// Ship-record sanity for the RAW path (the ZIP path needs none — the dead
// marker is the census law there). kind 1..5 live law (S59 L4/A4), owner
// race index <= 20 (roster size, species.md), inv cap 1..25 (ring span).
bool saneShip(const uint8_t* r) {
    const uint8_t kind = r[0x58];
    const uint8_t owner = r[0x56];
    const uint32_t cap = rd32(r + 0x15a);
    if (kind < 1 || kind > 5) return false;
    if (owner > 20) return false;
    if (cap < 1 || cap > 25) return false;
    if (!saneF32(rdf(r + 0x9e)) || !saneF32(rdf(r + 0xa2)) || !saneF32(rdf(r + 0xa6)))
        return false;
    return true;
}

// Fill one Record from a 0x162 window. Field set == parseShipRecords (t360)
// verbatim so BOTH paths hand Ship::fromRecord identical shapes.
void fillRecord(const uint8_t* r, int slot, formats::ShipSave::Record& rec) {
    rec.slot = uint8_t(slot);
    rec.ownerHandle = rd32(r + 0x54);
    rec.dead = (rec.ownerHandle >> 16) == 0xffff;  // r256c oc_of marker
    rec.weaponLevel = rd32(r + 0x00);
    rec.shieldLevel = rd32(r + 0x04);
    rec.laneStepX = rd32(r + 0x08);
    rec.laneStepZ = rd32(r + 0x0c);
    rec.driveTotal = rd32(r + 0x10);
    rec.hullBaseDrive = rd32(r + 0x14);
    rec.powerMax = rd32(r + 0x18);
    rec.cat2PowerCarry = rd32(r + 0x1c);
    rec.scannerTotal = rd32(r + 0x20);
    rec.specialCount = rd32(r + 0x24);
    rec.targetSlot = rd32(r + 0x28);
    rec.playerDesign = r[0x31];
    rec.ownerRace = r[0x56];
    rec.orderKind = r[0x58];
    rec.orderTarget = rd32(r + 0x59);
    rec.actEnum = r[0x5d];
    rec.actTarget = rd32(r + 0x5e);
    rec.resolverFlag = r[0x62];
    rec.gizmoSlotPtr = rd32(r + 0x63);
    rec.orderType = r[0x67];
    rec.orderPayload = rd32(r + 0x68);
    for (int i = 0; i < 3; ++i) rec.absTriple[i] = rdf(r + 0x6c + 4 * i);
    rec.power = rd32(r + 0x88);
    rec.integrity = rd32(r + 0x8c);
    rec.shields = rd32(r + 0x90);
    rec.moves = rd32(r + 0x94);
    rec.maxIntegrity = rd32(r + 0x98);
    rec.statusFlags = rd16(r + 0x9c);
    for (int i = 0; i < 3; ++i) rec.pos[i] = rdf(r + 0x9e + 4 * i);
    rec.hullKind = r[0xaa];
    rec.ringCidx.assign(formats::ShipSave::kRingSlots, 0xFF);
    for (uint32_t i = 0; i < formats::ShipSave::kRingSlots; ++i)
        rec.ringCidx[i] = r[0xab + 7 * i];
    rec.invCap = rd32(r + 0x15a);
    rec.filled = rd32(r + 0x15e);
}

std::string cp437Name(const uint8_t* p, int cap) {
    std::string s;
    for (int i = 0; i < cap && p[i]; ++i)
        s += (p[i] >= 0x20 && p[i] < 0x7f) ? char(p[i]) : '?';
    return s;
}

}  // namespace

uint32_t Observer::rawDay(const std::vector<uint8_t>& file) {
    if (file.size() < 4) return 0;
    return rd32(file.data());  // u32@0 = game-day law (4/4 corpus saves)
}

bool Observer::parseRawShipBlock(const std::vector<uint8_t>& file,
                                 std::vector<ShipRow>* out, std::string* err) {
    constexpr uint32_t S = kRawShipStride;
    const size_t n = file.size();
    if (n < size_t(12) * S) {
        if (err) *err = "file too small for a ship block";
        return false;
    }
    // Content-based discovery: a chain start is any home h where the marker
    // at h-4 reads a slot id, and walking strictly-ascending markers over
    // sane records yields >= 12 entries. (A hard-coded offset was REFUTED by
    // measurement: block homes shift between saves, _wip_t382.)
    const uint8_t* d = file.data();
    for (size_t h = 4; h + size_t(12) * S <= n; ++h) {
        uint32_t m0 = rd32(d + h - 4);
        if (m0 >= formats::ShipSave::kArraySlots) continue;
        if (!saneShip(d + h)) continue;
        // quick chain filter before the full walk
        if (rd32(d + h + S - 4) <= m0) continue;
        std::vector<std::pair<uint32_t, size_t>> chain;
        int32_t prev = -1;
        for (size_t p = h; p + 0x162 <= n;) {
            uint32_t mk = rd32(d + p - 4);
            if (mk >= formats::ShipSave::kArraySlots || int32_t(mk) <= prev) break;
            if (!saneShip(d + p)) break;
            chain.emplace_back(mk, p);
            prev = int32_t(mk);
            p += S;
        }
        if (chain.size() < 12) continue;
        out->clear();
        for (const auto& [slot, home] : chain) {
            ShipRow row;
            fillRecord(d + home, int(slot), row.rec);
            row.name = cp437Name(d + home + 0x34, 16);
            // Raw path: +0x59 is save-space rewritten (pointer region diff
            // class, _wip_t382) — NO deref, targetStar stays -1.
            out->push_back(std::move(row));
        }
        return true;
    }
    if (err) *err = "no ship-record marker chain found (not a native .SAV?)";
    return false;
}

bool Observer::parseRawStarBlock(const std::vector<uint8_t>& file,
                                 std::vector<StarRow>* out, std::string* err) {
    const uint8_t* d = file.data();
    const size_t n = file.size();
    for (size_t h = 0; h + kStarStride <= n; ++h) {
        if (!saneStar(d + h)) continue;
        // Confirm a run of >= 10 consecutive sane records before believing
        // (a lone sane 96-byte window is coincidence-prone).
        size_t end = h;
        while (end + kStarStride <= n && saneStar(d + end)) end += kStarStride;
        if ((end - h) / kStarStride < 10) continue;
        // Extend backwards.
        size_t start = h;
        while (start >= kStarStride && saneStar(d + start - kStarStride))
            start -= kStarStride;
        out->clear();
        int slot = 0;
        for (size_t p = start; p < end; p += kStarStride, ++slot) {
            StarRow s;
            s.slot = slot;
            s.typeK = rd32(d + p);
            s.pos[0] = rdf(d + p + 0x08);
            s.pos[1] = rdf(d + p + 0x0c);
            s.pos[2] = rdf(d + p + 0x10);
            s.owner = d[p + 0x14];
            s.name = cp437Name(d + p + kStarNameX, 24);
            out->push_back(std::move(s));
        }
        return true;
    }
    if (err) *err = "no star-slot table found (not a native .SAV?)";
    return false;
}

bool Observer::importSavestate(const std::string& path,
                               const std::vector<uint8_t>& payload,
                               uint32_t* day, std::vector<StarRow>* stars,
                               std::vector<ShipRow>* ships, std::string* err) {
    using formats::ShipSave;
    std::vector<uint8_t> mem;
    if (!ShipSave::readMemoryMember(path, &mem, err)) return false;
    size_t base = 0;
    if (payload.empty()) {
        if (err) *err = "payload image required for the base vote (work/ascend_payload.bin)";
        return false;
    }
    auto anch = ShipSave::buildAnchors(payload);
    if (!ShipSave::findImageBase(mem, anch, 5, &base, err)) return false;
    const size_t B = base;
    const size_t ds = B + ShipSave::kDataSeg;
    if (ds + 0x16146 > mem.size()) {
        if (err) *err = "member too small for the star count word";
        return false;
    }
    if (day) *day = ShipSave::turnCounter(mem, B);
    const uint32_t T = rd16(&mem[ds + 0x16145]);
    if (T == 0 || T > 100) {
        if (err) *err = "star count " + std::to_string(T) + " out of ladder range";
        return false;
    }
    stars->clear();
    for (uint32_t i = 0; i < T; ++i) {
        const uint8_t* r = &mem[ds + 0x13bc5 + size_t(i) * kStarStride];
        if (size_t(r - mem.data()) + kStarStride > mem.size()) {
            if (err) *err = "star window past end of member";
            return false;
        }
        StarRow s;
        s.slot = int(i);
        s.typeK = rd32(r);
        s.pos[0] = rdf(r + 0x08);
        s.pos[1] = rdf(r + 0x0c);
        s.pos[2] = rdf(r + 0x10);
        s.owner = r[0x14];
        s.name = cp437Name(r + kStarNameX, 24);
        stars->push_back(std::move(s));
    }
    std::vector<ShipSave::Record> recs;
    if (!ShipSave::parseShipRecords(mem, B, &recs, err)) return false;
    ships->clear();
    for (const auto& rec : recs) {
        if (rec.dead) continue;  // S59 L2 census filter
        ShipRow row;
        row.rec = rec;
        row.name = cp437Name(&mem[ShipSave::kDataSeg + B + ShipSave::kShipArrayX +
                                      size_t(rec.slot) * ShipSave::kRecordStride + 0x34],
                             16);
        // kind-4 star attribution: +0x59 guest-PHYSICAL -> member = phys +
        // 0x88 (t298 MEMBER LAW: member = physical + 0x88, i.e. physical =
        // member - 88; r1_t190 header) lands on the star-slot record;
        // recover the slot by address (exact division), verified 19/19 on
        // ring 60 (_wip_t382 S4).
        if (rec.orderKind == 4) {
            const size_t member = size_t(rec.orderTarget) + 0x88;
            const size_t tbl = ds + 0x13bc5;
            if (member >= tbl && (member - tbl) % kStarStride == 0) {
                const size_t idx = (member - tbl) / kStarStride;
                if (idx < T) row.targetStar = int(idx);
            }
        }
        ships->push_back(std::move(row));
    }
    return true;
}

ShipSim Observer::buildSim(uint32_t day, const std::vector<StarRow>& stars,
                           const std::vector<ShipRow>& ships) {
    ShipSim sim(1, int(day));
    for (const StarRow& s : stars) {
        SimStar st;
        st.id = s.slot;
        st.pos[0] = s.pos[0];
        st.pos[1] = s.pos[1];
        st.pos[2] = s.pos[2];
        sim.addStar(st);
    }
    for (const ShipRow& row : ships)
        sim.addShip(Ship::fromRecord(row.rec, int(day)));  // t361 import
    return sim;
}

std::string Observer::renderMap(const std::vector<float>& xs,
                                const std::vector<float>& zs,
                                const std::vector<char>& glyphs, int cols,
                                int rows) {
    if (xs.empty() || xs.size() != glyphs.size()) return "(nothing to plot)\n";
    float x0 = *std::min_element(xs.begin(), xs.end());
    float x1 = *std::max_element(xs.begin(), xs.end());
    float z0 = *std::min_element(zs.begin(), zs.end());
    float z1 = *std::max_element(zs.begin(), zs.end());
    if (x1 - x0 < 1.f) { x0 -= 1.f; x1 += 1.f; }
    if (z1 - z0 < 1.f) { z0 -= 1.f; z1 += 1.f; }
    std::vector<std::vector<char>> grid(size_t(rows), std::vector<char>(size_t(cols), '.'));
    for (size_t i = 0; i < xs.size(); ++i) {
        int cx = int((xs[i] - x0) / (x1 - x0) * float(cols - 1));
        int cz = int((zs[i] - z0) / (z1 - z0) * float(rows - 1));
        char& cell = grid[size_t(cz)][size_t(cx)];
        if (cell == '.')
            cell = glyphs[i];
        else if (cell != glyphs[i])
            cell = '@';  // collision marker (star + ship in one cell)
    }
    std::ostringstream os;
    os << "x " << x0 << " .. " << x1 << "   z " << z0 << " .. " << z1 << "\n";
    for (const auto& line : grid) {
        for (char c : line) os << c;
        os << '\n';
    }
    return os.str();
}

}  // namespace ascend::game
