// SPDX-License-Identifier: GPL-3.0-or-later

// t425 galaxy-map controls cycle pins. Law source: docs/re/_wip_t425.md
// (COSMOSWnd handler 0x26b34 msg map, capstone base-0 on
// work/ascend_restored.bin) + extracted/ascend00/windows.txt verbatim
// (BUTTONSTATE lines, RACE<N>CONTROL rows). Pins here are the PURE data
// law; the SDL wiring (toggle layers, race filter, popup click) is
// witnessed by scripts/t425_mapctl_witness.sh.
#include "ui/mapchrome.h"
#include "ui/exitpopup.h"

#include "harness.h"

using namespace ascend::ui;

TEST(mapctl_t425_toggle_defaults_match_buttonstate) {
    // windows.txt ln347/382/400 BUTTONSTATE 1, ln365 BUTTONSTATE 0
    // (TOGEMPIRE starts OFF); handler init 0x2718c sets the dword fields
    // visible and byte +0xd8 = 0xff.
    CHECK(kCtlDefaultLanes == true);
    CHECK(kCtlDefaultShips == true);
    CHECK(kCtlDefaultColonies == true);
    CHECK(kCtlDefaultEmpire == false);
    CHECK(kRaceFilterInit == 0xffu);
}

TEST(mapctl_t425_three_newly_routed_ctls_in_table) {
    // msgs 57/58/60/61 (TOGLANES/TOGSHIPS/TOGEMPIRE/TOGCOLONIES) all
    // resolve from their verbatim rects; each maps to a DISTINCT handler
    // toggle field per the msg map (c4/c8/58a/d0+cc).
    const MapCtl tl = *mapCtlFor({494, 418});   // TOGLANES  479..509,403..433
    const MapCtl te = *mapCtlFor({533, 418});   // TOGEMPIRE 518..548
    const MapCtl ts = *mapCtlFor({572, 418});   // TOGSHIPS  557..587
    const MapCtl tc = *mapCtlFor({611, 418});   // TOGCOLONIES 596..626
    CHECK(tl == MapCtl::TogLanes);
    CHECK(te == MapCtl::TogEmpire);
    CHECK(ts == MapCtl::TogShips);
    CHECK(tc == MapCtl::TogColonies);
    CHECK(kMapCtl[int(tl)].sendMessage == 57);
    CHECK(kMapCtl[int(te)].sendMessage == 60);
    CHECK(kMapCtl[int(ts)].sendMessage == 58);
    CHECK(kMapCtl[int(tc)].sendMessage == 61);
    // SHAPEFRAMEs verbatim (windows.txt ln352/370/371?->17/390?->18):
    CHECK(kMapCtl[int(tl)].shapeFrame == 15);
    CHECK(kMapCtl[int(te)].shapeFrame == 16);
    CHECK(kMapCtl[int(ts)].shapeFrame == 17);
    CHECK(kMapCtl[int(tc)].shapeFrame == 18);
}

TEST(mapctl_t425_race_slot_bits_are_powers_of_two) {
    // RACE<N>CONTROL bit column verbatim (ln429-435: 1,2,4,8,16,32,64) —
    // the msg-62 param the handler 0x27824 toggles in byte win+0xd8.
    for (int i = 0; i < 7; i++) {
        CHECK(kRaceSlots[i].bit == (1 << i));
        // msg 62 toggle law (0x27824): set bit -> clear, clear bit -> set;
        // one click on an all-visible mask leaves exactly that slot hidden.
        const unsigned after = kRaceFilterInit ^ unsigned(kRaceSlots[i].bit);
        CHECK((after & unsigned(kRaceSlots[i].bit)) == 0u);
        CHECK(after == (0xffu ^ unsigned(1u << i)));
    }
    // slot rects verbatim: x0 = 479 + 22i, y 449..465
    for (int i = 0; i < 7; i++) {
        CHECK(kRaceSlots[i].rect.x0 == 479 + 22 * i);
        CHECK(kRaceSlots[i].rect.y0 == 449);
        CHECK(kRaceSlots[i].rect.x1 == 479 + 22 * i + 16);
        CHECK(kRaceSlots[i].rect.y1 == 465);
    }
    // a centre click resolves to the owning slot
    CHECK(raceSlotFor({487, 457}) == 0);
    CHECK(raceSlotFor({619, 457}) == 6);
    // the gap between slots hits nothing (pitch 22 > width 16)
    CHECK(!raceSlotFor({519, 457}).has_value());
}

TEST(mapctl_t425b_face_family_five_records_per_slot) {
    // t425b FACE FAMILY LAW (docs/re/_wip_t425.md F5; census
    // scripts/t425b_face_census.py): slot i owns five 1starmap records at
    // base = 20 + 5i. The windows.txt SHAPEFRAME column (20,25,...,50) is the
    // +0 member; the outlined member is +2 and the grey member is +4.
    // VISIBLE = OUTLINED per the vendor's own help text (help.txt ln370-373,
    // HELPINDEX rcontrol == the RACECONTROLS HELPINDEX, verbatim): "Only
    // information pertaining to the species whose colors are OUTLINED will be
    // displayed".
    for (int i = 0; i < 7; i++) {
        CHECK(kRaceSlotFrameBase(i) == 20 + 5 * i);
        CHECK(kRaceSlotFrameVisible(i) == 22 + 5 * i);
        CHECK(kRaceSlotFrameHidden(i) == 24 + 5 * i);
        for (int j = i + 1; j < 7; j++) {
            CHECK(kRaceSlotFrameVisible(i) != kRaceSlotFrameVisible(j));
            CHECK(kRaceSlotFrameHidden(i) != kRaceSlotFrameHidden(j));
        }
    }
    CHECK(kRaceSlotFrameBase(0) == 20);   // windows.txt ln429 SHAPEFRAME
    CHECK(kRaceSlotFrameBase(6) == 50);   // windows.txt ln435 SHAPEFRAME
    // The control rect is 17x17 INCLUSIVE (479..495, 449..465) — exactly the
    // measured size of the OUTLINED members (16x16 for +0/+1/+4), so the
    // painted face covers its own rect and the outline lands on the rect edge.
    for (int i = 0; i < 7; i++) {
        CHECK(kRaceSlots[i].rect.x1 - kRaceSlots[i].rect.x0 + 1 == 17);
        CHECK(kRaceSlots[i].rect.y1 - kRaceSlots[i].rect.y0 + 1 == 17);
    }
}

TEST(exitpopup_t425_click_geometry_resolves_at_every_corner) {
    // The click branch recomputes exitCornerFor at the click point and
    // requires the point inside exitPopupRect: pin that a corner pixel
    // satisfies BOTH conditions on all four corners (the t419 draw law).
    const int W = 640, H = 480;
    const Pt corners[4] = {{0, 0}, {W - 1, 0}, {0, H - 1}, {W - 1, H - 1}};
    for (const Pt& c : corners) {
        const ExitCorner e = exitCornerFor(c.x, c.y, W, H);
        CHECK(e != ExitCorner::None);
        const Rect r = exitPopupRect(e, W, H);
        CHECK(inRect(r, c));
    }
    // a mid-screen point is never a popup click
    CHECK(exitCornerFor(320, 240, W, H) == ExitCorner::None);
}
