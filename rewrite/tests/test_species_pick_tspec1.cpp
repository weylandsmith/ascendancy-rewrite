// SPDX-License-Identifier: GPL-3.0-or-later

// tSPEC-1 PINS — the Begin-path RACELIST pick must reach PLAY (D33-L2;
// law docs/re/_wip_tSPEC1.md S1/S2, distilled from this cycle):
//   VENDOR LAW [verified disasm]: the RACELIST click arm 0x52d6c stores
//   word[win+0xb3]=clicked row (window-init 0x52c8c sets it to 0 = Minions)
//   and calls FUN_00022ce4(state=0x12e10, ebx=word[+0xb3], edx=count). In
//   0x22ce4 the PLAYER branch (loop k==0, 0x22f8d `mov bl,[esp+0x10]`) uses
//   that word with NO rand — AI players k>0 draw rand%21 distinct (0x22fba
//   idiv 0x15, collision scan 0x22fd8 against byte[raceRow+7]). 0x3e6bc
//   stores the specnum at race-row+7 (state+6+k*0x1ee); Begin's worldgen
//   0x238e8 indexes the home TABLES 0x88f90/0x88fe4 with byte[race-row+7]
//   (t30 site 0x23aeb), i.e. home size = T1[spec], terrain row = T2[spec]
//   (tPL-D1 MEASURED 85/85). The species-COUNT arm 0x52e58 passes the SAME
//   word[+0xb3] — count clicks never move the player's species.
//   PORT DEFECT (user: "home planet is medium eden REGARDLESS of species"):
//   the Begin rebuild used cfg.playerSpecies = CLI --species (default -1),
//   so every Begin game took the rng home path — species dropped.
// Pins: (1) pure handoff identity: newGameSettings carries the species word
// verbatim; (2) plumbing source-scan (tESC-1 idiom): title.cpp feeds the
// RACELIST selection, main.cpp prefers apply->species on the Begin leg;
// (3) behavior: same seed, Chamachies(19) vs Minions(0) -> DIFFERENT home
// size/row, each equal to its table entry (the witness shape unit-sized).
#include <cstdio>
#include <optional>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>

#include "game/campaign.h"
#include "ui/menulaw.h"
#include "harness.h"

#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif

namespace {
namespace ag = ascend::game;
namespace au = ascend::ui;
const std::string kRepo = ASCENDANCY_SOURCE_DIR;

std::string slurp(const std::string& rel) {
    std::ifstream f(kRepo + "/" + rel);
    std::ostringstream ss;
    ss << f.rdbuf();
    return ss.str();
}

#define REQUIRE(cond)         \
    do {                      \
        CHECK((cond));        \
        if (!(cond)) return;  \
    } while (0)

std::optional<ag::Campaign> mk(int playerSpecies, unsigned seed) {
    static ag::StarStats stats;
    static std::vector<std::string> names;
    static ag::ResearchTree tree;
    static std::vector<ag::PlanetItem> items;
    static std::vector<ag::Gizmo> gizmos;
    static std::vector<ag::DipFile> ai;
    static bool loaded = false;
    if (!loaded) {
        std::string err;
        auto st = ag::StarStats::load(kRepo + "/extracted/ascend00/starstat.txt", &err);
        if (!st) return std::nullopt;
        stats = *st;
        names = ag::loadStarNames(kRepo + "/extracted/ascend00/names.txt", &err);
        tree = ag::ResearchTree::loadFromFile(kRepo + "/extracted/ascend00/restree.txt", err);
        items = ag::loadPlanItems(kRepo + "/extracted/ascend00/planitem.txt", err);
        gizmos = ag::loadGizmos(kRepo + "/extracted/ascend00/gizmos.txt", err);
        for (int i = 0; i < 6; ++i) {
            ag::DipFile df;
            char path[256];
            std::snprintf(path, sizeof(path), "%s/extracted/ascend00/race%02d.dip",
                          ASCENDANCY_SOURCE_DIR, i);
            if (!df.loadFromFile(path, &err)) return std::nullopt;
            ai.push_back(std::move(df));
        }
        loaded = true;
    }
    ag::CampaignConfig cfg;
    cfg.seed = seed;
    cfg.aiCount = 6;
    cfg.playerSpecies = playerSpecies;
    ag::MapConfig mc;
    mc.seed = seed;
    ag::Galaxy g = ag::MapGenerator(mc, stats, names).generate();
    std::string err;
    return std::optional<ag::Campaign>(
        std::in_place, cfg, g, &tree, items, gizmos, ai, &err);
}
}  // namespace

