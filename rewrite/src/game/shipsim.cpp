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
        // T1 — product 160 inverts the /160). Mid-walk quantizer NOT applied
        // [INFERRED]: S17 T3 verified for stationary positions, arrival-time-
        // only is the inferred reading; on arrival the commit snaps to grid.
        const double inv = dWorld > 0 ? walk * (kSugarStepA * kSugarStepB) / dWorld : 0.0;
        for (int i = 0; i < 3; ++i)
            pos[i] = pos[i] + static_cast<float>(static_cast<double>(delta[i]) * inv);
    }
    if (*arrived) {
        // Arrival grid snap (S17 T3 [verified] stationary law; the 12
        // off-grid ships are all mid-transit kind-2 — corroborates arrival-
        // time snapping [inferred]).
        for (int i = 0; i < 3; ++i) pos[i] = snapGrid(pos[i]);
    }
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
        // itself is NOT cited and is never invented here).
        const SimStar* dest = star(l->b);
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
        // FUN_00049a34 body is NOT banked (colonizer/land path). The only
        // cited arrival behaviour for a system arrival without a committed
        // slot model is the T-6 no-free-slot branch (kind stays 4 + three
        // %1000-500 scatter draws, "vanishes at sea" [state semantics
        // INFERRED]). Applied under that flag; t363's planet-slot model owns
        // the colonise leg. NO new law is invented here.
        landingAttempt(s, rep);
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
    // loop ... then command exec"). Prologue: zero +0x9c; POWER refill; slot
    // refresh loop is gizmo scope (t363 seam). Body L1: kind-5 lane march
    // (T-7). Races ascending; ships in sorted-list order.
    for (int race : ownersOf()) {
        for (auto& s : ships_) {
            if (s.owner != race) continue;
            s.status = 0;                                   // [ship+0x9c] := 0
            s.power = powerRefill(s.powerMax, turn_ - s.etaDay);
            if (s.kind == OrderKind::Placement) laneMarch(s, rep);
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
            // FUN_0004a658): MOVES re-grant +0x94 := drive stat +0x10 — PER
            // SWEEP (the call sits inside the executor prologue, which the
            // driver re-invokes every sweep). (FUN_0004a658's upkeep burn
            // +0x88 -= design[+0x36] is t363 gizmo scope — honest seam; the
            // boundary-state refill-without-burn matches the t101 "POW frozen
            // at autosave" observation, S22 IDENTITY TIE.)
            for (auto& s : ships_)
                if (s.owner == race) s.moves = s.driveStat;

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
    }
    mix(lcg_.state);
    mix(static_cast<uint64_t>(turn_));
    return h;
}

}  // namespace ascend::game
