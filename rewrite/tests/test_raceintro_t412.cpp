// SPDX-License-Identifier: GPL-3.0-or-later

// t412 RACE INTRO law pins (docs/re/_wip_t412.md F3/F4/F5 + raceintro.h).
//  1. parseHistoryRace finds the specnum block via "SPECNUM n" and the
//     section keywords verbatim; a missing specnum reproduces the vendor's
//     "Species %d not found in history file." refusal (pool 0x83d71).
//  2. The transform law is '@' -> '\n', '_' -> ' ', '\n' -> ' ' (verified
//     FUN_0002b48a tail): "@@" = paragraph break, "_____" = indent filler.
//  3. buildIntroPanel: header = POWER; body = INTRO + TEXT + the ONE
//     atmosphere-gated section (0 PEACE / 1 NEUTRAL / 2 HOSTILE); out-of-
//     range atmosphere REFUSES the gated section, never clamps.
//  4. The real history.txt (REQUIRE_DATA): all 21 specnums parse; specnum 0
//     carries the cited first words; the atmosphere sections of a race that
//     has them land in the right body; no raw '@' or '_' survives.
//  5. The intro ink law introPalIndex(b) == b*4 + 0x13 matches the STATIC
//     table bytes (kIntroRaceBytes census of payload 0x12e18 + i*494).
//  6. wrapIntroLine respects the pixel budget and never truncates a word.
#include "ui/raceintro.h"

#include <cstdio>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>

#include "harness.h"

namespace {
namespace au = ascend::ui;
const std::string kRepo = ASCENDANCY_SOURCE_DIR;

std::string fixture() {
    // The file's real shape (CRLF normalised by the parser's trim):
    // comments, specnum blocks, keyword sections, blank-line separators.
    return "// Minions\r\n"
           "specnum 0\r\n"
           "power\r\n"
           "Supreme Planet Invaders\r\n"
           "endpower\r\n"
           "\r\n"
           "intro\r\n"
           "_____Your ancient programming has been reactivated.\r\n"
           "@@_____The Minions have detected transmissions.\r\n"
           "endintro\r\n"
           "\r\n"
           "peace\r\n"
           "PEACE LINE\r\n"
           "endpeace\r\n"
           "\r\n"
           "neutral\r\n"
           "NEUTRAL LINE\r\n"
           "endneutral\r\n"
           "\r\n"
           "hostile\r\n"
           "HOSTILE LINE\r\n"
           "endhostile\r\n"
           "\r\n"
           "text\r\n"
           "TEXT BODY\r\n"
           "endtext\r\n"
           "\r\n"
           "end\r\n"
           "\r\n"
           "// Snovemdomas\r\n"
           "specnum 1\r\n"
           "power\r\n"
           "Other Power\r\n"
           "endpower\r\n"
           "intro\r\n"
           "OTHER INTRO\r\n"
           "endintro\r\n"
           "end\r\n";
}
}  // namespace

TEST(raceintro_t412_parse_sections_verbatim) {
    std::string err;
    const auto r = au::parseHistoryRace(fixture(), 0, &err);
    CHECK(r.found);
    CHECK(r.power == "Supreme Planet Invaders");
    CHECK(r.intro ==
          "_____Your ancient programming has been reactivated.\n"
          "@@_____The Minions have detected transmissions.");
    CHECK(r.peace == "PEACE LINE");
    CHECK(r.neutral == "NEUTRAL LINE");
    CHECK(r.hostile == "HOSTILE LINE");
    CHECK(r.text == "TEXT BODY");
    // The second block does NOT leak into the first.
    const auto r1 = au::parseHistoryRace(fixture(), 1, &err);
    CHECK(r1.found && r1.power == "Other Power");
    CHECK(r1.peace.empty());
}

TEST(raceintro_t412_missing_specnum_vendor_error_verbatim) {
    std::string err;
    const auto r = au::parseHistoryRace(fixture(), 9, &err);
    CHECK(!r.found);
    // pool 0x83d71 verbatim ("Species %d not found in history file.\n")
    CHECK(err == "Species 9 not found in history file.");
}

