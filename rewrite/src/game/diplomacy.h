#pragma once
// Diplomacy: .dip parameter files + attitude model + dialogue templates.
// Spec: docs/re/diplomacy.md (cites extracted/ascend00/raceNN.dip,
// player.dip). Decision thresholds are [inferred] there and marked at each
// use site; the original decision loop is runtime-blocked (docs/BLOCKED.md).
#include <cstdint>
#include <map>
#include <string>
#include <vector>

namespace ascend::game {

// One race's DIPVALUES block (15 signed keys; player.dip carries the 8-key
// subset — missing oscillation keys mean "no oscillation").
struct DipValues {
    int acceptAlliance = 0, acceptPeace = 0, breakAlliance = 0;
    int declareWar = 0, proposeAlliance = 0, proposePeace = 0;
    int shipPatience = 0, startAttitude = 0;
    // oscillation (absent -> hasOscillation false, all zero)
    bool hasOscillation = false;
    int bioMaxNegative = 0, bioMaxPositive = 0, bioPeriod = 0;
    int bioSinX = 0, bioSinHalfX = 0, bioSinTwiceX = 0;
    int negPlayerTurns = 0;

    // Parse `DIPVALUES ... ACTIONS` from a .dip text (CP437 already decoded).
    // Returns false with err set on missing/empty block or unknown shape.
    static bool parse(const std::string& text, DipValues* out, std::string* err);
    static bool loadFromFile(const std::string& path, DipValues* out, std::string* err);
};

// A race's full .dip: values + DA_<key> dialogue bodies (vendor comment
// stripped; tokens %m %y %s %t left raw for renderDialogue).
struct DipFile {
    DipValues values;
    std::map<std::string, std::string> dialogue;  // "DA_Discover" -> body
    std::string displayName;                      // from header comment
    std::string abilityToken;                     // SA_<Name> or ""
    bool loadFromFile(const std::string& path, std::string* err);
};

// The documented mood model (docs/re/diplomacy.md §1, [inferred] phase
// arithmetic): attitude(t) = base + A(t), A(t) = maxPos*sin^2-ish blend...
// Kept EXPLICIT: A(t) = bioSinX*sin(x) + bioSinHalfX*sin(x/2) +
// bioSinTwiceX*sin(2x), x = 2*pi*t/bioPeriod, linearly scaled so the sum of
// |coefficients| maps into [bioMaxNegative, bioMaxPositive].
class AttitudeModel {
public:
    explicit AttitudeModel(const DipValues& v);
    // Multiplicative factor in [-1..1]*scale applied to interactions; 0 means
    // neutral. Races without oscillation keys return 0 for all t.
    double mood(int turn) const;

private:
    DipValues v_;
    double coeffAbsSum_ = 0;
};

// Dialogue rendering: replace %m %y %s %t; any OTHER %x stays literal
// (documented default, docs/re/diplomacy.md §2).
std::string renderDialogue(const std::string& body, const std::string& me,
                           const std::string& you, const std::string& star,
                           const std::string& third);

// Minimal policy engine [inferred thresholds, one place to re-check vs R1]:
// scale is the original 0..1000-ish attitude implied by START_ATTITUDE 310..620
// and DECLARE_WAR 130..450 in docs/re/diplomacy.md §1.
enum class DipAction { None, ProposePeace, ProposeAlliance, AcceptPeace,
                       AcceptAlliance, BreakAlliance, DeclareWar };
const char* dipActionName(DipAction a);

struct DipPolicyState {
    bool atWar = false;
    bool allied = false;
    int attitude = 0;  // running relationship score
};
// Evaluate one turn: adjusts state, returns the action to communicate.
DipAction decideDipAction(const DipValues& v, const AttitudeModel& mood,
                          int turn, DipPolicyState* st);

}  // namespace ascend::game
