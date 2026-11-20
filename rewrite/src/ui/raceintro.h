// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
// t412 RACE INTRO law (docs/re/_wip_t412.md F3/F4).
//
// THE VENDOR READS history.txt AT GAME START [verified, Ghidra
// ascend_restored.bin FUN_0002b48a, banked _wip_t412 F3]: the census site
// "history 0x2b4d5" (datafiles.md S2) is the pool immediate inside this
// function (0x82BB0+0x1190 = payload 0x83d40 = "history.txt"). The loader:
//   - scans lines for literal "SPECNUM" + "%s %d" until specnum ==
//     DAT_0007458e (the player species word); missing race ->
//     "Species %d not found in history file." (pool 0x83d71);
//   - POWER block  -> the header line (pool "%s: " 0x83dbd);
//   - INTRO block  -> body part 1 (204-B buffer, cap 0xc3);
//   - TEXT  block  -> body part 2 (1000-B buffer, cap 0x3e3);
//   - PEACE / NEUTRAL / HOSTILE blocks -> appended to the SAME body,
//     gated on DAT_00013bc4 == 0 / 1 / 2 (the three-way atmosphere word
//     Peaceful/Neutral/Hostile matches the New Game control's words
//     exactly [inferred binding; the gating itself is verified code]);
//   - a FINAL block -> a separate 3000-B buffer (cap 0xbb3) the render
//     tail never touches [role unmapped; NOT displayed here — seam].
//   - TRANSFORM [verified tail]: '@' -> '\n', '_' -> ' ', '\n' -> ' '.
//     So "@@" is a PARAGRAPH BREAK and "_____" is indent filler.
// Ink colour = game.pal[racebyte*4 + 0x13], racebyte = byte at
// 0x12e18 + specnum*494 (F4). Display geometry is UNCITED (the three
// FUN_0002fb38 args are unmapped); the port layout below is a documented
// choice, decider = a live vendor capture.
#include <string>
#include <vector>

