// SPDX-License-Identifier: GPL-3.0-or-later

// Per-ship engine skeleton (t361). Laws + citations are at the declaration
// sites in shipsim.h; build contract docs/re/pership-spec.md (2); session
// adjudications docs/re/_wip_t361.md S1. Evidence rule: no constant without a
// docs/ pointer. INFERRED surrogates are flagged inline.
#include "game/shipsim.h"

#include <algorithm>
#include <cmath>
#include <cstring>

namespace ascend::game {

namespace {
constexpr double kWorldToSugar = 0.00625;  // 1/160, pool 0x25ff MEASURED (S17 T2)
constexpr double kSugarStepA = 32.0;       // pool 0x2603 MEASURED (S17 T2)
constexpr double kSugarStepB = 5.0;        // pool 0x2607 MEASURED (S17 T2)
constexpr double kThirdSpeed = 1.0 / 3.0;  // 0.333333 pool word (S22 L1/L3)
constexpr float kGrid = 32.0f;             // DAT_000895dc MEASURED 20/20 (S17 T3)
constexpr float kPlaceJitter = 200.0f;     // rng%200 (T-3, §19 T3)
constexpr float kPlaceYOffset = -200.0f;   // LIVE -200.0 @B+0x82bb0+0xaee (T-3)

double norm3(const float v[3]) {
    return std::sqrt(static_cast<double>(v[0]) * v[0] +
                     static_cast<double>(v[1]) * v[1] +
                     static_cast<double>(v[2]) * v[2]);
}

// Quantizer FUN_000533e0: coord := round(coord/g)*g, sign-directed (S17 T3).
float snapGrid(float v) {
    const float a = std::fabs(v);
    const float s = std::round(a / kGrid) * kGrid;
    return v < 0 ? -s : s;
}
}  // namespace

// x86 default rounding mode = round-half-to-EVEN (fistp). C's round() is
// half-away-from-zero and would diverge on every .5 tie (determinism pin
// seeds exercise 1.5 -> 2 and 2.5 -> 2).
int32_t ShipSim::x86Round(float v) {
    const float f = std::floor(v);
    const float rem = v - f;
    int32_t below = static_cast<int32_t>(f);
    if (rem > 0.5f) return below + 1;
    if (rem < 0.5f) return below;
    return (below % 2 == 0) ? below : below + 1;  // tie -> even
}

Ship Ship::fromRecord(const formats::ShipSave::Record& r, int currentTurn) {
    Ship s;
    s.id = r.slot;
    s.owner = r.ownerRace;
    // S59 L3: live rows carry kind 1..5; anything else maps to NoOrder
    // defensively (the parser's dead filter is the census law, S59 L2).
    s.kind = r.orderKind <= 5 ? static_cast<OrderKind>(r.orderKind)
                              : OrderKind::NoOrder;
    s.orderTarget = r.orderTarget;   // raw guest-physical value; NOT dereferenced
    s.actTarget = r.actTarget;
    s.act = r.actEnum;
    s.orderType = r.orderType;
    s.pos[0] = r.pos[0]; s.pos[1] = r.pos[1]; s.pos[2] = r.pos[2];
    s.power = static_cast<int32_t>(r.power);
    s.powerMax = static_cast<int32_t>(r.powerMax);
    s.moves = static_cast<int32_t>(r.moves);
    s.driveStat = static_cast<int32_t>(r.driveTotal);
    s.integrity = static_cast<int32_t>(r.integrity);
    s.maxIntegrity = static_cast<int32_t>(r.maxIntegrity);
    s.status = r.statusFlags;
    s.laneStepX = static_cast<int32_t>(r.laneStepX);
    s.laneStepZ = static_cast<int32_t>(r.laneStepZ);
    // t363 imports (contract item 5): recalc-owned fields VERBATIM from the
    // record, ring cidx bytes verbatim, cap + filled verbatim (phantom +1
    // preserved — shipsave.h:34 law). NO recalcShip() on import: the recalc
    // zeroes [+0x18] powerMax (generator-sum only), so re-deriving here would
    // destroy the stored budget (named asymmetry, _wip_t363 S3a/contract).
    s.weaponLevel = r.weaponLevel;
    s.shieldLevel = r.shieldLevel;
    s.cat2PowerCarry = r.cat2PowerCarry;
    s.scannerTotal = r.scannerTotal;
    s.specialCount = r.specialCount;
    s.targetSlot = static_cast<int32_t>(r.targetSlot);
    s.hullBaseDrive = static_cast<int32_t>(r.hullBaseDrive);
    s.shields = r.shields;
    s.invCap = r.invCap;
    s.invFilled = r.filled;
    for (size_t i = 0; i < kRingSlots && i < r.ringCidx.size(); ++i)
        s.inv[i].cidx = r.ringCidx[i];
    // Slot use-words and payloads are NOT in the t360 parser's field set;
    // they default (0 / 0) — the refresh law restores use-words at the first
    // tail anyway (MEASURED 5940/5940, _wip_t363 S4 item 5).
    // +0x52 ETA is NOT in the t360 parser's field set (shipsave.h — cited
    // fields only). Import at turn `currentTurn` stamps eta := currentTurn
    // (INFERRED: delta 0 -> full refill on the first boundary; callers who
    // measure the ETA set it directly on the Ship afterwards).
    s.etaDay = currentTurn;
    return s;
}

ShipSim::ShipSim(unsigned seed, int turn) : turn_(turn) {
    lcg_.state = static_cast<uint32_t>(seed);
}

void ShipSim::addStar(const SimStar& s) { stars_.push_back(s); }
void ShipSim::addLane(const SimLane& l) { lanes_.push_back(l); }

void ShipSim::addShip(const Ship& s) {
    ships_.push_back(s);
    sortShipList();
}

Ship* ShipSim::findShip(int id) {
    for (auto& s : ships_)
        if (s.id == id) return &s;
    return nullptr;
}

const SimLane* ShipSim::lane(int id) const {
    for (const auto& l : lanes_)
        if (l.id == id) return &l;
    return nullptr;
}

const SimStar* ShipSim::star(int id) const {
    for (const auto& st : stars_)
        if (st.id == id) return &st;
    return nullptr;
}

std::vector<int> ShipSim::ownersOf() const {
    std::vector<int> owners;
    for (const auto& s : ships_)
        if (s.owner >= 0 &&
            std::find(owners.begin(), owners.end(), s.owner) == owners.end())
            owners.push_back(s.owner);
    std::sort(owners.begin(), owners.end());
    return owners;
}

// ---- t379 COUNT WINDOW (docs/re/_wip_t379.md S1/S4/S6, MEASURED 60/60) ----
// liveCount is the count-word census mirror: count == full-array live census
// on BOTH banks (41/41 at t1253, 40/40 at t1254) and on the production ring.
// It is a CENSUS, not a size: corpses stay in ships_ exactly as they stay in
// RAM (the finalizer marks, never relocates — no compaction was ever seen).
int ShipSim::liveCount() const {
    int n = 0;
    for (const auto& s : ships_)
        if (s.owner >= 0) ++n;
    return n;
}

// The count-word walk range(0, count) in ARRAY order (r1_slot.ship_array_law
// enumerates `for k in range(min(n, 0x6b))` over record indices; the sim's
// id IS the record index — law A2, fromRecord: s.id = r.slot). Sorting by id
// reproduces index order; taking the first liveCount entries reproduces the
// window: it contains corpses BY CONSTRUCTION (measured: s12 inside range(40)
// at t1254) and it MISSES the orphan (measured: s40, live, at index 40).
// Walkers of this seam apply the owner filter themselves — the window is a
// MEMORY SHAPE, not an eligibility list (fleet-list item 3: the count word is
// not the census; pickers scan past it via ships()).
std::vector<const Ship*> ShipSim::countWindow() const {
    std::vector<const Ship*> byId;
    byId.reserve(ships_.size());
    for (const auto& s : ships_) byId.push_back(&s);
    std::sort(byId.begin(), byId.end(),
              [](const Ship* a, const Ship* b) { return a->id < b->id; });
    const int n = liveCount();
    if (static_cast<int>(byId.size()) > n) byId.resize(static_cast<size_t>(n));
    return byId;
}

std::vector<const Ship*> ShipSim::orphanedShips() const {
    std::vector<const Ship*> out;
    const int n = liveCount();
    for (const auto& s : ships_)
        if (s.owner >= 0 && s.id >= n) out.push_back(&s);
    return out;
}

// Step (2): the ship-list order. Verbatim comparator 0x40eb4:
//   mov (%eax),%eax / mov (%edx),%edx / mov 0x52(%eax),%eax / sub 0x52(%edx),%eax
// (raw read _wip_t361 S1: the deref loads the record pointer, the operand is
// the +0x52 field). Ascending on +0x52, stable (std::stable_sort) so ties
// keep insertion order == list order, matching first-in-list tie semantics.
void ShipSim::sortShipList() {
    std::stable_sort(ships_.begin(), ships_.end(),
                     [](const Ship& a, const Ship& b) {
                         return a.etaDay < b.etaDay;
                     });
}

void ShipSim::setAct(int shipId, uint8_t act, uint32_t actTarget) {
    if (Ship* s = findShip(shipId)) {
        s->act = act;
        s->actTarget = actTarget;
    }
}

bool ShipSim::issueTravel(int shipId, int laneId) {
    Ship* s = findShip(shipId);
    if (!s) return false;
    // T-4 validation verbatim: order kind in {1,2} (travel issuer FUN_000220a8
    // validates {Move, StarTarget} before setting kind 5, ships.md §19 T3).
    if (s->kind != OrderKind::Move && s->kind != OrderKind::StarTarget)
        return false;
    if (!lane(laneId)) return false;
    s->kind = OrderKind::Placement;
    s->orderType = 5;      // issuer sets +0x67 := 5 for delayed moves (spec §1)
    s->laneId = laneId;
    s->laneX = 0;
    s->arrivedFlag = false;
    return true;
}

bool ShipSim::retreatToSystem(int shipId) {
    Ship* s = findShip(shipId);
    if (!s) return false;
    // T-5 verbatim: 0x220f2 downgrades kinds {3,1,2} to 4 (retreat-to-system,
    // ai-dossier §5, fired 143x both owners MEASURED).
    if (s->kind != OrderKind::Engage && s->kind != OrderKind::Move &&
        s->kind != OrderKind::StarTarget)
        return false;
    s->kind = OrderKind::InSystem;
    s->laneId = -1;
    return true;
}

// t378 — EMPTY-SPACE destination issue, ATOMIC PAIR (see shipsim.h note).
// Witness shape (all 4 in-window issues, t370_slot_events_all.txt): kind 4
// UNCHANGED, type (+0x67) -> 3, triple (+0x6c) := destination, same frame.
// The prior type at issue was 2 (s16), 0 (s38), 1 (s25, s18) — no gate on
// the previous order type is cited, so none is imposed; the kind gate is the
// cited walk-guard family (FUN_00049f54 requires kind 4; kinds 1/2/5 are
// sticky in the decider, ai-dossier §5). Refusal writes NOTHING: the
// type-3-with-stale-triple state is unreachable through this seam.
bool ShipSim::issueDestination(int shipId, float x, float y, float z) {
    Ship* s = findShip(shipId);
    if (!s) return false;                       // no-target sentinel (sim)
    if (s->kind != OrderKind::InSystem) return false;   // state untouched
    s->orderType = 3;                           // +0x67 := 3
    s->targetPos[0] = x;                        // +0x6c triple := destination
    s->targetPos[1] = y;
    s->targetPos[2] = z;                        // ... all in ONE step
    return true;
}

// t378 — ORDER-END leg (s14 00:24:02: type 3->0 + trip := (0,0,0) same
// frame). Iff the ship holds an empty-space order, BOTH fields clear in one
// call; object orders (type 1/2) never own +0x6c — refuse, state untouched.
bool ShipSim::clearDestination(int shipId) {
    Ship* s = findShip(shipId);
    if (!s) return false;
    if (s->orderType != 3) return false;        // state untouched
    s->orderType = 0;
    s->targetPos[0] = 0;
    s->targetPos[1] = 0;
    s->targetPos[2] = 0;
    return true;
}

void ShipSim::setFocus(int race, uint32_t focus) {
    for (auto& f : focus_)
        if (f.race == race) { f.focus = focus; return; }
    focus_.push_back({race, focus});
}

int32_t ShipSim::powerRefill(int32_t powerMax, int32_t deltaDays) {
    // trunc([+0x18] * (1 + clamp((T - [+0x52])//100, 0, 10)/10)) — combat.md
    // §1 (t101 leg3, 25/35 exact + 35/35 bounded on 60.sav). //100 is
    // truncating integer division; negative delta clamps to 0 (full refill is
    // impossible below the stamp, the clamp floor is the cited law).
    int32_t q = deltaDays / 100;
    if (q < 0) q = 0;
    if (q > 10) q = 10;
    return static_cast<int32_t>(static_cast<double>(powerMax) *
                                (1.0 + static_cast<double>(q) / 10.0));
}

// ---- t363 GIZMO INVENTORY --------------------------------------------------

void ShipSim::setDesigns(const std::vector<SimDesign>& designs) {
    designs_ = designs;
}

namespace {
const SimDesign& designRow(const std::vector<SimDesign>& designs, uint8_t cidx) {
    // Vendor law: edx = cidx*0x6a + 0x7650c — the row is addressed DIRECTLY,
    // so an out-of-range cidx would read garbage. The sim substitutes the
    // honest all-zero cat-5 row (no gate, no contributions) for rows the
    // caller never installed; static, so pins can rely on it.
    static const SimDesign kZeroRow;
    if (cidx >= designs.size()) return kZeroRow;
    return designs[cidx];
}
}  // namespace

void ShipSim::recalcShip(Ship& s) const {
    // FUN_00049acc verbatim (_wip_t363 S3a; raw re-read 0x49ad5..0x49c04).
    // Zero the accumulators, then driveTotal := hullBaseDrive read BEFORE the
    // other zeroes (0x49ae4 load, 0x49b29 store — the same field, so order is
    // immaterial here; kept for the law's sake).
    s.weaponLevel = 0; s.shieldLevel = 0; s.scannerTotal = 0;
    s.specialCount = 0; s.cat2PowerCarry = 0; s.targetSlot = 0;
    s.powerMax = 0;                                    // [+0x18] := 0 (0x49af5)
    s.driveStat = s.hullBaseDrive;
    int32_t cntA = 0, cntB = 0;
    // Window i < invCap EXCLUSIVE (0x49bae `cmp esi,ebp; jge exit`): slots at
    // or beyond cap are the phantom zone — read NOTHING from them.
    for (uint32_t i = 0; i < s.invCap && i < kRingSlots; ++i) {
        const InvSlot& slot = s.inv[i];
        if (slot.cidx == 0xff) continue;               // 0x49b36
        const SimDesign& d = designRow(designs_, slot.cidx);
        s.weaponLevel += d.rowWeapon;                  // +0x00 (0x49b52)
        s.shieldLevel += d.rowShield;                  // +0x04 (0x49b5c)
        s.driveStat   += d.rowDrive;                   // +0x10 (0x49b67)
        s.scannerTotal += d.rowScanner;                // +0x20 (0x49b72)
        s.powerMax    += d.rowGenPower;                // +0x18 (0x49b7d)
        if (d.cat == 2) s.cat2PowerCarry += d.power;   // +0x1c (0x49b85)
        // Special-cidx legs are keyed on the cidx BYTE, not the category
        // (0x49b91..0x49bcc). NB each cidx value is distinct: a slot matches
        // at most one leg.
        if (slot.cidx == kCidxColonizer) s.targetSlot = -1;        // 0x49b9b
        else if (slot.cidx == kCidxLaneDrive) ++cntA;              // 0x49bb6
        else if (slot.cidx == kCidxHyperdrive) ++cntB;             // 0x49bc0
        else if (slot.cidx == kCidxCloaker) ++s.specialCount;      // 0x49bc9
    }
    // fistp(cntA * ds:0x2583) / fistp(cntB * ds:0x258b) via the DERIVED pool
    // values (kLaneStepXPool/kLaneStepZPool — see shipsim.h; counts are small
    // ints, the x87-round-vs-C edge is unreachable).
    s.laneStepX = x86Round(static_cast<float>(cntA) * kLaneStepXPool);
    s.laneStepZ = x86Round(static_cast<float>(cntB) * kLaneStepZPool);
}

int32_t ShipSim::upkeep(Ship& s) {
    // FUN_0004a658 verbatim (_wip_t363 S1a + S4 item 1 correction; raw re-read
    // 0x4a65e..0x4a74a). Returns the burn applied to power.
    // MOVES branch: bit0 SET -> [+0x94] := 0 and SKIP THE RE-GRANT ONLY — the
    // shields zeroing and the ring scan STILL RUN (0x4a67b `jmp 0x4a6a6`, NOT
    // 0x4a727; S4 item 1 retracts the earlier "skip ring scan" wording).
    // Else re-grant: bit1 SET adds the ds:0x77f6c global (0x4a690 — polarity
    // S3c: GLOBAL ADDED WHEN BIT SET; identity UNMEASURED, sim-level
    // driveAddend_ stand-in); bit1 CLR plain [+0x10].
    if (s.status & 0x1) {
        s.moves = 0;
    } else {
        s.moves = s.driveStat + ((s.status & 0x2) ? driveAddend_ : 0);
    }
    s.shields = 0;                                     // [+0x90] := 0 ALWAYS
    const int32_t powerBefore = s.power;
    // Ring scan i < cap (0x4a6b0..0x4a6d4; window EXCLUSIVE, phantom slots
    // contribute nothing — same law as the recalc).
    for (uint32_t i = 0; i < s.invCap && i < kRingSlots; ++i) {
        InvSlot& slot = s.inv[i];
        if (slot.cidx == 0xff) continue;               // 0x4a6d8
        const SimDesign& d = designRow(designs_, slot.cidx);
        if (!d.upkeepGate) continue;                   // w16+0x33 bit 0x20 (0x4a6e9)
        if (slot.payload != 0xffffffffu) continue;     // 0x4a6f9
        // PAYABLE gate (0x4a70a `jl next`): cost > power skips the slot
        // ENTIRELY — no partial burn, no clamp, no charges (S1a NEW READ).
        if (s.power < d.power) continue;
        s.power -= d.power;                            // [+0x88] -= cost (0x4a710)
        if (d.cat == 1)                                // 0x4a716
            s.shields += static_cast<uint32_t>(d.rowShield);  // charges (0x4a71c)
    }
    // bit3 of status -> [+0x90] := 0 (0x4a73a) AFTER the scan.
    if (s.status & 0x8) s.shields = 0;
    return powerBefore - s.power;
}

void ShipSim::refreshUseCounts(Ship& s) {
    // Turn-tail loop 0x4a772..0x4a7a4 (_wip_t363 S1c + CORRECTION): every
    // non-empty slot's u16 use word := design[+0x42] (numUses). The operand
    // is RAW +0x42 (0x7654e - 0x7650c), NOT +0x4e — measured save-side
    // 5940/5940 (S4 item 5). Window i < cap; runs for EVERY ship (S1c NB).
    for (uint32_t i = 0; i < s.invCap && i < kRingSlots; ++i) {
        if (s.inv[i].cidx == 0xff) continue;           // 0x4a78c
        s.inv[i].use = static_cast<uint16_t>(
            designRow(designs_, s.inv[i].cidx).numUses);
    }
}

bool ShipSim::setSlot(Ship& s, uint32_t idx, uint8_t cidx) {
    // FUN_00049698 verbatim (_wip_t363 S6 raw re-read 0x4969b..0x496de).
    if (idx > s.invCap) return false;                  // 0x4969b jg: idx==cap ADMITTED
    if (idx >= kRingSlots) return false;               // sim array bound (cap<=25
                                       // in the vendor: cap := hull table
                                       // dword, MEASURED 1234/1234 rows — the
                                       // guard is defensive, never hit)
    if (s.inv[idx].cidx == cidx) return false;         // 0x496b4: same-cidx-
                                       // in-TARGET-slot only; duplicates
                                       // across slots are LEGAL (600 live
                                       // rows carry repeats, S4 item 5)
    if (s.inv[idx].cidx == 0xff) ++s.invFilled;        // 0x496bd inc [+0x15e]
    s.inv[idx].cidx = cidx;                            // 0x496cc store
    recalcShip(s);                                     // 0x496d3
    return true;
}

bool ShipSim::clearSlot(Ship& s, uint32_t idx) {
    // FUN_000496e4 verbatim (S6 raw 0x496ee..0x49713): NO index bound in the
    // vendor (direct deref) — a phantom slot is clearable; the sim clamps to
    // the array defensively (idx>=25: the vendor would corrupt memory, the
    // sim refuses — named divergence, no cited law covers it).
    if (idx >= kRingSlots) return false;
    if (s.inv[idx].cidx == 0xff) return false;         // 0x496f5 je -> return 0
    --s.invFilled;                                     // 0x496f7 dec [+0x15e]
    s.inv[idx].cidx = 0xff;                            // 0x496fd
    recalcShip(s);                                     // 0x49704
    return true;
}

bool ShipSim::fillFirstEmpty(Ship& s, uint8_t cidx) {
    // FUN_00049624 verbatim (S6 raw 0x49632..0x4968d): scan i=0..cap-1
    // (0x4964a `cmp eax,[+0x15a]; jl` — window is CAP, NOT all-25 as spec
    // G3's shorthand words it; cap<=0 -> 0x4963e exit, no slot).
    if (s.invCap == 0) return false;
    for (uint32_t i = 0; i < s.invCap && i < kRingSlots; ++i) {
        if (s.inv[i].cidx != 0xff) continue;
        ++s.invFilled;                                 // 0x4966f/0x49672
        s.inv[i].cidx = cidx;                          // 0x49678
        recalcShip(s);                                 // 0x49681
        return true;
    }
    return false;                                      // 0x4968d
}

bool ShipSim::carriesCode(const Ship& s, uint8_t code) const {
    // Window = cap (the C2 loop 0x42d3f `cmp edx,[ebx+0x15a]; jge next` walks
    // slots i<cap; phantom slots are NOT equipment).
    for (uint32_t i = 0; i < s.invCap && i < kRingSlots; ++i)
        if (s.inv[i].cidx == code) return true;
    return false;
}

const Ship* ShipSim::firstCarrier(uint8_t code) const {
    // C2 shape verbatim (engagement resolver loop 0x42d09..0x42d5b, raw
    // re-read): FIRST ship in LIST order with BYTE[+0x58]==4 (InSystem) AND
    // a slot == code. No strength comparison — eligibility is order-state +
    // equipment. Returns nullptr when no carrier qualifies.
    // t364 NOTE: the vendor's array is built BEFORE the death finalizer can
    // run mid-resolution, so corpses (owner 0xffff, kind 0 — C4) are absent
    // from it; the sim filters them explicitly (owner < 0 == the -1 mirror).
    for (const auto& s : ships_)
        if (s.owner >= 0 && s.kind == OrderKind::InSystem &&
            carriesCode(s, code))
            return &s;
    return nullptr;
}

// ---------------------------------------------------------------------------
// t364 PER-SHIP COMBAT ROUND (spec §5 K1..K10). Verbatim windows and this
// session's corrections C1..C8: docs/re/_wip_t364.md; resolver region
// combat.md S2k. EVIDENCE RULE: every branch below cites an address.
// ---------------------------------------------------------------------------

bool ShipSim::setStance(int shipId, int arg, int targetShipId) {
    Ship* s = findShip(shipId);
    if (!s) return false;
    // FUN_0004a55c VERBATIM (0x4a55c..0x4a601) = refusal + stance stores +
    // the volley tail (the loop at 0x4a5c1 is INSIDE this function). The
    // power refusal (cmp [ship+0x88],0 / ret, 0x4a561..0x4a56f) PRECEDES
    // every store — zero state change.
    if (s->power == 0) return false;
    s->dispatcherGate = 1;                 // [+0x62] := 1 (0x4a591)
    // Arg->handler map C2 (raw 0x4a597..0x4a5ae; the banked "arg2->0" is
    // SUPERSEDED): cmp dx,1/jb -> arg0 => 2; cmp dx,2/jbe captures {1,2} => 1;
    // cmp dx,3/je => 0. The vendor's default arm asserts (0x3e5, msg 0x2623)
    // and STILL runs the tail with +0x67 unchanged; the sim refuses instead
    // (named deviation — no shipped caller passes arg > 3).
    if (arg == 0)      s->orderType = 2;
    else if (arg <= 2) s->orderType = 1;
    else if (arg == 3) s->orderType = 0;
    else return false;
    s->fireTarget = targetShipId;          // [+0x68] := ebx (0x4a574/7d/86)
    // Tail: the VOLLEY LOOP (0x4a5c1..0x4a5fc). The vendor returns edi = the
    // LAST slot whose dispatch result had bit0; the sim surfaces the same
    // value through volleyTail's return.
    return volleyTail(*s) >= 0;
}

int ShipSim::companionScan(const Ship& s) const {
    // FUN_0004a604 verbatim: first i < [ship+0x15a] with design cat==0 AND
    // (design[+0x42] NumUses == 0  OR  slot use WORD != 0) -> -1 (edx :=
    // 0xffffffff, the ELIGIBLE sentinel Leg B tests != 0); none -> 0. The
    // vendor's dword-overlap slot reads (ship+0xa8/+0xaa sar shifts) are
    // byte-equivalent to the direct InvSlot reads used here.
    for (uint32_t i = 0; i < s.invCap && i < kRingSlots; ++i) {
        if (s.inv[i].cidx == 0xff) continue;
        const SimDesign& d = designRow(designs_, s.inv[i].cidx);
        if (d.cat != 0) continue;
        if (d.numUses != 0 && s.inv[i].use == 0) continue;
        return -1;
    }
    return 0;
}

int ShipSim::volleyTail(Ship& s) {
    // 0x4a5c1..0x4a5fc verbatim, ALWAYS mode 0 (0x4a5ec xor edx,edx — the
    // volley can never charge or apply; C3/C5). The [+0x63] store fires for
    // EVERY cat-0 slot BEFORE its dispatcher call (0x4a5ee precedes 0x4a5f1)
    // and the per-slot result is ignored for the store — after the loop
    // activeSlot == the LAST cat-0 slot scanned, even an out-of-ammo one
    // (the C5 quirk the mode-1 commit edges then fire).
    // 0x49f28 gate (BYTE [+0x62]): 0 routes to movement bookkeeping 0x49f54
    // (NOT combat — unmodelled), so the volley only reaches the dispatcher
    // after a stance set. The stance setter always sets +0x62 := 1.
    if (s.dispatcherGate == 0) return -1;
    int last = -1;
    for (uint32_t i = 0; i < s.invCap && i < kRingSlots; ++i) {
        const InvSlot& slot = s.inv[i];
        if (slot.cidx == 0xff) continue;                       // 0x4a5d6
        const SimDesign& d = designRow(designs_, slot.cidx);
        if (d.cat != 0) continue;                              // 0x4a5e1
        s.activeSlot = static_cast<int>(i);                    // 0x4a5ee
        // Dispatcher FUN_0004a360, mode-0 legs: NumUses law 0x4a373..0x4a397
        // (design word == 0 -> unlimited; else slot use == 0 -> OUT OF AMMO,
        // handler SKIPPED, result 0; mode != 1 -> no DEC). Result bit0
        // (0x4a5f6 test al,1) is banked ONLY for the gun handler (engage
        // flag 0x4bad4..0x4bafc); handlers 1/2 returns are NOT banked (C8) —
        // honest 0, never claim an undecoded value.
        const bool ammo = (d.numUses == 0) || (slot.use != 0);
        if (ammo && s.orderType == 0 && gunEngageFlag(s, d))
            last = static_cast<int>(i);                        // 0x4a5fa
    }
    return last;                                               // eax = edi
}

bool ShipSim::gunEngageFlag(const Ship& s, const SimDesign& d) const {
    // Engage-flag block 0x4bad4..0x4bafc: eax := 1 iff [esp+0x4cc] != 0
    // (entry -1, always true), ecx (in-range) != 0, target != shooter
    // (0x4bae2), design[+0x33] bit 0 GZ_TARGETSHIP (0x4baec; ALL 10 cat-0
    // file rows carry bitpos 0). IN-RANGE (C9, fresh read): the range==0
    // branch 0x4b9a3 `je 0x4bad4` SKIPS the distance math with ecx still the
    // init sentinel -1 => RANGE 0 = UNLIMITED RANGE, not never-fire. No
    // shipped cat-0 row has Range 0 (gizmos.txt 76-row census), so the leg
    // is zero-witness — modelled verbatim, flagged as such.
    const Ship* t = nullptr;
    for (const auto& c : ships_)
        if (c.id == s.fireTarget) { t = &c; break; }
    if (!t) return false;                        // [+0x68] null (assert 0xad)
    if (t == &s) return false;                   // 0x4bae2 self excluded
    if (!d.targetShip) return false;             // GZ_TARGETSHIP AND-term
    if (d.range != 0) {
        double limit = static_cast<double>(d.range) * 32.0;  // design[+0x3a]<<5
        if (s.status & 0x4) limit *= 2.0;   // [ship+0x9c]&4 fmul ds:0x2743 —
                                            // header const UNRESTORED, 2x
                                            // [inferred] (cat-1 twin
                                            // ds:0x85312 == 2.0 verified)
        const double dx = static_cast<double>(t->pos[0]) - s.pos[0];
        const double dy = static_cast<double>(t->pos[1]) - s.pos[1];
        const double dz = static_cast<double>(t->pos[2]) - s.pos[2];
        const double dist = std::sqrt(dx * dx + dy * dy + dz * dz);  // 0x76da0
        if (dist > limit) return false;          // 0x4baae jbe -> fail leg
    }
    return true;
}

ShipSim::EngagementReport ShipSim::commitShot(int shipId, int mode) {
    EngagementReport rep;
    Ship* s = findShip(shipId);
    if (!s) return rep;
    if (s->dispatcherGate == 0) return rep;   // 0x49f28 gate -> bookkeeping
    // Dispatcher FUN_0004a360 entry: ACTIVE slot (+0x63) required (the gun
    // handler asserts 0xff slot at 0x4b922; the dispatcher derefs [ecx] at
    // 0x4a36b — the sim's -1/0xff stand in for the null deref).
    if (s->activeSlot < 0 || s->activeSlot >= kRingSlots) return rep;
    InvSlot& slot = s->inv[s->activeSlot];
    if (slot.cidx == 0xff) return rep;
    const SimDesign& d = designRow(designs_, slot.cidx);
    // NumUses law + DEC, verbatim order (0x4a37b..0x4a397): the ammo skip
    // tests the use word BEFORE any DEC (esi := 0 set only at 0x4a387 when
    // use == 0 pre-DEC); the DEC (0x4a390) runs ONLY mode==1 AND use != 0 —
    // and runs BEFORE the handler, ungated by any handler-side gate.
    if (d.numUses != 0) {
        if (slot.use == 0) return rep;         // out of ammo: handler skipped
        if (mode == 1) --slot.use;             // THE use-consumption site
    }
    rep.handler = s->orderType;                // C1: +0x67 selects the handler

    if (s->orderType != 0) {
        // Handlers 1 (0x4c794), 2 (0x4ca50), 5 (0x4cd90): the shield/drive
        // bodies run NO hit call (C1 rel32 census of [0x4c794,0x4ca50):
        // {0x2a428,0x38840,0x39f00,0x496e4,0x76da0}) and their returns are
        // not banked; the special tree is K9 reference scope. Named no-op
        // legs — and NO charge: the MIN-charge tail 0x4c614 lives inside the
        // GUN handler; the other handlers' accounting (if any) is unbanked,
        // so the sim charges nothing for them (never invent).
        return rep;
    }

    // ---- GUN HANDLER 0x4b8e4 (fresh full read 0x4b8e4..0x4bb7a) ----------
    const int32_t cost = std::min(d.power, s->power);   // MIN entry-computed
                                                        // (0x4b951..0x4b961)
    Ship* t = findShip(s->fireTarget);
    if (!t) return rep;                       // [+0x68] null assert (0xad)
    if (s->kind != OrderKind::InSystem || t->kind != OrderKind::InSystem)
        return rep;                            // K1 gate 0x4b982..0x4b991
    if (s->systemId == 0 || s->systemId != t->systemId)
        return rep;                            // K1 system identity 0x4b997
    // Engage flag (range + self + TARGETSHIP) — gate fail exits at 0x4c780
    // WITHOUT charge and without damage.
    if (!gunEngageFlag(*s, d)) return rep;
    // Gate passed: mode==1 charges at the tail (0x4bb6c cmp mode,1 /
    // je 0x4c614) EVEN WHEN damage is 0 (the 0x4bb64 or-0x10 leg falls
    // THROUGH to 0x4bb6c, verified) — so the charge precedes the damage
    // branch below. DEC already applied (dispatcher, above).
    if (mode == 1) s->power -= cost;           // 0x4c614..0x4c62a
    // Damage 0x4bb2a..0x4bb43: ebx = cat0 ? design[+0x52] : 0; cidx 0x2f ->
    // design[+0x4a]. The sim's rowWeapon IS the derived +0x52 for cat-0 rows
    // (recalc law) and 0 for every other category — a non-gun active slot
    // under a gun stance lands here as damage 0, verbatim.
    int32_t dmg = d.rowWeapon;
    if (slot.cidx == 0x2f) dmg = d.special1;   // Myrmidonic Carbonizer 20
    if (dmg == 0) { rep.flags |= 0x10; return rep; }   // 0x4bb64 skip, no hit

    // ---- HIT PATH 0x4b740 (call site 0x4bb56; absorb chain 0x4b7a7..) -----
    int32_t flags = 0;
    int32_t absorb = dmg;
    if (t->status & 0x10) absorb = 0;          // invulnerable: edi := 0 (0x4b7bc)
    int32_t spill = 0;
    if (absorb > static_cast<int32_t>(t->shields)) {   // 0x4b7c4 jle
        spill = absorb - static_cast<int32_t>(t->shields);
        absorb = static_cast<int32_t>(t->shields);
        flags |= 2;                            // shield overflow (0x4b7d1)
    }
    int32_t hullAbs = spill;
    if (hullAbs >= static_cast<int32_t>(t->integrity)) {  // 0x4b7e0 jl: no
        hullAbs = static_cast<int32_t>(t->integrity);     // flag ONLY when
        flags |= 4;                            // spill < hull (0x4b7e8)
    }
    rep.flags = flags;
    rep.shots = 1;                             // the hit call happened

    // C3: mode != 1 exits at 0x4b7f6 BEFORE the star-record leg, the APPLY,
    // and the death call — flags only, NOTHING lands. (The dispatcher DEC
    // already ran above — verbatim: the DEC precedes the handler, so a
    // mode-0 probe is the ONLY thing that cannot spend ammo; C5: the volley
    // itself is mode-0, so volley probes never DEC either.)
    if (mode != 1) return rep;

    // APPLY 0x4b87a..0x4b890 (sub then store, shield layer first).
    t->shields = static_cast<uint32_t>(static_cast<int32_t>(t->shields) - absorb);
    t->integrity -= hullAbs;
    rep.shieldAbsorb = absorb;
    rep.hullAbsorb = hullAbs;
    if (t->integrity < 1) {
        // DEATH 0x49d2c -> finalizer 0x249b4 (C4). t379 CORRECTION (word-level
        // corpse witness, docs/re/_wip_t379.md S5: slot 12 across the t1253->
        // t1254 boundary, exactly 5 of 177 words differ): the finalizer store
        // set is owner(+0x56):=0xffff, kind(+0x58):=0, name(+0x34):=0 (byte-
        // level NUL stamp), + the count DEC (sim: the census mirror, t379
        // liveCount) — plus act(+0x5d):=0 which the RAM witness adds to the
        // disasm window. +0x62/+0x63/+0x68 are in NEITHER the verified disasm
        // (t364 C4) NOR the witness (+0x68 0x002589f6 survived death): the
        // previous clears here were unwitnessed hygiene and are REMOVED.
        // +0x90 shields:=0 appears in the witness but is UNATTRIBUTABLE
        // (upkeep zeroes it always) — not wired. Corpse travel-reissue legs
        // are moot after the finalizer; planet-slot release is planet-side
        // (non-goal). The corpse stays IN PLACE at its array index (t379).
        rep.destroyed = t->id;
        t->owner = -1;
        t->kind = OrderKind::NoOrder;
        t->act = 0;
    }
    return rep;
}

ShipSim::EngagementReport ShipSim::engageRound(int race, int targetShipId,
                                               bool objectivePlanetShielded,
                                               int mode) {
    EngagementReport rep;
    // Leg A (carrier) 0x42d09..0x42d5b — runs ONLY when the objective planet
    // has NO ACTIVE Ship/Orbital-Shield item (gate 0x42cea..0x42cf3, S2k;
    // operands are planet state -> caller supplies, M-e). The vendor's array
    // is owner-race filtered (K10) — the sim filters by race here too.
    if (!objectivePlanetShielded) {
        for (const auto& c : ships_) {
            if (c.owner != race || c.kind != OrderKind::InSystem) continue;
            if (!carriesCode(c, kCidxInvasionModule)) continue;
            Ship* carrier = findShip(c.id);
            rep.carrier = c.id;
            rep.legACommitted = true;
            // C6 VERBATIM stores (0x42d9c..0x42dbd) then RETURN — no gunfire
            // in the same resolution ([+0x63] := 0 null slot: the carrier's
            // commit edges would skip the dispatcher anyway).
            carrier->dispatcherGate = 0;       // [+0x62] := 0
            carrier->activeSlot = -1;          // [+0x63] := 0 (null slot)
            carrier->orderType = 1;            // [+0x67] := 1
            carrier->fireTarget = targetShipId;// [+0x68] := objective
            return rep;
        }
        // C7: no carrier. The objective-IS-local-player branch (jne 0x437ee,
        // outside the banked region) is UNMODELLED; the not-local fall-
        // through returns 2 ("nothing picked") — the sim mirrors it as an
        // empty report.
        return rep;
    }
    // Leg B 0x42de0..0x42e34 verbatim tests IN ORDER: kind==4, companionScan
    // != 0 (eax: -1 eligible), stance setter != 0. The stance setter RUNS
    // the volley tail, so its result is the volley's engage-bit0 — a ship
    // that cannot hit THIS target is NOT picked and the scan CONTINUES
    // (vendor loop structure). First match stores [esp+0x2d0] and the
    // loop-head halt test (0x42ded) ends the scan.
    Ship* shooter = nullptr;
    for (auto& c : ships_) {
        if (c.owner != race) continue;
        if (c.kind != OrderKind::InSystem) continue;      // 0x42e08
        if (companionScan(c) == 0) continue;              // 0x42e10/0x42e15
        // Named substitution (C8): the vendor passes arg 1 (+0x67 := 1, the
        // handler-1 body whose return is UNDECODED); the firepower this leg
        // resolves IS the cat-0 gun path, so the sim sets the GUN stance
        // (arg 3 -> +0x67 := 0) and evaluates the cited gun engage flag.
        if (!setStance(c.id, 3, targetShipId)) continue;  // 0x42e24/0x42e29
        shooter = &c;
        break;
    }
    if (!shooter) return rep;
    rep.shooter = shooter->id;
    // Damage step: the cited commit law at the caller's mode (K6: player
    // edges pass 1, AI paths 0). FIRES [+0x63] = the LAST cat-0 slot the
    // stance volley scanned — the C5 quirk, verbatim (may be out-of-ammo ->
    // dispatcher skip -> no shot; that is the vendor's behaviour).
    EngagementReport shot = commitShot(shooter->id, mode);
    shot.shooter = shooter->id;
    return shot;
}

ShipSim::MagnetronReport ShipSim::useMagnetron(int shipId, int mode) {
    // t377R — see shipsim.h for the full contract (evidence _wip_t377 S2/S3,
    // witness M1 ships.md S64). Gate ORDER is the deliverable.
    MagnetronReport rep;
    Ship* s = findShip(shipId);
    if (!s) return rep;
    // Entry 0x4a360 derefs [+0x63] directly (NO [+0x62] test at this entry —
    // that gate is the caller FUN_00049f28's). activeSlot < 0 stands in for
    // the null deref: named divergence, refuse with zero state change.
    if (s->activeSlot < 0 || s->activeSlot >= kRingSlots) return rep;
    InvSlot& slot = s->inv[s->activeSlot];
    // 0xff active slot: the vendor would read design row 255 (past the
    // 76-row table — garbage; the UI can never select it). Same named
    // refusal as the gun path (commitShot 0xff check). This is what makes
    // "no second use" total: after the first commit the slot is 0xff, so a
    // repeat call changes NOTHING (no DEC, no charge, no placement).
    if (slot.cidx == 0xff) return rep;
    const SimDesign& d = designRow(designs_, slot.cidx);
    // C3 entry-computed cost 0x4ca89 (BEFORE any gate/placement): the value
    // the charge tail 0x4cbe3 will subtract.
    const int32_t cost = std::min(d.power, s->power);
    rep.cost = cost;
    // C7 prologue 0x4a373..0x4a397 — BEFORE the handler, ungated by any
    // handler-side gate: numUses==0 -> unlimited (no DEC); slot use==0 ->
    // BLOCK (handler never runs); else DEC mode-1-ONLY. A gate-failed use
    // STILL consumes a charge (zero-witness composition consequence,
    // flagged at the declaration).
    rep.ranHandler = true;
    if (d.numUses != 0) {
        if (slot.use == 0) return rep;         // out of ammo: esi=0, ret 0
        if (mode == 1) --slot.use;             // THE consumption site
    }
    // Handler 0x4ca50 gates (generic orderType-2 handler; the magnetron leg
    // is the tail case tree below):
    // C1 range gate 0x4cb76..0x4cb95 — CORRECTED POLARITY: FAIL iff
    // dist < Range*32 (TOO-CLOSE rejected; Range==0 skips via je 0x4cb99).
    // dist measured from the ACTIVE target triple (sim holds targetPos).
    bool rangeOK = true;
    if (d.range != 0) {
        const double dx = static_cast<double>(s->targetPos[0]) - s->pos[0];
        const double dy = static_cast<double>(s->targetPos[1]) - s->pos[1];
        const double dz = static_cast<double>(s->targetPos[2]) - s->pos[2];
        const double dist = std::sqrt(dx * dx + dy * dy + dz * dz);  // 0x76da0
        rangeOK = !(dist < static_cast<double>(d.range) * 32.0);
    }
    // C2 return word 0x4cbd4: bit0 = affordable (design cost <= power,
    // 0x4ca90) AND rangeOK — the ONLY commit test. bit1 = TARGETLANE flag,
    // OR-ed into the word, NOT tested here (its consumers are elsewhere,
    // unbanked — do not invent them).
    const bool affordable = d.power <= s->power;
    if (affordable && rangeOK) rep.flags |= 1;
    if (d.targetLane) rep.flags |= 2;
    // mode != 1 exits at 0x4cbcd BEFORE any store: probe reports flags/cost,
    // lands nothing (the DEC above was mode-1-only, so probes cannot spend
    // ammo either).
    if (mode != 1) return rep;
    if (!(rep.flags & 1)) return rep;          // 0x4cbd4 test bit0 -> fail leg
    rep.committed = true;
    // C3 charge tail 0x4cbe3: power -= min(Power, power) at entry value.
    s->power -= cost;
    // Kind-2 tail case tree 0x4cd51 (switch on the slot cidx): the 0x20 /
    // 0x34..0x3b / 0x3e legs are planet/star visibility bookkeeping OUTSIDE
    // the ship model (named non-goals, S3) — the sim returns for them;
    // cidx 0x3c is the magnetron leg 0x4cd0d..0x4cd43.
    if (slot.cidx != kCidxMagnetron) return rep;
    // FUN_000220a8 target gate (sim surrogate, S3): M1's kind byte stayed 4
    // (InSystem) across the use; kinds outside the cited set are a named
    // non-goal -> refuse placement (DEC+charge ALREADY PAID, flagged).
    if (s->kind != OrderKind::InSystem) return rep;
    const SimStar* st = star(s->targetStar);
    if (!st) return rep;                       // target does not resolve
    // Placement FUN_00021f58 (C5 verbatim): triple := star triple; y +=
    // -200.0 (LIVE ds:0xaee); TWO LCG draws 0x7824f, x += draw%200, z +=
    // draw%200 (idiv ebx==200 both axes — the 0x4cd12 xor ebx,ebx feeds only
    // the assert-skip test 0x21f62, NOT the divisor; _wip_t377 C5 audit).
    // Separate statements: draw ORDER is the determinism law.
    const int jx = draw();
    const int jz = draw();
    float p[3];
    p[0] = st->pos[0] + static_cast<float>(jx % 200);
    p[1] = st->pos[1] + kPlaceYOffset;
    p[2] = st->pos[2] + static_cast<float>(jz % 200);
    // Store via FUN_00049aa8 = store +0x9e then CALL quantizer FUN_000533e0
    // (g=32) on ALL THREE axes — M1 landing ON the 32-grid. kind transient:
    // BYTE[+0x58] := 5 at 0x4cd26, := 4 at 0x2202f — no observation boundary
    // between the stores, net kind = InSystem (M1: kind byte stays 4).
    for (int i = 0; i < 3; ++i) s->pos[i] = snapGrid(p[i]);
    s->kind = OrderKind::InSystem;
    rep.placed = true;
    // Slot rebuild 0x4cd24..0x4cd39: idx = ([+0x63] - ring base)/7 — the
    // vendor's pointer-to-index map is IDENTITY in the sim's index space —
    // then FUN_000496e4 clear-slot (C8: filled dec, recalc). M1: ring slot
    // REMOVED in the same event = SINGLE-USE consumption is explicit law.
    // [+0x63] itself is NOT cleared (no cited law touches it; the sim keeps
    // the index — the next call meets the 0xff refusal above).
    clearSlot(*s, static_cast<uint32_t>(s->activeSlot));
    return rep;
}




bool ShipSim::starArrivalComplete(Ship& s) {
    // FUN_00049a34 + admission FUN_000499f8 verbatim (_wip_t363 S3d + S4
    // item 3 polarity; raw re-read 0x499f8..0x49aa4 — see shipsim.h for the
    // full contract). The order payload names the lane RECORD (edx arg); the
    // OLD order target [+0x59] names the system object entered against.
    const SimLane* l = lane(s.orderPayloadLane);
    // Admission (0x499fb..0x49a25): (laneStepX + laneStepZ > 0) skips the
    // species test; else the species col-0x12 gate must hold (NEVER-SEEN
    // form, spec N4 — per-ship flag, default false = never admits). THEN the
    // lane must exist and bit 0x2 must be CLEAR (SET == CLOSED/DENIED).
    const bool hasLaneGear = static_cast<int32_t>(s.laneStepX + s.laneStepZ) > 0;
    if (!hasLaneGear && !s.speciesLaneTravel) return false;
    if (!l || l->closed) return false;                 // 0x49a21 jne -> 0
    // Admitted (0x49a44..0x49a97). The kind==3 leg (target := system-object
    // table entry) is UNREACHABLE from the sole caller 0x4a33d — the walk
    // guard is kind 4 — so the sim takes the else leg verbatim: esi := the
    // EXISTING [+0x59] target. The sim's target home is targetStar; the lane
    // id home is laneId (+0x59's surrogate after the store).
    const int target = s.targetStar;
    s.kind = OrderKind::Placement;                     // 0x49a74 [+0x58] := 5
    s.laneX = 0;                                       // 0x49a78 [+0x9e] := 0
    s.laneId = s.orderPayloadLane;                     // 0x49a82 [+0x59] := lane
    // 0x49a85 `cmp esi,[ecx]`: 1.0f iff the old target == lane[0] (A-end
    // object, S22 L1). The sim compares sim-level ids: target == l->a.
    s.laneToB = (target == l->a);
    return true;
}


int32_t ShipSim::walkLaw(float pos[3], int32_t* power, int32_t* moves,
                         const float delta[3], bool* arrived) {
    // S17 T1 verbatim (FUN_00049f54 0x4a034..0x4a23d).
    const double dWorld = norm3(delta);
    const double d = dWorld * kWorldToSugar;
    double walk = std::min(d, static_cast<double>(*moves));
    int32_t steps = std::max(1, x86Round(static_cast<float>(walk)));
    // Power clamp verbatim: `if int[ship+0x88] < steps` — the operand is
    // STEPS, not walk (ships.md S17 T1).
    if (static_cast<double>(*power) < static_cast<double>(steps)) {
        walk = walk * static_cast<double>(*power) / static_cast<double>(steps);
        steps = *power;
    }
    if (arrived) *arrived = (walk == d);
    if (steps > 0 && walk > 0) {
        // per-step normalize(delta)*(walk/steps)*32.0*5.0 summed over steps
        // == normalize(delta)*walk*160 (the two FMUL moffs are REAL per S17
        // T1 — product 160 inverts the /160).
        const double inv = dWorld > 0 ? walk * (kSugarStepA * kSugarStepB) / dWorld : 0.0;
        for (int i = 0; i < 3; ++i)
            pos[i] = pos[i] + static_cast<float>(static_cast<double>(delta[i]) * inv);
    }
    // GRID SNAP IS UNCONDITIONAL IN THE COMMIT — t380 STATIC CORRECTION
    // (docs/re/_wip_t380.md S1c/S1d, instruction-level): the quantizer call
    // 0x4a2cf sits on the walk body's straight line (no arrival branch), and
    // the copy-back of the quantized scratch triple 0x4a2d9..0x4a2ed is
    // gated ONLY by cmp edi,0x1 (arg2 = mode). The executor commit passes
    // edx=1 (0x25560 -> call 0x49f28, the t364-banked commit site); the two
    // dry-run callers 0x15cc5/0x15df0 pass edx=0 (scratch quantize, no
    // store). Arrival (0x4a2f0 fild [+0x94]) drives BOOKKEEPING only, never
    // the snap. The t361-era "arrival-time-only" [INFERRED] reading is
    // SUPERSEDED: every committed walk position is 32-aligned mid-transit
    // too. Runtime corroboration: playtest s10 lane-END arrival
    // (-1280,-1952,384) = 40/61/12 x 32 EXACT; ALL off-grid rows ever seen
    // are kind-5 LANE-LOCAL x (march 14/28/14-over-3, never stored through
    // the quantizing helper) or kind-2 cross-system frames.
    // Tie semantics BANKED t380 (0x533e0 full read): q = trunc(round(v +
    // 16*sign(v))/32)*32 -> ties (v = 16 mod 32) go AWAY FROM ZERO —
    // identical to snapGrid's std::round(a/g)*g.
    for (int i = 0; i < 3; ++i) pos[i] = snapGrid(pos[i]);
    const double remaining = static_cast<double>(*moves) - walk;
    *power -= steps;                       // [+0x88] -= steps (commit)
    // [+0x94] := round(remaining walk) — walk LEFT after this commit
    // (S17 T1 verbatim), floored at 0 (walk <= moves by construction; the
    // floor guards the fp-tie edge only).
    *moves = x86Round(static_cast<float>(remaining > 0 ? remaining : 0.0));
    return steps;
}

void ShipSim::laneMarch(Ship& s, BoundaryReport& rep) {
    // T-7 verbatim (FUN_0004a74c 0x4a7a6.. guard kind==5; ships.md S22 L1):
    // step0 = float([+8] + [+c]); gate1 third-speed lane -> step *= 1/3
    // (pool word MEASURED); gate2 species col 0x12==0x12 -> max(step,1)*2.0
    // — NEVER-SEEN (S22 L5 zero witnesses): NOT encoded (spec N4 keeps the
    // cited FORMS; the sim has no species table seam before t363).
    // NEITHER MOVES nor POWER is spent (MEASURED-negative, S21 item 1).
    const SimLane* l = lane(s.laneId);
    if (!l) return;  // dangling lane target: NO law is cited for kind 5 with
                     // an unresolvable lane record (T-5 covers {3,1,2} only) —
                     // hold state, no movement, no invented behaviour.
    double step = static_cast<double>(s.laneStepX + s.laneStepZ);
    if (l->thirdSpeed) step *= kThirdSpeed;
    s.laneX = static_cast<float>(std::min(static_cast<double>(s.laneX) + step,
                                          static_cast<double>(l->len)));
    if (s.laneX >= l->len) {
        // Lane end -> arrival placement via the cited T-3 law (S21 item 5's
        // flip/turn-around lives in the frame switch, spec G-d: keep
        // lane-local progress, re-place via star coords — the transform
        // itself is NOT cited and is never invented here). t363 (contract
        // item 3): the endpoint honours the +0xa2 direction surrogate —
        // laneToB ? star(l->b) : star(l->a). Default laneToB=true keeps the
        // t361 golden pins green (their mkLane has A==B anyway).
        const SimStar* dest = star(s.laneToB ? l->b : l->a);
        s.kind = OrderKind::InSystem;  // byte[+0x58] := 4 at 0x2202f (T-3)
        if (dest) {
            // position := star + (0,-200,0); rng%200 on the OTHER two axes
            // (two FUN_0007824f draws, idiv 200 — §19 T3 / T-3 verbatim).
            // Separate statements: call order of draw() within one declaration
            // is UNSPECIFIED and the draw ORDER is the determinism law.
            const int jx = draw();
            const int jz = draw();
            s.pos[0] = dest->pos[0] + static_cast<float>(jx % 200);
            s.pos[1] = dest->pos[1] + kPlaceYOffset;
            s.pos[2] = dest->pos[2] + static_cast<float>(jz % 200);
            // t380: this is the FUN_00021f58 placement — its store leg IS
            // call 0x49aa8 (quantizing helper, _wip_t380 S1a/S1c): the raw
            // triple lands 32-ALIGNED (rng jitter quantized away). Runtime
            // corroboration: playtest s10 lane-END arrival (-1280,-1952,384)
            // = 40/61/12 x 32 EXACT (S64 M5).
            for (int i = 0; i < 3; ++i) s.pos[i] = snapGrid(s.pos[i]);
        }
        s.laneId = -1;
        rep.placed.push_back(s.id);
    }
}

void ShipSim::landingAttempt(Ship& s, BoundaryReport& rep) {
    // T-6 (FUN_00049880 -> landing attempt FUN_00039810): the free-slot test
    // reads the destination PLANET's orbital ring (u16 +0x18..+0x1a) — the
    // planet/slot model is t363 scope, so the skeleton takes the cited
    // NO-FREE-SLOT branch: +0x58 := 4 + THREE rng draws (%1000-500) scatter
    // via FUN_00052ff4/FUN_00049aa8 — the ship "vanishes at sea" (state
    // semantics INFERRED, ships.md §10). When t363 adds the slot model this
    // seam picks the first branch instead (+0x58 := 3, slot byte1 := 0x17).
    s.kind = OrderKind::InSystem;
    // The completed order is CONSUMED: the landed ship carries no pending
    // act (T-6 return -1 LANDED ends the order; the executor's stale-target
    // leg 0x41a30 clears act the same way). Without this, a dwelling ship
    // would re-walk d==0 and burn three scatter draws EVERY boundary — the
    // S24 dwell witness (constant state end-to-end over 150 turns) forbids
    // that. [inferred but law-forced: the only reading consistent with T-6
    // completion + S24 dwell stasis.]
    s.act = 0;
    const int j0 = draw();  // sequential: draw ORDER is the determinism law
    const int j1 = draw();
    const int j2 = draw();
    s.pos[0] += static_cast<float>(j0 % 1000 - 500);
    s.pos[1] += static_cast<float>(j1 % 1000 - 500);
    s.pos[2] += static_cast<float>(j2 % 1000 - 500);
    // t380: the scatter store at 0x399df IS call 0x49aa8 (quantizing helper,
    // _wip_t380 S1a): the scattered triple lands 32-ALIGNED — the rest-on-
    // grid law holds at EVERY committed galactic store, scatter included.
    for (int i = 0; i < 3; ++i) s.pos[i] = snapGrid(s.pos[i]);
    rep.landed.push_back(s.id);
}

int ShipSim::commitMove(Ship& s, BoundaryReport& rep) {
    // Walk guard verbatim: FUN_00049f54 requires byte[ship+0x58]==4 (ships.md
    // S17 T1; spec T-9 quotes the same guard). The pership-spec T-9 heading
    // "kind 1/2/3 in the executor" is the t359 summary — the CITED guard is
    // kind 4, and it resolves the assert law cleanly: in-system ships walk,
    // completion hooks land them to kind 3 (T-6) or keep them dwelling at 4,
    // so after movement kind is always 3 or 4 (0x419cf verbatim). Kind 3's
    // gun/ability chain is engagement scope (t364); kind 5 marches in the
    // turn tail (T-7), never here (S21 item 1 measured-negative); kinds 1/2
    // travel cross-system via the T-4 issuer (kind -> 5) and are sticky in
    // the decider (ai-dossier §5) — nothing to commit until they arrive as
    // kind 4 or their act goes stale (T-5).
    if (s.kind != OrderKind::InSystem) return 0;   // vendor arm reporting 0

    // Target triple by order TYPE +0x67 (S17 T1 verbatim: 3=abs triple
    // +0x6c, 1=ptr f[0..2], 2=star-handle f0/1/2, other incl 5 -> no walk).
    // The sim holds the type-1 ptr triple and the type-3 abs triple in the
    // same explicit targetPos field (INFERRED surrogate — the vendor derefs a
    // guest-physical pointer, the sim is driven from record state, spec N8).
    float delta[3];
    bool have = false;
    if (s.orderType == 1 || s.orderType == 3) {
        delta[0] = s.targetPos[0] - s.pos[0];
        delta[1] = s.targetPos[1] - s.pos[1];
        delta[2] = s.targetPos[2] - s.pos[2];
        have = true;
    } else if (s.orderType == 2) {
        const SimStar* st = star(s.targetStar);
        if (st) {
            delta[0] = st->pos[0] - s.pos[0];
            delta[1] = st->pos[1] - s.pos[1];
            delta[2] = st->pos[2] - s.pos[2];
            have = true;
        } else {
            retreatToSystem(s.id);  // dangling target ~ T-5 not-targetable
        }
    }
    if (!have) return 0;   // orderType 5/0 or dangling star: no walk, 0 status

    bool arrived = false;
    walkLaw(s.pos, &s.power, &s.moves, delta, &arrived);
    // VERBATIM commit-exit law (0x41b8f..0x41ba6: `sar eax,0x10; test eax,eax;
    // jle -> return 0; else return -1`): work is reported iff REMAINING WALK
    // > 0 after the commit. The sim's own commit law sets +0x94 :=
    // round(remaining) (S17 T1), so post-walk moves IS the remaining — the
    // most literal mapping available. [unverified micro-edge: the vendor
    // reads the RAW accumulator, the sim the rounded word; they differ only
    // when 0 < remaining < 0.5 — named in _wip_t362 S7, no witness either
    // way.] An ARRIVED ship with moves left reports work -> one extra no-op
    // sweep (act consumed at landing / stale-clear makes the re-pick empty),
    // STATE-EQUIVALENT to the vendor stopping; sweep accounting pinned in
    // test_piecemeal_t362.
    const int status = s.moves > 0 ? 1 : 0;
    if (!arrived) return status;   // walk committed, no completion hook
    s.arrivedFlag = true;

    // Completion hooks on arrival (S17 T1: type1 -> FUN_00049880, type2 ->
    // FUN_00049a34; ships.md §10 dispatch switch).
    if (s.orderType == 1) {
        landingAttempt(s, rep);      // T-6 (planet-slot model is t363)
    } else if (s.orderType == 2) {
        // FUN_00049a34 is BANKED (t363, _wip_t363 S3d/S6). Admitted: kind 2
        // -> 5 INSIDE the commit (0x49a74), lane-local x reset, laneId set,
        // direction flag stored. Denied: state untouched (0x49aa1 exit) —
        // the ship stays kind 4 with its act intact (no cited law clears it;
        // the t361-era scatter fallback is SUPERSEDED here, it stood in for
        // this body). The executor's assert leg then sees kind 5 -> counted
        // violation 0x93e per the raw sequence (S4 item 4), never fatal.
        if (starArrivalComplete(s)) rep.laned.push_back(s.id);
    }
    // orderType 3 (abs-triple ENGAGE anchor): arrival is the engagement
    // hand-off — t364 seam, no state change.
    return status;
}

BoundaryReport ShipSim::advanceBoundary() {
    BoundaryReport rep;

    // (1) Per-ship turn tail = FUN_0004a74c verbatim (IDENTITY TIE, ships.md
    // S22: the march L1 and the prologue live in ONE function; caller
    // FUN_0003e6e0 per-race turn tail, ai-dossier §1 phase order "per-race AI
    // loop ... then command exec"). Prologue ORDER (t363, _wip_t363 S1c + S4
    // item 2): status +0x9c := 0 (0x4a756) -> POWER refill (0x4a76c, the
    // clamp call 0x4a75f in between) -> slot use-count REFRESH loop
    // (0x4a772..0x4a7a4, every ship, no kind gate) -> kind-5 march body
    // (0x4a7a6 guard) -> upkeep FUN_0004a658 (0x4a95b, BOTH the march path
    // and the skip path converge on it). Status is zeroed BEFORE the upkeep
    // call, so within the tail the upkeep bit tests always see 0 (S4 item 2)
    // — the tail re-grants plain drive and the burn lands AFTER the refill:
    // the t361/t362 refill-without-burn seam CLOSED verbatim.
    for (int race : ownersOf()) {
        for (auto& s : ships_) {
            if (s.owner != race) continue;
            s.status = 0;                                   // [ship+0x9c] := 0
            s.power = powerRefill(s.powerMax, turn_ - s.etaDay);
            refreshUseCounts(s);                            // 0x4a772 loop
            if (s.kind == OrderKind::Placement) laneMarch(s, rep);
            upkeep(s);                                      // 0x4a95b
        }
    }

    // (2) list order (sorted array = engine state; +0x52 stamps move).
    sortShipList();

    // (3)+(4) Command executor driver = FUN_0002547c verbatim (t362). The
    // driver REPEATS the whole per-race pass while any race's executor call
    // reported work: 0x2550c reloads the race count, 0x2551b..0x25531 walks
    // every race entry (executor call 0x2554f, `or edi,eax` accumulate), then
    // 0x25525 `test edi,edi; jne 0x2550c`. A race reports work when its call
    // picked and committed a ship (return status != 0 — the ah arms at
    // 0x25560/0x25570/0x25587 are the mode==1 commit hooks; the no-pick path
    // 0x419c0 returns ebx==0). => PIECEMEAL DEPARTURE: one MIN-POWER pick per
    // sweep, sweeps run until the race's POWER drains. Witness: 3 same-owner
    // kind flips in ONE boundary, twice (work/r362_witness.out B2; owner 1
    // slots 17/20/29 t1104->1105, owner 2 slots 12/21/23 t1111->1112). The
    // t361 one-pick-per-boundary encoding is superseded by this leg.
    // Termination: every walked pick spends POWER (steps >= 1 while eligible,
    // POWER==0 fails the 0x4134e gate), so the loop drains. Safety cap below
    // sets executorStalled; it must never fire.
    std::vector<int> owners = ownersOf();
    bool drained = false;
    for (int sweep = 0; !drained && sweep < 100000; ++sweep) {
        bool anyWork = false;
        for (int race : owners) {
            // Resolver step 1 verbatim (T4: FUN_0003ea08 @0x412cf ->
            // FUN_0004a658): the FULL upkeep body — MOVES re-grant (+0x94 :=
            // drive stat +0x10, status-bit gated) PLUS the shield-maintenance
            // burn (+0x88 -= cost) — PER SWEEP (the call sits inside the
            // executor prologue, which the driver re-invokes every sweep;
            // _wip_t363 S1b). t363 closes the bare-re-grant seam: the burn
            // lands BEFORE this sweep's MIN-POWER pick, so it changes both
            // the pick ORDER and the drain rate (a burn-to-zero ship fails
            // the 0x4134e POWER>0 gate for the rest of the boundary).
            for (auto& s : ships_)
                if (s.owner == race) upkeep(s);

            // Stale-act law (0x41a1c..0x41a45): act target != the race's
            // current focus object -> act CLEARED (0x41a30 movb $0x0,[+0x5d]).
            // Focus cannot change mid-boundary (no caller between sweeps), so
            // clearing once on the first sweep is state-equivalent to the
            // vendor's per-sweep clear; the vendor's re-decide call 0x40178 is
            // decider policy (target scoring FUN_00039b28 NOT banked) — the
            // sim leaves the ship act-cleared and the caller re-sets via
            // setAct(). Documented seam, no invented AI.
            if (sweep == 0) {
                uint32_t focus = 0;
                bool hasFocus = false;
                for (const auto& f : focus_)
                    if (f.race == race) { focus = f.focus; hasFocus = true; }
                if (hasFocus) {
                    for (auto& s : ships_)
                        if (s.owner == race && s.act != 0 && s.actTarget != focus)
                            s.act = 0;
                }
            }

            // T-10 (word-decrement-only writer 0x3ac1c): the pick below reads
            // the word PRE-decrement (suppress-then-decrement, t361-pinned:
            // dwell 2 suppresses boundaries 1-2, fires on 3), and the
            // decrement runs ONCE per boundary — hoisted BELOW the sweep loop
            // so no sweep can act on a decremented value and a multi-sweep
            // boundary cannot re-decrement. Field home DISPUTED G-a — modelled
            // at sim level, never on a record offset.

            // Pick: act set, POWER > 0 (cmpl $0x0,+0x88; jle — raw 0x4134e),
            // kind != 1 (cmpb $0x1,+0x58; je — raw 0x41357, MOVE excluded from
            // the sweep verbatim), kind != 5 (the march spends NEITHER MOVES
            // nor POWER — MEASURED-negative S21 item 1 — and was already
            // advanced by the tail in step (1); the executor's case-1 gradient
            // hop is an issuer seam), dwell word == 0. MIN POWER, strict <
            // (jge skip => first ties), first-in-list order (0x4195d walk).
            Ship* pick = nullptr;
            for (auto& s : ships_) {
                if (s.owner != race) continue;
                if (s.act == 0) continue;
                if (s.power <= 0) continue;
                if (s.kind == OrderKind::Move || s.kind == OrderKind::Placement)
                    continue;
                if (s.dwellTurns > 0) continue;        // suppressed (T-10)
                if (!pick || s.power < pick->power) pick = &s;  // strict <
            }

            if (!pick) continue;      // this race silent this sweep

            // Commit the pick's move, then the ASSERT law (0x419cf..0x419f1).
            // Raw sequence: kind==3 -> call 0x39894, THEN cmpb $0x4 — a ship
            // still at kind 3 after the gate falls into assert id 0x93e at
            // 0x2a428 UNLESS the gate changed kind; ai-dossier §5 reads kind
            // 3/4 as both tolerated. The sim follows the dossier reading (kind
            // 3 tolerated — the gate body is engagement scope t364), and
            // COUNTS violations rather than crashing (headless). The sim's own
            // commits only ever leave kind 3-or-4, so asserts == 0 is the
            // expected pin.
            const int commitStatus = commitMove(*pick, rep);
            rep.acted.push_back(pick->id);
            if (pick->kind != OrderKind::Engage &&
                pick->kind != OrderKind::InSystem)
                ++rep.asserts;
            // Driver `or edi,eax` (0x25554): the repeat fires on the COMMIT
            // status, not the pick — a pick whose commit arm reports 0 (kind
            // not walkable, no target triple) leaves edi clear (_wip_t362 S6).
            if (commitStatus != 0) anyWork = true;
        }
        ++rep.sweeps;
        if (!anyWork) drained = true;
    }
    if (!drained) rep.executorStalled = true;

    // T-10 decrement pass ONCE per boundary, AFTER all sweeps read the words
    // (suppress-then-decrement order is t361-pinned; runs even when nothing
    // was picked). Races ascending per the per-race frame.
    for (int race : owners)
        for (auto& s : ships_)
            if (s.owner == race && s.dwellTurns > 0) --s.dwellTurns;

    ++turn_;
    return rep;
}

uint64_t ShipSim::digest() const {
    uint64_t h = 0xcbf29ce484222325ull;  // FNV-1a64 (shipsave pin convention)
    auto mix = [&h](uint64_t v) {
        for (int i = 0; i < 8; ++i) {
            h ^= (v >> (i * 8)) & 0xffu;
            h *= 0x100000001b3ull;
        }
    };
    auto mixf = [&](float f) {
        uint32_t u;
        std::memcpy(&u, &f, 4);
        mix(u);
    };
    mix(static_cast<uint64_t>(ships_.size()));
    for (const auto& s : ships_) {
        mix(static_cast<uint64_t>(s.id));
        mix(static_cast<uint64_t>(s.owner));
        mix(static_cast<uint64_t>(s.kind));
        mix(static_cast<uint64_t>(s.act));
        mix(s.orderTarget);
        mixf(s.pos[0]); mixf(s.pos[1]); mixf(s.pos[2]);
        mix(static_cast<uint64_t>(static_cast<uint32_t>(s.power)));
        mix(static_cast<uint64_t>(static_cast<uint32_t>(s.moves)));
        mix(static_cast<uint64_t>(static_cast<uint32_t>(s.integrity)));
        mix(static_cast<uint64_t>(s.dwellTurns));
        mixf(s.laneX);
        mix(static_cast<uint64_t>(s.laneId));
        // t363 state (contract item 4): shield charges, recalc-owned levels,
        // the inventory ring (cidx / use low-16 / payload per slot), cap and
        // the direction flag. The determinism pins stay green — the digest is
        // a pure function of state either way.
        mix(static_cast<uint64_t>(s.shields));
        mix(static_cast<uint64_t>(s.weaponLevel));
        mix(static_cast<uint64_t>(s.shieldLevel));
        for (int i = 0; i < kRingSlots; ++i) {
            mix(s.inv[i].cidx);
            mix(s.inv[i].use);
            mix(s.inv[i].payload);
        }
        mix(static_cast<uint64_t>(s.invCap));
        mix(s.laneToB ? 1ull : 0ull);
        // t364 state: the engagement quadruple (+0x62/+0x63/+0x67/+0x68) and
        // the system identity. The determinism pins stay green (digest is a
        // pure function of state either way).
        mix(s.dispatcherGate);
        mix(static_cast<uint64_t>(s.activeSlot));
        mix(s.orderType);
        mix(static_cast<uint64_t>(s.fireTarget));
        mix(s.systemId);
    }
    mix(lcg_.state);
    mix(static_cast<uint64_t>(turn_));
    return h;
}

}  // namespace ascend::game
