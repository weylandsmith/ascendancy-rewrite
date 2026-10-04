// ascendancy — reimplementation entry point.
//
// Current scope (docs/PLAN.md P3): boot SDL2 headless-able, locate and load
// the original extracted data through the verified readers, print an
// inventory, and run a stub turn loop. Game systems arrive in P4 in the PLAN
// order; each one cites docs/ for its constants (PLAN rule 1).
#include <SDL.h>
#include <SDL_mixer.h>

#include <cstdio>
#include <filesystem>
#include <memory>
#include <string>
#include <vector>

#include "formats/bin_table.h"
#include "formats/cob.h"
#include "game/campaign.h"
#include "game/diplomacy.h"
#include "game/economy.h"
#include "game/mapgen.h"
#include "game/research.h"
#include "game/species.h"
#include "game/starstat.h"
#include "ui/ui.h"

#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif

namespace fs = std::filesystem;
using ascend::formats::BinTable;
using ascend::formats::CobArchive;

namespace {

struct Options {
    fs::path dataRoot = ASCENDANCY_SOURCE_DIR;  // repo root holds extracted/
    int turns = 0;                              // 0 = interactive
    bool headless = false;                      // SDL dummy driver, no audio
    int campaign = 0;                           // N turns of seeded campaign
    unsigned seed = 1;
    bool ui = false;                            // P5a window (docs/re/ui-runtime.md)
    bool autoplay = false;
    bool audio = false;                         // SDL2_mixer (docs/re/audio.md §5)
    bool mute = false;                          // load everything, volume 0
    int playerSpecies = -1;                     // specnum 0..20 (docs/re/species.md)
};

bool parseArgs(int argc, char** argv, Options* o) {
    for (int i = 1; i < argc; ++i) {
        const std::string a = argv[i];
        if (a == "--data" && i + 1 < argc)
            o->dataRoot = argv[++i];
        else if (a == "--turns" && i + 1 < argc)
            o->turns = std::atoi(argv[++i]);
        else if (a == "--headless")
            o->headless = true;
        else if (a == "--campaign" && i + 1 < argc)
            o->campaign = std::atoi(argv[++i]);
        else if (a == "--seed" && i + 1 < argc)
            o->seed = static_cast<unsigned>(std::atol(argv[++i]));
        else if (a == "--ui")
            o->ui = true;
        else if (a == "--autoplay")
            o->autoplay = true;
        else if (a == "--audio")
            o->audio = true;
        else if (a == "--mute")
            o->mute = true;
        else if (a == "--species" && i + 1 < argc)
            o->playerSpecies = std::atoi(argv[++i]);
        else if (a == "--help")
            return false;
        else {
            std::printf("unknown argument: %s\n", a.c_str());
            return false;
        }
    }
    return true;
}

void usage() {
    std::printf(
        "usage: ascendancy [--data ROOT] [--turns N] [--headless]\n"
        "  --data ROOT   directory containing extracted/ (default: repo root)\n"
        "  --turns N     run N turns of the turn loop then exit\n"
        "  --headless    SDL dummy video driver, no audio device\n"
        "  --audio       SDL2_mixer: all 86 soundfx + theme00 (docs/re/audio.md)\n"
        "  --mute        load audio but master volume 0\n"
        "  --campaign N  play N turns of a seeded campaign (docs/re/turnloop.md)\n"
        "  --seed S      seed for --campaign (default 1)\n"
        "  --ui          open the P5a campaign window (docs/re/ui-runtime.md)\n"
        "  --autoplay    with --ui: advance a turn every 250 ms\n"
        "  --species N   play as species specnum N (0..20, docs/re/species.md);\n"
        "                default -1 = human, no special ability\n");
}

// Loads the three archives from the ORIGINAL game/ directory, because the
// verified container spec is the archive itself (docs/FINDINGS.md P1a). The
// extracted/ tree is used as the cross-check corpus.
struct GameData {
    std::vector<CobArchive> archives;
    int bin_tables = 0;
    bool ok = false;
};

bool loadGameData(const Options& o, GameData* g, std::string* err) {
    // game/ sits next to the repo root; allow --data to point at either.
    fs::path game = o.dataRoot / "game";
    if (!fs::exists(game)) game = o.dataRoot;
    for (const char* name : {"ascend00.cob", "ascend01.cob", "ascend02.cob"}) {
        const fs::path p = game / name;
        if (!fs::exists(p)) {
            *err = std::string("missing archive ") + p.string();
            return false;
        }
        auto a = CobArchive::load(p, err);
        if (!a) return false;
        g->archives.push_back(std::move(*a));
    }
    for (const auto& a : g->archives) {
        for (const auto& e : a.entries()) {
            const size_t dot = e.name.rfind('.');
            if (dot == std::string::npos || e.name.compare(dot, 4, ".bin") != 0) continue;
            const uint8_t* p = nullptr;
            uint32_t n = 0;
            if (!a.find(e.name, &p, &n)) continue;
            std::string e2;
            if (BinTable::parse(p, n, &e2)) ++g->bin_tables;
        }
    }
    g->ok = true;
    return true;
}

}  // namespace


