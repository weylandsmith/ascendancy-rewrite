// SPDX-License-Identifier: GPL-3.0-or-later

// t409 SPECIAL ABILITY DIALOG + SPECIES MENU law pins.
// LAW (docs/re/_wip_t409.md F1-F4 + abilitylaw.h / speciesmenu.h):
//  1. The help.txt abilNN parse yields EXACTLY 21 blocks, indices 0..20;
//     every title ends "Special Ability"; the 14 charged blocks carry the
//     "%d day%s to amass" line and buttons Use Ability(msg 1) + Cancel
//     (msg 0); the 7 passives {0,1,2,3,4,15,18} carry OK(msg 0) only (the
//     gate-3m split).
//  2. The ABILITYWIN modal rect is the windows.txt verbatim 60,100-395,355
//     and the hit law is the FULL-RECT dismiss (ABILBUTTON0/1 both cover
//     the whole window, msg 50 family).
//  3. The species menu header is the static.txt #11 shape
//     "K of T Species Known"; rows = CONTACTED owners only; an owner with
//     0 stars reads "Extinct" (static #12); flag face == the scenario
//     specnum (owner i+1 takes the i-th non-player roster entry).
//  4. The t409 Campaign accessors are display-only: reading them every
//     turn must not perturb the dynamics (md5-visible state identical).
#include "ui/abilitylaw.h"
#include "ui/speciesmenu.h"

#include <cctype>
#include <cstdio>
#include <filesystem>
#include <fstream>
#include <map>
#include <memory>
#include <optional>
#include <string>
#include <vector>

#include "game/campaign.h"
#include "game/diplomacy.h"
#include "game/mapgen.h"
#include "game/research.h"
#include "game/species.h"
#include "game/starstat.h"
#include "game/economy.h"
#include "harness.h"

#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif

namespace {
namespace au = ascend::ui;
namespace ag = ascend::game;
const std::string kRepo = ASCENDANCY_SOURCE_DIR;

// Marker-driven static.txt reader (fleet-screen.md F10 getter-index law;
// the t407/t408 copy — kept local so this file stays self-contained).
std::map<int, std::string> staticTxtEntries() {
    std::ifstream f(kRepo + "/extracted/ascend00/static.txt", std::ios::binary);
    std::map<int, std::string> out;
    std::vector<std::string> lines;
    std::string line;
    while (std::getline(f, line)) {
        if (!line.empty() && line.back() == '\r') line.pop_back();
        lines.push_back(line);
    }
    for (size_t i = 0; i < lines.size(); i++) {
        std::string s = lines[i];
        size_t b = s.find_first_not_of(" \t");
        if (b == std::string::npos) continue;
        s = s.substr(b);
        if (s.size() < 3 || s[0] != '/' || s[1] != '/') continue;
        std::string t = s.substr(2);
        size_t p = 0;
        while (p < t.size() && (t[p] == ' ' || t[p] == '\t')) p++;
        size_t q = p;
        while (q < t.size() && isdigit(static_cast<unsigned char>(t[q]))) q++;
        if (q == p) continue;
        int a = std::stoi(t.substr(p, q - p));
        int n = 1;
        size_t d = q;
        while (d < t.size() && (t[d] == ' ' || t[d] == '\t')) d++;
        if (d < t.size() && t[d] == '-') {
            d++;
            while (d < t.size() && (t[d] == ' ' || t[d] == '\t')) d++;
            size_t r = d;
            while (r < t.size() && isdigit(static_cast<unsigned char>(t[r]))) r++;
            if (r > d) n = std::stoi(t.substr(d, r - d)) - a + 1;
        }
        int got = 0;
        for (size_t j = i + 1; j < lines.size() && got < n; j++) {
            std::string e = lines[j];
            size_t eb = e.find_first_not_of(" \t");
            if (eb == std::string::npos) continue;
            e = e.substr(eb);
            if (e.size() < 2 || e.front() != '"' || e.back() != '"') continue;
            e = e.substr(1, e.size() - 2);
            size_t np = 0;
            while ((np = e.find("\\n", np)) != std::string::npos)
                e.replace(np, 2, "\n");
            out[a + got] = e;
            got++;
        }
    }
    return out;
}

// Seeded campaign over the SHIPPED data (t402/t407/t408 fixture pattern),
// player species = Minions (specnum 0) so abilityOf(kPlayer) is a real
// panel index.
std::optional<ag::Campaign> seededCampaign(int seed,
                                           std::vector<ag::SpeciesInfo>* roster) {
    static ag::StarStats stats;
    static std::vector<std::string> names;
    static ag::ResearchTree tree;
    static std::vector<ag::PlanetItem> items;
    static std::vector<ag::Gizmo> gizmos;
    static bool loaded = false;
    std::string e;
    if (!loaded) {
        auto st = ag::StarStats::load(kRepo + "/extracted/ascend00/starstat.txt", &e);
        if (!st) return std::nullopt;
        stats = *st;
        names = ag::loadStarNames(kRepo + "/extracted/ascend00/names.txt", &e);
        tree = ag::ResearchTree::loadFromFile(kRepo + "/extracted/ascend00/restree.txt", e);
        items = ag::loadPlanItems(kRepo + "/extracted/ascend00/planitem.txt", e);
        gizmos = ag::loadGizmos(kRepo + "/extracted/ascend00/gizmos.txt", e);
        loaded = !items.empty();
    }
    if (!loaded) return std::nullopt;
    if (!ag::loadAbilities(kRepo + "/extracted/ascend00", roster, &e))
        return std::nullopt;
    std::vector<ag::DipFile> ai;
    std::vector<ag::SpeciesAbility> abs;
    for (const auto& si : *roster) {
        if (int(abs.size()) >= 6) break;
        if (si.specnum == 0) continue;  // the player's species
        ag::DipFile df;
        char path[256];
        std::snprintf(path, sizeof(path), "%s/extracted/ascend00/race%02d.dip",
                      kRepo.c_str(), si.specnum);
        if (!df.loadFromFile(path, &e)) return std::nullopt;
        abs.push_back(si.ability);
        ai.push_back(std::move(df));
    }
    ag::CampaignConfig cfg;
    cfg.seed = seed;
    cfg.aiCount = 6;
    cfg.freeForAll = true;
    cfg.playerSpecies = 0;
    ag::MapConfig mc;
    mc.seed = seed;
    ag::Galaxy g = ag::MapGenerator(mc, stats, names).generate();
    if (g.stars.empty()) return std::nullopt;
    return std::make_optional<ag::Campaign>(cfg, g, &tree, items, gizmos, ai,
                                            abs, &e);
}

}  // namespace

