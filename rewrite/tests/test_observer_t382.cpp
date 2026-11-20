// SPDX-License-Identifier: GPL-3.0-or-later

// t382 OBSERVER (--save boot) pins — laws and witness values from
// docs/re/_wip_t382.md (MEASURED 2026-11-12 on work/r1/game/01..04.SAV +
// ring work/r1/playcap/save/60.sav + bank-t1086-preplay). Read-only: these
// tests open saves, never write. NO OQ row closes on these facts.
#include "game/observer.h"
#include "formats/shipsave.h"
#include "harness.h"

#include <algorithm>
#include <cstdio>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <vector>

namespace fs = std::filesystem;
using ascend::game::Observer;

namespace {

const std::string kRepo =
#ifdef ASCENDANCY_SOURCE_DIR
    ASCENDANCY_SOURCE_DIR
#else
    "."
#endif
    ;

std::vector<uint8_t> slurp(const std::string& p) {
    std::ifstream f(p, std::ios::binary);
    return std::vector<uint8_t>(std::istreambuf_iterator<char>(f),
                                std::istreambuf_iterator<char>());
}

// t439 FIXTURE LAW: the witness below is the frozen t1254 capture, so it must
// NOT be read from the LIVE ring work/r1/playcap/save/ — that directory is a
// rotating 20-slot window owned by whatever dosbox session is running, and
// t439's recovery relaunch rotated it to turn 1086, which silently invalidated
// every pinned scalar in observer_savestate_import_t382 (5 failures, gate red).
// work/r1/bank-t438-ring-2200/ is the `cp -a` of the ring as it stood when that
// capture was banked: same bytes, ZERO writers. Rule for every future ring pin:
// pin a bank dir (immutable), never playcap/save/ (rotating).
const char* kWitnessSave = "/work/r1/bank-t438-ring-2200/60.sav";

bool corpusSaves() {
    return fs::exists(kRepo + "/work/r1/game/04.SAV") &&
           fs::exists(kRepo + kWitnessSave);
}

}  // namespace

TEST(observer_raw_day_law_t382) {
    REQUIRE_DATA();
    if (!corpusSaves()) { std::printf("(skip: saves absent) "); return; }
    // u32@0 = game-day law, 4/4 corpus saves (STATE.md protected-saves note).
    CHECK(Observer::rawDay(slurp(kRepo + "/work/r1/game/01.SAV")) == 1086);
    CHECK(Observer::rawDay(slurp(kRepo + "/work/r1/game/02.SAV")) == 1253);
    CHECK(Observer::rawDay(slurp(kRepo + "/work/r1/game/03.SAV")) == 887);
    CHECK(Observer::rawDay(slurp(kRepo + "/work/r1/game/04.SAV")) == 1254);
}

TEST(observer_raw_ship_block_law_t382) {
    REQUIRE_DATA();
    if (!corpusSaves()) { std::printf("(skip: saves absent) "); return; }
    // 04.SAV: 38 live records; marker set == {0..18,20,22,24..40} (MEASURED;
    // the 3 gaps are records that came to exist AFTER the save instant, and
    // slot 12 is present here but died before the ring capture).
    std::vector<Observer::ShipRow> rows;
    std::string err;
    CHECK(Observer::parseRawShipBlock(slurp(kRepo + "/work/r1/game/04.SAV"), &rows, &err));
    CHECK(rows.size() == 38);
    std::vector<int> slots;
    for (const auto& r : rows) slots.push_back(r.rec.slot);
    // strictly ascending (marker law)
    CHECK(std::is_sorted(slots.begin(), slots.end()));
    CHECK(std::adjacent_find(slots.begin(), slots.end()) == slots.end());
    CHECK(std::find(slots.begin(), slots.end(), 19) == slots.end());
    CHECK(std::find(slots.begin(), slots.end(), 21) == slots.end());
    CHECK(std::find(slots.begin(), slots.end(), 12) != slots.end());
    // witness values (roster, owner race, kind)
    CHECK(!rows.empty() && rows[0].name == "Stradivarian");
    CHECK(!rows.empty() && rows[0].rec.ownerRace == 0 && rows[0].rec.orderKind == 4);
    // witness pos (04.SAV slot 0, MEASURED roster): guards fillRecord field
    // offsets on the raw path.
    CHECK(!rows.empty() && rows[0].rec.pos[0] == -352.f &&
          rows[0].rec.pos[1] == 64.f && rows[0].rec.pos[2] == -832.f);
    // raw path NEVER derefs +0x59 (save-space pointer rewrite class)
    for (const auto& r : rows) CHECK(r.targetStar == -1);
    // every record sane by the block law itself
    for (const auto& r : rows)
        CHECK(r.rec.orderKind >= 1 && r.rec.orderKind <= 5 && r.rec.ownerRace <= 20);

    // Counts on the other saves (MEASURED 41/31/30).
    std::vector<Observer::ShipRow> r2, r3, r1;
    CHECK(Observer::parseRawShipBlock(slurp(kRepo + "/work/r1/game/02.SAV"), &r2, &err));
    CHECK(r2.size() == 41);
    CHECK(Observer::parseRawShipBlock(slurp(kRepo + "/work/r1/game/03.SAV"), &r3, &err));
    CHECK(r3.size() == 31);
    CHECK(Observer::parseRawShipBlock(slurp(kRepo + "/work/r1/game/01.SAV"), &r1, &err));
    CHECK(r1.size() == 30);
}

