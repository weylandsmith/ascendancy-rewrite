#pragma once
#include <string>

#include "ui/audio.h"

namespace ascend::game { class Campaign; }

namespace ascend::ui {
// Opens the P5a window over a LIVE campaign (docs/re/ui-runtime.md §5).
// Blocks until quit or `turns` turns elapsed (0 = until quit). Returns 0 on
// clean exit and prints "ui ok: turn N". `autoplay` advances every 250 ms.
// `audio` (optional, docs/re/audio.md §5) plays click/laser/bang on the
// matching interactions.
int runCampaignUi(ascend::game::Campaign& camp, int turns, bool autoplay,
                  const std::string& fontPath, AudioEngine* audio = nullptr);
}  // namespace ascend::ui
