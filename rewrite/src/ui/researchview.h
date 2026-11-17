// SPDX-License-Identifier: GPL-3.0-or-later

#pragma once
// t408: THE RESEARCH SCREEN LAW (state 20 RESWIN; D13 "research is empty" +
// "can't select a technology"). Pure module (no SDL), the statuslist.h /
// fleetlist.h precedent. Pins tests/test_researchview_t408.cpp; working log
// docs/re/_wip_t408.md.
//
//   WINDOW LAW [verified windows.txt]: TYPE-100 L1755-1758 binds state 20 to
//   DATA\20RES.SHP; RESWIN TYPE 9 rect 7,46-476,472 STATE "1 20" — and the
//   STATE "1 20" census is EXACTLY FIVE records (RESWIN + the four pan
//   buttons), so the RIGHT INFO PANEL (vision-measured x 484..632 on the
//   banked captures) is CODE-DRAWN, not a window-table child.
//   20res.shp holds the four arrow faces ONLY (6 records ~15x30, ui-runtime
//   .md t391) — tree art is restree.shp content (named seam), so the tree is
//   honestly-vector WITH citation.
//
//   NODE STATES + CLICK LAW [verified help.txt reswin ln1668-1690 verbatim]:
//   "Disks containing pictures represent technologies you have discovered,
//   and empty disks represent technologies you can choose to study. @@You
//   can click on an empty disk to make it your current topic of study."
//   Corroborated end-to-end by the t268 live dossier (ui-runtime.md 6d):
//   clicking an EMPTY disk set the topic (900 px change confined to the
//   clicked bbox, NO confirm popup); clicking a DISCOVERED disk is a dossier
//   read, NO state change. => setStudy(): Available -> queue it; Owned /
//   already-Studying / Blocked -> silent false (no reject feedback exists in
//   any capture).
//
//   PANEL TEXT LAW [verified static.txt reswin.cpp pool, marker-driven reader
//   (fleet-screen.md F10 law): #122 "Current Project:", #123 "(No Progress)",
//   #124 "(%d day%s)", #125 "Allows", #130 "%s Knowledge %s"]. The t252
//   capture (native-vision grade, F6) shows the panel lines in this order,
//   green, centred: #122, icon, wrapped tech name, "(16 days)", #125, first
//   Allows entry, art. The no-project capture (t268) shows the panel FULLY
//   BLANK — the port renders nothing when no tech is queued; #123 is pinned
//   as data, not as a rendered line. #130 carries a SECOND %s that no capture
//   ever shows filled -> the port joins name + " Knowledge" (seam named).
//
//   ALLOWS LAW [verified 3/3, ui-runtime.md 6d]: Allows(restree row N) =
//   reverse join of gizmos.txt + planitem.txt records whose tech field ==
//   idx (N-3 == the all() index == rewrite Tech row). rewrite Gizmo.resReq
//   and PlanetItem.reqByte ARE that field (economy.h), table order is the
//   rendered order (the two-entry Energy Focusing witness rendered in file
//   order).
//
//   DAYS: the "(N days)" line renders ONLY for the in-progress topic
//   [verified t268]. The vendor's N is rate-dependent (two dossier points:
//   cost 110 -> 33 days vs cost 120 -> 15 days — NOT a function of cost
//   alone; n=2, do not derive). PORT DEFAULT [labelled]: days = ceil of
//   remaining / last-turn research rate, rate<=0 -> 0 days. Strict-close:
//   closes nothing.
//
//   LAYOUT [port-derived, labelled]: restree.txt carries NO coordinates and
//   no banked capture covers the full 66-node field, so node placement is
//   the deterministic derived law below (depth by longest prereq chain x
//   row order). NAMED SEAM: the vendor's organic positions (the captures
//   prove non-grid placement) need a pointer-law capture of the reswin node
//   table to close.
//
//   PAN LAW [verified windows.txt + t252 pixel-diff]: four buttons OUTSIDE
//   the RESWIN rect — RESROTLEFT 524,442-539,472 msg 50, RESROTRIGHT
//   540,442-554,472 msg 51, RESMOVEUP 563,442-593,457 msg 52, RESMOVEDOWN
//   563,458-593,472 msg 53. The rotate pair pans horizontally, the move
//   pair vertically (the t252 diff at (570,455) moved the view column).

