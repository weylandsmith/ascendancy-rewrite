// SPDX-License-Identifier: GPL-3.0-or-later

#pragma once
// tPL-B2: PRODUCTIVITY-BOX POPUPS (D26) — the msg-50 indicator popup law.
//
// Clicking a top-row productivity panel of the planet screen (windows.txt
// TYPE-29 children of PLANETALLOC, lines 1536..1587) sends SENDMESSAGE 50
// with SENDPARAM1 0/1/2/4. The vendor's PLANETALLOC handler arm 0x3d80b
// stores the key (ds:0x74528) and the clicked cell; the repaint runs the
// POPUP BUILDER FUN_0x3db80, which fills an ebp field struct and pushes
// formatted lines into the display queue (0x2fb38, display object 0x7d3a2).
// The live jump-table verdict (docs/re/_wip_tPLB2.md P6, member-delta
// 0xfd0 exact against the known selector table) binds KEY -> CASE BODY:
//
//   key 0 (PLRES  panel)  -> 0x3dc61 RESEARCH   (word getter(65), +0x46)
//   key 1 (PLIND  panel)  -> 0x3dd17 INDUSTRY   (word getter(68), +0x44)
//   key 2 (PLPRO  panel)  -> 0x3ddc0 PROSPERITY (word getter(70), +0x48)
//   key 3                 -> 0x3de5a SQUARE (unreachable: no windows.txt
//                            child sends PARAM1 3 — the other switch)
//   key 4 (PLPOP  panel)  -> 0x3e2c8 FULL-INFO chain
//
// THE TWO-LINE INDICATOR LAW [verified instruction-exact 0x3e4db..0x3e5db]:
//   L-D (gated +0x72 != 0): sprintf(getter(99) "%s %s: %d per day",
//       planet(+0x24 NAME), nameWord(+0x72), u16(+0x7e)); hold 0xf.
//   L-E (gated +0x6e != 0): if u16(+0x7a) == 0xffff ->
//       sprintf(+0x62 fmt, subject(+0x5a)); else
//       sprintf(getter(100) "%s will %s in %d day%s.", subject, verb(+0x6a),
//       u16(+0x7a), getter(28)"" iff days==1 else getter(29)"s"); hold 0x50.
//
// COUNTDOWN 0x47010 [verified 0x47010..0x47034]: eax=target, edx=acc,
// ebx=rate; rate <= 0 -> 0xffff; else eax = (target-acc-1)/rate + 1,
// clamped >= 1. == ceil((target-acc)/rate) floored at 1.
//
// PER-KEY FIELD FILL [verified, case bodies objdump-confirmed this task]:
//   RESEARCH   +0x72=getter(65)"Research", +0x7e=u16[+0x46] (RES/day);
//     if the race's current-research word WORD[0x76492+2r] != 0xffff:
//     +0x5a = tech NAME (RESTREE stride-75 record), +0x6e=-1,
//     +0x7a = 0x47010(eax=WORD[tech+0x3c] COST, edx=WORD[0x764a0+2r] acc,
//     ebx=0x46de0(race research bank)), +0x6a=getter(66)"be discovered",
//     +0x62=getter(67)"No progress is being made on %s."
//     No current research -> +0x6e stays 0 -> L-E never renders.
//   INDUSTRY   +0x72=getter(68)"Industry", +0x7e=u16[+0x44] (IND/day);
//     if the pending build cell u16[+0x52] != 0xffff: +0x5a = planitem
//     NAME (runtime stride-40 record +0xa), +0x6e=-1, +0x7a = 0x47010(
//     eax=0x394d8 cost, edx=u16[+0x50] buildAcc, ebx=u16[+0x44]),
//     +0x6a=getter(69)"be completed", +0x62=getter(67).
//     No pending item -> +0x6e stays 0 -> L-D only.
//     SEAM TPLB2-A: 0x394d8's Ship-design leg (item 23 -> 0x396cc
//     design cost) and the Automation x3 leg (item 35 && +0x52 match,
//     0x39545) are NOT modelled (same named seam as statuslist.h).
//   PROSPERITY +0x72=getter(70)"Prosperity", +0x7e=u16[+0x48] (PROS/day),
//     +0x5a=getter(71)"Population", +0x6a=getter(72)"grow", +0x6e=-1;
//     if u16[+0x42] pop >= u16[+0x4a] maxpop (0x3de08 `cmp %bx,%dx; jae`):
//       +0x62 = getter(74)"%s has no more room to grow." (+0x7a stays 0xffff);
//     else +0x7a = 0x47010(eax=dword[0x66e4] wrap=50, edx=u16[+0x4e]
//       growthCounter, ebx=u16[+0x48]) -> on 0xffff +0x62 =
//       getter(73)"%s is not growing."
//     *** THE USER WITNESS PATH: "Crimea 1 / Prosperity: 1 per day /
//     Population will grow in 50 days" = L-D (wrapping) + L-E. ***
//   FULL-INFO  L0 planet NAME alone (hold 0xf, raw push 0x3e2d3);
//     L1 getter(94)"%s %s Planet" from the RUNTIME word tables
//     0x7452c[u16+0x14 size] / 0x74540[u16+0x16 type] (hold 0x3c) — the
//     FILE-ORDER == runtime-slot-order census law (r402) maps these to the
//     SHIPPED statusSizeWord/statusTypeWord pair, same wiring as
//     statusLine1 (sizeIdx=sizeClassFor(surfaceCells), typeIdx=terrainRow);
//     L2 getter(96)"Owned by |%d|%s" (hold 0x5a): the |%d| is an inline
//     COLOUR-CHIP directive = raceIdx*4+0x13 (0x3e3f2 shl 2 / 0x3e3f5 add
//     0x13); owner byte +0x57 >= 0xff -> name buffer pre-filled
//     getter(95)"No One" (0x3e347); else race name table 0x74590+20*race.
//     SEAM TPLB2-B: the port text renderer has no inline chip — the chip
//     code is computed and pinned, the rendered text drops the directive
//     and draws the owner name in the owner's race colour instead.
//     L3 getter(97)"Maximum Population  %d" (TWO spaces, static.txt:287)
//       u16[+0x4a] (hold 0x78);
//     L4 getter(98)"Self Managed" iff owner==player && u16[+0x5a]==0xffff
//       (hold 0x96) — the port governor analog is -1 (campaign.h t45).
//     No L-D/L-E on a key-4 visit (+0x72/+0x6e stay 0 through the case).
//
// POPUP RECT LAW [verified 0x3dbe5..0x3dc34]: (wx+10, wy+10)..(wx+0x145,
// wy+0xcf) from the CLICKED widget's X0/Y0 (wrec[8]/wrec[0xc]); the port
// clips to the 640x480 frame.
//
// HOLD-TICK SEMANTICS [unverified]: the queue consumer (0x2fb38 -> display
// object 0x7d3a2) is not recovered; each line's hold value IS cited
// (0xf/0x3c/0x5a/0x78/0x96/0x50) but its time base is not. The port shows
// ALL lines stacked until the next planet-screen click dismisses the popup
// (documented default; the witness read three lines off a persisting
// popup). The tail sound gate (widget+0x6b -> 0x314a8) is NOT modelled.

