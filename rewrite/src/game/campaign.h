#pragma once
// Seeded campaign state + turn loop. Behaviour model and the verified/inferred
// split: docs/re/turnloop.md (cites end-*.txt vendor comments, planitem.txt
// rows, raceNN.dip). Combat laws t89-upgraded to the cited original
// (docs/re/combat.md S2d..S2i: deterministic volley, two-layer clamped
// absorb); aggregate-model caveats in S2i.
#include <algorithm>
#include <memory>
#include <random>
#include <string>
#include <vector>

#include "game/diplomacy.h"
#include "game/economy.h"
#include "game/mapgen.h"
#include "game/research.h"
#include "game/species.h"

namespace ascend::game {

// t365 ENGINE FLIP: the per-ship fleet engine bridge (combatPhase drives it;
// docs/re/_wip_t365.md, ruling D2=(b)). Incomplete here on purpose — the
// shipsim/shipsave headers stay out of the campaign's public surface.
class CampaignFleetBridge;

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
    // working population shown/used elsewhere = min(pop, storedCapFor()).
    double pop = 2;              // +0x42 analog, colonization :=2 [verified]
    // POP-CAP SEED LAW (income-law.md S10 t29+t33): world-gen @0x37f84..0x37f9e
    // writes capBase = NONBARRENCOUNT/3 + 5 into +0x55 AND +0x4a; recalc
    // then keeps +0x4a = clamp(0..100, capBase + sum MPOP(active slots)) —
    // Colony Base included; flags&4 rows all have mpop=0 so the skip is a
    // no-op (72066/72066 exact, t33 corrected pointer array). capBase is
    // seeded per star at Campaign construction (inline draw law, campaign.cpp ctor).
    int capBase = 0;             // +0x55 analog
    int surfaceCells = 23;       // +0x18 analog (seeded; income-law.md S10)
    // CELL CLASSES +0x00-byte analog per slot (income-law.md T36): the
    // 0x37d80 draw loop writes one class byte per slot — surface slots
    // [0,surfaceCells) from the row chain (barren 0 overrides 2; rng 0..
    // 32767), orbital ring [surfaceCells,+10) forced 1 WITHOUT drawing.
    std::vector<int> cellClasses;
    int growthBoom = 0;          // +0x66 bit0 analog: Lush Growth Bomb fired
    int growthCounter = 0;       // +0x4e analog (PROS-side counter, S6c)
    // t201 EMERGENCY-CHAIN state (FUN_0003fc4c, docs/re/ai-dossier.md S10):
    // +0x67 analog — day stamp read by the Surface-Mega-Shield chain
    // ((day - stamp)/period > shields). The original's per-turn stamp WRITE
    // site was NOT found statically (census r201, honest negative); the
    // rewrite stamps on a chain-C purchase [documented default].
    int emergencyStamp = 0;
    // Chain-A consumed flag: the original arms +0x66 bit1 at world-gen
    // (0x37f7b, same branch that rocks a cell) and chain A CLEARS it when
    // the Xeno dig buy succeeds (0x3fc78). Rewrite arms on the observable
    // trace cellClasses[0] rock [documented default].
    int digQueuedOrDone = 0;
    std::vector<int> items;      // indices into the planitem table (ACTIVE slots)
    // EXPLICIT cell assignment parallel to `items` (surface: index into the
    // surface cells; orbital: surfaceCells + ring index). HOME CB cell:
    // picker-uniform over non-rock surface cells, barren included (t42;
    // picker FUN_0003875c uniform-among-legal-empty, census
    // r1_cb_rank_final.py — the older t40 rank-2..70 envelope was a
    // nonbarren-filter artifact). BUILT-ITEM cell: picker-uniform among
    // legal non-rock EMPTY cells ADJACENT to an active item (rule G,
    // income-law.md S13, census scripts/r1_built_cell_law.py: 0/362
    // final-state violations). Orbital ring slots keep lowest-free
    // [documented default — rule G is surface-only (slot < +0x18), the
    // original's orbital assignment path is unrecovered]. Cell class drives
    // channel bonuses (class-2 home IND=2 x14, class-3 home PROS=2 x6,
    // income-law.md T40).
    std::vector<int> itemCells;
    // BUILD QUEUE (income-law.md S8+t28): pending item id or -1 (original
    // +0x54 == 0xFF) and the industry accumulator (+0x50). The original pays
    // stored IND into +0x50 EVERY turn a pending item exists (tick law
    // 0x39005/0x3907b) and completes when acc >= COST; the selector
    // (FUN_0003f130) runs ONLY on planets with no pending item (caller law
    // 0x3ea: `cmp byte [edx+0x54],0xff; jne skip`).
    int pendingItem = -1;
    int buildAcc = 0;
    // TERRAIN WEIGHT-ROW INDEX (+0x16 analog, income-law.md S10 world-gen):
    // the ctor's `rng % 11` draw (0x23a97/aa8), stored t281 because the cited
    // SA_Cornucopia body 0x43de4 SKIPS planets where WORD[rec+0x16]==10.
    // MEASURED (scripts/r1_t281_w16_census.py, two lineages): uniform over
    // 0..10 across owned AND unowned records — NOT a homeworld marker (the
    // t105 §3 [inferred] reading is REFUTED). Row 10 == preset [0,33,34,33],
    // the zero-barren template.
    int terrainRow = 0;
    // (SA_Cornucopia's old `richPros` field is DELETED t281: the cited body
    //  mutates SURFACE CELL CLASSES (repaint {0,1} -> {2,3,4}), whose income
    //  arrives through the T35 per-cell class bonus in channelAccFor — see
    //  abilityPhase and docs/re/_wip_t281.md.)
    // (SA_MoreMaxPop's old `capBonus` field is DELETED t280: the cited body
    // 0x4402a mutates the PRE-CLAMP seed word capBase (+0x55) by +2, not a
    // post-clamp bonus — see abilityPhase and income-law.md S10.)
    // SELECTED-ABILITY byte (+0x54 analogue; income-law.md S14 t45). Full
    // image writer census (scripts/r1_0x54_writer_sweep.py): queue writes
    // the pending item id, completion/demolish clear to 0xFF (-1 here);
    // the ONLY source of a governor value 33/34/35 is the activator
    // mode-3 cell SELECT @0x38b26 over a special item (Endless Party /
    // Scientist Takeover / Automation, runtime-table IDs measured 33/34/35).
    // Corpus: 0/2810 owned records hold 33/34/35 (scripts/r1_governor_
    // census.py, 484 saves) — default -1 mirrors the measured state.
    int governor = -1;
};