// Shared campaign builder for --campaign and --ui (docs/re/turnloop.md).
// The tables are function-local statics because Campaign stores pointers into
// them (research tree, item/gizmo tables).
std::unique_ptr<ascend::game::Campaign> buildCampaign(const Options& o,
                                                      std::string* err) {
    namespace ag = ascend::game;
    static const ag::ResearchTree tree =
        ag::ResearchTree::loadFromFile(
            (o.dataRoot / "extracted/ascend00/restree.txt").string(), *err);
    static const std::vector<ag::PlanetItem> items =
        ag::loadPlanItems((o.dataRoot / "extracted/ascend00/planitem.txt").string(), *err);
    static const std::vector<ag::Gizmo> gizmos =
        ag::loadGizmos((o.dataRoot / "extracted/ascend00/gizmos.txt").string(), *err);
    const fs::path d0 = o.dataRoot / "extracted" / "ascend00";
    auto stats = ag::StarStats::load(d0 / "starstat.txt", err);
    if (!stats) return nullptr;
    auto names = ag::loadStarNames(d0 / "names.txt", err);
    if (names.empty()) return nullptr;
    if (items.size() != 39 || gizmos.size() != 76) {
        *err = "table counts wrong: items " + std::to_string(items.size()) +
               " gizmos " + std::to_string(gizmos.size());
        return nullptr;
    }
    // Species roster cross-checked against help.txt (race02's tokenless
    // header resolves via its help-abil02 title; docs/re/abilities.md §1).
    static std::vector<ag::SpeciesInfo> roster;
    if (roster.empty() && !ag::loadAbilities(d0.string(), &roster, err))
        return nullptr;
    if (o.playerSpecies < -1 || o.playerSpecies >= static_cast<int>(roster.size())) {
        *err = "--species " + std::to_string(o.playerSpecies) +
               " out of range 0.." + std::to_string(roster.size() - 1);
        return nullptr;
    }
    // Six AI races = first six specnums that are not the player's [documented
    // default policy; the original's slot assignment is runtime-blocked].
    std::vector<ag::DipFile> ai;
    std::vector<ag::SpeciesAbility> abilities;
    for (const ag::SpeciesInfo& si : roster) {
        if (static_cast<int>(abilities.size()) >= 6) break;
        if (o.playerSpecies >= 0 && si.specnum == o.playerSpecies) continue;
        char name[32];
        std::snprintf(name, sizeof(name), "/race%02d.dip", si.specnum);
        ag::DipFile df;
        if (!df.loadFromFile(d0.string() + name, err)) return nullptr;
        abilities.push_back(si.ability);
        ai.push_back(std::move(df));
    }
    ag::CampaignConfig cfg;
    cfg.seed = o.seed;
    cfg.playerSpecies = o.playerSpecies;
    ag::MapConfig mc;
    mc.seed = o.seed;
    ag::Galaxy g = ag::MapGenerator(mc, *stats, names).generate();
    return std::make_unique<ag::Campaign>(cfg, g, &tree, items, gizmos, ai,
                                          abilities, err);
}

