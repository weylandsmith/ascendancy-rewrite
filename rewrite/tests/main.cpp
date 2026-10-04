#include "harness.h"

#include <cstdio>

int main() {
    int ran = 0;
    for (const auto& c : ascend::test::registry()) {
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
