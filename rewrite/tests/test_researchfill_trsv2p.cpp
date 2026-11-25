// SPDX-License-Identifier: GPL-3.0-or-later

// tRS-V2p THE RESEARCH DISK FILL LAW + ITS PORT SURFACE (law docs/re/
// research.md S9; working record docs/re/_wip_tRSV2.md P1-P8).
//
// Vendor chain (raw-stepper cited 0x481aa..0x48239 + 0x48383..0x483f7):
//   q = 0;                                        ; unowned AND not-studied
//   if owned mask: q = 20;                        ; 0x481ce  (16.16 0x10000)
//   else if row == studied word:
//     q = (word[0x764a0+2*row] * 18) / word[rec+0x3e] + 2;   ; 0x48205..218
//     clamp q [-17, +17];                         ; 0x48222/0x48234 AFTER +2
//   if q == 0 SKIP the picture blit (0x4838c); else scale = q/20 (the
//   shl 16 / idiv 20 at 0x48390..0x4839d IS 16.16 of q/20).
// CONSEQUENCE the pins encode: the studied branch MAXES AT 17 (at p=cost
// the raw arithmetic gives 20, the clamp cuts it to 17 = 0.85); q=20 is
// reachable ONLY via the owned leg. The _wip P7 draft's "p=cost -> 20"
// line was wrong against the cited clamp — corrected in research.md S9(c).
#include "formats/shp.h"
#include "ui/researchview.h"

#include <cstdio>
#include <fstream>
#include <string>

#include "harness.h"

#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif

namespace {
namespace au = ascend::ui;
const std::string kRepo = ASCENDANCY_SOURCE_DIR;
}  // namespace

TEST(researchfill_empty_disk_tRSV2) {
    // 0x481aa default + 0x481f1 jne exit: unowned AND not the studied row
    // -> q == 0 -> the 0x4838c guard skips the picture: EMPTY disk.
    CHECK(au::resDiskQ(false, false, 0, 220) == 0);
    // Progress on a NON-studied row never leaks (the vendor indexes
    // word[0x764a0+2*row] only behind the studied-row compare).
    CHECK(au::resDiskQ(false, false, 9999, 220) == 0);
    CHECK(au::resDiskFill(0) == 0.0);
}

TEST(researchfill_select_sliver_tRSV2) {
    // SELECT at progress 0: q = 0*18/cost + 2 = 2 (the +2 at 0x48218 is
    // the on-select sliver the D27 law names): fill 2/20 = 0.1.
    CHECK(au::resDiskQ(false, true, 0, 220) == 2);
    CHECK(au::resDiskFill(2) == 0.1);
    // 16.16 cross-check of the blit quotient (0x48390..0x4839d: q<<16
    // idiv 20, truncating): q=2 -> 131072/20 = 6553 = 0x1999.
    CHECK(2 * 65536 / 20 == 0x1999);
}

TEST(researchfill_midway_tRSV2) {
    // p = cost/2 with an even cost: q = (cost/2*18)/cost + 2 = 9 + 2 = 11
    // (fill 0.55). 16.16: 11*65536/20 = 36044 = 0x8CCC.
    CHECK(au::resDiskQ(false, true, 110, 220) == 11);
    CHECK(au::resDiskFill(11) == 0.55);
    CHECK(11 * 65536 / 20 == 0x8CCC);
    // Monotone in progress at fixed cost (the "widens" half of D27).
    int prev = -1;
    for (int p = 0; p <= 220; p += 11) {
        const int q = au::resDiskQ(false, true, p, 220);
        CHECK(q >= prev);
        prev = q;
    }
    CHECK(prev == 17);  // clamped before completion
}

TEST(researchfill_cost_clamps_to_17_tRSV2) {
    // THE CORRECTED LEG: raw arithmetic at p=cost is 18+2=20, the clamp
    // legs 0x48222/0x48234 (fired AFTER add eax,2) cut it to 17. The
    // final 15% of the wipe is the OWN-completion JUMP 17 -> 20.
    CHECK(au::resDiskQ(false, true, 220, 220) == 17);
    // Engineered over-progress (the P7 "q>17" leg): any p >= 19/18*cost
    // saturates at 17.
    CHECK(au::resDiskQ(false, true, 2 * 220, 220) == 17);
    CHECK(au::resDiskQ(false, true, 65535, 100) == 17);
    CHECK(au::resDiskFill(17) == 0.85);
}

TEST(researchfill_owned_full_tRSV2) {
    // 0x481ce: owned -> q = 20 REGARDLESS of progress/studied (16.16
    // 0x10000 = full picture; ring law flips frame 3 on the same field).
    CHECK(au::resDiskQ(true, false, 0, 220) == 20);
    CHECK(au::resDiskQ(true, true, 0, 220) == 20);
    CHECK(au::resDiskQ(true, true, 7, 220) == 20);
    CHECK(au::resDiskFill(20) == 1.0);
}

TEST(researchfill_cost_zero_seam_tRSV2) {
    // SEAM TRSV2p-A: the vendor idivs the cost word blind (SIGFPE class);
    // the port refuses with q=0 (empty disk) — no crash, no invented rate.
    CHECK(au::resDiskQ(false, true, 50, 0) == 0);
    CHECK(au::resDiskQ(false, true, 50, -5) == 0);
}

TEST(researchfill_art_centred_tRSV2) {
    // The blit composes dest = anchor + scale*bbox, so the picture stays
    // centred at every q/20 ONLY because restree.shp records are centred
    // about their anchor. MEASURED via the A1 BBOX-DIFF DIMS LAW (shp.md):
    // every record's signed quad is (-25,-25,24,24) -> content 50x50 with
    // L,T=(-25,-25) — centred on the anchor by construction (the raw u32
    // words at +0x10 are the R,B CORNERS, not dims; first-draft slip
    // corrected by the failing pin itself).
    ascend::formats::ShapeLibrary lib;
    std::string err;
    if (!lib.load(kRepo + "/extracted/ascend01/data/restree.shp", &err)) {
        std::printf("  note: restree.shp unavailable (%s)\n", err.c_str());
        return;
    }
    CHECK(lib.count() == 66);
    for (int k = 0; k < lib.count(); ++k) {
        const auto& r = lib.record(k);
        CHECK(r.left == -25 && r.top == -25);
        CHECK(r.width == 50 && r.height == 50);
    }
}

TEST(researchfill_wiring_tRSV2) {
    // Source-text wiring pin (the tNGS S29 precedent): ui.cpp must consult
    // the pure law behind the ring blit and load the picture lib.
    std::ifstream f(kRepo + "/rewrite/src/ui/ui.cpp");
    std::string src((std::istreambuf_iterator<char>(f)),
                    std::istreambuf_iterator<char>());
    CHECK(!src.empty());
    CHECK(src.find("resDiskQ(") != std::string::npos);
    CHECK(src.find("blitShapeScaleF(ren, kLibs[9], nd.row") !=
          std::string::npos);
    CHECK(src.find("\"restree.shp\"") != std::string::npos);
    // q==0 must be a SKIP, never a clamp-to-something.
    CHECK(src.find("if (q != 0)") != std::string::npos);
}
