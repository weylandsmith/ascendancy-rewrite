// SPDX-License-Identifier: GPL-3.0-or-later

#pragma once
#include <string>
#include <vector>

#include "game/species.h"  // SpeciesInfo (t393 New Game roster param)
#include "ui/audio.h"
#include "ui/boot.h"
#include "ui/menulaw.h"  // NewGameSettings (tNG-B B4 Begin-handoff out-param)

namespace ascend::formats { class Flic; }

namespace ascend::game { class Campaign; }

namespace ascend::ui {
// t385: the title screen (D8 user ruling 2026-11-14: boot goes to the title
// screen, all menu options present). Runs the boot state machine
// (ui/boot.h law, docs/re/boot.md) until it exits to Campaign or Quit.
// `initial` pre-selects a state (BootState::Campaign = the Resume-equivalent
// autoplay path, so gates need no synthetic title click). `maxIntroFrames`
// caps the intro movie (gate smoke: small N; 0 = play all). Returns the
// exit state; sets `err` and returns Quit if the window/fonts cannot be
// built. Prints one line per accepted click (`ui title click NAME -> state`)
// — automation verifies routing WITHOUT reading pixels.
// `windowOut` (t385b): on a Campaign exit, the SDL_Window (as void* — no
// SDL type in this header) is handed over UNDESTROYED and *windowOut set.
// Reuse is a measured requirement, not cosmetics: SDL2/X11 under WM-less
// Xvfb DISCARDS the first synthetic Button event delivered to a freshly
// created window (no focus model to credit it), so destroying the title
// window and creating a campaign window eats the gate's injected click.
// Measured 2026-11-14: click #1 after the swap lost, click #2 landed
// (scripts/_wip_t385_debug3.sh log); single-window boots never lose it.
BootState runTitleScreen(const std::string& dataRoot, BootState initial,
                         int maxIntroFrames, std::string* err,
                         void** windowOut = nullptr,
                         const std::string& savesDir = std::string(),
                         AudioEngine* audio = nullptr,
                         const ascend::game::Campaign* previewCamp = nullptr,
                         const std::vector<ascend::game::SpeciesInfo>* roster =
                             nullptr,
                         const std::vector<std::string>* lore = nullptr,
                         // tNG-B B4 SETTINGS-APPLY out-param: the Begin press
                         // fills it with the wheel triple (law ui/menulaw.h
                         // newGameSettings — state-identity: the vendor arms
                         // already write the play state at click time; Begin
                         // adds the world layer + the atmosphere global).
                         // nullptr / no-Begin = untouched (Resume path).
                         NewGameSettings* newGameOut = nullptr);

// Opens the P5a window over a LIVE campaign (docs/re/ui-runtime.md §5).
// Blocks until quit or `turns` turns elapsed (0 = until quit). Returns 0 on
// clean exit and prints "ui ok: turn N". `autoplay` advances every 250 ms.
// `audio` (optional, docs/re/audio.md §5) plays click/laser/bang on the
// matching interactions. `dataRoot` is the repo root holding extracted/;
// text is rendered with the VENDOR .fnt faces (smfont/bigfont, docs/re/fnt.md
// + ui-runtime.md §3 — OQ-017 CLOSED, substitute removed 2026-10-05f).
// `savesDir` (t388): the supply-your-own dir the Alt-L load screen lists
// (empty = no dir; the screen still opens and says so — honest zero).
int runCampaignUi(ascend::game::Campaign& camp, int turns, bool autoplay,
                  const std::string& dataRoot, AudioEngine* audio = nullptr,
                  void* window = nullptr,
                  const std::string& savesDir = std::string(),
                  const std::vector<ascend::game::SpeciesInfo>* roster =
                      nullptr);

// Plays an FLC video 1:1 into a 640x480 window (docs/re/flc.md): palette +
// indices converted on the CPU to ARGB, uploaded per frame via a streaming
// texture, paced by the file's per-frame delay / header speed. Any key or
// quit event stops playback (decode continues harmlessly to EOF). Returns 0
// on clean finish/interrupt, 1 on load failure.
// `audio` (t388b, docs/re/audio.md §6): when set, the cited SUBTITLE.TXT
// cue table fires by frame number — DIGITALMUSIC TUNEID 6 at frame 20 and
// TUNEID 7 at 988 (intro00/intro01; TUNEID is 0-based into the vendor's
// 29-entry music.txt table, measured t440 audio.md §6.3a),
// FADEMUSIC VOLUME 100/80/60/30 at frames 966/971/976/981 (dip) and 127 at
// 988 (restore; file order puts the 127 line before the TUNEID-7 block, so
// volume is restored before the tune switch). The ±1 base of FRAMENUMBER is
// not statically pinned; cues fire at index == N-1 (one 71 ms frame of
// possible slack, named not guessed). Null audio = silent.
int playIntro(const std::string& flicPath, int maxFrames,
              AudioEngine* audio = nullptr);
}  // namespace ascend::ui
