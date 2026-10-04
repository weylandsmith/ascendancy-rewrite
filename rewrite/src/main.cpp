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
#include <string>
#include <vector>

#include "formats/bin_table.h"
#include "formats/cob.h"

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
        "  --headless    SDL dummy video driver, no audio device\n");
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
