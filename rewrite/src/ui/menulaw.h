// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
// t387: the pure (no SDL) law side of the title-menu windows — NEWGAMEWND
// (New Game) geometry + hit-map, and the LOAD slot-list law. Geometry is
// verbatim from extracted/ascend00/windows.txt L575-717 (blocks read this
// iteration; law + coordinate-space witness banked docs/re/_wip_t387.md and
// distilled into docs/re/boot.md §6).
//
// COORDINATE SPACE [verified by geometry, _wip_t387]: every rect below is an
// ABSOLUTE screen coordinate — PARENT names a containment/dialogue owner, it
// is NOT a coordinate offset (relative reading puts RACELIST at x=836 and
// overlaps the bottom-row buttons; absolute puts them disjoint, equal-width,
// 9-px gutters).
#include <cmath>
#include <cstdint>
#include <functional>
#include <string>
#include <vector>

#include "ui/layout.h"

namespace ascend::ui {

// ---- New Game (state 3, SHAPEFILE DATA\3CFGNEW.SHP) ----------------------
// windows.txt TYPE 18 NEWGAMEWND: PARENT NONE, STATE "1 3", SHAPEFRAME 0.
inline constexpr Rect kNewgameWnd{334, 12, 488, 364};
// TYPE 10 RACELIST, PARENT NEWGAMEWND, SHAPEFRAME 7 (list frame; the race
// rows themselves are state-7 TYPE 6 controls — racesel screen, t388 seam).
inline constexpr Rect kRaceList{502, 45, 632, 372};

// The three state-3 child buttons (TYPE 0, STATE "1 3", SHAPEFRAME -1,
// SHAPEITEM 1 data\3cfgnew.shp 0 0 0 — the k0 wheel face). Labels are the
// TEXTITEM 0 strings with the vendor '^' word-join joined to spaces.
struct NewgameControl {
    const char* name;   // vendor NAME (verbatim)
    Rect rect;          // absolute, inclusive
    int message;        // SENDMESSAGE
    const char* label;  // display label ('^' -> ' ')
};
inline constexpr int kNewgameControlCount = 3;
extern const NewgameControl kNewgameControls[kNewgameControlCount];

// Which control (0..2) contains p, -1 if none. Inclusive edges, no clamp
// (same law as titleButtonAt).
int newgameControlAt(Pt p);

// t423c PLAYER-CHIP HIT LAW [verified disasm 0x529d2 zone cmp ebx
// 0x17b/0x1ed, ecx 0x1a4/0x1d8; idx = (x-0x17b)>>4]: the vendor chip zone
// is x379..493 y420..472 (BELOW windows.txt's MSG-0 label rect); chip idx
// rides a 16-px grid from x=379, so idx 0..7 are reachable (idx 7 = the
// neutral sliver at x>=491). Returns 0..7 or -1 outside the zone.
int newgameChipAt(Pt p);

// t423c COLOUR REASSIGN LAW [verified FUN_000232ec @0x232ec, capstone
// 0x232ec..0x23385]: out[0] = clicked; for i = 1..count-1 draw cand =
// rand()%7 (Borland LCG FUN_0007824f, *lcgState) re-picked while cand
// equals any ALREADY-WRITTEN out[j], j < i. All count colours distinct;
// the clicked idx is stored verbatim (7 = neutral allowed). No-op unless
// 2 <= count (vendor guard `1 < word[base+0xd88]`).
void assignRaceColours(int clicked, int count, unsigned int* lcgState,
                       unsigned char* out);

// ---- New Game full-screen layout (t393; docs/re/_wip_t393.md S6-S12) ------
// D10 (user 2026-11-14): the vendor New Game screen is a FULL-SCREEN switch
// (starfield backdrop + panels), not an overlay. The four bottom-row panels
// above are windows.txt-cited; the fifth zone — the Begin New Game button —
// is NOT in windows.txt (STARTGAME L1866 carries STATE "1 12", so it is not
// the state-3 button): its rect is a CITED MEASUREMENT off the user-supplied
// original capture scratchpad/newgame-original.png (capture = 640x480 + 1px
// border; screen coord = capture coord - 1; anchor: GALAXY_MORE x0=7 lands
// exactly on the capture's navy/left-bevel boundary).
inline constexpr Rect kBeginNewGameBtn{494, 373, 639, 472};
// tA2 [MEASURED browser shot +1,+1 law]: the BEGIN panel's VISUAL extent
// is NARROWER than the hit rect — navy interior row 430 runs x502..632
// (x494..501 is page texture per the t414 gutter law; x633 = (18,40,54)
// dark edge then chrome), interior starts y382 with the dark inset row
// 381 (col x560 y381 (12,24,34)); bottom y472 navy, y473 (65,73,79) then
// the bright rung y474 (97,97,97) = the same RAISED law. The pre-tA2
// fill painted navy over the gutter.
inline constexpr Rect kBeginPanelVisual{502, 381, 632, 472};
// Player^Color (windows.txt L653, TYPE 0, PARENT NONE, MSG 0): the fourth
// bottom-row zone. Label + colour chips; MSG 0 means the vendor sends no
// message on click (inert zone in the window table).
inline constexpr Rect kPlayerColorRect{379, 381, 493, 419};
// Summary block centre x [measured]: the three white lines centre on screen
// x ~170 (bands x 116..224 / 140..204 / 121..221). Begin label white ink
// rows measured 456..464 -> label top 455.
inline constexpr int kSummaryCentreX = 170, kBeginLabelTop = 455;

// Text placements [tA3 RE-MEASURED on the user original under the tA1 crop
// law (screen = image - 1; docs/re/_wip_tA3.md F2/F3), screen coords, ink
// rows]: species name (green) rows 17..26 centred x 412 ~= NEWGAMEWND
// centre 411; "Player Species" header (white) rows 15..24 centred x 568 ~=
// RACELIST centre 567. The pre-tA3 values 18/16 were the RAW browser rows
// (one below the crop-law screen rows — the S9 block predates the crop law).
// Both sites draw the BIG face (name: 10-row caps + big template win;
// header: caps rows 15..24 = bigfont's 10-row caps, sm 7-row REFUTED).
inline constexpr int kNameTop = 17, kHeaderTop = 15;
inline constexpr Rect kLoreBox{334, 258, 488, 330};
// tA3: lore TEXT starts at the measured ink top 265 (bands 265/276/287,
// pitch 11 CONFIRMED), not the box top 258 — the port drew 7 px high.
// Lore is the SM face (template 'the' sm 0.63 > bg 0.47; 8-row bands).
inline constexpr int kLoreTextTop = 265;
inline constexpr int kLoreLinePitch = 11;  // measured bands pitch 11
// tA3: summary lines measured (big-face template fits) at tops 326/339/352
// — top 326 (pre-tA3 327 = raw-row error), pitch 13 CONFIRMED.
inline constexpr int kSummaryTop = 326, kSummaryPitch = 13;
// tA3 CONTROL LABEL LAW: the three GALAXY/PLAYERS/DIFFICULTY TEXTITEMs are
// "0 <str> 2 0 10" — dy=10 verbatim, BIG face (Star Density/Species/
// Atmosphere big template fits 0.80-0.85 vs sm 0.21-0.30), centred on the
// rect (measured within 1 px). Player Color (no TEXTITEM; NAME label)
// measures browser row 394; under the same-window browser +1 drift law
// (the three dy=10 labels measure 392) its logical top is 393 = y0+12,
// centred, big face.
inline constexpr int kControlLabelDy = 10, kPlayerColorLabelDy = 12;

// RACELIST ROW LAW [MEASURED t393 on the user-supplied original]: the list
// is a THREE-SLOT scroll window, not a 7-row list. Silver bevel-ring census
// inside the interior gives row bands screen 49..153 / 157..262 / 266..372
// (pitch 108), x 506..631. Scroll arrows are 16x16 squares at the interior
// corners: up (616,47)-(631,62), down (616,356)-(631,371).
inline constexpr int kRaceSlotTop = 49, kRaceSlotH = 108, kRaceSlotPitch = 108;
inline constexpr int kRaceSlotCount = 3;
inline constexpr Rect kRaceArrowUp{616, 47, 631, 62};
inline constexpr Rect kRaceArrowDown{616, 356, 631, 371};
int newgameRowAt(Pt p);   // slot 0..2 or -1 (gutters/arrows dead for rows)
int newgameArrowAt(Pt p); // 0 = up, 1 = down, -1 = none

// ---- tNG-F2 SCROLL-ARROW GLYPH LAW (D20 F3 "arrow buttons still the wrong
// style and color"). [MEASURED refcap scratchpad/newgame-original.png,
// scripts/tNGF_arrow_map.py + grid dump docs/re/_wip_tNGF.md F3] The vendor
// arrows are NOT filled blue boxes: each is a 16-px-wide recessed cell with
// a dark-slate frame row, a navy well, and a small cyan triangle pointing
// out of a bright-rimmed base — six exact colour families:
//   navy well (12,32,48)   dark-slate frame (34,60,74)  mid slate (79,116,126)
//   cyan body (123,171,177) bright cyan (168,227,229)   highlight (190,255,255)
// The glyph ART is measured verbatim (per-px family map below); the widget
// record that supplies it (SHAPEFRAME vs painter blit) is NOT yet cited —
// named seam, the grid is the evidence. Paint extents are the MEASURED rows
// (up y47..63, down y356..372), one row taller than the cited hit rects
// (which stay kRaceArrowUp/kRaceArrowDown unchanged).
enum ArrowFamily {
    kArrowNone = -1, kArrowNavy = 0, kArrowDark, kArrowMid, kArrowCyan,
    kArrowBright, kArrowHi
};
RGB arrowGlyphColourAt(bool up, int x, int y);  // kArrowNone colour if off-glyph
bool arrowGlyphCovers(bool up, int x, int y);

// ---- t401 NEW GAME ART LAW (D11: framing missing, bottom-row artwork
// wrong, species column art not rendered, Begin box empty, description
// transparent). Measurement trail docs/re/t401-newgame-art.md S1-S10 on the
// USER-SUPPLIED originals (scratchpad/newgame-original.png +
// -very-dense- variant; capture->screen mapping cited there).

// WHEEL FRAME LAW t414 REVISED (user D15 "the icons below 'Star Density',
// 'Species', and 'Atmosphere' are repeating"). 3cfgnew.shp holds 13 usable
// records k0..k12 (k12 truncated at EOF but the visible 55 rows decode —
// scripts/t414_3cfgnew_dump.py); the controls own exactly 5+5+3 = 13 value
// steps, and the record CLASSES partition 5/5/3 (native-vision montage
// census, docs/re/_wip_t414.md S4): k0..k4 DOT-WELLS (dot count increases
// with index — t401 bright-cluster census 23/33/45/62 + k4), k5..k9
// ICON-RINGS, k10/k11/k12 ORBS (green/blue/red-spike). BIJECTION:
//   density    : star count RANKED in the sorted t78 ladder {15,25,50,75,
//                100} -> k0..k4 (was k0..k3,k3 — the repeat the user saw).
//   species    : n -> k(2+n), 3..Seven -> k5..k9 (unchanged; already
//                distinct; anchor Five->k7 measured, t401 S10).
//   atmosphere : v -> k(10+v): Peaceful->k10 (green orb), Neutral->k11
//                (blue orb — the original Neutral chroma (36,138,190)
//                matches k11's (36,137,190) x195 > k10 x123), Hostile->k12
//                (RED SPIKED orb — order law + colour law).
int newgameWheelFrame(int control, int value);

// ---- t414 NEW GAME FRAME + PREVIEW LAW (docs/re/_wip_t414.md S2) --------
// The screen is a TEXTURED CHROME PAGE with the cosmos punched in [all
// measured on the user original]: at y=200 the left texture ends x7; at
// x=300 the top texture ends y8 and the bottom texture starts y374; the
// DESC->RACELIST gutter x494..501 is texture. Draw texture FULL 640x480
// (textureColourAt), then black-fill kNewgameCosmosRect, then the points.
// tA2 RECESS LAW [MEASURED 2026-11-21, docs/re/_wip_tA2.md F2/F4; browser
// shot scratchpad/newgame-original.png game-rect +1,+1 law]: the pure
// black well is rows 8..372 x 8..492 (was {8,9,493,373} — 1px short at
// top, 1px over at right+bottom). The well is framed by a 1-px DARK
// RECESS on top/left/right (row 7 x7..493 vendor mean lum 24.2, colours
// (24,24,24)/(10,10,10)/(21,42,35)-class noise; col x7 mean 6.5; col
// x493 mean 22.9 — dark noise, NOT chrome, NOT pure black) and a 2-row
// RAISED RIDGE below (row 373 (61,61,61)/(53,78,78)-class mean 64.4, row
// 374 (97,97,97)/(85,125,125)-class mean 102.8 — the RAISED bevel: light
// BELOW, dark ABOVE = the well sits raised through the page; the vendor
// never shows the port's symmetric kBevel outline class here). The
// recess/ridge are drawn by the ONE chromePage pass (mapchrome
// newgameWellFrameAt), so the double-bar D19 signature (two bright chrome
// rows 7-8 below the top bar, docs F2) cannot recur.
inline constexpr Rect kNewgameCosmosRect{8, 8, 492, 372};
// Preview point count == the density setting (user: "a spinning star field
// commensurate with the star density"; the Very Dense original capture
// shows ~100 coloured points == ladder rung 100). Yaw advances per frame
// (spin); positions are splitmix64 on a sphere shell — deterministic, no
// rng (gate 3l law: preview must never touch the sim rng).
inline constexpr double kPreviewSpinPerFrame = 0.0035;

// Player^Color chips [tNG-C CHIP LAW, supersedes the t401 swatch read].
// Vendor head 0x5258d..0x52647: SEVEN raceflag emblems blitted at rect
// corners (381+16i, 433) (rect (381+16i,433)..(395+16i,463), pitch 16);
// raceflag content 15x25 with (L,T)=(0,0) [census F13] -> emblems occupy
// rows 433..457, x 381..395 (+16i). Chip i renders with palette slots
// 16..19 := game.pal[16+4i..19+4i] (0x53ee0). The t401 constants (X0=384,
// rows 434..459) were the tA3 raw-row drift class: emblem content starts
// 433, strip x-extent 381..491 (refcap tight bbox (381,433)-(491,458)).
inline constexpr int kPlayerChipX0 = 381, kPlayerChipPitch = 16,
                     kPlayerChipY = 433, kPlayerChipW = 15,
                     kPlayerChipH = 25, kPlayerChipCount = 7;
// SELECTED-CHIP FRAME LAW [measured F13, refcap chip0 white-px census]:
// white (255,255,255) hlines at y=434 and y=458 spanning x 381..395
// (+16i); the two VERTICALS rows 435..457 are NOT white — left edge
// (164,171,177), right edge (225,227,229) (chrome-grey family; unselected
// chips show their emblem ink at those columns, proving the greys are the
// frame). FUN_0002fe04 = 4 x FUN_0005bf71 line family (colours not
// statically decidable; refcap is the authority).
inline constexpr int kChipFrameTop = 434, kChipFrameBottom = 458;
inline constexpr RGB kChipFrameLeftGrey{164, 171, 177},
    kChipFrameRightGrey{225, 227, 229};
// The VISUAL panel runs to the bottom row (measured navy x380..493 rows
// 382..473 on the original); windows.txt's (379,381)-(493,419) is only
// the label/interactive zone.
inline constexpr Rect kPlayerColorPanel{379, 381, 493, 472};
// kPlayerChipRgb (t401 solid-swatch colours) REMOVED by the tNG-C chip law:
// the chips are raceflag ramp blits, not solid rects (D19 seed #4).


// Wheel blit anchor [measured]: the record's CONTENT circle (55 px wide)
// centres on the panel — original non-navy bbox x38..92 y408..462 inside
// the Star Density panel (cx 64). Blit at (panelCx - kWheelBlitHalfW,
// kWheelBlitTop). The pre-t401 port blitted k0 always at (cx-42, y0+26) =
// the "wrong artwork / wrong place" defect.
inline constexpr int kWheelBlitTop = 408, kWheelBlitHalfW = 28;
// tNG-B B3 PER-CONTROL ANCHOR RESIDUAL [measured, docs/re/_wip_tNGC.md
// F15-1c disc-extent centres ours-vs-vendor on the refcap state]: density
// ours (-1,+1), species ours (-1,0), atmosphere ours (+2.5,+1.5) — the
// blit must move by MINUS the residual: {+1,-1}, {+1,0}, {-2,-1}.
inline constexpr int kWheelBlitDx[3] = {1, 1, -2};
inline constexpr int kWheelBlitDy[3] = {-1, 0, -1};

// Description-panel art [measured]: portrait ring (green px x357..461,
// rows 45..149 -> centre (409,97) r 52); crest = raceflag frame <specnum>
// at NATIVE 14x24 (green bbox x441..455 y205..229 = exact size match);
// planet disc (purple bands x383..419 y198..239) — honest-vector circle.
inline constexpr Pt kDescRingCentre{409, 97};
inline constexpr int kDescRingR = 52;
inline constexpr Rect kDescCrestRect{441, 205, 454, 228};
// tNG-C PLANET LAW [verified]: the vendor anchor is NEWGAMEWND-relative
// (72,205) = screen (334+72, 12+205) = (406,217); dest = anchor + bbox
// (L,T) = (382,191). The old (401,218) fitted the t414 planets-ladder
// slice and is SUPERSEDED. kDescPlanetR (honest-vector fallback radius)
// stays until its consumer goes.
inline constexpr Pt kDescPlanetCentre{406, 217};
inline constexpr int kDescPlanetR = 18;

// RACELIST row art [measured]: portrait centre x 559 (row-2 ring greys at
// x506..511 / x608..612 -> dia ~107, r 53); smrace 49x49 SCALED 2x (98 px)
// inside the ring — the scale filter is a NAMED SEAM. The vendor rows
// carry NO text (two independent vision reads of the original crop).
inline constexpr int kRacePortraitCx = 559, kRacePortraitScale = 1;
inline constexpr int kRaceRingR = 53;

// Begin-box art [measured]: emblem zone green px x573..629 y390..446
// (centre (601,418)); smrace NATIVE 49x49 at (577,394) fits it exactly;
// hash-noise dot band (splitmix64, the t400 texture pattern) x496..570.
inline constexpr Rect kBeginEmblemRect{577, 394, 625, 442};
inline constexpr Pt kBeginEmblemCentre{601, 418};
inline constexpr Rect kBeginDotsBand{496, 390, 570, 446};

// Page texture on THIS screen [measured]: left margin x0..6 (the t400 §4
// band) and the RIGHT side from x494 (sparse texture columns 494/498/502/
// 614/634/637/639 at y=200). t400's map-screen band starts at 466 because
// the cosmos field ends there; on this screen the starfield runs to ~493.
extern const Rect kNewgameTextureBands[2];

// Portrait library file name for a specnum: smraceNN.shp — the unique
// race-named 49x49 portrait class (21 libs, dims census). Frame->species
// IDENTITY is the same named-seam class as t400's raceflag law.
std::string portraitLibName(int specnum);

// The three setting words + summary (static.txt verbatim, L429-457 block):
// density words 155-159, atmosphere 160-162, species count 163-167, summary
// template 168 "%s Star Cluster\n%s Species\n%s Atmosphere". The word->star
// count law is the t78 MEASURED ladder (mapgen.md OQ-012(a)): Average 50 ->
// Dense 75 -> Very Dense 100 -> Vacuous 15 -> Sparse 25 -> wrap.
inline constexpr int kDensityCycleCount = 5;
extern const char* const kDensityWords[kDensityCycleCount];
extern const int kDensityStarCounts[kDensityCycleCount];  // parallel, cited

// tNG-B B1 DENSITY CYCLE LAW [verified disasm 0x52db9..0x52dd7]: the click
// increments the rank word; when the OTHER density field hiword hits 5 the
// rank resets to 0 (wrap 5). Pure so the pin can test the wrap term.
inline int densityRankNext(int rank) {
    const int r = rank + 1;
    return r >= kDensityCycleCount ? 0 : r;
}
// Star-count law [verified straddle read 0x52df4/0x52dfb]: the arm reads
// hiword(dword[esp + rank*4 - 2]) over the dispatcher-head copy of table
// 0x895c8 {15,25,50,75,100} — the SORTED ladder indexed by rank 0..4.
// kDensityStarCounts is the same set in cycle order; rung count is identical
// either way (docs/re/_wip_tNGB.md straddle decode). Defined in menulaw.cpp.
int densityStarCount(int rank);

// tNG-B B2 SPECIES CYCLE LAW [verified disasm 0x52e58..0x52e6d]: the
// PLAYERS_MORE click increments word[win+0xb9]; when the incremented word
// hits 8 it resets to 3 — domain 3..Seven, visited from the vendor default
// 5 (window-init 0x52c55: word[+0xb9]=5, child wheel art +0x72=7 == k7
// 'Five', the t401 anchor) the sequence is 6,7,3,4,5,wrap. The arm then
// calls FUN_00022ce4 = RACE ASSIGNMENT (word[state+0xd88]=N, owner bits +
// home worlds re-rolled, star POSITIONS untouched) — NOT the full regen
// 0x226e4 the density arm runs. Pure so the pin pins the wrap term.
inline int speciesRankNext(int n) {
    const int v = n + 1;
    return v >= 8 ? 3 : v;
}

// tNG-B B4 ATMOSPHERE CYCLE LAW [verified disasm 0x52eec..0x52f01]: the
// DIFFICULTYMORE click increments word[win+0xbb]; when it hits 3 it resets
// to 0 — domain 0..2 (Peaceful/Neutral/Hostile), visited from the vendor
// default 1 (window-init 0x52c6b) the sequence 2,0,1,wrap. The arm makes
// NO state-fn call (unlike density 0x226e4 / species 0x22ce4) — atmosphere
// reaches campaign state ONLY through the Begin press, which stores
// byte[win+0xbb] into the global byte[0x13bc4] (0x52b3c/0x52b44, sole
// wheel writer; window-init 0x52c86 stores 1 unconditionally). Pure so the
// pin can test the wrap term.
inline int atmosphereRankNext(int v) {
    const int r = v + 1;
    return r >= 3 ? 0 : r;
}

// tNG-B B4 SETTINGS-APPLY LAW [verified begin block 0x52a44..0x52b75 +
// arm arg regs eax=0x12e10 on 0x52dfe/0x52e8d]: the wheel arms write THE
// PLAY STATE BASE at CLICK time (state-identity law) — Begin passes NO
// wheel words to worldgen (ebx=0 at 0x52a65) and applies exactly ONE
// setting: atmosphere -> byte[0x13bc4]. The triple below is the port's
// Begin-handoff contract: stars = the density rung the last regen drew,
// owners = the species word TOTAL races including the player (word
// [state+0xd88] == the race-count global 0x13b98, B2 law), gov = the
// atmosphere wheel (the byte[0x13bc4] value the dip-on-attack subtrahend
// 10*(gov+1) consumes, diplomacy.md §17.1). Pure so the pins pin the
// identity terms.
// tSPEC-1 ADDS species (the PLAYER specnum): the vendor RACELIST click arm
// 0x52d6c..0x52db8 stores word[win+0xb3]=clicked row (init 0 at 0x52c8c)
// and calls FUN_00022ce4(state, ebx=word[+0xb3], edx=count); inside
// 0x22ce4 the PLAYER branch (k==0, 0x22f8d) takes specnum = that word with
// NO rand (AI k>0 draw rand%21 distinct at 0x22fba), and 0x3e6bc stores it
// at race-row+7 — which Begin's worldgen 0x238e8 then indexes into the
// home TABLES 0x88f90/0x88fe4 (t30 0x23aeb mov dl,[eax+7]; tPL-D1 MEASURED
// 85/85: home size=T1[spec], terrain row=T2[spec]). The species-COUNT arm
// 0x52e58 passes the SAME word[+0xb3], so count clicks preserve the player
// row (docs/re/_wip_tSPEC1.md S1/S2). The port applies it at Begin like
// the rest of the triple.
struct NewGameSettings {
    int stars = 0;
    int owners = 0;
    int gov = 1;
    int species = 0;  // tSPEC-1: player specnum, word[win+0xb3] (vendor init 0)
    bool set = false;
};
inline NewGameSettings newGameSettings(int densityRank, int species,
                                       int atmosphere, int playerSpecies = 0) {
    NewGameSettings s;
    s.stars = densityStarCount(densityRank);
    s.owners = species;  // identity law: wheel value == TOTAL races
    s.gov = atmosphere;  // sole Begin-press global write [0x52b44]
    s.species = playerSpecies;  // tSPEC-1: RACELIST row == specnum (roster is
                                // specnum-ordered; speciesNameAt indexes it too)
    s.set = true;
    return s;
}

// tNG-B B1 PREVIEW-COSMOS HASH LAW: the per-star scatter value. The gen key
// (wheelGen * 0x100000001) is what makes a density click draw a NEW SET
// (vendor FUN_000226e4 full-regen is a rand() consumer at 0x22728); without
// it the points are per-index STABLE across clicks — the pre-tNG-B defect.
// Pure so the pin pins the gen-key term directly (mutation M7).
inline std::uint64_t cosmosHash(int i, unsigned gen) {
    return uint64_t(i) * 0x9e3779b97f4a7c15ull + 0x5851f42d403c3b23ull +
           uint64_t(gen) * 0x100000001ull;
}

// ---- tNGS P4 NEWGAME PREVIEW STARFIELD LAW (docs/re/_wip_tNGS.md S15,
// S22; supersedes the t423 cylinder model AND the pre-t423 splitmix
// sphere-surface sampler) --------------------------------------------------
// VENDOR GENERATOR LAW [verified asm FUN_00022878 0x22878..0x22ce1,
// work/tNGS3_22878a/b.asm]: per star k the vendor draws THREE ints
// v = rng%1000-500 (0x22b61/0x22b8d/0x22bb4, VERIFIED bytes 'b9 e8 03
// 00 00 ... 81 ea f4 01 00 00'), NORMALIZES the triple to the unit sphere
// (FUN_00052fa0), and scales by the SHELL ACCUMULATOR (start 440.0, step
// -75.0, reset 50.0 — the mapgen §OQ-025 shell table). z is NOT an
// independent axis: (x,y,z) = normalize(uniform[-500,499]^3) * shell(k).
// CAMERA LAW [verified FUN_00026a9c, S5]: position (0,0,-1500), FOV 35,
// identity orientation. Projection FUN_00053374: perspective divide,
// frndint with +0.5 bias, then viewport centre offsets.
// SPRITE CLASS LAW [verified asm 0x52817..0x5282f]: v = round(depth -
// 1500) = round(z); v>220 -> cls 0, 1..220 -> 1, -219..0 -> 2, <=-220 -> 3;
// shape = 4*type + cls (cos_star, t200 SEL law).
// ROTATION LAW [MEASURED 2026-11-22, run work/r1/c3-20261122-215511 +
// S14 static law]: the newgame field does NOT auto-spin — 6 frames over
// 60 s, star centroid displacement median 0.0 px, field-changed px flat
// (twinkle floor ~1085), control box 0. The t416 +-2deg/tick law belongs
// to the COSMOS MAP (state==3 latch 0x26dd1); the newgame screen opens
// COSMOSWnd through the generic init tail 0x26c89 which CLEARS the latch.
// The t423 F7 hover-armed spin zone (cursor x379..493 y420..472) is a
// separate cited law and stays modelled; only the IDLE spin is removed.
inline constexpr double kCosmosCamZ = -1500.0;      // [verified FUN_00026a9c]
inline constexpr double kCosmosFovDeg = 35.0;       // [verified 0x2716c]
// focal = well half-width / tan(FOV/2) = 242.5 / tan(17.5deg) = 769.1;
// the shell-440 ring then projects to 440*769.1/1500 = 225.6 px, inside
// the 8..492 well half-width 242.5 (fits; docs S15 envelope).
inline constexpr double kCosmosFocalPx = 769.1;
// Spin while the cursor is inside the t423 F7 armed zone (dispatcher
// 0x52993/0x529c1 cmp ebx 0x17b/0x1ed, ecx 0x1a4/0x1d8). Rate stays the
// port's t423 reading (6x) — cited as a zone, not a rate; IDLE = 0 (S22).
inline constexpr Rect kPreviewSpinZone{379, 420, 493, 472};
inline constexpr double kPreviewSpinArmedPerFrame = 6.0 * 0.0035;

// The three vendor draws from one hashed word: v = rng%1000-500 each.
// Splitmix64-mixed (gate 3l: preview must never touch the sim rng).
struct PreviewDraws {
    int vx, vy, vz;  // each in [-500, 499]
};
inline PreviewDraws previewDraws(std::uint64_t z) {
    z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ull;
    z = (z ^ (z >> 27)) * 0x94d045bb41f336ull;
    z = z ^ (z >> 31);
    return PreviewDraws{int(z % 1000ull) - 500, int((z >> 20) % 1000ull) - 500,
                        int((z >> 40) % 1000ull) - 500};
}

// tNG-S CYCLE 5 CADENCE LAW (docs/re/_wip_tNGS.md S28; supersedes the S27
// cadence transfer). The vendor newgame field is the state==3 COSMOSWnd
// branch (rect 17,12,324,320): init 0x26dd1 STORES [win+0xc0]=1, latching
// rotation ON, and the msg-0x3b pump dispatcher 0x27a18 applies the
// IMMEDIATE 2 DEG per tick (27a32 `mov dword [esp+0x14],2`; writer 0x283e4
// -> FUN_00053584 rotates the camera basis at win+0x14e, world Y per t416 F2).
// CADENCE MEASURED (run dbg-tngr-20261123-103130, scratch debugger, cursor
// parked): pump leg fires at newgame (12 banked, win 0xfd2310, latch=1);
// camera fwd azimuth sampled stopped->RUN->stopped drifts +104/+132/+128/
// +298/+642 deg over 2.25/2.25/2.25/5.25/10.25 s wall (fwd.y CONSTANT =>
// pure world-Y; zero drift during stopped phases). Each fire = exactly 2 deg,
// so fires/s = dtheta/2/T => 28-33 fires/s (overhead family), best long-window
// fit ~30-32/s => 60-65 DEG/S => CIRCUIT 5.6-6.1 s. USER STOPWATCH 5.3 s
// CONFIRMED. The S27 figure (2 deg/s, 180 s) was a poll-limited "~1/s"
// transferred from the t302/t305 campaign-map census — those counts tracked
// the ~1 s poll loop, never the cadence (banked law: hit-count at a hot leg
// on this instrument measures POLL RATE). The S27-X5 blob fit (3.58 px/s) was
// twinkle-coincidence matching at 1 s cadence vs ~100 px steps — the exact
// trap REFUTED-ROUTES ln1607 names.
inline constexpr double kPreviewSpinDegPerTick = 2.0;   // 0x27a32 imm
inline constexpr int kPreviewSpinTickMs = 32;           // ~31/s, S28-X3 band
                                                        // 28-33/s (5.6-6.1 s
                                                        // circuit; user 5.3 s)

// World-Y rotation of a model point by yawDeg (the vendor latch axis:
// FUN_00053584 mixes x,z; a screen-plane roll of x,y was the pre-S27
// defect shape). Pure: same inputs -> same outputs (determinism pin).
inline void previewSpinWorldY(double x, double z, double yawDeg,
                              double* ox, double* oz) {
    if (yawDeg == 0.0) { *ox = x; *oz = z; return; }
    const double t = yawDeg * 3.14159265358979323846 / 180.0;
    const double c = std::cos(t), sn = std::sin(t);
    *ox = x * c + z * sn;
    *oz = -x * sn + z * c;
}

// One preview star: model position (normalized box draw x shellRadius),
// depth-band sprite class, and the projected screen point (perspective
// divide + 0.5 bias + viewport centre). inWell=false when the point falls
// outside the cosmos rect (honest clip; NO sphere clip — S5).
// tNG-S S27: yawDeg rotates the model point about WORLD Y BEFORE the
// depth band + divide — the vendor pump rotates the camera basis, which
// is the star-side equivalent; the class (depth band) therefore cycles
// with the spin (measured: ~950 changed px/s includes reclass churn).
struct PreviewStar {
    double x, y, z;
    int cls;        // 0..3
    int sx, sy;     // screen px
    bool inWell;
};
inline PreviewStar previewStar(int vx, int vy, int vz, double shellRadius,
                               double cx, double cy, const Rect& well,
                               double yawDeg = 0.0) {
    const double fx = double(vx), fy = double(vy), fz = double(vz);
    const double len = std::sqrt(fx * fx + fy * fy + fz * fz);
    PreviewStar s{};
    if (len > 0.0) {  // vendor divides only when length>0 (FUN_00052fa0)
        s.x = fx / len * shellRadius;
        s.y = fy / len * shellRadius;
        s.z = fz / len * shellRadius;
    }
    // S27 spin: world-Y rotation of the model point BEFORE depth/projection
    // (isometry: |p| and y are preserved — pinned tngs_s27_*).
    if (yawDeg != 0.0) {
        double rx = 0.0, rz = 0.0;
        previewSpinWorldY(s.x, s.z, yawDeg, &rx, &rz);
        s.x = rx;
        s.z = rz;
    }
    const long v = std::lround(s.z);  // depth - 1500 with cam at -1500
    s.cls = v > 220 ? 0 : (v >= 1 ? 1 : (v >= -219 ? 2 : 3));
    const double depth = s.z - kCosmosCamZ;  // > 0 (shell <= 440 << 1500)
    s.sx = int(cx + s.x * kCosmosFocalPx / depth + 0.5);  // +0.5 bias S5
    s.sy = int(cy + s.y * kCosmosFocalPx / depth + 0.5);
    s.inWell = s.sx >= well.x0 && s.sx <= well.x1 && s.sy >= well.y0 &&
               s.sy <= well.y1;
    return s;
}
const char* densityWord(int starCount);  // "Average" for 50; nullptr off-ladder
const char* speciesCountWord(int n);     // "Three".."Seven"; nullptr else
const char* atmosphereWord(int v);       // 0 Peaceful / 1 Neutral / 2 Hostile
// Summary lines from a (density, species, atmosphere) triple; unknown values
// degrade to the bare noun ("Star Cluster") rather than inventing a word.
void newgameSummary(int starCount, int speciesCount, int atmosphere,
                    std::vector<std::string>* out);  // 3 lines, template 168

// LORE LAW (t393): extracted/ascend00/newgame.txt line N+1 == specnum N's
// sentence fragment ("are a mysterious group of robot creatures ..."); the
// vendor composes it with static.txt 154 "The %s %s" (name + fragment).
// Refuses (false, err) unless exactly 21 fragments parse (EOF marker 0x1a
// ends the file). Supply-your-own data rules apply: read, never embed.
bool loadNewgameLore(const std::string& path, std::vector<std::string>* out,
                     std::string* err);
std::string loreSentence(const std::string& name, const std::string& frag);

// Greedy word wrap against a measured-width function (the caller supplies
// VendorText::width; pure so it unit-tests without SDL). Never splits a
// word; a single word wider than maxW goes on its own line (honest overflow).
std::vector<std::string> wrapToWidth(
    const std::string& text, int maxW,
    const std::function<int(const std::string&)>& widthOf);

// ---- Load (LOADSCREEN/LOADLIST) -------------------------------------------
// TYPE 11 LOADSCREEN (7,7)-(632,37): the title strip; TYPE 10 LOADLIST
// (7,46)-(632,472): the slot list interior. STATE "3 2 4 15" on both.
inline constexpr Rect kLoadScreen{7, 7, 632, 37};
inline constexpr Rect kLoadList{7, 46, 632, 472};
// Row geometry [inferred — no cited row rect exists for LOADLIST]: rows are
// 30 tall with pitch 39 starting at LOADLIST.y0, the verbatim law of the
// only list census in windows.txt (RACE_1..RACE_7, y 7/46/85/124/...).
inline constexpr int kLoadRowH = 30;
inline constexpr int kLoadRowPitch = 39;

// One entry of the save-slot list. Slot law (docs/re/r1-savestate.md;
// Observer::rawDay): a raw .SAV carries its game-day as u32@0. A file
// shorter than 4 bytes is TORN (autosave rewrites slots in place; a copy can
// catch one mid-write) — torn slots are LISTED and marked, never clamped
// (t366/t369 torn-tolerance law).
struct SaveSlot {
    std::string name;   // file name as on disk (e.g. "41.sav")
    uint32_t day = 0;   // u32@0 law; 0 and meaningless when torn
    bool torn = false;  // size < 4 bytes
};

// List *.SAV / *.sav (case-insensitive extension) in `dir`, sorted by name
// ascending (the slot-name order the vendor ring uses). A missing or
// unreadable directory yields an empty list — an honest zero, never a guess.
// NEVER point this at game/: supply-your-own dir only (README law).
std::vector<SaveSlot> listSaveSlots(const std::string& dir);

// Which row index a click inside the load screen selects, -1 if the point is
// outside LOADLIST or below the last row. Rows are kLoadRowPitch apart from
// kLoadList.y0; the 9-px gutters between rows are no-man's land (no row).
int loadRowAt(Pt p, int slotCount);

// Pick law (refusal-not-clamp): accept iff index is in range and the slot is
// not torn. On refusal *why names the reason. Acceptance means the FILE is
// verified playable material; importing the state into a live Campaign is a
// named seam (docs/re/boot.md §6) — the rewrite has no campaign-state
// importer yet (Observer is read-only by contract).
bool loadPickAccepts(const std::vector<SaveSlot>& slots, int index,
                     std::string* why);

// tNG-C3 BEGIN STARFIELD LAW (D19 seed #3 CLOSED; cited law body
// 0x526f0..0x5282f, docs/re/_wip_tNGC.md F15-3): every galaxy star
// (vendor count law word[obj+0x572]) shrinks into the Begin panel:
// x = mx/5 + 5, y = my/5 + 5 where (mx,my) are MAP PIXEL coords (the
// /5 inputs are the hiwords of the record's position dwords — the same
// 0..639/0..479 space the map screen uses). OUR stars live on the
// 1024-grid (mapgen), so mx = x*640/1024, my = y*480/1024 BEFORE the /5.
// Positions are STATIC; rotation drives only the sprite class. Panel
// origin = kBeginPanelVisual (502,381); draw clipped to it.
// Returns false when the star falls outside the panel.
inline bool beginStarPos(int gx, int gy, int* px, int* py) {
    const int x = 502 + ((gx * 640 / 1024) / 5) + 5;
    const int y = 381 + ((gy * 480 / 1024) / 5) + 5;
    if (x < 502 || x > 632 || y < 381 || y > 472) return false;
    *px = x; *py = y;
    return true;
}

// FOUR-WAY SPRITE-CLASS LAW [verified 0x52817..0x5282d — supersedes the
// three-way F11 read]: v>220 -> 0, 0<v<=220 -> 1, -220<v<=0 -> 2,
// v<=-220 -> 3 (0x52817 pre-sets ecx=3; the cmp 0xdc jle KEEPS it).
inline int beginStarClass(long v) {
    return v > 220 ? 0 : (v > 0 ? 1 : (v > -220 ? 2 : 3));
}

// tNG-C3 THICK BEVELED RING LAW (refcap census, F15-3b): centre
// (600,417.5), OUTER diam 57, annulus r in [23.5,29], 5-px band; the
// emblem clips to the hole (clipR 23 about the centre).
inline bool beginRingAt(int x, int y) {
    const double dx = x - 600.0, dy = y - 417.5;
    const double rr = dx * dx + dy * dy;
    return rr >= 23.5 * 23.5 && rr <= 29.0 * 29.0;
}

}  // namespace ascend::ui
