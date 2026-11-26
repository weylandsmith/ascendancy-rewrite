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
//   LAYOUT [VERIFIED tRS-V1/V1b — SUPERSEDES the t408 derived grid]: the
//   generator is FUN_0004709c's reswin.txt-absent branch — depth relaxation
//   plus a CHAIN OF CIRCLES (one per depth column), camera pos (0,0,-150),
//   focal 320/tan(15deg), pinhole 0x53374 with the 0x76e08 chop rounding.
//   Full law + per-section citations: docs/re/_wip_tRSV1.md P1-P12 and
//   docs/re/research.md S8. The field is ~7-9x the window: reswin is a
//   PANNED WINDOW (t252 corroborates) — scale was part of D26.
//
//   SCROLL LAW [VERIFIED tRS-V1b — SUPERSEDES "rotate pans X, move pans Y"]:
//   four buttons OUTSIDE the RESWIN rect (windows.txt verbatim rects below,
//   msg 50..53). The dat_764c4 bit-pair state machine (0x47b44..0x47c42)
//   latches: the ROTATE pair yaws the camera basis +-3 deg/tick, the MOVE
//   pair DOLLIES camera posZ -1/+1 per tick (NOT a screen pan). The t252
//   pixel-diff that read as a column shift is consistent with the dolly.
//   Node art = resring.shp frames 0..3 1:1 centred (P3/P10); blocked rows
//   are neither drawn nor hittable (0x46d3c scope, P10).

#include <string>
#include <vector>

#include "game/campaign.h"
#include "game/research.h"
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

// tRS-B1 HIT LAW [verified sub 0x47478 @0x474fb..0x4752d]: the click hits a
// node iff |dx|<=24 AND |dy|<=24 from the node's projected centre — an
// INCLUSIVE +-24 SQUARE (reject legs `jle` at node-25 and `jge`/`jle` at
// node+25), fixed size, NOT scaled with the perspective ring radius.
inline constexpr int kResHitHalf = 24;

// ---- tRS-V1c: THE VENDOR TREE GEOMETRY (supersedes the t408/t419 derived
// layout; law docs/re/_wip_tRSV1.md P1-P12 + research.md S8) ---------------
// FUN_0004709c GENERATOR: depth relaxation (P1b) then a CHAIN OF CIRCLES —
// one circle per depth column k (0..esi-1, esi = maxdepth+1), column angle
// acc0 = 240+30k degrees, per node i (FILE order within the column):
//   Y = 30k + 15*(i&1);  Z0 = (i==0 ? R0(k) : 23);  X = 0;
//   rotate 0x5324c: X' = Z*sin(acc), Z' = Z*cos(acc);  acc += int(360/d(k))
//   as REPEATED f32 adds (integer division FIRST — 0x4743d VERBATIM).
//   R0(k) = 23 iff (k even AND C[k]>1) OR (k odd AND C[k]==2), else 4;
//   d(k)  = C[k] except odd k with C[k]>2 -> C[k]-1 (circle stays open).
// MEASURED on restree.txt (66 rows): esi=18, C=[3,4,3,5,6,5,3,4,2,4,4,4,4,
// 4,5,3,2,1] — the port pins reproduce it.
struct ResWorld { float x = 0.0f, y = 0.0f, z = 0.0f; };

struct ResearchGeom {
    std::vector<int> depth;       // per row: longest prereq chain (P1b)
    std::vector<int> slot;        // per row: index i within its column
    std::vector<int> C;           // C[k] = rows at depth k, size esi
    std::vector<ResWorld> world;  // per row: the vendor world triple
    int esi = 0;                  // column count = maxdepth + 1
};
ResearchGeom researchTreeGeometry(const ascend::game::ResearchTree& tree);

// The vendor camera (win+0xab block): position z win+0xe3 (rest -150.0,
// 0xc3160000 VERIFIED) and the orientation basis yaw (win+0x11f, rotated by
// 0x53504 = the 0x5324c world-Y mix — the t416 cosmos law). FOCAL is NOT a
// field: 0x203e4 computes 320/tan((30deg)/2) = 1194.19 once at window init.
struct ResCam {
    double posZ = -150.0;   // win+0xe3 (MOVE pair dollies this)
    double yawDeg = 0.0;    // basis yaw (ROT pair)
    // dat_764c4 bit-pair latches encoded 0=(0,0) 1=(1,0) 2=(1,1) 3=(0,1).
    int latchRot = 0, latchMove = 0;

    // Press law (0x47b44..0x47c42 VERBATIM, P11): pair A = msg 50/52,
    // pair B = msg 51/53. A: (0,0)->(1,0) start; (1,0)->(0,0) stop;
    //   (1,1)->(0,1) DEAD; (0,1)->(1,0) revive-left.
    // B: (0,0)/(1,0)/(0,1)->(1,1); (1,1)->(1,0).
    static int pressPair(int state, bool pairB);
    void pressRot(bool pairB) { latchRot = pressPair(latchRot, pairB); }
    void pressMove(bool pairB) { latchMove = pressPair(latchMove, pairB); }