// ---- 1. the abilNN parse census -------------------------------------------
TEST(abil_parse_census_t409) {
    REQUIRE_DATA();
    std::vector<au::AbilityPanel> panels;
    std::string err;
    CHECK(au::loadAbilityPanels(kRepo + "/extracted/ascend00/help.txt",
                                &panels, &err));
    CHECK(panels.size() == size_t(21));
    int charged = 0, passive = 0;
    for (size_t i = 0; i < panels.size(); i++) {
        const auto& p = panels[i];
        CHECK(p.index == int(i));  // contiguous 0..20
        CHECK(p.title.find("Special Ability") != std::string::npos);
        CHECK(!p.body.empty());
        const bool hasCharge = p.chargeLine.find("day%s") != std::string::npos;
        if (hasCharge) {
            charged++;
            CHECK(p.buttons.size() == size_t(2));
            if (p.buttons.size() == 2) {
                CHECK(p.buttons[0].title == "Use Ability");
                CHECK(p.buttons[0].msg == 1);
                CHECK(p.buttons[1].title == "Cancel");
                CHECK(p.buttons[1].msg == 0);
            }
        } else {
            passive++;
            CHECK(p.buttons.size() == size_t(1));
            if (!p.buttons.empty()) {
                CHECK(p.buttons[0].title == "OK");
                CHECK(p.buttons[0].msg == 0);
            }
        }
    }
    CHECK(charged == 14);
    CHECK(passive == 7);
    for (int idx : {0, 1, 2, 3, 4, 15, 18})
        CHECK(panels[size_t(idx)].chargeLine.empty());
}

TEST(abil_panel_lookup_and_verbatim_t409) {
    REQUIRE_DATA();
    std::vector<au::AbilityPanel> panels;
    std::string err;
    CHECK(au::loadAbilityPanels(kRepo + "/extracted/ascend00/help.txt",
                                &panels, &err));
    for (int i = 0; i < int(ag::SpeciesAbility::kCount); i++)
        CHECK(au::panelForIndex(panels, i) != nullptr);
    CHECK(au::panelForIndex(panels, -1) == nullptr);
    CHECK(au::panelForIndex(panels, 21) == nullptr);
    // abil00 verbatim (help.txt L1713..): the Minions block.
    CHECK(panels[0].title == "Minions Special Ability");
    CHECK(panels[0].body.find("invasions will always") != std::string::npos);
}

// ---- 2. modal geometry + full-rect dismiss law -----------------------------
TEST(abilitywin_rect_and_hit_t409) {
    // windows.txt ln2136-2143 verbatim.
    CHECK(au::kAbilityWin.x0 == 60);
    CHECK(au::kAbilityWin.y0 == 100);
    CHECK(au::kAbilityWin.x1 == 395);
    CHECK(au::kAbilityWin.y1 == 355);
    // ABILBUTTON0/1 BOTH cover the full rect -> every inside click hits.
    CHECK(au::abilityDialogHit(60, 100));
    CHECK(au::abilityDialogHit(395, 355));
    CHECK(au::abilityDialogHit(227, 227));
    CHECK(!au::abilityDialogHit(59, 200));
    CHECK(!au::abilityDialogHit(396, 200));
    CHECK(!au::abilityDialogHit(200, 99));
    CHECK(!au::abilityDialogHit(200, 356));
}

