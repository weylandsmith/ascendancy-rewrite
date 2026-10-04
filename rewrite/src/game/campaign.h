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

namespace ascend::game {

// Owner ids: 0 = human player (player.dip), 1..kAiCount = AI races
// (raceNN.dip in roster order; windows.txt NUMCONTROLS 7 upper bound —
// docs/re/turnloop.md §2).
constexpr int kPlayer = 0;

enum class Victory { None, Control, Extinct, LastAlive };
const char* victoryName(Victory v);
// The end-*.txt file whose vendor comment names this condition
// (docs/re/turnloop.md §1). "" for None.
const char* victoryConditionFile(Victory v);

struct PlanetState {
    double pop = 0;              // growth model: turnloop.md §3 [inferred]
    std::vector<int> items;      // indices into the planitem table
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
    int starCount = 75;         // mapgen snapshot default (mapgen.md §3)
    double initialPop = 20;     // [inferred default, turnloop.md §3]
    int popCap = 100;           // [inferred default; UPOP units undocumented]
};

class Campaign {
public:
    // All tables must be loaded and well-formed; errOut on failure. Home
    // stars are assigned deterministically: player first, then each AI takes
    // the star maximising min-distance to already-assigned homes (tie ->
    // lowest id). [documented default policy]
    Campaign(const CampaignConfig& cfg, Galaxy galaxy, const ResearchTree* tree,
             const std::vector<PlanetItem>& items, const std::vector<Gizmo>& gizmos,
             std::vector<DipFile> aiDip, std::string* errOut);

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
    int techsOwned(int owner) const;
    double resources(int owner) const;
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
    void diplomacyPhase();
    int attackScore(int owner) const;
    int defenseScore(int owner, int star) const;
    void setWar(int a, int b, bool on);
    Victory checkVictory() const;
    int itemId(const std::string& name) const;  // by NAME (verified rows), not index

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
    std::vector<char> war_;
    std::vector<int> fortify_;
    int Nowner_ = 0;
    int turn_ = 0;
    Victory victory_ = Victory::None;
    std::vector<CampaignEvent> events_;
};

}  // namespace ascend::game
