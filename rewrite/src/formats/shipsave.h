#pragma once
#include <cstdint>
#include <cstddef>
#include <string>
#include <utility>
#include <vector>

namespace ascend::formats {
// RESUME.GAM (dosbox-x savestate ZIP) ship-array reader — READ SIDE ONLY
// (queue row t360). Build contract: docs/re/pership-spec.md §0/§1/§6; save-side
// ground truth: docs/re/_wip_t360.md S2 (MEASURED 2026-11-09, production ring
// 41..60.sav, turn 1086, 20/20 base-verified).
//
// Laws (cited, never re-derived here):
//  * ZIP 'Memory' member == full guest RAM (r1_slot.py / OQ-011 CLOSED);
//    member address for data-segment offset X = B + kDataSeg + X.
//  * Base B via unanimous high-entropy anchor vote, min 5 votes
//    (scripts/r1_sav_scan.py; r360 re-derived B=0x1bf4d8 on 20/20 saves).
//  * Ship array at member offset B+kDataSeg+kShipArrayX, stride kRecordStride,
//    count word u32 at B+kDataSeg+kCountX >> 16, cap kArraySlots (spec A1).
//  * The count word is NOT the fleet census: live records exist past it
//    (ships.md fleet-list item 3; MEASURED 4 live at indices >= 30 of 30).
//    parseShipRecords() therefore scans the FULL 0..cap window and marks the
//    dead rows by the owner-handle marker (r256c oc_of law): rows with
//    (u32@+0x54)>>16 == 0xffff are dead/free.
//  * Owner attribution: race index == (u32@+0x54)>>16 == byte@+0x56 on every
//    live row (t273 law; MEASURED 600/600 save-side).
//  * Inventory ring: 25 slots stride 7 {cidx u8 (0xFF empty), u16 use-count,
//    u32 payload} at +0xab; the ring span ENDS at +0x15a where the cap dword
//    begins (0xab + 7*25 == 0x15a), so a probe at slot index == cap on a
//    cap==25 row reads the CAP WORD's low byte — a self-read artifact, never
//    inventory (layout fact + _wip_t360 S2). occupiedExclusive() probes only
//    real inventory: slots 0..min(cap,25)-1.
//  * filled(+0x15e) is stored verbatim; the derivation law is DISPUTED across
//    corpora (exclusive 600/600 here vs ships.md §18 inclusive 1234/1234 on
//    the t184 campaign) — the parser does NOT enforce either.
class ShipSave {
  public:
    static constexpr uint32_t kDataSeg = 0x82bb0;
    static constexpr uint32_t kShipArrayX = 0x3a095;
    static constexpr uint32_t kCountX = 0x43489;
    static constexpr uint32_t kTurnX = 0x12e10;
    static constexpr uint32_t kRecordStride = 0x162;
    static constexpr uint32_t kArraySlots = 0x6b;
    static constexpr uint32_t kRingSlots = 25;

    struct Record {
        uint8_t slot = 0xff;
        bool dead = true;              // owner-handle marker (r256c oc_of)
        uint32_t weaponLevel = 0;      // +0x00
        uint32_t shieldLevel = 0;      // +0x04
        uint32_t laneStepX = 0;        // +0x08
        uint32_t laneStepZ = 0;        // +0x0c
        uint32_t driveTotal = 0;       // +0x10
        uint32_t hullBaseDrive = 0;    // +0x14
        uint32_t powerMax = 0;         // +0x18
        uint32_t cat2PowerCarry = 0;   // +0x1c
        uint32_t scannerTotal = 0;     // +0x20
        uint32_t specialCount = 0;     // +0x24
        uint32_t targetSlot = 0;       // +0x28
        uint8_t playerDesign = 0;      // +0x31
        uint32_t ownerHandle = 0;      // +0x54 (guest handle; race = >>16)
        uint8_t ownerRace = 0xff;      // +0x56
        uint8_t orderKind = 0;         // +0x58 (0..5 live; spec §2)
        uint32_t orderTarget = 0;      // +0x59 (guest-PHYSICAL, rebase per save)
        uint8_t actEnum = 0;           // +0x5d
        uint32_t actTarget = 0;        // +0x5e
        uint8_t resolverFlag = 0;      // +0x62
        uint32_t gizmoSlotPtr = 0;     // +0x63 (guest-PHYSICAL)
        uint8_t orderType = 0;         // +0x67
        uint32_t orderPayload = 0;     // +0x68 (guest-PHYSICAL when pointer)
        float absTriple[3] = {0, 0, 0};  // +0x6c
        uint32_t power = 0;            // +0x88
        uint32_t integrity = 0;        // +0x8c
        uint32_t shields = 0;          // +0x90 (dual-use spec G-b)
        uint32_t moves = 0;            // +0x94
        uint32_t maxIntegrity = 0;     // +0x98
        uint16_t statusFlags = 0;      // +0x9c
        float pos[3] = {0, 0, 0};      // +0x9e
        uint8_t hullKind = 0;          // +0xaa
        std::vector<uint8_t> ringCidx; // +0xab, exactly kRingSlots cidx bytes
        uint32_t invCap = 0;           // +0x15a
        uint32_t filled = 0;           // +0x15e (verbatim, see header law)

