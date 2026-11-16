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

int researchDepth(const ag::ResearchTree& tree, int row) {
    // Longest prereq chain (research.md §3 spreads depths 0..17 on the live
    // 66 rows). Iterative memo to stay recursion-free on deep chains.
    static thread_local std::unordered_map<int, int> memo;
    memo.clear();
    for (int r = 0; r < tree.mainCount(); ++r) {
        // Walk up prereqs computing depth(r) on demand.
        std::vector<int> stack{r};
        while (!stack.empty()) {
            const int cur = stack.back();
            bool ready = true;
            for (int p : tree.all()[cur].prereqs) {
                if (p < 0 || p >= tree.mainCount()) continue;
                if (!memo.count(p)) { stack.push_back(p); ready = false; break; }
            }
            if (!ready) continue;
            int best = 0;
            for (int p : tree.all()[cur].prereqs)
                if (p >= 0 && p < tree.mainCount())
                    best = std::max(best, memo[p] + 1);
            memo[cur] = best;
            stack.pop_back();
        }
    }
    auto it = memo.find(row);
    return it == memo.end() ? 0 : it->second;
}

ResPoint researchNodePos(const ag::ResearchTree& tree, int row, int panX,
                         int panY) {
    // Derived layout (labelled seam): column = longest-chain depth, slot =
    // row index within that depth column (row order == file order, the same
    // posture as the t402 membership-order default).
    const int depth = researchDepth(tree, row);
    int slot = 0;
    for (int r = 0; r < row; ++r)
        if (researchDepth(tree, r) == depth) ++slot;
    return ResPoint{kResFieldX0 + depth * kResDepthPitch + panX,
                    kResFieldY0 + slot * kResRowPitch + panY};
}

ResHitResult researchHit(const ag::ResearchTree& tree,
                         const std::vector<TechNode>& nodes, int px, int py,
                         int panX, int panY) {
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
    // Nodes: nearest centre within the ring radius (only the visible tree
    // panel area hosts nodes; the panel clip is the painter's job).
    int bestRow = -1;
    long bestD2 = long{kResNodeRadius} * kResNodeRadius;
    for (const TechNode& nd : nodes) {
        const ResPoint c = researchNodePos(tree, nd.row, panX, panY);
        const long dx = px - c.x, dy = py - c.y;
        const long d2 = dx * dx + dy * dy;
        if (d2 <= bestD2) { bestD2 = d2; bestRow = nd.row; }
    }
    if (bestRow >= 0) { h.kind = ResHit::Node; h.row = bestRow; }
    return h;
}

}  // namespace ascend::ui
