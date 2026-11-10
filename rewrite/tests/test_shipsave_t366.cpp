// t366 per-ship SAVE WRITE-SIDE pins — pership-spec §6 S7 + _wip_t366.md.
//
// HONEST NOTE (the row's byte-compare leg): NO game-emitted vendor save with
// ship records can be produced headlessly here — the game's own save is
// UI-driven and the click path is cited-broken (REFUTED-ROUTES t261 / N8), and
// a second long-running capture is forbidden by the task contract. The only
// headlessly-produced saves are DOSBox-X savestate ZIPs ('Memory' == guest
// RAM snapshots). The shipped substitute is a REAL byte-compare against those
// vendor-saved bytes: parse -> write back -> the whole 17,055,880-byte member
// must be byte-identical (write-back idempotence), plus cited-only patch-law
// and rebase pins. Which fields round-trip: EXACTLY the parser's cited field
// set (shipsave.h); the writer never touches unmodelled gap bytes, so gaps
// keep whatever the vendor left (test 2 pins this). Engagement-transience of
// +0x62/+0x63 (t365 stance/gate/activeSlot) is a LAW reading, not a save-side
// observation — the churn census (scripts/r366_churn_census.py,
// work/r366_churn.out) shows zero churn there across the captured pairs
// because no captured save holds an in-combat-at-boundary ship.
#include "formats/shipsave.h"
#include "harness.h"

#include <algorithm>
#include <cstdio>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <vector>

namespace fs = std::filesystem;
using ascend::formats::ShipSave;

namespace {

const std::string kRepo =
#ifdef ASCENDANCY_SOURCE_DIR
    ASCENDANCY_SOURCE_DIR
#else
    "."
#endif
    ;

uint64_t fnv1a64(const uint8_t* p, size_t n) {
    uint64_t h = 0xcbf29ce484222325ull;
    for (size_t i = 0; i < n; ++i) {
        h ^= p[i];
        h *= 0x100000001b3ull;
    }
    return h;
}

std::vector<std::string> ringSaves() {
    std::vector<std::string> out;
    fs::directory_iterator end;
    for (fs::directory_iterator it(kRepo + "/work/r1/playcap/save"); it != end;
         ++it) {
        auto p = it->path().string();
        if (it->is_regular_file() && p.size() > 4 &&
            p.substr(p.size() - 4) == ".sav")
            out.push_back(p);
    }
    std::sort(out.begin(), out.end());
    return out;
}

// Synthetic record with distinct value per field (round-trip vehicle).
ShipSave::Record synthetic() {
    ShipSave::Record r;
    r.dead = false;
    r.weaponLevel = 0x11111111; r.shieldLevel = 0x22222222;
    r.laneStepX = 14; r.laneStepZ = 28;
    r.driveTotal = 3; r.hullBaseDrive = 2;
    r.powerMax = 40; r.cat2PowerCarry = 5;
    r.scannerTotal = 6; r.specialCount = 7; r.targetSlot = 8;
    r.playerDesign = 9;
    r.ownerHandle = 0x0002002a; r.ownerRace = 2;
    r.orderKind = 4; r.orderTarget = 0x0030abcd;
    r.actEnum = 1; r.actTarget = 0x0030ef01;
    r.resolverFlag = 3; r.gizmoSlotPtr = 0x00291234;
    r.orderType = 2; r.orderPayload = 0x00285678;
    r.absTriple[0] = 1.5f; r.absTriple[1] = -200.0f; r.absTriple[2] = 33.25f;
    r.power = 10; r.integrity = 55; r.shields = 44; r.moves = 2;
    r.maxIntegrity = 100; r.statusFlags = 0x0307;
    r.pos[0] = 123.5f; r.pos[1] = -6.5f; r.pos[2] = 0.0f;
    r.hullKind = 3;
    r.ringCidx.assign(ShipSave::kRingSlots, 0xFF);
    r.ringCidx[0] = 0x10; r.ringCidx[1] = 0x49; r.ringCidx[2] = 0x0c;
    r.invCap = 10; r.filled = 3;
    return r;
}

}  // namespace

