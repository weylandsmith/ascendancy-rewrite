// SPDX-License-Identifier: GPL-3.0-or-later

// t379 DEATH vs RECLAIM SHAPE pins — the count-window law + the corrected
// C4 store set. Evidence: docs/re/_wip_t379.md S1..S6 (banks
// work/r1/bank-play-20261111/ t1253 vs bank-play-20261111-late/ t1254,
// 20/20 base-verified each, plus the production ring; law holds 60/60).
// THE MEASURED FACTS these pins encode:
//  * ONE end-of-life shape: the C4 in-place corpse (owner word +0x56 :=
//    0xffff, kind +0x58 := 0, name +0x34 NUL-stamped, act +0x5d := 0 — the
//    exact 5-word diff of slot 12 across the boundary; +0x90 := 0 in the
//    witness is UNATTRIBUTABLE (upkeep always zeroes it) and NOT wired).
//  * NO compaction: slot 40's whole 0x162 record is BYTE-IDENTICAL across
//    the boundary (sha256-verified) — the vendor never wrote it.
//  * count word == full-array LIVE CENSUS (41/41 then 40/40), so the walk
//    range(0,count) contains the corpse AND orphans the highest live record
//    (s40 'Intil-Za' at index 40 of a window of 40). The two queue-side
//    "shapes" (corpse-retained-flag vs slot-vanished) are this ONE law read
//    at two indices.
//  * DEATH RETAINS: order type (+0x67 2->2), order payload (+0x68
//    0x002589f6->same), pos, power 1, integrity 20, eta +0x52 1018, ring
//    cidx x10 AND ring use-words, cap 10 / filled 10 (M6 law at record
//    level). The pre-t379 finalizer cleared +0x62/+0x63/+0x68 — unwitnessed
//    hygiene; the pins below are the mutation isolators.
// Corpus pins skip honestly when work/ is absent (public clone).
#include "formats/shipsave.h"
#include "game/shipsim.h"
#include "harness.h"

#include <algorithm>
#include <cstdio>
#include <filesystem>
#include <fstream>
#include <utility>
#include <vector>

namespace fs = std::filesystem;
namespace as = ascend::game;
using ascend::formats::ShipSave;

namespace {

const std::string kBankEarly =
    std::string(ASCENDANCY_SOURCE_DIR) + "/work/r1/bank-play-20261111";
const std::string kBankLate =
    std::string(ASCENDANCY_SOURCE_DIR) + "/work/r1/bank-play-20261111-late";

std::vector<std::string> bankSaves(const std::string& dir) {
    std::vector<std::string> out;
    if (!fs::is_directory(dir)) return out;
    fs::directory_iterator end;
    for (fs::directory_iterator it(dir); it != end; ++it) {
        auto p = it->path().string();
        if (it->is_regular_file() && p.size() > 4 && p.substr(p.size() - 4) == ".sav")
            out.push_back(p);
    }
    std::sort(out.begin(), out.end());
    return out;
}

// Anchors are built from the STATIC payload image (t360 law: the anchor vote
// matches a known needle set, not the save's own bytes).
bool payloadAnchors(std::vector<uint8_t>* payload,
                    std::vector<std::pair<size_t, std::vector<uint8_t>>>* anch) {
    const std::string p =
        std::string(ASCENDANCY_SOURCE_DIR) + "/work/ascend_payload.bin";
    std::ifstream f(p, std::ios::binary);
    if (!f) return false;
    payload->assign(std::istreambuf_iterator<char>(f),
                    std::istreambuf_iterator<char>());
    *anch = ShipSave::buildAnchors(*payload);
    return !anch->empty();
}

// The sim-side fixture for the boundary: the MEASURED s12 (dies) and s40
// (orphaned) rows. Values verbatim from _wip_t379 S4/S5 (t1253 side).
as::Ship mkS12() {
    as::Ship s;
    s.id = 12; s.owner = 2;                 // handle 0x00020000 (race 2)
    s.kind = as::OrderKind::InSystem;       // +0x58 == 4
    s.act = 1;                              // +0x5d == 1 (witness: cleared at death)
    s.orderType = 2;                        // +0x67 == 2 (RETAINED across death)
    s.fireTarget = 7;                       // +0x68 stand-in (RETAINED: 0x002589f6)
    s.dispatcherGate = 1;                   // +0x62 stand-in (RETAINED per disasm scope)
    s.activeSlot = 4;                       // +0x63 stand-in (RETAINED per disasm scope)
    s.pos[0] = 1280.f; s.pos[1] = -1760.f; s.pos[2] = 1344.f;
    s.power = 1; s.powerMax = 8;            // +0x88 1, +0x18 8
    s.integrity = 20; s.maxIntegrity = 20;  // +0x8c 20 (death does NOT zero hull)
    s.etaDay = 1018;                        // +0x52 1018
    s.invCap = 10; s.invFilled = 10;        // +0x15a 10 / +0x15e 10 (M6)
    const uint8_t ring[10] = {28, 28, 17, 43, 1, 36, 73, 43, 13, 13};
    for (int i = 0; i < 10; ++i) { s.inv[i].cidx = ring[i]; s.inv[i].use = (i == 4) ? 1 : 0; }
    return s;
}
as::Ship mkS40() {
    as::Ship s;
    s.id = 40; s.owner = 0;                 // handle 0x00000000 (race 0)
    s.kind = as::OrderKind::Move;           // +0x58 == 1
    s.power = 40; s.powerMax = 40;
    s.integrity = 40; s.maxIntegrity = 40;
    s.etaDay = 1241;                        // +0x52 1241
    s.invCap = 25; s.invFilled = 25;        // fully populated ring row
    for (int i = 0; i < 25; ++i) s.inv[i].cidx = static_cast<uint8_t>(0x10 + i);
    return s;
}

}  // namespace