    // tPF-7 RELEASE LAW (0x47d3b VERBATIM shape: `ebx=[0x764c4]; not ebp;
    // and ebx,ebp; mov [0x764c4],ebx` — the framework's button-release msg
    // 0x38/0x39 ANDs OUT the released control's bit pair; our 2-bit pair
    // encoding means AND-OUT == inactive state 0): releasing the mouse
    // clears THAT control's pair. This is what makes the vendor dials
    // CONTINUOUS-WITHOUT-LATCH (press moves while held, release stops) —
    // the user's D28 item 17 target, corroborated verbatim by the vendor's
    // own help resmove text (extracted/ascend00/help.txt: "Use the right
    // mouse button if you want to move or rotate continuously").
    // Per-msg mask split (0x38 vs 0x39) = seam TPF7-A; pair ownership by
    // control is windows.txt (RESROTLEFT/RIGHT msg 50/51 = rot pair,
    // RESMOVEUP/DOWN msg 52/53 = move pair).
    void releaseRot() { latchRot = 0; }
    void releaseMove() { latchMove = 0; }

    // Pump deltas (0x47c88/0x47cdb VERBATIM): rot (1,0)->+3deg, (1,1)->-3,
    // else 0 (DEAD pumps nothing); move (1,0)->-1, (1,1)->+1 x step, else 0
    // applied to posZ. NOTE: posZ -= 1 moves the camera AWAY from the tree
    // at z~0 (vZ = z - posZ grows), so RESMOVEUP SHRINKS the tree — the
    // _wip P10 draft parenthetical "(dolly IN: tree grows)" contradicts the
    // cited fadd chain and is superseded.
    static constexpr double kRotStepDeg = 3.0;
    static constexpr double kDollyStep = 1.0;  // seam TRSV1b-A (runtime
                                               // f32[0x9f108] not restored)
    // tPF-7 PUMP CADENCE: the framework fire-loop period. The reswin
    // self-schedules msg 0x3a with INTERVAL 0 at window init (0x47713 ->
    // 0x56374, docs/re/_wip_tPF7.md P4/P5), so it fires every pass of the
    // loop at 0x56608. The loop rate is DERIVED from two cited numbers:
    // live-measured cosmos pump rate 58.5 deg/s (tNG-S S30-X5, run
    // dbg-tngh-20261123-130254) / cosmos pump delta 2.0 deg VERBATIM
    // (cam3d.h kRotStepDeg, t416 F2) = 29.25 passes/s => 34 ms. The old
    // kSpinTickMs=1000 rested on a t302 MISREAD ("within ~1 s" first-fire
    // latency, explicitly 'NOT yet a law'); see _wip_tPF7.md P6. Direct
    // fire-loop measurement = seam TPF7-D.
    static constexpr int kPumpMs = 34;
    void tick();
    bool moving() const { return latchRot != 0 || latchMove != 0; }
};

// 320/tan(15deg) = 1194.19 (0x203b8+0x203e4 VERBATIM; the HALF-width-320
// convention matches the tNGS cosmos camera).
double resFocal();

// 0x76e08 ROUNDING VERBATIM: frndint with RC=chop (toward zero) — with the
// +0.5 bias this rounds positives to nearest and chops negatives
// ASYMMETRICALLY (-2.7+0.5 = -2.2 -> -2, NOT -3). Pinned.
int resVendorRound(double v);

struct ResPoint3 {
    int x = 0, y = 0;      // painted screen centre (absolute frame px)
    double z2 = 0.0;       // camera-space depth (edge-colour + sort key)
    bool legal = false;    // 0x46d3c scope: OWNED or all-prereqs-owned
    bool visible = false;  // legal && vZ >= 1.0 (port div guard)
};

// Screen centres for every node via the vendor chain: v = B*(world) - pos
// (0x53324 affine, B rows right/up/fwd per the 0x5324c yaw mix), then
// 0x53374: X = word(chop(focal*vX/vZ + 0.5) + 235) + panX mapped into the
// RESWIN interior, Y likewise +240. The u16 word-wrap of the vendor's
// `add word[...]` is replicated (int16 result). Blocked rows get
// legal=false and are NEVER drawn or hittable (P5/P10: 0x48566 gates the
// draw with the SAME 0x46d3c predicate as the hit sub). panX/panY are a
// labelled PORT affordance (post-projection screen offsets; the vendor has
// none — its scroll law is the ResCam basis yaw + posZ dolly above).
std::vector<ResPoint3> researchNodeScreen(const ResearchGeom& geom,
                                          const std::vector<TechNode>& nodes,
                                          int panX, int panY,
                                          const ResCam& cam);

