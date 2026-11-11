// SPDX-License-Identifier: GPL-3.0-or-later

#pragma once
#include <string>

#include "ui/audio.h"

namespace ascend::formats { class Flic; }

namespace ascend::game { class Campaign; }

namespace ascend::ui {
// Opens the P5a window over a LIVE campaign (docs/re/ui-runtime.md §5).
// Blocks until quit or `turns` turns elapsed (0 = until quit). Returns 0 on
// clean exit and prints "ui ok: turn N". `autoplay` advances every 250 ms.
// `audio` (optional, docs/re/audio.md §5) plays click/laser/bang on the
// matching interactions. `dataRoot` is the repo root holding extracted/;
// text is rendered with the VENDOR .fnt faces (smfont/bigfont, docs/re/fnt.md
// + ui-runtime.md §3 — OQ-017 CLOSED, substitute removed 2026-10-05f).
int runCampaignUi(ascend::game::Campaign& camp, int turns, bool autoplay,
                  const std::string& dataRoot, AudioEngine* audio = nullptr);

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