TEST(observer_raw_star_block_law_t382) {
    REQUIRE_DATA();
    if (!corpusSaves()) { std::printf("(skip: saves absent) "); return; }
    std::vector<Observer::StarRow> stars;
    std::string err;
    CHECK(Observer::parseRawStarBlock(slurp(kRepo + "/work/r1/game/04.SAV"), &stars, &err));
    CHECK(stars.size() == 50);  // corpus world T=50 (r1_t246 law, u16@0x16145)
    if (stars.size() == 50) {
        CHECK(stars[0].name == "Vega");
        CHECK(stars[0].typeK == 11);  // K census star0 (planets-ui.md §1 law)
        CHECK(stars[0].pos[0] > 359.4f && stars[0].pos[0] < 359.6f);
        CHECK(stars[2].name == "Atropos");
        // names unique (slot identity)
        std::vector<std::string> names;
        for (const auto& s : stars) names.push_back(s.name);
        std::sort(names.begin(), names.end());
        CHECK(std::adjacent_find(names.begin(), names.end()) == names.end());
    }
}

TEST(observer_savestate_import_t382) {
    REQUIRE_DATA();
    if (!corpusSaves()) { std::printf("(skip: saves absent) "); return; }
    auto payload = slurp(kRepo + "/work/ascend_payload.bin");
    CHECK(!payload.empty());
    uint32_t day = 0;
    std::vector<Observer::StarRow> stars;
    std::vector<Observer::ShipRow> ships;
    std::string err;
    CHECK(Observer::importSavestate(kRepo + kWitnessSave, payload,
                                    &day, &stars, &ships, &err));
    CHECK(day == 1254);
    CHECK(stars.size() == 50);
    CHECK(ships.size() == 40);  // full-window live census at capture
    // kind-4 +0x59 deref law: member = phys + 0x88 lands on the star-slot
    // record — 19/19 attribution measured; pin the witness s23 -> Atropos(2).
    int kind4 = 0, attributed = 0;
    for (const auto& r : ships) {
        if (r.rec.orderKind != 4) continue;
        ++kind4;
        if (r.targetStar >= 0) ++attributed;
        if (r.rec.slot == 23) CHECK(r.targetStar == 2);  // Atropos
    }
    CHECK(kind4 == 19);
    CHECK(attributed == 19);
    CHECK(ships[0].name == "Stradivarian");
}

TEST(observer_buildsim_and_refusal_t382) {
    REQUIRE_DATA();
    if (!corpusSaves()) { std::printf("(skip: saves absent) "); return; }
    std::vector<Observer::ShipRow> rows;
    std::string err;
    CHECK(Observer::parseRawShipBlock(slurp(kRepo + "/work/r1/game/04.SAV"), &rows, &err));
    auto sim = Observer::buildSim(1254, {}, rows);
    // fromRecord law A2: id == record slot; census mirror == imported count
    // (no corpses on the raw path — the block is the live list).
    CHECK(sim.liveCount() == int(rows.size()));
    CHECK(sim.findShip(rows.front().rec.slot) != nullptr);
    CHECK(sim.findShip(rows.front().rec.slot)->id == rows.front().rec.slot);

    // REFUSAL, not clamp: deterministic junk (no marker chain, no star run).
    std::vector<uint8_t> junk(size_t(200) * 0x166);
    uint32_t x = 0x12345678;
    for (auto& b : junk) { x = x * 1664525u + 1013904223u; b = uint8_t(x >> 13); }
    std::vector<Observer::ShipRow> none;
    std::vector<Observer::StarRow> noneStars;
    CHECK(!Observer::parseRawShipBlock(junk, &none, &err));
    CHECK(none.empty());
    CHECK(!Observer::parseRawStarBlock(junk, &noneStars, &err));
}

