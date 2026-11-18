// SPDX-License-Identifier: GPL-3.0-or-later
// t423c: player-colour chip hit law + FUN_000232ec reassign law.
// Evidence: docs/re/_wip_t423c2.md C2-F3 (capstone 0x232ec..0x23385) and
// C2-F6 (zone cmp ebx 0x17b/0x1ed, ecx 0x1a4/0x1d8; idx=(x-0x17b)>>4).
#include "harness.h"

#include "ui/menulaw.h"

namespace au = ascend::ui;

TEST(racecolour_chip_zone_windows_disasm) {
    // Zone edges are INCLUSIVE [verified 0x529d2 cmps].
    CHECK(au::newgameChipAt({378, 420}) == -1);
    CHECK(au::newgameChipAt({494, 420}) == -1);
    CHECK(au::newgameChipAt({379, 419}) == -1);
    CHECK(au::newgameChipAt({379, 473}) == -1);
    CHECK(au::newgameChipAt({379, 420}) == 0);
    CHECK(au::newgameChipAt({493, 472}) == 7);  // (493-0x17b)>>4 = 7
    // 16-px grid from x=379: idx flips at 395, 411, ... (vendor >>4 law,
    // NOT the t414 chip ART grid 384+16k — the hit grid is the disasm's).
    CHECK(au::newgameChipAt({394, 440}) == 0);
    CHECK(au::newgameChipAt({395, 440}) == 1);
    CHECK(au::newgameChipAt({411, 440}) == 2);
}

TEST(racecolour_reassign_fun_000232ec) {
    // Guard: `1 < word[base+0xd88]` — count<=1 writes NOTHING (not even
    // slot 0). Verified 0x23309 cmp dx,cx / jle ret.
    unsigned int s = 1;
    unsigned char out[8] = {9, 9, 9, 9, 9, 9, 9, 9};
    au::assignRaceColours(3, 1, &s, out);
    CHECK(out[0] == 9);

    // Player keeps the clicked idx VERBATIM (byte store dl); AI slots are
    // distinct from every already-written slot and drawn from rand()%7.
    s = 0x12e10u;
    unsigned char a[8] = {0};
    au::assignRaceColours(0, 7, &s, a);
    CHECK(a[0] == 0);
    for (int i = 1; i < 7; i++) CHECK(a[i] < 7);
    for (int i = 0; i < 7; i++)
        for (int j = i + 1; j < 7; j++) CHECK(a[i] != a[j]);

    // Clicked idx 7 (neutral sliver) is stored unclamped; the six AI
    // draws are distinct values from 0..6 (six of seven values appear).
    s = 0x12e10u;
    unsigned char b[8] = {0};
    au::assignRaceColours(7, 7, &s, b);
    CHECK(b[0] == 7);
    int seen[7] = {0, 0, 0, 0, 0, 0, 0};
    for (int i = 1; i < 7; i++) { CHECK(b[i] < 7); seen[b[i]]++; }
    for (int k = 0; k < 7; k++) CHECK(seen[k] <= 1);

    // Determinism for a fixed seed (the LCG law is cited; the seed VALUE
    // is the named seam — see title.cpp colourLcg).
    unsigned int s1 = 0xABCDu, s2 = 0xABCDu;
    unsigned char x[8] = {0}, y[8] = {0};
    au::assignRaceColours(2, 5, &s1, x);
    au::assignRaceColours(2, 5, &s2, y);
    for (int i = 0; i < 5; i++) CHECK(x[i] == y[i]);
    CHECK(s1 == s2);  // same draw count consumed
}
