// SPDX-License-Identifier: GPL-3.0-or-later

// tPF-7a RELEASE PARAM LAW + GATE-BIT EQUIVALENCE (seam TPF7-A closure;
// law docs/re/_wip_tPF7a.md P1-P5).
//
//   1. PARAM LAW (cited chain, _wip_tPF7a P2): the press tail arms msg
//      0x38 with queued PARAM = 1 after a MOVE press (msg 52/53) and 4
//      after a ROT press (msg 50/51); the one-shot dispatcher hands the
//      slot param to the handler VERBATIM (slot+0xa -> walker ecx ->
//      dispatch ebx -> handler ebp), so the release mask is ~1 (clears
//      the MOVE GATE bit0) or ~4 (clears the ROT GATE bit2). reswin's
//      only release producer is msg 0x38 — the "0x38 vs 0x39" framing was
//      a cross-window mis-map (ids 56/57/58 belong to COSMOSWnd).
//   2. GATE-BIT EQUIVALENCE: the vendor release preserves the DIRECTION
//      bit (clears only the gate); the port's pair-clear maps both
//      gate-clear states to code 0. Exhaustive check: for every raw latch
//      byte and every op sequence of length <= 4 (4 presses + 2 releases),
//      vendor model and port model produce identical per-step pump output
//      and identical gate state.
//   3. VENDOR MODEL FIDELITY: press legs reproduce the raw AND/OR
//      immediates (f7/fb pair-A-rot, fd/fe pair-A-move, or 0x8/0xc/0x2/
//      0x3 pair-B) byte-for-byte.
#include "ui/researchview.h"

#include <cmath>
#include <cstdio>

#include "harness.h"

