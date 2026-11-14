// SPDX-License-Identifier: GPL-3.0-or-later

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
#include <fstream>
#include <memory>
#include <string>
#include <vector>

#include "formats/bin_table.h"
#include "formats/cob.h"
#include "formats/flic.h"
#include "formats/fnt.h"
#include "game/campaign.h"
#include "game/diplomacy.h"
#include "game/economy.h"
#include "game/mapgen.h"
#include "game/observer.h"
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
    bool resume = false;                        // t385: boot straight to Campaign
    bool audio = false;                         // SDL2_mixer (docs/re/audio.md §5)
    bool mute = false;                          // load everything, volume 0
    int playerSpecies = -1;                     // specnum 0..20 (docs/re/species.md)
    int stars = 50;                             // galaxy density (t78 ladder
                                                // 15/25/50/75/100; mapgen.md
                                                // OQ-012(a))
    bool flic = false;                          // decode both vendor FLCs (docs/re/flc.md)
    bool fonts = false;                         // load all vendor .fnt faces (docs/re/fnt.md)
    int introFrames = -1;                       // -1 off; >=0: play intro, cap N frames (0=all)
    std::string saveFile;                       // t382: --save OBSERVER boot
    std::string savesDir;                       // t387: --saves DIR (load list)
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
        else if (a == "--resume")
            o->resume = true;  // t385: Resume-equivalent boot (skip title click)
        else if (a == "--audio")
            o->audio = true;
        else if (a == "--mute")
            o->mute = true;
        else if (a == "--species" && i + 1 < argc)
            o->playerSpecies = std::atoi(argv[++i]);
        else if (a == "--stars" && i + 1 < argc)
            o->stars = std::atoi(argv[++i]);
        else if (a == "--flic")
            o->flic = true;
        else if (a == "--fonts")
            o->fonts = true;
        else if (a == "--intro" && i + 1 < argc)
            o->introFrames = std::atoi(argv[++i]);
        else if (a == "--save" && i + 1 < argc)
            o->saveFile = argv[++i];
        else if (a == "--saves" && i + 1 < argc)
            o->savesDir = argv[++i];  // t387: supply-your-own saves dir
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
        "  --ui          boot to the TITLE SCREEN (t385, docs/re/boot.md);\n"
        "                campaign is one transition away (RESUME button)\n"
        "  --resume      with --ui: pre-select Campaign (Resume-equivalent\n"
        "                boot — what the autoplay gates use)\n"
        "  --autoplay    with --ui: advance a turn every 250 ms\n"
        "  --species N   play as species specnum N (0..20, docs/re/species.md);\n"
        "                default -1 = human, no special ability\n"
        "  --stars N     galaxy size; original density ladder measured\n"
        "                15/25/50/75/100 stars (mapgen.md OQ-012(a); default 50)\n"
        "  --flic        decode both vendor FLC videos end-to-end (docs/re/flc.md)\n"
        "  --fonts       load all vendor .fnt faces + ink census (docs/re/fnt.md)\n"
        "  --intro N     play the vendor intro (intro65a.flc), N frames cap (0=all)\n"
        "  --save FILE   READ-ONLY OBSERVER boot: print the day, star map and\n"
        "                ship field of a save file, then exit. Accepts a\n"
        "                dosbox-x savestate ZIP (ring .sav) or a native raw\n"
        "                .SAV. This is NOT gameplay: no orders, no writes,\n"
        "                no simulation advance (order UI awaits a selection\n"
        "                widget; right-click deselect law banked, selfplay.md)\n"
        "  --saves DIR   t387: directory the title LOAD screen lists\n"
        "                (supply-your-own .SAV slots only — NEVER game/).\n"
        "                Default: <data>/saves when it exists; an absent\n"
        "                dir is an honest empty list.\n");
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
    // t294 (OQ-016 residue 3 CLOSED): the original loads the terrain weight
    // rows / surface grid / pop-growth scalar from planitem.txt at scenario
    // init (FUN_00037fc0, income-law.md S10 t294). Load them here so a modded
    // planitem.txt drives world-gen exactly like the vendor exe; on load
    // failure fall back to the MEASURED vendor table (identical values) and
    // keep the error visible only if the item table also failed.
    ag::TerrainTables terrain = ag::vendorTerrainTables();
    {
        std::string terrErr;
        if (!ag::loadTerrainTables((d0 / "planitem.txt").string(), terrain, terrErr))
            terrain = ag::vendorTerrainTables();
    }
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
    cfg.terrain = terrain;  // t294: planitem.txt-sourced world-gen tables
    ag::MapConfig mc;
    mc.seed = o.seed;
    mc.starCount = o.stars;   // t78 density ladder (mapgen.md OQ-012(a))
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

