// tPF-7b COSMOS/SYSTEMCAM PUMP CADENCE PINS (sibling defect of tPF-7).
// Law: docs/re/_wip_tPF7b.md P1-P3; superseded misread: cam3d.h kSpinTickMs=
// 1000 (the t302 "~1/s" was POLL-LIMITED — REFUTED-ROUTES "tNG-S S28").
//  1. kFireLoopMs = 34 self-consistency: 1000/34 passes/s must sit inside the
//     two independent measured bands (S30-X5 58.5+-1 deg/s / 2 deg = 29.25/s;
//     S28-X3 fire-count 28-33/s) and the 360-deg circuit inside the tngs_s28
//     pin band 5.4-6.3 s.
//  2. Wiring: BOTH pump gates in ui.cpp gate on Camera3d::kFireLoopMs; the
//     retired name kSpinTickMs must be GONE from ui.cpp and cam3d.h (a
//     re-tightening on the misread constant is the defect shape); the
//     change-only witness instruments exist.
#include <cmath>
#include <fstream>
#include <sstream>
#include <string>

#include "harness.h"
#include "ui/cam3d.h"

#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif

namespace au = ascend::ui;

static std::string slurp(const std::string& p) {
    std::ifstream in(p);
    std::stringstream ss;
    ss << in.rdbuf();
    return ss.str();
}

TEST(cam_pump_cadence_tpf7b) {
    // The derived fire-loop period (docs/re/_wip_tPF7b.md P2).
    CHECK(au::Camera3d::kFireLoopMs == 34);
    const double passes_per_s = 1000.0 / au::Camera3d::kFireLoopMs;
    // S30-X5 channel: 58.5 +-1 deg/s at the verbatim 2 deg tick.
    CHECK(passes_per_s >= 28.75 && passes_per_s <= 29.75);
    // S28-X3 independent channel: 28-33 fires/s.
    CHECK(passes_per_s >= 28.0 && passes_per_s <= 33.0);
    // Circuit law (tngs_s28 precedent): 360 deg lands in 5.4-6.3 s wall.
    const double circuit = 360.0 / au::Camera3d::kRotStepDeg *
                           au::Camera3d::kFireLoopMs / 1000.0;
    CHECK(circuit >= 5.4 && circuit <= 6.3);
    // The misread value must not return under any name here.
    CHECK(au::Camera3d::kFireLoopMs < 100);
}

TEST(cam_pump_wiring_tpf7b) {
    const std::string ui = slurp(std::string(ASCENDANCY_SOURCE_DIR) +
                                 "/rewrite/src/ui/ui.cpp");
    const std::string h = slurp(std::string(ASCENDANCY_SOURCE_DIR) +
                                "/rewrite/src/ui/cam3d.h");
    if (ui.empty() || h.empty()) { CHECK(!"source unreadable"); return; }
    // Both gates switched to the shared constant (cosmos cam + systemCam).
    size_t n = 0;
    for (size_t pos = ui.find("Camera3d::kFireLoopMs"); pos != std::string::npos;
         pos = ui.find("Camera3d::kFireLoopMs", pos + 1))
        n++;
    CHECK(n == 2);  // exactly the two pump gates
    // Retired constant fully removed (pins/comments included): a survivor
    // means someone re-anchored on the poll-limited 1000 ms reading.
    CHECK(ui.find("kSpinTickMs") == std::string::npos);
    CHECK(h.find("kSpinTickMs") == std::string::npos);
    CHECK(h.find("static constexpr int kFireLoopMs = 34;") != std::string::npos);
    // Witness instruments (change-only pump census lines).
    CHECK(ui.find("ui cosmos pump yaw") != std::string::npos);
    CHECK(ui.find("ui sysview pump yaw") != std::string::npos);
    // The research pump keeps its own closed constant (tPF-7): touching it
    // here would silently re-open a CLOSED row's shipped law.
    CHECK(ui.find("ResCam::kPumpMs") != std::string::npos);
}