#include <string>
#include <vector>

#include "game/campaign.h"
#include "ui/layout.h"  // Rect
#include "ui/planetwin.h"  // PlanetPanel

namespace ascend::ui {

// One queued display line: text + the vendor hold word (cited above;
// render-ignored until the consumer law is recovered).
struct PopupLine {
    std::string text;
    int hold;
};

// FUN_0x47010 verbatim: target/acc/rate -> days, -1 == the 0xffff
// "no progress" sentinel (rate <= 0). Else max(1, ceil((target-acc)/rate)).
int countdownDays(int target, int acc, int rate);

// The popup rect for a click on the panel `pr` (inclusive, verbatim law;
// NOT frame-clipped — the renderer clips).
Rect indicatorPopupRect(Rect pr);

// ---- pure content law (the ebp field struct the builder fills) ----------
struct IndicatorContent {
    const char* nameWord = nullptr;    // +0x72 (null => no L-D line)
    int perDay = 0;                    // +0x7e
    const char* subject = nullptr;     // +0x5a (null => no L-E line)
    const char* verb = nullptr;        // +0x6a
    int days = -1;                     // +0x7a (-1 == 0xffff sentinel)
    const char* noProgress = nullptr;  // +0x62 (used on the sentinel leg)
};

// L-D + L-E exactly as 0x3e4db..0x3e5db formats them.
std::vector<PopupLine> indicatorLines(const std::string& planetName,
                                      const IndicatorContent& c);

// Full-info chain inputs (key 4). owner == -1 (0xff analog) -> "No One".
struct PlanetIdentity {
    std::string name;
    int sizeIdx = 0;   // +0x14 analog (statusSizeWord domain)
    int typeIdx = 0;   // +0x16 analog (statusTypeWord domain)
    int owner = -1;
    std::string ownerName;  // race name table analog (ignored if owner<0)
    int maxPop = 0;         // +0x4a analog
    bool selfManaged = false;
    // SEAM TPLB2-C: the |%d| chip code's raceIdx comes from a RUNTIME
    // table at 0x12e18 indexed by an owner-record transform (0x3e3da..
    // 0x3e3e6: ((owner*32-owner)*8-owner)*2 — a runtime-record stride,
    // unrecovered statically); the ui passes the owner's specnum as the
    // raceIdx analog (the roster build law makes them coincide on the
    // shipped scenarios).
    int chipRaceIdx = 0;
};
std::vector<PopupLine> fullInfoLines(const PlanetIdentity& id);

// The inline colour-chip directive code (0x3e3f2/0x3e3f5): raceIdx*4+0x13.
inline constexpr int raceChipCode(int raceIdx) { return raceIdx * 4 + 0x13; }

// ---- Campaign-fed builders -----------------------------------------------
// The popup for a msg-50 click on panel `panel` of planet `star`. Panels
// outside 0..3 (PLBUILD) produce an EMPTY popup (the 0x3dc53 `ja 0x3e4db`
// leg with the struct zeroed: no lines). `planetName` is the display name
// the ui already resolved (planet+0x24 analog).
std::vector<PopupLine> popupLinesFor(const ascend::game::Campaign& camp,
                                     int star, PlanetPanel panel,
                                     const std::string& planetName);

// ---- tPF-2 SQUARE-INFO POPUP (D28 P3/P5; law docs/re/_wip_tPF2.md F3b) ----
// The msg-50 builder's KEY-3 case body 0x3de5a..0x3e2c8, armed by a tile
// click (widget+0xab = the clicked cell). Content law (objdump-verified):
//   title  BYTE[cell]&8 ruins && owner==player -> getter(88)
//          "Xenoarcheological Ruins" (NO body, 0x3e1c1 jne); else
//          getter(89) "%s Square" with the colour word below (hold 0x14).
//   colour cell >= surfaceCells -> getter(83) "Orbital"; else the
//          cs:[0x28fa4] table on BYTE[cell]&7: 0 Black(76), 1 White(75),
//          2 Red+industry(77/78), 3 Green+prosperity(79/80), 4 Blue+
//          research(81/82) — same class map as tileEdgePaletteIndex.
//   body   orbital -> getter(90); White -> getter(91) verbatim; Black ->
//          getter(92) verbatim; else getter(93) "%s squares increase the
//          effectiveness of %s-producing structures." (hold 0x14 tail).
// SEAMS (documented, NOT modelled): the occupied-cell item line 0x3df46
// (race-append 0x396cc + "Automated " 0x1ff2 legs — no campaign-side
// automation flag) and the empty-cell progress line 0x3e07e (queue order
// unrecovered); the D28 refcaps show title+body only for empty cells.
struct SquareInfo {
    std::vector<PopupLine> lines;  // title (+ body unless ruins)
    bool buildable = false;  // D28 button law: Build+Cancel iff true.
                             // SUPERSEDED for the ui button set by tPF-2d
                             // (au::popupButtonIds, the vendor id array —
                             // this field remains the CHECKER's adjacency
                             // leg, pinned by test_squarepopup_tpf2; the
                             // ui no longer reads it).
};
SquareInfo squareInfoLines(const ascend::game::Campaign& camp, int star,
                           int cell);

// The button law gate alone (pure, pin target): Build iff `cell` is a
// SURFACE cell (cell < surfaceCells), EMPTY (no active item), and has an
// ACTIVE 4-neighbour in the lattice. Ruins/orbital/occupied refuse the
// Build button (OK only) — seam-named honest default (F3c).
bool squareBuildable(const ascend::game::Campaign& camp, int star, int cell);

}  // namespace ascend::ui
