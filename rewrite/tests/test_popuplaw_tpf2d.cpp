// SPDX-License-Identifier: GPL-3.0-or-later

// tPF-2d POPUP BUTTON LAW pins (fn 0x3d397..0x3d67e msg-1 leg; citations
// docs/re/_wip_tPF2d.md D2/D3/D5/D6 + docs/re/_wip_tPF2c.md C6):
//   1. LABEL REGISTRY (live-resolved 20/20 saves,
//      scripts/tPF2d_label_registry.py): u32[ds:0x744a0 + id*4] ->
//      Cancel/Create Colony/Abandon/Build/Leave Orbit/Refit/Invade/Automate
//      at ids 51..58, indicator words at 35..50.
//   2. ID-ARRAY LAW: empty cell -> ONE 54 for the FIRST checker-legal item
//      (skip 5), then BREAK (0x3d582 fall-through — "per item" refuted);
//      occupied -> 53 iff item != 5, then 58 iff checker(35); 51 ALWAYS
//      last (0x3d591..0x3d5a4).
//   3. CONSUMER GEOMETRY (0x3d594..0x3d65c): y band 337..367 absolute;
//      x cursor 160, w = (479-x)/remaining, next x = min(x+w,479)+1.
//   4. SINGLE-BUTTON PATH (0x3d684): n==1 -> label getter(30) "OK".
#include <cstdio>
#include <string>
#include <vector>

#include "ui/planetwin.h"
#include "harness.h"

namespace {
namespace au = ascend::ui;

// 1. registry words verbatim (D2).
TEST(popup_label_registry_tpf2d) {
    CHECK(std::string(au::popupButtonLabel(au::kPbCancel)) == "Cancel");
    CHECK(std::string(au::popupButtonLabel(au::kPbBuild)) == "Build");
    CHECK(std::string(au::popupButtonLabel(au::kPbAbandon)) == "Abandon");
    CHECK(std::string(au::popupButtonLabel(au::kPbAutomate)) == "Automate");
    CHECK(std::string(au::popupButtonLabel(44)) == "Mineral");
    CHECK(std::string(au::popupButtonLabel(50)) == "Cornucopia");
    CHECK(std::string(au::popupButtonLabel(34)) == "");  // key slot, not a word
    CHECK(std::string(au::popupButtonLabel(59)) == "");
}

// 2a. empty cell: exactly ONE Build then Cancel; nothing legal -> [51].
TEST(popup_ids_empty_single_build_tpf2d) {
    int seenFirst = -1;
    auto ids = au::popupButtonIds(0xff, [&](int item) {
        if (seenFirst < 0) seenFirst = item;
        return item == 2;  // only item 2 legal
    });
    CHECK(ids.size() == 2);
    CHECK(ids[0] == au::kPbBuild);
    CHECK(ids[1] == au::kPbCancel);
    CHECK(seenFirst == 0);  // loop starts at 0
    // BREAK law: probe order must STOP at the first pass (item 2 probed,
    // item 3 never).
    std::vector<int> probed;
    au::popupButtonIds(0xff, [&](int item) {
        probed.push_back(item);
        return item == 2;
    });
    CHECK(probed.size() == 3);           // 0,1,2 — no 3rd probe after pass
    CHECK(probed.back() == 2);
    auto none = au::popupButtonIds(0xff, [](int) { return false; });
    CHECK(none.size() == 1 && none[0] == au::kPbCancel);
    // Colony Base (5) is skipped in the loop (0x3d55f) even if "legal".
    bool probed5 = false;
    au::popupButtonIds(0xff, [&](int item) {
        if (item == 5) probed5 = true;
        return false;
    });
    CHECK(!probed5);
}

// 2b. occupied cell: 53 iff item != 5; 58 iff checker(35); 51 last.
TEST(popup_ids_occupied_tpf2d) {
    auto ids = au::popupButtonIds(7, [](int item) { return item == 35; });
    CHECK(ids.size() == 3);
    CHECK(ids[0] == au::kPbAbandon);
    CHECK(ids[1] == au::kPbAutomate);
    CHECK(ids[2] == au::kPbCancel);
    auto cb = au::popupButtonIds(5, [](int) { return false; });
    CHECK(cb.size() == 1 && cb[0] == au::kPbCancel);  // Colony Base: no 53
    auto noAuto = au::popupButtonIds(7, [](int) { return false; });
    CHECK(noAuto.size() == 2 && noAuto[0] == au::kPbAbandon);
    // Ship cells (cl == 0x17) are OUT OF DOMAIN: only the always-51 leg.
    auto ship = au::popupButtonIds(0x17, [](int) { return true; });
    CHECK(ship.size() == 1 && ship[0] == au::kPbCancel);
}

// 3. consumer spread law: exact vendor arithmetic (D3), refcap centres (D5).
TEST(popup_rects_spread_tpf2d) {
    const auto one = au::popupButtonRects(1);
    CHECK(one.size() == 1);
    CHECK(one[0].x0 == 160 && one[0].x1 == 479);   // w = (479-160)/1
    CHECK(one[0].y0 == 337 && one[0].y1 == 367);
    const auto two = au::popupButtonRects(2);
    CHECK(two[0].x0 == 160 && two[0].x1 == 319);   // w = 319/2 = 159
    CHECK(two[1].x0 == 320 && two[1].x1 == 479);
    // D5 pixel corroboration: refcap 'Build'/'Cancel' text centres ~233/~400
    // sit inside these rects near their centres (239.5/399.5).
    CHECK(200 < (two[0].x0 + two[0].x1) / 2 &&
          (two[0].x0 + two[0].x1) / 2 < 280);
    const auto three = au::popupButtonRects(3);
    CHECK(three[0].x0 == 160 && three[0].x1 == 266);  // 319/3 = 106
    CHECK(three[1].x0 == 267 && three[1].x1 == 373);  // (479-267)/2 = 106
    CHECK(three[2].x0 == 374 && three[2].x1 == 479);  // 479-374 = 105
    // Degenerate n=0 -> empty.
    CHECK(au::popupButtonRects(0).empty());
}

// 4. single-button label override (0x3d684: getter(30) 'OK').
TEST(popup_text_single_ok_tpf2d) {
    std::vector<int> onlyCancel{au::kPbCancel};
    CHECK(std::string(au::popupButtonText(onlyCancel, 0)) == "OK");
    std::vector<int> pair{au::kPbBuild, au::kPbCancel};
    CHECK(std::string(au::popupButtonText(pair, 0)) == "Build");
    CHECK(std::string(au::popupButtonText(pair, 1)) == "Cancel");
    // The refcap non-buildable popup: ids == [51] alone renders 'OK'.
    auto ids = au::popupButtonIds(0xff, [](int) { return false; });
    CHECK(ids.size() == 1 && std::string(au::popupButtonText(ids, 0)) == "OK");
}

}  // namespace