// The node centre for `row` at the given camera (pure convenience wrapper:
// geometry + one screen pass; O(n+e)).
struct ResPoint { int x = 0, y = 0; };
ResPoint researchNodePos(const ascend::game::ResearchTree& tree, int row,
                         int panX, int panY, const ResCam& cam = ResCam{});

// Longest-prereq-chain depth of a row (P1b value; memoised one-shot).
int researchDepth(const ascend::game::ResearchTree& tree, int row);

// Hit precedence (t405/t407 law shape): the four pan buttons FIRST (they
// sit outside the tree panel), then the node grid. THE SCOPE GATE: only
// LEGAL rows (state != Blocked == the 0x46d3c true-set, P10) are tested —
// blocked rows are not drawn and not hittable (0x48566 + 0x474fb). Scan
// order: rows HIGH->low, FIRST hit wins (the vendor SELECT sub 0x47478
// walks the row list downward; with the circle layout nodes CAN overlap, so
// the scan order is now observable — port follows it verbatim).
ResHitResult researchHit(const ascend::game::ResearchTree& tree,
                         const std::vector<TechNode>& nodes, int px, int py,
                         int panX, int panY,
                         const ResCam& cam = ResCam{});

// The node FRAME index (resring.shp record) per the P10 esi law VERBATIM
// (0x483fa..0x48470): 1 default; 0 iff row==studied && !owned; 3 iff owned;
// 2 iff row==word[win+0x9db] — the HOVER word (tPF-10: 0x47478 tracks the
// legal row under the cursor, so frame 2 = the bright-blue hover highlight,
// MEASURED resring k2 mean (76,157,198) on the port decode plane; the old
// "gold" label was a misread
// of the 0x5caac blitter choice, docs/re/_wip_tPF10.md P3).
int resNodeFrame(int row, bool studied, bool owned, bool hover);

// tPF-10 HOVER-WORD LAW (sub 0x47478 VERBATIM, work/tRS_reswin_fn.asm
// 0x47484..0x47555): the select sub re-hits the projected table from the
// MOUSE words on EVERY framework msg (all switch arms + default 0x47b33),
// stores the legal row under the cursor — 0xffff (-1 here) when off any
// disk — and writes word[win+0x9db] ONLY on change (0x4753a je / 0x47548).
// It is NOT a click latch: the commit chain (0x47d99) only READS the word.
inline int resHoverWord(int prev, const ResHitResult& h) {
    const int hit = (h.kind == ResHit::Node) ? h.row : -1;  // 0xffff leg
    return hit == prev ? prev : hit;                        // 0x4753a/0x47548
}

// The prereq-edge colour INDEX per the corrected P11 law: 0x6b - k with
// k = clamp(chop(0.25f*(0.5f*(z_this + z_prereq) + posz)), -3, +3); the
// caller substitutes index 0xf3 when the prereq is the SELECTED row
// (0x48314..0x48321 VERBATIM). z values are camera-space depths (ResPoint3
// z2); posz the camera position z.
int resEdgeColorIndex(double z_this, double z_prereq, double posz);

// ---- tRS-V2p: THE DISK FILL LAW (research.md S9; D27 user law) -----------
// Per-row picture value q, VERBATIM 0x481aa..0x48239 (raw-stepper cited):
//   q = 0;                                   ; unowned AND not-studied:
//                                            ; EMPTY disk (0x4838c skips)
//   owned (mask dword[rec+0x47]>>24 & raceBit): q = 20;   ; 0x481ce FULL
//   else if row == studied word:               ; the 0x76492 specnum field
//     q = (progress*18)/runtimeCost + 2;       ; 0x48205..0x48218
//     clamp q to [-17, +17];                   ; 0x48222/0x48234 (AFTER
//                                              ; the +2: max studied q=17)
// progress = word[0x764a0+2*row] (u16), runtimeCost = word[rec+0x3e] (the
// S6b RUNTIME cost). The clamp firing means p>=cost renders 0.85 and the
// final 15% is the OWN-completion JUMP 17->20 (S9(c) corrected). The
// negative leg is dead for real inputs (u16 progress >= 0 => q >= 2);
// ported verbatim anyway. SEAM TRSV2p-A: the vendor has NO cost==0 guard
// (idiv by zero = SIGFPE class); the port returns q=0 for cost<=0.
int resDiskQ(bool owned, bool studied, int progress, int runtimeCost);

// The blit scale factor q/20 (the 16.16 quotient of 0x48390..0x4839d:
// (int16)q << 16 idiv 20). q==0 -> 0.0 == no picture at all.
double resDiskFill(int q);

}  // namespace ascend::ui