// t382 OBSERVER boot (--save FILE): read-only report of day + star map +
// ship field. Returns exit code (0 on a successful read; 1 with the honest
// refusal reason otherwise — never a clamp). NO writes, NO SDL, NO archives:
// runs before loadGameData like the other media smokes.
int runObserver(const Options& o) {
    namespace ag = ascend::game;
    std::error_code ec;
    const fs::path p = o.saveFile;
    if (!fs::exists(p, ec)) {
        std::printf("observer: no such file: %s\n", p.string().c_str());
        return 1;
    }
    std::vector<uint8_t> file;
    {
        std::ifstream f(p, std::ios::binary);
        file.assign(std::istreambuf_iterator<char>(f), std::istreambuf_iterator<char>());
    }
    if (file.empty()) { std::printf("observer: empty file\n"); return 1; }

    std::vector<ag::Observer::StarRow> stars;
    std::vector<ag::Observer::ShipRow> ships;
    uint32_t day = 0;
    std::string err;
    const bool isZip = file.size() > 4 && file[0] == 'P' && file[1] == 'K';
    if (isZip) {
        // Anchor-vote payload (same corpus file the t360 parser pins use).
        std::vector<uint8_t> payload;
        {
            std::ifstream g(fs::path(ASCENDANCY_SOURCE_DIR) / "work/ascend_payload.bin",
                            std::ios::binary);
            payload.assign(std::istreambuf_iterator<char>(g), std::istreambuf_iterator<char>());
        }
        if (!ag::Observer::importSavestate(p.string(), payload, &day, &stars, &ships, &err)) {
            std::printf("observer: REFUSED (%s)\n", err.c_str());
            return 1;
        }
        std::printf("observer: savestate %s  day %u (u32@0 law via turn counter)\n",
                    p.filename().string().c_str(), day);
    } else {
        day = ag::Observer::rawDay(file);
        std::printf("observer: native save %s  day %u (u32@0 law)\n",
                    p.filename().string().c_str(), day);
        const bool okStars = ag::Observer::parseRawStarBlock(file, &stars, &err);
        if (!okStars) std::printf("observer: star table REFUSED (%s)\n", err.c_str());
        const bool okShips = ag::Observer::parseRawShipBlock(file, &ships, &err);
        if (!okShips) std::printf("observer: ship block REFUSED (%s)\n", err.c_str());
        if (!okStars && !okShips) return 1;  // not a save file at all
    }

    // Fleet roster (imported into a ShipSim via the t361 fromRecord law; the
    // sim is BUILT, never advanced — observer scope).
    auto sim = ag::Observer::buildSim(day, stars, ships);
    std::printf("fleet: %zu live records, sim census %d\n", ships.size(), sim.liveCount());
    for (const auto& row : ships) {
        std::printf("  s%-3d own=%u kind=%d pos=(%.0f,%.0f,%.0f)", row.rec.slot,
                    row.rec.ownerRace, row.rec.orderKind, row.rec.pos[0],
                    row.rec.pos[1], row.rec.pos[2]);
        if (row.targetStar >= 0 && row.targetStar < int(stars.size()))
            std::printf(" -> %s", stars[size_t(row.targetStar)].name.c_str());
        if (!row.name.empty()) std::printf("  %s", row.name.c_str());
        std::printf("\n");
    }

    // TWO separate frames, no claimed projection (frame residue named in
    // docs/re/_wip_t382.md S3): star table span ~±430, ship field on the
    // 32-aligned world grid span ~±2300.
    if (!stars.empty()) {
        std::vector<float> xs, zs;
        std::vector<char> gl;
        for (const auto& s : stars) {
            xs.push_back(s.pos[0]); zs.push_back(s.pos[2]);
            gl.push_back(s.owner ? 'O' : 'o');  // shape, not colour
        }
        std::printf("\nSTAR TABLE (star-record frame; 'o' unowned, 'O' owned):\n");
        std::printf("%s", ag::Observer::renderMap(xs, zs, gl, 72, 24).c_str());
    }
    if (!ships.empty()) {
        std::vector<float> xs, zs;
        std::vector<char> gl;
        for (const auto& r : ships) {
            xs.push_back(r.rec.pos[0]); zs.push_back(r.rec.pos[2]);
            gl.push_back(char('0' + (r.rec.orderKind > 5 ? 0 : r.rec.orderKind)));
        }
        std::printf("\nSHIP FIELD (32-aligned world frame; digit = order kind):\n");
        std::printf("%s", ag::Observer::renderMap(xs, zs, gl, 72, 24).c_str());
    }
    return 0;
}

