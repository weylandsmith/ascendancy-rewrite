// SPDX-License-Identifier: GPL-3.0-or-later

#pragma once
#include <string>

#include "ui/audio.h"
#include "ui/boot.h"

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
                         void** windowOut = nullptr);

// Opens the P5a window over a LIVE campaign (docs/re/ui-runtime.md §5).
// Blocks until quit or `turns` turns elapsed (0 = until quit). Returns 0 on
// clean exit and prints "ui ok: turn N". `autoplay` advances every 250 ms.
// `audio` (optional, docs/re/audio.md §5) plays click/laser/bang on the
// matching interactions. `dataRoot` is the repo root holding extracted/;
// text is rendered with the VENDOR .fnt faces (smfont/bigfont, docs/re/fnt.md
// + ui-runtime.md §3 — OQ-017 CLOSED, substitute removed 2026-10-05f).
int runCampaignUi(ascend::game::Campaign& camp, int turns, bool autoplay,
                  const std::string& dataRoot, AudioEngine* audio = nullptr,
                  void* window = nullptr);

// Plays an FLC video 1:1 into a 640x480 window (docs/re/flc.md): palette +
// indices converted on the CPU to ARGB, uploaded per frame via a streaming
// texture, paced by the file's per-frame delay / header speed. Any key or
// quit event stops playback (decode continues harmlessly to EOF). Returns 0
// on clean finish/interrupt, 1 on load failure. No audio: the vendor intro's
// music-track selection resolved (OQ-018 closed 2026-10-07: tune selector
// DAT_00010ba0 == 0 in every capture == theme00); residual engine detail
// tracked as OQ-022, so the silence fallback below stays honest for audio-off.
// default. The --intro path (intro65a.flc is the vendor intro per
// docs/re/media.md §1). maxFrames > 0 caps playback (gate smoke).
int playIntro(const std::string& flicPath, int maxFrames);
}  // namespace ascend::ui