TEST(shipsim_death_is_in_place_no_compaction_t379) {
    // Kill through the REAL finalizer path (commitShot hull<1, same rig as
    // t364's lethal pin), then pin the MEASURED corpse shape: the C4 store
    // set lands (owner -1 / kind 0 / act 0) and NOTHING else changes —
    // order type +0x67, the fireTarget(+0x68) stand-in, dispatcherGate
    // (+0x62), activeSlot (+0x63), pos, power, eta, ring cidx AND use-words,
    // cap/filled are all RETAINED (5-word diff witness, _wip_t379 S5; the
    // pre-t379 finalizer cleared +0x62/+0x63/+0x68 — unwitnessed, removed,
    // re-adding them is a CAUGHT mutant). No compaction: the corpse keeps
    // its id and stays findable.
    as::ShipSim sim(1);
    std::vector<as::SimDesign> t(0x4a);
    t[10] = as::SimDesign{}; t[10].cat = 0; t[10].power = 2; t[10].range = 25;
    t[10].rowWeapon = 6; t[10].targetShip = true;
    sim.setDesigns(t);
    as::Ship v = mkS12();
    v.systemId = 7; v.integrity = 3;           // dmg 6 -> hull < 1 (t364 clamp law)
    as::Ship a = mkS12();
    a.id = 0; a.owner = 1; a.systemId = 7; a.integrity = 10; a.maxIntegrity = 10;
    a.power = 10; a.powerMax = 10; a.invCap = 1;
    a.inv[0].cidx = 10;
    sim.addShip(v); sim.addShip(a);
    as::Ship* pa = sim.findShip(0);
    pa->orderType = 0; pa->dispatcherGate = 1; pa->fireTarget = 12; pa->activeSlot = 0;
    auto r = sim.commitShot(0, 1);
    CHECK(r.destroyed == 12);
    const as::Ship* c = sim.findShip(12);      // NO compaction: corpse at its id
    CHECK(c != nullptr);
    CHECK(c->owner == -1);                     // +0x56 := 0xffff (law A3)
    CHECK(c->kind == as::OrderKind::NoOrder);  // +0x58 := 0
    CHECK(c->act == 0);                        // +0x5d := 0 (witness leg)
    // RETENTION (the S5 word-diff minus the three stores above):
    CHECK(c->orderType == 2);                  // +0x67 2->2
    CHECK(c->fireTarget == 7);                 // +0x68 0x002589f6->same
    CHECK(c->dispatcherGate == 1);             // +0x62 outside store set
    CHECK(c->activeSlot == 4);                 // +0x63 outside store set
    CHECK(c->pos[0] == 1280.f && c->pos[1] == -1760.f && c->pos[2] == 1344.f);
    CHECK(c->power == 1 && c->powerMax == 8);  // NOT refilled, NOT zeroed
    CHECK(c->etaDay == 1018);
    CHECK(c->invCap == 10 && c->invFilled == 10);   // M6 at record level
    CHECK(c->inv[0].cidx == 28 && c->inv[9].cidx == 13);
    CHECK(c->inv[4].use == 1);                 // ring USE-WORDS retained
    CHECK(sim.liveCount() == 1);               // census mirror 2 -> 1 (count DEC)
}