// Seeded campaign to victory: docs/re/turnloop.md. Returns process exit code
// (0 when a victory was reached within --campaign turns).
int runCampaign(const Options& o) {
    namespace ag = ascend::game;
    std::string err;
    auto c = buildCampaign(o, &err);
    if (!c) { std::printf("campaign: %s\n", err.c_str()); return 1; }
    std::printf("campaign seed=%u stars=%zu lanes=%zu ai=6\n", o.seed,
                c->galaxy().stars.size(), c->galaxy().lanes.size());
    for (int t = 0; t < o.campaign && !c->over(); ++t) {
        c->advance();
        std::printf("%s\n", c->traceLine().c_str());
    }
    for (const auto& ev : c->events())
        std::printf("  [t%d] %s\n", ev.turn, ev.text.c_str());
    if (c->over()) {
        std::printf("VICTORY %s via %s.txt on turn %d (score %d%%)\n",
                    ag::victoryName(c->victory()), ag::victoryConditionFile(c->victory()),
                    c->turn(), c->playerScorePct());
        return 0;
    }
    std::printf("no victory after %d turns\n", o.campaign);
    return 1;
}

int main(int argc, char** argv) {
    Options o;
    if (!parseArgs(argc, argv, &o)) {
        usage();
        return 2;
    }
    if (o.headless) SDL_SetHint(SDL_HINT_VIDEODRIVER, "dummy");

    GameData g;
    std::string err;
    if (!loadGameData(o, &g, &err)) {
        std::printf("data load FAILED: %s\n", err.c_str());
        return 1;
    }
    std::printf("archives: %zu", g.archives.size());
    for (const auto& a : g.archives) std::printf(" %zu", a.count());
    std::printf("  (.bin tables parsed: %d)\n", g.bin_tables);

    if (SDL_Init(o.headless ? SDL_INIT_EVENTS : (SDL_INIT_VIDEO | SDL_INIT_EVENTS)) != 0) {
        std::printf("SDL_Init failed: %s\n", SDL_GetError());
        return 1;
    }
    std::printf("SDL %d.%d.%d initialised (video driver: %s)\n", SDL_MAJOR_VERSION,
                SDL_MINOR_VERSION, SDL_PATCHLEVEL, SDL_GetCurrentVideoDriver());

    if (o.campaign > 0 && !o.ui) {
        const int rc = runCampaign(o);
        SDL_Quit();
        return rc;
    }
    if (o.ui) {
        std::string cerr;
        auto camp = buildCampaign(o, &cerr);
        if (!camp) {
            std::printf("campaign: %s\n", cerr.c_str());
            SDL_Quit();
            return 1;
        }
        // Substitute face (docs/re/ui-runtime.md §3; vendor .fnt = OQ-017).
        const std::string font =
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf";
        std::unique_ptr<ascend::ui::AudioEngine> audio;
        if (o.audio) {
            audio = std::make_unique<ascend::ui::AudioEngine>();
            std::string aerr;
            if (!audio->init(o.dataRoot.string(), o.mute, &aerr)) {
                std::printf("audio: %s\n", aerr.c_str());
                SDL_Quit();
                return 1;
            }
            std::printf("audio ok: %d sfx chunks, music %lu B\n",
                        audio->chunksLoaded(), audio->musicBytes());
            audio->playMusic();
        }
        const int rc = ascend::ui::runCampaignUi(*camp, o.campaign, o.autoplay,
                                                 font, audio.get());
        SDL_Quit();
        return rc;
    }

    // Audio: the game's music is raw PCM whose sample rate is not yet known
    // (docs/re/media.md OQ-006), so P3 opens the device but plays nothing.
    if (!o.headless && Mix_OpenAudio(22050, AUDIO_S16SYS, 1, 1024) == 0) {
        std::printf("mixer open at 22050 Hz mono (rate is provisional, OQ-006)\n");
    }

    // Stub turn loop: real turn resolution is P4 (economy -> research ->
    // production -> movement -> combat -> AI -> diplomacy -> victory).
    const int turns = o.turns > 0 ? o.turns : 1;
    for (int t = 1; t <= turns; ++t) {
        SDL_Event ev;
        while (SDL_PollEvent(&ev)) {
            if (ev.type == SDL_QUIT) {
                SDL_Quit();
                return 0;
            }
        }
        if (turns > 1) std::printf("turn %d\n", t);
    }

    if (!o.headless) Mix_CloseAudio();
    SDL_Quit();
    std::printf("ok\n");
    return 0;
}
