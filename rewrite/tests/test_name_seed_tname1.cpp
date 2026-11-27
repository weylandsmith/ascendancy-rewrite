// SPDX-License-Identifier: GPL-3.0-or-later

// tNAME-1 PINS — per-game star names (D33-L3; law docs/re/_wip_tNAME1.md
// S2/S3/S6/S7, distilled this cycle):
//   VENDOR LAW [verified disasm FUN_00020fd4 = the game's main(), sole call
//   site 0x7b817]: the fresh path calls the clock getter 0x7821c then
//   srand 0x78273 at 0x213fc BEFORE worldgen; the record leg 0x21480..0x21490
//   overrides ONLY when the stored seed != -1. Worldgen FUN_000238e8 draws
//   every per-star/per-planet parameter (0x23da4 rng%5+1 planets, 0x23a86
//   rng%5 size, 0x23a97 rng%11 weight row) from the SINGLE Borland LCG
//   0x7824f. There is no separate name RNG: the names.txt pool is fixed
//   (mapgen.md S2), the per-game variation IS the seed draw.
//   CORPUS [measured scripts/tname1_homename_census.py + twin probe]: 25
//   fresh vendor lineages -> 25 DISTINCT owner-0 home star bases while home
//   CELLS stay constant per species (tPL-D1) — the user's law confirmed.
//   PORT DEFECT: seed had exactly one source (Options.seed default 1; the
//   Begin handoff carried no seed), so every Begin game re-drew the SAME
//   world — "always Phoebe".
// Pins: (1) handoff identity (seed rides verbatim); (2) title.cpp feeds a
// seed term into the Begin handoff and reports it; (3) main.cpp buildCampaign
// prefers apply->seed on the Begin leg and the clock draw is GUARDED to the
// interactive UI boot (headless default stays 1 — gate seed-identity law);
// (4) behavior: same seed -> same home star name; seed+1 -> different name,
// home TYPE still per-species.
#include <cstdio>
#include <fstream>
#include <optional>
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

std::string starBase(const std::string& name) {
    const size_t sp = name.rfind(' ');
    return sp == std::string::npos ? name : name.substr(0, sp);
}

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

TEST(name_handoff_carries_seed_tname1) {
    // (1) identity: the 5th arg rides into .seed verbatim; the legacy
    // 4-arg call still compiles with the default (tSPEC-1 pins unaffected).
    const au::NewGameSettings s = au::newGameSettings(2, 5, 1, 19, 0xC0FFEEu);
    CHECK(s.seed == 0xC0FFEEu);
    CHECK(s.species == 19);
    const au::NewGameSettings d = au::newGameSettings(0, 5, 1);
    CHECK(d.seed == 1u);  // deterministic default for non-UI/unit callers
    const au::NewGameSettings u;
    CHECK(!u.set && u.seed == 1u);
}

TEST(name_title_feeds_seed_tname1) {
    // (2a) the Begin press feeds a seed term derived from wheelBaseSeed (NOT
    // a constant) into newGameSettings. Mutation M2: drop the seed arg ->
    // CHECK fails. Anchor on the assignment statement (tSPEC-1 idiom: the
    // kBeginNewGameBtn literal also hits paint sites).
    const std::string src = slurp("rewrite/src/ui/title.cpp");
    const size_t fn = src.find("*newGameOut = newGameSettings(");
    CHECK(fn != std::string::npos);
    if (fn == std::string::npos) return;
    const size_t close = src.find(')', fn);
    REQUIRE(close != std::string::npos);
    const std::string args = src.substr(fn, close - fn);
    CHECK(args.find("wheelBaseSeed") != std::string::npos);
    CHECK(args.find("scrollOffset + selSlot") != std::string::npos);
    // Anti-comment (tESC-1 M1).
    const size_t lineStart = src.rfind('\n', fn);
    const std::string callLine = src.substr(lineStart + 1, fn - lineStart);
    CHECK(callLine.find("//") == std::string::npos);
    // (2b) the apply line REPORTS the seed (witness greps 'seed %u').
    const std::string tail = src.substr(fn, 2500);
    CHECK(tail.find("seed %u") != std::string::npos);
}

TEST(name_main_prefers_apply_seed_tname1) {
    // (3a) buildCampaign: on the Begin handoff the seed comes from apply.
    // Mutation M1: delete the two apply->seed lines -> CHECK fails.
    const std::string src = slurp("rewrite/src/main.cpp");
    const size_t blk = src.find("if (apply && apply->set) {");
    CHECK(blk != std::string::npos);
    if (blk == std::string::npos) return;
    const std::string body = src.substr(blk, 1200);
    CHECK(body.find("cfg.seed = apply->seed;") != std::string::npos);
    CHECK(body.find("mc.seed = apply->seed;") != std::string::npos);
    // (3b) the clock draw is GUARDED to the interactive boot: --seed seen =
    // authority (vendor cmp ebx,-1 leg), and headless never reaches it.
    // Mutation M3: remove the guard -> CHECK fails.
    CHECK(src.find("if (o.ui && !o.seedExplicit)") != std::string::npos);
    const size_t guard = src.find("if (o.ui && !o.seedExplicit)");
    CHECK(guard != std::string::npos);
    if (guard == std::string::npos) return;
    const std::string gbody = src.substr(guard, 700);
    CHECK(gbody.find("fresh-run seed") != std::string::npos);
    // The default stays 1 (headless seed-identity: gate matrix relies on it).
    CHECK(src.find("unsigned seed = 1;") != std::string::npos);
}

TEST(name_varies_by_seed_same_type_tname1) {
    // (4) the user-visible law at unit scale: same seed -> byte-identical
    // choice (determinism contract); seed vs seed+k -> DIFFERENT home star
    // NAME, while the home TYPE stays the species table entry (tPL-D1).
    REQUIRE_DATA();
    for (unsigned seed : {1u, 5u, 2024u}) {
        auto a = mk(19, seed);
        auto b = mk(19, seed);
        auto c = mk(19, seed + 1);
        auto d = mk(19, seed + 2);
        REQUIRE(bool(a) && bool(b) && bool(c) && bool(d));
        const int ha = a->homeStarFor(0), hb = b->homeStarFor(0);
        const int hc = c->homeStarFor(0), hd = d->homeStarFor(0);
        REQUIRE(ha >= 0 && hb >= 0 && hc >= 0 && hd >= 0);
        // determinism: same seed, same name
        CHECK(a->galaxy().stars[ha].name == b->galaxy().stars[hb].name);
        // variation: fresh seed draws a different home star (over 6 draws
        // of a 100-base pool the collision chance per pair is ~2%; require
        // at least ONE of the two neighbour-seed pairs to differ so a
        // single unlucky collision cannot flake the suite, while M4
        // (constant-seed regression) fails BOTH pairs).
        const bool vary1 = starBase(a->galaxy().stars[ha].name) !=
                           starBase(c->galaxy().stars[hc].name);
        const bool vary2 = starBase(a->galaxy().stars[ha].name) !=
                           starBase(d->galaxy().stars[hd].name);
        CHECK(vary1 || vary2);
        // type law untouched: Chamachies home stays 45 cells / row 7 for
        // EVERY seed (the other half of the user's law).
        CHECK(a->planetAt(ha).surfaceCells == 45);
        CHECK(a->planetAt(ha).terrainRow == 7);
        CHECK(c->planetAt(hc).surfaceCells == 45);
        CHECK(c->planetAt(hc).terrainRow == 7);
    }
}
