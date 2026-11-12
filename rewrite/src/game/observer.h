// SPDX-License-Identifier: GPL-3.0-or-later

#pragma once
#include <cstdint>
#include <string>
#include <vector>

#include "formats/shipsave.h"
#include "game/shipsim.h"

namespace ascend::game {
// t382 PLAYTEST BOOT — READ-ONLY OBSERVER (queue row t382).
// NOT gameplay: no order UI, no write-back (serializeRecord is NEVER called
// from this path), no simulation advance. It reads one save file, imports the
// fleet into a ShipSim via Ship::fromRecord (t361), and renders the star map
// and ship field as text. Input shapes and their laws (all MEASURED
// 2026-11-12, docs/re/_wip_t382.md — probes cited inline):
//
//  A) dosbox-x savestate ZIP (ring shape, work/r1/playcap/save/*.sav):
//     formats::ShipSave full path (anchor vote + member offsets, t360/t366).
//     Star table = K8 star-slot records: member B+kDataSeg+0x13bc5, stride
//     0x60, count u16 at image 0x16145, name CP437 at +0x1c, coords f32 triple
//     +0x08/+0x0c/+0x10 (planets-ui.md §1, r1_t246_header_law.py).
//     kind-4 ships: +0x59 is a guest-PHYSICAL star-object pointer; member =
//     phys + 0x88 (t298) lands EXACTLY on the star-slot record — 19/19
//     attribution on ring 60.sav (_wip_t382 S4).
//
//  B) native raw .SAV (work/r1/game/0[1-4].SAV):
//     day = u32@0 (4/4: 1086/1253/887/1254).
//     SHIP BLOCK: packed list of LIVE records; record i at file home
//     H + i*0x166 (stride 0x166 = 0x162 record + u32 marker at record-4);
//     marker = RAM slot id, strictly ascending; terminator = first marker
//     that is >= 0x6b or <= the previous marker. VALIDATED: 01.SAV block ==
//     the live-slot set of bank-t1086-preplay RAM (30 == 30 exact set
//     equality); 04.SAV block (38 slots) vs same-world ring-60 live set
//     (40): block has slot 12 (died between the save instant and the ring
//     capture) and lacks {19,21,23} (records that came to exist in the
//     remaining minutes of the same day-1254 session). The block is the
//     live list AT SAVE INSTANT — set drift across a same-day gap is
//     expected, not a format violation. Record fields are the SAME 0x162 layout as the ZIP path
//     (slot-0 lane-run map _wip_t382: diffs confined to the pointer region
//     +0x58..0x68 + state drift; name/owner/coords verbatim).
//     H SHIFTS between saves — discovery is a content-based marker-chain
//     scan, NEVER a hard-coded offset.
//     STAR BLOCK: stride 0x60 records (same shape); discovery scans for the
//     first record with a printable CP437 name at +0x1c and sane fields,
//     then walks both directions while records stay sane. Home 0x1e2a on all
//     four corpus saves; 50 records on the corpus world (T=50).
//
// FRAME RESIDUE (honest negative, _wip_t382 S3): ship pos triples are on the
// 32-aligned world frame (t380 quantizer law, extents ~±2300); star-record
// triples span ~±430 and NO scale factor unifies them (scan 3.5..8.0, mean
// nearest-star distance bottoms out ~630 with no snap). The two maps are
// therefore rendered SEPARATELY; no projection between frames is claimed.
class Observer {
  public:
    struct StarRow {
        int slot = 0;
        uint32_t typeK = 0;         // +0x00 (starstat index 0..12)
        float pos[3] = {0, 0, 0};   // +0x08 triple
        uint8_t owner = 0xff;       // +0x14 owner bitmask byte
        std::string name;           // +0x1c CP437, NUL-terminated
    };
    struct ShipRow {
        formats::ShipSave::Record rec;  // full t360 record (slot = RAM id)
        std::string name;               // record +0x34 CP437 (raw path;
                                        // ZIP path fills it too — read from
                                        // the member, not a new parser field)
        int targetStar = -1;            // ZIP path: +0x59 deref -> star slot
    };

    // ---- shape B: native raw .SAV ----
    static uint32_t rawDay(const std::vector<uint8_t>& file);  // u32@0 law

    // Marker-chain discovery + walk. Returns rows in block order (rec.slot =
    // RAM id; name from record +0x34). False + *err when no chain of >=
    // kMinChain sane records exists (REFUSAL, never a clamp).
    static constexpr uint32_t kRawShipStride = 0x166;
    static bool parseRawShipBlock(const std::vector<uint8_t>& file,
                                  std::vector<ShipRow>* out, std::string* err);

    // Star-block discovery + sane walk (both directions from first hit).
    static bool parseRawStarBlock(const std::vector<uint8_t>& file,
                                  std::vector<StarRow>* out, std::string* err);

    // ---- shape A: savestate ZIP (thin wrapper over formats::ShipSave) ----
    // payload = the exe payload image (work/ascend_payload.bin) that
    // buildAnchors derives the base vote from (t360; the CLI supplies it).
    // Imports stars from the K8 table and ships from the full-window parse
    // (dead rows filtered per S59 L2). targetStar filled for kind-4 ships
    // whose +0x59 derefs onto a star-slot record.
    static bool importSavestate(const std::string& path,
                                const std::vector<uint8_t>& payload,
                                uint32_t* day, std::vector<StarRow>* stars,
                                std::vector<ShipRow>* ships, std::string* err);

    // Shared: build a ShipSim from parsed rows (addStar/addShip +
    // Ship::fromRecord, t361). Returns the sim by value; the observer never
    // advances a boundary.
    static ShipSim buildSim(uint32_t day, const std::vector<StarRow>& stars,
                            const std::vector<ShipRow>& ships);

    // Text render (ASCII glyphs only, no colour — user deuteranopia law:
    // meaning is carried by glyph SHAPE, never colour). Auto-fitted grid.
    // Stars: 'o' unowned, 'O' owned (owner byte nonzero). Ships: digit of
    // orderKind (1..5); a cell holding both prints '@'.
    static std::string renderMap(const std::vector<float>& xs,
                                 const std::vector<float>& zs,
                                 const std::vector<char>& glyphs, int cols,
                                 int rows);
};

}  // namespace ascend::game
