// SPDX-License-Identifier: GPL-3.0-or-later
// tPF-10 RESEARCH HOVER/SELECT VISIBILITY pins (D28 items 19/20).
// Law (docs/re/_wip_tPF10.md P1-P3):
//  - HOVER-WORD LAW (sub 0x47478 VERBATIM, work/tRS_reswin_fn.asm
//    0x47484..0x47555): word[win+0x9db] is a HOVER tracker — the select
//    sub re-hits the projected table from the MOUSE words on EVERY
//    framework msg (call sites incl. the switch DEFAULT 0x47b33), stores
//    the legal row under the cursor or 0xffff off any disk, and writes
//    the word ONLY on change (0x4753a je / 0x47548). The commit chain
//    (0x47d99) only READS it — a click never latches it.
//  - FRAME LAW 0x483fa..0x48470 (work/tPF8_gate.asm): esi=1 default; 0
//    studied-and-not-owned; 3 owned; 2 iff row==word -> LAST WRITE WINS
//    (0x48460..0x4846b), so a hovered OWNED row draws frame 2.
//  - COLOUR MEASUREMENT (scripts/tPF10_ringcolour_census.py): resring.shp
//    k2 mean RGB (68,147,189) BRIGHT BLUE (top (60,200,252)); k0 mean
//    (156,90,63) WARM; k1 (56,88,135); k3 (160,91,91). D28 item 20
//    "hover -> highlighted blue" == frame 2; the pre-tPF-10 "gold path
//    0x5caac" label was a misread of the blitter CHOICE at 0x484c4.
#include "ui/researchview.h"

#include <cstdio>
#include <fstream>
#include <string>
#include <vector>
#include <map>

#include "formats/gamepal.h"
#include "formats/shp.h"
#include "harness.h"

#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif

namespace {
namespace au = ascend::ui;

au::ResHitResult hit(au::ResHit k, int row) {
    au::ResHitResult r;
    r.kind = k;
    r.row = row;
    return r;
}
}  // namespace

// 1. Hover-word law: Node hit -> row; ANY non-Node result -> -1 (the
//    0xffff off-disk leg 0x47484/0x4748f); store happens only on CHANGE
//    (identity preserved when unchanged — the store-on-change shape means
//    a repeated identical hit never re-writes, matching 0x4753a).
TEST(hoverword_law_tpf10) {
    CHECK(au::resHoverWord(-1, hit(au::ResHit::Node, 7)) == 7);
    CHECK(au::resHoverWord(7, hit(au::ResHit::Node, 7)) == 7);   // no change
    CHECK(au::resHoverWord(7, hit(au::ResHit::Node, 3)) == 3);   // new disk
    CHECK(au::resHoverWord(7, hit(au::ResHit::None, -1)) == -1); // off-disk
    // Pan-button hits are NOT Node: word goes 0xffff (vendor: 0x47478
    // finds no node under the pan button, stores 0xffff).
    CHECK(au::resHoverWord(7, hit(au::ResHit::RotLeft, -1)) == -1);
    CHECK(au::resHoverWord(7, hit(au::ResHit::MoveDown, -1)) == -1);
}

// 2. Frame law with HOVER semantics: frame 2 is the LAST write (0x48460),
//    overriding owned (3) AND studied (0) — a hovered disk of any state
//    draws the blue frame; unhovered states keep their law values.
TEST(frame_hover_lastwrite_tpf10) {
    CHECK(au::resNodeFrame(5, false, false, false) == 1);
    CHECK(au::resNodeFrame(5, true, false, false) == 0);
    CHECK(au::resNodeFrame(5, false, true, false) == 3);
    CHECK(au::resNodeFrame(5, true, true, false) == 3);
    // hover overrides EVERY earlier write:
    CHECK(au::resNodeFrame(5, false, false, true) == 2);
    CHECK(au::resNodeFrame(5, true, false, true) == 2);
    CHECK(au::resNodeFrame(5, false, true, true) == 2);
    CHECK(au::resNodeFrame(5, true, true, true) == 2);
}