TEST(species_handoff_identity_tspec1) {
    // The handoff carries the RACELIST word VERBATIM (0x22ce4 stores param
    // ebx into race-row+7 without arithmetic; the port's roster is
    // specnum-ordered, so row index == specnum). Mutation M1: drop the arg
    // (always 0) -> the 19 checks fail.
    const au::NewGameSettings s = au::newGameSettings(2, 5, 1, 19);
    CHECK(s.set);
    CHECK(s.species == 19);
    // Vendor window-init 0x52c8c: word[+0xb3]=0 (Minions) — the default
    // player species when no RACELIST row was clicked.
    const au::NewGameSettings d = au::newGameSettings(0, 5, 1);
    CHECK(d.species == 0);
    // The unset struct (no Begin press) must stay inert — species there is
    // meaningless, 'set' gates the whole apply (tNG-B B4 law).
    au::NewGameSettings u;
    CHECK(!u.set);
}

TEST(species_plumb_title_feeds_racelist_tspec1) {
    // title.cpp Begin press feeds the RACELIST selection (scrollOffset +
    // selSlot — the same expression speciesNameAt/species-pick log use)
    // into newGameSettings. Mutation M2: constant feeds -> CHECK fails.
    const std::string src = slurp("rewrite/src/ui/title.cpp");
    // Anchor on the handoff assignment itself (the kBeginNewGameBtn literal
    // also appears at paint sites earlier in the file).
    const size_t fn = src.find("*newGameOut = newGameSettings(");
    CHECK(fn != std::string::npos);
    if (fn == std::string::npos) return;
    // It must sit inside the BEGIN press block (btn literal precedes it).
    CHECK(src.rfind("kBeginNewGameBtn", fn) != std::string::npos);
    const size_t close = src.find(')', fn);
    CHECK(close != std::string::npos);
    const std::string args = src.substr(fn, close - fn);
    CHECK(args.find("scrollOffset + selSlot") != std::string::npos);
    // Anti-comment (tESC-1 M1): the call line must not be commented out.
    const size_t lineStart = src.rfind('\n', fn);
    const std::string callLine = src.substr(lineStart + 1, fn - lineStart);
    CHECK(callLine.find("//") == std::string::npos);
    const std::string tail = src.substr(fn, 2500);
    // The apply line must report the species too (witness reads it).
    CHECK(tail.find("gov %d species %d") != std::string::npos);
}

TEST(species_plumb_main_prefers_apply_tspec1) {
    // main.cpp buildCampaign: on the Begin handoff the species comes from
    // apply->species; the CLI flag stays the authority elsewhere.
    // Mutation M3: revert to o.playerSpecies -> CHECK fails.
    const std::string src = slurp("rewrite/src/main.cpp");
    CHECK(src.find("(apply && apply->set) ? apply->species : o.playerSpecies") !=
          std::string::npos);
    CHECK(src.find("cfg.playerSpecies = playerSpecies;") != std::string::npos);
    // The live line carries the play campaign's species (not the intent).
    CHECK(src.find("camp->playerSpecies()") != std::string::npos);
}

TEST(species_home_differs_by_pick_tspec1) {
    // The user-visible law at unit scale: SAME seed, two species picks ->
    // different home TYPE, each exactly its table entry. T1/T2 verbatim
    // (payload 0x88f90 / 0x88fe4, tPL-D1 85/85): Chamachies(19) -> idx 3
    // (45 cells) row 7; Minions(0) -> idx 4 (73) row 5. Pre-fix, BOTH picks
    // produced the same rng home (the D33-L2 complaint).
    REQUIRE_DATA();
    for (unsigned seed : {5u, 7u, 2024u}) {
        auto cha = mk(19, seed);
        auto min = mk(0, seed);
        REQUIRE(bool(cha) && bool(min));
        const int hc = cha->homeStarFor(0), hm = min->homeStarFor(0);
        REQUIRE(hc >= 0 && hm >= 0);
        CHECK(cha->planetAt(hc).surfaceCells == 45);
        CHECK(cha->planetAt(hc).terrainRow == 7);
        CHECK(min->planetAt(hm).surfaceCells == 73);
        CHECK(min->planetAt(hm).terrainRow == 5);
        CHECK(cha->planetAt(hc).surfaceCells != min->planetAt(hm).surfaceCells);
    }
}