int main(int argc, char** argv) {
    Options o;
    if (!parseArgs(argc, argv, &o)) {
        usage();
        return 2;
    }
    if (!o.saveFile.empty()) return runObserver(o);
    if (o.headless) SDL_SetHint(SDL_HINT_VIDEODRIVER, "dummy");

    // FLC decode report (docs/re/flc.md): replay both vendor videos through
    // the port and print the headline facts. Deliberately BEFORE the archive
    // load so a --flic run is a codec-only smoke.
    if (o.flic) {
        int rc = 0;
        for (const std::string& p : {(o.dataRoot / "game/logic.flc").string(),
                                     (o.dataRoot / "extracted/ascend02/data/intro65a.flc").string()}) {
            ascend::formats::Flic f;
            std::string err;
            if (!f.load(p, &err)) {
                std::printf("flic load FAILED %s: %s\n", p.c_str(), err.c_str());
                rc = 1;
                continue;
            }
            int frames = 0, repaired = 0;
            const bool ok = f.replay([&](int, const uint8_t*, const uint8_t*) { ++frames; },
                                     &err, &repaired);
            if (!ok) {
                std::printf("flic replay FAILED %s: %s\n", p.c_str(), err.c_str());
                rc = 1;
                continue;
            }
            std::printf("flic ok: %s %dx%d speed %ums frames %d (repaired FLI_COPY %d)\n",
                        fs::path(p).filename().c_str(), f.width(), f.height(),
                        f.speedMs(), frames, repaired);
        }
        return rc;
    }

    // Vendor .fnt faces (docs/re/fnt.md, OQ-017): load all three, render a
    // probe string, print per-font facts. Codec-only smoke (before archives).
    if (o.fonts) {
        int rc = 0;
        for (const std::string& p : {(o.dataRoot / "extracted/ascend01/data/smfont.fnt").string(),
                                     (o.dataRoot / "extracted/ascend01/data/bigfont.fnt").string(),
                                     (o.dataRoot / "extracted/ascend02/data/intro.fnt").string()}) {
            ascend::formats::Font f;
            std::string err;
            if (!f.load(p, &err)) {
                std::printf("font load FAILED %s: %s\n", p.c_str(), err.c_str());
                rc = 1;
                continue;
            }
            // Render "Ascendancy 1995" to a scanline strip to prove glyph
            // iteration works on the real bytes (sum of ink, like the test).
            std::string probe = "Ascendancy 1995";
            uint64_t ink = 0;
            for (char c : probe) {
                const auto& g = f.glyph(uint8_t(c));
                for (uint32_t i = 0; i < g.width * uint32_t(f.height()); i++)
                    ink += g.px[i] != 0xFF;
            }
            std::printf("font ok: %s h=%d ink('%s')=%llu census=%llu\n",
                        fs::path(p).filename().c_str(), f.height(), probe.c_str(),
                        (unsigned long long)ink, (unsigned long long)f.inkCensus());
        }
        return rc;
    }

    // Vendor intro playback (docs/re/flc.md; intro = docs/re/media.md §1).
    // Runs BEFORE the archive load so it is a self-contained media smoke.
    if (o.introFrames >= 0) {
        if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_EVENTS) != 0) {
            std::printf("SDL_Init failed: %s\n", SDL_GetError());
            return 1;
        }
        const int rc = ascend::ui::playIntro(
            (o.dataRoot / "extracted/ascend02/data/intro65a.flc").string(),
            o.introFrames);
        SDL_Quit();
        return rc;
    }

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
        // t385 (D8 user ruling 2026-11-14): --ui boots to the TITLE SCREEN;
        // the campaign is reached through ONE transition (vendor RESUME
        // button, msg 1/1), not the constructor path. --resume pre-selects
        // Campaign (the Resume-equivalent path the autoplay gates use, so
        // t382/--autoplay flows do not regress); --intro N caps the title's
        // intro movie for the gate smoke.
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
        using ascend::ui::BootState;
        const BootState entry =
            o.resume ? BootState::Campaign : BootState::Title;
        std::string terr;
        void* handedWindow = nullptr;  // t385: title loop reuses it for campaign
        // t387: the LOAD screen's slot dir — explicit --saves wins; else
        // <data>/saves when it exists; NEVER game/ (supply-your-own law).
        fs::path sdir = o.savesDir.empty()
                            ? o.dataRoot / "saves"
                            : fs::path(o.savesDir);
        std::error_code sec;
        const std::string savesDir =
            fs::is_directory(sdir, sec) ? sdir.string() : std::string();
        const BootState exit = ascend::ui::runTitleScreen(
            o.dataRoot.string(), entry,
            o.introFrames >= 0 ? o.introFrames : 0,  // 0 = all frames
            &terr, &handedWindow, savesDir);
        if (exit == BootState::Quit && entry != BootState::Quit &&
            !terr.empty()) {
            std::printf("title: %s\n", terr.c_str());
            SDL_Quit();
            return 1;
        }
        if (exit != BootState::Campaign) {
            std::printf("ui title exit: %s\n", bootStateName(exit));
            SDL_Quit();
            return 0;
        }
        const int rc = ascend::ui::runCampaignUi(*camp, o.campaign, o.autoplay,
                                                 o.dataRoot.string(), audio.get(),
                                                 handedWindow, savesDir);
        SDL_Quit();  // also tears down the handed-over window
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
