#pragma once
// Seeded campaign state + turn loop. Behaviour model and the verified/inferred
// split: docs/re/turnloop.md (cites end-*.txt vendor comments, planitem.txt
// rows, raceNN.dip). Combat is NOT implemented (OQ-010) — war is a recorded
// production penalty, stated in turnloop.md §5.
#include <random>
#include <string>
#include <vector>

#include "game/diplomacy.h"
#include "game/economy.h"
#include "game/mapgen.h"
#include "game/research.h"
#include "game/species.h"

namespace ascend::game {

// Owner ids: 0 = human player (player.dip), 1..kAiCount = AI races
// (raceNN.dip in roster order; windows.txt NUMCONTROLS 7 upper bound —
// docs/re/turnloop.md §2).
constexpr int kPlayer = 0;

enum class Victory { None, Control, Captured, Unification, Extinct, LastAlive };
const char* victoryName(Victory v);
// The end-*.txt file whose vendor comment names this condition
// (docs/re/turnloop.md §1). "" for None.
const char* victoryConditionFile(Victory v);

struct PlanetState {
    // MEASURED pop law (docs/re/income-law.md S6e, R1 threshold-chase capture
    // r1deep-20261007-224831): pop is the +0x42 counter (UPOP units),
    // colonization SETS it to 2; growth increments it +1 per counter wrap;
    // working population shown/used elsewhere = min(pop, popCapCap).
    double pop = 2;              // +0x42 analog, colonization :=2 [verified]
    int popCapCap = 25;          // +0x4a analog: scenario-template seeded per
                                 // planet (measured mid-game spread 13..28;
                                 // template table lift = open residue)
    int growthCounter = 0;       // +0x4e analog (PROS-side counter, S6c)
    std::vector<int> items;      // indices into the planitem table (ACTIVE slots)
    // BUILD QUEUE (income-law.md S8+t28): pending item id or -1 (original
    // +0x54 == 0xFF) and the industry accumulator (+0x50). The original pays
    // stored IND into +0x50 EVERY turn a pending item exists (tick law
    // 0x39005/0x3907b) and completes when acc >= COST; the selector
    // (FUN_0003f130) runs ONLY on planets with no pending item (caller law
    // 0x3ea: `cmp byte [edx+0x54],0xff; jne skip`).
    int pendingItem = -1;
    int buildAcc = 0;
    // Species-ability modifiers (docs/re/abilities.md §2): SA_MoreMaxPop adds
    // capBonus to the effective pop ceiling; SA_Cornucopia sets richPros
    // (= one Agriplot's PROS 2 [verified planitem.txt] on a "rich world",
    // the static.txt #56 planet-type name list).
    double capBonus = 0;
    double richPros = 0;
};

struct ShipInTransit {
    int owner = 0;
    int from = 0;
    int target = 0;
};

struct CampaignEvent {
    int turn = 0;
    std::string text;
};

struct CampaignConfig {
    unsigned seed = 1;
    // Free-for-all wars from turn 1 (arcade default; the diplomacy-gated war
    // entry is evaluated too but not required — docs/re/turnloop.md §5).
    bool freeForAll = true;
    int aiCount = 6;            // <= 6: NUMCONTROLS 7 total controls (turnloop.md §2)
    int starCount = 50;         // fresh campaigns measured 5/5 (r1-savestate 06p)
    double initialPop = 2;      // MEASURED: home + colonized planets both
                                // carry pop(+0x42)=2 in the chase capture
                                // while counters accumulate (income-law.md
                                // S6e); UPOP units, not the v1 logistic's
                                // 0..100 scale
    int popCap = 100;           // [inferred default; UPOP units undocumented]
    // Player species (specnum into docs/re/species.md): -1 = human, no SA_
    // (player.dip carries no ability token [verified]). >=0 grants that
    // species' ability to owner 0 like any AI race (docs/re/abilities.md).
    int playerSpecies = -1;
};

// Colony income channel stored value (MEASURED law, docs/re/income-law.md
// S6/t18b + t19; battery scripts/r1_income_channels.py). Exposed for the
// pinning test; semantics documented at campaign.cpp definition.
double colonyChannel(int acc, bool firstDoubleActive, bool compress);

class Campaign {
public:
    // All tables must be loaded and well-formed; errOut on failure. Home
    // stars are assigned deterministically: player first, then each AI takes
    // the star maximising min-distance to already-assigned homes (tie ->
    // lowest id). [documented default policy]
    Campaign(const CampaignConfig& cfg, Galaxy galaxy, const ResearchTree* tree,
             const std::vector<PlanetItem>& items, const std::vector<Gizmo>& gizmos,
             std::vector<DipFile> aiDip, std::string* errOut);
    // Same, with explicit species abilities: abilities[i] is the SA_ of the
    // race behind aiDip_[i] (owner i+1); size must equal aiDip.size() or be
    // empty (empty = derive from dip header tokens, which leaves race02/Orfa
    // unresolved — see game/species.cpp). Roster: docs/re/species.md;
    // effect mapping: docs/re/abilities.md.
    Campaign(const CampaignConfig& cfg, Galaxy galaxy, const ResearchTree* tree,
             const std::vector<PlanetItem>& items, const std::vector<Gizmo>& gizmos,
             std::vector<DipFile> aiDip, std::vector<SpeciesAbility> abilities,
             std::string* errOut);

