// SPDX-License-Identifier: GPL-3.0-or-later

// t360 per-ship SAVE PARSER (read-side) pins — docs/re/_wip_t360.md S2
// (MEASURED 2026-11-09 on the production ring work/r1/playcap/save/41..60.sav)
// + build contract docs/re/pership-spec.md §0/§1/§6. Read-side only: this
// test opens saves READ ONLY and asserts the parse against the banked census.
// NO OQ row closes on these facts (strict-close lives in the ledger, not here).
#include "formats/shipsave.h"
#include "harness.h"

#include <algorithm>
#include <cstdio>
#include <filesystem>
#include <fstream>
#include <map>
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

std::vector<std::string> ringSaves() {
    std::vector<std::string> out;
    fs::directory_iterator end;
    for (fs::directory_iterator it(kRepo + "/work/r1/playcap/save"); it != end; ++it) {
        auto p = it->path().string();
        if (it->is_regular_file() && p.size() > 4 && p.substr(p.size() - 4) == ".sav")
            out.push_back(p);
    }
    std::sort(out.begin(), out.end());
    return out;
}

// One save parsed end-to-end through the new API.
struct Parsed {
    bool ok = false;
    size_t base = 0;
    uint32_t turn = 0;
    uint32_t count = 0;
    std::vector<ShipSave::Record> recs;
};

Parsed parseOne(const std::string& path) {
    Parsed p;
    std::vector<uint8_t> mem;
    std::string err;
    if (!ShipSave::readMemoryMember(path, &mem, &err)) {
        std::printf("  %s: readMemoryMember failed: %s\n", path.c_str(), err.c_str());
        return p;
    }
    std::vector<uint8_t> payload;
    {
        std::ifstream f(kRepo + "/work/ascend_payload.bin", std::ios::binary);
        payload.assign(std::istreambuf_iterator<char>(f), std::istreambuf_iterator<char>());
    }
    auto anch = ShipSave::buildAnchors(payload);
    if (!ShipSave::findImageBase(mem, anch, 5, &p.base, &err)) {
        std::printf("  %s: findImageBase failed: %s\n", path.c_str(), err.c_str());
        return p;
    }
    p.turn = ShipSave::turnCounter(mem, p.base);
    p.count = ShipSave::countWord(mem, p.base);
    if (!ShipSave::parseShipRecords(mem, p.base, &p.recs, &err)) {
        std::printf("  %s: parseShipRecords failed: %s\n", path.c_str(), err.c_str());
        return p;
    }
    p.ok = true;
    return p;
}

uint64_t fnv1a64(const uint8_t* p, size_t n) {
    uint64_t h = 0xcbf29ce484222325ull;
    for (size_t i = 0; i < n; ++i) {
        h ^= p[i];
        h *= 0x100000001b3ull;
    }
    return h;
}

// Full-window live census of one parse (window 0..0x6a, dead rows excluded).
struct Census {
    uint32_t live = 0, dead = 0, beyond = 0;
    std::map<uint8_t, uint32_t> kinds, owners, caps;
};
Census censusOf(const Parsed& p) {
    Census c;
    for (const auto& r : p.recs) {
        if (r.dead) { ++c.dead; continue; }
        ++c.live;
        ++c.kinds[r.orderKind];
        ++c.owners[r.ownerRace];
        ++c.caps[r.invCap];
        if (r.slot >= p.count) ++c.beyond;
    }
    return c;
}

}  // namespace

