// SPDX-License-Identifier: GPL-3.0-or-later

// Diplomacy module tests — expectations cite docs/re/diplomacy.md or the
// verbatim .dip files under extracted/ascend00.
#include "game/diplomacy.h"
#include "harness.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <filesystem>
#include <string>

#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif

namespace {
namespace ag = ascend::game;

std::string dipPath(const char* name) {
    return std::string(ASCENDANCY_SOURCE_DIR) + "/extracted/ascend00/" + name;
}

ag::DipFile loadOrDie(const char* name) {
    ag::DipFile df;
    std::string err;
    if (!df.loadFromFile(dipPath(name), &err)) {
        std::fprintf(stderr, "load %s failed: %s\n", name, err.c_str());
        std::abort();
    }
    return df;
}

}  // namespace

TEST(dip_player_has_exactly_8_keys) {
    auto df = loadOrDie("player.dip");
    // player.dip carries the 8-key subset (docs/re/diplomacy.md §1)
    CHECK(df.values.hasOscillation == false);
    CHECK(df.values.startAttitude == 100);
    CHECK(df.values.acceptAlliance == 200);
    CHECK(df.values.acceptPeace == 100);
    CHECK(df.values.breakAlliance == 170);
    CHECK(df.values.declareWar == 70);
    CHECK(df.values.proposeAlliance == 250);
    CHECK(df.values.proposePeace == 150);
    CHECK(df.values.shipPatience == 100);
}

TEST(dip_race00_oscillation_values) {
    auto df = loadOrDie("race00.dip");
    CHECK(df.values.hasOscillation == true);
    CHECK(df.values.bioPeriod == 400);      // verbatim race00.dip
    CHECK(df.values.bioMaxNegative == -4);  // negative value must parse
    CHECK(df.values.bioMaxPositive == 4);
    CHECK(df.values.negPlayerTurns == 99);
    CHECK(df.values.declareWar == 290);
}

TEST(dip_negative_values_parse) {
    // parse-trap regression (docs/re/diplomacy.md §1): an isdigit-style
    // filter silently drops negative-valued keys.
    const char* text = "DIPVALUES\nSTART_ATTITUDE 500\nBIO_MAXNEGATIVE -5\n"
                       "BIO_MAXPOSITVE 5\nBIO_PERIOD 200\nBIO_SIN_X -3\n"
                       "ACTIONS\n";
    ag::DipValues v;
    std::string err;
    CHECK(ag::DipValues::parse(text, &v, &err));
    CHECK(err.empty());
    CHECK(v.bioMaxNegative == -5);
    CHECK(v.bioSinX == -3);
    CHECK(v.hasOscillation == true);
}

TEST(dip_rejects_unknown_key_and_missing_block) {
    ag::DipValues v;
    std::string err;
    const char* badKey = "DIPVALUES\nSTART_ATTITUDE 1\nNOT_A_KEY 2\nACTIONS\n";
    CHECK(!ag::DipValues::parse(badKey, &v, &err));
    CHECK(err.find("NOT_A_KEY") != std::string::npos);
    const char* noBlock = "some comments only\n";
    CHECK(!ag::DipValues::parse(noBlock, &v, &err));
}

TEST(dip_dialogue_blocks) {
    auto df = loadOrDie("race00.dip");
    CHECK(df.dialogue.size() == 15);  // docs/re/diplomacy.md §2 count
    auto it = df.dialogue.find("DA_DeclareWar");
    CHECK(it != df.dialogue.end());
    CHECK(!it->second.empty());
}

TEST(dip_render_tokens) {
    std::string s = ag::renderDialogue("We, %m, greet %y at %s re %t.",
                                       "HUMANS", "ORFA", "Sol", "MIB");
    CHECK(s == "We, HUMANS, greet ORFA at Sol re MIB.");
    CHECK(ag::renderDialogue("x%qz", "a", "b", "b", "b") == "x%qz");  // unknown literal
    CHECK(ag::renderDialogue("end%", "a", "b", "b", "b") == "end%");  // trailing %
}

