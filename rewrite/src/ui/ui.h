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
// matching interactions.
int runCampaignUi(ascend::game::Campaign& camp, int turns, bool autoplay,
                  const std::string& fontPath, AudioEngine* audio = nullptr);

// Plays an FLC video 1:1 into a 640x480 window (docs/re/flc.md): palette +
// indices converted on the CPU to ARGB, uploaded per frame via a streaming
// texture, paced by the file's per-frame delay / header speed. Any key or
// quit event stops playback (decode continues harmlessly to EOF). Returns 0
// on clean finish/interrupt, 1 on load failure. No audio: the vendor intro's
// music-track selection is unresolved (OQ-018), so silence is the honest
// default. The --intro path (intro65a.flc is the vendor intro per
// docs/re/media.md §1). maxFrames > 0 caps playback (gate smoke).
int playIntro(const std::string& flicPath, int maxFrames);
}  // namespace ascend::ui