TEST(shipsave_reader_and_base_vote_t360) {
    if (!fs::exists(kRepo + "/work/ascend_payload.bin") ||
        !fs::is_directory(kRepo + "/work/r1/playcap/save")) {
        std::printf("(skip: work/ corpus absent) ");
        return;
    }
    auto saves = ringSaves();
    CHECK(saves.size() >= 10);
    std::vector<uint8_t> payload;
    {
        std::ifstream f(kRepo + "/work/ascend_payload.bin", std::ios::binary);
        payload.assign(std::istreambuf_iterator<char>(f),
                       std::istreambuf_iterator<char>());
    }
    auto anch = ShipSave::buildAnchors(payload);
    CHECK(anch.size() >= 5);
    size_t ok = 0, torn = 0;
    for (const auto& s : saves) {
        std::vector<uint8_t> mem, mem2;
        std::string err;
        // RING-WRITER RACE (t369): a slot caught mid-rewrite by the 10 s
        // autosave rotation is not a reader failure — skip it (idempotence
        // of the READER is pinned on every slot that was whole).
        if (!ShipSave::readMemoryMember(s, &mem, &err) ||
            !ShipSave::readMemoryMember(s, &mem2, &err) || mem != mem2) {
            ++torn;
            continue;
        }
        CHECK(mem.size() == 17055880u);  // memsize=16 law (r1_sav_scan header)
        size_t B = 0;
        if (ShipSave::findImageBase(mem, anch, 5, &B, &err)) ++ok;
    }
    if (torn) std::printf("(torn ring slots skipped: %zu) ", torn);
    CHECK(ok + torn == saves.size());
    CHECK(ok >= 10);
    // Negative control: a truncated member must not vote a base.
    std::vector<uint8_t> tiny(1 << 20, 0);
    size_t B = 1;
    CHECK(!ShipSave::findImageBase(tiny, anch, 5, &B, nullptr));
    // Negative control: window past end of member is refused, not clamped.
    std::vector<uint8_t> stub(4096, 0);
    std::vector<ShipSave::Record> recs;
    CHECK(!ShipSave::parseShipRecords(stub, 0, &recs, nullptr));
}

TEST(shipsave_corpus_law_pins_t360) {
    // Laws that hold in ANY in-game campaign state (banked derivations:
    // attr t273, dead marker r256c oc_of, kind subset spec A4, dead-row shape
    // uniformity _wip_t360 S2). Run unconditionally on every readable save.
    if (!fs::exists(kRepo + "/work/ascend_payload.bin") ||
        !fs::is_directory(kRepo + "/work/r1/playcap/save")) {
        std::printf("(skip: work/ corpus absent) ");
        return;
    }
    uint64_t liveRows = 0, attrOk = 0, deadWithInv = 0;
    for (const auto& s : ringSaves()) {
        Parsed p = parseOne(s);
        if (!p.ok) continue;
        CHECK(p.turn >= 1 && p.turn <= 4000);  // in-game gate law
        CHECK(p.recs.size() == ShipSave::kArraySlots);
        for (const auto& r : p.recs) {
            if (r.dead) {
                CHECK(r.ownerHandle == 0xffff0000u);
                CHECK(r.orderKind == 0);
                // t360 dead-row SHAPE UNIFORMITY (invCap==5, filled==0) IS
                // RETRACTED — falsified by the 2026-11-11 user playtest: a
                // slot killed IN PLAY keeps its inventory (work/r1/
                // bank-play-20261111-late slot 12: handle 0xffff0000, kind 0,
                // invCap 10, filled 10). The old corpus only ever held
                // never-used slots. Death does NOT clear +0x15a/+0x15e.
                // What still holds: the ring span law.
                CHECK(r.invCap <= ShipSave::kRingSlots);
                if (r.invCap > 5u || r.filled > 0u) ++deadWithInv;
                continue;
            }
            ++liveRows;
            if ((r.ownerHandle >> 16) == r.ownerRace) ++attrOk;
            CHECK(r.orderKind >= 1 && r.orderKind <= 5);  // A4 live subset
            CHECK(r.invCap <= ShipSave::kRingSlots);      // ring span law: 0xab+7*25==0x15a
        }
    }
    CHECK(liveRows > 0);
    CHECK(attrOk == liveRows);  // t273 attribution law, corpus-wide
    if (deadWithInv)
        std::printf("(dead rows retaining inventory: %llu) ",
                    (unsigned long long)deadWithInv);
}