TEST(shipsim_count_window_contains_corpse_and_orphans_top_t379) {
    // The MEASURED t1254 shape at small scale: window size == live census,
    // the window contains the CORPSE (in-place death at a lower index), and
    // live records at ids >= the census fall OUTSIDE the window — orphans.
    // BOUNDARY witness: the corpus orphan s40 has id == count EXACTLY
    // (40 == 40), so the window law is id >= census, not id > census: ship
    // id2 here is the id==census row (census is 2 with the s12 corpse).
    // This is the seam a compacting refactor would silently erase.
    as::ShipSim sim(1);
    as::Ship b = mkS40(); b.id = 2;            // id == census boundary row
    sim.addShip(b);
    sim.addShip(mkS40());                      // s40 orphan
    sim.addShip(mkS12());                      // dies in place
    as::Ship* v = sim.findShip(12);
    v->owner = -1; v->kind = as::OrderKind::NoOrder; v->act = 0;

    auto win = sim.countWindow();
    CHECK(win.size() == 2u);                   // window == count == live census
    CHECK(win.size() == 2u && win[1]->id == 12);   // CORPSE inside the window
    auto orph = sim.orphanedShips();
    CHECK(orph.size() == 2u);                  // boundary row id2 AND s40
    // GUARDED indexing: CHECK does not abort; an unguarded orph[1] under a
    // size-breaking mutant segfaults the WHOLE suite (t379 M1/M5 lesson).
    CHECK(orph.size() == 2u && orph[0]->id == 2 && orph[1]->id == 40);
    // The orphan is fully intact (byte-identity witness): fields readable.
    CHECK(orph.size() == 2u && orph[1]->power == 40 && orph[1]->integrity == 40);
    CHECK(orph.size() == 2u && orph[1]->kind == as::OrderKind::Move);
    // ships() (the SORTED executor list) still sees the orphan — fleet-list
    // item 3: pickers must scan past the count word (ships.md / _wip_t360 S2).
    bool inShips = false;
    for (const auto& s : sim.ships())
        if (s.id == 40 && s.owner == 0) inShips = true;
    CHECK(inShips);
    // The corpse is NOT in the live census but IS in ships() (marked, never
    // removed) — the two enumerations differ BY CONSTRUCTION.
    bool corpseInList = false;
    for (const auto& s : sim.ships())
        if (s.id == 12) corpseInList = true;
    CHECK(corpseInList);
    CHECK(sim.liveCount() == 2);               // corpses excluded from census
}

TEST(shipsim_clean_boundary_no_orphans_t379) {
    // NEGATIVE CONTROL: without a death the window is exactly the live set in
    // id order and NOTHING is orphaned (the t1253 side: dense 0..40 with
    // count 41 — law test held 20/20: dead-in-window 0, live-beyond 0).
    // Fixture is DENSE from id 0: an id >= census is out-of-window by the
    // walk law range(count), so a sparse fixture would be vacuously orphaned.
    as::ShipSim sim(1);
    as::Ship a = mkS40(); a.id = 0; a.etaDay = 5;
    as::Ship b = mkS40(); b.id = 1; b.etaDay = 7;
    as::Ship c = mkS40(); c.id = 2; c.etaDay = 3;
    sim.addShip(a); sim.addShip(b); sim.addShip(c);
    auto win = sim.countWindow();
    CHECK(win.size() == 3u);
    CHECK(win[0]->id == 0 && win[1]->id == 1 && win[2]->id == 2);  // id order
    CHECK(sim.orphanedShips().empty());
    CHECK(sim.liveCount() == 3);
}

