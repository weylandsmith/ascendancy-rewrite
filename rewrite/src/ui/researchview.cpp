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

// t419 STALL FIX. The old law re-walked the whole prereq graph once PER
// CALL, and researchNodePos called it O(row) times per node — the painter
// (ui.cpp kScreenResearch) then did that for every node every frame at
// ~60fps, pinning one core (D15 addendum; DECISIONS.md static root cause).
// The layout computes each row's depth ONCE (memoised iterative DFS over
// all rows, `done` marks finality since depth 0 is a legal value) and each
// row's column slot ONCE (single counting pass).
ResearchLayout researchLayoutFor(const ag::ResearchTree& tree) {
    ResearchLayout L;
    const int n = tree.mainCount();
    L.depth.assign(size_t(n), 0);
    L.slot.assign(size_t(n), 0);
    std::vector<char> done(size_t(n), 0);
    for (int r = 0; r < n; ++r) {
        if (done[r]) continue;
        std::vector<int> stack{r};
        while (!stack.empty()) {
            const int cur = stack.back();
            bool ready = true;
            for (int p : tree.all()[cur].prereqs) {
                if (p < 0 || p >= n || done[p]) continue;
                stack.push_back(p);
                ready = false;
                break;
            }
            if (!ready) continue;
            int best = 0;
            for (int p : tree.all()[cur].prereqs)
                if (p >= 0 && p < n) best = std::max(best, L.depth[p] + 1);
            L.depth[cur] = best;
            done[cur] = 1;
            stack.pop_back();
        }
    }
    // Column slots: row order within each depth column (the same posture
    // as the t402 membership-order default), plus the column-count maxima
    // for the bbox centre (the 3D rotation origin, law in the header).
    int maxDepth = 0;
    for (int d : L.depth) maxDepth = std::max(maxDepth, d);
    L.maxDepth = maxDepth;
    std::vector<int> count(size_t(maxDepth + 1), 0);
    int maxSlots = 0;
    for (int r = 0; r < n; ++r) {
        L.slot[r] = count[size_t(L.depth[r])]++;
        maxSlots = std::max(maxSlots, L.slot[r]);
    }
    L.cx = kResFieldX0 + maxDepth * kResDepthPitch / 2;
    L.cy = kResFieldY0 + maxSlots * kResRowPitch / 2;
    return L;
}

ResPoint researchNodePosAt(const ResearchLayout& layout, int row, int panX,
                           int panY) {
    if (row < 0 || row >= int(layout.depth.size())) return ResPoint{0, 0};
    return ResPoint{kResFieldX0 + layout.depth[size_t(row)] * kResDepthPitch +
                        panX,
                    kResFieldY0 + layout.slot[size_t(row)] * kResRowPitch +
                        panY};
}

int researchDepth(const ag::ResearchTree& tree, int row) {
    // t419: delegates to the one-shot layout (identical answers — pinned —
    // but O(n+e) per call instead of O(n x graph) per call).
    const auto L = researchLayoutFor(tree);
    if (row < 0 || row >= int(L.depth.size())) return 0;
    return L.depth[size_t(row)];
}

std::vector<ResPoint3> researchNodeScreen(const ResearchLayout& layout,
                                          const std::vector<TechNode>& nodes,
                                          int panX, int panY,
                                          const Camera3d& cam) {
    // Header 3D LAW: flat XY field centred on the layout bbox centre (y
    // flipped to field-up), t399 pinhole via projectPoint at the t416
    // basis; screen frame re-anchored at (cx, cy) so the REST basis yields
    // the t408 2D centres EXACTLY (focal == kResStandoff -> scale 1).
    std::vector<ResPoint3> out;
    out.reserve(nodes.size());
    for (const TechNode& nd : nodes) {
        const ResPoint p2 = researchNodePosAt(layout, nd.row, 0, 0);
        const double fx = double(p2.x - layout.cx);
        const double fy = -double(p2.y - layout.cy);  // screen-down -> up
        const Projected pr = projectPoint(cam, fx, fy, 0.0, kResStandoff);
        ResPoint3 s;
        s.x = layout.cx + int(pr.x) + panX;
        s.y = layout.cy - int(pr.y) + panY;  // field-up -> screen-down
        s.r = std::max(2, int(std::lround(double(kResNodeRadius) * pr.scale)));
        s.z2 = pr.z2;
        out.push_back(s);
    }
    return out;
}

ResPoint researchNodePos(const ag::ResearchTree& tree, int row, int panX,
                         int panY) {
    // Derived layout (labelled seam): column = longest-chain depth, slot =
    // row index within that depth column (row order == file order, the same
    // posture as the t402 membership-order default). t419: one-shot layout.
    return researchNodePosAt(researchLayoutFor(tree), row, panX, panY);
}

ResHitResult researchHit(const ag::ResearchTree& tree,
                         const std::vector<TechNode>& nodes, int px, int py,
                         int panX, int panY, const Camera3d& cam) {
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
    // Nodes: THE VENDOR HIT LAW (tRS-B1, sub 0x47478 @0x474fb..0x4752d,
    // work/tRS_reswin_fn.asm): per node the click must satisfy
    //   x-25 < cx < x+25  AND  y-25 < cy < y+25   (signed `jle/jge` rejects
    // at exactly +-25 => INCLUSIVE +-24 SQUARE, half-open at 25), a FIXED
    // half-size on the PROJECTED centre — the vendor does NOT scale the hit
    // box with the node's perspective radius, and it is a SQUARE not a disc
    // (corner clicks (24,24) hit; edge clicks at 25 miss). The vendor scan
    // walks rows high->low and takes the FIRST hit among LEGAL rows (call
    // 0x46d3c gates before the range test); with pitch 78/96 the +-24 boxes
    // never overlap, so nearest-among-hits (kept below) is equivalent —
    // labelled, not asserted as vendor-identical scan order.
    const auto centres =
        researchNodeScreen(researchLayoutFor(tree), nodes, panX, panY, cam);
    int bestRow = -1;
    long bestD2 = -1;
    for (size_t i = 0; i < nodes.size(); ++i) {
        const long dx = px - centres[i].x, dy = py - centres[i].y;
        if (dx < -kResHitHalf || dx > kResHitHalf) continue;
        if (dy < -kResHitHalf || dy > kResHitHalf) continue;
        const long d2 = dx * dx + dy * dy;
        if (bestRow < 0 || d2 < bestD2) { bestD2 = d2; bestRow = nodes[i].row; }
    }
    if (bestRow >= 0) { h.kind = ResHit::Node; h.row = bestRow; }
    return h;
}

}  // namespace ascend::ui
