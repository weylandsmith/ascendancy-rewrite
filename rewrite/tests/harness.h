// SPDX-License-Identifier: GPL-3.0-or-later

// Minimal assertion harness: no external deps (the box is offline).
#pragma once
#include <cstdio>
#include <filesystem>
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

// t375: tests that dereference vendor data (extracted/ or game/*.cob) must
// SKIP, not crash, on a fresh public clone without the user-supplied data.
// Found by the packaging verification: run_tests segfaulted at
// test_research.cpp:40 (garbage std::string at 0x8) with no data present.
inline int& skipped() {
    static int s = 0;
    return s;
}

struct Register {
    Register(const char* name, void (*fn)()) { registry().push_back({name, fn}); }
};

// Does the vendor data this suite reads exist? A public clone ships code +
// docs only; the user extracts their own copy (README §Supply your own).
inline bool data_available() {
#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif
    namespace fs = std::filesystem;
    return fs::exists(fs::path(ASCENDANCY_SOURCE_DIR) / "extracted" / "ascend01");
}

inline void check(bool cond, const char* expr, const char* file, int line) {
    if (!cond) {
        std::printf("    FAIL %s:%d  %s\n", file, line, expr);
        ++failures();
    }
}

}  // namespace ascend::test

#define CHECK(cond) ::ascend::test::check((cond), #cond, __FILE__, __LINE__)
// Skip (not fail) a test that needs vendor data on a clone without it.
// Counted separately so a data-less run can never masquerade as a full pass:
// main prints "<ran> tests, <skipped> skipped, <failed> failed".
#define REQUIRE_DATA()                                                      \
    if (!::ascend::test::data_available()) {                                \
        ++::ascend::test::skipped();                                        \
        std::printf("SKIP ");                                               \
        return;                                                             \
    }
#define TEST(name)                                                     \
    static void name();                                                \
    static ::ascend::test::Register reg_##name(#name, &name);          \
    static void name()