TEST(charge_line_format_t409) {
    const std::string tmpl =
        "It will take %d day%s to amass the energy needed to use your "
        "ability.";
    CHECK(au::formatChargeLine(tmpl, 60) ==
          "It will take 60 days to amass the energy needed to use your "
          "ability.");
    CHECK(au::formatChargeLine(tmpl, 1) ==
          "It will take 1 day to amass the energy needed to use your "
          "ability.");
    CHECK(au::formatChargeLine(tmpl, -5) ==
          "It will take 0 days to amass the energy needed to use your "
          "ability.");
}

// ---- 3. static.txt #11/#12 markers (the species-menu strings) --------------
TEST(species_menu_static_markers_t409) {
    REQUIRE_DATA();
    const auto s = staticTxtEntries();
    CHECK(s.count(11) == 1);
    CHECK(s.at(11) == "%d of %d Species Known");
    CHECK(s.at(12) == "Extinct");
}

// ---- 4. membership + header over the seeded campaign -----------------------
TEST(species_menu_membership_t409) {
    REQUIRE_DATA();
    std::vector<ag::SpeciesInfo> roster;
    auto camp = seededCampaign(2024, &roster);
    if (!camp) { std::printf("    (campaign fixture unavailable)\n"); return; }
    CHECK(camp->ownerCount() == 7);  // player + 6 AI
    for (int t = 0; t < 12; t++) {
        const auto rows = au::speciesMenuRows(*camp, &roster);
        const std::string hdr = au::speciesMenuHeader(*camp);
        // The header's leading K == the row count (same known-gate).
        CHECK(std::stoi(hdr) == int(rows.size()));
        CHECK(hdr.find(" of 6 Species Known") != std::string::npos);
        for (const auto& r : rows) {
            CHECK(camp->playerKnows(r.owner));
            CHECK(r.owner >= 1 && r.owner <= 6);
            // flag face = scenario specnum (owner i+1 takes the i-th
            // non-player roster entry): owners 1..6 -> specnums 1..6.
            CHECK(r.flagSpecnum == r.owner);
            CHECK(r.extinct == (camp->starsOwned(r.owner) == 0));
        }
        camp->advance();
    }
}

TEST(extinct_row_law_t409) {
    REQUIRE_DATA();
    std::vector<ag::SpeciesInfo> roster;
    // Seed 5 contacted FLUDENTRI by turn ~9 in the t409 witness; seed 11
    // proved contact-slow (the original fixture skipped vacuously).
    auto camp = seededCampaign(5, &roster);
    if (!camp) { std::printf("    (campaign fixture unavailable)\n"); return; }
    // Drive until a KNOWN owner exists (the t409 row gate), then strip that
    // owner's stars: the row must FLIP to extinct — a flip only the
    // starsOwned()==0 branch can produce (mutation M8 re-scope: the naive
    // pre-contact fixture was vacuous, no known owner existed at turn 1).
    int target = -1;
    for (int t = 0; t < 60 && target < 1; t++) {
        for (const auto& r : au::speciesMenuRows(*camp, &roster))
            if (r.owner >= 1 && !r.extinct) { target = r.owner; break; }
        if (target < 1) camp->advance();
    }
    if (target < 1) { std::printf("    (no known owner within 60 turns)\n"); return; }
    for (size_t i = 0; i < camp->galaxy().stars.size(); i++)
        if (camp->starOwner(int(i)) == target) camp->setStarOwnerForTest(int(i), -1);
    CHECK(camp->starsOwned(target) == 0);
    bool sawTarget = false;
    for (const auto& r : au::speciesMenuRows(*camp, &roster))
        if (r.owner == target) { sawTarget = true; CHECK(r.extinct); }
    CHECK(sawTarget);  // the owner is still known -> the row still exists
}

// ---- 5. the t409 accessors are display-only --------------------------------
TEST(readonly_accessors_no_state_delta_t409) {
    REQUIRE_DATA();
    std::vector<ag::SpeciesInfo> roster;
    auto a = seededCampaign(2024, &roster);
    auto b = seededCampaign(2024, &roster);
    if (!a || !b) { std::printf("    (campaign fixture unavailable)\n"); return; }
    for (int t = 0; t < 30; t++) {
        const auto rows = au::speciesMenuRows(*a, &roster);
        for (const auto& r : rows) (void)r.name;
        (void)au::speciesMenuHeader(*a);
        a->advance();
        b->advance();
        CHECK(a->turn() == b->turn());
        CHECK(a->starsOwned(0) == b->starsOwned(0));
        CHECK(a->techsOwned(0) == b->techsOwned(0));
    }
}
