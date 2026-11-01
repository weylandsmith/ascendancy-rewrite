#include "game/species.h"

#include <fstream>
#include <regex>
#include <sstream>
#include <unordered_map>

#include "game/diplomacy.h"
#include "game/starstat.h"  // cp437ToUtf8

namespace ascend::game {
namespace {

// Token table order == the help.txt abil00..abil20 order == specnum order
// (cross-validated three ways in docs/re/abilities.md §1: dip header tokens,
// help block titles, history.txt blurb names).
const char* const kTokens[static_cast<int>(SpeciesAbility::kCount)] = {
    "SA_SuperMarines",      "SA_DoubleHull",      "SA_BuildOnBlack",
    "SA_KnowHomeWorlds",    "SA_KnowRaces",       "SA_HealShips",
    "SA_ForcePeace",        "SA_DoublePower",     "SA_RepelAlienShips",
    "SA_SapAlienPower",     "SA_Cornucopia",      "SA_BumpShipsInLanes",
    "SA_StealResearch",     "SA_ShieldPlanets",   "SA_MoreMaxPop",
    "SA_KnowStarLanes",     "SA_BlockStarLanes",  "SA_CauseWar",
    "SA_FastLaneTravel",    "SA_FreeResearch",    "SA_IndustryBoost",
};

// Charged abilities: those whose help abilNN block carries the vendor line
// "It will take %d day%s to amass the energy..." [verified help.txt
// L1829,1876,1923,1971,2018,2065,2112,2160,2207,2254,2320,2367,2435,2482].
bool chargedIdx(int idx) {
    switch (idx) {
        case 0: case 1: case 2: case 3: case 4: case 15: case 18:
            return false;  // passive: no amass-energy line in the block
        default:
            return true;
    }
}

}  // namespace

const char* abilityName(SpeciesAbility a) {
    const int i = static_cast<int>(a);
    return (i >= 0 && i < static_cast<int>(SpeciesAbility::kCount)) ? kTokens[i]
                                                                    : "SA_Unknown";
}

SpeciesAbility abilityFromToken(const std::string& token) {
    for (int i = 0; i < static_cast<int>(SpeciesAbility::kCount); ++i)
        if (token == kTokens[i]) return static_cast<SpeciesAbility>(i);
    return SpeciesAbility::Unknown;
}

bool abilityIsCharged(SpeciesAbility a) { return chargedIdx(static_cast<int>(a)); }

const char* abilityEffectNote(SpeciesAbility a) {
    // Same order as kTokens / help.txt abil00..abil20. Every entry cites its
    // help.txt line block; NO-OP filings say why (docs/re/abilities.md §2).
    static const char* const kNotes[static_cast<int>(SpeciesAbility::kCount)] = {
        "invasions always succeed, max one per turn [help.txt L1723]",
        "incoming hull damage halved [help.txt L1743]",
        "FILED NO-OP: black planet squares have no buildable-slot model [help.txt L1763]",
        "see all alien home stars: owner bits OR into every alien HOME star's select/lane-follow twin at scenario init (OQ-026 layer, ships.md S23 L9; vendor flag consumer unmapped -> help.txt is the effect law) [help.txt L1783]",
        "FILED NO-OP: dialogue is never gated by contact in the sim [help.txt L1803]",
        "fleet damage cleared [help.txt L1824]",
        "all wars of the user ended [help.txt L1870]",
        "attack power doubled this turn [help.txt L1917]",
        "enemy ships bound for user stars returned [help.txt L1965]",
        "enemy fleet power drained in border systems [help.txt L2012]",
        "least-populated colony gains PROS 2 [help.txt L2059]",
        "all in-transit ships returned to origin [help.txt L2106]",
        "techs known by >=2 others acquired [help.txt L2154]",
        "own stars un-capturable this turn [help.txt L2201]",
        "colony pop caps +25 [help.txt L2248]",
        "see all star lanes: owner bit OR into every lane mask at scenario init; the cosmos filter always admits them (OQ-026 layer, ships.md S23 L6/L9; passive cadence word 0) [help.txt L2295]",
        "lanes into own stars closed to others this turn [help.txt L2314]",
        "third parties' regard of the user ceilinged to each enemy's own DECLARE_WAR line (SA_Hatred body law 0x440b5, aicode.md S6.3; t256) [help.txt L2361]",
        "+1 launch hop (clamped 3) [help.txt L2409]",
        "queued discovery completes at once [help.txt L2429]",
        "every colony with a pending project gains 100 build-accumulator (per-planet +0x50 += 100 law 0x4418e, aicode.md S6.3; t256) [help.txt L2476]",
    };
    const int i = static_cast<int>(a);
    return (i >= 0 && i < static_cast<int>(SpeciesAbility::kCount)) ? kNotes[i] : "";
}

int abilityChargeTurns(SpeciesAbility a) {
    // MEASURED CADENCE TABLE (OQ-020 CLOSED t100; docs/re/aicode.md §6.4):
    // WORD[0x6780 + 2*ability] embedded in ascend.exe — live playcap/save/
    // 60.sav words == restored FILE 0x89330 byte-exact, ZERO stores image-
    // wide (constant scenario table; gate + reads 0x43b58/0x37bf1/0x3e7f6/
    // 0x43fee). ZERO entries {0..4,15,18,21} == the 7 passives == exactly
    // !chargedIdx (nonzero set {5..14,16,17,19,20}). The old 30-turn
    // documented default is FALSIFIED per-ability (HealShips 60, ForcePeace
    // 100, Cornucopia 150 ...).
    static const int kCad[static_cast<int>(SpeciesAbility::kCount)] = {
        0,   0,  0,   0,  0,   // 0-4  passives
        60, 100, 62,  77, 90,  // 5 HealShips, 6 ForcePeace, 7 DoublePower,
                                //   8 RepelAlienShips, 9 SapAlienPower
        150, 70, 63, 66, 72,   // 10 Cornucopia, 11 BumpShipsInLanes,
                                //   12 StealResearch, 13 ShieldPlanets,
                                //   14 MoreMaxPop
        0,                      // 15 KnowStarLanes (passive)
        92, 100,                // 16 BlockStarLanes, 17 CauseWar
        0,                      // 18 FastLaneTravel (passive)
        89, 68                  // 19 FreeResearch, 20 IndustryBoost
    };
    const int i = static_cast<int>(a);
    return (i >= 0 && i < static_cast<int>(SpeciesAbility::kCount)) ? kCad[i] : 0;
}

bool loadAbilities(const std::string& dataDir0, std::vector<SpeciesInfo>* out,
                   std::string* errOut) {
    // 1. Parse help.txt: abilNN -> species title ("Minions", "Orfa", ...).
    std::ifstream hf(dataDir0 + "/help.txt", std::ios::binary);
    if (!hf) { *errOut = dataDir0 + "/help.txt: cannot open"; return false; }
    std::stringstream hb; hb << hf.rdbuf();
    const std::string help = cp437ToUtf8(hb.str());
    std::regex blockRe(R"(// SA_(\w+)\r?\n\r?\nhelp abil(\d{2})\r?\n\r?\ntext\r?\n(.+?) Special Ability\r?\nendtext)");
    std::unordered_map<int, std::pair<std::string, std::string>> byIdx;
    for (auto it = std::sregex_iterator(help.begin(), help.end(), blockRe);
         it != std::sregex_iterator(); ++it) {
        const int idx = std::stoi((*it)[2]);
        // group(1) is the token WITHOUT the SA_ prefix (the regex matches
        // "SA_(\w+)") — restore it so abilityFromToken() can resolve it
        // (unit test caught the miss: race02 title lookup silently Unknown).
        byIdx[idx] = {"SA_" + (*it)[1].str(), (*it)[3].str()};
    }
    if (byIdx.size() != 21) {
        *errOut = "help.txt: expected 21 SA_ abil blocks, found " +
                  std::to_string(byIdx.size());
        return false;
    }
    // Title -> token must be unique (the race02 cross-check key). byIdx
    // values are {token, title} — key the map by TITLE (L-bug caught by the
    // unit test: first emplace keyed by token, silently breaking the race02
    // display-name lookup).
    std::unordered_map<std::string, std::string> titleToToken;
    for (auto& kv : byIdx) {
        if (!titleToToken.emplace(kv.second.second, kv.second.first).second) {
            *errOut = "help.txt: duplicate ability title '" + kv.second.second + "'";
            return false;
        }
    }

    // 2. Read the 21 raceNN.dip headers and reconcile.
    out->clear();
    for (int i = 0; i < 21; ++i) {
        char name[32];
        std::snprintf(name, sizeof(name), "/race%02d.dip", i);
        DipFile df;
        std::string err;
        if (!df.loadFromFile(dataDir0 + name, &err)) { *errOut = err; return false; }
        SpeciesInfo si;
        SpeciesAbility fromHdr = abilityFromToken(df.abilityToken);
        SpeciesAbility fromIdx = static_cast<SpeciesAbility>(i);
        if (!df.abilityToken.empty()) {
            if (fromHdr == SpeciesAbility::Unknown) {
                *errOut = std::string(name) + ": unknown token " + df.abilityToken;
                return false;
            }
            if (fromHdr != fromIdx) {
                *errOut = std::string(name) + ": header token " + df.abilityToken +
                          " disagrees with position index " + abilityName(fromIdx);
                return false;
            }
            // Display names are NOT cross-checked on tokened headers: the
            // two sources disagree on spelling ([verified] race03.dip says
            // "KAMBUCHA", help.txt title says "Kambuchka"), so the token is
            // the identity; names stay display-only.
            si.ability = fromHdr;
        } else {
            // race02.dip (Orfa): header carries no token [verified]. Identify
            // via the help title == dip display name rule; the position index
            // must agree as a secondary check.
            std::string disp = df.displayName;
            if (disp.rfind("the ", 0) == 0) disp = disp.substr(4);
            auto t = titleToToken.find(disp);
            if (t == titleToToken.end()) {
                *errOut = std::string(name) + ": tokenless header, display name '" +
                          df.displayName + "' matches no help.txt ability title";
                return false;
            }
            SpeciesAbility byTitle = abilityFromToken(t->second);
            if (byTitle != fromIdx) {
                *errOut = std::string(name) + ": tokenless header resolved to " +
                          t->second + " but position says " + abilityName(fromIdx);
                return false;
            }
            si.ability = byTitle;
        }
        si.specnum = i;
        si.dipName = df.displayName;
        out->push_back(std::move(si));
    }
    return true;
}

}  // namespace ascend::game