namespace ascend::ui {

// One parsed per-race block from history.txt (raw sections, file form).
struct HistoryRace {
    bool found = false;
    std::string power;    // POWER block, single line
    std::string intro;    // INTRO block raw text
    std::string text;     // TEXT block raw text
    std::string peace;    // PEACE block raw text (atmosphere 0)
    std::string neutral;  // NEUTRAL block raw text (atmosphere 1)
    std::string hostile;  // HOSTILE block raw text (atmosphere 2)
};

// Parse the whole history.txt image; returns the block for `specnum`
// (0..20). found=false + errOut when the specnum block does not exist —
// the vendor's "Species %d not found" error path, mirrored, never faked.
HistoryRace parseHistoryRace(const std::string& fileText, int specnum,
                             std::string* errOut);

// The vendor transform law applied to a raw section: '@' -> '\n',
// '_' -> ' ', '\n' -> ' ' (verified, FUN_0002b48a tail).
std::string introTransform(const std::string& raw);

// The assembled intro for a (specnum, atmosphere) pair:
//   header = power (the "%s: " prefix is the CALLER's render choice);
//   body   = transform(intro) + "\n" + transform(text) + "\n"
//            + transform(peace|neutral|hostile[atmosphere])
// Empty sections contribute nothing (the vendor concatenates what exists).
// atmosphere outside 0..2 keeps the body without a gated section (refuse,
// never clamp).
struct IntroPanel {
    std::string header;           // "power" line, raw (transform applied)
    std::vector<std::string> paragraphs;  // body split on '\n' (the '@@'
                                          // paragraph law), each with
                                          // leading/trailing blanks trimmed
    // t415 WELL SPLIT [measured, docs/re/_wip_t415.md F5]: the vendor
    // screenshot shows the INTRO block in the right well (white) and the
    // TEXT(+gated) block in the bottom well (race ink). The decompile
    // supports it: INTRO -> acStack_16c (a SEPARATE 204-B buffer), while
    // TEXT + PEACE/NEUTRAL/HOSTILE concat into acStack_624 — two buffers,
    // two wells. introWell = INTRO paras; textWell = TEXT + gated paras.
    std::vector<std::string> introWell;
    std::vector<std::string> textWell;
};
bool buildIntroPanel(const std::string& fileText, int specnum, int atmosphere,
                     IntroPanel* out, std::string* errOut);

// Word-wrap `para` into lines fitting `maxPx` at char width `charW`
// (the port's render law; the vendor's wrap width is uncited). Words are
// split on single spaces; a word longer than the line stands alone.
std::vector<std::string> wrapIntroLine(const std::string& para, int maxPx,
                                       int charW);

// The game.pal index law for the intro ink colour [verified F4]:
// idx = racebyte*4 + 0x13 with racebyte read from the race-table dump.
// Pure so the pins can check it against the extracted table bytes.
inline constexpr int introPalIndex(int raceColourByte) {
    return (raceColourByte & 0xff) * 4 + 0x13;
}

// The 21 static-table colour bytes at 0x12e18 + specnum*494 read verbatim
// from the restored image (work/ascend_payload.bin, census _wip_t412 F4).
// [verified bytes] for the static image; SEAM: at runtime the vendor's
// diplo table is scenario-populated (diplomacy.md), so a live game may
// carry different bytes than the shipped defaults. Decider: a RAM census
// of 0x12e18+2 during a live intro.
// t424b ENTRY [0] OVERWRITTEN [measured witness, docs/re/_wip_t424b.md F3]:
// the vendor screenshot (Minions intro) body ink = (56,170,85) =
// game.pal[0*4+0x13] => RUNTIME racebyte 0, not the static byte 16 (which
// renders red pal[83]). Only the WITNESSED entry changes; the other 20
// static bytes stay seam H3 (one race's witness cannot set 21 bytes, t415
// law). The static dump byte is recorded here so the change is auditable:
//   [0] static 16 -> witnessed 0.
inline constexpr int kIntroRaceBytes[21] = {
    0, 7, 0, 6, 135, 57, 2, 65, 16, 7, 0,
    1,  8, 116, 12, 0, 232, 92, 15, 0, 84};

// ---- PORT LAYOUT (t415 MEASURED, docs/re/_wip_t415.md F5) ---------------
// The three FUN_0002fb38 rect structs in FUN_0002b48a are readable via
// that function's own field accesses (box origin +0x0c/+0x10, extent
// +0x14/+0x18): call#3 header (7,7)-(632,37), call#2 right well
// (312,46)-(632,245), call#1 body (7,261)-(632,465). All three agree with
// the bright-run frame census off the user-supplied vendor screenshot to
// <=1 px. PORTRAIT lgrace<specnum> k0 NATIVE 296x199 at (7,46) (template
// match MSE 73 at that origin). EMBLEM raceflag k<specnum> NATIVE 14x24
// at (9,10). FRAME colour game.pal[62] (124,180,180); outer rect
// (2,2)-(636,477), header divider y39..41, band divider y247..250,
// vertical separator x304..307 (TOP BAND ONLY).
inline constexpr int kIntroHeaderX = 7, kIntroHeaderY = 7;
inline constexpr int kIntroHeaderW = 632, kIntroHeaderH = 37;
inline constexpr int kIntroEmblemX = 9, kIntroEmblemY = 10;  // 14x24 native
inline constexpr int kIntroPortraitX = 7, kIntroPortraitY = 46;  // 296x199
// Right well (INTRO block, white): interior of (312,46)-(632,245).
inline constexpr int kIntroRightX = 312, kIntroRightY = 46;
inline constexpr int kIntroRightX1 = 632, kIntroRightY1 = 245;
// Body well (TEXT + gated block, race ink): interior of (7,261)-(632,465).
inline constexpr int kIntroBodyX = 7, kIntroBodyY = 261;
inline constexpr int kIntroBodyX1 = 632, kIntroBodyY1 = 465;
// Text WRAP widths per well (measured: right line1 x348..598 inside
// 312..632; body line1 x18..612 inside 7..632 -> ~16-px side margins).
inline constexpr int kIntroRightWrap = 300;
inline constexpr int kIntroBodyWrap = 600;
inline constexpr int kIntroLinePitch = 13;  // t415 measured rows 56/69/82
                                            // and 271/284/298 (pitch 13)
// t415: both wells CENTRE their lines (measured: right line1 centre 473
// vs well centre 472; body centre 315 vs 319.5).
// Frame rects (outer + dividers) for the renderer:
inline constexpr int kIntroFrameX0 = 2, kIntroFrameY0 = 2;
inline constexpr int kIntroFrameX1 = 636, kIntroFrameY1 = 477;
inline constexpr int kIntroHeaderDivY = 40;    // measured run 39..41
inline constexpr int kIntroBandDivY = 248;     // measured run 247..250
inline constexpr int kIntroSepX = 305;         // measured run 304..307

// Well line capacity (pitch law): text rows start one pitch inside the
// well top; overflow is TRUNCATED HONESTLY (count printed once; no
// scroll driver exists — named seam).
inline constexpr int kIntroRightMaxLines =
    (kIntroRightY1 - kIntroRightY - kIntroLinePitch) / kIntroLinePitch;
inline constexpr int kIntroBodyMaxLines =
    (kIntroBodyY1 - kIntroBodyY - kIntroLinePitch) / kIntroLinePitch;

}  // namespace ascend::ui