// 3. COLOUR MEASUREMENT pin: frame 2 is blue at pixels (R < G < B with a
//    strong blue channel) and frame 0 (the post-commit studied ring) is
//    warm (R > G > B) — the two-word model behind D28 19/20. Values are
//    MEASURED means over the decoded record plane (828 px, the
//    tRSV1d-witnessed render set) x game.pal 6->8; tolerances +-6 catch
//    transcription drift of a channel or digit (libs are static data).
TEST(ringcolour_blue_warm_tpf10) {
    const std::string R = ASCENDANCY_SOURCE_DIR;
    ascend::formats::GamePalette pal;
    std::string err;
    if (!pal.load(R + "/extracted/ascend01/data/game.pal", &err)) {
        std::printf("ringcolour pin: palette unavailable (%s) — SKIP\n",
                    err.c_str());
        return;
    }
    ascend::formats::ShapeLibrary lib;
    if (!lib.load(R + "/extracted/ascend01/data/resring.shp", &err) ||
        lib.count() < 4) {
        std::printf("ringcolour pin: resring unavailable — SKIP\n");
        return;
    }
    auto ringMean = [&](int rec, int out[3]) {
        std::vector<uint8_t> px;
        if (!lib.decode(rec, px)) return false;
        const int w = lib.record(rec).width, h = lib.record(rec).height;
        if (int(px.size()) != w * h) return false;
        long s[3] = {0, 0, 0};
        int n = 0;
        for (int i = 0; i < w * h; ++i) {
            if (px[i] == 0) continue;  // transparent field
            uint32_t a = pal.argb(px[i]);
            s[0] += (a >> 16) & 0xff;
            s[1] += (a >> 8) & 0xff;
            s[2] += a & 0xff;
            ++n;
        }
        if (n < 700) return false;  // port decode fills the full 29x29
                                   // plane (tRSV1d witness n=828)  // ring coverage sanity (measured 197)
        out[0] = int(s[0] / n); out[1] = int(s[1] / n); out[2] = int(s[2] / n);
        return true;
    };
    int m2[3], m0[3], m1[3], m3[3];
    CHECK(ringMean(2, m2));
    CHECK(ringMean(0, m0));
    CHECK(ringMean(1, m1));
    CHECK(ringMean(3, m3));
    // frame 2 BRIGHT BLUE (measured 69,149,192 under the port 6->8 law): blue dominant, luminance
    // clearly above the dim default frame.
    CHECK(m2[2] > m2[1] && m2[1] > m2[0]);
    CHECK(m2[2] >= 192 && m2[2] <= 204);
    CHECK(m2[0] >= 70 && m2[0] <= 82);
    // frame 0 WARM (measured 158,92,63): red dominant.
    CHECK(m0[0] > m0[1] && m0[1] > m0[2]);
    // frame 2 is the BRIGHTEST frame (hover highlight must be visible):
    const long lum2 = m2[0] + m2[1] + m2[2];
    const long lum1 = m1[0] + m1[1] + m1[2];
    const long lum3 = m3[0] + m3[1] + m3[2];
    CHECK(lum2 > lum1 && lum2 > lum3);
}

// 4. WIRING (source-text, tPF-7 M4 lesson — pins are blind to ui.cpp):
//    (a) the MOTION leg calls researchHit + resHoverWord on the research
//        screen (hover highlight item 20);
//    (b) the PUMP leg re-hits via SDL_GetMouseState (item 19 "exit and
//        return" persistence law: re-entry clears, hover re-acquires);
//    (c) the CLICK leg uses resHoverWord, NOT a bare latch — and the
//        retired misnomer comment "vendor selection word" is GONE;
//    (d) the re-entry clear resSel = -1 survives (window-init 0x476f2).
TEST(hoverwiring_tpf10) {
    std::ifstream f(std::string(ASCENDANCY_SOURCE_DIR) +
                    "/rewrite/src/ui/ui.cpp");
    CHECK(f.is_open());
    std::string src((std::istreambuf_iterator<char>(f)),
                    std::istreambuf_iterator<char>());
    // (a) motion leg: the hover-word call appears inside the MOTION block
    //     (statement-window scan anchored at the block's unique token —
    //     a MOUSEMOTION-anchored 3000-char window BLEEDS into the click
    //     arm and goes vacuous: witnessed by mutation M3 round 1).
    const std::string kMotionTok =
        "if (screen == kScreenResearch && camp.researchTree()) {\n"
        "                    const auto nodes =\n"
        "                        researchNodes(camp, *camp.researchTree(), ag::kPlayer);";
    const auto motionAt = src.find(kMotionTok);
    CHECK(motionAt != std::string::npos);
    // GUARD: CHECK doesn't return (tPF-10 witness: an unguarded
    // substr(npos) threw out_of_range and ABORTED run_tests — a crash, not
    // a clean FAIL). Absent token => skip the window checks, the CHECK
    // above already failed.
    if (motionAt != std::string::npos) {
        const auto win = src.substr(motionAt, 900);
        CHECK(win.find("resHoverWord(resSel, h)") != std::string::npos);
        CHECK(win.find("researchHit(") != std::string::npos);
    }
    // (b) pump leg: SDL_GetMouseState + resHoverWord inside the resCam
    //     pump block.
    const auto pumpAt = src.find("lastResPumpMs >= (Uint32)ResCam::kPumpMs");
    CHECK(pumpAt != std::string::npos);
    if (pumpAt != std::string::npos) {
        const auto pwin = src.substr(pumpAt, 2000);
        CHECK(pwin.find("SDL_GetMouseState") != std::string::npos);
        CHECK(pwin.find("resHoverWord(resSel, h)") != std::string::npos);
    }
    // (c) click leg uses the helper; the bare-latch misnomer comment gone.
    CHECK(src.find("resSel = resHoverWord(resSel, h);") != std::string::npos);
    CHECK(src.find("vendor selection word") == std::string::npos);
    // (d) re-entry clear (0x476f2 analog) still present.
    CHECK(src.find("resSel = -1;") != std::string::npos);
}
