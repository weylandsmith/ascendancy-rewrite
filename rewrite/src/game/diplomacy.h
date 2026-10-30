#pragma once
// Diplomacy: .dip parameter files + attitude model + dialogue templates.
// Spec: docs/re/diplomacy.md — chooser law §7 (t12), DIPVALUES field map §8
// (t13), trade/share gates + cadence §9 (t14) are MEASURED; the nonzero
// relation-state ENUM semantics are capture-gated (§10, t77b). Decision
// logic below mirrors §7 for the two-party main branch only.
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

// Two-party policy engine mirroring the MEASURED chooser §7/§8 (thresholds
// are vendor DIPVALUES, strict comparisons); trade/third-party rungs of §9
// are intentionally NOT modelled here (W-B ownership-model gate, OQ-023).
// Scale is the original 0..1000-ish attitude implied by START_ATTITUDE
// 310..620 and DECLARE_WAR 130..450 in docs/re/diplomacy.md §1.
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

// t204 DIPLOMACY-ON-ATTACK hostility cost — FUN_00043a4c verbatim
// (0x43a4c..0x43b0e, restored image; callers 0x4b875 damage-apply,
// 0x39fba/0x3a255 planet-event; docs/re/_wip_t204.md S1..S4, gap map row 13).
// The VICTIM's attitude toward the attacker pays 10*(govByte+1), DOUBLED if
// the relation state was 3 (ALLIANCE, t189b identity). Guard: state==2 (AT
// WAR) pays nothing (0x43a90 -> 0x43b09, the handler's only no-write path).
// Alliance-violation CEILING (0x43acc..0x43ae7, a ceiling NOT a floor): iff
// allied AND the post-subtraction attitude is STILL strictly above the
// victim's own BREAK_ALLIANCE line (+0x1cf, diplomacy.md §8 positional map),
// slam it to breakAlliance-10 — guarantees the alliance dies. Returns true
// iff the hostility mark was written (original's -1 path at 0x43b00; the
// caller-visible meaning: this attack is an act of hostility, set the global
// attacked-bitmap bit for the victim race; false iff the at-war early return).
// govByte is the LIVE byte at [0x13bc4] (censused ==1 in 20/20 playcap saves;
// kept a parameter so pins cover the {0,1,2} ladder). NO rng draws (S5/D5).
bool applyAttackDipCost(const DipValues& v, bool victimAtWar, bool victimAllied,
                        int govByte, int* attitude);

// t207 GUARANTEE-WAR clamp — FUN_0003a174's post-handler site 0x3a25a..
// 0x3a291: after an INVASION pays applyAttackDipCost, iff that call took
// the non-war (-1) path and the victim's attitude cell is STILL strictly
// above the victim's DECLARE_WAR line (+0x1c9), slam it to declareWar-10 —
// the t180 chooser (att < +0x1c9 -> DA_DeclareWar) then guarantees war.
// No-op on the at-war path (the original skips on the handler's 0 return).
void guaranteeWarOnInvasion(const DipValues& v, bool victimAtWar, int* attitude);

// Live-measured scenario value of the subtrahend key byte [0x13bc4]
// (20/20 saves in work/r1/playcap/save, pointer law, t204 S3).
constexpr int kAttackDipGovByte = 1;

}  // namespace ascend::game
