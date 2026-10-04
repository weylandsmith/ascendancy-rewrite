#include "game/research.h"
#include "harness.h"

#include <algorithm>
#include <filesystem>
#include <fstream>
#include <unordered_set>
#include <vector>

#ifndef ASCENDANCY_SOURCE_DIR
#define ASCENDANCY_SOURCE_DIR "."
#endif

namespace {

std::filesystem::path src(const std::string& f) {
    return std::filesystem::path(ASCENDANCY_SOURCE_DIR) / "extracted" / "ascend00" / f;
}

ascend::game::ResearchTree loadOrDie(std::string& err) {
    return ascend::game::ResearchTree::loadFromFile(src("restree.txt").string(), err);
}

}  // namespace

TEST(research_loads_66_main_plus_40_variants) {
    std::string err;
    auto t = loadOrDie(err);
    CHECK(err.empty());
    CHECK(t.all().size() == 106);
    CHECK(t.mainCount() == 66);
    // docs/re/research.md §3 measured roots
    std::vector<std::string> roots;
    for (int i : t.mainIndices())
        if (t.all()[i].prereqs.empty()) roots.push_back(t.all()[i].name);
    std::sort(roots.begin(), roots.end());
    CHECK(roots.size() == 3);
    CHECK(roots[0] == "Orbital Structures");
    CHECK(roots[1] == "Tonklin Diary");
    CHECK(roots[2] == "Xenobiology");
    // '^' word-joiner becomes a space
    bool found = false;
    for (const auto& tech : t.all())
        if (tech.name == "Spacetime Surfing") found = true;
    CHECK(found);
}

TEST(research_costs_match_measured_histogram) {
    std::string err;
    auto t = loadOrDie(err);
    // docs/re/research.md §3: main costs 50..400; §4: variants uniformly 20.
    int lo = 1 << 30, hi = 0;
    for (int i : t.mainIndices()) {
        lo = std::min(lo, t.all()[i].cost);
        hi = std::max(hi, t.all()[i].cost);
    }
    CHECK(lo == 50);
    CHECK(hi == 400);
    int variants = 0;
    for (const auto& tech : t.all())
        if (tech.variant) {
            ++variants;
            CHECK(tech.cost == 20);
        }
    CHECK(variants == 40);
    // a spot value straight from the table: Illusory^Machinations c=300
    bool spot = false;
    for (const auto& tech : t.all())
        if (tech.name == "Illusory Machinations") {
            spot = true;
            CHECK(tech.cost == 300);
            CHECK(tech.prereqs.size() == 2);
        }
    CHECK(spot);
}

TEST(research_graph_is_acyclic_with_forward_refs) {
    std::string err;
    auto t = loadOrDie(err);
    CHECK(t.wellFormed(err));
    // docs/re/research.md §2: file order is NOT topological; forward refs exist.
    int forward = 0;
    for (size_t i = 0; i < t.all().size(); ++i)
        for (int p : t.all()[i].prereqs)
            if (p > static_cast<int>(i)) ++forward;
    CHECK(forward == 3);
    // all variant prereqs land in the main block (research.md §4)
    for (const auto& tech : t.all())
        if (tech.variant)
            for (int p : tech.prereqs) CHECK(p < t.mainCount());
}

TEST(research_availability_gating) {
    std::string err;
    auto t = loadOrDie(err);
    const int n = static_cast<int>(t.all().size());
    std::vector<bool> owned(n, false);
    auto avail = t.available(owned);
    // With nothing owned, exactly the main roots are available: variants all
    // either have prereqs or would also appear; measure both sets.
    std::unordered_set<int> a(avail.begin(), avail.end());
    CHECK(a.count(0) == 1);  // Orbital Structures
    CHECK(a.count(2) == 1);  // Tonklin Diary
    CHECK(a.count(6) == 1);  // Xenobiology
    CHECK(a.count(1) == 0);  // Interplanetary Exploration needs 0
    // Own 0 -> its dependent becomes available
    owned[0] = true;
    auto avail2 = t.available(owned);
    CHECK(std::find(avail2.begin(), avail2.end(), 1) != avail2.end());
    CHECK(std::find(avail2.begin(), avail2.end(), 0) == avail2.end());
    // includeVariants=false hides ALL-CAPS techs
    auto nomod = t.available(owned, /*includeVariants=*/false);
    for (int i : nomod) CHECK(!t.all()[i].variant);
}

TEST(research_parser_rejects_corrupt_input) {
    struct Bad {
        const char* what;
        const char* text;
    } bad[] = {
        {"missing terminator", "66\r\nFoo^Tech 0 50\r\n"},
        {"bad count line", "sixty\r\nFoo 0 50 255\r\n"},
        {"too few rows for count", "99\r\nFoo 0 50 255\r\n"},
        {"non-numeric field",
         "1\r\nFoo 0 fifty 255\r\nBAR 0 20 255\r\n"},
        {"no rows at all", "66\r\n"},
    };
    auto tmp = std::filesystem::temp_directory_path() / "ascendancy_restree_bad.txt";
    for (const auto& b : bad) {
        {
            std::ofstream o(tmp, std::ios::binary);
            o << b.text;
        }
        std::string err;
        auto t = ascend::game::ResearchTree::loadFromFile(tmp.string(), err);
        CHECK(!err.empty());
    }
    std::filesystem::remove(tmp);
    // missing file also refuses loudly
    std::string err;
    auto t = ascend::game::ResearchTree::loadFromFile(
        (std::filesystem::path(ASCENDANCY_SOURCE_DIR) / "no-such-restree.txt").string(), err);
    CHECK(!err.empty());
}
