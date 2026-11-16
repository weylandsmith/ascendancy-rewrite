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
inline constexpr int kIntroRaceBytes[21] = {
    16, 7, 0, 6, 135, 57, 2, 65, 16, 7, 0,
    1,  8, 116, 12, 0, 232, 92, 15, 0, 84};

// ---- PORT LAYOUT (documented choice, _wip_t412 F5) -----------------------
// The vendor draw-call immediates (7 / 261 / 639 / 465; 7 / 245 / 639 /
// 312; 7 / 37 / 639 / 599) have UNMAPPED field roles — 599 exceeds the
// 480-line screen, so they are NOT trusted as rects. The port draws:
// header at (kIntroHeaderX, kIntroHeaderY); body paragraphs from
// (kIntroBodyX, kIntroBodyY) wrapped to kIntroBodyWidth px at pitch
// kIntroLinePitch; dismiss hint on the last row. Click/any key = continue.
inline constexpr int kIntroHeaderX = 7, kIntroHeaderY = 7;
inline constexpr int kIntroBodyX = 7, kIntroBodyY = 40;
inline constexpr int kIntroBodyWidth = 632;
inline constexpr int kIntroLinePitch = 13;  // t392 measured text pitch

// Body lines that fit the screen (rows kIntroBodyY..479 minus a 16-px
// hint band). Overflow beyond this is TRUNCATED HONESTLY (the count is
// printed once by the renderer; no scroll driver exists — named seam).
inline constexpr int kIntroMaxLines = (480 - 16 - kIntroBodyY) / kIntroLinePitch;

}  // namespace ascend::ui