TEST(raceintro_t412_transform_law) {
    // '@' -> '\n'; '_' -> ' '; '\n' -> ' ' (FUN_0002b48a tail, verified).
    CHECK(au::introTransform("a@b") == "a\nb");
    CHECK(au::introTransform("@@") == "\n\n");
    CHECK(au::introTransform("_____x") == "     x");
    CHECK(au::introTransform("a\nb") == "a b");
    CHECK(au::introTransform("no_markers") == "no markers");
}

TEST(raceintro_t412_panel_atmosphere_gating) {
    std::string err;
    au::IntroPanel p0, p1, p2, pbad;
    CHECK(au::buildIntroPanel(fixture(), 0, 0, &p0, &err));
    CHECK(p0.header == "Supreme Planet Invaders");
    CHECK(au::buildIntroPanel(fixture(), 0, 1, &p1, &err));
    CHECK(au::buildIntroPanel(fixture(), 0, 2, &p2, &err));
    // The gated line differs per atmosphere and appears exactly once.
    const auto has = [](const au::IntroPanel& p, const char* s) {
        int n = 0;
        for (const auto& l : p.paragraphs)
            if (l.find(s) != std::string::npos) n++;
        return n;
    };
    CHECK(has(p0, "PEACE LINE") == 1 && has(p0, "NEUTRAL LINE") == 0 &&
          has(p0, "HOSTILE LINE") == 0);
    CHECK(has(p1, "NEUTRAL LINE") == 1 && has(p1, "PEACE LINE") == 0);
    CHECK(has(p2, "HOSTILE LINE") == 1 && has(p2, "PEACE LINE") == 0);
    // refuse-not-clamp: atmosphere 3 keeps INTRO+TEXT, gains nothing.
    CHECK(au::buildIntroPanel(fixture(), 0, 3, &pbad, &err));
    CHECK(has(pbad, "PEACE LINE") == 0 && has(pbad, "NEUTRAL LINE") == 0 &&
          has(pbad, "HOSTILE LINE") == 0 && has(pbad, "TEXT BODY") == 1);
    // The '@@' law split the intro into TWO paragraphs; '_' fillers are
    // gone; no raw marker survives anywhere.
    CHECK(p0.paragraphs.size() >= 4);  // 2 intro paras + text + peace
    for (const auto& l : p0.paragraphs)
        CHECK(l.find('@') == std::string::npos &&
              l.find('_') == std::string::npos);
    CHECK(p0.paragraphs[0] == "Your ancient programming has been reactivated.");
}

TEST(raceintro_t412_real_history_all_21) {
    REQUIRE_DATA();
    std::ifstream f(kRepo + "/extracted/ascend00/history.txt",
                    std::ios::binary);
    CHECK(bool(f));
    std::stringstream ss;
    ss << f.rdbuf();
    const std::string txt = ss.str();
    std::string err;
    for (int spec = 0; spec < 21; spec++) {
        const auto r = au::parseHistoryRace(txt, spec, &err);
        CHECK(r.found);
        CHECK(!r.power.empty());
        CHECK(!r.intro.empty());
        CHECK(!r.text.empty());
    }
    // specnum 0 cited first words (history.txt ln 7, verified).
    au::IntroPanel p;
    CHECK(au::buildIntroPanel(txt, 0, 1, &p, &err));
    CHECK(p.header == "Supreme Planet Invaders");
    CHECK(p.paragraphs[0].rfind(
              "Your ancient programming has been reactivated.", 0) == 0);
    // Census [measured]: specnum 1 (Snovemdomas) is the ONLY race with
    // non-empty PEACE/NEUTRAL/HOSTILE blocks in the shipped file (all
    // others carry empty pairs) — the gating must actually change ITS body.
    au::IntroPanel o0, o1;
    CHECK(au::buildIntroPanel(txt, 1, 0, &o0, &err));
    CHECK(au::buildIntroPanel(txt, 1, 1, &o1, &err));
    CHECK(o0.paragraphs != o1.paragraphs);
    // The other 20 races: atmosphere never changes the body (empty gated
    // sections contribute nothing).
    CHECK(au::buildIntroPanel(txt, 0, 0, &o0, &err));
    CHECK(au::buildIntroPanel(txt, 0, 2, &o1, &err));
    CHECK(o0.paragraphs == o1.paragraphs);
}

