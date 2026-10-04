// Diplomacy module tests — expectations cite docs/re/diplomacy.md or the
// verbatim .dip files under extracted/ascend00.
#include "game/diplomacy.h"
#include "harness.h"

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstdlib>
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
