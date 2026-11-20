// SPDX-License-Identifier: GPL-3.0-or-later

// t434 FLEET ROW INK/SELECTION LAW pins (docs/re/_wip_t434.md F4/F6).
// LAW [verified fn 0x50d12, work/r331_disasm.txt 0x50d50..0x50d8d]: the
// row colour word = raceColourByte*4 + 0x13 (game.pal index; the race row
// +0x1 byte, stride 0x1ee, masked BYTE-wide at 0x50d6c), OVERRIDDEN to the
// immediate 0xf3 == pal[243] (white) when the row is selected (edi != 0,
// 0x50d7e..0x50d8d). Same law as the t427 planets-row text selection.
// WITNESS [measured, work/screens/t253/fleet_open_game.png]: selected row 1
// name band 48 px (255,255,255); rows 0/2/3 name AND location bands
// (0,170,82) green (zero cyan px — the pre-t434 fixed-cyan location was a
// port defect); zero row-frame/marker pixels anywhere.
#include "ui/fleetlist.h"
#include "ui/raceintro.h"  // kIntroRaceBytes
#include "harness.h"

namespace {
namespace au = ascend::ui;

TEST(fleetlist_row_ink_law_t434) {
    // Unselected: idx = byte*4 + 0x13 for every static colour byte.
    for (int b : au::kIntroRaceBytes)
        CHECK(au::fleetRowPalIndex(false, b) == (b & 0xff) * 4 + 0x13);
    // Byte-truncation law (and eax,0xff at 0x50d6c): only the LOW byte.
    CHECK(au::fleetRowPalIndex(false, 256 + 7) == 7 * 4 + 0x13);
}

TEST(fleetlist_row_selection_white_t434) {
    // Selected: 0xf3 REGARDLESS of the race byte (0x50d86 is an
    // unconditional mov of the immediate into the colour slot).
    for (int b : au::kIntroRaceBytes)
        CHECK(au::fleetRowPalIndex(true, b) == 0xf3);
}

TEST(fleetlist_row_ink_witness_legs_t434) {
    // Chamachies witness leg (t253 header "Chamachies"): specnum 19, static
    // colour byte 0 -> pal[0x13]; the t253 unselected ink (0,170,82) is
    // that index through the DOSBox conversion (the same index the t424b
    // race-intro witness pinned green for runtime byte 0).
    CHECK(au::kIntroRaceBytes[19] == 0);
    CHECK(au::fleetRowPalIndex(false, au::kIntroRaceBytes[19]) == 0x13);
    CHECK(au::fleetRowPalIndex(false, au::kIntroRaceBytes[0]) == 0x13);
    // A NON-zero byte must NOT alias pal[0x13] (catch a const-0 mutant).
    CHECK(au::fleetRowPalIndex(false, 7) == 7 * 4 + 0x13);
    CHECK(au::fleetRowPalIndex(false, 7) != au::fleetRowPalIndex(false, 0));
}

}  // namespace
