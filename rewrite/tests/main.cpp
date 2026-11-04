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
        std::printf("  %-52s", c.name);
        c.fn();
        ++ran;
        std::printf("%s\n", ascend::test::failures() == before ? "ok" : "FAILED");
    }
    const int bad = ascend::test::failures();
    std::printf("\n%d tests, %d failed\n", ran, bad);
    return bad == 0 ? 0 : 1;
}