TEST(shipsave_frozen_ring_t1086_exact_t360) {
    // EXACT match against the banked census (_wip_t360 S2) — valid ONLY while
    // the production ring still holds turn 1086 (the state the census measured;
    // the whole 0x6b-slot window was byte-identical across 41..60.sav). If the
    // user has played on, turn differs and this case self-skips: the law test
    // above is the durable one.
    if (!fs::exists(kRepo + "/work/ascend_payload.bin") ||
        !fs::is_directory(kRepo + "/work/r1/playcap/save")) {
        std::printf("(skip: work/ corpus absent) ");
        return;
    }
    int pinned = 0;
    std::string pinnedSlot;
    for (const auto& s : ringSaves()) {
        Parsed p = parseOne(s);
        if (!p.ok || p.turn != 1086) continue;
        ++pinned;
        pinnedSlot = s;
        CHECK(p.base == 0x1bf4d8u);   // MEASURED 20/20
        CHECK(p.count == 30u);        // MEASURED 20/20 (and NOT the census: see below)
        Census c = censusOf(p);
        CHECK(c.live == 30u);         // live records exceed the count word...
        CHECK(c.beyond == 4u);        // ...4 of them at indices >= 30 (ships.md item 3)
        CHECK(c.dead == 77u);         // 107 - 30
        using Hist = std::map<uint8_t, uint32_t>;
        Hist wantKinds{{3, 4}, {4, 3}, {5, 23}};
        Hist wantOwners{{0, 14}, {1, 7}, {2, 9}};
        Hist wantCaps{{10, 25}, {15, 1}, {25, 4}};
        CHECK(c.kinds == wantKinds);
        CHECK(c.owners == wantOwners);
        CHECK(c.caps == wantCaps);
        // filled == occupiedExclusive on every live row (600/600 corpus-wide;
        // the DISPUTED inclusive reading is the cap-word self-read artifact,
        // asserted next on cap==25 rows).
        for (const auto& r : p.recs) {
            if (r.dead) continue;
            CHECK(r.filled == r.occupiedExclusive());
        }
    }
    if (pinned == 0) { std::printf("(skip: ring no longer at turn 1086) "); return; }
    // RING-WRITER RACE FIX (t369): pin against ONE slot captured during the
    // loop above (pinnedSlot), read ONCE. The old code re-listed
    // ringSaves().front() per record — front is the oldest-mtime slot, i.e.
    // the one the 10 s ring writer is rewriting, so the gate raced torn ZIPs
    // AND the slot identity drifted mid-test. The byte pins below held on ALL
    // 20 slots when measured (_wip_t360 S2), so slot choice is law-neutral.
    Parsed p = parseOne(pinnedSlot);
    CHECK(p.ok);
    std::vector<uint8_t> mem;
    std::string err;
    CHECK(ShipSave::readMemoryMember(pinnedSlot, &mem, &err));
    // Ring-boundary artifact pin (layout law, _wip_t360 S2): the stride-7 probe
    // at slot index == cap on a cap==25 row lands on the cap dword's low byte.
    for (const auto& r : p.recs) {
        if (r.dead || r.invCap != 25) continue;
        size_t arr = p.base + ShipSave::kDataSeg + ShipSave::kShipArrayX;
        uint8_t probe = mem[arr + size_t(r.slot) * ShipSave::kRecordStride + 0xab +
                            7 * 25];
        CHECK(probe == uint8_t(r.invCap & 0xff));  // == 25, never 0xFF: the artifact
    }
    // Whole-window byte pin: md5 54bea6e3e9cd66236dd3ff0d6ba34738 / FNV-1a 64
    // 0x3acb4b625a289f54 over 0x6b*0x162 = 37878 B (Python cross-check
    // _wip_t360 S2; identical on all 20 ring saves).
    size_t arr = p.base + ShipSave::kDataSeg + ShipSave::kShipArrayX;
    CHECK(fnv1a64(mem.data() + arr, size_t(ShipSave::kArraySlots) * ShipSave::kRecordStride) ==
          0x3acb4b625a289f54ull);
}