namespace ascend::test {
namespace {
namespace au = ascend::ui;

// Raw vendor latch byte: bit0 move-gate, bit1 move-dir, bit2 rot-gate,
// bit3 rot-dir (0x47b44..0x47d4d census, _wip_tPF7a P1/P4).
int vendorPress(int L, int msg) {
    switch (msg) {
        case 0x32:  // rot left: gate bit2, dir bit3
            if (L & 4) return (L & 8) ? (L & ~8) : (L & ~4);  // f7 revive-left / fb stop
            return (L | 4) & ~8;                              // start (1,0)
        case 0x33:  // rot right
            if (L & 4) return (L & 8) ? (L & ~4) : (L | 8);   // fb DEAD / or 8
            return L | 0xc;                                   // or 0xc
        case 0x34:  // move up: gate bit0, dir bit1
            if (L & 1) return (L & 2) ? (L & ~2) : (L & ~1);  // fd flip / fe stop
            return (L | 1) & ~2;                              // start (1,0)
        case 0x35:  // move down
            if (L & 1) return (L & 2) ? (L & ~1) : (L | 2);   // fe DEAD / or 2
            return L | 3;                                     // or 3
        default:
            return L;
    }
}
int vendorRelease(int L, int param) { return L & ~param; }  // 0x47d41..0x47d4d

// Pump outputs per pass (0x47c88..0x47d12): gate tested FIRST, dir picks
// sign; gate-clear legs contribute exactly nothing.
void vendorTick(int L, double& dyaw, double& dpos) {
    if (L & 4) dyaw += (L & 8) ? -3.0 : 3.0;
    if (L & 1) dpos += (L & 2) ? 1.0 : -1.0;
}

// Raw byte -> port pair codes: (gate,dir) -> 0=(0,0) 1=(1,0) 2=(1,1)
// 3=(0,1).
int toPortCode(int gate, int dir) { return dir ? (gate ? 2 : 3) : (gate ? 1 : 0); }

void applyPort(au::ResCam& c, int op, int& vL) {
    switch (op) {
        case 0: c.pressRot(false);  vL = vendorPress(vL, 0x32); break;
        case 1: c.pressRot(true);   vL = vendorPress(vL, 0x33); break;
        case 2: c.pressMove(false); vL = vendorPress(vL, 0x34); break;
        case 3: c.pressMove(true);  vL = vendorPress(vL, 0x35); break;
        // Release ops use the PARAM LAW: move press armed param 1, rot
        // press armed param 4.
        case 4: c.releaseMove();    vL = vendorRelease(vL, 1); break;
        case 5: c.releaseRot();     vL = vendorRelease(vL, 4); break;
    }
}
}  // namespace

TEST(release_param_law_tpf7a) {
    // The shipped masks: param 1 kills ONLY the move gate, param 4 ONLY
    // the rot gate; direction bits survive (the vendor ~ebp AND-OUT).
    int L = 0;
    L = vendorPress(L, 0x35);            // move down: (1,1) move pair
    CHECK(L == 3);
    int r = vendorRelease(L, 1);         // the armed move release
    CHECK((r & 1) == 0);                 // move gate cleared
    CHECK((r & 2) != 0);                 // move DIR preserved (vendor DEAD)
    CHECK(r == vendorRelease(L, 1));
    L = vendorPress(0, 0x33);            // rot right: (1,1) rot pair
    r = vendorRelease(L, 4);
    CHECK((r & 4) == 0);
    CHECK((r & 8) != 0);
    // Cross-pair isolation: a move-armed release NEVER touches rot bits.
    L = 0xf;                             // both pairs (1,1)
    CHECK(vendorRelease(L, 1) == (0xf & ~1));
    CHECK(vendorRelease(L, 4) == (0xf & ~4));
    // A move-armed param on a rot-press state is vacuous, and vice versa —
    // exactly what makes release idempotent per pair.
    CHECK(vendorRelease(vendorPress(0, 0x33), 1) == vendorPress(0, 0x33));
}

TEST(release_gate_equivalence_tpf7a) {
    // EXHAUSTIVE: every raw latch byte x every op sequence of length 4
    // (ops 0..5: 4 presses, move-release, rot-release). The port's
    // pair-clear release must match the vendor gate-clear release on
    // EVERY pump step and on the surviving gate state.
    int ops[4];
    int mismatches = 0;
    for (int L0 = 0; L0 < 256; ++L0) {
        for (int seq = 0; seq < 6 * 6 * 6 * 6; ++seq) {
            ops[0] = seq % 6;
            ops[1] = (seq / 6) % 6;
            ops[2] = (seq / 36) % 6;
            ops[3] = (seq / 216) % 6;
            au::ResCam c;
            c.latchRot = toPortCode((L0 >> 2) & 1, (L0 >> 3) & 1);
            c.latchMove = toPortCode(L0 & 1, (L0 >> 1) & 1);
            int vL = L0;
            bool bad = false;
            for (int k = 0; k < 4 && !bad; ++k) {
                applyPort(c, ops[k], vL);
                double vy = 0.0, vz = 0.0;
                vendorTick(vL, vy, vz);
                const double py0 = c.yawDeg, pz0 = c.posY;
                c.tick();
                if (c.yawDeg - py0 != vy || c.posY - pz0 != vz) bad = true;
            }
            // Gate state must agree (dead-state code 0 vs 3 may differ).
            const int vgate = (vL & 5);
            const int pgate = ((c.latchRot == 1 || c.latchRot == 2) ? 4 : 0) |
                              ((c.latchMove == 1 || c.latchMove == 2) ? 1 : 0);
            if (vgate != pgate) bad = true;
            if (bad) {
                if (mismatches < 4)
                    std::printf("  mismatch L0=%02x seq=%d ops=%d%d%d%d vL=%02x\n",
                                L0, seq, ops[0], ops[1], ops[2], ops[3], vL);
                ++mismatches;
            }
        }
    }
    CHECK(mismatches == 0);
}

TEST(vendor_press_legs_match_port_pressPair_tpf7a) {
    // The port pressPair must equal the raw-immediate model on all four
    // controls x all four pair states (rot pair bits2/3, move pair bits0/1).
    for (int code = 0; code <= 3; ++code) {
        const int gate = (code == 1 || code == 2), dir = (code == 2 || code == 3);
        // rot pair A (msg 50) / B (msg 51)
        const int vA = vendorPress(4 * gate + 8 * dir, 0x32);
        au::ResCam a;
        a.latchRot = code;
        a.pressRot(false);
        const int pA = toPortCode((vA >> 2) & 1, (vA >> 3) & 1);
        CHECK(a.latchRot == pA);
        const int vB = vendorPress(4 * gate + 8 * dir, 0x33);
        au::ResCam b;
        b.latchRot = code;
        b.pressRot(true);
        CHECK(b.latchRot == toPortCode((vB >> 2) & 1, (vB >> 3) & 1));
        // move pair A (msg 52) / B (msg 53)
        const int vC = vendorPress(gate + 2 * dir, 0x34);
        au::ResCam m;
        m.latchMove = code;
        m.pressMove(false);
        CHECK(m.latchMove == toPortCode(vC & 1, (vC >> 1) & 1));
        const int vD = vendorPress(gate + 2 * dir, 0x35);
        au::ResCam n;
        n.latchMove = code;
        n.pressMove(true);
        CHECK(n.latchMove == toPortCode(vD & 1, (vD >> 1) & 1));
    }
}

}  // namespace ascend::test
