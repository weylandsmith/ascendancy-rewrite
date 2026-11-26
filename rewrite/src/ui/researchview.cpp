// SPDX-License-Identifier: GPL-3.0-or-later

// t408 RESEARCH SCREEN law implementation — see researchview.h for the full
// citation block (windows.txt state-20 census, help reswin click law,
// static.txt #122/#124/#125/#130, the ui-runtime.md 6d ALLOWS reverse join,
// the t252/t268 native-vision grades).

#include "ui/researchview.h"

#include <algorithm>
#include <cmath>
#include <unordered_map>

namespace ascend::ui {

namespace ag = ascend::game;

std::vector<TechNode> researchNodes(const ag::Campaign& camp,
                                    const ag::ResearchTree& tree,
                                    int owner) {
    std::vector<TechNode> out;
    const int n = tree.mainCount();  // variants never load (research.md §6c)
    out.reserve(n);
    for (int r = 0; r < n; ++r) {
        TechNode nd;
        nd.row = r;
        if (camp.techRowOwnedFor(owner, r)) {
            nd.state = TechNodeState::Owned;
        } else {
            bool prereqsOk = true;
            for (int p : tree.all()[r].prereqs)
                if (!camp.techRowOwnedFor(owner, p)) { prereqsOk = false; break; }
            if (prereqsOk)
                nd.state = camp.isTechQueuedFor(owner, r) ? TechNodeState::Study
                                                          : TechNodeState::Available;
            else
                nd.state = TechNodeState::Blocked;
        }
        out.push_back(nd);
    }
    return out;
}

bool setStudy(ag::Campaign& camp, const ag::ResearchTree& tree, int owner,
              int row) {
    // help reswin: "empty disks represent technologies you CAN CHOOSE TO
    // STUDY ... click on an empty disk to make it your current topic".
    // Everything else is a silent no-op (t268: discovered disk = readout
    // only; no capture shows any reject feedback).
    if (row < 0 || row >= tree.mainCount()) return false;
    if (camp.techRowOwnedFor(owner, row)) return false;
    for (int p : tree.all()[row].prereqs)
        if (!camp.techRowOwnedFor(owner, p)) return false;
    camp.setQueuedTechFor(owner, row);
    return true;
}

std::string researchHeaderText(const std::string& ownerName) {
    // static #130 "%s Knowledge %s": the captures (t252/t268) render only
    // "<race> Knowledge" — the second slot never appears filled. Seam named
    // in the header block; the join is what the witness shows.
    return ownerName + " Knowledge";
}

std::vector<std::string> allowsList(const ag::Campaign& camp, int row) {
    // ALLOWS LAW [verified 3/3, ui-runtime.md 6d]: gizmos + planitems whose
    // tech field == row, in TABLE ORDER (the Energy Focusing witness rendered
    // gizmos.txt:230 then :260). '^' -> ' ' is the loader display law
    // (research.md §6a: names in RAM never contain '^').
    auto spaced = [](std::string s) {
        for (char& c : s) if (c == '^') c = ' ';
        return s;
    };
    std::vector<std::string> out;
    const int ng = camp.gizmoCount();
    for (int i = 0; i < ng; ++i) {
        const ag::Gizmo* g = camp.gizmoAt(i);
        if (g && g->resReq == row) out.push_back(spaced(g->name));
    }
    const int ni = camp.planItemCount();
    for (int i = 0; i < ni; ++i) {
        const ag::PlanetItem* it = camp.planetItem(i);
        if (it && it->reqByte == row) out.push_back(spaced(it->name));
    }
    return out;
}

std::string researchDaysLine(double remaining, double rateLastTurn) {
    // #124 "(%d day%s)"; singular iff N == 1 (the t402/t407 plural-pair
    // law). PORT DEFAULT ETA: ceil(remaining / last-turn rate); rate<=0 ->
    // 0 (the vendor rate law is unmeasured — n=2 dossier points, F6).
    double days = 0.0;
    if (rateLastTurn > 0.0 && remaining > 0.0)
        days = std::ceil(remaining / rateLastTurn);
    const int n = static_cast<int>(days);
    return "(" + std::to_string(n) + (n == 1 ? " day)" : " days)");
}

// ---- tRS-V1c: THE VENDOR TREE GEOMETRY (supersedes the t408 derived grid
// and the t419 flat-field law; law docs/re/_wip_tRSV1.md P1-P12) -----------
//
// DEPTH (P1b, 0x471f9..0x472c5): multi-pass relaxation. A row is assigned
// only once EVERY prereq carries a value; the value is max(A[p]+1). The
// vendor's [esp+0xf4] "a pass set no unmarked-prereq flag" gate is the loop
// exit; rows whose prereqs are all assigned are skipped on later passes
// (done[] marks finality since 0 is a legal depth).
//
// esi (the column count) is the vendor's own accumulator: esi starts 0 and
// every relaxation step over an ASSIGNED prereq takes esi = max(esi, A[p]+2)
// (0x472xx); on the shipped 66-row tree this measures 18 = maxdepth+1
// (_wip P8). DEVIATION (labelled): the placement loop is clamped to place
// EVERY column (the vendor loop is k < esi; a tree whose deepest row were a
// leaf would leave it unplaced there — no such row exists in restree.txt,
// pinned).
//
// PLACEMENT (P1c/P11, 0x472d4..0x47472): one CIRCLE per depth column k.
//   C[k] = rows at depth k; acc0 = 240+30k degrees; per node i (FILE order):
//   Y = 30k + 15*(i&1); Z0 = (i==0 ? R0(k) : 23); X = 0;
//   X' = Z0*sin(acc), Z' = Z0*cos(acc) (0x5324c VERBATIM at X=0);
//   acc += int(360/d) as REPEATED f32 adds (0x4743d: INTEGER division
//   first). R0/d rules per P1c. DEVIATION (labelled): libm double sin/cos
//   in place of the Borland x87 fprem-loop fsin/fcos — the x87 result is an
//   f32 within ~1 ulp; at the 7-9x reswin scale that is sub-pixel.
ResearchGeom researchTreeGeometry(const ag::ResearchTree& tree) {
    ResearchGeom G;
    const int n = tree.mainCount();  // variants never load (research.md 6c)
    G.depth.assign(size_t(n), -1);   // -1 == the vendor 0xff sentinel
    G.slot.assign(size_t(n), -1);
    G.world.assign(size_t(n), ResWorld{});

    // -- P1b relaxation passes ------------------------------------------
    int esi = 0;
    bool progress = true;
    while (progress) {
        progress = false;
        for (int r = 0; r < n; ++r) {
            if (G.depth[r] != -1) continue;
            bool ready = true;
            int best = 0;
            for (int p : tree.all()[r].prereqs) {
                if (p < 0 || p >= n) continue;
                if (G.depth[p] == -1) { ready = false; break; }
                best = std::max(best, G.depth[p] + 1);
                esi = std::max(esi, G.depth[p] + 2);
            }
            if (!ready) continue;
            G.depth[r] = best;
            progress = true;
        }
    }
    // Cycles (a loader bug, research.md 2) would strand rows at -1: place
    // them at depth 0 rather than crash (labelled guard; 66/66 converge).
    int maxDepth = 0;
    for (int r = 0; r < n; ++r) {
        if (G.depth[r] == -1) G.depth[r] = 0;
        maxDepth = std::max(maxDepth, G.depth[r]);
    }
    G.esi = std::max(esi, maxDepth + 1);  // clamp law above

    // -- C[k] counts (0x472e6..0x47300) ---------------------------------
    G.C.assign(size_t(G.esi), 0);
    for (int r = 0; r < n; ++r) ++G.C[size_t(G.depth[r])];

    // -- the chain of circles (0x47333..0x47472) ------------------------
    constexpr double kDeg2Rad = 0.0174532924;  // ds:0x88b88 f32 VERBATIM
    for (int k = 0; k < G.esi; ++k) {
        const int c = G.C[size_t(k)];
        int d = c;
        int r0 = 4;
        if ((k & 1) == 0) {
            if (c > 1) r0 = 23;                    // 0x473b1 even leg
        } else if (c > 2) {
            d = c - 1;                             // 0x47373 `dec ebp`
        } else {
            r0 = (c == 2) ? 23 : 4;                // 0x473b1 odd leg
        }
        float acc = float(240 + 30 * k);           // 0x47352 fild
        int i = 0;
        for (int r = 0; r < n; ++r) {              // FILE order
            if (G.depth[r] != k) continue;
            ResWorld w;
            w.x = 0.0f;                            // 0x47432
            w.y = float(30 * k + 15 * (i & 1));    // 0x473fd..0x4741e
            const double R = (i == 0) ? double(r0) : 23.0;  // 0x47421/0x47458
            const double th = double(acc) * kDeg2Rad;
            w.x = float(R * std::sin(th));         // 0x5324c at X=0
            w.z = float(R * std::cos(th));
            G.world[size_t(r)] = w;
            G.slot[size_t(r)] = i;
            ++i;
            if (d > 0) acc += float(int(360 / d));  // 0x4743d INTEGER div
            // (d==0 with a non-empty column cannot occur: d = C or C-1 >= 1
            // for C>=1 on every branch above — TRSV1-A closed, _wip P8.)
        }
    }
    return G;
}

int researchDepth(const ag::ResearchTree& tree, int row) {
    const auto G = researchTreeGeometry(tree);
    if (row < 0 || row >= int(G.depth.size())) return 0;
    return G.depth[size_t(row)];
}

double resFocal() {
    // 0x203b8 args (30.0 fov, ..., 320); 0x203e4: focal = 320/tan(fov/2).
    return 320.0 / std::tan(15.0 * 3.14159265358979323846 / 180.0);
}

int resVendorRound(double v) {
    // 0x76e08: RC=chop frndint == trunc toward zero (the caller has already
    // added the +0.5 bias). -2.2 -> -2, 2.7 -> 2.
    return int(v);
}

// The vendor word arithmetic of 0x53374's trailing `add word[...]`: the
// projection value and the +235/+240 centres are u16 WORDS.
static int u16wrap(long v) { return int(std::uint16_t(v & 0xffff)); }

std::vector<ResPoint3> researchNodeScreen(const ResearchGeom& geom,
                                          const std::vector<TechNode>& nodes,
                                          int panX, int panY,
                                          const ResCam& cam) {
    // Basis (0x53504 yaw mix on win+0x11f = the 0x5324c world-Y rotation of
    // the identity basis; t416 law): right = (cos,0,-sin), up = (0,1,0),
    // fwd = (-sin,0,cos). View = M*world + t, t = -pos (0x20414) with
    // pos = (0,0,posZ): vX = X cos - Z sin; vY = Y; vZ = X sin + Z cos - posZ.
    const double th = cam.yawDeg * 3.14159265358979323846 / 180.0;
    const double cs = std::cos(th), sn = std::sin(th);
    const double focal = resFocal();
    std::vector<ResPoint3> out;
    out.reserve(nodes.size());
    for (const TechNode& nd : nodes) {
        ResPoint3 s;
        s.legal = nd.state != TechNodeState::Blocked;  // 0x46d3c (P10)
        if (nd.row >= 0 && nd.row < int(geom.world.size())) {
            const ResWorld& w = geom.world[size_t(nd.row)];
            const double vX = double(w.x) * cs - double(w.z) * sn;
            const double vY = double(w.y);
            const double vZ = double(w.x) * sn + double(w.z) * cs - cam.posZ;
            s.z2 = vZ;
            // Port guard (labelled): the vendor divides unconditionally into
            // a u16 word (wraps); never draw/hit a row at or behind the eye.
            if (s.legal && vZ >= 1.0) {
                s.visible = true;
                const int px = u16wrap(
                    resVendorRound(focal * vX / vZ + 0.5) + 235);
                const int py = u16wrap(
                    resVendorRound(focal * vY / vZ + 0.5) + 240);
                // Vendor absolute -> this frame: the RESWIN rect sits at the
                // full-frame origin (windows.txt 7,46-476,472), so the word
                // IS the pixel; panX/panY are the labelled port affordance.
                s.x = px + panX;
                s.y = py + panY;
            }
        }
        out.push_back(s);
    }
    return out;
}

ResPoint researchNodePos(const ag::ResearchTree& tree, int row, int panX,
                         int panY, const ResCam& cam) {
    const auto G = researchTreeGeometry(tree);
    if (row < 0 || row >= int(G.world.size())) return ResPoint{0, 0};
    const double th = cam.yawDeg * 3.14159265358979323846 / 180.0;
    const double cs = std::cos(th), sn = std::sin(th);
    const ResWorld& w = G.world[size_t(row)];
    const double vX = double(w.x) * cs - double(w.z) * sn;
    const double vZ = double(w.x) * sn + double(w.z) * cs - cam.posZ;
    if (vZ < 1.0) return ResPoint{0, 0};
    return ResPoint{u16wrap(resVendorRound(resFocal() * vX / vZ + 0.5) + 235) +
                        panX,
                    u16wrap(resVendorRound(resFocal() * double(w.y) / vZ + 0.5) +
                            240) +
                        panY};
}

int ResCam::pressPair(int state, bool pairB) {
    // dat_764c4 bit-pair transitions (0x47b44..0x47c42 VERBATIM, P11).
    // Encoding 0=(0,0) 1=(1,0) 2=(1,1) 3=(0,1).
    if (!pairB) {  // pair A (msg 50 ROTLEFT / 52 MOVEUP)
        // (0,0)->start(1,0); (1,0)->stop(0,0); (1,1)->DEAD(0,1);
        // (0,1)->revive-left(1,0).
        switch (state) { case 0: return 1; case 1: return 0;
                         case 2: return 3; default: return 1; }
    }
    // pair B (msg 51 ROTRIGHT / 53 MOVEDOWN): every state -> (1,1)
    // except (1,1)->(1,0) (the 0x47b44..0x47c42 chain, P11).
    return (state == 2) ? 1 : 2;
}

void ResCam::tick() {
    // Pump deltas (0x47c88..0x47d12 VERBATIM): rot (1,0)->+3, (1,1)->-3,
    // DEAD/none nothing; move (1,0)->-1, (1,1)->+1 x kDollyStep.
    if (latchRot == 1) yawDeg += kRotStepDeg;
    else if (latchRot == 2) yawDeg -= kRotStepDeg;
    if (latchMove == 1) posZ -= kDollyStep;
    else if (latchMove == 2) posZ += kDollyStep;
}

int resNodeFrame(int row, bool studied, bool owned, bool hover) {
    // 0x483fa..0x48470 VERBATIM (P10): esi=1 default; studied-and-not-owned
    // -> 0; owned -> 3; the HOVER word (win+0x9db, tPF-10) overrides with 2
    // LAST (0x48460..0x4846b) — a hovered owned row draws frame 2.
    int esi = 1;
    if (studied && !owned) esi = 0;
    if (owned) esi = 3;
    if (hover) esi = 2;
    (void)row;
    return esi;
}

int resEdgeColorIndex(double z_this, double z_prereq, double posz) {
    // 0x482a8..0x482c7 VERBATIM (P11 corrected): k = chop(0.25f*(0.5f*(
    // z_this+z_prereq) + posz)) clamped to +-3; colour index 0x6b - k.
    double k = 0.25 * (0.5 * (z_this + z_prereq) + posz);
    int ki = resVendorRound(k);
    if (ki < -3) ki = -3;
    if (ki > 3) ki = 3;
    return 0x6b - ki;
}

ResHitResult researchHit(const ag::ResearchTree& tree,
                         const std::vector<TechNode>& nodes, int px, int py,
                         int panX, int panY, const ResCam& cam) {
    ResHitResult h;
    // Pan buttons FIRST (they live outside the RESWIN rect; t405/t407
    // precedence law). Verbatim rects (windows.txt).
    auto in = [](const Rect& r, int x, int y) {
        return x >= r.x0 && x <= r.x1 && y >= r.y0 && y <= r.y1;
    };
    if (in(kResRotLeft, px, py))   { h.kind = ResHit::RotLeft;   return h; }
    if (in(kResRotRight, px, py))  { h.kind = ResHit::RotRight;  return h; }
    if (in(kResMoveUp, px, py))    { h.kind = ResHit::MoveUp;    return h; }
    if (in(kResMoveDown, px, py))  { h.kind = ResHit::MoveDown;  return h; }
    // Nodes: THE VENDOR HIT LAW (tRS-B1, sub 0x47478 @0x474fb..0x4752d):
    // INCLUSIVE +-24 SQUARE on the PROJECTED centre, fixed size. tRS-V1c:
    // the scan gates the SAME 0x46d3c legality as the draw (Blocked rows are
    // not tested at all) and walks rows HIGH->low taking the FIRST hit —
    // observable now that the circle layout lets boxes overlap (nearest wins
    // was only equivalent on the old non-overlapping grid).
    const auto centres =
        researchNodeScreen(researchTreeGeometry(tree), nodes, panX, panY, cam);
    for (int i = int(nodes.size()) - 1; i >= 0; --i) {
        if (!centres[size_t(i)].visible) continue;
        const long dx = px - centres[size_t(i)].x;
        const long dy = py - centres[size_t(i)].y;
        if (dx < -kResHitHalf || dx > kResHitHalf) continue;
        if (dy < -kResHitHalf || dy > kResHitHalf) continue;
        h.kind = ResHit::Node;
        h.row = nodes[size_t(i)].row;
        return h;
    }
    return h;
}

// tRS-V2p: THE DISK FILL LAW VERBATIM (research.md S9(b), raw-stepper cited
// 0x481aa..0x48239). Branch order matters: owned beats studied.
int resDiskQ(bool owned, bool studied, int progress, int runtimeCost) {
    if (owned) return 20;                            // 0x481ce
    if (!studied) return 0;                          // 0x481aa default +
                                                     // 0x481f1 jne exit
    if (runtimeCost <= 0) return 0;                  // SEAM TRSV2p-A: the
                                                     // vendor idivs blind
    const int q = (progress * 18) / runtimeCost + 2;  // 0x48205..0x48218
    if (q < -17) return -17;                          // 0x48222..0x48227
    if (q > 17) return 17;                            // 0x48234..0x48239
    return q;
}

double resDiskFill(int q) { return double(q) / 20.0; }  // 0x48390..0x4839d

}  // namespace ascend::ui