#include <string>
#include <vector>

#include "game/campaign.h"
#include "game/research.h"
#include "ui/cam3d.h"
#include "ui/layout.h"

namespace ascend::ui {

// One node per LIVE tech row (the 66 main rows; variants never load —
// research.md §6c). `row` indexes ResearchTree::all().
enum class TechNodeState { Owned, Study, Available, Blocked };

struct TechNode {
    int row = -1;
    TechNodeState state = TechNodeState::Blocked;
};

// Partition law: Owned == ownedTech; Study == queued && !owned; Available ==
// !owned && every prereq owned; Blocked otherwise. Rows past the main count
// (variants) are EXCLUDED (OQ-013 CLOSED).
std::vector<TechNode> researchNodes(const ascend::game::Campaign& camp,
                                    const ascend::game::ResearchTree& tree,
                                    int owner);

// SET-STUDY LAW (help reswin + t268 click witness). Returns true iff the
// click lands: Available -> queued via Campaign::setQueuedTechFor; every
// other state is a SILENT reject (Owned = dossier read only).
bool setStudy(ascend::game::Campaign& camp,
              const ascend::game::ResearchTree& tree, int owner, int row);

// The header line: static #130 first-%s join "<name> Knowledge" (second %s
// seam, F6). Pure so the join is pinned without a race-name lookup.
std::string researchHeaderText(const std::string& ownerName);

// The Allows list for one tech row [verified reverse join, ui-runtime 6d]:
// gizmos (table order) then planitems (table order) whose tech field == row;
// '^' -> ' ' (the loader display law). Empty vector is a legal answer.
std::vector<std::string> allowsList(const ascend::game::Campaign& camp,
                                    int row);

// The "(N days)" line for the CURRENT topic only (#124 "(%d day%s)",
// singular iff N==1 — the t402/t407 plural-pair law). remaining/rate are
// fed by the caller (Campaign accessors); rate<=0 -> "(0 days)" [port
// default, labelled in the header block].
std::string researchDaysLine(double remaining, double rateLastTurn);

// ---- geometry -------------------------------------------------------------
// The four pan buttons VERBATIM from windows.txt (see header block). Note
// RESROTRIGHT x1=554 leaves a gap before RESMOVEUP x0=563 — verbatim, not a
// typo to "fix".
inline constexpr Rect kResRotLeft{524, 442, 539, 472};
inline constexpr Rect kResRotRight{540, 442, 554, 472};
inline constexpr Rect kResMoveUp{563, 442, 593, 457};
inline constexpr Rect kResMoveDown{563, 458, 593, 472};

enum class ResHit { None, RotLeft, RotRight, MoveUp, MoveDown, Node };

struct ResHitResult {
    ResHit kind = ResHit::None;
    int row = -1;  // valid iff kind == Node
};

// Node hit radius: rings measured ~50 px diameter on the t268 capture
// (native-vision; empty ring at ~(72,327) spans ~41..100 per the t268
// pixel-diff bbox 41-100 x 299-358 — 60 px box INCLUDING the ring, so the
// disk radius is 30).
inline constexpr int kResNodeRadius = 30;

// Derived layout law (labelled; seam in the header block): x = depth by the
// LONGEST prereq chain (0..17 per research.md §3) scaled by kResDepthPitch;
// y = row index within the depth column by kResRowPitch. Nodes are laid out
// column-major so prereq edges always run left->right.
inline constexpr int kResDepthPitch = 96;   // 2*radius + 36 lane room
inline constexpr int kResRowPitch = 78;     // radius*2 + 18
inline constexpr int kResFieldX0 = 40;      // interior 7 + ring margin
inline constexpr int kResFieldY0 = 76;      // interior 46 + header room

struct ResPoint { int x = 0, y = 0; };

// ---- t419: THE O(n^2/frame) KILLER + THE 3D TREE --------------------------
// STALL LAW (D15 addendum; DECISIONS.md static root cause): the old law
// recomputed researchDepth (a full memoised graph walk) once per slot-row
// per NODE per FRAME. ResearchLayout computes depth AND column slot ONCE
// (single memoised pass + single counting pass), so a frame costs O(n+e).
// researchDepth()/researchNodePos() keep their t408 signatures (pins) by
// delegating to a one-shot layout.
struct ResearchLayout {
    std::vector<int> depth;  // per row: longest prereq chain
    std::vector<int> slot;   // per row: index within its depth column
    int cx = kResFieldX0;    // field centre (bbox mid) at pan 0 — the 3D
    int cy = kResFieldY0;    //   projection origin
    int maxDepth = 0;
};
ResearchLayout researchLayoutFor(const ascend::game::ResearchTree& tree);

// 2D centre from a precomputed layout (pure offset arithmetic).
ResPoint researchNodePosAt(const ResearchLayout& layout, int row, int panX,
                           int panY);

// 3D LAW (D15 "another 3d rotating dealie"; NAMED SEAM: the vendor reswin
// draw chain was never recovered — grep of every disassembly window on disk
// finds no reswin/resmove FUN; the mechanism reuses the t416 COSMOSWnd
// basis law verbatim, which IS cited). The tree is a FLAT XY field (screen
// axes at rest): field point = (pos2D - layout centre, 0) px, y flipped to
// field-up. The rotate dials (msg 50/51, windows.txt verbatim — the SAME
// dial msgs as the cosmos, whose latch+pump law t416 recovered at
// 0x27d6f../0x27a18) pressSpin on a dedicated Camera3d; the move pair
// (msg 52/53) SCROLLS post-projection (user spec verbatim: "scrolling
// (up/down)"). Projection is the t399 pinhole (FUN_00053374 law) via
// projectPoint with standoff == focal == kResStandoff: at the REST basis
// scale == 1.0 exactly and screen == the t408 2D law EXACTLY (pins + the
// t408 witness click coordinates survive unchanged).
inline constexpr double kResStandoff = 1200.0;  // == focal: rest scale 1

// The dedicated research camera at REST (focal == standoff): projectPoint
// through this camera is scale-EXACTLY 1 and reduces to the t408 2D law.
inline Camera3d researchRestCam() {
    Camera3d c;
    c.focal = kResStandoff;
    return c;
}

struct ResPoint3 {
    int x = 0, y = 0;      // painted screen centre
    int r = kResNodeRadius;  // ring radius scaled by the perspective factor
    double z2 = 0.0;       // camera-space depth (back-to-front sort key)
};

// Screen-space centres for every node (index == nodes vector index == row,
// the researchNodes order law). `cam` is the caller's dedicated research
// camera (focal == kResStandoff); pan applies POST-projection in screen px.
std::vector<ResPoint3> researchNodeScreen(const ResearchLayout& layout,
                                          const std::vector<TechNode>& nodes,
                                          int panX, int panY,
                                          const Camera3d& cam);

// The node centre for `row` given the tree (pure; deterministic) plus the
// pan offsets (px). Pan clamping lives in the caller (ui.cpp) so the law
// here stays a pure coordinate function. t419: delegates to a one-shot
// layout (identical answers, no per-call graph re-walk).
ResPoint researchNodePos(const ascend::game::ResearchTree& tree, int row,
                         int panX, int panY);

// Longest-prereq-chain depth of a row (memoised DFS; the tree is acyclic —
// research.md §2 — cycles would be a loader bug, refused upstream).
int researchDepth(const ascend::game::ResearchTree& tree, int row);

// Hit precedence (t405/t407 law shape): the four pan buttons are evaluated
// FIRST (they sit outside the tree panel), then the node grid. A point near
// no node is inert. `nodes` is the partition (only non-blocked... no: ALL
// nodes are hittable — blocked nodes still show; the click law rejects
// them via setStudy, matching the vendor's silent no-op). t419: hits test
// the PROJECTED centres (a `cam` is required — passing the rest camera is
// exact 2D); the layout is built ONCE per call (O(n+e), not O(n^2 x graph)).
ResHitResult researchHit(const ascend::game::ResearchTree& tree,
                         const std::vector<TechNode>& nodes, int px, int py,
                         int panX, int panY,
                         const Camera3d& cam = researchRestCam());

}  // namespace ascend::ui