        // Count of cidx != 0xFF over REAL inventory: slots 0..min(cap,25)-1.
        uint32_t occupiedExclusive() const;
    };

    // Inflate the 'Memory' member of a savestate ZIP (method 0 or 8).
    static bool readMemoryMember(const std::string& path,
                                 std::vector<uint8_t>* mem, std::string* err);

    // Anchor-vote port of scripts/r1_sav_scan.py: windows of 128 zero-free
    // bytes with >40 distinct values at 16 KiB stride of the payload image.
    static std::vector<std::pair<size_t, std::vector<uint8_t>>>
    buildAnchors(const std::vector<uint8_t>& payload);

    // Unanimous vote (>= minVotes distinct anchors landing on the same B).
    static bool findImageBase(const std::vector<uint8_t>& mem,
                              const std::vector<std::pair<size_t, std::vector<uint8_t>>>& anchors,
                              uint32_t minVotes, size_t* base, std::string* err);

    static uint32_t countWord(const std::vector<uint8_t>& mem, size_t base);
    static uint32_t turnCounter(const std::vector<uint8_t>& mem, size_t base);

    // Full-window parse: exactly kArraySlots records, dead rows flagged, not
    // skipped (the count word is not the census — see header). False + *err
    // if the window would read past the member.
    static bool parseShipRecords(const std::vector<uint8_t>& mem, size_t base,
                                 std::vector<Record>* out, std::string* err);

    // ---- WRITE SIDE (t366, pership-spec §6 S7) ----
    // Serialize ONE record back into the RESUME.GAM member layout.
    // CITED-ONLY PATCH LAW (binding, _wip_t366 S3): the writer stores EXACTLY
    // the field offsets parseShipRecords() reads, and touches NOTHING else in
    // the stride — the unmodelled gap bytes (+0x0a.., +0x32.., the ring-slot
    // use-word/payload, ...) are neither read nor zeroed. A whole-record emit
    // into fresh memory therefore cannot yet be faithful in the gaps; the
    // supported operation is write-back into an existing member (idempotence
    // is the pinned property: parse -> write -> byte-identical).
    // Ring note: slot stride 7 {cidx u8, use u16, payload u32}; only the cidx
    // byte at +0xab+7*i is written (use/payload are not in the parser's set).
    static void serializeRecord(const Record& rec, uint8_t* r);

    // Full-window write-back at base (same geometry checks as the parser).
    static bool writeShipRecords(std::vector<uint8_t>* mem, size_t base,
                                 const std::vector<Record>& recs,
                                 std::string* err);

    // Pointer-valued fields (+0x59 orderTarget, +0x63 gizmoSlotPtr,
    // +0x68 orderPayload) hold guest-PHYSICAL addresses (t298 POINTER-VALUE
    // LAW; spec §6 S2). Moving records between runs of DIFFERENT base B means
    // shifting these three values by (newB - oldB) — nothing else. Delta 0 is
    // a no-op (same-run write-back).
    static void rebaseRecord(Record* rec, uint32_t delta);
};

}  // namespace ascend::formats