TEST(shipsim_dead_row_shape_corpus_playtest_t379) {
    // CORPUS PIN (skips when work/ banks absent — public clone): every save
    // in BOTH banks reproduces the measured census shape (scripts/
    // r379_shape_census.py + r379_shape_verify.py):
    //   count == full-window live census
    //   dead-in-window == live-beyond-window (the orphan balance)
    //   t1253 side: s12 live race-2 row; t1254 side: s12 dead marker
    //   (handle 0xffff0000, kind 0) and s40 LIVE with handle 0x00000000.
    auto early = bankSaves(kBankEarly);
    auto late = bankSaves(kBankLate);
    std::vector<uint8_t> payload;
    std::vector<std::pair<size_t, std::vector<uint8_t>>> anch;
    if (early.empty() || late.empty() || !payloadAnchors(&payload, &anch)) {
        std::printf("(skip: playtest banks/payload absent) ");
        return;
    }
    // The census measured IDENTICAL shapes on all 20 slots per bank
    // (r379_shape_census.py); parse 5 per side to bound suite runtime.
    if (early.size() > 5) early.resize(5);
    if (late.size() > 5) late.resize(5);
    for (const auto& side : {early, late}) {
        const bool lateSide = (side == late);
        for (const auto& path : side) {
            std::vector<uint8_t> mem;
            std::string err;
            if (!ShipSave::readMemoryMember(path, &mem, &err)) { CHECK(false); continue; }
            size_t base = 0;
            if (!ShipSave::findImageBase(mem, anch, 5, &base, &err)) { CHECK(false); continue; }
            std::vector<ShipSave::Record> recs;
            if (!ShipSave::parseShipRecords(mem, base, &recs, &err)) { CHECK(false); continue; }
            CHECK(recs.size() == static_cast<size_t>(ShipSave::kArraySlots));
            const uint32_t count = ShipSave::countWord(mem, base);
            uint32_t live = 0, deadIn = 0, beyond = 0;
            for (const auto& r : recs) {
                if (r.dead) { if (r.slot < count) ++deadIn; }
                else { ++live; if (r.slot >= count) ++beyond; }
            }
            CHECK(live == count);              // count == live census (60/60)
            CHECK(deadIn == beyond);           // orphan balance (balance law)
            if (lateSide) {
                CHECK(deadIn == 1u);           // exactly the s12 corpse
                CHECK(beyond == 1u);
                const auto& s12 = recs[12];
                CHECK(s12.dead);
                CHECK(s12.ownerHandle == 0xffff0000u);   // the C4 word store
                CHECK(s12.orderKind == 0);               // kind := 0
                // M6 at record level on the REAL corpse:
                CHECK(s12.invCap == 10u && s12.filled == 10u);
                CHECK(s12.ringCidx.size() == 25u && s12.ringCidx[0] == 28 &&
                      s12.ringCidx[9] == 13 && s12.ringCidx[10] == 0xFF);
                const auto& s40 = recs[40];
                CHECK(!s40.dead);              // orphan still live by marker law
                CHECK(s40.ownerHandle == 0x00000000u);
                CHECK(s40.orderKind == 1);
                CHECK(s40.power == 40u && s40.integrity == 40u);
                CHECK(s40.invCap == 25u && s40.filled == 25u);
            } else {
                CHECK(deadIn == 0u);
                CHECK(beyond == 0u);           // t1253: packed, nothing orphaned
                const auto& s12 = recs[12];
                CHECK(!s12.dead);
                CHECK(s12.ownerHandle == 0x00020000u);
                CHECK(s12.orderKind == 4);
            }
        }
    }
}

TEST(shipsim_orphan_record_untouched_corpus_t379) {
    // THE load-bearing byte-identity witness (r379_shape_verify.py T1): slot
    // 40's WHOLE 0x162 record is identical between the t1253 bank and the
    // t1254 bank — the vendor NEVER wrote it; its disappearance from the
    // count-window rows is purely the count DEC at index 12. Pinned here
    // against the ZIP Memory members directly (read-only).
    auto early = bankSaves(kBankEarly);
    auto late = bankSaves(kBankLate);
    std::vector<uint8_t> payload;
    std::vector<std::pair<size_t, std::vector<uint8_t>>> anch;
    if (early.empty() || late.empty() || !payloadAnchors(&payload, &anch)) {
        std::printf("(skip: playtest banks/payload absent) ");
        return;
    }
    std::vector<uint8_t> a, l;
    std::string err;
    if (!ShipSave::readMemoryMember(early.front(), &a, &err)) { CHECK(false); return; }
    if (!ShipSave::readMemoryMember(late.front(), &l, &err)) { CHECK(false); return; }
    size_t ba = 0, bl = 0;
    if (!ShipSave::findImageBase(a, anch, 5, &ba, &err) ||
        !ShipSave::findImageBase(l, anch, 5, &bl, &err)) { CHECK(false); return; }
    const size_t offA = ba + ShipSave::kDataSeg + ShipSave::kShipArrayX + 40 * ShipSave::kRecordStride;
    const size_t offL = bl + ShipSave::kDataSeg + ShipSave::kShipArrayX + 40 * ShipSave::kRecordStride;
    CHECK(offA + ShipSave::kRecordStride <= a.size());
    CHECK(offL + ShipSave::kRecordStride <= l.size());
    CHECK(std::equal(a.begin() + offA, a.begin() + offA + ShipSave::kRecordStride,
                     l.begin() + offL));   // BYTE-IDENTICAL: never written
}
