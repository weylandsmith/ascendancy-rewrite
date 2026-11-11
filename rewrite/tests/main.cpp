// SPDX-License-Identifier: GPL-3.0-or-later

#include "harness.h"

#include <cstdio>
#include <cstring>
#include <cstring>

int main(int argc, char** argv) {
    // Optional substring filter (t295): `run_tests <frag>` runs only tests
    // whose name contains <frag>; no arg = run all (behaviour unchanged).
    const char* filt = argc > 1 ? argv[1] : nullptr;
    int ran = 0;
    for (const auto& c : ascend::test::registry()) {
        if (filt && !std::strstr(c.name, filt)) continue;
        const int before = ascend::test::failures();
        const int sbefore = ascend::test::skipped();
        std::printf("  %-52s", c.name);
        c.fn();
        ++ran;
        if (ascend::test::skipped() != sbefore)
            std::printf("skipped (no vendor data)\n");
        else
            std::printf("%s\n", ascend::test::failures() == before ? "ok" : "FAILED");
    }
    const int bad = ascend::test::failures();
    std::printf("\n%d tests, %d skipped, %d failed\n", ran,
                ascend::test::skipped(), bad);
    return bad == 0 ? 0 : 1;
}