TEST(raceintro_t412_ink_law_matches_table) {
    // introPalIndex(b) = b*4 + 0x13; the 21 census bytes are the static
    // table at 0x12e18 + specnum*494 (verified _wip_t412 F4). Orfa (2)
    // byte 0 -> pal 19 = the vendor lore green family.
    CHECK(au::introPalIndex(0) == 0x13);
    CHECK(au::introPalIndex(16) == 83);
    // t424b: Minions (0) WITNESSED runtime byte is 0 (vendor screenshot ink
    // (56,170,85) = pal[19]; _wip_t424b F3) — static dump byte was 16.
    CHECK(au::kIntroRaceBytes[0] == 0);
    CHECK(au::kIntroRaceBytes[2] == 0);
    CHECK(au::kIntroRaceBytes[20] == 84);
}

TEST(raceintro_t412_wrap_budget_and_word_integrity) {
    const auto lines = au::wrapIntroLine("alpha beta gamma delta", 40, 8);
    // 40 px / 8 px = 5 chars: "alpha" fits alone per line (beta=4 + space
    // would be 40+8 > 40).
    CHECK(lines.size() == 4);
    CHECK(lines[0] == "alpha" && lines[3] == "delta");
    // An over-long word stands alone, NEVER truncated.
    const auto one = au::wrapIntroLine("supercalifragilistic", 40, 8);
    CHECK(one.size() == 1 && one[0] == "supercalifragilistic");
    // Degenerate budget refuses to wrap (returns the para whole), never
    // drops text.
    const auto none = au::wrapIntroLine("keep me", 0, 8);
    CHECK(none.size() == 1 && none[0] == "keep me");
    const auto none2 = au::wrapIntroLine("keep me", 100, 0);
    CHECK(none2.size() == 1 && none2[0] == "keep me");
}

// t415 WELL SPLIT (docs/re/_wip_t415.md F5): INTRO -> introWell (the
// right-well buffer acStack_16c); TEXT + the atmosphere-gated section ->
// textWell (the body buffer acStack_624); `paragraphs` keeps the legacy
// merged order INTRO+TEXT+gated (t412 pins ride on it).
TEST(raceintro_t415_well_split) {
    std::string err;
    au::IntroPanel p0, p2;
    CHECK(au::buildIntroPanel(fixture(), 0, 0, &p0, &err));
    CHECK(au::buildIntroPanel(fixture(), 0, 2, &p2, &err));
    // introWell holds ONLY the INTRO block paragraphs.
    CHECK(!p0.introWell.empty());
    CHECK(p0.introWell[0] == "Your ancient programming has been reactivated.");
    for (const auto& l : p0.introWell)
        CHECK(l.find("HOSTILE LINE") == std::string::npos);
    // textWell holds TEXT + the gated section (atmosphere-selected).
    bool bodyHasText = false, hostileIn2 = false, hostileIn0 = false;
    for (const auto& l : p0.textWell) {
        if (l.find("TEXT BODY") != std::string::npos) bodyHasText = true;
        if (l.find("HOSTILE LINE") != std::string::npos) hostileIn0 = true;
    }
    for (const auto& l : p2.textWell)
        if (l.find("HOSTILE LINE") != std::string::npos) hostileIn2 = true;
    CHECK(bodyHasText);
    CHECK(hostileIn2);
    CHECK(!hostileIn0);
    // Legacy merged body = introWell then textWell, same order.
    CHECK(p0.paragraphs.size() == p0.introWell.size() + p0.textWell.size());
    for (size_t i = 0; i < p0.introWell.size(); i++)
        CHECK(p0.paragraphs[i] == p0.introWell[i]);
    // Layout law: the right well is 320x199 (the Ghidra call#2 rect),
    // portrait 296x199 at (7,46) fits its well (296+7 = 303 <= sep 305).
    CHECK(au::kIntroRightX1 - au::kIntroRightX == 320);
    CHECK(au::kIntroRightY1 - au::kIntroRightY == 199);
    CHECK(au::kIntroPortraitX + 296 <= au::kIntroSepX);
    CHECK(au::kIntroLinePitch == 13);
}
