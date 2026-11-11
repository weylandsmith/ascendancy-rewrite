// SPDX-License-Identifier: GPL-3.0-or-later

#include "formats/shipsave.h"

#include <zlib.h>

#include <cstdio>
#include <cstring>
#include <map>

namespace ascend::formats {

uint32_t ShipSave::Record::occupiedExclusive() const {
    uint32_t n = invCap < kRingSlots ? invCap : kRingSlots;
    uint32_t occ = 0;
    for (uint32_t i = 0; i < n && i < ringCidx.size(); ++i)
        if (ringCidx[i] != 0xFF) ++occ;
    return occ;
}

namespace {

uint16_t rd16(const uint8_t* p) { return uint16_t(p[0]) | (uint16_t(p[1]) << 8); }
uint32_t rd32(const uint8_t* p) {
    return uint32_t(p[0]) | (uint32_t(p[1]) << 8) | (uint32_t(p[2]) << 16) |
           (uint32_t(p[3]) << 24);
}
float rdf(const uint8_t* p) {
    uint32_t u = rd32(p);
    float f;
    std::memcpy(&f, &u, 4);
    return f;
}

}  // namespace

bool ShipSave::readMemoryMember(const std::string& path,
                                std::vector<uint8_t>* mem, std::string* err) {
    // Minimal ZIP reader: End Of Central Directory -> central directory ->
    // the 'Memory' entry's local header -> stored or raw-deflate body.
    // (dosbox-x writes method=8; method 0 accepted defensively.)
    FILE* fp = std::fopen(path.c_str(), "rb");
    if (!fp) {
        if (err) *err = "open failed: " + path;
        return false;
    }
    std::vector<uint8_t> all;
    {
        uint8_t buf[65536];
        size_t got;
        while ((got = std::fread(buf, 1, sizeof(buf), fp)) > 0)
            all.insert(all.end(), buf, buf + got);
    }
    std::fclose(fp);

    // Scan backwards for EOCD signature 0x06054b50 (last 64 KiB + min size).
    long eocd = -1;
    size_t lo = all.size() > 65536 + 22 ? all.size() - 65536 - 22 : 0;
    for (size_t i = all.size(); i-- > lo;) {
        if (i + 22 <= all.size() && rd32(&all[i]) == 0x06054b50u) { eocd = long(i); break; }
    }
    if (eocd < 0) {
        if (err) *err = "no EOCD (not a ZIP): " + path;
        return false;
    }
    uint16_t nEntries = rd16(&all[eocd + 10]);
    uint32_t cdOff = rd32(&all[eocd + 16]);
    if (cdOff + 22 > all.size()) {
        if (err) *err = "central directory out of range";
        return false;
    }
    size_t p = cdOff;
    for (uint16_t e = 0; e < nEntries; ++e) {
        if (p + 46 > all.size() || rd32(&all[p]) != 0x02014b50u) {
            if (err) *err = "central directory corrupt";
            return false;
        }
        uint16_t method = rd16(&all[p + 10]);
        uint32_t csize = rd32(&all[p + 20]);
        uint32_t usize = rd32(&all[p + 24]);
        uint16_t nameLen = rd16(&all[p + 28]);
        uint16_t extraLen = rd16(&all[p + 30]);
        uint16_t cmtLen = rd16(&all[p + 32]);
        uint32_t lho = rd32(&all[p + 42]);
        std::string name(reinterpret_cast<const char*>(&all[p + 46]), nameLen);
        p += 46 + nameLen + extraLen + cmtLen;
        if (name != "Memory") continue;
        if (lho + 30 > all.size() || rd32(&all[lho]) != 0x04034b50u) {
            if (err) *err = "Memory local header corrupt";
            return false;
        }
        uint16_t lName = rd16(&all[lho + 26]);
        uint16_t lExtra = rd16(&all[lho + 28]);
        size_t data = lho + 30 + lName + lExtra;
        if (data + csize > all.size()) {
            if (err) *err = "Memory data out of range";
            return false;
        }
        mem->assign(usize, 0);
        if (method == 0) {
            if (csize != usize) {
                if (err) *err = "stored member size mismatch";
                return false;
            }
            std::memcpy(mem->data(), &all[data], usize);
            return true;
        }
        if (method != 8) {
            if (err) *err = "unsupported ZIP method " + std::to_string(method);
            return false;
        }
        z_stream zs{};
        if (inflateInit2(&zs, -MAX_WBITS) != Z_OK) {
            if (err) *err = "inflateInit2 failed";
            return false;
        }
        zs.next_in = const_cast<Bytef*>(&all[data]);
        zs.avail_in = csize;
        zs.next_out = mem->data();
        zs.avail_out = uInt(usize);
        int r = inflate(&zs, Z_FINISH);
        size_t produced = usize - zs.avail_out;
        inflateEnd(&zs);
        if (r != Z_STREAM_END || produced != usize) {
            if (err) *err = "inflate failed (r=" + std::to_string(r) +
                            ", produced " + std::to_string(produced) +
                            " != " + std::to_string(usize) + ")";
            return false;
        }
        return true;
    }
    if (err) *err = "no Memory member in ZIP";
    return false;
}

std::vector<std::pair<size_t, std::vector<uint8_t>>>
ShipSave::buildAnchors(const std::vector<uint8_t>& payload) {
    // Verbatim port of r1_sav_scan.build_anchors: 128-byte windows at 16 KiB
    // stride with >40 distinct byte values and w.strip(b"\x00") == w. NOTE
    // (t360 port trap, _wip_t360 S4): Python strip() removes END bytes only,
    // so the zero law is "no zero at first/last byte" — MIDDLE zeros pass.
    // An anywhere-zero early-break yields 0 anchors vs Python's 12.
    std::vector<std::pair<size_t, std::vector<uint8_t>>> anch;
    for (size_t p = 0; p + 128 <= payload.size(); p += 0x4000) {
        const uint8_t* w = &payload[p];
        if (w[0] == 0 || w[127] == 0) continue;  // strip() end-semantics
        int hist[256] = {0};
        for (int i = 0; i < 128; ++i) ++hist[w[i]];
        int distinct = 0;
        for (int v : hist) distinct += v != 0;
        if (distinct > 40) anch.emplace_back(p, std::vector<uint8_t>(w, w + 128));
    }
    return anch;
}

bool ShipSave::findImageBase(const std::vector<uint8_t>& mem,
                             const std::vector<std::pair<size_t, std::vector<uint8_t>>>& anchors,
                             uint32_t minVotes, size_t* base, std::string* err) {
    // find_base port: an anchor votes (hit_position - payload_offset) only if
    // it occurs EXACTLY once in mem (ambiguous windows don't vote).
    std::map<long, uint32_t> votes;
    for (const auto& a : anchors) {
        size_t hits = 0, first = 0;
        const uint8_t* hay = mem.data();
        const uint8_t* needle = a.second.data();
        for (size_t i = 0; i + 128 <= mem.size(); ++i) {
            if (hay[i] != needle[0]) continue;
            if (std::memcmp(hay + i, needle, 128) == 0) {
                ++hits;
                first = i;
                if (hits > 5) break;  // bounded: already ambiguous
            }
        }
        if (hits == 1) votes[long(first) - long(a.first)] += 1;
    }
    long best = 0;
    uint32_t bestVotes = 0;
    for (const auto& kv : votes)
        if (kv.second > bestVotes) { bestVotes = kv.second; best = kv.first; }
    if (bestVotes >= minVotes) {
        *base = size_t(best);
        return true;
    }
    if (err) *err = "base vote too weak (" + std::to_string(bestVotes) +
                    " < " + std::to_string(minVotes) + ")";
    return false;
}

namespace {

void wr16(uint8_t* p, uint16_t v) { p[0] = uint8_t(v); p[1] = uint8_t(v >> 8); }
void wr32(uint8_t* p, uint32_t v) {
    p[0] = uint8_t(v); p[1] = uint8_t(v >> 8); p[2] = uint8_t(v >> 16);
    p[3] = uint8_t(v >> 24);
}
void wrf(uint8_t* p, float f) {
    uint32_t u;
    std::memcpy(&u, &f, 4);
    wr32(p, u);
}

}  // namespace

void ShipSave::serializeRecord(const Record& rec, uint8_t* r) {
    // CITED-ONLY PATCH LAW (_wip_t366 S3, header): store EXACTLY the parser's
    // field set; unmodelled stride gaps keep their existing bytes. The dead
    // marker is NOT special-cased — a dead Record carries the vendor
    // (kind,cap,filled)==(0,5,0) shape verbatim (S59 L2) and round-trips like
    // any row.
    wr32(r + 0x00, rec.weaponLevel);
    wr32(r + 0x04, rec.shieldLevel);
    wr32(r + 0x08, rec.laneStepX);
    wr32(r + 0x0c, rec.laneStepZ);
    wr32(r + 0x10, rec.driveTotal);
    wr32(r + 0x14, rec.hullBaseDrive);
    wr32(r + 0x18, rec.powerMax);
    wr32(r + 0x1c, rec.cat2PowerCarry);
    wr32(r + 0x20, rec.scannerTotal);
    wr32(r + 0x24, rec.specialCount);
    wr32(r + 0x28, rec.targetSlot);
    r[0x31] = rec.playerDesign;
    wr32(r + 0x54, rec.ownerHandle);
    r[0x56] = rec.ownerRace;
    r[0x58] = rec.orderKind;
    wr32(r + 0x59, rec.orderTarget);
    r[0x5d] = rec.actEnum;
    wr32(r + 0x5e, rec.actTarget);
    r[0x62] = rec.resolverFlag;
    wr32(r + 0x63, rec.gizmoSlotPtr);
    r[0x67] = rec.orderType;
    wr32(r + 0x68, rec.orderPayload);
    for (int i = 0; i < 3; ++i) wrf(r + 0x6c + 4 * i, rec.absTriple[i]);
    wr32(r + 0x88, rec.power);
    wr32(r + 0x8c, rec.integrity);
    wr32(r + 0x90, rec.shields);
    wr32(r + 0x94, rec.moves);
    wr32(r + 0x98, rec.maxIntegrity);
    wr16(r + 0x9c, rec.statusFlags);
    for (int i = 0; i < 3; ++i) wrf(r + 0x9e + 4 * i, rec.pos[i]);
    r[0xaa] = rec.hullKind;
    for (uint32_t i = 0; i < kRingSlots && i < rec.ringCidx.size(); ++i)
        r[0xab + 7 * i] = rec.ringCidx[i];
    wr32(r + 0x15a, rec.invCap);
    wr32(r + 0x15e, rec.filled);
}

bool ShipSave::writeShipRecords(std::vector<uint8_t>* mem, size_t base,
                                const std::vector<Record>& recs,
                                std::string* err) {
    size_t arr = base + kDataSeg + kShipArrayX;
    if (arr + size_t(kArraySlots) * kRecordStride > mem->size()) {
        if (err) *err = "ship window past end of Memory member";
        return false;
    }
    if (recs.size() != kArraySlots) {
        if (err) *err = "expected exactly kArraySlots records, got " +
                        std::to_string(recs.size());
        return false;
    }
    for (uint32_t k = 0; k < kArraySlots; ++k)
        serializeRecord(recs[k], mem->data() + arr + size_t(k) * kRecordStride);
    return true;
}

void ShipSave::rebaseRecord(Record* rec, uint32_t delta) {
    if (delta == 0) return;  // same-run write-back is a no-op
    // t298 POINTER-VALUE LAW: these three stored u32s are guest-PHYSICAL
    // addresses; a run whose image base moved by `delta` shifts them by the
    // SAME delta. Every other field is a value, not an address.
    rec->orderTarget += delta;
    rec->gizmoSlotPtr += delta;
    rec->orderPayload += delta;
}

uint32_t ShipSave::countWord(const std::vector<uint8_t>& mem, size_t base) {
    return rd32(&mem[base + kDataSeg + kCountX]) >> 16;
}

uint32_t ShipSave::turnCounter(const std::vector<uint8_t>& mem, size_t base) {
    return rd32(&mem[base + kDataSeg + kTurnX]);
}

bool ShipSave::parseShipRecords(const std::vector<uint8_t>& mem, size_t base,
                                std::vector<Record>* out, std::string* err) {
    size_t arr = base + kDataSeg + kShipArrayX;
    if (arr + size_t(kArraySlots) * kRecordStride > mem.size()) {
        if (err) *err = "ship window past end of Memory member";
        return false;
    }
    out->clear();
    out->resize(kArraySlots);
    for (uint32_t k = 0; k < kArraySlots; ++k) {
        const uint8_t* r = mem.data() + arr + size_t(k) * kRecordStride;
        Record& rec = (*out)[k];
        rec.slot = uint8_t(k);
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
        rec.ringCidx.assign(kRingSlots, 0xFF);
        for (uint32_t i = 0; i < kRingSlots; ++i) rec.ringCidx[i] = r[0xab + 7 * i];
        rec.invCap = rd32(r + 0x15a);
        rec.filled = rd32(r + 0x15e);
    }
    return true;
}

}  // namespace ascend::formats