struct ShipInTransit {
    // GAP ROW 16 BOUNDARY (accepted t256c, docs/re/ai-dossier.md S11): this
    // transit-only struct is the rewrite's ENTIRE ship state. The cited
    // per-ship order laws (ai-dossier §5: kind +0x58, stickiness {1,2,5},
    // congregation, 0x220f2 retreat-downgrade; t179 P1 power tie-break,
    // t179 P3 invasion-module carrier) are NOT wireable here and were
    // deliberately NOT stubbed — adding guessed per-ship state would create
    // behaviour the corpus never witnessed (AI kind-2: 0 obs; ACT=2: 17 obs
    // over 1.8M slot-obs, scripts/r256c_shipstate.py). Implement them only
    // inside a real per-ship build (OQ-019), verbatim from §5.
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
    // (popCap field retired t29 — pop caps are per-planet seeded values,
    // income-law.md S10; see PlanetState::capBase / storedCapFor.)
    // Player species (specnum into docs/re/species.md): -1 = human, no SA_
    // (player.dip carries no ability token [verified]). >=0 grants that
    // species' ability to owner 0 like any AI race (docs/re/abilities.md).
    int playerSpecies = -1;
    // t294 (OQ-016 residue 3): terrain weight rows + surface grid + pop-growth
    // scalar. The ORIGINAL loads these from planitem.txt at scenario init
    // (FUN_00037fc0; income-law.md S10 t294 block) — main.cpp fills this via
    // loadTerrainTables(); the default is the measured vendor table (file ==
    // banked runtime == live RAM), NOT a guess.
    TerrainTables terrain = vendorTerrainTables();
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
    // t365: unique_ptr member (fleetSim_) — out-of-line dtor so the
    // incomplete CampaignFleetBridge type is only destroyed in campaign.cpp;
    // the move ctor is DEFAULTED out-of-line (a user-declared dtor deletes
    // the implicit one, and the test harness returns campaigns by value —
    // makeCampaign; copy stays deleted, which is correct for campaign state).
    ~Campaign();
    Campaign(Campaign&&);
    int starsOwned(int owner) const;
    int starOwner(int starId) const { return owner_[starId]; }
    // t204 pin surface (established harness idiom — planetAt const_cast,
    // freeTechGrantFor PUBLIC): force a star's owner for wiring an attack
    // scenario. Does NOT seed pop/CB (the engagement math only needs owner).
    void setStarOwnerForTest(int starId, int owner) { owner_[starId] = owner; }
    // t284 pin surfaces for the CONTROLLED-SYSTEMS producer (same pattern as
    // setWarForTest): grant the viewer's SELECT-mask bit on one star (the
    // starSelVis_/+0x17 gate), install an explicit transit list (the contest
    // gate reads from==lane.a&&target==lane.b or the reverse), and run the
    // producer on demand.
    void setStarSelVisForTest(int star, int viewer) {
        starSelVis_[star] |= static_cast<char>(viewerMaskFor(viewer));
    }
    void setFleetForTest(std::vector<ShipInTransit> f) { fleet_ = std::move(f); }
    void recomputeScoreStarsForTest() { recomputeScoreStars(); }
    // t291 PIN SURFACE: the end-ctrl comparator arm of checkVictory, callable
    // directly after staging scoreStars_/owner_ (the vendor evaluator is a pure
    // read of DAT_482fb + DAT_16143 at the end-turn pass; a direct call is the
    // same read without waiting ~1300 turns of dynamics).
    Victory checkVictoryForTest() const { return checkVictory(); }
    // t291 PIN SURFACE: stage V (the DAT_482fb analog) to an EXACT value so the
    // comparator boundary floor(2T/3) / floor(2T/3)+1 is testable without
    // engineering a flood of that precise size (thin setter, same pattern as
    // setIndustryForTest).
    void setScoreStarsForTest(int v) { scoreStars_ = v; }
    // t204 pin surface: scenario peace/war toggle (pins "peace never clears
    // the attacked mark" — permanence is the measured property, so the pin
    // must be able to make peace). Thin wrapper over the private setWar.
    void setWarForTest(int a, int b, bool on) { setWar(a, b, on); }
    // t280: override one owner's SA_ after construction (CauseWar boundary
    // pin needs a deterministic AI-side ability without racing the roster
    // draw; same pattern as setWarForTest/setAttitudeForTest).
    void setAbilityForTest(int owner, SpeciesAbility a) { ability_[owner] = a; }
    // t208 pin surface: scenario industry stockpile set (mirror of ind_,
    // §3 stockpile semantics). Exists so an e2e pin can clear the
    // SuperMarines invasion gate (ind_[a] >= ship cost, campaign.cpp:1895)
    // DETERMINISTICALLY instead of depending on the turn-1 income accrual.
    // Header-inline scenario hook, NO production call site: zero semantic
    // delta (t206 no-re-run rule).
    void setIndustryForTest(int owner, double v) { ind_[owner] = v; }
    int driveHopsFor(int owner) const;  // docs/re/ships.md §3 (launch range)
    int techsOwned(int owner) const;
    double resources(int owner) const;

