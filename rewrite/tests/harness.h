// SPDX-License-Identifier: GPL-3.0-or-later

// Minimal assertion harness: no external deps (the box is offline).
#pragma once
#include <cstdio>
#include <string>
#include <vector>

namespace ascend::test {

struct Case {
    const char* name;
    void (*fn)();
};

inline std::vector<Case>& registry() {
    static std::vector<Case> r;
    return r;
}

inline int& failures() {
    static int f = 0;
    return f;
}

struct Register {
    Register(const char* name, void (*fn)()) { registry().push_back({name, fn}); }
};

inline void check(bool cond, const char* expr, const char* file, int line) {
    if (!cond) {
        std::printf("    FAIL %s:%d  %s\n", file, line, expr);
        ++failures();
    }
}

}  // namespace ascend::test

#define CHECK(cond) ::ascend::test::check((cond), #cond, __FILE__, __LINE__)
#define TEST(name)                                                     \
    static void name();                                                \
    static ::ascend::test::Register reg_##name(#name, &name);          \
    static void name()