TEST(shipsave_writeback_idempotent_t366) {
    if (!fs::exists(kRepo + "/work/ascend_payload.bin") ||
        !fs::is_directory(kRepo + "/work/r1/playcap/save")) {
        std::printf("(skip: work/ corpus absent) ");
        return;
    }
    std::vector<uint8_t> payload;
    {
        std::ifstream f(kRepo + "/work/ascend_payload.bin", std::ios::binary);
        payload.assign(std::istreambuf_iterator<char>(f),
                       std::istreambuf_iterator<char>());
    }
    auto anch = ShipSave::buildAnchors(payload);
    auto saves = ringSaves();
    CHECK(saves.size() >= 10);
    size_t ok = 0;
    for (const auto& s : saves) {
        std::vector<uint8_t> mem;
        std::string err;
        if (!ShipSave::readMemoryMember(s, &mem, &err)) continue;
        size_t B = 0;
        if (!ShipSave::findImageBase(mem, anch, 5, &B, &err)) continue;
        std::vector<ShipSave::Record> recs;
        if (!ShipSave::parseShipRecords(mem, B, &recs, &err)) continue;
        uint64_t before = fnv1a64(mem.data(), mem.size());
        CHECK(ShipSave::writeShipRecords(&mem, B, recs, &err));
        uint64_t after = fnv1a64(mem.data(), mem.size());
        // THE byte-compare vs vendor-saved bytes: identical whole member.
        if (before == after && mem.size() == 17055880u) ++ok;
        else std::printf("\n  %s: write-back diverged %016llx -> %016llx\n",
                         s.c_str(), (unsigned long long)before,
                         (unsigned long long)after);
        // Second pass: idempotence is stable, not oscillating.
        CHECK(ShipSave::writeShipRecords(&mem, B, recs, &err));
        CHECK(fnv1a64(mem.data(), mem.size()) == after);
    }
    CHECK(ok == saves.size());
}

TEST(shipsave_synthetic_roundtrip_and_patch_law_t366) {
    // Field-level round-trip through the rewrite (spec S7 fallback): serialize
    // a synthetic record into a patterned buffer, re-read it by hand at the
    // cited offsets, and assert the unmodelled gaps kept the pattern.
    std::vector<uint8_t> buf(ShipSave::kRecordStride, 0xa5);
    ShipSave::Record r = synthetic();
    ShipSave::serializeRecord(r, buf.data());
    auto rd32 = [&](size_t o) {
        return uint32_t(buf[o]) | (uint32_t(buf[o + 1]) << 8) |
               (uint32_t(buf[o + 2]) << 16) | (uint32_t(buf[o + 3]) << 24);
    };
    CHECK(rd32(0x00) == r.weaponLevel);
    CHECK(rd32(0x04) == r.shieldLevel);
    CHECK(rd32(0x08) == 14u);
    CHECK(rd32(0x0c) == 28u);
    CHECK(rd32(0x18) == 40u);
    CHECK(buf[0x31] == 9);
    CHECK(rd32(0x54) == 0x0002002au);
    CHECK(buf[0x56] == 2);
    CHECK(buf[0x58] == 4);
    CHECK(rd32(0x59) == 0x0030abcd);  // +0x59 is the u32 home (parser law)
    CHECK(buf[0x5d] == 1);
    CHECK(rd32(0x5e) == 0x0030ef01);
    CHECK(buf[0x62] == 3);
    CHECK(rd32(0x63) == 0x00291234);
    CHECK(buf[0x67] == 2);
    CHECK(rd32(0x68) == 0x00285678);
    CHECK(rd32(0x88) == 10u);
    CHECK(rd32(0x8c) == 55u);
    CHECK(rd32(0x9c) == 0x0307u);
    CHECK(buf[0xaa] == 3);
    CHECK(buf[0xab] == 0x10 && buf[0xab + 7] == 0x49 &&
          buf[0xab + 14] == 0x0c);
    CHECK(rd32(0x15a) == 10u);
    CHECK(rd32(0x15e) == 3u);
    // PATCH LAW: ring-slot stride 7 -> use-word/payload bytes stay patterned.
    CHECK(buf[0xab + 1] == 0xa5 && buf[0xab + 2] == 0xa5);
    CHECK(buf[0xab + 3] == 0xa5 && buf[0xab + 6] == 0xa5);
    // Gaps keep the pattern: +0x32..+0x53, +0x84..+0x87. (+0x0a is NOT a gap —
    // it is the third byte of the +0x08 laneStepX u32, which the parser also
    // reads as u32. +0xb0 IS a gap: slot 0 spans +0xab..+0xb1, byte +0xb0 is
    // its payload byte 2, unwritten.)
    for (size_t o = 0x32; o < 0x54; ++o) CHECK(buf[o] == 0xa5);
    CHECK(buf[0x84] == 0xa5 && buf[0x87] == 0xa5);
    CHECK(buf[0xb0] == 0xa5);   // slot-0 payload byte, preserved gap
    // floats verbatim (bit patterns incl negative and -0.0 class values)
    float got;
    uint32_t u = rd32(0x9e);
    std::memcpy(&got, &u, 4);
    CHECK(got == 123.5f);
    u = rd32(0x9e + 4);
    std::memcpy(&got, &u, 4);
    CHECK(got == -6.5f);
}