TEST(dip_header_ability) {
    auto df = loadOrDie("race00.dip");
    CHECK(df.abilityToken == "SA_SuperMarines");  // docs/re/species.md roster
    auto d11 = loadOrDie("race11.dip");
    CHECK(d11.abilityToken == "SA_BumpShipsInLanes");
}

TEST(dip_mood_oscillates_within_envelope) {
    auto df = loadOrDie("race00.dip");
    ag::AttitudeModel m(df.values);
    double lo = 1e9, hi = -1e9;
    for (int t = 0; t < 400; ++t) {
        double v = m.mood(t);
        lo = std::min(lo, v);
        hi = std::max(hi, v);
        CHECK(v >= -4.0001 && v <= 4.0001);  // +-4 envelope
    }
    CHECK(hi > 1.0);   // actually oscillates, not flat
    CHECK(lo < -1.0);
    CHECK(std::abs(m.mood(0) - m.mood(400)) < 1e-12);  // period 400
}

TEST(dip_mood_zero_without_oscillation) {
    auto df = loadOrDie("player.dip");
    ag::AttitudeModel m(df.values);
    for (int t = 0; t < 50; ++t) CHECK(m.mood(t) == 0.0);
}

TEST(dip_policy_war_on_low_attitude) {
    auto df = loadOrDie("race00.dip");
    ag::AttitudeModel m(df.values);
    ag::DipPolicyState st;
    st.attitude = 0;  // below race00 DECLARE_WAR = 290
    auto act = ag::decideDipAction(df.values, m, 200, &st);
    // mood(200) is mid-cycle; attitude stays < 290 either way
    CHECK(act == ag::DipAction::DeclareWar);
    CHECK(st.atWar == true);
    CHECK(std::string(ag::dipActionName(act)) == "DeclareWar");
}

TEST(dip_action_chooser_law_oq015_t12) {
    // MEASURED (docs/re/diplomacy.md §7): FUN_00044a44 return value == DA_
    // ACTIONS pool index (file order). Pin the ACTIONS file order and the
    // two decoded state-threshold branches' byte-level shape in the image.
    namespace fs = std::filesystem;
    const std::string dip = dipPath("race00.dip");
    if (!fs::exists(dip)) { std::printf("(skip: race00.dip absent) "); return; }
    std::FILE* f = std::fopen(dip.c_str(), "rb");
    if (!f) { CHECK(false); return; }
    std::fseek(f, 0, SEEK_END); long n = std::ftell(f); std::fseek(f, 0, SEEK_SET);
    std::string d(static_cast<size_t>(n), '\0');
    size_t got = std::fread(&d[0], 1, static_cast<size_t>(n), f);
    std::fclose(f);
    CHECK(got == static_cast<size_t>(n));
    // Pool index law (file order, §4/§7 mapping used by return values):
    const char* kOrder[] = {"DA_Discover", "DA_DiscoverAskHelp", "DA_DeclareWar",
        "DA_ProposeAlliance", "DA_TradeStarlanes", "DA_TradeStars",
        "DA_TradeResearch", "DA_OfferPeaceToOtherRace", "DA_BreakAlliance",
        "DA_DeclareWarOnOtherRace", "DA_BreakAllianceWithOtherRace",
        "DA_ProposeAllianceToOtherRace", "DA_HelpControlSystem",
        "DA_OfferPeace", "DA_NoDipAction"};
    size_t prev = d.find("ACTIONS");
    CHECK(prev != std::string::npos);
    for (const char* nm : kOrder) {
        size_t p = d.find(nm, prev);
        CHECK(p != std::string::npos);
        prev = p + 1;  // strictly ascending positions == file order
    }
    // Image shape: chooser prologue compares state byte to 2 then 3, and
    // call-site @0x447d0 gates AL==0xe (JZ epilogue 0x44713).
    const std::string imgp = std::string(ASCENDANCY_SOURCE_DIR) + "/work/ascend_restored.bin";
    if (!fs::exists(imgp)) { std::printf("(skip: work/ absent) "); return; }
    f = std::fopen(imgp.c_str(), "rb");
    if (!f) { CHECK(false); return; }
    auto at = [&](size_t a, size_t k) {
        std::array<unsigned char, 16> b{};
        std::fseek(f, static_cast<long>(a), SEEK_SET);
        std::fread(b.data(), 1, k, f);
        return b;
    };
    // E8 6F 02 00 00 @0x447d0 -> CALL 0x44a44; 3C 0E @0x447d7; 0F84 rel.
    auto b = at(0x447d0, 10);
    CHECK(b[0] == 0xe8 && b[1] == 0x6f && b[2] == 0x02 && b[3] == 0x00 && b[4] == 0x00);
    CHECK(b[5] == 0x88 && b[6] == 0xc3);            // MOV BL, AL
    CHECK(b[7] == 0x3c && b[8] == 0x0e);            // CMP AL, 0xe
    std::fclose(f);
}