    // t365 PIN SURFACES (engine flip): the per-ship engine the combat phase
    // drives, and its engagement census (seed-comparison evidence, ruling
    // D2 "removed after seeds agree" — test_campaign_fleet_t365).
    const class CampaignFleetBridge* fleetSim() const;
    // --- read-only inspection (tests + UI; docs/re/abilities.md §5) ---
    SpeciesAbility abilityOf(int owner) const { return ability_[owner]; }
    int chargeFor(int owner) const { return charge_[owner]; }
    bool atWar(int a, int b) const { return war_[a * Nowner_ + b] != 0; }
    bool laneBlockedStar(int star) const { return laneBlock_[star] != 0; }
    bool invincibleStar(int star) const { return invincible_[star] != 0; }
    bool sapActiveFor(int owner) const { return sapActive_[owner] != 0; }
    // Full planet state for law pin-tests (cellClasses/capBase, T36).
    const PlanetState& planetAt(int star) const { return planets_[star]; }
    // Completed queue items on a star (active-slot analogue; tests pin the
    // BUILD-QUEUE law income-law.md S8/S9).
    int builtItemCount(int star) const {
        return static_cast<int>(planets_[star].items.size());
    }
    int pendingItemFor(int star) const { return planets_[star].pendingItem; }
    int buildAccFor(int star) const { return planets_[star].buildAcc; }
    // Public +0x4a analog for tests/UI (income-law.md S10 seed law).
    int popCapAt(int star) const { return storedCapFor(star); }
    // Per-planet channel words +0x44/+0x46/+0x48 incl. the t45 governor
    // branch (the original's recalc produces exactly these three words;
    // the city screen reads them). Public for law-pin tests, precedent
    // drawCbCell.
    struct ChannelWords { int ind, res, pros; };
    ChannelWords channelWordsFor(int star) const {
        return {storedIndFor(star), storedResFor(star), storedProsFor(star)};
    }
    // Selected-ability/governor byte (+0x54 analogue, income-law.md S14
    // t45): -1 (0xFF) unless the activator mode-3 SELECT put a special
    // item id (33/34/35) there. Corpus default: never set (0/2810).
    int governorFor(int star) const { return planets_[star].governor; }
    // RAW doubled IND accumulator (pre-compression) = the value the
    // recalc governor branch shifts >>2 (FUN_00038ba4 @0x38df6 loads
    // [ESP+0x28] AFTER the Hyperpower doubler block @0x38d3f..0x38d76).
    int rawIndAccFor(int star) const {
        const ChannelAcc a = channelAccFor(star);
        return a.ind + (a.dblI ? a.ind >> 1 : 0);
    }
    // +0x4c USED-POP analog. LAW UPGRADED t202b (docs/re/_wip_t202.md S11,
    // scripts/r202d_usedpop_models.py RC=0 over 2900 corpus planet records):
    // +0x4c = SUM OF ITEM UPOP over ALL SLOTTED items, skipping item 23
    // (Ship), item-table flags&0x40 (20 Outpost, 21 Transport Tubes) and
    // slot-flags bit1 — model M4 exact on 2760/2900 (95.2%); the 140-row
    // residual is the M3 shape (active UPOP + 1) i.e. the Automation bonus
    // below. The t199/t45 reading "pending-item UPOP only" is SUPERSEDED:
    // the pending term measures 0 on 2900/2900 records (the autosave ring
    // never catches pending != 0xFFFF -> INERT in the corpus), while mature
    // planets read 51/61 where the inactive-only sum predicts 0/1.
    // The governor AUTOMATION bonus is kept: branch @0x38e16 of
    // FUN_00038ba4 adds dword [0x743b9]>>0x18 = row-35 UPOP (item-table base
    // 0x73e40 + 35*0x28 = 0x743b8, dword +1..+4, SAR >>0x18 lands on UPOP;
    // runtime-measured 1 in 32/32 saves). Governor is -1 corpus-wide
    // (scripts/r1_governor_census.py), so the bonus stays inert on measured
    // state; pinned by campaign_governor_law_t45.
    // The rewrite stores ACTIVE items only, so the slot-flags&2 skip is a
    // no-op by construction (same mapping as shieldThreatFor, t201).
    int usedPopFor(int star) const {
        const PlanetState& ps = planets_[star];
        int u = 0;
        for (int it : ps.items) {
            if (it == 23) continue;                      // Ship excluded
            if ((*items_)[it].flags & 0x40) continue;    // Outpost / Tubes
            u += (*items_)[it].upop;
        }
        if (ps.governor == 35) u += (*items_)[35].upop;  // Automation UPOP
        return u;
    }
    // ------------------------------------------------------------------
    // t202b DEMOLISH CHANNEL pickers — the two victim scans inside the AI
    // build evaluator FUN_0003f130 (docs/re/_wip_t202.md S1/S3/S5/S13;
    // verbatim disasm work/ai_selector_disasm.txt 0x3f178..0x3f209 and
    // 0x3f354..0x3f418). `items`/`mpop`/`upop`/`requires` are parallel
    // arrays in SLOT order (the original walks the slot pointer +4i); the
    // return value is the SLOT index to demolish, or -1 for "no candidate".
    // OVER-CAP VICTIM 0x3f1bb..0x3f1c7: skip item 5 (Colony Base, 0x3f1a8),
    // skip any item with MPOP != 0, keep the STRICT largest UPOP (best init
    // 0 @0x3f17c -> UPOP == 0 never wins), ties keep the FIRST cell.
    // t28's "largest MPOP" summary had the byte identity inverted: byte+3 is
    // MPOP and is the SKIP test; byte+4 = [ebx+1] sar 0x18 is UPOP and is the
    // scored operand.
    static int overCapDemolishPick(const std::vector<int>& items,
                                   const std::vector<int>& mpop,
                                   const std::vector<int>& upop) {
        int best = -1, bestU = 0;  // 0x3f17c xor ebp,ebp
        for (size_t i = 0; i < items.size(); ++i) {
            if (items[i] < 0 || items[i] == 5) continue;  // empty / Colony Base
            if (mpop[i] != 0) continue;                   // 0x3f1bb
            if (upop[i] > bestU) { bestU = upop[i]; best = static_cast<int>(i); }
        }
        return best;
    }
    // MIN-REQUIRES SWEEP VICTIM 0x3f354..0x3f3d5: NO item-5 skip (a Colony
    // Base CAN be swept); skip items whose MPOP >= margin, where margin =
    // cap - pop, the FREE-cell figure ([esp+0xcc]); keep the STRICT smallest
    // REQUIRES, ties keep the FIRST cell. The 0x1869f init sentinel never
    // prunes (any u8 REQUIRES < 99999), so a 0xFF-requires item PARTICIPATES
    // and wins whenever it is the first minimal candidate — t28's "sentinel
    // never binds" stands with this corrected reason.
    static int minRequiresDemolishPick(const std::vector<int>& items,
                                       const std::vector<int>& mpop,
                                       const std::vector<int>& requires,
                                       int margin) {
        int best = -1, bestR = 99999;  // 0x3f354 mov ecx,0x1869f
        for (size_t i = 0; i < items.size(); ++i) {
            if (items[i] < 0) continue;
            if (mpop[i] >= margin) continue;
            if (requires[i] < bestR) { bestR = requires[i]; best = static_cast<int>(i); }
        }
        return best;
    }
    // POPULATION BAND LAW (t199, docs/re/planets-ui.md S4 [verified
    // 0x3ce39..0x3cef8]): the PLPOP grid paints one shape per slot
    // i = 0..cap-1 (ten per row, +0x0a column step) with
    //   SEL(i) = 1 + [i >= used] + [i >= pop]
    // so with the corpus law used <= pop <= cap (2900/2900 planet records,
    // r1_t198 census) the three bands are exactly the player's testimony:
    // SEL 1 = working pop ("busy"), SEL 2 = pop not working ("free"),
    // SEL 3 = empty slot. out has cap entries (values 1..3; above the corpus
    // law the formula still matches the vendor: both increments fire, giving
    // 3). Pure function of the three words so the law is pinned without the
    // table tables; pop is the +0x42 double truncated to int exactly as the
    // original's u16 word holds an integer count.
    static void popBands(int used, int pop, int cap, std::vector<int>& out) {
        out.assign(cap < 0 ? 0 : cap, 0);
        for (int i = 0; i < static_cast<int>(out.size()); ++i)
            out[i] = 1 + (i >= used ? 1 : 0) + (i >= pop ? 1 : 0);
    }
    std::vector<int> popBandsFor(int star) const {
        std::vector<int> v;
        popBands(usedPopFor(star), static_cast<int>(planets_[star].pop),
                 storedCapFor(star), v);
        return v;
    }
    // ------------------------------------------------------------------
    // t201 EMERGENCY CHAIN — FUN_0003fc4c (docs/re/ai-dossier.md S10,
    // evidence work/t201_fc4c.txt + docs/re/_wip_t201.md S1d/S1f).
    // Pure law for the pin; gates carry per-item legal/absent facts.
    // Returns the FORCED item id, or -1 (original "none forced" -> the
    // selector's normal pick continues; 0x3f4da cmp eax,-1; je end).
    struct EmergencyGate {
        bool digArmed = false;                            // +0x66 bit1
        bool digLegal = false, digAbsent = false;         // item 38
        bool shipyard = false;                            // item 22 PRESENT
        bool shieldLegal = false, shieldPresent = false;  // item 18
        bool megaLegal = false;                           // item 19: NO
                                                          // absence check
        bool cloakLegal = false, cloakAbsent = false;     // item 11
        // Chain-E fallback template MEASURED (live pool bytes at the
        // relocated 0x67b8 immediate): items {12,13,14,15,37}.
        bool templateLegal[5] = {false, false, false, false, false};
        bool templateAbsent[5] = {true, true, true, true, true};
    };
    static int emergencyChainPick(int ind, int pros, int freeCells,
                                  int shields, int owner, unsigned deltaDays,
                                  unsigned period, const EmergencyGate& g,
                                  int rngPct);
    static unsigned emergencyPeriodFor(int hop) {  // 0x3fd73..0x3fd92
        return hop == 0 ? 200u : hop == 1 ? 225u : hop < 4 ? 300u : 400u;
    }
    // Derived threat counters (recalc FUN_00038ba4 law, verified
    // 2880/2900 + 2900/2900 this session): ACTIVE slots whose item file
    // FLAGS word has bit 0x8 (shields 18/19/26/27) / bit 0x4 (orbital
    // defences 17/28/29/30).
    int shieldThreatFor(int star) const;   // +0x59 analog
    int orbitalThreatFor(int star) const;  // +0x58 analog
    int fleetDamageFor(int owner) const { return fleetDamage_[owner]; }
    bool invadesAlwaysSucceeds(int owner) const {
        return ability_[owner] == SpeciesAbility::SuperMarines;
    }
    int attackScoreFor(int owner) const { return attackScore(owner); }
    int defenseScoreFor(int owner, int star) const { return defenseScore(owner, star); }
    // t365: owned-pop operand helper (aggregate oracle input).
    double ownedPopFor(int owner) const;
    // t89 (OQ-010): aggregate shield-charge analogue, shield absorb of
    // hit-path 0x4b740 (docs/re/combat.md S2d/S2h).
    int shieldChargesFor(int owner) const;
    // Set every research row for one owner (law-pinning + scenario hook).
    void setAllTechs(int owner, bool owned);
    // t203 pin surface: total table rows, queued-target readback, single-row
    // owned readback (mirror of ownedTech / queuedTech; docs/re/_wip_t203.md).
    int techCountTotal() const { return static_cast<int>(tree_->all().size()); }
    bool isTechQueuedFor(int owner, int row) const { return queuedTech[owner] == row; }
    bool techRowOwnedFor(int owner, int row) const { return ownedTech[owner][row]; }
    void setQueuedTechFor(int owner, int row) { queuedTech[owner] = row; }
    // TWO-LAYER CLAMPED ABSORB SPLIT [verified 0x4b7c4..0x4b7d1 + apply
    // 0x4b87a..0x4b890, S2h-audited]: the shield layer absorbs
    // min(volley, charges) and ONLY the remainder spills to the hull layer.
    // Exposed as a pure function so the law is pinned by test.
    static void absorbSplit(int volley, int charges, int& absorb, int& spill) {
        absorb = std::min(volley, charges);
        spill = volley - absorb;
    }
    // (t256's static hatredClamp — the SA_Hatred/SA_CauseWar ceiling mirror —
    // is RETIRED t280: the raw re-read of 0x440b5 (see abilityPhase case
    // CauseWar + _wip_t280 S2) shows the vendor clamps att[k->x] (enemy k
    // toward third party x) at x's OWN DECLARE_WAR, not att[x->self] at r's;
    // every cell of the corrected law is AI->AI = state the rewrite does not
    // carry, so there is nothing pure-form to pin. campaign.cpp case CauseWar
    // is announce-only.)
    // t93 (OQ-016): AI RESEARCH PICK tier decision — pure form of the
    // sentinel + preferred tiers of FUN_00040018 (0x400b3..0x40134, body
    // 0x40018..0x40175, disassembly re-verified t93; docs/re/aicode.md
    // §3c/§3d). 'cand' = row-order, legality-filtered, cap-32 candidates
    // (0x4002e..0x40083); 'sentinelHit' = the race's rng%100 < 45 roll
    // succeeded (flag DAT_00074902, live-measured 0x0f = every shipped
    // scenario AI, t92; the rewrite applies it to all AI owners as the
    // shipped-scenario mirror). Preferred membership on the live 66-row
    // table is {1,47} (§3c membership math: no other raw entry can equal
    // a row index). Returns the preferred row (first candidate that is a
    // member wins, 0x40129..0x4012d), or -1 = no preferred hit — sentinel
    // skip (chosen=-2 exits the scan at guard 0x400fb) OR plain miss — in
    // which case the caller runs the uniform fallback 0x4013f. Pinned by
    // TEST(campaign_research_picker_law_oq016).
    static int aiResearchPreferred(const std::vector<int>& cand, bool sentinelHit) {
        if (sentinelHit) return -1;
        for (int t : cand)
            if (t == 1 || t == 47) return t;
        return -1;
    }
    const std::vector<CampaignEvent>& events() const { return events_; }
    const Galaxy& galaxy() const { return galaxy_; }
    // --- OQ-026 PER-EMPIRE VISIBILITY LAYER (docs/re/ships.md S23 L5/L6/L9) ---
    // The original stores a per-empire bitmask on every lane record
    // (lane rec+0x20, bit e = 1<<empire-index, S23 L5 t191) and a twin pair
    // on every star (obj +0x16 lane-follow / +0x17 select, S23 L9 t194).
    // The UI CONSUMER is the cosmos list builder FUN_00028fc0: lane i gets a
    // display entry IFF rec+0x20 & viewer_mask != 0 (no entry => never drawn
    // by painter FUN_000284bc, never clickable); stars are ALWAYS listed,
    // but star-click FUN_00028e70 gates select on star+0x17 & mask and
    // lane-follow on star+0x16 & mask. Grants are OR-only (no lane-pool-scoped
    // clear exists => reveal is sticky, S23 L5).
    static int viewerMaskFor(int viewer) {
        // FUN_00021a84 law verbatim (S23 L9): mask = idx==0xff ? 0xff :
        // 1<<(idx&0x1f). 255 = spectator/reveal-everything viewer.
        return viewer == 0xff ? 0xff : (1 << (viewer & 0x1f));
    }
    // Filter law 0x2914e analog: would the cosmos builder admit lane `lane`
    // for this viewer?
    bool laneVisibleTo(int lane, int viewer) const;
    // Star-click FUN_00028e70 analogs (star +0x17 / +0x16 & viewer mask).
    bool starSelectableBy(int star, int viewer) const;
    bool starLaneFollowableBy(int star, int viewer) const;
    // Mid-game witness analog (t193 measured 49/58 admitted for the player).
    int visibleLaneCountFor(int viewer) const;
    // Display-list builders: lanes filtered by the mask (pool order, the
    // builder's iteration order); stars UNCONDITIONALLY (S23 L9 honest
    // negative — the builder kind-0 adds stars with no mask test).
    std::vector<int> cosmosLanesFor(int viewer) const;
    std::vector<int> cosmosStarsFor(int viewer) const;
    // FUN_00046354 shape (S23 L6 t192): mutual lane-vision share between
    // empires a and b. N = vis-rng % (allied ? 6 : 3) + 1 grants PER CALL
    // (ALLIANCE doubles the budget). Receive leg: a receives every lane b
    // sees and a doesn't, up to N; bidirectional adds the mirrored lend leg.
    // Fires BIDIRECTIONAL at alliance formation (cited site 0x45778) and
    // RECEIVE-ONLY in the per-race contact loop (cited shape 0x55f6e).
    // Returns the number of lane grants made (event text).
    int shareLaneVision(int a, int b, bool bidirectional, bool allied);
    // Star twin FUN_00046524 (S23 L6: "same shape", modulus 4 if state==3
    // else 2). Each mask byte (+0x16/+0x17 -> starLaneVis_/starSelVis_) is
    // shared INDEPENDENTLY [inferred: t193 census shows the two bytes with
    // different distributions]; OR-only. Pairing this twin to both share
    // sites is [unverified] (the twin's callers are not in the banked set).
    void shareStarVision(int a, int b, bool bidirectional, bool allied);
    int playerScorePct() const;  // TRUNC(100*scoreStars()/T), score.md S2 law
    // t284 CONTROLLED-SYSTEMS LAW (the DAT_000482fb analog; producer witnessed
    // t283, predicate decoded + corpus-replayed t284 — docs/re/_wip_t284.md):
    // the vendor's "STARS CONTROLLED %d" is NOT owned-star count. It is a
    // per-end-turn-pass FLOOD from the player's home star over the lane graph:
    //   V = 0; if home star still carries player presence: V = 1 and flood.
    // A lane admits its far star iff (a) far star visible to the player
    // (star +0x17 analog -> starSelVis_), (b) far star's presence mask holds no
    // race that is neither the player nor allied (star +0x14|+0x15 analog ->
    // owner_ proxy, measured 48/50 exact vs the planet-record owner set), and
    // (c) NO non-allied ship holds an order INTO the lane (ship +0x59 == lane
    // pointer, measured: kind-5 lane orders carry lane-pool pointers). A
    // failing lane PRUNES its whole subtree. Cadence: 0 at load, recomputed
    // ONLY in the end-of-turn pass (FUN_00024f24 tail; fires +3.1-3.3 s after
    // NEXTTURN, quiet 90 s zero). Corpus replay: 295/409 EXACT, all 114
    // misses are pre-first-end-turn slots (stored 0), lane-mark footprint
    // 409/409 (scripts/r284_vreplay.py).
    int scoreStars() const { return scoreStars_; }
    // t204 DIPLOMACY-ON-ATTACK readbacks (gap map row 13; law in
    // diplomacy.h::applyAttackDipCost), t205-corrected INDEX IDENTITY:
    // [0x48304] is a BYTE ARRAY indexed by STAR INDEX, not one global byte —
    // 0x43afa writes byte[0x48304 + (dword[edi+2]>>16)] and t205 measured
    // dword[0x13bc5+0x60k+2]>>16 == k for every row k<50 (self-handle law;
    // the EDX arg is a STAR record, cf. 0x4b806/0x4b82c building it from the
    // ship's +0x59 star pointer). Byte value = mask of VICTIM races fired at
    // at that star while NOT at war (the -1 return path). PERMANENT for the
    // attack channel (no clear site for bits 1<<r exists; bit 0 is a SEPARATE
    // channel — a call-scoped contact-notice latch whose only clear is the
    // 0x24dd0 all-stars sweep, t206). CONSUMER LAW (t206, diplomacy.md S18):
    // victim bits feed ONLY unit-order/display (status |=0x20 at 0x41659,
    // eligibility scan result at 0x42be8) — no diplo-value or AI feed — so
    // this mirror staying unconsumed in the rewrite is FAITHFUL.
    // attackedMarks() OR-reduces the array (the t204 pin surface);
    // attackedAt(star) reads one cell.
    unsigned char attackedMarks() const {
        unsigned char m = 0;
        for (size_t i = 0; i < attacked_.size(); ++i) m |= attacked_[i];
        return m;
    }
    unsigned char attackedAt(int star) const {
        return star >= 0 && star < static_cast<int>(attacked_.size()) ? attacked_[star] : 0;
    }
    const DipPolicyState& dipStateAt(int ai) const { return dipState_[ai]; }
    // t256 pin surface (species_cause_war_hatred_ceiling_t256): set one AI's
    // attitude baseline so the SA_Hatred ceiling law is testable without
    // waiting for the oscillation model to move it.
    void setAttitudeForTest(int ai, int v) { dipState_[ai].attitude = v; }
    std::string traceLine() const;  // one-line status for playthrough logs
    // Pick a Colony-Base cell the way the original's picker does: ONE
    // worldNext() draw over the planet's NON-ROCK surface cells, barren
    // class 0 INCLUDED (picker FUN_0003875c uniform-among-legal-empty;
    // legality of class 0 for item 5 per FUN_0003830c rule order —
    // income-law.md T42, census scripts/r1_cell_choice_census.py).
    // Returns -1 only if the planet has no non-rock cell (original: the
    // picker yields 0xffff and placement silently no-ops). PUBLIC for the
    // t42 uniformity pin; consumes one worldLcg_ draw per call.
    int drawCbCell(const PlanetState& ps);
    // Rule-G neighbour test (income-law.md S13, CLOSED t43): true iff one of
    // the FOUR graph neighbours of `cell` — (row-1,x),(row+1,x),(row,x-1),
    // (row,x+1) in continuous-x coords over the runtime row-width/row-start
    // tables (verified byte-for-byte from guest RAM, kRows-anchored) — is
    // marked active. Mirrors checker FUN_0003830c @0x385b7..0x386fe
    // (FUN_0003965c row lookup + four FUN_000395c4 probes; any active word2
    // bit0 -> legal). PUBLIC for the t43 pin. sizeClass: 0..4 from
    // sizeClassFor(); unknown geometry -> false.
    static bool cellActiveNeighbour(const std::vector<char>& active,
                                    int sizeClass, int surfaceCells, int cell);
    // SurfaceCells -> runtime planet-type index (verified 1:1 across 484
    // saves: 7->0, 11->1, 23->2, 45->3, 73->4; else -1).
    static int sizeClassFor(int surfaceCells);
    // t43 built-item cell draw (income-law.md S13): ONE worldNext() over
    // EMPTY non-rock surface cells with an ACTIVE neighbour; -1 if none.
    // t203: when ps.pendingItem == 38 (Xeno dig) the set is EMPTY ROCK cells
    // instead (checker rule D 0x38533 ==-law). PUBLIC for the t43 pin;
    // mutates worldLcg_.
    int drawItemCell(const PlanetState& ps);
    // t203 FREE-TECH GRANT (FUN_00046e84 verbatim, docs/re/_wip_t203.md S1/
    // S4): uniform rng over rows not owned and != the owner's queued TARGET,
    // NO prereq gate; marks owned, never touches the target. -1 + no draw
    // when zero candidates. Mutates campaign rng_. PUBLIC for the t203 pin.
    int freeTechGrantFor(int owner);

private:
    void pickHomeStars();
    void incomeAndGrow();
    void buildPhase();
    void researchPhase();
    void expansionPhase();
    void combatPhase();
    void abilityPhase();
    // t284 CONTROLLED-SYSTEMS producer (see scoreStars() above): the
    // FUN_00024f24 tail — clear lane marks, seed from home presence, flood.
    void recomputeScoreStars();
    void floodControlled(int star, std::vector<char>& laneDone,
                         unsigned allowedMask, int& count) const;
    // OQ-026: per-turn receive-leg sweep (cited shape 0x55f6e EBX=-1 inside
    // the per-race event loop, party-1 = current player row [0x7458e]; ships
    // .md S23 L6). One-shot per empire pair: fires the first turn a starlane
    // joins a star the player holds to a star that empire holds
    // [documented default site — the rewrite has no per-race event loop].
    void visibilityPhase();
    void diplomacyPhase();
    int attackScore(int owner) const;
    int defenseScore(int owner, int star) const;
    void setWar(int a, int b, bool on);
    Victory checkVictory() const;
    int itemId(const std::string& name) const;  // by NAME (verified rows), not index
    // Species-ability hooks (docs/re/abilities.md §2-§3).
    bool lanePassable(int owner, int target) const;  // SA_BlockStarLanes
    int popCapFor(int star) const;                 // +0x4a seed law (S10)
    // Stored-channel helpers (income-law.md S6 recalc): compressed IND /
    // raw RES of one star, Hyperpower(12)/Internet(14) first-occurrence
    // doubling per S6. needClassFor: FUN_0003fec4 need-class law (S9 t28).
    int storedIndFor(int star) const;
    int storedResFor(int star) const;
    int storedProsFor(int star) const;
    // World-generation LCG continuation (banked FUN_0007824f law; state
    // seeded := cfg.seed at construction [injected-state inferred]). ONE
    // stream serves the terrain draw, the t40 home-CB placement, AND the
    // t41 colonised-planet CB grant — it NEVER touches campaign rng_
    // (REFUTED-ROUTES RNG discipline: the campaign stream must stay put so
    // combat/expansion timelines remain reproducible).
    int worldNext();
    int homeNext();  // t295 home-draw stream (same FUN_0x7824f form, homeLcg_)
    // Seed a freshly-claimed planet: pop := 2 [verified S6e] + exactly one
    // Colony Base via drawCbCell (t41 law, scripts/r1_colony_items.py:
    // 2720/2720 owned records corpus-wide carry an ACTIVE Colony Base; the
    // 2 same-world in-run colonisation observations both show CB-only,
    // pop 2, cap == seed+2 exact). Original paths producing that state
    // (t42 raw disasm): EVENT handler FUN_0003aa0a @0x3b0bd..0x3b0d1 =
    // activator FUN_00038840 mode 0 with the CARGO slot record (+0xae),
    // legality gated at @0x3afed; and FUN_00041d64..0x41d7b = POP:=2 +
    // PICKER FUN_00038818 (uniform among legal empties). The cargo-slot
    // chooser upstream of +0xae is not yet recovered [open]; the rewrite
    // uses the picker draw for arrivals (observed arrival ranks 4 and 40
    // are consistent with it; income-law.md T42).
    void seedColonyBaseColony(int star);
    // Shared raw-channel accumulator triple {IND, PROS, RES} under the
    // battery law (income-law.md T35 gating + T36b placement): k-th surface
    // item sits on surface cell k (first-empty-slot verified 17980/18620
    // contiguous; items on barren at terrain rate 263/892 vs 31.6%),
    // class-cell +1 bonus only when the item's own channel field != 0.
    // Orbital items read ring classes (always 1 -> never bonus-eligible).
    struct ChannelAcc {
        int ind = 0, pros = 0, res = 0;
        bool dblI = false, dblP = false, dblR = false;
    };
    ChannelAcc channelAccFor(int star) const;
    // +0x4a analog (income-law.md S10): clamp(0..100, capBase + MPOP sum,
    // items flags&4 and Colony Base excluded).
    int storedCapFor(int star) const;
    int needClassFor(int star) const;