TEST(observer_synthetic_terminator_laws_t382) {
    // SYNTHETIC pins (labelled: they pin the OBSERVER's stated discovery
    // laws, not vendor-measured data — no corpus save contains a
    // duplicate-marker adjacency or a K>12 star run, so only constructed
    // inputs separate these branches; mutation campaign t382 M2/M4).
    // (a) Terminator: a marker chain stops at a REPEATED marker.
    auto saneShipAt = [](std::vector<uint8_t>& f, size_t h, uint8_t kind) {
        f[h + 0x56] = 0;                       // owner race 0
        f[h + 0x58] = kind;                    // live kind
        f[h + 0x15a] = 5;                      // invCap
        for (int i = 0; i < 3; ++i) f[h + 0x9e + 4 * i] = 0x00;  // pos 0.0f
    };
    std::vector<uint8_t> f(size_t(40) * 0x166, 0);
    for (uint32_t n = 0; n < 12; ++n) {
        uint32_t mk = n;  // markers 0..11
        std::memcpy(&f[size_t(n) * 0x166], &mk, 4);
        saneShipAt(f, size_t(n) * 0x166 + 4, 4);
    }
    // then a DUPLICATE marker 11 followed by sane records — the walk must
    // stop at the duplicate: exactly 12 rows, never 13+.
    for (uint32_t n = 12; n < 16; ++n) {
        uint32_t mk = (n == 12) ? 11u : n;
        std::memcpy(&f[size_t(n) * 0x166], &mk, 4);
        saneShipAt(f, size_t(n) * 0x166 + 4, 4);
    }
    std::vector<Observer::ShipRow> rows;
    std::string err;
    CHECK(Observer::parseRawShipBlock(f, &rows, &err));
    CHECK(rows.size() == 12);

    // (b) Star sanity: type index domain is the 13 starstat types (K <= 12,
    // planets-ui.md §1 census); a run of K==13 records is REFUSED. Name is
    // exactly 3 chars: any byte-SHIFTED discovery window then reads a name
    // of < 3 printable chars (the surrounding zero pad terminates it), so
    // K==13 is the ONLY discriminator separating this fixture.
    std::vector<uint8_t> s(size_t(20) * 0x60, 0);
    for (int i = 0; i < 14; ++i) {
        size_t h = size_t(i) * 0x60;
        uint32_t K = 13;  // out of the 0..12 domain
        std::memcpy(&s[h], &K, 4);
        float x = 10.f * (i + 1), y = 1.f;
        std::memcpy(&s[h + 0x08], &x, 4);
        std::memcpy(&s[h + 0x0c], &y, 4);
        std::memcpy(&s[h + 0x1c], "Fak", 3);
    }
    std::vector<Observer::StarRow> stars;
    CHECK(!Observer::parseRawStarBlock(s, &stars, &err));
}

TEST(observer_render_map_t382) {
    // Pure projection: corners map to grid corners; collisions mark '@'.
    std::vector<float> xs = {0.f, 100.f, 50.f, 50.f};
    std::vector<float> zs = {0.f, 100.f, 50.f, 50.f};
    std::vector<char> g = {'a', 'b', 'c', 'd'};
    const std::string m = Observer::renderMap(xs, zs, g, 11, 11);
    const size_t header = m.find('\n') + 1;
    const std::string body = m.substr(header);
    CHECK(body[0] == 'a');                                   // (0,0) corner
    CHECK(body[10 * 12 + 10] == 'b');                        // far corner
    CHECK(body[5 * 12 + 5] == '@');                          // two glyphs collide
    CHECK(Observer::renderMap({}, {}, {}, 4, 4) == "(nothing to plot)\n");
}