TEST(shipsave_rebase_and_refusals_t366) {
    // rebaseRecord shifts ONLY the three pointer-valued fields (t298 law;
    // delta = B_new - B_old per the CLOSED pointer law runtime = P0 + off).
    ShipSave::Record r = synthetic();
    ShipSave::Record orig = r;
    ShipSave::rebaseRecord(&r, 0);  // same-run no-op
    CHECK(r.orderTarget == orig.orderTarget);
    ShipSave::rebaseRecord(&r, 0x1000);
    CHECK(r.orderTarget == orig.orderTarget + 0x1000);
    CHECK(r.gizmoSlotPtr == orig.gizmoSlotPtr + 0x1000);
    CHECK(r.orderPayload == orig.orderPayload + 0x1000);
    // Non-pointer fields untouched by rebase.
    CHECK(r.integrity == orig.integrity);
    CHECK(r.ownerHandle == orig.ownerHandle);
    CHECK(r.statusFlags == orig.statusFlags);
    CHECK(r.ringCidx == orig.ringCidx);
    // Self-inverse: rebasing back restores the original record exactly.
    ShipSave::rebaseRecord(&r, uint32_t(0u - 0x1000u));
    CHECK(r.orderTarget == orig.orderTarget);
    CHECK(r.gizmoSlotPtr == orig.gizmoSlotPtr);
    CHECK(r.orderPayload == orig.orderPayload);

    // Refusals: window past member end; wrong record count.
    std::vector<uint8_t> stub(4096, 0);
    std::string err;
    CHECK(!ShipSave::writeShipRecords(&stub, 0, {}, &err));
    std::vector<ShipSave::Record> recs(ShipSave::kArraySlots);
    // Geometry-valid base in a buffer sized EXACTLY to the window (zero
    // slack): the boundary write must succeed (a >= mutant is caught here —
    // t366 M5 re-scope: with slack the exact-equality edge is unobservable).
    std::vector<uint8_t> big(ShipSave::kDataSeg + ShipSave::kShipArrayX +
                                 size_t(ShipSave::kArraySlots) *
                                     ShipSave::kRecordStride,
                             0);
    CHECK(ShipSave::writeShipRecords(&big, 0, recs, &err));
    // One byte past the boundary -> refused, not clamped (window would read
    // off the end by exactly 1).
    CHECK(!ShipSave::writeShipRecords(&big, 1, recs, &err));
    // Wrong record count at VALID geometry -> refused (full-window contract;
    // a partial emit would silently leave stale rows unaccounted).
    std::vector<ShipSave::Record> half(recs.begin(),
                                       recs.begin() + ShipSave::kArraySlots - 1);
    CHECK(!ShipSave::writeShipRecords(&big, 0, half, &err));
}