    CampaignConfig cfg_;
    Galaxy galaxy_;
    const ResearchTree* tree_;
    const std::vector<PlanetItem>* items_;
    const std::vector<Gizmo>* gizmos_ = nullptr;  // combat strength inputs (OQ-010)
    std::vector<DipFile> aiDip_;  // aiDip_[i] drives owner i+1
    std::mt19937 rng_;
    // World-generation LCG state (banked FUN_0007824f law, see worldNext()).
    uint32_t worldLcg_ = 0;
    // t295 home-draw stream (same FUN_0x7824f form, isolated state; see
    // pickHomeStars). Seeded from cfg.seed at construction.
    uint32_t homeLcg_ = 0;

    std::vector<int> owner_;                   // per star
    std::vector<PlanetState> planets_;         // per star (only owned stars use it)
    std::vector<std::vector<bool>> ownedTech;  // per owner, indexed by Tech id
    std::vector<double> res;                   // research stockpile per owner
    std::vector<double> ind_;                  // per-turn industry budget (buildPhase)
    std::vector<int> queuedTech;               // per owner, Tech id or -1
    std::vector<double> techProgress;          // per owner
    std::vector<ShipInTransit> fleet_;
    // t365 ENGINE FLIP: the per-ship engine (combatPhase owns its boundary
    // steps; docs/re/campaign_fleet_bridge doc header). Lazily constructed;
    // destructor out-of-line (incomplete type in this header).
    std::unique_ptr<CampaignFleetBridge> fleetSim_;
    std::vector<DipPolicyState> dipState_;     // per AI owner
    // War table (symmetric bits, owner x owner) + capture fortify counter
    // per star. Model + constants: docs/re/turnloop.md §5 [inferred].
    std::vector<int> homeStar_;                   // per owner, fixed pickHomeStars id
    std::vector<char> war_;
    // t204: attacked-mark array analog of [0x48304] — t205 CORRECTED the
    // index identity: one byte PER STAR (0x43afa writes
    // byte[0x48304 + (dword[edi+2]>>16)], dword[star_record+2]>>16 == the
    // row's OWN star index, measured k<50 20/20 saves), value = mask of
    // victim races fired at at that star while NOT at war. PERMANENT for the
    // attack channel (no clear site for 1<<r bits; bit 0 has an unrelated
    // set/clear pair 0x24e39/0x24e84). docs/re/_wip_t205.md S2/S4.
    std::vector<unsigned char> attacked_;
    std::vector<int> fortify_;
    // Species abilities (docs/re/abilities.md): ability_[o] = owner o's SA_
    // (Unknown = none); charge_[o] is the MEASURED count-up counter (original
    // row+0x19e, aicode.md §6.4): +1 per abilityPhase, fires the body iff it
    // equals abilityChargeTurns() exactly, resets to 0 on fire. Transient
    // per-activation flags:
    // doublePower_[o] (attack x2 this combat), invincible_[s] (star shield),
    // laneBlock_[s] (star whose lanes are blocked this combat).
    std::vector<SpeciesAbility> ability_;
    std::vector<int> charge_;
    std::vector<char> doublePower_, sapActive_, invincible_, laneBlock_;
    std::vector<int> fleetDamage_;  // per owner: accumulated hull damage (SA_DoubleHull / SA_HealShips / SA_SapAlienPower)
    // OQ-026 visibility state (docs/re/ships.md S23). Masks are OR-only
    // (sticky law, S23 L5): laneVis_ per galaxy lane (rec+0x20 analog),
    // starLaneVis_ / starSelVis_ per star (obj +0x16 / +0x17 analogs — two
    // separate vectors because t193's mid-game census censuses the twin
    // bytes with DIFFERENT distributions {1:160,6:180,...} vs {1:260,6:240,...},
    // so they are not one value). Seeded at construction: an empire sees
    // every lane incident to a star it owns and both bits of its own stars
    // (t192 new-game witness "race r's list == EXACTLY {mask==1<<r}" + t193
    // re-read "the per-race list is the race's OWN claimed lanes"; the init
    // PATH that writes the first 1<<r bits is not among the cited writers ->
    // [documented default]). SA_KnowStarLanes ORs its bit into every lane
    // (help.txt L2295 through the only consumer surface t194 proved exists);
    // SA_KnowHomeWorlds ORs its bit into both bytes of every ALIEN HOME star
    // (L1783 "see all alien home stars"). Separate draw stream visLcg_ — the
    // campaign rng_ must stay untouched (REFUTED-ROUTES RNG discipline) and
    // the terrain worldLcg_ is reserved for world-gen laws.
    std::vector<int> laneVis_;
    std::vector<char> starLaneVis_, starSelVis_;
    uint32_t visLcg_ = 0;
    int visNext();  // same FUN_0007824f form as worldNext(), own stream
    void seedVisibility();
    bool contactSeen(int a, int b) const;  // colony-star adjacency (share trigger)
    std::vector<char> contacted_;          // owner x owner: receive-leg fired
    int Nowner_ = 0;
    int turn_ = 0;
    // t284: DAT_000482fb analog ("STARS CONTROLLED"). 0 at construction/load
    // (the value is DERIVED state, never restored — t283 watchpoint + S10 #2),
    // recomputed by recomputeScoreStars() at the END of every advance().
    int scoreStars_ = 0;
    Victory victory_ = Victory::None;
    std::vector<CampaignEvent> events_;
};

}  // namespace ascend::game