    // Advance one full turn (income -> growth -> build -> research ->
    // expansion -> diplomacy -> victory). Idempotent per call; returns the
    // victory that ENDED the game (Victory::None while running). Once a
    // victory has occurred, further calls are no-ops returning it.
    Victory advance();

    int turn() const { return turn_; }
    bool over() const { return victory_ != Victory::None; }
    Victory victory() const { return victory_; }
    int starsOwned(int owner) const;
    int starOwner(int starId) const { return owner_[starId]; }
    int driveHopsFor(int owner) const;  // docs/re/ships.md §3 (launch range)
    int techsOwned(int owner) const;
    double resources(int owner) const;
    // --- read-only inspection (tests + UI; docs/re/abilities.md §5) ---
    SpeciesAbility abilityOf(int owner) const { return ability_[owner]; }
    int chargeFor(int owner) const { return charge_[owner]; }
    bool atWar(int a, int b) const { return war_[a * Nowner_ + b] != 0; }
    bool laneBlockedStar(int star) const { return laneBlock_[star] != 0; }
    bool invincibleStar(int star) const { return invincible_[star] != 0; }
    bool sapActiveFor(int owner) const { return sapActive_[owner] != 0; }
    double richProsFor(int star) const { return planets_[star].richPros; }
    // Completed queue items on a star (active-slot analogue; tests pin the
    // BUILD-QUEUE law income-law.md S8/S9).
    int builtItemCount(int star) const {
        return static_cast<int>(planets_[star].items.size());
    }
    int pendingItemFor(int star) const { return planets_[star].pendingItem; }
    int buildAccFor(int star) const { return planets_[star].buildAcc; }
    double popCapBonusFor(int star) const { return planets_[star].capBonus; }
    int fleetDamageFor(int owner) const { return fleetDamage_[owner]; }
    bool invadesAlwaysSucceeds(int owner) const {
        return ability_[owner] == SpeciesAbility::SuperMarines;
    }
    int attackScoreFor(int owner) const { return attackScore(owner); }
    int defenseScoreFor(int owner, int star) const { return defenseScore(owner, star); }
    const std::vector<CampaignEvent>& events() const { return events_; }
    const Galaxy& galaxy() const { return galaxy_; }
    int playerScorePct() const;  // stars-owned share, static.txt '%'-template (§1)
    std::string traceLine() const;  // one-line status for playthrough logs

private:
    void pickHomeStars();
    void incomeAndGrow();
    void buildPhase();
    void researchPhase();
    void expansionPhase();
    void combatPhase();
    void abilityPhase();
    void diplomacyPhase();
    int attackScore(int owner) const;
    int defenseScore(int owner, int star) const;
    void setWar(int a, int b, bool on);
    Victory checkVictory() const;
    int itemId(const std::string& name) const;  // by NAME (verified rows), not index
    // Species-ability hooks (docs/re/abilities.md §2-§3).
    bool lanePassable(int owner, int target) const;  // SA_BlockStarLanes
    double popCapFor(int star) const;                // cfg cap + SA_MoreMaxPop bonus
    // Stored-channel helpers (income-law.md S6 recalc): compressed IND /
    // raw RES of one star, Hyperpower(12)/Internet(14) first-occurrence
    // doubling per S6. needClassFor: FUN_0003fec4 need-class law (S9 t28).
    int storedIndFor(int star) const;
    int storedResFor(int star) const;
    int storedProsFor(int star) const;
    int needClassFor(int star) const;

    CampaignConfig cfg_;
    Galaxy galaxy_;
    const ResearchTree* tree_;
    const std::vector<PlanetItem>* items_;
    const std::vector<Gizmo>* gizmos_ = nullptr;  // combat strength inputs (OQ-010)
    std::vector<DipFile> aiDip_;  // aiDip_[i] drives owner i+1
    std::mt19937 rng_;

    std::vector<int> owner_;                   // per star
    std::vector<PlanetState> planets_;         // per star (only owned stars use it)
    std::vector<std::vector<bool>> ownedTech;  // per owner, indexed by Tech id
    std::vector<double> res;                   // research stockpile per owner
    std::vector<double> ind_;                  // per-turn industry budget (buildPhase)
    std::vector<int> queuedTech;               // per owner, Tech id or -1
    std::vector<double> techProgress;          // per owner
    std::vector<ShipInTransit> fleet_;
    std::vector<DipPolicyState> dipState_;     // per AI owner
    // War table (symmetric bits, owner x owner) + capture fortify counter
    // per star. Model + constants: docs/re/turnloop.md §5 [inferred].
    std::vector<int> homeStar_;                   // per owner, fixed pickHomeStars id
    std::vector<char> war_;
    std::vector<int> fortify_;
    // Species abilities (docs/re/abilities.md): ability_[o] = owner o's SA_
    // (Unknown = none); charge_[o] counts down per abilityPhase, firing at 0
    // and resetting to abilityChargeTurns(). Transient per-activation flags:
    // doublePower_[o] (attack x2 this combat), invincible_[s] (star shield),
    // laneBlock_[s] (star whose lanes are blocked this combat).
    std::vector<SpeciesAbility> ability_;
    std::vector<int> charge_;
    std::vector<char> doublePower_, sapActive_, invincible_, laneBlock_;
    std::vector<int> fleetDamage_;  // per owner: accumulated hull damage (SA_DoubleHull / SA_HealShips / SA_SapAlienPower)
    int Nowner_ = 0;
    int turn_ = 0;
    Victory victory_ = Victory::None;
    std::vector<CampaignEvent> events_;
};

}  // namespace ascend::game
