// SPDX-License-Identifier: GPL-3.0-or-later

// tPF-7 RESEARCH CONTROL LAWS: release leg + pump cadence
// (D28 items 16/17/18; law docs/re/_wip_tPF7.md P1-P6).
//
//   1. RELEASE LAW (0x47d3b shape): releasing a pair clears it from EVERY
//      latched state, and clears ONLY that pair (the other keeps latching).
//   2. HOLD CYCLE: press-then-release is inert at the pump (a click must
//      not start permanent rotation — the exact item-17 complaint shape);
//      press-hold advances every tick; direction pair opposes.
//   3. PUMP CADENCE kPumpMs = 34: derived 1000 ms / (58.5 deg/s / 2 deg)
//      = 29.25 passes/s (P6); pins assert the derivation is INTERNALLY
//      consistent (34 ms * 29.25/s ~= 1000 ms) and that the old 1000 ms is
//      NOT the shipped constant.
//   4. WIRING (source-text): ui.cpp applies releaseRot/releaseMove on
//      SDL_MOUSEBUTTONUP, gates the research pump on ResCam::kPumpMs, and
//      zeroes the latches on screen exit (window-init 0x47679 law).
#include "ui/researchview.h"

#include <cmath>
#include <cstdio>
#include <fstream>
#include <sstream>
#include <string>

#include "harness.h"

#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif

namespace {
namespace au = ascend::ui;

std::string slurp(const std::string& p) {
    std::ifstream f(p);
    std::ostringstream ss;
    ss << f.rdbuf();
    return ss.str();
}
}  // namespace

namespace ascend::test {

TEST(research_release_law_tpf7) {
    // Release from every latched state clears the pair (0x47d3b AND-OUT;
    // 2-bit encoding => state 0), and NEVER touches the other pair.
    for (int s = 0; s <= 3; ++s) {
        au::ResCam c;
        c.latchRot = s;
        c.latchMove = s;
        c.releaseRot();
        CHECK(c.latchRot == 0);
        CHECK(c.latchMove == s);  // move pair untouched
        au::ResCam d;
        d.latchRot = s;
        d.latchMove = s;
        d.releaseMove();
        CHECK(d.latchMove == 0);
        CHECK(d.latchRot == s);  // rot pair untouched
    }
    // After release the camera is not "moving" (pump gates on moving()).
    au::ResCam c;
    c.pressRot(false);
    CHECK(c.moving());
    c.releaseRot();
    CHECK(!c.moving());
    c.pressMove(true);
    CHECK(c.moving());
    c.releaseMove();
    CHECK(!c.moving());
}

TEST(research_hold_cycle_tpf7) {
    // A held rotation advances exactly one tick, then the release freezes
    // it — the item-17 complaint ("latch on when clicked once") is exactly
    // a missing release leg: the vendor stops on button-up.
    au::ResCam b;
    b.pressRot(false);   // hold begins...
    b.tick();            // ...one tick of motion...
    b.releaseRot();      // ...then the release leg STOPS it
    const double yaw_after_hold = b.yawDeg;
    CHECK(yaw_after_hold == au::ResCam{}.yawDeg + au::ResCam::kRotStepDeg);
    // Post-release ticks change nothing (this is the anti-sticky property).
    b.tick();
    b.tick();
    CHECK(b.yawDeg == yaw_after_hold);

    // Press-hold: 5 ticks move monotonically; opposite press flips direction
    // WHILE still held (vendor (1,1) state); release stops everything.
    au::ResCam c;
    c.pressRot(false);                    // (1,0) => +3/tick
    double prev = c.yawDeg;
    for (int i = 0; i < 5; ++i) {
        c.tick();
        CHECK(c.yawDeg > prev);
        prev = c.yawDeg;
    }
    c.pressRot(true);                     // (1,1) => -3/tick, still moving
    CHECK(c.moving());
    c.tick();
    CHECK(c.yawDeg < prev);
    c.releaseRot();
    const double stop = c.yawDeg;
    c.tick();
    CHECK(c.yawDeg == stop);

    // Move pair opposes the same way and has the DEAD (0,1) state: press
    // pairA then pairA again reaches (0,0); press pairB from (0,0) reaches
    // (1,1)=2; the (0,1)=3 state pumps NOTHING (0x47cd0 bit0-clear leg).
    // tRS-SC: the pumped coordinate is posY (win+0xe3), rest 0; depth posZ
    // is NEVER pumped.
    au::ResCam m;
    m.pressMove(false);                   // (1,0) => posY -= 1/tick
    CHECK(m.latchMove == 1);
    m.tick();
    CHECK(m.posY < 0.0);
    CHECK(m.posZ == -150.0);              // depth invariant (tRS-SC)
    m.pressMove(true);                    // (1,1) => posY += 1/tick
    CHECK(m.latchMove == 2);
    double z = m.posY;
    m.tick();
    CHECK(m.posY > z);
    m.latchMove = 3;                      // vendor DEAD state (0,1)
    z = m.posY;
    m.tick();
    CHECK(m.posY == z);                   // pumps nothing
    m.releaseMove();
    CHECK(m.latchMove == 0);
}

TEST(research_pump_cadence_tpf7) {
    // kPumpMs is the framework fire-loop period: 1000/29.25 ms = 34.19 ms,
    // shipped rounded 34 (derivation _wip_tPF7.md P6 from the cited 58.5
    // deg/s live measurement / 2 deg cited cosmos pump delta).
    CHECK(au::ResCam::kPumpMs == 34);
    const double passes_per_s = 1000.0 / au::ResCam::kPumpMs;
    CHECK(std::fabs(passes_per_s - 29.25) < 1.0);  // 29.4 vs 29.25
    // The old kSpinTickMs reading must NOT govern the research pump (it was
    // a t302 first-fire-latency misread — 29x slow, the item-16 defect).
    CHECK(au::ResCam::kPumpMs < 100);
    // At the shipped cadence a held rotation covers >= 60 deg in 1 s
    // (3 deg * 29 passes), the vendor-feel floor from S30's 58.5+-1 deg/s.
    CHECK(au::ResCam::kRotStepDeg * passes_per_s >= 60.0);
}

TEST(research_release_wiring_tpf7) {
    const std::string s = slurp(std::string(ASCENDANCY_SOURCE_DIR) +
                                "/rewrite/src/ui/ui.cpp");
    if (s.empty()) { CHECK(!"ui.cpp unreadable"); return; }
    // Release leg exists on button-UP and picks the pair by tracker.
    CHECK(s.find("SDL_MOUSEBUTTONUP") != std::string::npos);
    CHECK(s.find("resCam.releaseRot()") != std::string::npos);
    CHECK(s.find("resCam.releaseMove()") != std::string::npos);
    // The research pump gates on the new cadence, not kSpinTickMs.
    CHECK(s.find("ResCam::kPumpMs") != std::string::npos);
    // Screen-exit clears the latch word (window-init 0x47679 law).
    CHECK(s.find("resCam.latchRot = resCam.latchMove = 0;") !=
          std::string::npos);
    // The press arms the hold tracker for both pairs (rot controls and move
    // controls each set their own tracker value).
    size_t n1 = 0, n2 = 0;
    for (size_t pos = s.find("resHold = 1"); pos != std::string::npos;
         pos = s.find("resHold = 1", pos + 1))
        ++n1;
    for (size_t pos = s.find("resHold = 2"); pos != std::string::npos;
         pos = s.find("resHold = 2", pos + 1))
        ++n2;
    CHECK(n1 >= 2);  // two rot controls
    CHECK(n2 >= 2);  // two move controls
}

}  // namespace ascend::test
