#pragma once
// Species special abilities (SA_<Token>) wired into the campaign.
// Roster + effect prose: docs/re/species.md and extracted/ascend00/help.txt
// blocks `help abilNN` (vendor text quoted in docs/re/abilities.md; every
// effect below cites its abil block line range). Charge/cooldown arithmetic
// is NOT exposed by any data file — documented default in abilities.md §3.
#include <array>
#include <string>
#include <vector>

namespace ascend::game {

struct DipFile;  // game/diplomacy.h (only needed by loadAbilities)

enum class SpeciesAbility : int {
    Unknown = -1,
    SuperMarines = 0, DoubleHull, BuildOnBlack, KnowHomeWorlds, KnowRaces,
    HealShips, ForcePeace, DoublePower, RepelAlienShips, SapAlienPower,
    Cornucopia, BumpShipsInLanes, StealResearch, ShieldPlanets, MoreMaxPop,
    KnowStarLanes, BlockStarLanes, CauseWar, FastLaneTravel, FreeResearch,
    IndustryBoost, kCount
};
const char* abilityName(SpeciesAbility a);   // "SA_SuperMarines" form
SpeciesAbility abilityFromToken(const std::string& token);  // Unknown if no match

// The vendor charge text shown on gated abilities (help.txt, verbatim):
// "It will take %d day%s to amass the energy needed to use your ability."
// 14 of the 21 abilNN blocks carry it; 7 (indices 0,1,2,3,4,15,18) are
// always-on passive abilities [verified, scripts/ability_probe.py].
bool abilityIsCharged(SpeciesAbility a);
// Charge time in days = MEASURED cadence word WORD[0x6780+2*ability]
// (t100, aicode.md §6.4; abilities.md §3): turns between activations; 0 for
// passives (the vendor table's zero entries are exactly the passive set).
int abilityChargeTurns(SpeciesAbility a);
// One-line effect/no-op citation for EVERY token ("SA_X: <effect> [help.txt
// L<nnnn>]" or "... FILED NO-OP ..."). Non-empty for all 21 — a unit test
// (and gate 3m) asserts it, which is what licenses the claim that the roster
// is fully wired-or-filed rather than partially silent (docs/re/abilities.md).
const char* abilityEffectNote(SpeciesAbility a);

// Load the 21 raceNN.dip headers, cross-check each SA_ token against the
// 21 `help abilNN` tokens in help.txt, and return them in specnum order 0..20.
// race02.dip (Orfa) carries NO token in its header [verified] — its ability
// is identified solely by the help-abil02 title match; the merged entry's
// token is SA_BuildOnBlack. Fails (errOut set) if the two sources disagree
// anywhere or counts != 21.
struct SpeciesInfo {
    int specnum = -1;
    std::string dipName;        // header display name ("" for race02)
    SpeciesAbility ability = SpeciesAbility::Unknown;
};
bool loadAbilities(const std::string& dataDir0,   // dir holding raceNN.dip + help.txt
                   std::vector<SpeciesInfo>* out, std::string* errOut);

}  // namespace ascend::game