TEST(dip_strict_threshold_oq015_t13) {
    // MEASURED (docs/re/diplomacy.md §7/§8): original comparisons STRICT —
    // propose-alliance fires only when PROPOSE_ALLIANCE < att (not >=).
    ag::DipValues v;
    v.declareWar = 290; v.proposePeace = 450; v.proposeAlliance = 750;
    v.breakAlliance = 510; v.negPlayerTurns = 99;  // race00 values (§8)
    v.hasOscillation = false;
    ag::AttitudeModel mood(v);
    ag::DipPolicyState st; st.attitude = 750; st.atWar = false; st.allied = false;
    // att == threshold exactly -> NO action (strict <)
    CHECK(ag::decideDipAction(v, mood, 5, &st) == ag::DipAction::None);
    st.attitude = 751;
    CHECK(ag::decideDipAction(v, mood, 5, &st) == ag::DipAction::ProposeAlliance);
    st.attitude = 290;
    CHECK(ag::decideDipAction(v, mood, 5, &st) == ag::DipAction::None);  // not war
    st.attitude = 289;
    CHECK(ag::decideDipAction(v, mood, 5, &st) == ag::DipAction::DeclareWar);
}

TEST(dip_trade_predicate_bytes_oq015_t14) {
    // MEASURED §9 pins from the restored image: each trade gate ends in
    // FCOMP qword pool-const; min-count cmp bytes; state==3 skip.
    namespace fs = std::filesystem;
    const std::string imgp = std::string(ASCENDANCY_SOURCE_DIR) + "/work/ascend_restored.bin";
    if (!fs::exists(imgp)) { std::printf("(skip: work/ absent) "); return; }
    std::FILE* f = std::fopen(imgp.c_str(), "rb");
    if (!f) { CHECK(false); return; }
    auto at = [&](size_t a, std::initializer_list<int> want) {
        unsigned char b[8] = {};
        std::fseek(f, static_cast<long>(a), SEEK_SET);
        size_t n = std::fread(b, 1, want.size(), f);
        CHECK(n == want.size());
        size_t i = 0;
        for (int w : want) CHECK(b[i++] == static_cast<unsigned char>(w));
    };
    at(0x462e2, {0x83, 0xf8, 0x05});               // starlanes: CMP EAX,5
    // FCOMP pool consts: first stays RAW (0x2432) -- imm-fixups apply only
    // SOME imms (the 143-class); second is FIXED UP 0x243a+0x82BB0=0x804fea.
    at(0x4630f, {0xdc, 0x1d, 0x32, 0x24});         // pool 0x2432 (0.9) raw
    at(0x4632e, {0xdc, 0x1d, 0xea, 0x4f, 0x08, 0x00}); // pool 0x243a (2.0) fixed
    at(0x46262, {0x80, 0xbc, 0x03, 0xc0, 0x01, 0x00, 0x00, 0x03}); // state==3 skip
    std::fclose(f);
}
