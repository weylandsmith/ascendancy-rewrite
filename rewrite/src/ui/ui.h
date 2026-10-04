#pragma once
#include <string>
namespace ascend::game { class Campaign; }

namespace ascend::ui {
// Opens the P5a window over a LIVE campaign (docs/re/ui-runtime.md §5).
// Blocks until quit or `turns` turns elapsed (0 = until quit). Returns 0 on
// clean exit and prints "ui ok: turn N". `autoplay` advances every 250 ms.
int runCampaignUi(ascend::game::Campaign& camp, int turns, bool autoplay,
                  const std::string& fontPath);
}  // namespace ascend::ui
